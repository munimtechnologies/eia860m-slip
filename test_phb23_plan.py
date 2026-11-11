"""Checks that docs/phb23-plan.md is a complete pre-registration (id, what was seen, gates,
predictions with probabilities, what happens with the result, limits), that its bars match the
constants in tools/phb23/phb23.py, and runs the tool's own unit tests (tools/phb23/test_phb23.py)
on made-up rows. Reads no outside data.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "tools", "phb23"))

import phb23  # noqa: E402
from test_phb23 import (AggTests, CompareTests, ConstantTests, HelperTests,  # noqa: E402,F401
                        PolarsReadTests, ScoreTests)


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class Phb23PlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = read("docs/phb23-plan.md")
        cls.code = read("tools/phb23/phb23.py")
        cls.fetch = read("tools/phb23/fetch_plan_phb23.py")

    def test_structure(self):
        for text in ("Status: pre-registration, nothing run yet. Pre-registration id: phb23-1.",
                     "## What we have seen (before writing this)", "## Method",
                     "## Gate (if it fails, nothing is scored)",
                     "## Predictions (probability we give each)",
                     "## What happens with the result", "## Limits",
                     "made with AI agents working in MV2's name",
                     "no person has checked this plan by hand",
                     "No person has checked these quotes against the PDFs.",
                     "No person has checked this alignment.",
                     "A failed bar is reported as failed, with its cause, and is not re-scored.",
                     "pudl/issues/4646", "Not seen:", "6,532,003 bytes", "2,250,542 bytes",
                     "1,034,817 bytes", "spend time validating the numeric data",
                     "`mmiles_part_b2_total`", "`num_srvs_part_b3_total`",
                     "`mmiles_plastic_total`", "(phrecon-plan.md)", "(phsize-plan.md)"):
            self.assertIn(text, self.plan)
        self.assertNotIn("MIT", self.plan)

    def test_predictions(self):
        for text in ("**P1 (65%):** at least 97% pass PHMSA's rule for mains, grand total "
                     "against the Section 4 sum.",
                     "**P2 (75%):** at least 97% pass for mains, grand total against the "
                     "Section 1 total.",
                     "**P3 (80%):** at least 97% pass for mains, cell sum against the grand "
                     "total.",
                     "**P4 (60%):** at least 95% pass for services, grand total against the "
                     "Section 4 sum.",
                     "**P5 (65%):** in at least 90% of discriminating reports for mains",
                     "If fewer than 100 reports are discriminating, there is nothing to test, "
                     "and P5 counts as failed.",
                     "**P6 (65%):** in at most 10% of discriminating reports for mains",
                     "and P6 counts as failed.",
                     "**P7 (70%):** at least 95% pass for mains, the Section 2 steel total",
                     "**P8 (55%):**", "at least 60% pass grand total against the Section 1 total",
                     "If fewer than 10 such reports fail, there is nothing to test, and P8 "
                     "counts as failed.",
                     "**Gate G1:**", "**Gate G2:** at least 5,000 reports in 2017 to 2025",
                     "at least 300 in each of at least 7 of those 9 years.",
                     "`tools/phb23/phb23.py` 0.1.0", "slices of 1,000,000 rows",
                     "240-minute limit", "up to 3,000 rows", "1 CPU, 2 GB",
                     "within 0.5% of it", "within 0.3 miles (mains) or exactly equal (services)",
                     "Floating-point slack of 0.000001"):
            self.assertIn(text, self.plan)

    def test_bars_match_code(self):
        for text in ('VERSION = "0.1.0"', "G2_MIN_LATE = 5000", "G2_MIN_PER_YEAR = 300",
                     "G2_MIN_YEARS = 7", "P1_MIN = 0.97", "P2_MIN = 0.97", "P3_MIN = 0.97",
                     "P4_MIN = 0.95", "P5_MIN = 0.90", "P5_MIN_N = 100", "P6_MAX = 0.10",
                     "P7_MIN = 0.95", "P8_MIN = 0.60", "P8_MIN_FAILS = 10", "FAIL_CAP = 3000",
                     "PLASTIC_CAP = 3000", "SLICE_ROWS = 1000000", "BIG = 60.0",
                     "SHARE_TOL = 0.005", "SMALL_MAINS_TOL = 0.3", "EPS = 1e-6",
                     "LATE_FIRST = 2017", "LATE_LAST = 2025", "Apache-2.0"):
            self.assertIn(text, self.code)
        self.assertEqual(phb23.LATE_LAST - phb23.LATE_FIRST + 1, 9)
        for table in (phb23.B1_TABLE, phb23.B2_TABLE, phb23.B4_TABLE):
            self.assertIn("`" + table + "`", self.plan)
        self.assertEqual(phb23.STEEL[-1], "steel")
        self.assertEqual(phb23.PLASTIC, ("pvc", "pe", "abs", "other_plastic", "plastic"))
        self.assertEqual(phb23.OTHER, ("other", "other_alt", "other_material"))
        for text in ("steel = the four steel kinds and `steel`",
                     "plastic = `pvc`, `pe`, `abs`, `other_plastic` and `plastic`",
                     "other = `other`, `other_alt` and `other_material`"):
            self.assertIn(text, self.plan)
        self.assertIn('TOKEN = "Pre-registration id: phb23-1."', self.fetch)
        self.assertIn('FILES = ("phb23.py", "test_phb23.py")', self.fetch)


if __name__ == "__main__":
    unittest.main()
