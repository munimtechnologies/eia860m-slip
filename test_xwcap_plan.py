"""Checks that docs/xwcap-plan.md states what was seen before the bars were set, names its
gates and bars, and that tools/xwcap/xwcap_check.py scores the same thresholds. Reads text
only, so it needs no polars.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class XwcapPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/xwcap-plan.md")
        cls.code = read("tools/xwcap/xwcap_check.py")

    def test_status_and_id(self):
        self.assertIn("Status: pre-registration, nothing run yet. Pre-registration id: "
                      "xwcap-1.", self.doc)
        self.assertIn("## What we have seen (before writing this)", self.doc)
        self.assertIn("found 20 pairs at 1.5 or more (0.9% of 2,179), 11 of them at 2 or more",
                      self.doc)
        self.assertIn("10 GT, 4 combined-cycle codes (one CA, three CT), 3 ST and 3 IC",
                      self.doc)
        self.assertIn("190,240 bytes", self.doc)
        self.assertIn('TOKEN = "Pre-registration id: xwcap-1."',
                      read("tools/xwcap/fetch_plan_code.py"))

    def test_bars(self):
        for text in ("**Gate G1:**", "**Gate G2:**", "**Gate G3:**", "**P1 (75%):**",
                     "**P2 (60%):**", "**P3 (55%):**", "**P4 (70%):**", "**P5 (65%):**",
                     "the 4 columns", "2022 or later", "at least 1,500 groups",
                     "between 0.7 and 1.3", "fewer than 5% of the study set are over",
                     "fewer than half of the over groups are in class cc",
                     "at least 20% of the over groups are in class candidate",
                     "at least 10 over groups", "plant 57865 is over and in class candidate",
                     "at least 70% were in over groups", "at least 10 such units",
                     "at least 1.5", "by at least 10 MW", "below 0.5",
                     "at least half of the group's excess", "OP, SB, OS or OA",
                     "GT, ST, IC, CT, CA, CS or CC", "CT, CA, CS or CC"):
            self.assertIn(text, self.doc)

    def test_code_scores_the_same_thresholds(self):
        for text in ('VERSION = "0.1.0"', "MIN_YEAR = 2022", "OVER = 1.5", "UNDER = 0.5",
                     "MIN_EXCESS_MW = 10.0", "CAND_SHARE = 0.5", "WATCH_PLANT = 57865",
                     'CC_CODES = {"CT", "CA", "CS", "CC"}',
                     'COMBUSTION = {"GT", "ST", "IC", "CT", "CA", "CS", "CC"}',
                     'EXISTING = {"OP", "SB", "OS", "OA"}',
                     's["G2"] = m["study"] >= 1500',
                     's["G3"] = 0.7 <= m["median_ratio"] <= 1.3',
                     's["P1"] = m["over"] < 0.05 * m["study"]',
                     'if m["over"] >= 10:',
                     's["P2"] = m["over_by_class"]["cc"] < 0.5 * m["over"]',
                     's["P3"] = m["over_by_class"]["candidate"] >= 0.20 * m["over"]',
                     'if pc and pc["study"] >= 1:',
                     's["P4"] = pc["over"] == pc["study"] and pc["candidate"] == pc["study"]',
                     'if ps and ps["in_prev_study"] >= 10:',
                     's["P5"] = ps["also_over_prev"] >= 0.70 * ps["in_prev_study"]',
                     'OPS_TABLE = "out_epacems__yearly_operational_characteristics"',
                     'XW_TABLE = "core_epa__assn_eia_epacamd"',
                     'GEN_TABLE = "core_eia860__scd_generators"'):
            self.assertIn(text, self.code)
        self.assertIn("xwcap_check.py` 0.1.0", self.doc)

    def test_disclosure(self):
        self.assertIn("made with AI agents working in MV2's name", self.doc)
        self.assertIn("PUDL's code (MIT) and data (CC BY 4.0) are downloaded at run time and "
                      "not stored here.", self.doc)
        self.assertIn("Apache-2.0", self.code)
        self.assertNotIn("MIT License", self.code)


if __name__ == "__main__":
    unittest.main()
