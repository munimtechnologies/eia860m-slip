"""Checks that docs/subplant-amb2-plan.md describes what tools/subplant-amb2/ runs: version, the
reused tools, the rule, the gates and the bars. Reads every file as text, so it needs no pandas.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class SubplantAmb2PlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/subplant-amb2-plan.md")
        cls.code = read("tools/subplant-amb2/subplant_amb2.py")
        cls.tests = read("tools/subplant-amb2/test_subplant_amb2.py")

    def test_status_and_id(self):
        self.assertIn("Status: pre-registration, nothing run yet.", self.doc)
        self.assertIn("Pre-registration id: subplant-amb-2.", self.doc)

    def test_versions(self):
        self.assertIn('VERSION = "0.1.0"', self.code)
        self.assertIn('SA_VERSION = "0.1.0"', self.code)
        self.assertIn('SA_MD5 = "2dec70ebe46e81d6fb2a1500f0e7e632"', self.code)
        self.assertIn("`tools/subplant-amb2/subplant_amb2.py` 0.1.0", self.doc)
        self.assertIn("`tools/subplant-amb/subplant_amb.py` 0.1.0 unchanged (md5 "
                      "2dec70ebe46e81d6fb2a1500f0e7e632)", self.doc)
        self.assertIn("`tools/subplant-gap/subplant_gap.py` 0.1.0 (md5 "
                      "276817f5826157f3f2dc6a94f94c730f)", self.doc)

    def test_rule(self):
        self.assertIn('CLASSES = ("covered", "single", "name", "unit", "unresolved")', self.code)
        self.assertIn('out.loc[hit, "class"] = "unit"', self.code)
        self.assertIn('named = xy[xy["boiler_id"].notna()]', self.code)
        self.assertIn('inferred = rows[rows["boiler_id"].notna()]', self.code)
        for text in ("An EPA unit **has a boiler** if a year-Y crosswalk row names a `boiler_id`",
                     "moves to a fifth class, **unit**. It infers no boiler.",
                     "The **main year** is 2024."):
            self.assertIn(text, self.doc)
        self.assertIn("MAIN_YEAR = 2024", self.code)

    def test_gates(self):
        self.assertIn("G1_UNRESOLVED = (400, 470)", self.code)
        self.assertIn("G1_RESOLVED = (420, 465)", self.code)
        for text in ("**Gate G0:**", "**Gate G1:**", "between 400 and 470 unresolved rows",
                     "between 420 and 465 resolved subplants"):
            self.assertIn(text, self.doc)

    def test_bars(self):
        for text in ("**Q1 (60%):**", "**Q2 (55%):**", "**Q3 (60%):**", "**Q4 (55%):**",
                     "at least half of the first rule's 2024 unresolved rows move to the class unit",
                     "at most 100 of the 2024 ambiguous subplants are still unresolved",
                     "the gap is under 10% of their linked boilers' heat input",
                     'whose normalized id contains "HRSG"'):
            self.assertIn(text, self.doc)
        for text in ('m["rows_by_class"]["unit"] * 2 >= m["unresolved_rule1"]',
                     'm["ambiguous_after_rule2"] <= 100',
                     'm["rule2_gap_mmbtu"] < 0.10 * m["rule2_linked_mmbtu"]',
                     'm["rule2_gap_hrsg_mmbtu"] * 2 >= m["rule2_gap_mmbtu"]',
                     '"HRSG" in sa.norm(x)'):
            self.assertIn(text, self.code)

    def test_unit_tests_cover_the_rule(self):
        for text in ("def test_rule1_unchanged", "def test_rule2_classes", "def test_metrics",
                     '(17, "1A", "ST1"): "unit"', '(18, "U1", "G2"): "unit"',
                     '(12, "CT1", "GT1"): "unresolved"', '(11, "U1", "G1"): "single"'):
            self.assertIn(text, self.tests)

    def test_seen_before_and_nothing_stored(self):
        self.assertIn("What we had seen before writing this:", self.doc)
        self.assertIn("PUDL's data (CC BY 4.0) is downloaded at run time and not stored here.",
                      self.doc)
        self.assertIn("PUDL's data (CC BY 4.0) is downloaded at run time and not stored here.",
                      self.code)
        for text in (self.code, self.tests):
            self.assertIn("Apache-2.0", text)


if __name__ == "__main__":
    unittest.main()
