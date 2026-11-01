"""Pre-registered count of what sits on each side of the short down runs behind PUDL's
min_down_time_hours (issue #5514), which units have them, and where the null-load hours
with heat input go (pre-registration id cems-flank-1; plan: docs/cems-flank-plan.md in
munimtechnologies/eia860m-slip).

This script reruns cems-blank-1's pipeline (blank_check.py 0.1.0, unchanged and imported,
never edited; Colorado, Indiana and Wisconsin; report year 2025) with no patch and with the
fill patch, and:

  1. for every down run, records the operating_time_hours of the hour just before and just
     after it and puts each in a bucket: null, 0, below 0.5, 0.5 to below 0.999, full;
  2. sorts the units with a minimum down time by prime mover, from PUDL's EPA-EIA crosswalk
     and EIA-860 generators, and by EIA-860's time from cold shutdown to full load;
  3. keeps, from the frame PUDL's binning step returns (before PUDL drops units with one load
     factor or fewer), each unit's count of hours with no gross load and with heat input.

PUDL's code (MIT) and data (CC BY 4.0) are downloaded at run time and not stored here.

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.).
"""

import argparse
import importlib
import io
import json
import os
import sys
import tempfile

import polars as pl

import blank_check as bc
import fill_isolated as fi
import mindown_check as mc
import mindown_v2 as v2
import stubs

VERSION = "0.1.0"
UNIT_COLS = bc.UNIT_COLS
TIME_COL = bc.TIME_COL
BIN_COL = bc.BIN_COL
FULL_HOUR = 0.999
HALF_HOUR = 0.5
MODES = ("none", "fill")
BUCKETS = ("null", "zero", "lt_half", "half_to_full", "full")
NIGHTLY = "https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/%s.parquet"
XW_TABLE = "core_epa__assn_eia_epacamd"
GEN_TABLE = "core_eia860__scd_generators"
XW_COLS = ["report_year", "plant_id_epa", "emissions_unit_id_epa", "plant_id_eia",
           "generator_id"]
GEN_COLS = ["plant_id_eia", "generator_id", "report_date", "prime_mover_code",
            "time_cold_shutdown_full_load_code"]
INT_COLS = ("plant_id_epa", "plant_id_eia", "report_year")
STR_COLS = ("emissions_unit_id_epa", "generator_id", "prime_mover_code",
            "time_cold_shutdown_full_load_code")
CC_CODES = {"CT", "CA", "CS", "CC"}
CLASSES = ("GT", "CC", "ST", "IC", "other", "unmatched")
CT_BASED = ["GT", "CC"]
COLD_RANK = {"10M": 1, "1H": 2, "12H": 3, "OVER": 4}
START_CLASSES = ("fast", "slow", "unknown")
WORKING_COLS = UNIT_COLS + ["load_factor_nunique", "gross_load_mw", "operating_time_hours",
                            "heat_content_mmbtu"]
SEEN = {"two_at2_runs": 748, "at2_units": 178}


# ---- flanking hours ---------------------------------------------------------------------------

def op_bucket(v):
    """Bucket of one flanking hour's operating_time_hours."""
    if v is None or v != v:
        return "null"
    if v <= 0:
        return "zero"
    if v < HALF_HOUR:
        return "lt_half"
    if v < FULL_HOUR:
        return "half_to_full"
    return "full"


def bucket_counts(values):
    c = {b: 0 for b in BUCKETS}
    for v in values:
        c[op_bucket(v)] += 1
    n = sum(c.values())
    c["n"] = n
    c["partial"] = c["lt_half"] + c["half_to_full"]
    c["partial_share"] = round(c["partial"] / n, 4) if n else None
    return c


def flank_table(df, unit_cols=UNIT_COLS, time_col=TIME_COL):
    """One row per down run (consecutive null-bin hours of one unit, as PUDL counts them).

    before/after: the unit has an hour exactly 1 h before the run's first hour / after its
    last hour. op_before/op_after: that hour's operating_time_hours (null when there is no
    such hour, or when it reports none).
    """
    df = fi.sort_hours(df, unit_cols, time_col)
    same_prev = pl.all_horizontal([pl.col(c).eq(pl.col(c).shift(1)) for c in unit_cols])
    same_next = pl.all_horizontal([pl.col(c).eq(pl.col(c).shift(-1)) for c in unit_cols])
    hour_before = (pl.col(time_col) - pl.col(time_col).shift(1)).dt.total_seconds().eq(3600)
    hour_after = (pl.col(time_col).shift(-1) - pl.col(time_col)).dt.total_seconds().eq(3600)
    df = df.with_columns(
        (same_prev & hour_before).fill_null(False).alias("_before"),
        (same_next & hour_after).fill_null(False).alias("_after"),
    ).with_columns(
        pl.when(pl.col("_before")).then(pl.col("operating_time_hours").shift(1))
        .alias("_op_before"),
        pl.when(pl.col("_after")).then(pl.col("operating_time_hours").shift(-1))
        .alias("_op_after"),
    )
    runs = df.filter(pl.col(BIN_COL).is_null()).with_columns(
        bc.run_id_expr(unit_cols, time_col).alias("_run"))

    def first(c):
        return pl.col(c).sort_by(time_col).first()

    def last(c):
        return pl.col(c).sort_by(time_col).last()

    return runs.group_by(unit_cols + ["_run"]).agg(
        pl.len().cast(pl.Int64).alias("length"),
        first(time_col).alias("start"),
        first("_before").alias("before"),
        last("_after").alias("after"),
        first("_op_before").alias("op_before"),
        last("_op_after").alias("op_after"),
    ).drop("_run").sort(unit_cols + ["start"])


def describe(runs):
    b = runs.filter(pl.col("before"))["op_before"].to_list()
    a = runs.filter(pl.col("after"))["op_after"].to_list()
    return {"runs": runs.height, "before": bucket_counts(b), "after": bucket_counts(a),
            "both": bucket_counts(b + a)}


def k1_check(ft, rt, unit_cols=UNIT_COLS):
    """Gate K1: the flank table and blank_check's run table list the same runs, and a 'full'
    flank here is exactly blank_check's before_full / after_full."""
    keys = unit_cols + ["start"]
    j = ft.join(rt.select(keys + ["before_full", "after_full"]), on=keys, how="inner")
    full_b = pl.col("before") & (pl.col("op_before") >= FULL_HOUR).fill_null(False)
    full_a = pl.col("after") & (pl.col("op_after") >= FULL_HOUR).fill_null(False)
    bad = j.filter((full_b != pl.col("before_full")) | (full_a != pl.col("after_full")))
    return {"ft": ft.height, "rt": rt.height, "joined": j.height, "mismatch": bad.height}


def add_k1(total, part):
    for k, v in part.items():
        total[k] = total.get(k, 0) + v
    return total


# ---- the frame PUDL's binning step returns ------------------------------------------------------

def working_summary(w, unit_cols=UNIT_COLS):
    """Per unit: PUDL's load_factor_nunique and its hours with no gross load."""
    nl = pl.col("gross_load_mw").is_null()
    heat = pl.col("heat_content_mmbtu").fill_null(0.0)
    return w.group_by(unit_cols).agg(
        pl.col("load_factor_nunique").first().cast(pl.Int64).alias("nunique"),
        pl.len().cast(pl.Int64).alias("hours"),
        nl.sum().cast(pl.Int64).alias("null_load_hours"),
        (nl & (pl.col("heat_content_mmbtu") > 0).fill_null(False)).sum().cast(pl.Int64)
        .alias("null_load_heat_hours"),
        (nl & (pl.col("operating_time_hours") > 0).fill_null(False)).sum().cast(pl.Int64)
        .alias("null_load_op_hours"),
        heat.sum().alias("heat_mmbtu"),
        heat.filter(nl).sum().alias("null_load_heat_mmbtu"),
    ).sort(unit_cols)


def working_totals(ws):
    le1 = pl.col("nunique") <= 1
    return {
        "units": ws.height,
        "units_nunique_le1": ws.filter(le1).height,
        "units_nunique_le1_with_heat": ws.filter(le1 & (pl.col("heat_mmbtu") > 0)).height,
        "null_load_hours": int(ws["null_load_hours"].sum()),
        "null_load_heat_hours": int(ws["null_load_heat_hours"].sum()),
        "null_load_heat_hours_valid": int(ws.filter(~le1)["null_load_heat_hours"].sum()),
        "null_load_op_hours": int(ws["null_load_op_hours"].sum()),
        "heat_mmbtu": float(ws["heat_mmbtu"].sum()),
        "heat_mmbtu_nunique_le1": float(ws.filter(le1)["heat_mmbtu"].sum()),
        "null_load_heat_mmbtu": float(ws["null_load_heat_mmbtu"].sum()),
    }


def estimate_with_working(oc, lf, state, mode, sink):
    """blank_check.estimate, with PUDL's assign_groupwise_load_factor_bins wrapped so its
    returned frame (all units, before the load_factor_nunique > 1 filter) is kept."""
    original = oc.assign_groupwise_load_factor_bins

    def assign_groupwise_load_factor_bins(*args, **kwargs):
        res = original(*args, **kwargs)
        sink.append(res.select(WORKING_COLS))
        return res

    oc.assign_groupwise_load_factor_bins = assign_groupwise_load_factor_bins
    try:
        return bc.estimate(oc, lf, state, mode)
    finally:
        oc.assign_groupwise_load_factor_bins = original


# ---- unit types ---------------------------------------------------------------------------------

def unit_class(codes):
    """Prime-mover class of a CEMS unit from its generators' EIA-860 prime mover codes."""
    c = {x for x in codes if x}
    if not c:
        return "unmatched"
    if c & CC_CODES:
        return "CC"
    for one in ("GT", "ST", "IC"):
        if c == {one}:
            return one
    return "other"


def start_class(codes):
    """fast: every known code is 10M or 1H; slow: any known code is 12H or OVER."""
    known = [COLD_RANK[x] for x in codes if x in COLD_RANK]
    if not known:
        return "unknown"
    return "fast" if max(known) <= 2 else "slow"


def clean(df):
    casts = []
    for c, dt in df.schema.items():
        if isinstance(dt, (pl.Categorical, pl.Enum)) or dt == pl.Categorical:
            casts.append(pl.col(c).cast(pl.String))
    if casts:
        df = df.with_columns(casts)
    return df.with_columns([pl.col(c).cast(pl.Int64) for c in INT_COLS if c in df.columns]
                           + [pl.col(c).cast(pl.String) for c in STR_COLS if c in df.columns])


def load_table(name, cols):
    raw, headers = mc.fetch(NIGHTLY % name, timeout=600)
    df = clean(pl.read_parquet(io.BytesIO(raw), columns=cols))
    return df, {"bytes": len(raw), "md5": mc.md5(raw), "rows": df.height,
                "last_modified": headers.get("Last-Modified")}


def choose_year(xw, report_year):
    years = [y for y in xw["report_year"].drop_nulls().unique().to_list() if y <= report_year]
    return max(years) if years else None


def unit_types(xw, gens, year, unit_cols=UNIT_COLS):
    x = (xw.filter((pl.col("report_year") == year) & pl.col("emissions_unit_id_epa").is_not_null()
                   & pl.col("generator_id").is_not_null())
         .select(unit_cols + ["plant_id_eia", "generator_id"]).unique())
    g = (gens.filter(pl.col("report_date").dt.year() <= year)
         .group_by(["plant_id_eia", "generator_id"])
         .agg(pl.col("prime_mover_code").sort_by("report_date").drop_nulls().last(),
              pl.col("time_cold_shutdown_full_load_code").sort_by("report_date").drop_nulls()
              .last()))
    per = (x.join(g, on=["plant_id_eia", "generator_id"], how="left")
           .group_by(unit_cols)
           .agg(pl.col("prime_mover_code"), pl.col("time_cold_shutdown_full_load_code"),
                pl.col("generator_id")))
    rows = []
    for r in per.to_dicts():
        pm, cold = r["prime_mover_code"], r["time_cold_shutdown_full_load_code"]
        rows.append({"plant_id_epa": r["plant_id_epa"],
                     "emissions_unit_id_epa": r["emissions_unit_id_epa"],
                     "unit_class": unit_class(pm), "start_class": start_class(cold),
                     "prime_movers": ";".join(sorted({c for c in pm if c})),
                     "cold_codes": ";".join(sorted({c for c in cold if c})),
                     "generators": len(r["generator_id"])})
    schema = {"plant_id_epa": pl.Int64, "emissions_unit_id_epa": pl.String,
              "unit_class": pl.String, "start_class": pl.String, "prime_movers": pl.String,
              "cold_codes": pl.String, "generators": pl.Int64}
    return pl.DataFrame(rows, schema=schema).sort(unit_cols)


def attach_types(units, types, unit_cols=UNIT_COLS):
    u = units.with_columns(pl.col("plant_id_epa").cast(pl.Int64),
                           pl.col("emissions_unit_id_epa").cast(pl.String))
    return u.join(types, on=unit_cols, how="left").with_columns(
        pl.col("unit_class").fill_null("unmatched"), pl.col("start_class").fill_null("unknown"))


def type_summary(units):
    """units: one row per unit with min_down_time_hours (fill patch), unit_class, start_class."""
    m = units.filter(pl.col("min_down_time_hours").is_not_null())
    matched = m.filter(pl.col("unit_class") != "unmatched")
    ct = pl.col("unit_class").is_in(CT_BASED)
    at2 = pl.col("min_down_time_hours") == 2
    le2 = pl.col("min_down_time_hours") <= 2
    ge3 = pl.col("min_down_time_hours") >= 3
    st = matched.filter(pl.col("unit_class") == "ST")
    slow = m.filter(pl.col("start_class") == "slow")

    def group(g):
        return {"units": g.height, "at2": g.filter(at2).height, "le2": g.filter(le2).height,
                "ge3": g.filter(ge3).height, "median": g["min_down_time_hours"].median()}

    return {
        "units_with_min": m.height,
        "unmatched": m.height - matched.height,
        "at2_units": matched.filter(at2).height,
        "ct_at2": matched.filter(at2 & ct).height,
        "ge3_units": matched.filter(ge3).height,
        "ct_ge3": matched.filter(ge3 & ct).height,
        "st_units": st.height,
        "st_at2": st.filter(at2).height,
        "slow_units": slow.height,
        "slow_le2": slow.filter(le2).height,
        "by_class": {c: group(m.filter(pl.col("unit_class") == c)) for c in CLASSES},
        "by_start": {c: group(m.filter(pl.col("start_class") == c)) for c in START_CLASSES},
    }


# ---- scoring ------------------------------------------------------------------------------------

def score(result):
    s = {}
    k1 = result.get("k1", {})
    if all(m in k1 for m in MODES):
        s["K1"] = all(k1[m]["ft"] == k1[m]["rt"] == k1[m]["joined"] and k1[m]["mismatch"] == 0
                      for m in MODES)
    c = result.get("counts")
    if c:
        s["K2"] = (abs(c["two_at2_runs"] - SEEN["two_at2_runs"]) <= 0.02 * SEEN["two_at2_runs"]
                   and abs(c["at2_units"] - SEEN["at2_units"]) <= 0.02 * SEEN["at2_units"])
    w = result.get("working")
    if w:
        s["K3"] = w["null_load_heat_hours_valid"] == 0
        s["D1"] = w["null_load_heat_hours"] >= 10000
        s["D2"] = w["units_nunique_le1_with_heat"] >= 5
    f = result.get("flank")
    if f:
        a, b, lg = f["two_at2"]["both"], f["iso1"]["both"], f["long10"]["both"]
        s["F1"] = a["n"] > 0 and a["partial"] >= 0.70 * a["n"]
        s["F2"] = (a["n"] > 0 and b["n"] > 0 and b["partial"] >= 0.70 * b["n"]
                   and abs(b["partial"] / b["n"] - a["partial"] / a["n"]) <= 0.15)
        s["F3"] = lg["n"] > 0 and lg["partial"] >= 0.70 * lg["n"]
    t = result.get("types")
    if t and t.get("units_with_min"):
        s["U0"] = t["units_with_min"] - t["unmatched"] >= 0.80 * t["units_with_min"]
        if s["U0"]:
            if t["at2_units"] and t["ge3_units"]:
                s["U1"] = t["ct_at2"] / t["at2_units"] >= t["ct_ge3"] / t["ge3_units"] + 0.10
            if t["st_units"] >= 5:
                s["U2"] = t["st_at2"] >= 0.40 * t["st_units"]
            if t["slow_units"] >= 5:
                s["U3"] = t["slow_le2"] >= 0.40 * t["slow_units"]
    return s


# ---- the run ------------------------------------------------------------------------------------

def subsets(runs, units):
    """runs: dict mode -> run table; units: dict mode -> unit output with min_down_time_hours."""
    at2 = units["fill"].filter(pl.col("min_down_time_hours") == 2).select(UNIT_COLS)
    f, n = runs["fill"], runs["none"]
    two_at2 = f.join(at2, on=UNIT_COLS, how="semi").filter(pl.col("length") == 2)
    return {
        "two_at2": two_at2,
        "two_all": f.filter(pl.col("length") == 2),
        "iso1": n.filter((pl.col("length") == 1) & pl.col("before") & pl.col("after")),
        "mid3_9": f.filter((pl.col("length") >= 3) & (pl.col("length") <= 9)),
        "long10": f.filter(pl.col("length") >= 10),
    }, at2.height


def real_data(oc, out_dir):
    pf, route, errors = mc.open_hourly()
    read_states = v2.fixed_read_states()
    res = {"states": mc.STATES, "report_year": mc.REPORT_YEAR, "route": route,
           "open_errors": errors, "read": {}}
    runs = {m: [] for m in MODES}
    units = {m: [] for m in MODES}
    working = []
    k1 = {m: {} for m in MODES}
    for state in mc.STATES:
        # one state at a time keeps memory to one state's three years
        frames, info = read_states(pf, [state], range(mc.REPORT_YEAR - 2, mc.REPORT_YEAR + 1))
        res["read"][state] = info
        if state not in frames:
            continue
        lf = frames.pop(state).lazy()
        for mode in MODES:
            if mode == "none":
                sink = []
                out, frame = estimate_with_working(oc, lf, state, mode, sink)
                if len(sink) != 1:
                    raise RuntimeError("expected one binning call, saw %d" % len(sink))
                working.append(working_summary(sink.pop()).with_columns(
                    pl.lit(state).alias("state_run")))
            else:
                out, frame = bc.estimate(oc, lf, state, mode)
                frame = fi.fill_isolated_null_bins(frame, UNIT_COLS)
            ft = flank_table(frame)
            add_k1(k1[mode], k1_check(ft, bc.run_table(frame)))
            del frame
            runs[mode].append(ft.with_columns(pl.lit(state).alias("state_run")))
            units[mode].append(out.select(UNIT_COLS + ["min_down_time_hours"]).with_columns(
                pl.lit(state).alias("state_run")))
        del lf
    res["k1"] = k1
    r = {m: pl.concat(runs[m], how="vertical_relaxed") for m in MODES}
    u = {m: pl.concat(units[m], how="vertical_relaxed") for m in MODES}
    subs, at2_units = subsets(r, u)
    res["counts"] = {"two_at2_runs": subs["two_at2"].height, "at2_units": at2_units,
                     "units": u["fill"].height,
                     "units_with_min": u["fill"]["min_down_time_hours"].drop_nulls().len(),
                     "runs_none": r["none"].height, "runs_fill": r["fill"].height}
    res["flank"] = {k: describe(v) for k, v in subs.items()}
    r["fill"].write_csv(os.path.join(out_dir, "runs_fill.csv"))
    ws = pl.concat(working, how="vertical_relaxed")
    res["working"] = working_totals(ws)
    ws.write_csv(os.path.join(out_dir, "working_units.csv"))
    return res, u["fill"], subs["two_at2"]


def types_part(result, units_fill, two_at2, out_dir):
    result["downloads"] = {}
    xw, result["downloads"][XW_TABLE] = load_table(XW_TABLE, XW_COLS)
    gens, result["downloads"][GEN_TABLE] = load_table(GEN_TABLE, GEN_COLS)
    year = choose_year(xw, mc.REPORT_YEAR)
    result["crosswalk_year"] = year
    types = unit_types(xw, gens, year)
    u = attach_types(units_fill, types)
    u.write_csv(os.path.join(out_dir, "units_types.csv"))
    result["types"] = type_summary(u)
    result["cold_codes_raw"] = {str(k): int(v) for k, v in gens.filter(
        pl.col("report_date").dt.year() == year)["time_cold_shutdown_full_load_code"]
        .value_counts().iter_rows()}
    t2 = attach_types(two_at2, types)
    result["flank_two_at2_by_class"] = {
        c: describe(t2.filter(pl.col("unit_class") == c))["both"] for c in CLASSES}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    result = {"tool": "flank_check.py " + VERSION, "blank_check": bc.VERSION,
              "mindown_check": mc.VERSION, "fill_isolated": fi.VERSION,
              "python": sys.version.split()[0], "polars": pl.__version__,
              "started": mc.now()}

    def save():
        result["scores"] = score(result)
        with open(os.path.join(a.out_dir, "flank_check.json"), "w", encoding="utf-8") as f:
            json.dump(result, f, indent=1, default=str)

    result["hourly_head"] = bc.head(mc.HTTPS % (mc.S3_BUCKET, mc.NIGHTLY_HOURLY))
    mod_raw = mc.fetch(mc.RAW % (mc.SHA_MAIN, mc.MODULE_PATH))[0]
    test_raw = mc.fetch(mc.RAW % (mc.SHA_MAIN, mc.TEST_PATH))[0]
    result["pudl_files"] = {mc.MODULE_PATH: {"bytes": len(mod_raw), "md5": mc.md5(mod_raw)},
                            mc.TEST_PATH: {"bytes": len(test_raw), "md5": mc.md5(test_raw)}}
    root = tempfile.mkdtemp(prefix="mv2stub-")
    pkg, _ = stubs.build(root, mod_raw.decode("utf-8"), test_raw.decode("utf-8"))
    sys.path.insert(0, pkg)
    oc = importlib.import_module("pudl.analysis.operational_characteristics")
    save()
    units_fill = two_at2 = None
    try:
        real, units_fill, two_at2 = real_data(oc, a.out_dir)
        for k in ("k1", "counts", "flank", "working"):
            result[k] = real.pop(k)
        result["real"] = real
    except Exception as exc:
        result["error"] = "%s: %s" % (type(exc).__name__, exc)
    save()
    if units_fill is not None:
        try:
            types_part(result, units_fill, two_at2, a.out_dir)
        except Exception as exc:
            result["types_error"] = "%s: %s" % (type(exc).__name__, exc)
    result["finished"] = mc.now()
    save()
    print(json.dumps(result, indent=1, default=str))


if __name__ == "__main__":
    main()
