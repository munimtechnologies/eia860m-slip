"""Checks that docs/cems-blank-plan.md states what was seen before the bars were set, names
its gates and bars, and that tools/cems-blank/blank_check.py scores the same thresholds.
Reads text only, so it needs no polars.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))

# Counted in compete-results/cems-mindown-v3/out/units_none_vs_fill.csv.
V3 = {"units": 305, "no_min": 46, "none_at1": 199, "fill_at2": 178, "moved_to_2": 153,
      "already_2": 25}
ISOLATED = {"Colorado": 404, "Indiana": 260, "Wisconsin": 146}


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class CemsBlankPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/cems-blank-plan.md")
        cls.code = read("tools/cems-blank/blank_check.py")

    def test_status_and_id(self):
        self.assertIn("Status: pre-registration, nothing run yet. Pre-registration id: "
                      "cems-blank-1.", self.doc)
        self.assertIn("## What we have seen (before writing this)", self.doc)
        self.assertIn('TOKEN = "Pre-registration id: cems-blank-1."',
                      read("tools/cems-blank/fetch_plan_code.py"))

    def test_seen_counts(self):
        v = V3
        self.assertEqual(v["moved_to_2"] + v["already_2"], v["fill_at2"])
        self.assertIn("so %d have one" % (v["units"] - v["no_min"]), self.doc)
        self.assertIn("%d of those %d are at exactly 2 hours: the %d that moved from 1 hour "
                      "plus %d that were already at 2 hours."
                      % (v["fill_at2"], v["units"] - v["no_min"], v["moved_to_2"],
                         v["already_2"]), self.doc)
        self.assertIn("took the units at 1 hour from %d to 0" % v["none_at1"], self.doc)
        self.assertIn("404 in Colorado, 260 in Indiana and 146 in Wisconsin", self.doc)
        self.assertEqual(round(1.07 / 22.9 * 100, 1), 4.7)
        self.assertIn("about 4.7%", self.doc)

    def test_bars(self):
        for text in ("**Gate B0:**", "**Gate B1:**", "**P0 (85%):**", "**P1 (55%):**",
                     "**P2 (75%):**", "**P3 (55%):**", "**P4 (65%):**", "**P5 (65%):**",
                     "If B0 or B1 fails, P0-P5 are reported but not scored.",
                     "for at least 99% of units", "at least 99% of the one-hour sandwiched",
                     "at least half of the units at exactly 2 hours",
                     "at least 90% of the hours", "falls by at least 40%",
                     "between 1% and 10% of all down-run hours", "fewer than 20% of the units",
                     "`operating_time_hours` of at least 0.999"):
            self.assertIn(text, self.doc)

    def test_code_scores_the_same_thresholds(self):
        for text in ('VERSION = "0.1.0"', "FULL_HOUR = 0.999",
                     'm[k]["run_min_equal"] >= 0.99 * m[k]["units"]',
                     'v3[k]["equal"] >= 0.99 * v3[k]["rows"]',
                     'n["isolated_no_op_no_heat"] >= 0.99 * n[',
                     'f["at2_upflank"] >= 0.5 * f["at2"]',
                     'f["two_runs_no_op_hours"] >= 0.90 * f[',
                     'f["cf_strict_le2"] <= 0.60 * f["le2"]',
                     '0.01 <= f["run_op_hours"] / f["run_hours"] <= 0.10',
                     'f["units_min_runs_op"] < 0.20 * f["units_with_min"]'):
            self.assertIn(text, self.code)
        self.assertIn("blank_check.py` 0.1.0", self.doc)

    def test_disclosure(self):
        self.assertIn("made with AI agents working in MV2's name", self.doc)
        self.assertIn("PUDL's code (MIT) and data (CC BY 4.0) are downloaded at run time and "
                      "not stored here.", self.doc)
        self.assertIn("Apache-2.0", self.code)


if __name__ == "__main__":
    unittest.main()
