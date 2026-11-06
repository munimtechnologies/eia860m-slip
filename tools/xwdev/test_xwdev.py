"""Unit tests for xwdev.py (no network). Apache-2.0. MV2 of Munim, Inc. (made with AI agents)."""

import unittest

import xwdev

GLENARM = xwdev.LEADS[2]
COLS = {"epa_plant": "p", "epa_gen": "g", "eia_plant": "ep", "eia_gen": "eg"}


class ColTests(unittest.TestCase):
    def test_find_cols(self):
        found, missing = xwdev.find_cols(["sequence_number", "epa_plant_id", "EPA_GENERATOR_ID",
                                          "eia_plant_id", "eia_generator_id", "match_type_gen"])
        self.assertEqual(missing, [])
        self.assertEqual(found["epa_plant"], "epa_plant_id")
        self.assertEqual(found["epa_gen"], "EPA_GENERATOR_ID")
        self.assertEqual(found["match_gen"], "match_type_gen")
        self.assertNotIn("epa_unit", found)

    def test_missing(self):
        found, missing = xwdev.find_cols(["epa_plant_id"])
        self.assertEqual(missing, ["epa_gen", "eia_plant", "eia_gen"])
        found, missing = xwdev.find_cols([])
        self.assertEqual(len(missing), 4)


class IndexTests(unittest.TestCase):
    def test_index_rows(self):
        rows = [{"p": "422", "g": " stg5", "ep": "422.0", "eg": "gt5"},
                {"p": "422", "g": "CTG5", "ep": "", "eg": ""}]
        by_gen, linked, plants = xwdev.index_rows(rows, COLS)
        self.assertEqual(by_gen, {(422, "STG5"): {(422, "GT5")}})
        self.assertEqual(linked, {(422, "GT5")})
        self.assertEqual(plants, {422})

    def test_ids(self):
        self.assertEqual(xwdev.gid(1.0), "1")
        self.assertEqual(xwdev.gid(None), "")
        self.assertEqual(xwdev.pint("57865.0"), 57865)
        self.assertIsNone(xwdev.pint("ELK1"))
        self.assertIsNone(xwdev.pint(""))


class LeadTests(unittest.TestCase):
    def test_stands(self):
        st = xwdev.lead_status(GLENARM, {(422, "STG5"): {(422, "GT5")}}, {(422, "GT5")})
        self.assertEqual(st["outcome"], "stands")
        self.assertEqual(st["links"], {"STG5": ["422/GT5"]})

    def test_fixed(self):
        st = xwdev.lead_status(GLENARM, {(422, "STG5"): {(422, "ST1")}}, {(422, "ST1")})
        self.assertEqual(st["outcome"], "fixed")
        self.assertEqual(st["candidates_linked"], ["422/ST1"])

    def test_absent(self):
        self.assertEqual(xwdev.lead_status(GLENARM, {}, set())["outcome"], "absent")

    def test_other(self):
        st = xwdev.lead_status(GLENARM, {(422, "STG5"): {(422, "GT5")}},
                               {(422, "GT5"), (422, "ST1")})
        self.assertEqual(st["outcome"], "other")

    def test_both_links_is_other(self):
        st = xwdev.lead_status(GLENARM, {(422, "STG5"): {(422, "GT5"), (422, "ST1")}},
                               {(422, "GT5"), (422, "ST1")})
        self.assertEqual(st["outcome"], "other")


class ScoreTests(unittest.TestCase):
    def res(self, outcomes, rows=5000, plants=4, missing=()):
        return {"g1": {"missing_cols": list(missing), "rows": rows, "plants_present": plants},
                "leads": {l[0]: {"outcome": o} for l, o in zip(xwdev.LEADS, outcomes)}}

    def test_all_stand(self):
        s = xwdev.score(self.res(["stands"] * 4))
        self.assertEqual(s, {"G1": True, "P1": True, "P2": True, "P3": True, "P4": True,
                             "P5": True})

    def test_one_fixed(self):
        s = xwdev.score(self.res(["fixed", "stands", "stands", "stands"]))
        self.assertFalse(s["P1"])
        self.assertTrue(s["P2"])
        self.assertFalse(s["P5"])

    def test_gate(self):
        self.assertEqual(xwdev.score(self.res(["stands"] * 4, rows=100)), {"G1": False})
        self.assertEqual(xwdev.score(self.res(["stands"] * 4, plants=3)), {"G1": False})
        self.assertEqual(xwdev.score(self.res(["stands"] * 4, missing=["eia_gen"])),
                         {"G1": False})
        self.assertEqual(xwdev.score({}), {})

    def test_constants(self):
        self.assertEqual(xwdev.MIN_ROWS, 4000)
        self.assertEqual(xwdev.PREDICTED["P1"], "Antelope Elk")
        self.assertEqual(len(xwdev.COMMIT), 40)
        self.assertEqual(xwdev.LEADS[1], ("Chalk Point", 1571, {"SGT1": (1571, "GT1")},
                                          ((61890, "SGT1"),)))


if __name__ == "__main__":
    unittest.main()
