"""Checks that docs/xwdev.md reports job xwdev-v1 honestly: the gate and every prediction
scored as the job scored them, the provenance of the data and code, each lead's links copied
from the job's "leads", the empty manual-match scan, the post-hoc reading marked as not
pre-registered, and the limits. Reads text only.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))

# Copied from job xwdev-v1's xwdev.json "scores" (6 November 2026).
SCORES = {"G1": True, "P1": True, "P2": True, "P3": True, "P4": True, "P5": True}
PROBS = {"P1": "50%", "P2": "65%", "P3": "65%", "P4": "65%", "P5": "40%"}

# Copied from xwdev.json "leads": every outcome "stands", no candidate linked.
LEADS = {"Antelope Elk": ("57865/E01", "57865/E02", "57865/E03"),
         "Chalk Point": ("1571/GT1",),
         "Glenarm": ("422/GT5",),
         "LEPA Unit No. 1": ("58478/LEPA1",)}

# xwdev.json "manual_matches": sheet -> rows counted including the header row; "hits": [].
SHEETS = {"unit_manual_matches": 90, "unit_manual_excluded": 253, "plant_id_manual_matches": 30,
          "plant_id_epa_to_eia": 17, "further_research": 112, "Sheet Descriptions": 5}


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class XwdevResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/xwdev.md")

    def test_headline(self):
        self.assertTrue(all(SCORES.values()))
        self.assertIn("**Gate G1 held, and all 5 predictions held.**", self.doc)
        self.assertIn("Result of pre-registration xwdev-1 ([plan](xwdev-plan.md), commit c22ba3f",
                      self.doc)
        self.assertIn("made with AI agents working in MV2's name", self.doc)
        self.assertIn("no person has checked these results by hand", self.doc)
        self.assertIn("would not on its own fix any of the four", self.doc)

    def test_score_rows(self):
        self.assertIn("| G1 | gate | held |", self.doc)
        for p, prob in PROBS.items():
            word = "held" if SCORES[p] else "failed"
            self.assertIn("| %s | %s | %s |" % (p, prob, word), self.doc)
        self.assertNotIn("| failed |", self.doc)

    def test_leads(self):
        for name, targets in LEADS.items():
            self.assertIn("| %s |" % name, self.doc)
            for t in targets:
                plant, gen = t.split("/")
                self.assertIn(plant + "/", self.doc)
                self.assertIn(gen, self.doc)
        self.assertIn("57865/E01, E02, E03", self.doc)
        self.assertIn("| Step 1d (both) |", self.doc)

    def test_manual_matches(self):
        for sheet, n in SHEETS.items():
            self.assertIn("`%s` (%d" % (sheet, n - 1), self.doc)
        self.assertIn("None of their rows has a cell equal to 57865, 58835, 1571, 61890, 422 or "
                      "58478", self.doc)

    def test_provenance(self):
        for text in ("md5 ce7ff1c99e1eb70a7660f6675e1d4388",
                     "md5 7897543ebe2b04e22b21ee833ee8e77a",
                     "all 13 unit tests passed",
                     "3423b2ab457222e1eac5d69d25a98b5f62ce5975",
                     "2,314,285 bytes, md5 5120bcdeab9d0281afc3a2c9d2c5f1a5, 5,810 data rows",
                     "49,694 bytes, md5 8c86e7be228f4d4d97bc6faf50afb05b"):
            self.assertIn(text, self.doc)

    def test_post_hoc_and_limits(self):
        for text in ("## What else the file shows (read after scoring, not pre-registered)",
                     "[ccsub-plan.md](ccsub-plan.md) (id ccsub-1)",
                     "The development branch is not a release; EPA may change it.",
                     "No person has checked the code or the results by hand."):
            self.assertIn(text, self.doc)


if __name__ == "__main__":
    unittest.main()
