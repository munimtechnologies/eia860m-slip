"""Unit tests for xwcap_check.py on small made-up groups (no downloads).

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.)."""

import unittest

import xwcap_check as xc


def gen(pm, cap, status="OP"):
    return {"pm": pm, "status": status, "cap": cap}


class ComponentTests(unittest.TestCase):
    def test_shared_generator_joins_units(self):
        edges = [((1, "A"), (1, "G1")), ((1, "B"), (1, "G1")), ((1, "C"), (1, "G2"))]
        comps = xc.components(edges)
        self.assertEqual(len(comps), 2)
        self.assertEqual(comps[0], ({(1, "A"), (1, "B")}, {(1, "G1")}))
        self.assertEqual(comps[1], ({(1, "C")}, {(1, "G2")}))

    def test_chain_is_one_group(self):
        edges = [((1, "A"), (1, "G1")), ((1, "A"), (1, "G2")), ((1, "B"), (1, "G2"))]
        comps = xc.components(edges)
        self.assertEqual(len(comps), 1)
        self.assertEqual(comps[0][1], {(1, "G1"), (1, "G2")})


class AnalyseTests(unittest.TestCase):
    def test_engine_link_with_unlinked_turbine_is_candidate(self):
        edges = [((10, "1"), (10, "E01"))]
        ops = {(10, "1"): 204.0}
        gens = {(10, "E01"): gen("IC", 9.3), (10, "E02"): gen("IC", 9.3),
                (10, "ELK1"): gen("GT", 202.0)}
        (r,) = xc.analyse(edges, ops, gens)
        self.assertTrue(r["study"])
        self.assertAlmostEqual(r["ratio"], 204.0 / 9.3)
        self.assertTrue(r["over"])
        self.assertEqual(r["cls"], "candidate")
        self.assertEqual(r["candidates"], [(10, "ELK1")])

    def test_combined_cycle_link_is_cc(self):
        edges = [((20, "CT1"), (20, "CT1"))]
        gens = {(20, "CT1"): gen("CT", 180.0), (20, "ST9"): gen("GT", 300.0)}
        (r,) = xc.analyse(edges, {(20, "CT1"): 300.0}, gens)
        self.assertTrue(r["over"])
        self.assertEqual(r["cls"], "cc")
        self.assertEqual(r["candidates"], [])

    def test_small_excess_is_not_over(self):
        edges = [((30, "1"), (30, "G1"))]
        (r,) = xc.analyse(edges, {(30, "1"): 12.0}, {(30, "G1"): gen("GT", 6.0)})
        self.assertTrue(r["study"])
        self.assertEqual(r["ratio"], 2.0)
        self.assertFalse(r["over"])
        self.assertIsNone(r["cls"])

    def test_missing_capacity_leaves_study(self):
        edges = [((40, "1"), (40, "G1")), ((40, "1"), (40, "G2"))]
        (r,) = xc.analyse(edges, {(40, "1"): 100.0}, {(40, "G1"): gen("GT", 50.0)})
        self.assertFalse(r["study"])
        self.assertIsNone(r["ratio"])
        self.assertFalse(r["over"])

    def test_retired_or_small_or_linked_generators_are_not_candidates(self):
        edges = [((50, "1"), (50, "G1")), ((50, "2"), (50, "G3"))]
        gens = {(50, "G1"): gen("GT", 100.0), (50, "G2"): gen("GT", 150.0, "RE"),
                (50, "G3"): gen("GT", 150.0), (50, "G4"): gen("PV", 150.0),
                (50, "G5"): gen("GT", 49.0)}
        recs = xc.analyse(edges, {(50, "1"): 200.0, (50, "2"): 100.0}, gens)
        self.assertEqual(recs[0]["units"], [(50, "1")])
        self.assertTrue(recs[0]["over"])
        self.assertEqual(recs[0]["cls"], "other")
        self.assertFalse(recs[1]["over"])

    def test_units_without_load_add_nothing(self):
        edges = [((60, "1"), (60, "G1")), ((60, "2"), (60, "G1"))]
        (r,) = xc.analyse(edges, {(60, "1"): 80.0, (60, "2"): None}, {(60, "G1"): gen("ST", 100.0)})
        self.assertEqual(r["cems_max"], 80.0)
        self.assertEqual(r["n_units_max"], 1)
        self.assertAlmostEqual(r["ratio"], 0.8)
        self.assertFalse(r["under"])


class SummaryAndScoreTests(unittest.TestCase):
    def test_summary_counts(self):
        edges = [((10, "1"), (10, "E01")), ((20, "CT1"), (20, "CT1")), ((30, "1"), (30, "G1")),
                 ((70, "1"), (70, "G1"))]
        gens = {(10, "E01"): gen("IC", 9.3), (10, "ELK1"): gen("GT", 202.0),
                (20, "CT1"): gen("CT", 180.0), (30, "G1"): gen("GT", 100.0),
                (70, "G1"): gen("ST", 100.0)}
        ops = {(10, "1"): 204.0, (20, "CT1"): 300.0, (30, "1"): 100.0, (70, "1"): 40.0}
        s = xc.summary(xc.analyse(edges, ops, gens))
        self.assertEqual(s["study"], 4)
        self.assertEqual(s["over"], 2)
        self.assertEqual(s["over_2x"], 1)
        self.assertEqual(s["under"], 1)
        self.assertEqual(s["over_by_class"], {"cc": 1, "candidate": 1, "other": 0})
        self.assertEqual(s["single_pair_study"], 4)

    def test_persistence(self):
        cur = [{"units": [(1, "A"), (1, "B")], "study": True, "over": True},
               {"units": [(2, "A")], "study": True, "over": True}]
        prev = [{"units": [(1, "A")], "study": True, "over": True},
                {"units": [(1, "B")], "study": True, "over": False}]
        self.assertEqual(xc.persistence(cur, prev),
                         {"over_units": 3, "in_prev_study": 2, "also_over_prev": 1})

    def test_plant_check(self):
        edges = [((10, "1"), (10, "E01"))]
        gens = {(10, "E01"): gen("IC", 9.3), (10, "ELK1"): gen("GT", 202.0)}
        recs = xc.analyse(edges, {(10, "1"): 204.0}, gens)
        pc = xc.plant_check(recs, 10, gens, {(10, "E01")})
        self.assertEqual((pc["groups"], pc["study"], pc["over"], pc["candidate"]), (1, 1, 1, 1))
        self.assertEqual([g["generator_id"] for g in pc["eia_generators"]], ["E01", "ELK1"])
        self.assertEqual([g["linked"] for g in pc["eia_generators"]], [True, False])

    def test_score(self):
        r = {"year": 2024, "g1": {"missing_cols": []},
             "main": {"study": 2000, "median_ratio": 0.98, "over": 40,
                      "over_by_class": {"cc": 19, "candidate": 9, "other": 12}},
             "plant_check": {"study": 3, "over": 3, "candidate": 3},
             "persistence": {"in_prev_study": 50, "also_over_prev": 36}}
        s = xc.score(r)
        self.assertEqual(s, {"G1": True, "G2": True, "G3": True, "P1": True, "P2": True,
                             "P3": True, "P4": True, "P5": True})
        r["main"]["over"] = 120
        r["main"]["over_by_class"] = {"cc": 60, "candidate": 23, "other": 37}
        r["persistence"]["also_over_prev"] = 34
        r["plant_check"]["candidate"] = 2
        s = xc.score(r)
        self.assertEqual(s, {"G1": True, "G2": True, "G3": True, "P1": False, "P2": False,
                             "P3": False, "P4": False, "P5": False})

    def test_gates_stop_predictions(self):
        r = {"year": 2021, "g1": {"missing_cols": []},
             "main": {"study": 2000, "median_ratio": 0.98, "over": 40,
                      "over_by_class": {"cc": 19, "candidate": 8, "other": 13}}}
        self.assertEqual(xc.score(r), {"G1": False, "G2": True, "G3": True})
        r["year"] = 2024
        r["main"]["median_ratio"] = 1.31
        self.assertEqual(xc.score(r), {"G1": True, "G2": True, "G3": False})

    def test_median(self):
        self.assertEqual(xc.median([3, 1, 2]), 2)
        self.assertEqual(xc.median([4, 1, 2, 3]), 2.5)
        self.assertIsNone(xc.median([]))


if __name__ == "__main__":
    unittest.main()
