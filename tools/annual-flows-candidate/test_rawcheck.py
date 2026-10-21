"""Unit tests for rawcheck (no network; every expected value is traced in the comments).

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.
"""

import io
import json
import os
import tempfile
import unittest
import zipfile

import pandas as pd

import rawcheck as rc

NAN = float("nan")


def recs(rows):
    # Frames as rawcheck.frame returns them: workbook.py records indexed by key.
    return pd.DataFrame(rows, columns=["key", "sheet", "status", "planned_m",
                                       "capacity_mw"]).set_index("key")


def xlsx_bytes(sheets):
    """An xlsx file in memory with one sheet per (name, rows), rows written without a header."""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        for name, rows in sheets:
            pd.DataFrame(rows).to_excel(w, sheet_name=name, header=False, index=False)
    return buf.getvalue()


class Names(unittest.TestCase):
    def test_zip_key(self):
        self.assertEqual(rc.zip_key("2026-08"), "eia860m-2026.zip")

    def test_pick_copies(self):
        hist = {"k": [{"first_date": "2026-08-27", "first_id": "1"},
                      {"first_date": "2026-09-27", "first_id": "2"},
                      {"first_date": "2026-10-05", "first_id": "3"}]}
        pick = lambda since, limit=3: [h["first_id"] for h in rc.pick_copies(hist, "k", since, limit)]
        self.assertEqual(pick("2026-09-24"), ["2", "3"])        # 1 is before the date
        self.assertEqual(pick("2026-09-24", limit=1), ["3"])    # the newest one
        self.assertEqual(pick("2026-11-01"), ["3"])             # none that recent: newest alone
        self.assertEqual(rc.pick_copies(hist, "missing", "2026-09-24"), [])

    def test_member_for(self):
        names = ["eia860m-2026/august_generator2026.xlsx", "july_generator2026.xlsx",
                 "datapackage.json", "august_notes2026.txt"]
        self.assertEqual(rc.member_for(names, "2026-08"),
                         ("eia860m-2026/august_generator2026.xlsx",
                          ["eia860m-2026/august_generator2026.xlsx"]))     # .txt is not a sheet
        self.assertEqual(rc.member_for(names, "2026-07")[0], "july_generator2026.xlsx")
        # Year and month number; 2026-080 is not month 08 (a digit follows).
        names = ["eia860m-2026-08.xlsx", "eia860m-2026-09.xlsx", "x-2026-080.xlsx"]
        self.assertEqual(rc.member_for(names, "2026-08"),
                         ("eia860m-2026-08.xlsx", ["eia860m-2026-08.xlsx"]))
        self.assertEqual(rc.member_for(["202608.xlsx"], "2026-08")[0], "202608.xlsx")
        self.assertEqual(rc.member_for(names, "2026-10"), (None, []))
        # Two hits: the shorter name wins (25 characters against 31).
        two = ["old/august_generator2026_r.xlsx", "august_generator2026.xlsx"]
        self.assertEqual(rc.member_for(two, "2026-08")[0], "august_generator2026.xlsx")

    def test_checksum(self):
        # md5("abc") = 900150983cd24fb0d6963f7d28e17f72.
        self.assertTrue(rc.checksum_ok(b"abc", "md5:900150983cd24fb0d6963f7d28e17f72"))
        self.assertFalse(rc.checksum_ok(b"abc", "md5:00"))
        self.assertIsNone(rc.checksum_ok(b"abc", "sha256:ab"))
        self.assertIsNone(rc.checksum_ok(b"abc", None))

    def test_file_urls(self):
        self.assertEqual(rc.file_urls("22995197", "eia860m-2026.zip")[0],
                         "https://zenodo.org/api/records/22995197/files/eia860m-2026.zip/content")


class Compare(unittest.TestCase):
    def test_same_value(self):
        self.assertTrue(rc.same_value("capacity_mw", 1.0, 1.04))
        self.assertFalse(rc.same_value("capacity_mw", 1.0, 1.1))   # 0.1 > 0.05
        self.assertTrue(rc.same_value("planned_m", NAN, None))      # both missing
        self.assertFalse(rc.same_value("planned_m", NAN, 24321.0))
        self.assertTrue(rc.same_value("planned_m", 24321.0, 24321.0))
        self.assertTrue(rc.same_value("status", "U", "U"))
        self.assertFalse(rc.same_value("status", "U", "V"))

    def test_diff(self):
        z = recs([["1/A", "Planned", "U", 24321.0, 10.0], ["1/B", "Planned", "P", NAN, 5.0],
                  ["2/C", "Planned", "T", 24330.0, 3.0]])
        e = recs([["1/A", "Planned", "U", 24322.0, 10.0], ["1/B", "Planned", "P", NAN, 5.0],
                  ["3/D", "Planned", "V", 24325.0, 1.0]])
        d = rc.diff(z, e)
        # Both: 1/A, 1/B. Only 1/A's planned month differs (24321 against 24322).
        self.assertEqual((d["archive_keys"], d["eia_keys"], d["both"]), (3, 3, 2))
        self.assertEqual((d["archive_only"], d["eia_only"]), (["2/C"], ["3/D"]))
        self.assertEqual((d["archive_only_n"], d["eia_only_n"]), (1, 1))
        self.assertEqual(d["fields"]["planned_m"],
                         {"differ": 1, "sample": [{"key": "1/A", "archive": 24321.0,
                                                   "eia": 24322.0}]})
        self.assertEqual(d["fields"]["status"]["differ"], 0)
        self.assertEqual(d["fields"]["capacity_mw"]["differ"], 0)

    def test_show(self):
        e = recs([["1/A", "Planned", "U", 24322.0, 10.0]])
        rows = rc.show({"eia": e, "archive_9": None}, ["1/A", "9/Z"])
        # 24322 = 2026 * 12 + 10 -> 2026-11.
        self.assertEqual(rows, [
            {"key": "1/A", "eia": {"sheet": "Planned", "status": "U", "planned": "2026-11",
                                   "mw": 10.0}, "archive_9": None},
            {"key": "9/Z", "eia": None, "archive_9": None}])

    def test_interest(self):
        data = {"months": [{"report": "2026-08", "self_check": {"difference_sample": [
            {"key": "1/A", "pudl": "none", "workbook": "new"},
            {"key": "2/B", "pudl": "none", "workbook": "left"}]}},
            {"report": "2026-09", "error": "workbook not downloaded"}]}
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "workbook.json")
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(data, fh)
            self.assertEqual(rc.interest(path, "2026-08"), ["1/A", "2/B"])
            self.assertEqual(rc.interest(path, "2026-09"), [])
            self.assertEqual(rc.interest(os.path.join(d, "missing.json"), "2026-08"), [])


class Files(unittest.TestCase):
    ROWS = [["Plant ID", "Generator ID", "Nameplate Capacity (MW)", "Status",
             "Planned Operation Month", "Planned Operation Year"],
            [7, "06", 5.0, "(U) Under construction", 3, 2027]]

    def test_frame(self):
        data = xlsx_bytes([("Planned", self.ROWS), ("Planned_PR", self.ROWS)])
        f, err = rc.frame(data)
        self.assertIsNone(err)
        # Planned_PR is skipped; "06" is keyed "6"; 2027 * 12 + 3 - 1 = 24326.
        self.assertEqual(list(f.index), ["7/6"])
        self.assertEqual((f.at["7/6", "status"], f.at["7/6", "planned_m"],
                          f.at["7/6", "capacity_mw"]), ("U", 24326.0, 5.0))
        self.assertEqual(rc.frame(b"not a workbook")[0], None)

    def test_check_month(self):
        # EIA's file and two archived copies: copy 1 holds the same bytes, copy 2 a workbook
        # whose planned year is 2028 (24338 = 2028 * 12 + 3 - 1) instead of 2027.
        eia = xlsx_bytes([("Planned", self.ROWS)])
        later = [self.ROWS[0], [7, "06", 5.0, "(U) Under construction", 3, 2028]]
        other = xlsx_bytes([("Planned", later)])
        archives = []
        for rid, body in (("1", eia), ("2", other)):
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w") as zf:
                zf.writestr("august_generator2026.xlsx", body)
                zf.writestr("datapackage.json", "{}")
            archives.append(({"key": "eia860m-2026.zip", "first_id": rid,
                              "first_date": "2026-09-2%s" % rid, "first_version": rid},
                             zipfile.ZipFile(io.BytesIO(buf.getvalue()))))
        m = rc.check_month("2026-08", eia, archives, ["7/6"])
        self.assertEqual([c["member"] for c in m["copies"]], ["august_generator2026.xlsx"] * 2)
        self.assertEqual([c["same_file"] for c in m["copies"]], [True, False])
        self.assertNotIn("diff", m["copies"][0])
        d = m["copies"][1]["diff"]
        self.assertEqual(d["fields"]["planned_m"]["differ"], 1)
        self.assertEqual(d["fields"]["planned_m"]["sample"],
                         [{"key": "7/6", "archive": 24338.0, "eia": 24326.0}])
        # The key in each source read: EIA's and copy 2's (copy 1 is the same file, not read).
        self.assertEqual(m["keys"], [{"key": "7/6",
                                      "eia": {"sheet": "Planned", "status": "U",
                                              "planned": "2027-03", "mw": 5.0},
                                      "archive_2": {"sheet": "Planned", "status": "U",
                                                    "planned": "2028-03", "mw": 5.0}}])
        # A month of another year's zip has no copies here.
        self.assertEqual(rc.check_month("2025-12", eia, archives, [])["copies"], [])


if __name__ == "__main__":
    unittest.main()
