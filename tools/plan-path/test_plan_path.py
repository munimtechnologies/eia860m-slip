"""Tests for plan_path (MV2 of Munim, Inc.; made with AI agents). Apache-2.0."""

import json
import os
import tempfile
import unittest

import numpy as np
import pandas as pd

import plan_path as pp

M = lambda y, mo: y * 12 + mo - 1  # noqa: E731

# Lines as the January 2026 edition's page text gives them (jan26.txt, page 52), plus a
# generation-table page whose "Wind" row must not be taken.
GEN_PAGE = ("Wind .................................... 133.5 118.5 84.7 128.0 140.6 125.1 91.9 135.4 149.0 131.7 "
            "96.7 143.2 464.7 493.0 520.6\nSolar photovoltaic systems smaller than one megawatt 12.0 GW\n")
CAP_PAGE = ("Q1 Q2 Q3 Q4 Q1 Q2 Q3 Q4 Q1 Q2 Q3 Q4 2025 2026 2027\n"
            "Wind ................................................. 153.7 154.7 155.3 160.4 161.2 165.1 165.7 170.1 "
            "170.7 171.3 171.3 173.9 160.4 170.1 173.9\n"
            "Solar photovoltaic ............................ 119.5 124.9 130.4 139.2 147.7 153.2 157.1 171.3 176.0 "
            "187.2 194.2 207.8 139.2 171.3 207.8\n"
            "Solar thermal .................................... 1.4 1.4 1.4 1.4 1.4 1.4 1.4 1.4 1.4 1.6 1.6 1.6 1.4 "
            "1.4 1.6\n"
            "Wind ................................................. 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 "
            "0.1 0.1 0.1\n")
TEXT = "\n===== page 1 =====\n" + GEN_PAGE + "\n===== page 2 =====\n" + CAP_PAGE


def rec(report, plant, gen, status, tech="Solar Photovoltaic", planned=None, op=None, mw=100.0, summer=None):
    return {"report_date": report, "valid_until_date": np.nan, "plant_id_eia": plant, "generator_id": gen,
            "capacity_mw": mw, "summer_capacity_mw": mw if summer is None else summer,
            "current_planned_generator_operating_date": planned, "generator_operating_date": op,
            "operational_status_code": status, "technology_description": tech}


def changelog():
    return pp.prepare(pd.DataFrame([
        rec("2025-11-01", 1, "A", "P", planned="2026-03-01"),
        rec("2026-04-01", 1, "A", "OP", op="2026-03-01"),
        rec("2025-11-01", 2, "B", "U", planned="2026-06-01", mw=200.0, summer=180.0),
        rec("2026-05-01", 2, "B", "U", planned="2027-02-01", mw=200.0, summer=180.0),
        rec("2025-12-01", 3, "C", "P", tech="Onshore Wind Turbine", planned="2026-09-01", mw=50.0),
        rec("2025-11-01", 4, "D", "OP", op="2020-01-01"),
        rec("2025-11-01", 5, "E", "U", planned="2025-12-01"),
        rec("2025-11-01", 6, "F", "T", planned="2026-02-01", mw=40.0),
        rec("2025-11-01", 7, "G", "P", tech="Batteries", planned="2026-03-01", mw=999.0),
    ]))


class SteoRows(unittest.TestCase):
    def test_capacity_rows(self):
        rows = pp.steo_rows(TEXT)
        self.assertEqual(rows["solar"], (139.2, 171.3, 207.8))
        self.assertEqual(rows["wind"], (160.4, 170.1, 173.9))

    def test_no_table(self):
        self.assertEqual(pp.steo_rows("\n===== page 1 =====\n" + GEN_PAGE), {})

    def test_edition_month_and_pairing(self):
        self.assertEqual(pp.edition_month("oct26"), M(2026, 10))
        self.assertEqual(pp.edition_month("Jan26"), M(2026, 1))
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "jan26.txt"), "w", encoding="utf-8") as fh:
                fh.write(TEXT)
            out = pp.read_steo(d, ["jan26", "feb26"])
        self.assertEqual(out[0]["pairs_with_report"], "2025-11")
        self.assertEqual(out[0]["solar_2026"], 32.1)
        self.assertEqual(out[0]["wind_2026"], 9.7)
        self.assertEqual(out[1]["error"], "no page text")


class PlanSide(unittest.TestCase):
    def test_only_solar_and_wind_kept(self):
        self.assertEqual(sorted(set(changelog()["tech"])), ["solar", "wind"])

    def test_december(self):
        r = pp.path_row(changelog(), M(2025, 12))
        self.assertEqual(r["solar_added_nameplate"], 0.0)
        self.assertAlmostEqual(r["solar_planned_nameplate"], 0.34)  # A, B, F; not E (2025) or D
        self.assertAlmostEqual(r["solar_planned_summer"], 0.32)
        self.assertAlmostEqual(r["wind_planned_nameplate"], 0.05)
        self.assertEqual(r["solar_planned_units"], 3)
        self.assertEqual(r["solar_overdue_nameplate"], 0.0)

    def test_april_online_and_overdue(self):
        r = pp.path_row(changelog(), M(2026, 4))
        self.assertAlmostEqual(r["solar_added_nameplate"], 0.1)
        self.assertAlmostEqual(r["solar_planned_nameplate"], 0.24)  # B and F
        self.assertAlmostEqual(r["solar_implied_nameplate"], 0.34)
        self.assertAlmostEqual(r["solar_overdue_nameplate"], 0.04)  # F, planned February
        self.assertEqual(r["report"], "2026-04")

    def test_may_slip(self):
        r = pp.path_row(changelog(), M(2026, 5))
        self.assertAlmostEqual(r["solar_planned_nameplate"], 0.04)
        self.assertAlmostEqual(r["solar_implied_nameplate"], 0.14)

    def test_snapshot_drops_expired_records(self):
        df = pp.prepare(pd.DataFrame([dict(rec("2025-11-01", 8, "H", "P", planned="2026-05-01"),
                                           valid_until_date="2026-01-01")]))
        self.assertEqual(len(pp.snapshot(df, M(2026, 1))), 1)
        self.assertEqual(len(pp.snapshot(df, M(2026, 2))), 0)

    def test_online_month_from_first_operating_report(self):
        df = pp.prepare(pd.DataFrame([rec("2025-11-01", 9, "I", "U", planned="2026-01-01"),
                                      rec("2026-02-01", 9, "I", "OP")]))
        self.assertAlmostEqual(pp.path_row(df, M(2026, 2))["solar_added_nameplate"], 0.1)


class Summary(unittest.TestCase):
    def test_checks_and_predictions(self):
        rows = [pp.path_row(changelog(), m) for m in range(M(2025, 11), M(2026, 6) + 1)]
        steo = [{"edition": "jan26", "pairs_with_report": "2025-11", "solar_end_2025": 139.2, "solar_end_2026": 171.3,
                 "solar_2026": 32.1, "wind_end_2025": 160.4, "wind_end_2026": 170.1, "wind_2026": 9.7},
                {"edition": "feb26", "pairs_with_report": "2025-12", "solar_2026": 0.2, "solar_end_2025": 139.2},
                {"edition": "apr26", "pairs_with_report": "2026-02", "solar_2026": 0.3, "solar_end_2025": 139.2}]
        s = pp.summarize(rows, steo)
        self.assertEqual(s["measure"], "nameplate")  # 0.34 is nearer 43.4 than 0.32
        self.assertFalse(s["checks"]["C1"]["passed"])
        self.assertTrue(s["checks"]["C2"]["jan26_reproduced"])
        self.assertFalse(s["checks"]["C2"]["passed"])  # only 3 sane editions
        self.assertTrue(s["checks"]["C3"]["passed"])
        self.assertEqual([p["edition"] for p in s["pairs"]], ["jan26", "feb26", "apr26"])
        self.assertAlmostEqual(s["pairs"][1]["gap_gw"], 0.14)
        self.assertAlmostEqual(s["predictions"]["P1"]["drop_gw"], 0.2)
        self.assertFalse(s["predictions"]["P1"]["held"])
        self.assertFalse(s["predictions"]["P2"]["held"])
        self.assertAlmostEqual(s["predictions"]["P4"]["change_gw"], -31.8)
        self.assertEqual(s["predictions"]["P5"]["latest_report"], "2026-06")


class EndToEnd(unittest.TestCase):
    def test_main_writes_outputs(self):
        raw = pd.DataFrame([rec("2025-11-01", 1, "A", "P", planned="2026-03-01"),
                            rec("2026-04-01", 1, "A", "OP", op="2026-03-01")])
        for c in ("report_date", "current_planned_generator_operating_date", "generator_operating_date"):
            raw[c] = pd.to_datetime(raw[c])
        with tempfile.TemporaryDirectory() as d:
            data, out = os.path.join(d, "data"), os.path.join(d, "out")
            os.makedirs(data)
            os.makedirs(out)
            raw.to_parquet(os.path.join(data, "core_eia860m__changelog_generators.parquet"))
            with open(os.path.join(out, "jan26.txt"), "w", encoding="utf-8") as fh:
                fh.write(TEXT)
            self.assertEqual(pp.main(["--data-dir", data, "--steo-dir", out, "--out-dir", out, "jan26"]), 0)
            with open(os.path.join(out, "plan_path.json"), encoding="utf-8") as fh:
                j = json.load(fh)
            self.assertEqual(j["summary"]["last_report"], "2026-04")
            self.assertEqual(len(j["path"]), 6)  # 2025-11 to 2026-04
            self.assertEqual(j["steo"][0]["solar_2026"], 32.1)
            with open(os.path.join(out, "plan_path.md"), encoding="utf-8") as fh:
                self.assertIn("| jan26 | 2025-11 | 32.1 |", fh.read())


if __name__ == "__main__":
    unittest.main()
