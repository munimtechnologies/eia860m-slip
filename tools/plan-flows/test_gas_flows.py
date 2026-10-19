"""Tests for gas_flows (MV2 of Munim, Inc.; made with AI agents). Apache-2.0."""

import json
import os
import tempfile
import unittest

import numpy as np
import pandas as pd

import gas_flows as gf
import plan_flows as pf

M = lambda y, mo: y * 12 + mo - 1  # noqa: E731
CC = "Natural Gas Fired Combined Cycle"
CT = "Natural Gas Fired Combustion Turbine"
PV = "Solar Photovoltaic"


def rec(report, plant, gen, status, tech, planned=None, op=None, mw=100.0, valid=np.nan, name=None):
    return {"report_date": report, "valid_until_date": valid, "plant_id_eia": plant, "generator_id": gen,
            "capacity_mw": mw, "summer_capacity_mw": mw, "current_planned_generator_operating_date": planned,
            "generator_operating_date": op, "operational_status_code": status, "technology_description": tech,
            "plant_name_eia": name or "Plant %d" % plant}


# Traced by hand. December 2025 gas book: CC1 900 (TS, January 2026), OC1 1100 (U, August 2026), CT1 200 (P,
# December 2026), CT2 150 (V, April 2026), CT3 100 (L, October 2026) = 2.45 GW. ST1 has run since 2010 (online
# outside 2026); CAES is compressed-air storage and is not read. Feb: CC1 online since January (+0 to the book,
# came online 0.9). Mar: ICE1 newly listed (+0.05). Apr: CT3 drops out of the inventory (-0.10). May: CT1 slips
# to June 2027 (-0.20); CT2 online since April. Jun: OC1 moves to testing, September 2026 (no flow). August
# book: CC1, OC1, CT2, ICE1 = 2.20 GW. Solar PV1 stays planned for 2026; battery BA1 too; wind W1 comes online.
RECORDS = [
    rec("2025-11-01", 8, "ST1", "OP", "Natural Gas Steam Turbine", op="2010-01-01", mw=400.0),
    rec("2025-12-01", 1, "CC1", "TS", CC, planned="2026-01-01", mw=900.0, name="Trumbull Energy Center"),
    rec("2026-02-01", 1, "CC1", "OP", CC, op="2026-01-15", mw=900.0, name="Trumbull Energy Center"),
    rec("2025-12-01", 2, "OC1", "U", CC, planned="2026-08-01", mw=1100.0, name="Orange County Advanced Power Station"),
    rec("2026-06-01", 2, "OC1", "TS", CC, planned="2026-09-01", mw=1100.0, name="Orange County Advanced Power Station"),
    rec("2025-12-01", 3, "CT1", "P", CT, planned="2026-12-01", mw=200.0),
    rec("2026-05-01", 3, "CT1", "P", CT, planned="2027-06-01", mw=200.0),
    rec("2025-12-01", 4, "CT2", "V", CT, planned="2026-04-01", mw=150.0),
    rec("2026-05-01", 4, "CT2", "OP", CT, op="2026-04-20", mw=150.0),
    rec("2025-12-01", 5, "CT3", "L", CT, planned="2026-10-01", mw=100.0, valid="2026-03-01"),
    rec("2026-03-01", 6, "ICE1", "U", "Natural Gas Internal Combustion Engine", planned="2026-11-01", mw=50.0),
    rec("2025-12-01", 7, "CAES", "P", "Natural Gas with Compressed Air Storage", planned="2026-06-01", mw=300.0),
    rec("2025-12-01", 9, "PV1", "U", PV, planned="2026-06-01", mw=200.0),
    rec("2026-08-01", 9, "PV1", "U", PV, planned="2026-11-01", mw=200.0),
    rec("2025-12-01", 9, "BA1", "U", "Batteries", planned="2026-06-01", mw=50.0),
    rec("2025-12-01", 10, "W1", "T", "Onshore Wind Turbine", planned="2026-03-01", mw=80.0),
    rec("2026-04-01", 10, "W1", "OP", "Onshore Wind Turbine", op="2026-03-10", mw=80.0),
]


def changelog():
    return pf.prepare(pd.DataFrame(RECORDS))


class Reading(unittest.TestCase):
    def test_gas_states(self):
        df = changelog()
        gas = pf.states(df, M(2025, 12), gf.GAS)
        self.assertEqual(sorted(gas.index), ["1/CC1", "2/OC1", "3/CT1", "4/CT2", "5/CT3", "8/ST1"])
        self.assertEqual(gas.at["1/CC1", "state"], "planned_2026")
        self.assertEqual(gas.at["8/ST1", "state"], "online_other")
        self.assertNotIn("7/CAES", df["key"].tolist())
        self.assertEqual(sorted(pf.states(df, M(2025, 12)).index), ["9/PV1"])
        self.assertEqual(pf.states(df, M(2026, 8), "wind").at["10/W1", "state"], "online_2026")

    def test_subtypes(self):
        self.assertEqual(gf.subtypes(changelog()), {"1/CC1": "cc", "2/OC1": "cc", "3/CT1": "ct", "4/CT2": "ct",
                                                     "5/CT3": "ct", "6/ICE1": "other", "8/ST1": "other"})

    def test_plant_names_and_census(self):
        raw = pd.DataFrame(RECORDS)
        names = gf.plant_names(raw)
        self.assertEqual(names["1"], "Trumbull Energy Center")
        self.assertEqual(names["3"], "Plant 3")
        self.assertEqual(gf.plant_names(raw.drop(columns=["plant_name_eia"])), {})
        self.assertEqual(gf.tech_census(raw), {CC: 4, CT: 5, "Natural Gas Internal Combustion Engine": 1,
                                               "Natural Gas Steam Turbine": 1,
                                               "Natural Gas with Compressed Air Storage": 1})


class Run(unittest.TestCase):
    def setUp(self):
        self.names = gf.plant_names(pd.DataFrame(RECORDS))
        (self.flows, self.fate, self.cross, self.stages, self.subs, self.named, self.s, self.gens, self.book,
         self.latest_m) = gf.run(changelog(), self.names)

    def test_fate(self):
        f = self.fate["fate"]
        self.assertEqual(self.latest_m, M(2026, 8))
        self.assertAlmostEqual(self.fate["base_book"], 2.45)
        self.assertAlmostEqual(self.fate["latest_book"], 2.20)
        self.assertAlmostEqual(f["online_2026"], 1.05)
        self.assertAlmostEqual(f["planned_2026"], 1.10)
        self.assertAlmostEqual(f["planned_later"], 0.20)
        self.assertAlmostEqual(f["not_listed"], 0.10)
        self.assertAlmostEqual(f["online_other"], 0.0)
        self.assertAlmostEqual(self.fate["entries"]["not_listed"], 0.05)
        self.assertAlmostEqual(self.fate["entries_total"], 0.05)
        self.assertEqual(len(self.gens), 6)
        self.assertEqual([g["subtype"] for g in self.gens], ["cc", "cc", "ct", "ct", "ct", "other"])

    def test_flows(self):
        self.assertEqual(len(self.flows), 9)  # 2025-11 to 2026-08
        by = {f["report"]: f for f in self.flows}
        self.assertAlmostEqual(by["2025-12"]["in_not_listed"], 2.45)
        self.assertAlmostEqual(by["2026-02"]["came_online"], 0.9)
        self.assertAlmostEqual(by["2026-03"]["in_not_listed"], 0.05)
        self.assertAlmostEqual(by["2026-03"]["book_cur"], 2.50)
        self.assertAlmostEqual(by["2026-04"]["out_not_listed"], 0.10)
        self.assertAlmostEqual(by["2026-04"]["book_cur"], 2.40)
        self.assertAlmostEqual(by["2026-05"]["out_planned_later"], 0.20)
        self.assertAlmostEqual(by["2026-05"]["came_online"], 0.15)
        self.assertAlmostEqual(by["2026-05"]["book_cur"], 2.20)
        self.assertAlmostEqual(by["2026-06"]["entries"] + by["2026-06"]["exits"], 0.0)
        self.assertEqual(self.book["2025-11"], 0.0)
        self.assertEqual(self.book["2026-08"], 2.20)

    def test_stages_and_subtypes(self):
        b, e = self.stages["building"], self.stages["early"]
        self.assertAlmostEqual(b["base_gw"], 2.15)
        self.assertAlmostEqual(b["online_share"], 1.05 / 2.15)
        self.assertAlmostEqual(b["later_share"], 0.0)
        self.assertAlmostEqual(b["gone_share"], 0.0)
        self.assertAlmostEqual(e["base_gw"], 0.30)
        self.assertAlmostEqual(e["later_share"], 0.2 / 0.3)
        self.assertAlmostEqual(e["gone_share"], 0.1 / 0.3)
        cc, ct, other = self.subs["cc"], self.subs["ct"], self.subs["other"]
        self.assertAlmostEqual(cc["base_book"], 2.0)
        self.assertAlmostEqual(cc["fate"]["online_2026"], 0.9)
        self.assertAlmostEqual(cc["fate"]["planned_2026"], 1.1)
        self.assertAlmostEqual(cc["latest_book"], 2.0)
        self.assertAlmostEqual(ct["base_book"], 0.45)
        self.assertAlmostEqual(ct["fate"]["online_2026"], 0.15)
        self.assertAlmostEqual(ct["fate"]["planned_later"], 0.2)
        self.assertAlmostEqual(ct["fate"]["not_listed"], 0.1)
        self.assertAlmostEqual(ct["latest_book"], 0.15)
        self.assertAlmostEqual(other["base_book"], 0.0)
        self.assertAlmostEqual(other["latest_book"], 0.05)
        self.assertAlmostEqual(other["entries"]["not_listed"], 0.05)

    def test_cross(self):
        self.assertAlmostEqual(self.cross["solar"]["base_book"], 0.2)
        self.assertAlmostEqual(self.cross["solar"]["fate"]["planned_2026"], 0.2)
        self.assertAlmostEqual(self.cross["wind"]["base_book"], 0.08)
        self.assertAlmostEqual(self.cross["wind"]["fate"]["online_2026"], 0.08)
        self.assertAlmostEqual(self.cross[gf.BATTERY]["fate"]["planned_2026"], 0.05)
        self.assertAlmostEqual(self.cross[gf.GAS]["base_book"], 2.45)
        self.assertAlmostEqual(gf.left_share(self.cross[gf.GAS]), 0.3 / 2.45)

    def test_named(self):
        tr, oc = self.named["trumbull"], self.named["orange_county"]
        self.assertEqual(tr["plants"], {"1": "Trumbull Energy Center"})
        self.assertEqual(oc["plants"], {"2": "Orange County Advanced Power Station"})
        self.assertEqual([(g["generator_id"], g["latest_state"], g["latest_online"]) for g in tr["generators"]],
                         [("CC1", "online_2026", "2026-01")])
        self.assertEqual([(g["generator_id"], g["latest_state"], g["latest_status"], g["latest_planned"])
                          for g in oc["generators"]], [("OC1", "planned_2026", "TS", "2026-09")])

    def test_checks_and_predictions(self):
        c, p = self.s["checks"], self.s["predictions"]
        self.assertTrue(c["K1"]["passed"])
        self.assertTrue(c["K2"]["passed"])
        self.assertFalse(c["K3"]["passed"])  # not the real data
        self.assertFalse(c["K4"]["passed"])  # 2.45 GW is not within 20% of 6.3
        self.assertTrue(p["G1"]["held"])   # 1.05 of 2.45
        self.assertTrue(p["G2"]["held"])   # 0.20 of 2.45
        self.assertTrue(p["G3"]["held"])   # 0.10 of 2.45
        self.assertTrue(p["G4"]["held"])   # cc 0.45 against ct 0.3333
        self.assertAlmostEqual(p["G4"]["ct_online_share"], round(0.15 / 0.45, 4))
        self.assertTrue(p["G5"]["held"])   # early left 1.0; building later 0.0
        self.assertTrue(p["G6"]["held"])
        self.assertEqual([g["generator_id"] for g in gf.movers(self.gens)], ["CT1", "CT3"])


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
            self.assertEqual(gf.main(["--data-dir", data, "--out-dir", out]), 0)
            with open(os.path.join(out, "gas_flows.json"), encoding="utf-8") as fh:
                j = json.load(fh)
            self.assertEqual(j["summary"]["technology_census"][CC], 4)
            self.assertEqual(j["summary"]["technology_census"]["Natural Gas with Compressed Air Storage"], 1)
            self.assertAlmostEqual(j["fate"]["fate"]["planned_later"], 0.2)
            recs = j["named"]["orange_county"]["records"]
            self.assertEqual(len(recs), 2)
            self.assertEqual(recs[0]["report_date"], "2025-12-01")
            self.assertEqual(recs[1]["operational_status_code"], "TS")
            self.assertEqual(recs[1]["current_planned_generator_operating_date"], "2026-09-01")
            self.assertEqual(recs[1]["valid_until_date"], "")
            self.assertEqual(len(j["named"]["trumbull"]["records"]), 2)
            with open(os.path.join(out, "gas_flows.md"), encoding="utf-8") as fh:
                md = fh.read()
            self.assertIn("| 2026-05 | 2.20 | -0.20 |", md)
            self.assertIn("| 3 | CT1 | ct | P | 2026-12 | 200.0 | planned_later | 2027-06 |", md)
            self.assertIn("| gas | 2.45 | ", md)
            self.assertIn("Trumbull Energy Center", md)
            for name in ("gas_flows.csv", "gas_flows_generators.csv"):
                self.assertTrue(os.path.exists(os.path.join(out, name)))


if __name__ == "__main__":
    unittest.main()
