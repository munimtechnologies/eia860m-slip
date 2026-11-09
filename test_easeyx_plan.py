"""Checks that docs/easeyx-plan.md is a complete pre-registration (id, what was seen, gates,
predictions with probabilities, what happens with the result, limits), that its bars match the
constants in tools/easeyx/easeyx.py, and runs the tool's own unit tests
(tools/easeyx/test_easeyx.py) on made-up rows. Reads no outside data.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "tools", "easeyx"))

from test_easeyx import (BuildTests, ConstantTests, HelperTests,  # noqa: E402,F401
                         ReadTests, ScoreTests)


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class EaseyxPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = read("docs/easeyx-plan.md")
        cls.code = read("tools/easeyx/easeyx.py")
        cls.fetch = read("tools/easeyx/fetch_plan_code.py")

    def test_structure(self):
        for text in ("Status: pre-registration, nothing run yet. Pre-registration id: easeyx-1.",
                     "## What we have seen (before writing this)", "## Method",
                     "## Gate (if it fails, nothing is scored)",
                     "## Predictions (probability we give each)",
                     "## What happens with the result", "## Limits",
                     "made with AI agents working in MV2's name",
                     "no person has checked this plan by hand",
                     "A failed bar is reported as failed, with its cause, and is not re-scored.",
                     "camd-eia-crosswalk-latest/issues/7", "pudl/issues/5752",
                     "e52a3a533f745b98b88f0556473fee0d4cbcf96d", "Not seen:"):
            self.assertIn(text, self.plan)

    def test_predictions(self):
        for text in ("**P1 (55%):** between 70% and 85% of reference keys",
                     "**P2 (70%):** of the reference keys missing from `facility-2024.csv`, "
                     "at least 80%",
                     "**P3 (65%):** at least 97% of reference keys",
                     "**P4 (40%):**", "at most 5% of reference keys",
                     "**P5 (50%):**", "for at least 90%.",
                     "**Gate G1:**", "between 7,000 and 7,400 data rows",
                     "**Gate G2:** all 15 files 2010-2024",
                     "**Gate G3:** `facility-2024.csv` has at least 3,000 rows, and at least 50%",
                     "derived retirement year is before 2010",
                     "`tools/easeyx/easeyx.py` 0.1.0", "120-minute limit"):
            self.assertIn(text, self.plan)

    def test_bars_match_code(self):
        for text in ('VERSION = "0.1.0"', "FIRST_YEAR = 2010", "SCORED_LAST = 2024",
                     "EXTRA_YEAR = 2025", "EARLIEST_RET = 2010", "G1_MIN_ROWS = 7000",
                     "G1_MAX_ROWS = 7400", "G3_MIN_ROWS_2024 = 3000",
                     "G3_MIN_UNION_SHARE = 0.50", "P1_MIN = 0.70", "P1_MAX = 0.85",
                     "P2_MIN = 0.80", "P3_MIN = 0.97", "P4_MAX = 0.05", "P5_MIN = 0.90",
                     'REF_SHA = "e52a3a533f745b98b88f0556473fee0d4cbcf96d"',
                     "https://api.epa.gov/easey/bulk-files/facility/facility-{year}.csv"):
            self.assertIn(text, self.code)
        self.assertIn('TOKEN = "Pre-registration id: easeyx-1."', self.fetch)
        self.assertIn("Apache-2.0", self.code)


if __name__ == "__main__":
    unittest.main()
