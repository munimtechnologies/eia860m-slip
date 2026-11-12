"""Checks that every count stated in docs/phsize.md (result of pre-registration phsize-1) is what
data/phsize-run.json, data/phsize-groups.csv and data/phsize-flagged-sample.csv (the job's
outputs, unchanged) say. Reads no outside data.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import csv
import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
OVER6 = ("all_materials", "steel", "cast_iron", "plastic", "other", "copper")
NO_MAIN8 = ("cast_or_wrought_iron", "pvc", "pe", "abs", "other_plastic", "other_alt",
            "reconditioned_cast_iron")
MAIN8 = ("steel", "all_materials", "copper", "ductile_iron", "other")


def path(rel):
    return os.path.join(HERE, rel)


def fmt(n):
    return f"{int(n):,}"


def pct(a, b):
    return f"{100.0 * a / b:.2f}%"


def read_csv(rel):
    with open(path(rel), encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


class PhsizeResultTests(unittest.TestCase):
    # The job's JSON is kept as `res`: naming it `run` would hide unittest's TestCase.run.
    @classmethod
    def setUpClass(cls):
        with open(path("docs/phsize.md"), encoding="utf-8") as fh:
            cls.doc = fh.read()
        with open(path("data/phsize-run.json"), encoding="utf-8") as fh:
            cls.res = json.load(fh)
        cls.groups = read_csv("data/phsize-groups.csv")
        cls.sample = read_csv("data/phsize-flagged-sample.csv")
        cls.m = cls.res["measures"]

    def test_run_and_scores(self):
        self.assertEqual(self.res["tool"], "phsize.py 0.1.0")
        self.assertEqual((self.res["started"], self.res["finished"]),
                         ("2026-11-12T13:40:40Z", "2026-11-12T13:40:44Z"))
        self.assertIn("13:40:40-13:40:44 UTC", self.doc)
        self.assertEqual(self.res["scores"], {"G1": True, "G2": True, "P1": True, "P2": True,
                                              "P3": True, "P4": True, "P5": True})
        self.assertIn("**All 5 predictions held (P1-P5).**", self.doc)

    def test_input_and_gates(self):
        t = self.res["table"]
        self.assertEqual((t["bytes"], t["rows"], t["missing_cols"]), (6532003, 8086486, []))
        self.assertEqual(t["md5"], "cdbd34b13d84132c4eb799c250f0cc7d")
        self.assertIn("md5 `" + t["md5"] + "`, 6,532,003 bytes", self.doc)
        self.assertEqual(t["last_modified"], "Thu, 12 Nov 2026 08:25:24 GMT")
        self.assertIn("Last-Modified 12 Nov 2026 08:25:24 GMT", self.doc)
        self.assertEqual(self.res["gates"], {"G1": True, "G2": True})
        g = self.res["gate_measures"]
        self.assertEqual((g["rows"], g["mains_rows"], g["services_rows"], g["both_rows"], g["years"]),
                         (8086486, 5707917, 5406361, 3028915, [1970, 2025]))
        self.assertIn("It has 8,086,486 rows from report years 1970-2025: 5,707,917 with a mains "
                      "value, 5,406,361 with a services value and 3,028,915 with both.", self.doc)
        self.assertIn("| G1 file and seven columns | no missing columns | yes |", self.doc)
        self.assertIn("| 8,086,486 rows; 5,406,361 services rows | yes |", self.doc)

    def test_groups_file_matches_totals(self):
        g = self.res["gate_measures"]
        for col, key in (("rows", "rows"), ("mains_rows", "mains_rows"),
                         ("services_rows", "services_rows"), ("both_rows", "both_rows")):
            self.assertEqual(sum(int(r[col]) for r in self.groups), g[key], col)
        years = [int(r["year"]) for r in self.groups]
        self.assertEqual((min(years), max(years)), (1970, 2025))

    def test_p1_p2_null_size(self):
        m = self.m
        self.assertEqual((m["null_size_rows"], m["null_size_rows_expected_material"]),
                         (133648, 133648))
        self.assertEqual(m["shares"]["null_ok"], 1.0)
        self.assertIn("| at least 100 | 133,648 | yes |", self.doc)
        self.assertIn("| at least 99% | 133,648 of 133,648 (100.00%) | yes |", self.doc)
        self.assertIn("**133,648 services rows have no `main_size`.**", self.doc)
        nul = m["null_size_by_material"]
        self.assertEqual(set(nul), set(OVER6) | {"other_alt"})
        early = sum(nul[k][0] for k in OVER6)
        self.assertEqual(early, 94390)
        for k in OVER6:
            self.assertEqual(nul[k][1:3], [1970, 1983], k)
        self.assertEqual(nul["other_alt"][:3], [39258, 1984, 2009])
        self.assertIn("94,390 of them are from report years 1970-1983, for the six materials",
                      self.doc)
        self.assertIn("The other 39,258 are `other_alt`, 1984-2009.", self.doc)
        parts = []
        for k in OVER6 + ("other_alt",):
            v = nul[k]
            parts.append(f"`{k}` {fmt(v[0])} ({v[1]}-{v[2]}, {fmt(v[3])})")
        self.assertIn("(rows, report years, sum of services): " + "; ".join(parts) + ".", self.doc)
        self.assertEqual(max(int(y) for y in m["null_size_by_year"]), 2009)
        self.assertIn("No null-size services row is from 2010 or later.", self.doc)
        self.assertEqual((nul["other_alt"][3], m["services_sum_null_size"]), (4925592.0, 5288553.0))
        self.assertIn("4,925,592 of the 5,288,553 null-size services", self.doc)

    def test_p3_eight_no_main(self):
        m = self.m
        self.assertEqual(m["eight_in_no_main8_rows"], 329767)
        self.assertIn("| at least 100 | 329,767 | yes |", self.doc)
        e = m["eight_in_by_material"]
        parts = [f"`{k}` {fmt(e[k][0])} ({fmt(e[k][3])})" for k in NO_MAIN8]
        self.assertIn("(rows; sum of services): " + "; ".join(parts) + ".", self.doc)
        self.assertEqual(sum(e[k][0] for k in NO_MAIN8), 329767)
        self.assertEqual(sum(e[k][3] for k in NO_MAIN8), m["services_sum_eight_no_main8"])
        self.assertEqual(m["services_sum_eight_no_main8"], 135122.0)
        self.assertIn("Together 329,767 rows and 135,122 services.", self.doc)
        parts5 = [f"`{k}` {fmt(e[k][0])} ({fmt(e[k][3])})" for k in MAIN8]
        self.assertIn("8-inch mains column:** " + "; ".join(parts5) + ".", self.doc)
        self.assertEqual(sum(e[k][0] for k in MAIN8), 306326)
        self.assertIn("Together 306,326 rows.", self.doc)
        self.assertEqual(set(e), set(NO_MAIN8) | set(MAIN8))
        for k, v in e.items():
            self.assertEqual(v[4], 0, k)
        self.assertEqual(m["reports"], {"null_size": 68245, "eight_no_main8": 62739})
        self.assertIn("68,245 reports have a null-size services row and 62,739 have", self.doc)

    def test_p4_p5(self):
        m = self.m
        self.assertEqual(m["services_other_sizes"], {})
        self.assertEqual(len(m["services_by_size"]), 11)
        self.assertIn("| none | none (11 sizes, null included) | yes |", self.doc)
        flagged = m["services_sum_null_size"] + m["services_sum_eight_no_main8"]
        base = m["services_sum_non_total"]
        self.assertEqual((flagged, base), (5423675.0, 5892453697.0))
        self.assertLess(flagged / base, 0.01)
        self.assertEqual(pct(flagged, base), "0.09%")
        self.assertIn(f"| under 1% | {fmt(flagged)} of {fmt(base)} (0.09%) | yes |", self.doc)
        self.assertIn("hold 0.09% of all services counted (P5)", self.doc)

    def test_after_the_fact_eight_in_split(self):
        eight = [r for r in self.groups if r["main_size"] == "8_in"]
        svc = sum(int(r["services_rows"]) for r in eight)
        self.assertEqual(svc, 636093)
        self.assertEqual(svc, self.m["services_by_size"]["8_in"])
        for r in eight:
            y = int(r["year"])
            if y >= 1984:
                self.assertEqual(int(r["mains_rows"]), 0, r)
            else:
                self.assertEqual(int(r["services_rows"]), 0, r)
            self.assertEqual(int(r["both_rows"]), 0, r)
        self.assertEqual(min(int(r["year"]) for r in eight if int(r["services_rows"])), 1984)
        self.assertEqual(max(int(r["year"]) for r in eight if int(r["mains_rows"])), 1983)
        self.assertIn("all 636,093 services rows labelled `8_in` are from report years 1984-2025, "
                      "and in those years no `8_in` row has a mains value. Before 1984, no `8_in` "
                      "row has a services value.", self.doc)
        self.assertIn("**No row labelled `8_in` has both a mains and a services value**", self.doc)

    def test_sample(self):
        self.assertEqual(len(self.sample), 3000)
        for r in self.sample:
            self.assertTrue(r["main_size"] == "<null>"
                            or (r["main_size"] == "8_in" and r["material"] in NO_MAIN8), r)
        self.assertIn("the first 3,000 flagged rows by year", self.doc)

    def test_disclosure(self):
        for text in ("made with AI agents working in MV2's name",
                     "no person has checked these results by hand",
                     "[plan](phsize-plan.md)", "pudl/issues/4646",
                     "Text and data CC BY 4.0; code Apache-2.0.",
                     "03:06:28 UTC on 11 November 2026",
                     "After the fact (not pre-registered)",
                     "It was not pre-registered.",
                     "None of this has been checked against PHMSA's raw files or forms."):
            self.assertIn(text, self.doc)


if __name__ == "__main__":
    unittest.main()
