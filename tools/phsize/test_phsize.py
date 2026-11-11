"""Unit tests for phsize.py on made-up grouped rows (no data, no polars needed).

Apache-2.0. MV2 of Munim, Inc. (made with AI agents)."""

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import phsize  # noqa: E402


def grp(year, material, size, services_rows=0, services_sum=0.0, mains_rows=0, both=0, rows=None):
    return {"year": year, "material": material, "main_size": size,
            "rows": rows if rows is not None else max(services_rows, mains_rows),
            "mains_rows": mains_rows, "services_rows": services_rows, "both_rows": both,
            "mains_sum": float(mains_rows), "services_sum": services_sum}


class ConstantTests(unittest.TestCase):
    def test_constants(self):
        self.assertEqual(phsize.TABLE, "_core_phmsagas__yearly_distribution_by_material_and_size")
        self.assertTrue(phsize.URL.endswith(phsize.TABLE + ".parquet"))
        self.assertIn(phsize.NULL, phsize.SERVICE_SIZES)
        self.assertNotIn("over_12_in", phsize.SERVICE_SIZES)
        self.assertNotIn("2_in_or_less", phsize.SERVICE_SIZES)
        for m in phsize.OVER6:
            self.assertIn(m, phsize.NULL_OK)
        self.assertEqual(set(phsize.NO_MAIN8) & set(phsize.OVER6), set())
        self.assertEqual((phsize.P1_MIN, phsize.P2_MIN, phsize.P3_MIN, phsize.P4_MAX_OTHER,
                          phsize.P5_MAX_SHARE), (100, 0.99, 100, 0, 0.01))


class HelperTests(unittest.TestCase):
    def test_key_fnum_share(self):
        self.assertEqual(phsize.key(None), phsize.NULL)
        self.assertEqual(phsize.key(float("nan")), phsize.NULL)
        self.assertEqual(phsize.key("8_in"), "8_in")
        self.assertEqual(phsize.fnum(None), 0.0)
        self.assertEqual(phsize.fnum(float("nan")), 0.0)
        self.assertEqual(phsize.fnum("2.5"), 2.5)
        self.assertEqual(phsize.share(1, 4), 0.25)
        self.assertIsNone(phsize.share(1, 0))


class StudyTests(unittest.TestCase):
    def make(self):
        return phsize.Study([
            grp(1990, "steel", None, services_rows=150, services_sum=30.0),
            grp(1991, "other_alt", None, services_rows=5, services_sum=2.0),
            grp(1990, "steel", "8_in", services_rows=10, services_sum=1.0, mains_rows=10, both=4),
            grp(1990, "pe", "8_in", services_rows=120, services_sum=3.0),
            grp(1990, "pe", "1_to_2_in", services_rows=1000, services_sum=10000.0),
            grp(1990, "pe", "total", services_rows=1000, services_sum=99999.0),
            grp(1990, "steel", "2_in_or_less", mains_rows=500),
        ])

    def test_totals_and_gates(self):
        st = self.make()
        t, years = st.totals()
        self.assertEqual((t["services_rows"], t["mains_rows"], t["both_rows"], years),
                         (2285, 510, 4, [1990, 1991]))
        g, gm = phsize.gates({"bytes": 10, "missing_cols": []}, st)
        self.assertEqual(g, {"G1": True, "G2": False})  # fewer than 100,000 rows
        g, _ = phsize.gates({"bytes": 10, "missing_cols": ["services"]}, st)
        self.assertFalse(g["G1"])

    def test_sizes(self):
        st = self.make()
        self.assertEqual(st.services_by_size(), {phsize.NULL: 155, "1_to_2_in": 1000, "8_in": 130,
                                                 "total": 1000})
        self.assertEqual(st.mains_by_size(), {"2_in_or_less": 500, "8_in": 10})

    def test_score(self):
        m, s = self.make().score()
        self.assertEqual(m["null_size_rows"], 155)
        self.assertEqual(m["null_size_rows_expected_material"], 155)
        self.assertEqual(m["null_size_by_material"]["steel"], [150, 1990, 1990, 30.0, 0])
        self.assertEqual(m["null_size_by_year"], {"1990": 150, "1991": 5})
        self.assertEqual(m["eight_in_no_main8_rows"], 120)
        self.assertEqual(m["eight_in_by_material"]["steel"], [10, 1990, 1990, 1.0, 4])
        self.assertEqual(m["services_other_sizes"], {})
        base = 30.0 + 2.0 + 1.0 + 3.0 + 10000.0
        self.assertEqual(m["services_sum_non_total"], base)
        self.assertEqual(m["shares"]["null_sum"], round(32.0 / base, 6))
        self.assertEqual(m["shares"]["null_plus_eight_sum"], round(35.0 / base, 6))
        self.assertEqual(s, {"P1": True, "P2": True, "P3": True, "P4": True, "P5": True})

    def test_score_failures(self):
        st = phsize.Study([
            grp(1990, "pvc", None, services_rows=50, services_sum=500.0),
            grp(1990, "steel", "over_12_in", services_rows=3, services_sum=1.0),
            grp(1990, "pe", "1_to_2_in", services_rows=10, services_sum=10.0),
        ])
        m, s = st.score()
        self.assertEqual(m["null_size_rows_expected_material"], 0)
        self.assertEqual(m["services_other_sizes"], {"over_12_in": 3})
        self.assertEqual(s, {"P1": False, "P2": False, "P3": False, "P4": False, "P5": False})

    def test_nothing_to_test(self):
        m, s = phsize.Study([grp(1990, "pe", "1_to_2_in", services_rows=10,
                                 services_sum=10.0)]).score()
        self.assertEqual(m["null_size_rows"], 0)
        self.assertIsNone(m["shares"]["null_ok"])
        self.assertFalse(s["P2"])
        self.assertTrue(s["P5"])

    def test_nan_year_and_sums(self):
        st = phsize.Study([{"year": None, "material": None, "main_size": float("nan"),
                            "rows": 1, "mains_rows": 0, "services_rows": 1, "both_rows": 0,
                            "mains_sum": None, "services_sum": float("nan")}])
        r = st.g[0]
        self.assertEqual((r["year"], r["material"], r["main_size"], r["services_sum"]),
                         (0, phsize.NULL, phsize.NULL, 0.0))
        self.assertFalse(math.isnan(r["mains_sum"]))


if __name__ == "__main__":
    unittest.main()
