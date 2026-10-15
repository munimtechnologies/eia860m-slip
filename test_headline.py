"""Tests for headline.py (MV2 of Munim, Inc., made with AI agents). Apache-2.0. Standard library only."""

import os
import tempfile
import unittest

import headline


def row(year, tech, kind, gw, bound="=", published="2025-01-01"):
    return {"year": year, "tech": tech, "kind": kind, "gw": gw, "bound": bound,
            "published": published, "source": "https://www.eia.gov/x", "basis": ""}


class TestData(unittest.TestCase):
    def setUp(self):
        self.rows = headline.load()

    def test_rows_are_well_formed(self):
        self.assertGreater(len(self.rows), 50)
        seen = set()
        for r in self.rows:
            self.assertIn(r["kind"], headline.KINDS)
            self.assertIn(r["bound"], headline.BOUNDS)
            self.assertIn(r["tech"], headline.TECHS)
            self.assertGreater(r["gw"], 0.0)
            self.assertTrue(r["source"].startswith("https://www.eia.gov/"), r["source"])
            self.assertTrue(r["basis"])
            key = (r["year"], r["tech"], r["kind"], r["published"])
            self.assertNotIn(key, seen)
            seen.add(key)

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


if __name__ == "__main__":
    unittest.main()
