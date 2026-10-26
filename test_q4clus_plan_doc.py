"""Doc test: what docs/q4clus-plan.md says was known is recomputed from data/nexttech_cohort.csv and
docs/clusterboot.md, the practice run's output (docs/q4clus-practice-v1-output.md) agrees with it,
and the plan's checks, bars and expected chances match tools/annual-flows-candidate/q4clus.py.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import csv
import math
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SEP = "2026-09"
GAPS = ((1, 1, "1 month"), (2, 3, "2-3 months"), (4, 12, "4-12 months"), (13, None, "more than 12 months"))
# Published cells (on time, rows) of the forty-first result and its intervals
HISTORY = (("R1", "B1", (1230, 2657), (1474, 3568), "+0.0200 to +0.0795"),
           ("R2", "B2", (297, 816), (205, 728), "+0.0275 to +0.1405"),
           ("R3", "B5", (639, 1636), (171, 644), "+0.0798 to +0.1686"))


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


def diff(x, y):
    return x[0] / x[1] - y[0] / y[1]


class Q4clusPlanDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = read("docs", "q4clus-plan.md")
        cls.out = read("docs", "q4clus-practice-v1-output.md")
        cls.code = read("tools", "annual-flows-candidate", "q4clus.py")
        cls.history = read("docs", "clusterboot.md")
        with open(os.path.join(HERE, "data", "nexttech_cohort.csv"), newline="", encoding="utf-8") as fh:
            co = list(csv.DictReader(fh))
        cls.n_rows = len(co)
        last, cls.rows = {}, []
        for r in sorted(co, key=lambda r: (r["month"], r["key"])):
            k = r["key"]
            cls.rows.append(dict(r, cell=cell_of(None if k not in last else mi(r["month"]) - mi(last[k]))))
            last[k] = r["month"]

    def c(self, group, name):
        """September 2026 -> (on time, generator-months, plants)"""
        rows = [r for r in self.rows if r["month"] == SEP and r["group"] == group and r["cell"] == name]
        return (sum(r["now"] == "Operating" for r in rows), len(rows),
                len(set(r["key"].split("/")[0] for r in rows)))

    def test_status(self):
        self.assertIn("Status: pre-registered, not yet scored.", self.plan)
        for s in ("**C1.**", "**C2.**", "**R1.**", "**R2.**", "**R3.**", "**K1.**", "**K2.**", "**K3.**",
                  "at least 30 rows", "at least 30 rows and at least 10 plants each", "at commit ea63c15",
                  '"Next Release Date: November 24, 2026"', "2,000 resamples of them with replacement, seed 20261025",
                  "the 95% interval runs from the 51st to the 1,950th sorted difference",
                  "(950,816 bytes, md5 1681df9fdee9878ca2c359d1239c6467, 14,807 rows; next-month groups from August "
                  "2015 to September 2026)", "`q4clus.py --require-plan`"):
            self.assertIn(s, self.plan)
        self.assertEqual(self.n_rows, 14807)
        self.assertEqual(max(r["month"] for r in self.rows), SEP)
        self.assertEqual((2000 * 25 // 1000 + 1, 2000 * 975 // 1000), (51, 1950))

    def test_history(self):
        b1, b2, b5 = HISTORY
        for pid, bid, x, y, inter in HISTORY:
            d = "%+.4f (%s)" % (diff(x, y), inter)
            self.assertIn("%s; 1 month after the last listing %s of %s" % (d, n(x[0]), n(x[1])), self.history)
            self.assertIn("%s of %s" % (n(y[0]), n(y[1])), self.history)
            self.assertIn('"%s": ((%d, %d), (%d, %d)),' % (pid, x[0], x[1], y[0], y[1]), self.code)
        self.assertIn("first listings 1,474 of 3,568 at 3,316 plants", self.history)
        self.assertIn("first listings 205 of 728 at 680 plants", self.history)
        self.assertIn("2-3 months after 171 of 644 at 443 plants", self.history)
        f = lambda b: "%+.4f (%s), from %s of %s against %s of %s" % (diff(b[2], b[3]), b[4], n(b[2][0]), n(b[2][1]),
                                                                      n(b[3][0]), n(b[3][1]))
        self.assertIn("B1, solar, 2016-2025, 1 month after the last listing minus first listings %s; B2, batteries, "
                      "the same, %s; B5, solar, January 2022 to August 2026, 1 month after minus 2-3 months after %s."
                      % (f(b1), f(b2), f(b5)), self.plan)
        for pid, bid, x, y, inter in HISTORY:
            self.assertIn("**%s.** %s's 95%% interval contains the forty-first result's %s difference, %+.4f." % (
                "K" + pid[1], pid, bid, diff(x, y)), self.plan)

    def test_design(self):
        ratios = []
        for pid, bid, x, y, inter in HISTORY:
            lo, hi = [float(v) for v in inter.split(" to ")]
            px, py = x[0] / x[1], y[0] / y[1]
            se = math.sqrt(px * (1 - px) / x[1] + py * (1 - py) / y[1])
            ratios.append("%.2f" % ((hi - lo) / (2 * 1.96 * se)))
        self.assertEqual(ratios, ["1.19", "1.22", "1.07"])
        self.assertIn("Those intervals were 1.19 (B1), 1.22 (B2) and 1.07 (B5) times as wide", self.plan)
        self.assertIn("DESIGN = 1.2", self.code)

    def test_september(self):
        cells = [self.c(g, x) for g in ("solar", "batteries") for x in ("1 month", "first", "2-3 months")]
        self.assertEqual(cells, [(14, 35, 34), (16, 41, 40), (5, 24, 24), (5, 11, 11), (6, 16, 16),
                                 (3, 10, cells[5][2])])
        s = "solar, 1 month after the last listing %d of %d at %d plants, first listings %d of %d at %d plants, " \
            "2-3 months after %d of %d at %d plants; " % (cells[0] + cells[1] + cells[2])
        s += "batteries, 1 month after the last listing %d of %d at %d plants, first listings %d of %d at %d plants, " \
             "2-3 months after %d of %d." % (cells[3] + cells[4] + cells[5][:2])
        self.assertIn(s, self.plan)
        self.assertIn('SEPTEMBER_ROWS = {("solar", "first"): 41, ("solar", "1 month"): 35, ("solar", "2-3 months"): 24,',
                      self.code)
        self.assertIn('("batteries", "first"): 16, ("batteries", "1 month"): 11, ("batteries", "2-3 months"): 10}',
                      self.code)
        point = diff(cells[0], cells[1])
        self.assertEqual("%+.4f" % point, "+0.0098")
        self.assertIn("R1 would have held (+0.0098, 95%% interval -0.2158 to +0.2452), R2 and R3 would not have been "
                      "scored (cells of %d and %d rows)" % (cells[3][1], cells[2][1]), self.plan)

    def test_practice_output(self):
        for s in ("| C1 | held | 2026-09: 57 of 170 against 57 of 170 |", "| C2 | held | 170 rows, 0 disagree |",
                  "| R1 | held | 1 month minus first: +0.0098, 95% interval -0.2158 to +0.2452; 1 month: 14 of 35 at "
                  "34 plants; first: 16 of 41 at 40 plants |", "| R2 | not scored |", "| R3 | not scored |",
                  "| K1 | held |", "| K2 | not scored |", "| K3 | not scored |",
                  "| 2026-09 | True | 170 | 170 | 0 |", "2000 resamples, seed 20261025.",
                  "(950816 bytes, md5 1681df9fdee9878ca2c359d1239c6467; 14807 rows).",
                  "1 month: 5 of 11 at 11 plants; first: 6 of 16 at 16 plants",
                  "2-3 months: 5 of 24 at 24 plants"):
            self.assertIn(s, self.out)
        self.assertIn("its 170 appended rows equal the cohort's September rows, and C1 and C2 held", self.plan)
        self.assertIn("K1 would have held, and K2 and K3 would not have been scored.", self.plan)

    def test_expected(self):
        sizes = {"R1": (105, 123), "R2": (33, 48), "R3": (105, 72)}
        sep = {"R1": (35, 41), "R2": (11, 16), "R3": (35, 24)}
        for pid, bid, x, y, inter in HISTORY:
            self.assertEqual(sizes[pid], (3 * sep[pid][0], 3 * sep[pid][1]))
            px, py = x[0] / x[1], y[0] / y[1]
            se = 1.2 * math.sqrt(px * (1 - px) / sizes[pid][0] + py * (1 - py) / sizes[pid][1])
            chance = 0.5 * (1 + math.erf((px - py) / se / math.sqrt(2)))
            row = "| %s | %d, %d | %+.4f | %.2f |" % (pid, sizes[pid][0], sizes[pid][1], diff(x, y), chance)
            self.assertIn(row, self.plan)
            self.assertIn(row, self.out)
        self.assertIn("R1 and R2 each fail about one time in four", self.plan)
        self.assertIn("R2's one-month cell is expected to have about 33 rows", self.plan)

    def test_code_matches_plan(self):
        for s in ('__version__ = "0.1.0"', 'PLAN_URL = nc.BASE + "docs/q4clus-plan.md"', "MIN_ROWS = 30",
                  "MIN_PLANTS = 10", 'o = "held" if r["point"] > 0 else "failed"',
                  'o = "held" if r["lo"] <= h <= r["hi"] else "failed"',
                  "if not ok or min(t[1], t[3]) < min_rows:",
                  'if not ok or min(t[1], t[3]) < min_rows or min(p[:2]) < min_plants or r["lo"] is None:',
                  'ok = c1["held"] and c2["held"]', 'plant=r["key"].split("/")[0]',
                  'rx, ry = 3 * SEPTEMBER_ROWS[(g, x)], 3 * SEPTEMBER_ROWS[(g, y)]',
                  '("R1", "solar", "1 month", "first",', '("R2", "batteries", "1 month", "first",',
                  '("R3", "solar", "1 month", "2-3 months",', '("K1", "R1",', '("K2", "R2",', '("K3", "R3",'):
            self.assertIn(s, self.code)
        boot = read("tools", "annual-flows-candidate", "clusterboot.py")
        for s in ("RESAMPLES = 2000", "SEED = 20261025", "return d[n * 25 // 1000], d[n * 975 // 1000 - 1]"):
            self.assertIn(s, boot)
        held = read("tools", "annual-flows-candidate", "q4held.py")
        for s in ('SCORED = ("2026-10", "2026-11", "2026-12")', 'COHORT_MD5 = "1681df9fdee9878ca2c359d1239c6467"'):
            self.assertIn(s, held)
        nextcount = read("tools", "annual-flows-candidate", "nextcount.py")
        for s in ('PLAN_MARK = "Status: pre-registered, not yet scored."', "COHORT_ROWS = 14807",
                  "ea63c150a8ed41cc1fcad901ccab51686c924d46/data/nexttech_cohort.csv"):
            self.assertIn(s, nextcount)


if __name__ == "__main__":
    unittest.main()
