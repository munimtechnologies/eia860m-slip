"""Checks that docs/pudl-pr2-plan.md states what job watchsep-v2 saw before the bars were set,
and names its gates and bars. Reads text only, so it needs no pandas.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))

# Copied from compete-results/watchsep-v2/out/check/workbook.json, months[0].self_check.
SELF_CHECK = {"pudl_rows": 559, "workbook_rows": 568, "union": 568, "same_change": 559,
              "same_share": 0.9842, "pudl_rows_same_share": 1.0}
DIFFERENCES = {"none -> delayed": 4, "none -> advanced": 3, "none -> within_band": 2}
KEYS = {"66545/MMTHS": "delayed", "66893/TXJS2": "within_band", "67836/GSP1": "delayed",
        "67836/GSP2": "delayed", "68149/RAVEB": "advanced", "68240/SS3PV": "delayed",
        "69463/BCRSP": "within_band", "69967/FTS": "advanced", "70202/PS56": "advanced"}
WORKBOOK_MD5 = "8aff7842ae751cf7a42f34dd1b75fb84"
EIA_SEP_MD5 = "4c741eb77a5ccad5aca32ffe43f398af"


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class PudlPr2PlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/pudl-pr2-plan.md")

    def test_status_and_id(self):
        self.assertIn("Status: pre-registration, nothing run yet on the build it scores.",
                      self.doc)
        self.assertIn("Pre-registration id: pudl-pr-2.", self.doc)
        self.assertIn("## What we have seen (before writing this)", self.doc)

    def test_seen_counts(self):
        s = SELF_CHECK
        self.assertEqual(s["union"] - s["same_change"], sum(DIFFERENCES.values()))
        self.assertEqual(len(KEYS), sum(DIFFERENCES.values()))
        for kind, n in DIFFERENCES.items():
            self.assertEqual(sum(1 for v in KEYS.values() if v == kind.split(" -> ")[1]), n)
        self.assertEqual(round(s["same_change"] / s["union"], 4), s["same_share"])
        self.assertIn("%d workbook rows and %d PUDL rows; all %d of PUDL's rows"
                      % (s["workbook_rows"], s["pudl_rows"], s["pudl_rows"]), self.doc)
        self.assertIn("(same_share %.4f," % s["same_share"], self.doc)
        for key, change in KEYS.items():
            self.assertIn("| %s | %s |" % (key, change), self.doc)
        self.assertEqual(self.doc.count("\n| 6"), 8)
        self.assertEqual(self.doc.count("\n| 7"), 1)

    def test_files(self):
        self.assertIn("commit cf668cf, md5 %s" % WORKBOOK_MD5, self.doc)
        self.assertEqual(self.doc.count(EIA_SEP_MD5), 2)
        self.assertIn("Zenodo record 23639605, version 51.0.0", self.doc)

    def test_bars(self):
        for text in ("**Gate H0:**", "**Gate H1:**", "**P1 (80%):**", "**P2 (65%):**",
                     "**P3 (60%):**", "**P4 (75%):**",
                     "for both 68149/RAVEB and 70202/PS56",
                     "at least 7 of the 9 keys above",
                     "same_share is at least 0.995 (with 568 rows, at most 2 differ)",
                     "If H0 or H1 fails, P1-P4 are reported but not scored."):
            self.assertIn(text, self.doc)
        self.assertGreaterEqual(int(0.995 * 568 + 0.999), 566)

    def test_disclosure(self):
        self.assertIn("made with AI agents working in MV2's name", self.doc)
        self.assertIn("PUDL's data (CC BY 4.0) is downloaded at run time and not stored here.",
                      self.doc)


if __name__ == "__main__":
    unittest.main()
