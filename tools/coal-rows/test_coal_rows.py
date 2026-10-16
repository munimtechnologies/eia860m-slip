"""Tests for coal_rows on a hand-built changelog. MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import unittest

import numpy as np
import pandas as pd

import coal_rows

COAL = {"technology_description": "Conventional Steam Coal", "energy_source_code_1": "BIT"}
GAS = {"technology_description": "Natural Gas Fired Combined Cycle", "energy_source_code_1": "NG"}


def rec(plant, report, valid, status, mw, planned=None, retired=None, fuel=COAL, summer=True):
    r = {"report_date": report, "valid_until_date": valid, "plant_id_eia": plant,
         "plant_name_eia": "Plant %d" % plant, "generator_id": "1", "utility_name_eia": "U",
         "state": "ST", "capacity_mw": mw + 10, "summer_capacity_mw": mw if summer else np.nan,
         "planned_generator_retirement_date": planned, "generator_retirement_date": retired,
         "operational_status_code": status}
    r.update(fuel)
    return r


def frame():
    rows = [
        # 1: planned for 2021 in both inventories, retired 2021-06.
        rec(1, "2020-01-01", "2021-05-01", "OP", 100, planned="2021-06-01"),
        rec(1, "2021-06-01", None, "RE", 100, retired="2021-06-01"),
        # 2: dated 2025 at both inventories, re-dated 2021-09 in March 2021, retired 2021-09.
        rec(2, "2020-01-01", "2021-02-01", "OP", 200, planned="2025-12-01"),
        rec(2, "2021-03-01", "2021-08-01", "OP", 200, planned="2021-09-01"),
        rec(2, "2021-09-01", None, "RE", 200, retired="2021-09-01"),
        # 3: no planned date, retired 2021-11; nameplate only (300) on both records.
        rec(3, "2020-01-01", "2021-10-01", "OP", 290, summer=False),
        rec(3, "2021-11-01", None, "RE", 290, retired="2021-11-01", summer=False),
        # 4: planned for 2021, deferred to 2023 in July 2021, never retired.
        rec(4, "2020-01-01", "2021-06-01", "OP", 400, planned="2021-12-01"),
        rec(4, "2021-07-01", None, "OP", 400, planned="2023-12-01"),
        # 5: gas, retired 2021: not coal.
        rec(5, "2020-01-01", "2021-04-01", "OP", 500, fuel=GAS),
        rec(5, "2021-05-01", None, "RE", 500, retired="2021-05-01", fuel=GAS),
        # 6: no date in October 2020, dated 2021-03 from December 2020, retired 2021-03.
        rec(6, "2020-01-01", "2020-11-01", "OP", 50),
        rec(6, "2020-12-01", "2021-02-01", "OP", 50, planned="2021-03-01"),
        rec(6, "2021-03-01", None, "RE", 50, retired="2021-03-01"),
    ]
    return coal_rows.prepare(pd.DataFrame(rows))


class CoalRowsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.res = coal_rows.analyse(frame())
        cls.year = cls.res["years"][0]

    def test_years_and_range(self):
        self.assertEqual([y["year"] for y in self.res["years"]], [2021])
        self.assertEqual(self.res["report_min"], "2020-01")
        self.assertEqual(self.res["report_max"], "2021-11")
        self.assertTrue(self.year["partial"])

    def test_retired_coal_only(self):
        # 100 + 200 + 300 (nameplate fallback) + 50; the gas unit is excluded.
        self.assertEqual(self.year["retired_n"], 4)
        self.assertAlmostEqual(self.year["retired_mw"], 650.0)
        self.assertEqual(self.year["eia_plan_gw"], 2.7)
        self.assertEqual(self.year["eia_final_gw"], 5.5618)

    def test_december_inventory(self):
        inv = self.year["inventories"]["dec"]
        self.assertEqual(inv["month"], "2020-12")
        self.assertEqual(inv["plan_n"], 3)
        self.assertAlmostEqual(inv["plan_mw"], 550.0)
        self.assertEqual(inv["plan_outcome"], {"retired_in_year": 150.0, "retired_earlier": 0.0,
                                               "retired_later": 0.0, "not_retired": 400.0})
        self.assertAlmostEqual(inv["plan_delivery"], 0.2727)
        b = inv["retired_by_class"]
        self.assertEqual((b["planned_same_year"], b["planned_later"], b["no_date"], b["not_listed"]),
                         (150.0, 200.0, 300.0, 0.0))
        self.assertAlmostEqual(inv["unplanned_share"], 0.7692)

    def test_october_inventory(self):
        inv = self.year["inventories"]["oct"]
        self.assertEqual(inv["month"], "2020-10")
        self.assertAlmostEqual(inv["plan_mw"], 500.0)
        self.assertAlmostEqual(inv["plan_outcome"]["retired_in_year"], 100.0)
        b = inv["retired_by_class"]
        self.assertEqual((b["planned_same_year"], b["planned_later"], b["no_date"]), (100.0, 200.0, 350.0))

    def test_first_dated_and_in_year(self):
        g = {r["key"]: r for r in self.res["generators"]}
        self.assertEqual(g["1/1"]["first_dated"], "2020-01")
        self.assertEqual(g["2/1"]["first_dated"], "2021-03")
        self.assertEqual(g["3/1"]["first_dated"], "2021-11")
        self.assertEqual(g["6/1"]["first_dated"], "2020-12")
        self.assertEqual(g["2/1"]["class_dec"], "planned_later")
        self.assertEqual(g["2/1"]["planned_at_dec"], "2025-12")
        self.assertEqual(g["6/1"]["class_oct"], "no_date")
        self.assertEqual(g["6/1"]["class_dec"], "planned_same_year")
        # Units 2 and 3 first carried a 2021 date during 2021.
        self.assertAlmostEqual(self.year["decided_in_year_mw"], 500.0)

    def test_followup(self):
        f = self.res["followup"]
        self.assertEqual((f["year"], f["inventory"], f["plan_n"]), (2021, "2020-12", 3))
        now = {r["key"]: r["now"] for r in f["rows"]}
        self.assertEqual(now, {"1/1": "retired", "4/1": "dated_later", "6/1": "retired"})
        self.assertEqual(f["mw_by_status"], {"retired": 150.0, "dated_later": 400.0})

    def test_top_unplanned(self):
        top = coal_rows.top_unplanned(self.res["generators"], 2021)
        self.assertEqual([r["plant"] for r in top], ["Plant 3", "Plant 2"])
        self.assertEqual(top[0]["classes"], "no_date")

    def test_render(self):
        md = coal_rows.render(self.res, {"records": 14})
        self.assertIn("| 2021 (partial) | 2020-12 | 2.7 | 0.55 | 0.15 | 0.65 | 5.5618 |", md)
        self.assertIn("## 2021: largest retirements not planned for the year", md)
        self.assertIn("| Plant 3 | ST | 300.0 | 1 | no_date | 2021-11 | 2021-11 |", md)

    def test_is_coal(self):
        self.assertTrue(coal_rows.is_coal("LIG", None))
        self.assertFalse(coal_rows.is_coal("PC", "Petroleum Coke"))
        self.assertTrue(coal_rows.is_coal(np.nan, "Conventional Steam Coal"))
        self.assertFalse(coal_rows.is_coal(np.nan, None))


if __name__ == "__main__":
    unittest.main()
