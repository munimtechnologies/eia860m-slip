"""Tests for order_dates (MV2 of Munim, Inc.; made with AI agents). Apache-2.0."""

import datetime as dt
import os
import unittest

import numpy as np
import pandas as pd

import order_dates as od

D = dt.date


def rec(report, plant_id, name, gen, state, status, planned=None, retired=None, fuel="SUB", mw=100.0):
    return {"report_date": report, "valid_until_date": np.nan, "plant_id_eia": plant_id,
            "plant_name_eia": name, "generator_id": gen, "state": state, "capacity_mw": mw,
            "summer_capacity_mw": mw, "planned_generator_retirement_date": planned,
            "generator_retirement_date": retired, "operational_status_code": status,
            "energy_source_code_1": fuel}


ORDERS = [{"order": "A", "plant_key": "campbell", "issued": D(2025, 5, 23), "expires": D(2025, 8, 21)},
          {"order": "B", "plant_key": "campbell", "issued": D(2025, 8, 20), "expires": D(2025, 11, 19)}]
UNIT = {"plant_key": "campbell", "plant": "J.H. Campbell", "state": "MI", "pattern": "campbell",
        "coal_plant": True, "ids": ["1"], "expected_plant_id": "1710"}


def campbell():
    return od.prepare(pd.DataFrame([
        rec("2025-04-01", 1710, "J H Campbell", "1", "MI", "OP", "2025-05-01"),
        rec("2025-06-01", 1710, "J H Campbell", "1", "MI", "OP", "2025-08-01"),
        rec("2025-09-01", 1710, "J H Campbell", "1", "MI", "OP", "2025-11-01"),
    ]))


class Helpers(unittest.TestCase):
    def test_month_end_leap(self):
        self.assertEqual(od.month_end(2024 * 12 + 1), D(2024, 2, 29))
        self.assertEqual(od.month_end(2025 * 12 + 11), D(2025, 12, 31))

    def test_in_force_prefers_renewal(self):
        self.assertEqual(od.in_force(ORDERS, D(2025, 8, 20))["order"], "B")
        self.assertEqual(od.in_force(ORDERS, D(2025, 7, 31))["order"], "A")

    def test_in_force_gap_and_expiry_day(self):
        self.assertIsNone(od.in_force(ORDERS, D(2025, 11, 30)))
        self.assertEqual(od.in_force(ORDERS, D(2025, 11, 19))["order"], "B")
        self.assertIsNone(od.in_force(ORDERS, D(2025, 5, 22)))

    def test_classify(self):
        o = {"expires": D(2025, 8, 21)}
        base = {"status": "OP", "plan_ret_m": 2025 * 12 + 7, "ret_m": np.nan}
        self.assertEqual(od.classify(base, o), "exact")
        self.assertEqual(od.classify(dict(base, plan_ret_m=2025 * 12 + 8), o), "plus1")
        self.assertEqual(od.classify(dict(base, plan_ret_m=2025 * 12 + 6), o), "minus1")
        self.assertEqual(od.classify(dict(base, plan_ret_m=2025 * 12 + 11), o), "later")
        self.assertEqual(od.classify(dict(base, plan_ret_m=2025 * 12 + 4), o), "earlier")
        self.assertEqual(od.classify(dict(base, plan_ret_m=np.nan), o), "no_date")
        self.assertEqual(od.classify(dict(base, status="RE"), o), "retired")
        self.assertEqual(od.classify(dict(base, status="SB"), None), "no_order")
        self.assertEqual(od.classify(dict(base, status="U"), o), "not_operating")
        self.assertEqual(od.classify(None, o), "not_listed")

    def test_changes(self):
        self.assertEqual(od.changes(["2025-05", "2025-08", "2025-08", "", "2025-11"]), 2)
        self.assertEqual(od.changes([]), 0)


class Analyse(unittest.TestCase):
    def test_ratchet(self):
        res = od.analyse(campbell(), ORDERS, [UNIT])
        got = [(r["report"], r["planned"], r["order"], r["class"]) for r in res["rows"]]
        self.assertEqual(got, [
            ("2025-05", "2025-05", "A", "earlier"),
            ("2025-06", "2025-08", "A", "exact"),
            ("2025-07", "2025-08", "A", "exact"),
            ("2025-08", "2025-08", "B", "earlier"),
            ("2025-09", "2025-11", "B", "exact"),
        ])
        p = res["plants"][0]
        self.assertEqual((p["scored"], p["exact"], p["max_changes"]), (5, 3, 2))
        self.assertEqual(p["planned_before"], ["2025-05"])
        self.assertEqual(p["planned_latest"], ["2025-11"])
        self.assertEqual(p["method"], "generator_ids")
        self.assertEqual(p["mw"], 100.0)

    def test_fallback_and_coal_filter(self):
        df = od.prepare(pd.DataFrame([
            rec("2025-04-01", 1710, "J H Campbell", "X1", "MI", "OP", "2025-06-01"),
            rec("2025-04-01", 1710, "J H Campbell", "X2", "MI", "OP"),
            rec("2025-04-01", 9999, "Campbell Hydro", "1", "MI", "OP", "2025-06-01", fuel="WAT"),
            rec("2025-04-01", 8888, "Campbell", "1", "OH", "OP", "2025-06-01"),
        ]))
        res = od.analyse(df, ORDERS, [UNIT])
        p = res["plants"][0]
        self.assertEqual(p["method"], "fallback")
        self.assertEqual(p["generators"], ["1710/X1"])
        self.assertEqual(p["plant_ids"], ["1710"])

    def test_score(self):
        res = od.analyse(campbell(), ORDERS, [UNIT])
        sc = od.score(res, 5)
        self.assertEqual((sc["P1"]["n"], sc["P1"]["exact"]), (5, 3))
        self.assertTrue(sc["P1"]["hit"])
        self.assertFalse(sc["P2"]["hit"])
        self.assertTrue(sc["P3"]["hit"])
        self.assertFalse(sc["P4"]["hit"])
        self.assertIsNone(sc["P5"]["hit"])
        self.assertFalse(sc["C3"]["pass"])

    def test_shipped_tables_parse(self):
        orders = od.read_orders(os.path.join(od.HERE, "orders.csv"))
        units = od.read_units(os.path.join(od.HERE, "units.csv"))
        self.assertEqual(len(units), 8)
        self.assertEqual({o["plant_key"] for o in orders}, {u["plant_key"] for u in units})
        for o in orders:
            self.assertLess(o["issued"], o["expires"])
            self.assertLessEqual((o["expires"] - o["issued"]).days, 95)
        self.assertEqual(od.in_force([o for o in orders if o["plant_key"] == "campbell"],
                                     D(2026, 8, 31))["order"], "202-26-39")
        self.assertIsNone(od.in_force([o for o in orders if o["plant_key"] == "wagner"],
                                      D(2026, 2, 28)))


if __name__ == "__main__":
    unittest.main()
