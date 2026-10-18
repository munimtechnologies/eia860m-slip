"""Tests for plan_flows (MV2 of Munim, Inc.; made with AI agents). Apache-2.0."""

import csv
import json
import os
import tempfile
import unittest

import numpy as np
import pandas as pd

import plan_flows as pf

M = lambda y, mo: y * 12 + mo - 1  # noqa: E731


def rec(report, plant, gen, status, tech="Solar Photovoltaic", planned=None, op=None, mw=100.0, summer=None,
        valid=np.nan):
    return {"report_date": report, "valid_until_date": valid, "plant_id_eia": plant, "generator_id": gen,
            "capacity_mw": mw, "summer_capacity_mw": mw if summer is None else summer,
            "current_planned_generator_operating_date": planned, "generator_operating_date": op,
            "operational_status_code": status, "technology_description": tech}


# Traced by hand. December 2025 book: A 100, B 180 (summer), F 40, J 30, K 100 = 0.45 GW.
# Jan: H (planned for 2025-12) comes online in 2026: +0.05. Feb: I pulled in from 2027 (+0.07), K resized
# 100 -> 120 (+0.02). Mar: G new (+0.06), J cancelled (IP, -0.03). Apr: F drops out of the inventory (-0.04),
# A comes online (stays in the book). May: B slips to 2027 (-0.18). August book: A, G, H, I, K = 0.40 GW.
RECORDS = [
    rec("2025-11-01", 13, "D", "OP", op="2020-01-01"),
    rec("2025-12-01", 1, "A", "P", planned="2026-03-01"),
    rec("2026-04-01", 1, "A", "OP", op="2026-03-01"),
    rec("2025-12-01", 2, "B", "U", planned="2026-06-01", mw=200.0, summer=180.0),
    rec("2026-05-01", 2, "B", "U", planned="2027-02-01", mw=200.0, summer=180.0),
    rec("2025-12-01", 6, "F", "T", planned="2026-02-01", mw=40.0, valid="2026-03-01"),
    rec("2026-03-01", 7, "G", "P", planned="2026-10-01", mw=60.0),
    rec("2025-12-01", 8, "H", "V", planned="2025-12-01", mw=50.0),
    rec("2026-01-01", 8, "H", "OP", op="2026-01-01", mw=50.0),
    rec("2025-12-01", 9, "I", "P", planned="2027-05-01", mw=70.0),
    rec("2026-02-01", 9, "I", "L", planned="2026-11-01", mw=70.0),
    rec("2025-12-01", 10, "J", "P", planned="2026-08-01", mw=30.0),
    rec("2026-03-01", 10, "J", "IP", mw=30.0),
    rec("2025-12-01", 11, "K", "V", planned="2026-09-01", mw=100.0),
    rec("2026-02-01", 11, "K", "V", planned="2026-09-01", mw=120.0),
    rec("2025-12-01", 12, "W", "P", tech="Onshore Wind Turbine", planned="2026-07-01", mw=50.0),
    rec("2026-08-01", 12, "W", "P", tech="Onshore Wind Turbine", planned="2027-01-01", mw=50.0),
    rec("2025-12-01", 14, "X", "P", tech="Batteries", planned="2026-03-01", mw=999.0),
]


def changelog():
    return pf.prepare(pd.DataFrame(RECORDS))


def book(st):
    return pf.gw(st.loc[st["state"].isin(pf.IN_BOOK), "cap"])


class States(unittest.TestCase):
    def test_december_book(self):
        st = pf.states(changelog(), M(2025, 12))
        self.assertAlmostEqual(book(st), 0.45)
        self.assertEqual(st.at["8/H", "state"], "planned_other")
        self.assertEqual(st.at["9/I", "state"], "planned_later")
        self.assertEqual(st.at["13/D", "state"], "online_other")
        self.assertNotIn("12/W", st.index)  # wind is read separately
        self.assertNotIn("14/X", st.index)

    def test_april_online_and_unlisted(self):
        st = pf.states(changelog(), M(2026, 4))
        self.assertEqual(st.at["1/A", "state"], "online_2026")
        self.assertEqual(st.at["10/J", "state"], "other_status")
        self.assertNotIn("6/F", st.index)
        self.assertAlmostEqual(book(st), 0.58)

    def test_march_still_lists_f(self):
        st = pf.states(changelog(), M(2026, 3))
        self.assertEqual(st.at["6/F", "state"], "planned_2026")  # valid through its valid_until month

    def test_wind(self):
        self.assertEqual(pf.states(changelog(), M(2026, 8), "wind").at["12/W", "state"], "planned_later")


class Split(unittest.TestCase):
    def setUp(self):
        self.df = changelog()

    def pair(self, a, b):
        return pf.split(pf.states(self.df, a), pf.states(self.df, b))

    def test_february_to_march(self):
        f = self.pair(M(2026, 2), M(2026, 3))
        self.assertAlmostEqual(f["book_prev"], 0.59)
        self.assertAlmostEqual(f["book_cur"], 0.62)
        self.assertAlmostEqual(f["in_not_listed"], 0.06)
        self.assertAlmostEqual(f["out_other_status"], 0.03)
        self.assertEqual(f["out_other_status_codes"], {"IP": 0.03})
        self.assertAlmostEqual(f["residual"], 0.0)

    def test_january_february_and_resize(self):
        jan = self.pair(M(2025, 12), M(2026, 1))
        self.assertAlmostEqual(jan["in_planned_other"], 0.05)
        self.assertAlmostEqual(jan["entries_online"], 0.05)
        feb = self.pair(M(2026, 1), M(2026, 2))
        self.assertAlmostEqual(feb["in_planned_later"], 0.07)
        self.assertAlmostEqual(feb["resize"], 0.02)
        self.assertAlmostEqual(feb["residual"], 0.0)

    def test_april_and_may(self):
        apr = self.pair(M(2026, 3), M(2026, 4))
        self.assertAlmostEqual(apr["out_not_listed"], 0.04)
        self.assertAlmostEqual(apr["came_online"], 0.1)
        self.assertEqual(apr["units_left"], 1)
        may = self.pair(M(2026, 4), M(2026, 5))
        self.assertAlmostEqual(may["out_planned_later"], 0.18)
        self.assertAlmostEqual(may["book_cur"], 0.40)


class Fate(unittest.TestCase):
    def test_december_book_in_august(self):
        df = changelog()
        fate = pf.book_fate(pf.states(df, M(2025, 12)), pf.states(df, M(2026, 8)))
        f = fate["fate"]
        self.assertAlmostEqual(f["online_2026"], 0.1)
        self.assertAlmostEqual(f["planned_2026"], 0.1)  # K at its December 100 MW
        self.assertAlmostEqual(f["planned_later"], 0.18)
        self.assertAlmostEqual(f["other_status"], 0.03)
        self.assertAlmostEqual(f["not_listed"], 0.04)
        self.assertAlmostEqual(sum(f.values()), 0.45)
        self.assertAlmostEqual(fate["entries"]["not_listed"], 0.06)
        self.assertAlmostEqual(fate["entries"]["planned_other"], 0.05)
        self.assertAlmostEqual(fate["entries"]["planned_later"], 0.07)
        self.assertAlmostEqual(fate["entries_total"], 0.18)
        self.assertAlmostEqual(fate["entries_online"], 0.05)
        self.assertAlmostEqual(fate["resize"], 0.02)
        self.assertEqual(fate["entries_units"], 3)
        self.assertAlmostEqual(fate["by_base_status"]["P"]["base_gw"], 0.13)
        self.assertAlmostEqual(fate["by_base_status"]["P"]["online_2026"], 0.1)
        self.assertAlmostEqual(fate["by_base_status"]["U"]["planned_later"], 0.18)
        self.assertAlmostEqual(fate["other_status_codes"]["IP"], 0.03)


class Summary(unittest.TestCase):
    def test_checks_and_predictions(self):
        flows, fate, wind_fate, s, gens, bk, latest_m = pf.run(changelog())
        self.assertEqual(latest_m, M(2026, 8))
        self.assertEqual([f["report"] for f in flows][:2], ["2025-12", "2026-01"])
        self.assertEqual(len(flows), 9)  # 2025-11 to 2026-08
        self.assertTrue(s["checks"]["C1"]["passed"])
        self.assertEqual(s["checks"]["C2"]["reports_compared"], 10)
        self.assertFalse(s["checks"]["C2"]["passed"])  # not the real data
        self.assertTrue(s["checks"]["C3"]["passed"])
        p = s["predictions"]
        self.assertFalse(p["F1"]["held"])
        self.assertFalse(p["F2"]["held"])
        self.assertTrue(p["F3"]["held"])  # 0.1 of 0.45
        self.assertTrue(p["F4"]["held"])  # 0.07 against 0.18
        self.assertAlmostEqual(p["F5"]["building_gw"], 0.28)
        self.assertAlmostEqual(p["F5"]["building_online_share"], 0.0)
        self.assertFalse(p["F5"]["held"])
        self.assertAlmostEqual(wind_fate["fate"]["planned_later"], 0.05)
        self.assertEqual(len(gens), 8)  # A, B, F, G, H, I, J, K
        self.assertEqual(bk["2026-08"], 0.4)


class EndToEnd(unittest.TestCase):
    def test_main_writes_outputs(self):
        raw = pd.DataFrame(RECORDS)
        for c in ("report_date", "current_planned_generator_operating_date", "generator_operating_date",
                  "valid_until_date"):
            raw[c] = pd.to_datetime(raw[c])
        with tempfile.TemporaryDirectory() as d:
            data, out = os.path.join(d, "data"), os.path.join(d, "out")
            os.makedirs(data)
            raw.to_parquet(os.path.join(data, "core_eia860m__changelog_generators.parquet"))
            self.assertEqual(pf.main(["--data-dir", data, "--out-dir", out]), 0)
            with open(os.path.join(out, "plan_flows.json"), encoding="utf-8") as fh:
                j = json.load(fh)
            self.assertEqual(j["summary"]["latest_report_used"], "2026-08")
            self.assertAlmostEqual(j["fate"]["fate"]["planned_later"], 0.18)
            with open(os.path.join(out, "plan_flows_generators.csv"), encoding="utf-8") as fh:
                rows = list(csv.DictReader(fh))
            b = next(r for r in rows if r["generator_id"] == "B")
            self.assertEqual((b["base_planned"], b["latest_state"], b["latest_planned"]),
                             ("2026-06", "planned_later", "2027-02"))
            g = next(r for r in rows if r["generator_id"] == "G")
            self.assertEqual((g["base_state"], g["latest_state"]), ("not_listed", "planned_2026"))
            with open(os.path.join(out, "plan_flows.md"), encoding="utf-8") as fh:
                self.assertIn("| 2026-05 | 0.40 | -0.18 |", fh.read())


if __name__ == "__main__":
    unittest.main()
