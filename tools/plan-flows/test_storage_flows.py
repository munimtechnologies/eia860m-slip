"""Tests for storage_flows (MV2 of Munim, Inc.; made with AI agents). Apache-2.0."""

import json
import os
import tempfile
import unittest

import numpy as np
import pandas as pd

import plan_flows as pf
import storage_flows as sf

M = lambda y, mo: y * 12 + mo - 1  # noqa: E731


def rec(report, plant, gen, status, tech="Batteries", planned=None, op=None, mw=100.0, valid=np.nan):
    return {"report_date": report, "valid_until_date": valid, "plant_id_eia": plant, "generator_id": gen,
            "capacity_mw": mw, "summer_capacity_mw": mw, "current_planned_generator_operating_date": planned,
            "generator_operating_date": op, "operational_status_code": status, "technology_description": tech}


PV = "Solar Photovoltaic"
# Traced by hand. December 2025 battery book: BA1 100, BA2 80, BA3 40, BA4 60 = 0.28 GW (BA6 is 2027, OLD
# online since 2020). Feb: BA6 pulled in from 2027 (+0.07). Apr: BA3 drops out of the inventory (-0.04), BA5
# new (+0.03). May: BA2 slips to 2027 (-0.08). Jul: BA1 comes online. August book: BA1, BA4, BA5, BA6 = 0.26.
# Solar leads: plant 1 PV1 (200 > PV1B 20) online by August, plant 2 PV2 slipped to 2027, plant 3 PV3 still
# 2026. So BA1 and BA2 agree with their plant's solar, BA3 does not, BA4 has no solar.
RECORDS = [
    rec("2025-11-01", 9, "OLD", "OP", op="2020-01-01", mw=10.0),
    rec("2025-12-01", 1, "BA1", "U", planned="2026-06-01", mw=100.0),
    rec("2026-07-01", 1, "BA1", "OP", op="2026-06-01", mw=100.0),
    rec("2025-12-01", 2, "BA2", "P", planned="2026-09-01", mw=80.0),
    rec("2026-05-01", 2, "BA2", "P", planned="2027-03-01", mw=80.0),
    rec("2025-12-01", 3, "BA3", "V", planned="2026-10-01", mw=40.0, valid="2026-03-01"),
    rec("2025-12-01", 4, "BA4", "T", planned="2026-12-01", mw=60.0),
    rec("2026-04-01", 5, "BA5", "P", planned="2026-11-01", mw=30.0),
    rec("2025-12-01", 6, "BA6", "L", planned="2027-06-01", mw=70.0),
    rec("2026-02-01", 6, "BA6", "L", planned="2026-12-01", mw=70.0),
    rec("2025-12-01", 1, "PV1", "U", tech=PV, planned="2026-06-01", mw=200.0),
    rec("2026-07-01", 1, "PV1", "OP", tech=PV, op="2026-05-01", mw=200.0),
    rec("2025-12-01", 1, "PV1B", "L", tech=PV, planned="2026-11-01", mw=20.0, valid="2026-04-01"),
    rec("2025-12-01", 2, "PV2", "P", tech=PV, planned="2026-09-01", mw=100.0),
    rec("2026-08-01", 2, "PV2", "P", tech=PV, planned="2027-03-01", mw=100.0),
    rec("2025-12-01", 3, "PV3", "V", tech=PV, planned="2026-10-01", mw=50.0),
    rec("2025-12-01", 7, "GAS", "P", tech="Natural Gas Fired Combined Cycle", planned="2026-05-01", mw=500.0),
]


def changelog():
    return pf.prepare(pd.DataFrame(RECORDS))


class Reading(unittest.TestCase):
    def test_batteries_read_solar_unchanged(self):
        df = changelog()
        bat = pf.states(df, M(2025, 12), sf.BATTERY)
        self.assertEqual(sorted(bat.index), ["1/BA1", "2/BA2", "3/BA3", "4/BA4", "6/BA6", "9/OLD"])
        self.assertEqual(bat.at["6/BA6", "state"], "planned_later")
        self.assertEqual(bat.at["9/OLD", "state"], "online_other")
        sol = pf.states(df, M(2025, 12))
        self.assertEqual(sorted(sol.index), ["1/PV1", "1/PV1B", "2/PV2", "3/PV3"])
        self.assertNotIn("7/GAS", df["key"].tolist())

    def test_lead_states(self):
        df = changelog()
        lead = sf.lead_states(pf.states(df, M(2025, 12)), pf.states(df, M(2026, 8)))
        self.assertEqual(lead, {"1": "online_2026", "2": "planned_later", "3": "planned_2026"})


class Run(unittest.TestCase):
    def setUp(self):
        self.flows, self.fate, self.stages, self.pair, self.s, self.gens, self.book, self.latest_m = \
            sf.run(changelog())

    def test_fate(self):
        f = self.fate["fate"]
        self.assertEqual(self.latest_m, M(2026, 8))
        self.assertAlmostEqual(self.fate["base_book"], 0.28)
        self.assertAlmostEqual(self.fate["latest_book"], 0.26)
        self.assertAlmostEqual(f["online_2026"], 0.1)
        self.assertAlmostEqual(f["planned_2026"], 0.06)
        self.assertAlmostEqual(f["planned_later"], 0.08)
        self.assertAlmostEqual(f["not_listed"], 0.04)
        self.assertAlmostEqual(self.fate["entries"]["not_listed"], 0.03)
        self.assertAlmostEqual(self.fate["entries"]["planned_later"], 0.07)
        self.assertAlmostEqual(self.fate["entries_total"], 0.1)
        self.assertEqual(len(self.gens), 6)

    def test_flows(self):
        self.assertEqual(len(self.flows), 9)  # 2025-11 to 2026-08
        by = {f["report"]: f for f in self.flows}
        self.assertAlmostEqual(by["2025-12"]["in_not_listed"], 0.28)
        self.assertAlmostEqual(by["2026-02"]["in_planned_later"], 0.07)
        self.assertAlmostEqual(by["2026-04"]["out_not_listed"], 0.04)
        self.assertAlmostEqual(by["2026-04"]["in_not_listed"], 0.03)
        self.assertAlmostEqual(by["2026-04"]["book_cur"], 0.34)
        self.assertAlmostEqual(by["2026-05"]["out_planned_later"], 0.08)
        self.assertAlmostEqual(by["2026-07"]["came_online"], 0.1)
        self.assertEqual(self.book["2025-11"], 0.0)
        self.assertEqual(self.book["2026-08"], 0.26)

    def test_stages(self):
        b, e = self.stages["building"], self.stages["early"]
        self.assertAlmostEqual(b["base_gw"], 0.14)
        self.assertAlmostEqual(b["online_share"], 0.1 / 0.14)
        self.assertAlmostEqual(b["gone_share"], 0.04 / 0.14)
        self.assertAlmostEqual(b["later_share"], 0.0)
        self.assertAlmostEqual(e["base_gw"], 0.08)
        self.assertAlmostEqual(e["later_share"], 1.0)

    def test_paired(self):
        p = self.pair
        self.assertAlmostEqual(p["paired_gw"], 0.22)
        self.assertAlmostEqual(p["agree_gw"], 0.18)
        self.assertAlmostEqual(p["matrix"]["online_2026"]["online_2026"], 0.1)
        self.assertAlmostEqual(p["matrix"]["planned_later"]["planned_later"], 0.08)
        self.assertAlmostEqual(p["matrix"]["other"]["planned_2026"], 0.04)
        self.assertAlmostEqual(p["alone"]["planned_2026"], 0.06)
        self.assertEqual(p["units"], {"paired": 3, "alone": 1})

    def test_checks_and_predictions(self):
        c, p = self.s["checks"], self.s["predictions"]
        self.assertTrue(c["K1"]["passed"])
        self.assertTrue(c["K2"]["passed"])
        self.assertFalse(c["K3"]["passed"])  # not the real data
        self.assertFalse(c["K4"]["passed"])
        self.assertTrue(p["B1"]["held"])   # 0.08 of 0.28
        self.assertFalse(p["B2"]["held"])  # 0.1 of 0.28 is not under 35%
        self.assertTrue(p["B3"]["held"])   # 0.04 against 0.08
        self.assertTrue(p["B4"]["held"])
        self.assertTrue(p["B5"]["held"])   # 0.10 of 0.26
        self.assertTrue(p["B6"]["held"])   # 0.18 of 0.22
        self.assertEqual([g["generator_id"] for g in sf.movers(self.gens)], ["BA2", "BA3"])


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
            self.assertEqual(sf.main(["--data-dir", data, "--out-dir", out]), 0)
            with open(os.path.join(out, "storage_flows.json"), encoding="utf-8") as fh:
                j = json.load(fh)
            self.assertEqual(j["summary"]["technology_census"], {"Batteries": 10})
            self.assertAlmostEqual(j["fate"]["fate"]["planned_later"], 0.08)
            with open(os.path.join(out, "storage_flows.md"), encoding="utf-8") as fh:
                md = fh.read()
            self.assertIn("| 2026-05 | 0.26 | -0.08 |", md)
            self.assertIn("| 2 | BA2 | P | 2026-09 | 80.0 | planned_later | 2027-03 |", md)
            for name in ("storage_flows.csv", "storage_flows_generators.csv"):
                self.assertTrue(os.path.exists(os.path.join(out, name)))


if __name__ == "__main__":
    unittest.main()
