"""Checks the dated update at the end of docs/pudl-pr.md: it is added after the scored text,
names the commit it reports and says nothing was re-run. Reads text only.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
HEADING = "## Update, 31 October 2026: the pull request now ends every last record one month later"


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class PudlPrUpdateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/pudl-pr.md")

    def test_update_comes_after_the_scored_text(self):
        self.assertEqual(self.doc.count(HEADING), 1)
        self.assertGreater(self.doc.index(HEADING), self.doc.index("## Limits"))
        self.assertIn("Both gates held and 10 of 10 predictions held.",
                      self.doc[:self.doc.index(HEADING)])

    def test_update_names_the_commit(self):
        update = self.doc[self.doc.index(HEADING):]
        for text in ("commit 925a120", "End every changelog series on the same date",
                     "was not valid in the final month it was actually observed",
                     "missed every generator whose last value had not just changed",
                     "`test_make_changelog_last_records_all_end_on_the_same_date`",
                     "https://github.com/catalyst-cooperative/pudl/issues/5738",
                     "head is now c91b4aa",
                     "nothing here has been re-run on the new head yet"):
            self.assertIn(text, update)


if __name__ == "__main__":
    unittest.main()
