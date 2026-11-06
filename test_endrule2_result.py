"""Checks that docs/endrule2.md reports endrule-2 as its plan requires: both gates and the four
predictions scored with the plan's bars on job endrule2-v1's counts, and the descriptive
endwrap-check section marked as not pre-registered. Reads text only.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))

# Counts copied from job endrule2-v1's endrule2.json (6 November 2026): n, in E-1, in E, cancel.
BY_END = {"2026-02": (44, 44, 0, 32), "2026-03": (24, 24, 0, 15), "2026-04": (28, 28, 0, 22),
          "2026-05": (21, 21, 0, 9), "2026-06": (26, 26, 0, 15), "2026-07": (10, 10, 0, 8)}


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class Endrule2ResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/endrule2.md")
        cls.plan = read("docs/endrule2-plan.md")

    def test_scores_follow_the_plan_bars(self):
        n = sum(v[0] for v in BY_END.values())
        prev = sum(v[1] for v in BY_END.values())
        end = sum(v[2] for v in BY_END.values())
        cancel = sum(v[3] for v in BY_END.values())
        self.assertEqual((n, prev, end, cancel), (153, 153, 0, 101))
        self.assertTrue(n >= 100)                                         # G2 (size part)
        self.assertTrue(prev / n >= 0.95)                                 # Q1
        self.assertTrue(end / n <= 0.05)                                  # Q2
        self.assertTrue(all(v[1] / v[0] >= 0.90 and v[2] / v[0] <= 0.10
                            for v in BY_END.values()))                    # Q3
        self.assertTrue(cancel / n >= 0.60)                               # Q4
        self.assertEqual(round(100 * cancel / n, 1), 66.0)
        self.assertIn("Pre-registration id: endrule-2.", self.plan)
        self.assertIn("**Q4 (55%):** at least 60% of the fresh generators are on the \"Canceled "
                      "or Postponed\" sheet in month E.", self.plan)

    def test_headline_and_tables(self):
        self.assertIn("**Both gates held and 4 of 4 predictions held.**", self.doc)
        for text in ("| Q1 (85%): >= 95% of fresh generators listed in E-1 | held | 153 of 153 "
                     "(100%) |",
                     "| Q2 (85%): <= 5% listed in E | held | 0 of 153 (0%) |",
                     "| Q3 (70%): every group >= 90% in E-1 and <= 10% in E | held |",
                     "| Q4 (55%): >= 60% on \"Canceled or Postponed\" in E | held | 101 of 153 "
                     "(66.0%) |",
                     "| G2: nine workbooks read; fresh groups >= 100 | held | 9 of 9; 153 fresh "
                     "generators |",
                     "38,160 of the 38,162 generators"):
            self.assertIn(text, self.doc)
        for month, (n, prev, end, cancel) in BY_END.items():
            self.assertIn("| %s | %d | %d | %d | %d |" % (month, n, prev, end, cancel), self.doc)
        self.assertIn("| 2026-08 (seen in endrule-1, not scored) | 8 | 8 | 0 | 7 |", self.doc)
        self.assertIn("| 2026-09 (seen in endrule-1, not scored) | 4 | 4 | 0 | 2 |", self.doc)
        self.assertEqual(153 - 101, 52)
        self.assertIn("The 52 fresh generators", self.doc)

    def test_provenance(self):
        for text in ("md5 2be6ac001022cf230f87dc70dc740496",
                     "md5 c73d0b5653ddef583d4927a0ebcffb0e",
                     "md5 5090d7695d8065746557ca0b8df6fe2b",
                     "| 2026-01 | 6ef97d18d915c1937bd107dbe203976f |",
                     "| 2026-09 | 4c741eb77a5ccad5aca32ffe43f398af |",
                     "233,063 rows, 40,073 generators"):
            self.assertIn(text, self.doc)

    def test_endwrap_section_is_descriptive(self):
        self.assertIn("## The end-rule wrapper on the same build (descriptive, not "
                      "pre-registered)", self.doc)
        for text in ("37,186 end one month after it and 4 end on it",
                     "1,911 of 233,063 records",
                     "Lupinus Storage 3 (LUPE3), Payne Battlecreek Solar (GRS10) and Baxter Creek "
                     "Solar (PV1)",
                     "[September watchlist](watchlist-2026-09.md)",
                     "was not compared row by row with the published edition"):
            self.assertIn(text, self.doc)

    def test_links_and_disclosure(self):
        self.assertIn("[plan](endrule2-plan.md)", self.doc)
        self.assertIn("made with AI agents working in MV2's name", self.doc)
        self.assertIn("no person has checked these results by hand", self.doc)
        self.assertIn("PUDL's code (MIT) and data (CC BY 4.0) are downloaded at run time and "
                      "not stored here.", self.doc)


if __name__ == "__main__":
    unittest.main()
