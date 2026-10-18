"""Tests for spot (MV2 of Munim, Inc.; made with AI agents). Apache-2.0."""

import os
import tempfile
import unittest

import pandas as pd

import spot


class Select(unittest.TestCase):
    def test_picks_named_generators_in_report_order(self):
        df = pd.DataFrame({
            "plant_id_eia": [65855, 65855, 65855, 1],
            "generator_id": ["TE1PV", " TE1PV", "OTHER", "TE1PV"],
            "report_date": ["2026-02-01", "2025-12-01", "2025-12-01", "2025-12-01"],
            "capacity_mw": [644.8, 836.8, 5.0, 1.0],
        })
        rows = spot.select(df, (("65855", "TE1PV"),))
        self.assertEqual(list(rows["capacity_mw"]), [836.8, 644.8])

    def test_render_names_each_generator(self):
        df = pd.DataFrame({"plant_id_eia": [67123], "generator_id": ["MISII"],
                           "report_date": ["2025-12-01"], "capacity_mw": [331.6]})
        md = spot.render(spot.select(df))
        self.assertIn("## 67123/MISII", md)
        self.assertIn("331.6", md)
        self.assertIn("No plant name column in this file.", md)

    def test_render_empty(self):
        df = pd.DataFrame({"plant_id_eia": [1], "generator_id": ["X"], "report_date": ["2025-12-01"]})
        self.assertIn("No records found.", spot.render(spot.select(df)))


class ByName(unittest.TestCase):
    def test_no_name_column(self):
        df = pd.DataFrame({"plant_id_eia": [1], "generator_id": ["X"], "report_date": ["2025-12-01"]})
        self.assertIsNone(spot.by_name(df))

    def test_matches_every_record_of_a_named_plant(self):
        df = pd.DataFrame({
            "plant_id_eia": [70001, 70001, 70001, 70002],
            "generator_id": ["BESS1", "BESS1", "PV1", "G1"],
            "plant_name_eia": ["Tehuacana Creek BESS", "Tehuacana Creek BESS", "Tehuacana Creek BESS", "Other"],
            "report_date": ["2026-02-01", "2025-12-01", "2025-12-01", "2025-12-01"],
            "summer_capacity_mw": [418.0, 418.0, 5.0, 9.0],
        })
        named = spot.by_name(df)
        self.assertEqual(list(named["_key"]), ["70001/BESS1", "70001/BESS1", "70001/PV1"])
        self.assertEqual(list(named["report_date"])[:2], ["2025-12-01", "2026-02-01"])
        md = spot.render(spot.select(df), ["plant_id_eia"], named)
        self.assertIn("## Battery plants by name", md)
        self.assertIn("Tehuacana Creek BESS", md)


class Main(unittest.TestCase):
    def test_main_with_names(self):
        df = pd.DataFrame({
            "plant_id_eia": [65855, 65855, 70001],
            "generator_id": ["TE1PV", "TE1PV", "B1"],
            "plant_name_eia": ["Some Solar", "Some Solar", "Lunis Creek Storage"],
            "report_date": pd.to_datetime(["2026-02-01", "2025-12-01", "2025-12-01"]),
            "capacity_mw": [644.8, 836.8, 621.0],
        })
        with tempfile.TemporaryDirectory() as d:
            data, out = os.path.join(d, "data"), os.path.join(d, "out")
            os.makedirs(data)
            df.to_parquet(os.path.join(data, "core_eia860m__changelog_generators.parquet"))
            self.assertEqual(spot.main(["--data-dir", data, "--out-dir", out]), 0)
            with open(os.path.join(out, "spot.md"), encoding="utf-8") as fh:
                md = fh.read()
            self.assertIn("## 65855/TE1PV", md)
            self.assertIn("Lunis Creek Storage", md)
            self.assertNotIn("## 70001/B1", md)
            self.assertTrue(os.path.exists(os.path.join(out, "spot_named.csv")))


if __name__ == "__main__":
    unittest.main()
