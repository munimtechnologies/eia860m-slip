"""Tests for retiredscope.py on hand-built workbooks: one pre-2002 generator leaves the Retired sheet,
one renamed generator leaves it. MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import unittest

import pandas as pd

import retiredscope as rs

OP_HEAD = ["Plant ID", "Plant State", "Generator ID", "Nameplate Capacity (MW)", "Technology", "Status"]
RE_HEAD = ["Plant ID", "Plant State", "Generator ID", "Nameplate Capacity (MW)", "Technology",
           "Retirement Month", "Retirement Year"]
TITLE = "Retired generators since 2002"


def raw(head, rows, title="EIA-860M generator inventory"):
    t = [title] + [None] * (len(head) - 1)
    return pd.DataFrame([t, head] + [list(r) for r in rows], dtype=object)


def book(operating, retired, canceled=()):
    return rs.book_from_sheets({"Operating": raw(OP_HEAD, operating),
                                "Retired": raw(RE_HEAD, retired, TITLE),
                                "Canceled or Postponed": raw(OP_HEAD, canceled)})


SOLAR = (1, "CT", "A", 10.0, "Solar", "(OP) Operating")
OLD = (10, "ME", "1", 5.0, "Petroleum Liquids", 6, 1995)
KEEP = (11, "TX", "GT1", 20.0, "Natural Gas Fired Combustion Turbine", 3, 2005)
COAL_OP = (12, "CA", "ST1", 50.0, "Conventional Steam Coal", "(OP) Operating")
COAL_RE = (12, "CA", "ST1", 50.0, "Conventional Steam Coal", 2, 2017)
HYDRO = (13, "NY", "3", 2.0, "Conventional Hydroelectric", 1, 2003)
OLD_CN = (10, "ME", "1", 5.0, "Petroleum Liquids", "(CN) Canceled")
B1 = (1439, "TX", "1A", 10.0, "Natural Gas Steam Turbine", 1, 2010)
B2 = (1439, "TX", "1B", 10.0, "Natural Gas Steam Turbine", 1, 2010)
R1 = (1439, "TX", "1", 20.0, "Natural Gas Steam Turbine", 1, 2010)

FEB, FEB_NOTES = book([SOLAR, COAL_OP], [OLD, KEEP])
MAR, MAR_NOTES = book([SOLAR], [KEEP, COAL_RE, HYDRO], canceled=[OLD_CN])
BEFORE, _ = book([SOLAR], [B1, B2])
AFTER, _ = book([SOLAR], [R1])


class HelperTests(unittest.TestCase):
    def test_months(self):
        self.assertEqual(rs.prev_month("2024-01"), "2023-12")
        self.assertEqual(rs.prev_month("2017-03"), "2017-02")
        need = rs.months_needed()
        self.assertEqual(len(need), 22)
        self.assertTrue(set(rs.COMPARE) <= set(need))
        self.assertEqual(len(rs.LEAVERS), 41)
        self.assertEqual(len(set(rs.LEAVERS)), 41)

    def test_years(self):
        self.assertEqual(rs.year_bin(1995), "before 2002")
        self.assertEqual(rs.year_bin("2002"), "2002 or later")
        self.assertEqual(rs.year_bin("2001.0"), "before 2002")
        self.assertEqual(rs.year_bin(None), "missing")
        self.assertEqual(rs.year_bin(float("nan")), "missing")

    def test_sheets(self):
        self.assertTrue(rs.is_retired("Retired"))
        self.assertFalse(rs.is_retired("Retired_PR"))
        self.assertFalse(rs.is_retired("Operating"))
        self.assertEqual(FEB_NOTES["Retired"], [TITLE])
        self.assertEqual(sorted(rs.retired(FEB)), ["10/1", "11/GT1"])
        self.assertEqual(rs.where(MAR, "10/1"), "Canceled or Postponed")
        self.assertEqual(rs.where(MAR, "11/GT1"), "Retired")
        self.assertEqual(rs.where(MAR, "99/9"), "not listed")


class ScopeTests(unittest.TestCase):
    def test_scope(self):
        s = rs.scope(FEB, MAR)
        self.assertEqual((s["retired_rows"], s["retired_keys"]), ([2, 3], [2, 3]))
        self.assertEqual(s["retired_bins"][0], [{"value": "2002 or later", "n": 1}, {"value": "before 2002", "n": 1}])
        self.assertEqual(s["retired_bins"][1], [{"value": "2002 or later", "n": 3}])
        self.assertEqual(s["left_keys"], ["10/1"])
        self.assertEqual((s["left"]["n"], s["left"]["mw"]), (1, 5.0))
        self.assertEqual(s["left"]["bins"], [{"value": "before 2002", "n": 1}])
        self.assertEqual(s["left"]["years"], [{"value": "1995", "n": 1}])
        self.assertEqual(s["left"]["state"], [{"value": "ME", "n": 1}])
        self.assertEqual(s["left_where"], [{"value": "Canceled or Postponed", "n": 1}])
        self.assertEqual((s["entered"]["n"], s["entered"]["mw"]), (1, 2.0))
        self.assertEqual(s["entered"]["bins"], [{"value": "2002 or later", "n": 1}])
        self.assertEqual(s["moved_in"], 1)

    def test_leaver(self):
        e = rs.leaver(BEFORE, AFTER, "1439/1A")
        self.assertEqual((e["sheet_before"], e["retirement_year"], e["retirement_month"]), ("Retired", 2010, 1))
        self.assertEqual((e["technology"], e["state"], e["nameplate_mw"]), ("Natural Gas Steam Turbine", "TX", 10))
        self.assertEqual((e["listed_after"], e["where_after"], e["plant_keys"]), (False, "not listed", [2, 1]))
        self.assertEqual(e["new_at_plant"], [{"key": "1439/1", "sheet": "Retired", "retirement_year": 2010,
                                              "technology": "Natural Gas Steam Turbine", "nameplate_mw": 20}])
        self.assertTrue(rs.consistent(e))
        self.assertFalse(rs.consistent(rs.leaver(BEFORE, BEFORE, "1439/1A")))
        self.assertFalse(rs.consistent(rs.leaver(AFTER, AFTER, "1439/1A")))

    def test_render(self):
        e = dict({"month": "2024-01", "consistent": True}, **rs.leaver(BEFORE, AFTER, "1439/1A"))
        res = {"files": [{"month": "2017-02", "member": "m.xlsx", "bytes": 9, "md5": "a", "eia_bytes": 9,
                          "eia_md5": "a", "same_file": True, "errors": []}],
               "titles": {"2017-02": ["T"], "2017-03": []}, "scope": rs.scope(FEB, MAR), "leavers": [e]}
        md = rs.render(res)
        self.assertIn("| 2017-02 | m.xlsx | 9 | a | 9 | a | True |", md)
        self.assertIn("Retired sheet rows: 2017-02 2, 2017-03 3. Keys: 2, 3.", md)
        self.assertIn("Left the Retired sheet and listed on no sheet the route reads in 2017-03: 1 (5.0 MW). "
                      "Retirement years: before 2002 1.", md)
        self.assertIn("Where 2017-03 lists them: Canceled or Postponed 1.", md)
        self.assertIn("Text above the Retired sheet's header, 2017-02: T", md)
        self.assertIn("Text above the Retired sheet's header, 2017-03: none", md)
        self.assertIn("Consistent with gapcensus-v1 (Retired the month before, on no routed sheet the month it "
                      "left): 1 of 1.", md)
        self.assertIn("| 2024-01 | 1439/1A | 2010-1 | Natural Gas Steam Turbine | TX | 10 | not listed | 2, 1 | "
                      "1439/1 (Retired, 2010, 20 MW) |", md)
        self.assertIn("Not run: x", rs.render({"error": "x"}))


if __name__ == "__main__":
    unittest.main()
