"""Checks that docs/step1d-plan.md states what was seen before the bars were set and names its
gate and bars, and that tools/step1d/step1d.py (standard library only) scores the same
thresholds on the plan's own boundary values.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class Step1dPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/step1d-plan.md")
        cls.code = read("tools/step1d/step1d.py")

    def test_status_and_seen(self):
        self.assertIn("Status: pre-registration, nothing run yet. Pre-registration id: "
                      "step1d-1.", self.doc)
        self.assertIn("## What we have seen (before writing this)", self.doc)
        self.assertIn("No other row of the file has been read, and no count over it has "
                      "been made.", self.doc)
        self.assertIn("29 of 3,030 groups", self.doc)
        self.assertIn('TOKEN = "Pre-registration id: step1d-1."',
                      read("tools/step1d/fetch_plan_code.py"))

    def test_bars(self):
        for text in ("**Gate G1:**", "**S1 (65%):**", "**S2 (50%):**", "**S3 (70%):**",
                     "**S4 (55%):**",
                     "at least 1,000 step-1a pairs and at least 10 step-1d pairs",
                     "above zero and at least twice the share among step-1a pairs",
                     "at least 3 step-1d pairs outside CAMD plant 57865",
                     "fewer than 10% of step-1a pairs are far apart",
                     "at least 5 step-1d pairs have a prefix clash, and at least 30% of them",
                     "3c7d6724cddee38dfb6a06debca732c33a227ed6"):
            self.assertIn(text, self.doc)
        for text in ('VERSION = "0.1.0"', "MIN_1A = 1000", "MIN_1D = 10", 'ELK_PLANT = "57865"',
                     'COMMIT = "3c7d6724cddee38dfb6a06debca732c33a227ed6"',
                     's["S1"] = d > 0 and d >= 2 * a',
                     's["S2"] = m["d_r3_outside_elk"] >= 3',
                     's["S3"] = a < 0.10',
                     's["S4"] = c["n"] >= 5 and c["share_r15"] >= 0.30'):
            self.assertIn(text, self.code)
        self.assertIn("`tools/step1d/step1d.py` 0.1.0", self.doc)

    def test_scoring_on_the_bars(self):
        sys.path.insert(0, os.path.join(HERE, "tools", "step1d"))
        try:
            import step1d as sd
        finally:
            sys.path.pop(0)
        m = {"columns_ok": True,
             "steps": {"1a": {"n": 1000, "share_r15": 0.05}, "1d": {"n": 10, "share_r15": 0.1}},
             "d_r3_outside_elk": 3, "d_clash": {"n": 5, "share_r15": 0.3}}
        self.assertEqual(sd.score(m), {"G1": True, "S1": True, "S2": True, "S3": True,
                                       "S4": True})
        m["steps"]["1d"]["n"] = 9
        self.assertEqual(sd.score(m), {"G1": False})
        self.assertEqual(sd.step_of("3_1_Generator (generators) match on plant and gen IDs  "
                                    "Step 1d: Modify IDs; remove leading letters"), "1d")

    def test_disclosure(self):
        self.assertIn("made with AI agents working in MV2's name", self.doc)
        self.assertIn("EPA's file is downloaded at run time and not stored here.", self.doc)
        self.assertIn("Apache-2.0", self.code)
        self.assertNotIn("MIT License", self.code)


if __name__ == "__main__":
    unittest.main()
