"""Pre-registered check of a fix for PUDL issue #5514 (min_down_time_hours collapses to 1 hour
because an isolated hour with no reported load counts as a "down" run).

Plan with every bar: docs/cems-mindown-plan.md in munimtechnologies/eia860m-slip
(pre-registration id cems-mindown-1). This script:

  1. waits until the plan is live (no data is read before that);
  2. downloads PUDL's src/pudl/analysis/operational_characteristics.py and
     tests/unit/analysis/operational_characteristics_test.py at main (4d3366b), unchanged;
  3. runs PUDL's unit tests with no patch, the sort-only patch and the fill patch (T1, T2);
  4. runs five hand-made cases through PUDL's calculate_min_up_or_down_times (C1-C5) and
     300 random shuffled frames against reference.py (T4);
  5. reads PUDL's nightly out_epacems__yearly_operational_characteristics (N1);
  6. reads the nightly core_epacems__hourly_emissions rows of three states for 2023-2025 and
     runs PUDL's own estimate_operational_characteristics_by_unit on them for report year 2025
     with each patch, compares the unpatched run with the nightly table (gate R0) and the
     patched runs with the unpatched run (F1-F4).

PUDL's code (MIT) and data (CC BY 4.0) are downloaded at run time and not stored here.

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.).
"""

import argparse
import hashlib
import importlib
import io
import json
import os
import random
import subprocess
import sys
import tempfile
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

import polars as pl

import fill_isolated as fi
import reference as ref
import stubs

VERSION = "0.1.0"
SHA_MAIN = "4d3366b30d05a4c1c13cd8e88ba9b7b2f9ea6db2"
RAW = "https://raw.githubusercontent.com/catalyst-cooperative/pudl/%s/%s"
MODULE_PATH = "src/pudl/analysis/operational_characteristics.py"
TEST_PATH = "tests/unit/analysis/operational_characteristics_test.py"
S3_BUCKET = "pudl.catalyst.coop"
NIGHTLY_OUT = "nightly/out_epacems__yearly_operational_characteristics.parquet"
NIGHTLY_HOURLY = "nightly/core_epacems__hourly_emissions.parquet"
HTTPS = "https://s3.us-west-2.amazonaws.com/%s/%s"
STATES = ["CO", "IN", "WI"]
REPORT_YEAR = 2025
NUM_QUARTERS = 12
MIN_STABLE_HOURS = 8
HOURLY_COLS = ["plant_id_eia", "plant_id_epa", "emissions_unit_id_epa",
               "operating_datetime_utc", "state", "operating_time_hours", "gross_load_mw",
               "heat_content_mmbtu"]
UNIT_COLS = ["plant_id_epa", "emissions_unit_id_epa"]
MAX_READ_BYTES = 2_500_000_000
RANDOM_FRAMES = 300
SEED = 20261030
UA = {"User-Agent": "mv2-cems-mindown-check/0.1 (MV2, Munim, Inc.; mv2@munimtech.com)"}
BIN = pl.Struct({"left": pl.Float64, "right": pl.Float64})
BASE = datetime(2024, 1, 1)


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def fetch(url, timeout=120):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read(), dict(resp.headers)


def wait_for(url, token, minutes):
    deadline = time.time() + minutes * 60
    polls = 0
    while True:
        polls += 1
        try:
            if token in fetch(url)[0].decode("utf-8", "replace"):
                return True, polls, now()
        except Exception:
            pass
        if time.time() > deadline:
            return False, polls, now()
        time.sleep(60)


def md5(raw):
    return hashlib.md5(raw).hexdigest()


# ---- PUDL's unit tests ------------------------------------------------------------------------

def run_pudl_tests(pkg, tests, mode, work_dir):
    xml = os.path.join(tempfile.gettempdir(), "pudl-tests-%s.xml" % mode)
    env = dict(os.environ, MV2_PATCH=mode,
               PYTHONPATH=os.pathsep.join([pkg, work_dir, os.environ.get("PYTHONPATH", "")]))
    proc = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                           "--junitxml=" + xml, tests], env=env, capture_output=True,
                          text=True, timeout=900)
    res = {"mode": mode, "returncode": proc.returncode,
           "stdout_tail": proc.stdout[-3000:], "stderr_tail": proc.stderr[-2000:]}
    try:
        root = ET.parse(xml).getroot()
        suite = root if root.tag == "testsuite" else root.find("testsuite")
        cases = suite.findall(".//testcase")
        failed = []
        for case in cases:
            for kind in ("failure", "error"):
                node = case.find(kind)
                if node is not None:
                    failed.append({"name": case.get("name"), "kind": kind,
                                   "message": (node.get("message") or "")[:400]})
        res.update({"collected": len(cases), "failed": len(failed), "failures": failed,
                    "passed": len(cases) - len(failed)
                    - len([c for c in cases if c.find("skipped") is not None]),
                    "suite_errors": int(suite.get("errors", 0))})
    except Exception as exc:
        res["xml_error"] = "%s: %s" % (type(exc).__name__, exc)
    text = res["stdout_tail"] + res["stderr_tail"]
    res["name_errors"] = text.count("NameError")
    res["import_errors"] = text.count("ImportError") + text.count("ModuleNotFoundError")
    return res


# ---- hand-made cases and random frames -----------------------------------------------------------

def cems_frame(rows):
    """rows of (plant, unit, hour offset, bin dict or None, min stable bin dict or None)."""
    return pl.DataFrame(
        {"plant_id_epa": [r[0] for r in rows],
         "emissions_unit_id_epa": [r[1] for r in rows],
         "operating_datetime_utc": [BASE + timedelta(hours=r[2]) for r in rows],
         "load_factor_bin": [r[3] for r in rows],
         "min_stable_bin": [r[4] for r in rows]},
        schema={"plant_id_epa": pl.Int64, "emissions_unit_id_epa": pl.String,
                "operating_datetime_utc": pl.Datetime("us"), "load_factor_bin": BIN,
                "min_stable_bin": BIN})


def empty_output(units):
    return pl.DataFrame(
        {"plant_id_epa": [u[0] for u in units], "emissions_unit_id_epa": [u[1] for u in units],
         "min_up_time_hours": [None] * len(units), "min_down_time_hours": [None] * len(units)},
        schema={"plant_id_epa": pl.Int64, "emissions_unit_id_epa": pl.String,
                "min_up_time_hours": pl.Float64, "min_down_time_hours": pl.Float64})


def run_calc(oc, mode, cems, units):
    original = fi.patch(oc, mode)
    try:
        out = empty_output(units)
        for kind in ("up", "down"):
            out = oc.calculate_min_up_or_down_times(out, cems, UNIT_COLS, kind)
    finally:
        fi.unpatch(oc, original)
    return {(r["plant_id_epa"], r["emissions_unit_id_epa"]):
            (r["min_up_time_hours"], r["min_down_time_hours"]) for r in out.to_dicts()}


def as_float(pair):
    return tuple(None if v is None else float(v) for v in pair)


U = {"left": 0.5, "right": 0.6}
LO = {"left": 0.1, "right": 0.2}
MS = {"left": 0.3, "right": 0.4}
CASES = {
    # name: (bins, hours, expected (min_up, min_down) with no patch, with the fill patch)
    "C1_isolated_null": ([U, U, U, None, U, U, U, U], None, (3, 1), (8, None)),
    "C2_two_null_hours": ([U, U, None, None, U, U, U, U], None, (2, 2), (2, 2)),
    "C3_null_after_gap": ([U, U, U, None, U, U, U, U], [0, 1, 2, 4, 5, 6, 7, 8], (3, 1), (3, 1)),
    "C4_null_first_hour": ([None, U, U, U, U, U, U, U], None, (7, 1), (7, 1)),
    "C5_low_neighbours": ([U, LO, None, LO, U, U, U, U], None, (1, 1), (1, None)),
}


def check_cases(oc):
    res = {}
    for name, (bins, hours, plain, filled) in CASES.items():
        hours = list(range(len(bins))) if hours is None else hours
        cems = cems_frame([(1, "A", h, b, MS) for h, b in zip(hours, bins)])
        got_none = run_calc(oc, "none", cems, [(1, "A")])[(1, "A")]
        got_fill = run_calc(oc, "fill", cems, [(1, "A")])[(1, "A")]
        res[name] = {"none": got_none, "fill": got_fill,
                     "held": (as_float(got_none) == as_float(plain)
                              and as_float(got_fill) == as_float(filled))}
    return res


def random_rows(rng):
    bins = [None, {"left": 0.1, "right": 0.2}, {"left": 0.3, "right": 0.4},
            {"left": 0.5, "right": 0.6}, {"left": 0.7, "right": 0.8}]
    rows = []
    for u in range(rng.randint(1, 3)):
        plant, unit = rng.randint(1, 2), "U%d" % u
        ms = None if rng.random() < 0.15 else rng.choice(bins[1:])
        h = 0
        for _ in range(rng.randint(10, 60)):
            h += 2 if rng.random() < 0.05 else 1
            b = None if rng.random() < 0.2 else rng.choice(bins[1:])
            rows.append((plant, unit, h, b, ms))
    # several units may share a plant id; keep (plant, unit) pairs distinct
    seen, out = set(), []
    for r in rows:
        if (r[0], r[1], r[2]) not in seen:
            seen.add((r[0], r[1], r[2]))
            out.append(r)
    rng.shuffle(out)
    return out


def check_random(oc):
    rng = random.Random(SEED)
    res = {"frames": 0, "rows": 0, "isolated_null_bins": 0, "fill_matches_ref": 0,
           "sort_matches_plain_ref": 0, "none_on_sorted_matches_plain_ref": 0,
           "failures": []}
    for i in range(RANDOM_FRAMES):
        rows = random_rows(rng)
        units = sorted({(r[0], r[1]) for r in rows})
        cems = cems_frame(rows)
        plain = ref.min_up_down([((r[0], r[1]), BASE + timedelta(hours=r[2]),
                                  None if r[3] is None else (r[3]["left"], r[3]["right"]),
                                  None if r[4] is None else (r[4]["left"], r[4]["right"]))
                                 for r in rows], fill=False)
        filled = ref.min_up_down([((r[0], r[1]), BASE + timedelta(hours=r[2]),
                                   None if r[3] is None else (r[3]["left"], r[3]["right"]),
                                   None if r[4] is None else (r[4]["left"], r[4]["right"]))
                                  for r in rows], fill=True)
        got = {
            "fill": run_calc(oc, "fill", cems, units),
            "sort": run_calc(oc, "sort", cems, units),
            "none_sorted": run_calc(oc, "none", fi.sort_hours(cems, UNIT_COLS), units),
        }
        res["frames"] += 1
        res["rows"] += len(rows)
        res["isolated_null_bins"] += fi.count_isolated_null_bins(cems, UNIT_COLS)
        for key, want, label in (("fill", filled, "fill_matches_ref"),
                                 ("sort", plain, "sort_matches_plain_ref"),
                                 ("none_sorted", plain, "none_on_sorted_matches_plain_ref")):
            ok = all(as_float(got[key][u]) == as_float(want[u]) for u in units)
            res[label] += int(ok)
            if not ok and len(res["failures"]) < 5:
                res["failures"].append({"frame": i, "mode": key,
                                        "got": {str(u): got[key][u] for u in units},
                                        "want": {str(u): want[u] for u in units}})
    return res


# ---- nightly tables --------------------------------------------------------------------------

def nightly_out():
    raw, headers = fetch(HTTPS % (S3_BUCKET, NIGHTLY_OUT), timeout=300)
    df = pl.read_parquet(io.BytesIO(raw))
    info = {"bytes": len(raw), "md5": md5(raw), "last_modified": headers.get("Last-Modified"),
            "columns": df.columns, "rows": df.height}
    years = {}
    for (y,), g in df.group_by(["report_year"]):
        n = g.height
        one = g.filter(pl.col("min_down_time_hours") == 1).height
        up_one = g.filter(pl.col("min_up_time_hours") == 1).height
        years[int(y)] = {"units": n, "min_down_eq_1": one, "min_up_eq_1": up_one,
                         "min_down_null": g["min_down_time_hours"].null_count(),
                         "share_min_down_eq_1": round(one / n, 4) if n else None}
    info["by_report_year"] = {k: years[k] for k in sorted(years)}
    return df, info


def open_hourly():
    import pyarrow.parquet as pq
    errors = []
    try:
        import pyarrow.fs as pafs
        fs = pafs.S3FileSystem(anonymous=True, region="us-west-2")
        return pq.ParquetFile(fs.open_input_file(S3_BUCKET + "/" + NIGHTLY_HOURLY)), "s3", errors
    except Exception as exc:
        errors.append("s3: %s: %s" % (type(exc).__name__, exc))
    import fsspec
    f = fsspec.filesystem("https").open(HTTPS % (S3_BUCKET, NIGHTLY_HOURLY), block_size=2**24)
    return pq.ParquetFile(f), "https", errors


def stat_range(rg, idx, col):
    j = idx.get(col)
    if j is None:
        return None
    s = rg.column(j).statistics
    if s is None or not s.has_min_max:
        return None
    lo, hi = s.min, s.max
    if isinstance(lo, bytes):
        lo, hi = lo.decode(), hi.decode()
    return lo, hi


def year_of(v):
    return v.year if hasattr(v, "year") else None


def read_states(pf, states, years):
    md = pf.metadata
    names = [md.schema.column(j).path_in_schema for j in range(md.num_columns)]
    idx = {n: j for j, n in enumerate(names)}
    cols = [c for c in HOURLY_COLS + ["year"] if c in idx]
    info = {"row_groups": md.num_row_groups, "rows": md.num_rows, "columns": names,
            "missing_columns": [c for c in HOURLY_COLS if c not in idx]}
    keep, nbytes = [], 0
    for i in range(md.num_row_groups):
        rg = md.row_group(i)
        yr = stat_range(rg, idx, "year")
        if yr is None:
            t = stat_range(rg, idx, "operating_datetime_utc")
            yr = (year_of(t[0]), year_of(t[1])) if t else None
            if yr and None in yr:
                yr = None
        if yr is not None and (yr[1] < min(years) or yr[0] > max(years)):
            continue
        st = stat_range(rg, idx, "state")
        if st is not None and not any(st[0] <= s <= st[1] for s in states):
            continue
        keep.append(i)
        nbytes += sum(rg.column(idx[c]).total_compressed_size for c in cols)
    info.update({"row_groups_read": len(keep), "compressed_bytes_read": nbytes})
    if info["missing_columns"]:
        raise RuntimeError("missing columns %s" % info["missing_columns"])
    if nbytes > MAX_READ_BYTES:
        raise RuntimeError("would read %d bytes (cap %d)" % (nbytes, MAX_READ_BYTES))
    parts = {s: [] for s in states}
    for i in keep:
        df = pl.from_arrow(pf.read_row_group(i, columns=cols))
        for c, dt in df.schema.items():
            if dt == pl.Categorical or isinstance(dt, pl.Enum):
                df = df.with_columns(pl.col(c).cast(pl.String))
        df = df.filter(pl.col("state").is_in(states)
                       & pl.col("operating_datetime_utc").dt.year().is_in(list(years)))
        if "year" in df.columns:
            df = df.drop("year")
        for s in states:
            sub = df.filter(pl.col("state") == s)
            if sub.height:
                parts[s].append(sub)
    frames = {s: pl.concat(p) for s, p in parts.items() if p}
    info["state_rows"] = {s: f.height for s, f in frames.items()}
    info["time_dtype"] = str(next(iter(frames.values()))["operating_datetime_utc"].dtype) \
        if frames else None
    return frames, info


def estimate(oc, lf, state, mode):
    probe = []
    original = fi.patch(oc, mode, probe)
    try:
        cems = oc.filter_cems_for_heat_rate_analysis(
            lf, final_year_quarter="%dq4" % REPORT_YEAR, num_quarters=NUM_QUARTERS,
            states=[state])
        out = oc.estimate_operational_characteristics_by_unit(
            cems, min_stable_consecutive_hours=MIN_STABLE_HOURS)
    finally:
        fi.unpatch(oc, original)
    return out, probe


def same(a, b):
    if a is None or b is None:
        return a is None and b is None
    if isinstance(a, float) and isinstance(b, float):
        return a == b or (a != a and b != b)
    return a == b


def compare(a, b, keys, cols):
    """Per-column count of keyed rows of a equal in b; rows of a missing from b."""
    bmap = {tuple(r[k] for k in keys): r for r in b.to_dicts()}
    found, equal, diffs = 0, {c: 0 for c in cols}, []
    for r in a.to_dicts():
        other = bmap.get(tuple(r[k] for k in keys))
        if other is None:
            continue
        found += 1
        for c in cols:
            if same(r.get(c), other.get(c)):
                equal[c] += 1
            elif len(diffs) < 10:
                diffs.append({"unit": [r[k] for k in keys], "column": c,
                              "a": r.get(c), "b": other.get(c)})
    return {"rows": a.height, "found": found, "equal": equal, "examples": diffs}


def real_data(oc, nightly_df, out_dir):
    res = {"states": STATES, "report_year": REPORT_YEAR}
    pf, route, errors = open_hourly()
    res["route"], res["open_errors"] = route, errors
    nightly_y = nightly_df.filter(pl.col("report_year") == REPORT_YEAR)
    keys = [k for k in ("plant_id_epa", "emissions_unit_id_epa") if k in nightly_df.columns]
    outs = {m: [] for m in ("none", "sort", "fill")}
    res["per_state"], res["read"] = {}, {}
    for state in STATES:
        # one state at a time keeps memory to one state's three years
        frames, info = read_states(pf, [state], range(REPORT_YEAR - 2, REPORT_YEAR + 1))
        res["read"][state] = info
        if state not in frames:
            res["per_state"][state] = {"error": "no rows"}
            continue
        lf = frames.pop(state).lazy()
        st = {}
        for mode in ("none", "sort", "fill"):
            t0 = time.time()
            out, probe = estimate(oc, lf, state, mode)
            st[mode] = {"units": out.height, "seconds": round(time.time() - t0, 2),
                        "calls": len(probe),
                        "calls_sorted": sum(p["sorted"] for p in probe),
                        "isolated_null_bins_down_call": [p["isolated_null_bins"] for p in probe
                                                         if p["up_or_down"] == "down"]}
            outs[mode].append(out.with_columns(pl.lit(state).alias("state_run")))
        res["per_state"][state] = st
        del lf
    runs = {m: pl.concat(v, how="vertical_relaxed") for m, v in outs.items() if v}
    cols = [c for c in runs["none"].columns if c != "state_run"]
    common = [c for c in cols if c in nightly_y.columns and c not in keys]
    res["R0"] = compare(runs["none"], nightly_y, keys, common)
    res["R0_keys"] = keys
    res["fill_vs_none"] = compare(runs["fill"], runs["none"], UNIT_COLS,
                                  [c for c in cols if c not in UNIT_COLS])
    res["sort_vs_none"] = compare(runs["sort"], runs["none"], UNIT_COLS,
                                  [c for c in cols if c not in UNIT_COLS])
    for m, df in runs.items():
        res["counts_" + m] = {
            "units": df.height,
            "min_down_eq_1": df.filter(pl.col("min_down_time_hours") == 1).height,
            "min_up_eq_1": df.filter(pl.col("min_up_time_hours") == 1).height,
            "min_down_null": df["min_down_time_hours"].null_count(),
            "min_down_median": df["min_down_time_hours"].median(),
        }
    joined = runs["none"].select(UNIT_COLS + ["state_run", "min_down_time_hours",
                                              "min_up_time_hours"]).join(
        runs["fill"].select(UNIT_COLS + ["min_down_time_hours", "min_up_time_hours"]),
        on=UNIT_COLS, how="left", suffix="_fill")
    joined.write_csv(os.path.join(out_dir, "units_none_vs_fill.csv"))
    return res


def score(result):
    s = {}
    t = result.get("pudl_tests", {})
    s["G1"] = all(t.get(m, {}).get("collected", 0) == 29 and t[m].get("name_errors", 1) == 0
                  and t[m].get("import_errors", 1) == 0 for m in ("none", "fill"))
    s["T1"] = t.get("none", {}).get("failed") == 0 and t.get("none", {}).get("collected") == 29
    s["T2"] = t.get("fill", {}).get("failed") == 0 and t.get("fill", {}).get("collected") == 29
    s["T3"] = all(c["held"] for c in result.get("cases", {}).values()) and bool(
        result.get("cases"))
    r = result.get("random", {})
    s["T4"] = bool(r) and r["fill_matches_ref"] == r["frames"] == RANDOM_FRAMES \
        and r["sort_matches_plain_ref"] == RANDOM_FRAMES
    n = result.get("nightly_out", {}).get("by_report_year", {}).get(REPORT_YEAR)
    s["N1"] = bool(n) and n["share_min_down_eq_1"] >= 0.5
    real = result.get("real", {})
    if "R0" in real:
        r0 = real["R0"]
        s["R0"] = (r0["rows"] > 0 and r0["found"] >= 0.95 * r0["rows"]
                   and all(r0["equal"].get(c, 0) >= 0.95 * r0["found"]
                           for c in ("min_down_time_hours", "min_up_time_hours")))
        none, fill = real["counts_none"], real["counts_fill"]
        s["F1_applicable"] = none["min_down_eq_1"] >= 20
        s["F1"] = none["min_down_eq_1"] > 0 and fill["min_down_eq_1"] <= 0.25 * none[
            "min_down_eq_1"]
        s["F2"] = abs(fill["min_up_eq_1"] - none["min_up_eq_1"]) <= 0.10 * none["min_up_eq_1"]
        fv = real["fill_vs_none"]
        s["F3"] = fv["found"] == fv["rows"] and all(
            v == fv["found"] for c, v in fv["equal"].items()
            if c not in ("min_down_time_hours", "min_up_time_hours"))
        sv = real["sort_vs_none"]
        s["F4"] = sv["found"] == sv["rows"] and all(v == sv["found"]
                                                    for v in sv["equal"].values())
    return s


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--wait-for", default="")
    ap.add_argument("--token", default="")
    ap.add_argument("--minutes", type=float, default=150)
    ap.add_argument("--skip-real", action="store_true")
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    work_dir = os.path.dirname(os.path.abspath(__file__))
    result = {"tool": "mindown_check.py " + VERSION, "fill_isolated": fi.VERSION,
              "python": sys.version.split()[0], "polars": pl.__version__}
    try:
        import pyarrow
        import pandas
        result["pyarrow"], result["pandas"] = pyarrow.__version__, pandas.__version__
    except Exception as exc:
        result["versions_error"] = str(exc)

    def save():
        result["scores"] = score(result)
        with open(os.path.join(a.out_dir, "mindown_check.json"), "w", encoding="utf-8") as f:
            json.dump(result, f, indent=1, default=str)

    if a.wait_for:
        live, polls, at = wait_for(a.wait_for, a.token, a.minutes)
        result["plan_live"] = {"live": live, "polls": polls, "at": at}
        if not live:
            save()
            print(json.dumps(result, indent=1, default=str))
            return
    result["started"] = now()

    mod_raw = fetch(RAW % (SHA_MAIN, MODULE_PATH))[0]
    test_raw = fetch(RAW % (SHA_MAIN, TEST_PATH))[0]
    result["pudl_files"] = {MODULE_PATH: {"bytes": len(mod_raw), "md5": md5(mod_raw)},
                            TEST_PATH: {"bytes": len(test_raw), "md5": md5(test_raw)}}
    root = tempfile.mkdtemp(prefix="mv2stub-")
    pkg, tests = stubs.build(root, mod_raw.decode("utf-8"), test_raw.decode("utf-8"))

    result["pudl_tests"] = {m: run_pudl_tests(pkg, tests, m, work_dir)
                            for m in ("none", "sort", "fill")}
    save()

    sys.path.insert(0, pkg)
    oc = importlib.import_module("pudl.analysis.operational_characteristics")
    result["cases"] = check_cases(oc)
    result["random"] = check_random(oc)
    save()

    try:
        nightly_df, result["nightly_out"] = nightly_out()
    except Exception as exc:
        nightly_df, result["nightly_out"] = None, {"error": "%s: %s" % (type(exc).__name__, exc)}
    save()

    if not a.skip_real and nightly_df is not None:
        try:
            result["real"] = real_data(oc, nightly_df, a.out_dir)
        except Exception as exc:
            result["real"] = {"error": "%s: %s" % (type(exc).__name__, exc)}
    result["finished"] = now()
    save()
    print(json.dumps(result, indent=1, default=str))


if __name__ == "__main__":
    main()
