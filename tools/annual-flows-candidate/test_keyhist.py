"""Unit tests for keyhist.py. MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import hashlib
import os
import tempfile
import unittest

import pandas as pd

import keyhist as kh
import watchlist as wl

M = wl.parse_month


def wrow(sheet, status, planned, mw):
    return {"sheet": sheet, "status": status, "planned": planned, "mw": mw}


def prow(status, planned, mw, report="2026-01"):
    return {"report": report, "status": status, "planned": planned, "mw": mw}


class SameTests(unittest.TestCase):
    def test_absent(self):
        self.assertTrue(kh.same(None, None))
        self.assertFalse(kh.same(None, prow("U", "2026-09", 14.0)))
        self.assertFalse(kh.same(wrow("Planned", "U", "2026-09", 14.0), None))

    def test_canceled_counts_as_absent(self):
        self.assertTrue(kh.same(wrow("Canceled or Postponed", "CN", None, 5.0), None))
        self.assertFalse(kh.same(wrow("Canceled or Postponed", "CN", None, 5.0),
                                 prow("U", "2026-09", 5.0)))

    def test_fields(self):
        p = prow("U", "2026-09", 14.0)
        self.assertTrue(kh.same(wrow("Planned", "U", "2026-09", 14.0), p))
        self.assertFalse(kh.same(wrow("Planned", "U", "2026-10", 14.0), p))
        self.assertFalse(kh.same(wrow("Planned", "V", "2026-09", 14.0), p))
        self.assertTrue(kh.same(wrow("Planned", "U", "2026-09", 14.04), p))
        self.assertFalse(kh.same(wrow("Planned", "U", "2026-09", 14.1), p))

    def test_planned_month_only_on_planned_sheet(self):
        self.assertTrue(kh.same(wrow("Operating", "OP", None, 5.0), prow("OP", "2025-01", 5.0)))


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({
            "key": ["1/A", "2/B"],
            "report_m": [float(M("2026-01")), float(M("2026-02"))],
            "until_m": [float(M("2026-03")), float(M("2026-02"))],
            "status": ["U", "T"],
            "planned_m": [float(M("2026-09")), float(M("2027-01"))],
            "capacity_mw": [14.0, 5.0]})

        def frame(rows):
            return pd.DataFrame(rows, columns=["key", "sheet", "status", "planned_m", "capacity_mw"])

        self.frames = {
            "2026-01": frame([["1/A", "Planned", "U", float(M("2026-09")), 14.0]]),
            "2026-02": frame([["1/A", "Planned", "U", float(M("2026-10")), 14.0],
                              ["2/B", "Planned", "T", float(M("2027-01")), 5.0]]),
            "2026-03": frame([["1/A", "Planned", "U", float(M("2026-10")), 14.0],
                              ["2/B", "Canceled or Postponed", "CN", None, 5.0]])}
        self.months = ["2026-01", "2026-02", "2026-03"]

    def test_stale_record(self):
        h = kh.history("1/A", self.frames, self.df, self.months)
        self.assertEqual([r["same"] for r in h["months"]], [True, False, False])
        self.assertEqual(h["first_differs"], "2026-02")
        self.assertEqual(h["months_differ"], 2)
        self.assertEqual([r["pudl_as_workbook_of"] for r in h["months"]],
                         [[], ["2026-01"], ["2026-01"]])
        self.assertEqual(h["months"][1]["pudl"], prow("U", "2026-09", 14.0))
        self.assertEqual(h["months"][1]["workbook"], wrow("Planned", "U", "2026-10", 14.0))

    def test_ends_on_canceled_sheet(self):
        h = kh.history("2/B", self.frames, self.df, self.months)
        self.assertEqual([r["same"] for r in h["months"]], [True, True, True])
        self.assertIsNone(h["first_differs"])
        self.assertIsNone(h["months"][0]["workbook"])
        self.assertIsNone(h["months"][2]["pudl"])
        self.assertEqual(h["months"][2]["workbook"]["sheet"], "Canceled or Postponed")

    def test_for_compare(self):
        f = kh.for_compare(self.frames["2026-03"].assign(technology_description="Batteries"))
        self.assertEqual(list(f["key"]), ["1/A"])
        self.assertIn("technology", f.columns)
        self.assertNotIn("technology_description", f.columns)

    def test_render(self):
        h = kh.history("1/A", self.frames, self.df, self.months)
        fields = {"status": {"agree": 2, "compared": 2}, "planned_month": {"agree": 1, "compared": 2},
                  "capacity": {"agree": 2, "compared": 2}}
        res = {"pudl_source": "x.parquet", "pudl_max": "2026-03", "zip": {"cached": True},
               "months": [{"month": "2026-01", "compare": {
                   "workbook_keys": 3, "pudl_keys": 2, "both": 2, "workbook_only": 1,
                   "pudl_only": 0, "fields": fields}}, {"month": "2026-02"}],
               "keys": [h]}
        md = kh.render(res)
        self.assertIn("| 2026-01 | 3 | 2 | 2 | 1 | 0 | 2 of 2 | 1 of 2 | 2 of 2 |", md)
        self.assertIn("| 2026-02 | not read | | | | | | | |", md)
        self.assertIn("| 1/A | 2026-02 | 2 of 3 |", md)
        self.assertIn("| 2026-02 | Planned: U, 2026-10, 14.0 MW | U, 2026-09, 14.0 MW (from 2026-01) "
                      "| False | 2026-01 |", md)
        self.assertIn("Not run: x", kh.render(dict(res, error="x")))


class ZipTests(unittest.TestCase):
    def test_kept_copy_with_right_md5_is_used(self):
        body = b"not really a zip"
        old = kh.ZIP_MD5
        kh.ZIP_MD5 = hashlib.md5(body).hexdigest()
        try:
            with tempfile.TemporaryDirectory() as d:
                with open(os.path.join(d, "zenodo-%s-%s" % (kh.RECORD, kh.ZIP)), "wb") as fh:
                    fh.write(body)
                data, info = kh.get_zip(d)
        finally:
            kh.ZIP_MD5 = old
        self.assertEqual(data, body)
        self.assertTrue(info["cached"])
        self.assertEqual(info["tried"], [])


if __name__ == "__main__":
    unittest.main()
