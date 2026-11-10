"""Checks that docs/easeyx3-plan.md is a complete pre-registration (id, what was seen, gates,
predictions with probabilities, what happens with the result, limits), that its bars match the
constants in tools/easeyx/easeyx3.py, and runs the tool's own unit tests
(tools/easeyx/test_easeyx3.py) on made-up rows. Reads no outside data.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "tools", "easeyx"))

from test_easeyx3 import (ConstantTests, HelperTests, ReadTests,  # noqa: E402,F401
                          ScoreTests)


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class Easeyx3PlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = read("docs/easeyx3-plan.md")
        cls.code = read("tools/easeyx/easeyx3.py")
        cls.fetch = read("tools/easeyx/fetch_plan_code3.py")

    def test_structure(self):
        for text in ("Status: pre-registration, nothing run yet. Pre-registration id: easeyx-3.",
                     "## What we have seen (before writing this)", "## Method",
                     "## Gate (if it fails, nothing is scored)",
                     "## Predictions (probability we give each)",
                     "## What happens with the result", "## Limits",
                     "made with AI agents working in MV2's name",
                     "no person has checked this plan by hand",
                     "A failed bar is reported as failed, with its cause, and is not re-scored.",
                     "camd-eia-crosswalk-latest/issues/7", "pudl/issues/5705", "(easeyx.md)",
                     "(easeyx2.md)", "e52a3a533f745b98b88f0556473fee0d4cbcf96d", "Not seen:",
                     "JCT21-JCT30"):
            self.assertIn(text, self.plan)

    def test_predictions(self):
        for text in ("**P1 (65%):**", "at least 90% are linked reference keys",
                     "**P2 (70%):** at least 80% of linked reference keys keep the same ids.",
                     "**P3 (70%):**", "the reference links at least 95% to that pair.",
                     "**P4 (45%):**", "at least 60% have their same-id pair among the PUDL pairs.",
                     "**P5 (40%):** at least 10 reference keys are first seen in the 2025 file",
                     "**Gate G1:**", "**Gate G2:** the EPA-side file has 7,187 data rows",
                     "**Gate G3:**", "at least 20,000 distinct (plant, generator) pairs, and report "
                     "year 2024", "`tools/easeyx/easeyx3.py` 0.1.0", "`tools/easeyx/easeyx.py` 0.1.0",
                     "420-minute limit", "core_eia860__scd_generators"):
            self.assertIn(text, self.plan)

    def test_bars_match_code(self):
        for text in ('VERSION = "0.1.0"', "G2_SIDE_ROWS = 7187", "G3_MIN_PAIRS = 20000",
                     "G3_YEAR = 2024", "NEW_YEAR = 2025", "P1_MIN = 0.90", "P2_MIN = 0.80",
                     "P3_MIN = 0.95", "P4_MIN = 0.60", "P5_MIN_KEYS = 10",
                     'REF_MD5 = "106d813fd9b850f11a0be088f317ef13"',
                     'GEN_TABLE = "core_eia860__scd_generators"', "Apache-2.0"):
            self.assertIn(text, self.code)
        self.assertIn('TOKEN = "Pre-registration id: easeyx-3."', self.fetch)
        self.assertIn('"easeyx.py", "easeyx3.py", "test_easeyx3.py"', self.fetch)


if __name__ == "__main__":
    unittest.main()
