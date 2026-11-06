"""Unit tests for ccsplit.py (stdlib only; polars is needed only by main()).

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.).
"""

import datetime
import unittest

import ccsplit as c


def xw(year, pe, ue, ge, pi, gi):
    return {"report_year": year, "plant_id_epa": pe, "emissions_unit_id_epa": ue,
            "generator_id_epa": ge, "plant_id_eia": pi, "generator_id": gi}


def gen(pi, gi, date, cap, pm, status):
    return {"plant_id_eia": pi, "generator_id": gi, "report_date": date, "capacity_mw": cap,
            "prime_mover_code": pm, "operational_status_code": status}


XW = [
    # collapsed combined cycle: both CAMD generators on the EIA CT; the CA is unlinked
    xw(2024, 422, "GT5", "CTG5", 422, "GT5"),
    xw(2024, 422, "GT5", "STG5", 422, "GT5"),
    # normal combined cycle
    xw(2024, 100, "CT1", "CTG1", 100, "CT1"),
    xw(2024, 100, "CT1", "STG1", 100, "ST1"),
    # two CAMD generators on one CT, but the plant has no CA
    xw(2024, 200, "1", "A", 200, "1"),
    xw(2024, 200, "1", "B", 200, "1"),
    # orphan CA without a collapse
    xw(2024, 300, "CT1", "CTG1", 300, "CT1"),
    # collapse onto a CA (not a CT): not a hit
    xw(2024, 400, "X", "G1", 400, "ST"),
    xw(2024, 400, "X", "G2", 400, "ST"),
    xw(2024, 400, "Y", "G3", 400, "CT9"),
    # a row with no EIA generator is skipped for links
    xw(2024, 500, "U", "G", 500, None),
    # 2019: the same collapse at 422
    xw(2019, 422, "GT5", "CTG5", 422, "GT5"),
    xw(2019, 422, "GT5", "STG5", 422, "GT5"),
]

D24 = "2024-01-01"
GENS = [
    gen(422, "GT5", D24, 71.0, "CT", "OP"),
    gen(422, "ST1", D24, 16.0, "CA", "OP"),
    gen(100, "CT1", D24, 170.0, "CT", "OP"),
    gen(100, "ST1", D24, 90.0, "CA", "OP"),
    gen(100, "ST9", D24, 20.0, "CA", "RE"),
    gen(200, "1", D24, 50.0, "CT", "OP"),
    gen(300, "CT1", D24, 100.0, "CT", "OP"),
    gen(300, "ST1", D24, 60.0, "CA", "OP"),
    gen(400, "ST", D24, 30.0, "CA", "OP"),
    gen(400, "ST2", D24, 30.0, "CA", "OP"),
    gen(400, "CT9", D24, 40.0, "CT", "OP"),
    gen(422, "GT5", datetime.date(2019, 1, 1), 71.0, "CT", "OP"),
    gen(422, "ST1", datetime.date(2019, 1, 1), 16.0, "CA", "OP"),
]


class IdTests(unittest.TestCase):
    def test_gid(self):
        self.assertEqual(c.gid(1.0), "1")
        self.assertEqual(c.gid(" st1 "), "ST1")
        self.assertEqual(c.gid(None), "")
        self.assertEqual(c.gid(float("nan")), "")

    def test_pint_fnum(self):
        self.assertEqual(c.pint("422"), 422)
        self.assertEqual(c.pint(422.0), 422)
        self.assertIsNone(c.pint(None))
        self.assertIsNone(c.fnum(float("nan")))
        self.assertEqual(c.fnum("16.5"), 16.5)


class IndexTests(unittest.TestCase):
    def test_links(self):
        links = c.index_links(XW)
        self.assertEqual(sorted(links), [2019, 2024])
        y = links[2024]
        self.assertEqual(y["units"][(422, "GT5")], {(422, "GT5"): {"CTG5", "STG5"}})
        self.assertIn((100, "ST1"), y["linked"])
        self.assertIn(500, y["eia_plants"])
        self.assertNotIn((500, ""), y["linked"])

    def test_gens(self):
        g = c.index_gens(GENS + [gen(422, "GT5", D24, None, "CT", "OP")])
        self.assertEqual(g[2024][(422, "GT5")], {"cap": 71.0, "pm": "CT", "status": "OP"})
        self.assertEqual(g[2019][(422, "ST1")]["cap"], 16.0)

    def test_gens_capacity_fills_in(self):
        g = c.index_gens([gen(1, "A", D24, None, "CT", "OP"), gen(1, "A", D24, 5.0, "CT", "OP")])
        self.assertEqual(g[2024][(1, "A")]["cap"], 5.0)


class LintTests(unittest.TestCase):
    def setUp(self):
        self.links = c.index_links(XW)
        self.gens = c.index_gens(GENS)
        self.lint = c.year_lint(self.links[2024], self.gens[2024])

    def test_hits(self):
        self.assertEqual(self.lint["hit_plants"], [422])
        self.assertEqual(len(self.lint["hits"]), 1)
        h = self.lint["hits"][0]
        self.assertEqual((h["camd_plant"], h["camd_unit"], h["eia_plant"], h["eia_generator"]),
                         (422, "GT5", 422, "GT5"))
        self.assertEqual(h["camd_generators"], ["CTG5", "STG5"])
        self.assertEqual(h["orphan_cas"], [{"generator": "ST1", "cap": 16.0}])
        self.assertTrue(h["st_in_camd_ids"])

    def test_plants(self):
        # CT linked at 422, 100, 200, 300, 400; operating CA at 422, 100, 300, 400
        self.assertEqual(self.lint["cc_plants"], 4)
        # orphan CA: 422/ST1, 300/ST1, 400/ST2 (100/ST9 is retired, 100/ST1 is linked)
        self.assertEqual(self.lint["orphan_ca_plants"], [300, 400, 422])
        d = {x["eia_plant"]: x for x in self.lint["orphan_detail"]}
        self.assertEqual(d[400]["linked_cts"], ["CT9"])
        self.assertFalse(d[400]["hit"])
        self.assertTrue(d[422]["hit"])

    def test_pm_share(self):
        self.assertEqual(c.pm_share(self.gens[2024], {422, 100}), 1.0)
        g = {(1, "A"): {"cap": 1.0, "pm": "", "status": "OP"},
             (1, "B"): {"cap": 1.0, "pm": "CT", "status": "OP"}}
        self.assertEqual(c.pm_share(g, {1}), 0.5)
        self.assertIsNone(c.pm_share(g, {2}))

    def test_p4_and_p6(self):
        lints = {str(y): c.year_lint(self.links[y], self.gens[y]) for y in (2019, 2024)}
        p4 = c.p4_persist(lints, self.links, 2024)
        self.assertEqual((p4["n"], p4["also"]), (1, 1))
        self.assertIsNone(c.p4_persist(lints, self.links, 2024, year=2018))
        self.assertEqual(c.p6_ratios(self.lint), {"422": round(16.0 / 71.0, 4)})


class ScoreTests(unittest.TestCase):
    def res(self, cc=250, hit_plants=(422, 58478, 1, 2, 3), orphan=10, p4=(4, 3),
            ratios=None):
        hits = [{"st_in_camd_ids": i != 0} for i in range(len(hit_plants))]
        return {"g1": {"missing_cols": [], "newest": 2024, "pm_share": 0.99, "cc_plants": cc},
                "by_year": {"2024": {"hit_plants": list(hit_plants), "hits": hits,
                                     "orphan_ca_plants": list(range(orphan))}},
                "p4": {"n": p4[0], "also": p4[1]},
                "p6_ratios": ratios if ratios is not None else {"422": 0.23, "58478": 0.3}}

    def test_all_held(self):
        s = c.score(self.res())
        self.assertEqual(s, {"G1": True, "G2": True, "P1": True, "P2": True, "P3": True,
                             "P4": True, "P5": True, "P6": True})

    def test_gate1_fails(self):
        self.assertEqual(c.score(self.res(cc=199)), {"G1": False})
        r = self.res()
        r["g1"]["pm_share"] = 0.9
        self.assertEqual(c.score(r), {"G1": False})

    def test_gate2_fails(self):
        self.assertEqual(c.score(self.res(hit_plants=(422, 1, 2, 3, 4))),
                         {"G1": True, "G2": False})

    def test_failed_bars(self):
        s = c.score(self.res(hit_plants=(422, 58478), orphan=3, p4=(4, 2),
                             ratios={"422": 0.05, "58478": 0.3}))
        self.assertFalse(s["P1"])
        self.assertTrue(s["P2"])
        self.assertFalse(s["P3"])
        self.assertFalse(s["P4"])
        self.assertFalse(s["P6"])

    def test_p4_needs_three(self):
        self.assertNotIn("P4", c.score(self.res(p4=(2, 2))))


if __name__ == "__main__":
    unittest.main()
