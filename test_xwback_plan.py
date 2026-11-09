"""Checks that docs/xwback-plan.md is a complete pre-registration (id, what was seen, gates,
predictions with probabilities, what happens with the result, limits), that its bars match the
constants in tools/xwback/xwback.py, that the 14 plants and 57 units it says were seen are those
of data/xwstale-units-2018-2024.csv, and runs the tool's own unit tests
(tools/xwback/test_xwback.py) on made-up rows. Reads no outside data.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import csv
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "tools", "xwback"))

from test_xwback import (AggregateTests, AstoriaTests, ConstantTests,  # noqa: E402,F401
                         HelperTests, ScoreTests)

XWSTALE_CSV = os.path.join(HERE, "data", "xwstale-units-2018-2024.csv")
SEEN = (356, 563, 856, 887, 1642, 2401, 2836, 2866, 6019, 8226, 10099, 50385, 52056, 55243)


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class XwbackPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = read("docs/xwback-plan.md")
        cls.code = read("tools/xwback/xwback.py")
        cls.fetch = read("tools/xwback/fetch_plan_code.py")

    def test_structure(self):
        for text in ("Status: pre-registration, nothing run yet. Pre-registration id: xwback-1.",
                     "## What we have seen (before writing this)", "## Method",
                     "## Gate (if it fails, nothing is scored)",
                     "## Predictions (probability we give each)",
                     "## What happens with the result", "## Limits",
                     "made with AI agents working in MV2's name",
                     "no person has checked this plan by hand",
                     "A failed bar is reported as failed, with its cause, and is not re-scored.",
                     "pudl/issues/3684", "pudl/issues/3676", "pudl/issues/5752",
                     "The retired tab only includes those retired generators which were reported "
                     "in the most current data cycle.",
                     "Not seen: which later year each plant returns in"):
            self.assertIn(text, self.plan)

    def test_predictions(self):
        for text in ("**P1 (70%):** at least 13 of the 14 plants are listed in 2026, and every "
                     "one of their 2026 rows has `data_maturity` monthly_update.",
                     "**P2 (80%):** of all generator rows of the 14 plants in 2025 and 2026, at "
                     "least 95% have `operational_status_code` RE.",
                     "**P3 (55%):** at most 10% of population C persist",
                     "**P4 (60%):** at least 80% of population C are listed in 2026.",
                     "**P5 (55%):** at most 10% of population C are listed in 2025.",
                     "**Gate G1:** the table has every column used and report years 2018 to 2026.",
                     "**Gate G2:** population A has 14 plants and 57 units",
                     "**Gate G3:** every one of the 14 plants is listed in some year after 2024",
                     "falls in 2002 to 2021",
                     "from three years after that first year up to 2024",
                     "prime mover CA, CS, CT, GT, IC or ST",
                     "`tools/xwback/xwback.py` 0.1.0"):
            self.assertIn(text, self.plan)

    def test_bars_match_code(self):
        for text in ('VERSION = "0.1.0"', "NEWEST_ANNUAL = 2024",
                     "G1_YEARS = tuple(range(2018, 2027))", "POP_PLANTS = 14", "POP_UNITS = 57",
                     "P1_MIN_PLANTS = 13", 'P1_MATURITY = "monthly_update"', "P2_SHARE = 0.95",
                     "C_FIRST = 2002", "C_LAST = 2021", "P3_GAP = 3", "P3_MAX_SHARE = 0.10",
                     "P4_SHARE = 0.80", "P5_MAX_SHARE = 0.10", 'RETIRED = "RE"',
                     'COMB = ("CA", "CS", "CT", "GT", "IC", "ST")', "ASTORIA_YEAR = 2023"):
            self.assertIn(text, self.code)
        self.assertIn('TOKEN = "Pre-registration id: xwback-1."', self.fetch)

    def test_seen_plants_in_plan(self):
        text = ", ".join(str(p) for p in SEEN[:-1]) + " and " + str(SEEN[-1])
        self.assertIn(text, self.plan)

    @unittest.skipUnless(os.path.exists(XWSTALE_CSV), "data file not in this checkout")
    def test_seen_matches_xwstale_data(self):
        with open(XWSTALE_CSV, encoding="utf-8", newline="") as fh:
            rows = [r for r in csv.DictReader(fh)
                    if r["report_year"] == "2024" and r["listed_later"] == "True"]
        self.assertEqual(len(rows), 57)
        self.assertEqual(tuple(sorted({int(r["plant_id_eia"]) for r in rows})), SEEN)
        self.assertEqual(sorted({r["last_listed_year"] for r in rows}), ["2022", "2023", "2024"])


if __name__ == "__main__":
    unittest.main()
