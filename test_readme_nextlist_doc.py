"""Doc test: what README.md says about the October 2026 next-month list and the two plans added on
26-27 October 2026 (docs/nextlist-plan.md, docs/q4clus-plan.md) matches the plans themselves, and the
paragraphs around the additions are unchanged.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8") as fh:
        return fh.read()


class ReadmeNextlistTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.readme = read("README.md")
        cls.plan = read("docs", "nextlist-plan.md")
        cls.q4clus = read("docs", "q4clus-plan.md")

    def test_plans_not_scored(self):
        self.assertIn("Status: pre-registered, not yet scored.", self.plan)
        self.assertIn("Status: pre-registered, not yet scored.", self.q4clus)

    def test_list_paragraph(self):
        self.assertIn("**A list of every generator planned for October 2026, with base rates.** "
                      "[`docs/nextlist-2026-10.md`](docs/nextlist-2026-10.md) lists the 161 generators", self.readme)
        for s in ("the 161 generators at 136 plants (11,460.2 MW) that EIA's September 2026 workbook plans to start "
                  "operating in October 2026",
                  "the share of earlier generators in the same technology group and listing cell that were listed as "
                  "operating in their planned month",
                  "p expects 56.8 of the 161 generators on time",
                  "every month from January 2020 to September 2026",
                  "-0.0016 (95% interval -0.0034 to +0.0003)",
                  "the backtest does not show that the cells add anything beyond the plain shares",
                  "(expected 24 November 2026)",
                  "p describes earlier generators like each one; it is not a forecast made with knowledge of any "
                  "plant, and it is not advice."):
            self.assertIn(s, self.plan)
            self.assertIn(s, self.readme)
        self.assertIn("p's Brier score was 0.2295, r0's 0.2311", self.plan)
        self.assertIn("p's Brier score was 0.2295, against 0.2311 for the share of all rows", self.readme)
        self.assertIn("(data: [`data/nextlist_2026-10.csv`](data/nextlist_2026-10.csv))", self.readme)
        self.assertIn("is pre-registered in [`docs/nextlist-plan.md`](docs/nextlist-plan.md) and is scored after "
                      "EIA's October 2026 workbook", self.readme)

    def test_plans_paragraph(self):
        self.assertIn("Also [`q4clus-plan.md`](docs/q4clus-plan.md) (whether, in the next-month groups of October to "
                      "December 2026 pooled, the solar and battery one-month-slip gaps that the forty-first result "
                      "left standing point the same way, with whole plants resampled)", self.readme)
        self.assertIn("Scored period: October, November and December 2026 pooled.", self.q4clus)
        self.assertIn("This plan asks whether the three readings that stand point the same way", self.q4clus)
        self.assertIn("2,000 resamples of them with replacement", self.q4clus)
        self.assertIn("and [`nextlist-plan.md`](docs/nextlist-plan.md) (whether p on the October 2026 list has a "
                      "lower Brier score than the share of all rows and than the technology group's share, two bars).",
                      self.readme)
        for s in ("- **N1.** The Brier score of p on the October list is lower than r0's.",
                  "- **N2.** The Brier score of p on the October list is lower than r1's.",
                  "r0, the share of all rows, and r1, the technology group's share"):
            self.assertIn(s, self.plan)
        self.assertNotIn("**N3.**", self.plan)

    def test_placement_and_neighbours(self):
        series = self.readme.index("**The series in one place.**")
        listing = self.readme.index("**A list of every generator planned for October 2026, with base rates.**")
        results = self.readme.index("## All results")
        self.assertLess(series, listing)
        self.assertLess(listing, results)
        self.assertEqual(self.readme.count("**A list of every generator planned for October 2026"), 1)
        # The paragraph of plans not yet scored still starts as before and keeps q4held-plan.md's sentence whole.
        self.assertIn("Pre-registered, not yet scored: [`dec2026-plan.md`](docs/dec2026-plan.md) (whether December "
                      "2026 has the largest next-month group of 2026 and a share above the year's, two bars) and "
                      "[`oct2026-plan.md`](docs/oct2026-plan.md) (EIA's October 2026 workbook, due 24 November 2026, "
                      "scored on release against five bars", self.readme)
        self.assertIn("and rows with 5 or more earlier listings less often, three bars, fixed before any of those "
                      "months was published). Also [`q4clus-plan.md`](docs/q4clus-plan.md)", self.readme)
        for s in ("and what does not (the wind and gas reversals, and a one-month advantage for all technologies "
                  "together).",
                  "| 34-41 | The next-month series in one place: every bar and outcome, and what still stands "
                  "(descriptive) | [`nextmonth-series.md`](docs/nextmonth-series.md) |",
                  "Code: Apache License 2.0 (see LICENSE)."):
            self.assertIn(s, self.readme)
        self.assertNotIn("MIT", self.readme)


if __name__ == "__main__":
    unittest.main()
