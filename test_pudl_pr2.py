"""Checks that docs/pudl-pr2.md scores gates H0-H1 and predictions P1-P4 of pre-registration
pudl-pr-2 (docs/pudl-pr2-plan.md) with the numbers job pudl-pr2-v1 wrote
(out/check/workbook.json and out/check/watchlist_2026-09_workbook.csv), using the plan's own
bars, and that the failed bar is reported as failed. Reads text only.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))

# Copied from compete-results/pudl-pr2-v1/out/check/workbook.json.
AFTER = {"pudl_rows": 568, "workbook_rows": 571, "union": 571, "same_change": 568,
         "same_share": 0.9947, "pudl_rows_same_share": 1.0, "checks_all_pass": True,
         "pudl_max": "2026-09", "differences": {"none -> left": 3},
         "left": (7, 10)}
DIFF_KEYS = ["67674/LUPE3", "67788/GRS10", "69144/PV1"]
# From the plan's baseline (job watchsep-v2, 31 October 2026).
BEFORE = {"pudl_rows": 559, "workbook_rows": 568, "same_share": 0.9842}
NINE = ["66545/MMTHS", "66893/TXJS2", "67836/GSP1", "67836/GSP2", "68149/RAVEB",
        "68240/SS3PV", "69463/BCRSP", "69967/FTS", "70202/PS56"]
# Rows of out/check/watchlist_2026-09_workbook.csv for the nine keys (absent = no change).
CHANGE_NOW = {"68149/RAVEB": "advanced", "68240/SS3PV": "delayed",
              "69463/BCRSP": "within_band", "69967/FTS": "advanced",
              "70202/PS56": "advanced"}
EIA_MD5 = "4c741eb77a5ccad5aca32ffe43f398af"
SCORES = {"H0": True, "H1": True, "P1": True, "P2": True, "P3": False, "P4": True}


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class PudlPr2ResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/pudl-pr2.md")

    def test_scores_follow_the_plan_bars(self):
        a = AFTER
        nine_match = [k for k in NINE if k not in DIFF_KEYS]
        s = {
            "H0": a["pudl_max"] >= "2026-09",
            "H1": a["checks_all_pass"] and a["same_change"] >= 0.98 * a["pudl_rows"],
            "P1": CHANGE_NOW["68149/RAVEB"] == "advanced"
            and CHANGE_NOW["70202/PS56"] == "advanced"
            and "68149/RAVEB" not in DIFF_KEYS and "70202/PS56" not in DIFF_KEYS,
            "P2": len(nine_match) >= 7,
            "P3": a["same_share"] >= 0.995,
            "P4": a["pudl_rows_same_share"] == 1.0,
        }
        self.assertEqual(s, SCORES)
        self.assertEqual(round(a["same_change"] / a["union"], 4), a["same_share"])
        self.assertEqual(round(BEFORE["pudl_rows"] / BEFORE["workbook_rows"], 4),
                         BEFORE["same_share"])
        self.assertIn("**Both gates held and 3 of 4 predictions held; P3 failed.**", self.doc)

    def test_score_rows(self):
        a = AFTER
        for row in (
                "| Gate H0 | held | rebuilt after the merge; latest report %s; EIA's md5 "
                "unchanged |" % a["pudl_max"],
                "| Gate H1 | held | checks C1-C4 all pass; %d of %d PUDL rows (100%%) match the "
                "workbook route |" % (a["same_change"], a["pudl_rows"]),
                "| P2 (65%) | held | 9 of the 9 keys match; the bar was at least 7 |",
                "| P3 (60%%) | failed | same_share = %.4f (%d of %d keys); the bar was at least "
                "0.995 |" % (a["same_share"], a["same_change"], a["union"]),
                "| P4 (75%%) | held | pudl_rows_same_share = %.1f |" % a["pudl_rows_same_share"]):
            self.assertIn(row, self.doc)

    def test_before_after_and_keys(self):
        self.assertIn("| PUDL rows for 2026-09 | %d | %d |"
                      % (BEFORE["pudl_rows"], AFTER["pudl_rows"]), self.doc)
        self.assertIn("| Workbook-route rows | %d | %d |"
                      % (BEFORE["workbook_rows"], AFTER["workbook_rows"]), self.doc)
        self.assertIn("| same_share | %.4f | %.4f |"
                      % (BEFORE["same_share"], AFTER["same_share"]), self.doc)
        for key in NINE:
            if key in CHANGE_NOW:
                self.assertIn("| %s | " % key, self.doc)
                line = [ln for ln in self.doc.splitlines() if ln.startswith("| %s |" % key)][0]
                self.assertIn("| %s in both" % CHANGE_NOW[key], line)
            else:
                self.assertIn("| %s | " % key, self.doc)
                line = [ln for ln in self.doc.splitlines() if ln.startswith("| %s |" % key)][0]
                self.assertIn("| no September change in either |", line)
        for key in DIFF_KEYS:
            self.assertTrue(any(ln.startswith("| %s |" % key) for ln in self.doc.splitlines()))
        self.assertEqual(AFTER["differences"]["none -> left"], len(DIFF_KEYS))
        self.assertEqual(AFTER["left"][1] - AFTER["left"][0], len(DIFF_KEYS))
        self.assertIn("The workbook route counts %d generators as \"left\" in September and "
                      "PUDL's edition %d." % (AFTER["left"][1], AFTER["left"][0]), self.doc)

    def test_provenance_and_disclosure(self):
        for text in (EIA_MD5, "c305ed1", "8aff7842ae751cf7a42f34dd1b75fb84",
                     "Zenodo record 23639605", "[plan](pudl-pr2-plan.md)",
                     "no comment was posted on the PR",
                     "made with AI agents working in MV2's name; no person has checked these "
                     "results by hand",
                     "PUDL's code (MIT) and data (CC BY 4.0) are downloaded at run time and not "
                     "stored here."):
            self.assertIn(text, self.doc)
        self.assertNotIn("MIT License", self.doc)


if __name__ == "__main__":
    unittest.main()
