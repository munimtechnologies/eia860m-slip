"""Tests for headline.py (MV2 of Munim, Inc., made with AI agents). Apache-2.0. Standard library only."""

import os
import tempfile
import unittest

import headline


def row(year, tech, kind, gw, bound="=", published="2025-01-01"):
    return {"year": year, "tech": tech, "kind": kind, "gw": gw, "bound": bound,
            "published": published, "source": "https://www.eia.gov/x", "basis": ""}


def check_well_formed(case, rows, at_least):
    case.assertGreater(len(rows), at_least)
    seen = set()
    for r in rows:
        case.assertIn(r["kind"], headline.KINDS)
        case.assertIn(r["bound"], headline.BOUNDS)
        case.assertIn(r["tech"], headline.TECHS)
        case.assertGreater(r["gw"], 0.0)
        case.assertTrue(r["source"].startswith("https://www.eia.gov/"), r["source"])
        case.assertTrue(r["basis"])
        key = (r["year"], r["tech"], r["kind"], r["published"])
        case.assertNotIn(key, seen)
        seen.add(key)


class TestData(unittest.TestCase):
    def setUp(self):
        self.rows = headline.load()

    def test_rows_are_well_formed(self):
        check_well_formed(self, self.rows, 50)

    def test_every_year_has_a_total_plan(self):
        for year in range(2020, 2027):
            self.assertIsNotNone(headline.plan(self.rows, year, "total"), year)

    def test_final_beats_later_and_first(self):
        a = headline.best_actual(self.rows, 2024, "solar")
        self.assertEqual(a["kind"], "actual_final")
        self.assertAlmostEqual(a["gw"], 30.916)

    def test_value_beats_bound(self):
        # 2020 wind: a later '> 14 GW' and a first estimate of 20.9 GW.
        a = headline.best_actual(self.rows, 2020, "wind")
        self.assertEqual((a["kind"], a["gw"]), ("actual_first", 20.9))
        a = headline.best_actual(self.rows, 2025, "wind")
        self.assertEqual(a["bound"], "<")

    def test_ratios(self):
        t = {(x["year"], x["tech"]): x for x in headline.realization(self.rows)}
        self.assertAlmostEqual(t[(2023, "total")]["ratio"], 40.4 / 54.5)
        self.assertAlmostEqual(t[(2023, "solar")]["ratio"], 19.0 / 29.1)
        self.assertAlmostEqual(t[(2024, "total")]["ratio"], 50.454 / 62.8)
        self.assertAlmostEqual(t[(2025, "battery")]["ratio"], 15.0 / 18.2)
        self.assertAlmostEqual(t[(2021, "wind")]["ratio"], 17.1 / 12.2)
        self.assertIsNone(t[(2026, "total")]["ratio"])
        self.assertIsNone(t[(2020, "total")]["ratio"])

    def test_projection_2026(self):
        p = headline.projection(self.rows, 2026, (2023, 2024, 2025))
        lo, hi, n = p["total"]
        self.assertAlmostEqual(lo, 86.0 * 40.4 / 54.5)
        self.assertAlmostEqual(hi, 86.0 * 53.0 / 63.0)
        self.assertEqual(n, 3)
        lo, hi, n = p["solar"]
        self.assertAlmostEqual(lo, 43.4 * 19.0 / 29.1)
        self.assertAlmostEqual(hi, 43.4 * 30.916 / 36.4)
        # 2025 wind is only a bound, so 2024 is the one year used.
        self.assertEqual(p["wind"][2], 1)
        self.assertNotIn("nuclear", p)

    def test_markdown(self):
        text = headline.to_markdown(self.rows, 2026, (2023, 2024, 2025))
        self.assertIn("| 2023 | total | 54.5 | 40.4 | actual_first | 74% |", text)
        self.assertIn("| 2025 | wind | 7.7 | < 5.9 | actual_first | < 77% |", text)
        self.assertIn("| total | 86 | 63.8 | 72.3 | 3 |", text)


class TestRetirements(unittest.TestCase):
    def setUp(self):
        self.rows = headline.load(headline.RETIREMENTS_CSV)

    def test_rows_are_well_formed(self):
        check_well_formed(self, self.rows, 35)

    def test_every_year_has_a_total_plan(self):
        for year in range(2020, 2027):
            self.assertIsNotNone(headline.plan(self.rows, year, "total"), year)

    def test_which_actual(self):
        # 2024: the Electric Power Annual (9.03 GW) beats the first article (7.5 GW).
        a = headline.best_actual(self.rows, 2024, "total")
        self.assertEqual((a["kind"], a["gw"]), ("actual_final", 9.0274))
        # 2022 coal: the 2026 article's 13.7 GW beats the 2023 article's 11.5 GW.
        self.assertEqual(headline.best_actual(self.rows, 2022, "coal")["gw"], 13.7)
        # The STEO row is a forecast, never an actual.
        self.assertEqual(headline.best_actual(self.rows, 2025, "coal")["gw"], 2.6)

    def test_ratios(self):
        t = {(x["year"], x["tech"]): x for x in headline.realization(self.rows)}
        self.assertAlmostEqual(t[(2023, "total")]["ratio"], 13.5 / 15.6)
        self.assertAlmostEqual(t[(2024, "total")]["ratio"], 9.0274 / 5.2)
        self.assertAlmostEqual(t[(2025, "total")]["ratio"], 4.6 / 12.3)
        self.assertAlmostEqual(t[(2021, "coal")]["ratio"], 5.6 / 2.7)
        self.assertAlmostEqual(t[(2024, "gas")]["ratio"], 4.2692 / 2.4)
        self.assertAlmostEqual(t[(2021, "nuclear")]["ratio"], 0.965 / 5.1)
        self.assertEqual(t[(2023, "coal")]["bound"], "~")
        self.assertIsNone(t[(2022, "total")]["ratio"])

    def test_projection_2026(self):
        p = headline.projection(self.rows, 2026, (2023, 2024, 2025))
        lo, hi, n = p["total"]
        self.assertAlmostEqual(lo, 11.0 * 4.6 / 12.3)
        self.assertAlmostEqual(hi, 11.0 * 9.0274 / 5.2)
        self.assertEqual(n, 3)
        lo, hi, n = p["coal"]
        self.assertAlmostEqual(lo, 6.4 * 2.6 / 8.1)
        self.assertAlmostEqual(hi, 6.4 * 3.9586 / 2.3)
        self.assertEqual(n, 3)
        self.assertEqual(p["gas"][2], 1)
        self.assertNotIn("nuclear", p)

    def test_markdown(self):
        text = headline.to_markdown(self.rows, 2026, (2023, 2024, 2025))
        self.assertIn("| 2025 | total | 12.3 | 4.6 | actual_first | 37% |", text)
        self.assertIn("| 2024 | total | 5.2 | 9.0274 | actual_final | 174% |", text)
        self.assertIn("| 2023 | coal | 8.9 | 10.8 | actual_first | ~121% |", text)
        self.assertIn("| total | 11 | 4.1 | 19.1 | 3 |", text)
        self.assertIn("| coal | 6.4 | 2.1 | 11.0 | 3 |", text)


class TestRules(unittest.TestCase):
    def test_latest_within_a_kind(self):
        rows = [row(2030, "solar", "plan", 10.0),
                row(2030, "solar", "actual_later", 7.0, published="2031-03-01"),
                row(2030, "solar", "actual_later", 8.0, published="2032-03-01"),
                row(2030, "solar", "actual_first", 9.0, published="2031-02-01")]
        self.assertEqual(headline.best_actual(rows, 2030, "solar")["gw"], 8.0)

    def test_no_actual(self):
        rows = [row(2030, "gas", "plan", 2.0), row(2030, "gas", "steo", 1.0)]
        self.assertIsNone(headline.best_actual(rows, 2030, "gas"))
        self.assertEqual(headline.projection(rows, 2030, (2030,)), {})

    def test_main_writes_file(self):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "t.md")
            headline.main(["--out", out])
            with open(out, encoding="utf-8") as fh:
                self.assertIn("Range for 2026", fh.read())

    def test_main_retirements(self):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "r.md")
            headline.main(["--retirements", "--out", out])
            with open(out, encoding="utf-8") as fh:
                self.assertIn("| coal | 6.4 | 2.1 | 11.0 | 3 |", fh.read())


if __name__ == "__main__":
    unittest.main()
