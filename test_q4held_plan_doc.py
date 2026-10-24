"""Doc test: what docs/q4held-plan.md says was known is recomputed from data/nexttech_cohort.csv,
the practice run's output (docs/q4held-practice-v1-output.md) agrees with it, and the plan's checks
and bars match tools/annual-flows-candidate/q4held.py.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import collections
import csv
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EARLY, LATE, HELD, SEP = ("2016-01", "2019-12"), ("2022-01", "2025-12"), ("2026-01", "2026-08"), ("2026-09", "2026-09")


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8") as fh:
        return fh.read()


def mi(month):
    return int(month[:4]) * 12 + int(month[5:7]) - 1


def s(c):
    return c[0] / c[1]


def f(c):
    return "%.3f (%s of %s)" % (s(c), "{:,}".format(c[0]), "{:,}".format(c[1]))


class Q4heldPlanDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = read("docs", "q4held-plan.md")
        cls.out = read("docs", "q4held-practice-v1-output.md")
        cls.code = read("tools", "annual-flows-candidate", "q4held.py")
        with open(os.path.join(HERE, "data", "nexttech_cohort.csv"), newline="", encoding="utf-8") as fh:
            co = list(csv.DictReader(fh))
        cls.n_rows = len(co)
        count, last, cls.rows = collections.Counter(), {}, []
        for r in sorted(co, key=lambda r: (r["month"], r["key"])):
            k = r["key"]
            cls.rows.append(dict(r, prior=count[k], gap=None if k not in last else mi(r["month"]) - mi(last[k])))
            count[k] += 1
            last[k] = r["month"]

    def cell(self, period, test=lambda r: True):
        sel = [r for r in self.rows if period[0] <= r["month"] <= period[1] and test(r)]
        return sum(r["now"] == "Operating" for r in sel), len(sel)

    def first(self, p, g=None):
        return self.cell(p, lambda r: r["prior"] == 0 and (g is None or r["group"] == g))

    def gap(self, p, lo, hi, g=None):
        return self.cell(p, lambda r: r["gap"] is not None and lo <= r["gap"] <= hi and (g is None or r["group"] == g))

    def five(self, p):
        return self.cell(p, lambda r: r["prior"] >= 5)

    def test_status(self):
        self.assertIn("Status: pre-registered, not yet scored.", self.plan)
        for s_ in ("**C1.**", "**C2.**", "**Q1.**", "**Q2.**", "**Q3.**", "at least 30 rows", "at commit ea63c15",
                   '"Next Release Date: November 24, 2026"', "(950,816 bytes, md5 1681df9fdee9878ca2c359d1239c6467, "
                   "14,807 rows; next-month groups from August 2015 to September 2026)"):
            self.assertIn(s_, self.plan)
        self.assertEqual(self.n_rows, 14807)
        self.assertEqual(max(r["month"] for r in self.rows), "2026-09")

    def test_known_before(self):
        late = (self.first(LATE), self.gap(LATE, 1, 1), self.gap(LATE, 2, 3))
        self.assertIn("2022-2025: first listings %s, repeat listings 1 month after the last one %s, 2-3 months after "
                      "%s." % tuple(f(c) for c in late), self.plan)
        held = (self.first(HELD), self.gap(HELD, 1, 1), self.gap(HELD, 2, 3), self.five(HELD))
        self.assertIn("January to August 2026 (thirty-seventh result): %s, %s and %s; 5 or more earlier listings "
                      "%s." % tuple(f(c) for c in held), self.plan)
        self.assertEqual(held, ((144, 473), (166, 479), (43, 173), (15, 92)))

    def test_known_september(self):
        self.assertEqual(self.cell(SEP), (57, 170))
        first, one, two, mid, five = (self.first(SEP), self.gap(SEP, 1, 1), self.gap(SEP, 2, 3), self.gap(SEP, 4, 12),
                                      self.five(SEP))
        rep = self.cell(SEP, lambda r: r["prior"] >= 1)
        self.assertIn("first listings %s, 1 month after the last listing %s, 2-3 months after %s, 4-12 months after %s, "
                      "5 or more earlier listings %s; repeat listings together %s." % (
                          f(first), f(one), f(two), f(mid), f(five), f(rep)), self.plan)
        self.assertEqual((first, one, two, five, rep), ((26, 61), (19, 52), (9, 42), (4, 22), (31, 109)))
        self.assertGreater(s(one), s(two))
        self.assertLess(s(one), s(first))
        self.assertLess(five[1], 30)
        self.assertIn("On September alone Q1 would have held, Q2 failed, and Q3 not been scored (22 rows).", self.plan)
        tech = []
        for g in ("solar", "batteries"):
            tech += [f(c) for c in (self.first(SEP, g), self.gap(SEP, 1, 1, g), self.gap(SEP, 2, 3, g))]
        self.assertIn("solar %s, %s, %s; batteries %s, %s, %s." % tuple(tech), self.plan)

    def test_practice_output(self):
        for s_ in ("| C1 | held | 2026-09: 57 of 170 against 57 of 170 |", "| C2 | held | 170 rows, 0 disagree |",
                   "| Q1 | held | 19 of 52 against 9 of 42 |", "| Q2 | failed | 19 of 52 against 26 of 61 |",
                   "| Q3 | not scored | 4 of 22 against 26 of 61 |", "| 2026-09 | True | 170 | 170 | 0 |",
                   "(950816 bytes, md5 1681df9fdee9878ca2c359d1239c6467; 14807 rows)."):
            self.assertIn(s_, self.out)
        for name, c in (("first", self.first(SEP)), ("1 month", self.gap(SEP, 1, 1)), ("2-3 months", self.gap(SEP, 2, 3)),
                        ("4-12 months", self.gap(SEP, 4, 12)), ("5 or more earlier", self.five(SEP))):
            self.assertIn("| 2026-09 | %s | %d | %d | %.4f |" % (name, c[1], c[0], s(c)), self.out)
        self.assertIn("its 170 appended rows equal the cohort's September rows", self.plan)

    def test_how_it_could_fail(self):
        m3 = ["%.3f" % (s(self.gap(p, 1, 1)) - s(self.first(p))) for p in (LATE, HELD)]
        self.assertEqual(m3, ["0.028", "0.042"])
        self.assertIn("its margin was 0.028 in 2022-2025 and 0.042 in January to August 2026, and in September 2026 "
                      "first listings (0.426) beat repeat listings 1 month after the last one (0.365)", self.plan)
        self.assertIn("it had 92 in eight months of 2026 and 22 in September", self.plan)
        for p in (EARLY, LATE, HELD, SEP):
            self.assertGreater(s(self.gap(p, 1, 1)), s(self.gap(p, 2, 3)))
        self.assertIn("Q1 held in every period counted so far", self.plan)

    def test_code_matches_plan(self):
        for s_ in ('__version__ = "0.1.0"', 'COHORT_MD5 = "1681df9fdee9878ca2c359d1239c6467"',
                   'SCORED = ("2026-10", "2026-11", "2026-12")', 'PLAN_URL = nc.BASE + "docs/q4held-plan.md"',
                   '("first", lambda r: r["prior"] == 0),', '("1 month", lambda r: r["gap"] == 1),',
                   '("2-3 months", lambda r: r["gap"] is not None and 2 <= r["gap"] <= 3),',
                   '("5 or more earlier", lambda r: r["prior"] >= 5),',
                   'pred("Q1", ok, c["1 month"], c["2-3 months"], "above",',
                   'pred("Q2", ok, c["1 month"], c["first"], "above",',
                   'pred("Q3", ok, c["5 or more earlier"], c["first"], "below",',
                   "def score(rows, scored, known, min_cell=nc.MIN_COHORT):",
                   'ok = c1["held"] and c2["held"]',
                   'bad = [r["key"] + " " + r["month"] for r in sel if (r.get("listing") == "first") != (r["prior"] == 0)]'):
            self.assertIn(s_, self.code)
        nextcount = read("tools", "annual-flows-candidate", "nextcount.py")
        for s_ in ("MIN_COHORT = 30", 'PLAN_MARK = "Status: pre-registered, not yet scored."', "COHORT_ROWS = 14807",
                   '__version__ = "0.1.0"', "ea63c150a8ed41cc1fcad901ccab51686c924d46/data/nexttech_cohort.csv"):
            self.assertIn(s_, nextcount)


if __name__ == "__main__":
    unittest.main()
