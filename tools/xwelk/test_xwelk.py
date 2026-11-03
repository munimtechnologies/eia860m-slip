"""Unit tests for xwelk.py's pure helpers (no network, no polars).

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.)."""

import datetime
import unittest

import xwelk

CSV = (
    "SEQUENCE_NUMBER,CAMD_PLANT_ID,CAMD_UNIT_ID,EIA_PLANT_ID,EIA_GENERATOR_ID,MATCH_TYPE_GEN,"
    "MATCH_TYPE_BOILER\n"
    "1,3,1,3,1,exact,\n"
    "2,57865,1,57865,E01,step 1d,\n"
    "3,57865,2,57865,E02,step 1d,\n"
    "4,58835,X,58835,ELK1,exact,b\n"
    "5,100,9,200,9,exact,\n"
)


class EpaRowsTests(unittest.TestCase):
    def test_keeps_rows_of_either_plant(self):
        r = xwelk.epa_rows(CSV)
        self.assertEqual(r["rows"], 5)
        self.assertEqual([x["SEQUENCE_NUMBER"] for x in r["plant_rows"]], ["2", "3", "4"])
        self.assertEqual(r["header"][1], "CAMD_PLANT_ID")

    def test_match_type_counts(self):
        r = xwelk.epa_rows(CSV)
        self.assertEqual(r["match_type_counts"]["MATCH_TYPE_GEN"], {"exact": 3, "step 1d": 2})
        self.assertEqual(r["match_type_counts"]["MATCH_TYPE_BOILER"], {"": 4, "b": 1})

    def test_eia_side_alone_is_enough(self):
        text = "CAMD_PLANT_ID,EIA_PLANT_ID\n999,58835\n999,1\n"
        self.assertEqual(len(xwelk.epa_rows(text)["plant_rows"]), 1)


class YearlySumTests(unittest.TestCase):
    def test_sums_by_generator_and_year(self):
        rows = [
            {"plant_id_eia": 58835, "generator_id": "1", "report_date": datetime.date(2024, 1, 1),
             "net_generation_mwh": 10.0},
            {"plant_id_eia": 58835, "generator_id": "1", "report_date": datetime.date(2024, 2, 1),
             "net_generation_mwh": 5.5},
            {"plant_id_eia": 58835, "generator_id": "1", "report_date": "2023-12-01",
             "net_generation_mwh": 1.0},
            {"plant_id_eia": 57865, "generator_id": "E01",
             "report_date": datetime.date(2024, 3, 1), "net_generation_mwh": None},
            {"plant_id_eia": 57865, "generator_id": "E01", "report_date": None,
             "net_generation_mwh": 7.0},
        ]
        out = xwelk.yearly_sum(rows, ("plant_id_eia", "generator_id"), "report_date",
                               "net_generation_mwh")
        self.assertEqual(out, [
            {"plant_id_eia": 57865, "generator_id": "E01", "year": 2024,
             "net_generation_mwh": None},
            {"plant_id_eia": 58835, "generator_id": "1", "year": 2023, "net_generation_mwh": 1.0},
            {"plant_id_eia": 58835, "generator_id": "1", "year": 2024, "net_generation_mwh": 15.5},
        ])

    def test_constants(self):
        self.assertEqual(xwelk.PLANTS, (57865, 58835))
        self.assertTrue(xwelk.EPA_CSV.endswith(
            "/3c7d6724cddee38dfb6a06debca732c33a227ed6/epa_eia_crosswalk.csv"))


if __name__ == "__main__":
    unittest.main()
