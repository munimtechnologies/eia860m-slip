"""Unit tests for ccsub.py on made-up rows (no downloads).

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import unittest

import ccsub as c


def srow(pi, gi, sid, unit=None, eu=None):
    return {"plant_id_eia": pi, "plant_id_epa": pi, "subplant_id": sid, "unit_id_pudl": unit,
            "emissions_unit_id_epa": eu, "generator_id": gi}


class IdTests(unittest.TestCase):
    def test_gid(self):
        self.assertEqual(c.gid(" st1 "), "ST1")
        self.assertEqual(c.gid(3.0), "3")
        self.assertEqual(c.gid(float("nan")), "")
        self.assertEqual(c.gid(None), "")
        self.assertEqual(c.gid(7), "7")

    def test_pint(self):
        self.assertEqual(c.pint("422"), 422)
        self.assertEqual(c.pint(2.0), 2)
        self.assertIsNone(c.pint(None))
        self.assertIsNone(c.pint("x"))


class IndexTests(unittest.TestCase):
    def test_index_sub(self):
        idx = c.index_sub([srow(422, "GT5", 5, 3, "GT5"), srow(422, "st1", 5, 3, "ST1"),
                           srow(422, None, 9, None, "XX"), srow(422, "GT1", None, None, None)])
        self.assertEqual(idx["present"], {(422, "GT5"), (422, "ST1"), (422, "GT1")})
        self.assertEqual(idx["gen_subs"][(422, "ST1")], {5})
        self.assertNotIn((422, "GT1"), idx["gen_subs"])
        self.assertEqual(idx["gen_units"][(422, "GT5")], {"3"})
        self.assertEqual(idx["sub_cems"][(422, 5)], {"GT5", "ST1"})
        self.assertEqual(idx["sub_cems"][(422, 9)], {"XX"})
        self.assertEqual(idx["sub_gens"][(422, 5)], {"GT5", "ST1"})


class ClassifyTests(unittest.TestCase):
    def setUp(self):
        self.idx = c.index_sub([
            srow(1, "CT1", 1, 7, "U1"), srow(1, "CA1", 1, 7, "CA1"),   # joined, shared unit
            srow(2, "CT1", 1, None, "U1"), srow(2, "CA1", 2, None, "CA1"),  # apart
            srow(3, "CT1", 1, None, "U1"),                                # CA absent
            srow(4, "CT1", 1, None, "U1"), srow(4, "CA1", 1, None, "U1"),  # joined, no unit
        ])

    def test_joined(self):
        r = c.classify(1, "CA1", ("CT1",), self.idx)
        self.assertEqual(r["class"], "joined")
        self.assertTrue(r["shared_unit"])
        self.assertEqual(r["subplant_generators"], ["CA1", "CT1"])
        self.assertEqual(r["subplant_cems_units"], ["CA1", "U1"])

    def test_apart(self):
        r = c.classify(2, "CA1", ("CT1",), self.idx)
        self.assertEqual(r["class"], "apart")
        self.assertFalse(r["shared_unit"])
        self.assertEqual((r["subplants"], r["ct_subplants"]), ([2], [1]))

    def test_absent(self):
        self.assertEqual(c.classify(3, "CA1", ("CT1",), self.idx)["class"], "absent")

    def test_joined_without_unit(self):
        r = c.classify(4, "CA1", ("CT1",), self.idx)
        self.assertEqual(r["class"], "joined")
        self.assertFalse(r["shared_unit"])

    def test_check_orphans_and_cts_missing(self):
        orph = {1: (("CT1",), ("CA1",)), 3: (("CT1", "CT9"), ("CA1",))}
        res = c.check_orphans(self.idx, orph)
        self.assertEqual([(r["plant"], r["class"]) for r in res], [(1, "joined"), (3, "absent")])
        self.assertEqual(c.cts_missing(self.idx, orph), ["3/CT9"])


class ConstantTests(unittest.TestCase):
    def test_orphans(self):
        self.assertEqual(len(c.ORPHANS), 9)
        self.assertEqual(sum(len(v[1]) for v in c.ORPHANS.values()), 10)
        self.assertTrue(all(p in c.ORPHANS for p in c.HIT_PLANTS))
        self.assertEqual(c.ORPHANS[60589], (("GEN1", "GEN2"), ("GEN3",)))


class BaseTests(unittest.TestCase):
    def test_base_rate(self):
        idx = c.index_sub([srow(1, "CT1", 1), srow(1, "CA1", 1), srow(1, "CA2", 2),
                           srow(2, "GT1", 1), srow(2, "CA1", 1)])
        gens = c.index_gens([
            {"plant_id_eia": 1, "generator_id": "CT1", "report_date": "2024-01-01",
             "capacity_mw": 100, "prime_mover_code": "CT", "operational_status_code": "OP"},
            {"plant_id_eia": 1, "generator_id": "CA1", "report_date": "2024-01-01",
             "capacity_mw": 50, "prime_mover_code": "CA", "operational_status_code": "OP"},
            {"plant_id_eia": 1, "generator_id": "CA2", "report_date": "2024-01-01",
             "capacity_mw": 50, "prime_mover_code": "CA", "operational_status_code": "OP"},
            {"plant_id_eia": 1, "generator_id": "CA3", "report_date": "2024-01-01",
             "capacity_mw": 0, "prime_mover_code": "CA", "operational_status_code": "OP"},
            {"plant_id_eia": 2, "generator_id": "GT1", "report_date": "2024-01-01",
             "capacity_mw": 100, "prime_mover_code": "GT", "operational_status_code": "OP"},
            {"plant_id_eia": 2, "generator_id": "CA1", "report_date": "2024-01-01",
             "capacity_mw": 50, "prime_mover_code": "CA", "operational_status_code": "OP"},
        ])
        linked = {(1, "CT1"), (1, "CA1"), (1, "CA2"), (1, "CA3"), (2, "GT1"), (2, "CA1")}
        b = c.base_rate(linked, gens, idx)
        # plant 2 has no linked CT, so it is not a CC plant; CA3 has zero nameplate.
        self.assertEqual((b["n"], b["joined"], b["share"]), (2, 1, 0.5))
        self.assertEqual(b["not_joined"][0]["generator"], "CA2")

    def test_index_linked(self):
        out = c.index_linked([{"report_year": 2024, "plant_id_eia": 1, "generator_id": "ct1"},
                              {"report_year": 2024, "plant_id_eia": 1, "generator_id": None}])
        self.assertEqual(out, {2024: {(1, "CT1")}})


def orphan(pi, cls, shared=True):
    return {"plant": pi, "class": cls, "shared_unit": shared}


class ScoreTests(unittest.TestCase):
    def base(self, orphans, n=300, joined=295):
        return {"g1": {"missing_cols": [], "rows": 50000, "cts_missing": []},
                "orphans": orphans, "base": {"n": n, "joined": joined}}

    def test_all_held(self):
        o = [orphan(p, "joined") for p in (422, 58478, 60589, 7242, 7307, 10682, 52176)]
        o += [orphan(55419, "apart", False), orphan(55419, "joined"), orphan(55524, "apart")]
        s = c.score(self.base(o))
        self.assertEqual(s, {"G1": True, "P1": True, "P2": True, "P3": True, "P4": True,
                             "P5": True})

    def test_failed_bars(self):
        o = [orphan(422, "joined", False), orphan(58478, "apart"), orphan(60589, "absent")]
        o += [orphan(7242, "joined"), orphan(7307, "joined")]
        s = c.score(self.base(o, n=300, joined=284))
        self.assertEqual(s, {"G1": True, "P1": False, "P2": False, "P3": False, "P4": False,
                             "P5": False})

    def test_unscored(self):
        o = [orphan(422, "joined"), orphan(58478, "joined"), orphan(7307, "apart")]
        s = c.score(self.base(o, n=150, joined=150))
        self.assertNotIn("P4", s)
        self.assertNotIn("P5", s)
        self.assertTrue(s["P3"])

    def test_gate_fails(self):
        r = self.base([orphan(422, "joined")])
        r["g1"]["cts_missing"] = ["422/GT5"]
        self.assertEqual(c.score(r), {"G1": False})
        r = self.base([orphan(422, "joined")])
        r["g1"]["rows"] = 19999
        self.assertEqual(c.score(r), {"G1": False})
        self.assertEqual(c.score({}), {})

    def test_constants(self):
        self.assertEqual((c.MIN_ROWS, c.P2_MIN, c.P3_MIN, c.P4_MIN_N, c.P5_MIN_N, c.P5_SHARE),
                         (20000, 7, 2, 3, 200, 0.95))


if __name__ == "__main__":
    unittest.main()
