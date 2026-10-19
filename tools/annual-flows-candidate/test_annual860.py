"""Tests for annual860.py on hand-built tables. MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import unittest

import numpy as np
import pandas as pd

import annual860 as an


def m(year, month):
    return float(year * 12 + month - 1)


def annual():
    return pd.DataFrame({
        "plant_id_eia": [1, 1, 2, 3, 4],
        "generator_id": ["w1", "W1 ", "G", "S", "B"],
        "report_date": ["2017-01-01", "2018-01-01", "2017-01-01", "2018-01-01", "2017-01-01"],
        "operational_status_code": ["OP", "OP", "U", "OP", "SB"],
        "generator_operating_date": ["2017-12-01", "2017-11-01", None, None, "2016-05-01"],
        "capacity_mw": [100.0, 100.0, 50.0, 20.0, 5.0],
    })


def plan():
    return pd.DataFrame({
        "year": [2017, 2017, 2017, 2017],
        "group": ["wind_onshore", "wind_onshore", "solar", "solar"],
        "mw": [100.0, 50.0, 20.0, 5.0],
        "state": ["slipped", "online_in_year", "online_in_year", "not_listed"],
        "cls": ["in_year", "in_year", "undated", "not_in_860"],
    })


def rows_for(planned):
    """Summary rows with the given planned MW per (group, state) for 2017, nothing else set."""
    rows = []
    for (g, s), mw in planned.items():
        rows.append(dict({"year": 2017, "group": g, "state": s, "planned_mw": mw,
                          "delivered_860m_mw": 0.0, "adds_up": True},
                         **{c: 0.0 for c in an.CLASSES}))
    return rows


class KeyTests(unittest.TestCase):
    def test_norm_key(self):
        self.assertEqual(an.norm_key(60671.0, " stg1"), "60671/STG1")
        self.assertEqual(an.norm_key("628", "CC1ST"), "628/CC1ST")
        self.assertIsNone(an.norm_key(None, "A"))
        self.assertIsNone(an.norm_key("x", "A"))
        self.assertIsNone(an.norm_key(np.nan, "A"))
        self.assertIsNone(an.norm_key(5, None))
        self.assertIsNone(an.norm_key(5, "  "))
        self.assertEqual(an.plan_key("1/w1"), "1/W1")


class AnnualTests(unittest.TestCase):
    def test_annual_first(self):
        first, listed = an.annual_first(annual())
        self.assertEqual(listed, {"1/W1", "2/G", "3/S", "4/B"})
        self.assertEqual(sorted(first.index), ["1/W1", "3/S", "4/B"])
        self.assertEqual(first["1/W1"], m(2017, 11))  # earliest of two dated records
        self.assertTrue(np.isnan(first["3/S"]))
        self.assertEqual(first["4/B"], m(2016, 5))

    def test_annual_class(self):
        first, listed = an.annual_first(annual())
        cls = lambda y, k: an.annual_class(y, k, first, listed)
        self.assertEqual(cls(2017, "1/w1"), "in_year")
        self.assertEqual(cls(2016, "1/W1"), "next_year")
        self.assertEqual(cls(2015, "1/W1"), "later")
        self.assertEqual(cls(2018, "1/W1"), "before")
        self.assertEqual(cls(2017, "3/S"), "undated")
        self.assertEqual(cls(2017, "2/G"), "never")
        self.assertEqual(cls(2017, "9/X"), "not_in_860")
        self.assertEqual(cls(2017, "4/B"), "before")


class SummaryTests(unittest.TestCase):
    def test_summarize(self):
        rows = {(r["group"], r["state"]): r for r in an.summarize(plan())}
        a = rows[("all", "all")]
        self.assertEqual((a["planned_mw"], a["in_year"], a["undated"], a["not_in_860"], a["before"]),
                         (175.0, 150.0, 20.0, 5.0, 0.0))
        self.assertEqual((a["delivered_860m_mw"], a["share_860m"], a["share_860"]), (70.0, 0.4, 0.857))
        self.assertTrue(all(r["adds_up"] for r in rows.values()))
        w = rows[("wind_onshore", "all")]
        self.assertEqual((w["planned_mw"], w["share_860m"], w["share_860"]), (150.0, 0.333, 1.0))
        self.assertEqual(rows[("wind_onshore", "slipped")]["in_year"], 100.0)
        self.assertEqual(sorted(s for g, s in rows if g == "all"),
                         ["all", "not_listed", "online_in_year", "slipped"])

    def test_checks(self):
        rows = rows_for(an.EXPECTED_2017)
        self.assertTrue(an.checks(rows, [], [2016, 2017, 2018])["all_pass"])
        self.assertFalse(an.checks(rows, ["capacity_mw"], [2017, 2018])["C2"]["pass"])
        self.assertFalse(an.checks(rows, [], [2017])["C2"]["pass"])
        off = dict(an.EXPECTED_2017)
        off[("wind_onshore", "slipped")] += 0.2
        c = an.checks(rows_for(off), [], [2017, 2018])
        self.assertFalse(c["C1"]["pass"])
        self.assertFalse(c["all_pass"])
        rows[0]["adds_up"] = False
        self.assertEqual(an.checks(rows, [], [2017, 2018])["C3"]["not_adding_up"], 1)

    def test_predictions(self):
        rows = rows_for({("wind_onshore", "all"): 100.0, ("wind_onshore", "slipped"): 40.0,
                         ("all", "all"): 200.0})
        r = {(x["group"], x["state"]): x for x in rows}
        r[("wind_onshore", "all")]["in_year"] = 75.0
        r[("wind_onshore", "slipped")]["in_year"] = 19.0
        r[("all", "all")]["in_year"] = 130.0
        r[("all", "all")]["delivered_860m_mw"] = 120.0
        p = an.predictions(rows)
        self.assertEqual((p["W1"]["share_860"], p["W1"]["held"]), (0.75, True))
        self.assertEqual((p["W2"]["share_860"], p["W2"]["held"]), (0.475, False))
        self.assertEqual((p["W3"]["share_860"], p["W3"]["held"]), (0.65, False))
        self.assertEqual(p["W4"]["years_860_above_860m"], [2017])
        self.assertIsNone(p["W4"]["held"])  # fewer than 8 years: not scorable


if __name__ == "__main__":
    unittest.main()
