"""Checks that docs/xwpair.md reports job xwpair-v1 honestly: the gates and every prediction scored
as the job scored them (three failed, three not scored, with their cause), the year table and the
2024 scores recomputed from data/xwpair-units-2018-2024.csv, the 2024 size-matched units copied
from that file, the provenance, the post-hoc reading marked as not pre-registered, and the limits.
Reads local files only.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import csv
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))

# Copied from job xwpair-v1's xwpair.json "scores" (7 November 2026). P4-P6 are absent there:
# not scored.
SCORES = {"G1": True, "P1": True, "P2": False, "P3": False, "G2": True, "P7": False}
PROBS = {"P1": "60%", "P2": "65%", "P3": "55%", "P4": "70%", "P5": "55%", "P6": "60%",
         "P7": "50%"}
# xwpair.json "summary": year -> CEMS units (not in the data file).
CEMS = {2018: 4718, 2019: 4572, 2020: 4475, 2021: 4437, 2022: 4359, 2023: 4273, 2024: 4215}
# xwpair.json "oge" (2024) and "oge_rows".
OGE_ROWS, OGE_UNITS, OGE_PRESENT, OGE_UNMATCHED = 346, 306, 17, 0
# Bars from tools/xwpair/xwpair.py 0.1.0.
P1_LO, P1_HI, P2_SHARE, P3_MIN, P4_MIN_N, P5_MIN_N, P7_MIN = 0.02, 0.10, 0.30, 25, 20, 10, 10
CLASSES = ("no_load", "no_candidate", "no_size_match", "ambiguous", "unique_pair")


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


def rows(path):
    with open(os.path.join(HERE, path), encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


class XwpairResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/xwpair.md")
        cls.rows = rows("data/xwpair-units-2018-2024.csv")

    def test_headline(self):
        self.assertIn("**Both gates held; 1 of the 4 predictions that could be scored held, "
                      "3 failed, and 3 could not be scored.**", self.doc)
        self.assertIn("Result of pre-registration xwpair-1 ([plan](xwpair-plan.md), commit "
                      "6265651", self.doc)
        self.assertIn("made with AI agents working in MV2's name", self.doc)
        self.assertIn("no person has checked these results by hand", self.doc)

    def test_score_rows(self):
        self.assertIn("| G1 | gate | held |", self.doc)
        self.assertIn("| G2 | gate | held |", self.doc)
        for p, prob in PROBS.items():
            if p in SCORES:
                word = "held" if SCORES[p] else "failed"
            else:
                word = "not scored"
            self.assertIn("| %s | %s | %s |" % (p, prob, word), self.doc)
        self.assertIn("**Why P2 and P3 failed.**", self.doc)
        self.assertIn("**Why P4 to P6 could not be scored, and P7 failed.**", self.doc)
        self.assertIn("are reported as failed or not scored and are not re-scored", self.doc)

    def test_data_file(self):
        self.assertEqual(len(self.rows), 1867)
        self.assertIn("(1867 rows)", self.doc)

    def test_year_table(self):
        for y, n in CEMS.items():
            ys = [r for r in self.rows if int(r["report_year"]) == y]
            cand = sum(1 for r in ys if r["candidates_id_pm_mw"])
            cells = [str(y), str(n), str(len(ys)), str(cand)]
            cells += [str(sum(1 for r in ys if r["class"] == c)) for c in CLASSES]
            self.assertIn("| " + " | ".join(cells) + " |", self.doc)

    def test_newest_scores_recomputed(self):
        r24 = [r for r in self.rows if r["report_year"] == "2024"]
        self.assertEqual(len(r24), 273)
        share = len(r24) / CEMS[2024]
        self.assertEqual(P1_LO <= share <= P1_HI, SCORES["P1"])
        cand = sum(1 for r in r24 if r["candidates_id_pm_mw"])
        self.assertEqual(cand, 43)
        self.assertEqual(cand / len(r24) >= P2_SHARE, SCORES["P2"])
        pairs = [r for r in r24 if r["class"] == "unique_pair"]
        self.assertEqual(len(pairs) >= P3_MIN, SCORES["P3"])
        new_pairs = [r for r in pairs if r["in_oge_campd_rows"] != "True"]
        self.assertEqual(len(new_pairs) >= P7_MIN, SCORES["P7"])
        self.assertEqual([(r["plant_id_epa"], r["emissions_unit_id_epa"],
                           r["proposed_generator_id"]) for r in pairs], [("6061", "3", "MOR2")])
        self.assertTrue(OGE_PRESENT < P4_MIN_N and OGE_UNMATCHED < P5_MIN_N)
        self.assertNotIn("P4", SCORES)
        self.assertEqual(sum(1 for r in r24 if r["in_oge_campd_rows"] == "True"), OGE_UNMATCHED)
        for text in ("346 rows with the CAMPD note", "for 306 CEMS units",
                     "17 of OGE's 306 CAMPD units are 2024 CEMS units"):
            self.assertIn(text, self.doc)

    def test_size_matched_units(self):
        matched = [r for r in self.rows if r["report_year"] == "2024" and r["size_matched_generators"]]
        self.assertEqual(len(matched), 12)
        plants = {}
        for r in matched:
            plants.setdefault(r["plant_id_epa"], []).append(r)
        self.assertEqual(sorted(plants), ["55098", "55248", "55524", "60345", "6061"])
        for pe, rs in plants.items():
            units = ", ".join(r["emissions_unit_id_epa"] for r in rs)
            peaks = ", ".join("%g" % float(r["max_gross_load_mw"]) for r in rs)
            self.assertIn("| %s / %s | %s |" % (pe, units, peaks), self.doc)
        # OGE-in-table column: the CAMPD flag is False for all 12 (OGE's coverage of 4 of the 5
        # plants comes from older, non-CAMPD rows read by hand, see the doc).
        self.assertTrue(all(r["in_oge_campd_rows"] == "False" for r in matched))
        overlap = {(r["plant_id_epa"], r["emissions_unit_id_epa"]) for r in self.rows
                   if r["in_oge_campd_rows"] == "True"}
        self.assertEqual(len(overlap), 9)

    def test_proposed_rows(self):
        for unit, gen in (("1", "GEN1"), ("1", "GEN3"), ("2", "GEN2"), ("2", "GEN3")):
            self.assertIn("| 55098 | %s | 55098 | %s |" % (unit, gen), self.doc)

    def test_provenance(self):
        for text in ("md5 51589823a9d6c3ef268101ba99ef445d",
                     "md5 cf958cb9cf6c5b9a2eec0e1c0c31b61f",
                     "all 12 unit tests passed",
                     "190,240 bytes, md5 420d50a7e4d066d29eee909eab73d932, 44,833 rows",
                     "3,295,621 bytes, md5 689d3ac11dcb5648fc5f6519aa68740d, 118,117 rows",
                     "7,718,170 bytes, md5 6c4372366df319de1888d8fc6ea1ec0e, 667,073 rows",
                     "45,943 bytes, md5 d1275db58bd4cc9767c9ec0548d47ef7"):
            self.assertIn(text, self.doc)

    def test_post_hoc_and_limits(self):
        for text in ("## What else the rows show (read after scoring, not pre-registered)",
                     "## Proposed rows, for a person to check",
                     "is our assumption from the matching numbers; no person has checked it",
                     "Why most of OGE's units are not in PUDL's 2024 CEMS table was not checked.",
                     "No person has checked the code or the results by hand."):
            self.assertIn(text, self.doc)


if __name__ == "__main__":
    unittest.main()
