"""Runs the unit tests of tools/coal-rows/coaloct.py (hand-built sheets, no network) and checks that its
gate and bars are the ones docs/coaloct-plan.md fixed.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "tools", "coal-rows"))

import coaloct as co  # noqa: E402
from test_coaloct import *  # noqa: E402,F401,F403


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class CodeMatchesPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = read("docs/coaloct-plan.md")
        cls.sep = json.loads(read("data/coalsep_2026-09.json"))

    def test_plan_still_unscored(self):
        self.assertIn("Status: pre-registered, not yet scored.", self.plan)
        self.assertIn("`coaloct-v1` will run `coaloct.py`, the code of `coalsep.py` 0.1.0", self.plan)
        self.assertIn("once EIA posts `october_generator2026.xlsx`", self.plan)
        self.assertEqual(co.OCT[0], "october_generator2026.xlsx")

    def test_gate_is_coalsep_v1(self):
        r = self.sep
        self.assertEqual((r["files"]["september"]["md5"], r["files"]["september"]["size"]), co.SEPT[1:])
        self.assertIn("still has 14,013,970 bytes and md5 %s" % co.SEPT[1], self.plan)
        self.assertEqual(r["predictions"]["S1"]["retired_2026"], [])
        got = {}
        for a in r["ahead"]:
            if a["first"] <= co.G2_WINDOW[1]:
                for u in a["units"].split(", "):
                    got["%s/%s" % (a["plant_id"], u)] = a["months"]
        self.assertEqual(got, co.G2_UNITS)
        self.assertEqual((r["predictions"]["S3"]["units"], r["predictions"]["S3"]["mw"]), (9, co.G2_MW))

    def test_bars(self):
        self.assertIn("| O2 | No coal unit on the Operating sheet is dated before %s. |" % co.O2_BEFORE, self.plan)
        self.assertIn("Sherburne County 1 (6090/1) and Comanche 2 (470/2) are both still dated 2026-12.", self.plan)
        self.assertEqual(co.O3_STILL_2026, {"6090/1": "2026-12", "470/2": "2026-12"})
        self.assertIn("the 16 coal generators (6,354.4 MW)", self.plan)
        self.assertEqual(len(co.PLAN), 16)
        self.assertIn("operating coal plant dated to retire from 2026-11 to 2027-12", self.plan)
        self.assertEqual(co.AHEAD, ("2026-11", "2027-12"))


if __name__ == "__main__":
    unittest.main()
