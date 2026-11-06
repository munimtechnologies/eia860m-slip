"""Checks that docs/step1d-look.md reports job step1d-look-v1 honestly: marked descriptive and
not pre-registered, the counts by group copied from the job's summary, the six far-apart
step-1d links with their one unlinked closer candidate each, and the limits. Reads text only.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))

# Copied from job step1d-look-v1's step1d_look.json "summary" (6 November 2026):
# group: (n, linked_gen_in_sep_2026, with_unlinked_closer, with_same_id_same_state)
SUMMARY = {"1d far apart (r >= 1.5)": (6, 6, 6, 5),
           "1d letters differ (r < 1.5)": (34, 34, 1, 12),
           "1b/1c far apart": (0, 0, 0, 0),
           "1a far apart": (24, 24, 11, 20),
           "Manual Match far apart": (6, 6, 4, 5)}

# (CAMD MW, candidate MW, ratio shown in the doc)
CANDIDATES = [(202.0, 199.8, "1.011"), (93.0, 94.0, "1.011"), (16.78, 16.0, "1.049"),
              (17.0, 17.1, "1.006")]


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class Step1dLookResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/step1d-look.md")

    def test_marked_descriptive(self):
        self.assertIn("**This look is descriptive, not pre-registered: it sets no bars and "
                      "scores nothing.**", self.doc)
        self.assertIn("Each is a lead for a person to check, not a finding.", self.doc)
        self.assertIn("made with AI agents working in MV2's name", self.doc)
        self.assertIn("no person has checked these results by hand", self.doc)
        self.assertIn("[step1d.md](step1d.md)", self.doc)

    def test_group_table(self):
        for name, (n, linked, unl, same) in SUMMARY.items():
            self.assertIn("| %s | %d | %d | %d | %d |" % (name, n, linked, unl, same), self.doc)
        self.assertEqual(sum(v[0] for v in SUMMARY.values()), 70)
        self.assertIn("in the four non-empty groups (70 links)", self.doc)
        self.assertEqual(SUMMARY["1d letters differ (r < 1.5)"][0] - 1, 33)
        self.assertIn("The other 33 have", self.doc)

    def test_six_links(self):
        for text in ("| 1 / ELK1 | 202 | 57865/E01, 9.3 MW, IC | 58835/ELK1 Elk Station, 199.8 MW, "
                     "GT, operating | 1.011 |",
                     "| SMECO / SGT1 | 93 | 1571/GT1, 16 MW, GT | 61890/SGT1 NRG Chalk Point CT, "
                     "94 MW, GT, operating | 1.011 |",
                     "| GT5 / STG5 | 16.78 | 422/GT5, 71 MW, CT | 422/ST1 Glenarm, 16 MW, CA, "
                     "operating | 1.049 |",
                     "| CC01 / STG1 | 17 | 58478/LEPA1, 57 MW, CT | 58478/LEPA2 LEPA Unit No. 1, "
                     "17.1 MW, CA, operating | 1.006 |"):
            self.assertIn(text, self.doc)
        self.assertEqual(self.doc.count("| 57865 Antelope Elk Energy Center, TX |"), 3)
        for camd, cand, shown in CANDIDATES:
            r = max(camd, cand) / min(camd, cand)
            # Compare with a tolerance: 16.78 / 16 = 1.04875 sits on a rounding boundary.
            self.assertAlmostEqual(r, float(shown), delta=0.0006)
            self.assertIn("| %s |" % shown, self.doc)
            self.assertLess(r, 1.05)

    def test_manual_sums(self):
        self.assertEqual(136 + 136, 272)
        self.assertAlmostEqual(27.5 + 27.5, 55.0)
        self.assertIn("(272 against 265 MW; 55 against 60.4 MW)", self.doc)

    def test_provenance_and_limits(self):
        for text in ("3c7d6724cddee38dfb6a06debca732c33a227ed6",
                     "md5 b7ec4b014ab66c2926f77ea86fa1ea16, 6,935 rows",
                     "md5 4c741eb77a5ccad5aca32ffe43f398af",
                     "md5 494a198670cbf7f6449327838be9b1c4",
                     "its 8 unit tests passed",
                     "`sanity_elk1_finds_58835: true`",
                     "EPA's file and EIA's workbook are downloaded at run time and not stored "
                     "here.",
                     "No person has checked the code or the results by hand."):
            self.assertIn(text, self.doc)


if __name__ == "__main__":
    unittest.main()
