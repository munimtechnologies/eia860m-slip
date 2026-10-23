"""Tests for retiredentry.py on a hand-built changelog and workbook: one generator moves from Operating to
Retired, one is first listed on Retired, one leaves and comes back. MV2 of Munim, Inc. (made with AI agents).
Apache-2.0."""

import csv
import gzip
import io
import unittest

import pandas as pd

import retiredentry as ren

HEAD = ["Plant ID", "Plant Name", "Plant State", "Generator ID", "Nameplate Capacity (MW)", "Technology",
        "Retirement Month", "Retirement Year"]
RET = [(1517, "Maine Yankee", "ME", "1", 920.0, "Nuclear", 8, 1997),
       (None, "Saxton", "PA", "1", 3.0, "Nuclear", None, None),
       (77, "Piqua", "OH", "GT1", 10.0, "Natural Gas Fired Combustion Turbine", 1, 2010),
       (5, "Solar Farm", "CA", "PV1", 5.0, "Solar Photovoltaic", 2, 2020)]
OP_HEAD = ["Plant ID", "Plant Name", "Plant State", "Generator ID", "Nameplate Capacity (MW)", "Technology", "Status"]
OP = [(566, "Millstone", "CT", "2", 910.0, "Nuclear", "(OP) Operating")]


def raw(head, rows):
    return pd.DataFrame([["EIA-860M generator inventory"] + [None] * (len(head) - 1), head] + [list(r) for r in rows],
                        dtype=object)


def book():
    sheets = {"Operating": raw(OP_HEAD, OP), "Retired": raw(HEAD, RET)}
    b, scan = [], []
    for n, r in sheets.items():
        b.append(ren.rg.book_sheet(n, r))
        scan += ren.nuclear_rows(n, r)
    return b, scan


def row(month, key, event, sheet=""):
    return {"report_month": month, "key": key, "event": event, "sheet": sheet}


LOG = [row("2015-07", "1/A", "first", "Operating"), row("2026-07", "1/A", "changed", "Retired"),
       row("2026-09", "1/A", "left"), row("2026-08", "2/B", "first", "Retired"), row("2026-09", "2/B", "left"),
       row("2020-01", "3/C", "first", "Retired"), row("2020-05", "3/C", "left"),
       row("2020-06", "3/C", "back", "Retired"), row("2021-01", "3/C", "changed", "Retired"),
       row("2026-09", "3/C", "left"), row("2020-01", "9/Z", "first", "Operating")]
KEYS3 = ("1/A", "2/B", "3/C")


class HelperTests(unittest.TestCase):
    def test_constants(self):
        self.assertEqual(len(ren.KEYS), 16)
        self.assertEqual(len({k.split("/")[0] for k in ren.KEYS}), 15)
        self.assertTrue(all(y < 2002 for y in ren.AUG_YEARS.values()))
        self.assertIn(ren.SHA, ren.LOG_URL)
        self.assertEqual(len(ren.months()), 135)
        self.assertEqual(ren.months("2015-11", "2016-02"), ["2015-11", "2015-12", "2016-01", "2016-02"])

    def test_wait_plan(self):
        got = iter([b"404: Not Found", b"x\nStatus: pre-registered, not yet scored.\n"])
        self.assertTrue(ren.wait_plan(10, get=lambda u: next(got), sleep=lambda s: None, clock=lambda: 0))
        self.assertFalse(ren.wait_plan(10, get=lambda u: b"404", sleep=lambda s: None, clock=lambda: 100))

    def test_load_log(self):
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(["report_month", "key", "event", "sheet"])
        w.writerow(["2026-08", "2/B", "first", "Retired"])
        data = gzip.compress(buf.getvalue().encode("utf-8"))
        self.assertEqual(ren.load_log(data), [row("2026-08", "2/B", "first", "Retired")])


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.hist = ren.history(LOG, KEYS3)

    def test_history(self):
        self.assertEqual(sorted(self.hist), list(KEYS3))
        self.assertEqual([r["report_month"] for r in self.hist["1/A"]], ["2015-07", "2026-07", "2026-09"])

    def test_arrival(self):
        self.assertEqual(ren.arrival(self.hist["1/A"]), {"month": "2026-07", "event": "changed", "from": "Operating"})
        self.assertEqual(ren.arrival(self.hist["2/B"]), {"month": "2026-08", "event": "first", "from": "never listed"})
        self.assertEqual(ren.arrival(self.hist["3/C"]), {"month": "2020-01", "event": "first", "from": "never listed"})
        self.assertIsNone(ren.arrival([row("2020-01", "9/Z", "first", "Operating")]))
        self.assertEqual(ren.arrival([row("2020-01", "4/D", "first", "Operating"), row("2020-02", "4/D", "left"),
                                      row("2021-01", "4/D", "back", "Retired")])["from"], "no sheet")

    def test_after_arrival(self):
        a = ren.arrival(self.hist["1/A"])
        self.assertEqual(ren.after_arrival(self.hist["1/A"], a), [])
        c = ren.after_arrival(self.hist["3/C"], ren.arrival(self.hist["3/C"]))
        self.assertEqual([(r["report_month"], r["event"]) for r in c], [("2020-05", "left"), ("2020-06", "back")])
        self.assertEqual(ren.after_arrival([], None), [])
        self.assertTrue(all(ren.left_in(self.hist[k]) for k in KEYS3))
        self.assertFalse(ren.left_in(self.hist["1/A"], "2026-08"))

    def test_state(self):
        rows = self.hist["1/A"]
        self.assertEqual([ren.state(rows, m) for m in ("2015-06", "2026-06", "2026-07", "2026-09")],
                         [None, "Operating", "Retired", None])
        self.assertEqual(ren.present(self.hist, "2026-08"), 3)
        self.assertEqual(ren.present(self.hist, "2026-07"), 2)
        self.assertEqual(ren.present(self.hist, "2020-05"), 0)
        self.assertEqual(ren.runs([("a", 1), ("b", 1), ("c", 2)]), [["a", "b", 1], ["c", "c", 2]])


class BookTests(unittest.TestCase):
    def setUp(self):
        self.book, self.scan = book()

    def test_nuclear_rows(self):
        self.assertEqual([(r["sheet"], r["plant_name"]) for r in self.scan],
                         [("Operating", "Millstone"), ("Retired", "Maine Yankee"), ("Retired", "Saxton"),
                          ("Retired", "Piqua")])
        self.assertEqual(self.scan[1], {"sheet": "Retired", "plant_id": "1517", "plant_name": "Maine Yankee",
                                        "generator_id": "1", "technology": "Nuclear", "retirement_year": 1997,
                                        "nameplate_mw": 920})
        self.assertEqual((self.scan[2]["plant_id"], self.scan[2]["retirement_year"]), (None, None))
        self.assertEqual([r["plant_name"] for r in ren.old_nuclear(self.scan)], ["Maine Yankee", "Saxton"])

    def test_entry(self):
        e = ren.entry(self.book, "1517/1")
        self.assertEqual(e, {"on_retired": True, "where": "Retired", "retirement_year": 1997, "retirement_month": 8,
                             "technology": "Nuclear", "nameplate_mw": 920})
        self.assertEqual(ren.entry(self.book, "566/2"), {"on_retired": False, "where": "Operating"})
        self.assertEqual(ren.entry(self.book, "9/9"), {"on_retired": False, "where": "not listed"})
        s = ren.sheet_summary(self.book)
        self.assertEqual((s["retired"], s["before"]), (3, ["1517/1"]))
        self.assertEqual(s["bins"], [{"value": "2002 or later", "n": 2}, {"value": "before 2002", "n": 1}])

    def test_score(self):
        hist = ren.history(LOG, KEYS3)
        arr = {k: ren.arrival(hist[k]) for k in ("1/A", "2/B")}
        years = {"1/A": 1990, "2/B": 1980}
        scan = [{"sheet": "Retired", "technology": "Nuclear", "retirement_year": 1990},
                {"sheet": "Retired", "technology": "Nuclear", "retirement_year": 1980},
                {"sheet": "Operating", "technology": "Nuclear", "retirement_year": None},
                {"sheet": "Retired", "technology": "Nuclear", "retirement_year": 2013}]
        p = ren.score(arr, {"1/A": {"retirement_year": 1990}, "2/B": {"retirement_year": 1981}},
                      {"1/A": [], "2/B": []}, scan, years)
        self.assertEqual([(x["id"], x["outcome"]) for x in p],
                         [("R1", "failed"), ("R2", "failed"), ("R3", "held"), ("R4", "held")])
        self.assertEqual(p[0]["value"], "2 of 2 reach it; month(s): 2026-07, 2026-08")
        self.assertEqual((p[1]["value"], p[2]["value"], p[3]["value"]),
                         ("1 of 2", "2 of 2 on it every month from arrival to 2026-08", "2 rows"))
        p = ren.score(arr, {"1/A": None, "2/B": {}}, {"1/A": [], "2/B": [LOG[0]]}, None, years)
        self.assertEqual([(x["id"], x["outcome"]) for x in p],
                         [("R1", "failed"), ("R2", "not scored"), ("R3", "failed"), ("R4", "not scored")])
        one = {k: {"month": "2026-08", "event": "first", "from": "never listed"} for k in years}
        self.assertEqual(ren.score(one, {k: {"retirement_year": y} for k, y in years.items()}, {}, [], years)[0]
                         ["outcome"], "held")

    def test_render(self):
        res = {"log": {"url": "u", "bytes": 9, "md5": "m", "rows": 3, "first": "2015-07", "last": "2026-09"},
               "files": [{"month": "2026-09", "source": "s", "bytes": 1, "md5": "a", "errors": [],
                          "same_as_monthcheck": True}],
               "predictions": [{"id": "R1", "outcome": "held", "value": "v", "bar": "b"},
                               {"id": "R4", "outcome": "not scored", "value": "v", "bar": "b"}],
               "keys": [{"key": "1517/1", "arrival": {"month": "2026-08", "event": "first", "from": "never listed"},
                         "entry": ren.entry(self.book, "1517/1"), "where_before": "not listed", "other_rows": [],
                         "left_sep": True}],
               "runs": [["2015-07", "2026-07", 0], ["2026-08", "2026-08", 1], ["2026-09", "2026-09", 0]],
               "sheets": {"2026-08": ren.sheet_summary(self.book)}, "scans": {"2026-08": self.scan}}
        md = ren.render(res)
        self.assertIn("Changelog: u (9 bytes, md5 m; 3 rows, 2015-07 to 2026-09). Expected 1054060 bytes and "
                      "117756 rows: False.", md)
        self.assertIn("| 2026-09 | s | 1 | a | none |", md)
        self.assertIn("September file is the one monthcheck-sep2026-v1 read (14013970 bytes, md5 "
                      "4c741eb77a5ccad5aca32ffe43f398af): True.", md)
        self.assertIn("Held: 1 of 1 scored.", md)
        self.assertIn("| 1517/1 | 2026-08 | first | never listed | 1997 | 1997 | Nuclear | 920 | not listed | none "
                      "| True |", md)
        self.assertIn("| 2026-08 | 2026-08 | 1 |", md)
        self.assertIn("| 2026-08 | 3 | 2002 or later 2; before 2002 1 | 1 | none |", md)
        self.assertIn("| 2026-08 | Retired 2; Operating 1 | 2 |", md)
        self.assertIn("| Retired | - | Saxton | 1 | - | 3 |", md)
        self.assertIn("Rows whose plant name has shippingport or vallecitos or saxton or piqua: Retired Saxton -/1 "
                      "Nuclear -; Retired Piqua 77/GT1 Natural Gas Fired Combustion Turbine 2010.", md)
        self.assertIn("Not run: x", ren.render({"error": "x"}))


if __name__ == "__main__":
    unittest.main()
