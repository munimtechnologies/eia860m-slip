"""Doc test: every number in docs/gapwin.md (thirty-ninth result) is recomputed from
data/nexttech_cohort.csv, and the job's raw output (docs/gapwin-v1-output.md), log and unit-test
log agree with the recomputation.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import collections
import csv
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EARLY, WIN, LATE, HELD = ("2016-01", "2019-12"), ("2020-01", "2021-12"), ("2022-01", "2025-12"), ("2026-01", "2026-08")
PERIODS = (EARLY, WIN, LATE, HELD)
GAPS = ((1, 1, "1 month"), (2, 3, "2-3 months"), (4, 12, "4-12 months"), (13, None, "more than 12 months"))
CELLS = ("first",) + tuple(x[2] for x in GAPS)
GROUPS = ("solar", "batteries", "gas", "wind", "other")


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8") as fh:
        return fh.read()


def n(x):
    return "{:,}".format(x)


def mi(month):
    return int(month[:4]) * 12 + int(month[5:7]) - 1


def label(v, bins):
    for lo, hi, name in bins:
        if v >= lo and (hi is None or v <= hi):
            return name
    return None


def cell_of(r):
    return "first" if r["gap"] is None else label(r["gap"], GAPS)


def cell(rows):
    return sum(r["now"] == "Operating" for r in rows), len(rows)


def s(c):
    return c[0] / c[1]


def f(c):
    return "%.3f (%s of %s)" % (s(c), n(c[0]), n(c[1]))


def gp(rows):
    keys = set(r["key"] for r in rows)
    return len(keys), len(set(k.split("/")[0] for k in keys))


class GapwinDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs", "gapwin.md")
        cls.out = read("docs", "gapwin-v1-output.md")
        cls.readme = read("README.md")
        with open(os.path.join(HERE, "data", "nexttech_cohort.csv"), newline="", encoding="utf-8") as fh:
            co = list(csv.DictReader(fh))
        count, last, cls.rows = collections.Counter(), {}, []
        for r in sorted(co, key=lambda r: (r["month"], r["key"])):
            k = r["key"]
            cls.rows.append(dict(r, prior=count[k], gap=None if k not in last else mi(r["month"]) - mi(last[k])))
            count[k] += 1
            last[k] = r["month"]

    def sel(self, period, test=lambda r: True):
        return [r for r in self.rows if period[0] <= r["month"] <= period[1] and test(r)]

    def rows_of(self, period, group, name):
        return self.sel(period, lambda r: (group is None or r["group"] == group) and cell_of(r) == name)

    def c(self, period, group, name):
        return cell(self.rows_of(period, group, name))

    def test_c0(self):
        self.assertEqual(len(self.rows), 14807)
        self.assertEqual(len(self.sel(WIN)), 2826)
        self.assertIn("(2,826 generator-months)", self.doc)
        got = [cell(self.sel(WIN, lambda r, g=g: r["group"] == g)) for g in ("solar", "batteries", "gas", "wind")]
        self.assertEqual(got, [(686, 1600), (103, 344), (150, 375), (143, 373)])
        self.assertIn("| held | 14,807 rows; 2020-2021: solar 686 of 1,600, batteries 103 of 344, gas 150 of 375, "
                      "wind 143 of 373 |", self.doc)
        self.assertIn("| C0 | held | 14807 rows; 2020-2021: solar 686 of 1600, batteries 103 of 344, gas 150 of 375, "
                      "wind 143 of 373 |", self.out)

    def test_bars(self):
        bars = (("W1", "solar", "first", 1), ("W2", "solar", "2-3 months", 1), ("W3", "batteries", "first", 1),
                ("W4", "gas", "first", -1), ("W5", "wind", "first", -1))
        margins, outcomes = [], []
        for pid, g, y, way in bars:
            a, b = self.c(WIN, g, "1 month"), self.c(WIN, g, y)
            self.assertGreaterEqual(min(a[1], b[1]), 30)
            m = way * (s(a) - s(b))
            o = "held" if m > 0 else "failed"
            self.assertIn("| %s | %s against %s |" % (o, f(a), f(b)), self.doc)
            self.assertIn("| %s | %s | 1 month: %d of %d; %s: %d of %d |" % (pid, o, a[0], a[1], y, b[0], b[1]), self.out)
            margins.append("%.3f" % m)
            outcomes.append(o)
        self.assertEqual(outcomes, ["held", "failed", "held", "held", "held"])
        self.assertEqual(margins, ["0.033", "-0.004", "0.100", "0.005", "0.112"])
        self.assertIn("were 0.033 (W1), 0.100 (W3), 0.005 (W4) and 0.112 (W5); W2 went the wrong way by 0.004.",
                      self.doc)
        self.assertIn("Held: 4 of 5 scored", self.out)
        self.assertIn("4 of 5 predictions held, and the reproduction check C0 held. W2 failed.", self.doc)
        a, b = self.c(WIN, "gas", "1 month"), self.c(WIN, "gas", "first")
        self.assertGreater((a[0] + 1) / a[1], s(b))
        self.assertIn("(%d of %d, %.3f) would have made it fail" % (a[0] + 1, a[1], (a[0] + 1) / a[1]), self.doc)

    def test_plants(self):
        got = [gp(self.rows_of(WIN, g, x)) for g, x in (
            ("solar", "1 month"), ("solar", "2-3 months"), ("batteries", "1 month"), ("wind", "1 month"),
            ("wind", "first"), ("gas", "1 month"), ("gas", "first"))]
        self.assertEqual(got, [(311, 299), (162, 156), (67, 64), (76, 67), (143, 138), (71, 28), (168, 62)])
        flat = tuple(x for p in got for x in p)
        self.assertIn("solar's one-month cell has %d generators at %d plants and its 2-3 month cell %d at %d; batteries' "
                      "one-month cell has %d at %d; wind's one-month cell %d at %d and its first listings %d at %d. Gas "
                      "is concentrated: its one-month cell has %d generators at %d plants, its first listings %d at %d."
                      % flat, self.doc)

    def test_table(self):
        for g in (None, "solar", "batteries", "gas", "wind"):
            self.assertIn("| %s | %s | %s | %s |" % (
                g or "all technologies", f(self.c(WIN, g, "first")), f(self.c(WIN, g, "1 month")),
                f(self.c(WIN, g, "2-3 months"))), self.doc)
        lines = 0
        for g in (None,) + GROUPS:
            for name in CELLS:
                rows = self.rows_of(WIN, g, name)
                if not rows:
                    continue
                c, k = cell(rows), gp(rows)
                self.assertIn("| %s to %s | %s | %s | %d | %d | %.4f | %d | %d |" % (
                    WIN[0], WIN[1], g or "all", name, c[1], c[0], s(c), k[0], k[1]), self.out)
                lines += 1
        self.assertEqual(lines, 30)
        self.assertEqual(lines, self.out.count("\n| 20"))

    def test_periods(self):
        def d(p, g, x, y):
            a, b = self.c(p, g, x), self.c(p, g, y)
            return "%+.3f%s" % (s(a) - s(b), " (under 30 rows)" if min(a[1], b[1]) < 30 else "")
        for g in (None, "solar", "batteries", "gas", "wind"):
            self.assertIn("| %s | %s |" % (g or "all technologies", " | ".join(
                d(p, g, "1 month", "first") for p in PERIODS)), self.doc)
        for g in (None, "solar"):
            self.assertIn("| %s | %s |" % (g or "all technologies", " | ".join(
                d(p, g, "1 month", "2-3 months") for p in PERIODS)), self.doc)
        for g in ("solar", "batteries"):
            self.assertTrue(all(s(self.c(p, g, "1 month")) > s(self.c(p, g, "first")) for p in PERIODS))
        self.assertTrue(all(s(self.c(p, "wind", "1 month")) < s(self.c(p, "wind", "first")) for p in (EARLY, WIN, LATE)))
        gaps = ["%.3f" % (s(self.c(p, "wind", "first")) - s(self.c(p, "wind", "1 month"))) for p in (EARLY, WIN, LATE)]
        self.assertEqual(max(gaps), gaps[1])
        gas = ["%.3f" % (s(self.c(p, "gas", "first")) - s(self.c(p, "gas", "1 month"))) for p in (EARLY, LATE, WIN)]
        self.assertEqual(gas, ["0.092", "0.190", "0.005"])
        self.assertIn("Gas's gap was 0.092 and 0.190 in the periods it was found in, and 0.005 in the held-out one.",
                      self.doc)

    def test_order_of_events(self):
        log = read("docs", "gapwin-v1-stdout.txt").splitlines()
        self.assertEqual(log[0], "2026-10-25T00:23:25Z plan served: "
                                 "https://raw.githubusercontent.com/munimtechnologies/eia860m-slip/main/docs/gapwin-plan.md")
        self.assertEqual(log[1], "cohort file 950816 bytes, md5 1681df9fdee9878ca2c359d1239c6467, 14807 rows")
        self.assertFalse(any("plan not served yet" in x for x in log))
        self.assertLess("2026-10-25T00:07:44Z", log[0][:20])
        self.assertIn("The plan was committed at 00:07:44 UTC on 25 October 2026 (commit 67c562b).", self.doc)
        self.assertIn("its first poll of the plan's address, at 00:23:25 UTC, was served the plan", self.doc)
        self.assertIn("(950,816 bytes, md5 1681df9fdee9878ca2c359d1239c6467, 14,807 rows)", self.doc)
        self.assertIn("ea63c150a8ed41cc1fcad901ccab51686c924d46/data/nexttech_cohort.csv", self.out)
        unit = read("docs", "gapwin-v1-unittests.txt")
        self.assertIn("Ran 11 tests", unit)
        self.assertTrue(unit.rstrip().endswith("OK"))
        self.assertIn("after its 11 unit tests passed", self.doc)
        self.assertIn("Status: pre-registered, not yet scored.", read("docs", "gapwin-plan.md"))
        self.assertIn('__version__ = "0.1.0"', read("tools", "annual-flows-candidate", "gapwin.py"))

    def test_readme(self):
        self.assertIn("| 39 | In 2020-2021, a generator planned for the next month right after a one-month slip was on "
                      "time more often than a new listing in solar and batteries and less often in wind and gas; in "
                      "solar, not more often than one back after a 2-3 month slip (4 of 5 held) | "
                      "[`gapwin.md`](docs/gapwin.md) |", self.readme)
        self.assertIn("(thirty-ninth result, scored against [`docs/gapwin-plan.md`](docs/gapwin-plan.md); 4 of 5 held)",
                      self.readme)
        for s_ in ("**In 2020-2021 too, a one-month slip was a good sign for solar and batteries and a bad one for "
                   "wind.**", "in solar (0.447 against 0.414) and batteries (0.352 against 0.252), and less often in "
                   "wind (0.350 against 0.462)", "Gas held only by 0.005 (0.400 against 0.405)",
                   "were on time 0.451, not less often than after a one-month slip"):
            self.assertIn(s_, self.readme)


if __name__ == "__main__":
    unittest.main()
