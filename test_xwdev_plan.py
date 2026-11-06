"""Checks that docs/xwdev-plan.md is a complete pre-registration (id, what was seen, gate,
predictions with probabilities, what happens with the result, limits) and that its bars match
the constants in tools/xwdev/xwdev.py. Reads text only.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class XwdevPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = read("docs/xwdev-plan.md")
        cls.code = read("tools/xwdev/xwdev.py")
        cls.fetch = read("tools/xwdev/fetch_plan_code.py")

    def test_structure(self):
        for text in ("Status: pre-registration, nothing run yet. Pre-registration id: xwdev-1.",
                     "## What we have seen (before writing this)", "## Method",
                     "## Gate (if it fails, nothing is scored)",
                     "## Predictions (probability we give each)",
                     "## What happens with the result", "## Limits",
                     "made with AI agents working in MV2's name",
                     "no person has checked this plan by hand",
                     "No row of the file was reported to us",
                     "A failed bar is reported as failed, with its cause, and is not re-scored."):
            self.assertIn(text, self.plan)

    def test_predictions(self):
        for text in ("**P1 (50%):** the Antelope Elk lead stands.",
                     "**P2 (65%):** the Chalk Point lead stands.",
                     "**P3 (65%):** the Glenarm lead stands.",
                     "**P4 (65%):** the LEPA Unit No. 1 lead stands.",
                     "**P5 (40%):** all four leads stand.",
                     "at least 4,000 data rows"):
            self.assertIn(text, self.plan)

    def test_bars_match_code(self):
        for text in ('VERSION = "0.1.0"', "MIN_ROWS = 4000",
                     'COMMIT = "3423b2ab457222e1eac5d69d25a98b5f62ce5975"',
                     '("Chalk Point", 1571, {"SGT1": (1571, "GT1")}, ((61890, "SGT1"),))',
                     '("Glenarm", 422, {"STG5": (422, "GT5")}, ((422, "ST1"),))',
                     '("LEPA Unit No. 1", 58478, {"STG1": (58478, "LEPA1")}, '
                     '((58478, "LEPA2"),))',
                     'PLANT_IDS = (57865, 58835, 1571, 61890, 422, 58478)'):
            self.assertIn(text, self.code)
        self.assertIn('TOKEN = "Pre-registration id: xwdev-1."', self.fetch)
        for text in ("3423b2ab457222e1eac5d69d25a98b5f62ce5975",
                     "| Chalk Point | 1571 / SGT1 | EIA 1571 / GT1 | EIA 61890 / SGT1 |",
                     "| Glenarm | 422 / STG5 | EIA 422 / GT5 | EIA 422 / ST1 |",
                     "| LEPA Unit No. 1 | 58478 / STG1 | EIA 58478 / LEPA1 | EIA 58478 / LEPA2 |",
                     "`tools/xwdev/xwdev.py` 0.1.0"):
            self.assertIn(text, self.plan)


if __name__ == "__main__":
    unittest.main()
