"""Checks that docs/xwpudl-plan.md is a complete pre-registration (id, what was seen, gate,
predictions with probabilities, what happens with the result, limits) and that its bars match
the constants in tools/xwpudl/xwpudl.py. Reads text only.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class XwpudlPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = read("docs/xwpudl-plan.md")
        cls.code = read("tools/xwpudl/xwpudl.py")
        cls.fetch = read("tools/xwpudl/fetch_plan_code.py")

    def test_structure(self):
        for text in ("Status: pre-registration, nothing run yet. Pre-registration id: xwpudl-1.",
                     "## What we have seen (before writing this)", "## Method",
                     "## Gate (if it fails, nothing is scored)",
                     "## Predictions (probability we give each)",
                     "## What happens with the result", "## Limits",
                     "made with AI agents working in MV2's name",
                     "no person has checked this plan by hand",
                     "A failed bar is reported as failed, with its cause, and is not re-scored."):
            self.assertIn(text, self.plan)

    def test_predictions(self):
        for text in ("**P1 (80%):** the Chalk Point lead stands in the newest report year.",
                     "**P2 (70%):** the Glenarm lead stands in the newest report year.",
                     "**P3 (70%):** the LEPA Unit No. 1 lead stands in the newest report year.",
                     "**P4 (60%):**", "**P5 (55%):**",
                     "its newest report year is 2023 or later",
                     "at least 10 such candidate-years",
                     "for report year 2021"):
            self.assertIn(text, self.plan)

    def test_bars_match_code(self):
        for text in ('VERSION = "0.1.0"', "MIN_NEWEST = 2023", "MIN_P4_CELLS = 10",
                     "P5_YEAR = 2021", '("Chalk Point", 1571, {"SGT1": (1571, "GT1")}, '
                     '((61890, "SGT1"),))',
                     '("Glenarm", 422, {"STG5": (422, "GT5")}, ((422, "ST1"),))',
                     '("LEPA Unit No. 1", 58478, {"STG1": (58478, "LEPA1")}, '
                     '((58478, "LEPA2"),))'):
            self.assertIn(text, self.code)
        self.assertIn('TOKEN = "Pre-registration id: xwpudl-1."', self.fetch)
        for text in ("| Chalk Point | 1571 / SGT1 | EIA 1571 / GT1 | EIA 61890 / SGT1 |",
                     "| Glenarm | 422 / STG5 | EIA 422 / GT5 | EIA 422 / ST1 |",
                     "| LEPA Unit No. 1 | 58478 / STG1 | EIA 58478 / LEPA1 | EIA 58478 / LEPA2 |",
                     "`tools/xwpudl/xwpudl.py` 0.1.0"):
            self.assertIn(text, self.plan)


if __name__ == "__main__":
    unittest.main()
