"""Checks that docs/xwstale-plan.md is a complete pre-registration (id, what was seen, gates,
predictions with probabilities, what happens with the result, limits), that its bars match the
constants in tools/xwstale/xwstale.py, that the yearly counts it says were seen are the absent
and not_operating counts of data/xwgap-units-2018-2024.csv, and runs the tool's own unit tests
(tools/xwstale/test_xwstale.py) on made-up rows. Reads no outside data.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import collections
import csv
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "tools", "xwstale"))

from test_xwstale import (ClassifyTests, ConstantTests, HelperTests,  # noqa: E402,F401
                          ScoreTests, SummaryTests)

XWGAP_CSV = os.path.join(HERE, "data", "xwgap-units-2018-2024.csv")
SEEN = {"2018": 18, "2019": 27, "2020": 28, "2021": 28, "2022": 23, "2023": 39, "2024": 65}


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class XwstalePlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = read("docs/xwstale-plan.md")
        cls.code = read("tools/xwstale/xwstale.py")
        cls.fetch = read("tools/xwstale/fetch_plan_code.py")

    def test_structure(self):
        for text in ("Status: pre-registration, nothing run yet. Pre-registration id: xwstale-1.",
                     "## What we have seen (before writing this)", "## Method",
                     "## Gate (if it fails, nothing is scored)",
                     "## Predictions (probability we give each)",
                     "## What happens with the result", "## Limits",
                     "made with AI agents working in MV2's name",
                     "no person has checked this plan by hand",
                     "no EIA-860 listing year or retirement date for any plant",
                     "A failed bar is reported as failed, with its cause, and is not re-scored.",
                     "camd-eia-crosswalk/issues/44", "pudl/issues/5752",
                     "methodology/operational_characteristics.html"):
            self.assertIn(text, self.plan)

    def test_predictions(self):
        for text in ("**P1 (60%):** at least 60% of the 65 units are retired_before.",
                     "**P2 (55%):** at least 90% of the retired_before units had their latest "
                     "retirement in 2022 or 2023",
                     "**P3 (60%):** at most 10 of the 65 units are never_listed.",
                     "**P4 (40%):** all 35 absent units at plants 563, 2866 and 55243 are "
                     "retired_before, with their latest retirement in 2023.",
                     "**P5 (40%):** in each report year from 2019 to 2023, at least half",
                     "**Gate G2:** the population file has 317 rows, 65 of them",
                     "(EIA 6019, unit 1, 2024) is classed retired_before with its latest "
                     "retirement in 2022",
                     "report years 2018 to 2024",
                     "prime mover CA, CS, CT, GT, IC or ST",
                     "`tools/xwstale/xwstale.py` 0.1.0"):
            self.assertIn(text, self.plan)

    def test_bars_match_code(self):
        for text in ('VERSION = "0.1.0"', "NEWEST = 2024", "POP_ROWS = 317", "POP_NEWEST = 65",
                     'ZIMMER = (2024, 6019, "1")', "ZIMMER_YEAR = 2022", "P1_SHARE = 0.6",
                     "P2_SHARE = 0.9", "P3_MAX = 10", "P4_PLANTS = (563, 2866, 55243)",
                     "P4_UNITS = 35", "P4_YEAR = 2023",
                     "P5_YEARS = (2019, 2020, 2021, 2022, 2023)", "P5_SHARE = 0.5",
                     'COMB = ("CA", "CS", "CT", "GT", "IC", "ST")',
                     "y in range(2018, NEWEST + 1)",
                     "c[\"retired_before_in_window\"] = sum(1 for u in rb if u[\"retired_year\"] "
                     ">= u[\"year\"] - 2)"):
            self.assertIn(text, self.code)
        self.assertIn('TOKEN = "Pre-registration id: xwstale-1."', self.fetch)

    def test_seen_counts_in_plan(self):
        text = ", ".join("%d (%s)" % (n, y) for y, n in sorted(SEEN.items()))
        self.assertIn(text, self.plan)
        self.assertEqual(SEEN["2024"], 65)

    @unittest.skipUnless(os.path.exists(XWGAP_CSV), "data file not in this checkout")
    def test_seen_counts_match_xwgap_data(self):
        with open(XWGAP_CSV, encoding="utf-8", newline="") as fh:
            rows = list(csv.DictReader(fh))
        self.assertEqual(len(rows), 317)
        got = collections.Counter(r["report_year"] for r in rows
                                  if r["reason"] in ("absent", "not_operating"))
        self.assertEqual(dict(got), SEEN)
        p4 = [r for r in rows if r["report_year"] == "2024" and r["reason"] == "absent"
              and r["plant_id_eia"] in ("563", "2866", "55243")]
        self.assertEqual(len(p4), 35)
        zimmer = [r for r in rows if r["report_year"] == "2024" and r["plant_id_eia"] == "6019"]
        self.assertEqual([(r["emissions_unit_id_epa"], r["reason"]) for r in zimmer],
                         [("1", "absent")])
        frontera = sorted(r["report_year"] for r in rows if r["plant_id_eia"] == "55098"
                          and r["reason"] == "absent")
        self.assertEqual(sorted(set(frontera)), ["2018", "2019", "2020", "2021", "2022"])


if __name__ == "__main__":
    unittest.main()
