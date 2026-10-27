"""Unit tests for nextlist.py (MV2 of Munim, Inc.; made with AI agents). Apache-2.0. Standard library only."""

import json
import os
import tempfile
import unittest

import nextlist as nl


def r(month, key, group="solar", now="Planned", cell=None):
    out = {"month": month, "key": key, "group": group, "now": now}
    if cell is not None:
        out["cell"] = cell
    return out


class Months(unittest.TestCase):
    def test_add_months_and_window(self):
        self.assertEqual(nl.add_months("2026-10", -1), "2026-09")
        self.assertEqual(nl.add_months("2026-01", -1), "2025-12")
        self.assertEqual(nl.add_months("2026-10", 3), "2027-01")
        self.assertEqual(nl.window("2026-10"), ("2022-10", "2026-09"))
        self.assertEqual(nl.window("2026-10", 2), ("2026-08", "2026-09"))


class Groups(unittest.TestCase):
    def test_tech_group(self):
        self.assertEqual(nl.tech_group("Solar Photovoltaic"), "solar")
        self.assertEqual(nl.tech_group("Batteries"), "batteries")
        self.assertEqual(nl.tech_group("Natural Gas Fired Combined Cycle"), "gas")
        self.assertEqual(nl.tech_group("Onshore Wind Turbine"), "wind")
        self.assertEqual(nl.tech_group("Conventional Hydroelectric"), "other")
        self.assertEqual(nl.tech_group(None), "other")

    def test_cells(self):
        rows = [r("2026-01", "1/A"), r("2026-02", "1/A"), r("2026-05", "1/A"), r("2027-09", "1/A"),
                r("2026-01", "2/B"), r("2026-06", "2/B")]
        got = {(x["key"], x["month"]): (x["prior"], x["cell"]) for x in nl.annotate(rows)}
        self.assertEqual(got[("1/A", "2026-01")], (0, "first"))
        self.assertEqual(got[("1/A", "2026-02")], (1, "1 month"))
        self.assertEqual(got[("1/A", "2026-05")], (2, "2-3 months"))
        self.assertEqual(got[("1/A", "2027-09")], (3, "more than 12 months"))
        self.assertEqual(got[("2/B", "2026-06")], (1, "4-12 months"))


class Rates(unittest.TestCase):
    rows = [r("2026-07", "9/Z", now="Operating", cell="first"),      # before the window
            r("2026-08", "1/A", now="Operating", cell="first"),
            r("2026-09", "2/B", cell="first"),
            r("2026-09", "3/C", now="Operating", cell="1 month"),
            r("2026-09", "4/D", group="gas", cell="first"),
            r("2026-10", "5/E", now="Operating", cell="first")]     # the target month itself

    def test_rates(self):
        t = nl.rates(self.rows, "2026-10", n=2)
        self.assertEqual(t[("solar", "first")], (1, 2))
        self.assertEqual(t[("solar", None)], (2, 3))
        self.assertEqual(t[(None, "first")], (1, 3))
        self.assertEqual(t[(None, None)], (2, 4))

    def test_forecast_fallbacks(self):
        t = nl.rates(self.rows, "2026-10", n=2)
        self.assertEqual(nl.forecast("solar", "first", t, 2), (0.5, "group and cell", 2))
        p, src, n = nl.forecast("solar", "1 month", t, 2)
        self.assertAlmostEqual(p, 2 / 3)
        self.assertEqual((src, n), ("group", 3))
        p, src, n = nl.forecast("wind", "first", t, 2)
        self.assertAlmostEqual(p, 1 / 3)
        self.assertEqual((src, n), ("cell", 3))
        self.assertEqual(nl.forecast("wind", "4-12 months", t, 2), (0.5, "all", 4))
        self.assertEqual(nl.forecast("solar", "first", t, 5), (0.5, "all", 4))

    def test_references(self):
        t = nl.rates(self.rows, "2026-10", n=2)
        r0, r1 = nl.references("solar", t, 2)
        self.assertAlmostEqual(r0, 0.5)
        self.assertAlmostEqual(r1, 2 / 3)
        self.assertEqual(nl.references("gas", t, 2), (0.5, 0.5))


class Backtest(unittest.TestCase):
    def test_no_leak(self):
        a = [r("2026-01", "1/A", now="Operating", cell="first"), r("2026-02", "2/B", cell="first")]
        bt = nl.backtest(a, start="2026-02", end="2026-02")
        self.assertEqual(len(bt), 1)
        self.assertEqual((bt[0]["key"], bt[0]["y"], bt[0]["p"], bt[0]["p_source"], bt[0]["r0"]),
                         ("2/B", 0, 1.0, "all", 1.0))
        s = nl.summary(bt)
        self.assertEqual(s["brier_p"], 1.0)


def scored_rows():
    return [{"key": "1/A", "y": 1, "p": 0.8, "r0": 0.5, "r1": 0.6, "nameplate_mw": 10.0},
            {"key": "2/B", "y": 0, "p": 0.2, "r0": 0.5, "r1": 0.4, "nameplate_mw": 30.0}]


class Scores(unittest.TestCase):
    def test_summary(self):
        s = nl.summary(scored_rows())
        self.assertEqual((s["rows"], s["plants"], s["on_time"]), (2, 2, 1))
        self.assertAlmostEqual(s["expected"], 1.0)
        self.assertAlmostEqual(s["brier_p"], 0.04)
        self.assertAlmostEqual(s["brier_r0"], 0.25)
        self.assertAlmostEqual(s["brier_r1"], 0.16)
        self.assertAlmostEqual(s["m_minus_r0"], -0.21)
        self.assertAlmostEqual(s["m_minus_r1"], -0.12)
        self.assertAlmostEqual(s["mw"], 40.0)
        self.assertAlmostEqual(s["mw_on_time"], 10.0)
        self.assertAlmostEqual(s["mw_expected"], 14.0)

    def test_boot(self):
        lo, hi = nl.boot(scored_rows(), "p", "r0", resamples=200)
        self.assertAlmostEqual(lo, -0.21)
        self.assertAlmostEqual(hi, -0.21)
        self.assertEqual(nl.boot(scored_rows(), "p", "r1", resamples=200),
                         nl.boot(scored_rows(), "p", "r1", resamples=200))
        self.assertEqual(nl.boot(scored_rows()[:1], "p", "r0"), (None, None))

    def test_score(self):
        listed = [dict(x) for x in scored_rows()] + [{"key": "3/C", "p": 0.5, "r0": 0.5, "r1": 0.5,
                                                      "nameplate_mw": 1.0}]
        rows, s = nl.score(listed, {"1/A": "Operating", "2/B": "Planned"})
        self.assertEqual((len(rows), s["missing"], s["on_time"]), (2, 1, 1))
        self.assertAlmostEqual(s["brier_p"], 0.04)
        self.assertAlmostEqual(s["interval_minus_r0"][0], -0.21)

    def test_calibration(self):
        rows = [{"p": 0.1, "y": 0}, {"p": 0.15, "y": 1}, {"p": 0.55, "y": 1}]
        c = nl.calibration(rows)
        self.assertEqual([(x["p_from"], x["rows"]) for x in c], [(0.0, 2), (0.5, 1)])
        self.assertAlmostEqual(c[0]["mean_p"], 0.125)
        self.assertAlmostEqual(c[0]["on_time"], 0.5)

    def test_read_outcomes(self):
        b = b"key,status_before,now\r\n1/A,V,Operating\r\n2/B,U,Planned\r\n"
        self.assertEqual(nl.read_outcomes(b), {"1/A": "Operating", "2/B": "Planned"})


class Lists(unittest.TestCase):
    def test_build_list(self):
        cohort = [r("2026-08", "1/K"), r("2026-09", "1/K"), r("2026-10", "3/K", now="Operating")]
        group = [{"key": "1/K", "group": "solar"}, {"key": "2/K", "group": "solar"}]
        got = {x["key"]: x for x in nl.build_list(cohort, "2026-10", group)}
        self.assertEqual(sorted(got), ["1/K", "2/K"])
        self.assertEqual((got["1/K"]["prior"], got["1/K"]["cell"]), (2, "1 month"))
        self.assertEqual((got["2/K"]["prior"], got["2/K"]["cell"]), (0, "first"))
        self.assertEqual((got["1/K"]["p"], got["1/K"]["p_source"], got["1/K"]["p_rows"]), (0.0, "all", 2))

    def test_keys_check(self):
        cohort = [{"month": "2026-09", "key": "1/A", "group": "solar"},
                  {"month": "2026-09", "key": "2/B", "group": "wind"},
                  {"month": "2026-08", "key": "3/C", "group": "solar"}]
        k = nl.keys_check([{"key": "1/A", "group": "solar"}, {"key": "2/B", "group": "gas"}], cohort, "2026-09")
        self.assertEqual((k["held"], k["cohort_rows"], k["group_differs"]), (True, 2, 1))
        k = nl.keys_check([{"key": "1/A", "group": "solar"}], cohort, "2026-09")
        self.assertEqual((k["held"], k["only_cohort"]), (False, ["2/B"]))

    def test_list_summary(self):
        s = nl.list_summary([{"key": "1/A", "p": 0.5, "nameplate_mw": 10.0},
                             {"key": "1/B", "p": 0.25, "nameplate_mw": None}])
        self.assertEqual((s["rows"], s["plants"]), (2, 1))
        self.assertAlmostEqual(s["expected"], 0.75)
        self.assertAlmostEqual(s["mw"], 10.0)
        self.assertAlmostEqual(s["mw_expected"], 5.0)


class Main(unittest.TestCase):
    def test_wrong_cohort_file(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "cohort.csv")
            with open(path, "w", newline="", encoding="utf-8") as fh:
                fh.write("month,key,technology,group,now,nameplate_mw,found\r\n"
                         "2026-09,1/A,Batteries,batteries,Planned,5,True\r\n")
            out = os.path.join(d, "out")
            self.assertEqual(nl.main(["--cohort", path, "--out-dir", out]), 2)
            with open(os.path.join(out, "nextlist.md"), encoding="utf-8") as fh:
                self.assertIn("Error: cohort file is not the one at commit ea63c15", fh.read())
            with open(os.path.join(out, "nextlist.json"), encoding="utf-8") as fh:
                self.assertFalse(json.load(fh)["cohort"]["same"])


if __name__ == "__main__":
    unittest.main()
