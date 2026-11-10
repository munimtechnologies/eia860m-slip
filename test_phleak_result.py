"""Checks that every count stated in docs/phleak.md (result of pre-registration phleak-1) is what
data/phleak-run.json and the three phleak CSV files in data/ (the job's outputs, unchanged) say.
Reads no outside data.

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


def pct(a, b):
    return f"{100.0 * a / b:.2f}%"


def read_csv(rel):
    with open(path(rel), encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


class PhleakResultTests(unittest.TestCase):
    # The job's JSON is kept as `res`: naming it `run` would hide unittest's TestCase.run.
    @classmethod
    def setUpClass(cls):
        with open(path("docs/phleak.md"), encoding="utf-8") as fh:
            cls.doc = fh.read()
        with open(path("data/phleak-run.json"), encoding="utf-8") as fh:
            cls.res = json.load(fh)
        cls.haz = read_csv("data/phleak-hazardous-gt-all.csv")
        cls.multi = read_csv("data/phleak-multistate-reports.csv")
        cls.com = read_csv("data/phleak-commodity.csv")
        cls.p = cls.res["profile"]
        cls.m = cls.res["measures"]

    def test_run_and_scores(self):
        self.assertEqual(self.res["tool"], "phleak.py 0.1.0")
        self.assertEqual((self.res["started"], self.res["finished"]),
                         ("2026-11-10T21:46:36Z", "2026-11-10T21:46:42Z"))
        self.assertIn("21:46:36-21:46:42 UTC", self.doc)
        self.assertEqual(self.res["scores"], {"G1": True, "G2": True, "G3": True, "P1": True,
                                              "P2": True, "P3": False, "P4": True, "P5": True,
                                              "P6": True, "P7": True})
        self.assertIn("**6 of the 7 predictions held (P1, P2, P4-P7); P3 failed, because there was "
                      "nothing to test.**", self.doc)

    def test_input_and_gates(self):
        t = self.res["table"]
        self.assertEqual((t["bytes"], t["rows"], t["missing_cols"]), (1734682, 633659, []))
        self.assertEqual(t["last_modified"], "Tue, 10 Nov 2026 08:52:05 GMT")
        self.assertIn(t["md5"], self.doc)
        self.assertIn("1,734,682 bytes, Last-Modified 10 Nov 2026 08:52:05 GMT", self.doc)
        self.assertEqual((self.p["rows"], self.p["groups"], self.p["years"]),
                         (633659, 89114, [1970, 2025]))
        self.assertIn("633,659 rows in 89,114 reports, from report years 1970-2025",
                      self.doc)
        self.assertEqual(self.res["gates"], {"G1": True, "G2": True, "G3": True})
        g = self.res["gate_measures"]
        self.assertEqual((len(g["severity_values"]), len(g["source_values"])), (2, 13))
        self.assertIn("| 633,659 rows; report years 1970-2025 | yes |", self.doc)
        self.assertIn("| 2 severities; 13 sources, all in `LEAK_SOURCE_PHMSAGAS` | yes |", self.doc)

    def test_p1_p2_commodity(self):
        c = self.m["commodity"]
        self.assertEqual((c["pre_2015_nonnull_rows"], c["from_2015_rows"], c["from_2015_null_rows"]),
                         (0, 145719, 0))
        self.assertIn("| 0 before 2015; 0 of 145,719 missing from 2015 | yes |", self.doc)
        self.assertEqual((c["unmapped_values"], c["unmapped_rows"]), ([], 0))
        vals = {k: v for k, v in self.p["commodity"].items() if k != "<null>"}
        self.assertEqual(len(vals), 10)
        self.assertIn("| 10 values, none unmapped | yes |", self.doc)
        self.assertEqual(sum(v[0] for v in vals.values()), 145719)
        self.assertEqual(self.p["commodity"]["<null>"], [487940, 1970, 2014])
        want = [("Natural Gas", 140678), ("Propane Gas", 4126), ("Landfill Gas", 363),
                ("Synthetic Gas", 325), ("Hydrogen Gas", 192), ("OTHER GAS: Natural Gas", 25),
                ("OTHER GAS: Propane", 4), ("OTHER GAS: City of York", 3),
                ("OTHER GAS: Other Gas - Propane", 2), ("OTHER GAS: Nitrogen", 1)]
        for name, n in want:
            self.assertEqual(vals[name][0], n, name)
        self.assertIn("Natural Gas 140,678; Propane Gas 4,126; Landfill Gas 363; Synthetic Gas 325; "
                      "Hydrogen Gas 192; `OTHER GAS: Natural Gas` 25; `OTHER GAS: Propane` 4; "
                      "`OTHER GAS: City of York` 3; `OTHER GAS: Other Gas - Propane` 2; "
                      "`OTHER GAS: Nitrogen` 1", self.doc)
        self.assertEqual(vals["OTHER GAS: Propane"][1:], [2025, 2025])
        self.assertEqual(vals["OTHER GAS: Other Gas - Propane"][1:], [2025, 2025])
        mp = {r["commodity"]: r["pudl_install_decade_map"] for r in self.com}
        self.assertEqual(mp["OTHER GAS: Propane"], "propane_gas")
        self.assertEqual(mp["OTHER GAS: Other Gas - Propane"], "propane_gas")
        self.assertEqual(len(self.com), 11)
        self.assertIn("both only in report year 2025. PUDL's existing install-decade map already "
                      "sends both to `propane_gas`", self.doc)

    def test_p3_sums(self):
        s = self.m["sums"]
        self.assertEqual((s["checked"], s["passed"], s["share"], s["by_year"]), (0, 0, None, {}))
        self.assertEqual((s["mains|no_total"], s["services|no_total"], s["services|total_only"]),
                         (100342, 73651, 10085))
        self.assertNotIn("mains|total_only", s)
        self.assertIn("| 0 tested | no |", self.doc)
        self.assertIn("100,342 report-severity mains counts and 73,651 services counts with parts but "
                      "no total, and 10,085 services totals with no part", self.doc)
        self.assertEqual(self.p["source"]["total"], [10085, 1978, 1983])
        self.assertIn("The `total` source has 10,085 rows, all from report years 1978-1983", self.doc)

    def test_p4_hazardous(self):
        h = self.m["hazardous_vs_all"]
        self.assertEqual((h["ok"], h["compared"], h["hazardous_gt_all"]), (195026, 195128, 102))
        self.assertIn(f"| 195,026 of 195,128 ({pct(195026, 195128)}) | yes |", self.doc)
        self.assertEqual(len(self.haz), 102)
        by = {}
        for r in self.haz:
            by[r["report_year"]] = by.get(r["report_year"], 0) + 1
            self.assertGreater(float(r["hazardous_leaks"]), float(r["all_leaks"]))
        self.assertEqual(by, {"2011": 3, "2012": 50, "2013": 24, "2014": 25})
        self.assertIn("**Hazardous above all leaks: 102 cases, all from report years 2011-2014** "
                      "(3 in 2011, 50 in 2012, 24 in 2013, 25 in 2014)", self.doc)
        zero = sum(float(r["all_leaks"]) == 0 and float(r["hazardous_leaks"]) > 0 for r in self.haz)
        self.assertEqual(zero, 59)
        self.assertIn("In 59 of them the all-leaks count is 0", self.doc)
        self.assertIn("would fail 102 times, all in 2011-2014", self.doc)

    def test_p5_p6_p7(self):
        self.assertEqual(self.m["primary_key"], {"extra_rows": 0, "duplicate_keys": 0})
        self.assertIn("| 0 duplicate rows | yes |", self.doc)
        ms = self.m["multi_state"]
        self.assertEqual((ms["rows"], ms["rows_to_2003"], ms["ok"]), (2544, 2544, True))
        yrs = [int(y) for y in self.p["multi_state_by_year"]]
        self.assertEqual((min(yrs), max(yrs)), (1984, 2003))
        self.assertIn("| 2,544 rows, all 1984-2003 | yes |", self.doc)
        self.assertEqual(len(self.multi), 424)
        self.assertEqual(sum(int(r["rows"]) for r in self.multi), 2544)
        self.assertIn("The 2,544 rows belong to 424 reports", self.doc)
        self.assertEqual((self.m["negatives"]["rows"], self.p["negative_rows"]), (0, 0))
        self.assertIn("| no negative rows | 0 rows | yes |", self.doc)

    def test_sources_by_era(self):
        src = self.p["source"]
        self.assertEqual(len(src), 13)
        eras = {"construction_defect": [1970, 2003], "material_defect": [1984, 2003],
                "third_party": [1984, 2003], "outside_force": [1990, 2003],
                "equipment_failure": [2004, 2025], "excavation_damage": [2004, 2025],
                "incorrect_operation": [2004, 2025], "natural_force_damage": [2004, 2025],
                "corrosion_failure": [1970, 2025], "other": [1970, 2025],
                "other_outside_force": [1970, 2025], "pipe_weld_joint_failure": [1970, 2025],
                "total": [1978, 1983]}
        for k, v in eras.items():
            self.assertEqual(src[k][1:], v, k)
        self.assertIn("`construction_defect` 1970-2003; `material_defect` and `third_party` 1984-2003; "
                      "`outside_force` 1990-2003; `equipment_failure`, `excavation_damage`, "
                      "`incorrect_operation` and `natural_force_damage` 2004-2025; "
                      "`corrosion_failure`, `other`, `other_outside_force` and "
                      "`pipe_weld_joint_failure` 1970-2025; `total` 1978-1983", self.doc)

    def test_states(self):
        k = self.p["state_kinds"]
        self.assertEqual(k, {"multi": 2544, "null": 97919, "other": 96, "single": 533100})
        self.assertEqual(sum(k.values()), 633659)
        self.assertIn("**Null `operating_state`: 97,919 rows.**", self.doc)
        nb, ry = self.p["state_null_by_year"], self.p["rows_by_year"]
        for y in range(1970, 1978):
            self.assertEqual(nb[str(y)], ry[str(y)], y)
        self.assertEqual((nb["1978"], ry["1978"], nb["1979"], ry["1979"]), (15140, 15158, 15320, 15368))
        self.assertIn("15,140 of 15,158 rows in 1978 and 15,320 of 15,368 in 1979", self.doc)
        later = {int(y): n for y, n in nb.items() if int(y) >= 1980}
        self.assertEqual(max(later), 1999)
        self.assertEqual(sorted(later.values(), reverse=True)[:2], [894, 852])
        self.assertEqual((later[1991], later[1992]), (894, 852))
        self.assertIn("up to 1999 (most in 1991, 894 rows, and 1992, 852 rows)", self.doc)
        o = self.p["other_state_values_top50"]
        self.assertEqual(sum(o.values()), 96)
        self.assertEqual((o["ar"], o["az"], o["ak"], o["2"], o["PA7"]), (48, 24, 6, 6, 6))
        ky = [v for s, v in o.items() if s.strip() == "ky" and s != "ky"]
        self.assertEqual(ky, [6])
        self.assertIn("**Other state values: 96 rows.**", self.doc)
        self.assertIn("(`ar` 48, `az` 24, `ak` 6), `ky` with trailing spaces (6), `2` (6) and "
                      "`PA7` (6)", self.doc)

    def test_operators_severity_years(self):
        z = self.p["operator_zero_by_year"]
        self.assertEqual(z, {"1976": 60, "1978": 15, "1980": 3006, "1981": 2916, "1982": 2532,
                             "1983": 4242})
        self.assertEqual((self.p["operator_zero_rows"], self.p["operator_null_rows"]), (12771, 0))
        self.assertIn("**Operator id 0: 12,771 rows**, in 1976 (60), 1978 (15), 1980 (3,006), "
                      "1981 (2,916), 1982 (2,532) and 1983 (4,242). No operator id is null.", self.doc)
        self.assertEqual(self.p["severity"], {"all_leaks": 532205, "hazardous_leaks": 101454})
        self.assertIn("`all_leaks` has 532,205 rows and `hazardous_leaks` 101,454", self.doc)
        self.assertEqual(self.p["rows_both_values_null"], 0)
        ry = {int(y): n for y, n in self.p["rows_by_year"].items()}
        rest = [n for y, n in ry.items() if y >= 2004 and y not in (2010, 2011)]
        self.assertGreaterEqual(min(rest), 11500)
        self.assertLessEqual(max(rest), 14300)
        self.assertEqual((ry[2010], ry[2011]), (17423, 22930))
        self.assertIn("These are 11,500-14,300 from 2004 on, except 2010 (17,423) and 2011 (22,930)",
                      self.doc)

    def test_disclosure(self):
        for text in ("made with AI agents working in MV2's name",
                     "no person has checked these results by hand",
                     "[plan](phleak-plan.md)", "pudl/issues/5435",
                     "Text and data CC BY 4.0; code Apache-2.0.",
                     "16:00:18 UTC on 10 November 2026",
                     "None of this has been checked against PHMSA's raw files or forms."):
            self.assertIn(text, self.doc)


if __name__ == "__main__":
    unittest.main()
