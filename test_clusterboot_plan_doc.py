"""Doc test: what docs/clusterboot-plan.md says was known is recomputed from data/nexttech_cohort.csv,
and its check, rule and bars match tools/annual-flows-candidate/clusterboot.py.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import csv
import hashlib
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
POOL, RECENT = ("2016-01", "2025-12"), ("2022-01", "2026-08")
GAPS = ((1, 1, "1 month"), (2, 3, "2-3 months"), (4, 12, "4-12 months"), (13, None, "more than 12 months"))


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8") as fh:
        return fh.read()


def n(x):
    return "{:,}".format(x)


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
    return "%.3f (%s of %s)" % (c[0] / c[1], n(c[0]), n(c[1]))


class ClusterbootPlanDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = read("docs", "clusterboot-plan.md")
        cls.code = read("tools", "annual-flows-candidate", "clusterboot.py")
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

    def c(self, period, group, name):
        """-> (on time, generator-months, plants)"""
        rows = [r for r in self.rows if period[0] <= r["month"] <= period[1] and r["group"] == group
                and r["cell"] == name]
        return (sum(r["now"] == "Operating" for r in rows), len(rows),
                len(set(r["key"].split("/")[0] for r in rows)))

    def test_status(self):
        self.assertIn("Status: pre-registered, not yet scored.", self.plan)
        for s in ("**C0.**", "**B1.**", "**B2.**", "**B3.**", "**B4.**", "**B5.**", "at least 30 plants",
                  "at commit ea63c15", "draws 2,000 resamples", "`random.Random(20261025).choices`",
                  "The 95% interval runs from the 51st to the 1,950th of them."):
            self.assertIn(s, self.plan)
        self.assertEqual((2000 * 25 // 1000 + 1, 2000 * 975 // 1000), (51, 1950))

    def test_known(self):
        for g in ("solar", "batteries", "wind", "gas"):
            m, fi = self.c(POOL, g, "1 month"), self.c(POOL, g, "first")
            self.assertIn("  - %s: 1 month after the last listing %s at %s plants, first listings %s at %s plants; "
                          "1 month minus first %+.3f" % (g, f(m), n(m[2]), f(fi), n(fi[2]), m[0] / m[1] - fi[0] / fi[1]),
                          self.plan)
        m, t = self.c(RECENT, "solar", "1 month"), self.c(RECENT, "solar", "2-3 months")
        self.assertIn("  - and for B5, solar from January 2022 to August 2026: 1 month after the last listing %s at %s "
                      "plants, 2-3 months after %s at %s plants; 1 month minus 2-3 months %+.3f" % (
                          f(m), n(m[2]), f(t), n(t[2]), m[0] / m[1] - t[0] / t[1]), self.plan)
        self.assertIn("(gas: 576 generator-months at 108 plants)", self.plan)
        self.assertEqual(self.c(POOL, "gas", "1 month")[1:], (576, 108))

    def test_c0(self):
        self.assertEqual((self.n_rows, self.md5), (14807, "1681df9fdee9878ca2c359d1239c6467"))
        self.assertIn("The file has 14,807 rows and md5 1681df9fdee9878ca2c359d1239c6467, and its ten generator-month "
                      "cells listed above reproduce exactly.", self.plan)
        keys = [(p, g, x) for p, g, x in (("POOL", g, x) for g in ("solar", "batteries", "wind", "gas")
                                          for x in ("first", "1 month"))]
        keys += [("RECENT", "solar", "1 month"), ("RECENT", "solar", "2-3 months")]
        self.assertEqual(len(keys), 10)
        for p, g, x in keys:
            on, rows, _ = self.c(POOL if p == "POOL" else RECENT, g, x)
            self.assertIn('(%s, "%s", "%s"): (%d, %d)' % (p, g, x, on, rows), self.code)
        for s in ("COHORT_ROWS = 14807", 'COHORT_MD5 = "1681df9fdee9878ca2c359d1239c6467"'):
            self.assertIn(s, self.code)

    def test_code_matches_plan(self):
        for s in ('PLAN_URL = BASE + "main/docs/clusterboot-plan.md"', 'POOL = ("2016-01", "2025-12")',
                  'RECENT = ("2022-01", "2026-08")', "MIN_PLANTS = 30", "RESAMPLES = 2000", "SEED = 20261025",
                  '__version__ = "0.1.0"',
                  'COHORT_URL = BASE + "ea63c150a8ed41cc1fcad901ccab51686c924d46/data/nexttech_cohort.csv"',
                  '("B1", POOL, "solar", "1 month", "first", 1, "above",',
                  '("B2", POOL, "batteries", "1 month", "first", 1, "above",',
                  '("B3", POOL, "wind", "1 month", "first", -1, "spans",',
                  '("B4", POOL, "gas", "1 month", "first", -1, "spans",',
                  '("B5", RECENT, "solar", "1 month", "2-3 months", 1, "above",',
                  'o = "held" if r["lo"] > 0 else "failed"', 'o = "held" if r["lo"] <= 0 <= r["hi"] else "failed"',
                  "vals = [by[k] for k in sorted(by)]", "rng = random.Random(seed)",
                  "for v in rng.choices(vals, k=n):", "return d[n * 25 // 1000], d[n * 975 // 1000 - 1]",
                  'plant=k.split("/")[0]', "if r is None or min(r[\"plants\"][:2]) < MIN_PLANTS:"):
            self.assertIn(s, self.code)
        self.assertIn('GAPS = ((1, 1, "1 month"), (2, 3, "2-3 months"), (4, 12, "4-12 months"), '
                      '(13, None, "more than 12 months"))', self.code)


if __name__ == "__main__":
    unittest.main()
