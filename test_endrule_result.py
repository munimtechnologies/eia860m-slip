"""Checks that docs/endrule.md reports endrule-1 as its plan requires: G2 failed, so nothing is
scored, and the descriptive counts match job endrule-v1's output. Reads text only.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class EndruleResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/endrule.md")
        cls.plan = read("docs/endrule-plan.md")

    def test_gate_failed_and_nothing_scored(self):
        self.assertIn("**Gate G1 held, gate G2 failed, so nothing was scored.**", self.doc)
        self.assertIn("A8 and A7 each hold at least 10 generators", self.plan)
        self.assertIn("A8 = 4 and A7 = 8 (the bar was at least 10 each)", self.doc)
        self.assertIn("P1 to P5 are not scored and will not be re-scored.", self.doc)
        self.assertIn("(descriptive, not scored)", self.doc)
        self.assertIn("they do not count as held predictions", self.doc)
        for word in ("| P1 (85%) | held", "| P2 (85%) | held", "| P4 (90%) | held"):
            self.assertNotIn(word, self.doc)

    def test_counts_from_the_job(self):
        for text in ("| A8 listed in August 2026 | 4 of 4 |",
                     "| A8 listed in September 2026 | 0 of 4 |",
                     "| A7 listed in July 2026 | 8 of 8 |",
                     "| A7 listed in August 2026 | 0 of 8 |",
                     "38,160 of 38,162 (99.99%)",
                     "| LUPE3, GRS10, PV1 on August's Planned sheet | 3 of 3 |",
                     "| The 7 \"left in both\" keys listed in August | 0 of 7 |",
                     "md5 2be6ac001022cf230f87dc70dc740496",
                     "md5 5090d7695d8065746557ca0b8df6fe2b",
                     "233,063 rows, 40,073 generators",
                     "66466/43580, 67674/LUPE3, 67788/GRS10, 69144/PV1"):
            self.assertIn(text, self.doc)
        self.assertEqual(round(38160 / 38162, 4), 0.9999)

    def test_links_and_disclosure(self):
        self.assertIn("[plan](endrule-plan.md)", self.doc)
        self.assertIn("[endrule-2](endrule2-plan.md)", self.doc)
        self.assertIn("made with AI agents working in MV2's name", self.doc)
        self.assertIn("no person has checked these results by hand", self.doc)
        self.assertIn("PUDL's code (MIT) and data (CC BY 4.0) are downloaded at run time and "
                      "not stored here.", self.doc)


if __name__ == "__main__":
    unittest.main()
