"""Checks that docs/xwpair-plan.md is a complete pre-registration (id, what was seen, gates,
predictions with probabilities, what happens with the result, limits), that its bars match the
constants in tools/xwpair/xwpair.py, and runs the tool's own unit tests (tools/xwpair/
test_xwpair.py) on made-up rows. Reads no outside data.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "tools", "xwpair"))

from test_xwpair import CensusTests, IdTests, IndexTests, ScoreTests  # noqa: E402,F401


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class XwpairPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = read("docs/xwpair-plan.md")
        cls.code = read("tools/xwpair/xwpair.py")
        cls.fetch = read("tools/xwpair/fetch_plan_code.py")

    def test_structure(self):
        for text in ("Status: pre-registration, nothing run yet. Pre-registration id: xwpair-1.",
                     "## What we have seen (before writing this)", "## Method",
                     "## Gate (if it fails, nothing is scored)",
                     "## Predictions (probability we give each)",
                     "## What happens with the result", "## Limits",
                     "made with AI agents working in MV2's name",
                     "no person has checked this plan by hand",
                     "No count of CEMS units without a crosswalk row in PUDL's tables, of their "
                     "candidate generators, or of unique pairs has been made by us or reported "
                     "to us.",
                     "A failed bar is reported as failed, with its cause, and is not re-scored.",
                     "open-grid-emissions/pull/476", "from 488 to 349"):
            self.assertIn(text, self.plan)

    def test_predictions(self):
        for text in ("**P1 (60%):** unmatched units are between 2% and 10%",
                     "**P2 (65%):** at least 30% of unmatched units have at least one candidate",
                     "**P3 (55%):** there are at least 25 unique pairs.",
                     "**P4 (70%):** of OGE's CAMPD units that are CEMS units that year, at least "
                     "80% are unmatched",
                     "Scored only if there are at least 20 such units.",
                     "**P5 (55%):** of those unmatched OGE units, in at least 60%",
                     "Scored only if there are at least 10 such units.",
                     "**P6 (60%):** of our unique pairs at OGE's units, at least 75%",
                     "Scored only if there are at least 5 such pairs.",
                     "**P7 (50%):** at least 10 unique pairs",
                     "the newest report year in both is 2023 or later",
                     "that year has at least 2,000 CEMS units",
                     "at least 150 rows with the CAMPD note",
                     "between 0.5 and 1.5", "prime mover CA, CS, CT, GT, IC or ST",
                     "e6d1e3f487f338829108b348919eb9a37aa82616",
                     "`tools/xwpair/xwpair.py` 0.1.0"):
            self.assertIn(text, self.plan)

    def test_bars_match_code(self):
        for text in ('VERSION = "0.1.0"', "MIN_NEWEST = 2023", "MIN_UNITS = 2000",
                     "MIN_OGE_ROWS = 150", "P1_LO = 0.02", "P1_HI = 0.10", "P2_SHARE = 0.3",
                     "P3_MIN = 25", "P4_MIN_N = 20", "P4_SHARE = 0.8", "P5_MIN_N = 10",
                     "P5_SHARE = 0.6", "P6_MIN_N = 5", "P6_SHARE = 0.75", "P7_MIN = 10",
                     "LO = 0.5", "HI = 1.5", 'COMB = ("CA", "CS", "CT", "GT", "IC", "ST")',
                     'OGE_SHA = "e6d1e3f487f338829108b348919eb9a37aa82616"',
                     'OGE_NOTE = "CAMPD Facility database mapping"'):
            self.assertIn(text, self.code)
        self.assertIn('TOKEN = "Pre-registration id: xwpair-1."', self.fetch)


if __name__ == "__main__":
    unittest.main()
