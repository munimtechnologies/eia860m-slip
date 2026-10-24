"""Tests for monthrun.py. MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import tempfile
import unittest
import zipfile

import monthrun as mr


class MonthsTests(unittest.TestCase):
    def test_consecutive(self):
        self.assertIsNone(mr.check_months("2026-08", ["2026-09", "2026-10"]))

    def test_year_end(self):
        self.assertIsNone(mr.check_months("2026-11", ["2026-12", "2027-01"]))

    def test_gap(self):
        self.assertEqual(mr.check_months("2026-08", ["2026-10"]), "2026-10 given where 2026-09 was expected")

    def test_none(self):
        self.assertEqual(mr.check_months("2026-08", []), "no EIA month given")


class P5Tests(unittest.TestCase):
    def test_rule(self):
        scan = [{"technology": "Nuclear", "retirement_year": 1990, "sheet": "Retired"},
                {"technology": "Nuclear", "retirement_year": 2001, "sheet": "Retired"},
                {"technology": "Nuclear", "retirement_year": 2002, "sheet": "Retired"},
                {"technology": "Nuclear", "retirement_year": 2013, "sheet": "Retired"},
                {"technology": "Nuclear", "retirement_year": None, "sheet": "Retired"},
                {"technology": "Conventional Steam Coal", "retirement_year": 1990, "sheet": "Retired"},
                {"technology": None, "retirement_year": 1980, "sheet": "Operating"}]
        self.assertEqual([r["retirement_year"] for r in mr.p5_rows(scan)], [1990, 2001])


class S3Tests(unittest.TestCase):
    def row(self, month, key, event, sheet=""):
        return {"report_month": month, "key": key, "event": event, "sheet": sheet}

    def test_listed_again(self):
        rows = [self.row("2026-08", "1/1", "first", "Retired"), self.row("2026-08", "2/1", "first", "Retired"),
                self.row("2026-09", "1/1", "left"), self.row("2026-09", "2/1", "left"),
                self.row("2026-10", "2/1", "back", "Operating")]
        keys = ("1/1", "2/1", "3/1")
        self.assertEqual(mr.s3_back(rows, "2026-10", keys), ["2/1"])
        self.assertEqual(mr.s3_back(rows, "2026-09", keys), [])
        self.assertEqual(mr.s3_back(rows, "2026-08", keys), ["1/1", "2/1"])

    def test_constants(self):
        self.assertEqual(len(mr.S3_KEYS), 16)
        self.assertEqual(mr.S3_MAX, 3)
        self.assertEqual(mr.NUCLEAR_BEFORE, 2002)
        self.assertEqual(mr.PLAN_BAND["2026-10"], (0.219512, 0.473958))


class CohortTests(unittest.TestCase):
    def test_first_listing(self):
        stats = [{"month": "2026-08", "detail": [{"key": "A"}]},
                 {"month": "2026-09", "detail": [{"key": "A"}, {"key": "B"}]},
                 {"month": "2026-10", "detail": [{"key": "B"}, {"key": "C"}]}]
        self.assertEqual(mr.first_listing(stats, "2026-09"), {"A": False, "B": True})
        self.assertEqual(mr.first_listing(stats, "2026-10"), {"B": False, "C": True})
        self.assertEqual(mr.first_listing(stats, "2026-11"), {})

    def test_by_tech(self):
        detail = [{"key": "A", "now": "Operating"}, {"key": "B", "now": "Planned"}, {"key": "C", "now": "Operating"}]
        techs = {"A": "Solar Photovoltaic", "B": "Solar Photovoltaic", "C": "Batteries"}
        first = {"A": True, "B": False, "C": False}
        got = [(x["group"], x["listing"], x["cohort"], x["operating"]) for x in mr.by_tech(detail, techs, first)]
        self.assertEqual(got, [("solar", "first", 1, 1), ("solar", "repeat", 1, 0), ("solar", "all", 2, 1),
                               ("batteries", "repeat", 1, 1), ("batteries", "all", 1, 1),
                               ("all", "first", 1, 1), ("all", "repeat", 2, 1), ("all", "all", 3, 2)])

    def test_by_tech_missing_technology(self):
        got = mr.by_tech([{"key": "A", "now": "absent"}], {}, {})
        self.assertEqual([(x["group"], x["listing"], x["cohort"]) for x in got],
                         [("other", "repeat", 1), ("other", "all", 1), ("all", "repeat", 1), ("all", "all", 1)])


class BandTests(unittest.TestCase):
    def test_same(self):
        b = mr.band_check({"band": (9 / 41, 91 / 192)}, "2026-10")
        self.assertTrue(b["same"])

    def test_differs(self):
        self.assertFalse(mr.band_check({"band": (0.22, 0.47)}, "2026-10")["same"])
        self.assertFalse(mr.band_check({"band": None}, "2026-10")["same"])

    def test_no_plan_band(self):
        self.assertIsNone(mr.band_check({"band": (0.2, 0.4)}, "2026-09"))


class ExpectTests(unittest.TestCase):
    def setUp(self):
        self.t = {"listed": 38162, "events": {"left": 20}, "left_by_sheet": {"Retired": 16}, "cohort": 170,
                  "cohort_by": {"Operating": 57}}
        self.score = {"predictions": [{"id": "P1", "held": True}, {"id": "P2", "held": True},
                                      {"id": "P3", "held": False}, {"id": "P4", "held": True},
                                      {"id": "P5", "held": True}]}

    def test_all_same(self):
        e = mr.expect_check("2026-09", self.t, {"listed": 38011}, self.score, 0, 28, 0)
        self.assertTrue(all(v[2] for v in e.values()))
        self.assertEqual(len(e), 10)

    def test_one_differs(self):
        e = mr.expect_check("2026-09", self.t, {"listed": 38011}, self.score, 0, 16, 0)
        self.assertEqual([k for k, v in e.items() if not v[2]], ["p5_before"])

    def test_target_missing(self):
        e = mr.expect_check("2026-09", None, None, self.score, None, None, None)
        self.assertFalse(e["listed"][2])

    def test_no_expectation(self):
        self.assertIsNone(mr.expect_check("2026-10", self.t, None, self.score, 0, 0, 0))


class FileTests(unittest.TestCase):
    def test_month_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "eia860m-2026.zip")
            with zipfile.ZipFile(p, "w") as zf:
                zf.writestr("august_generator2026.xlsx", b"aug")
            paths = [(2026, p)]
            self.assertEqual(mr.month_bytes("2026-09", {"2026-09": b"sep"}, paths), (b"sep", "EIA's site"))
            self.assertEqual(mr.month_bytes("2026-08", {}, paths), (b"aug", "PUDL archive: august_generator2026.xlsx"))
            self.assertEqual(mr.month_bytes("2026-07", {}, paths), (None, "not in the zip"))
            self.assertEqual(mr.month_bytes("2025-08", {}, paths), (None, "no zip"))

    def test_scan_month_bad_bytes(self):
        book, scan, why = mr.scan_month(b"not a workbook")
        self.assertIsNone(book)
        self.assertIsNone(scan)
        self.assertTrue(why)


if __name__ == "__main__":
    unittest.main()
