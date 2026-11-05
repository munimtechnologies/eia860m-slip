"""Checks that docs/endrule-plan.md states what was seen before the bars were set, names its
gates and bars, and that tools/endrule/endrule.py scores the same thresholds. Reads text only,
so it needs no pandas.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class EndrulePlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/endrule-plan.md")
        cls.code = read("tools/endrule/endrule.py")

    def test_status_and_id(self):
        self.assertIn("Status: pre-registration, nothing run yet. Pre-registration id: "
                      "endrule-1.", self.doc)
        self.assertIn("## What we have seen (before writing this)", self.doc)
        self.assertIn("returned a 55,901-byte page that is not an xlsx file", self.doc)
        self.assertIn("md5 2be6ac001022cf230f87dc70dc740496, 233,063 rows", self.doc)
        self.assertIn('TOKEN = "Pre-registration id: endrule-1."',
                      read("tools/endrule/fetch_plan_code.py"))

    def test_bars(self):
        for text in ("**Gate G1:**", "**Gate G2:**", "**P1 (85%):**", "**P2 (85%):**",
                     "**P3 (80%):**", "**P4 (90%):**", "**P5 (75%):**",
                     "at least 95% of A8 are listed in August 2026",
                     "at most 5% of A8 are listed in September 2026",
                     "at least 95% of A7 are listed in July 2026 and at most 5% in August 2026",
                     "at least 99% of A9 are listed in September 2026",
                     "A8 and A7 each hold at least 10 generators",
                     "2026-11-02 18:13:25 UTC", "neither \"cancel\" nor \"_pr\""):
            self.assertIn(text, self.doc)

    def test_code_scores_the_same_thresholds(self):
        for text in ('VERSION = "0.1.0"', 'MERGED = "2026-11-02T18:13:25Z"',
                     'LATEST = "2026-09"', "MIN_GROUP = 10",
                     'GROUPS = {"A9": "2026-10", "A8": "2026-09", "A7": "2026-08"}',
                     'SKIP = ("cancel", "_pr")',
                     's["P1"] = m["A8_in_2026-08"]["share"] >= 0.95',
                     's["P2"] = m["A8_in_2026-09"]["share"] <= 0.05',
                     's["P3"] = m["A7_in_2026-07"]["share"] >= 0.95 and '
                     'm["A7_in_2026-08"]["share"] <= 0.05',
                     's["P4"] = m["A9_in_2026-09"]["share"] >= 0.99',
                     's["P5"] = m["diff_on_aug_planned"] == len(DIFF) and '
                     'm["left_both_listed_aug"] == 0'):
            self.assertIn(text, self.code)
        self.assertIn("`tools/endrule/endrule.py` 0.1.0", self.doc)
        for key in ("67674/LUPE3", "67788/GRS10", "69144/PV1", "65399/U3", "65655/HECHQ",
                    "66692/HOLLY", "66692/HOLY", "67660/MALAL", "68198/TRS", "68811/RIPLE"):
            self.assertIn(key, self.doc)
            self.assertIn('"%s"' % key, self.code)

    def test_disclosure(self):
        self.assertIn("made with AI agents working in MV2's name", self.doc)
        self.assertIn("PUDL's code (MIT) and data (CC BY 4.0) are downloaded at run time and "
                      "not stored here.", self.doc)
        self.assertIn("Apache-2.0", self.code)
        self.assertNotIn("MIT License", self.code)


if __name__ == "__main__":
    unittest.main()
