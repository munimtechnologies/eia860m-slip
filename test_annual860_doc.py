"""Checks the numbers in docs/annual-flows-eia860.md against the raw output of compete job
annual860-v2 (data/annual860_v2.json and docs/annual860-v2-unittests.txt). EIA's figures are quoted
from EIA and are not checked here. MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
YEARS = list(range(2017, 2026))


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8") as fh:
        return fh.read()


def tables(text):
    """Map each '## ' heading to the tables under it, each a list of {column: cell} rows."""
    out, head, cols = {}, None, None
    for line in text.splitlines():
        if line.startswith("## "):
            head, cols = line[3:].strip(), None
            out[head] = []
        elif line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if cols is None:
                cols = cells
                out.setdefault(head, []).append([])
            elif not all(c and set(c) <= set("-:") for c in cells):
                out[head][-1].append(dict(zip(cols, cells)))
        else:
            cols = None
    return out


def fmt(mw):
    return "{:,.1f}".format(mw)


def pct(a, b):
    return "{:.1f}%".format(100 * a / b)


class AnnualEia860DocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = read("docs", "annual-flows-eia860.md")
        cls.doc = tables(cls.text)
        cls.out = json.loads(read("data", "annual860_v2.json"))
        cls.log = read("docs", "annual860-v2-unittests.txt")
        cls.rows = {(r["year"], r["group"], r["state"]): r for r in cls.out["rows"]}

    def r(self, year, group="all", state="all"):
        return self.rows[(year, group, state)]

    def test_checks(self):
        c = self.out["checks"]
        self.assertTrue(c["all_pass"])
        for k in ("C1", "C2", "C3", "C4"):
            self.assertTrue(c[k]["pass"], k)
        self.assertEqual(c["C2"]["missing_columns"], [])
        ran = int(re.search(r"Ran (\d+) tests", self.log).group(1))
        self.assertEqual(len(re.findall(r" \.\.\. ok$", self.log, re.M)), ran)
        self.assertTrue(self.log.rstrip().endswith("OK"))
        got = c["C1"]["got"]
        years = self.out["meta"]["annual_report_years"]
        expected = {
            "C1": "%s MW planned, %s MW online in year; onshore wind %s MW, %s MW, %s MW slipped" % (
                fmt(got["all/all"]), fmt(got["all/online_in_year"]), fmt(got["wind_onshore/all"]),
                fmt(got["wind_onshore/online_in_year"]), fmt(got["wind_onshore/slipped"])),
            "C2": "none missing; report years %d-%d" % (years[0], years[-1]),
            "C3": "%d rows, %d not adding up" % (c["C3"]["rows"], c["C3"]["not_adding_up"]),
            "C4": "%.1f%% undated" % (100 * c["C4"]["undated_share_2017"]),
            "unit tests": "%d of %d passed" % (ran, ran),
        }
        rows = {x["check"]: x["result"] for x in self.doc["Checks (all passed)"][0]}
        self.assertEqual(rows, expected)
        self.assertIn("report years %d-%d" % (years[0], years[-1]), self.text)

    def test_predictions(self):
        p = self.out["predictions"]
        w, ws, a = self.r(2017, "wind_onshore"), self.r(2017, "wind_onshore", "slipped"), self.r(2017)
        rows = {x["prediction"]: x for x in self.doc["Predictions (all four failed)"][0]}
        self.assertEqual(sorted(rows), ["W1", "W2", "W3", "W4"])
        for k, x in (("W1", w), ("W2", ws), ("W3", a)):
            self.assertEqual(rows[k]["result"], "%.4f (%s of %s MW)" % (
                p[k]["share_860"], fmt(x["in_year"]), fmt(x["planned_mw"])))
            self.assertAlmostEqual(p[k]["share_860"], x["in_year"] / x["planned_mw"], places=4)
            self.assertLess(x["in_year"] / x["planned_mw"], p[k]["floor"])
        self.assertEqual(rows["W4"]["result"], "%d of %d years" % (
            len(p["W4"]["years_860_above_860m"]), len(p["W4"]["years"])))
        self.assertEqual(p["W4"]["years"], list(range(2017, 2025)))
        for k in rows:
            self.assertIs(p[k]["held"], False)
            self.assertEqual(rows[k]["verdict"], "failed")

    def test_year_table(self):
        rows = self.doc["Every year, all technologies (MW)"][0]
        self.assertEqual([int(x["year"]) for x in rows], YEARS)
        for x in rows:
            o = self.r(int(x["year"]))
            self.assertEqual(
                (x["planned"], x["delivered in EIA-860M"], x["in year by annual date"],
                 x["difference"], x["share_860m"], x["share_860"]),
                (fmt(o["planned_mw"]), fmt(o["delivered_860m_mw"]), fmt(o["in_year"]),
                 fmt(o["delivered_860m_mw"] - o["in_year"]), "%.3f" % o["share_860m"],
                 "%.3f" % o["share_860"]), x["year"])
            self.assertGreaterEqual(o["delivered_860m_mw"], o["in_year"])

    def test_stated_numbers(self):
        meta = self.out["meta"]
        mc, kept = meta["annual_maturity_counts"], meta["annual_rows_kept"]
        w, ws, a = self.r(2017, "wind_onshore"), self.r(2017, "wind_onshore", "slipped"), self.r(2017)
        diffs = {y: self.r(y)["delivered_860m_mw"] - self.r(y)["in_year"] for y in YEARS}
        lo, hi = min(diffs, key=diffs.get), max(diffs, key=diffs.get)
        self.assertLess(max(diffs[y] / self.r(y)["planned_mw"] for y in YEARS), 0.04)
        g22 = self.r(2022, "gas_cc")
        stated = [
            "%s of the January 2017 EIA-860M plan" % pct(a["delivered_860m_mw"], a["planned_mw"]),
            "%s of its onshore wind" % pct(w["delivered_860m_mw"], w["planned_mw"]),
            "{:,} bytes".format(meta["annual_bytes"]),
            "{:,} `monthly_update` and {:,} `incremental_ytd` rows".format(
                mc["monthly_update"], mc["incremental_ytd"]),
            "{:,} rows were kept, {:,} marked `final` and {} with no `data_maturity` value".format(
                kept, mc["final"], kept - mc["final"]),
            "%s MW came online in 2017 by the annual operating date, against %s MW by EIA-860M" % (
                fmt(a["in_year"]), fmt(a["delivered_860m_mw"])),
            "identical: %s MW" % fmt(w["in_year"]),
            "Of the %s MW, the annual record dates %s MW to 2018 and %s MW to later years, and lists "
            "%s MW that never operated" % (fmt(ws["planned_mw"]), fmt(ws["next_year"]),
                                           fmt(ws["later"]), fmt(ws["never"])),
            "by %s MW (%d) to %s MW (%d)" % (fmt(diffs[lo]), lo, fmt(diffs[hi]), hi),
            "under 4% of the year's planned MW",
            "share is %.3f in EIA-860M, %.3f by the annual date" % (g22["share_860m"],
                                                                    g22["share_860"]),
            "%s MW in 2024, %s MW in 2025" % (fmt(self.r(2024)["never"]), fmt(self.r(2025)["never"])),
            "%s MW of the 2017 plan has no annual record" % fmt(a["not_in_860"]),
        ]
        for s in stated:
            self.assertIn(s, self.text, s)
        self.assertEqual(w["in_year"], w["delivered_860m_mw"])
        self.assertEqual((ws["before"], ws["in_year"], ws["undated"], ws["not_in_860"]),
                         (0.0, 0.0, 0.0, 0.0))
        self.assertAlmostEqual(ws["next_year"] + ws["later"] + ws["never"], ws["planned_mw"],
                               places=6)
        self.assertEqual(self.out["wind_2017_gaps"], [])


if __name__ == "__main__":
    unittest.main()
