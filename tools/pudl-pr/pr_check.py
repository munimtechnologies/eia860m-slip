"""Independent check of PUDL pull request #5731 (make_changelog keeps reverted values), and
of the date until which a series' last changelog record is valid.

Downloads src/pudl/helpers.py and tests/unit/helpers_test.py from PUDL at the PR's head
(c98ea31) and at main (4d3366b), takes make_changelog (and the PR's _valid_until) out with
ast, and runs, against the PR's function:

  Q1  PUDL's make_changelog unit tests at the PR head.
  Q2  PUDL's make_changelog unit tests at main (the 8 cases pudl-fix-v2 ran).
  Q3  the PR head's tests against main's function: some fail (the PR says the reversion
      tests fail on main).
  Q4  200 random one-record-per-date frames against the consecutive reference rule of
      check_fix.py 0.1.0, shuffled input giving the same output, and frames with no
      returning value giving the same rows as main.
  Q5  200 random tall frames (several records per series and date) against a snapshot
      reference: a date is kept, with all its distinct records, when its set of records
      differs from the previous date's set.
  Q6  no kept record in those tall frames is valid until a date on or before its own
      report date.
  Q7  1,000,000 rows: the PR keeps the numpy count of consecutive changes; run time of the
      PR and of main.
  S1  three three-month series through both functions: unchanged (OP, OP, OP), changed
      in the middle (OP, OA, OA) and changed on the last date (OP, OA, OP).

and on PUDL's nightly core_eia860m__changelog_generators:

  L1, L2  how each generator's last record ends relative to the table's last report date.

The plan with every bar is docs/pudl-pr-plan.md in munimtechnologies/eia860m-slip. PUDL's
code (MIT) and data (CC BY 4.0) are downloaded at run time and not stored with this tool.

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.).
"""

import argparse
import hashlib
import io
import json
import os
import sys
import time

import numpy as np
import pandas as pd

# check_fix.py (840ac28) and check_fix2.py (a8926e1), fetched by get_pinned2.py.
sys.path.insert(0, os.environ.get("PUDL_FIX_PINNED", "/out/pinned"))

import check_fix as cf  # noqa: E402
import check_fix2 as cf2  # noqa: E402

VERSION = "0.1.0"
SHA_PR = "c98ea31c5d7401ca21d47028d6cfda1a8322b856"
SHA_MAIN = cf.SHA_NEW
NIGHTLY = ("https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/"
           "core_eia860m__changelog_generators.parquet")
GEN_IDS = ["plant_id_eia", "generator_id"]


# ---- loading ------------------------------------------------------------------------------

def pr_source(helpers_src):
    """_valid_until and make_changelog of the PR head, as one block of source."""
    return cf.extract(helpers_src, "_valid_until") + "\n\n\n" + cf.extract(helpers_src)


def load_pr(src):
    ns = {"pd": pd, "np": np}
    exec(compile(src, "<pudl.helpers@pr>", "exec"), ns)
    return ns["make_changelog"]


# ---- comparing outputs ----------------------------------------------------------------------

def same_rows(a, b):
    """Same columns and the same rows in the same order, compared as text."""
    if sorted(a.columns) != sorted(b.columns) or len(a) != len(b):
        return False
    cols = sorted(a.columns)
    return (a[cols].astype(str).values.tolist() == b[cols].astype(str).values.tolist())


def snapshot_reference(df, series_cols):
    """{(date, values)} kept when a date's set of records differs from the previous date's."""
    value_cols = [c for c in df.columns if c != "report_date"]
    at = {}
    for s, d, v in zip(cf.rows(df, series_cols), df["report_date"], cf.rows(df, value_cols)):
        at.setdefault(s, {}).setdefault(pd.Timestamp(d), set()).add(v)
    kept = set()
    for by_date in at.values():
        prev = None
        for d in sorted(by_date):
            if prev is None or by_date[d] != by_date[prev]:
                kept.update((d, v) for v in by_date[d])
            prev = d
    return kept


def zero_or_backwards(df):
    rd = pd.to_datetime(df["report_date"])
    vu = pd.to_datetime(df["valid_until_date"])
    return int((vu <= rd).sum())


# ---- checks -------------------------------------------------------------------------------

def check_random(pr, main, n_each=100, seed=20261030):
    """Q4 (wide) and Q5/Q6 (tall)."""
    rng = np.random.default_rng(seed)
    kinds = ([("wide", v) for v in (0, 1, 2) for _ in range(n_each // 3 + 1)][:n_each]
             + [("wide_noreturn", 0)] * n_each + [("tall", 0)] * (2 * n_each))
    wide = {"frames": 0, "rows": 0, "ref_match": 0, "no_dup_rows": 0,
            "order_independent": 0, "noreturn_frames": 0, "noreturn_same_as_main": 0,
            "failures": []}
    tall = {"frames": 0, "rows": 0, "ref_match": 0, "no_dup_rows": 0,
            "order_independent": 0, "zero_or_backwards": 0, "rows_kept": 0,
            "rows_kept_by_value_rule": 0, "failures": []}
    for i, (kind, variant) in enumerate(kinds):
        if kind == "tall":
            df, idx, series_cols, t = cf.tall_frame(rng), cf.TALL_IDX, \
                ["plant_id_eia", "column_name"], tall
        else:
            df, idx, series_cols, t = cf.wide_frame(
                rng, returns=(kind == "wide"), variant=variant), cf.WIDE_IDX, GEN_IDS, wide
        value_cols = [c for c in df.columns if c != "report_date"]
        got = pr(df.copy(), idx).reset_index(drop=True)
        shuffled = pr(df.sample(frac=1, random_state=i).copy(), idx).reset_index(drop=True)
        kept = cf.as_set(got, value_cols)
        ref = snapshot_reference(df, series_cols) if kind == "tall" \
            else cf.reference(df, series_cols)
        ok = {"ref_match": kept == ref, "no_dup_rows": len(kept) == len(got),
              "order_independent": same_rows(got, shuffled)}
        t["frames"] += 1
        t["rows"] += len(df)
        for k, v in ok.items():
            t[k] += int(v)
        if kind == "tall":
            t["zero_or_backwards"] += zero_or_backwards(got)
            t["rows_kept"] += len(got)
            t["rows_kept_by_value_rule"] += len(cf.reference(df, series_cols))
            if zero_or_backwards(got):
                ok["no_zero_or_backwards"] = False
        if kind == "wide_noreturn":
            t["noreturn_frames"] += 1
            t["noreturn_same_as_main"] += int(
                same_rows(got, main(df.copy(), idx).reset_index(drop=True)))
        if not all(ok.values()) and len(t["failures"]) < 5:
            t["failures"].append({"frame": i, "kind": kind, "variant": variant,
                                  "failed": [k for k, v in ok.items() if not v],
                                  "input": df.astype(str).values.tolist()})
    return wide, tall


def series_frame(statuses):
    return pd.DataFrame({
        "plant_id_eia": [1] * len(statuses), "generator_id": ["A"] * len(statuses),
        "report_date": pd.to_datetime(cf.DATES8[:len(statuses)]),
        "operational_status_code": statuses,
    })


def describe(got):
    return ["%s %s until %s" % (d.strftime("%Y-%m-%d"), s, u.strftime("%Y-%m-%d"))
            for d, s, u in zip(got["report_date"], got["operational_status_code"],
                               got["valid_until_date"])]


def check_last_date(pr, main):
    """S1: three three-month series, through both functions."""
    cases = {"unchanged": ["OP", "OP", "OP"], "changed_middle": ["OP", "OA", "OA"],
             "changed_last": ["OP", "OA", "OP"]}
    return {name: {label: describe(fn(series_frame(st), cf.WIDE_IDX))
                   for label, fn in (("pr", pr), ("main", main))}
            for name, st in cases.items()}


def check_bench(pr, main):
    """Q7: 1,000,000 rows."""
    df, expected = cf.bench_frame()
    out = {"rows": len(df), "numpy_consecutive_count": expected}
    for label, fn in (("main", main), ("pr", pr)):
        t0 = time.perf_counter()
        got = fn(df.copy(), cf.WIDE_IDX)
        out[label + "_seconds"] = round(time.perf_counter() - t0, 3)
        out[label + "_rows_kept"] = len(got)
    out["ratio"] = round(out["pr_seconds"] / out["main_seconds"], 2)
    return out


# ---- PUDL's own tests ---------------------------------------------------------------------

def run_pudl_tests(runs, impls, gen_dir):
    """runs: {label: (test_src, impl_name)}; impls: {impl_name: module text}."""
    import pytest

    os.makedirs(gen_dir, exist_ok=True)
    for name, text in impls.items():
        with open(os.path.join(gen_dir, name + ".py"), "w", encoding="utf-8") as f:
            f.write(text)
    tests, added = {}, {}
    for label, (test_src, impl) in runs.items():
        module, tests[label] = cf.pudl_test_module(test_src, impl)
        module, added[label] = cf2.add_imports(module, test_src)
        with open(os.path.join(gen_dir, "test_%s.py" % label), "w", encoding="utf-8") as f:
            f.write(module)
    col = cf.Collector()
    code = pytest.main([gen_dir, "-q", "-p", "no:cacheprovider", "--rootdir", gen_dir],
                       plugins=[col])
    out = {"pytest_exit": int(code)}
    for label in runs:
        res = {k: v for k, v in col.results.items() if "test_%s.py" % label in k}
        errs = {k: v for k, v in col.errors.items() if "test_%s.py" % label in k}
        out[label] = {"test_functions": tests[label], "imports_added": added[label],
                      "collected": len(res),
                      "passed": sum(v == "passed" for v in res.values()),
                      "failed": sorted(k for k, v in res.items() if v != "passed"),
                      "name_errors": sum("NameError" in e for e in errs.values()),
                      "errors": {k: v[-600:] for k, v in errs.items()}}
    return out


# ---- the nightly changelog ----------------------------------------------------------------

def last_date_counts(df):
    """L1/L2: how each generator's last record ends against the table's last report date."""
    df = df.copy()
    df["report_date"] = pd.to_datetime(df["report_date"])
    df["valid_until_date"] = pd.to_datetime(df["valid_until_date"])
    last_date = df["report_date"].max()
    month_before = last_date - pd.DateOffset(months=1)
    last = df.sort_values(GEN_IDS + ["report_date"], kind="stable").groupby(
        GEN_IDS, dropna=False, observed=True).tail(1)
    covered = df[(df["report_date"] <= last_date) & (df["valid_until_date"] > last_date)]
    out = {
        "rows": int(len(df)),
        "generators": int(len(last)),
        "last_report_date": last_date.strftime("%Y-%m-%d"),
        "has_report_date_max": "report_date_max" in df.columns,
        "valid_until_missing": int(df["valid_until_date"].isna().sum()),
        "last_starts_on_last_date": int((last["report_date"] == last_date).sum()),
        "last_until_last_date_started_before_month_before": int(
            ((last["valid_until_date"] == last_date)
             & (last["report_date"] < month_before)).sum()),
        "last_until_last_date_started_month_before": int(
            ((last["valid_until_date"] == last_date)
             & (last["report_date"] == month_before)).sum()),
        "last_until_after_last_date": int((last["valid_until_date"] > last_date).sum()),
        "generators_covered_on_last_date": int(
            covered.drop_duplicates(GEN_IDS).shape[0]),
    }
    if out["has_report_date_max"]:
        rdm = pd.to_datetime(last["report_date_max"])
        on_last = rdm == last_date
        out["reported_on_last_date"] = int(on_last.sum())
        out["reported_on_last_date_unchanged"] = int(
            (on_last & (last["report_date"] < last_date)).sum())
        out["reported_on_last_date_unchanged_until_last_date"] = int(
            (on_last & (last["report_date"] < last_date)
             & (last["valid_until_date"] == last_date)).sum())
    a = (out["reported_on_last_date_unchanged"] if out["has_report_date_max"]
         else out["last_until_last_date_started_before_month_before"])
    b = out["last_starts_on_last_date"]
    out["L1_a"], out["L1_b"] = a, b
    out["L1_share"] = round(a / (a + b), 4) if a + b else None
    out["examples"] = [{k: str(v) for k, v in r.items()} for r in last[
        (last["valid_until_date"] == last_date) & (last["report_date"] < month_before)
    ].head(3)[GEN_IDS + ["report_date", "valid_until_date"]].to_dict("records")]
    return out


# ---- main ---------------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--wait-for", default="")
    ap.add_argument("--token", default="")
    ap.add_argument("--minutes", type=float, default=120)
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    result = {"tool": "pr_check.py " + VERSION, "check_fix": cf.VERSION,
              "check_fix2": cf2.VERSION, "python": sys.version.split()[0],
              "pandas": pd.__version__, "numpy": np.__version__}
    if a.wait_for:
        live, polls, at = cf.wait_for(a.wait_for, a.token, a.minutes)
        result["plan_live"] = {"live": live, "polls": polls, "at": at}
    result["started"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    src = {}
    for label, sha in (("pr", SHA_PR), ("main", SHA_MAIN)):
        raw = cf.fetch(cf.RAW % (sha, "src/pudl/helpers.py"))
        src[label] = raw.decode("utf-8")
        test_raw = cf.fetch(cf.RAW % (sha, "tests/unit/helpers_test.py"))
        src[label + "_tests"] = test_raw.decode("utf-8")
        result["helpers_" + sha[:7]] = {"bytes": len(raw), "md5": hashlib.md5(raw).hexdigest()}
        result["helpers_test_" + sha[:7]] = {"bytes": len(test_raw),
                                             "md5": hashlib.md5(test_raw).hexdigest()}
    pr_src = pr_source(src["pr"])
    main_src = cf.extract(src["main"])
    result["make_changelog_md5"] = {
        "pr": hashlib.md5(pr_src.encode("utf-8")).hexdigest(),
        "main": hashlib.md5(main_src.encode("utf-8")).hexdigest()}
    pr, main_fn = load_pr(pr_src), cf.load(main_src)

    head = "import numpy as np\nimport pandas as pd\n\n\n"
    result["tests"] = run_pudl_tests(
        {"pr_on_pr": (src["pr_tests"], "impl_pr"),
         "main_on_pr": (src["main_tests"], "impl_pr"),
         "pr_on_main": (src["pr_tests"], "impl_main")},
        {"impl_pr": head + pr_src + "\n", "impl_main": head + main_src + "\n"},
        os.path.join(a.out_dir, "gen"))
    result["Q4"], result["Q5"] = check_random(pr, main_fn)
    result["S1"] = check_last_date(pr, main_fn)
    result["Q7"] = check_bench(pr, main_fn)

    try:
        raw, headers = cf.fetch(NIGHTLY), {}
        req = cf.urllib.request.Request(NIGHTLY, headers=cf.UA, method="HEAD")
        with cf.urllib.request.urlopen(req, timeout=60) as resp:
            headers = dict(resp.headers)
        df = pd.read_parquet(io.BytesIO(raw))
        missing = [c for c in GEN_IDS + ["report_date", "valid_until_date"]
                   if c not in df.columns]
        result["nightly"] = {"bytes": len(raw), "md5": hashlib.md5(raw).hexdigest(),
                             "last_modified": headers.get("Last-Modified", ""),
                             "columns": list(map(str, df.columns)),
                             "missing_columns": missing}
        if not missing:
            result["nightly"].update(last_date_counts(df))
    except Exception as exc:  # reported, not hidden
        result["nightly"] = {"error": "%s: %s" % (type(exc).__name__, exc)}
    result["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    with open(os.path.join(a.out_dir, "pr_check.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1, default=str)
    shown = dict(result)
    shown["tests"] = {k: ({kk: vv for kk, vv in v.items() if kk != "errors"}
                          if isinstance(v, dict) else v)
                      for k, v in result["tests"].items()}
    print(json.dumps(shown, indent=1, default=str))


if __name__ == "__main__":
    main()
