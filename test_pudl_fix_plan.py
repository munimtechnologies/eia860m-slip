"""Checks that docs/pudl-fix-plan.md describes what tools/pudl-fix/check_fix.py and
keep_changes.py run: versions, pinned PUDL commits, the step replaced and the frame counts.
Reads all three as text, so it needs no pandas.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SHA_OLD = "af08a70361fb09e0bf3b509778317b7c8873b69f"
SHA_NEW = "4d3366b30d05a4c1c13cd8e88ba9b7b2f9ea6db2"


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class PudlFixPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/pudl-fix-plan.md")
        cls.check = read("tools/pudl-fix/check_fix.py")
        cls.fix = read("tools/pudl-fix/keep_changes.py")

    def test_status_and_id(self):
        self.assertIn("Status: pre-registration, nothing scored yet.", self.doc)
        self.assertIn("Pre-registration id: pudl-fix-1.", self.doc)

    def test_versions_and_commits(self):
        self.assertIn('VERSION = "0.1.0"', self.check)
        self.assertIn('VERSION = "0.1.0"', self.fix)
        self.assertIn("`tools/pudl-fix/keep_changes.py` 0.1.0", self.doc)
        self.assertIn("`tools/pudl-fix/check_fix.py` 0.1.0", self.doc)
        for sha in (SHA_OLD, SHA_NEW):
            self.assertIn('"%s"' % sha, self.check)
            self.assertIn(sha, self.doc)

    def test_step_replaced(self):
        self.assertIn(').drop_duplicates(\n        subset=[c for c in df_all if c != "report_date"],',
                      self.fix)
        self.assertIn("df_changelog = keep_changes(", self.fix)
        self.assertIn("one `drop_duplicates` step", self.doc)

    def test_frame_counts(self):
        self.assertIn("def check_random(orig, patched, n_each=100, seed=20261029):", self.check)
        self.assertIn('[("tall", 0)] * (2 * n_each)', self.check)
        self.assertIn("def bench_frame(n_series=20000, n_months=50, seed=7):", self.check)
        self.assertIn("400 seeded random frames", self.doc)
        self.assertIn("1,000,000 synthetic generator-months (20,000 generators over 50 months)",
                      self.doc)

    def test_no_pudl_code_stored(self):
        self.assertIn("PUDL's code (MIT) is downloaded at run time and not stored here.", self.doc)
        self.assertNotIn("def make_changelog", self.check)
        self.assertNotIn("def make_changelog", self.fix)


if __name__ == "__main__":
    unittest.main()
