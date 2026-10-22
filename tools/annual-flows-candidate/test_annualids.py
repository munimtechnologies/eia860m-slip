"""Tests for annualids.py on hand-built workbooks: an annual 2025 file, a December 2025 monthly workbook that
still lists one annual-retired generator as operating, and an August 2026 one whose Retired sheet has two
generators the annual file does not list (one at a plant it lists, one at a plant it does not).
MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import unittest

import pandas as pd

import annual860 as an
import annualids as ai
import retiredgap as rg

OP_HEAD = ["Utility ID", "Plant Code", "State", "Generator ID", "Technology", "Nameplate Capacity (MW)", "Status",
           "Planned Retirement Year"]
RE_HEAD = ["Utility ID", "Plant Code", "State", "Generator ID", "Technology", "Nameplate Capacity (MW)", "Status",
           "Retirement Month", "Retirement Year"]
M_OP_HEAD = ["Plant ID", "Plant State", "Generator ID", "Nameplate Capacity (MW)", "Technology", "Status",
             "Planned Retirement Month", "Planned Retirement Year"]
M_RE_HEAD = ["Plant ID", "Plant State", "Generator ID", "Nameplate Capacity (MW)", "Technology",
             "Retirement Month", "Retirement Year"]


def raw(head, rows, title="Form EIA-860 Data - Schedule 3, 'Generator Data'"):
    t = [title] + [None] * (len(head) - 1)
    return pd.DataFrame([t, head] + [list(r) for r in rows], dtype=object)


SOLAR = (9, 1, "CT", "A", "Solar Photovoltaic", 10.0, "OP", 2040)
BOTH = (9, 12, "CA", "ST1", "Conventional Steam Coal", 50.0, "RE", 2, 2017)
LATE_GT = (9, 30, "TX", "G", "Natural Gas Fired Combustion Turbine", 20.0, "RE", 11, 2025)
ANNUAL = [an.annual_sheet("Operable", raw(OP_HEAD, [SOLAR])),
          an.annual_sheet("Retired and Canceled", raw(RE_HEAD, [BOTH, LATE_GT]))]

M_A = (1, "CT", "A", 10.0, "Solar", "(OP) Operating", None, None)
M_G = (30, "TX", "G", 20.0, "Natural Gas", "(OP) Operating", 11, 2025)
R_ST1 = (12, "CA", "ST1", 50.0, "Conventional Steam Coal", 2, 2017)
R_3 = (13, "NY", "3", 2.0, "Conventional Hydroelectric", 1, 2003)
R_B = (1, "CT", "B", 4.0, "Solar", 6, 2010)
R_G = (30, "TX", "G", 20.0, "Natural Gas", 11, 2025)
R_GT = (14, "OH", "GT", 1.0, "Natural Gas", 5, 2026)
LATE = [rg.book_sheet("Operating", raw(M_OP_HEAD, [M_A, M_G])),
        rg.book_sheet("Retired", raw(M_RE_HEAD, [R_ST1, R_3, R_B]))]
LAST = [rg.book_sheet("Operating", raw(M_OP_HEAD, [M_A])),
        rg.book_sheet("Retired", raw(M_RE_HEAD, [R_ST1, R_G, R_3, R_B, R_GT])),
        rg.book_sheet("Canceled or Postponed", raw(M_OP_HEAD, []))]
HISTORY = {2023: {"13/3": "Operable OP"}, 2024: {"13/3": "Retired and Canceled RE", "1/A": "Operable OP"}}


def prev_month(m):
    y, mo = int(m[:4]), int(m[5:7])
    return "%d-%02d" % ((y, mo - 1) if mo > 1 else (y - 1, 12))


class HelperTests(unittest.TestCase):
    def test_constants(self):
        self.assertEqual(ai.YEARS, tuple(range(2016, 2026)))
        self.assertIn(ai.CENSUS_YEAR, ai.YEARS)
        self.assertEqual((ai.LATE, ai.LAST), an.MONTHLY)
        leaver_plants = {ai.plant_of(k) for _, k in an.LEAVERS}
        for p, m in ai.FOCUS:
            self.assertIn(p, leaver_plants)
            self.assertEqual(prev_month(min(lm for lm, k in an.LEAVERS if ai.plant_of(k) == p)), m, p)

    def test_plant_rows(self):
        self.assertEqual(ai.plant_rows(ANNUAL, "1"), [{"sheet": "Operable", "key": "1/A", "status": "OP",
                                                        "retirement_year": None, "nameplate_mw": 10}])
        self.assertEqual(ai.plant_rows(LATE, "1"), [
            {"sheet": "Operating", "key": "1/A", "status": "OP", "retirement_year": None, "nameplate_mw": 10},
            {"sheet": "Retired", "key": "1/B", "status": None, "retirement_year": 2010, "nameplate_mw": 4}])
        self.assertEqual(ai.plant_rows(ANNUAL, "99"), [])

    def test_listed(self):
        self.assertEqual(ai.plants(ANNUAL), {"1", "12", "30"})
        self.assertEqual(ai.listed(ANNUAL), {"1/A": "Operable OP", "12/ST1": "Retired and Canceled RE",
                                             "30/G": "Retired and Canceled RE"})


class CensusTests(unittest.TestCase):
    def test_late_operating(self):
        lo = ai.late_operating(ANNUAL, LATE, LAST)
        self.assertEqual(lo["rows"], [{"key": "30/G", "annual_year": 2025, "annual_mw": 20,
                                       "technology": "Natural Gas Fired Combustion Turbine", "late_status": "OP",
                                       "late_planned_year": 2025, "late_planned_month": 11,
                                       "where_last": "Retired"}])
        self.assertEqual((lo["n"], lo["in_census_year"], lo["mw"]), (1, 1, 20.0))
        self.assertEqual(lo["years"], [{"value": "2025", "n": 1}])
        self.assertEqual(lo["where_last"], [{"value": "Retired", "n": 1}])
        self.assertIs(lo["p2"]["held"], True)
        self.assertIsNone(ai.late_operating(ANNUAL, LATE)["rows"][0]["where_last"])

    def test_extra(self):
        ex = ai.extra(ANNUAL, LAST, HISTORY)
        self.assertEqual([r["key"] for r in ex["rows"]], ["1/B", "13/3"])
        b, h = ex["rows"]
        self.assertEqual((b["plant_listed"], b["last_year"], b["last_where"], b["retirement_year"]),
                         (True, None, None, 2010))
        self.assertEqual((h["plant_listed"], h["last_year"], h["last_where"], h["nameplate_mw"]),
                         (False, 2024, "Retired and Canceled RE", 2))
        self.assertEqual((ex["n"], ex["plant_not_listed"], ex["mw"], ex["mw_plant_not_listed"]), (2, 1, 6.0, 2.0))
        self.assertEqual(ex["plant_listed"], [{"value": "False", "n": 1}, {"value": "True", "n": 1}])
        self.assertEqual(ex["last_year"], [{"value": "-", "n": 1}, {"value": "2024", "n": 1}])
        self.assertEqual(ex["years_plant_not_listed"], [{"value": "2003", "n": 1}])
        self.assertEqual(ex["years_plant_listed"], [{"value": "2010", "n": 1}])
        self.assertIs(ex["p1"]["held"], False)

    def test_render(self):
        res = {"files": [{"year": 2025, "url": "u", "cached": True, "bytes": 9, "md5": "a", "errors": [],
                          "sheets": [{"sheet": "Operable", "header_row": 1, "rows": 1}]}],
               "monthly_files": [{"month": "2025-12", "member": "w.xlsx", "bytes": 8, "md5": "b", "errors": []}],
               "leavers": [{"month": "2024-01", "key": "1439/1A", "years": [an.leaver_row(ANNUAL, 2025, "1439/1A")]}],
               "focus": {p: {"annual": {"2025": ai.plant_rows(ANNUAL, p)}, "monthly": {}} for p, _ in ai.FOCUS},
               "late_operating": ai.late_operating(ANNUAL, LATE, LAST),
               "extra": ai.extra(ANNUAL, LAST, HISTORY)}
        md = ai.render(res)
        self.assertIn("| annual 2025 | u | True | 9 | a | none |", md)
        self.assertIn("| monthly 2025-12 | w.xlsx | - | 8 | b | none |", md)
        self.assertIn("| 1439/1A | 2024-01 | not listed |", md)
        self.assertIn("- annual 2025: no rows", md)
        self.assertIn("Generators: 1 (20.0 MW). Retirement years by the annual file: 2025 1.", md)
        self.assertIn("P2 (more than half retired in 2025 by the annual file): 1 of 1; held.", md)
        self.assertIn("Generators: 2 (6.0 MW). Plant on a sheet of the annual 2025 file: False 1; True 1.", md)
        self.assertIn("At plants on no sheet: 1 (2.0 MW); retirement years: 2003 1.", md)
        self.assertIn("Last earlier annual file (2016 to 2024) that lists them: - 1; 2024 1. "
                      "How it lists them: - 1; Retired and Canceled RE 1.", md)
        self.assertIn("P1 (more than half at plants the annual 2025 file lists on no sheet): 1 of 2; failed.", md)


if __name__ == "__main__":
    unittest.main()
