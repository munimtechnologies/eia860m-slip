"""Checks that docs/phdecade-plan.md is a complete pre-registration (id, what was seen, gates,
predictions with probabilities, what happens with the result, limits), that its bars and lists
match the constants in tools/phdecade/phdecade.py, and runs the tool's own unit tests
(tools/phdecade/test_phdecade.py) on made-up rows. Reads no outside data.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "tools", "phdecade"))

import phdecade  # noqa: E402
from test_phdecade import (ConstantTests, HelperTests, MatchTests, StudyTests)  # noqa: E402,F401


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class PhdecadePlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = read("docs/phdecade-plan.md")
        cls.code = read("tools/phdecade/phdecade.py")
        cls.fetch = read("tools/phdecade/fetch_plan_phdecade.py")

    def test_structure(self):
        for text in ("Status: pre-registration, nothing run yet. Pre-registration id: phdecade-1.",
                     "## What we have seen (before writing this)", "## Method",
                     "## Gate (if it fails, nothing is scored)",
                     "## Predictions (probability we give each)",
                     "## What happens with the result", "## Limits",
                     "made with AI agents working in MV2's name",
                     "no person has checked this plan by hand",
                     "A failed bar is reported as failed, with its cause, and is not re-scored.",
                     "pudl/issues/5505", "Not seen:", "1,034,817 bytes",
                     "core_phmsagas__yearly_distribution_by_install_decade.parquet",
                     "but we should verify this before dropping the data."):
            self.assertIn(text, self.plan)

    def test_predictions(self):
        for text in ("**P1 (75%):** at least 40% of pairs have an old mains change.",
                     "**P2 (85%):** the pairs with an old mains change hold at least 80%",
                     "**P3 (75%):**", "If no old bucket changes at all, there is nothing to test, "
                     "and P3 counts as failed.",
                     "**P4 (75%):**", "at least 25% of the absolute changes in the current bucket",
                     "If the current bucket never changes, P4 counts as failed.",
                     "**P5 (70%):** in at least 8 of the 10 year pairs",
                     "**P6 (65%):** at least 40% of pairs have an old services change.",
                     "**Gate G1:**", "**Gate G2:** at least 2,000 pairs, and at least 100 pairs "
                     "in at least 8 of the 10 year pairs.",
                     "`tools/phdecade/phdecade.py` 0.1.0", "240-minute limit", "the 300 largest",
                     "1 CPU, 1 GB", "report years 2015 to 2025", "more than 0.001 miles",
                     "more than 1 mile and more than 1% of the year-t value"):
            self.assertIn(text, self.plan)

    def test_lists_match_code(self):
        old4 = "pre_1940, 1940s, 1950s and 1960s"
        self.assertIn(old4, self.plan)
        self.assertEqual(tuple(old4.replace(" and ", ", ").split(", ")), phdecade.OLD4)
        fields = ("report_id, report_date, operator_id_phmsa, commodity, operating_state, "
                  "install_decade, mains_miles, services")
        self.assertIn("8 fields: " + fields, self.plan)
        self.assertEqual(tuple(fields.split(", ")), phdecade.NEED)
        self.assertEqual(phdecade.LAST_T1 - phdecade.FIRST_T, 10)

    def test_bars_match_code(self):
        for text in ('VERSION = "0.1.0"', "G2_MIN_PAIRS = 2000", "G2_MIN_PER_YEAR = 100",
                     "G2_MIN_YEARS = 8", "P1_MIN = 0.40", "P2_MIN = 0.80", "P4_MIN = 0.25",
                     "P5_MIN_YEARS = 8", "P6_MIN = 0.40", "MAINS_TOL = 0.001",
                     "SERVICES_TOL = 0.0", "MATERIAL_MILES = 1.0", "MATERIAL_SHARE = 0.01",
                     "TOP_CAP = 300", "FIRST_T = 2015", "LAST_T1 = 2025",
                     'TABLE = "core_phmsagas__yearly_distribution_by_install_decade"',
                     "Apache-2.0"):
            self.assertIn(text, self.code)
        self.assertIn('TOKEN = "Pre-registration id: phdecade-1."', self.fetch)
        self.assertIn('FILES = ("phdecade.py", "test_phdecade.py")', self.fetch)


if __name__ == "__main__":
    unittest.main()
