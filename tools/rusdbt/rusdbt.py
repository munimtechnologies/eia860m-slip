# Copyright 2026 Munim, Inc.
# Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working in the name of MV2 of Munim, Inc. (mv2@munimtech.com).
"""rusdbt: run PUDL's own dbt test on proposed RUS Form 7 liabilities totals.

pudl#5760 asks for `subcomponents_sum_to_total` data tests on
core_rus7__yearly_balance_sheet_liabilities and its out_ version, validated
with dbt. tools/rusliab measured the proposed tests with a plain-Python copy
of the macro. This script checks the same tests with PUDL's real dbt project:

1. downloads the three nightly parquet tables it needs;
2. shallow-clones only the dbt/ folder of catalyst-cooperative/pudl main;
3. adds the five proposed tests (tests-block.yml, the exact text of the PR)
   to both liabilities schema.yml files, plus one negative control on the core
   table (payments_unapplied ADDED instead of subtracted), which must fail;
4. runs `dbt test` for the subcomponents_sum_to_total tests of the two
   liabilities tables and of core_rus7__yearly_balance_sheet_assets (whose
   tests already pass on main: a positive control for the harness);
5. reads dbt's run_results.json and manifest.json and scores the four
   pre-registered predictions in README.md.

It only measures. Nothing is sent to PUDL.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.request

NIGHTLY = "https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/"
PUDL_REPO = "https://github.com/catalyst-cooperative/pudl"
UA = {"User-Agent": "MV2-Munim-Inc (mv2@munimtech.com)"}

CORE = "core_rus7__yearly_balance_sheet_liabilities"
OUT = "out_rus7__yearly_balance_sheet_liabilities"
ASSETS = "core_rus7__yearly_balance_sheet_assets"
TABLES = [CORE, OUT, ASSETS]

LTD = [
    "long_term_debt_rus",
    "long_term_debt_ffb_rus_guaranteed",
    "long_term_debt_other_rus_guaranteed",
    "long_term_debt_other",
    "long_term_debt_rus_economic_development",
]
# (total_label, subcomponents_list, negative_subcomponents_list)
GROUPS = [
    ("total_margins_and_equities", [
        "memberships",
        "patronage_capital",
        "operating_margins_prior_years",
        "operating_margins_current_year",
        "non_operating_margins",
        "other_margins_and_equities",
    ], []),
    ("total_long_term_debt", LTD, ["payments_unapplied"]),
    ("total_noncurrent_obligations", [
        "noncurrent_obligations_under_capital_leases",
        "noncurrent_obligations_asset_retirement",
    ], []),
    ("total_current_and_accrued_liabilities", [
        "notes_payable",
        "accounts_payable",
        "consumer_deposits",
        "current_maturities_long_term_debt",
        "economic_development",
        "current_maturities_capital_leases",
        "other_current_and_accrued_liabilities",
    ], []),
    ("total_liabilities_and_other_credits", [
        "total_margins_and_equities",
        "total_long_term_debt",
        "total_noncurrent_obligations",
        "total_current_and_accrued_liabilities",
        "regulatory",
        "other_deferred_credits",
    ], []),
]
NEG_CONTROL = ("total_long_term_debt", LTD + ["payments_unapplied"], [])

# Pre-registered: tools/rusliab measured 4,601 failing borrower-years for the
# negative control on the 2026-11-09 nightly. P3 allows +-1% for data drift.
NEG_EXPECTED = 4601
NEG_LOW = 4555
NEG_HIGH = 4647


def test_block(total, subs, neg, indent=10):
    """Lines of one subcomponents_sum_to_total test, as in PR #5729."""
    p = " " * indent
    lines = [
        p + "- subcomponents_sum_to_total:",
        p + "    arguments:",
        p + "      group_by_columns:",
        p + "        - borrower_id_rus",
        p + "        - report_date",
        p + "      categorical_column: liability_type",
        p + "      value_column: ending_balance",
        p + "      subcomponents_list:",
    ]
    lines += [p + "        - " + s for s in subs]
    if neg:
        lines.append(p + "      negative_subcomponents_list:")
        lines += [p + "        - " + s for s in neg]
    lines += [p + "      total_label: " + total, p + "      tolerance: 10"]
    return lines


def proposed_lines():
    out = []
    for total, subs, neg in GROUPS:
        out += test_block(total, subs, neg)
    return out


def patch_schema(text, table, block_lines):
    """Insert block_lines at the end of `table`'s data_tests (before columns:)."""
    lines = text.split("\n")
    name_line = "      - name: " + table
    if name_line not in lines:
        raise ValueError("table not found: " + table)
    i = lines.index(name_line)
    for j in range(i + 1, len(lines)):
        if lines[j].rstrip() == "        columns:":
            return "\n".join(lines[:j] + list(block_lines) + lines[j:])
        if lines[j].startswith("      - name: "):
            break
    raise ValueError("no columns: line for " + table)


def find_key(obj, key):
    """First value of `key` anywhere in nested dicts/lists, else None."""
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for v in obj.values():
            r = find_key(v, key)
            if r is not None:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = find_key(v, key)
            if r is not None:
                return r
    return None


def records_from(run_results, manifest):
    """One record per subcomponents_sum_to_total result."""
    recs = []
    nodes = manifest.get("nodes", {})
    for res in run_results.get("results", []):
        uid = res.get("unique_id", "")
        node = nodes.get(uid, {})
        meta = node.get("test_metadata") or {}
        if meta.get("name") != "subcomponents_sum_to_total":
            continue
        kw = meta.get("kwargs") or {}
        deps = (node.get("depends_on") or {}).get("nodes") or []
        table = deps[0].split(".")[-1] if deps else ""
        recs.append({
            "unique_id": uid,
            "table": table,
            "total_label": find_key(kw, "total_label"),
            "subcomponents_list": find_key(kw, "subcomponents_list") or [],
            "negative_subcomponents_list": find_key(kw, "negative_subcomponents_list") or [],
            "status": res.get("status"),
            "failures": res.get("failures"),
            "message": res.get("message"),
        })
    return recs


def is_neg_control(r):
    return (r["table"] == CORE and r["total_label"] == "total_long_term_debt"
            and "payments_unapplied" in r["subcomponents_list"])


def passed(r):
    return r["status"] == "pass" and (r["failures"] or 0) == 0


def evaluate(recs):
    """Score P1-P4. Any dbt 'error' (not 'fail') in a group = 'not tested'."""
    def proposed(table):
        return [r for r in recs if r["table"] == table and not is_neg_control(r)]

    def all_pass(group, expected_n):
        if any(r["status"] not in ("pass", "fail", "warn") for r in group):
            return "not tested"
        if len(group) != expected_n:
            return "not tested"
        return "held" if all(passed(r) for r in group) else "failed"

    verdicts = {
        "P1": all_pass(proposed(CORE), 5),
        "P2": all_pass(proposed(OUT), 5),
    }
    neg = [r for r in recs if is_neg_control(r)]
    if len(neg) != 1 or neg[0]["status"] not in ("pass", "fail", "warn"):
        verdicts["P3"] = "not tested"
    else:
        n = neg[0]["failures"] or 0
        ok = neg[0]["status"] == "fail" and NEG_LOW <= n <= NEG_HIGH
        verdicts["P3"] = "held" if ok else "failed"
    assets = [r for r in recs if r["table"] == ASSETS]
    if not assets:
        verdicts["P4"] = "not tested"
    else:
        verdicts["P4"] = all_pass(assets, len(assets))
    return verdicts


def fetch(table, data_dir):
    os.makedirs(data_dir, exist_ok=True)
    path = os.path.join(data_dir, table + ".parquet")
    if not os.path.exists(path):
        req = urllib.request.Request(NIGHTLY + table + ".parquet", headers=UA)
        with urllib.request.urlopen(req, timeout=300) as r, open(path, "wb") as f:
            f.write(r.read())
    return path


def sh(cmd, cwd=None, env=None, timeout=1800):
    print("$ " + " ".join(cmd), flush=True)
    p = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True,
                       timeout=timeout)
    return p.returncode, p.stdout, p.stderr


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--clone-dir", default="/tmp/pudl")
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    result = {"tool": "rusdbt 0.1.0", "tables": {}}

    for t in TABLES:
        p = fetch(t, a.data_dir)
        result["tables"][t] = {"bytes": os.path.getsize(p)}

    if os.path.exists(a.clone_dir):
        shutil.rmtree(a.clone_dir)
    rc, o, e = sh(["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse",
                   PUDL_REPO, a.clone_dir])
    if rc != 0:
        print(o, e)
        raise SystemExit("clone failed")
    sh(["git", "-C", a.clone_dir, "sparse-checkout", "set", "dbt"])
    rc, sha, _ = sh(["git", "-C", a.clone_dir, "rev-parse", "HEAD"])
    result["pudl_commit"] = sha.strip()
    dbt_dir = os.path.join(a.clone_dir, "dbt")

    block = proposed_lines()
    for t in (CORE, OUT):
        f = os.path.join(dbt_dir, "models", "pudl", "rus7", t, "schema.yml")
        with open(f, encoding="utf-8") as fh:
            text = fh.read()
        extra = list(block)
        if t == CORE:
            extra += test_block(*NEG_CONTROL)
        with open(f, "w", encoding="utf-8") as fh:
            fh.write(patch_schema(text, t, extra))

    prof = "/tmp/rusdbt-profiles"
    os.makedirs(prof, exist_ok=True)
    with open(os.path.join(prof, "profiles.yml"), "w", encoding="utf-8") as fh:
        fh.write("pudl_duckdb:\n  target: mv2\n  outputs:\n    mv2:\n"
                 "      type: duckdb\n      path: /tmp/rusdbt.duckdb\n      threads: 1\n")
    os.makedirs("/tmp/pudl_output", exist_ok=True)
    env = dict(os.environ)
    env["PARQUET_BASE_PATH"] = os.path.abspath(a.data_dir)
    env["PUDL_OUTPUT"] = "/tmp/pudl_output"
    env["DBT_PROFILES_DIR"] = prof

    rc, o, e = sh(["dbt", "--version"], cwd=dbt_dir, env=env)
    result["dbt_version"] = o.strip()
    rc, o, e = sh(["dbt", "deps"], cwd=dbt_dir, env=env)
    result["dbt_deps_rc"] = rc
    if rc != 0:
        print(o[-3000:], e[-3000:])
    sel = [t + ",test_name:subcomponents_sum_to_total" for t in (CORE, OUT, ASSETS)]
    sel = ["source:pudl." + s for s in sel]
    rc, o, e = sh(["dbt", "test", "--target", "mv2", "--select"] + sel,
                  cwd=dbt_dir, env=env, timeout=3600)
    result["dbt_test_rc"] = rc
    with open(os.path.join(a.out_dir, "dbt_test_stdout.txt"), "w", encoding="utf-8") as fh:
        fh.write(o + "\n--- stderr ---\n" + e)
    print(o[-6000:])

    tgt = os.path.join(dbt_dir, "target")
    try:
        with open(os.path.join(tgt, "run_results.json"), encoding="utf-8") as fh:
            rr = json.load(fh)
        with open(os.path.join(tgt, "manifest.json"), encoding="utf-8") as fh:
            mf = json.load(fh)
    except OSError as exc:
        result["error"] = "no dbt target files: %s" % exc
        rr, mf = {}, {}
    shutil.copy(os.path.join(tgt, "run_results.json"), a.out_dir) if rr else None
    recs = records_from(rr, mf)
    result["results"] = recs
    result["verdicts"] = evaluate(recs)
    with open(os.path.join(a.out_dir, "rusdbt.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1)
    for r in recs:
        print("%-46s %-40s neg=%s %s failures=%s" % (
            r["table"], r["total_label"], ",".join(r["negative_subcomponents_list"]),
            r["status"], r["failures"]))
    print("verdicts", json.dumps(result["verdicts"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
