"""Unit tests for layouts.py. MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import io
import json
import os
import tempfile
import unittest
import zipfile

import pandas as pd

import layouts as lo
import rawcheck as rc
import workbook as wk

HEAD = ["Plant ID", "Generator ID", "Nameplate Capacity (MW)", "Status"]
PLAN_HEAD = HEAD + ["Planned Operation Month", "Planned Operation Year"]


def frame(rows):
    return pd.DataFrame(rows, dtype=object)


OP = frame([["EIA-860M operating generators", None, None, None, None],
            ["Entity ID"] + HEAD,
            [1, 100, "1", 5.0, "(OP) Operating"],
            [2, 102, "A", 2.0, "(SB) Standby/Backup"],
            ["Note: data are preliminary", None, None, None, None]])
PL = frame([PLAN_HEAD,
            [101, "0011", 3.0, "(U) Under construction", 1, 2027],
            [100, "1", 5.0, "(P) Planned", 6, 2027]])
CN = frame([HEAD, [103, "X", 1.0, "(CN) Cancelled"]])
PR = frame([HEAD, [104, "1", 1.0, "(OP) Operating"]])
RE = frame([["Plant ID", "Generator ID", "Nameplate Capacity (MW)", "Retirement Month",
             "Retirement Year"], [105, "1", 7.0, 3, 2020]])
NOTES = frame([["Notes"], ["See EIA website"]])


def sheets():
    return {"Operating": OP, "Planned": PL, "Retired": RE, "Canceled or Postponed": CN,
            "Operating_PR": PR, "Notes": NOTES}


class SheetTests(unittest.TestCase):
    def test_kind_and_left_out(self):
        self.assertEqual([lo.kind(n) for n in ("Operating", "Planned", "Retired",
                                               "Canceled or Postponed", "Operating_PR", "Notes")],
                         ["operating", "planned", "retired", "canceled", "operating", "other"])
        self.assertTrue(lo.left_out("Operating_PR"))
        self.assertTrue(lo.left_out("Canceled or Postponed"))
        self.assertFalse(lo.left_out("Planned"))

    def test_operating_sheet(self):
        info, rec = lo.sheet_info("Operating", OP)
        self.assertEqual(info["header_row"], 1)
        self.assertEqual(info["rows"], 2)
        self.assertEqual(info["statuses"], ["OP", "SB"])
        self.assertEqual(info["picks"]["capacity"], "Nameplate Capacity (MW)")
        self.assertEqual(info["picks"]["status"], "Status")
        self.assertIsNone(info["picks"]["planned_month"])
        self.assertIsNone(info["picks"]["state"])
        self.assertIsNone(info["planned_missing"])
        self.assertEqual(info["problems"], [])
        self.assertEqual(list(rec["key"]), ["100/1", "102/A"])

    def test_planned_sheet(self):
        info, rec = lo.sheet_info("Planned", PL)
        self.assertEqual(info["header_row"], 0)
        self.assertEqual(info["planned_missing"], 0)
        self.assertEqual(info["problems"], [])
        self.assertEqual(list(rec["key"]), ["101/11", "100/1"])
        self.assertEqual(list(rec["planned_m"]), [2027 * 12, 2027 * 12 + 5])

    def test_retired_sheet_needs_no_status(self):
        info, _ = lo.sheet_info("Retired", RE)
        self.assertIsNone(info["picks"]["status"])
        self.assertIsNone(info["picks"]["planned_month"])
        self.assertEqual(info["problems"], [])

    def test_problems(self):
        info, _ = lo.sheet_info("Planned", frame([r[:5] for r in PL.values.tolist()]))
        self.assertEqual(info["problems"], ["no planned month or year column"])
        info, _ = lo.sheet_info("Operating", frame([HEAD, [100, "1", 5.0, None],
                                                    [101, "1", 5.0, "(OP) Operating"]]))
        self.assertEqual(info["problems"], ["status blank in 1 of 2 rows"])
        info, _ = lo.sheet_info("Operating", NOTES)
        self.assertEqual(info["problems"], ["no header row"])
        self.assertEqual(info["top"], [["Notes"], ["See EIA website"]])
        info, rec = lo.sheet_info("Notes", NOTES)
        self.assertEqual(info["problems"], [])
        self.assertIsNone(rec)
        info, _ = lo.sheet_info("Canceled or Postponed", NOTES)
        self.assertEqual(info["problems"], [])


class MonthTests(unittest.TestCase):
    def test_month_counts_as_workbook_frame(self):
        m = lo.month_info("2026-08", sheets())
        wb, _, dup = wk.workbook_frame(sheets())
        self.assertEqual(m["keys"], len(wb))
        self.assertEqual(m["keys"], 4)
        self.assertEqual(m["duplicate_keys"], dup)
        self.assertEqual(m["duplicate_keys"], 1)
        self.assertEqual(m["rows"], 5)
        self.assertTrue(m["readable"])
        self.assertEqual(m["problems"], [])

    def test_month_without_operating_rows(self):
        m = lo.month_info("2015-07", {"Operating": NOTES, "Planned": PL})
        self.assertEqual(m["problems"], ["Operating: no header row", "no Operating sheet with rows"])
        self.assertFalse(m["readable"])

    def test_read_month_from_zip(self):
        xbuf = io.BytesIO()
        with pd.ExcelWriter(xbuf, engine="openpyxl") as xw:
            for name, raw in sheets().items():
                raw.to_excel(xw, sheet_name=name, header=False, index=False)
        zbuf = io.BytesIO()
        with zipfile.ZipFile(zbuf, "w") as zf:
            zf.writestr("eia860m-2026-08.xlsx", xbuf.getvalue())
            zf.writestr("readme.txt", "x")
        with zipfile.ZipFile(io.BytesIO(zbuf.getvalue())) as zf:
            m = lo.read_month(zf, "2026-08")
            gone = lo.read_month(zf, "2026-07")
        self.assertEqual(m["member"], "eia860m-2026-08.xlsx")
        self.assertTrue(m["readable"])
        self.assertEqual(m["keys"], 4)
        self.assertEqual(m["md5"], rc.md5(xbuf.getvalue()))
        self.assertIsNone(gone["member"])
        self.assertFalse(gone["readable"])


class ZipTests(unittest.TestCase):
    def test_listed_md5(self):
        text = json.dumps({"resources": [
            {"name": "eia860m-2015.zip", "path": "https://zenodo.org/records/1/files/eia860m-2015.zip",
             "hash": "ABC"},
            {"path": "https://x/y/eia860m-2016.zip?download=1", "hash": "md5:def"},
            {"name": "datapackage.json"}]})
        self.assertEqual(lo.listed_md5(text), {"eia860m-2015.zip": "abc", "eia860m-2016.zip": "def"})
        self.assertEqual(lo.listed_md5("not json"), {})

    def test_get_zip_downloads_then_keeps(self):
        good = rc.md5(b"abc")
        with tempfile.TemporaryDirectory() as d:
            path, info = lo.get_zip(2015, d, good, None, download=lambda url: (b"abc", None))
            self.assertTrue(os.path.exists(path))
            self.assertEqual(os.path.basename(path), "zenodo-22995197-eia860m-2015.zip")
            self.assertTrue(info["md5_matches_page"])
            self.assertFalse(info["md5_matches_datapackage"])
            self.assertFalse(info["cached"])
            self.assertEqual(info["bytes"], 3)

            def boom(url):
                raise AssertionError("a kept copy must not be downloaded again")
            path2, info2 = lo.get_zip(2015, d, None, good, download=boom)
            self.assertEqual(path2, path)
            self.assertTrue(info2["cached"])
            self.assertTrue(info2["md5_matches_datapackage"])

    def test_get_zip_refuses_wrong_md5(self):
        with tempfile.TemporaryDirectory() as d:
            path, info = lo.get_zip(2016, d, rc.md5(b"abc"), None, download=lambda url: (b"xyz", None))
            self.assertIsNone(path)
            self.assertEqual(len(info["tried"]), 2)
            self.assertTrue(all("matches neither" in t["error"] for t in info["tried"]))
            self.assertFalse(os.listdir(d))


class PublishedTests(unittest.TestCase):
    def test_waits_until_same(self):
        with tempfile.TemporaryDirectory() as d:
            for n, body in (("a.txt", b"A"), ("b.txt", b"B")):
                with open(os.path.join(d, n), "wb") as fh:
                    fh.write(body)
            calls = []

            def fetch(url):
                calls.append(url)
                return b"old" if len(calls) <= 2 else {"base/a.txt": b"A", "base/b.txt": b"B"}[url]
            res = lo.same_as_published("base/", ("a.txt", "b.txt"), 10, here=d, fetch=fetch,
                                       clock=lambda: 0, pause=lambda s: None)
            self.assertTrue(res["same"])
            self.assertEqual(res["checks"], 2)

    def test_gives_up_at_deadline(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "a.txt"), "wb") as fh:
                fh.write(b"A")
            ticks = iter([0, 1000, 1000])

            def fetch(url):
                raise OSError("404")
            res = lo.same_as_published("base/", ("a.txt",), 1, here=d, fetch=fetch,
                                       clock=lambda: next(ticks), pause=lambda s: None)
            self.assertFalse(res["same"])
            self.assertEqual(res["checks"], 1)
            self.assertIn("404", res["files"]["a.txt"]["error"])


class RenderTests(unittest.TestCase):
    def test_render_and_tables(self):
        m = lo.month_info("2026-08", sheets())
        m.update(member="eia860m-2026-08.xlsx", seconds=1.0)
        years = [{"year": 2026, "zip": {"tried": [], "md5_matches_page": True}, "error": None,
                  "months": [m, {"month": "2026-09", "member": None, "readable": False,
                                 "problems": []}], "unclaimed": ["x.xlsx"]}]
        t = lo.totals(years)
        self.assertEqual((t["workbooks_found"], t["readable"], t["first_month"]), (1, 1, "2026-08"))
        lay = lo.layouts(years)
        self.assertEqual([x["kind"] for x in lay], ["operating", "planned", "retired"])
        self.assertEqual(lo.sheet_sets(years)[0]["months"], 1)
        result = {"datapackage": {"read": True, "md5": {"a": "b"}}, "years": years, "totals": t,
                  "layouts": lay, "sheet_sets": lo.sheet_sets(years)}
        md = lo.render(result)
        self.assertIn("Readable: 1 of 1 workbooks found (2026-08 to 2026-08, 1 years)", md)
        self.assertIn("- 2026: x.xlsx", md)
        self.assertEqual(len(lo.sheet_table(years)), 6)
        json.dumps(result, default=str)


if __name__ == "__main__":
    unittest.main()
