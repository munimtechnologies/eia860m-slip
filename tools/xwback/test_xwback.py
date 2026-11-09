"""Unit tests for xwback.py on made-up rows. Reads no outside data.

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import xwback as xb  # noqa: E402

POP_CSV = ("report_year,plant_id_epa,emissions_unit_id_epa,plant_id_eia,xwgap_reason,class,cause,"
           "last_listed_year,listed_later,combustion_generators,undated,retiring_after_year,"
           "latest_retirement_year\n"
           "2024,887,1,887,absent,retired_before,,2022,True,6,0,0,2022\n"
           "2024,887,2,887,absent,retired_before,,2022,True,6,0,0,2022\n"
           "2024,59073,214JA,59073,absent,other,undated,2020,False,9,9,0,\n"
           "2023,887,1,887,absent,retired_before,,2022,True,6,0,0,2022\n"
           "2024,55243,CT2-1A,55243,absent,other,undated,2023,True,21,1,0,\n")


def t(plant, gen, year, status, ret=None, maturity="final", pm="GT"):
    return (plant, gen, "%d-01-01" % year, status, ret, maturity, pm)


def fixture():
    rows = []
    # Plant 1: operating 2018-2020, all retired 2021 (listed 2021-2022), gone 2023-2025, back 2026.
    for y in (2018, 2019, 2020):
        rows += [t(1, "A", y, "OP"), t(1, "B", y, "OP")]
    for y in (2021, 2022):
        rows += [t(1, "A", y, "RE", "2021-05-01"), t(1, "B", y, "RE", "2021-06-01")]
    rows += [t(1, "A", 2026, "RE", "2021-05-01", "monthly_update"),
             t(1, "B", 2026, "RE", "2021-06-01", "monthly_update")]
    # Plant 2: retired 2005, still listed every annual year to 2024 (persists), and in 2025.
    for y in range(2005, 2026):
        rows.append(t(2, "1", y, "RE", "2005-01-01", "final" if y < 2025 else "final"))
    # Plant 3: fully retired 2010 but a non-RE row in 2012 (reused id): not in population C.
    rows += [t(3, "X", 2010, "RE", "2010-01-01"), t(3, "Y", 2012, "OP")]
    # Plant 4: fully retired 2023: outside C (first year after C_LAST).
    rows += [t(4, "Z", 2023, "RE", "2023-02-01")]
    # Plant 5: still operating: never fully retired.
    rows += [t(5, "Q", 2024, "OP"), t(5, "Q", 2026, "OP", None, "monthly_update")]
    # Bad rows are skipped.
    rows += [(None, "A", "2020-01-01", "OP", None, "final", "GT"), (6, "", "2020-01-01", "OP",
             None, "final", "GT"), (6, "A", None, "OP", None, "final", "GT")]
    return rows


class HelperTests(unittest.TestCase):
    def test_helpers(self):
        self.assertEqual(xb.gid(1.0), "1")
        self.assertEqual(xb.gid(float("nan")), "")
        self.assertEqual(xb.gid(" re "), "RE")
        self.assertEqual(xb.pint("55243"), 55243)
        self.assertIsNone(xb.pint(None))
        self.assertEqual(xb.iso("2026-08-01 00:00:00"), "2026-08-01")
        self.assertIsNone(xb.iso(""))
        self.assertEqual(xb.mat(" Monthly_Update "), "monthly_update")
        self.assertEqual(xb.mat(None), "")

    def test_read_population(self):
        units, plants = xb.read_population(POP_CSV)
        self.assertEqual(units, [(887, "1"), (887, "2"), (55243, "CT2-1A")])
        self.assertEqual(plants, [887, 55243])


class AggregateTests(unittest.TestCase):
    def setUp(self):
        self.plants, self.detail, self.maturity = xb.aggregate(fixture(), {1, 99})

    def test_aggregate(self):
        self.assertEqual(sorted(self.plants), [1, 2, 3, 4, 5])
        self.assertEqual(sorted(self.plants[1]), [2018, 2019, 2020, 2021, 2022, 2026])
        self.assertEqual(self.plants[1][2021], {"gens": {"A", "B"}, "re": {"A", "B"}})
        self.assertEqual(self.plants[1][2020]["re"], set())
        self.assertEqual(len(self.detail[1]), 12)
        self.assertEqual(self.detail[99], [])
        self.assertEqual(self.maturity[(2026, "monthly_update")], 3)
        self.assertEqual(self.maturity[(2024, "final")], 2)

    def test_population_c(self):
        cs = xb.population_c(self.plants)
        self.assertEqual([(c["plant"], c["first_retired_year"], c["last_annual"], c["persist"],
                           c["in_2025"], c["in_2026"]) for c in cs],
                         [(1, 2021, 2022, False, False, True), (2, 2005, 2024, True, True, False)])
        s = xb.summarize_c(cs)
        self.assertEqual((s["n"], s["persist"], s["in_2025"], s["in_2026"]), (2, 1, 1, 1))
        self.assertEqual(s["by_first_year"]["2021"], {"n": 1, "persist": 0, "in_2025": 0,
                                                      "in_2026": 1})

    def test_population_a(self):
        (a,) = xb.population_a([1], [(1, "u1"), (1, "u2")], self.plants, self.detail)
        self.assertEqual((a["units_2024"], a["last_annual"], a["rows_2025"], a["rows_2026"],
                          a["later_rows"], a["later_re"], a["p1_ok"]),
                         (2, 2022, 0, 2, 2, 2, True))
        self.assertEqual(a["maturity_2026"], {"monthly_update": 2})
        (b,) = xb.population_a([5], [(5, "u")], self.plants, {5: []})
        self.assertFalse(b["p1_ok"])


class AstoriaTests(unittest.TestCase):
    def test_undated(self):
        rows = [{"gen": "G1", "year": 2023, "status": "RE", "ret": "2023-05-01",
                 "maturity": "final", "pm": "GT"},
                {"gen": "G2", "year": 2022, "status": "OP", "ret": None, "maturity": "final",
                 "pm": "GT"},
                {"gen": "G2", "year": 2023, "status": "OS", "ret": None, "maturity": "final",
                 "pm": "GT"},
                {"gen": "G2", "year": 2026, "status": "RE", "ret": "2023-05-01",
                 "maturity": "monthly_update", "pm": "GT"},
                {"gen": "G3", "year": 2023, "status": "OP", "ret": None, "maturity": "final",
                 "pm": "PV"}]
        got = xb.astoria_undated(rows)
        self.assertEqual(sorted(got), ["G2"])
        self.assertEqual([(r["year"], r["status"], r["ret"]) for r in got["G2"]],
                         [(2022, "OP", None), (2023, "OS", None), (2026, "RE", "2023-05-01")])


def good_res():
    a = [{"years": [2022, 2026], "p1_ok": True, "later_rows": 10, "later_re": 10}
         for _ in range(14)]
    return {"g1": {"missing_cols": [], "years": list(range(2001, 2027))},
            "g2": {"plants": 14, "units": 57}, "pop_a": a,
            "pop_c_summary": {"n": 100, "persist": 10, "in_2025": 3, "in_2026": 80}}


class ScoreTests(unittest.TestCase):
    def test_all_hold_at_bars(self):
        r = good_res()
        r["pop_c_summary"]["in_2025"] = 10
        self.assertEqual(xb.score(r), {"G1": True, "G2": True, "G3": True, "P1": True,
                                       "P2": True, "P3": True, "P4": True, "P5": True})

    def test_bars(self):
        r = good_res()
        r["pop_a"][0]["p1_ok"] = r["pop_a"][1]["p1_ok"] = False
        r["pop_a"][0]["later_re"] = 2  # 132/140 = 94.3%
        r["pop_c_summary"].update(persist=11, in_2026=79, in_2025=11)
        s = xb.score(r)
        self.assertEqual((s["P1"], s["P2"], s["P3"], s["P4"], s["P5"]),
                         (False, False, False, False, False))
        r = good_res()
        r["pop_a"][0]["p1_ok"] = False  # 13 of 14 still holds
        self.assertTrue(xb.score(r)["P1"])

    def test_gates(self):
        r = good_res()
        r["g1"]["years"] = list(range(2001, 2026))
        self.assertEqual(xb.score(r), {"G1": False})
        r = good_res()
        r["g2"]["units"] = 56
        self.assertEqual(xb.score(r), {"G1": True, "G2": False})
        r = good_res()
        r["pop_a"][3]["years"] = [2022, 2023]
        self.assertEqual(xb.score(r), {"G1": True, "G2": True, "G3": False})
        self.assertEqual(xb.score({}), {})


class ConstantTests(unittest.TestCase):
    def test_constants(self):
        self.assertEqual(xb.VERSION, "0.1.0")
        self.assertEqual(xb.G1_YEARS, tuple(range(2018, 2027)))
        self.assertEqual((xb.POP_PLANTS, xb.POP_UNITS, xb.P1_MIN_PLANTS), (14, 57, 13))
        self.assertEqual((xb.P2_SHARE, xb.P3_MAX_SHARE, xb.P4_SHARE, xb.P5_MAX_SHARE),
                         (0.95, 0.10, 0.80, 0.10))
        self.assertEqual((xb.C_FIRST, xb.C_LAST, xb.P3_GAP), (2002, 2021, 3))


if __name__ == "__main__":
    unittest.main()
