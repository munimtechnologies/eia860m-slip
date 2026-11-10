"""Unit tests for phleak.py on made-up rows (no download, no polars).

Apache-2.0. MV2 of Munim, Inc. (made with AI agents working in MV2's name)."""

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import phleak as P  # noqa: E402

A, H = "all_leaks", "hazardous_leaks"
ROWS = [
    # report A: 2016, one state, natural gas
    ("A", "2016-01-01", "100", "Natural Gas", "TX", A, "corrosion_failure", 3.0, 1.0),
    ("A", "2016-01-01", "100", "Natural Gas", "TX", A, "excavation_damage", 2.0, 0.0),
    ("A", "2016-01-01", "100", "Natural Gas", "TX", A, "total", 5.0, 1.0),
    ("A", "2016-01-01", "100", "Natural Gas", "TX", H, "corrosion_failure", 1.0, 0.0),
    ("A", "2016-01-01", "100", "Natural Gas", "TX", H, "total", 4.0, 0.0),
    # report B: 1990, operator 0, no commodity, two states
    ("B", "1990-01-01", "0", None, "NY NJ", A, "third_party", 2.0, None),
    ("B", "1990-01-01", "0", None, "NY NJ", A, "total", 2.0, None),
    ("B", "1990-01-01", "0", None, "NY NJ", H, "third_party", 3.0, float("nan")),
    # report C: 2016, unknown commodity, no state, a negative and a duplicated total
    ("C", "2016-01-01", "200", "OTHER GAS: Helium", None, A, "total", -1.0, 2.0),
    ("C", "2016-01-01", "200", "OTHER GAS: Helium", None, A, "total", 0.0, 0.0),
]


def profile(rows=ROWS):
    prof = P.Profile()
    for row in rows:
        prof.add(row)
    return prof


class ConstantTests(unittest.TestCase):
    def test_constants(self):
        self.assertEqual(P.VERSION, "0.1.0")
        self.assertEqual(len(P.SOURCES), 13)
        self.assertIn("total", P.SOURCES)
        self.assertEqual(len(P.COMMODITY_MAP), 15)
        self.assertEqual(P.COMMODITY_MAP["OTHER GAS: City of York"], "other")
        self.assertEqual(P.TOL, 1.0)
        self.assertEqual(len(P.COLS), 9)
        self.assertTrue(P.URL.endswith("/nightly/_core_phmsagas__yearly_distribution_leaks.parquet"))


class HelperTests(unittest.TestCase):
    def test_text_num_year(self):
        self.assertIsNone(P.text(None))
        self.assertIsNone(P.text(float("nan")))
        self.assertEqual(P.text(" TX"), " TX")
        self.assertIsNone(P.num(None))
        self.assertIsNone(P.num("x"))
        self.assertIsNone(P.num(float("nan")))
        self.assertEqual(P.num("3"), 3.0)
        self.assertEqual(P.year("2015-01-01"), 2015)
        self.assertEqual(P.year("1990-01-01 00:00:00.000000"), 1990)
        self.assertEqual(P.year(None), 0)
        self.assertEqual(P.year("n/a"), 0)

    def test_state_kind(self):
        self.assertEqual(P.state_kind("TX"), "single")
        self.assertEqual(P.state_kind(" TX "), "single")
        self.assertEqual(P.state_kind("NY NJ"), "multi")
        self.assertEqual(P.state_kind("ny,nj, ct"), "multi")
        self.assertEqual(P.state_kind(None), "null")
        self.assertEqual(P.state_kind("  "), "null")
        self.assertEqual(P.state_kind("Texas"), "other")
        self.assertEqual(P.state_kind("NEW YORK"), "other")
        self.assertEqual(P.state_kind("tx"), "other")

    def test_share(self):
        self.assertIsNone(P.share(1, 0))
        self.assertEqual(P.share(4, 5), 0.8)


class ProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prof = profile()

    def test_counts(self):
        p = self.prof
        self.assertEqual(p.rows, 10)
        self.assertEqual(len(p.groups), 3)
        self.assertEqual(p.commodity, {"Natural Gas": 5, P.NULL: 3, "OTHER GAS: Helium": 2})
        self.assertEqual(p.commodity_years[P.NULL], [1990, 1990])
        self.assertEqual(p.state_kinds, {"single": 5, "multi": 3, "null": 2})
        self.assertEqual(p.multi_by_year, {1990: 3})
        self.assertEqual(p.state_null_by_year, {2016: 2})
        self.assertEqual(p.op_zero_by_year, {1990: 3})
        self.assertEqual(p.neg_rows, 1)
        self.assertEqual(p.negatives[0][:3], [2016, "C", "200"])
        self.assertEqual(p.empty_rows, 0)
        s = p.summary()
        self.assertEqual(s["years"], [1990, 2016])
        self.assertEqual(s["source"]["total"], [5, 1990, 2016])

    def test_sum_checks(self):
        counts, by_year, fails = P.sum_checks(self.prof.groups)
        self.assertEqual(counts["mains|checked"], 3)
        self.assertEqual(counts["mains|passed"], 2)
        self.assertEqual(counts["mains|failed"], 1)
        self.assertEqual(counts["services|checked"], 2)
        self.assertEqual(counts["services|passed"], 2)
        self.assertEqual(counts["services|failed"], 0)
        self.assertEqual(counts["mains|no_total"], 1)
        self.assertEqual(counts["mains|total_only"], 1)
        self.assertEqual(counts["services|total_only"], 1)
        self.assertEqual(counts["hazardous_leaks|mains|failed"], 1)
        self.assertEqual(by_year[2016], {"checked": 4, "failed": 1})
        self.assertEqual(fails, [[2016, "A", "100", "Natural Gas", "TX", H, "mains",
                                  4.0, 1.0, 3.0, 1]])

    def test_tolerance(self):
        rows = [("D", "2020-01-01", "5", "Natural Gas", "CA", A, "other", 2.0, 2.0),
                ("D", "2020-01-01", "5", "Natural Gas", "CA", A, "total", 3.0, 4.0)]
        counts, _, fails = P.sum_checks(profile(rows).groups)
        self.assertEqual(counts["mains|passed"], 1)
        self.assertEqual(counts["services|failed"], 1)
        self.assertEqual(len(fails), 1)

    def test_haz_checks(self):
        hz, viol = P.haz_checks(self.prof.groups)
        self.assertEqual(hz["compared"], 5)
        self.assertEqual(hz["ok"], 4)
        self.assertEqual(hz["hazardous_gt_all"], 1)
        self.assertEqual(viol, [[1990, "B", "0", P.NULL, "NY NJ", "third_party", "mains", 2.0, 3.0]])

    def test_pk_dupes(self):
        extra, keys, ex = P.pk_dupes(self.prof.groups)
        self.assertEqual((extra, keys), (1, 1))
        self.assertEqual(ex, [["C", "200", P.NULL, A, "total", 2]])
        rows = [("D", "2016-01-01", "300", "Natural Gas", "CA", A, "total", 1.0, 1.0),
                ("D", "2016-01-01", "300", "Propane Gas", "CA", A, "total", 1.0, 1.0),
                ("D", "2016-01-01", "300", "Propane Gas", "CA", A, "other", 1.0, 1.0)]
        self.assertEqual(P.pk_dupes(profile(rows).groups)[:2], (1, 1))

    def test_multi_state_score(self):
        ms = P.multi_state_score(self.prof.multi_by_year)
        self.assertEqual((ms["rows"], ms["share"], ms["ok"]), (3, 1.0, False))
        ms = P.multi_state_score({1990: 96, 2005: 4}, min_rows=100)
        self.assertEqual((ms["rows_to_2003"], ms["share"], ms["ok"]), (96, 0.96, True))
        self.assertFalse(P.multi_state_score({1990: 94, 2005: 6})["ok"])

    def test_score(self):
        m, scores, tables = P.score(self.prof)
        cm = m["commodity"]
        self.assertEqual(cm["pre_2015_nonnull_rows"], 0)
        self.assertEqual(cm["from_2015_rows"], 7)
        self.assertEqual(cm["from_2015_null_share"], 0.0)
        self.assertEqual(cm["unmapped_values"], ["OTHER GAS: Helium"])
        self.assertEqual(cm["unmapped_rows"], 2)
        self.assertEqual((m["sums"]["checked"], m["sums"]["passed"], m["sums"]["share"]),
                         (5, 4, 0.8))
        self.assertEqual(m["hazardous_vs_all"]["share"], 0.8)
        self.assertEqual(scores, {"P1": True, "P2": False, "P3": False, "P4": False,
                                  "P5": False, "P6": False, "P7": False})
        self.assertEqual(tables["phleak-multistate-reports.csv"][1],
                         [[1990, "B", "0", P.NULL, "NY NJ", 3]])
        self.assertEqual(len(tables["phleak-commodity.csv"][1]), 3)
        self.assertEqual(sorted(tables), ["phleak-commodity.csv", "phleak-hazardous-gt-all.csv",
                                          "phleak-multistate-reports.csv", "phleak-negatives.csv",
                                          "phleak-pk-duplicates.csv", "phleak-sum-failures.csv"])

    def test_clean_rows_score_true(self):
        rows = [("E", "2016-01-01", "7", "Natural Gas", "OH", A, "corrosion_failure", 1.0, 2.0),
                ("E", "2016-01-01", "7", "Natural Gas", "OH", A, "total", 1.0, 2.0),
                ("E", "2016-01-01", "7", "Natural Gas", "OH", H, "corrosion_failure", 1.0, 0.0),
                ("E", "2016-01-01", "7", "Natural Gas", "OH", H, "total", 1.0, 0.0)]
        m, scores, _ = P.score(profile(rows))
        self.assertTrue(all(scores[k] for k in ("P1", "P2", "P3", "P4", "P5", "P7")))
        self.assertFalse(scores["P6"])

    def test_gates(self):
        info = {"bytes": 10, "missing_cols": []}
        g, gm = P.gates(info, self.prof)
        self.assertEqual(g, {"G1": True, "G2": False, "G3": True})
        bad = profile(ROWS + [("Z", "2016-01-01", "1", None, "TX", A, "mystery", 1.0, 1.0)])
        self.assertFalse(P.gates(info, bad)[0]["G3"])
        self.assertFalse(P.gates({"bytes": 10, "missing_cols": ["mains"]}, self.prof)[0]["G1"])
        self.assertTrue(math.isfinite(gm["rows"]))


if __name__ == "__main__":
    unittest.main()
