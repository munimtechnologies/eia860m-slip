"""Checks that docs/ccsub.md reports job ccsub-v1 honestly: the gate and every prediction scored as
the job scored them, the scores recomputed from data/ccsub-steam-2024.csv where the file allows,
every steam generator's row copied from that file, the provenance, the post-hoc reading marked
as not pre-registered, and the limits. Reads local files only.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import csv
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))

# Copied from job ccsub-v1's ccsub.json "scores" (7 November 2026).
SCORES = {"G1": True, "P1": True, "P2": True, "P3": True, "P4": True, "P5": True}
PROBS = {"P1": "85%", "P2": "55%", "P3": "65%", "P4": "60%", "P5": "80%"}
# ccsub.json "base" (not in the data file).
BASE_N, BASE_JOINED = 559, 559
# Bars from tools/ccsub/ccsub.py 0.1.0 / docs/ccsub-plan.md.
P2_MIN, P3_MIN, P4_MIN_N, P5_SHARE, P5_MIN_N = 7, 2, 3, 0.95, 200
HIT = {("422", "ST1"), ("58478", "LEPA2"), ("60589", "GEN3")}


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


def rows(path):
    with open(os.path.join(HERE, path), encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


class CcsubResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/ccsub.md")
        cls.rows = rows("data/ccsub-steam-2024.csv")

    def test_headline(self):
        self.assertIn("**Gate G1 held and all 5 predictions held.**", self.doc)
        self.assertTrue(all(SCORES.values()))
        self.assertIn("Result of pre-registration ccsub-1 ([plan](ccsub-plan.md), commit 6f69ea9",
                      self.doc)
        self.assertIn("made with AI agents working in MV2's name", self.doc)
        self.assertIn("no person has checked these results by hand", self.doc)

    def test_score_rows(self):
        self.assertIn("| G1 | gate | held |", self.doc)
        for p, prob in PROBS.items():
            word = "held" if SCORES[p] else "failed"
            self.assertIn("| %s | %s | %s |" % (p, prob, word), self.doc)

    def test_scores_recomputed(self):
        self.assertEqual(len(self.rows), 10)
        self.assertIn("(10 rows)", self.doc)
        classes = [r["class"] for r in self.rows]
        self.assertEqual("absent" not in classes, SCORES["P1"])
        joined = [r for r in self.rows if r["class"] == "joined"]
        self.assertEqual(len(joined), 7)
        self.assertEqual(len(joined) >= P2_MIN, SCORES["P2"])
        hits_joined = sum(1 for r in joined if (r["plant_id_eia"], r["generator_id"]) in HIT)
        self.assertEqual(hits_joined, 2)
        self.assertEqual(hits_joined >= P3_MIN, SCORES["P3"])
        self.assertTrue(len(joined) >= P4_MIN_N)
        self.assertEqual(all(r["shared_unit_id_pudl"] == "True" for r in joined), SCORES["P4"])
        self.assertTrue(BASE_N >= P5_MIN_N)
        self.assertEqual(BASE_JOINED / BASE_N >= P5_SHARE, SCORES["P5"])
        self.assertIn("559 of 559 linked operating CA generators", self.doc)

    def test_generator_rows(self):
        for r in self.rows:
            units = "%s / %s" % (r["unit_id_pudl"] or "none", r["ct_unit_id_pudl"] or "none")
            cells = (r["plant_id_eia"], r["generator_id"], r["class"], r["subplant_ids"],
                     r["linked_ct_generators"], r["ct_subplant_ids"], units,
                     r["subplant_generators"])
            self.assertIn("| " + " | ".join(cells) + " |", self.doc)

    def test_provenance(self):
        for text in ("md5 f91fe0220de4adb5ede0c0fc22df68aa",
                     "md5 1e4172279d5860990a539479c3cd006a",
                     "all 16 unit tests passed",
                     "411,998 bytes, md5 eedd186816cc3f0715ffe48538fcf35e, 45,398 rows",
                     "190,240 bytes, md5 420d50a7e4d066d29eee909eab73d932, 44,833 rows",
                     "7,718,170 bytes, md5 6c4372366df319de1888d8fc6ea1ec0e, 667,073 rows"):
            self.assertIn(text, self.doc)

    def test_post_hoc_and_limits(self):
        for text in ("## What else the rows show (read after scoring, not pre-registered)",
                     "we did not read EIA's own files to check",
                     "We did not check this in PUDL's code.",
                     "this is a close proxy for it, not the same thing",
                     "No person has checked the code or the results by hand."):
            self.assertIn(text, self.doc)


if __name__ == "__main__":
    unittest.main()
