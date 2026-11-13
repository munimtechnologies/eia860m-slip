"""Checks that every number stated in docs/phdecade.md (result of pre-registration phdecade-1) is
what data/phdecade-run.json and the three CSVs (the job's outputs, unchanged) say. Reads no
outside data.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import csv
import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ORDER = ("pre_1940", "1940s", "1950s", "1960s", "1970s", "1980s", "1990s", "2000s", "2010s",
         "2020s", "unknown_decade")
TOL = 0.001


def path(rel):
    return os.path.join(HERE, rel)


def n0(x):
    """Thousands separators, rounded to a whole number ("-0" written as "0")."""
    s = f"{float(x):,.0f}"
    return "0" if s == "-0" else s


def pct(a, b, digits=2):
    return f"{100.0 * a / b:.{digits}f}%"


def read_csv(rel):
    with open(path(rel), encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


class PhdecadeResultTests(unittest.TestCase):
    # The job's JSON is kept as `res`: naming it `run` would hide unittest's TestCase.run.
    @classmethod
    def setUpClass(cls):
        with open(path("docs/phdecade.md"), encoding="utf-8") as fh:
            cls.doc = fh.read()
        with open(path("data/phdecade-run.json"), encoding="utf-8") as fh:
            cls.res = json.load(fh)
        cls.by = read_csv("data/phdecade-by-year-decade.csv")
        cls.pairs = read_csv("data/phdecade-pairs.csv")
        cls.top = read_csv("data/phdecade-top-old-changes.csv")
        cls.m = cls.res["measures"]

    def test_run_and_scores(self):
        self.assertEqual(self.res["tool"], "phdecade.py 0.1.0")
        self.assertEqual((self.res["started"], self.res["finished"]),
                         ("2026-11-13T02:06:24Z", "2026-11-13T02:06:26Z"))
        self.assertIn("13 November 2026, 02:06:24-02:06:26 UTC", self.doc)
        self.assertEqual(self.res["scores"], {"G1": True, "G2": True, "P1": False, "P2": True,
                                              "P3": True, "P4": True, "P5": True, "P6": True})
        self.assertIn("**5 of the 6 predictions held (P2-P6); P1 failed.**", self.doc)
        self.assertIn("| at least 40% | 4,200 of 14,430 (29.11%) | **no** |", self.doc)

    def test_input_and_gates(self):
        t = self.res["table"]
        self.assertEqual((t["bytes"], t["rows"], t["rows_in_window"], t["missing_cols"],
                          t["years"]), (1034817, 324580, 170075, [], [2004, 2025]))
        self.assertIn("md5 `" + t["md5"] + "`, 1,034,817 bytes", self.doc)
        self.assertEqual(t["last_modified"], "Thu, 12 Nov 2026 08:25:35 GMT")
        self.assertIn("Last-Modified 12 Nov 2026 08:25:35 GMT", self.doc)
        self.assertIn("It has 324,580 rows from report years 2004-2025, 170,075 of them in "
                      "2015-2025.", self.doc)
        self.assertEqual((self.res["keys"], self.res["key_years"]), (1657, 16121))
        self.assertEqual(self.res["ambiguous_key_years_by_year"], {"2025": 1})
        self.assertIn("1,657 keys (operator, commodity, state) and 16,121 key-years. One key-year "
                      "(in 2025)", self.doc)
        g = self.res["gate_measures"]
        self.assertEqual((g["pairs"], g["years_with_enough_pairs"]), (14430, 10))
        self.assertIn("| 14,430 pairs; 10 of 10 year pairs with at least 100 | yes |", self.doc)
        parts = [f"{k}: {n0(v)}" for k, v in sorted(g["pairs_by_t"].items())]
        self.assertIn("Pairs by first year: " + "; ".join(parts) + ".", self.doc)
        self.assertEqual(len(self.pairs), g["pairs"])

    def test_predictions(self):
        m = self.m
        n = m["pairs"]
        self.assertEqual(m["pairs_old_mains_changed"], 4200)
        self.assertEqual(pct(4200, n), "29.11%")
        self.assertIn("**Older decades change in 4,200 of 14,430 operator-year pairs (29.11%)**",
                      self.doc)
        self.assertEqual(m["pairs_old_mains_material"], 2545)
        self.assertIn("2,545 pairs (17.64%)", self.doc)
        self.assertEqual(pct(2545, n), "17.64%")
        a, b = m["miles_t_old_changed"], m["miles_t_all"]
        line = f"{n0(a)} of {n0(b)} ({pct(a, b)})"
        self.assertEqual(line, "12,216,055 of 13,195,131 (92.58%)")
        self.assertIn("| at least 80% | " + line + " | yes |", self.doc)
        self.assertIn("they hold " + line.replace(" (", " miles of main ("), self.doc)
        self.assertIn("| below -0.001 miles | " + n0(m["net_old_dm"]) + " miles | yes |", self.doc)
        self.assertIn("lose mains on net: -44,619 miles**", self.doc)
        go, gc = m["gross_old_dm"], m["gross_cur_dm"]
        self.assertIn(f"| at least 25% | {n0(go)} / {n0(gc)} ({pct(go, gc)}) | yes |", self.doc)
        self.assertIn(f"add up to {n0(go)} miles, {go / gc:.2f} times the current decade's "
                      f"{n0(gc)}**", self.doc)
        self.assertEqual(m["years_old4_net_negative"], 8)
        self.assertIn("| at least 8 of 10 | 8 of 10 | yes |", self.doc)
        self.assertEqual(m["pairs_old_services_changed"], 6608)
        self.assertIn("| at least 40% | 6,608 of 14,430 (45.79%) | yes |", self.doc)
        self.assertEqual(pct(6608, n), "45.79%")

    def test_two_ways_of_differencing(self):
        m = self.m
        self.assertAlmostEqual(m["net_cur_dm"] + m["net_old_dm"], m["net_total_dm"], places=2)
        self.assertIn("the current decade gains 188,698 miles", self.doc)
        self.assertEqual(n0(m["net_cur_dm"]), "188,698")
        self.assertEqual(n0(m["net_total_dm"]), "144,079")
        self.assertIn("Differencing the totals gives 144,079 miles; differencing the current "
                      "decade gives 188,698.", self.doc)
        gap = pct(-m["net_old_dm"], m["net_cur_dm"], 1)
        self.assertIn("The gap is " + gap + " of the current-decade figure.", self.doc)
        self.assertIn("that is 188,698 miles of main, against a change in total main of 144,079",
                      self.doc)
        cur = [r for r in self.by if r["is_current"] == "1"]
        # The CSV values are rounded to 3 decimals, so the sums can differ in the last places.
        self.assertAlmostEqual(sum(float(r["net_mains_change"]) for r in cur), m["net_cur_dm"],
                               delta=0.1)
        old = [r for r in self.by if r["is_current"] == "0"]
        self.assertAlmostEqual(sum(float(r["net_mains_change"]) for r in old), m["net_old_dm"],
                               delta=0.1)

    def test_why_p1_failed(self):
        m = self.m
        n = m["pairs"]
        no_old = n - m["pairs_old_mains_changed"]
        self.assertEqual((no_old, m["pairs_static"], no_old - m["pairs_static"]),
                         (10230, 3075, 7155))
        self.assertIn("of the 10,230 pairs with no old mains change, 3,075 (21.31% of all pairs) "
                      "changed nothing at all, and the other 7,155", self.doc)
        rest = pct(m["miles_t_all"] - m["miles_t_old_changed"], m["miles_t_all"])
        self.assertIn("Together these pairs hold " + rest + " of the miles", self.doc)
        self.assertEqual(sum(1 for r in self.pairs if int(r["old_buckets_mains_changed"])), 4200)

    def test_bucket_table(self):
        dec = self.m["old_by_decade"]
        self.assertEqual(set(dec), set(ORDER))
        for d in ORDER:
            v = dec[d]
            row = "| `%s` | %s |" % (d, " | ".join(n0(x) for x in v))
            self.assertIn(row, self.doc, d)
        self.assertEqual(max(ORDER, key=lambda d: dec[d][5]), "unknown_decade")
        self.assertIn("`unknown_decade` has the largest gross change of any old bucket (97,279 "
                      "miles), then the `1960s` (36,011) and `pre_1940` (33,262).", self.doc)
        ranked = sorted(ORDER, key=lambda d: -dec[d][5])
        self.assertEqual(ranked[:3], ["unknown_decade", "1960s", "pre_1940"])
        self.assertEqual(sum(1 for r in self.by if r["is_current"] == "0" and r["decade"] == "2010s"
                             and int(r["t"]) < 2019), 0)
        self.assertEqual({int(r["t"]) for r in self.by
                          if r["is_current"] == "0" and r["decade"] == "2020s"},
                         {2015, 2016, 2017, 2018})

    def test_old4_and_current_negative(self):
        parts = [f"{k}: {n0(v)}" for k, v in sorted(self.m["old4_net_dm_by_t"].items())]
        self.assertIn("Net mains change of the four oldest buckets by first year: "
                      + "; ".join(parts) + ".", self.doc)
        self.assertEqual(self.m["pairs_cur_negative"], 208)
        self.assertIn("The current decade went down in 208 pairs.", self.doc)

    def test_after_the_fact_services(self):
        cur = sum(float(r["net_services_change"]) for r in self.by if r["is_current"] == "1")
        old = sum(float(r["net_services_change"]) for r in self.by if r["is_current"] == "0")
        self.assertEqual((n0(cur), n0(-old)), ("12,547,040", "6,237,105"))
        self.assertAlmostEqual(old, sum(v[6] for v in self.m["old_by_decade"].values()), places=2)
        self.assertIn("the current decade gains 12,547,040 services and the old buckets lose "
                      "6,237,105 on net (" + pct(-old, cur, 1) + " of the current-decade gain)",
                      self.doc)

    def test_after_the_fact_2010s(self):
        rows = sorted((int(r["t"]), float(r["net_mains_change"])) for r in self.by
                      if r["decade"] == "2010s" and r["is_current"] == "0")
        self.assertEqual([t for t, _ in rows], list(range(2019, 2025)))
        parts = [f"{t}: {n0(v)}" for t, v in rows]
        self.assertIn("Net mains change of the `2010s` bucket by first year: " + "; ".join(parts)
                      + ".", self.doc)
        self.assertIn("It still grew by 4,184 miles from the 2019 report to the 2020 report.",
                      self.doc)

    def test_after_the_fact_redating_examples(self):
        self.assertEqual(len(self.top), 300)

        def find(t, dec):
            for r in self.top:
                if (r["t"], r["operator_id_phmsa"], r["commodity"], r["operating_state"],
                        r["decade"]) == (str(t), "4473", "natural_gas", "TX", dec):
                    return float(r["mains_t"]), float(r["mains_t1"])
            raise AssertionError((t, dec))

        self.assertEqual(find(2016, "unknown_decade"), (0.0, 5518.72))
        self.assertEqual(find(2016, "1950s"), (2338.0, 6.23))
        self.assertEqual(find(2021, "unknown_decade"), (5162.94, 3.79))
        self.assertEqual(find(2021, "pre_1940"), (8.12, 3712.2))
        for text in ("went from 0 to 5,518.72 miles in `unknown_decade` from 2016 to 2017",
                     "its `1950s` went from 2,338 to 6.23",
                     "From 2021 to 2022 its `unknown_decade` went from 5,162.94 to 3.79",
                     "its `pre_1940` went from 8.12 to 3,712.2"):
            self.assertIn(text, self.doc)

    def test_disclosure(self):
        for text in ("made with AI agents working in MV2's name",
                     "no person has checked these results by hand",
                     "[plan](phdecade-plan.md)", "pudl/issues/5505",
                     "Text and data CC BY 4.0; code Apache-2.0.",
                     "04:38:08 UTC on 11 November 2026",
                     "**After the fact (not pre-registered): services.**",
                     "P1 is reported as failed and is not re-scored.",
                     "None of this has been checked against PHMSA's raw files or forms."):
            self.assertIn(text, self.doc)


if __name__ == "__main__":
    unittest.main()
