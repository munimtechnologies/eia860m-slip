"""Checks that docs/minload-plan.md states what was seen before the bars were set, names its
gates and bars, and that tools/minload/minload_check.py scores the same thresholds. Reads text
only, so it needs no polars.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class MinloadPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/minload-plan.md")
        cls.code = read("tools/minload/minload_check.py")

    def test_status_and_id(self):
        self.assertIn("Status: pre-registration, nothing run yet. Pre-registration id: "
                      "minload-1.", self.doc)
        self.assertIn("## What we have seen (before writing this)", self.doc)
        self.assertIn("We have not read any row of the operational-characteristics table",
                      self.doc)
        self.assertIn('TOKEN = "Pre-registration id: minload-1."',
                      read("tools/minload/fetch_plan_code.py"))
        self.assertIn("3,293,894 bytes", self.doc)

    def test_bars(self):
        for text in ("**Gate G1:**", "**Gate G2:**", "**Gate G3:**", "**P1 (55%):**",
                     "**P2 (65%):**", "**P3 (85%):**", "**P4 (60%):**", "**P5 (70%):**",
                     "**P6 (60%):**", "all 13 columns", "2022 or later", "at least 300 pairs",
                     "between 0.7 and 1.3", "at least half of the comparison set",
                     "fewer than 40% of the comparison set agree", "at least 0.80",
                     "below 0.50", "at least 15 percentage points higher for GT than for ST",
                     "at least 20 pairs", "at least 15% of the comparison set",
                     "below 80% of EIA's", "within 20% of 1"):
            self.assertIn(text, self.doc)

    def test_code_scores_the_same_thresholds(self):
        for text in ('VERSION = "0.1.0"', "MIN_YEAR = 2022", "AGREE = 0.20", "LOW = 0.80",
                     's["G2"] = c["n"] >= 300', "0.7 <= c[\"median_max_frac\"] <= 1.3",
                     's["P1"] = c["above"] >= 0.5 * c["n"]',
                     's["P2"] = c["within_20"] < 0.40 * c["n"]',
                     's["P6"] = c["below_80"] >= 0.15 * c["n"]',
                     's["P3"] = c["spearman_mw"] >= 0.80',
                     's["P4"] = c["spearman_frac"] < 0.50',
                     'gt["units"] >= 20 and st["units"] >= 20',
                     '>= st["null_factor"] / st["units"] + 0.15',
                     'CC_CODES = {"CT", "CA", "CS", "CC"}',
                     'OPS_TABLE = "out_epacems__yearly_operational_characteristics"',
                     'XW_TABLE = "core_epa__assn_eia_epacamd"',
                     'GEN_TABLE = "core_eia860__scd_generators"'):
            self.assertIn(text, self.code)
        self.assertIn("minload_check.py` 0.1.0", self.doc)

    def test_disclosure(self):
        self.assertIn("made with AI agents working in MV2's name", self.doc)
        self.assertIn("PUDL's code (MIT) and data (CC BY 4.0) are downloaded at run time and "
                      "not stored here.", self.doc)
        self.assertIn("Apache-2.0", self.code)
        self.assertNotIn("MIT License", self.code)


if __name__ == "__main__":
    unittest.main()
