"""Checks that docs/unitzero-plan.md describes what tools/unitzero/ runs: version, tables, the
gate and the bars. Reads every file as text, so it needs no pandas.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class UnitzeroPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/unitzero-plan.md")
        cls.code = read("tools/unitzero/unitzero.py")
        cls.tests = read("tools/unitzero/test_unitzero.py")

    def test_status_and_id(self):
        self.assertIn("Status: pre-registration, nothing run yet.", self.doc)
        self.assertIn("Pre-registration id: unitzero-1.", self.doc)
        self.assertIn("pre-registration id unitzero-1", self.code)

    def test_version(self):
        self.assertIn('VERSION = "0.1.0"', self.code)
        self.assertIn("`tools/unitzero/unitzero.py` 0.1.0", self.doc)

    def test_tables(self):
        for table in ("core_epa__assn_eia_epacamd", "core_epa__assn_eia_epacamd_subplant_ids",
                      "core_eia__entity_generators", "core_eia__entity_boilers"):
            self.assertIn('"%s"' % table, self.code)
            self.assertIn("`%s`" % table, self.doc)
        self.assertIn("core_epacems__hourly_emissions.parquet", self.code)
        self.assertIn("`core_epacems__hourly_emissions`", self.doc)
        self.assertIn("USEPA/camd-eia-crosswalk/master/epa_eia_crosswalk.csv", self.code)
        for col in ("CAMD_PLANT_ID", "CAMD_UNIT_ID", "CAMD_GENERATOR_ID", "EIA_PLANT_ID",
                    "EIA_GENERATOR_ID", "EIA_BOILER_ID"):
            self.assertIn('"%s"' % col, self.code)
            self.assertIn("`%s`" % col, self.doc)

    def test_constants_match_bars(self):
        for text in ("GATE_MIN_CEMS_PLANTS = 1000", "P5_ROW_SHARE = 0.001"):
            self.assertIn(text, self.code)
        for text in ("**Gate G1:**", "**P1 (40%):**", "**P2 (35%):**", "**P3 (75%):**",
                     "**P4 (55%):**", "**P5 (85%):**", "1,000 or more distinct",
                     "fewer than 0.1% of all CEMS"):
            self.assertIn(text, self.doc)

    def test_scoring_lines(self):
        for text in ('"P1": epa_unit["zero"] + epa_unit["multi_zero"] >= 1',
                     '"P2": m["cems"]["empty_unit_rows"] >= 1',
                     '"P5": m["cems"]["empty_unit_rows"] < P5_ROW_SHARE * m["cems"]["rows_scanned"]'):
            self.assertIn(text, self.code)
        self.assertIn('["generator_id"]["empty"] == 0', self.code)
        self.assertIn('["boiler_id"]["empty"] == 0', self.code)
        self.assertIn('m["epa_crosswalk_collisions"]["CAMD_UNIT_ID"]', self.code)
        self.assertIn('m["epa_crosswalk_collisions"]["EIA_GENERATOR_ID"]', self.code)

    def test_rules_described_match_code(self):
        self.assertIn('_HELPER_MATCH = re.compile(r"^0+\\d+$")', self.code)
        self.assertIn('re.sub(r"^0+", "", value)', self.code)
        self.assertIn('value.lstrip("0")', self.code)
        for text in ("`^0+\\d+$`", "`^0+`", '"0" stays "0"', '"00" and "000" become'):
            self.assertIn(text, self.doc)
        for name in ("def test_pudl_helper_matches_pudl_unit_test_cases",
                     "def test_pudl_helper_all_zero_ids", "def test_cems_strip",
                     "def test_the_two_disagree_only_on_single_zero", "def test_collisions",
                     "def test_gate"):
            self.assertIn(name, self.tests)

    def test_nothing_of_pudl_stored(self):
        line = "PUDL's data (CC BY 4.0) is downloaded at run time and not stored here."
        self.assertIn(line, self.doc)
        self.assertIn(line, self.code)
        for text in (self.code, self.tests):
            self.assertIn("Apache-2.0", text)
        self.assertIn("No person has checked these results by hand.", self.doc)


if __name__ == "__main__":
    unittest.main()
