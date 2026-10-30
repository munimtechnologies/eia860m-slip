"""Checks that docs/subplant-gap-plan.md describes what tools/subplant-gap/ runs: version,
tables, years, the gate and the bars. Reads every file as text, so it needs no pandas.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class SubplantGapPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/subplant-gap-plan.md")
        cls.code = read("tools/subplant-gap/subplant_gap.py")
        cls.tests = read("tools/subplant-gap/test_subplant_gap.py")

    def test_status_and_id(self):
        self.assertIn("Status: pre-registration, nothing run yet.", self.doc)
        self.assertIn("Pre-registration id: subplant-gap-1.", self.doc)

    def test_version(self):
        self.assertIn('VERSION = "0.1.0"', self.code)
        self.assertIn("`tools/subplant-gap/subplant_gap.py` 0.1.0", self.doc)

    def test_tables(self):
        for table in ("core_epa__assn_eia_epacamd", "core_epa__assn_eia_epacamd_subplant_ids",
                      "core_eia860__assn_boiler_generator", "core_eia923__monthly_boiler_fuel"):
            self.assertIn('"%s"' % table, self.code)
            self.assertIn("`%s`" % table, self.doc)

    def test_years_and_gate(self):
        for text in ("MAIN_YEAR = 2024", "GATE_YEAR = 2023", "GATE_PLANT = 50472",
                     'GATE_GAP = ("BLR3", "BLR4")', 'GATE_COVERED = ("BLR1", "BLR2")',
                     "GATE_HEAT = (7_000_000, 9_500_000)", 'MSW_CODES = ("MSW", "MSB", "MSN")'):
            self.assertIn(text, self.code)
        for text in ("The **main year** is 2024.", "in 2023, at plant 50472, BLR3 and BLR4 are gap "
                     "boilers, BLR1 and BLR2 are matched", "between 7.0 and 9.5 million MMBtu",
                     "(MSW, MSB or MSN)"):
            self.assertIn(text, self.doc)

    def test_rule(self):
        self.assertIn('d["fuel_consumed_units"].fillna(0) * d["fuel_mmbtu_per_unit"].fillna(0)',
                      self.code)
        self.assertIn('b["gap"] = ~b["covered"] & (b["mmbtu"] > 0)', self.code)
        self.assertIn('xy["boiler_id"].isna() & xy["generator_id"].notna()', self.code)
        self.assertIn('ss["gap_share"].notna() & (ss["gap_share"] > 0.5)', self.code)
        self.assertIn("`fuel_consumed_units` times `fuel_mmbtu_per_unit`", self.doc)
        self.assertIn("with a blank `boiler_id`", self.doc)

    def test_bars(self):
        for text in ("**Gate G0:**", "**Gate G1:**", "**P1 (75%):**", "**P2 (70%):**",
                     "**P3 (60%):**", "**P4 (70%):**", "at least 20 plants",
                     "at least 25 million MMBtu", "at least 10 strict CEMS subplants",
                     "at least 3 have a largest gap boiler"):
            self.assertIn(text, self.doc)
        for text in ('s["gap_plants"] >= 20', 's["gap_mmbtu"] >= 25_000_000',
                     's["subplants_gap_share_over_half"] >= 10',
                     's["subplants_gap_share_over_half_not_msw"] >= 3'):
            self.assertIn(text, self.code)

    def test_unit_tests_cover_issue_pattern(self):
        self.assertIn("def test_issue_5681_pattern", self.tests)
        self.assertIn("def test_ambiguous", self.tests)
        self.assertIn("def test_zero_heat_is_not_a_gap", self.tests)

    def test_nothing_of_pudl_stored(self):
        self.assertIn("PUDL's data (CC BY 4.0) is downloaded at run time and not stored here.",
                      self.doc)
        self.assertIn("PUDL's data (CC BY 4.0) is downloaded at run time and not stored here.",
                      self.code)
        for text in (self.code, self.tests):
            self.assertIn("Apache-2.0", text)


if __name__ == "__main__":
    unittest.main()
