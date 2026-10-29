"""Checks that docs/pudl-make-changelog-check.md reports the cases and pinned PUDL commit that
tools/pudl-check/check_changelog.py runs. Reads both as text, so it needs no pandas.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SHA = "af08a70361fb09e0bf3b509778317b7c8873b69f"


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class PudlCheckDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/pudl-make-changelog-check.md")
        cls.code = read("tools/pudl-check/check_changelog.py")

    def test_status_and_commit(self):
        self.assertIn("Status: reproduction, no prediction tested.", self.doc)
        self.assertIn("at commit %s" % SHA, self.doc)
        self.assertIn("md5 2810fbaba0ea8e87ec560342b3f69f79", self.doc)
        self.assertIn('VERSION = "0.1.0"', self.code)
        self.assertIn("check_changelog.py` 0.1.0", self.doc)

    def test_cases_match_code(self):
        self.assertIn('"return": (["OP", "OA", "OP"], [0, 1, 2]),', self.code)
        self.assertIn('"no_return": (["OP", "OA", "SB"], [0, 1, 2]),', self.code)
        self.assertIn('"repeat": (["OP", "OP", "OA"], [0, 2]),', self.code)
        self.assertIn('DATES = ["2026-01-01", "2026-02-01", "2026-03-01"]', self.code)
        self.assertIn("| OP, OA, OP | Jan, Feb | Jan, Feb, Mar |", self.doc)
        self.assertIn("| OP, OA, SB | Jan, Feb, Mar | Jan, Feb, Mar |", self.doc)
        self.assertIn("| OP, OP, OA | Jan, Mar | Jan, Mar |", self.doc)

    def test_idx_and_limits(self):
        self.assertIn('IDX = ["plant_id_eia", "generator_id", "report_date"]', self.code)
        self.assertIn('idx `["plant_id_eia", "generator_id", "report_date"]`', self.doc)
        self.assertIn("PUDL's code (MIT) is not stored in this repository.", self.doc)
        self.assertIn("no person has checked them by hand", self.doc)


if __name__ == "__main__":
    unittest.main()
