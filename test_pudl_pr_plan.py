"""Checks that docs/pudl-pr-plan.md describes what tools/pudl-pr/pr_check.py runs: version,
pinned commits, the nightly table and the bars. Reads both as text, so it needs no pandas.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SHA_PR = "c98ea31c5d7401ca21d47028d6cfda1a8322b856"
SHA_MAIN = "4d3366b30d05a4c1c13cd8e88ba9b7b2f9ea6db2"


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class PudlPrPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/pudl-pr-plan.md")
        cls.code = read("tools/pudl-pr/pr_check.py")
        cls.pinned = read("tools/pudl-pr/get_pinned2.py")
        cls.check_fix = read("tools/pudl-fix/check_fix.py")

    def test_status_and_id(self):
        self.assertIn("Status: pre-registration, nothing run yet.", self.doc)
        self.assertIn("Pre-registration id: pudl-pr-1.", self.doc)

    def test_version_and_commits(self):
        self.assertIn('VERSION = "0.1.0"', self.code)
        self.assertIn("`tools/pudl-pr/pr_check.py` 0.1.0", self.doc)
        self.assertIn('SHA_PR = "%s"' % SHA_PR, self.code)
        self.assertIn(SHA_PR, self.doc)
        self.assertIn('SHA_NEW = "%s"' % SHA_MAIN, self.check_fix)
        self.assertIn("SHA_MAIN = cf.SHA_NEW", self.code)
        self.assertIn(SHA_MAIN, self.doc)

    def test_pinned_tools(self):
        for text in ('"840ac280dd1a7d70d4124bc405f7c7a3ab4e39d9", "check_fix.py"',
                     '"a8926e1fee5a7c8ec6fac9b74489457d546973fc", "check_fix2.py"',
                     '"5054a0486fc87ea1a1d789b7a2a78c96"',
                     '"7778e066becebc113379a7bde29a07ff"'):
            self.assertIn(text, self.pinned)
        self.assertIn("`check_fix.py` 0.1.0 (840ac28)", self.doc)
        self.assertIn("`check_fix2.py` 0.2.0 (a8926e1)", self.doc)

    def test_nightly_table(self):
        self.assertIn('"core_eia860m__changelog_generators.parquet"', self.code)
        self.assertIn("nightly `core_eia860m__changelog_generators`", self.doc)

    def test_bars(self):
        for text in ("**Gate:**", "**Q1 (95%):**", "**Q2 (95%):**", "**Q3 (90%):**",
                     "**Q4 (85%):**", "**Q5 (80%):**", "**Q6 (90%):**", "**Q7 (95%):**",
                     "**S1 (90%):**", "**Nightly gate:**", "**L1 (85%):**", "**L2 (90%):**"):
            self.assertIn(text, self.doc)
        self.assertIn("the PR keeps 38,229 records", self.doc)
        for case in ('"unchanged": ["OP", "OP", "OP"]', '"changed_middle": ["OP", "OA", "OA"]',
                     '"changed_last": ["OP", "OA", "OP"]'):
            self.assertIn(case, self.code)
        self.assertIn('"generators_covered_on_last_date"', self.code)
        self.assertIn('"L1_share"', self.code)

    def test_nothing_of_pudl_stored(self):
        self.assertIn("PUDL's code (MIT) and data (CC BY 4.0) are downloaded at run time "
                      "and not stored here.", self.doc)
        self.assertNotIn("def make_changelog", self.code)


if __name__ == "__main__":
    unittest.main()
