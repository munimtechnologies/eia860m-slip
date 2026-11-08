"""Unit tests for xwgap.py on made-up rows (no downloads).

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import unittest

import xwgap as x


def orow(y, pe, ue, pi, peak):
    return {"report_year": y, "plant_id_epa": pe, "emissions_unit_id_epa": ue,
            "plant_id_eia": pi, "max_gross_load_mw": peak}


def xrow(y, pe, ue, pi, gi):
    return {"report_year": y, "plant_id_epa": pe, "emissions_unit_id_epa": ue,
            "plant_id_eia": pi, "generator_id": gi}


def grow(pi, gi, cap, pm, status="OP", date="2024-01-01"):
    return {"plant_id_eia": pi, "generator_id": gi, "report_date": date, "capacity_mw": cap,
            "prime_mover_code": pm, "operational_status_code": status}


def world():
    """One year, 2024. Plant 1: unit A linked to G1; unit B (peak 100) unmatched, the only
    operating generator G1 (95 MW) is linked -> all_linked with a fit. Plant 2: unit 01 unmatched,
    no EIA rows -> absent; EPA plant 2 also links unit Z to EIA plant 20. Plant 3: unit CT3
    unmatched, generators retired -> not_operating, same-id CT3. Plant 4: unit U unmatched with an
    unlinked operating CT -> has a candidate, skipped. Plant 5: unit N no peak -> skipped."""
    ops = x.index_ops([orow(2024, 1, "A", 1, 90.0), orow(2024, 1, "B", 1, 100.0),
                       orow(2024, 2, "01", None, 50.0), orow(2024, 2, "Z", 20, 10.0),
                       orow(2024, 3, "CT3", 3, 40.0), orow(2024, 4, "U", 4, 80.0),
                       orow(2024, 5, "N", 5, None)])
    xw = x.index_xw([xrow(2024, 1, "A", 1, "G1"), xrow(2024, 2, "Z", 20, "Z1")])
    gens = x.index_gens([grow(1, "G1", 95.0, "CT"), grow(1, "PV1", 5.0, "PV"),
                         grow(3, "CT3", 45.0, "GT", "RE"), grow(4, "CT1", 80.0, "CT"),
                         grow(5, "N1", 10.0, "GT")])
    return ops, xw, gens


class IdTests(unittest.TestCase):
    def test_ids(self):
        self.assertEqual(x.gid(" ct1 "), "CT1")
        self.assertEqual(x.gid(3.0), "3")
        self.assertEqual(x.gid(float("nan")), "")
        self.assertEqual(x.uid("01"), "1")
        self.assertEqual(x.uid("000"), "0")
        self.assertEqual(x.uid(None), "")
        self.assertEqual(x.pint("2.0"), 2)
        self.assertIsNone(x.pint("x"))
        self.assertIsNone(x.fnum(float("nan")))

    def test_size_ok(self):
        self.assertTrue(x.size_ok(100.0, 95.0))
        self.assertTrue(x.size_ok(50.0, 100.0))
        self.assertFalse(x.size_ok(151.0, 100.0))
        self.assertFalse(x.size_ok(None, 100.0))
        self.assertFalse(x.size_ok(10.0, 0.0))


class IndexTests(unittest.TestCase):
    def test_index_ops(self):
        ops = x.index_ops([orow(2024, 2, "01", None, 50.0), orow(2024, 2, "1", 22, 60.0)])
        self.assertEqual(ops[2024][(2, "1")], {"pi": 22, "peak": 60.0})

    def test_index_xw(self):
        xw = x.index_xw([xrow(2024, 1, "A", 1, "g1"), xrow(2024, 1, "B", 1, None),
                         xrow(2024, 1, "C", 9, "X")])[2024]
        self.assertEqual(xw["units"], {(1, "A"), (1, "C")})
        self.assertEqual(xw["linked"], {(1, "G1"), (9, "X")})
        self.assertEqual(xw["gen_units"][(1, "G1")], {(1, "A")})
        self.assertEqual(xw["epa_to_eia"][1], {1, 9})

    def test_index_gens_first_capacity_wins(self):
        g = x.index_gens([grow(1, "G1", None, "CT"), grow(1, "G1", 95.0, "CT"),
                          grow(1, "G1", 80.0, "CT")])
        self.assertEqual(g[2024][(1, "G1")]["cap"], 95.0)


class GapTests(unittest.TestCase):
    def setUp(self):
        ops, xw, gens = world()
        self.units = x.year_gaps(ops[2024], xw[2024], gens[2024], {(2, "1")}, {(1, "B")})
        self.by = {(u["plant_id_epa"], u["unit"]): u for u in self.units}

    def test_which_units(self):
        self.assertEqual(sorted(self.by), [(1, "B"), (2, "1"), (3, "CT3")])

    def test_reasons_and_leads(self):
        b, a, r = self.by[(1, "B")], self.by[(2, "1")], self.by[(3, "CT3")]
        self.assertEqual((b["reason"], b["linked_fits"], b["linked_fit_units"]),
                         ("all_linked", ["G1"], ["1/A"]))
        self.assertEqual((b["generators"], b["statuses"], b["unmatched_prev"]),
                         (2, ["OP"], True))
        self.assertEqual((a["reason"], a["generators"], a["other_eia_plants"], a["in_oge"]),
                         ("absent", 0, [20], True))
        self.assertEqual((r["reason"], r["same_id"], r["statuses"], r["unmatched_prev"]),
                         ("not_operating", ["CT3"], ["RE"], False))

    def test_summary(self):
        c = x.summarize(self.units)
        self.assertEqual(c, {"n": 3, "absent": 1, "not_operating": 1, "all_linked": 1,
                             "all_linked_with_fit": 1, "same_id": 1, "other_eia_plant": 1,
                             "in_oge": 1, "with_prev_year": 3, "unmatched_prev": 1,
                             "plants": 3})

    def test_no_previous_year(self):
        ops, xw, gens = world()
        units = x.year_gaps(ops[2024], xw[2024], gens[2024], set(), None)
        self.assertTrue(all(u["unmatched_prev"] is None for u in units))
        self.assertEqual(x.summarize(units)["with_prev_year"], 0)


class OgeTests(unittest.TestCase):
    def test_parse_oge(self):
        text = ("plant_id_epa,emissions_unit_id_epa,plant_id_eia,generator_id,start_year,"
                "end_year,notes\n60345,OCEC1A,60345,1A,,,x\n6061,03,6061,MOR1,,,\n,,1,G,,,\n")
        n, units = x.parse_oge(text)
        self.assertEqual(n, 2)
        self.assertEqual(units, {(60345, "OCEC1A"), (6061, "3")})


class ScoreTests(unittest.TestCase):
    def res(self, **c):
        base = {"n": 50, "absent": 10, "not_operating": 10, "all_linked": 30,
                "all_linked_with_fit": 15, "same_id": 10, "other_eia_plant": 0, "in_oge": 13,
                "with_prev_year": 50, "unmatched_prev": 35, "plants": 30}
        base.update(c)
        return {"g1": {"missing_cols": [], "newest": 2024, "cems_units": 4000},
                "summary": {"2024": base}, "oge_rows": 400}

    def test_all_hold(self):
        self.assertEqual(x.score(self.res()), {"G1": True, "G2": True, "P1": True, "P2": True,
                                               "P3": True, "P4": True, "G3": True, "P5": True,
                                               "P6": True})

    def test_bars(self):
        s = x.score(self.res(absent=9, not_operating=30, all_linked=11, all_linked_with_fit=5,
                             same_id=9, in_oge=12, unmatched_prev=34))
        self.assertEqual((s["P1"], s["P2"], s["P3"], s["P4"], s["P5"], s["P6"]),
                         (False, False, False, False, False, False))

    def test_unscored(self):
        s = x.score(self.res(all_linked=9, absent=21, not_operating=20, with_prev_year=0))
        self.assertNotIn("P3", s)
        self.assertNotIn("P6", s)
        r = self.res()
        r["oge_rows"] = 10
        s = x.score(r)
        self.assertFalse(s["G3"])
        self.assertNotIn("P5", s)

    def test_gates(self):
        self.assertEqual(x.score(self.res(n=39)), {"G1": True, "G2": False})
        r = self.res()
        r["g1"]["newest"] = 2022
        self.assertEqual(x.score(r), {"G1": False})
        self.assertEqual(x.score({}), {})


class ConstantTests(unittest.TestCase):
    def test_constants(self):
        self.assertEqual((x.LO, x.HI, x.MIN_GAP, x.P2_SHARE, x.P3_MIN_N, x.P3_SHARE, x.P4_MIN,
                          x.P5_SHARE, x.P6_SHARE), (0.5, 1.5, 40, 0.2, 10, 0.5, 10, 0.25, 0.7))
        self.assertEqual(x.REASONS, ("absent", "not_operating", "all_linked"))


if __name__ == "__main__":
    unittest.main()
