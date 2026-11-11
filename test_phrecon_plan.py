"""Checks that docs/phrecon-plan.md is a complete pre-registration (id, what was seen, gates,
predictions with probabilities, what happens with the result, limits), that its bars match the
constants in tools/phrecon/phrecon.py, and runs the tool's own unit tests
(tools/phrecon/test_phrecon.py) on made-up rows. Reads no outside data.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "tools", "phrecon"))

import phrecon  # noqa: E402
from test_phrecon import (AggTests, CompareTests, ConstantTests, HelperTests,  # noqa: E402,F401
                          ScoreTests)


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class PhreconPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = read("docs/phrecon-plan.md")
        cls.code = read("tools/phrecon/phrecon.py")
        cls.fetch = read("tools/phrecon/fetch_plan_phrecon.py")

    def test_structure(self):
        for text in ("Status: pre-registration, nothing run yet. Pre-registration id: phrecon-1.",
                     "## What we have seen (before writing this)", "## Method",
                     "## Gate (if it fails, nothing is scored)",
                     "## Predictions (probability we give each)",
                     "## What happens with the result", "## Limits",
                     "made with AI agents working in MV2's name",
                     "no person has checked this plan by hand",
                     "no person has checked these quotes against the PDFs",
                     "A failed bar is reported as failed, with its cause, and is not re-scored.",
                     "pudl/issues/4646", "Not seen:", "2,250,542 bytes", "1,034,817 bytes",
                     "to reconcile totals across Parts B1 and B4",
                     "spend time validating the numeric data"):
            self.assertIn(text, self.plan)
        self.assertNotIn("MIT", self.plan)

    def test_predictions(self):
        for text in ("**P1 (70%):** at least 97% of comparable 2017 to 2025 reports pass "
                     "PHMSA's rule for mains.",
                     "**P2 (55%):** at least 90% of comparable 2017 to 2025 reports match "
                     "exactly for mains.",
                     "**P3 (60%):**", "at least 60% are B4 higher",
                     "If fewer than 10 fail, there is nothing to test, and P3 counts as failed.",
                     "**P4 (65%):** at least 95% of comparable 2017 to 2025 reports pass "
                     "PHMSA's rule for services.",
                     "**P5 (55%):**", "at least 10 percentage points higher",
                     "If fewer than 1,000 reports from 2009 and earlier are comparable, there is "
                     "nothing to test, and P5 counts as failed.",
                     "**P6 (50%):**", "at least one negative `mains_miles` or `services` value",
                     "**P7 (75%):**", "in at least 97% of comparable 2017 to 2025 reports.",
                     "**Gate G1:**", "**Gate G2:** at least 5,000 comparable reports for mains "
                     "in 2017 to 2025, and at least 300 in each of those 9 years.",
                     "`tools/phrecon/phrecon.py` 0.1.0", "240-minute limit", "up to 3,000 rows",
                     "up to 2,000 rows", "1 CPU, 2 GB", "within 0.5% of the B4 sum",
                     "within 0.3 miles (mains) or exactly equal (services)",
                     "mains within 0.001 miles", "leaving out `all_materials`"):
            self.assertIn(text, self.plan)

    def test_bars_match_code(self):
        for text in ('VERSION = "0.1.0"', "G2_MIN_LATE = 5000", "G2_MIN_PER_YEAR = 300",
                     "P1_MIN = 0.97", "P2_MIN = 0.90", "P3_MIN = 0.60", "P3_MIN_FAILS = 10",
                     "P4_MIN = 0.95", "P5_GAP = 0.10", "P5_MIN_PRE = 1000", "P6_MIN_NEG = 1",
                     "P7_MIN = 0.97", "FAIL_CAP = 3000", "NEG_CAP = 2000", "BIG = 60.0",
                     "SHARE_TOL = 0.005", "SMALL_MAINS_TOL = 0.3", "EXACT_MAINS_TOL = 0.001",
                     "LATE_FIRST = 2017", "LATE_LAST = 2025", "PRE_LAST = 2009",
                     'SKIP_MATERIALS = ("all_materials",)', "Apache-2.0"):
            self.assertIn(text, self.code)
        self.assertEqual(phrecon.LATE_LAST - phrecon.LATE_FIRST + 1, 9)
        self.assertIn("_core_phmsagas__yearly_distribution_by_material.parquet", self.plan)
        self.assertIn(phrecon.B4_TABLE + ".parquet", self.plan)
        self.assertIn('TOKEN = "Pre-registration id: phrecon-1."', self.fetch)
        self.assertIn('FILES = ("phrecon.py", "test_phrecon.py")', self.fetch)


if __name__ == "__main__":
    unittest.main()
