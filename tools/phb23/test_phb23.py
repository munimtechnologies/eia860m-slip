"""Unit tests for phb23.py on made-up rows (no data; the one polars test is skipped without polars).

Apache-2.0. MV2 of Munim, Inc. (made with AI agents)."""

import datetime
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import phb23  # noqa: E402

try:
    import polars as pl
except ImportError:  # the publish test environment has no polars
    pl = None


def b1_rows():
    return [
        # A 2018: everything agrees
        (2018, "a", 1, "unprotected_steel_bare", 40, 10),
        (2018, "a", 1, "cathodically_protected_steel_coated", 60, 20),
        (2018, "a", 1, "plastic", 100, 50), (2018, "a", 1, "total", 200, 80),
        (2018, "a", 1, "all_materials", 200, 80),
        # B 2019: B2 agrees with B1, B4 is higher; pvc alone matches B1 plastic
        (2019, "b", 2, "plastic", 50, 10), (2019, "b", 2, "copper", 50, 5),
        (2019, "b", 2, "total", 100, 15),
        # D 2020: no B2 report
        (2020, "d", 4, "total", 5, 1),
        # E 2020: B2 grand total mains blank
        (2020, "e", 5, "total", 7, 3), (2020, "e", 5, "cast_iron", 7, 3),
        (None, "x", 9, "total", 1, 1),
    ]


def b2_rows():
    return [
        (2018, "a", 1, "steel", "2_in_or_less", 30, None),
        (2018, "a", 1, "steel", "2_to_4_in", 70, None),
        (2018, "a", 1, "steel", "1_in_or_less", None, 30),
        (2018, "a", 1, "steel", "total", 100, 30),
        (2018, "a", 1, "pvc", "2_in_or_less", 20, None),
        (2018, "a", 1, "pvc", "total", 20, 0),
        (2018, "a", 1, "pe", "2_in_or_less", 80, None),
        (2018, "a", 1, "pe", "1_in_or_less", None, 50),
        (2018, "a", 1, "pe", "total", 80, 50),
        (2018, "a", 1, "all_materials", "2_in_or_less", 130, None),
        (2018, "a", 1, "all_materials", "total", 200, 80),
        (2019, "b", 2, "pvc", "total", 50, 10),
        (2019, "b", 2, "pe", "total", 30, 4),
        (2019, "b", 2, "copper", "total", 50, 5),
        (2019, "b", 2, "copper", "2_to_4_in", 50, None),
        (2019, "b", 2, "pvc", "2_in_or_less", 50, None),
        (2019, "b", 2, "pe", "2_in_or_less", 30, None),
        (2019, "b", 2, "copper", "1_in_or_less", None, 5),
        (2019, "b", 2, "all_materials", "total", 100, 15),
        (2019, "b", 2, "steel", None, None, 7),
        # C 2005: B2 only
        (2005, "c", 3, "plastic", "total", 10, 2),
        (2005, "c", 3, "plastic", "2_to_4_in", 10, None),
        (2005, "c", 3, "plastic", None, None, 2),
        (2005, "c", 3, "total", "total", 10, 2),
        (2020, "e", 5, "all_materials", "total", None, 3),
        (2020, "e", 5, "cast_iron", "total", 7, 3),
        (2020, "e", 5, "cast_iron", "2_in_or_less", 7, None),
        (2020, "e", 5, "cast_iron", "1_in_or_less", None, 3),
        (None, "x", 9, "steel", "total", 1, 1),
    ]


def b4_rows():
    return [
        (2018, "a", 1, "1990s", 150, 60), (2018, "a", 1, "2010s", 50, 20),
        (2018, "a", 1, "total_decades", 200, 80),
        (2019, "b", 2, "1960s", 110, 15),
        (2020, "d", 4, "2020s", 5, 1),
        (2020, "e", 5, "2010s", None, None),
        (None, "y", 9, "1950s", 1, 1),
    ]


def build():
    b1, i1 = phb23.agg_b1(b1_rows())
    b2, i2 = phb23.agg_b2(b2_rows())
    b4, i4 = phb23.agg_b4(b4_rows())
    recs, years, grp = phb23.compare(b1, b2, b4)
    return {"b1": b1, "i1": i1, "b2": b2, "i2": i2, "b4": b4, "i4": i4, "recs": recs,
            "years": years, "grp": grp}


class ConstantTests(unittest.TestCase):
    def test_constants(self):
        self.assertEqual(phb23.B1_TABLE, "_core_phmsagas__yearly_distribution_by_material")
        self.assertEqual(phb23.B2_TABLE,
                         "_core_phmsagas__yearly_distribution_by_material_and_size")
        self.assertEqual(phb23.B4_TABLE, "core_phmsagas__yearly_distribution_by_install_decade")
        self.assertTrue((phb23.BASE % phb23.B2_TABLE).endswith(phb23.B2_TABLE + ".parquet"))
        self.assertEqual((phb23.BIG, phb23.SHARE_TOL, phb23.SMALL_MAINS_TOL),
                         (60.0, 0.005, 0.3))
        self.assertEqual((phb23.LATE_FIRST, phb23.LATE_LAST), (2017, 2025))
        self.assertEqual((phb23.G2_MIN_LATE, phb23.G2_MIN_PER_YEAR, phb23.G2_MIN_YEARS),
                         (5000, 300, 7))
        self.assertEqual((phb23.P1_MIN, phb23.P2_MIN, phb23.P3_MIN, phb23.P4_MIN, phb23.P5_MIN,
                          phb23.P5_MIN_N, phb23.P6_MAX, phb23.P7_MIN, phb23.P8_MIN,
                          phb23.P8_MIN_FAILS),
                         (0.97, 0.97, 0.97, 0.95, 0.90, 100, 0.10, 0.95, 0.60, 10))

    def test_groups(self):
        self.assertEqual(phb23.group("unprotected_steel_coated"), "steel")
        self.assertEqual(phb23.group("steel"), "steel")
        self.assertEqual(phb23.group("pe"), "plastic")
        self.assertEqual(phb23.group("plastic"), "plastic")
        self.assertEqual(phb23.group("other_alt"), "other")
        self.assertEqual(phb23.group("copper"), "copper")


class HelperTests(unittest.TestCase):
    def test_helpers(self):
        self.assertEqual(phb23.key(None), phb23.NULL)
        self.assertEqual(phb23.key(float("nan")), phb23.NULL)
        self.assertIsNone(phb23.num("x"))
        self.assertEqual(phb23.num("2.5"), 2.5)
        self.assertIsNone(phb23.share(1, 0))
        self.assertEqual(phb23.flag(None), "")
        self.assertEqual(phb23.flag(True), 1)
        acc = [None, None]
        phb23.add(acc, 0, None)
        phb23.add(acc, 1, 2.0)
        phb23.add(acc, 1, 3.0)
        self.assertEqual(acc, [None, 5.0])

    def test_within(self):
        w = phb23.within
        self.assertTrue(w(50.2, 50, "mains"))
        self.assertFalse(w(50.4, 50, "mains"))
        self.assertTrue(w(60.3, 60, "mains"))
        self.assertTrue(w(100.5, 100, "mains"))
        self.assertFalse(w(100.6, 100, "mains"))
        self.assertFalse(w(61, 60, "services"))
        self.assertTrue(w(1000, 1004, "services"))
        self.assertFalse(w(20, 100, "mains"))


class AggTests(unittest.TestCase):
    def test_b1(self):
        d = build()
        self.assertEqual(len(d["b1"]), 4)
        self.assertEqual(d["b1"][(2018, "a", "1")],
                         {"t": [200.0, 80.0], "g": {"steel": [100.0, 30.0],
                                                     "plastic": [100.0, 50.0]}})
        self.assertEqual(d["i1"], {"b1_rows_all_materials": 1, "b1_rows_no_year": 1})

    def test_b2(self):
        d = build()
        self.assertEqual(len(d["b2"]), 4)
        a = d["b2"][(2018, "a", "1")]
        self.assertEqual(a["G"], [200.0, 80.0])
        self.assertEqual(a["C"], [200.0, 80.0])
        self.assertEqual(a["M"], {"steel": [100.0, 30.0], "plastic": [100.0, 50.0]})
        self.assertEqual((a["pvc"], a["plo"]), ([20.0, 0.0], [80.0, 50.0]))
        b = d["b2"][(2019, "b", "2")]
        self.assertEqual((b["G"], b["C"]), ([100.0, 15.0], [130.0, 5.0]))
        self.assertEqual(b["M"], {"plastic": [80.0, 14.0], "copper": [50.0, 5.0]})
        c = d["b2"][(2005, "c", "3")]
        self.assertEqual((c["G"], c["C"], c["M"], c["pvc"]),
                         ([None, None], [10.0, None], {"plastic": [10.0, 2.0]}, [None, None]))
        self.assertEqual(d["b2"][(2020, "e", "5")]["G"], [None, 3.0])
        self.assertEqual(d["i2"], {"b2_rows_all_materials_by_size": 1,
                                   "b2_null_size_rows_with_value_2017_2025": 1,
                                   "b2_null_size_rows_with_value_pre_2010": 1,
                                   "b2_plastic_total_rows_pre_2010": 1,
                                   "b2_rows_material_total": 1, "b2_rows_no_year": 1})

    def test_b2_slices(self):
        rows = b2_rows()
        whole, wi = phb23.agg_b2(rows)
        out, info = {}, None
        out, info = phb23.agg_b2(rows[:7], out, info)
        out, info = phb23.agg_b2(rows[7:], out, info)
        self.assertEqual(out, whole)
        self.assertEqual(info, wi)

    def test_b4(self):
        d = build()
        self.assertEqual(d["b4"][(2018, "a", "1")], {"s": [200.0, 80.0]})
        self.assertEqual(d["b4"][(2020, "e", "5")], {"s": [None, None]})
        self.assertEqual(d["i4"], {"b4_total_rows": 1, "b4_rows_no_year": 1})


class CompareTests(unittest.TestCase):
    def test_years(self):
        y = build()["years"]
        self.assertEqual(sorted(y), [2005, 2018, 2019, 2020])
        self.assertEqual((y[2005]["b1"], y[2005]["b2"], y[2005]["b4"]), (0, 1, 0))
        self.assertEqual((y[2020]["b1"], y[2020]["b2"], y[2020]["b4"]), (2, 1, 2))
        a = y[2018]
        self.assertEqual([a["mains_" + p] for p in phb23.PARTS],
                         [1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0])
        self.assertEqual([a["services_" + p] for p in phb23.PARTS],
                         [1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0])
        b = y[2019]
        self.assertEqual([b["mains_" + p] for p in phb23.PARTS],
                         [1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1])
        self.assertEqual([b["services_" + p] for p in phb23.PARTS],
                         [1, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1])
        e = y[2020]
        self.assertEqual(sum(e["mains_" + p] for p in phb23.PARTS), 0)
        self.assertEqual((e["services_g1_comparable"], e["services_g1_pass"],
                          e["services_cg_comparable"], e["services_cg_pass"],
                          e["services_g4_comparable"]), (1, 1, 1, 1, 0))

    def test_groups(self):
        rows = phb23.group_rows(build()["grp"])
        self.assertEqual(len(rows), 8)
        self.assertEqual(rows[0], ["2017_2025", "cast_iron", "mains", 1, 1])
        self.assertIn(["2017_2025", "plastic", "mains", 2, 1], rows)
        self.assertIn(["2017_2025", "plastic", "services", 2, 1], rows)
        self.assertEqual(rows[-2], ["2017_2025", "steel", "mains", 1, 1])

    def test_records(self):
        recs = build()["recs"]
        self.assertEqual([r["key"][1] for r in recs], ["c", "a", "b", "e"])
        self.assertEqual(recs[1]["mains"]["pl"], (100.0, 20.0, 80.0, 100.0, True, False))
        self.assertEqual(recs[2]["services"]["pl"], (10.0, 10.0, 4.0, 14.0, False, True))
        self.assertEqual((recs[0]["mains"]["c"], recs[0]["mains"]["g"]), (10.0, None))
        self.assertIsNone(recs[3]["mains"]["g4"])

    def test_fail_rows(self):
        rows, n = phb23.fail_rows(build()["recs"])
        self.assertEqual(n, 2)
        self.assertEqual(rows[0], [2019, "b", "2", "mains", 100.0, 130.0, 100.0, 110.0, 0, 1, 0])
        self.assertEqual(rows[1], [2019, "b", "2", "services", 15.0, 5.0, 15.0, 15.0, 1, 1, 0])
        rows, n = phb23.fail_rows(build()["recs"], cap=1)
        self.assertEqual((len(rows), n), (1, 2))

    def test_plastic_rows(self):
        rows, n = phb23.plastic_rows(build()["recs"])
        self.assertEqual(n, 4)
        self.assertEqual(rows[0], [2018, "a", "1", "mains", 100.0, 20.0, 80.0, 100.0, 1, 0])
        self.assertEqual(rows[1], [2018, "a", "1", "services", 50.0, 0.0, 50.0, 50.0, 1, 0])
        self.assertEqual(rows[2], [2019, "b", "2", "mains", 50.0, 50.0, 30.0, 80.0, 0, 1])
        self.assertEqual(phb23.plastic_rows(build()["recs"], cap=1)[0][0][3], "mains")

    def test_by_year_rows(self):
        header, rows = phb23.by_year_rows(build()["years"])
        self.assertEqual(len(header), 32)
        self.assertEqual(header[:5], ["year", "b1", "b2", "b4", "mains_g4_comparable"])
        self.assertEqual([r[0] for r in rows], [2005, 2018, 2019, 2020])
        self.assertEqual(rows[0], [2005, 0, 1, 0] + [0] * 28)


class ScoreTests(unittest.TestCase):
    def test_score_default(self):
        d = build()
        m, s = phb23.score(d["years"], d["grp"])
        self.assertEqual((m["late_mains_g4_pass_share"], m["late_mains_g1_pass_share"],
                          m["late_mains_cg_pass_share"], m["late_mains_c4_pass_share"],
                          m["late_services_g4_pass_share"], m["late_services_g1_pass_share"],
                          m["late_services_cg_pass_share"]),
                         (0.5, 1.0, 0.5, 0.5, 1.0, 1.0, 0.666667))
        self.assertEqual((m["late_mains_plastic_discriminating"],
                          m["late_mains_plastic_group_pass_share"],
                          m["late_mains_plastic_pvc_pass_share"],
                          m["late_services_plastic_discriminating"],
                          m["late_steel_mains_comparable"], m["late_steel_mains_pass_share"],
                          m["late_mains_g4_fails_with_b1"],
                          m["late_mains_g4_fails_g1_pass_share"]),
                         (2, 0.5, 0.5, 2, 1, 1.0, 1, None))
        self.assertEqual(s, {"P1": False, "P2": True, "P3": False, "P4": True, "P5": False,
                             "P6": False, "P7": True, "P8": False})

    def test_score_small_bars(self):
        d = build()
        m, s = phb23.score(d["years"], d["grp"], p5_min_n=1, p8_min_fails=1)
        self.assertEqual(m["late_mains_g4_fails_g1_pass_share"], 1.0)
        self.assertEqual((s["P5"], s["P6"], s["P8"]), (False, False, True))

    def test_nothing_to_test(self):
        m, s = phb23.score({}, {})
        self.assertIsNone(m["late_mains_g4_pass_share"])
        self.assertEqual(set(s.values()), {False})

    def test_gates(self):
        years = build()["years"]
        ok = [{"bytes": 10, "missing_cols": []}] * 3
        g, gm = phb23.gates(ok, years)
        self.assertEqual(g, {"G1": True, "G2": False})
        self.assertEqual(gm["late_mains_g4_comparable"], 2)
        self.assertEqual(gm["mains_g4_comparable_by_late_year"]["2019"], 1)
        self.assertEqual(len(gm["mains_g4_comparable_by_late_year"]), 9)
        self.assertEqual(gm["late_years_with_enough"], 0)
        g, _ = phb23.gates(ok[:2] + [{"bytes": 5, "missing_cols": ["main_size"]}], years)
        self.assertFalse(g["G1"])


@unittest.skipIf(pl is None, "polars not installed")
class PolarsReadTests(unittest.TestCase):
    def test_read_slices_matches_tuples(self):
        rows = [r for r in b2_rows() if r[1] == "a"]
        f = (lambda v: None if v is None else float(v))
        data = {"report_date": [datetime.date(r[0], 1, 1) for r in rows],
                "report_id": [r[1] for r in rows],
                "operator_id_phmsa": [r[2] for r in rows],
                "material": [r[3] for r in rows], "main_size": [r[4] for r in rows],
                "mains_miles": [f(r[5]) for r in rows], "services": [f(r[6]) for r in rows]}
        schema = {"report_date": pl.Date, "report_id": pl.String, "operator_id_phmsa": pl.Int64,
                  "material": pl.String, "main_size": pl.String, "mains_miles": pl.Float64,
                  "services": pl.Float64}
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "b2.parquet")
            pl.DataFrame(data, schema=schema).write_parquet(path)
            out, info = {}, phb23.Counter()
            meta = phb23.read_slices(pl, path, phb23.B2_NEED,
                                     lambda it: phb23.agg_b2(it, out, info), slice_rows=4)
        self.assertEqual((meta["rows"], meta["slices"], meta["years"]), (11, 3, [2018, 2018]))
        self.assertEqual(meta["missing_cols"], [])
        whole, wi = phb23.agg_b2(rows)
        self.assertEqual(out, whole)
        self.assertEqual(info, wi)


if __name__ == "__main__":
    unittest.main()
