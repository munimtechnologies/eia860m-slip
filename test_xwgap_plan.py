"""Checks that docs/xwgap-plan.md is a complete pre-registration (id, what was seen, gates,
predictions with probabilities, what happens with the result, limits), that its bars match the
constants in tools/xwgap/xwgap.py, that the yearly counts it says were seen are the no_candidate
counts of data/xwpair-units-2018-2024.csv, and runs the tool's own unit tests
(tools/xwgap/test_xwgap.py) on made-up rows. Reads no outside data.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import collections
import csv
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "tools", "xwgap"))

from test_xwgap import (ConstantTests, GapTests, IdTests, IndexTests,  # noqa: E402,F401
                        OgeTests, ScoreTests)

XWPAIR_CSV = os.path.join(HERE, "data", "xwpair-units-2018-2024.csv")
SEEN = {"2018": 24, "2019": 34, "2020": 41, "2021": 46, "2022": 44, "2023": 53, "2024": 75}


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class XwgapPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = read("docs/xwgap-plan.md")
        cls.code = read("tools/xwgap/xwgap.py")
        cls.fetch = read("tools/xwgap/fetch_plan_code.py")

    def test_structure(self):
        for text in ("Status: pre-registration, nothing run yet. Pre-registration id: xwgap-1.",
                     "## What we have seen (before writing this)", "## Method",
                     "## Gate (if it fails, nothing is scored)",
                     "## Predictions (probability we give each)",
                     "## What happens with the result", "## Limits",
                     "made with AI agents working in MV2's name",
                     "no person has checked this plan by hand",
                     "no count of their reasons has been made by us or reported to us",
                     "A failed bar is reported as failed, with its cause, and is not re-scored.",
                     "camd-eia-crosswalk/issues/44", "pudl/pull/5543",
                     "open-grid-emissions/pull/476",
                     "`e6d1e3f487f338829108b348919eb9a37aa82616`"):
            self.assertIn(text, self.plan)

    def test_predictions(self):
        for text in ("**P1 (45%):** all_linked is the most common reason",
                     "**P2 (40%):** at least 20% of gap units are absent.",
                     "**P3 (50%):** at least half of the all_linked gap units have a fit. "
                     "Scored only if there are at least 10 all_linked gap units.",
                     "**P4 (35%):** at least 10 gap units have a same-id generator",
                     "**P5 (35%):** OGE's manual table has a row for at least 25% of gap units.",
                     "**P6 (70%):** at least 70% of gap units were also unmatched the year "
                     "before.",
                     "**Gate G2:** the newest year has at least 40 gap units.",
                     "has at least 150 rows with a plant and unit id",
                     "at least 2,000 CEMS units", "0.5 to 1.5 times its peak",
                     "`tools/xwgap/xwgap.py` 0.1.0"):
            self.assertIn(text, self.plan)

    def test_bars_match_code(self):
        for text in ('VERSION = "0.1.0"', "MIN_NEWEST = 2023", "MIN_UNITS = 2000",
                     "MIN_GAP = 40", "MIN_OGE_ROWS = 150", "P2_SHARE = 0.2", "P3_MIN_N = 10",
                     "P3_SHARE = 0.5", "P4_MIN = 10", "P5_SHARE = 0.25", "P6_SHARE = 0.7",
                     "LO = 0.5", "HI = 1.5", 'COMB = ("CA", "CS", "CT", "GT", "IC", "ST")',
                     'OGE_SHA = "e6d1e3f487f338829108b348919eb9a37aa82616"'):
            self.assertIn(text, self.code)
        self.assertIn('TOKEN = "Pre-registration id: xwgap-1."', self.fetch)

    def test_seen_counts_in_plan(self):
        text = ", ".join("%d (%s)" % (n, y) for y, n in sorted(SEEN.items()))
        self.assertIn(text, self.plan)
        self.assertIn("273 of 4,215 CEMS units had no row", self.plan)
        self.assertIn("186 had no CEMS peak load, 12 had", self.plan)
        self.assertEqual(273 - 186 - 12, SEEN["2024"])

    @unittest.skipUnless(os.path.exists(XWPAIR_CSV), "data file not in this checkout")
    def test_seen_counts_match_xwpair_data(self):
        with open(XWPAIR_CSV, encoding="utf-8", newline="") as fh:
            rows = list(csv.DictReader(fh))
        got = collections.Counter(r["report_year"] for r in rows if r["class"] == "no_candidate")
        self.assertEqual(dict(got), SEEN)
        y24 = collections.Counter(r["class"] for r in rows if r["report_year"] == "2024")
        self.assertEqual(sum(y24.values()), 273)
        self.assertEqual(y24["no_load"], 186)


if __name__ == "__main__":
    unittest.main()
