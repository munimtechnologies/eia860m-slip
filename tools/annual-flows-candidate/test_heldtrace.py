"""Unit tests for heldtrace.py. MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import unittest

import pandas as pd

import heldtrace as ht
import history as hs
import watchlist as wl

M = wl.parse_month
NAN = float("nan")


def frame(rows):
    return pd.DataFrame(rows, columns=["key", "sheet", "status", "planned_m", "capacity_mw"])


def pudl(rows):
    df = pd.DataFrame(rows, columns=["report_date", "valid_until_date", "plant_id_eia",
                                     "generator_id", "capacity_mw",
                                     "current_planned_generator_operating_date",
                                     "operational_status_code"])
    return hs.prepare(df)


class AtMonthTests(unittest.TestCase):
    def test_at_month(self):
        h = [(10, "A"), (12, None), (13, "B")]
        self.assertEqual([ht.at_month(h, r) for r in (9, 10, 11, 12, 13, 14)],
                         [None, "A", "A", None, "B", "B"])
        self.assertIsNone(ht.at_month([], 10))

    def test_where_of(self):
        h = [(10, ("OP", None, 10.0)), (11, ("OA", None, 10.0))]
        self.assertEqual(ht.where_of(h, (("OA", None, 10.0), 11)), "same")
        self.assertEqual(ht.where_of(h, (("OA", None, 10.0), 10)), "differs")
        self.assertEqual(ht.where_of(h, (("OA", None, 10.0), 9)), "absent")


class TraceTests(unittest.TestCase):
    def setUp(self):
        self.df = pudl([
            # 5/E: OP 10, then OA; the workbook's OP of January has no MW
            ("2016-01-01", "2016-02-01", 5, "E", 10.0, None, "OP"),
            ("2016-02-01", "2016-04-01", 5, "E", 10.0, None, "OA"),
            # 6/F: as 5/E, but PUDL's January record has no MW either
            ("2016-01-01", "2016-02-01", 6, "F", NAN, None, "OP"),
            ("2016-02-01", "2016-04-01", 6, "F", 10.0, None, "OA"),
            # 7/G: PUDL says OS from the start, the workbook OP
            ("2016-01-01", "2016-04-01", 7, "G", 10.0, None, "OS"),
            # 8/H: in no workbook; its March report makes PUDL's data run to March, since
            # records in force end at PUDL's latest report (eia860m_slip.listed_until)
            ("2016-03-01", "2016-04-01", 8, "H", 1.0, None, "OP")])
        self.frames = [
            ("2016-01", frame([["5/E", "Operating", "OP", None, NAN],
                               ["6/F", "Operating", "OP", None, NAN],
                               ["7/G", "Operating", "OP", None, 10.0]])),
            ("2016-02", frame([["5/E", "Operating", "OA", None, 10.0],
                               ["6/F", "Operating", "OA", None, 10.0],
                               ["7/G", "Operating", "OP", None, 10.0]])),
            ("2016-03", frame([["5/E", "Operating", "OP", None, 10.0],
                               ["6/F", "Operating", "OP", None, 10.0]]))]

    def test_counts_equal_replay(self):
        res = ht.trace(self.df, iter(self.frames))
        self.assertEqual(res["kinds"], [{"year": 2016, "predicted": 0, "pudl_later": 0,
                                         "held_before": 2, "other": 2}])
        y = hs.replay(self.df, iter(self.frames))["years"][2016]
        self.assertEqual((y["hits"], y["pudl_later"], y["held_before"], y["other"]), (0, 0, 2, 2))

    def test_where_held_plants_events(self):
        res = ht.trace(self.df, iter(self.frames))
        self.assertEqual(res["where"], [
            {"year": 2016, "kind": "held_before", "at": "same", "n": 2},
            {"year": 2016, "kind": "other", "at": "differs", "n": 2}])
        self.assertEqual(res["held"], [
            {"year": 2016, "simulated": "equals workbook", "strict": False, "at": "same", "n": 1},
            {"year": 2016, "simulated": "equals workbook", "strict": True, "at": "same", "n": 1}])
        self.assertEqual(res["plants"], [{"plant": "5", "n": 1}, {"plant": "6", "n": 1}])
        self.assertEqual(res["events"], [
            {"month": "2016-01", "first": 3, "changed": 0, "left": 0, "back": 0},
            {"month": "2016-02", "first": 0, "changed": 2, "left": 0, "back": 0},
            {"month": "2016-03", "first": 0, "changed": 2, "left": 1, "back": 0}])
        self.assertEqual(res["keys"], {})

    def test_key_rows(self):
        res = ht.trace(self.df, iter(self.frames), ("7/G", "9/Z"))
        self.assertEqual(res["keys"]["9/Z"], [])
        rows = res["keys"]["7/G"]
        self.assertEqual([(r["month"], r["result"], r["seen_before"]) for r in rows], [
            ("2016-01", "other", False), ("2016-02", "other", True),
            ("2016-03", "left the workbook", False)])
        self.assertEqual(rows[0], {"month": "2016-01", "sheet": "Operating",
                                   "workbook": "OP, -, 10.0 MW", "simulated": "OP, -, 10.0 MW",
                                   "seen_before": False, "pudl": "OS, -, 10.0 MW",
                                   "pudl_reported": "2016-01", "result": "other"})

    def test_render(self):
        res = ht.trace(self.df, iter(self.frames), ("7/G", "9/Z"))
        md = ht.render({"pudl": {"bytes": 1, "mtime": "x", "max_report": "2016-03"},
                        "months_read": 3, "result": res})
        self.assertIn("| 2016 | 0 | 0 | 2 | 2 |", md)
        self.assertIn("| 2016 | held_before | same | 2 |", md)
        self.assertIn("| 2016 | equals workbook | False | same | 1 |", md)
        self.assertIn("| 6 | 1 |", md)
        self.assertIn("| 2016-03 | 0 | 2 | 1 | 0 |", md)
        self.assertIn("| 2016-02 | Operating | OP, -, 10.0 MW | OP, -, 10.0 MW | True | "
                      "OS, -, 10.0 MW | 2016-01 | other |", md)
        self.assertIn("| not in any workbook | | | | | | | |", md)
        self.assertIn("Not run: x", ht.render({"error": "x"}))


if __name__ == "__main__":
    unittest.main()
