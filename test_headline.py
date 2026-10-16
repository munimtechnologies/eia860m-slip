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
        check_well_formed(self, self.rows, 120)

    def test_every_year_has_a_total_plan(self):
        for year in range(2020, 2027):
            self.assertIsNotNone(headline.plan(self.rows, year, "total"), year)

    def test_final_beats_later_and_first(self):
        a = headline.best_actual(self.rows, 2024, "solar")
        self.assertEqual(a["kind"], "actual_final")
        self.assertAlmostEqual(a["gw"], 30.916)

    def test_which_actual(self):
        # 2020 wind: the Electric Power Annual (14.66 GW) replaces the partly scheduled first count (20.9 GW).
        a = headline.best_actual(self.rows, 2020, "wind")
        self.assertEqual((a["kind"], a["gw"]), ("actual_final", 14.6649))
        # 2021 battery: only an upper bound (EIA-860 puts batteries in Other Energy Sources).
        a = headline.best_actual(self.rows, 2021, "battery")
        self.assertEqual((a["kind"], a["bound"]), ("actual_final", "<"))
        a = headline.best_actual(self.rows, 2025, "wind")
        self.assertEqual(a["bound"], "<")

    def test_ratios(self):
        t = {(x["year"], x["tech"]): x for x in headline.realization(self.rows)}
        self.assertAlmostEqual(t[(2020, "total")]["ratio"], 32.2382 / 42.0)
        self.assertAlmostEqual(t[(2020, "wind")]["ratio"], 14.6649 / 18.5)
        self.assertAlmostEqual(t[(2021, "wind")]["ratio"], 14.9314 / 12.2)
        self.assertAlmostEqual(t[(2022, "solar")]["ratio"], 11.0532 / 21.5)
        self.assertAlmostEqual(t[(2023, "total")]["ratio"], 42.318 / 54.5)
        self.assertAlmostEqual(t[(2023, "solar")]["ratio"], 18.8876 / 29.1)
        self.assertAlmostEqual(t[(2023, "battery")]["ratio"], 6.4 / 9.4)
        self.assertAlmostEqual(t[(2024, "total")]["ratio"], 50.454 / 62.8)
        self.assertAlmostEqual(t[(2025, "battery")]["ratio"], 15.0 / 18.2)
        self.assertEqual(t[(2022, "battery")]["bound"], "<")
        self.assertIsNone(t[(2026, "total")]["ratio"])
        self.assertIsNone(t[(2025, "gas")]["ratio"])

    def test_earlier_years(self):
        # 0.2.4: plans for 2016, 2018 and 2019 against the Electric Power Annual; no 2017 plan was found.
        t = {(x["year"], x["tech"]): x for x in headline.realization(self.rows)}
        self.assertAlmostEqual(t[(2019, "total")]["ratio"], 23.3017 / 23.7)
        self.assertAlmostEqual(t[(2018, "gas")]["ratio"], 19.3998 / 20.0)
        self.assertAlmostEqual(t[(2016, "wind")]["ratio"], 8.7541 / 6.8)
        self.assertEqual(t[(2016, "total")]["kind"], "actual_final")
        self.assertNotIn((2017, "total"), t)

    def test_projection_2026(self):
        p = headline.projection(self.rows, 2026, (2023, 2024, 2025))
        lo, hi, n = p["total"]
        self.assertAlmostEqual(lo, 86.0 * 42.318 / 54.5)
        self.assertAlmostEqual(hi, 86.0 * 53.0 / 63.0)
        self.assertEqual(n, 3)
        lo, hi, n = p["solar"]
        self.assertAlmostEqual(lo, 43.4 * 18.8876 / 29.1)
        self.assertAlmostEqual(hi, 43.4 * 30.916 / 36.4)
        # 2025 wind is only a bound, so 2023 and 2024 are the years used.
        lo, hi, n = p["wind"]
        self.assertAlmostEqual(lo, 11.8 * 5.154 / 8.2)
        self.assertAlmostEqual(hi, 11.8 * 6.5864 / 6.0)
        self.assertEqual(n, 2)
        self.assertEqual(p["gas"][2], 2)
        self.assertNotIn("nuclear", p)

    def test_markdown(self):
        text = headline.to_markdown(self.rows, 2026, (2023, 2024, 2025))
        self.assertIn("| 2023 | total | 54.5 | 42.318 | actual_final | 78% |", text)
        self.assertIn("| 2022 | wind | 7.6 | 9.1545 | actual_final | 120% |", text)
        self.assertIn("| 2021 | battery | 4.3 | < 3.2531 | actual_final | < 76% |", text)
        self.assertIn("| 2025 | wind | 7.7 | < 5.9 | actual_first | < 77% |", text)
        self.assertIn("| total | 86 | 66.8 | 72.3 | 3 |", text)
        self.assertIn("| wind | 11.8 | 7.4 | 13.0 | 2 |", text)


class TestRetirements(unittest.TestCase):
    def setUp(self):
        self.rows = headline.load(headline.RETIREMENTS_CSV)

    def test_rows_are_well_formed(self):
        check_well_formed(self, self.rows, 70)

    def test_every_year_has_a_total_plan(self):
        for year in range(2020, 2027):
            self.assertIsNotNone(headline.plan(self.rows, year, "total"), year)

    def test_which_actual(self):
        # 2024: the Electric Power Annual (9.03 GW) beats the first article (7.5 GW).
        a = headline.best_actual(self.rows, 2024, "total")
        self.assertEqual((a["kind"], a["gw"]), ("actual_final", 9.0274))
        # 2022 coal: the Electric Power Annual (13.68 GW) beats both articles (11.5 and 13.7 GW).
        a = headline.best_actual(self.rows, 2022, "coal")
        self.assertEqual((a["kind"], a["gw"]), ("actual_final", 13.6798))
        # 2023 coal: the final 9.22 GW replaces the derived 10.8 GW.
        a = headline.best_actual(self.rows, 2023, "coal")
        self.assertEqual((a["kind"], a["gw"], a["bound"]), ("actual_final", 9.2249, "="))
        # The STEO row is a forecast, never an actual.
        self.assertEqual(headline.best_actual(self.rows, 2025, "coal")["gw"], 2.6)

    def test_ratios(self):
        t = {(x["year"], x["tech"]): x for x in headline.realization(self.rows)}
        self.assertAlmostEqual(t[(2020, "total")]["ratio"], 16.3795 / 11.0)
        self.assertAlmostEqual(t[(2020, "coal")]["ratio"], 10.4567 / 5.8)
        self.assertAlmostEqual(t[(2022, "total")]["ratio"], 17.9391 / 14.9)
        self.assertAlmostEqual(t[(2023, "total")]["ratio"], 15.2379 / 15.6)
        self.assertAlmostEqual(t[(2024, "total")]["ratio"], 9.0274 / 5.2)
        self.assertAlmostEqual(t[(2025, "total")]["ratio"], 4.6 / 12.3)
        self.assertAlmostEqual(t[(2021, "coal")]["ratio"], 5.5618 / 2.7)
        self.assertAlmostEqual(t[(2024, "gas")]["ratio"], 4.2692 / 2.4)
        self.assertAlmostEqual(t[(2021, "nuclear")]["ratio"], 1.0394 / 5.1)
        self.assertEqual(t[(2023, "coal")]["bound"], "=")
        self.assertIsNone(t[(2025, "gas")]["ratio"])

    def test_earlier_years(self):
        # 0.2.4: 2019 coal retired at 287% of the January plan; 2018 has a coal plan but no total plan.
        t = {(x["year"], x["tech"]): x for x in headline.realization(self.rows)}
        self.assertAlmostEqual(t[(2019, "coal")]["ratio"], 12.8951 / 4.5)
        self.assertAlmostEqual(t[(2019, "total")]["ratio"], 20.0635 / 8.3)
        a = headline.best_actual(self.rows, 2018, "coal")
        self.assertEqual((a["kind"], a["gw"]), ("actual_final", 13.3042))
        self.assertNotIn((2018, "total"), t)

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
        lo, hi, n = p["gas"]
        self.assertAlmostEqual(lo, 4.6 * 5.128 / 6.2)
        self.assertAlmostEqual(hi, 4.6 * 4.2692 / 2.4)
        self.assertEqual(n, 2)
        self.assertNotIn("nuclear", p)

    def test_markdown(self):
        text = headline.to_markdown(self.rows, 2026, (2023, 2024, 2025))
        self.assertIn("| 2025 | total | 12.3 | 4.6 | actual_first | 37% |", text)
        self.assertIn("| 2024 | total | 5.2 | 9.0274 | actual_final | 174% |", text)
        self.assertIn("| 2023 | coal | 8.9 | 9.2249 | actual_final | 104% |", text)
        self.assertIn("| 2023 | total | 15.6 | 15.2379 | actual_final | 98% |", text)
        self.assertIn("| gas | 4.6 | 3.8 | 8.2 | 2 |", text)
        self.assertIn("| total | 11 | 4.1 | 19.1 | 3 |", text)
        self.assertIn("| coal | 6.4 | 2.1 | 11.0 | 3 |", text)


class TestRules(unittest.TestCase):
    def test_latest_within_a_kind(self):
        rows = [row(2030, "solar", "plan", 10.0),
                row(2030, "solar", "actual_later", 7.0, published="2031-03-01"),
                row(2030, "solar", "actual_later", 8.0, published="2032-03-01"),
                row(2030, "solar", "actual_first", 9.0, published="2031-02-01")]
        self.assertEqual(headline.best_actual(rows, 2030, "solar")["gw"], 8.0)

    def test_value_beats_bound(self):
        rows = [row(2030, "battery", "plan", 10.0),
                row(2030, "battery", "actual_final", 6.0, bound="<"),
                row(2030, "battery", "actual_first", 5.0, published="2031-02-01")]
        a = headline.best_actual(rows, 2030, "battery")
        self.assertEqual((a["kind"], a["gw"]), ("actual_first", 5.0))

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
