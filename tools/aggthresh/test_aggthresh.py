# Copyright 2026 Munim, Inc.
# Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working in the name of MV2 of Munim, Inc. (mv2@munimtech.com).
"""Unit tests for aggthresh (stdlib only; PyYAML and DuckDB are not needed)."""
import unittest

import aggthresh as ag

SAMPLE = """---
sources:
  - name: pudl
    tables:
      - name: t1
        data_tests:
          - expect_columns_not_all_null
          - check_row_counts_per_partition:
              arguments:
                partition_expr: year
        columns:
          - name: a
            data_tests:
              - dbt_expectations.expect_column_min_to_be_between:
                  arguments:
                    min_value: 0.0
                  config:
                    error_if: ">13"
                  description: >
                    Fail if many more negative values appear.
          - name: b
            data_tests:
              - dbt_expectations.expect_column_values_to_be_between:
                  arguments:
                    min_value: 0.0
                    max_value: 1.0
                  config:
                    error_if: ">0"
          - name: c
            data_tests:
              - dbt_expectations.expect_column_max_to_be_between:
                  arguments:
                    max_value: 5
                    group_by:
                      - year
                  config:
                    error_if: ">2"
              - dbt_expectations.expect_column_min_to_be_between:
                  arguments:
                    min_value: 0
          - name: d
            data_tests:
              - dbt_expectations.expect_column_sum_to_be_between:
                  arguments:
                    min_value: 0
                  config:
                    error_if: ">1" # 0.4% of the data
              - dbt_expectations.expect_column_mean_to_be_between:
                  arguments:
                    min_value: 0
                  config:
                    severity: warn
                    error_if: ">5"
"""

MIN = "dbt_expectations.expect_column_min_to_be_between"
DOC = {"sources": [{"name": "pudl", "tables": [{
    "name": "t1",
    "data_tests": ["expect_columns_not_all_null",
                   {"check_row_counts_per_partition": {"arguments": {"partition_expr": "year"}}}],
    "columns": [
        {"name": "a", "data_tests": [{MIN: {
            "arguments": {"min_value": 0.0}, "config": {"error_if": ">13"},
            "description": "Fail if many more negative values appear.\n"}}]},
        {"name": "b", "data_tests": [{"dbt_expectations.expect_column_values_to_be_between": {
            "arguments": {"min_value": 0.0, "max_value": 1.0}, "config": {"error_if": ">0"}}}]},
        {"name": "c", "data_tests": [
            {"dbt_expectations.expect_column_max_to_be_between": {
                "arguments": {"max_value": 5, "group_by": ["year"]},
                "config": {"error_if": ">2"}}},
            {MIN: {"arguments": {"min_value": 0}}}]},
        {"name": "d", "data_tests": [
            {"dbt_expectations.expect_column_sum_to_be_between": {
                "arguments": {"min_value": 0}, "config": {"error_if": ">1"}}},
            {"dbt_expectations.expect_column_mean_to_be_between": {
                "arguments": {"min_value": 0},
                "config": {"severity": "warn", "error_if": ">5"}}}]},
    ]}]}]}


class TestThresholds(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(ag.parse_cond(">13"), (">", 13.0))
        self.assertEqual(ag.parse_cond(" >= 2 "), (">=", 2.0))
        self.assertEqual(ag.parse_cond("!=0"), ("!=", 0.0))
        self.assertIsNone(ag.parse_cond("garbage"))

    def test_can_error(self):
        self.assertEqual(ag.can_error(">13"), (False, "ok"))
        self.assertEqual(ag.can_error(">1"), (False, "ok"))
        self.assertEqual(ag.can_error(">0"), (True, "ok"))
        self.assertEqual(ag.can_error(">=1"), (True, "ok"))
        self.assertEqual(ag.can_error(None), (True, "ok"))
        self.assertEqual(ag.can_error(">5", "warn"), (False, "severity_warn"))
        self.assertEqual(ag.can_error("x"), (None, "unparsed"))
        self.assertEqual(ag.can_error(">13", max_failures=20), (True, "ok"))


class TestYamlMethod(unittest.TestCase):
    def test_categories(self):
        tests = ag.scan_docs([("f.yml", DOC)])
        self.assertEqual(len(tests), 8)
        cats = [(t["column"], t["test"].split(".")[-1], t["category"]) for t in tests]
        self.assertEqual(cats, [
            ("", "expect_columns_not_all_null", "row_level_or_custom"),
            ("", "check_row_counts_per_partition", "row_level_or_custom"),
            ("a", "expect_column_min_to_be_between", "aggregate_unreachable_error_if"),
            ("b", "expect_column_values_to_be_between", "row_level_or_custom"),
            ("c", "expect_column_max_to_be_between", "aggregate_grouped"),
            ("c", "expect_column_min_to_be_between", "aggregate_ok"),
            ("d", "expect_column_sum_to_be_between", "aggregate_unreachable_error_if"),
            ("d", "expect_column_mean_to_be_between", "aggregate_severity_warn"),
        ])

    def test_top_level_error_if_and_group_by(self):
        doc = {"sources": [{"tables": [{"name": "t", "columns": [{"name": "x", "data_tests": [
            {MIN: {"error_if": ">3"}},
            {MIN: {"group_by": ["y"], "error_if": ">3"}}]}]}]}]}
        cats = [t["category"] for t in ag.scan_docs([("f", doc)])]
        self.assertEqual(cats, ["aggregate_unreachable_error_if", "aggregate_grouped"])


class TestLineMethod(unittest.TestCase):
    def test_items(self):
        items = ag.line_scan(SAMPLE)
        self.assertEqual([it["name"].split(".")[-1] for it in items], [
            "expect_columns_not_all_null", "check_row_counts_per_partition",
            "expect_column_min_to_be_between", "expect_column_values_to_be_between",
            "expect_column_max_to_be_between", "expect_column_min_to_be_between",
            "expect_column_sum_to_be_between", "expect_column_mean_to_be_between"])
        self.assertEqual(items[2]["error_if"], ">13")
        self.assertTrue(items[4]["has_group_by"])
        self.assertIsNone(items[5]["error_if"])
        self.assertEqual(items[6]["comment"], "0.4% of the data")
        self.assertEqual(items[7]["severity"], "warn")
        self.assertEqual([ag.line_flagged(it) for it in items],
                         [False, False, True, False, False, False, True, False])

    def test_score_scan_agrees(self):
        tests = ag.scan_docs([("f.yml", DOC)])
        items = [("f.yml", it) for it in ag.line_scan(SAMPLE)]
        res = ag.score_scan(tests, items)
        self.assertEqual(res["A1"]["n_flagged"], 2)
        self.assertFalse(res["A1"]["held"])
        self.assertEqual(res["S1"]["line_count"], 2)
        self.assertTrue(res["S1"]["held"])
        self.assertEqual(res["A2"]["n_sized"], 2)
        self.assertFalse(res["K1"]["held"])

    def test_controls(self):
        mk = lambda table, col, test, cat: {"table": table, "column": col, "test": test,
                                            "category": cat, "error_if": ""}
        tests = [
            mk("core_rus7__yearly_statement_of_operations", "opex_ytd", MIN,
               "aggregate_unreachable_error_if"),
            mk("core_epamats__hourly_emissions", "operating_time_hours",
               "dbt_expectations.expect_column_values_to_be_between", "row_level_or_custom"),
            mk("core_epamats__hourly_emissions", "heat_content_mmbtu", MIN,
               "aggregate_unreachable_error_if"),
        ]
        res = ag.score_scan(tests, [])
        self.assertTrue(res["K1"]["held"])
        self.assertTrue(res["K2"]["held"])
        self.assertTrue(res["K3"]["held"])
        self.assertTrue(ag.has_sizing_language("Fail if many more negative values appear."))
        self.assertFalse(ag.has_sizing_language("row_condition: x > 0\nmin_value: 0"))


ROWS = [
    ("1", "2020-01-01", "patronage_and_operating_margins", "total_minus", 100.0, 1000.0, 900.0),
    ("1", "2020-01-01", "patronage_capital_or_margins", "non_operating_margins_interest",
     5.0, 50.0, 40.0),
    ("1", "2020-01-01", "patronage_capital_or_margins", "other_capital_credits",
     None, 200.0, 150.0),
    ("1", "2020-01-01", "patronage_capital_or_margins", "other_capital_credits_ytd",
     20.0, None, None),
    ("1", "2020-01-01", "patronage_capital_or_margins", "total", 125.0, 1250.0, 1090.0),
]


class TestSoo(unittest.TestCase):
    def test_occ(self):
        res = ag.occ_checks(ROWS)
        for k in ["O1", "O2", "O3"]:
            self.assertTrue(res[k]["held"], k)

    def test_totals(self):
        res = ag.totals_checks(ROWS)
        self.assertEqual(res["O4"]["failed_as_labelled"], 1)
        self.assertEqual(res["O4"]["failed_relabelled"], 0)
        for k in ["O4", "O5", "OC"]:
            self.assertTrue(res[k]["held"], k)
        self.assertEqual(res["explore_budget"]["failed_relabelled"], 0)

    def test_totals_order_independent(self):
        rows = [ROWS[3], ROWS[2]] + [ROWS[0], ROWS[1], ROWS[4]]
        self.assertEqual(ag.patronage_total_failures(rows, 4, relabel=True), (1, 0))
        self.assertEqual(ag.patronage_total_failures(rows, 4, relabel=False), (1, 1))

    def test_occ_fails_when_fixed(self):
        fixed = [r for r in ROWS if r[3] != "other_capital_credits_ytd"]
        fixed = [(b, d, g, t, 20.0 if t == "other_capital_credits" else m, y, u)
                 for b, d, g, t, m, y, u in fixed]
        res = ag.occ_checks(fixed)
        self.assertFalse(res["O1"]["held"])
        self.assertFalse(res["O2"]["held"])

    def test_score_agg(self):
        agg = {c: {"dbt_query_rows": 1, "rows_below_zero": 5, "error_if_threshold": 9}
               for c in ag.VALUE_COLS}
        self.assertTrue(all(v["held"] for v in ag.score_agg(agg).values()))
        agg["opex_ytd"]["dbt_query_rows"] = 0
        self.assertFalse(ag.score_agg(agg)["A3b"]["held"])


if __name__ == "__main__":
    unittest.main()
