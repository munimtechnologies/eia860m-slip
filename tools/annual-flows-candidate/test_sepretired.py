"""Tests for sepretired.py on hand-built workbooks: an August Retired sheet whose generators leave,
move to Operating or to Canceled or Postponed in September, and an annual file that lists some of
them as retired. MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import calendar
import unittest

import pandas as pd

import annual860 as an
import retiredgap as rg
import sepretired as sr

M_HEAD = ["Entity ID", "Entity Name", "Plant ID", "Plant Name", "Plant State", "Generator ID",
          "Nameplate Capacity (MW)", "Technology", "Status"]
M_RE_HEAD = ["Entity ID", "Entity Name", "Plant ID", "Plant Name", "Plant State", "Generator ID",
             "Nameplate Capacity (MW)", "Technology", "Retirement Month", "Retirement Year"]
OP_HEAD = ["Utility ID", "Plant Code", "State", "Generator ID", "Technology", "Nameplate Capacity (MW)", "Status",
           "Planned Retirement Year"]
RE_HEAD = ["Utility ID", "Plant Code", "State", "Generator ID", "Technology", "Nameplate Capacity (MW)", "Status",
           "Retirement Month", "Retirement Year"]


def raw(head, rows, title="U.S. Electric Generating Units"):
    t = [title] + [None] * (len(head) - 1)
    return pd.DataFrame([t, head] + [list(r) for r in rows], dtype=object)


GT3 = (1, "U", 885, "Alpha", "IL", "3", 50.0, "Natural Gas Fired Combustion Turbine", "(OP) Operating")
GT77 = (3, "W", 77, "Gamma", "TX", "GT", 20.0, "Natural Gas Fired Combustion Turbine", "(OP) Operating")
AUG_RE = raw(M_RE_HEAD, [(1, "U", 885, "Alpha", "IL", "1", 100.0, "Conventional Steam Coal", 6, 2015),
                         (1, "U", 885, "Alpha", "IL", "2", 120.0, "Conventional Steam Coal", 6, 2015),
                         (2, "V", 360, "Beta", "CA", "1", 5.5, "Petroleum Liquids", 1, 1999),
                         (2, "V", 360, "Beta", "CA", "2", 7.0, "Petroleum Liquids", 1, 2026),
                         (3, "W", 77, "Gamma", "TX", "GT", 20.0, "Natural Gas Fired Combustion Turbine", 3, 2010)])
AUG = [rg.book_sheet("Operating", raw(M_HEAD, [GT3])), rg.book_sheet("Retired", AUG_RE),
       rg.book_sheet("Canceled or Postponed", raw(M_HEAD, []))]
SEP = [rg.book_sheet("Operating", raw(M_HEAD, [GT3, GT77])),
       rg.book_sheet("Retired", raw(M_RE_HEAD, [(2, "V", 360, "Beta", "CA", "2", 7.0, "Petroleum Liquids", 1, 2026),
                                                (4, "X", 99, "Delta", "NY", "A", 2.0, "Onshore Wind Turbine", 8,
                                                 2026)])),
       rg.book_sheet("Canceled or Postponed", raw(M_HEAD, [(2, "V", 360, "Beta", "CA", "1", 5.5, "Petroleum Liquids",
                                                            "(CN) Cancelled")]))]
ANNUAL = [an.annual_sheet("Operable", raw(OP_HEAD, [(9, 885, "IL", "3", "Natural Gas Fired Combustion Turbine", 50.0,
                                                     "OP", None)])),
          an.annual_sheet("Retired and Canceled", raw(RE_HEAD, [
              (9, 885, "IL", "1", "Conventional Steam Coal", 100.0, "RE", 6, 2015),
              (9, 885, "IL", "2", "Conventional Steam Coal", 120.0, "RE", 6, 2015),
              (9, 360, "CA", "1", "Petroleum Liquids", 5.5, "RE", 1, 1999)]))]
KEYS = ("885/1", "885/2", "360/1")
NAMES = sr.plant_names(AUG_RE, {"885", "360"})


class HelperTests(unittest.TestCase):
    def test_constants(self):
        self.assertEqual(len(sr.KEYS), 16)
        self.assertEqual(len(set(sr.KEYS)), 16)
        self.assertEqual(len({k.split("/")[0] for k in sr.KEYS}), 15)
        self.assertEqual((sr.S2_MIN, sr.S3_MAX, sr.SINCE, sr.YEAR), (12, 3, 2002, 2025))
        self.assertTrue(sr.PLAN_URL.endswith("/main/docs/sepretired-plan.md"))
        self.assertEqual(sr.deadline_ts("2026-10-24T06:00"), calendar.timegm((2026, 10, 24, 6, 0, 0, 0, 0, 0)))

    def test_scope(self):
        self.assertEqual(sr.scope(1999), "before 2002")
        self.assertEqual(sr.scope("2002.0"), "2002-2025")
        self.assertEqual(sr.scope(2025), "2002-2025")
        self.assertEqual(sr.scope(2026), "after 2025")
        self.assertEqual(sr.scope(None), "missing")

    def test_plant_names(self):
        self.assertEqual(NAMES, {"885": "Alpha", "360": "Beta"})
        no_name = raw(["Plant ID", "Generator ID", "Status"], [(885, "1", "OP")])
        self.assertEqual(sr.plant_names(no_name, {"885"}), {})

    def test_wait_plan(self):
        answers, sleeps = iter([b"404: Not Found", b"# x\n\nStatus: pre-registered, not yet scored.\n"]), []
        self.assertTrue(sr.wait_plan(10, get=lambda u: next(answers), sleep=sleeps.append, clock=lambda: 0))
        self.assertEqual(sleeps, [600])

        def fail(url):
            raise OSError("404")

        clock, sleeps = iter([0, 5, 11]), []
        self.assertFalse(sr.wait_plan(10, get=fail, sleep=sleeps.append, clock=lambda: next(clock)))
        self.assertEqual(len(sleeps), 2)

    def test_read_sep(self):
        calls = []

        def html(url):
            calls.append(url)
            if "archive" in url:
                raise OSError("404")
            return b"<!doctype html>"

        f, book, names = sr.read_sep({"885"}, get=html)
        self.assertEqual((f["source"], len(f["errors"]), book, names, len(calls)), (None, 2, None, {}, 2))
        f, book, names = sr.read_sep({"885"}, get=lambda u: b"PK\x03\x04junk")
        self.assertEqual((f["source"], f["bytes"], f["same_as_monthcheck"], book), (sr.SEP_URLS[0], 8, False, None))
        self.assertEqual(f["md5"], rg.md5(b"PK\x03\x04junk"))
        self.assertTrue(f["errors"][-1].startswith("not read: "))
        self.assertEqual(sr.read_named(b"not a workbook", {"885"})[:2], (None, {}))


class RowTests(unittest.TestCase):
    def setUp(self):
        self.rows = sr.leaver_rows(KEYS, AUG, NAMES, SEP, ANNUAL)

    def test_rows(self):
        self.assertEqual(self.rows[0], {
            "key": "885/1", "plant_name": "Alpha", "state": "IL", "technology": "Conventional Steam Coal",
            "retirement_month": 6, "retirement_year": 2015, "scope": "2002-2025", "nameplate_mw": 100,
            "where_sep": "not listed", "plant_aug": "Operating 1; Retired 2", "plant_sep": "Operating 1",
            "annual": "Retired and Canceled RE", "annual_retired": True})
        r = self.rows[2]
        self.assertEqual((r["scope"], r["nameplate_mw"], r["where_sep"], r["plant_aug"], r["plant_sep"]),
                         ("before 2002", 5.5, "Canceled or Postponed", "Retired 2", "Retired 1; Canceled or Postponed 1"))
        self.assertEqual((r["annual"], r["annual_retired"]), ("Retired and Canceled RE", False))
        gone = sr.leaver_rows(("99/A",), AUG, NAMES, SEP, None)[0]
        self.assertEqual((gone["scope"], gone["annual"], gone["annual_retired"], gone["plant_name"]),
                         ("not on August's Retired sheet", "not read", False, None))

    def test_score(self):
        p = sr.score(self.rows, True, True)
        self.assertEqual([x["outcome"] for x in p], ["failed", "failed", "not scored yet"])
        self.assertEqual(p[0]["value"], "2 of 3 on no sheet of the 2026-09 workbook")
        self.assertEqual(p[1]["value"], "2 of 3 listed as retired (RE, 2002-2025) by the annual EIA-860 2025")
        self.assertEqual(p[2]["bar"], "at most 3 of 3 listed again on a sheet the changelog reads")
        self.assertEqual(sr.score(self.rows, True, True, s2_min=2)[1]["outcome"], "held")
        self.assertEqual([x["outcome"] for x in sr.score(self.rows, False, False)],
                         ["not scored", "not scored", "not scored yet"])

    def test_compare(self):
        c = sr.compare(AUG, SEP)
        self.assertEqual((c["aug"], c["sep"], c["left"], c["left_mw"], c["entered"], c["entered_mw"]),
                         (5, 2, 4, 245.5, 1, 2.0))
        self.assertEqual(c["left_scope"], [{"value": "2002-2025", "n": 3}, {"value": "before 2002", "n": 1}])
        self.assertEqual(c["left_where_sep"], [{"value": "not listed", "n": 2},
                                               {"value": "Canceled or Postponed", "n": 1},
                                               {"value": "Operating", "n": 1}])
        self.assertEqual(c["aug_scope"], [{"value": "2002-2025", "n": 3}, {"value": "after 2025", "n": 1},
                                          {"value": "before 2002", "n": 1}])
        self.assertEqual((c["entered_scope"], c["entered_where_aug"]),
                         ([{"value": "after 2025", "n": 1}], [{"value": "not listed", "n": 1}]))

    def test_census(self):
        s = sr.census_summary(an.census(ANNUAL, SEP, 2025))
        self.assertEqual(s, {"annual_retired": 2, "annual_retired_mw": 220.0,
                             "where_in_monthly": [{"value": "not listed", "n": 2}], "not_in_monthly": 2,
                             "not_in_monthly_mw": 220.0, "monthly_retired": 2, "monthly_retired_in_scope": 0,
                             "both": 0, "monthly_not_annual": 0})

    def test_render(self):
        res = {"rows": self.rows, "files": [{"name": "EIA-860M 2026-09", "source": "u", "bytes": 9, "md5": "m",
                                             "errors": []}],
               "sep_file": {"same_as_monthcheck": True}, "predictions": sr.score(self.rows, True, True, s2_min=2),
               "leavers_mw": 225.5, "compare": sr.compare(AUG, SEP),
               "census": {"2026-09": sr.census_summary(an.census(ANNUAL, SEP, 2025))}}
        md = sr.render(res)
        for s in ("| EIA-860M 2026-09 | u | 9 | m | none |",
                  "September file is the one monthcheck-sep2026-v1 read (14013970 bytes, md5 "
                  "4c741eb77a5ccad5aca32ffe43f398af): True.",
                  "| S1 | failed | 2 of 3 on no sheet of the 2026-09 workbook | all 3 on no sheet (Canceled or "
                  "Postponed and *_PR included) |",
                  "Held: 1 of 2 scored.",
                  "| 360/1 | Beta | CA | Petroleum Liquids | 1/1999 | 5.5 | before 2002 | Canceled or Postponed | "
                  "Retired 2 | Retired 1; Canceled or Postponed 1 | Retired and Canceled RE |",
                  "Together: 225.5 MW on August's Retired sheet, at 2 plants. Scope: 2002-2025 2; before 2002 1. "
                  "Retirement years: 1999 1; 2015 2. Technologies: Conventional Steam Coal 2; Petroleum Liquids 1. "
                  "States: IL 2; CA 1.",
                  "Generators on the Retired sheet: 5 in 2026-08, 2 in 2026-09. By retirement year, 2026-08: "
                  "2002-2025 3; after 2025 1; before 2002 1; 2026-09: after 2025 2.",
                  "Left the sheet: 4 (245.5 MW). By retirement year: 2002-2025 3; before 2002 1. Where September "
                  "lists them: not listed 2; Canceled or Postponed 1; Operating 1.",
                  "Entered the sheet: 1 (2.0 MW). By retirement year: after 2025 1. Where August listed them: "
                  "not listed 1.",
                  "Annual retired (status RE, retired 2002 to 2025): 2 (220.0 MW). Where the 2026-09 workbook lists "
                  "them: not listed 2. On no sheet of it: 2 (220.0 MW).",
                  "Monthly Retired sheet: 2 generators, 0 retired 2002 to 2025; of those, 0 also annual retired "
                  "and 0 not."):
            self.assertIn(s, md)


if __name__ == "__main__":
    unittest.main()
