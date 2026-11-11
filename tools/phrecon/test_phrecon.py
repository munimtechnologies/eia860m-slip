"""Unit tests for phrecon.py on made-up rows (no data, no polars needed).

Apache-2.0. MV2 of Munim, Inc. (made with AI agents)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import phrecon  # noqa: E402


def b1_rows():
    return [
        # A 2018: B1 total equals the B4 sum exactly
        (2018, "a", 1, "plastic", 70, 30), (2018, "a", 1, "cast_or_wrought_iron", 30, 10),
        (2018, "a", 1, "total", 100, 40),
        # B 2018: mains 0.2 miles over a B4 sum of 50 (inside the 0.3-mile rule)
        (2018, "b", 2, "plastic", 50.2, 20), (2018, "b", 2, "total", 50.2, 20),
        # C 2019: B4 sum 205 vs B1 total 200 (outside 0.5% of 205)
        (2019, "c", 3, "unprotected_steel_bare", 150, 80), (2019, "c", 3, "plastic", 50, 20),
        (2019, "c", 3, "total", 200, 100),
        # D 2019: a negative material value; services 5 vs a B4 sum of 6 (must match exactly)
        (2019, "d", 4, "plastic", -2, 3), (2019, "d", 4, "copper", 12, 2),
        (2019, "d", 4, "total", 10, 5),
        # E 2005: before the 2010 form; mains 80 vs 70
        (2005, "e", 5, "plastic", 80, 40), (2005, "e", 5, "total", 80, 40),
        # F 2018: no B4 report
        (2018, "f", 6, "plastic", 30, 10), (2018, "f", 6, "total", 30, 10),
        # H 2020: mains total left blank
        (2020, "h", 8, "plastic", 5, 9), (2020, "h", 8, "total", None, 9),
        # I 2020: an all_materials row (skipped), a duplicate plastic row; B4 values all blank
        (2020, "i", 9, "plastic", 7, 3), (2020, "i", 9, "all_materials", 7, 3),
        (2020, "i", 9, "plastic", None, None), (2020, "i", 9, "total", 7, 3),
        (None, "x", 9, "plastic", 1, 1),
    ]


def r4(year, rid, op, dec, mains, services, state="IA"):
    return (year, rid, op, "natural_gas", state, dec, mains, services)


def b4_rows():
    return [
        r4(2018, "a", 1, "2010s", 60, 25), r4(2018, "a", 1, "1950s", 40, 15),
        r4(2018, "a", 1, "total_decades", 100, 40),
        r4(2018, "b", 2, "1990s", 50, 20),
        r4(2019, "c", 3, "1960s", 150, 80), r4(2019, "c", 3, "unknown_decade", 55, 20, "IA IL"),
        r4(2019, "d", 4, "2010s", 10, 6),
        r4(2005, "e", 5, "1970s", 70, 40),
        r4(2018, "g", 7, "1980s", 3, 1),
        r4(2020, "h", 8, "2020s", 5, 9),
        r4(2020, "i", 9, "2010s", None, None),
        r4(None, "y", 10, "1950s", 1, 1),
    ]


def build():
    b1, info1, neg, mats = phrecon.agg_b1(b1_rows())
    b4, info4 = phrecon.agg_b4(b4_rows())
    recs, years = phrecon.compare(b1, b4)
    return b1, info1, neg, mats, b4, info4, recs, years


class ConstantTests(unittest.TestCase):
    def test_constants(self):
        self.assertEqual(phrecon.B1_TABLE, "_core_phmsagas__yearly_distribution_by_material")
        self.assertEqual(phrecon.B4_TABLE, "core_phmsagas__yearly_distribution_by_install_decade")
        self.assertTrue((phrecon.BASE % phrecon.B1_TABLE).endswith(phrecon.B1_TABLE + ".parquet"))
        self.assertEqual((phrecon.BIG, phrecon.SHARE_TOL, phrecon.SMALL_MAINS_TOL,
                          phrecon.EXACT_MAINS_TOL), (60.0, 0.005, 0.3, 0.001))
        self.assertEqual((phrecon.LATE_FIRST, phrecon.LATE_LAST, phrecon.PRE_LAST),
                         (2017, 2025, 2009))
        self.assertEqual((phrecon.G2_MIN_LATE, phrecon.G2_MIN_PER_YEAR), (5000, 300))
        self.assertEqual((phrecon.P1_MIN, phrecon.P2_MIN, phrecon.P3_MIN, phrecon.P3_MIN_FAILS,
                          phrecon.P4_MIN, phrecon.P5_GAP, phrecon.P5_MIN_PRE, phrecon.P6_MIN_NEG,
                          phrecon.P7_MIN), (0.97, 0.90, 0.60, 10, 0.95, 0.10, 1000, 1, 0.97))
        self.assertEqual(phrecon.SKIP_MATERIALS, ("all_materials",))


class HelperTests(unittest.TestCase):
    def test_helpers(self):
        self.assertEqual(phrecon.key(None), phrecon.NULL)
        self.assertEqual(phrecon.key(float("nan")), phrecon.NULL)
        self.assertEqual(phrecon.key(12), "12")
        self.assertIsNone(phrecon.num(None))
        self.assertIsNone(phrecon.num(float("nan")))
        self.assertIsNone(phrecon.num("x"))
        self.assertEqual(phrecon.num("2.5"), 2.5)
        self.assertEqual(phrecon.share(1, 4), 0.25)
        self.assertIsNone(phrecon.share(1, 0))
        self.assertIsNone(phrecon.frac(1, 0))

    def test_era(self):
        self.assertEqual([phrecon.era(y) for y in (2009, 2010, 2016, 2017, 2025, 2026)],
                         ["pre_2010", "2010_2016", "2010_2016", "2017_2025", "2017_2025",
                          "other"])

    def test_within(self):
        w = phrecon.within
        self.assertTrue(w(50.2, 50, "mains"))
        self.assertFalse(w(50.4, 50, "mains"))
        self.assertTrue(w(60.3, 60, "mains"))
        self.assertTrue(w(100.5, 100, "mains"))
        self.assertFalse(w(100.6, 100, "mains"))
        self.assertFalse(w(61, 60, "services"))
        self.assertTrue(w(60, 60, "services"))
        self.assertTrue(w(100.5, 100, "services"))
        self.assertTrue(w(1000, 1004, "services"))

    def test_exact(self):
        self.assertTrue(phrecon.exact(10.0005, 10, "mains"))
        self.assertFalse(phrecon.exact(10.002, 10, "mains"))
        self.assertTrue(phrecon.exact(3, 3, "services"))
        self.assertFalse(phrecon.exact(3.5, 3, "services"))


class AggTests(unittest.TestCase):
    def test_b1(self):
        b1, info, neg, mats, _, _, _, _ = build()
        self.assertEqual(len(b1), 8)
        self.assertEqual(b1[(2019, "d", "4")], {"t": [10.0, 5.0], "s": [10.0, 5.0], "n": [2, 2]})
        self.assertEqual(b1[(2020, "h", "8")], {"t": [None, 9.0], "s": [5.0, 9.0], "n": [1, 1]})
        self.assertEqual(b1[(2020, "i", "9")], {"t": [7.0, 3.0], "s": [7.0, 3.0], "n": [1, 1]})
        self.assertEqual(info, {"rows_no_year": 1, "duplicate_rows": 1,
                                "rows_skipped_material": 1, "negative_values": 1,
                                "negative_mains_miles": 1})
        self.assertEqual(neg, [(2019, "d", "4", "plastic", "mains_miles", -2.0)])
        self.assertEqual(mats["2017_2025"]["plastic"], 8)
        self.assertEqual(mats["2017_2025"]["total"], 7)
        self.assertEqual(mats["2017_2025"]["all_materials"], 1)
        self.assertEqual(mats["pre_2010"], {"plastic": 1, "total": 1})

    def test_b4(self):
        _, _, _, _, b4, info, _, _ = build()
        self.assertEqual(len(b4), 8)
        self.assertEqual(b4[(2019, "c", "3")], {"s": [205.0, 100.0], "n": [2, 2],
                                                "commodity": "natural_gas", "state": "IA"})
        self.assertEqual(b4[(2018, "a", "1")]["s"], [100.0, 40.0])
        self.assertEqual(b4[(2020, "i", "9")]["n"], [0, 0])
        self.assertEqual(info, {"total_rows": 1, "rows_other_labels": 1, "rows_no_year": 1})


class CompareTests(unittest.TestCase):
    def test_years(self):
        years = build()[7]
        self.assertEqual(sorted(years), [2005, 2018, 2019, 2020])
        y = years[2005]
        self.assertEqual((y["both"], y["mains_comparable"], y["mains_pass"], y["mains_exact"],
                          y["mains_fail_b4_lower"], y["services_pass"], y["mains_s1s4_pass"],
                          y["services_s1s4_pass"]), (1, 1, 0, 0, 1, 1, 0, 1))
        y = years[2018]
        self.assertEqual((y["both"], y["b1_only"], y["b4_only"], y["mains_comparable"],
                          y["mains_pass"], y["mains_exact"], y["services_exact"],
                          y["mains_s1s4_pass"]), (2, 1, 1, 2, 2, 1, 2, 2))
        y = years[2019]
        self.assertEqual((y["mains_comparable"], y["mains_pass"], y["mains_fail_b4_higher"],
                          y["services_pass"], y["services_fail_b4_higher"],
                          y["mains_s1s4_comparable"], y["mains_s1s4_pass"]),
                         (2, 1, 1, 1, 1, 2, 1))
        y = years[2020]
        self.assertEqual((y["both"], y["mains_comparable"], y["mains_no_b1_total"],
                          y["mains_no_b4_values"], y["services_comparable"],
                          y["services_no_b4_values"], y["mains_b1sum_comparable"],
                          y["services_b1sum_pass"], y["mains_s1s4_comparable"]),
                         (2, 0, 1, 1, 1, 1, 1, 2, 1))

    def test_records(self):
        recs = build()[6]
        self.assertEqual([r["key"][1] for r in recs], ["e", "a", "b", "c", "d", "h", "i"])
        b = recs[2]["mains"]
        self.assertEqual((b["pass"], b["exact"], b["side"]), (True, False, "b4_lower"))
        c = recs[3]["mains"]
        self.assertEqual((c["b1"], c["b4"], c["diff"], c["pass"], c["side"]),
                         (200.0, 205.0, 5.0, False, "b4_higher"))
        self.assertEqual(recs[4]["services"]["side"], "b4_higher")
        self.assertIsNone(recs[5]["mains"])
        self.assertIsNone(recs[5]["mains_b1sum"])
        self.assertIsNone(recs[6]["services"])

    def test_fail_rows(self):
        recs = build()[6]
        rows, n = phrecon.fail_rows(recs)
        self.assertEqual(n, 3)
        self.assertEqual(rows[0], [2005, "e", "5", "natural_gas", "IA", 80.0, 70.0, 80.0, -10.0,
                                   0, 40.0, 40.0, 0.0, 1])
        self.assertEqual(rows[1], [2019, "c", "3", "natural_gas", "IA", 200.0, 205.0, 200.0,
                                   5.0, 0, 100.0, 100.0, 0.0, 1])
        self.assertEqual(rows[2], [2019, "d", "4", "natural_gas", "IA", 10.0, 10.0, 10.0, 0.0,
                                   1, 5.0, 6.0, 1.0, 0])
        rows, n = phrecon.fail_rows(recs, cap=2)
        self.assertEqual((len(rows), n), (2, 3))

    def test_by_year_rows(self):
        header, rows = phrecon.by_year_rows(build()[7])
        self.assertEqual(len(header), 20)
        self.assertEqual([r[0] for r in rows], [2005, 2018, 2019, 2020])
        self.assertEqual(rows[1], [2018, 2, 1, 1, 2, 2, 1, 0, 0, 0, 0, 2, 2, 2, 0, 0, 2, 2, 2, 2])


class ScoreTests(unittest.TestCase):
    def test_score_default(self):
        _, info1, _, _, _, _, _, years = build()
        m, s = phrecon.score(years, info1)
        self.assertEqual((m["late"]["mains_comparable"], m["late"]["mains_pass"],
                          m["late"]["mains_exact"], m["late"]["services_comparable"],
                          m["late"]["services_pass"], m["late"]["mains_b1sum_comparable"],
                          m["late"]["mains_s1s4_comparable"], m["late"]["mains_s1s4_pass"]),
                         (4, 3, 2, 5, 4, 5, 5, 4))
        self.assertEqual((m["late_mains_pass_share"], m["late_mains_exact_share"],
                          m["late_mains_fails"], m["late_fails_b4_higher_share"],
                          m["late_services_pass_share"], m["pre_mains_pass_share"],
                          m["pass_gap_late_minus_pre"], m["b1_negative_values"],
                          m["late_b1sum_mains_pass_share"]),
                         (0.75, 0.5, 1, None, 0.8, 0.0, None, 1, 1.0))
        self.assertEqual(s, {"P1": False, "P2": False, "P3": False, "P4": False, "P5": False,
                             "P6": True, "P7": True})

    def test_score_small_bars(self):
        _, info1, _, _, _, _, _, years = build()
        m, s = phrecon.score(years, info1, p3_min_fails=1, p5_min_pre=1)
        self.assertEqual((m["late_fails_b4_higher_share"], m["pass_gap_late_minus_pre"]),
                         (1.0, 0.75))
        self.assertTrue(s["P3"])
        self.assertTrue(s["P5"])

    def test_nothing_to_test(self):
        m, s = phrecon.score({}, {})
        self.assertIsNone(m["late_mains_pass_share"])
        self.assertEqual(set(s.values()), {False})

    def test_gates(self):
        years = build()[7]
        ok = [{"bytes": 10, "missing_cols": []}, {"bytes": 5, "missing_cols": []}]
        g, gm = phrecon.gates(ok, years)
        self.assertEqual(g, {"G1": True, "G2": False})
        self.assertEqual(gm["late_mains_comparable"], 4)
        self.assertEqual(gm["mains_comparable_by_late_year"]["2018"], 2)
        self.assertEqual(gm["mains_comparable_by_late_year"]["2017"], 0)
        self.assertEqual(len(gm["mains_comparable_by_late_year"]), 9)
        self.assertEqual(gm["late_years_with_enough"], 0)
        g, _ = phrecon.gates([ok[0], {"bytes": 5, "missing_cols": ["services"]}], years)
        self.assertFalse(g["G1"])


if __name__ == "__main__":
    unittest.main()
