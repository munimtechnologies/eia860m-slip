"""Checks that docs/xwpudl.md reports job xwpudl-v1 honestly: the gate and every prediction
scored as the job scored them, the provenance of the data and code, the year-by-year table
copied from the job's "leads", the 42 candidate-years with 0 linked, the post-hoc reading
marked as not pre-registered, and the limits. Reads text only.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))

# Copied from job xwpudl-v1's xwpudl.json "scores" (6 November 2026).
SCORES = {"G1": True, "P1": True, "P2": True, "P3": True, "P4": True, "P5": True}
PROBS = {"P1": "80%", "P2": "70%", "P3": "70%", "P4": "60%", "P5": "55%"}

# Copied from xwpudl.json "leads": persists per year 2018..2024; None = camd_gens_found false.
YEARS = (2018, 2019, 2020, 2021, 2022, 2023, 2024)
LEADS = {"Antelope Elk": (True, True, True, True, True, True, True),
         "Chalk Point": (True, True, True, None, None, True, True),
         "Glenarm": (True, True, True, True, True, True, True),
         "LEPA Unit No. 1": (True, True, True, True, True, True, True)}

# xwpudl.json "p4": 6 candidates x 7 years, 0 linked.
P4_CELLS, P4_LINKED = 42, 0


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class XwpudlResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/xwpudl.md")

    def test_headline(self):
        self.assertTrue(all(SCORES.values()))
        self.assertIn("**Gate G1 held, and all 5 predictions held.**", self.doc)
        self.assertIn("Result of pre-registration xwpudl-1 ([plan](xwpudl-plan.md), commit c8c1ae6",
                      self.doc)
        self.assertIn("made with AI agents working in MV2's name", self.doc)
        self.assertIn("no person has checked these results by hand", self.doc)

    def test_score_rows(self):
        self.assertIn("| G1 | gate | held |", self.doc)
        for p, prob in PROBS.items():
            word = "held" if SCORES[p] else "failed"
            self.assertIn("| %s | %s | %s |" % (p, prob, word), self.doc)
        self.assertNotIn("| failed |", self.doc)

    def test_year_table(self):
        for name, row in LEADS.items():
            cells = ["stands" if v else ("no row" if v is None else "does not stand")
                     for v in row]
            self.assertIn("| " + " | ".join(cells) + " |", self.doc)
            self.assertIn("| %s |" % name, self.doc)
        stands = sum(1 for row in LEADS.values() for v in row if v)
        none = sum(1 for row in LEADS.values() for v in row if v is None)
        self.assertEqual((stands, none), (26, 2))
        self.assertEqual(len(YEARS) * len(LEADS), 28)
        self.assertIn("26 of the 28 lead-years stand and the other 2 have no row", self.doc)

    def test_p4(self):
        self.assertEqual(P4_CELLS, 6 * len(YEARS))
        self.assertIn("all 42 candidate-years (6 candidate generators times 7 report years)",
                      self.doc)
        self.assertIn("0 of 42 linked", self.doc)
        self.assertIn("No row in any report year names EIA plant 58835 or 61890 at all.",
                      self.doc)

    def test_provenance(self):
        for text in ("md5 c2c184d2947fa3b176db2c561bacbe59",
                     "md5 63107679cc1cafb41b037b5640d79d1e",
                     "all 10 unit tests passed",
                     "190,240 bytes, md5 420d50a7e4d066d29eee909eab73d932, 44,833 rows",
                     "7,718,170 bytes, md5 6c4372366df319de1888d8fc6ea1ec0e, 667,073 rows",
                     "`sanity_elk_2024_persists: true`"):
            self.assertIn(text, self.doc)

    def test_post_hoc_and_limits(self):
        for text in ("## What else the rows show (read after scoring, not pre-registered)",
                     "CEMS peak 5.312 times its capacity",
                     "[xwdev-plan.md](xwdev-plan.md), id xwdev-1",
                     "PUDL's data is downloaded at run time and not stored here.",
                     "No person has checked the code or the results by hand."):
            self.assertIn(text, self.doc)


if __name__ == "__main__":
    unittest.main()
