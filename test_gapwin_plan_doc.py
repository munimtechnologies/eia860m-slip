"""Doc test: what docs/gapwin-plan.md says was known is recomputed from data/nexttech_cohort.csv,
and its check and bars match tools/annual-flows-candidate/gapwin.py.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import collections
import csv
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EARLY, LATE, WIN = ("2016-01", "2019-12"), ("2022-01", "2025-12"), ("2020-01", "2021-12")


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8") as fh:
        return fh.read()


def mi(month):
    return int(month[:4]) * 12 + int(month[5:7]) - 1


def f(c):
    return "%.3f (%s of %s)" % (c[0] / c[1], "{:,}".format(c[0]), "{:,}".format(c[1]))


class GapwinPlanDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = read("docs", "gapwin-plan.md")
        cls.code = read("tools", "annual-flows-candidate", "gapwin.py")
        with open(os.path.join(HERE, "data", "nexttech_cohort.csv"), newline="", encoding="utf-8") as fh:
            co = list(csv.DictReader(fh))
        cls.n_rows = len(co)
        count, last, cls.rows = collections.Counter(), {}, []
        for r in sorted(co, key=lambda r: (r["month"], r["key"])):
            k = r["key"]
            cls.rows.append(dict(r, prior=count[k], gap=None if k not in last else mi(r["month"]) - mi(last[k])))
            count[k] += 1
            last[k] = r["month"]

    def cell(self, period, test):
        sel = [r for r in self.rows if period[0] <= r["month"] <= period[1] and test(r)]
        return sum(r["now"] == "Operating" for r in sel), len(sel)

    def share(self, period, group, lo, hi):
        if lo is None:
            c = self.cell(period, lambda r: r["group"] == group and r["gap"] is None)
        else:
            c = self.cell(period, lambda r: r["group"] == group and r["gap"] is not None and lo <= r["gap"] <= hi)
        return c[0] / c[1]

    def test_status(self):
        self.assertIn("Status: pre-registered, not yet scored.", self.plan)
        for s in ("**C0.**", "**W1.**", "**W2.**", "**W3.**", "**W4.**", "**W5.**", "at least 30 rows",
                  "at commit ea63c15"):
            self.assertIn(s, self.plan)

    def test_known_by_year(self):
        for name, g in (("Solar", "solar"), ("Batteries", "batteries"), ("Gas", "gas"), ("Wind", "wind")):
            c20 = self.cell(("2020-01", "2020-12"), lambda r: r["group"] == g)
            c21 = self.cell(("2021-01", "2021-12"), lambda r: r["group"] == g)
            self.assertIn("  - %s: %s in 2020, %s in 2021." % (name, f(c20), f(c21)), self.plan)
        self.assertEqual(self.cell(WIN, lambda r: True)[1], 2826)
        self.assertIn("(2,826 generator-months)", self.plan)

    def test_c0(self):
        self.assertEqual(self.n_rows, 14807)
        got = {g: self.cell(WIN, lambda r, g=g: r["group"] == g) for g in ("solar", "batteries", "gas", "wind")}
        self.assertEqual(got, {"solar": (686, 1600), "batteries": (103, 344), "gas": (150, 375), "wind": (143, 373)})
        self.assertIn("The file has 14,807 rows, and its 2020-2021 generator-months reproduce solar 686 of 1,600, "
                      "batteries 103 of 344, gas 150 of 375 and wind 143 of 373", self.plan)
        self.assertIn('KNOWN = {"solar": (686, 1600), "batteries": (103, 344), "gas": (150, 375), "wind": (143, 373)}',
                      self.code)

    def test_known_cells(self):
        d = lambda p, g, a, b: "%.3f" % (self.share(p, g, *a) - self.share(p, g, *b))
        first, one, two = (None, None), (1, 1), (2, 3)
        gas = [d(p, "gas", first, one) for p in (EARLY, LATE)]
        wind = [d(p, "wind", first, one) for p in (EARLY, LATE)]
        sol = [d(p, "solar", one, two) for p in (EARLY, LATE)]
        self.assertEqual((gas, wind, sol), (["0.092", "0.190"], ["0.014", "0.071"], ["0.030", "0.131"]))
        self.assertIn("by %s (2016-2019) and %s (2022-2025), and a wind one by %s and %s" % (
            gas[0], gas[1], wind[0], wind[1]), self.plan)
        self.assertIn("solar's one-month cell was above its 2-3 month cell by %s in 2016-2019 and %s in 2022-2025" % (
            sol[0], sol[1]), self.plan)
        self.assertIn("wind's margin in 2016-2019 was only 0.014", self.plan)
        self.assertIn("a 2-3 month slip cost solar little (0.030)", self.plan)
        self.assertIn("batteries had only 344 generator-months in the two years", self.plan)

    def test_code_matches_plan(self):
        for s in ('PLAN_URL = nc.BASE + "docs/gapwin-plan.md"', 'WIN = ("2020-01", "2021-12")', "import gaptech as gt",
                  "import nextcount as nc", '__version__ = "0.1.0"',
                  '("W1", "solar", "1 month", "first", "above",', '("W2", "solar", "1 month", "2-3 months", "above",',
                  '("W3", "batteries", "1 month", "first", "above",', '("W4", "gas", "1 month", "first", "below",',
                  '("W5", "wind", "1 month", "first", "below",', "ok = lambda c=c, x=x, y=y: s(c[x]) > s(c[y])",
                  "ok = lambda c=c, x=x, y=y: s(c[x]) < s(c[y])", "c = gt.cells(a, g, WIN)"):
            self.assertIn(s, self.code)
        self.assertIn("MIN_COHORT = 30", read("tools", "annual-flows-candidate", "nextcount.py"))
        self.assertIn('CELLS = ("first",) + tuple(x[2] for x in nc.GAPS)',
                      read("tools", "annual-flows-candidate", "gaptech.py"))


if __name__ == "__main__":
    unittest.main()
