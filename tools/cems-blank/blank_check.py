"""Pre-registered count behind the 2-hour minimum down times left by the fill patch for PUDL
issue #5514 (pre-registration id cems-blank-1; plan: docs/cems-blank-plan.md in
munimtechnologies/eia860m-slip).

The fill patch (tools/cems-mindown/fill_isolated.py 0.1.0) fills only single blank hours, so
a unit whose shortest down run is two blank hours ends at a 2-hour minimum down time. This
script runs the same pipeline as job cems-mindown-v3 (mindown_check.py 0.1.0 with
mindown_v2.py's reader fix; Colorado, Indiana and Wisconsin; report year 2025) with no patch
and with the fill patch. In each run it keeps the hourly frame that PUDL's
calculate_min_up_or_down_times receives for down times and describes every down run
(consecutive null load_factor_bin hours of one unit, as PUDL counts them): its length,
whether the unit has an hour just before and just after it, whether those hours are at or
above the unit's minimum stable bin and report a full operating hour, and how many of the
run's own hours report operating time or heat input.

PUDL's code (MIT) and data (CC BY 4.0) are downloaded at run time and not stored here.

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.).
"""

import argparse
import importlib
import json
import os
import sys
import tempfile
import urllib.request

import polars as pl

import fill_isolated as fi
import mindown_check as mc
import mindown_v2 as v2
import stubs

VERSION = "0.1.0"
UNIT_COLS = ["plant_id_epa", "emissions_unit_id_epa"]
TIME_COL = fi.TIME_COL
BIN_COL = fi.BIN_COL
MS_COL = "min_stable_bin"
KEEP = UNIT_COLS + [TIME_COL, BIN_COL, MS_COL, "operating_time_hours", "heat_content_mmbtu"]
FULL_HOUR = 0.999
MODES = ("none", "fill")
V3_CSV = "v3_units.csv"
V3_COLS = {"none": "min_down_time_hours", "fill": "min_down_time_hours_fill"}

UPFLANK = pl.col("before_up") & pl.col("after_up")
STRICT = UPFLANK & pl.col("before_full") & pl.col("after_full")
ISOLATED = (pl.col("length") == 1) & pl.col("before") & pl.col("after")


def up_expr(bin_col=BIN_COL, ms_col=MS_COL):
    """PUDL's filter_for_min_stable_bin as a boolean: the bin is at or above the min stable bin."""
    return ((pl.col(bin_col).struct.field("left") >= pl.col(ms_col).struct.field("left"))
            & (pl.col(bin_col).struct.field("right") >= pl.col(ms_col).struct.field("right"))
            ).fill_null(False)


def run_id_expr(unit_cols=UNIT_COLS, time_col=TIME_COL):
    """PUDL's _add_run_id_expr (4d3366b) without its state option."""
    same_unit = pl.all_horizontal([pl.col(c).eq(pl.col(c).shift()) for c in unit_cols])
    consecutive = pl.col(time_col).diff().dt.total_seconds().truediv(3600).eq(1)
    return (~(same_unit & consecutive)).fill_null(True).cum_sum()


def run_table(df, unit_cols=UNIT_COLS, time_col=TIME_COL):
    """One row per down run: consecutive null-bin hours of one unit, as PUDL counts them.

    before/after: the unit has an hour exactly 1 h before the run's first hour / after its
    last hour (that hour has a non-null bin, or it would belong to the run).
    before_up/after_up: that hour is at or above the unit's min stable bin.
    before_full/after_full: that hour reports a full operating hour.
    op_hours/heat_hours: the run's hours reporting operating time / heat input above 0.
    """
    df = fi.sort_hours(df, unit_cols, time_col)
    same_prev = pl.all_horizontal([pl.col(c).eq(pl.col(c).shift(1)) for c in unit_cols])
    same_next = pl.all_horizontal([pl.col(c).eq(pl.col(c).shift(-1)) for c in unit_cols])
    hour_before = (pl.col(time_col) - pl.col(time_col).shift(1)).dt.total_seconds().eq(3600)
    hour_after = (pl.col(time_col).shift(-1) - pl.col(time_col)).dt.total_seconds().eq(3600)
    df = df.with_columns(
        (same_prev & hour_before).fill_null(False).alias("_before"),
        (same_next & hour_after).fill_null(False).alias("_after"),
        up_expr().alias("_up"),
        (pl.col("operating_time_hours") >= FULL_HOUR).fill_null(False).alias("_full"),
    ).with_columns(
        (pl.col("_before") & pl.col("_up").shift(1)).fill_null(False).alias("_before_up"),
        (pl.col("_after") & pl.col("_up").shift(-1)).fill_null(False).alias("_after_up"),
        (pl.col("_before") & pl.col("_full").shift(1)).fill_null(False).alias("_before_full"),
        (pl.col("_after") & pl.col("_full").shift(-1)).fill_null(False).alias("_after_full"),
        (pl.col("operating_time_hours") > 0).fill_null(False).alias("_op"),
        (pl.col("heat_content_mmbtu") > 0).fill_null(False).alias("_heat"),
    )
    runs = df.filter(pl.col(BIN_COL).is_null()).with_columns(
        run_id_expr(unit_cols, time_col).alias("_run"))

    def first(c):
        return pl.col(c).sort_by(time_col).first()

    def last(c):
        return pl.col(c).sort_by(time_col).last()

    return runs.group_by(unit_cols + ["_run"]).agg(
        pl.len().cast(pl.Int64).alias("length"),
        first(time_col).alias("start"),
        first("_before").alias("before"),
        last("_after").alias("after"),
        first("_before_up").alias("before_up"),
        last("_after_up").alias("after_up"),
        first("_before_full").alias("before_full"),
        last("_after_full").alias("after_full"),
        pl.col("_op").sum().cast(pl.Int64).alias("op_hours"),
        pl.col("_heat").sum().cast(pl.Int64).alias("heat_hours"),
    ).drop("_run").sort(unit_cols + ["start"])


def unit_table(runs, out, unit_cols=UNIT_COLS):
    """Per unit of PUDL's output: its min_down_time_hours and what the run table says.

    cf_min / cf_up_min: the shortest down run once runs of 1-2 hours with strict / up flanks
    are set aside (empty when no run is left).
    """
    short = pl.col("length") <= 2
    shortest = pl.col("length") == pl.col("length").min()
    per = runs.group_by(unit_cols).agg(
        pl.len().cast(pl.Int64).alias("runs"),
        pl.col("length").min().alias("run_min"),
        (UPFLANK & (pl.col("length") == 2)).any().alias("upflank_2h"),
        (STRICT & (pl.col("length") == 2)).any().alias("strict_2h"),
        pl.col("length").filter(~(STRICT & short)).min().alias("cf_min"),
        pl.col("length").filter(~(UPFLANK & short)).min().alias("cf_up_min"),
        pl.col("op_hours").filter(shortest).sum().alias("min_runs_op_hours"),
    )
    return out.select(unit_cols + ["min_down_time_hours"]).join(per, on=unit_cols, how="left")


def buckets(s):
    v = s.drop_nulls()
    return {"1": int((v == 1).sum()), "2": int((v == 2).sum()), "3": int((v == 3).sum()),
            "4-9": int(((v >= 4) & (v <= 9)).sum()), "10+": int((v >= 10).sum()),
            "none": int(s.null_count())}


def summarize(units, runs, unit_cols=UNIT_COLS):
    u = units.with_columns(
        pl.col("run_min").cast(pl.Float64).eq_missing(pl.col("min_down_time_hours"))
        .alias("_same"))
    has_min = u.filter(pl.col("min_down_time_hours").is_not_null())
    at2 = u.filter(pl.col("min_down_time_hours") == 2)
    two = runs.join(at2.select(unit_cols), on=unit_cols, how="semi").filter(
        pl.col("length") == 2)
    iso = runs.filter(ISOLATED)
    return {
        "units": u.height,
        "run_min_equal": int(u["_same"].sum()),
        "units_with_min": has_min.height,
        "at1": has_min.filter(pl.col("min_down_time_hours") == 1).height,
        "at2": at2.height,
        "le2": has_min.filter(pl.col("min_down_time_hours") <= 2).height,
        "at2_upflank": int(at2["upflank_2h"].fill_null(False).sum()),
        "at2_strict": int(at2["strict_2h"].fill_null(False).sum()),
        "cf_strict_le2": has_min.filter(pl.col("cf_min") <= 2).height,
        "cf_upflank_le2": has_min.filter(pl.col("cf_up_min") <= 2).height,
        "min_buckets": buckets(has_min["min_down_time_hours"]),
        "cf_strict_buckets": buckets(has_min["cf_min"]),
        "cf_upflank_buckets": buckets(has_min["cf_up_min"]),
        "min_median": has_min["min_down_time_hours"].median(),
        "cf_strict_median": has_min["cf_min"].median(),
        "two_runs": two.height,
        "two_runs_hours": 2 * two.height,
        "two_runs_no_op_hours": 2 * two.height - int(two["op_hours"].sum()),
        "two_runs_heat_hours": int(two["heat_hours"].sum()),
        "two_runs_sandwiched": two.filter(pl.col("before") & pl.col("after")).height,
        "two_runs_upflank": two.filter(UPFLANK).height,
        "two_runs_strict": two.filter(STRICT).height,
        "isolated_runs": iso.height,
        "isolated_no_op_no_heat": iso.filter((pl.col("op_hours") == 0)
                                             & (pl.col("heat_hours") == 0)).height,
        "isolated_upflank": iso.filter(UPFLANK).height,
        "isolated_strict": iso.filter(STRICT).height,
        "runs": runs.height,
        "run_hours": int(runs["length"].sum()),
        "run_op_hours": int(runs["op_hours"].sum()),
        "run_heat_hours": int(runs["heat_hours"].sum()),
        "units_min_runs_op": has_min.filter(pl.col("min_runs_op_hours") > 0).height,
    }


def read_v3(path):
    return pl.read_csv(path, schema_overrides={
        "plant_id_epa": pl.Int64, "emissions_unit_id_epa": pl.String, "state_run": pl.String,
        "min_down_time_hours": pl.Float64, "min_up_time_hours": pl.Float64,
        "min_down_time_hours_fill": pl.Float64, "min_up_time_hours_fill": pl.Float64})


def compare_v3(units, v3, v3_col):
    """How many of cems-mindown-v3's units are found, with the same min_down_time_hours."""
    now = units.select(pl.col("plant_id_epa").cast(pl.Int64),
                       pl.col("emissions_unit_id_epa").cast(pl.String),
                       pl.col("min_down_time_hours").alias("_now"),
                       pl.lit(True).alias("_found"))
    j = v3.select(UNIT_COLS + [v3_col]).join(now, on=UNIT_COLS, how="left")
    found = j["_found"].fill_null(False)
    equal = found & j[v3_col].eq_missing(j["_now"])
    return {"rows": v3.height, "found": int(found.sum()), "equal": int(equal.sum()),
            "units_now": units.height}


def score(result):
    s = {}
    m = result.get("modes", {})
    if not all(k in m for k in MODES):
        return s
    n, f = m["none"], m["fill"]
    s["B0"] = (all(m[k]["run_min_equal"] >= 0.99 * m[k]["units"] for k in MODES)
               and n["isolated_runs"] == n.get("isolated_counted_by_fill_isolated"))
    v3 = result.get("v3", {})
    s["B1"] = all(k in v3 and v3[k]["equal"] >= 0.99 * v3[k]["rows"] for k in MODES)
    s["P0"] = n["isolated_runs"] > 0 and n["isolated_no_op_no_heat"] >= 0.99 * n[
        "isolated_runs"]
    s["P1"] = f["at2"] > 0 and f["at2_upflank"] >= 0.5 * f["at2"]
    s["P2"] = f["two_runs_hours"] > 0 and f["two_runs_no_op_hours"] >= 0.90 * f[
        "two_runs_hours"]
    s["P3"] = f["le2"] > 0 and f["cf_strict_le2"] <= 0.60 * f["le2"]
    s["P4"] = f["run_hours"] > 0 and 0.01 <= f["run_op_hours"] / f["run_hours"] <= 0.10
    s["P5"] = f["units_with_min"] > 0 and f["units_min_runs_op"] < 0.20 * f["units_with_min"]
    return s


def estimate(oc, lf, state, mode):
    """PUDL's two functions with fill_isolated's patch; also returns the frame the down call
    received, before the patch's own sort and fill."""
    original = fi.patch(oc, mode)
    patched = oc.calculate_min_up_or_down_times
    sink = []

    def calculate_min_up_or_down_times(output, cems_with_stable_bins, unit_cols, up_or_down):
        if up_or_down == "down":
            sink.append(cems_with_stable_bins.select(KEEP))
        return patched(output, cems_with_stable_bins, unit_cols, up_or_down)

    oc.calculate_min_up_or_down_times = calculate_min_up_or_down_times
    try:
        cems = oc.filter_cems_for_heat_rate_analysis(
            lf, final_year_quarter="%dq4" % mc.REPORT_YEAR, num_quarters=mc.NUM_QUARTERS,
            states=[state])
        out = oc.estimate_operational_characteristics_by_unit(
            cems, min_stable_consecutive_hours=mc.MIN_STABLE_HOURS)
    finally:
        fi.unpatch(oc, original)
    if len(sink) != 1:
        raise RuntimeError("expected one down call, saw %d" % len(sink))
    return out, sink[0]


def head(url):
    try:
        req = urllib.request.Request(url, headers=mc.UA, method="HEAD")
        with urllib.request.urlopen(req, timeout=60) as resp:
            h = dict(resp.headers)
        return {k: h.get(k) for k in ("Last-Modified", "ETag", "Content-Length")}
    except Exception as exc:
        return {"error": "%s: %s" % (type(exc).__name__, exc)}


def real_data(oc, out_dir, v3_path):
    pf, route, errors = mc.open_hourly()
    read_states = v2.fixed_read_states()
    res = {"states": mc.STATES, "report_year": mc.REPORT_YEAR, "route": route,
           "open_errors": errors, "read": {}}
    runs = {m: [] for m in MODES}
    units = {m: [] for m in MODES}
    isolated_counted = 0
    for state in mc.STATES:
        # one state at a time keeps memory to one state's three years
        frames, info = read_states(pf, [state], range(mc.REPORT_YEAR - 2, mc.REPORT_YEAR + 1))
        res["read"][state] = info
        if state not in frames:
            continue
        lf = frames.pop(state).lazy()
        for mode in MODES:
            out, frame = estimate(oc, lf, state, mode)
            if mode == "none":
                isolated_counted += fi.count_isolated_null_bins(frame, UNIT_COLS)
            else:
                frame = fi.fill_isolated_null_bins(frame, UNIT_COLS)
            r = run_table(frame)
            del frame
            runs[mode].append(r.with_columns(pl.lit(state).alias("state_run")))
            units[mode].append(unit_table(r, out).with_columns(pl.lit(state).alias("state_run")))
        del lf
    v3 = read_v3(v3_path)
    res["modes"], res["v3"] = {}, {}
    for mode in MODES:
        r = pl.concat(runs[mode], how="vertical_relaxed")
        u = pl.concat(units[mode], how="vertical_relaxed")
        res["modes"][mode] = summarize(u, r)
        res["v3"][mode] = compare_v3(u, v3, V3_COLS[mode])
        u.write_csv(os.path.join(out_dir, "units_%s.csv" % mode))
        if mode == "fill":
            at2 = u.filter(pl.col("min_down_time_hours") == 2).select(UNIT_COLS)
            r.join(at2, on=UNIT_COLS, how="semi").filter(pl.col("length") == 2).write_csv(
                os.path.join(out_dir, "two_hour_runs_fill.csv"))
    res["modes"]["none"]["isolated_counted_by_fill_isolated"] = isolated_counted
    return res


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--v3", default=V3_CSV)
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    result = {"tool": "blank_check.py " + VERSION, "mindown_check": mc.VERSION,
              "fill_isolated": fi.VERSION, "python": sys.version.split()[0],
              "polars": pl.__version__, "started": mc.now()}

    def save():
        result["scores"] = score(result)
        with open(os.path.join(a.out_dir, "blank_check.json"), "w", encoding="utf-8") as f:
            json.dump(result, f, indent=1, default=str)

    result["hourly_head"] = head(mc.HTTPS % (mc.S3_BUCKET, mc.NIGHTLY_HOURLY))
    mod_raw = mc.fetch(mc.RAW % (mc.SHA_MAIN, mc.MODULE_PATH))[0]
    test_raw = mc.fetch(mc.RAW % (mc.SHA_MAIN, mc.TEST_PATH))[0]
    result["pudl_files"] = {mc.MODULE_PATH: {"bytes": len(mod_raw), "md5": mc.md5(mod_raw)},
                            mc.TEST_PATH: {"bytes": len(test_raw), "md5": mc.md5(test_raw)}}
    root = tempfile.mkdtemp(prefix="mv2stub-")
    pkg, _ = stubs.build(root, mod_raw.decode("utf-8"), test_raw.decode("utf-8"))
    sys.path.insert(0, pkg)
    oc = importlib.import_module("pudl.analysis.operational_characteristics")
    save()
    try:
        result["real"] = real_data(oc, a.out_dir, a.v3)
        result["modes"], result["v3"] = result["real"].pop("modes"), result["real"].pop("v3")
    except Exception as exc:
        result["error"] = "%s: %s" % (type(exc).__name__, exc)
    result["finished"] = mc.now()
    save()
    print(json.dumps(result, indent=1, default=str))


if __name__ == "__main__":
    main()
