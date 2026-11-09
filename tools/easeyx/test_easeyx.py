"""Unit tests for easeyx.py on made-up rows (standard library only; reads no outside data).

Apache-2.0. MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import easeyx as E  # noqa: E402

HEADER = ('"State","Facility Name","Facility ID","Unit ID","Year","Operating Status",'
          '"Commercial Operation Date","Primary Fuel Type",'
          '"Associated Generators & Nameplate Capacity (MWe)"\n')


def fac(year, rows):
    lines = [HEADER]
    for plant, unit, status, cod, gens in rows:
        lines.append('"AL","P%s","%s","%s","%d","%s","%s","Coal","%s"\n'
                     % (plant, plant, unit, year, status, cod, gens))
    return E.read_facility("".join(lines), year)


REF_HEAD = ("SEQUENCE_NUMBER,CAMD_PLANT_ID,CAMD_UNIT_ID,CAMD_GENERATOR_ID,CAMD_STATUS,"
            "CAMD_STATUS_DATE,CAMD_RETIRE_YEAR\n")


class HelperTests(unittest.TestCase):
    def test_norm_col(self):
        self.assertEqual(E.norm_col("Associated Generators & Nameplate Capacity (MWe)"),
                         "associated_generators_nameplate_capacity_mwe")
        self.assertEqual(E.norm_col(" Facility ID "), "facility_id")

    def test_parse_generators(self):
        self.assertEqual(E.parse_generators("1 (153.1)"), [("1", 153.1)])
        self.assertEqual(E.parse_generators("CT1 (170), CT2 (170.5)"),
                         [("CT1", 170.0), ("CT2", 170.5)])
        self.assertEqual(E.parse_generators(""), [("", None)])
        self.assertEqual(E.parse_generators("GEN1"), [("GEN1", None)])
        self.assertEqual(E.parse_generators("A (x)"), [("A", None)])

    def test_status(self):
        self.assertEqual(E.status_class("Operating"), "OPR")
        self.assertEqual(E.status_class("Operating (Started 05/15/2021)"), "OPR")
        self.assertEqual(E.status_class("Operating (Retired 06/01/2023)"), "RET")
        self.assertEqual(E.status_class("Retired"), "RET")
        self.assertEqual(E.status_class("Long-term Cold Storage"), "LTCS")
        self.assertEqual(E.status_class("Future"), "FUT")
        self.assertEqual(E.status_class(""), "OTHER")
        self.assertEqual(E.retired_year_in("Operating (Retired 06/01/2023)"), 2023)
        self.assertEqual(E.retired_year_in("Retired 2015-08-24"), 2015)
        self.assertIsNone(E.retired_year_in("Retired"))

    def test_keys_and_days(self):
        self.assertEqual(E.plant_key("3.0"), "3")
        self.assertEqual(E.plant_key(" 55243 "), "55243")
        self.assertEqual(E.loose("01"), "1")
        self.assertEqual(E.loose("0"), "0")
        self.assertEqual(E.loose(""), "")
        self.assertEqual(str(E.parse_day("1954-02-11T00:00:00")), "1954-02-11")
        self.assertEqual(str(E.parse_day("2/12/1954")), "1954-02-12")
        self.assertIsNone(E.parse_day(""))
        self.assertEqual(E.int_or0("2015.0"), 2015)
        self.assertEqual(E.int_or0(""), 0)


class ReadTests(unittest.TestCase):
    def test_read_reference(self):
        text = REF_HEAD + ("1,3,1,1,OPR,1954-02-11T00:00:00,0\n"
                           "2,3,1,1,OPR,1954-02-11T00:00:00,0\n"
                           "3,3,3,3,RET,2015-08-24T00:00:00,2015\n"
                           "4,,,,,,\n")
        info, ref = E.read_reference(text)
        self.assertEqual((info["rows"], info["rows_no_camd_key"], info["duplicate_key_rows"],
                          info["keys"]), (4, 1, 1, 2))
        self.assertEqual(ref[("3", "3", "3")]["retire_year"], 2015)

    def test_reference_missing_column(self):
        info, ref = E.read_reference("A,B\n1,2\n")
        self.assertIn("CAMD_PLANT_ID", info["missing_cols"])
        self.assertEqual(ref, {})

    def test_read_facility(self):
        info, recs = fac(2024, [("3", "1", "Operating", "1954-02-12", "1 (153.1)"),
                                ("3", "CT", "Operating", "2001-01-01", "G1 (80), G2 (80)"),
                                ("3", "X", "Operating", "2001-01-01", "")])
        self.assertEqual((info["rows"], info["keys"], info["missing_cols"]), (3, 4, []))
        self.assertIn(("3", "CT", "G2"), recs)
        self.assertIn(("3", "X", ""), recs)
        self.assertEqual(recs[("3", "1", "1")]["capacity"], 153.1)

    def test_facility_missing_column(self):
        info, recs = E.read_facility('"Facility ID","Unit ID"\n"3","1"\n', 2024)
        self.assertIn("operating_status", info["missing_cols"])
        self.assertEqual(recs, {})


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.files = {
            2010: fac(2010, [("1", "A", "Operating", "1970-01-01", "A (10)"),
                             ("1", "B", "Operating (Retired 06/01/2010)", "1970-01-01", "B (10)"),
                             ("2", "C", "Operating", "1960-01-01", "C (5)")])[1],
            2011: fac(2011, [("1", "A", "Operating", "1970-01-01", "A (10)"),
                             ("1", "B", "Retired", "1970-01-01", "B (10)")])[1],
            2012: fac(2012, [("1", "A", "Operating", "1970-01-01", "A (10)"),
                             ("3", "D", "Future", "", "D (1)"),
                             ("4", "E", "Retired", "1950-01-01", "E (1)")])[1],
        }

    def test_history_and_derive(self):
        hist = E.build_history(self.files)
        self.assertEqual(hist[("1", "A", "A")]["years"], [2010, 2011, 2012])
        d = E.derive(hist[("1", "B", "B")])
        self.assertEqual((d["latest_class"], d["retire_year"], d["latest_year"]), ("RET", 2010, 2011))
        self.assertEqual(E.derive(hist[("4", "E", "E")])["retire_year"], 2012)
        self.assertEqual(E.derive(hist[("2", "C", "C")])["retire_year"], 0)

    def test_rule_f(self):
        hist = E.build_history(self.files)
        f = E.rule_f(hist)
        self.assertEqual(set(f), {("1", "A", "A"), ("1", "B", "B"), ("2", "C", "C"),
                                  ("4", "E", "E")})
        hist[("5", "F", "F")] = {"years": [2010],
                                 "by_year": {2010: {"status": "Operating (Retired 01/01/2009)"}}}
        self.assertNotIn(("5", "F", "F"), E.rule_f(hist))


class ScoreTests(unittest.TestCase):
    def test_score_and_gates(self):
        files = {2023: fac(2023, [("1", "A", "Operating", "1970-01-01", "A (10)"),
                                  ("1", "B", "Operating (Retired 06/01/2023)", "1970-01-01",
                                   "B (10)")])[1],
                 2024: fac(2024, [("1", "A", "Operating", "1970-01-02", "A (10)"),
                                  ("1", "N", "Operating", "2024-01-01", "N (1)")])[1]}
        ref = {("1", "A", "A"): {"status": "OPR", "status_date": "1970-01-01T00:00:00",
                                 "retire_year": 0},
               ("1", "B", "B"): {"status": "RET", "status_date": "2023-06-01T00:00:00",
                                 "retire_year": 2023},
               ("9", "Z", "Z"): {"status": "RET", "status_date": "2012-01-01T00:00:00",
                                 "retire_year": 2012}}
        m, s, hist, f = E.score(ref, files, last_year=2024)
        self.assertEqual((m["p1_keys_in_last_file"], m["p2_missing_from_last_file"],
                          m["p2_missing_ret_or_ltcs"], m["p3_keys_in_union"]), (1, 2, 2, 2))
        self.assertEqual((m["rule_f_keys"], m["p4_f_minus_ref"], m["p4_ref_minus_f"],
                          m["p4_symmetric_difference"]), (3, 1, 1, 2))
        self.assertEqual((m["p5_ref_ret_keys_in_union"], m["p5_retire_year_match"]), (1, 1))
        self.assertEqual(s, {"P1": False, "P2": True, "P3": False, "P4": False, "P5": True})
        rep = E.reported(ref, files, hist, f, last_year=2024)
        self.assertEqual(rep["opr_status_date_vs_commercial_operation_days"], {"1": 1})
        self.assertEqual(rep["ref_minus_f"], {"RET|not_in_files": 1})
        self.assertEqual(rep["f_minus_ref_by_latest_class"], {"OPR": 1})
        self.assertEqual(rep["ret_retire_year_diff"], {"0": 1})
        self.assertEqual(rep["unit_level"], {"ref_units": 3, "in_last_file": 1, "in_union": 2})

    def test_gates(self):
        infos = {y: {"rows": 5000, "missing_cols": []} for y in range(2010, 2025)}
        files = {2024: {("1", "A", "A"): {}}}
        ref = {("1", "A", "A"): {}, ("2", "B", "B"): {}}
        g, gm = E.gates({"rows": 7100, "missing_cols": []}, infos, files, ref)
        self.assertEqual(g, {"G1": True, "G2": True, "G3": True})
        self.assertEqual(gm["union_share"], 0.5)
        del infos[2015]
        g, _ = E.gates({"rows": 6900, "missing_cols": []}, infos, files, ref)
        self.assertEqual((g["G1"], g["G2"]), (False, False))


class ConstantTests(unittest.TestCase):
    def test_constants(self):
        self.assertEqual(E.VERSION, "0.1.0")
        self.assertEqual(E.REF_SHA, "e52a3a533f745b98b88f0556473fee0d4cbcf96d")
        self.assertEqual((E.FIRST_YEAR, E.SCORED_LAST, E.EXTRA_YEAR, E.EARLIEST_RET),
                         (2010, 2024, 2025, 2010))
        self.assertEqual((E.P1_MIN, E.P1_MAX, E.P2_MIN, E.P3_MIN, E.P4_MAX, E.P5_MIN),
                         (0.70, 0.85, 0.80, 0.97, 0.05, 0.90))


if __name__ == "__main__":
    unittest.main()
