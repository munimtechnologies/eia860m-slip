"""Checks that docs/endrule2-plan.md states what was seen before the bars were set, names its
gates and bars, and that tools/endrule2/endrule2.py scores the same thresholds. Reads text
only, so it needs no pandas.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class Endrule2PlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/endrule2-plan.md")
        cls.code = read("tools/endrule2/endrule2.py")

    def test_status_and_seen(self):
        self.assertIn("Status: pre-registration, nothing run yet. Pre-registration id: "
                      "endrule-2.", self.doc)
        self.assertIn("## What we have seen (before writing this)", self.doc)
        self.assertIn("2026-02: 44, 2026-03: 24, 2026-04: 28, 2026-05: 21, 2026-06: 26, "
                      "2026-07: 10, so 153 generators in all", self.doc)
        self.assertEqual(44 + 24 + 28 + 21 + 26 + 10, 153)
        self.assertIn("Which EIA sheets list these 153 was not read.", self.doc)
        self.assertIn("38,160 of the 38,162", self.doc)
        self.assertIn('TOKEN = "Pre-registration id: endrule-2."',
                      read("tools/endrule2/fetch_plan_code.py"))

    def test_bars(self):
        for text in ("**Gate G1:**", "**Gate G2:**", "**Q1 (85%):**", "**Q2 (85%):**",
                     "**Q3 (70%):**", "**Q4 (55%):**",
                     "at least 95% of the fresh generators are listed in month E-1",
                     "at most 5% of the fresh generators are listed in month E.",
                     "at least 90% are listed in month E-1 and at most 10% in month E",
                     "at least 60% of the fresh generators are on the \"Canceled or "
                     "Postponed\" sheet in month E",
                     "the fresh groups together hold at least 100 generators",
                     "2026-11-02 18:13:25 UTC"):
            self.assertIn(text, self.doc)

    def test_code_scores_the_same_thresholds(self):
        for text in ('VERSION = "0.1.0"', 'LATEST = "2026-09"', "MIN_FRESH = 100",
                     'FRESH = ("2026-02", "2026-03", "2026-04", "2026-05", "2026-06", '
                     '"2026-07")',
                     's["Q1"] = f["in_prev_share"] >= 0.95',
                     's["Q2"] = f["in_end_share"] <= 0.05',
                     'r["in_prev"] / r["n"] >= 0.90 and r["in_end"] / r["n"] <= 0.10',
                     's["Q4"] = f["cancel_end_share"] >= 0.60',
                     "import endrule as er"):
            self.assertIn(text, self.code)
        self.assertIn("`tools/endrule2/endrule2.py` 0.1.0", self.doc)
        self.assertIn("`tools/endrule/endrule.py` 0.1.0, reused unchanged", self.doc)

    def test_disclosure(self):
        self.assertIn("made with AI agents working in MV2's name", self.doc)
        self.assertIn("PUDL's code (MIT) and data (CC BY 4.0) are downloaded at run time and "
                      "not stored here.", self.doc)
        self.assertIn("Apache-2.0", self.code)
        self.assertNotIn("MIT License", self.code)


if __name__ == "__main__":
    unittest.main()
