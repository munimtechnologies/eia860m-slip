"""Checks that every count stated in docs/xwtz.md (result of pre-registration xwtz-1) is what
data/xwtz-run.json, data/xwtz-verify.json and data/xwtz-flagged-units.csv (the job's outputs,
unchanged) say. Reads no outside data.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import csv
import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def path(rel):
    return os.path.join(HERE, rel)


def fmt(n):
    return f"{n:,}"


class XwtzResultTests(unittest.TestCase):
    # The job's JSON is kept as `res`: naming it `run` would hide unittest's TestCase.run.
    @classmethod
    def setUpClass(cls):
        with open(path("docs/xwtz.md"), encoding="utf-8") as fh:
            cls.doc = fh.read()
        with open(path("data/xwtz-run.json"), encoding="utf-8") as fh:
            cls.res = json.load(fh)
        with open(path("data/xwtz-verify.json"), encoding="utf-8") as fh:
            cls.ver = json.load(fh)
        with open(path("data/xwtz-flagged-units.csv"), encoding="utf-8", newline="") as fh:
            cls.flagged = list(csv.DictReader(fh))

    def test_scores(self):
        self.assertEqual(self.res["scores"], {"G1": True, "G2": True, "G3": True, "P1": True,
                                              "P2": True, "P3": True, "P4": False, "P5": False})
        self.assertIn("**3 of the 5 predictions held (P1, P2, P3); P4 and P5 failed.**", self.doc)
        self.assertEqual(len(self.res["downloads"]), 3)
        for name, d in self.res["downloads"].items():
            self.assertIn(d["md5"], self.doc, name)
            self.assertIn(fmt(d["rows"]) + " rows", self.doc, name)
            self.assertEqual(d["missing_cols"], [])

    def test_gates(self):
        xw = self.res["xw_info"]
        self.assertEqual((xw["unit_keys"], xw["multi_keys"], xw["leading_zero_keys"]), (5167, 4, 0))
        self.assertIn("5,163 of 5,167 (99.92%)", self.doc)
        self.assertEqual(round(100 * xw["unique_share"], 2), 99.92)
        years = self.res["g1"]["years"]
        self.assertEqual((min(years), max(years)), (2000, 2025))
        self.assertEqual(self.res["summary"]["by_year"]["2024"]["units"], 4215)
        self.assertEqual(xw["renumbered_plants"], 27)

    def test_year_table(self):
        by_year = self.res["summary"]["by_year"]
        self.assertEqual(sorted(by_year), [str(y) for y in range(2018, 2025)])
        for year, s in by_year.items():
            line = (f"| {year} | {fmt(s['units'])} | {fmt(s['plants'])} | "
                    f"{s['fallback']} ({s['fallback_plants']}) | {s['multi']} | "
                    f"{s['inconsistent']} | {s['no_tz']} | {s['suspicious']} | {s['tz_diff']} |")
            self.assertIn(line, self.doc)
            self.assertEqual((s["not_in_entity"], s["inconsistent"], s["no_tz"], s["suspicious"],
                              s["tz_diff"]), (0, 0, 0, 0, 0))
            self.assertEqual((s["renumbered"], s["renumbered_plants"]), (77, 26))
        a = self.res["summary"]["all_years"]
        self.assertEqual((a["unit_years"], a["fallback_units"], a["fallback_plants"],
                          a["multi_units"], a["multi_plants"]), (31049, 278, 122, 4, 1))
        self.assertEqual(sum(s["units"] for s in by_year.values()), 31049)
        self.assertIn("All (31,049 unit-years)", self.doc)
        self.assertIn("278 units (122 plants)", self.doc)

    def test_entity_plants(self):
        e = self.res["entity_plants"]
        self.assertEqual((e["plants"], e["with_timezone"], e["timezones"][""]), (20071, 19799, 272))
        self.assertIn("272 of 20,071", self.doc)

    def test_flagged_file(self):
        self.assertEqual(len(self.flagged), 16)
        self.assertIn("16 rows of the flagged file", self.doc)
        self.assertEqual({r["flags"] for r in self.flagged}, {"multi"})
        self.assertEqual({r["plant_id_epa"] for r in self.flagged}, {"63628"})
        self.assertEqual({r["emissions_unit_id_epa"] for r in self.flagged},
                         {"5A-1", "5A-2", "5B-1", "5B-2"})
        self.assertEqual(sorted({r["report_year"] for r in self.flagged}),
                         ["2021", "2022", "2023", "2024"])
        self.assertEqual({r["timezone"] for r in self.flagged}, {"America/Chicago"})

    def test_verify(self):
        self.assertEqual(self.res["verify_plan"]["flagged_total"], 0)
        self.assertEqual(self.ver["controls"], [3, 7, 9])
        plant_years = self.ver["rows"]
        self.assertEqual(len(plant_years), 23)
        self.assertEqual(sum(r["null_utc"] for r in plant_years), 0)
        self.assertEqual(min(r["year"] for r in plant_years), 2018)
        self.assertEqual(max(r["year"] for r in plant_years), 2026)
        self.assertIn("23 plant-years from 2018 to 2026, no null `operating_datetime_utc`", self.doc)

    def test_disclosure(self):
        for text in ("made with AI agents working in MV2's name",
                     "no person has checked these results by hand",
                     "[plan](xwtz-plan.md)", "pudl/issues/5162"):
            self.assertIn(text, self.doc)


if __name__ == "__main__":
    unittest.main()
