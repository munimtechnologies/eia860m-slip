"""Tests for baseline860.py on hand-built tables. MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import unittest

import numpy as np
import pandas as pd

import baseline860 as bn


def m(year, month):
    return float(year * 12 + month - 1)


def annual():
    wind, solar = "Onshore Wind Turbine", "Solar Photovoltaic"
    return pd.DataFrame({
        "plant_id_eia": [1, 1, 2, 2, 3, 4, 5, 6, 7],
        "generator_id": ["W1", "W1", "S", "S", "G", "B", "X", "w2 ", "A"],
        "report_date": ["2016-01-01", "2017-01-01", "2016-01-01", "2018-01-01", "2016-01-01",
                        "2016-01-01", "2016-01-01", "2016-01-01", "2015-01-01"],
        "operational_status_code": ["U", "OP", "P", "OP", "T", "OP", "CN", "L", "U"],
        "generator_operating_date": [None, "2017-11-01", None, "2018-03-01", None, "2015-05-01",
                                     None, None, None],
        "capacity_mw": [100.0, 100.0, 50.0, 50.0, 30.0, 5.0, 20.0, 40.0, 10.0],
        "current_planned_generator_operating_date": [
            "2017-06-01", None, "2017-12-01", None, "2018-02-01", None, "2017-03-01",
            "2017-01-01", "2017-05-01"],
        "technology_description": [wind, wind, solar, solar, "Natural Gas Fired Combined Cycle",
                                   "Batteries", wind, wind, solar],
        "plant_name_eia": ["Alpha", "Alpha", "Beta", "Beta", "Gamma", "Delta", "Eps", None, "Zeta"],
    })


def plan():
    return pd.DataFrame({
        "year": [2017, 2017, 2017, 2018],
        "key": ["1/w1", "8/W", "9/OLD", "10/Z"],
        "group": ["wind_onshore", "wind_onshore", "solar", "gas_cc"],
        "mw": [95.0, 60.0, 20.0, 70.0],
        "state": ["online_in_year", "slipped", "rekeyed_online", "online_in_year"],
        "cls": ["in_year", "later", "in_year", "in_year"],
        "plant": ["Alpha", "Eta", "Theta", "Iota"],
        "lookup_key": ["1/w1", "8/W", "2/S", "10/Z"],
    })


def sides():
    a = annual()
    first, listed = bn.an.annual_first(a)
    return {y: bn.mark(bn.baseline(a, y), plan(), y, first, listed) for y in (2017, 2018)}


def row(year, group, **kw):
    r = {"year": year, "group": group, "baseline_mw": 0.0, "in_year": 0.0, "both_mw": 0.0,
         "plan_860m_mw": 0.0, "delivered_860m_mw": 0.0, "adds_up": True}
    r.update(kw)
    return r


class BaselineTests(unittest.TestCase):
    def test_baseline(self):
        b = bn.baseline(annual(), 2017)
        # Report year 2016 only, planned codes only (not OP or CN), planned month in 2017.
        self.assertEqual(list(b["key"]), ["1/W1", "2/S", "6/W2"])
        self.assertEqual(list(b["mw"]), [100.0, 50.0, 40.0])
        self.assertEqual(list(b["group"]), ["wind_onshore", "solar", "wind_onshore"])
        self.assertEqual(list(b["plant"]), ["Alpha", "Beta", ""])
        self.assertEqual(len(bn.baseline(annual(), 2018)), 0)  # nothing in report year 2017

    def test_mark(self):
        b, mm = sides()[2017]
        self.assertEqual(list(b["cls"]), ["in_year", "next_year", "never"])
        self.assertEqual(list(b["overlap"]), ["both", "both", "annual_only"])
        self.assertEqual(list(mm["key"]), ["1/w1", "8/W", "9/OLD"])
        # 9/OLD was re-keyed to 2/S, which the annual plan has.
        self.assertEqual(list(mm["overlap"]), ["both", "m_only", "both"])


class SummaryTests(unittest.TestCase):
    def test_summarize(self):
        rows = {(r["year"], r["group"]): r for r in bn.summarize(sides())}
        self.assertEqual(sorted(rows), [(2017, "all"), (2017, "solar"), (2017, "wind_onshore"),
                                        (2018, "all"), (2018, "gas_cc")])
        a = rows[(2017, "all")]
        self.assertEqual((a["baseline_mw"], a["in_year"], a["next_year"], a["never"], a["before"]),
                         (190.0, 100.0, 50.0, 40.0, 0.0))
        self.assertEqual((a["share_in_year"], a["both_mw"], a["both_share_in_year"],
                          a["annual_only_mw"], a["annual_only_share_in_year"]),
                         (0.5263, 150.0, 0.6667, 40.0, 0.0))
        self.assertEqual((a["plan_860m_mw"], a["delivered_860m_mw"], a["share_860m"],
                          a["m_only_mw"], a["m_only_share_860m"]),
                         (175.0, 115.0, 0.6571, 60.0, 0.0))
        w = rows[(2017, "wind_onshore")]
        self.assertEqual((w["baseline_mw"], w["share_in_year"], w["both_mw"], w["plan_860m_mw"],
                          w["share_860m"]), (140.0, 0.7143, 100.0, 155.0, 0.6129))
        s = rows[(2017, "solar")]
        self.assertEqual((s["annual_only_share_in_year"], s["m_only_share_860m"], s["share_860m"]),
                         (None, None, 1.0))
        r18 = rows[(2018, "all")]
        self.assertEqual((r18["baseline_mw"], r18["share_in_year"], r18["plan_860m_mw"],
                          r18["m_only_mw"]), (0.0, None, 70.0, 70.0))
        self.assertTrue(all(r["adds_up"] for r in rows.values()))

    def test_checks(self):
        years = list(range(2001, 2027))
        rows = [row(2017, "all", baseline_mw=25000.0, plan_860m_mw=26268.8),
                row(2017, "wind_onshore", plan_860m_mw=6858.3)]
        self.assertTrue(bn.checks(rows, [], years)["all_pass"])
        c = bn.checks(rows, [], [y for y in years if y != 2016])
        self.assertEqual((c["D1"]["missing_report_years"], c["D1"]["pass"]), ([2016], False))
        self.assertFalse(bn.checks(rows, ["technology_description"], years)["D1"]["pass"])
        rows[1]["plan_860m_mw"] = 6858.45
        self.assertFalse(bn.checks(rows, [], years)["D2"]["pass"])
        rows[1]["plan_860m_mw"] = 6858.3
        rows[0]["baseline_mw"] = 9000.0
        c = bn.checks(rows, [], years)
        self.assertEqual((c["D4"]["pass"], c["all_pass"]), (False, False))
        rows[0]["baseline_mw"] = 25000.0
        rows[1]["adds_up"] = False
        self.assertEqual(bn.checks(rows, [], years)["D3"]["not_adding_up"], 1)
        self.assertFalse(bn.checks([], [], years)["D2"]["pass"])

    def test_predictions_2017(self):
        rows = [row(2017, "all", baseline_mw=24000.0, in_year=18000.0, plan_860m_mw=26000.0,
                    delivered_860m_mw=16000.0),
                row(2017, "wind_onshore", baseline_mw=7000.0, in_year=5550.0, both_mw=5600.0)]
        p = bn.predictions(rows)
        self.assertEqual((p["B1"]["off"], p["B1"]["held"]), (0.0438, True))  # 1,100 / 25,100
        self.assertEqual((p["B2"]["share_in_year"], p["B2"]["held"]), (0.75, True))  # at the floor
        self.assertEqual((p["B3"]["share_in_year"], p["B3"]["held"]), (0.7929, False))
        self.assertEqual((p["B4"]["both_share"], p["B4"]["held"]), (0.8, True))  # at the limit
        self.assertEqual((p["B5"]["years"], p["B5"]["years_annual_above_860m"]), ([2017], [2017]))
        self.assertIsNone(p["B5"]["held"])  # fewer than 8 years: not scorable
        none = bn.predictions([])
        self.assertEqual([none[k]["held"] for k in ("B1", "B2", "B3", "B4", "B5")], [None] * 5)

    def test_predictions_b5(self):
        def rows(n_above):
            return [row(y, "all", baseline_mw=100.0, plan_860m_mw=100.0, delivered_860m_mw=60.0,
                        in_year=80.0 if i < n_above else 50.0)
                    for i, y in enumerate(range(2017, 2025))]
        p = bn.predictions(rows(5))
        self.assertEqual((p["B5"]["years_annual_above_860m"], p["B5"]["held"]),
                         ([2017, 2018, 2019, 2020, 2021], False))
        self.assertTrue(bn.predictions(rows(6))["B5"]["held"])
        self.assertEqual(bn.predictions(rows(8))["B1"]["off"], round(25000.0 / 25100.0, 4))

    def test_top(self):
        f = pd.DataFrame({"key": ["b", "a", "c"], "plant": [np.nan, "A", "C"],
                          "group": ["solar"] * 3, "mw": [5.0, 5.0, 9.04],
                          "cls": ["never", "in_year", "later"]})
        t = bn.top(f, bn.ANNUAL_LIST, n=2)
        self.assertEqual([x["key"] for x in t], ["c", "a"])
        self.assertEqual(t[0], {"key": "c", "plant": "C", "group": "solar", "mw": 9.0,
                                "cls": "later"})
        self.assertEqual(bn.top(f, bn.ANNUAL_LIST)[2]["plant"], "")


if __name__ == "__main__":
    unittest.main()
