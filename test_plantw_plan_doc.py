"""Doc test: what docs/plantw-plan.md says was known is recomputed from data/nexttech_cohort.csv,
and its check and bars match tools/annual-flows-candidate/plantw.py.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import csv
import hashlib
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
POOL, RECENT, WIN = ("2016-01", "2025-12"), ("2022-01", "2026-08"), ("2020-01", "2021-12")
GAPS = ((1, 1, "1 month"), (2, 3, "2-3 months"), (4, 12, "4-12 months"), (13, None, "more than 12 months"))


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8") as fh:
        return fh.read()


def mi(month):
    return int(month[:4]) * 12 + int(month[5:7]) - 1


def cell_of(gap):
    if gap is None:
        return "first"
    for lo, hi, name in GAPS:
        if gap >= lo and (hi is None or gap <= hi):
            return name
    return None


def f(c):
    return "%.3f (%s of %s)" % (c[0] / c[1], "{:,}".format(c[0]), "{:,}".format(c[1]))


class PlantwPlanDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = read("docs", "plantw-plan.md")
        cls.code = read("tools", "annual-flows-candidate", "plantw.py")
        path = os.path.join(HERE, "data", "nexttech_cohort.csv")
        with open(path, "rb") as fh:
            cls.md5 = hashlib.md5(fh.read()).hexdigest()
        with open(path, newline="", encoding="utf-8") as fh:
            co = list(csv.DictReader(fh))
        cls.n_rows = len(co)
        last, cls.rows = {}, []
        for r in sorted(co, key=lambda r: (r["month"], r["key"])):
            k = r["key"]
            cls.rows.append(dict(r, cell=cell_of(None if k not in last else mi(r["month"]) - mi(last[k]))))
            last[k] = r["month"]

    def rows_of(self, period, group, name):
        return [r for r in self.rows if period[0] <= r["month"] <= period[1] and r["group"] == group
                and r["cell"] == name]

    def c(self, period, group, name):
        rows = self.rows_of(period, group, name)
        return sum(r["now"] == "Operating" for r in rows), len(rows)

    def test_status(self):
        self.assertIn("Status: pre-registered, not yet scored.", self.plan)
        for s in ("**C0.**", "**P1.**", "**P2.**", "**P3.**", "**P4.**", "**P5.**", "at least 30 plants",
                  "at commit ea63c15", "A tie counts as failed."):
            self.assertIn(s, self.plan)

    def test_known_pooled(self):
        for g in ("solar", "batteries", "wind", "gas"):
            self.assertIn("  - %s: first listings %s, 1 month after the last listing %s" % (
                g, f(self.c(POOL, g, "first")), f(self.c(POOL, g, "1 month"))), self.plan)
        self.assertIn("solar from January 2022 to August 2026: 1 month after the last listing %s, 2-3 months after %s" % (
            f(self.c(RECENT, "solar", "1 month")), f(self.c(RECENT, "solar", "2-3 months"))), self.plan)
        d = lambda p, g, x, y: "%.3f" % (self.c(p, g, x)[0] / self.c(p, g, x)[1] - self.c(p, g, y)[0] / self.c(p, g, y)[1])
        self.assertEqual((d(POOL, "solar", "1 month", "first"), d(POOL, "batteries", "1 month", "first"),
                          d(RECENT, "solar", "1 month", "2-3 months")), ("0.050", "0.082", "0.125"))
        self.assertIn("solar's one-month advantage (0.050 in generator-months)", self.plan)
        self.assertIn("(0.082 and 0.125)", self.plan)
        gas = [self.rows_of(WIN, "gas", x) for x in ("1 month", "first")]
        got = [(len(set(r["key"] for r in rs)), len(set(r["key"].split("/")[0] for r in rs))) for rs in gas]
        self.assertEqual(got, [(71, 28), (168, 62)])
        self.assertIn("gas's one-month cell had 71 generators at 28 plants and its first listings 168 at 62", self.plan)

    def test_c0(self):
        self.assertEqual((self.n_rows, self.md5), (14807, "1681df9fdee9878ca2c359d1239c6467"))
        self.assertEqual((self.c(POOL, "solar", "first"), self.c(POOL, "solar", "1 month")), ((1474, 3568), (1230, 2657)))
        self.assertIn("The file has 14,807 rows and md5 1681df9fdee9878ca2c359d1239c6467, and its pooled 2016-2025 "
                      "solar cells reproduce, in generator-months, first listings 1,474 of 3,568 and 1 month after the "
                      "last listing 1,230 of 2,657.", self.plan)
        for s in ('KNOWN = {("solar", "first"): (1474, 3568), ("solar", "1 month"): (1230, 2657)}',
                  "COHORT_ROWS = 14807", 'COHORT_MD5 = "1681df9fdee9878ca2c359d1239c6467"'):
            self.assertIn(s, self.code)

    def test_code_matches_plan(self):
        for s in ('PLAN_URL = BASE + "main/docs/plantw-plan.md"', 'POOL = ("2016-01", "2025-12")',
                  'RECENT = ("2022-01", "2026-08")', "MIN_PLANTS = 30", '__version__ = "0.1.0"',
                  'COHORT_URL = BASE + "ea63c150a8ed41cc1fcad901ccab51686c924d46/data/nexttech_cohort.csv"',
                  '("P1", POOL, "solar", "1 month", "first", "above",',
                  '("P2", POOL, "batteries", "1 month", "first", "above",',
                  '("P3", POOL, "wind", "1 month", "first", "below",',
                  '("P4", POOL, "gas", "1 month", "first", "below",',
                  '("P5", RECENT, "solar", "1 month", "2-3 months", "above",',
                  'o = "held" if cx["pw"] > cy["pw"] else "failed"', 'o = "held" if cx["pw"] < cy["pw"] else "failed"',
                  'plant=k.split("/")[0]', "pw = sum(v[0] / v[1] for v in by.values()) / len(by) if by else None"):
            self.assertIn(s, self.code)
        self.assertIn('CELLS = ("first",) + tuple(x[2] for x in nc.GAPS)',
                      read("tools", "annual-flows-candidate", "gaptech.py"))
        self.assertIn('GAPS = ((1, 1, "1 month"), (2, 3, "2-3 months"), (4, 12, "4-12 months"), '
                      '(13, None, "more than 12 months"))', self.code)


if __name__ == "__main__":
    unittest.main()
