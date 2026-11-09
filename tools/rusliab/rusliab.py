# rusliab.py - candidate totals checks for PUDL's RUS Form 7 balance sheet liabilities.
# By MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
# Apache-2.0.
#
# Re-implements the semantics of PUDL's dbt macro `subcomponents_sum_to_total`
# (dbt/macros/expect_subcomponents_sum_to_total.sql, main, 2026-11-09) in plain Python:
#   1. group by group_by_columns + categorical column, SUM(value) (NULL if all values NULL)
#   2. per group: subcomponents_sum = SUM(-v for negative labels, +v for listed labels)
#      (NULL if no non-null contribution); grand_total = MAX(v of total label)
#   3. failure if both non-null and ABS(subcomponents_sum - grand_total) > tolerance
# and runs candidate tests (from the table's own `total_` columns, PUDL issue #5154)
# on the nightly parquet files. It only measures; it changes nothing in PUDL.
import argparse
import json
import os
import sys
import urllib.request
from collections import defaultdict

NIGHTLY = "https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/"
GROUP = ("borrower_id_rus", "report_date")
CAT = "liability_type"
VAL = "ending_balance"
TOL = 10

MARGINS = ["memberships", "patronage_capital", "operating_margins_prior_years",
           "operating_margins_current_year", "non_operating_margins",
           "other_margins_and_equities"]
LTD = ["long_term_debt_rus", "long_term_debt_ffb_rus_guaranteed",
       "long_term_debt_other_rus_guaranteed", "long_term_debt_other",
       "long_term_debt_rus_economic_development"]
NONCURRENT = ["noncurrent_obligations_under_capital_leases",
              "noncurrent_obligations_asset_retirement"]
CURRENT = ["notes_payable", "accounts_payable", "consumer_deposits",
           "current_maturities_long_term_debt", "economic_development",
           "current_maturities_capital_leases", "other_current_and_accrued_liabilities"]
GRAND = ["total_margins_and_equities", "total_long_term_debt",
         "total_noncurrent_obligations", "total_current_and_accrued_liabilities",
         "regulatory", "other_deferred_credits"]

# name -> (subcomponents, negative subcomponents, total label)
TESTS = {
    "margins_and_equities": (MARGINS, [], "total_margins_and_equities"),
    "long_term_debt_less_unapplied": (LTD, ["payments_unapplied"], "total_long_term_debt"),
    "long_term_debt_plus_unapplied": (LTD + ["payments_unapplied"], [], "total_long_term_debt"),
    "long_term_debt_without_unapplied": (LTD, [], "total_long_term_debt"),
    "noncurrent_obligations": (NONCURRENT, [], "total_noncurrent_obligations"),
    "current_and_accrued": (CURRENT, [], "total_current_and_accrued_liabilities"),
    "liabilities_and_other_credits": (GRAND, [], "total_liabilities_and_other_credits"),
}
EXPECTED_LABELS = set(MARGINS + LTD + NONCURRENT + CURRENT + GRAND
                      + ["payments_unapplied", "total_liabilities_and_other_credits"])


def sum_by_label(rows, group=GROUP, cat=CAT, val=VAL):
    """Step 1: {(group key): {label: SUM(value) or None}}."""
    out = defaultdict(dict)
    for r in rows:
        key = tuple(r[g] for g in group)
        lab = r[cat]
        if lab is None:
            continue
        v = r[val]
        if v is None:
            out[key].setdefault(lab, None)
        else:
            cur = out[key].get(lab)
            out[key][lab] = float(v) if cur is None else cur + float(v)
    return out


def check(sums, subs, negs, total, tol=TOL):
    """Steps 2-3. Returns (n_checked, n_no_total, n_no_subs, failures list)."""
    failures = []
    n_checked = n_no_total = n_no_subs = 0
    for key, labs in sums.items():
        s = None
        for lab, v in labs.items():
            if v is None:
                continue
            if lab in negs:
                s = (s or 0.0) - v
            elif lab in subs:
                s = (s or 0.0) + v
        g = labs.get(total)
        if g is None:
            n_no_total += 1
            continue
        if s is None:
            n_no_subs += 1
            continue
        n_checked += 1
        if abs(s - g) > tol:
            failures.append({"key": [str(k) for k in key], "subcomponents_sum": s,
                             "grand_total": g, "absolute_diff": abs(s - g)})
    return n_checked, n_no_total, n_no_subs, failures


def year_of(d):
    return str(d)[:4]


def fetch(table, data_dir):
    os.makedirs(data_dir, exist_ok=True)
    path = os.path.join(data_dir, table + ".parquet")
    if not os.path.exists(path):
        req = urllib.request.Request(NIGHTLY + table + ".parquet",
                                     headers={"User-Agent": "MV2-Munim-Inc (mv2@munimtech.com)"})
        try:
            with urllib.request.urlopen(req, timeout=300) as r, open(path, "wb") as f:
                f.write(r.read())
        except Exception as e:  # noqa: BLE001
            print(f"fetch failed {table}: {e}")
            return None
    return path


def run_table(table, data_dir, out):
    import polars as pl
    path = fetch(table, data_dir)
    if path is None:
        return {"table": table, "error": "not fetched"}
    df = pl.read_parquet(path)
    res = {"table": table, "rows": df.height, "columns": df.columns,
           "schema": {c: str(t) for c, t in df.schema.items()}}
    labels = sorted(x for x in df[CAT].unique().to_list() if x is not None)
    res["labels"] = labels
    res["labels_missing_from_tests"] = sorted(set(labels) - EXPECTED_LABELS)
    res["test_labels_missing_from_table"] = sorted(EXPECTED_LABELS - set(labels))
    if "is_total" in df.columns:
        res["is_total_labels"] = sorted(
            df.filter(pl.col("is_total"))[CAT].unique().drop_nulls().to_list())
    years = df.select(pl.col("report_date").cast(pl.Utf8).str.slice(0, 4).alias("y"))["y"]
    res["years"] = sorted(set(years.to_list()))
    res["groups"] = df.select(list(GROUP)).unique().height
    pu = df.filter(pl.col(CAT) == "payments_unapplied")[VAL].drop_nulls()
    res["payments_unapplied"] = {"nonnull": pu.len(), "positive": int((pu > 0).sum()),
                                 "negative": int((pu < 0).sum())}
    nulls = df.group_by(CAT).agg(pl.col(VAL).is_null().sum().alias("n_null"),
                                 pl.len().alias("n")).sort(CAT)
    res["nulls_by_label"] = {r[CAT]: [r["n_null"], r["n"]] for r in nulls.to_dicts()}
    sums = sum_by_label(df.select(list(GROUP) + [CAT, VAL]).iter_rows(named=True))
    res["tests"] = {}
    for name, (subs, negs, total) in TESTS.items():
        n, nt, ns, fails = check(sums, subs, negs, total)
        by_year = defaultdict(int)
        for f in fails:
            by_year[year_of(f["key"][1])] += 1
        fails.sort(key=lambda f: -f["absolute_diff"])
        res["tests"][name] = {
            "subcomponents": subs, "negative_subcomponents": negs, "total_label": total,
            "groups_checked": n, "groups_without_total": nt, "groups_without_subcomponents": ns,
            "failures": len(fails),
            "failure_share": round(len(fails) / n, 5) if n else None,
            "failures_by_year": dict(sorted(by_year.items())),
            "largest_failures": fails[:15],
        }
        with open(os.path.join(out, f"{table}__{name}__failures.json"), "w") as fh:
            json.dump(fails, fh)
    return res, sums


def balance_check(liab_sums, data_dir):
    """Post-hoc cross-table check: total liabilities and other credits vs total assets."""
    import polars as pl
    path = fetch("core_rus7__yearly_balance_sheet_assets", data_dir)
    if path is None:
        return {"error": "assets not fetched"}
    a = pl.read_parquet(path).filter(pl.col("asset_type") == "total")
    assets = {}
    for r in a.iter_rows(named=True):
        if r["ending_balance"] is not None:
            assets[(r["borrower_id_rus"], r["report_date"])] = float(r["ending_balance"])
    n = 0
    fails = []
    for key, labs in liab_sums.items():
        g = labs.get("total_liabilities_and_other_credits")
        if g is None or key not in assets:
            continue
        n += 1
        if abs(g - assets[key]) > TOL:
            fails.append({"key": [str(k) for k in key], "total_liabilities": g,
                          "total_assets": assets[key], "absolute_diff": abs(g - assets[key])})
    fails.sort(key=lambda f: -f["absolute_diff"])
    by_year = defaultdict(int)
    for f in fails:
        by_year[year_of(f["key"][1])] += 1
    return {"pairs": n, "failures": len(fails), "failures_by_year": dict(sorted(by_year.items())),
            "largest": fails[:15]}


def describe(table, data_dir):
    """Structure only, for choosing the next RUS table: columns, string labels."""
    import polars as pl
    path = fetch(table, data_dir)
    if path is None:
        return {"table": table, "error": "not fetched"}
    df = pl.read_parquet(path)
    d = {"table": table, "rows": df.height, "schema": {c: str(t) for c, t in df.schema.items()},
         "labels": {}}
    for c, t in df.schema.items():
        if t == pl.Utf8 or str(t).startswith("Categorical") or str(t).startswith("Enum"):
            u = df[c].cast(pl.Utf8).unique().drop_nulls()
            if u.len() <= 120 and c not in ("borrower_id_rus", "borrower_name_rus"):
                d["labels"][c] = sorted(u.to_list())
    return d


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="out")
    ap.add_argument("--data-dir", default="/data/rus7-20261109")
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    summary = {"tolerance": TOL, "source": NIGHTLY, "tables": {}}
    core_sums = None
    for t in ("core_rus7__yearly_balance_sheet_liabilities",
              "out_rus7__yearly_balance_sheet_liabilities"):
        r = run_table(t, a.data_dir, a.out_dir)
        if isinstance(r, tuple):
            res, sums = r
            if core_sums is None:
                core_sums = sums
        else:
            res = r
        summary["tables"][t] = res
    if core_sums is not None:
        summary["balance_check_not_preregistered"] = balance_check(core_sums, a.data_dir)
    summary["next_tables"] = [describe(t, a.data_dir) for t in (
        "core_rus7__yearly_utility_plant_changes",
        "core_rus7__yearly_statement_of_operations")]
    with open(os.path.join(a.out_dir, "rusliab.json"), "w") as fh:
        json.dump(summary, fh, indent=1, default=str)
    for t, res in summary["tables"].items():
        print(t, res.get("rows"), res.get("error", ""))
        for name, tr in res.get("tests", {}).items():
            print(f"  {name}: checked {tr['groups_checked']} failures {tr['failures']}"
                  f" no_total {tr['groups_without_total']} no_subs {tr['groups_without_subcomponents']}")
    print("balance", json.dumps({k: v for k, v in summary.get(
        "balance_check_not_preregistered", {}).items() if k != "largest"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
