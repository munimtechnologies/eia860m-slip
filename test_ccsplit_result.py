"""Checks that docs/ccsplit.md reports job ccsplit-v1 honestly: the gates and every prediction
scored as the job scored them (two failed, with their cause), the year table recomputed from the
published data files, the 2024 hits and the P6 ratios recomputed from data/ccsplit-hits-2018-
2024.csv, the provenance, the post-hoc reading marked as not pre-registered, and the limits.
Reads local files only.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import csv
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))

# Copied from job ccsplit-v1's ccsplit.json "scores" (7 November 2026).
SCORES = {"G1": True, "G2": True, "P1": False, "P2": True, "P3": True, "P4": True, "P5": True,
          "P6": False}
PROBS = {"P1": "70%", "P2": "75%", "P3": "55%", "P4": "60%", "P5": "55%", "P6": "65%"}
# ccsplit.json "summary": year -> cc_plants (not in the data files).
CC_PLANTS = {2018: 439, 2019: 444, 2020: 445, 2021: 444, 2022: 444, 2023: 444, 2024: 442}
# Bars from tools/ccsplit/ccsplit.py 0.1.0.
P1_MIN, P3_FACTOR, P6_LO, P6_HI, P6_SHARE = 5, 2, 0.1, 1.2, 0.7


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


def rows(path):
    with open(os.path.join(HERE, path), encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


class CcsplitResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/ccsplit.md")
        cls.hits = rows("data/ccsplit-hits-2018-2024.csv")
        cls.orph = rows("data/ccsplit-orphans-2018-2024.csv")

    def test_headline(self):
        self.assertIn("**Both gates held; 4 of 6 predictions held, 2 failed.**", self.doc)
        self.assertEqual(sum(1 for p in PROBS if SCORES[p]), 4)
        self.assertIn("Result of pre-registration ccsplit-1 ([plan](ccsplit-plan.md), commit "
                      "90832cd", self.doc)
        self.assertIn("made with AI agents working in MV2's name", self.doc)
        self.assertIn("no person has checked these results by hand", self.doc)

    def test_score_rows(self):
        self.assertIn("| G1 | gate | held |", self.doc)
        self.assertIn("| G2 | gate | held |", self.doc)
        for p, prob in PROBS.items():
            word = "held" if SCORES[p] else "failed"
            self.assertIn("| %s | %s | %s |" % (p, prob, word), self.doc)
        self.assertIn("**Why P6 failed.**", self.doc)
        self.assertIn("The bar is reported as failed and is not re-scored.", self.doc)

    def test_data_files(self):
        self.assertEqual(len(self.hits), 20)
        self.assertEqual(len(self.orph), 59)
        self.assertIn("(20 rows)", self.doc)
        self.assertIn("(59 rows)", self.doc)

    def test_year_table(self):
        for y, cc in CC_PLANTS.items():
            o = [r for r in self.orph if int(r["report_year"]) == y]
            hp = {r["plant_id_eia"] for r in self.hits if int(r["report_year"]) == y}
            self.assertEqual(hp, {r["plant_id_eia"] for r in o if r["hit"] == "True"})
            self.assertIn("| %d | %d | %d | %d |" % (y, cc, len(o), len(hp)), self.doc)

    def test_newest_scores_recomputed(self):
        h24 = [r for r in self.hits if r["report_year"] == "2024"]
        o24 = [r for r in self.orph if r["report_year"] == "2024"]
        n = len({r["plant_id_eia"] for r in h24})
        self.assertEqual(n >= P1_MIN, SCORES["P1"])
        self.assertEqual(len(o24) >= P3_FACTOR * n, SCORES["P3"])
        self.assertEqual(all("ST" in r["generator_ids_epa"] for r in h24), SCORES["P5"])
        ratios = {}
        for r in h24:
            ratios[r["plant_id_eia"]] = round(float(r["orphan_ca_capacity_mw"])
                                              / float(r["ct_capacity_mw"]), 4)
        self.assertEqual(ratios, {"422": 0.2254, "58478": 0.3, "60589": 1.2177})
        inside = sum(1 for v in ratios.values() if P6_LO <= v <= P6_HI)
        self.assertEqual(inside / len(ratios) >= P6_SHARE, SCORES["P6"])
        for r in h24:
            cells = (r["emissions_unit_id_epa"], r["generator_ids_epa"],
                     r["generator_id_eia_ct"], r["ct_capacity_mw"],
                     r["orphan_ca_generators"], r["orphan_ca_capacity_mw"])
            self.assertIn("| " + " | ".join(cells) + " |", self.doc)
            self.assertIn("| %s | %s | %s | %s |" % (r["plant_id_epa"], r["emissions_unit_id_epa"],
                                                     r["plant_id_eia"], r["orphan_ca_generators"]),
                          self.doc)

    def test_provenance(self):
        for text in ("md5 59829bbe7e62f3f10ca73c34b5e6e5d8",
                     "md5 cd39f269a8b3616cb58aa4fc70cca1d6",
                     "all 14 unit tests passed",
                     "190,240 bytes, md5 420d50a7e4d066d29eee909eab73d932, 44,833 rows",
                     "7,718,170 bytes, md5 6c4372366df319de1888d8fc6ea1ec0e, 667,073 rows"):
            self.assertIn(text, self.doc)

    def test_post_hoc_and_limits(self):
        for text in ("## What else the rows show (read after scoring, not pre-registered)",
                     "## Proposed rows, for a person to check",
                     "[ccsub-plan.md](ccsub-plan.md), id ccsub-1",
                     "The two counts are not expected to agree.",
                     "this run did not read `GEN2`'s nameplate",
                     "No person has checked the code or the results by hand."):
            self.assertIn(text, self.doc)


if __name__ == "__main__":
    unittest.main()
