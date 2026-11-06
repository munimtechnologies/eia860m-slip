"""Unit tests for xwpair.py (stdlib only; polars is needed only by main()).

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.).
"""

import datetime
import unittest

import xwpair as c


def ops(year, pe, ue, pi, peak):
    return {"report_year": year, "plant_id_epa": pe, "emissions_unit_id_epa": ue,
            "plant_id_eia": pi, "max_gross_load_mw": peak}


def xw(year, pe, ue, pi, gi):
    return {"report_year": year, "plant_id_epa": pe, "emissions_unit_id_epa": ue,
            "plant_id_eia": pi, "generator_id": gi}


def gen(pi, gi, cap, pm, status, date="2024-01-01"):
    return {"plant_id_eia": pi, "generator_id": gi, "report_date": date, "capacity_mw": cap,
            "prime_mover_code": pm, "operational_status_code": status}


OPS = [
    ops(2024, 10, "01", 10, 100.0),
    ops(2024, 10, "1", 10, 105.0),      # same unit as "01": the larger peak wins
    ops(2024, 10, "2", 10, 45.0),
    ops(2024, 20, "A", None, 80.0),     # no EIA plant: plant_id_epa is used
    ops(2024, 30, "CT1", 30, 60.0),
    ops(2024, 30, "CT2", 30, 60.0),
    ops(2024, 40, "B", 40, None),       # no load
    ops(2024, 50, "L", 50, 70.0),       # linked
    ops(2024, 60, "X", 60, 90.0),       # no combustion candidate at the plant
    ops(2023, 10, "1", 10, 99.0),
]

XW = [
    xw(2024, 50, "L", 50, "G1"),
    xw(2024, 10, "9", 10, "LINKED"),
    xw(2024, 10, "2", 10, None),        # names no EIA generator: unit 10/2 stays unmatched
    xw(2023, 10, "1", 10, "GA"),
]

GENS = [
    gen(10, "GA", 100.0, "CT", "OP"),
    gen(10, "GB", 45.0, "CA", "OP"),
    gen(10, "LINKED", 100.0, "CT", "OP"),
    gen(10, "RET", 100.0, "CT", "RE"),
    gen(20, "G", 200.0, "CT", "OP"),
    gen(30, "CT1", 60.0, "CT", "OP"),
    gen(30, "CT2", 60.0, "CT", "OP"),
    gen(40, "S", 10.0, "ST", "OP"),
    gen(50, "G1", 70.0, "CT", "OP"),
    gen(60, "PV", 90.0, "PV", "OP"),
    gen(10, "GA", 100.0, "CT", "OP", datetime.date(2023, 1, 1)),
]

OGE_TEXT = ("plant_id_epa,emissions_unit_id_epa,plant_id_eia,generator_id,start_year,end_year,"
            "notes\r\n"
            "10,001,10,GA,,,CAMPD Facility database mapping\r\n"
            "30,CT1,30,CT1,,,CAMPD Facility database mapping\r\n"
            "30,CT2,30,CT2,,,CAMPD Facility database mapping\r\n"
            "50,L,50,G1,,,CAMPD Facility database mapping\r\n"
            "10,2,10,ZZ,,,CAMPD Facility database mapping\r\n"
            "99,Q,99,Q,,,CAMPD Facility database mapping\r\n"
            "1,1,1,1,,,some other note\r\n")


class IdTests(unittest.TestCase):
    def test_gid_uid(self):
        self.assertEqual(c.gid(1.0), "1")
        self.assertEqual(c.gid(" st1 "), "ST1")
        self.assertEqual(c.gid(None), "")
        self.assertEqual(c.uid("001"), "1")
        self.assertEqual(c.uid("0"), "0")
        self.assertEqual(c.uid("00"), "0")
        self.assertEqual(c.uid(" ct0009 "), "CT0009")
        self.assertEqual(c.uid(None), "")
        self.assertEqual(c.uid(1.0), "1")

    def test_size_ok(self):
        self.assertTrue(c.size_ok(105.0, 100.0))
        self.assertFalse(c.size_ok(40.0, 100.0))
        self.assertFalse(c.size_ok(160.0, 100.0))
        self.assertFalse(c.size_ok(None, 100.0))
        self.assertFalse(c.size_ok(50.0, 0.0))


class IndexTests(unittest.TestCase):
    def test_ops(self):
        o = c.index_ops(OPS)
        self.assertEqual(sorted(o), [2023, 2024])
        self.assertEqual(o[2024][(10, "1")], {"pi": 10, "peak": 105.0})
        self.assertEqual(o[2024][(20, "A")], {"pi": 20, "peak": 80.0})
        self.assertIsNone(o[2024][(40, "B")]["peak"])
        self.assertEqual(len(o[2024]), 8)

    def test_xw(self):
        x = c.index_xw(XW)
        self.assertEqual(x[2024]["units"], {(50, "L"), (10, "9")})
        self.assertEqual(x[2024]["linked"], {(50, "G1"), (10, "LINKED")})


class CensusTests(unittest.TestCase):
    def setUp(self):
        self.o = c.index_ops(OPS)
        self.x = c.index_xw(XW)
        self.g = c.index_gens(GENS)
        self.r = c.year_pairs(self.o[2024], self.x[2024], self.g[2024])
        self.by = {(u["plant_id_epa"], u["unit"]): u for u in self.r["units"]}

    def test_counts(self):
        self.assertEqual(self.r["counts"], {
            "cems_units": 8, "unmatched": 7, "with_candidate": 6, "no_load": 1,
            "no_candidate": 1, "no_size_match": 1, "ambiguous": 2, "unique_pair": 2})

    def test_classes(self):
        self.assertEqual(self.by[(10, "1")]["class"], "unique_pair")
        self.assertEqual(self.by[(10, "1")]["pair"], "GA")
        self.assertEqual(self.by[(10, "2")]["pair"], "GB")
        self.assertEqual(self.by[(20, "A")]["class"], "no_size_match")
        self.assertEqual(self.by[(30, "CT1")]["class"], "ambiguous")
        self.assertEqual(self.by[(30, "CT1")]["size_matches"], ["CT1", "CT2"])
        self.assertEqual(self.by[(30, "CT1")]["same_id_matches"], ["CT1"])
        self.assertEqual(self.by[(40, "B")]["class"], "no_load")
        self.assertEqual(self.by[(60, "X")]["class"], "no_candidate")
        self.assertNotIn((50, "L"), self.by)

    def test_candidates_exclude_linked_retired(self):
        ids = [x["generator"] for x in self.by[(10, "1")]["candidates"]]
        self.assertEqual(ids, ["GA", "GB"])

    def test_oge(self):
        n, oge = c.parse_oge(OGE_TEXT)
        self.assertEqual(n, 6)
        self.assertEqual(oge[(10, "1")], {(10, "GA")})
        self.assertNotIn((1, "1"), oge)
        v = c.validate(self.r, self.o[2024], oge)
        self.assertEqual((v["oge_units"], v["present"], v["unmatched"], v["contained"],
                          v["pairs_in_oge"], v["pairs_agree"], v["new_pairs"]),
                         (6, 5, 4, 3, 2, 1, 0))
        self.assertEqual(v["present_matched"], [[50, "L"]])
        self.assertEqual(v["not_contained"], [[10, "2"]])
        self.assertEqual(v["pairs_disagree"], [[10, "2"]])


class ScoreTests(unittest.TestCase):
    def res(self, unmatched=200, present=40, pairs_in=10, oge_rows=171):
        return {"g1": {"missing_cols": [], "newest": 2024, "cems_units": 4000},
                "by_year": {"2024": {"counts": {"cems_units": 4000, "unmatched": unmatched,
                                                "with_candidate": 120, "unique_pair": 30}}},
                "oge_rows": oge_rows,
                "oge": {"present": present, "unmatched": 36, "contained": 30,
                        "pairs_in_oge": pairs_in, "pairs_agree": 9, "new_pairs": 12}}

    def test_all_held(self):
        self.assertEqual(c.score(self.res()), {"G1": True, "P1": True, "P2": True, "P3": True,
                                               "G2": True, "P4": True, "P5": True, "P6": True,
                                               "P7": True})

    def test_gate1_fails(self):
        r = self.res()
        r["g1"]["cems_units"] = 1999
        self.assertEqual(c.score(r), {"G1": False})
        r = self.res()
        r["g1"]["missing_cols"] = ["max_gross_load_mw"]
        self.assertEqual(c.score(r), {"G1": False})

    def test_gate2_fails(self):
        s = c.score(self.res(oge_rows=0))
        self.assertFalse(s["G2"])
        self.assertNotIn("P4", s)
        self.assertNotIn("P7", s)

    def test_failed_and_unscored(self):
        s = c.score(self.res(unmatched=40, present=19, pairs_in=4))
        self.assertFalse(s["P1"])
        self.assertTrue(s["P2"])
        self.assertNotIn("P4", s)
        self.assertNotIn("P6", s)
        self.assertTrue(s["P5"])


if __name__ == "__main__":
    unittest.main()
