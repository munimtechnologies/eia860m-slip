"""Checks that docs/ccsub-plan.md is a complete pre-registration (id, what was seen, gate,
predictions with probabilities, what happens with the result, limits), that its bars match the
constants in tools/ccsub/ccsub.py, that the 10 steam generators fixed in the code are the 2024
rows of data/ccsplit-orphans-2018-2024.csv, and runs the tool's own unit tests
(tools/ccsub/test_ccsub.py) on made-up rows. Reads no outside data.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import csv
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "tools", "ccsub"))

import ccsub  # noqa: E402
from test_ccsub import (BaseTests, ClassifyTests, ConstantTests, IdTests,  # noqa: E402,F401
                        IndexTests, ScoreTests)

ORPHANS_CSV = os.path.join(HERE, "data", "ccsplit-orphans-2018-2024.csv")


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class CcsubPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = read("docs/ccsub-plan.md")
        cls.code = read("tools/ccsub/ccsub.py")
        cls.fetch = read("tools/ccsub/fetch_plan_code.py")

    def test_structure(self):
        for text in ("Status: pre-registration, nothing run yet. Pre-registration id: ccsub-1.",
                     "## What we have seen (before writing this)", "## Method",
                     "## Gate (if it fails, nothing is scored)",
                     "## Predictions (probability we give each)",
                     "## What happens with the result", "## Limits",
                     "made with AI agents working in MV2's name",
                     "no person has checked this plan by hand",
                     "no count of subplant membership for these generators has been made by us "
                     "or reported to us",
                     "A failed bar is reported as failed, with its cause, and is not re-scored.",
                     "pudl/pull/5543", "open-grid-emissions/pull/476",
                     "So for Open Grid Emissions this check is a close proxy, not the same "
                     "table."):
            self.assertIn(text, self.plan)

    def test_predictions(self):
        for text in ("**P1 (85%):** all 10 steam generators have a row",
                     "**P2 (55%):** at least 7 of the 10 are joined.",
                     "**P3 (65%):** at least 2 of the 3 at hit plants",
                     "**P4 (60%):** every joined steam generator shares a unit",
                     "Scored only if at least 3 are joined.",
                     "**P5 (80%):** at least 95% of the linked operating CA generators",
                     "Scored only if there are at least 200 of them.",
                     "at least 20,000 rows",
                     "`tools/ccsub/ccsub.py` 0.1.0"):
            self.assertIn(text, self.plan)

    def test_bars_match_code(self):
        for text in ('VERSION = "0.1.0"', "MIN_ROWS = 20000", "P2_MIN = 7", "P3_MIN = 2",
                     "P4_MIN_N = 3", "P5_MIN_N = 200", "P5_SHARE = 0.95",
                     "HIT_PLANTS = (422, 58478, 60589)",
                     'SUB_TABLE = "core_epa__assn_eia_epacamd_subplant_ids"'):
            self.assertIn(text, self.code)
        self.assertIn('TOKEN = "Pre-registration id: ccsub-1."', self.fetch)

    def test_plan_lists_the_ten(self):
        for pi, (_cts, cas) in ccsub.ORPHANS.items():
            for ca in cas:
                self.assertIn("%s %s" % (pi, ca) if pi != 55419 else "55419 ST6 and ST7",
                              self.plan)

    @unittest.skipUnless(os.path.exists(ORPHANS_CSV), "data file not in this checkout")
    def test_orphans_match_ccsplit_data(self):
        with open(ORPHANS_CSV, encoding="utf-8", newline="") as fh:
            rows = [r for r in csv.DictReader(fh) if r["report_year"] == "2024"]
        want = {int(r["plant_id_eia"]): (tuple(r["linked_ct_generators"].split(";")),
                                         tuple(r["orphan_ca_generators"].split(";")))
                for r in rows}
        self.assertEqual(want, ccsub.ORPHANS)
        hits = sorted(int(r["plant_id_eia"]) for r in rows if r["hit"] == "True")
        self.assertEqual(tuple(hits), ccsub.HIT_PLANTS)


if __name__ == "__main__":
    unittest.main()
