"""Checks that docs/rusops-plan.md describes what tools/rusops/ runs: id, version, tables, the
regex, the line-29 items and the bars. Reads every file as text.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class RusopsPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/rusops-plan.md")
        cls.code = read("tools/rusops/rusops.py")
        cls.tests = read("tools/rusops/test_rusops.py")

    def test_status_and_id(self):
        self.assertIn("Status: pre-registration, nothing run yet.", self.doc)
        self.assertIn("Pre-registration id: rusops-1.", self.doc)
        self.assertIn("pre-registration id rusops-1", self.code)

    def test_version(self):
        self.assertIn('VERSION = "0.1.0"', self.code)
        self.assertIn("`tools/rusops/rusops.py` 0.1.0", self.doc)

    def test_tables_and_colmap(self):
        for table in ("core_rus7__yearly_statement_of_operations",
                      "out_rus7__yearly_statement_of_operations"):
            self.assertIn('"%s"' % table, self.code)
            self.assertIn("`%s`" % table, self.doc)
        path = "src/pudl/package_data/rus7/column_maps/statement_of_operations.csv"
        self.assertIn(path, self.code)
        self.assertIn(path, self.doc)
        for g in ("cost_of_electric_service", "opex", "patronage_and_operating_margins",
                  "patronage_capital_or_margins"):
            self.assertIn('"%s"' % g, self.code)
            self.assertIn("`%s`" % g, self.doc)
        self.assertIn('PERIODS = ["opex_ytd", "opex_ytd_budget", "opex_report_month"]', self.code)
        self.assertIn("_ytd_opex_report_month", self.code)

    def test_line29_items(self):
        for t in ("total_minus", "non_operating_margins_interest", "construction_funds_allowance",
                  "equity_investment_losses", "non_operating_margins_other",
                  "generation_and_transmission_capital", "extraordinary_items"):
            self.assertIn('"%s"' % t, self.code)
            self.assertIn("`%s`" % t, self.doc)
        self.assertIn('OCC = "other_capital_credits"', self.code)
        self.assertIn('OCC_YTD = "other_capital_credits_ytd"', self.code)
        self.assertIn('LINE29_TOTAL = ("patronage_capital_or_margins", "total")', self.code)

    def test_constants_match_bars(self):
        for text in ("TOL = 10", "P3_SHARE = 0.01", "P5_SHARE = 0.05"):
            self.assertIn(text, self.code)
        for text in ("**Gate G1:**", "**P1 (90%):**", "**P2 (90%):**", "**P3 (60%):**",
                     "**P4 (65%):**", "**P5 (55%):**", "at least 1% of the table's borrower-years",
                     "fewer than 5% of the", "a $10 tolerance"):
            self.assertIn(text, self.doc)

    def test_scoring_lines(self):
        for text in ('"P1": split_ok(core)', '"P2": split_ok(out)',
                     '"P4": l29m["as_labelled"]["failures"] > l29m["merged"]["failures"]',
                     'a["opex_ytd"]["nonnull"] == 0', 'b["opex_report_month"]["nonnull"] == 0'):
            self.assertIn(text, self.code)
        for name in ("def test_misplaced_ytd_makes_an_orphan", "def test_split_label_fails_only_as_labelled",
                     "def test_ytd_unaffected", "def test_all_hold", "def test_each_can_fail"):
            self.assertIn(name, self.tests)

    def test_licence_and_disclosure(self):
        line = "PUDL's data (CC BY 4.0) is downloaded at run time and not stored here."
        self.assertIn(line, self.doc)
        self.assertIn(line, self.code)
        for text in (self.code, self.tests):
            self.assertIn("Apache-2.0", text)
        self.assertIn("No person has checked these results by hand.", self.doc)
        self.assertIn("Made with AI agents working in MV2's name", self.doc)


if __name__ == "__main__":
    unittest.main()
