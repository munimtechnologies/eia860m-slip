"""Check keep_changes as a drop-in fix for the dedup step of PUDL's make_changelog.

Downloads src/pudl/helpers.py and tests/unit/helpers_test.py from PUDL at pinned
commits, takes make_changelog and its unit tests out with ast, and runs:

  E1  make_changelog is the same text at both pinned commits, and the step to replace
      appears exactly once.
  E2  PUDL's own make_changelog unit tests, against the original and the patched function.
  E3  the three cases from PUDL issue #5730.
  E4  400 random frames (one record per date, and several per date as in the tall
      forensics tables) against a plain-Python reference rule.
  E5  missing values that come back (float NaN, pandas NA).
  E6  a tall series whose value comes back.
  E7  1,000,000 rows: run time of both, and the patched count against a numpy count.

The plan with every bar is docs/pudl-fix-plan.md in munimtechnologies/eia860m-slip.
PUDL's code (MIT) is downloaded at run time and not stored with this tool.

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.).
"""

import argparse
import ast
import hashlib
import json
import os
import sys
import time
import urllib.request

import numpy as np
import pandas as pd

import keep_changes as kc

VERSION = "0.1.0"
SHA_OLD = "af08a70361fb09e0bf3b509778317b7c8873b69f"
SHA_NEW = "4d3366b30d05a4c1c13cd8e88ba9b7b2f9ea6db2"
RAW = "https://raw.githubusercontent.com/catalyst-cooperative/pudl/%s/%s"
UA = {"User-Agent": "mv2-pudl-fix-check/0.1 (MV2, Munim, Inc.; mv2@munimtech.com)"}

WIDE_IDX = ["plant_id_eia", "generator_id", "report_date"]
TALL_IDX = ["plant_id_eia", "report_date"]
DATES8 = ["2026-%02d-01" % m for m in range(1, 9)]
STATUSES = ["OP", "OA", "SB", None]
CAPS = [1.0, 2.0, np.nan]
TALL_VALUES = ["a", "b", "c", None]
NA = ("<missing>",)


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def wait_for(url, token, minutes):
    """Poll url until its text contains token; returns (live, polls, utc time)."""
    deadline = time.time() + minutes * 60
    polls = 0
    while True:
        polls += 1
        try:
            if token in fetch(url).decode("utf-8", "replace"):
                return True, polls, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        except Exception:
            pass
        if time.time() > deadline:
            return False, polls, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        time.sleep(60)


def extract(source, name="make_changelog"):
    """Source text of the top-level function `name`, without its decorators."""
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(source, node)
    raise LookupError(name)


def load(func_src):
    ns = {"pd": pd, "np": np, "keep_changes": kc.keep_changes}
    exec(compile(func_src, "<pudl.helpers>", "exec"), ns)
    return ns["make_changelog"]


# ---- reference rule, in plain Python -------------------------------------------------

def norm(v):
    try:
        if pd.isna(v):
            return NA
    except (TypeError, ValueError):
        pass
    return v


def rows(df, cols):
    return [tuple(norm(v) for v in r) for r in df[cols].itertuples(index=False, name=None)]


def as_set(df, value_cols):
    """{(report_date, values)} of a frame, with missing values made equal."""
    dates = [pd.Timestamp(d) for d in df["report_date"]]
    return set(zip(dates, rows(df, value_cols)))


def reference(df, series_cols):
    """Keep (date, values) when the series' previous date had no record with those values."""
    value_cols = [c for c in df.columns if c != "report_date"]
    at = {}
    for s, d, v in zip(rows(df, series_cols), df["report_date"], rows(df, value_cols)):
        at.setdefault(s, {}).setdefault(pd.Timestamp(d), set()).add(v)
    kept = set()
    for by_date in at.values():
        prev = None
        for d in sorted(by_date):
            for v in by_date[d]:
                if prev is None or v not in by_date[prev]:
                    kept.add((d, v))
            prev = d
    return kept


# ---- frames ---------------------------------------------------------------------------

def wide_frame(rng, returns=True, variant=0):
    recs = []
    for p in range(int(rng.integers(1, 4))):
        for g in range(int(rng.integers(1, 3))):
            months = [m for m in range(8) if rng.random() < 0.8] or [0]
            status, cap, counter = None, None, 0
            for i, m in enumerate(months):
                if i == 0 or rng.random() < 0.4:
                    if returns:
                        status = STATUSES[int(rng.integers(len(STATUSES)))]
                        cap = CAPS[int(rng.integers(len(CAPS)))]
                    else:
                        counter += 1
                        status, cap = "S%d" % counter, float(counter)
                recs.append((p, "G%d" % g, DATES8[m], status, cap))
    df = pd.DataFrame(recs, columns=WIDE_IDX + ["operational_status_code", "capacity_mw"])
    df["report_date"] = pd.to_datetime(df["report_date"])
    if variant == 1:
        df["operational_status_code"] = df["operational_status_code"].astype("string")
    elif variant == 2:
        df["operational_status_code"] = df["operational_status_code"].astype(object)
    return df


def tall_frame(rng):
    plants, dates, cols, vals = [], [], [], []
    for p in range(int(rng.integers(1, 3))):
        for col in ("state", "county"):
            months = [m for m in range(6) if rng.random() < 0.8] or [0]
            for m in months:
                for _ in range(int(rng.integers(1, 4))):
                    plants.append(p)
                    dates.append(DATES8[m])
                    cols.append(col)
                    vals.append(TALL_VALUES[int(rng.integers(len(TALL_VALUES)))])
    return pd.DataFrame({
        "plant_id_eia": plants,
        "report_date": pd.to_datetime(dates),
        "column_name": cols,
        "record_value": pd.Series(vals, dtype=object),
    })


def frames_equal(a, b):
    try:
        pd.testing.assert_frame_equal(a, b)
        return True
    except AssertionError:
        return False


# ---- checks ---------------------------------------------------------------------------

def check_cases(orig, patched):
    """E3: the three cases of issue #5730."""
    cases = {"return": ["OP", "OA", "OP"], "no_return": ["OP", "OA", "SB"],
             "repeat": ["OP", "OP", "OA"]}
    out = {}
    for name, statuses in cases.items():
        df = pd.DataFrame({
            "plant_id_eia": [1, 1, 1], "generator_id": ["A", "A", "A"],
            "report_date": pd.to_datetime(DATES8[:3]), "operational_status_code": statuses,
        })
        res = {}
        for label, fn in (("original", orig), ("patched", patched)):
            got = fn(df.copy(), WIDE_IDX)
            res[label] = {
                "dates_kept": got["report_date"].dt.strftime("%Y-%m-%d").tolist(),
                "valid_until": got["valid_until_date"].dt.strftime("%Y-%m-%d").tolist(),
            }
        out[name] = res
    return out


def check_missing(orig, patched):
    """E5: a missing value that comes back."""
    cap = pd.DataFrame({
        "plant_id_eia": [1] * 4, "generator_id": ["A"] * 4,
        "report_date": pd.to_datetime(DATES8[:4]), "operational_status_code": ["OP"] * 4,
        "capacity_mw": [np.nan, np.nan, 5.0, np.nan],
    })
    status = pd.DataFrame({
        "plant_id_eia": [1] * 3, "generator_id": ["A"] * 3,
        "report_date": pd.to_datetime(DATES8[:3]),
        "operational_status_code": pd.array(["OP", pd.NA, "OP"], dtype="string"),
    })
    out = {}
    for name, df in (("float_nan", cap), ("string_na", status)):
        out[name] = {
            label: fn(df.copy(), WIDE_IDX)["report_date"].dt.strftime("%Y-%m-%d").tolist()
            for label, fn in (("original", orig), ("patched", patched))
        }
    return out


def check_tall(orig, patched):
    """E6: values a, b on Jan and Feb, a on Mar, a and b on Apr, in one series."""
    vals = [("a", 0), ("b", 0), ("a", 1), ("b", 1), ("a", 2), ("a", 3), ("b", 3)]
    df = pd.DataFrame({
        "plant_id_eia": [1] * len(vals),
        "report_date": pd.to_datetime([DATES8[m] for _, m in vals]),
        "column_name": ["state"] * len(vals),
        "record_value": pd.Series([v for v, _ in vals], dtype=object),
    })
    out = {}
    for label, fn in (("original", orig), ("patched", patched)):
        got = fn(df.copy(), TALL_IDX)
        out[label] = [
            "%s %s until %s" % (d.strftime("%Y-%m-%d"), v, u.strftime("%Y-%m-%d"))
            for d, v, u in zip(got["report_date"], got["record_value"], got["valid_until_date"])
        ]
    return out


def check_random(orig, patched, n_each=100, seed=20261029):
    """E4: random frames against the reference rule."""
    rng = np.random.default_rng(seed)
    kinds = ([("wide", v) for v in (0, 1, 2) for _ in range(n_each // 3 + 1)][:n_each]
             + [("wide_noreturn", 0)] * n_each + [("tall", 0)] * (2 * n_each))
    tally = {"frames": 0, "rows": 0, "ref_match": 0, "no_dup_rows": 0, "superset": 0,
             "order_independent": 0, "noreturn_frames": 0, "noreturn_identical": 0,
             "frames_where_patched_keeps_more": 0, "extra_rows_kept": 0, "failures": []}
    for i, (kind, variant) in enumerate(kinds):
        if kind == "tall":
            df, idx = tall_frame(rng), TALL_IDX
            series_cols = ["plant_id_eia", "column_name"]
        else:
            df, idx = wide_frame(rng, returns=(kind == "wide"), variant=variant), WIDE_IDX
            series_cols = ["plant_id_eia", "generator_id"]
        value_cols = [c for c in df.columns if c != "report_date"]
        a = orig(df.copy(), idx)
        b = patched(df.copy(), idx)
        shuffled = patched(df.sample(frac=1, random_state=i).copy(), idx)
        sa, sb = as_set(a, value_cols), as_set(b, value_cols)
        ok = {
            "ref_match": sb == reference(df, series_cols),
            "no_dup_rows": len(sb) == len(b),
            "superset": sa <= sb,
            "order_independent": frames_equal(b.reset_index(drop=True),
                                              shuffled.reset_index(drop=True)),
        }
        tally["frames"] += 1
        tally["rows"] += len(df)
        for k, v in ok.items():
            tally[k] += int(v)
        if len(b) > len(a):
            tally["frames_where_patched_keeps_more"] += 1
            tally["extra_rows_kept"] += len(b) - len(a)
        if kind == "wide_noreturn":
            tally["noreturn_frames"] += 1
            tally["noreturn_identical"] += int(frames_equal(a, b))
        if not all(ok.values()) and len(tally["failures"]) < 5:
            tally["failures"].append({"frame": i, "kind": kind, "variant": variant,
                                      "failed": [k for k, v in ok.items() if not v],
                                      "input": df.astype(str).values.tolist()})
    return tally


def bench_frame(n_series=20000, n_months=50, seed=7):
    rng = np.random.default_rng(seed)
    n = n_series * n_months
    sid = np.repeat(np.arange(n_series), n_months)
    month = np.tile(np.arange(n_months), n_series)
    change = rng.random(n) < 0.02
    change[month == 0] = True
    at = np.flatnonzero(change)[np.cumsum(change) - 1]
    status = np.array(["OP", "OA", "SB", "OS"], dtype=object)[rng.integers(0, 4, n)[at]]
    cap = rng.integers(1, 5, n).astype(float)[at]
    df = pd.DataFrame({
        "plant_id_eia": sid // 3,
        "generator_id": np.array(["1", "2", "GT1"], dtype=object)[sid % 3],
        "report_date": pd.date_range("2022-01-01", periods=n_months, freq="MS").values[month],
        "operational_status_code": status,
        "capacity_mw": cap,
    })
    # numpy count of what the consecutive rule keeps (one record per series and month)
    differs = np.ones(n, dtype=bool)
    same = (status[1:] == status[:-1]) & (cap[1:] == cap[:-1]) & (sid[1:] == sid[:-1])
    differs[1:] = ~same
    return df, int(differs.sum())


def check_bench(orig, patched):
    """E7: run time on 1,000,000 rows."""
    df, expected = bench_frame()
    out = {"rows": len(df), "numpy_consecutive_count": expected}
    for label, fn in (("original", orig), ("patched", patched)):
        t0 = time.perf_counter()
        got = fn(df.copy(), WIDE_IDX)
        out[label + "_seconds"] = round(time.perf_counter() - t0, 3)
        out[label + "_rows_kept"] = len(got)
    out["ratio"] = round(out["patched_seconds"] / out["original_seconds"], 2)
    return out


# ---- PUDL's own unit tests --------------------------------------------------------------

HEADER = ("import datetime\n\nimport numpy as np\nimport pandas as pd\nimport pytest\n\n"
          "from %s import make_changelog\n")


def pudl_test_module(test_src, impl_name):
    """PUDL's test_make_changelog* tests and the top-level names they use, as one module."""
    tree = ast.parse(test_src)
    lines = test_src.splitlines(keepends=True)
    top = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            top[node.name] = node
        elif isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            top[node.targets[0].id] = node
    keep = {n for n in top if n.startswith("test_make_changelog")}
    todo = list(keep)
    while todo:
        for sub in ast.walk(top[todo.pop()]):
            if isinstance(sub, ast.Name) and sub.id in top and sub.id not in keep:
                keep.add(sub.id)
                todo.append(sub.id)
    parts = [HEADER % impl_name]
    for node in tree.body:
        name = getattr(node, "name", None) or (
            node.targets[0].id if isinstance(node, ast.Assign) and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name) else None)
        if name in keep:
            decos = getattr(node, "decorator_list", [])
            start = min([d.lineno for d in decos] + [node.lineno])
            parts.append("".join(lines[start - 1:node.end_lineno]))
    return "\n\n".join(parts) + "\n", sorted(n for n in keep if n.startswith("test_"))


class Collector:
    def __init__(self):
        self.results = {}
        self.errors = {}

    def pytest_runtest_logreport(self, report):
        if report.when == "call" or report.outcome != "passed":
            if self.results.get(report.nodeid, "passed") == "passed":
                self.results[report.nodeid] = report.outcome
            if report.outcome == "failed":
                self.errors[report.nodeid] = str(report.longrepr)[-1500:]


def run_pudl_tests(test_src, orig_src, patched_src, gen_dir):
    import pytest

    os.makedirs(gen_dir, exist_ok=True)
    impls = {
        "impl_orig": "import numpy as np\nimport pandas as pd\n\n\n" + orig_src + "\n",
        "impl_patched": ("import numpy as np\nimport pandas as pd\n\n"
                         "from keep_changes import keep_changes\n\n\n" + patched_src + "\n"),
    }
    for name, text in impls.items():
        with open(os.path.join(gen_dir, name + ".py"), "w", encoding="utf-8") as f:
            f.write(text)
    tests = None
    for label, impl in (("orig", "impl_orig"), ("patched", "impl_patched")):
        module, tests = pudl_test_module(test_src, impl)
        with open(os.path.join(gen_dir, "test_pudl_%s.py" % label), "w", encoding="utf-8") as f:
            f.write(module)
    col = Collector()
    code = pytest.main([gen_dir, "-q", "-p", "no:cacheprovider", "--rootdir", gen_dir],
                       plugins=[col])
    out = {"pytest_exit": int(code), "test_functions": tests}
    for label in ("orig", "patched"):
        res = {k: v for k, v in col.results.items() if "test_pudl_%s.py" % label in k}
        out[label] = {"collected": len(res),
                      "passed": sum(v == "passed" for v in res.values()),
                      "failed": sorted(k for k, v in res.items() if v != "passed")}
    out["errors"] = col.errors
    return out


# ---- main -------------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--wait-for", default="")
    ap.add_argument("--token", default="")
    ap.add_argument("--minutes", type=float, default=90)
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    result = {"tool": "check_fix.py " + VERSION, "keep_changes": kc.VERSION,
              "python": sys.version.split()[0], "pandas": pd.__version__,
              "numpy": np.__version__}
    if a.wait_for:
        live, polls, at = wait_for(a.wait_for, a.token, a.minutes)
        result["plan_live"] = {"live": live, "polls": polls, "at": at}
    result["started"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    srcs = {}
    for sha in (SHA_OLD, SHA_NEW):
        raw = fetch(RAW % (sha, "src/pudl/helpers.py"))
        func = extract(raw.decode("utf-8"))
        srcs[sha] = func
        result["helpers_" + sha[:7]] = {
            "bytes": len(raw), "md5": hashlib.md5(raw).hexdigest(),
            "make_changelog_md5": hashlib.md5(func.encode("utf-8")).hexdigest()}
    orig_src = srcs[SHA_NEW]
    result["E1"] = {"same_function_text": srcs[SHA_OLD] == srcs[SHA_NEW],
                    "target_count": orig_src.count(kc.TARGET)}
    patched_src = kc.patch_source(orig_src)
    with open(os.path.join(a.out_dir, "make_changelog_patched.diff.txt"), "w",
              encoding="utf-8") as f:
        f.write("--- dedup step at %s\n%s\n+++ replacement\n%s" % (
            SHA_NEW, kc.TARGET, kc.REPLACEMENT))
    orig, patched = load(orig_src), load(patched_src)

    test_raw = fetch(RAW % (SHA_NEW, "tests/unit/helpers_test.py"))
    result["helpers_test_" + SHA_NEW[:7]] = {"bytes": len(test_raw),
                                             "md5": hashlib.md5(test_raw).hexdigest()}
    result["E2"] = run_pudl_tests(test_raw.decode("utf-8"), orig_src, patched_src,
                                  os.path.join(a.out_dir, "gen"))
    result["E3"] = check_cases(orig, patched)
    result["E4"] = check_random(orig, patched)
    result["E5"] = check_missing(orig, patched)
    result["E6"] = check_tall(orig, patched)
    result["E7"] = check_bench(orig, patched)
    result["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    with open(os.path.join(a.out_dir, "fix_check.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1, default=str)
    shown = dict(result)
    shown["E2"] = {k: v for k, v in result["E2"].items() if k != "errors"}
    print(json.dumps(shown, indent=1, default=str))


if __name__ == "__main__":
    main()
