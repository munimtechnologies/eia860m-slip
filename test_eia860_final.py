"""Tests for eia860_final.py (MV2 of Munim, Inc., made with AI agents). Apache-2.0.

The tests need pandas and openpyxl (the tool does too). Where they are not installed
the tests are skipped, so a test host without them reports skipped, not failed.
"""

import os
import tempfile
import unittest
import zipfile

try:
    import openpyxl  # noqa: F401  (write_zip builds the test workbook with it)
    import pandas as pd
    import eia860_final as ef
except ImportError:  # no pandas or openpyxl on this host
    pd = None
    ef = None

needs_pandas = unittest.skipIf(pd is None, "pandas or openpyxl is not installed")

OP_HEAD = ["Utility ID", "Plant Code", "Generator ID", "Nameplate Capacity (MW)", "Summer  Capacity (MW)",
           "Operating Year", "Energy Source 1", "Status"]
RT_HEAD = OP_HEAD + ["Retirement Year"]


def sheet(head, rows):
    title = ["Form EIA-860 Data - Schedule 3, 'Generator Data'"] + [None] * (len(head) - 1)
    note = ["NOTE: test footnote"] + [None] * (len(head) - 1)
    return pd.DataFrame([title, head] + rows + [note])


OPERABLE = [[1, 10, "A", 100.0, 90.0, 2030, "SUN", "OP"],
            [1, 11, "B", 50.0, 45.0, 2030, "NG", "OP"],
            [1, 12, "C", 30.0, " ", 2030, "WND", "OP"],
            [1, 13, "D", 500.0, 480.0, 2010, "BIT", "OP"]]
RETIRED = [[1, 20, "E", 200.0, 190.0, 1980, "BIT", "RE", 2030],
           [1, 21, "F", 20.0, 18.0, 2030, "NG", "RE", 2030],
           [1, 22, "G", 40.0, 40.0, None, "SUN", "CN", 2030],
           [1, 23, "H", 60.0, 55.0, 1990, "NG", "RE", 2029]]


def write_zip(d, year=2030):
    xlsx = os.path.join(d, "3_1_Generator_Y%d.xlsx" % year)
    with pd.ExcelWriter(xlsx, engine="openpyxl") as w:
        sheet(OP_HEAD, OPERABLE).to_excel(w, sheet_name="Operable", header=False, index=False)
        sheet(OP_HEAD, []).to_excel(w, sheet_name="Proposed", header=False, index=False)
        sheet(RT_HEAD, RETIRED).to_excel(w, sheet_name="Retired and Canceled", header=False, index=False)
    path = os.path.join(d, "eia860%d.zip" % year)
    with zipfile.ZipFile(path, "w") as z:
        z.write(xlsx, "3_1_Generator_Y%d.xlsx" % year)
    os.remove(xlsx)
    return path


@needs_pandas
class TestParts(unittest.TestCase):
    def test_group_of(self):
        self.assertEqual(ef.group_of(" bit "), "coal")
        self.assertEqual(ef.group_of("SUB"), "coal")
        self.assertEqual(ef.group_of("NG"), "gas")
        self.assertEqual(ef.group_of("MWH"), "battery")
        self.assertEqual(ef.group_of("WAT"), "other")
        self.assertEqual(ef.group_of(float("nan")), "other")

    def test_with_header(self):
        df = ef.with_header(sheet(OP_HEAD, OPERABLE))
        self.assertEqual(len(df), 4)
        self.assertIn("summer capacity (mw)", df.columns)
        self.assertEqual(ef.col(df, "summer capacity (mw)"), "summer capacity (mw)")
        with self.assertRaises(ValueError):
            ef.with_header(pd.DataFrame([["a", "b"], [1, 2]]))

    def test_sums(self):
        s = ef.sums(ef.with_header(sheet(OP_HEAD, OPERABLE[:3])))
        self.assertEqual(s["total"], {"summer_mw": 135.0, "nameplate_mw": 180.0, "n": 3})
        self.assertEqual(s["wind"]["summer_mw"], 0.0)
        self.assertNotIn("coal", s)

    def test_sums_empty(self):
        df = ef.with_header(sheet(OP_HEAD, []))
        self.assertEqual(ef.sums(df), {"total": {"summer_mw": 0.0, "nameplate_mw": 0.0, "n": 0}})


@needs_pandas
class TestYear(unittest.TestCase):
    def test_year_summary(self):
        with tempfile.TemporaryDirectory() as d:
            s = ef.year_summary(write_zip(d), 2030)
        self.assertEqual(s["additions"]["total"]["summer_mw"], 135.0)
        self.assertEqual(s["additions"]["solar"]["n"], 1)
        self.assertEqual(s["additions_built_and_retired_same_year"]["total"]["summer_mw"], 18.0)
        self.assertEqual(s["retirements"]["total"], {"summer_mw": 208.0, "nameplate_mw": 220.0, "n": 2})
        self.assertEqual(s["retirements"]["coal"]["summer_mw"], 190.0)
        self.assertNotIn("solar", s["retirements"])
        self.assertEqual(s["rows"], {"operable": 4, "retired_sheet": 4, "retired_status_re": 3})
        self.assertEqual(s["retired_sheet_status"], {"RE": 3, "CN": 1})

    def test_find_zip(self):
        with tempfile.TemporaryDirectory() as d:
            sub = os.path.join(d, "x")
            os.makedirs(sub)
            path = write_zip(sub, 2031)
            with open(os.path.join(d, "readme.txt"), "w") as fh:
                fh.write("not a zip")
            self.assertEqual(ef.find_zip(d, 2031), path)
            self.assertIsNone(ef.find_zip(d, 2032))


@needs_pandas
class TestScoring(unittest.TestCase):
    def summary(self, add_total, ret_total):
        return {"additions": {"total": {"summer_mw": add_total}, "solar": {"summer_mw": 27950.0}},
                "retirements": {"total": {"summer_mw": ret_total}, "coal": {"summer_mw": 2700.0}}}

    def test_calibrate_and_gate(self):
        epa = {"additions": {"total": 1000.0}, "retirements": {"total": 200.0, "coal": 100.0}}
        cal = ef.calibrate(self.summary(1005.0, 199.0), epa)
        self.assertAlmostEqual(cal["additions_total"]["rel_diff"], 0.005)
        self.assertEqual(cal["retirements_coal"]["rel_diff"], 26.0)
        # Only totals gate: the coal row is far off here, yet the gate passes.
        self.assertTrue(ef.gate({2023: cal, 2024: cal}))
        bad = ef.calibrate(self.summary(1020.0, 199.0), epa)
        self.assertFalse(ef.gate({2023: cal, 2024: bad}))
        self.assertFalse(ef.gate({}))

    def test_score(self):
        r = ef.score(self.summary(55200.0, 5000.0))
        self.assertTrue(r["additions_total"]["in_range"])
        self.assertFalse(r["retirements_total"]["in_range"])
        self.assertTrue(r["additions_solar"]["in_range"])
        self.assertAlmostEqual(r["additions_total"]["of_plan"], round(55200.0 / 63000.0, 4))
        self.assertAlmostEqual(r["retirements_coal"]["revision_vs_first"], round(2700.0 / 2600.0 - 1, 4))
        self.assertEqual(r["additions_wind"]["computed_mw"], 0.0)
        self.assertNotIn("in_range", r["additions_wind"])

    def test_markdown(self):
        result = {"gate_passed": True, "errors": {2023: "boom"},
                  "calibration": {2024: ef.calibrate(self.summary(50454.0, 9027.4), ef.EPA[2024])},
                  "score_2025": ef.score(self.summary(55120.0, 5000.0))}
        text = ef.to_markdown(result)
        self.assertIn("**passed**", text)
        self.assertIn("| additions_total | 50454.0 | 50454.0 | +0.00% |", text)
        # 55120 = 1.04 x 53000, so the revision prints without a rounding edge.
        self.assertIn("| additions_total | 55120.0 | 63000.0 | 87.5% | 53000.0 | +4.0% | 55000-55500 | True |", text)
        self.assertIn("Error for 2023: boom", text)


if __name__ == "__main__":
    unittest.main()
