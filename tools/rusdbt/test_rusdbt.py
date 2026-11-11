# Copyright 2026 Munim, Inc.
# Licensed under the Apache License, Version 2.0 (Apache-2.0).
"""Tests for rusdbt (stdlib only; no dbt or network needed)."""
import os
import unittest

import rusdbt

HERE = os.path.dirname(os.path.abspath(__file__))

SAMPLE = "\n".join([
    "version: 2",
    "sources:",
    "  - name: pudl",
    "    tables:",
    "      - name: core_rus7__yearly_balance_sheet_liabilities",
    "        data_tests:",
    "          - expect_columns_not_all_null",
    "        columns:",
    "          - name: report_date",
    "",
])


def rec(table, total, status="pass", failures=0, subs=None, neg=None):
    return {"table": table, "total_label": total, "status": status,
            "failures": failures, "subcomponents_list": subs or ["x"],
            "negative_subcomponents_list": neg or []}


def five(table, status="pass", failures=0):
    return [rec(table, g[0], status, failures, g[1], g[2]) for g in rusdbt.GROUPS]


def neg_control(status="fail", failures=4601):
    return rec(rusdbt.CORE, "total_long_term_debt", status, failures,
               rusdbt.LTD + ["payments_unapplied"], [])


class TestBlock(unittest.TestCase):
    def test_generated_block_equals_pr_text(self):
        with open(os.path.join(HERE, "tests-block.yml"), encoding="utf-8") as fh:
            pr_text = fh.read()
        self.assertEqual("\n".join(rusdbt.proposed_lines()) + "\n", pr_text)

    def test_every_label_once_under_grand_total(self):
        leaves = []
        for total, subs, neg in rusdbt.GROUPS[:4]:
            leaves += subs + neg
        grand = rusdbt.GROUPS[4][1]
        leaves += [s for s in grand if not s.startswith("total_")]
        self.assertEqual(len(leaves), 23)
        self.assertEqual(len(set(leaves)), 23)

    def test_negative_control_adds_payments_unapplied(self):
        total, subs, neg = rusdbt.NEG_CONTROL
        self.assertEqual(total, "total_long_term_debt")
        self.assertIn("payments_unapplied", subs)
        self.assertEqual(neg, [])
        self.assertTrue(rusdbt.NEG_LOW <= rusdbt.NEG_EXPECTED <= rusdbt.NEG_HIGH)


class TestPatch(unittest.TestCase):
    def test_inserts_before_columns(self):
        out = rusdbt.patch_schema(SAMPLE, rusdbt.CORE, ["          - X"])
        lines = out.split("\n")
        i = lines.index("          - X")
        self.assertEqual(lines[i - 1], "          - expect_columns_not_all_null")
        self.assertEqual(lines[i + 1], "        columns:")
        self.assertEqual(out.replace("          - X\n", ""), SAMPLE)

    def test_missing_table_raises(self):
        with self.assertRaises(ValueError):
            rusdbt.patch_schema(SAMPLE, rusdbt.OUT, ["x"])

    def test_missing_columns_raises(self):
        text = SAMPLE.replace("        columns:\n          - name: report_date\n", "")
        with self.assertRaises(ValueError):
            rusdbt.patch_schema(text, rusdbt.CORE, ["x"])


class TestRecords(unittest.TestCase):
    def test_find_key_nested(self):
        kw = {"model": "m", "arguments": {"total_label": "t", "a": [{"b": 1}]}}
        self.assertEqual(rusdbt.find_key(kw, "total_label"), "t")
        self.assertEqual(rusdbt.find_key(kw, "b"), 1)
        self.assertIsNone(rusdbt.find_key(kw, "zzz"))

    def test_records_from_manifest(self):
        uid = "test.p.source_subcomponents_x"
        rr = {"results": [
            {"unique_id": uid, "status": "fail", "failures": 7, "message": "Got 7"},
            {"unique_id": "test.p.other", "status": "pass", "failures": 0},
        ]}
        mf = {"nodes": {
            uid: {"test_metadata": {"name": "subcomponents_sum_to_total",
                                    "kwargs": {"total_label": "total_long_term_debt",
                                               "subcomponents_list": ["a"],
                                               "negative_subcomponents_list": ["payments_unapplied"]}},
                  "depends_on": {"nodes": ["source.p.pudl." + rusdbt.CORE]}},
            "test.p.other": {"test_metadata": {"name": "expect_columns_not_all_null"}},
        }}
        recs = rusdbt.records_from(rr, mf)
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs[0]["table"], rusdbt.CORE)
        self.assertEqual(recs[0]["failures"], 7)
        self.assertEqual(recs[0]["negative_subcomponents_list"], ["payments_unapplied"])


class TestEvaluate(unittest.TestCase):
    def base(self):
        return (five(rusdbt.CORE) + five(rusdbt.OUT) + [neg_control()]
                + [rec(rusdbt.ASSETS, "total")])

    def test_all_held(self):
        v = rusdbt.evaluate(self.base())
        self.assertEqual(v, {"P1": "held", "P2": "held", "P3": "held", "P4": "held"})

    def test_one_failure_fails_p2(self):
        recs = self.base()
        recs[5 + 2] = rec(rusdbt.OUT, "total_noncurrent_obligations", "fail", 3)
        v = rusdbt.evaluate(recs)
        self.assertEqual(v["P1"], "held")
        self.assertEqual(v["P2"], "failed")

    def test_error_is_not_tested(self):
        recs = self.base()
        recs[0] = rec(rusdbt.CORE, "total_margins_and_equities", "error", None)
        self.assertEqual(rusdbt.evaluate(recs)["P1"], "not tested")

    def test_missing_test_is_not_tested(self):
        recs = self.base()
        del recs[0]
        self.assertEqual(rusdbt.evaluate(recs)["P1"], "not tested")

    def test_neg_control_bounds(self):
        for n, want in ((4555, "held"), (4647, "held"), (4554, "failed"),
                        (4648, "failed"), (0, "failed")):
            recs = self.base()
            recs[10] = neg_control("fail" if n else "pass", n)
            self.assertEqual(rusdbt.evaluate(recs)["P3"], want, n)

    def test_no_assets_is_not_tested(self):
        recs = self.base()[:-1]
        self.assertEqual(rusdbt.evaluate(recs)["P4"], "not tested")


if __name__ == "__main__":
    unittest.main()
