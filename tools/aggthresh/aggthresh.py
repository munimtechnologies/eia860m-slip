# Copyright 2026 Munim, Inc.
# Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working in the name of MV2 of Munim, Inc. (mv2@munimtech.com).
"""aggthresh: PUDL aggregate dbt tests whose error_if threshold can never be reached.

dbt counts a test's failures as the number of rows its query returns, and
error_if compares that count with a threshold (default "!=0"). The
dbt_expectations aggregate tests (expect_column_min_to_be_between, ..._max_...,
..._sum_..., ...) compile to one aggregate row when no group_by is given
(metaplane/dbt-expectations macros/schema_tests/_generalized/
expression_is_true.sql), so they return 0 or 1 rows. With error_if ">13" or
">1600", a failing aggregate test returns 1 row, 1 > 13 is false, and dbt
reports "warn". PUDL's validation (src/pudl/validate/dbt.py) runs `dbt build`
with no --warn-error, so a warn never fails the build: such a test cannot fail.

Part 1 (static) streams PUDL's source tarball at a pinned commit, reads every
dbt YAML file, and lists those tests two independent ways (YAML parse and a
line scanner) so the two counts can be compared.

Part 2 (data) runs the exact query shape dbt_expectations compiles for the
three min tests on core_rus7__yearly_statement_of_operations against PUDL's
nightly parquet, next to the row-level count the thresholds look sized for.
It also measures a column-map slip in the same table: the RUS-7 raw field
'othercapitalcreditsthismonth' is mapped to
'patronage_capital_or_margins_other_capital_credits_ytd_opex_report_month', so
the transform's regex files it under opex_type 'other_capital_credits_ytd'
instead of 'other_capital_credits'.

Pre-registered predictions are in docs/aggthresh.md. It only measures;
nothing is sent to PUDL.
"""
import argparse
import csv
import json
import os
import re
import sys
import tarfile
import time
import urllib.request

TOOL = "aggthresh 0.1.0"
PUDL_COMMIT = "551954e7af0e3bb7c7c314ac0ee1734a0efbedaa"
TARBALL = "https://codeload.github.com/catalyst-cooperative/pudl/tar.gz/" + PUDL_COMMIT
SOO_URL = ("https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/"
           "core_rus7__yearly_statement_of_operations.parquet")
UA = "aggthresh/0.1 (MV2 of Munim, Inc.; mv2@munimtech.com)"

# dbt_expectations tests that compile to one aggregate row per group_by group
# (one row in all when there is no group_by).
AGGREGATE_TESTS = {
    "expect_column_min_to_be_between",
    "expect_column_max_to_be_between",
    "expect_column_mean_to_be_between",
    "expect_column_median_to_be_between",
    "expect_column_sum_to_be_between",
    "expect_column_stdev_to_be_between",
    "expect_column_quantile_values_to_be_between",
    "expect_column_proportion_of_unique_values_to_be_between",
    "expect_column_unique_value_count_to_be_between",
    "expect_column_distinct_count_to_equal",
    "expect_column_distinct_count_to_be_greater_than",
    "expect_column_distinct_count_to_be_less_than",
    "expect_table_row_count_to_be_between",
    "expect_table_row_count_to_equal",
}

COND_RE = re.compile(r"^\s*(>=|<=|!=|<>|==|=|>|<)\s*(-?\d+(?:\.\d+)?)\s*$")
SIZING_RE = re.compile(
    r"(%|\brecords?\b|\brows?\b|\binstances?\b|\bcases\b|\bvalues\b|of the data)",
    re.IGNORECASE)


# ---------------------------------------------------------------- thresholds
def parse_cond(cond):
    """Parse a dbt error_if/warn_if string such as '>13' into (op, number)."""
    m = COND_RE.match(str(cond))
    if not m:
        return None
    return m.group(1), float(m.group(2))


def cond_true(op, n, f):
    if op == ">":
        return f > n
    if op == ">=":
        return f >= n
    if op == "<":
        return f < n
    if op == "<=":
        return f <= n
    if op in ("=", "=="):
        return f == n
    return f != n  # != and <>


def can_error(error_if, severity=None, max_failures=1):
    """Can a test whose query returns at most max_failures rows reach 'fail'?

    Returns (True/False/None, reason). None means the condition is not a
    simple comparison this tool understands."""
    if severity is not None and str(severity).strip().lower() == "warn":
        return False, "severity_warn"
    cond = "!=0" if error_if is None else error_if
    parsed = parse_cond(cond)
    if parsed is None:
        return None, "unparsed"
    op, n = parsed
    return any(cond_true(op, n, f) for f in range(1, max_failures + 1)), "ok"


# ---------------------------------------------------------------- YAML method
def split_test(item):
    """A dbt test entry is 'name' or {'name': body}. Return (name, body)."""
    if isinstance(item, str):
        return item, {}
    if isinstance(item, dict) and len(item) == 1:
        name, body = next(iter(item.items()))
        return str(name), (body if isinstance(body, dict) else {})
    return None, {}


def test_params(body):
    args = body.get("arguments") or {}
    if not isinstance(args, dict):
        args = {}
    config = body.get("config") or {}
    if not isinstance(config, dict):
        config = {}
    return {
        "error_if": config.get("error_if", body.get("error_if")),
        "severity": config.get("severity", body.get("severity")),
        "group_by": args.get("group_by", body.get("group_by")),
        "row_condition": args.get("row_condition", body.get("row_condition")),
        "description": body.get("description") or config.get("description") or "",
    }


def iter_tests(doc):
    """Yield (table, column, test_name, body) for every test in a dbt YAML doc."""
    if not isinstance(doc, dict):
        return
    for top in ("sources", "models"):
        for src in doc.get(top) or []:
            if not isinstance(src, dict):
                continue
            tables = src.get("tables") if top == "sources" else [src]
            for table in tables or []:
                if not isinstance(table, dict):
                    continue
                tname = table.get("name")
                for item in (table.get("data_tests") or table.get("tests") or []):
                    name, body = split_test(item)
                    if name:
                        yield tname, None, name, body
                for col in table.get("columns") or []:
                    if not isinstance(col, dict):
                        continue
                    for item in (col.get("data_tests") or col.get("tests") or []):
                        name, body = split_test(item)
                        if name:
                            yield tname, col.get("name"), name, body


def classify(name, params):
    short = name.split(".")[-1]
    if short not in AGGREGATE_TESTS:
        return "row_level_or_custom"
    if params["group_by"]:
        return "aggregate_grouped"
    ok, reason = can_error(params["error_if"], params["severity"])
    if reason == "severity_warn":
        return "aggregate_severity_warn"
    if ok is None:
        return "aggregate_unparsed_error_if"
    if ok:
        return "aggregate_ok"
    return "aggregate_unreachable_error_if"


def scan_docs(docs):
    """docs: list of (path, parsed_yaml). Return one dict per test."""
    out = []
    for path, doc in docs:
        for table, column, name, body in iter_tests(doc):
            p = test_params(body)
            out.append({
                "file": path, "table": table, "column": column or "",
                "test": name, "error_if": "" if p["error_if"] is None else str(p["error_if"]),
                "severity": "" if p["severity"] is None else str(p["severity"]),
                "group_by": json.dumps(p["group_by"]) if p["group_by"] else "",
                "description": " ".join(str(p["description"]).split()),
                "category": classify(name, p),
            })
    return out


# ---------------------------------------------------------------- line method
TESTS_KEY_RE = re.compile(r"^(\s*)(data_tests|tests):\s*(#.*)?$")
ITEM_RE = re.compile(r"^(\s*)-\s+((?:[a-z_]+\.)?[a-z_0-9]+)\s*:?\s*(#.*)?$")
ERROR_IF_RE = re.compile(r"""^\s*error_if:\s*(["']?)([^"'#]*)\1\s*(#.*)?$""")
SEVERITY_RE = re.compile(r"""^\s*severity:\s*(["']?)([A-Za-z]+)\1""")
GROUP_BY_RE = re.compile(r"^\s*group_by:")


def indent(line):
    return len(line) - len(line.lstrip(" "))


def line_scan(text):
    """Independent line-based scan. Return one dict per test item found under
    a data_tests/tests key: name, line (1-based), error_if, comment, severity,
    has_group_by, block_text."""
    lines = text.splitlines()
    out = []
    i = 0
    while i < len(lines):
        m = TESTS_KEY_RE.match(lines[i])
        if not m:
            i += 1
            continue
        key_indent = len(m.group(1))
        item_indent = None
        j = i + 1
        cur = None
        while j < len(lines):
            line = lines[j]
            if not line.strip() or line.lstrip().startswith("#"):
                j += 1
                continue
            ind = indent(line)
            is_item = line.lstrip().startswith("- ")
            if item_indent is None:
                if is_item and ind >= key_indent:
                    item_indent = ind
                else:
                    break
            if ind < item_indent or (ind == item_indent and not is_item):
                break
            if ind == item_indent and is_item:
                if cur:
                    out.append(cur)
                im = ITEM_RE.match(line)
                cur = {"name": im.group(2) if im else line.strip()[2:].split(":")[0].strip(),
                       "line": j + 1, "error_if": None, "comment": "", "severity": None,
                       "has_group_by": False, "block_text": ""}
            elif cur is not None:
                cur["block_text"] += line.strip() + "\n"
                em = ERROR_IF_RE.match(line)
                if em:
                    cur["error_if"] = em.group(2).strip()
                    cur["comment"] = (em.group(3) or "").lstrip("#").strip()
                sm = SEVERITY_RE.match(line)
                if sm:
                    cur["severity"] = sm.group(2)
                if GROUP_BY_RE.match(line):
                    cur["has_group_by"] = True
            j += 1
        if cur:
            out.append(cur)
        i = j if j > i else i + 1
    return out


def line_flagged(item):
    short = item["name"].split(".")[-1]
    if short not in AGGREGATE_TESTS or item["has_group_by"]:
        return False
    if item["error_if"] is None:
        return False
    ok, reason = can_error(item["error_if"], item["severity"])
    return ok is False and reason == "ok"


def has_sizing_language(text):
    return bool(SIZING_RE.search(text or ""))


# ---------------------------------------------------------------- fetching
def iter_dbt_yaml(url=TARBALL):
    """Stream the PUDL tarball; yield (repo path, text) for dbt/**.yml."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=600) as resp:
        with tarfile.open(fileobj=resp, mode="r|gz") as tf:
            for m in tf:
                if not m.isfile():
                    continue
                parts = m.name.split("/", 1)
                if len(parts) < 2:
                    continue
                rel = parts[1]
                if rel.startswith("dbt/") and rel.endswith((".yml", ".yaml")):
                    fh = tf.extractfile(m)
                    if fh is not None:
                        yield rel, fh.read().decode("utf-8")


# ---------------------------------------------------------------- RUS-7 SOO
SOO_ROW_CONDITION = ("opex_type != 'interest_charged_to_construction_credit' and "
                     "opex_group != 'patronage_capital_or_margins'")
SOO_THRESHOLDS = {"opex_report_month": 6750, "opex_ytd": 1600, "opex_ytd_budget": 810}
PATRONAGE_SUBS = [
    "total_minus",
    "non_operating_margins_interest",
    "construction_funds_allowance",
    "equity_investment_losses",
    "non_operating_margins_other",
    "generation_and_transmission_capital",
    "other_capital_credits",
    "extraordinary_items",
]
VALUE_COLS = ["opex_report_month", "opex_ytd", "opex_ytd_budget"]


def occ_checks(rows):
    """rows: (borrower, report_date, opex_group, opex_type, month, ytd, budget)
    for the two patronage groups. Score O1-O3."""
    ytd_rows = [r for r in rows if r[3] == "other_capital_credits_ytd"]
    occ_rows = [r for r in rows if r[3] == "other_capital_credits"]
    res = {}
    res["O1"] = {
        "claim": ("rows with opex_type 'other_capital_credits_ytd' exist, all in group "
                  "patronage_capital_or_margins, and none has an opex_ytd or opex_ytd_budget value"),
        "n_rows": len(ytd_rows),
        "groups": sorted({str(r[2]) for r in ytd_rows}),
        "n_with_ytd": sum(1 for r in ytd_rows if r[5] is not None),
        "n_with_budget": sum(1 for r in ytd_rows if r[6] is not None),
        "n_with_month": sum(1 for r in ytd_rows if r[4] is not None),
    }
    res["O1"]["held"] = (len(ytd_rows) > 0
                         and res["O1"]["groups"] == ["patronage_capital_or_margins"]
                         and res["O1"]["n_with_ytd"] == 0 and res["O1"]["n_with_budget"] == 0)
    res["O2"] = {
        "claim": "no row with opex_type 'other_capital_credits' has an opex_report_month value",
        "n_rows": len(occ_rows),
        "n_with_month": sum(1 for r in occ_rows if r[4] is not None),
        "n_with_ytd": sum(1 for r in occ_rows if r[5] is not None),
    }
    res["O2"]["held"] = len(occ_rows) > 0 and res["O2"]["n_with_month"] == 0
    big = [r for r in ytd_rows if r[4] is not None and abs(r[4]) > 10]
    res["O3"] = {
        "claim": "at least one borrower-year has |this-month other capital credits| > 10 (USD), filed under 'other_capital_credits_ytd'",
        "n_borrower_years": len({(r[0], r[1]) for r in big}),
        "n_nonzero": sum(1 for r in ytd_rows if r[4] not in (None, 0, 0.0)),
    }
    res["O3"]["held"] = res["O3"]["n_borrower_years"] >= 1
    return res


def patronage_total_failures(rows, value_idx, relabel, drop=(), tol=10.0):
    """Check total (line 28) = sum of lines 20-27 per borrower-year.

    value_idx: 4 month, 5 ytd, 6 budget. relabel: count
    'other_capital_credits_ytd' as 'other_capital_credits'. Rows whose total
    is NULL are skipped; NULL subcomponents count as 0."""
    by_key = {}
    for r in rows:
        t = r[3]
        if relabel and t == "other_capital_credits_ytd":
            t = "other_capital_credits"
        v = r[value_idx]
        d = by_key.setdefault((r[0], r[1]), {})
        if v is not None:
            d[t] = (d.get(t) or 0.0) + float(v)
        elif t not in d:
            d[t] = None
    subs = [s for s in PATRONAGE_SUBS if s not in drop]
    checked = failed = 0
    for d in by_key.values():
        total = d.get("total")
        if total is None:
            continue
        checked += 1
        s = sum((d.get(c) or 0.0) for c in subs)
        if abs(s - total) > tol:
            failed += 1
    return checked, failed


def totals_checks(rows):
    res = {}
    cm, fm_lab = patronage_total_failures(rows, 4, relabel=False)
    _, fm_rel = patronage_total_failures(rows, 4, relabel=True)
    res["O4"] = {
        "claim": ("a patronage-capital totals check on opex_report_month fails on more "
                  "borrower-years as labelled than with 'other_capital_credits_ytd' counted "
                  "as other_capital_credits"),
        "checked": cm, "failed_as_labelled": fm_lab, "failed_relabelled": fm_rel,
        "held": fm_lab > fm_rel,
    }
    cy, fy = patronage_total_failures(rows, 5, relabel=True)
    res["O5"] = {
        "claim": "the same check on opex_ytd (relabelled) fails on at most 5% of borrower-years",
        "checked": cy, "failed": fy,
        "fraction": (fy / cy) if cy else None,
        "held": cy > 0 and fy / cy <= 0.05,
    }
    cc, fc = patronage_total_failures(rows, 5, relabel=True, drop=("total_minus",))
    res["OC"] = {
        "claim": "control: dropping total_minus (line 20) from the subcomponents makes at least 50% of borrower-years fail on opex_ytd",
        "checked": cc, "failed": fc,
        "fraction": (fc / cc) if cc else None,
        "held": cc > 0 and fc / cc >= 0.5,
    }
    cb, fb = patronage_total_failures(rows, 6, relabel=True)
    _, fb_lab = patronage_total_failures(rows, 6, relabel=False)
    res["explore_budget"] = {"checked": cb, "failed_relabelled": fb,
                             "failed_as_labelled": fb_lab}
    _, fy_lab = patronage_total_failures(rows, 5, relabel=False)
    res["explore_ytd_as_labelled"] = {"checked": cy, "failed": fy_lab}
    return res


def soo_fetch(url=SOO_URL):
    import duckdb  # imported here so the unit tests run without it
    con = duckdb.connect()
    con.execute("SET threads=2")
    con.execute("SET memory_limit='300MB'")
    try:
        con.execute("INSTALL httpfs")
        con.execute("LOAD httpfs")
    except Exception as e:  # autoload may already cover it
        print("httpfs note:", e, file=sys.stderr)
    lit = "'" + url.replace("'", "''") + "'"
    src = "read_parquet(" + lit + ")"
    agg = {}
    for col in VALUE_COLS:
        # The query shape dbt_expectations compiles for
        # expect_column_min_to_be_between(min_value=0) with this row_condition.
        q = ("SELECT * FROM (SELECT min(" + col + ") >= 0.0 AS expression FROM " + src
             + " WHERE " + SOO_ROW_CONDITION + ") AS g WHERE NOT (expression = true)")
        dbt_rows = con.execute(q).fetchall()
        mn = con.execute("SELECT min(" + col + ") FROM " + src + " WHERE "
                         + SOO_ROW_CONDITION).fetchone()[0]
        n_neg = con.execute("SELECT count(*) FROM " + src + " WHERE (" + SOO_ROW_CONDITION
                            + ") AND " + col + " < 0").fetchone()[0]
        by_type = con.execute(
            "SELECT CAST(opex_group AS VARCHAR), CAST(opex_type AS VARCHAR), count(*) FROM "
            + src + " WHERE (" + SOO_ROW_CONDITION + ") AND " + col
            + " < 0 GROUP BY 1, 2 ORDER BY 3 DESC").fetchall()
        agg[col] = {"dbt_query_rows": len(dbt_rows),
                    "min": None if mn is None else float(mn),
                    "rows_below_zero": int(n_neg),
                    "error_if_threshold": SOO_THRESHOLDS[col],
                    "below_zero_by_type": [[g, t, int(n)] for g, t, n in by_type]}
    rows = con.execute(
        "SELECT CAST(borrower_id_rus AS VARCHAR), CAST(report_date AS VARCHAR), "
        "CAST(opex_group AS VARCHAR), CAST(opex_type AS VARCHAR), opex_report_month, "
        "opex_ytd, opex_ytd_budget FROM " + src + " WHERE CAST(opex_group AS VARCHAR) IN "
        "('patronage_and_operating_margins', 'patronage_capital_or_margins')").fetchall()
    rows = [(b, d, g, t,
             None if m is None else float(m),
             None if y is None else float(y),
             None if u is None else float(u)) for b, d, g, t, m, y, u in rows]
    types = con.execute("SELECT CAST(opex_group AS VARCHAR), CAST(opex_type AS VARCHAR), "
                        "count(*) FROM " + src + " GROUP BY 1, 2 ORDER BY 1, 2").fetchall()
    meta = con.execute("SELECT num_rows, created_by FROM parquet_file_metadata(" + lit
                       + ")").fetchall()
    return agg, rows, [[g, t, int(n)] for g, t, n in types], [list(m) for m in meta]


def score_agg(agg):
    res = {}
    for key, col in (("A3a", "opex_report_month"), ("A3b", "opex_ytd"),
                     ("A3c", "opex_ytd_budget")):
        a = agg[col]
        res[key] = {
            "claim": ("the dbt_expectations query for the " + col + " min test returns exactly "
                      "1 row (so the test can only warn under error_if '>"
                      + str(a["error_if_threshold"]) + "'), while more than 1 row is below 0"),
            "dbt_query_rows": a["dbt_query_rows"], "rows_below_zero": a["rows_below_zero"],
            "held": a["dbt_query_rows"] == 1 and a["rows_below_zero"] > 1,
        }
    return res


# ---------------------------------------------------------------- scoring scan
def find(tests, table, column, short):
    return [t for t in tests if t["table"] == table and t["column"] == column
            and t["test"].split(".")[-1] == short]


def score_scan(tests, line_items):
    """tests: from scan_docs over dbt/schema_inputs. line_items: list of
    (path, item) from line_scan over the same files."""
    res = {}
    flagged = [t for t in tests if t["category"] == "aggregate_unreachable_error_if"]
    res["A1"] = {
        "claim": ("at least 40 aggregate dbt_expectations tests in dbt/schema_inputs have no "
                  "group_by and an error_if that one failing row cannot reach"),
        "n_flagged": len(flagged),
        "n_tables": len({t["table"] for t in flagged}),
        "by_test": {},
        "held": len(flagged) >= 40,
    }
    for t in flagged:
        k = t["test"].split(".")[-1]
        res["A1"]["by_test"][k] = res["A1"]["by_test"].get(k, 0) + 1
    line_flag = [(p, it) for p, it in line_items if line_flagged(it)]
    sized = [(p, it) for p, it in line_flag
             if has_sizing_language(it["comment"]) or has_sizing_language(it["block_text"])]
    res["A2"] = {
        "claim": ("at least 3 flagged tests size their threshold in rows, records, cases, "
                  "values or percent of the data (comment or description)"),
        "n_sized": len(sized),
        "examples": [[p, it["line"], it["error_if"], it["comment"]] for p, it in sized[:12]],
        "held": len(sized) >= 3,
    }
    res["S1"] = {
        "claim": "the line scanner flags exactly as many tests as the YAML parse",
        "yaml_count": len(flagged), "line_count": len(line_flag),
        "held": len(flagged) == len(line_flag),
    }
    k1 = find(tests, "core_rus7__yearly_statement_of_operations", "opex_ytd",
              "expect_column_min_to_be_between")
    res["K1"] = {"claim": "control: RUS-7 SOO opex_ytd min test (error_if '>1600') is flagged",
                 "found": len(k1),
                 "held": len(k1) == 1 and k1[0]["category"] == "aggregate_unreachable_error_if"}
    k2 = find(tests, "core_epamats__hourly_emissions", "operating_time_hours",
              "expect_column_values_to_be_between")
    res["K2"] = {"claim": ("control: EPA MATS operating_time_hours values test (row level, "
                           "error_if '>0') is not flagged"),
                 "found": len(k2),
                 "held": len(k2) == 1 and k2[0]["category"] == "row_level_or_custom"}
    k3 = find(tests, "core_epamats__hourly_emissions", "heat_content_mmbtu",
              "expect_column_min_to_be_between")
    res["K3"] = {"claim": "control: EPA MATS heat_content_mmbtu min test (error_if '>13') is flagged",
                 "found": len(k3),
                 "held": len(k3) == 1 and k3[0]["category"] == "aggregate_unreachable_error_if"}
    cats = {}
    for t in tests:
        cats[t["category"]] = cats.get(t["category"], 0) + 1
    res["explore"] = {
        "n_tests": len(tests),
        "categories": cats,
        "custom_with_error_if": sorted({t["test"] for t in tests
                                        if t["category"] == "row_level_or_custom"
                                        and t["error_if"] and t["error_if"] != "!=0"}),
    }
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description=TOOL)
    ap.add_argument("--tarball", default=TARBALL)
    ap.add_argument("--soo-url", default=SOO_URL)
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    t0 = time.time()
    import yaml  # imported here so the unit tests run without PyYAML

    texts = list(iter_dbt_yaml(args.tarball))
    inputs = [(p, t) for p, t in texts if p.startswith("dbt/schema_inputs/")]
    models = [(p, t) for p, t in texts if p.startswith("dbt/models/")]
    parse_errors = []

    def load(pairs):
        docs = []
        for p, t in pairs:
            try:
                docs.append((p, yaml.safe_load(t)))
            except Exception as e:  # report, never hide
                parse_errors.append([p, str(e)[:200]])
        return docs

    tests = scan_docs(load(inputs))
    model_tests = scan_docs(load(models))
    line_items = [(p, it) for p, t in inputs for it in line_scan(t)]
    res = score_scan(tests, line_items)
    res["explore"]["n_schema_inputs_files"] = len(inputs)
    res["explore"]["yaml_parse_errors"] = parse_errors
    res["explore"]["models_flagged"] = sum(
        1 for t in model_tests if t["category"] == "aggregate_unreachable_error_if")
    with open(os.path.join(args.out_dir, "aggthresh-tests.csv"), "w", newline="",
              encoding="utf-8") as fh:
        cols = ["file", "table", "column", "test", "error_if", "severity", "group_by",
                "category", "description"]
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for t in tests:
            if t["category"].startswith("aggregate"):
                w.writerow({c: t[c] for c in cols})
    with open(os.path.join(args.out_dir, "aggthresh-lines.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["file", "line", "test", "error_if", "comment"])
        for p, it in line_items:
            if line_flagged(it):
                w.writerow([p, it["line"], it["name"], it["error_if"], it["comment"]])

    agg, rows, types, meta = soo_fetch(args.soo_url)
    res.update(score_agg(agg))
    res.update(occ_checks(rows))
    res.update(totals_checks(rows))
    res["explore_soo"] = {"agg": agg, "opex_types": types}
    res["meta"] = {"tool": TOOL, "pudl_commit": PUDL_COMMIT, "tarball": args.tarball,
                   "soo_url": args.soo_url, "parquet_metadata": meta,
                   "seconds": round(time.time() - t0, 1),
                   "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    with open(os.path.join(args.out_dir, "aggthresh-results.json"), "w",
              encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, sort_keys=True)
    for k in ["A1", "A2", "S1", "K1", "K2", "K3", "A3a", "A3b", "A3c",
              "O1", "O2", "O3", "O4", "O5", "OC"]:
        r = res[k]
        print(k, "HELD" if r["held"] else "FAILED", json.dumps(r, sort_keys=True))
    print("explore", json.dumps(res["explore"], sort_keys=True))
    print("meta", json.dumps(res["meta"], sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
