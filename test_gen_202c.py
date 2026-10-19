"""Tests for gen_202c (standard library only). MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import datetime as dt
import unittest

import gen_202c as g
import orders_202c


def order(key, start, end):
    return {"kind": "plant", "plant_key": key, "effective": dt.date.fromisoformat(start),
            "expires": dt.date.fromisoformat(end)}


ORDERS = [order("a", "2026-01-15", "2026-02-10"), order("a", "2026-02-11", "2026-05-11")]
UNITS = {"a": {"plant": "Plant A", "plant_id": "1", "gens": ["1", "2"], "mw": 10.0},
         "b": {"plant": "Plant B", "plant_id": "2", "gens": ["1"], "mw": 5.0}}


def fixture_values():
    v = {}
    for y in (2021, 2022, 2023, 2024):
        v[("1", "1", "%d-01" % y)] = 200.0
        v[("1", "2", "%d-01" % y)] = 0.0
        v[("1", "1", "%d-02" % y)] = 100.0
        if y != 2021:
            v[("1", "2", "%d-02" % y)] = 50.0
    v[("1", "1", "2024-03")] = 70.0
    v[("1", "2", "2024-03")] = 1.0
    v.update({("1", "1", "2026-01"): 10.0, ("1", "2", "2026-01"): 0.0,
              ("1", "1", "2026-02"): 30.0, ("1", "2", "2026-02"): -5.0,
              ("1", "1", "2026-03"): 0.0, ("1", "2", "2026-03"): 0.0,
              ("1", "1", "2026-04"): 40.0})
    return v


class Months(unittest.TestCase):
    def test_range_and_days(self):
        self.assertEqual(g.month_range("2025-11", "2026-02"),
                         ["2025-11", "2025-12", "2026-01", "2026-02"])
        self.assertEqual(g.month_days("2024-02"), 29)
        self.assertEqual(g.month_days("2026-02"), 28)

    def test_order_days(self):
        self.assertEqual(g.order_days(ORDERS, "a", "2025-12"), 0)
        self.assertEqual(g.order_days(ORDERS, "a", "2026-01"), 17)
        self.assertEqual(g.order_days(ORDERS, "a", "2026-02"), 28)
        self.assertEqual(g.order_days(ORDERS, "a", "2026-04"), 30)
        self.assertEqual(g.order_days(ORDERS, "a", "2026-05"), 11)


class Values(unittest.TestCase):
    def test_plant_month_and_baseline(self):
        v, u = fixture_values(), UNITS["a"]
        self.assertEqual(g.plant_month(v, u, "2026-02"), 25.0)
        self.assertIsNone(g.plant_month(v, u, "2026-04"))
        self.assertIsNone(g.plant_month(v, u, "2021-02"))
        self.assertEqual(g.baseline(v, u, "2026-01"), (200.0, 4))
        self.assertEqual(g.baseline(v, u, "2026-02"), (150.0, 3))
        self.assertEqual(g.baseline(v, u, "2026-03"), (None, 1))
        self.assertEqual(g.baseline(v, u, "2026-04"), (None, 0))


class Analyse(unittest.TestCase):
    def setUp(self):
        self.res = g.analyse(fixture_values(), UNITS, ORDERS, "2026-05")

    def test_rows(self):
        rows = self.res["rows"]
        self.assertEqual([r["month"] for r in rows],
                         ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05"])
        self.assertEqual([r["full"] for r in rows], [False, True, True, True, False])
        self.assertEqual([r["included"] for r in rows], [False, True, False, False, False])
        self.assertEqual(rows[0]["baseline_mwh"], 200.0)
        self.assertEqual(rows[2]["mwh"], 0.0)
        self.assertIsNone(rows[1]["y2025_mwh"])

    def test_plant_totals(self):
        self.assertEqual([p["plant_key"] for p in self.res["plants"]], ["a"])
        p = self.res["plants"][0]
        self.assertEqual(p["first_order_day"], "2026-01-15")
        self.assertEqual(p["missing_full_months"], ["2026-04"])
        want = {"months": 1, "mwh": 25.0, "baseline_mwh": 150.0, "ratio": 0.1667,
                "cf": 0.0037, "cf_baseline": 0.0223, "idle_months": 0}
        self.assertEqual(p["all"], want)
        self.assertEqual(p["w26"], want)
        self.assertEqual(self.res["combined_w26"], want)

    def test_render(self):
        cov = g.coverage_of(fixture_values(), UNITS, {})
        sc = g.score(self.res, {}, {k: UNITS["b"] for k in g.UD_PLANTS}, cov)
        md = g.render(self.res, sc, {})
        self.assertIn("# Net generation of the plants under DOE 202(c) orders", md)
        self.assertIn("| a | 2026-02 | 28 | yes | 25 | 150 | 3 |  | yes |", md)


def t(months, ratio):
    return {"months": months, "ratio": ratio}


class Score(unittest.TestCase):
    def build(self, cen):
        plants = [{"plant_key": "campbell", "all": t(16, 0.70), "w26": t(7, 0.6)},
                  {"plant_key": "centralia", "all": t(7, -0.01), "w26": t(7, -0.01)},
                  {"plant_key": "craig", "all": t(7, 0.02), "w26": t(7, 0.02)},
                  {"plant_key": "culley", "all": t(7, 0.64), "w26": t(7, 0.64)},
                  {"plant_key": "schahfer", "all": t(7, 0.3), "w26": t(7, 0.3)},
                  {"plant_key": "eddystone", "all": t(0, None), "w26": t(0, None)},
                  {"plant_key": "wagner", "all": t(9, 0.9), "w26": t(2, 0.9)},
                  {"plant_key": "stanton", "all": t(1, 0.8), "w26": t(1, 0.8)}]
        rows = [{"plant_key": "centralia", "month": m, "mwh": v} for m, v in cen]
        return {"last": "2026-07", "rows": rows, "plants": plants,
                "combined_w26": {"ratio": 0.42}}

    def score(self, cen):
        units = {k: {"plant_id": "9", "gens": ["1"]} for k in g.UD_PLANTS}
        return g.score(self.build(cen), {}, units, {"no_base": []})

    def test_score(self):
        sc = self.score([("2025-12", 5.0), ("2026-01", -100.0), ("2026-02", 0.0),
                         ("2026-03", -50.0), ("2026-04", None)])
        self.assertTrue(sc["C1"]["pass"])
        self.assertEqual(len(sc["C2"]["plants"]), 7)
        self.assertTrue(sc["C2"]["pass"])
        self.assertTrue(sc["G1"]["hit"])
        self.assertEqual(sc["G2"]["months"], {"2026-01": -100.0, "2026-02": 0.0, "2026-03": -50.0})
        self.assertTrue(sc["G2"]["hit"])
        self.assertTrue(sc["G3"]["hit"])
        self.assertEqual(sc["G4"]["below"], ["campbell", "centralia", "craig", "culley", "schahfer"])
        self.assertTrue(sc["G4"]["hit"])
        self.assertFalse(sc["G5"]["hit"])
        self.assertIsNone(sc["X1"]["q1_2026"])

    def test_centralia_runs(self):
        sc = self.score([("2026-01", -100.0), ("2026-02", 12.0), ("2026-03", -50.0)])
        self.assertFalse(sc["G2"]["hit"])
        sc = self.score([("2026-01", -100.0), ("2026-02", 0.0)])
        self.assertFalse(sc["G2"]["hit"])

    def test_quarter(self):
        units = {k: {"plant_id": str(i), "gens": ["1"]} for i, k in enumerate(g.UD_PLANTS)}
        v = {(str(i), "1", "2026-%02d" % mo): 100.0 for i in range(5) for mo in (1, 2, 3)}
        self.assertEqual(g.quarter(v, units, g.UD_PLANTS, 2026), 1500.0)
        del v[("4", "1", "2026-03")]
        self.assertIsNone(g.quarter(v, units, g.UD_PLANTS, 2026))

    def test_coverage(self):
        v = {("1", "1", "2023-05"): 1.0}
        self.assertEqual(g.coverage_of(v, UNITS, {})["no_base"], ["1/2", "2/1"])


class RealTables(unittest.TestCase):
    def test_units(self):
        u = g.load_units()
        self.assertEqual(sorted(u), ["campbell", "centralia", "craig", "culley", "eddystone",
                                     "schahfer", "stanton", "wagner"])
        self.assertEqual(u["campbell"]["gens"], ["1", "2", "3"])
        self.assertEqual(u["campbell"]["plant_id"], "1710")
        self.assertEqual(u["schahfer"]["gens"], ["17", "18"])
        self.assertEqual(u["culley"]["mw"], 90.0)

    def test_real_order_days(self):
        rows = orders_202c.load()
        want = {("campbell", "2025-05"): 9, ("eddystone", "2025-05"): 2, ("craig", "2025-12"): 2,
                ("centralia", "2026-01"): 31, ("schahfer", "2026-03"): 31,
                ("craig", "2026-06"): 30, ("wagner", "2026-04"): 0, ("wagner", "2026-05"): 10,
                ("wagner", "2026-06"): 30, ("stanton", "2026-06"): 27, ("stanton", "2026-07"): 31}
        for (k, m), n in want.items():
            self.assertEqual(g.order_days(rows, k, m), n, (k, m))


if __name__ == "__main__":
    unittest.main()
