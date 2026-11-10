"""Unit tests for easeyx3.py on made-up rows (standard library only; reads no outside data).

Apache-2.0. MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import easeyx as E  # noqa: E402
import easeyx3 as X  # noqa: E402

REF_TEXT = (
    "CAMD_PLANT_ID,CAMD_UNIT_ID,CAMD_GENERATOR_ID,CAMD_STATUS,EIA_PLANT_ID,EIA_GENERATOR_ID,"
    "MATCH_TYPE_GEN\n"
    "1,A,G1,OPR,1,G1,3_1_Exact\n"
    "1,B,g2,OPR,1,G2,3_1_Exact\n"
    "2,C,CT1,OPR,2,1,4_2_Other\n"
    "3,D,01,RET,3,1,4_2_Other\n"
    "4,E,,OPR,NA,NA,NA\n"
    "5,F,F1,OPR,5,F1,3_1_Exact\n"
    "1,A,G1,OPR,1,G1B,3_1_Exact\n"
    "6,H,H1,OPR,6,H1,3_1_Exact\n")

SIDE_TEXT = (
    "state,facility_name,plant_id,unit_id,generator_id,nameplate_capacity_mw,primary_fuel_type,"
    "latitude,longitude,latest_status,latest_class,derived_retire_year,commercial_operation_date,"
    "first_year,latest_year\n"
    "AL,One,1,A,G1,100,Coal,,,Operating,OPR,0,,2010,2025\n"
    "AL,One,1,B,g2,50,Coal,,,Operating,OPR,0,,2010,2025\n"
    "AL,Two,2,C,CT1,10,Gas,,,Operating,OPR,0,,2010,2025\n"
    "AL,Three,3,D,01,10,Gas,,,Retired,RET,2015,,2010,2015\n"
    "AL,Four,4,E,,5,Oil,,,Operating,OPR,0,,2012,2025\n"
    "AL,Six,6,H,H1,20,Gas,,,Operating,OPR,0,,2025,2025\n"
    "AL,Seven,7,N1,N1,30,Gas,,,Operating,OPR,0,,2025,2025\n"
    "AL,Seven,7,N2,N2,30,Gas,,,Operating,OPR,0,,2024,2025\n"
    "AL,Eight,8,R,R1,30,Gas,,,Retired,RET,2020,,2010,2020\n")

PUDL_ROWS = [("1", "G1", "2024-01-01", "OP"), ("1", "G1", "2025-01-01", "OP"),
             ("1", "G2", "2024-01-01", "OP"), ("2", "CT1", "2024-01-01", "OP"),
             ("2", "1", "2024-01-01", "OP"), ("7", "n1", "2025-01-01", "OP"),
             ("7", "N1", "2023-01-01", "SB"), ("9", None, "2024-01-01", "OP"),
             (None, "X", "2024-01-01", "OP"), ("6", "H1", "2026-01-01", None)]


def made_up():
    ref_info, ref = X.read_reference_links(REF_TEXT)
    side_info, side = X.read_side(SIDE_TEXT)
    pairs, years = X.pudl_pairs(PUDL_ROWS)
    return ref_info, ref, side_info, side, pairs, years


class HelperTests(unittest.TestCase):
    def test_blank_and_keys(self):
        for v in (None, "", " ", "NA", " na ", "NaN", "None", "NULL"):
            self.assertTrue(X.blank(v), v)
        self.assertFalse(X.blank("0"))
        self.assertEqual(X.gen_key(" gt1 "), "GT1")
        self.assertEqual(X.gen_key("NA"), "")
        self.assertEqual(X.plant("3.0"), "3")
        self.assertEqual(X.plant("NA"), "")
        self.assertEqual(X.plant(None), "")
        self.assertEqual(X.pair(("1", "B", "g2")), ("1", "G2"))
        self.assertTrue(X.ok(0.5, 0.5))
        self.assertFalse(X.ok(None, 0.1))


class ReadTests(unittest.TestCase):
    def test_reference(self):
        info, ref, _, _, _, _ = made_up()
        self.assertEqual((info["rows"], info["keys"], info["linked_keys"], info["multi_link_keys"],
                          info["missing_cols"]), (8, 7, 6, 1, []))
        self.assertEqual(ref[("1", "A", "G1")]["links"], {("1", "G1"), ("1", "G1B")})
        self.assertEqual(ref[("4", "E", "")]["links"], set())
        self.assertEqual(ref[("4", "E", "")]["match_types"], set())
        self.assertEqual(ref[("3", "D", "01")]["status"], "RET")

    def test_side(self):
        _, _, info, side, _, _ = made_up()
        self.assertEqual((info["rows"], info["keys"], info["missing_cols"]), (9, 9, []))
        self.assertEqual(side[("7", "N1", "N1")]["first_year"], 2025)
        self.assertEqual(side[("1", "B", "g2")]["capacity"], "50")

    def test_missing_columns(self):
        info, ref = X.read_reference_links("CAMD_PLANT_ID,CAMD_UNIT_ID\n1,A\n")
        self.assertIn("EIA_GENERATOR_ID", info["missing_cols"])
        self.assertEqual((ref, info["keys"]), ({}, 0))
        info, side = X.read_side("plant_id,unit_id\n1,A\n")
        self.assertIn("generator_id", info["missing_cols"])
        self.assertEqual((side, info["keys"]), ({}, 0))

    def test_pudl_pairs(self):
        _, _, _, _, pairs, years = made_up()
        self.assertEqual(sorted(pairs), [("1", "G1"), ("1", "G2"), ("2", "1"), ("2", "CT1"),
                                         ("6", "H1"), ("7", "N1")])
        self.assertEqual(pairs[("7", "N1")], {"last_year": 2025, "last_status": "OP"})
        self.assertEqual(pairs[("1", "G1")]["last_year"], 2025)
        self.assertEqual(pairs[("6", "H1")], {"last_year": 2026, "last_status": ""})
        self.assertEqual(years, {2023, 2024, 2025, 2026})


class ScoreTests(unittest.TestCase):
    def test_measures(self):
        _, ref, _, side, pairs, _ = made_up()
        m, scores, rep, not_same, new_opr = X.score(ref, side, pairs)
        self.assertEqual(m["carry_forward"],
                         {"side_keys": 9, "by_class": {"OPR|linked": 4, "OPR|new": 2,
                                                       "OPR|unlinked": 1, "RET|linked": 1,
                                                       "RET|new": 1},
                          "opr_keys": 7, "opr_linked": 4, "share": round(4 / 7, 5)})
        self.assertEqual(m["ref_first_seen_2025"],
                         {"ref_keys": 7, "ref_keys_not_in_side": 1, "keys": 1,
                          "by_status": {"OPR": 1}})
        self.assertEqual(m["exact_in_ref"], {"linked_keys": 6, "same_ids": 4,
                                             "share": round(4 / 6, 5), "same_ids_loose": 5})
        self.assertEqual(m["exact_precision"], {"linked_keys_with_pair_in_pudl": 4,
                                                "ref_links_to_it": 3, "share": 0.75})
        self.assertEqual(m["new_opr"], {"keys": 2, "pair_in_pudl": 1, "share": 0.5,
                                        "by_first_year": {"2024": 1, "2025": 1},
                                        "pudl_last_status": {"OP": 1}})
        self.assertEqual(scores, {"P1": False, "P2": False, "P3": False, "P4": False,
                                  "P5": False})
        self.assertEqual(not_same, [("2", "C", "CT1"), ("3", "D", "01")])
        self.assertEqual(new_opr, [("7", "N1", "N1"), ("7", "N2", "N2")])
        self.assertEqual(rep["match_types_linked_top20"], {"3_1_Exact": 4, "4_2_Other": 2})
        self.assertEqual(rep["match_types_not_same_top20"], {"4_2_Other": 2})
        self.assertEqual(rep["not_same_pair_in_pudl"], 1)
        self.assertEqual(rep["not_same_by_status"], {"OPR": 1, "RET": 1})
        self.assertEqual(rep["ref_unlinked_by_status"], {"OPR": 1})
        self.assertEqual(rep["new_by_class"], {"OPR": 2, "RET": 1})
        self.assertEqual(rep["ref_first_seen_2025_keys"], ["6|H|H1"])

    def test_scores_flip_at_bars(self):
        _, ref, _, side, pairs, _ = made_up()
        saved = (X.P1_MIN, X.P2_MIN, X.P3_MIN, X.P4_MIN, X.P5_MIN_KEYS)
        try:
            X.P1_MIN, X.P2_MIN, X.P3_MIN, X.P4_MIN, X.P5_MIN_KEYS = 0.5, 0.6, 0.75, 0.5, 1
            _, scores, _, _, _ = X.score(ref, side, pairs)
            self.assertEqual(scores, {"P1": True, "P2": True, "P3": True, "P4": True, "P5": True})
        finally:
            X.P1_MIN, X.P2_MIN, X.P3_MIN, X.P4_MIN, X.P5_MIN_KEYS = saved

    def test_rows(self):
        _, ref, _, side, pairs, _ = made_up()
        rows = X.new_rows(ref, side, pairs)
        self.assertEqual(rows[0], ["7", "N1", "N1", "AL", "Seven", "OPR", 2025, 2025, "30", "Gas",
                                   "yes", 2025, "OP"])
        self.assertEqual(rows[2][:3] + rows[2][10:], ["8", "R", "R1", "no", "", ""])
        self.assertEqual(len(rows), 3)
        _, _, _, not_same, _ = X.score(ref, side, pairs)
        self.assertEqual(X.not_same_rows(ref, not_same, pairs),
                         [["2", "C", "CT1", "OPR", "2:1", "yes", "4_2_Other"],
                          ["3", "D", "01", "RET", "3:1", "no", "4_2_Other"]])

    def test_gates(self):
        ref_info, _, side_info, _, pairs, years = made_up()
        g, gm = X.gates(X.REF_MD5, ref_info, side_info, {"missing_cols": []}, pairs, years)
        self.assertEqual(g, {"G1": True, "G2": False, "G3": False})
        self.assertEqual((gm["side_rows"], gm["pudl_pairs"], gm["pudl_years"]), (9, 6, [2023, 2026]))
        g, _ = X.gates("x", ref_info, dict(side_info, rows=7187), {"missing_cols": []}, pairs, years)
        self.assertEqual((g["G1"], g["G2"]), (False, True))
        big = {("%d" % i, "G"): {"last_year": 2024, "last_status": "OP"} for i in range(20000)}
        g, _ = X.gates(X.REF_MD5, ref_info, side_info, {"missing_cols": []}, big, {2024})
        self.assertTrue(g["G3"])
        g, _ = X.gates(X.REF_MD5, ref_info, side_info, {"missing_cols": ["generator_id"]}, big,
                       {2024})
        self.assertFalse(g["G3"])
        g, _ = X.gates(X.REF_MD5, ref_info, side_info, {"missing_cols": []}, big, {2023})
        self.assertFalse(g["G3"])


class ConstantTests(unittest.TestCase):
    def test_constants(self):
        self.assertEqual(X.VERSION, "0.1.0")
        self.assertEqual(E.VERSION, "0.1.0")
        self.assertEqual(X.REF_MD5, "106d813fd9b850f11a0be088f317ef13")
        self.assertEqual((X.G2_SIDE_ROWS, X.G3_MIN_PAIRS, X.G3_YEAR, X.NEW_YEAR),
                         (7187, 20000, 2024, 2025))
        self.assertEqual((X.P1_MIN, X.P2_MIN, X.P3_MIN, X.P4_MIN, X.P5_MIN_KEYS),
                         (0.90, 0.80, 0.95, 0.60, 10))
        self.assertEqual(X.GEN_TABLE, "core_eia860__scd_generators")


if __name__ == "__main__":
    unittest.main()
