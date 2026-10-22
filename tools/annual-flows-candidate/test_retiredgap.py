"""Tests for retiredgap.py on hand-built workbooks with one generator missing from the middle month.
MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import unittest

import pandas as pd

import retiredgap as rg

OP_HEAD = ["Plant ID", "Plant State", "Generator ID", "Nameplate Capacity (MW)", "Technology", "Status"]
RE_HEAD = ["Plant ID", "Plant State", "Generator ID", "Nameplate Capacity (MW)", "Technology",
           "Retirement Month", "Retirement Year"]
TITLE = ["EIA-860M generator inventory", None, None, None, None, None]


def raw(head, rows):
    width = len(head)
    title = (TITLE + [None] * width)[:width]
    note = ["NOTE: preliminary data"] + [None] * (width - 1)
    return pd.DataFrame([title, head] + [list(r) for r in rows] + [note], dtype=object)


def book(retired, canceled=()):
    sheets = {"Operating": raw(OP_HEAD, [(1, "CT", "A", 10.0, "Solar", "(OP) Operating"),
                                         ("00002", "NY", 1.0, 5.0, "Wind", "(OP) Operating")]),
              "Retired": raw(RE_HEAD, retired),
              "Canceled or Postponed": raw(OP_HEAD, canceled)}
    return [rg.book_sheet(n, r) for n, r in sheets.items()]


GT1 = (3, "TX", "GT1", 20.0, "Natural Gas Fired Combustion Turbine", 6, 2010)
COAL = ("4", "TX", "2", 7.5, "Conventional Steam Coal", 12, 2015)
NEW = (5, "OK", "1", 1.0, "Batteries", 1, 2024)


def sources():
    eia = {"2024-10": book([GT1, COAL]), "2024-11": book([GT1, COAL]), "2024-12": book([GT1, COAL, NEW])}
    arc = {"2024-10": book([GT1, COAL]),
           "2024-11": book([COAL], canceled=[(3, "TX", "GT1", 20.0, "Gas", "(CN) Canceled")]),
           "2024-12": book([GT1, COAL, NEW])}
    return {"archive": arc, "eia": eia}


class HelperTests(unittest.TestCase):
    def test_ids(self):
        self.assertEqual(rg.plain_id("00002"), "2")
        self.assertEqual(rg.plain_id(3.0), "3")
        self.assertIsNone(rg.plain_id(None))
        self.assertIsNone(rg.plain_id(float("nan")))
        self.assertEqual(rg.plain_id("NOTE: x"), "NOTE: x")
        self.assertEqual(rg.gen_id(1.0), "1")
        self.assertEqual(rg.gen_id(" GT1 "), "GT1")
        self.assertEqual(rg.gen_id(None), "")

    def test_member_for(self):
        names = ["eia860m-2024-1.xlsx", "x/eia860m-2024-11.xlsx", "eia860m-2024-110.xlsx", "notes.txt"]
        self.assertEqual(rg.member_for(names, "2024-11"), "x/eia860m-2024-11.xlsx")
        self.assertEqual(rg.member_for(["november_generator2024.xlsx"], "2024-11"), "november_generator2024.xlsx")
        self.assertIsNone(rg.member_for(names, "2024-12"))

    def test_urls_and_download(self):
        self.assertEqual(rg.eia_urls("2024-11")[0],
                         "https://www.eia.gov/electricity/data/eia860m/archive/xls/november_generator2024.xlsx")

        def fake(url):
            if url == "u1":
                raise OSError("refused")
            return b"<html>" if url == "u2" else b"PK\x03\x04rest"

        data, url, errors = rg.download(["u1", "u2", "u3"], get=fake)
        self.assertEqual((data, url, len(errors)), (b"PK\x03\x04rest", "u3", 2))
        self.assertEqual(rg.download(["u1"], get=fake)[:2], (None, None))

    def test_route(self):
        self.assertTrue(rg.route("Retired"))
        self.assertFalse(rg.route("Canceled or Postponed"))
        self.assertFalse(rg.route("Operating_PR"))


class BookTests(unittest.TestCase):
    def test_sheet(self):
        b = book([GT1, COAL])
        op, ret = b[0], b[1]
        self.assertEqual((op["header_row"], op["rows"], sorted(op["keys"])), (1, 2, ["1/A", "2/1"]))
        self.assertEqual((ret["rows"], sorted(ret["keys"])), (2, ["3/GT1", "4/2"]))
        self.assertEqual(ret["keys"]["3/GT1"]["retirement_year"], 2010)
        self.assertEqual(ret["keys"]["3/GT1"]["state"], "TX")
        self.assertIsNone(ret["keys"]["3/GT1"]["status"])
        self.assertEqual(op["keys"]["1/A"]["status"], "(OP) Operating")
        self.assertFalse(b[2]["route"])
        self.assertEqual(b[2]["rows"], 0)

    def test_report(self):
        res = rg.report(sources())
        a, e = res["gaps"]["archive"], res["gaps"]["eia"]
        self.assertEqual((a["keys"], a["left"], a["back"], a["back_keys"]), ([4, 3, 5], 1, 1, ["3/GT1"]))
        self.assertEqual(a["sheet_before"], [{"value": "Retired", "n": 1}])
        self.assertEqual(a["sheet_after"], [{"value": "Retired", "n": 1}])
        self.assertEqual(a["retirement_year"], [{"value": "2010", "n": 1}])
        self.assertEqual(a["state"], [{"value": "TX", "n": 1}])
        self.assertEqual(a["mw"], 20.0)
        self.assertEqual((e["keys"], e["left"], e["back"], e["mw"]), ([4, 4, 5], 0, 0, 0))
        self.assertEqual(res["archive_gap_in_eia_middle"], 1)

    def test_render(self):
        res = rg.report(sources())
        res.update(zip="z.zip", files=[{"month": "2024-11", "member": "eia860m-2024-11.xlsx", "archive_bytes": 9,
                                        "archive_md5": "a", "eia_url": "u", "eia_bytes": 8, "eia_md5": "b",
                                        "same_file": False, "errors": [],
                                        "sheets": {"archive": [{"sheet": "Retired", "rows": 1, "route": True},
                                                               {"sheet": "Canceled or Postponed", "rows": 1,
                                                                "route": False}]}}])
        md = rg.render(res)
        self.assertIn("| archive | 4 | 3 | 5 | 1 | 1 | 20.0 |", md)
        self.assertIn("| 2024-11 | archive | Retired 1; Canceled or Postponed 1 - |", md)
        self.assertIn("Of the archive's 1, listed in EIA's own 2024-11 file: 1.", md)
        self.assertIn("First 20 of archive's: 3/GT1", md)
        self.assertIn("Not run: x", rg.render({"error": "x"}))


if __name__ == "__main__":
    unittest.main()
