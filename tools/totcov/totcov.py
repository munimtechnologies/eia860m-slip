# Copyright 2026 Munim, Inc.
# Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working in the name of MV2 of Munim, Inc. (mv2@munimtech.com).
"""totcov: can each of PUDL's "subcomponents sum to total" data tests ever fail?

PUDL's dbt macro `subcomponents_sum_to_total` compares, for every group, the
sum of the subcomponent rows with the row carrying `total_label`. When no row
in a group carries the total label, `grand_total` is NULL, the comparison
`ABS(subcomponents_sum - grand_total) > tolerance` is NULL, and the group
passes silently (unless the optional `minimum_total_coverage` is set). A test
whose total label never occurs in its categorical column therefore checks
nothing at all.

This script:
1. sparse-clones the dbt/ folder of catalyst-cooperative/pudl main;
2. finds every subcomponents_sum_to_total test in dbt/models/**/schema.yml;
3. downloads the nightly parquet of each table those tests use;
4. for each test, re-implements the macro in DuckDB and counts groups, groups
   with a total row ("coverage"), groups that fail, and how often each label
   occurs (a label that never occurs is a typo or a wrong column);
5. measures proposed replacement tests for core_rus7__yearly_utility_plant_changes,
   with a deliberately wrong negative control, and three specific label checks
   on core_rus7__yearly_statement_of_operations;
6. scores the pre-registered predictions in README.md.

It only measures. Nothing is sent to PUDL. duckdb and PyYAML are imported only
inside the functions that need them, so the unit tests run without them.
"""
import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request

NIGHTLY = "https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/"
PUDL_REPO = "https://github.com/catalyst-cooperative/pudl"
UA = {"User-Agent": "MV2-Munim-Inc (mv2@munimtech.com)"}
MAX_TABLE_BYTES = 600 * 1024 * 1024
MAX_TOTAL_BYTES = 4 * 1024 * 1024 * 1024

UPC = "core_rus7__yearly_utility_plant_changes"
UPO = "out_rus7__yearly_utility_plant_changes"
SOO = "core_rus7__yearly_statement_of_operations"
ASSETS = "core_rus7__yearly_balance_sheet_assets"
IN_SERVICE_ITEMS = [
    "distribution",
    "general",
    "headquarters",
    "intangibles",
    "transmission",
    "regional_transmission_and_market_operation",
    "all_other",
]


# ---------------------------------------------------------------- SQL pieces
def qi(name):
    """Quote an identifier for DuckDB."""
    return '"' + str(name).replace('"', '""') + '"'


def ql(value):
    """Quote a string literal for DuckDB."""
    return "'" + str(value).replace("'", "''") + "'"


def as_list(x):
    """The macro's normalisation: a string becomes a one-item list."""
    if x is None:
        return []
    if isinstance(x, str):
        return [x]
    return list(x)


def label_cond(cols, label):
    """SQL for one label (one value per categorical column), as in the macro."""
    vals = as_list(label)
    if len(vals) != len(cols):
        raise ValueError("label %r must have one value per categorical column %r"
                         % (label, cols))
    return "(" + " AND ".join("%s = %s" % (qi(c), ql(v)) for c, v in zip(cols, vals)) + ")"


def labels_cond(cols, labels):
    """OR of several label conditions."""
    return "(" + " OR ".join(label_cond(cols, lab) for lab in labels) + ")"


def filtered_sql(table_ref, row_condition):
    sql = "SELECT * FROM " + table_ref
    if row_condition:
        sql += " WHERE " + str(row_condition)
    return sql


def summary_sql(table_ref, spec):
    """One row per group: subcomponents_sum and grand_total, as the macro builds them."""
    gb = [qi(c) for c in spec["group_by"]]
    cols = spec["cols"]
    cc = [qi(c) for c in cols]
    grouped = "SELECT %s, SUM(%s) AS tc_value FROM (%s) f GROUP BY %s" % (
        ", ".join(gb + cc), qi(spec["value"]),
        filtered_sql(table_ref, spec["row_condition"]), ", ".join(gb + cc))
    whens = []
    if spec["negs"]:
        whens.append("WHEN %s THEN -1 * tc_value" % labels_cond(cols, spec["negs"]))
    if spec["subs"]:
        whens.append("WHEN %s THEN tc_value" % labels_cond(cols, spec["subs"]))
    else:
        whens.append("WHEN NOT %s THEN tc_value" % label_cond(cols, spec["total"]))
    sub_sum = "SUM(CASE %s END) AS subs_sum" % " ".join(whens)
    grand = "MAX(CASE WHEN %s THEN tc_value END) AS grand_total" % label_cond(cols, spec["total"])
    sel = ", ".join(gb + [sub_sum, grand])
    group = (" GROUP BY " + ", ".join(gb)) if gb else ""
    return "SELECT %s FROM (%s) g%s" % (sel, grouped, group)


def metrics_sql(table_ref, spec):
    """Counts for one test: groups, coverage, failures."""
    tol = float(spec["tolerance"])
    return (
        "SELECT COUNT(*) AS n_groups, COUNT(grand_total) AS n_with_total, "
        "COUNT(subs_sum) AS n_with_subs, "
        "COALESCE(SUM(CASE WHEN ABS(subs_sum - grand_total) > %r THEN 1 ELSE 0 END), 0) AS n_fail, "
        "COALESCE(SUM(CASE WHEN subs_sum IS NOT NULL AND grand_total IS NULL THEN 1 ELSE 0 END), 0)"
        " AS n_subs_no_total FROM (%s) s" % (tol, summary_sql(table_ref, spec)))


def label_counts_sql(table_ref, spec):
    """Rows (after the row condition) matching each distinct label of the test."""
    labels = unique_labels(spec)
    parts = ["COALESCE(SUM(CASE WHEN %s THEN 1 ELSE 0 END), 0) AS l%d"
             % (label_cond(spec["cols"], lab), i) for i, lab in enumerate(labels)]
    return labels, "SELECT %s FROM (%s) f" % (", ".join(parts),
                                             filtered_sql(table_ref, spec["row_condition"]))


def unique_labels(spec):
    out = []
    for lab in [spec["total"]] + list(spec["subs"]) + list(spec["negs"]):
        key = tuple(as_list(lab))
        if key not in [tuple(as_list(x)) for x in out]:
            out.append(lab)
    return out


# ---------------------------------------------------------------- YAML specs
def extract_tests(doc, path=""):
    """Every subcomponents_sum_to_total test in one parsed schema.yml document."""
    found = []
    if not isinstance(doc, dict):
        return found
    tables = []
    for src in doc.get("sources") or []:
        tables += list((src or {}).get("tables") or [])
    tables += list(doc.get("models") or [])
    for tbl in tables:
        if not isinstance(tbl, dict):
            continue
        tests = tbl.get("data_tests") or tbl.get("tests") or []
        idx = 0
        for t in tests:
            if not (isinstance(t, dict) and "subcomponents_sum_to_total" in t):
                continue
            body = t["subcomponents_sum_to_total"] or {}
            args = dict(body.get("arguments") or {})
            for k, v in body.items():
                if k != "arguments" and k not in args:
                    args[k] = v
            found.append({"table": tbl.get("name"), "file": path, "index": idx,
                          "args": args})
            idx += 1
    return found


def normalize(raw, kind="existing"):
    """Turn a YAML test (or a proposed test) into the spec used by the SQL builders."""
    a = raw["args"]
    cols = as_list(a.get("categorical_column", a.get("categorical_columns")))
    return {
        "kind": kind,
        "table": raw["table"],
        "file": raw.get("file", ""),
        "index": raw.get("index", 0),
        "name": raw.get("name", ""),
        "group_by": as_list(a.get("group_by_columns")),
        "cols": cols,
        "value": a.get("value_column"),
        "total": a.get("total_label"),
        "subs": list(a.get("subcomponents_list") or []),
        "negs": list(a.get("negative_subcomponents_list") or []),
        "tolerance": float(a.get("tolerance", 0.01)),
        "row_condition": a.get("row_condition"),
        "min_cov": a.get("minimum_total_coverage"),
        "config": a.get("config") or {},
    }


def allowed_failures(config):
    """Failures dbt tolerates before an error; None if the test only warns."""
    config = config or {}
    if str(config.get("severity", "error")).strip().lower() == "warn":
        return None
    rule = str(config.get("error_if", "!=0")).replace(" ", "")
    m = re.fullmatch(r"(>=|>|!=)(\d+)", rule)
    if not m:
        return None
    op, n = m.group(1), int(m.group(2))
    if op == ">":
        return n
    if op == ">=":
        return n - 1
    return 0 if n == 0 else None


def dbt_failures(m, spec):
    """Rows the dbt test would return: failing groups, plus coverage rows if enabled."""
    n = m["n_fail"]
    cov = spec.get("min_cov")
    if cov is not None and m["n_with_total"] < float(cov) * m["n_groups"]:
        n += m["n_subs_no_total"]
    return n


# ---------------------------------------------------------------- proposals
def proposed_specs():
    """Candidate replacements for the utility plant changes totals test (Part E)."""
    specs = []
    for table in (UPC, UPO):
        for value in ("ending_balance", "additions", "retirements", "adjustments_and_transfers"):
            specs.append({"table": table, "name": "in_service_items_%s" % value, "args": {
                "group_by_columns": ["borrower_id_rus", "report_date"],
                "categorical_column": "utility_plant_item",
                "value_column": value,
                "subcomponents_list": list(IN_SERVICE_ITEMS),
                "total_label": "total",
                "tolerance": 10,
                "row_condition": "utility_plant_group = 'utility_plant_in_service'",
            }})
        for value in ("ending_balance", "additions"):
            specs.append({"table": table, "name": "total_plant_%s" % value, "args": {
                "group_by_columns": ["borrower_id_rus", "report_date"],
                "categorical_column": ["utility_plant_group", "utility_plant_item"],
                "value_column": value,
                "subcomponents_list": [["utility_plant_in_service", "total"],
                                       ["total_utility_plant", "construction_work_in_progress"]],
                "total_label": ["total_utility_plant", "total"],
                "tolerance": 10,
            }})
    # Negative control: distribution plant (the largest item) left out, must fail.
    specs.append({"table": UPC, "name": "NEG_CONTROL_no_distribution", "args": {
        "group_by_columns": ["borrower_id_rus", "report_date"],
        "categorical_column": "utility_plant_item",
        "value_column": "ending_balance",
        "subcomponents_list": [i for i in IN_SERVICE_ITEMS if i != "distribution"],
        "total_label": "total",
        "tolerance": 10,
        "row_condition": "utility_plant_group = 'utility_plant_in_service'",
    }})
    return specs


SPECIFIC_SQL = {
    "soo_other_capital_credits_ytd": (
        "SELECT COUNT(*) AS n, COUNT(opex_report_month) AS nn_month, COUNT(opex_ytd) AS nn_ytd, "
        "COUNT(opex_ytd_budget) AS nn_budget FROM {t} WHERE opex_type = 'other_capital_credits_ytd'"),
    "soo_other_capital_credits": (
        "SELECT COUNT(*) AS n, COUNT(opex_report_month) AS nn_month, COUNT(opex_ytd) AS nn_ytd, "
        "COUNT(opex_ytd_budget) AS nn_budget FROM {t} WHERE opex_type = 'other_capital_credits'"),
    "soo_idc_credit_label": (
        "SELECT COUNT(*) AS n FROM {t} WHERE opex_type = 'interest_charged_to_construction_credit'"),
    "soo_idc_label": (
        "SELECT COUNT(*) AS n, "
        "COALESCE(SUM(CASE WHEN opex_report_month < 0 THEN 1 ELSE 0 END), 0) AS neg_month, "
        "COALESCE(SUM(CASE WHEN opex_ytd < 0 THEN 1 ELSE 0 END), 0) AS neg_ytd, "
        "COALESCE(SUM(CASE WHEN opex_ytd_budget < 0 THEN 1 ELSE 0 END), 0) AS neg_budget "
        "FROM {t} WHERE opex_type = 'interest_charged_to_construction'"),
    "soo_opex_types": (
        "SELECT opex_group, opex_type, COUNT(*) AS n FROM {t} GROUP BY 1, 2 ORDER BY 1, 2"),
    "upc_groups_items": (
        "SELECT utility_plant_group, utility_plant_item, COUNT(*) AS n, COUNT(ending_balance) AS nn "
        "FROM {t} GROUP BY 1, 2 ORDER BY 1, 2"),
}

CROSS_SQL = (
    "WITH a AS (SELECT borrower_id_rus, report_date, asset_type, SUM(ending_balance) AS v "
    "FROM {a} WHERE asset_type IN ('utility_plant_in_service', 'construction_work_in_progress', "
    "'total_utility_plant') GROUP BY 1, 2, 3), "
    "e AS (SELECT borrower_id_rus, report_date, CASE "
    "WHEN utility_plant_group = 'utility_plant_in_service' AND utility_plant_item = 'total' "
    "THEN 'utility_plant_in_service' "
    "WHEN utility_plant_group = 'total_utility_plant' "
    "AND utility_plant_item = 'construction_work_in_progress' THEN 'construction_work_in_progress' "
    "WHEN utility_plant_group = 'total_utility_plant' AND utility_plant_item = 'total' "
    "THEN 'total_utility_plant' END AS asset_type, SUM(ending_balance) AS v FROM {e} GROUP BY 1, 2, 3) "
    "SELECT a.asset_type, COUNT(*) AS n_both, "
    "SUM(CASE WHEN ABS(a.v - e.v) > 10 THEN 1 ELSE 0 END) AS n_differ "
    "FROM a JOIN e USING (borrower_id_rus, report_date, asset_type) "
    "WHERE a.v IS NOT NULL AND e.v IS NOT NULL GROUP BY 1 ORDER BY 1")


# ---------------------------------------------------------------- scoring
def evaluate(results, specific):
    """Score P1-P6 of README.md. results: list of dicts with spec + metrics."""
    v = {}
    ex = [r for r in results if r["kind"] == "existing" and r["table"] in (UPC, UPO)]
    ok_ex = [r for r in ex if "error" not in r]
    if not ok_ex or not any(r["table"] == UPC for r in ok_ex):
        v["P1"] = "not tested"
    else:
        v["P1"] = "held" if all(r["n_groups"] > 0 and r["n_with_total"] == 0
                                for r in ok_ex) else "failed"

    prop = [r for r in results if r["kind"] == "proposed" and r["table"] == UPC
            and not r["name"].startswith("NEG")]
    neg = [r for r in results if r["kind"] == "proposed" and r["name"].startswith("NEG")]
    if len(prop) != 6 or any("error" in r for r in prop) or len(neg) != 1 or "error" in neg[0]:
        v["P2"] = "not tested"
        v["P3"] = "not tested"
    else:
        v["P2"] = "held" if all(r["n_with_total"] >= 0.9 * r["n_groups"] and r["n_groups"] > 0
                                for r in prop) else "failed"
        n = neg[0]
        v["P3"] = "held" if (n["n_with_total"] > 0 and n["n_fail"] >= 0.9 * n["n_with_total"]) \
            else "failed"

    a = specific.get("soo_other_capital_credits_ytd")
    b = specific.get("soo_other_capital_credits")
    if not a or not b or "error" in a or "error" in b:
        v["P4"] = "not tested"
        v["P5"] = "not tested"
    else:
        v["P4"] = "held" if (a["n"] > 0 and a["nn_ytd"] == 0 and a["nn_budget"] == 0
                             and b["nn_month"] == 0) else "failed"
        v["P5"] = "held" if (a["n"] > 0 and a["nn_month"] > 0) else "failed"

    c = specific.get("soo_idc_credit_label")
    d = specific.get("soo_idc_label")
    if not c or not d or "error" in c or "error" in d:
        v["P6"] = "not tested"
    else:
        v["P6"] = "held" if (c["n"] == 0 and d["n"] > 0) else "failed"

    ev = [r for r in results if r["kind"] == "existing" and "error" not in r
          and r.get("allowed") is not None]
    if len(ev) < 10:
        v["P7"] = "not tested"
    else:
        within = sum(1 for r in ev if r["dbt_failures"] <= r["allowed"])
        v["P7"] = "held" if within >= 0.95 * len(ev) else "failed"
    return v


# ---------------------------------------------------------------- running
def sh(cmd, cwd=None, timeout=1800):
    print("$ " + " ".join(cmd), flush=True)
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return p.returncode, p.stdout, p.stderr


def head_size(url):
    req = urllib.request.Request(url, headers=UA, method="HEAD")
    with urllib.request.urlopen(req, timeout=120) as r:
        return int(r.headers.get("Content-Length") or 0)


def fetch(table, data_dir, budget):
    """Download one nightly table; returns (path or None, note)."""
    path = os.path.join(data_dir, table + ".parquet")
    if os.path.exists(path):
        return path, "cached"
    url = NIGHTLY + table + ".parquet"
    try:
        size = head_size(url)
    except Exception as exc:  # noqa: BLE001
        return None, "head failed: %s" % exc
    if size > MAX_TABLE_BYTES:
        return None, "skipped: %d bytes" % size
    if size > budget[0]:
        return None, "skipped: total download budget"
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=900) as r, open(path, "wb") as f:
        shutil.copyfileobj(r, f, 1 << 20)
    budget[0] -= os.path.getsize(path)
    return path, "downloaded %d bytes" % os.path.getsize(path)


def run_spec(con, path, spec):
    ref = "read_parquet(%s)" % ql(path)
    row = con.execute(metrics_sql(ref, spec)).fetchone()
    m = dict(zip(["n_groups", "n_with_total", "n_with_subs", "n_fail", "n_subs_no_total"],
                 [int(x or 0) for x in row]))
    labels, sql = label_counts_sql(ref, spec)
    counts = con.execute(sql).fetchone()
    m["label_rows"] = [{"label": lab, "rows": int(n or 0)} for lab, n in zip(labels, counts)]
    m["absent_labels"] = [x["label"] for x in m["label_rows"] if x["rows"] == 0]
    m["coverage"] = round(m["n_with_total"] / m["n_groups"], 4) if m["n_groups"] else None
    return m


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--clone-dir", default="/tmp/pudl")
    a = ap.parse_args(argv)
    import duckdb  # noqa: PLC0415
    import yaml  # noqa: PLC0415

    os.makedirs(a.out_dir, exist_ok=True)
    os.makedirs(a.data_dir, exist_ok=True)
    result = {"tool": "totcov 0.1.0", "tables": {}, "results": [], "specific": {}}

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

    raws = []
    files = sorted(glob.glob(os.path.join(a.clone_dir, "dbt", "models", "**", "schema.yml"),
                             recursive=True))
    result["schema_files"] = len(files)
    for f in files:
        with open(f, encoding="utf-8") as fh:
            doc = yaml.safe_load(fh)
        raws += extract_tests(doc, os.path.relpath(f, a.clone_dir))
    specs = [normalize(r) for r in raws] + [normalize(r, "proposed") for r in proposed_specs()]
    print("tests found: %d existing, %d proposed" % (len(raws), len(specs) - len(raws)), flush=True)

    tables = sorted({s["table"] for s in specs} | {SOO, ASSETS, UPC})
    budget = [MAX_TOTAL_BYTES]
    paths = {}
    for t in tables:
        try:
            p, note = fetch(t, a.data_dir, budget)
        except Exception as exc:  # noqa: BLE001
            p, note = None, "download failed: %s" % exc
        result["tables"][t] = note
        print(t, note, flush=True)
        if p:
            paths[t] = p

    con = duckdb.connect()
    con.execute("SET memory_limit = '1200MB'")
    con.execute("SET threads = 2")
    for s in specs:
        r = dict(s)
        r["allowed"] = allowed_failures(s["config"]) if s["kind"] == "existing" else None
        if s["table"] not in paths:
            r["error"] = "table not available: %s" % result["tables"].get(s["table"])
        else:
            try:
                r.update(run_spec(con, paths[s["table"]], s))
                r["dbt_failures"] = dbt_failures(r, s)
            except Exception as exc:  # noqa: BLE001
                r["error"] = str(exc)[:500]
        result["results"].append(r)

    if SOO in paths:
        ref = "read_parquet(%s)" % ql(paths[SOO])
        for key in ("soo_other_capital_credits_ytd", "soo_other_capital_credits",
                    "soo_idc_credit_label", "soo_idc_label"):
            try:
                cur = con.execute(SPECIFIC_SQL[key].format(t=ref))
                names = [d[0] for d in cur.description]
                result["specific"][key] = dict(zip(names, [int(x or 0) for x in cur.fetchone()]))
            except Exception as exc:  # noqa: BLE001
                result["specific"][key] = {"error": str(exc)[:500]}
        try:
            rows = con.execute(SPECIFIC_SQL["soo_opex_types"].format(t=ref)).fetchall()
            result["specific"]["soo_opex_types"] = [list(map(str, x[:2])) + [int(x[2])] for x in rows]
        except Exception as exc:  # noqa: BLE001
            result["specific"]["soo_opex_types"] = {"error": str(exc)[:500]}
    if UPC in paths:
        ref = "read_parquet(%s)" % ql(paths[UPC])
        try:
            rows = con.execute(SPECIFIC_SQL["upc_groups_items"].format(t=ref)).fetchall()
            result["specific"]["upc_groups_items"] = [[str(x[0]), str(x[1]), int(x[2]), int(x[3])]
                                                      for x in rows]
        except Exception as exc:  # noqa: BLE001
            result["specific"]["upc_groups_items"] = {"error": str(exc)[:500]}
    if UPC in paths and ASSETS in paths:
        try:
            rows = con.execute(CROSS_SQL.format(
                a="read_parquet(%s)" % ql(paths[ASSETS]),
                e="read_parquet(%s)" % ql(paths[UPC]))).fetchall()
            result["specific"]["cross_assets_vs_plant_changes"] = [
                [str(x[0]), int(x[1]), int(x[2] or 0)] for x in rows]
        except Exception as exc:  # noqa: BLE001
            result["specific"]["cross_assets_vs_plant_changes"] = {"error": str(exc)[:500]}

    result["verdicts"] = evaluate(result["results"], result["specific"])
    with open(os.path.join(a.out_dir, "totcov.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1, default=str)
    with open(os.path.join(a.out_dir, "totcov.csv"), "w", encoding="utf-8") as fh:
        fh.write("kind,table,index,name,value,total_label,n_groups,n_with_total,coverage,"
                 "n_fail,allowed,absent_labels,error\n")
        for r in result["results"]:
            fh.write(",".join('"%s"' % str(x).replace('"', "'") for x in [
                r["kind"], r["table"], r["index"], r["name"], r["value"], r["total"],
                r.get("n_groups", ""), r.get("n_with_total", ""), r.get("coverage", ""),
                r.get("n_fail", ""), r.get("allowed", ""),
                ";".join(str(x) for x in r.get("absent_labels", [])), r.get("error", "")]) + "\n")
    for r in result["results"]:
        print("%-9s %-52s %-28s %-34s groups=%s total=%s fail=%s allowed=%s absent=%s %s" % (
            r["kind"], r["table"], r["value"], str(r["total"])[:34], r.get("n_groups"),
            r.get("n_with_total"), r.get("n_fail"), r.get("allowed"),
            r.get("absent_labels"), r.get("error", "")))
    print("specific", json.dumps(result["specific"], default=str)[:6000])
    print("verdicts", json.dumps(result["verdicts"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
