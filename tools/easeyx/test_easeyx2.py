"""Unit tests for easeyx2.py on made-up rows (standard library only; reads no outside data).

Apache-2.0. MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import easeyx as E  # noqa: E402
import easeyx2 as X  # noqa: E402

HEADER = ('"State","Facility Name","Facility ID","Unit ID","Year","Operating Status",'
          '"Commercial Operation Date","Primary Fuel Type","Latitude","Longitude",'
          '"Associated Generators & Nameplate Capacity (MWe)"\n')

REF_HEAD = ("SEQUENCE_NUMBER,CAMD_STATE,CAMD_FACILITY_NAME,CAMD_PLANT_ID,CAMD_UNIT_ID,"
            "CAMD_GENERATOR_ID,CAMD_NAMEPLATE_CAPACITY,CAMD_FUEL_TYPE,CAMD_LATITUDE,"
            "CAMD_LONGITUDE,CAMD_STATUS,CAMD_STATUS_DATE,CAMD_RETIRE_YEAR\n")


def fac(year, rows):
    lines = [HEADER]
    for state, name, plant, unit, status, fuel, lat, lon, gens in rows:
        lines.append('"%s","%s","%s","%s","%d","%s","","%s","%s","%s","%s"\n'
                     % (state, name, plant, unit, year, status, fuel, lat, lon, gens))
    return E.read_facility("".join(lines), year)[1]


def made_up():
    files = {
        2022: fac(2022, [("AL", "Barry", "1", "A", "Operating", "Coal", "31.0069", "-88.0103",
                          "A (100)"),
                         ("AL", "Barry", "1", "B", "Operating", "Coal", "31.0069", "-88.0103",
                          "B (50)"),
                         ("AL", "Gorgas", "2", "C", "Operating", "Pipeline Natural Gas", "33.0",
                          "-87.0", "C (10)")]),
        2023: fac(2023, [("AL", "Barry", "1", "A", "Operating", "Coal", "31.0069", "-88.0103",
                          "A (100.04)"),
                         ("AL", "Gorgas  Plant", "2", "C", "Operating", "Coal", "33.01", "-87.0",
                          "C (12)")]),
        2024: fac(2024, [("AL", "barry ", "1", "A", "Operating", "Coal", "31.0070", "-88.0103",
                          "A (100.04)")]),
    }
    ref_text = REF_HEAD + (
        "1,AL,Barry,1,A,A,100,Coal,31.0069,-88.0103,OPR,1954-02-11T00:00:00,0\n"
        "2,AL,Barry,1,B,B,50,,31.0069,-88.0103,RET,2023-03-01T00:00:00,2023\n"
        "3,AL,Gorgas,2,C,C,10,Pipeline Natural Gas,33.0,-87.0,RET,2023-12-31T00:00:00,2023\n"
        "4,AL,Barry,1,A,A,999,Oil,0,0,OPR,1954-02-11T00:00:00,0\n"
        "5,TX,Zed,9,Z,Z,5,Coal,30,-97,RET,2012-01-01T00:00:00,2012\n")
    info, ref = X.read_reference_attrs(ref_text)
    return files, info, ref, E.build_history(files)


class HelperTests(unittest.TestCase):
    def test_fnum_and_norm(self):
        self.assertEqual(X.fnum(" 153.1 "), 153.1)
        self.assertEqual(X.fnum(12), 12.0)
        self.assertIsNone(X.fnum(""))
        self.assertIsNone(X.fnum(None))
        self.assertIsNone(X.fnum("x"))
        self.assertEqual(X.norm_text("  Gorgas   Plant "), "gorgas plant")
        self.assertEqual(X.norm_text(None), "")

    def test_compare(self):
        r = {"state": "AL", "facility_name": "Barry", "capacity": "100", "fuel": "Coal",
             "latitude": "31.0069", "longitude": "-88.0103"}
        f = {"state": "al", "facility_name": " barry", "capacity": 100.05, "fuel": "COAL",
             "latitude": "31.0079", "longitude": "-88.0103"}
        for a in X.ATTRS:
            self.assertIs(X.compare(a, r, f), True, a)
        f2 = dict(f, capacity=100.06, latitude="31.0080", fuel="Coal, Pipeline Natural Gas")
        self.assertIs(X.compare("capacity", r, f2), False)
        self.assertIs(X.compare("coords", r, f2), False)
        self.assertIs(X.compare("fuel", r, f2), False)
        self.assertIsNone(X.compare("fuel", dict(r, fuel=""), f))
        self.assertIsNone(X.compare("capacity", r, dict(f, capacity=None)))
        self.assertIsNone(X.compare("coords", r, dict(f, longitude="")))
        self.assertIsNone(X.compare("state", dict(r, state=" "), f))
        with self.assertRaises(ValueError):
            X.compare("colour", r, f)
        self.assertEqual(X.show("coords", r), "31.0069;-88.0103")
        self.assertEqual(X.show("capacity", {"capacity": None}), "")

    def test_diff_tag(self):
        self.assertEqual([X.diff_tag(d) for d in (-3, -1, 0, 1, 2, 3)],
                         ["<-1", "-1", "0", "+1", "+2", ">+2"])


class ReadTests(unittest.TestCase):
    def test_read_reference_attrs(self):
        _, info, ref, _ = made_up()
        self.assertEqual((info["rows"], info["keys"], info["missing_cols"]), (5, 4, []))
        self.assertEqual(ref[("1", "A", "A")]["capacity"], "100")
        self.assertEqual(ref[("1", "B", "B")]["fuel"], "")
        self.assertEqual(ref[("2", "C", "C")]["retire_year"], 2023)

    def test_missing_column(self):
        info, ref = X.read_reference_attrs("CAMD_PLANT_ID,CAMD_UNIT_ID\n1,A\n")
        self.assertIn("CAMD_FUEL_TYPE", info["missing_cols"])
        self.assertEqual((ref, info["keys"]), ({}, 0))


class ScoreTests(unittest.TestCase):
    def test_compare_all(self):
        _, _, ref, hist = made_up()
        counts, by_status, pairs, rows = X.compare_all(ref, hist)
        self.assertEqual(dict(counts["state"]), {"match": 3})
        self.assertEqual(dict(counts["facility_name"]),
                         {"match": 2, "differ": 1, "differ_other_year_matches": 1})
        self.assertEqual(dict(counts["capacity"]),
                         {"match": 2, "differ": 1, "differ_other_year_matches": 1})
        self.assertEqual(dict(counts["fuel"]),
                         {"match": 1, "differ": 1, "na": 1, "differ_other_year_matches": 1})
        self.assertEqual(dict(counts["coords"]),
                         {"match": 2, "differ": 1, "differ_other_year_matches": 1})
        self.assertEqual(dict(pairs), {"Pipeline Natural Gas -> Coal": 1})
        self.assertEqual(by_status["fuel"]["RET_LTCS|na"], 1)
        self.assertEqual(by_status["fuel"]["OPR|match"], 1)
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[0][:5], ["2", "C", "C", "RET", "facility_name"])
        self.assertEqual(rows[0][7:], [2023, "2022"])

    def test_silent_and_score(self):
        _, _, ref, hist = made_up()
        silent = X.silent_ret(ref, hist)
        self.assertEqual([s["key"] for s in silent], [("1", "B", "B"), ("2", "C", "C")])
        self.assertEqual([s["last_year"] for s in silent], [2022, 2023])
        m, scores, rep, rows, silent2 = X.score(ref, hist)
        self.assertEqual(m["keys_compared"], 3)
        self.assertEqual(m["state"]["share"], 1.0)
        self.assertEqual(m["capacity"]["share"], round(2 / 3, 5))
        self.assertEqual(m["fuel"]["share"], 0.5)
        self.assertEqual((m["silent"]["keys"], m["silent"]["dated"],
                          m["silent"]["ref_year_is_last_or_next"], m["silent"]["ref_year_is_last"],
                          m["silent"]["ref_year_is_next"]), (2, 2, 2, 1, 1))
        self.assertEqual(m["silent"]["ref_minus_last"], {"+1": 1, "0": 1})
        self.assertEqual(m["silent"]["by_last_year"], {"2022": 1, "2023": 1})
        self.assertEqual(m["silent"]["by_latest_class"], {"OPR": 2})
        self.assertEqual(scores, {"P1": True, "P2": False, "P3": False, "P4": False,
                                  "P5": False, "P6": True})
        self.assertEqual(rep["retire_year_rules"],
                         {"ref_ret_keys_dated": 2, "derived_only": 0,
                          "derived_else_last_year": 1, "derived_else_last_year_plus_1": 1})

    def test_gates(self):
        _, _, ref, hist = made_up()
        infos = {y: {"rows": 4000, "missing_cols": []} for y in range(2010, 2025)}
        g, gm = X.gates({"rows": 7100, "missing_cols": []}, infos, ref, hist)
        self.assertEqual(g, {"G1": True, "G2": True, "G3": False})
        self.assertEqual((gm["found"], gm["silent"]), (3, 2))
        g, _ = X.gates({"rows": 7100, "missing_cols": []}, infos, ref, hist, found_min=3,
                       silent_range=(2, 2))
        self.assertEqual(g, {"G1": True, "G2": True, "G3": True})
        del infos[2016]
        g, _ = X.gates({"rows": 6999, "missing_cols": []}, infos, ref, hist)
        self.assertEqual((g["G1"], g["G2"]), (False, False))


class ConstantTests(unittest.TestCase):
    def test_constants(self):
        self.assertEqual(X.VERSION, "0.1.0")
        self.assertEqual(E.VERSION, "0.1.0")
        self.assertEqual((X.FIRST_YEAR, X.LAST_YEAR), (2010, 2024))
        self.assertEqual(sorted(X.EASEYX1_MD5), list(range(2010, 2025)))
        self.assertEqual((X.CAP_TOL, X.COORD_TOL), (0.05, 0.001))
        self.assertEqual((X.P1_MIN, X.P2_MIN, X.P3_MIN, X.P4_MIN, X.P5_MIN, X.P6_MIN),
                         (0.99, 0.90, 0.90, 0.90, 0.90, 0.85))
        self.assertEqual((X.G3_MIN_FOUND, X.G3_SILENT_MIN, X.G3_SILENT_MAX), (6900, 300, 500))


if __name__ == "__main__":
    unittest.main()
