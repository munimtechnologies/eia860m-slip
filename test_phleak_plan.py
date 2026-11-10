"""Checks that docs/phleak-plan.md is a complete pre-registration (id, what was seen, gates,
predictions with probabilities, what happens with the result, limits), that its bars match the
constants in tools/phleak/phleak.py, and runs the tool's own unit tests
(tools/phleak/test_phleak.py) on made-up rows. Reads no outside data.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "tools", "phleak"))

from test_phleak import (ConstantTests, HelperTests, ProfileTests)  # noqa: E402,F401


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class PhleakPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = read("docs/phleak-plan.md")
        cls.code = read("tools/phleak/phleak.py")
        cls.fetch = read("tools/phleak/fetch_plan_phleak.py")

    def test_structure(self):
        for text in ("Status: pre-registration, nothing run yet. Pre-registration id: phleak-1.",
                     "## What we have seen (before writing this)", "## Method",
                     "## Gate (if it fails, nothing is scored)",
                     "## Predictions (probability we give each)",
                     "## What happens with the result", "## Limits",
                     "made with AI agents working in MV2's name",
                     "no person has checked this plan by hand",
                     "A failed bar is reported as failed, with its cause, and is not re-scored.",
                     "pudl/issues/5435", "pudl/issues/4646", "Not seen:", "1,734,682 bytes",
                     "_core_phmsagas__yearly_distribution_leaks.parquet"):
            self.assertIn(text, self.plan)

    def test_predictions(self):
        for text in ("**P1 (70%):** no row before report year 2015 has a commodity, and at most 1%",
                     "**P2 (75%):**", "15-entry map",
                     "**P3 (55%):**", "at least 95% equal the sum of their sources within 1.",
                     "**P4 (80%):**", "in at least 99% of compared",
                     "**P5 (70%):** the proposed key has no duplicate rows.",
                     "**P6 (70%):** at least 100 rows have a multi-state", "up to 2003.",
                     "**P7 (45%):** no row has a negative mains or services value.",
                     "**Gate G1:**", "**Gate G2:** at least 10,000 rows, report years 2015 and 2024",
                     "no later than 2003", "**Gate G3:**", "the 13 values of `LEAK_SOURCE_PHMSAGAS`",
                     "`tools/phleak/phleak.py` 0.1.0", "240-minute limit", "differ by at most 1"):
            self.assertIn(text, self.plan)

    def test_bars_match_code(self):
        for text in ('VERSION = "0.1.0"', "G2_MIN_ROWS = 10000", "G2_YEARS = (2015, 2024)",
                     "G2_MAX_FIRST_YEAR = 2003", "COMMODITY_YEAR = 2015",
                     "P1_MAX_NULL_SHARE = 0.01", "P3_MIN = 0.95", "P4_MIN = 0.99",
                     "P6_MIN_ROWS = 100", "P6_MAX_YEAR = 2003", "P6_MIN = 0.95", "TOL = 1.0",
                     'TABLE = "_core_phmsagas__yearly_distribution_leaks"', "Apache-2.0"):
            self.assertIn(text, self.code)
        self.assertIn('TOKEN = "Pre-registration id: phleak-1."', self.fetch)
        self.assertIn('FILES = ("phleak.py", "test_phleak.py")', self.fetch)


if __name__ == "__main__":
    unittest.main()
