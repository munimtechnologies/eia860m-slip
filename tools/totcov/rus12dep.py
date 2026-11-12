# Copyright 2026 Munim, Inc.
# Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working in the name of MV2 of Munim, Inc. (mv2@munimtech.com).
"""rus12dep: PUDL's RUS-12 depreciation changes totals tests, and a proposed fix.

PUDL's tables core_rus12__yearly_depreciation_changes and
out_rus12__yearly_depreciation_changes each carry four
subcomponents_sum_to_total tests with categorical_column
depreciation_and_amortization_group and total_label 'total_depreciation'.
'total_depreciation' is not a value of depreciation_and_amortization_group:
the field's enum, DEPRECIATION_CHANGES_GROUP_RUS12, has two values
(electric_plant_in_service, provision_for_depreciation_and_amortization), and
the transform builds the column from a regex over exactly those two names.
'total_depreciation' is a depreciation_and_amortization_item. The tests'
row_condition (group = 'electric_plant_in_service') makes it doubly sure: after
the filter no row can carry another group. The macro's grand_total is NULL in
every group, so the eight tests can never fail (see docs/rus12dep.md).

This script measures, on PUDL's nightly parquet:
- the eight existing tests as written, and again without their row_condition
  (in case dbt does not pass a row_condition placed beside `arguments`) (D1);
- the fix the tests' own description asks for: within electric plant in
  service, the depreciation items sum to the 'total_depreciation' item
  (categorical_column depreciation_and_amortization_item) (D2);
- a negative control: the proposed ending_balance test with every item's sign
  flipped, which must fail wherever the real check holds and |total| > $10 (D3);
- exploratory, no prediction: the (group, item) pairs present; the proposed
  test without retirement_work_in_progress; and the provision group's 'total'
  built from its items with and without the electric plant total.

It reuses totcov.py's re-implementation of the dbt macro (fetched from
munimtechnologies/eia860m-slip, tools/totcov/totcov.py). It only measures;
nothing is sent to PUDL.
"""
import argparse
import json
import os
import sys

import totcov

TOOL = "rus12dep 0.1.0"
TABLES = ["core_rus12__yearly_depreciation_changes",
          "out_rus12__yearly_depreciation_changes"]
VALUES = ["accruals", "retirements_less_net_salvage", "adjustments_and_transfers",
          "ending_balance"]
KEYS = ["borrower_id_rus", "report_date"]
GROUP = "depreciation_and_amortization_group"
ITEM = "depreciation_and_amortization_item"
EPIS = "electric_plant_in_service"
PROV = "provision_for_depreciation_and_amortization"
GROUPS = [EPIS, PROV]  # DEPRECIATION_CHANGES_GROUP_RUS12 (PUDL enums.py, main 2026-11-12)
EPIS_COND = "%s='%s'" % (GROUP, EPIS)  # the existing tests' row_condition, verbatim
RWIP = "retirement_work_in_progress"
PLANT_ITEMS = [  # the seven depreciation_*_plant items of DEPRECIATION_CHANGES_ITEMS_RUS12
    "depreciation_steam_production_plant",
    "depreciation_nuclear_production_plant",
    "depreciation_hydraulic_production_plant",
    "depreciation_other_production_plant",
    "depreciation_transmission_plant",
    "depreciation_distribution_plant",
    "depreciation_general_plant",
]
EPIS_ITEMS = PLANT_ITEMS + [RWIP]


def existing_specs(with_row_condition=True):
    """The four tests on each table, as in PUDL's schema.yml (main, 2026-11-12)."""
    out = []
    for table in TABLES:
        for value in VALUES:
            args = {
                "group_by_columns": list(KEYS),
                "categorical_column": GROUP,
                "value_column": value,
                "total_label": "total_depreciation",
            }
            name = "existing_%s" % value
            kind = "existing"
            if with_row_condition:
                args["row_condition"] = EPIS_COND
            else:
                name += "_no_row_condition"
                kind = "existing_norc"
            out.append(totcov.normalize({"table": table, "name": name, "args": args}, kind))
    return out


def proposed_specs(items=None, kind="proposed", suffix=""):
    """Within electric plant in service: items sum to the 'total_depreciation' item."""
    items = list(EPIS_ITEMS if items is None else items)
    out = []
    for table in TABLES:
        for value in VALUES:
            out.append(totcov.normalize({"table": table, "name": "proposed_%s%s" % (value, suffix),
                                         "args": {
                "group_by_columns": list(KEYS),
                "categorical_column": ITEM,
                "value_column": value,
                "subcomponents_list": items,
                "total_label": "total_depreciation",
                "tolerance": 10,
                "row_condition": EPIS_COND,
            }}, kind))
    return out


def negative_spec():
    """Negative control: the proposed ending_balance test with every item's sign flipped.

    With every item negated, a group whose items sum to S and whose total is T
    compares -S with T. If the real check holds (|S - T| <= 10) and |T| > 10,
    then |-S - T| >= 2|T| - |S - T| > 10, so the control must fail there.
    subcomponents_list is given explicitly (all eight items) so that no other
    item in the group can enter the sum.
    """
    return totcov.normalize({"table": TABLES[0], "name": "NEG_items_negated", "args": {
        "group_by_columns": list(KEYS),
        "categorical_column": ITEM,
        "value_column": "ending_balance",
        "subcomponents_list": ["__none__"],
        "negative_subcomponents_list": list(EPIS_ITEMS),
        "total_label": "total_depreciation",
        "tolerance": 10,
        "row_condition": EPIS_COND,
    }}, "negative")


def provision_specs(pairs, table):
    """Exploratory: the provision group's 'total' built from the pairs found.

    Two variants per value column: its own items only, and its own items plus
    the electric plant in service 'total_depreciation'.
    """
    present = set((str(g), str(i)) for g, i in pairs)
    if (PROV, "total") not in present:
        return []
    own = sorted([g, i] for g, i in present if g == PROV and i != "total")
    out = []
    variants = [("own_items", own)]
    if (EPIS, "total_depreciation") in present:
        variants.append(("own_items_plus_epis", own + [[EPIS, "total_depreciation"]]))
    for label, subs in variants:
        if not subs:
            continue
        for value in VALUES:
            out.append(totcov.normalize({"table": table,
                                         "name": "provision_%s_%s" % (label, value), "args": {
                "group_by_columns": list(KEYS),
                "categorical_column": [GROUP, ITEM],
                "value_column": value,
                "subcomponents_list": subs,
                "total_label": [PROV, "total"],
                "tolerance": 10,
            }}, "exploratory"))
    return out


def material_sql(table_ref, spec):
    """Groups with items and a total larger than $10 in absolute value; and how many fail."""
    return ("SELECT COUNT(*) AS n_material, "
            "COALESCE(SUM(CASE WHEN ABS(subs_sum - grand_total) > 10 THEN 1 ELSE 0 END), 0)"
            " AS n_material_fail FROM (%s) s "
            "WHERE subs_sum IS NOT NULL AND ABS(grand_total) > 10"
            % totcov.summary_sql(table_ref, spec))


def evaluate(results):
    """Score D1-D3 of docs/rus12dep.md."""
    v = {}
    ex = [r for r in results if r["kind"] in ("existing", "existing_norc")]
    if len(ex) != 16 or any("error" in r for r in ex):
        v["D1"] = "not tested"
    else:
        v["D1"] = "held" if all(r["n_groups"] > 0 and r["n_with_total"] == 0
                                for r in ex) else "failed"
    pr = [r for r in results if r["kind"] == "proposed"]
    if len(pr) != 8 or any("error" in r for r in pr):
        v["D2"] = "not tested"
    else:
        v["D2"] = "held" if all(
            r["n_with_subs"] > 0
            and r["n_with_subs"] - r["n_subs_no_total"] >= 0.9 * r["n_with_subs"]
            for r in pr) else "failed"
    neg = [r for r in results if r["kind"] == "negative"]
    if len(neg) != 1 or "error" in neg[0] or not neg[0].get("n_material"):
        v["D3"] = "not tested"
    else:
        n = neg[0]
        v["D3"] = "held" if n["n_material_fail"] >= 0.9 * n["n_material"] else "failed"
    return v


PAIRS_SQL = ("SELECT %s, %s, COUNT(*) AS n, COUNT(ending_balance) AS nn FROM {t} "
             "GROUP BY 1, 2 ORDER BY 1, 2" % (GROUP, ITEM))


def measure(con, path, spec):
    r = dict(spec)
    try:
        r.update(totcov.run_spec(con, path, spec))
        if spec["kind"] in ("negative", "proposed", "proposed_no_rwip"):
            ref = "read_parquet(%s)" % totcov.ql(path)
            row = con.execute(material_sql(ref, spec)).fetchone()
            r["n_material"], r["n_material_fail"] = int(row[0] or 0), int(row[1] or 0)
    except Exception as exc:  # noqa: BLE001
        r["error"] = str(exc)[:500]
    return r


def all_specs():
    return (existing_specs(True) + existing_specs(False) + proposed_specs()
            + proposed_specs(PLANT_ITEMS, "proposed_no_rwip", "_no_rwip") + [negative_spec()])


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args(argv)
    import duckdb  # noqa: PLC0415

    os.makedirs(a.out_dir, exist_ok=True)
    os.makedirs(a.data_dir, exist_ok=True)
    result = {"tool": TOOL, "tables": {}, "pairs": {}, "results": []}
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
    specs = all_specs()
    for t in TABLES:
        if t not in paths:
            continue
        ref = "read_parquet(%s)" % totcov.ql(paths[t])
        rows = con.execute(PAIRS_SQL.format(t=ref)).fetchall()
        result["pairs"][t] = [[str(x[0]), str(x[1]), int(x[2]), int(x[3])] for x in rows]
        specs += provision_specs([(x[0], x[1]) for x in rows], t)
    for s in specs:
        if s["table"] not in paths:
            r = dict(s)
            r["error"] = "table not available: %s" % result["tables"].get(s["table"])
        else:
            r = measure(con, paths[s["table"]], s)
        result["results"].append(r)
        print("%-16s %-40s %-46s groups=%s with_subs=%s total=%s fail=%s material=%s/%s "
              "absent=%s %s" % (
                  r["kind"], r["table"][:40], r["name"][:46], r.get("n_groups"),
                  r.get("n_with_subs"), r.get("n_with_total"), r.get("n_fail"),
                  r.get("n_material_fail"), r.get("n_material"), r.get("absent_labels"),
                  r.get("error", "")), flush=True)
    result["verdicts"] = evaluate(result["results"])
    with open(os.path.join(a.out_dir, "rus12dep.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1, default=str)
    print("pairs", json.dumps(result["pairs"], default=str)[:6000])
    print("verdicts", json.dumps(result["verdicts"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
