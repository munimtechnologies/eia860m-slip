"""Checks that every number stated in docs/rusdbt.md (result of pre-registration rusdbt-1) is what
data/rusdbt-run.json and data/rusdbt-dbt-stdout.txt (the job's outputs, unchanged) say. Reads no
outside data.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
CORE = "core_rus7__yearly_balance_sheet_liabilities"
OUT = "out_rus7__yearly_balance_sheet_liabilities"
ASSETS = "core_rus7__yearly_balance_sheet_assets"
TOTALS = ("total_margins_and_equities", "total_long_term_debt", "total_noncurrent_obligations",
          "total_current_and_accrued_liabilities", "total_liabilities_and_other_credits")


def path(rel):
    return os.path.join(HERE, rel)


class RusdbtResultTests(unittest.TestCase):
    # The job's JSON is kept as `res`: naming it `run` would hide unittest's TestCase.run.
    @classmethod
    def setUpClass(cls):
        with open(path("docs/rusdbt.md"), encoding="utf-8") as fh:
            cls.doc = fh.read()
        with open(path("data/rusdbt-run.json"), encoding="utf-8") as fh:
            cls.res = json.load(fh)
        with open(path("data/rusdbt-dbt-stdout.txt"), encoding="utf-8", errors="replace") as fh:
            cls.stdout = fh.read()
        cls.results = cls.res["results"]

    def proposed(self, table):
        return [r for r in self.results if r["table"] == table
                and "payments_unapplied" not in r["subcomponents_list"]]

    def negative(self):
        return [r for r in self.results if "payments_unapplied" in r["subcomponents_list"]]

    def test_setup(self):
        self.assertEqual(self.res["tool"], "rusdbt 0.1.0")
        self.assertIn("`rusdbt 0.1.0`", self.doc)
        self.assertEqual(self.res["pudl_commit"], "060c1875c47d557420cd63e55ca07dce2bc80838")
        self.assertIn("commit `" + self.res["pudl_commit"] + "`", self.doc)
        self.assertIn("installed: 1.12.7", self.res["dbt_version"])
        self.assertIn("duckdb: 1.11.1", self.res["dbt_version"])
        self.assertIn("dbt-core 1.12.7 with dbt-duckdb 1.11.1", self.doc)
        for table, size in ((CORE, "1,025,519"), (OUT, "1,115,797"), (ASSETS, "1,064,867")):
            self.assertEqual(f"{self.res['tables'][table]['bytes']:,}", size)
            self.assertIn(f"`{table}` ({size} bytes)", self.doc)
        self.assertEqual((self.res["dbt_deps_rc"], self.res["dbt_test_rc"]), (0, 1))

    def test_counts_and_summary(self):
        self.assertEqual(len(self.results), 16)
        self.assertIn("16 data tests ran", self.doc)
        self.assertIn("PASS=15 WARN=0 ERROR=1 SKIP=0", self.stdout)
        self.assertIn("`PASS=15 WARN=0 ERROR=1 SKIP=0`", self.doc)
        self.assertEqual(sum(r["status"] == "pass" for r in self.results), 15)

    def test_verdicts(self):
        self.assertEqual(self.res["verdicts"],
                         {"P1": "held", "P2": "held", "P3": "held", "P4": "held"})
        self.assertIn("**All 4 predictions held (P1-P4).**", self.doc)

    def test_p1_p2(self):
        for table in (CORE, OUT):
            rows = self.proposed(table)
            self.assertEqual(sorted(r["total_label"] for r in rows), sorted(TOTALS), table)
            for r in rows:
                self.assertEqual((r["status"], r["failures"]), ("pass", 0), r["unique_id"])
            ltd = [r for r in rows if r["total_label"] == "total_long_term_debt"][0]
            self.assertEqual(ltd["negative_subcomponents_list"], ["payments_unapplied"])
        self.assertIn("| P1 five proposed tests on the core table | all pass, 0 failures | "
                      "5 of 5 pass | yes |", self.doc)
        self.assertIn("| P2 five proposed tests on the out table | all pass, 0 failures | "
                      "5 of 5 pass | yes |", self.doc)
        for t in TOTALS:
            self.assertIn(f"| `{t}`", self.doc)

    def test_p3_negative_control(self):
        neg = self.negative()
        self.assertEqual(len(neg), 1)
        n = neg[0]
        self.assertEqual((n["table"], n["status"], n["failures"]), (CORE, "fail", 4601))
        self.assertEqual(n["negative_subcomponents_list"], [])
        self.assertTrue(4555 <= n["failures"] <= 4647)
        self.assertIn("FAIL 4601", self.stdout)
        self.assertIn("| P3 negative control fails | 4,555-4,647 failing borrower-years | 4,601 | yes |",
                      self.doc)
        self.assertIn("failed for exactly 4,601 borrower-years", self.doc)

    def test_p4_positive_control(self):
        rows = [r for r in self.results if r["table"] == ASSETS]
        self.assertEqual(len(rows), 5)
        for r in rows:
            self.assertEqual((r["status"], r["failures"]), ("pass", 0), r["unique_id"])
        self.assertIn("| P4 existing assets tests pass | all pass | 5 of 5 pass | yes |", self.doc)

    def test_disclosure(self):
        for text in ("Made with AI agents working in MV2's name",
                     "no person\nhas checked these results by hand",
                     "Text and data CC BY 4.0; code Apache-2.0.",
                     "23:24:46 UTC on 11 November 2026, commit `6d5d7cc`",
                     "pudl/issues/5760",
                     "not checked against the RUS Form 7\n  instructions"):
            self.assertIn(text, self.doc)


if __name__ == "__main__":
    unittest.main()
