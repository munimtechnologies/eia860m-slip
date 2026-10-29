"""Run PUDL's own make_changelog on small examples where a value returns (A, B, A).

Reads src/pudl/helpers.py at a pinned commit as text, takes only the make_changelog
function out of it with ast (the rest of the module needs a full PUDL install), runs it
on three tiny frames and writes what it keeps. Nothing else from PUDL is imported.

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.).
"""

import argparse
import ast
import hashlib
import json
import os
import sys

import numpy as np
import pandas as pd

VERSION = "0.1.0"
IDX = ["plant_id_eia", "generator_id", "report_date"]
DATES = ["2026-01-01", "2026-02-01", "2026-03-01"]

# name -> monthly statuses for one generator, and the rows a changelog that compares
# each record only with the one before it would keep
CASES = {
    "return": (["OP", "OA", "OP"], [0, 1, 2]),
    "no_return": (["OP", "OA", "SB"], [0, 1, 2]),
    "repeat": (["OP", "OP", "OA"], [0, 2]),
}


def extract(source, name="make_changelog"):
    """Source text of the top-level function `name`, without its decorators."""
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(source, node)
    raise LookupError(name)


def load(source, name="make_changelog"):
    ns = {"pd": pd, "np": np}
    exec(compile(extract(source, name), "<pudl.helpers>", "exec"), ns)
    return ns[name]


def frame(statuses):
    return pd.DataFrame({
        "plant_id_eia": [1] * len(statuses),
        "generator_id": ["A"] * len(statuses),
        "report_date": pd.to_datetime(DATES[:len(statuses)]),
        "operational_status_code": statuses,
    })


def run_case(fn, statuses, expected_rows):
    df = frame(statuses)
    out = fn(df.copy(), IDX)
    kept = sorted(out["report_date"].dt.strftime("%Y-%m-%d").tolist())
    want = [DATES[i] for i in expected_rows]
    return {
        "statuses_in": statuses,
        "dates_kept": kept,
        "statuses_kept": out.sort_values("report_date")["operational_status_code"].tolist(),
        "consecutive_rule_keeps": want,
        "matches_consecutive_rule": kept == want,
        "columns_out": [str(c) for c in out.columns],
    }


def check(source, fn=None):
    fn = fn or load(source)
    cases = {k: run_case(fn, s, e) for k, (s, e) in CASES.items()}
    ret = cases["return"]
    return {
        "return_dropped": DATES[2] not in ret["dates_kept"],
        "last_status_kept": ret["statuses_kept"][-1] if ret["statuses_kept"] else None,
        "cases": cases,
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--sha", required=True)
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args(argv)
    raw = open(a.src, "rb").read()
    result = {
        "tool": "check_changelog.py " + VERSION,
        "pudl_commit": a.sha,
        "helpers_md5": hashlib.md5(raw).hexdigest(),
        "helpers_bytes": len(raw),
        "python": sys.version.split()[0],
        "pandas": pd.__version__,
    }
    source = raw.decode("utf-8")
    result["make_changelog_source"] = extract(source)
    result.update(check(source))
    os.makedirs(a.out_dir, exist_ok=True)
    with open(os.path.join(a.out_dir, "changelog_check.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1)
    shown = {k: v for k, v in result.items() if k != "make_changelog_source"}
    print(json.dumps(shown, indent=1))


if __name__ == "__main__":
    main()
