"""Unit tests for xwpudl.py (no network, no polars). Apache-2.0. Made with AI agents working in
MV2's name (MV2, Munim, Inc.)."""

import datetime
import unittest

import xwpudl as X


def xw(year, pe, ue, ge, pi, gi):
    return {"report_year": year, "plant_id_epa": pe, "emissions_unit_id_epa": ue,
            "generator_id_epa": ge, "plant_id_eia": pi, "generator_id": gi}


GLENARM = [l for l in X.LEADS if l[0] == "Glenarm"][0]
ELK = [l for l in X.LEADS if l[0] == "Antelope Elk"][0]


class IdTests(unittest.TestCase):
    def test_gid_and_pint(self):
        self.assertEqual(X.gid(" stg5 "), "STG5")
        self.assertEqual(X.gid(1.0), "1")
        self.assertEqual(X.gid(float("nan")), "")
        self.assertEqual(X.gid(None), "")
        self.assertEqual(X.pint("422"), 422)
        self.assertEqual(X.pint(58478.0), 58478)
        self.assertIsNone(X.pint(""))

    def test_leads_constants(self):
        self.assertEqual([l[0] for l in X.LEADS],
                         ["Antelope Elk", "Chalk Point", "Glenarm", "LEPA Unit No. 1"])
        self.assertEqual(set(X.PREDICTED.values()), {"Chalk Point", "Glenarm",
                                                     "LEPA Unit No. 1"})
        self.assertEqual(X.MIN_NEWEST, 2023)
        self.assertEqual(X.MIN_P4_CELLS, 10)
        self.assertEqual(X.P5_YEAR, 2021)


class LeadTests(unittest.TestCase):
    def test_persists(self):
        rows = [xw(2024, 422, "GT5", "CTG5", 422, "GT5"), xw(2024, 422, "GT5", "STG5", 422, "GT5"),
                xw(2024, 422, "GT3", "GT3", 422, "GT3")]
        by_gen, linked, plants = X.index_links(rows)
        st = X.lead_year(GLENARM, by_gen[2024], linked[2024])
        self.assertTrue(st["camd_gens_found"])
        self.assertTrue(st["linked_to_flagged"])
        self.assertEqual(st["candidates_linked"], [])
        self.assertTrue(st["persists"])
        self.assertEqual(st["links"], {"STG5": ["422/GT5"]})
        self.assertEqual(plants[2024], {422})

    def test_fixed_when_candidate_linked(self):
        rows = [xw(2024, 422, "GT5", "CTG5", 422, "GT5"), xw(2024, 422, "GT5", "STG5", 422, "ST1")]
        by_gen, linked, _ = X.index_links(rows)
        st = X.lead_year(GLENARM, by_gen[2024], linked[2024])
        self.assertFalse(st["linked_to_flagged"])
        self.assertTrue(st["camd_gen_to_candidate"])
        self.assertEqual(st["candidates_linked"], ["422/ST1"])
        self.assertFalse(st["persists"])

    def test_candidate_linked_by_another_unit_breaks_persist(self):
        rows = [xw(2024, 422, "GT5", "STG5", 422, "GT5"), xw(2024, 422, "X", "Y", 422, "ST1")]
        by_gen, linked, _ = X.index_links(rows)
        st = X.lead_year(GLENARM, by_gen[2024], linked[2024])
        self.assertTrue(st["linked_to_flagged"])
        self.assertFalse(st["persists"])

    def test_missing_camd_gen(self):
        rows = [xw(2024, 57865, "1", "ELK1", 57865, "E01"),
                xw(2024, 57865, "2", "ELK2", 57865, "E02")]
        by_gen, linked, _ = X.index_links(rows)
        st = X.lead_year(ELK, by_gen[2024], linked[2024])
        self.assertFalse(st["camd_gens_found"])
        self.assertFalse(st["persists"])


class GenTests(unittest.TestCase):
    def test_index_gens_and_p4(self):
        rows = [{"plant_id_eia": 422, "generator_id": "ST1", "report_date": datetime.date(2021, 1, 1),
                 "capacity_mw": 16.0, "prime_mover_code": "CA", "operational_status_code": "OP"},
                {"plant_id_eia": 422, "generator_id": "ST1", "report_date": "2024-01-01",
                 "capacity_mw": 16.0, "prime_mover_code": "CA", "operational_status_code": "OP"},
                {"plant_id_eia": 422, "generator_id": "GT1", "report_date": "2024-01-01",
                 "capacity_mw": 28.8, "prime_mover_code": "GT", "operational_status_code": "OP"}]
        g = X.index_gens(rows, [(422, "ST1")])
        self.assertEqual(sorted(g[(422, "ST1")]), [2021, 2024])
        self.assertNotIn((422, "GT1"), g)
        leads = {l[0]: {"2021": {"candidates_linked": []}, "2024": {"candidates_linked": []}}
                 for l in X.LEADS}
        leads["Glenarm"]["2024"]["candidates_linked"] = ["422/ST1"]
        p4 = X.p4_cells(leads, g, [2021, 2024])
        self.assertEqual((p4["cells"], p4["linked"]), (2, 1))


class ScoreTests(unittest.TestCase):
    def res(self, persists=True, newest=2024, plants=4, cells=12, linked=0, p5=True):
        leads = {l[0]: {str(newest): {"persists": persists}} for l in X.LEADS}
        return {"g1": {"missing_cols": [], "newest": newest, "plants_in_newest": plants},
                "leads": leads, "p4": {"cells": cells, "linked": linked},
                "p5": {"61890/SGT1": p5, "422/ST1": True, "58478/LEPA2": True}}

    def test_all_hold(self):
        self.assertEqual(X.score(self.res()), {"G1": True, "P1": True, "P2": True, "P3": True,
                                               "P4": True, "P5": True})

    def test_gate_fails(self):
        self.assertEqual(X.score(self.res(newest=2022)), {"G1": False})
        self.assertEqual(X.score(self.res(plants=3)), {"G1": False})

    def test_failures_and_too_few_cells(self):
        s = X.score(self.res(persists=False, cells=9, p5=False))
        self.assertFalse(s["P1"])
        self.assertNotIn("P4", s)
        self.assertFalse(s["P5"])
        self.assertFalse(X.score(self.res(linked=1))["P4"])


if __name__ == "__main__":
    unittest.main()
