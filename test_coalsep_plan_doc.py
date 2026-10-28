"""Checks docs/coalsep-plan.md against the two CSVs it names.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import csv
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


def rows(path):
    with open(os.path.join(HERE, path), encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


class CoalsepPlanDocTests(unittest.TestCase):
    def setUp(self):
        self.doc = read("docs/coalsep-plan.md")

    def test_status_and_bars(self):
        self.assertIn("Status: pre-registered, not yet scored.", self.doc)
        self.assertIn("| S1 | No coal row on the Retired sheet has retirement year 2026. | about 85% |", self.doc)
        self.assertIn("Sherburne County 1 (6090/1) and Comanche 2 (470/2) are both still dated 2026-12.", self.doc)
        self.assertIn("totals 3,000 to 4,500 MW, and at least 60% of it is at plants under DOE orders.", self.doc)
        self.assertIn("at least 15 of the 16 plan generators", self.doc)

    def test_plan_matches_followup_csv(self):
        plan = rows("data/coal_plan_2026_followup.csv")
        self.assertEqual(len(plan), 16)
        self.assertIn("The 16 generators (6,354.4 MW)".lower(), self.doc.lower())
        total = sum(float(r["mw"]) for r in plan)
        self.assertEqual("{:,.1f}".format(total), "6,354.4")
        by_key = {r["key"]: r for r in plan}
        for key, mw in (("6090/1", "680.0"), ("470/2", "335.0")):
            self.assertEqual(by_key[key]["planned_now"], "2026-12")
            self.assertEqual("{:.1f}".format(float(by_key[key]["mw"])), mw)
            self.assertIn("(%s MW)" % mw, self.doc)

    def test_order_plants_match_orders_csv(self):
        keys = {r["plant_key"] for r in rows("data/doe_202c_orders.csv") if r["kind"] == "plant"}
        self.assertEqual(keys, {"campbell", "eddystone", "wagner", "centralia", "schahfer", "culley", "craig",
                                "stanton"})
        self.assertIn("the eight plants with plant orders in", self.doc)
        for name in ("Campbell 1710", "Eddystone 3161", "Wagner 1554", "Centralia 3845", "Schahfer 6085",
                     "Culley 1012", "Craig 6021", "Stanton 564"):
            self.assertIn(name, self.doc)

    def test_forecast_f1_against_orders_csv(self):
        self.assertIn("F1: DOE issues a 202(c) order that covers Sherburne County 1", self.doc)
        self.assertIn("Our probability: 60%.", self.doc)
        orders = [r for r in rows("data/doe_202c_orders.csv") if r["kind"] == "plant"]
        coal = ("campbell", "centralia", "schahfer", "culley", "craig", "stanton")
        self.assertIn("six coal plants at or near their planned retirement (Campbell, Centralia, Schahfer, "
                      "Culley, Craig and Stanton), three of them in MISO", self.doc)
        self.assertEqual(sorted({r["plant_key"] for r in orders if r["area"] == "MISO"}),
                         ["campbell", "culley", "schahfer"])
        self.assertIn("each order at these six plants has been followed by a new one issued no later than "
                      "the day it expired", self.doc)
        for key in coal:
            seq = sorted((r for r in orders if r["plant_key"] == key), key=lambda r: r["issued"])
            self.assertGreaterEqual(len(seq), 2, key)
            for before, after in zip(seq, seq[1:]):
                self.assertLessEqual(after["issued"], before["expires"], (key, after["order"]))
        firsts = {}
        for r in orders:
            firsts[r["plant_key"]] = min(firsts.get(r["plant_key"], r["issued"]), r["issued"])
        self.assertEqual(max(firsts.values()), "2026-06-04")
        self.assertEqual(firsts["stanton"], "2026-06-04")
        self.assertIn("no first order to a new plant since Stanton on 4 June 2026", self.doc)
        self.assertNotIn("intermountain", {r["plant_key"] for r in orders})
        self.assertIn("with no 202(c) order in our orders table", self.doc)

    def test_recorded_files(self):
        self.assertIn("14,013,970 bytes, md5 4c741eb77a5ccad5aca32ffe43f398af", self.doc)
        self.assertIn("13,955,142 bytes, md5 9727ac867236faab7d5503175dacdf38", self.doc)


if __name__ == "__main__":
    unittest.main()
