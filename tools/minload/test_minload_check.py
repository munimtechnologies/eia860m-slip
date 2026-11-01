"""Unit tests for minload_check.py on small hand-made frames (no network).

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.)."""

import datetime
import unittest

import polars as pl

import minload_check as mc

D24 = datetime.date(2024, 1, 1)
D23 = datetime.date(2023, 1, 1)


def xw_mixed():
    # 2024: A-G1 and C-G3 are one to one; B and B2 share G2; D has G4 and G5; F has no
    # generator. The 2023 row is another year.
    return pl.DataFrame({
        "report_year": [2024, 2024, 2024, 2024, 2024, 2024, 2024, 2023],
        "plant_id_epa": [1, 1, 1, 2, 3, 3, 5, 4],
        "emissions_unit_id_epa": ["A", "B", "B2", "C", "D", "D", "F", "E"],
        "plant_id_eia": [1, 1, 1, 2, 3, 3, 5, 4],
        "generator_id": ["G1", "G2", "G2", "G3", "G4", "G5", None, "G6"],
    })


def xw_simple():
    return pl.DataFrame({
        "report_year": [2024, 2024, 2024, 2024],
        "plant_id_epa": [1, 2, 6, 7],
        "emissions_unit_id_epa": ["A", "C", "H", "J"],
        "plant_id_eia": [1, 2, 6, 7],
        "generator_id": ["G1", "G3", "G7", "G8"],
    })


def ops_frame():
    return pl.DataFrame({
        "plant_id_epa": [1, 2, 6, 7, 1],
        "emissions_unit_id_epa": ["A", "C", "H", "J", "A"],
        "max_gross_load_mw": [100.0, 240.0, 50.0, 80.0, 100.0],
        "min_stable_load_factor": [0.5, 0.25, None, 0.25, 0.875],
        "report_year": [2024, 2024, 2024, 2024, 2023],
    })


def gens_frame(min_2024=(40.0, 100.0, 20.0, 0.0)):
    return pl.DataFrame({
        "plant_id_eia": [1, 2, 6, 7, 1],
        "generator_id": ["G1", "G3", "G7", "G8", "G1"],
        "report_date": [D24, D24, D24, D24, D23],
        "prime_mover_code": ["ST", "CT", "GT", "XX", "ST"],
        "operational_status_code": ["OP", "OP", "OP", "OP", "OP"],
        "capacity_mw": [100.0, 250.0, 50.0, 100.0, 100.0],
        "minimum_load_mw": list(min_2024) + [10.0],
    }, schema_overrides={"minimum_load_mw": pl.Float64})


class StatsTests(unittest.TestCase):
    def test_median(self):
        self.assertEqual(mc.median([3, 1, 2]), 2)
        self.assertEqual(mc.median([4, 1, 3, 2]), 2.5)
        self.assertIsNone(mc.median([]))

    def test_avg_ranks(self):
        self.assertEqual(mc.avg_ranks([10, 20, 20, 30]), [1.0, 2.5, 2.5, 4.0])
        self.assertEqual(mc.avg_ranks([30, 10, 20]), [3.0, 1.0, 2.0])

    def test_spearman(self):
        self.assertAlmostEqual(mc.spearman([1, 2, 3, 4], [10, 20, 30, 45]), 1.0)
        self.assertAlmostEqual(mc.spearman([1, 2, 3], [9, 5, 1]), -1.0)
        self.assertIsNone(mc.spearman([1, 2, 3], [5, 5, 5]))
        self.assertIsNone(mc.spearman([1], [2]))

    def test_quantiles(self):
        q = mc.quantiles([5, 1, 4, 2, 3])
        self.assertEqual(q["0.5"], 3)
        self.assertEqual(q["0.1"], 1)
        self.assertEqual(q["0.9"], 5)


class MatchTests(unittest.TestCase):
    def test_one_to_one(self):
        x = mc.one_to_one(xw_mixed(), 2024)
        self.assertEqual(x.height, 2)
        self.assertEqual(x["emissions_unit_id_epa"].to_list(), ["A", "C"])
        self.assertEqual(x["generator_id"].to_list(), ["G1", "G3"])

    def test_build_and_classes(self):
        m = mc.build(ops_frame(), xw_simple(), gens_frame(), 2024)
        self.assertEqual(m.height, 4)
        self.assertEqual(m["emissions_unit_id_epa"].to_list(), ["A", "C", "H", "J"])
        self.assertEqual(m["pm_class"].to_list(), ["ST", "CC", "GT", "other"])
        self.assertEqual(m["pudl_min_mw"].to_list()[:2], [50.0, 60.0])
        self.assertIsNone(m["pudl_min_mw"].to_list()[2])
        # the 2023 rows are not used
        self.assertEqual(m["minimum_load_mw"].to_list()[0], 40.0)

    def test_comparable_and_summary(self):
        m = mc.build(ops_frame(), xw_simple(), gens_frame(), 2024)
        c = mc.comparable(m)
        self.assertEqual(c["emissions_unit_id_epa"].to_list(), ["A", "C"])
        s = mc.compare_summary(c)
        self.assertEqual(s["n"], 2)
        self.assertEqual(s["above"], 1)
        self.assertEqual(s["below"], 1)
        self.assertEqual(s["within_20"], 0)
        self.assertEqual(s["below_80"], 1)
        self.assertAlmostEqual(s["median_ratio"], 0.925)
        self.assertAlmostEqual(s["median_max_frac"], 0.98)
        self.assertAlmostEqual(s["spearman_mw"], 1.0)
        self.assertIsNone(s["spearman_frac"])  # both EIA fractions are 0.4
        self.assertEqual(mc.compare_summary(c.filter(pl.col("pm_class") == "IC")), {"n": 0})

    def test_null_by_class(self):
        m = mc.build(ops_frame(), xw_simple(), gens_frame(), 2024)
        nb = mc.null_by_class(m)
        self.assertEqual(nb["GT"], {"units": 1, "null_factor": 1, "eia_min_reported": 1})
        self.assertEqual(nb["ST"], {"units": 1, "null_factor": 0, "eia_min_reported": 1})
        self.assertEqual(nb["other"], {"units": 1, "null_factor": 0, "eia_min_reported": 0})
        self.assertEqual(nb["IC"]["units"], 0)

    def test_choose_year(self):
        xw = pl.concat([xw_simple(), xw_simple().with_columns(pl.lit(2023).cast(pl.Int64)
                                                              .alias("report_year"))])
        y, years = mc.choose_year(ops_frame(), xw, gens_frame())
        self.assertEqual((y, years), (2024, [2023, 2024]))
        y, years = mc.choose_year(ops_frame(), xw, gens_frame((None, None, None, None)))
        self.assertEqual((y, years), (2023, [2023]))

    def test_coverage(self):
        cov = mc.coverage(gens_frame((40.0, None, 20.0, 0.0)))
        self.assertEqual(cov[2024], {"gens": 4, "with_min": 3, "positive_min": 2})
        self.assertEqual(cov[2023], {"gens": 1, "with_min": 1, "positive_min": 1})


class ScoreTests(unittest.TestCase):
    def result(self, **over):
        r = {"year": 2024, "g1": {"missing_cols": [], "rows_year": 10},
             "compare": {"n": 400, "above": 220, "within_20": 100, "below_80": 80,
                         "median_max_frac": 0.95, "spearman_mw": 0.9, "spearman_frac": 0.3},
             "null_by_class": {"GT": {"units": 40, "null_factor": 20},
                               "ST": {"units": 50, "null_factor": 10}}}
        r.update(over)
        return r

    def test_all_hold(self):
        s = mc.score(self.result())
        for k in ("G1", "G2", "G3", "P1", "P2", "P3", "P4", "P5", "P6"):
            self.assertTrue(s[k], k)

    def test_misses(self):
        r = self.result()
        r["compare"].update({"above": 150, "within_20": 200, "below_80": 30,
                             "spearman_mw": 0.6, "spearman_frac": 0.7})
        r["null_by_class"]["GT"]["null_factor"] = 10
        s = mc.score(r)
        for k in ("P1", "P2", "P3", "P4", "P5", "P6"):
            self.assertFalse(s[k], k)

    def test_gates(self):
        s = mc.score(self.result(year=2021))
        self.assertFalse(s["G1"])
        self.assertNotIn("P1", s)
        self.assertNotIn("P5", s)
        r = self.result()
        r["compare"]["median_max_frac"] = 1.6
        s = mc.score(r)
        self.assertFalse(s["G3"])
        self.assertNotIn("P1", s)
        self.assertNotIn("P6", s)
        self.assertTrue(s["P3"])
        r = self.result()
        r["compare"]["n"] = 250
        s = mc.score(r)
        self.assertFalse(s["G2"])
        self.assertNotIn("P3", s)
        r = self.result()
        r["null_by_class"]["ST"]["units"] = 19
        self.assertNotIn("P5", mc.score(r))


if __name__ == "__main__":
    unittest.main()
