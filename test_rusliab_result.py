"""Checks that every count stated in docs/rusliab.md is what data/rusliab-run.json (the output of
job rusliab-v1, unchanged) says. Reads no outside data.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TABLES = ("core_rus7__yearly_balance_sheet_liabilities",
          "out_rus7__yearly_balance_sheet_liabilities")
EXPECTED = {
    "margins_and_equities": 0,
    "long_term_debt_less_unapplied": 0,
    "long_term_debt_plus_unapplied": 4601,
    "long_term_debt_without_unapplied": 4599,
    "noncurrent_obligations": 0,
    "current_and_accrued": 0,
    "liabilities_and_other_credits": 0,
}


def path(rel):
    return os.path.join(HERE, rel)


class RusliabResultTests(unittest.TestCase):
    # The job's JSON is kept as `res`: naming it `run` would hide unittest's TestCase.run.
    @classmethod
    def setUpClass(cls):
        with open(path("docs/rusliab.md"), encoding="utf-8") as fh:
            cls.doc = fh.read()
        with open(path("data/rusliab-run.json"), encoding="utf-8") as fh:
            cls.res = json.load(fh)

    def test_tables(self):
        self.assertEqual(self.res["tolerance"], 10)
        for t in TABLES:
            tab = self.res["tables"][t]
            self.assertEqual((tab["rows"], tab["groups"], len(tab["labels"])), (237524, 8483, 28))
            self.assertEqual(tab["rows"], 28 * 8483)
            self.assertEqual((tab["years"][0], tab["years"][-1], len(tab["years"])),
                             ("2006", "2021", 16))
            self.assertEqual(tab["labels_missing_from_tests"], [])
            self.assertEqual(tab["test_labels_missing_from_table"], [])
            self.assertEqual(len(tab["is_total_labels"]), 5)
            self.assertTrue(all(n_null == 0 for n_null, _ in tab["nulls_by_label"].values()))
            self.assertEqual(tab["payments_unapplied"],
                             {"nonnull": 8483, "positive": 4602, "negative": 1})
        for text in ("237,524 rows", "8,483 borrower-years (report years 2006-2021)",
                     "28 `liability_type` labels", "with no null `ending_balance`",
                     "non-zero in 4,603 borrower-years (4,602 positive, 1 negative)"):
            self.assertIn(text, self.doc)

    def test_counts(self):
        for t in TABLES:
            tests = self.res["tables"][t]["tests"]
            self.assertEqual(set(tests), set(EXPECTED))
            for name, fails in EXPECTED.items():
                tr = tests[name]
                self.assertEqual((tr["groups_checked"], tr["groups_without_total"],
                                  tr["groups_without_subcomponents"], tr["failures"]),
                                 (8483, 0, 0, fails), (t, name))
            self.assertEqual(tests["long_term_debt_less_unapplied"]["negative_subcomponents"],
                             ["payments_unapplied"])
        self.assertEqual(self.doc.count("| 8,483 | 0 |"), 5)
        self.assertIn("| 8,483 | 4,601 (54.2%) |", self.doc)
        self.assertIn("| 8,483 | 4,599 (54.2%) |", self.doc)
        self.assertEqual(round(100 * 4601 / 8483, 1), 54.2)
        self.assertEqual(round(100 * 4599 / 8483, 1), 54.2)

    def test_labels_used_once(self):
        tests = self.res["tables"][TABLES[0]]["tests"]
        used = []
        for name in ("margins_and_equities", "long_term_debt_less_unapplied",
                     "noncurrent_obligations", "current_and_accrued"):
            used += tests[name]["subcomponents"] + tests[name]["negative_subcomponents"]
        grand = tests["liabilities_and_other_credits"]["subcomponents"]
        leaves = used + [g for g in grand if not g.startswith("total_")]
        self.assertEqual(len(leaves), 23)
        self.assertEqual(len(set(leaves)), 23)
        totals = set(self.res["tables"][TABLES[0]]["is_total_labels"])
        self.assertEqual(set(self.res["tables"][TABLES[0]]["labels"]), set(leaves) | totals)
        self.assertEqual(sum(g.startswith("total_") for g in grand), 4)

    def test_largest_case(self):
        tests = self.res["tables"][TABLES[0]]["tests"]
        top_without = tests["long_term_debt_without_unapplied"]["largest_failures"][0]
        top_plus = tests["long_term_debt_plus_unapplied"]["largest_failures"][0]
        self.assertEqual(top_without["key"], ["SC0031", "2018-12-01"])
        self.assertEqual(top_plus["key"], ["SC0031", "2018-12-01"])
        debt = top_without["subcomponents_sum"]
        unapplied = top_plus["subcomponents_sum"] - debt
        total = top_without["grand_total"]
        self.assertEqual((debt, unapplied, total), (227198268.0, 110621576.0, 116576692.0))
        self.assertEqual(debt - unapplied, total)
        self.assertIn("debt lines $227,198,268, payments unapplied $110,621,576, total $116,576,692",
                      self.doc)

    def test_balance_and_next(self):
        b = self.res["balance_check_not_preregistered"]
        self.assertEqual((b["pairs"], b["failures"]), (8483, 0))
        nxt = {d["table"]: d["rows"] for d in self.res["next_tables"]}
        self.assertEqual(nxt, {"core_rus7__yearly_utility_plant_changes": 77848,
                               "core_rus7__yearly_statement_of_operations": 199762})
        self.assertIn("77,848 rows", self.doc)
        self.assertIn("199,762 rows", self.doc)

    def test_disclosure(self):
        for text in ("made with AI agents working in MV2's name",
                     "no person has checked these results by hand",
                     "not from dbt", "pudl/issues/5154", "not a pre-registered study"):
            self.assertIn(text, self.doc)


if __name__ == "__main__":
    unittest.main()
