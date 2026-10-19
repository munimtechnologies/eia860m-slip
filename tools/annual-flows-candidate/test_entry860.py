"""Tests for entry860.py on hand-built tables. MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import unittest

import numpy as np
import pandas as pd

import entry860 as en


def m(year, month):
    return float(year * 12 + month - 1)


def changelog():
    """EIA-860M records: report, valid until, plant, generator, MW, planned month, status."""
    recs = [("2016-06-01", None, 1, "A", 10.0, "2018-03-01", "P"),
            ("2017-04-01", None, 2, "B", 20.0, "2017-09-01", "U"),
            ("2016-01-01", None, 3, "C", 5.0, None, "OP"),
            ("2016-02-01", "2016-05-01", 4, "d ", 40.0, "2016-12-01", "L"),
            ("2016-11-01", None, 6, "F", 15.0, "2017-05-01", "T"),
            ("2017-08-01", None, 7, "G", 30.0, None, "OP"),
            ("2018-06-01", None, 99, "Z", 1.0, None, "OP")]
    raw = pd.DataFrame(recs, columns=["report_date", "valid_until_date", "plant_id_eia",
                                      "generator_id", "capacity_mw",
                                      "current_planned_generator_operating_date",
                                      "operational_status_code"])
    return en.es.prepare(raw)


def annual_side():
    """One year's annual side as baseline860.mark returns it."""
    keys = ["1/A", "2/B", "3/C", "4/D", "5/E", "6/F", "7/G", "8/H"]
    return pd.DataFrame({
        "key": keys,
        "group": ["solar", "wind_onshore", "solar", "solar", "solar", "solar", "wind_onshore",
                  "gas_cc"],
        "mw": [10.0, 20.0, 5.0, 40.0, 25.0, 15.0, 30.0, 50.0],
        "plant": ["Alpha", "Beta", "Gamma", "Delta", "Eps", "Zeta", "Eta", "Theta"],
        "year": [2017] * 8,
        "cls": ["later", "in_year", "before", "never", "in_year", "in_year", "before", "in_year"],
        "overlap": ["annual_only"] * 7 + ["both"]})


def new_entries():
    return pd.DataFrame({"year": [2017, 2017], "key": ["2/B", "9/Q"],
                         "group": ["wind_onshore", "solar"], "mw": [20.0, 12.0],
                         "state": ["new_entry", "new_entry"], "nkey": ["2/B", "9/Q"]})


def classified():
    df = changelog()
    return en.classify(annual_side(), 2017, en.january(df, 2017), en.entries(df),
                       pd.Series({"2/B": m(2017, 10)}))


def texts(col):
    """A text column as a list, missing values as None (pandas 3 stores None as NaN)."""
    return [x if isinstance(x, str) else None for x in col]


def row(year, group, **kw):
    r = {"year": year, "group": group, "baseline_mw": 0.0, "annual_only_mw": 0.0,
         "in_january_planned_in_year": 0.0, "entered_after_january": 0.0, "after_operating": 0.0,
         "after_building": 0.0, "new_entry_mw": 0.0, "new_entry_in_annual_plan_mw": 0.0,
         "adds_up": True}
    r.update(kw)
    return r


class EntryTests(unittest.TestCase):
    def test_band(self):
        self.assertEqual([en.band(s) for s in ("OP", "SB", "U", "V", "TS", "T", "P", "L", "OT",
                                               "CN")],
                         ["operating", "operating", "building", "building", "building",
                          "approved", "early", "early", "other", "other"])

    def test_entries(self):
        first = en.entries(changelog())
        self.assertEqual(sorted(first.index), ["1/A", "2/B", "3/C", "4/D", "6/F", "7/G", "99/Z"])
        self.assertEqual((first.at["2/B", "first_m"], first.at["2/B", "first_status"]),
                         (m(2017, 4), "U"))
        self.assertEqual(first.at["4/D", "first_m"], m(2016, 2))  # 'd ' trimmed, upper-cased

    def test_january(self):
        jan = en.january(changelog(), 2017)
        # 4/D's only record ended in 2016-05; 2/B and 7/G were first listed after January.
        self.assertEqual(sorted(jan.index), ["1/A", "3/C", "6/F"])
        self.assertEqual(jan.at["6/F", "planned_m"], m(2017, 5))

    def test_classify(self):
        f = classified()
        self.assertEqual(list(f["key"]), ["1/A", "2/B", "3/C", "4/D", "5/E", "6/F", "7/G"])
        self.assertEqual(list(f["entry"]),
                         ["in_january_other_month", "entered_after_january",
                          "in_january_not_planned", "listed_before_not_in_january",
                          "never_in_860m", "in_january_planned_in_year",
                          "entered_after_january"])
        self.assertEqual(texts(f["first_listed"]),
                         ["2016-06", "2017-04", "2016-01", "2016-02", None, "2016-11", "2017-08"])
        self.assertEqual(texts(f["first_band"]),
                         ["early", "building", "operating", "early", None, "approved",
                          "operating"])
        self.assertEqual(texts(f["online_860"]), [None, "2017-10", None, None, None, None, None])
        self.assertTrue(np.isnan(f.loc[4, "first_m"]))

    def test_timing(self):
        t = en.entry_timing(classified(), 2017)
        self.assertEqual(t, {"2017-Q1": 0.0, "2017-Q2": 20.0, "2017-Q3": 30.0, "2017-Q4": 0.0,
                             "after_2017": 0.0})


class SummaryTests(unittest.TestCase):
    def test_summarize(self):
        rows = {(r["year"], r["group"]): r for r in
                en.summarize({2017: annual_side()}, {2017: classified()}, {2017: new_entries()})}
        self.assertEqual(sorted(rows), [(2017, "all"), (2017, "gas_cc"), (2017, "solar"),
                                        (2017, "wind_onshore")])
        a = rows[(2017, "all")]
        self.assertEqual((a["baseline_mw"], a["annual_only_mw"]), (195.0, 145.0))
        self.assertEqual([a[c] for c in en.ENTRY], [5.0, 10.0, 15.0, 50.0, 40.0, 25.0])
        self.assertEqual((a["after_share"], a["after_operating"], a["after_building"],
                          a["after_op_or_building_share"], a["after_in_year_share"]),
                         (0.3448, 30.0, 20.0, 1.0, 0.4))
        self.assertEqual((a["new_entry_mw"], a["new_entry_in_annual_plan_mw"],
                          a["new_entry_in_annual_plan_share"]), (32.0, 20.0, 0.625))
        w = rows[(2017, "wind_onshore")]
        self.assertEqual((w["baseline_mw"], w["after_share"], w["new_entry_in_annual_plan_share"]),
                         (50.0, 1.0, 1.0))
        g = rows[(2017, "gas_cc")]
        self.assertEqual((g["baseline_mw"], g["annual_only_mw"], g["after_share"],
                          g["new_entry_in_annual_plan_share"]), (50.0, 0.0, None, None))
        self.assertTrue(all(r["adds_up"] for r in rows.values()))

    def test_checks(self):
        rows = [row(y, "all", baseline_mw=b, annual_only_mw=o)
                for y, (b, o) in en.PUBLISHED.items()]
        rows[0]["new_entry_mw"] = 4626.7
        self.assertTrue(en.checks(rows, [])["all_pass"])
        self.assertFalse(en.checks(rows, ["plant_name_eia"])["E1"]["pass"])
        rows[3]["annual_only_mw"] += 0.2
        self.assertFalse(en.checks(rows, [])["E1"]["pass"])
        rows[3]["annual_only_mw"] -= 0.2
        rows[2]["in_january_planned_in_year"] = 3.0
        c = en.checks(rows, [])
        self.assertEqual((c["E3"]["pass"], c["all_pass"]), (False, False))
        rows[2]["in_january_planned_in_year"] = 0.0
        rows[0]["new_entry_mw"] = 4600.0
        self.assertFalse(en.checks(rows, [])["E4"]["pass"])
        rows[0]["new_entry_mw"] = 4626.7
        rows[5]["adds_up"] = False
        self.assertEqual(en.checks(rows, [])["E2"]["not_adding_up"], 1)
        self.assertFalse(en.checks(rows[1:], [])["all_pass"])

    def test_predictions(self):
        rows = [row(2017, "all", annual_only_mw=1000.0, entered_after_january=600.0,
                    after_operating=300.0, after_building=179.0, new_entry_mw=400.0,
                    new_entry_in_annual_plan_mw=200.0)]
        p = en.predictions(rows)
        self.assertEqual((p["A1"]["after_share"], p["A1"]["held"]), (0.6, True))  # at the floor
        self.assertEqual((p["A2"]["op_or_building_share"], p["A2"]["held"]), (0.7983, False))
        self.assertEqual((p["A3"]["years"], p["A3"]["held"]), ([2017], None))  # not scorable
        self.assertEqual((p["A4"]["new_entry_in_annual_plan_share"], p["A4"]["held"]), (0.5, True))
        none = en.predictions([])
        self.assertEqual([none[k]["held"] for k in ("A1", "A2", "A3", "A4")], [None] * 4)

    def test_predictions_a3(self):
        def rows(n_half):
            return [row(y, "all", annual_only_mw=100.0,
                        entered_after_january=50.0 if i < n_half else 49.9)
                    for i, y in enumerate(range(2017, 2025))]
        p = en.predictions(rows(5))
        self.assertEqual((p["A3"]["years_after_share_at_least_half"], p["A3"]["held"]),
                         ([2017, 2018, 2019, 2020, 2021], False))
        self.assertTrue(en.predictions(rows(6))["A3"]["held"])

    def test_top(self):
        f = classified()
        t = en.bn.top(f, en.LIST_COLS, n=2)
        self.assertEqual([x["key"] for x in t], ["4/D", "7/G"])
        self.assertEqual(t[1], {"key": "7/G", "plant": "Eta", "group": "wind_onshore", "mw": 30.0,
                                "entry": "entered_after_january", "first_listed": "2017-08",
                                "first_band": "operating", "cls": "before", "online_860": ""})


if __name__ == "__main__":
    unittest.main()
