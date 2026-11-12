"""Checks that docs/spboil-plan.md describes what tools/spboil/ runs: version, tables, the gate
and the bars. Reads every file as text, so it needs no pandas.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class SpboilPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/spboil-plan.md")
        cls.code = read("tools/spboil/spboil.py")
        cls.tests = read("tools/spboil/test_spboil.py")

    def test_status_and_id(self):
        self.assertIn("Status: pre-registration, nothing run yet.", self.doc)
        self.assertIn("Pre-registration id: spboil-1.", self.doc)
        self.assertIn("pre-registration id spboil-1", self.code)

    def test_version(self):
        self.assertIn('VERSION = "0.1.0"', self.code)
        self.assertIn("`tools/spboil/spboil.py` 0.1.0", self.doc)

    def test_tables(self):
        for table in ("core_epa__assn_eia_epacamd", "core_epa__assn_eia_epacamd_subplant_ids",
                      "core_eia860__assn_boiler_generator", "core_eia860__scd_generators"):
            self.assertIn('"%s"' % table, self.code)
            self.assertIn("`%s`" % table, self.doc)

    def test_constants_match_bars(self):
        for text in ("MANUAL_PLANT = 1391", "WATCH_PLANT = 52151", "GATE_PLANT_SHARE = 0.99",
                     "GATE_ROW_TOL = 0.01", "P2_SHARE = 0.02", "P3_EXTRA = 5",
                     "P4_SHARE = 0.01", "P5_NULL_SHARE = 0.5"):
            self.assertIn(text, self.code)
        for text in ("**Gate G1:**", "**P1 (80%):**", "**P2 (75%):**", "**P3 (70%):**",
                     "**P4 (50%):**", "**P5 (85%):**", "at 99% or more of its", "within 1%",
                     "fewer than 2% of plants with a crosswalk match", "no more than 5 plants",
                     "1% or more of the rebuilt table", "more than half of the rows",
                     "plant 1391 as one subplant", "Plant 52151"):
            self.assertIn(text, self.doc)

    def test_scoring_lines(self):
        for text in ('"P1": m["xw"]["plants_changed"] >= 1',
                     '"P2": m["xw"]["plants_changed"] < P2_SHARE * m["plants_with_crosswalk_match"]',
                     '"P3": m["xw_bga"]["plants_changed"] <= m["xw"]["plants_changed"] + P3_EXTRA',
                     '"P4": m["step1"]["extra_rows"] >= P4_SHARE * m["rebuild_rows"]',
                     '"P5": m["step1"]["null_boiler_share"] > P5_NULL_SHARE'):
            self.assertIn(text, self.code)

    def test_unit_tests_cover_both_steps(self):
        for name in ("def test_step1_extra_row_and_repeated_pair",
                     "def test_step2_xw_joins_shared_boiler", "def test_step2_bga_adds_generator_c",
                     "def test_unit_id_pudl_already_links", "def test_gate_catches_a_different_partition"):
            self.assertIn(name, self.tests)

    def test_nothing_of_pudl_stored(self):
        line = "PUDL's data (CC BY 4.0) is downloaded at run time and not stored here."
        self.assertIn(line, self.doc)
        self.assertIn(line.replace("PUDL's data", "PUDL's data"), self.code.replace("\n", " "))
        for text in (self.code, self.tests):
            self.assertIn("Apache-2.0", text)
        self.assertIn("No person has checked these results by hand.", self.doc)


if __name__ == "__main__":
    unittest.main()
