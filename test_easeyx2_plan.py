"""Checks that docs/easeyx2-plan.md is a complete pre-registration (id, what was seen, gates,
predictions with probabilities, what happens with the result, limits), that its bars match the
constants in tools/easeyx/easeyx2.py, and runs the tool's own unit tests
(tools/easeyx/test_easeyx2.py) on made-up rows. Reads no outside data.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "tools", "easeyx"))

from test_easeyx2 import (ConstantTests, HelperTests, ReadTests,  # noqa: E402,F401
                          ScoreTests)


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class Easeyx2PlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = read("docs/easeyx2-plan.md")
        cls.code = read("tools/easeyx/easeyx2.py")
        cls.fetch = read("tools/easeyx/fetch_plan_code2.py")

    def test_structure(self):
        for text in ("Status: pre-registration, nothing run yet. Pre-registration id: easeyx-2.",
                     "## What we have seen (before writing this)", "## Method",
                     "## Gate (if it fails, nothing is scored)",
                     "## Predictions (probability we give each)",
                     "## What happens with the result", "## Limits",
                     "made with AI agents working in MV2's name",
                     "no person has checked this plan by hand",
                     "A failed bar is reported as failed, with its cause, and is not re-scored.",
                     "camd-eia-crosswalk-latest/issues/7", "(easeyx.md)",
                     "e52a3a533f745b98b88f0556473fee0d4cbcf96d", "Not seen:"):
            self.assertIn(text, self.plan)

    def test_predictions(self):
        for text in ("**P1 (80%):** state matches for at least 99%.",
                     "**P2 (60%):** facility name matches for at least 90%.",
                     "**P3 (55%):** nameplate capacity is within 0.05 MW for at least 90%.",
                     "**P4 (50%):** fuel matches for at least 90%.",
                     "**P5 (60%):** coordinates are within 0.001 degrees for at least 90%.",
                     "**P6 (55%):**", "the last year or the last year plus one for at least 85%.",
                     "**Gate G1:**", "between 7,000 and 7,400 data rows",
                     "**Gate G2:** all 15 files 2010-2024",
                     "**Gate G3:** at least 6,900 reference keys",
                     "between 300 and 500",
                     "`tools/easeyx/easeyx2.py` 0.1.0", "`tools/easeyx/easeyx.py` 0.1.0",
                     "420-minute limit"):
            self.assertIn(text, self.plan)

    def test_bars_match_code(self):
        for text in ('VERSION = "0.1.0"', "FIRST_YEAR = 2010", "LAST_YEAR = 2024",
                     "G1_MIN_ROWS = 7000", "G1_MAX_ROWS = 7400", "G3_MIN_FOUND = 6900",
                     "G3_SILENT_MIN = 300", "G3_SILENT_MAX = 500", "CAP_TOL = 0.05",
                     "COORD_TOL = 0.001", "P1_MIN = 0.99", "P2_MIN = 0.90", "P3_MIN = 0.90",
                     "P4_MIN = 0.90", "P5_MIN = 0.90", "P6_MIN = 0.85",
                     'REF_MD5 = "106d813fd9b850f11a0be088f317ef13"', "Apache-2.0"):
            self.assertIn(text, self.code)
        self.assertIn('TOKEN = "Pre-registration id: easeyx-2."', self.fetch)
        self.assertIn('"easeyx.py", "easeyx2.py", "test_easeyx2.py"', self.fetch)


if __name__ == "__main__":
    unittest.main()
