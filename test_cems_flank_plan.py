"""Checks that docs/cems-flank-plan.md states what was seen before the bars were set, names
its gates and bars, and that tools/cems-flank/flank_check.py scores the same thresholds.
Reads text only, so it needs no polars.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))

# Published in docs/cems-blank.md (cems-blank-1) and counted in its job's 2-hour-run CSV.
SEEN = {"two_runs": 748, "at2_units": 178, "with_min": 259, "full_before": 9, "full_after": 15,
        "down_hours": 3843401}


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class CemsFlankPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/cems-flank-plan.md")
        cls.code = read("tools/cems-flank/flank_check.py")
        cls.blank = read("docs/cems-blank.md")

    def test_status_and_id(self):
        self.assertIn("Status: pre-registration, nothing run yet. Pre-registration id: "
                      "cems-flank-1.", self.doc)
        self.assertIn("## What we have seen (before writing this)", self.doc)
        self.assertIn('TOKEN = "Pre-registration id: cems-flank-1."',
                      read("tools/cems-flank/fetch_plan_code.py"))
        self.assertIn('"blank_check.py": "5524198e03689cce88bba1102e733638"',
                      read("tools/cems-flank/check_md5.py"))

    def test_seen_counts_match_cems_blank(self):
        s = SEEN
        self.assertIn("of the %d two-hour runs at units at exactly 2 hours, the hour before "
                      "reports a full operating hour (at least 0.999) in %d and the hour after "
                      "in %d." % (s["two_runs"], s["full_before"], s["full_after"]), self.doc)
        self.assertIn("in %d of 748 runs and the hour after in %d of 748"
                      % (s["full_before"], s["full_after"]), self.blank)
        self.assertIn("%d of the %d units with a minimum down time" % (s["at2_units"],
                                                                      s["with_min"]), self.doc)
        self.assertIn("among 3,843,401 down-run hours", self.doc)
        self.assertIn("0 of 3,843,401 down-run hours", self.blank)
        self.assertIn('SEEN = {"two_at2_runs": %d, "at2_units": %d}'
                      % (s["two_runs"], s["at2_units"]), self.code)

    def test_bars(self):
        for text in ("**Gate K1:**", "**Gate K2:**", "**Gate K3:**", "**Gate U0:**",
                     "**F1 (70%):**", "**F2 (60%):**", "**F3 (65%):**", "**D1 (60%):**",
                     "**D2 (75%):**", "**U1 (50%):**", "**U2 (60%):**", "**U3 (55%):**",
                     "each within 2%", "at least 80% of the units",
                     "at least 70% of the flanking hours of the 2-hour runs",
                     "within 15 percentage points", "down runs of 10 hours or more",
                     "at least 10,000 hours", "at least 5 units",
                     "at least 10 percentage points above",
                     "at least 40% of ST units", "at least 40% of slow-start units",
                     "at least 5 such units"):
            self.assertIn(text, self.doc)

    def test_code_scores_the_same_thresholds(self):
        for text in ('VERSION = "0.1.0"', "FULL_HOUR = 0.999", "HALF_HOUR = 0.5",
                     '<= 0.02 * SEEN["two_at2_runs"]', '<= 0.02 * SEEN["at2_units"]',
                     's["K3"] = w["null_load_heat_hours_valid"] == 0',
                     'w["null_load_heat_hours"] >= 10000',
                     'w["units_nunique_le1_with_heat"] >= 5',
                     'a["partial"] >= 0.70 * a["n"]', 'b["partial"] >= 0.70 * b["n"]',
                     '<= 0.15', 'lg["partial"] >= 0.70 * lg["n"]',
                     '>= 0.80 * t["units_with_min"]',
                     't["ct_ge3"] / t["ge3_units"] + 0.10',
                     't["st_units"] >= 5', 't["st_at2"] >= 0.40 * t["st_units"]',
                     't["slow_units"] >= 5', 't["slow_le2"] >= 0.40 * t["slow_units"]',
                     'CC_CODES = {"CT", "CA", "CS", "CC"}',
                     'COLD_RANK = {"10M": 1, "1H": 2, "12H": 3, "OVER": 4}',
                     'XW_TABLE = "core_epa__assn_eia_epacamd"',
                     'GEN_TABLE = "core_eia860__scd_generators"'):
            self.assertIn(text, self.code)
        self.assertIn("flank_check.py` 0.1.0", self.doc)

    def test_disclosure(self):
        self.assertIn("made with AI agents working in MV2's name", self.doc)
        self.assertIn("PUDL's code (MIT) and data (CC BY 4.0) are downloaded at run time and "
                      "not stored here.", self.doc)
        self.assertIn("cuts against his own patch", self.doc)
        self.assertIn("Apache-2.0", self.code)


if __name__ == "__main__":
    unittest.main()
