"""Checks that docs/subplant-amb-plan.md describes what tools/subplant-amb/ runs: version, the
reused tool, the classes, the gates and the bars. Reads every file as text, so it needs no pandas.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class SubplantAmbPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/subplant-amb-plan.md")
        cls.code = read("tools/subplant-amb/subplant_amb.py")
        cls.tests = read("tools/subplant-amb/test_subplant_amb.py")

    def test_status_and_id(self):
        self.assertIn("Status: pre-registration, nothing run yet.", self.doc)
        self.assertIn("Pre-registration id: subplant-amb-1.", self.doc)

    def test_versions(self):
        self.assertIn('VERSION = "0.1.0"', self.code)
        self.assertIn('SG_VERSION = "0.1.0"', self.code)
        self.assertIn('SG_MD5 = "276817f5826157f3f2dc6a94f94c730f"', self.code)
        self.assertIn("`tools/subplant-amb/subplant_amb.py` 0.1.0", self.doc)
        self.assertIn("`tools/subplant-gap/subplant_gap.py` 0.1.0 unchanged (md5 "
                      "276817f5826157f3f2dc6a94f94c730f", self.doc)

    def test_tables(self):
        for table in ("core_epa__assn_eia_epacamd", "core_epa__assn_eia_epacamd_subplant_ids",
                      "core_eia860__assn_boiler_generator", "core_eia923__monthly_boiler_fuel"):
            self.assertIn("`%s`" % table, self.doc)

    def test_rule(self):
        self.assertIn('CLASSES = ("covered", "single", "name", "unresolved")', self.code)
        self.assertIn('re.sub(r"[^A-Z0-9]", "", str(x).upper()).lstrip("0")', self.code)
        self.assertIn("cands = [c for c in (mine or sub[key]) if (r.plant_id_eia, c) not in covered]",
                      self.code)
        for text in ("**covered** if no candidate is left", "**single** if exactly one candidate",
                     "**name** if exactly one candidate has the same normalized id",
                     "otherwise **unresolved**", "(`ct-01` and `CT1` match; `HRSG1` and `CT1` do not)",
                     "The **main year** is 2024."):
            self.assertIn(text, self.doc)
        self.assertIn("MAIN_YEAR = 2024", self.code)

    def test_gates(self):
        self.assertIn("G1_AMBIGUOUS = (580, 625)", self.code)
        self.assertIn("G1_GAP_PLANTS = (6, 10)", self.code)
        for text in ("**Gate G0:**", "**Gate G1:**", "between 580 and 625 ambiguous subplants",
                     "between 6 and 10 strict gap plants"):
            self.assertIn(text, self.doc)

    def test_bars(self):
        for text in ("**P1 (60%):**", "**P2 (65%):**", "**P3 (55%):**", "**P4 (50%):**",
                     "at least half of the 2024 ambiguous subplants are resolved",
                     "at least 60% of the 2024 ambiguous rows", "under 1% of their linked boilers'",
                     "at least 100 ambiguous rows"):
            self.assertIn(text, self.doc)
        for text in ('m["resolved_subplants"] * 2 >= m["ambiguous_subplants"]',
                     'm["rows_generator_without_boiler"] >= 0.6 * m["rows"]',
                     'm["resolved_gap_mmbtu"] < 0.01 * m["resolved_linked_mmbtu"]',
                     'm["rows_by_class"]["name"] >= 100'):
            self.assertIn(text, self.code)

    def test_unit_tests_cover_each_class(self):
        for text in ("def test_classes", "def test_matched_boiler_is_not_a_candidate",
                     "def test_revise", '("unresolved", None, "subplant")',
                     '("covered", None, "generator")'):
            self.assertIn(text, self.tests)

    def test_nothing_of_pudl_stored(self):
        self.assertIn("PUDL's data (CC BY 4.0) is downloaded at run time and not stored here.",
                      self.doc)
        self.assertIn("PUDL's data (CC BY 4.0) is downloaded at run time and not stored here.",
                      self.code)
        for text in (self.code, self.tests):
            self.assertIn("Apache-2.0", text)


if __name__ == "__main__":
    unittest.main()
