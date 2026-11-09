"""Checks that every count stated in docs/xwback.md (result of pre-registration xwback-1) is what
data/xwback-plants.csv and data/xwback-retired-plants.csv (the job's outputs, unchanged) say, and
that the scores in data/xwback-run.json are the ones the page reports. Reads no outside data.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import csv
import json
import os
import unittest
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))


def path(rel):
    return os.path.join(HERE, rel)


def rows(rel):
    with open(path(rel), encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


class XwbackResultTests(unittest.TestCase):
    # The job's JSON is kept as `res`: naming it `run` would hide unittest's TestCase.run.
    @classmethod
    def setUpClass(cls):
        with open(path("docs/xwback.md"), encoding="utf-8") as fh:
            cls.doc = fh.read()
        cls.pop_a = rows("data/xwback-plants.csv")
        cls.pop_c = rows("data/xwback-retired-plants.csv")
        with open(path("data/xwback-run.json"), encoding="utf-8") as fh:
            cls.res = json.load(fh)

    def test_scores(self):
        self.assertEqual(self.res["scores"], {"G1": True, "G2": True, "G3": True, "P1": True,
                                              "P2": True, "P3": False, "P4": True, "P5": False})
        self.assertIn("**3 of the 5 predictions held (P1, P2, P4); P3 and P5 failed.**", self.doc)
        self.assertEqual(self.res["downloads"]["core_eia860__scd_generators"]["md5"],
                         "6c4372366df319de1888d8fc6ea1ec0e")
        self.assertIn("6c4372366df319de1888d8fc6ea1ec0e", self.doc)
        self.assertIn("667,073 rows", self.doc)
        self.assertEqual(self.res["downloads"]["core_eia860__scd_generators"]["rows"], 667073)
        self.assertEqual(self.res["g2"], {"plants": 14, "units": 57})

    def test_population_a(self):
        a = self.pop_a
        self.assertEqual(len(a), 14)
        self.assertEqual(sum(int(r["units_2024"]) for r in a), 57)
        self.assertTrue(all(r["rows_2025"] == "0" for r in a))
        self.assertEqual(sum(int(r["later_rows"]) for r in a), 81)
        self.assertEqual(sum(int(r["later_rows_RE"]) for r in a), 81)
        self.assertEqual(sum(int(r["rows_2026"]) for r in a), 81)
        self.assertTrue(all(set(json.loads(r["maturity_2026"])) == {"monthly_update"} for r in a))
        self.assertEqual(Counter(r["last_annual_year"] for r in a),
                         Counter({"2022": 9, "2023": 4, "2024": 1}))
        self.assertEqual([r["plant_id_eia"] for r in a if r["last_annual_year"] == "2024"],
                         ["356"])
        self.assertIn("all 81 rows `monthly_update`", self.doc)

    def test_population_c(self):
        c = self.pop_c
        n = len(c)
        self.assertEqual(n, 1350)
        persist = sum(r["listed_3plus_years_later"] == "True" for r in c)
        in25 = sum(r["in_2025"] == "True" for r in c)
        in26 = sum(r["in_2026"] == "True" for r in c)
        self.assertEqual((persist, in25, in26), (753, 497, 1312))
        last = Counter(int(r["last_annual_year"]) for r in c)
        groups = {"2024": last[2024], "2009": last[2009],
                  "2010-2014": sum(last[y] for y in range(2010, 2015)),
                  "2015-2019": sum(last[y] for y in range(2015, 2020)),
                  "2020-2023": sum(last[y] for y in range(2020, 2024)),
                  "2002-2008": sum(last[y] for y in range(2002, 2009))}
        self.assertEqual(groups, {"2024": 497, "2009": 237, "2010-2014": 214,
                                  "2015-2019": 243, "2020-2023": 158, "2002-2008": 1})
        self.assertEqual(sum(groups.values()), n)
        carried = [r for r in c if r["last_annual_year"] == "2024"]
        self.assertTrue(all(r["listed_3plus_years_later"] == "True" for r in carried))
        self.assertEqual(sum(r["in_2025"] == "True" for r in carried), 496)
        self.assertEqual(persist - len(carried), 256)
        self.assertEqual(n - in26, 38)
        self.assertEqual(sum(r["in_2025"] == "False" and r["in_2026"] == "False" for r in c), 23)
        for p in ("155", "334", "569", "596"):
            row = next(r for r in c if r["plant_id_eia"] == p)
            self.assertEqual(row["last_annual_year"], "2009")
            self.assertIn(row["first_retired_year"], ("2002", "2003", "2004"))
        for text in ("753 of 1,350 (55.8%)", "497 of 1,350 (36.8%)", "1,312 of 1,350 (97.2%)",
                     "| 497 | 36.8% |", "| 237 | 17.6% |", "| 214 | 15.9% |", "| 243 | 18.0% |",
                     "| 158 | 11.7% |", "| 1 | 0.1% |", "853 plants (63.2%)", "256 plants",
                     "38 are not; 23 of those"):
            self.assertIn(text, self.doc)

    def test_astoria(self):
        ctg = self.res["astoria_undated"]["CTG01"]
        self.assertEqual([(r["year"], r["status"], r["ret"]) for r in ctg],
                         [(2020, "L", None), (2021, "L", None), (2022, "CN", None),
                          (2023, "CN", None)])
        self.assertEqual(list(self.res["astoria_undated"]), ["CTG01"])
        self.assertIn("**CTG01**", self.doc)

    def test_disclosure(self):
        for text in ("made with AI agents working in MV2's name",
                     "no person has checked these results by hand",
                     "This reading is after the fact, not pre-registered.",
                     "pudl/issues/3684", "pudl/issues/5752", "[plan](xwback-plan.md)"):
            self.assertIn(text, self.doc)


if __name__ == "__main__":
    unittest.main()
