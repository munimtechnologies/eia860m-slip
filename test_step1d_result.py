"""Checks that docs/step1d.md reports step1d-1 as its plan requires: the gate and the four
predictions scored with the plan's bars on job step1d-v1's counts, S4 reported as failed with
its cause, and the six far-apart step-1d pairs listed. Reads text only.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))

# Counts copied from job step1d-v1's step1d.json (6 November 2026).
A_N, A_R15, A_R3 = 5108, 24, 1
D_N, D_R15, D_R3 = 113, 6, 6
D_R3_OUTSIDE_ELK = 3
CLASH_N, CLASH_R15 = 40, 6
MANUAL_N, MANUAL_R15 = 59, 6


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class Step1dResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/step1d.md")
        cls.plan = read("docs/step1d-plan.md")

    def test_scores_follow_the_plan_bars(self):
        a, d = A_R15 / A_N, D_R15 / D_N
        self.assertTrue(A_N >= 1000 and D_N >= 10)            # G1
        self.assertTrue(d > 0 and d >= 2 * a)                 # S1
        self.assertTrue(D_R3_OUTSIDE_ELK >= 3)                # S2
        self.assertTrue(a < 0.10)                             # S3
        self.assertFalse(CLASH_N >= 5 and CLASH_R15 / CLASH_N >= 0.30)  # S4
        self.assertEqual(round(d, 4), 0.0531)
        self.assertEqual(round(a, 4), 0.0047)
        self.assertEqual(round(MANUAL_R15 / MANUAL_N, 4), 0.1017)
        self.assertIn("Pre-registration id: step1d-1.", self.plan)
        self.assertIn("**S4 (55%):** at least 5 step-1d pairs have a prefix clash, and at least "
                      "30% of them are far apart.", self.plan)

    def test_headline_and_table(self):
        self.assertIn("**Gate G1 held, and 3 of 4 predictions held (S1, S2, S3); S4 failed.**",
                      self.doc)
        for text in ("| G1: columns, >= 1,000 step-1a pairs, >= 10 step-1d pairs | held |",
                     "| S1 (65%): step-1d far-apart share > 0 and >= 2x the step-1a share | held |",
                     "| S2 (50%): >= 3 step-1d pairs outside plant 57865 at r >= 3 | held | 3 "
                     "(exactly at the bar) |",
                     "| S3 (70%): < 10% of step-1a pairs far apart | held | 0.47% |",
                     "| S4 (55%): >= 5 step-1d prefix-clash pairs, >= 30% of them far apart | "
                     "failed | 40 clash pairs, 6 far apart (15%) |",
                     "| 1a exact ids | 5,108 | 24 | 1 | 0.47% |",
                     "| 1d leading letters removed | 113 | 6 | 6 | 5.31% |",
                     "| Manual Match | 59 | 6 | 0 | 10.17% |",
                     "**Why S4 failed.**",
                     "34 of the 40 such pairs differ by less than 1.5 times"):
            self.assertIn(text, self.doc)
        self.assertEqual(CLASH_N - CLASH_R15, 34)
        self.assertEqual(round(CLASH_R15 / CLASH_N, 2), 0.15)

    def test_pairs_and_provenance(self):
        for text in ("| 1571 Chalk Point, MD | SMECO / SGT1 | 93 | 1571 Chalk Point LLC / GT1 | 16 "
                     "| GT | 5.812 |",
                     "| 422 Glenarm, CA | GT5 / STG5 | 16.78 | 422 Glenarm / GT5 | 71 | CT | 4.231 |",
                     "| 58478 LEPA Unit No. 1, LA | CC01 / STG1 | 17 | 58478 LEPA Unit No. 1 / LEPA1 "
                     "| 57 | CT | 3.353 |",
                     "md5 b7ec4b014ab66c2926f77ea86fa1ea16, 6,935 rows",
                     "md5 494a198670cbf7f6449327838be9b1c4",
                     "3c7d6724cddee38dfb6a06debca732c33a227ed6"):
            self.assertIn(text, self.doc)
        self.assertEqual(self.doc.count("| 57865 Antelope Elk Energy Center, TX |"), 3)
        self.assertEqual(round(93 / 16, 3), 5.812)
        self.assertEqual(round(71 / 16.78, 3), 4.231)
        self.assertEqual(round(57 / 17, 3), 3.353)
        self.assertEqual(round(202 / 9.3, 2), 21.72)

    def test_honest_framing(self):
        self.assertIn("[plan](step1d-plan.md)", self.doc)
        self.assertIn("made with AI agents working in MV2's name", self.doc)
        self.assertIn("no person has checked these results by hand", self.doc)
        self.assertIn("it is not by itself proof that the link is wrong", self.doc)
        self.assertIn("## What the rows show (descriptive, not pre-registered)", self.doc)
        self.assertIn("EPA's file is downloaded at run time and not stored here.", self.doc)


if __name__ == "__main__":
    unittest.main()
