"""Checks that every count stated in docs/easeyx2.md (result of pre-registration easeyx-2) is what
data/easeyx2-run.json and the two easeyx2 CSV files in data/ (the job's outputs, unchanged) say,
and that the after-the-fact 2025 counts are what easeyx-1's data/easeyx-epa-side-2025.csv says.
Reads no outside data.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import csv
import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def path(rel):
    return os.path.join(HERE, rel)


def fmt(n):
    return f"{n:,}"


def pct(a, b):
    return f"{100.0 * a / b:.2f}%"


def norm(s):
    return " ".join((s or "").split()).lower()


def read_csv(rel):
    with open(path(rel), encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def key(row):
    return (row["plant_id"], row["unit_id"], row["generator_id"])


class Easeyx2ResultTests(unittest.TestCase):
    # The job's JSON is kept as `res`: naming it `run` would hide unittest's TestCase.run.
    @classmethod
    def setUpClass(cls):
        with open(path("docs/easeyx2.md"), encoding="utf-8") as fh:
            cls.doc = fh.read()
        with open(path("data/easeyx2-run.json"), encoding="utf-8") as fh:
            cls.res = json.load(fh)
        cls.diffs = read_csv("data/easeyx2-attribute-differences.csv")
        cls.silent = read_csv("data/easeyx2-silent-retirements.csv")
        cls.side25 = {key(r): r for r in read_csv("data/easeyx-epa-side-2025.csv")}

    def test_run_and_scores(self):
        self.assertEqual(self.res["tool"], "easeyx2.py 0.1.0 (easeyx.py 0.1.0)")
        self.assertEqual((self.res["started"], self.res["finished"]),
                         ("2026-11-10T07:47:35Z", "2026-11-10T07:47:36Z"))
        self.assertIn("07:47:35-07:47:36 UTC", self.doc)
        self.assertEqual(self.res["scores"], {"G1": True, "G2": True, "G3": True, "P1": True,
                                              "P2": True, "P3": True, "P4": True, "P5": True,
                                              "P6": True})
        self.assertIn("**All 6 predictions held (P1-P6).**", self.doc)

    def test_inputs(self):
        r = self.res["reference"]
        self.assertTrue(r["same_as_easeyx1"])
        self.assertEqual((r["rows"], r["keys"], r["missing_cols"]), (7182, 7174, []))
        self.assertIn(r["md5"], self.doc)
        self.assertIn("e52a3a533f745b98b88f0556473fee0d4cbcf96d", r["url"])
        self.assertEqual(sorted(self.res["downloads"]), [str(y) for y in range(2010, 2025)])
        self.assertTrue(all(d["same_as_easeyx1"] for d in self.res["downloads"].values()))
        self.assertIn("All 15 md5s equal the ones", self.doc)

    def test_gates(self):
        g = self.res["gate_measures"]
        self.assertEqual(g, {"ref_rows": 7182, "found": 7039, "silent": 390})
        self.assertIn("no missing columns; 7,182 rows", self.doc)
        self.assertIn("| 7,039 found; 390 silent | yes |", self.doc)

    def test_predictions(self):
        m = self.res["measures"]
        self.assertEqual(m["keys_compared"], 7039)
        for a in ("state", "facility_name", "capacity", "fuel", "coords"):
            self.assertEqual(m[a]["match"] + m[a]["differ"] + m[a]["not_comparable"], 7039)
        s = m["state"]
        self.assertIn(f"| {fmt(s['match'])} of {fmt(s['match'] + s['differ'])} "
                      f"({pct(s['match'], s['match'] + s['differ'])}) | yes |", self.doc)
        n = m["facility_name"]
        self.assertEqual((n["match"], n["differ"]), (7037, 2))
        self.assertIn(f"{fmt(n['match'])} of 7,039 ({pct(7037, 7039)})", self.doc)
        c = m["capacity"]
        self.assertEqual((c["match"], c["differ"], c["not_comparable"]), (6799, 0, 240))
        self.assertIn(f"6,799 of 6,799 ({pct(6799, 6799)}); 240 not comparable", self.doc)
        f = m["fuel"]
        self.assertEqual((f["match"], f["differ"], f["not_comparable"]), (6928, 16, 95))
        self.assertIn(f"6,928 of 6,944 ({pct(6928, 6944)}); 95 not comparable", self.doc)
        self.assertIn(f"same fuel for {pct(6928, 6944)}", self.doc)
        k = m["coords"]
        self.assertEqual((k["match"], k["differ"]), (7039, 0))
        self.assertEqual(self.doc.count(f"7,039 of 7,039 ({pct(7039, 7039)})"), 2)
        sil = m["silent"]
        self.assertEqual((sil["keys"], sil["dated"], sil["ref_year_is_last_or_next"]), (390, 390, 364))
        self.assertIn(f"364 of 390 ({pct(364, 390)})", self.doc)
        self.assertIn(f"that year or the next for 364 ({pct(364, 390)})", self.doc)

    def test_not_comparable_and_differences(self):
        b = self.res["reported"]["by_status"]
        self.assertEqual(b["capacity"].get("OPR|na"), 166)
        self.assertEqual(b["capacity"].get("RET_LTCS|na"), 74)
        self.assertEqual(b["fuel"].get("RET_LTCS|na"), 95)
        self.assertNotIn("OPR|na", b["fuel"])
        self.assertEqual(b["fuel"].get("OPR|differ"), 16)
        self.assertNotIn("RET_LTCS|differ", b["fuel"])
        self.assertIn("240 keys (166 OPR, 74 retired or cold storage in the reference) and fuel "
                      "for 95 (all retired or cold storage)", self.doc)
        names = [r for r in self.diffs if r["attribute"] == "facility_name"]
        self.assertEqual(len(names), 2)
        self.assertEqual({r["plant_id"] for r in names}, {"54915"})
        self.assertTrue(all(r["years_matching_ref"] == "" for r in names))
        self.assertEqual({r["ref_value"] for r in names}, {"Michigan Power Limited Partnership"})
        self.assertEqual({r["file_value"] for r in names}, {"DTE Michigan Power, LLC"})
        fuels = [r for r in self.diffs if r["attribute"] == "fuel"]
        self.assertEqual(len(fuels), 16)
        self.assertEqual(len(self.diffs), 18)
        self.assertTrue(all(r["ref_status"] == "OPR" for r in fuels))
        coal = [r for r in fuels if "coal" in norm(r["file_value"]) and "coal" not in norm(r["ref_value"])]
        self.assertEqual(len(coal), 7)
        self.assertEqual({r["plant_id"] for r in coal}, {"645", "1554", "3149", "6193"})
        resid = [r for r in fuels if "residual" in norm(r["file_value"])]
        self.assertEqual((len(resid), {r["plant_id"] for r in resid}), (2, {"3148"}))
        other = [r for r in fuels if r["ref_value"] == "Other Gas"]
        self.assertEqual((len(other), {r["plant_id"] for r in other}), (3, {"55088"}))
        twitty = [r for r in fuels if r["plant_id"] == "6195"]
        self.assertEqual(len(twitty), 4)
        self.assertEqual({r["years_matching_ref"] for r in twitty},
                         {"|".join(str(y) for y in range(2010, 2020))})
        self.assertEqual(self.res["measures"]["fuel"]["differ_other_year_matches"], 4)
        self.assertIn("7 list coal in the 2024 file but only gas in the reference (plants 645, 1554, "
                      "3149 and 6193), 2 list residual oil as well (3148), 3 are \"Other Gas\"", self.doc)

    def test_silent(self):
        sil = self.res["measures"]["silent"]
        self.assertEqual(sil["ref_minus_last"], {"+1": 72, "+2": 6, "0": 292, ">+2": 20})
        self.assertEqual(len(self.silent), 390)
        diffs = [int(r["ref_retire_year"]) - int(r["last_year_in_files"]) for r in self.silent]
        self.assertEqual(min(diffs), 0)
        self.assertEqual((diffs.count(0), diffs.count(1), diffs.count(2), sum(d > 2 for d in diffs)),
                         (292, 72, 6, 20))
        self.assertIn(f"the same year for 292 ({pct(292, 390)}), one year later for 72, two years "
                      f"later for 6, more for 20", self.doc)
        self.assertEqual(max(sil["by_last_year"].values()), 77)
        self.assertEqual(sil["by_last_year"]["2016"], 77)
        self.assertIn("2016 has the most (77)", self.doc)
        dec31 = sum(r["ref_status_date"][5:10] == "12-31" for r in self.silent)
        self.assertEqual(dec31, 302)
        self.assertIn("The reference status date of 302 of them is 31 December", self.doc)

    def test_dating_rules(self):
        r = self.res["reported"]["retire_year_rules"]
        self.assertEqual(r, {"ref_ret_keys_dated": 1645, "derived_only": 1231,
                             "derived_else_last_year": 1523, "derived_else_last_year_plus_1": 1303})
        self.assertEqual(1231 + 292, 1523)
        self.assertEqual(1231 + 72, 1303)
        self.assertIn(f"gets 1,231 exactly right ({pct(1231, 1645)}", self.doc)
        self.assertIn(f"gets 1,523 ({pct(1523, 1645)})", self.doc)
        self.assertIn(f"gets 1,303 ({pct(1303, 1645)})", self.doc)
        self.assertIn(f"gives {pct(1523, 1645)} exactly", self.doc)
        late = 1645 - 1523 - (72 + 6 + 20)
        self.assertEqual(late, 24)
        self.assertIn("The 122 left wrong under the best rule are the 24 the files date one year late "
                      "and the 98 silent units", self.doc)

    def test_after_the_fact_2025(self):
        last24 = [r for r in self.silent if r["last_year_in_files"] == "2024"]
        self.assertEqual(len(last24), 37)
        dated, gone = [], []
        for r in last24:
            row = self.side25.get(key(r))
            self.assertIsNotNone(row, key(r))
            if row["latest_year"] == "2025":
                dated.append((r, row))
            else:
                self.assertEqual(row["latest_year"], "2024")
                gone.append(r)
        self.assertEqual((len(dated), len(gone)), (15, 22))
        for r, row in dated:
            self.assertEqual(r["ref_retire_year"], "2025")
            self.assertEqual(row["derived_retire_year"], "2025")
            m = re.search(r"Retired (\d\d)/(\d\d)/(\d{4})", row["latest_status"])
            self.assertIsNotNone(m, row["latest_status"])
            self.assertEqual(f"{m.group(3)}-{m.group(1)}-{m.group(2)}", r["ref_status_date"][:10])
        for r in gone:
            self.assertEqual(r["ref_retire_year"], "2024")
            self.assertEqual(r["ref_status_date"][:10], "2024-12-31")
        self.assertIn("**37 silent units were last seen in 2024.** 15 of them", self.doc)
        self.assertIn("The other 22 are missing from the 2025 file", self.doc)
        fuels = [r for r in self.diffs if r["attribute"] == "fuel"]
        fixed = [r for r in fuels if norm(self.side25[key(r)]["primary_fuel_type"]) == norm(r["ref_value"])]
        still = [r for r in fuels if r not in fixed]
        self.assertEqual(len(fixed), 11)
        self.assertEqual(sorted(r["plant_id"] for r in still), ["55088"] * 3 + ["6193"] * 2)
        self.assertTrue(all(self.side25[key(r)]["latest_year"] == "2025" for r in fuels))
        for r in self.diffs:
            if r["attribute"] == "facility_name":
                self.assertNotEqual(self.side25[key(r)]["facility_name"], r["ref_value"])
        self.assertIn("**11 of the 16 fuel differences go away**", self.doc)
        self.assertIn("The other 5 (55088 and two units at 6193)", self.doc)

    def test_disclosure(self):
        for text in ("made with AI agents working in MV2's name",
                     "no person has checked these results by hand",
                     "[plan](easeyx2-plan.md)", "camd-eia-crosswalk-latest/issues/7",
                     "Text and data CC BY 4.0; code Apache-2.0.", "(not pre-registered)"):
            self.assertIn(text, self.doc)


if __name__ == "__main__":
    unittest.main()
