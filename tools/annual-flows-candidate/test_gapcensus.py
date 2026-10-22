"""Tests for gapcensus.py on hand-built months: two retired generators leave, one comes back the
next month and one 14 months later, a planned one moves to Operating, an operating one leaves.
MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import unittest

import pandas as pd

import gapcensus as gc
import history as hs

OP, OP12, RE = ("OP", None, 10.0), ("OP", None, 12.0), ("RE", None, 5.0)
P, P_OP = ("P", 24300, 1.0), ("OP", None, 1.0)
SH = {"1/A": "Operating", "2/B": "Retired", "3/C": "Retired", "4/D": "Planned"}


def months():
    """(month, wm, sheets) for six months."""
    sh2 = dict(SH, **{"4/D": "Operating"})
    return [("2024-09", {"1/A": OP, "2/B": RE, "3/C": RE, "4/D": P}, SH),
            ("2024-10", {"1/A": OP12, "2/B": RE, "3/C": RE, "4/D": P}, SH),
            ("2024-11", {"1/A": OP12, "4/D": P}, SH),
            ("2024-12", {"1/A": OP12, "2/B": RE, "4/D": P_OP}, sh2),
            ("2026-01", {"1/A": OP12, "2/B": RE, "3/C": RE, "4/D": P_OP}, sh2),
            ("2026-02", {"2/B": RE, "3/C": RE, "4/D": P_OP}, sh2)]


def run():
    c = gc.Census()
    out = [c.feed(m, wm, {k: sh[k] for k in wm}) for m, wm, sh in months()]
    return c, out


class HelperTests(unittest.TestCase):
    def test_months(self):
        self.assertEqual(gc.next_month("2026-08"), "2026-09")
        self.assertEqual(gc.next_month("2026-12"), "2027-01")
        self.assertEqual(gc.m_index("2026-01") - gc.m_index("2024-11"), 14)

    def test_sheet_group_and_outcome(self):
        self.assertEqual(gc.sheet_group("Retired"), "Retired")
        self.assertEqual(gc.sheet_group("Planned "), "Planned")
        self.assertEqual(gc.sheet_group("Canceled or Postponed"), "other")
        self.assertEqual(gc.sheet_group(None), "other")
        self.assertEqual([gc.outcome(g) for g in (None, 1, 2, 12, 13)],
                         ["not_back", "back_1", "back_2_12", "back_2_12", "back_13_plus"])

    def test_eia_plan(self):
        got = ["2026-07", "2026-08"]
        self.assertEqual(gc.eia_plan("2026-08", got), "compare")
        self.assertEqual(gc.eia_plan("2026-09", got), "append")
        self.assertEqual(gc.eia_plan("2026-11", got), "skip")
        self.assertEqual(gc.eia_plan("2026-09", []), "skip")

    def test_compare_text(self):
        a = "h\r\nx\r\n"
        self.assertEqual(gc.compare_text(a, a)["same"], True)
        self.assertIsNone(gc.compare_text(a, a)["first_difference"])
        d = gc.compare_text(a, "h\r\ny\r\n")
        self.assertEqual((d["same"], d["first_difference"], d["published_line"], d["rebuilt_line"]),
                         (False, 2, "x", "y"))
        d = gc.compare_text(a, a + "z\r\n")
        self.assertEqual((d["first_difference"], d["lines_published"], d["lines_rebuilt"],
                          d["published_line"], d["rebuilt_line"]), (3, 2, 3, None, "z"))

    def test_log_text(self):
        text = gc.log_text([hs.log_row("2024-11", "2/B", "left", None),
                            hs.log_row("2024-12", "2/B", "back", ("Retired", "RE", None, 5.0))])
        self.assertEqual(text, "report_month,key,plant_id_eia,generator_id,event,sheet,status,"
                               "planned_month,nameplate_mw\r\n2024-11,2/B,2,B,left,,,,\r\n"
                               "2024-12,2/B,2,B,back,Retired,RE,,5.0\r\n")


class CensusTests(unittest.TestCase):
    def test_events(self):
        c, out = run()
        self.assertEqual([e for _, e, _ in out[0]], ["first"] * 4)
        self.assertEqual(out[1], [("1/A", "changed", ("Operating", "OP", None, 12.0))])
        self.assertEqual(out[2], [("2/B", "left", None), ("3/C", "left", None)])
        self.assertEqual(out[3], [("2/B", "back", ("Retired", "RE", None, 5.0)),
                                  ("4/D", "changed", ("Operating", "OP", None, 1.0))])
        self.assertEqual(out[4], [("3/C", "back", ("Retired", "RE", None, 5.0))])
        self.assertEqual(out[5], [("1/A", "left", None)])
        self.assertEqual(c.months, [m for m, _, _ in months()])

    def test_lefts(self):
        c, _ = run()
        self.assertEqual(c.lefts, [["2024-11", "2/B", "Retired", "2024-12"],
                                   ["2024-11", "3/C", "Retired", "2026-01"],
                                   ["2026-02", "1/A", "Operating", None]])
        self.assertEqual([c.gap(e) for e in c.lefts], [1, 14, None])
        self.assertEqual(c.one_month(), [("2024-11", "2/B", "Retired")])

    def test_outcomes(self):
        c, _ = run()
        rows = c.outcomes()
        self.assertEqual(rows, [
            {"year": "2024", "sheet": "Retired", "left": 2, "back_1": 1, "back_2_12": 0,
             "back_13_plus": 1, "not_back": 0},
            {"year": "2026", "sheet": "Operating", "left": 1, "back_1": 0, "back_2_12": 0,
             "back_13_plus": 0, "not_back": 1}])
        self.assertEqual([(r["sheet"], r["left"], r["not_back"]) for r in gc.by_sheet(rows)],
                         [("Operating", 1, 1), ("Retired", 2, 0)])


class PudlTests(unittest.TestCase):
    def test_status(self):
        df = pd.DataFrame({"plant_id_eia": [2, 2, 3, 5], "generator_id": ["B", "B", "C", "E"],
                           "report_date": ["2020-01-01", "2024-12-01", "2024-01-01", "2024-01-01"],
                           "valid_until_date": ["2024-12-01", None, "2024-11-01", None]})
        got = gc.pudl_status(df, [("2/B", "2024-11"), ("3/C", "2024-11"), ("9/Z", "2024-11"),
                                  ("2/B", "2019-06"), ("5/E", "2024-11")])
        self.assertEqual(got, {("2/B", "2024-11"): "in force", ("3/C", "2024-11"): "closed",
                               ("9/Z", "2024-11"): "none", ("2/B", "2019-06"): "none",
                               ("5/E", "2024-11"): "in force"})

    def test_gap_months(self):
        pairs = [("2024-11", "2/B", "Retired"), ("2024-11", "7/G", "Planned"), ("2021-08", "8/H", "Operating")]
        pudl = {("2/B", "2024-11"): "in force", ("7/G", "2024-11"): "closed"}
        self.assertEqual(gc.gap_months(pairs, pudl), [
            {"month": "2021-08", "n": 1, "pudl_in_force": 0, "Operating": 1, "Planned": 0, "Retired": 0, "other": 0},
            {"month": "2024-11", "n": 2, "pudl_in_force": 1, "Operating": 0, "Planned": 1, "Retired": 1, "other": 0}])


class NovTests(unittest.TestCase):
    def test_nov_sheets(self):
        book = [{"sheet": "Operating", "keys": {"1/A": {}}},
                {"sheet": "Canceled or Postponed", "keys": {"4/D": {}, "1/A": {}}}]
        got = gc.nov_sheets(book, ["1/A", "4/D", "2/B", "3/C"])
        self.assertEqual(got, {"Operating+Canceled or Postponed": 1, "Canceled or Postponed": 1,
                               "not listed": 2})

    def test_render(self):
        c, _ = run()
        out = c.outcomes()
        res = {"outcomes": out, "by_sheet": gc.by_sheet(out), "gap_months": gc.gap_months(c.one_month()),
               "pudl_counts": {}}
        md = gc.render({"months": c.months, "months_unreadable": [], "result": res, "log_rows": 9,
                        "log_file": "x.csv.gz", "published": {"error": "offline"}})
        self.assertIn("| Retired | 2 | 1 | 0 | 1 | 0 |", md)
        self.assertIn("| 2024-11 | 1 | 0 | 0 | 1 | 0 | 0 |", md)
        self.assertIn("Not compared: offline", md)
        self.assertIn("PUDL status of all one-month gaps: none.", md)
        self.assertIn("Not run: x", gc.render({"error": "x"}))


if __name__ == "__main__":
    unittest.main()
