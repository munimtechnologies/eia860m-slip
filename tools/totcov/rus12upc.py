# Copyright 2026 Munim, Inc.
# Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working in the name of MV2 of Munim, Inc. (mv2@munimtech.com).
"""rus12upc: PUDL's RUS-12 utility plant changes totals tests, and a proposed fix.

PUDL's tables core_rus12__yearly_utility_plant_changes and
out_rus12__yearly_utility_plant_changes each carry four
subcomponents_sum_to_total tests with categorical_column utility_plant_group
and total_label 'total'. 'total' is not a value of utility_plant_group (its
enum, UTILITY_PLANT_GROUP_RUS12, has seven plant groups); it is a value of
utility_plant_item. The macro's grand_total is therefore NULL in every group
and the eight tests can never fail (see docs/rus12upc.md).

This script measures, on PUDL's nightly parquet:
- the eight existing tests, as written (Q1);
- the fix their own description asks for: within each lower plant group,
  the items sum to the group's 'total' item (group_by adds
  utility_plant_group, categorical_column utility_plant_item) (Q2);
- a negative control: the proposed ending_balance test with every item's
  sign flipped, which must fail wherever the real check holds and the total
  is above $10 (Q3);
- exploratory, no prediction: the (group, item) pairs present, and the three
  upper totals described in PUDL's enum comments, built from the pairs found.

It reuses totcov.py's re-implementation of the dbt macro. It only measures;
nothing is sent to PUDL.
"""
import argparse
import json
import os
import sys

import totcov

TABLES = ["core_rus12__yearly_utility_plant_changes",
          "out_rus12__yearly_utility_plant_changes"]
VALUES = ["retirements", "additions", "adjustments_and_transfers", "ending_balance"]
LOWER = ["intangible_plant", "production_plant", "transmission_plant", "distribution_plant"]
UPPER = [  # (group, groups whose 'total' item feeds it), from PUDL's enum comments
    ("electric_plant_in_service", LOWER),
    ("utility_plant_in_service", ["electric_plant_in_service"]),
    ("total_utility_plant", ["utility_plant_in_service"]),
]
ITEMS = [  # UTILITY_PLANT_ITEM_RUS12 without 'total' (PUDL enums.py, main 2026-11-12)
    "land_and_land_rights", "other", "station_equipment", "structures_and_improvements",
    "general_plant", "hydro", "nuclear", "steam", "construction_work_in_progress",
    "acquisition_adjustments", "completed_construction", "electric_plant_held_for_future_use",
    "electric_plant_leased_to_others", "electric_plant_purchased_or_sold",
    "nuclear_fuel_assemblies", "rto_iso_plant",
]
EXCL = ("utility_plant_group NOT IN ('electric_plant_in_service', "
        "'utility_plant_in_service', 'total_utility_plant')")
KEYS = ["borrower_id_rus", "report_date"]


def existing_specs():
    """The four tests on each table, as in PUDL's schema.yml (main, 2026-11-12)."""
    out = []
    for table in TABLES:
        for value in VALUES:
            out.append(totcov.normalize({"table": table, "name": "existing_%s" % value, "args": {
                "group_by_columns": list(KEYS),
                "categorical_column": "utility_plant_group",
                "value_column": value,
                "total_label": "total",
                "row_condition": EXCL,
            }}, "existing"))
    return out


def proposed_specs():
    """Per lower plant group: items sum to the group's 'total' item."""
    out = []
    for table in TABLES:
        for value in VALUES:
            out.append(totcov.normalize({"table": table, "name": "proposed_%s" % value, "args": {
                "group_by_columns": KEYS + ["utility_plant_group"],
                "categorical_column": "utility_plant_item",
                "value_column": value,
                "total_label": "total",
                "tolerance": 10,
                "row_condition": EXCL,
            }}, "proposed"))
    return out


def negative_spec():
    """Negative control: the proposed ending_balance test with every item's sign flipped.

    (Leaving utility_plant_group out of group_by would NOT be a control: summed
    over all groups, items and totals still agree.) With every item negated,
    a group whose items sum to S and whose total is T compares -S with T. If
    the real check holds (|S - T| <= 10) and |T| > 10, then
    |-S - T| >= 2|T| - |S - T| > 10, so the control must fail there.
    """
    return totcov.normalize({"table": TABLES[0], "name": "NEG_items_negated", "args": {
        "group_by_columns": KEYS + ["utility_plant_group"],
        "categorical_column": "utility_plant_item",
        "value_column": "ending_balance",
        "subcomponents_list": [],
        "negative_subcomponents_list": list(ITEMS),
        "total_label": "total",
        "tolerance": 10,
        "row_condition": EXCL,
    }}, "negative")


def material_sql(table_ref, spec):
    """Groups with items and a total larger than $10 in absolute value; and how many fail."""
    return ("SELECT COUNT(*) AS n_material, "
            "COALESCE(SUM(CASE WHEN ABS(subs_sum - grand_total) > 10 THEN 1 ELSE 0 END), 0)"
            " AS n_material_fail FROM (%s) s "
            "WHERE subs_sum IS NOT NULL AND ABS(grand_total) > 10"
            % totcov.summary_sql(table_ref, spec))


def upper_specs(pairs, table):
    """Exploratory: the upper totals, built from the (group, item) pairs found.

    pairs: iterable of (utility_plant_group, utility_plant_item).
    """
    out = []
    present = set((str(g), str(i)) for g, i in pairs)
    for group, feeders in UPPER:
        if (group, "total") not in present:
            continue
        subs = [[f, "total"] for f in feeders if (f, "total") in present]
        subs += sorted([g, i] for g, i in present if g == group and i != "total")
        if not subs:
            continue
        for value in VALUES:
            out.append(totcov.normalize({"table": table, "name": "upper_%s_%s" % (group, value),
                                         "args": {
                "group_by_columns": list(KEYS),
                "categorical_column": ["utility_plant_group", "utility_plant_item"],
                "value_column": value,
                "subcomponents_list": subs,
                "total_label": [group, "total"],
                "tolerance": 10,
            }}, "exploratory"))
    return out


def evaluate(results):
    """Score Q1-Q3 of docs/rus12upc.md."""
    v = {}
    ex = [r for r in results if r["kind"] == "existing"]
    if len(ex) != 8 or any("error" in r for r in ex):
        v["Q1"] = "not tested"
    else:
        v["Q1"] = "held" if all(r["n_groups"] > 0 and r["n_with_total"] == 0
                                for r in ex) else "failed"
    pr = [r for r in results if r["kind"] == "proposed"]
    if len(pr) != 8 or any("error" in r for r in pr):
        v["Q2"] = "not tested"
    else:
        v["Q2"] = "held" if all(
            r["n_with_subs"] > 0
            and r["n_with_subs"] - r["n_subs_no_total"] >= 0.9 * r["n_with_subs"]
            for r in pr) else "failed"
    neg = [r for r in results if r["kind"] == "negative"]
    if len(neg) != 1 or "error" in neg[0] or not neg[0].get("n_material"):
        v["Q3"] = "not tested"
    else:
        n = neg[0]
        v["Q3"] = "held" if n["n_material_fail"] >= 0.9 * n["n_material"] else "failed"
    return v


PAIRS_SQL = ("SELECT utility_plant_group, utility_plant_item, COUNT(*) AS n, "
             "COUNT(ending_balance) AS nn FROM {t} GROUP BY 1, 2 ORDER BY 1, 2")


def measure(con, path, spec):
    r = dict(spec)
    try:
        r.update(totcov.run_spec(con, path, spec))
        if spec["kind"] == "negative":
            ref = "read_parquet(%s)" % totcov.ql(path)
            row = con.execute(material_sql(ref, spec)).fetchone()
            r["n_material"], r["n_material_fail"] = int(row[0] or 0), int(row[1] or 0)
    except Exception as exc:  # noqa: BLE001
        r["error"] = str(exc)[:500]
    return r


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args(argv)
    import duckdb  # noqa: PLC0415

    os.makedirs(a.out_dir, exist_ok=True)
    os.makedirs(a.data_dir, exist_ok=True)
    result = {"tool": "rus12upc 0.1.0", "tables": {}, "pairs": {}, "results": []}
    budget = [totcov.MAX_TOTAL_BYTES]
    paths = {}
    for t in TABLES:
        try:
            p, note = totcov.fetch(t, a.data_dir, budget)
        except Exception as exc:  # noqa: BLE001
            p, note = None, "download failed: %s" % exc
        result["tables"][t] = note
        print(t, note, flush=True)
        if p:
            paths[t] = p

    con = duckdb.connect()
    con.execute("SET memory_limit = '700MB'")
    con.execute("SET threads = 1")
    specs = existing_specs() + proposed_specs() + [negative_spec()]
    for t in TABLES:
        if t not in paths:
            continue
        ref = "read_parquet(%s)" % totcov.ql(paths[t])
        rows = con.execute(PAIRS_SQL.format(t=ref)).fetchall()
        result["pairs"][t] = [[str(x[0]), str(x[1]), int(x[2]), int(x[3])] for x in rows]
        specs += upper_specs([(x[0], x[1]) for x in rows], t)
    for s in specs:
        if s["table"] not in paths:
            r = dict(s)
            r["error"] = "table not available: %s" % result["tables"].get(s["table"])
        else:
            r = measure(con, paths[s["table"]], s)
        result["results"].append(r)
        print("%-11s %-42s %-48s groups=%s with_subs=%s total=%s fail=%s absent=%s %s" % (
            r["kind"], r["table"][:42], r["name"], r.get("n_groups"), r.get("n_with_subs"),
            r.get("n_with_total"), r.get("n_fail"), r.get("absent_labels"),
            r.get("error", "")), flush=True)
    result["verdicts"] = evaluate(result["results"])
    with open(os.path.join(a.out_dir, "rus12upc.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1, default=str)
    print("pairs", json.dumps(result["pairs"], default=str)[:6000])
    print("verdicts", json.dumps(result["verdicts"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
