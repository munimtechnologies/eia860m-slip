"""Checks docs/coaloct-plan.md against job coalsep-v1's output (data/coalsep_2026-09.json) and the two CSVs
it names.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import csv
import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))

# EIA plant ID -> (name on the plan page, units in the job output, month in the job output)
DATED_2026 = {"1710": ("Campbell 1-3", "1, 2, 3", "2026-11"), "6085": ("Schahfer 17-18", "17, 18", "2026-12"),
              "6090": ("Sherburne County 1", "1", "2026-12"), "6021": ("Craig 1", "1", "2026-12"),
              "470": ("Comanche 2", "2", "2026-12"), "1012": ("Culley 2", "2", "2026-12")}
COAL_ORDER_PLANTS = ("campbell", "centralia", "schahfer", "culley", "craig", "stanton")


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


def rows(path):
    with open(os.path.join(HERE, path), encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def mw(x):
    return "{:,.1f}".format(x)


class CoaloctPlanDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/coaloct-plan.md")
        cls.res = json.loads(read("data/coalsep_2026-09.json"))

    def test_status_and_bars(self):
        self.assertIn("Status: pre-registered, not yet scored.", self.doc)
        self.assertIn("| O1 | No coal row on the Retired sheet has retirement year 2026. | about 85% |", self.doc)
        self.assertIn("| O2 | No coal unit on the Operating sheet is dated before 2026-11. | about 85% |", self.doc)
        self.assertIn("Sherburne County 1 (6090/1) and Comanche 2 (470/2) are both still dated 2026-12. | about 75% |",
                      self.doc)
        self.assertNotIn("| O4 |", self.doc)
        self.assertNotIn("MIT", self.doc)

    def test_chances(self):
        chances = dict(re.findall(r"^\| (O\d) \| .+ \| about (\d+)% \|", self.doc, re.M))
        self.assertEqual(chances, {"O1": "85", "O2": "85", "O3": "75"})
        expected = sum(int(c) for c in chances.values())
        self.assertIn("The three chances add up to %d.%02d predictions expected to hold." %
                      (expected // 100, expected % 100), self.doc)

    def test_september_known(self):
        r = self.res
        self.assertEqual(r["version"], "0.1.0")
        self.assertEqual(r["predictions"]["S1"]["retired_2026"], [])
        self.assertIn("has 0 coal rows on its Retired sheet with retirement year 2026;", self.doc)
        self.assertEqual(r["overdue"], [])
        self.assertFalse(any("2026-10" in a["months"] for a in r["ahead"]))
        self.assertIn("has no operating coal unit dated before 2026-10, and none dated 2026-10.", self.doc)
        y26 = [a for a in r["ahead"] if a["first"] <= "2026-12"]
        self.assertEqual({a["plant_id"] for a in y26}, set(DATED_2026))
        for a in y26:
            name, units, month = DATED_2026[a["plant_id"]]
            self.assertEqual((a["units"], a["months"]), (units, month), name)
            self.assertIn("%s (%s MW)" % (name, mw(a["mw"])), self.doc)
        units = sum(len(a["units"].split(", ")) for a in y26)
        total = sum(a["mw"] for a in y26)
        self.assertEqual((units, mw(total)), (9, "3,584.5"))
        self.assertEqual((r["predictions"]["S3"]["units"], mw(r["predictions"]["S3"]["mw"])), (units, mw(total)))
        self.assertIn("dates %d operating coal units in six plants to retire in 2026, %s MW in all" %
                      (units, mw(total)), self.doc)
        self.assertIn("the same %d operating coal units dated 2026-10 to 2026-12, with the same months, %s MW in all" %
                      (units, mw(total)), self.doc)
        self.assertIn("Campbell 1-3 (1,330.5 MW) to 2026-11, and Schahfer 17-18", self.doc)

    def test_september_file(self):
        f = self.res["files"]["september"]
        self.assertTrue(f["same_as_recorded"])
        self.assertIn("still has %s bytes and md5 %s" % ("{:,}".format(f["size"]), f["md5"]), self.doc)
        self.assertEqual(f["md5"], "4c741eb77a5ccad5aca32ffe43f398af")

    def test_plan_generators(self):
        plan = rows("data/coal_plan_2026_followup.csv")
        self.assertEqual(len(plan), 16)
        self.assertIn("the 16 coal generators (%s MW)" % mw(sum(float(p["mw"]) for p in plan)), self.doc)
        by_key = {p["key"]: p for p in plan}
        for key in ("6090/1", "470/2"):
            self.assertEqual(self.res["predictions"]["S2"]["still"][key], "2026-12")
            self.assertIn(key, by_key)

    def test_orders(self):
        orders = rows("data/doe_202c_orders.csv")
        self.assertEqual(max(r["issued"] for r in orders), "2026-10-12")
        self.assertEqual(max(orders, key=lambda r: r["issued"])["order"], "202-26-50")
        self.assertIn("lists no order newer than 202-26-50 (12 October)", self.doc)
        latest = {}
        for r in orders:
            if r["kind"] == "plant" and r["plant_key"] in COAL_ORDER_PLANTS:
                if r["plant_key"] not in latest or r["issued"] > latest[r["plant_key"]]["issued"]:
                    latest[r["plant_key"]] = r
        self.assertEqual(sorted(latest), sorted(COAL_ORDER_PLANTS))
        first = min(latest.values(), key=lambda r: r["expires"])
        self.assertEqual((first["plant_key"], first["expires"]), ("campbell", "2026-11-14"))
        self.assertIn("the first order expiry among the coal plants DOE holds open is Campbell's, on 14 November 2026",
                      self.doc)
        self.assertEqual(sorted(latest[k]["expires"] for k in ("schahfer", "culley", "craig")),
                         ["2026-12-18", "2026-12-18", "2026-12-25"])
        self.assertIn("expire on 14 November (Campbell) and 18 to 25 December 2026", self.doc)


if __name__ == "__main__":
    unittest.main()
