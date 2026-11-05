"""Checks the left3 read section of docs/pudl-pr2.md against job left3-v1's output
(out/left3.json, copied below) and that it links the endrule-1 plan. Reads text only.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))

# From compete-results/left3-v1/out/left3.json: the key's last PUDL record (report month,
# operational_status_code, valid_until_date) and the September 2026 sheets that list it.
DIFF = {"67674/LUPE3": ("2026-06", "U", "2026-09-01", "Canceled or Postponed"),
        "67788/GRS10": ("2025-05", "L", "2026-09-01", "Canceled or Postponed"),
        "69144/PV1": ("2026-05", "V", "2026-09-01", "on no sheet")}
LEFT_BOTH = {"65399/U3": "2026-08-01", "65655/HECHQ": "2026-08-01",
             "66692/HOLLY": "2026-08-01", "66692/HOLY": "2026-08-01",
             "67660/MALAL": "2026-08-01", "68198/TRS": "2026-08-01",
             "68811/RIPLE": "2026-08-01"}
PUDL_MD5 = "2be6ac001022cf230f87dc70dc740496"
PUDL_ROWS = 233063
AUG_BYTES = 55901


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class Left3ReadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        doc = read("docs/pudl-pr2.md")
        head = "## The left3 read (5 November 2026, not pre-registered)"
        cls.doc = doc
        cls.sec = doc[doc.index(head):]

    def test_three_keys_rows(self):
        for key, (rep, status, end, where) in DIFF.items():
            self.assertIn("| %s | from report %s, status %s | %s | %s |"
                          % (key, rep, status, end, where), self.sec)

    def test_left_both(self):
        self.assertEqual(set(LEFT_BOTH.values()), {"2026-08-01"})
        self.assertIn("All %d keys that both routes count as \"left\" in September (%s) have a "
                      "last record ending 2026-08-01" % (len(LEFT_BOTH), ", ".join(LEFT_BOTH)),
                      self.sec)
        self.assertIn("all 7 are on the \"Canceled or Postponed\" sheet in September", self.sec)

    def test_provenance(self):
        self.assertIn("md5 %s, %s rows" % (PUDL_MD5, format(PUDL_ROWS, ",")), self.sec)
        self.assertIn("returned a %s-byte page that is not an xlsx file"
                      % format(AUG_BYTES, ","), self.sec)
        self.assertIn("`tools/left3/left3.py` 0.1.0", self.sec)
        self.assertIn("4c741eb77a5ccad5aca32ffe43f398af", self.sec)

    def test_cause_and_honesty(self):
        for text in ("one month past the entity's final report date",
                     "the first date it is *no longer* in force",
                     "MV2's reading of the end date, not PUDL's data",
                     "P3 is not re-scored.", "[endrule-1](endrule-plan.md)",
                     "nothing about it is posted on PUDL"):
            self.assertIn(text, self.sec)
        self.assertIn("P3 stays failed as scored.", self.doc)
        self.assertIn("**Both gates held and 3 of 4 predictions held; P3 failed.**", self.doc)


if __name__ == "__main__":
    unittest.main()
