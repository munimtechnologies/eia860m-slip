"""Checks that docs/phzero-plan.md is a complete pre-registration (id, what was seen, gates,
predictions with probabilities, what happens with the result, limits), that its bars match the
constants in tools/phzero/phzero.py, and runs the tool's own unit tests
(tools/phzero/test_phzero.py) on made-up rows. Reads no outside data.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "tools", "phzero"))

from test_phzero import (ConstantTests, HelperTests, StudyTests)  # noqa: E402,F401


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class PhzeroPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = read("docs/phzero-plan.md")
        cls.code = read("tools/phzero/phzero.py")
        cls.fetch = read("tools/phzero/fetch_plan_phzero.py")

    def test_structure(self):
        for text in ("Status: pre-registration, nothing run yet. Pre-registration id: phzero-1.",
                     "## What we have seen (before writing this)", "## Method",
                     "## Gate (if it fails, nothing is scored)",
                     "## Predictions (probability we give each)",
                     "## What happens with the result", "## Limits",
                     "made with AI agents working in MV2's name",
                     "no person has checked this plan by hand",
                     "A failed bar is reported as failed, with its cause, and is not re-scored.",
                     "pudl/issues/4646", "Not seen:", "2,152,092 bytes",
                     "core_phmsagas__yearly_distribution_operators.parquet",
                     "1980: 501, 1981: 486, 1982: 422, 1983: 707 (these sum to 2,131)"):
            self.assertIn(text, self.plan)

    def test_predictions(self):
        for text in ("**P1 (75%):** the table has between 1,500 and 2,800 zero rows.",
                     "**P2 (85%):** at least 99% of the zero rows are from report years 1976 to 1983",
                     "**P3 (85%):** at most 1% of the zero rows",
                     "**P4 (50%):** at least 5% of the zero rows",
                     "**P5 (45%):**", "at least 5 percentage points more",
                     "**P6 (80%):**", "at least 98% of the rows with a real id",
                     "**P7 (65%):** the same, at least 97%, on report years before 1990.",
                     "**P8 (60%):**", "at least 97% of the rows before 1990",
                     "**Gate G1:**", "**Gate G2:** at least 50,000 rows",
                     "no later than 1975, and report year 2024 present",
                     "**Gate G3:** at least 500 zero rows.",
                     "inc, incorporated, co, company, corp, corporation, llc, ltd, lp, the and of",
                     "`tools/phzero/phzero.py` 0.1.0", "240-minute limit", "up to 5,000"):
            self.assertIn(text, self.plan)

    def test_bars_match_code(self):
        for text in ('VERSION = "0.1.0"', "G2_MIN_ROWS = 50000", "G2_MAX_FIRST_YEAR = 1975",
                     "G2_LAST_YEAR = 2024", "G3_MIN_ZEROS = 500", "P1_RANGE = (1500, 2800)",
                     "P2_YEARS = (1976, 1983)", "P2_MIN = 0.99", "P3_MAX = 0.01",
                     "P4_MIN = 0.05", "P5_MIN_GAIN = 0.05", "P6_MIN = 0.98", "P7_MIN = 0.97",
                     "P8_MIN = 0.97", "EARLY = 1990", "MISS_CAP = 5000",
                     'TABLE = "core_phmsagas__yearly_distribution_operators"', "Apache-2.0"):
            self.assertIn(text, self.code)
        for word in ("inc", "incorporated", "co", "company", "corp", "corporation", "llc",
                     "ltd", "lp", "the", "of"):
            self.assertIn('"%s"' % word, self.code)
        self.assertIn('TOKEN = "Pre-registration id: phzero-1."', self.fetch)
        self.assertIn('FILES = ("phzero.py", "test_phzero.py")', self.fetch)


if __name__ == "__main__":
    unittest.main()
