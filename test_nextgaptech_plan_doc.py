"""Doc test: what docs/nextgaptech-plan.md says was known is recomputed from data/nexttech_cohort.csv,
and its check and bars match tools/annual-flows-candidate/gaptech.py.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import collections
import csv
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EARLY, LATE, HELD = ("2016-01", "2019-12"), ("2022-01", "2025-12"), ("2026-01", "2026-08")


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8") as fh:
        return fh.read()


def mi(month):
    return int(month[:4]) * 12 + int(month[5:7]) - 1


def f(c):
    return "%.3f (%s of %s)" % (c[0] / c[1], "{:,}".format(c[0]), "{:,}".format(c[1]))


class NextgaptechPlanDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = read("docs", "nextgaptech-plan.md")
        cls.code = read("tools", "annual-flows-candidate", "gaptech.py")
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

    def test_status(self):
        self.assertIn("Status: pre-registered, not yet scored.", self.plan)
        for s in ("**C0.**", "**G1.**", "**G2.**", "**G3.**", "**G4.**", "at least 30 rows", "at commit ea63c15"):
            self.assertIn(s, self.plan)

    def test_c0(self):
        self.assertEqual(self.n_rows, 14807)
        got = [self.cell(p, lambda r: True) for p in (EARLY, LATE, HELD)]
        self.assertEqual(got, [(1980, 4223), (2110, 6047), (366, 1194)])
        firsts = [self.cell(LATE, lambda r, g=g: r["group"] == g and r["prior"] == 0) for g in ("solar", "batteries")]
        self.assertEqual(firsts, [(536, 1483), (143, 514)])
        self.assertIn("The file has 14,807 rows; its generator-months reproduce 1,980 of 4,223 (2016-2019), 2,110 of "
                      "6,047 (2022-2025) and 366 of 1,194 (January to August 2026); and the first listings of 2022-2025 "
                      "reproduce 536 of 1,483 for solar and 143 of 514 for batteries.", self.plan)
        for s in ("KNOWN = {nc.EARLY: (1980, 4223), nc.LATE: (2110, 6047), HELD: (366, 1194)}",
                  'KNOWN_FIRST = {"solar": (536, 1483), "batteries": (143, 514)}', 'HELD = ("2026-01", "2026-08")'):
            self.assertIn(s, self.code)

    def test_known_all(self):
        def gap(p, lo, hi):
            return self.cell(p, lambda r: r["gap"] is not None and lo <= r["gap"] <= hi)
        first = [self.cell(p, lambda r: r["prior"] == 0) for p in (LATE, HELD)]
        one = [gap(p, 1, 1) for p in (LATE, HELD)]
        two = [gap(p, 2, 3) for p in (LATE, HELD)]
        self.assertIn("2022-2025: first listings %s, repeat listings 1 month after the last one %s, 2-3 months after "
                      "%s." % (f(first[0]), f(one[0]), f(two[0])), self.plan)
        self.assertIn("January to August 2026: %s, %s and %s." % (f(first[1]), f(one[1]), f(two[1])), self.plan)

    def test_known_by_technology(self):
        for name, g, p in (("Solar, 2022-2025", "solar", LATE), ("Batteries, 2022-2025", "batteries", LATE),
                           ("Solar, January to August 2026", "solar", HELD)):
            cs = [self.cell(p, lambda r, a=a: r["group"] == g and (r["prior"] == a if a < 3 else r["prior"] >= 3))
                  for a in (0, 1, 2, 3)]
            self.assertIn("%s: %s, %s, %s, %s." % (name, f(cs[0]), f(cs[1]), f(cs[2]), f(cs[3])), self.plan)
        self.assertIn("0.363 against 0.361 with none", self.plan)
        self.assertIn("(0.277 against 0.290)", self.plan)

    def test_code_matches_plan(self):
        for s in ('PLAN_URL = nc.BASE + "docs/nextgaptech-plan.md"', "import nextcount as nc", '__version__ = "0.1.0"',
                  'CELLS = ("first",) + tuple(x[2] for x in nc.GAPS)',
                  '("G1", sl, "1 month", "first",', '("G2", sl, "1 month", "2-3 months",',
                  '("G3", s26, "1 month", "2-3 months",', '("G4", bl, "1 month", "first",',
                  'sl, bl, s26 = cells(a, "solar", nc.LATE), cells(a, "batteries", nc.LATE), cells(a, "solar", HELD)',
                  "lambda c=c, x=x, y=y: s(c[x]) > s(c[y])"):
            self.assertIn(s, self.code)
        nextcount = read("tools", "annual-flows-candidate", "nextcount.py")
        for s in ("MIN_COHORT = 30", 'GAPS = ((1, 1, "1 month"), (2, 3, "2-3 months")', '__version__ = "0.1.0"',
                  'GROUPS = ("solar", "batteries", "gas", "wind", "other")'):
            self.assertIn(s, nextcount)

    def test_readme(self):
        readme = read("README.md")
        # Scored on 24 October 2026 (docs/nextgaptech.md), so it left the README's list of plans not yet scored.
        self.assertNotIn("Also [`nextgaptech-plan.md`](docs/nextgaptech-plan.md) (whether", readme)
        self.assertIn("Whether a one-month slip is a good sign within solar and within batteries was pre-registered in "
                      "[`docs/nextgaptech-plan.md`](docs/nextgaptech-plan.md) and is scored in the thirty-eighth result.",
                      readme)


if __name__ == "__main__":
    unittest.main()
