# Copyright 2026 Munim, Inc.
# Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working in the name of MV2 of Munim, Inc. (mv2@munimtech.com).
"""Unit tests for totcov. The DuckDB test is skipped when duckdb is not installed."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import totcov  # noqa: E402

UPC_DOC = {"version": 2, "sources": [{"name": "pudl", "tables": [{
    "name": "core_rus7__yearly_utility_plant_changes",
    "data_tests": [
        "expect_columns_not_all_null",
        {"check_row_counts_per_partition": {"arguments": {"partition_expr": "x"}}},
        {"subcomponents_sum_to_total": {
            "arguments": {
                "group_by_columns": ["borrower_id_rus", "report_date"],
                "categorical_column": "utility_plant_group",
                "value_column": "ending_balance",
                "total_label": "total",
            },
            "row_condition": "utility_plant_group='utility_plant_in_service'",
        }},
        {"dbt_utils.expression_is_true": {"arguments": {"expression": "1=1"},
                                          "config": {"error_if": ">62"}}},
    ],
}]}]}


class TestSqlPieces(unittest.TestCase):
    def test_as_list(self):
        self.assertEqual(totcov.as_list("a"), ["a"])
        self.assertEqual(totcov.as_list(["a", "b"]), ["a", "b"])
        self.assertEqual(totcov.as_list(None), [])

    def test_label_cond_single(self):
        self.assertEqual(totcov.label_cond(["c"], "total"), "(\"c\" = 'total')")

    def test_label_cond_pair(self):
        got = totcov.label_cond(["g", "i"], ["total_utility_plant", "total"])
        self.assertEqual(got, "(\"g\" = 'total_utility_plant' AND \"i\" = 'total')")

    def test_label_cond_mismatch(self):
        with self.assertRaises(ValueError):
            totcov.label_cond(["g", "i"], "total")

    def test_quote_literal(self):
        self.assertEqual(totcov.ql("o'x"), "'o''x'")

    def test_fallback_branch_without_list(self):
        spec = totcov.normalize(totcov.extract_tests(UPC_DOC)[0])
        sql = totcov.summary_sql("t", spec)
        self.assertIn("WHEN NOT (\"utility_plant_group\" = 'total') THEN tc_value", sql)
        self.assertIn("WHERE utility_plant_group='utility_plant_in_service'", sql)

    def test_negative_branch_first(self):
        spec = totcov.normalize({"table": "x", "args": {
            "group_by_columns": ["b"], "categorical_column": "c", "value_column": "v",
            "subcomponents_list": ["s1", "s2"], "negative_subcomponents_list": ["n1"],
            "total_label": "tot", "tolerance": 10}})
        sql = totcov.summary_sql("t", spec)
        self.assertLess(sql.index("THEN -1 * tc_value"), sql.index("\"c\" = 's1'"))
        self.assertNotIn("WHEN NOT", sql)
        self.assertIn("> 10.0", totcov.metrics_sql("t", spec))

    def test_unique_labels(self):
        spec = {"total": "t", "subs": ["a", "t", "b"], "negs": ["a"]}
        self.assertEqual(totcov.unique_labels(spec), ["t", "a", "b"])


class TestYaml(unittest.TestCase):
    def test_extract_one_test(self):
        found = totcov.extract_tests(UPC_DOC, "f.yml")
        self.assertEqual(len(found), 1)
        args = found[0]["args"]
        self.assertEqual(args["categorical_column"], "utility_plant_group")
        self.assertEqual(args["row_condition"], "utility_plant_group='utility_plant_in_service'")
        self.assertEqual(found[0]["table"], "core_rus7__yearly_utility_plant_changes")

    def test_extract_non_dict(self):
        self.assertEqual(totcov.extract_tests(None), [])

    def test_normalize_defaults(self):
        spec = totcov.normalize(totcov.extract_tests(UPC_DOC)[0])
        self.assertEqual(spec["cols"], ["utility_plant_group"])
        self.assertEqual(spec["tolerance"], 0.01)
        self.assertEqual(spec["subs"], [])
        self.assertIsNone(spec["min_cov"])

    def test_allowed_failures(self):
        self.assertEqual(totcov.allowed_failures({}), 0)
        self.assertEqual(totcov.allowed_failures(None), 0)
        self.assertEqual(totcov.allowed_failures({"error_if": ">62"}), 62)
        self.assertEqual(totcov.allowed_failures({"error_if": ">= 5"}), 4)
        self.assertEqual(totcov.allowed_failures({"error_if": "!=0"}), 0)
        self.assertIsNone(totcov.allowed_failures({"severity": "warn"}))
        self.assertIsNone(totcov.allowed_failures({"error_if": "<3"}))

    def test_dbt_failures_coverage(self):
        m = {"n_fail": 2, "n_groups": 10, "n_with_total": 5, "n_subs_no_total": 5}
        self.assertEqual(totcov.dbt_failures(m, {"min_cov": None}), 2)
        self.assertEqual(totcov.dbt_failures(m, {"min_cov": 0.9}), 7)
        self.assertEqual(totcov.dbt_failures(m, {"min_cov": 0.5}), 2)

    def test_proposed_specs(self):
        specs = totcov.proposed_specs()
        self.assertEqual(len(specs), 13)
        neg = [s for s in specs if s["name"].startswith("NEG")]
        self.assertEqual(len(neg), 1)
        self.assertNotIn("distribution", neg[0]["args"]["subcomponents_list"])
        for s in specs:
            totcov.summary_sql("t", totcov.normalize(s, "proposed"))


def fake_results():
    up = totcov.UPC
    res = [{"kind": "existing", "table": up, "name": "", "n_groups": 5, "n_with_total": 0}]
    for i in range(6):
        res.append({"kind": "proposed", "table": up, "name": "p%d" % i,
                    "n_groups": 10, "n_with_total": 10, "n_fail": 0})
    res.append({"kind": "proposed", "table": up, "name": "NEG_CONTROL_no_distribution",
                "n_groups": 10, "n_with_total": 10, "n_fail": 9})
    spec = {
        "soo_other_capital_credits_ytd": {"n": 3, "nn_month": 2, "nn_ytd": 0, "nn_budget": 0},
        "soo_other_capital_credits": {"n": 3, "nn_month": 0, "nn_ytd": 3, "nn_budget": 3},
        "soo_idc_credit_label": {"n": 0},
        "soo_idc_label": {"n": 5, "neg_month": 1, "neg_ytd": 1, "neg_budget": 1},
    }
    return res, spec


class TestEvaluate(unittest.TestCase):
    def test_all_held(self):
        res, spec = fake_results()
        v = totcov.evaluate(res, spec)
        for k in ("P1", "P2", "P3", "P4", "P5", "P6"):
            self.assertEqual(v[k], "held", k)
        self.assertEqual(v["P7"], "not tested")

    def test_p1_fails_with_total(self):
        res, spec = fake_results()
        res[0]["n_with_total"] = 1
        self.assertEqual(totcov.evaluate(res, spec)["P1"], "failed")

    def test_p3_fails_weak_control(self):
        res, spec = fake_results()
        res[-1]["n_fail"] = 5
        self.assertEqual(totcov.evaluate(res, spec)["P3"], "failed")

    def test_errors_not_tested(self):
        res, spec = fake_results()
        res[1]["error"] = "boom"
        spec["soo_idc_label"] = {"error": "x"}
        v = totcov.evaluate(res, spec)
        self.assertEqual(v["P2"], "not tested")
        self.assertEqual(v["P6"], "not tested")

    def test_p4_p5(self):
        res, spec = fake_results()
        spec["soo_other_capital_credits_ytd"]["nn_month"] = 0
        v = totcov.evaluate(res, spec)
        self.assertEqual(v["P4"], "held")
        self.assertEqual(v["P5"], "failed")
        spec["soo_other_capital_credits"]["nn_month"] = 1
        self.assertEqual(totcov.evaluate(res, spec)["P4"], "failed")

    def test_p7(self):
        res, spec = fake_results()
        for i in range(20):
            res.append({"kind": "existing", "table": "x", "name": "", "allowed": 3,
                        "dbt_failures": 0 if i else 9})
        self.assertEqual(totcov.evaluate(res, spec)["P7"], "held")
        res[-2]["dbt_failures"] = 9
        self.assertEqual(totcov.evaluate(res, spec)["P7"], "failed")


class TestDuckdb(unittest.TestCase):
    def setUp(self):
        try:
            import duckdb  # noqa: PLC0415
        except ImportError:
            self.skipTest("duckdb not installed")
        self.con = duckdb.connect()
        rows = []
        for b, dist, gen, tot, cwip, grand in (("A", 100, 20, 120, 5, 125),
                                               ("B", 50, 10, 75, 0, 75)):
            rows += [(b, "utility_plant_in_service", "distribution", dist),
                     (b, "utility_plant_in_service", "general", gen),
                     (b, "utility_plant_in_service", "total", tot),
                     (b, "total_utility_plant", "construction_work_in_progress", cwip),
                     (b, "total_utility_plant", "total", grand)]
        vals = ", ".join("('%s', DATE '2020-12-01', '%s', '%s', %d)" % r for r in rows)
        self.con.execute(
            "CREATE TABLE t AS SELECT * FROM (VALUES %s) v(borrower_id_rus, report_date, "
            "utility_plant_group, utility_plant_item, ending_balance)" % vals)

    def metrics(self, spec):
        row = self.con.execute(totcov.metrics_sql("t", spec)).fetchone()
        return dict(zip(["n_groups", "n_with_total", "n_with_subs", "n_fail", "n_subs_no_total"],
                        row))

    def test_existing_test_is_vacuous(self):
        spec = totcov.normalize(totcov.extract_tests(UPC_DOC)[0])
        m = self.metrics(spec)
        self.assertEqual(m["n_groups"], 2)
        self.assertEqual(m["n_with_total"], 0)
        self.assertEqual(m["n_fail"], 0)

    def test_proposed_catches_bad_total(self):
        spec = totcov.normalize({"table": "t", "args": {
            "group_by_columns": ["borrower_id_rus", "report_date"],
            "categorical_column": "utility_plant_item", "value_column": "ending_balance",
            "subcomponents_list": ["distribution", "general"], "total_label": "total",
            "tolerance": 10,
            "row_condition": "utility_plant_group = 'utility_plant_in_service'"}})
        m = self.metrics(spec)
        self.assertEqual((m["n_groups"], m["n_with_total"], m["n_fail"]), (2, 2, 1))

    def test_two_column_labels(self):
        spec = totcov.normalize({"table": "t", "args": {
            "group_by_columns": ["borrower_id_rus", "report_date"],
            "categorical_column": ["utility_plant_group", "utility_plant_item"],
            "value_column": "ending_balance",
            "subcomponents_list": [["utility_plant_in_service", "total"],
                                   ["total_utility_plant", "construction_work_in_progress"]],
            "total_label": ["total_utility_plant", "total"], "tolerance": 10}})
        m = self.metrics(spec)
        self.assertEqual((m["n_with_total"], m["n_fail"]), (2, 0))
        labels, sql = totcov.label_counts_sql("t", spec)
        self.assertEqual(list(self.con.execute(sql).fetchone()), [2, 2, 2])


if __name__ == "__main__":
    unittest.main()
