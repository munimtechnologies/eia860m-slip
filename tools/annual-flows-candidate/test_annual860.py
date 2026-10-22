"""Tests for annual860.py on hand-built workbooks: an annual file with a retired generator the
monthly workbook leaves out, and a monthly Retired sheet with one the annual file leaves out.
MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import io
import os
import tempfile
import unittest
import zipfile

import pandas as pd

import annual860 as an
import retiredgap as rg

OP_HEAD = ["Utility ID", "Plant Code", "State", "Generator ID", "Technology", "Nameplate Capacity (MW)", "Status",
           "Planned Retirement Year"]
RE_HEAD = ["Utility ID", "Plant Code", "State", "Generator ID", "Technology", "Nameplate Capacity (MW)", "Status",
           "Retirement Month", "Retirement Year"]
M_OP_HEAD = ["Plant ID", "Plant State", "Generator ID", "Nameplate Capacity (MW)", "Technology", "Status"]
M_RE_HEAD = ["Plant ID", "Plant State", "Generator ID", "Nameplate Capacity (MW)", "Technology",
             "Retirement Month", "Retirement Year"]


def raw(head, rows, title="Form EIA-860 Data - Schedule 3, 'Generator Data'"):
    t = [title] + [None] * (len(head) - 1)
    return pd.DataFrame([t, head] + [list(r) for r in rows], dtype=object)


SOLAR = (9, 1, "CT", "A", "Solar Photovoltaic", 10.0, "OP", 2040)
COAL = (9, 1572, "MD", "ST1", "Conventional Steam Coal", 196.0, "RE", 8, 2020)
OLD = (9, 10, "ME", "1", "Petroleum Liquids", 5.0, "RE", 6, 1995)
BOTH = (9, 12, "CA", "ST1", "Conventional Steam Coal", 50.0, "RE", 2, 2017)
WIND = (9, 20, "TX", "W", "Onshore Wind Turbine", 3.0, "CN", None, None)
NOTE = ("NOTE: see the file layout", None, None, None, None, None, None, None, None)

ANNUAL = [an.annual_sheet("Operable", raw(OP_HEAD, [SOLAR])),
          an.annual_sheet("Retired and Canceled", raw(RE_HEAD, [COAL, OLD, BOTH, WIND, NOTE]))]
MONTHLY = [rg.book_sheet("Operating", raw(M_OP_HEAD, [(1, "CT", "A", 10.0, "Solar", "(OP) Operating")])),
           rg.book_sheet("Retired", raw(M_RE_HEAD, [(12, "CA", "ST1", 50.0, "Conventional Steam Coal", 2, 2017),
                                                    (13, "NY", "3", 2.0, "Conventional Hydroelectric", 1, 2003),
                                                    (14, "OH", "GT", 1.0, "Natural Gas", 5, 2026)])),
           rg.book_sheet("Canceled or Postponed", raw(M_OP_HEAD, []))]


class HelperTests(unittest.TestCase):
    def test_constants(self):
        self.assertEqual(len(an.LEAVERS), 41)
        self.assertEqual(len(set(an.LEAVERS)), 41)
        self.assertIn(an.CENSUS_YEAR, an.YEARS)
        self.assertEqual(an.urls(2024), [an.BASE + "xls/eia8602024.zip", an.BASE + "archive/xls/eia8602024.zip"])

    def test_code_and_years(self):
        self.assertEqual(an.code("(RE) Retired"), "RE")
        self.assertEqual(an.code("CN"), "CN")
        self.assertIsNone(an.code(None))
        self.assertEqual(an.year_bin(2001), "before 2002")
        self.assertEqual(an.year_bin("2002.0"), "2002 or later")
        self.assertEqual(an.year_bin(None), "missing")

    def test_member(self):
        names = ["eia8602025/1___Utility_Y2025.xlsx", "3_1_Generator_Y2025_Early_Release.xlsx",
                 "3_1_Generator_Y2025.xlsx"]
        self.assertEqual(an.member_3_1(names, 2025), "3_1_Generator_Y2025.xlsx")
        self.assertEqual(an.member_3_1(["x/3_1_Generator_Y2020.xlsx"], 2021), "x/3_1_Generator_Y2020.xlsx")
        self.assertIsNone(an.member_3_1(["2___Plant_Y2025.xlsx"], 2025))

    def test_get_annual(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("3_1_Generator_Y2024.xlsx", b"x")
        data, calls = buf.getvalue(), []

        def get(url):
            calls.append(url)
            if "archive" not in url:
                raise OSError("404")
            return data

        with tempfile.TemporaryDirectory() as d:
            path, info = an.get_annual(2024, d, get=get)
            self.assertEqual((info["url"], info["cached"], len(info["errors"])), (an.urls(2024)[1], False, 1))
            self.assertEqual((info["bytes"], info["md5"]), (len(data), rg.md5(data)))
            self.assertEqual(os.path.basename(path), "eia8602024.zip")
            path2, info2 = an.get_annual(2024, d, get=get)
            self.assertEqual((path2, info2["cached"], info2["md5"], len(calls)), (path, True, rg.md5(data), 2))


class BookTests(unittest.TestCase):
    def test_sheet(self):
        op, re_ = ANNUAL
        self.assertEqual((op["header_row"], op["rows"], re_["rows"]), (1, 1, 4))
        self.assertEqual(op["keys"]["1/A"], {"status": "OP", "retirement_year": None, "technology": "Solar Photovoltaic",
                                              "state": "CT", "nameplate_mw": 10})
        self.assertEqual(re_["keys"]["1572/ST1"]["retirement_year"], 2020)
        self.assertEqual(sorted(re_["keys"]), ["10/1", "12/ST1", "1572/ST1", "20/W"])

    def test_where(self):
        self.assertEqual(an.annual_where(ANNUAL, "1572/ST1"), "Retired and Canceled RE")
        self.assertEqual(an.annual_where(ANNUAL, "1/A"), "Operable OP")
        self.assertEqual(an.annual_where(ANNUAL, "99/9"), "not listed")
        self.assertEqual(an.where(MONTHLY, "12/ST1"), "Retired")
        self.assertEqual(an.where(MONTHLY, "1572/ST1"), "not listed")

    def test_retired(self):
        self.assertEqual(sorted(an.annual_retired(ANNUAL, 2025)), ["12/ST1", "1572/ST1"])
        self.assertEqual(sorted(an.annual_retired(ANNUAL, 2019)), ["12/ST1"])
        t = an.retired_sheet_tallies(ANNUAL)
        self.assertEqual(t["status"], [{"value": "RE", "n": 3}, {"value": "CN", "n": 1}])
        self.assertEqual(t["re_bins"], [{"value": "2002 or later", "n": 2}, {"value": "before 2002", "n": 1}])

    def test_leaver_row(self):
        r = an.leaver_row(ANNUAL, 2025, "1572/ST1")
        self.assertEqual(r, {"year": 2025, "where": "Retired and Canceled RE", "retirement_year": 2020,
                             "nameplate_mw": 196, "plant": {"Operable": 0, "Retired and Canceled": 1}})
        r = an.leaver_row(ANNUAL, 2025, "1439/1A")
        self.assertEqual((r["where"], r["retirement_year"], r["nameplate_mw"]), ("not listed", None, None))


class CensusTests(unittest.TestCase):
    def test_census(self):
        c = an.census(ANNUAL, MONTHLY, 2025)
        self.assertEqual((c["annual_retired"]["n"], c["annual_retired"]["mw"]), (2, 246.0))
        self.assertEqual(c["where_in_monthly"], [{"value": "Retired", "n": 1}, {"value": "not listed", "n": 1}])
        self.assertEqual((c["not_in_monthly"]["n"], c["not_in_monthly"]["mw"]), (1, 196.0))
        self.assertEqual(c["not_in_monthly"]["years"], [{"value": "2020", "n": 1}])
        self.assertEqual(c["not_in_monthly"]["state"], [{"value": "MD", "n": 1}])
        self.assertEqual([r["key"] for r in c["not_in_monthly_rows"]], ["1572/ST1"])
        self.assertEqual((c["monthly_retired"], c["monthly_retired_in_scope"]), (3, 2))
        self.assertEqual((c["monthly_not_annual"], c["monthly_not_annual_where"]),
                         (1, [{"value": "not listed", "n": 1}]))
        self.assertEqual(c["monthly_not_annual_rows"], [{"key": "13/3", "where_annual": "not listed",
                                                         "retirement_year": 2003, "nameplate_mw": 2}])
        self.assertEqual((c["both"], c["same_year"]), (1, 1))

    def test_render(self):
        res = {"census_year": 2025,
               "files": [{"year": 2025, "url": "u", "cached": False, "bytes": 9, "md5": "a", "member": "m.xlsx",
                          "errors": [], "sheets": [{"sheet": "Operable", "header_row": 1, "rows": 1}],
                          "retired_sheet": an.retired_sheet_tallies(ANNUAL)}],
               "monthly_files": [{"month": "2025-12", "member": "w.xlsx", "bytes": 8, "md5": "b", "errors": []}],
               "leavers": [{"month": "2021-12", "key": "1572/ST1", "years": [an.leaver_row(ANNUAL, 2025, "1572/ST1")]}],
               "census": {"2025-12": an.census(ANNUAL, MONTHLY, 2025)}}
        md = an.render(res)
        self.assertIn("| 2025 | u | False | 9 | a | m.xlsx | Operable 1 | none |", md)
        self.assertIn("| 2025 | RE 3; CN 1 | 2002 or later 2; before 2002 1 |", md)
        self.assertIn("| 1572/ST1 | 2021-12 | Retired and Canceled RE (2020, 196 MW) |", md)
        self.assertIn("Annual retired (status RE, retired 2002 to 2025): 2 (246.0 MW).", md)
        self.assertIn("Where the 2025-12 workbook lists them: Retired 1; not listed 1.", md)
        self.assertIn("On no sheet of the 2025-12 workbook: 1 (196.0 MW). Retirement years: 2020 1.", md)
        self.assertIn("Monthly Retired sheet: 3 generators, 2 retired 2002 to 2025; of those, 1 also annual retired "
                      "(same retirement year: 1) and 1 not. Where the annual file lists those 1: not listed 1.", md)


if __name__ == "__main__":
    unittest.main()
