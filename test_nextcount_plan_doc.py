"""Doc test: what docs/nextcount-plan.md says was known is recomputed from data/nexttech_cohort.csv and
docs/monthrun-practice-v1-output.md, its bars match tools/annual-flows-candidate/nextcount.py, and
README.md's correction of 24 October 2026 matches the dated update in docs/nexttechonce.md.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import csv
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EARLY, LATE = ("2016-01", "2019-12"), ("2022-01", "2025-12")


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8") as fh:
        return fh.read()


def n(x):
    return "{:,}".format(x)


class NextcountPlanDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = read("docs", "nextcount-plan.md")
        cls.readme = read("README.md")
        with open(os.path.join(HERE, "data", "nexttech_cohort.csv"), newline="", encoding="utf-8") as fh:
            cls.co = list(csv.DictReader(fh))

    def test_status(self):
        self.assertIn("Status: pre-registered, not yet scored.", self.plan)
        for s in ("**C0.**", "**K1.**", "**K2.**", "**K3.**", "at least 30 rows", "at commit ea63c15"):
            self.assertIn(s, self.plan)

    def test_cohort_file(self):
        self.assertEqual(len(self.co), 14807)
        months = sorted(r["month"] for r in self.co)
        self.assertEqual((months[0], months[-1]), ("2015-08", "2026-09"))
        self.assertIn("(14,807 rows, one per generator and cohort month, August 2015 to September 2026)", self.plan)
        for p, k in ((EARLY, (1980, 4223)), (LATE, (2110, 6047))):
            sel = [r for r in self.co if p[0] <= r["month"] <= p[1]]
            self.assertEqual((sum(r["now"] == "Operating" for r in sel), len(sel)), k)
        self.assertIn("1,980 of 4,223 in 2016-2019 and 2,110 of 6,047 in 2022-2025", self.plan)

    def test_within_period_split(self):
        got = {}
        for p in (EARLY, LATE):
            seen, first, rep = set(), [0, 0], [0, 0]
            for r in sorted((r for r in self.co if p[0] <= r["month"] <= p[1]), key=lambda r: r["month"]):
                c = rep if r["key"] in seen else first
                seen.add(r["key"])
                c[1] += 1
                c[0] += r["now"] == "Operating"
            got[p] = (first, rep)
        (f, r), (g, s) = got[EARLY], got[LATE]
        self.assertIn("In 2016-2019 first listings were on time %.3f (%s of %s) and later ones %.3f (%s of %s); in "
                      "2022-2025, %.3f (%s of %s) and %.3f (%s of %s)." % (
                          f[0] / f[1], n(f[0]), n(f[1]), r[0] / r[1], n(r[0]), n(r[1]),
                          g[0] / g[1], n(g[0]), n(g[1]), s[0] / s[1], n(s[0]), n(s[1])), self.plan)

    def test_september_split(self):
        out = read("docs", "monthrun-practice-v1-output.md")
        self.assertIn("| all | first | 61 | 26 | 0.4262 |", out)
        self.assertIn("| all | repeat | 109 | 31 | 0.2844 |", out)
        self.assertIn("26 of 61 first listings were on time (0.4262) and 31 of 109 repeat listings (0.2844)", self.plan)

    def test_gas_plant(self):
        gas = [r for r in self.co if EARLY[0] <= r["month"] <= EARLY[1] and r["key"].split("/")[0] == "60264"
               and r["group"] == "gas"]
        self.assertEqual(len(gas), 102)
        self.assertEqual(len(set(r["key"] for r in gas)), 12)
        self.assertIn("one gas plant (60264) has 102 gas generator-months of 2016-2019, its 12 turbines", self.plan)

    def test_code_matches_plan(self):
        code = read("tools", "annual-flows-candidate", "nextcount.py")
        for s in ('PLAN_URL = BASE + "docs/nextcount-plan.md"', "COHORT_ROWS = 14807", "MIN_COHORT = 30",
                  'BINS = ("0", "1", "2", "3+")', "KNOWN = {EARLY: (1980, 4223), LATE: (2110, 6047)}",
                  'EARLY, LATE = ("2016-01", "2019-12"), ("2022-01", "2025-12")',
                  "ea63c150a8ed41cc1fcad901ccab51686c924d46/data/nexttech_cohort.csv", 'GAS_PLANT = "60264"'):
            self.assertIn(s, code)

    def test_readme(self):
        upd = read("docs", "nexttechonce.md")
        upd = upd[upd.index("## Update, 24 October 2026: more repeat listings explain almost none of the extra fall"):]
        for s in ("0.002 of the 0.120 fall", "fell by 0.137 (0.477 to 0.340), against 0.100 for first listings "
                  "(0.462 to 0.361)"):
            self.assertIn(s, upd)
        self.assertIn("which is part of why the share counted in generator-months fell further. *Corrected on 24 "
                      "October 2026: the larger number of repeat listings explains under 2% of the generator-month "
                      "fall (0.002 of 0.120). What made that fall steeper is that repeat listings were on time much "
                      "less often than before (0.477 to 0.340, against 0.462 to 0.361 for first listings); see the "
                      "dated update at the end of the note.*", self.readme)
        self.assertIn("is pre-registered in [`docs/nextcount-plan.md`](docs/nextcount-plan.md).", self.readme)
        self.assertIn("Also [`nextcount-plan.md`](docs/nextcount-plan.md) (whether the next-month share falls with "
                      "the number of times a generator was planned for the next month before, three bars).",
                      self.readme)


if __name__ == "__main__":
    unittest.main()
