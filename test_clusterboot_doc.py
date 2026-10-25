"""Doc test: every count and point difference in docs/clusterboot.md (forty-first result) is
recomputed from data/nexttech_cohort.csv, the 2,000 resamples of each of the five bars are drawn
again with the same seed, and the job's raw output (docs/clusterboot-v1-output.md), log and
unit-test log agree with the recomputation.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import csv
import hashlib
import os
import random
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
POOL, RECENT = ("2016-01", "2025-12"), ("2022-01", "2026-08")
PERIODS = (("2016-01", "2019-12"), ("2020-01", "2021-12"), ("2022-01", "2025-12"), ("2026-01", "2026-08"))
GAPS = ((1, 1, "1 month"), (2, 3, "2-3 months"), (4, 12, "4-12 months"), (13, None, "more than 12 months"))
SEED, RESAMPLES = 20261025, 2000
NAMES = {"first": "first listings", "1 month": "1 month after the last listing", "2-3 months": "2-3 months after"}
KNOWN = {
    (POOL, "solar", "first"): (1474, 3568), (POOL, "solar", "1 month"): (1230, 2657),
    (POOL, "batteries", "first"): (205, 728), (POOL, "batteries", "1 month"): (297, 816),
    (POOL, "wind", "first"): (237, 497), (POOL, "wind", "1 month"): (191, 465),
    (POOL, "gas", "first"): (312, 687), (POOL, "gas", "1 month"): (206, 576),
    (RECENT, "solar", "1 month"): (639, 1636), (RECENT, "solar", "2-3 months"): (171, 644),
}
BARS = (("B1", POOL, "solar", "1 month", "first", 1, "above"), ("B2", POOL, "batteries", "1 month", "first", 1, "above"),
        ("B3", POOL, "wind", "1 month", "first", -1, "spans"), ("B4", POOL, "gas", "1 month", "first", -1, "spans"),
        ("B5", RECENT, "solar", "1 month", "2-3 months", 1, "above"))
COMPARE = (("solar", "1 month", "first", 1), ("batteries", "1 month", "first", 1), ("wind", "1 month", "first", -1),
           ("gas", "1 month", "first", -1), ("solar", "1 month", "2-3 months", 1), (None, "1 month", "first", 1))
ROW = re.compile(r"\| (\d{4}-\d{2}) to (\d{4}-\d{2}) \| (\w+) \| ([^|]+) \| ([+-]\d\.\d{4}) \| ([+-]\d\.\d{4}) to "
                 r"([+-]\d\.\d{4}) \| (\d+), (\d+)( \(under 30 plants\))? \|$")


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


def label(x, y, sign):
    return "%s minus %s" % ((x, y) if sign > 0 else (y, x))


def boot(by, sign):
    """-> the 51st and 1,950th of 2,000 sorted differences, plants drawn as clusterboot.py 0.1.0 draws them."""
    vals = [by[k] for k in sorted(by)]
    rng = random.Random(SEED)
    d = []
    for _ in range(RESAMPLES):
        a = b = c = e = 0
        for v in rng.choices(vals, k=len(vals)):
            a += v[0]
            b += v[1]
            c += v[2]
            e += v[3]
        d.append(sign * (a / b - c / e) if b and e else 0.0)
    d.sort()
    return d[50], d[1949]


class ClusterbootDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs", "clusterboot.md")
        cls.out = read("docs", "clusterboot-v1-output.md")
        cls.readme = read("README.md")
        path = os.path.join(HERE, "data", "nexttech_cohort.csv")
        with open(path, "rb") as fh:
            cls.md5 = hashlib.md5(fh.read()).hexdigest()
        with open(path, newline="", encoding="utf-8") as fh:
            co = list(csv.DictReader(fh))
        cls.n_rows = len(co)
        last, cls.rows = {}, []
        for r in sorted(co, key=lambda r: (r["month"], r["key"])):
            k = r["key"]
            gap = None if k not in last else mi(r["month"]) - mi(last[k])
            cls.rows.append(dict(r, cell=cell_of(gap), plant=k.split("/")[0], ok=r["now"] == "Operating"))
            last[k] = r["month"]
        cls.table = {}
        for line in cls.out.splitlines():
            m = ROW.match(line)
            if m:
                cls.table[m.group(1, 2, 3, 4)] = m

    def pick(self, period, group, name):
        return [r for r in self.rows if period[0] <= r["month"] <= period[1]
                and (group is None or r["group"] == group) and r["cell"] == name]

    def clusters(self, period, group, x, y):
        by = {}
        for i, name in ((0, x), (2, y)):
            for r in self.pick(period, group, name):
                p = by.setdefault(r["plant"], [0, 0, 0, 0])
                p[i] += 1 if r["ok"] else 0
                p[i + 1] += 1
        return by

    def point(self, period, group, x, y, sign):
        by = self.clusters(period, group, x, y)
        t = [sum(v[i] for v in by.values()) for i in range(4)]
        px, py = sum(1 for v in by.values() if v[1]), sum(1 for v in by.values() if v[3])
        return by, t, px, py, sign * (t[0] / t[1] - t[2] / t[3])

    def iv(self, period, group, lab):
        m = self.table[(period[0], period[1], group, lab)]
        return float(m.group(6)), float(m.group(7))

    def test_c0(self):
        self.assertEqual((self.n_rows, self.md5), (14807, "1681df9fdee9878ca2c359d1239c6467"))
        for (period, g, name), want in KNOWN.items():
            rows = self.pick(period, g, name)
            self.assertEqual((sum(1 for r in rows if r["ok"]), len(rows)), want)
        self.assertIn("| held | 14,807 rows, md5 1681df9fdee9878ca2c359d1239c6467; 10 of 10 cells reproduced |", self.doc)
        self.assertIn("| C0 | held | 14807 rows, md5 1681df9fdee9878ca2c359d1239c6467; 10 of 10 published cells "
                      "reproduced |", self.out)

    def test_bars(self):
        outcomes, ends = [], {}
        for pid, period, g, x, y, sign, expect in BARS:
            by, t, px, py, point = self.point(period, g, x, y, sign)
            self.assertGreaterEqual(min(px, py), 30)
            lo, hi = boot(by, sign)
            ends[pid] = (lo, hi)
            o = "held" if (lo > 0 if expect == "above" else lo <= 0 <= hi) else "failed"
            outcomes.append(o)
            self.assertIn("| %s | %s | %s: %+.4f, 95%% interval %+.4f to %+.4f; %s: %d of %d at %d plants; %s: %d of %d "
                          "at %d plants |" % (pid, o, label(x, y, sign), point, lo, hi, x, t[0], t[1], px, y, t[2],
                                              t[3], py), self.out)
            cnt = {x: (t[0], t[1], px), y: (t[2], t[3], py)}
            a, b = (x, y) if sign > 0 else (y, x)
            self.assertIn("| %s | %+.4f (%+.4f to %+.4f); %s %s of %s at %s plants; %s %s of %s at %s plants |" % (
                o, point, lo, hi, NAMES[a], n(cnt[a][0]), n(cnt[a][1]), n(cnt[a][2]), NAMES[b], n(cnt[b][0]),
                n(cnt[b][1]), n(cnt[b][2])), self.doc)
            if pid in ("B1", "B2"):
                self.assertIn("about %.2f more often" % point, self.doc)
        self.assertEqual(outcomes, ["held"] * 5)
        self.assertIn("Held: 5 of 5 scored", self.out)
        self.assertIn("5 of 5 predictions held, and the reproduction check C0 held.", self.doc)
        self.assertIn("Every compared cell has at least 30 plants, so all five were scored.", self.doc)
        nearest = min((abs(v), pid, v) for pid, e in ends.items() for v in e)
        spans = min((abs(v), pid, v) for pid in ("B3", "B4") for v in ends[pid])
        self.assertEqual((nearest[1], ends["B1"][0]), ("B1", nearest[2]))
        self.assertEqual((spans[1], ends["B3"][0]), ("B3", spans[2]))
        self.assertIn("the end closest to 0 is B1's lower end (%+.4f), and of the two bars expected to include 0, "
                      "B3's lower end (%+.4f)." % (nearest[2], spans[2]), self.doc)

    def test_tables(self):
        for period in PERIODS + (POOL, RECENT):
            for g, x, y, sign in COMPARE:
                _, _, px, py, point = self.point(period, g, x, y, sign)
                m = self.table[(period[0], period[1], g or "all", label(x, y, sign))]
                self.assertEqual(m.group(5), "%+.4f" % point)
                self.assertEqual((int(m.group(8)), int(m.group(9))), (px, py))
                self.assertEqual(bool(m.group(10)), min(px, py) < 30)
                self.assertLessEqual(float(m.group(6)), float(m.group(7)))
        self.assertEqual(len(self.table), 36)
        self.assertEqual(sum(1 for k in self.table if k[:2] in PERIODS), 24)
        self.assertIn("these are 24 intervals that were not fixed as bars", self.doc)

    def test_period_reading(self):
        above = lambda p, g, lab: self.iv(p, g, lab)[0] > 0
        spans = lambda p, g, lab: self.iv(p, g, lab)[0] <= 0 <= self.iv(p, g, lab)[1]
        t = self.table
        self.assertEqual([above(p, "solar", "1 month minus first") for p in PERIODS], [True, False, True, False])
        m = t[("2022-01", "2025-12", "solar", "1 month minus first")]
        self.assertIn("the interval is above 0 in 2016-2019 and 2022-2025 (narrowly: %s to %s) and includes 0 in "
                      "2020-2021 and January to August 2026." % (m.group(6), m.group(7)), self.doc)
        self.assertEqual([above(p, "batteries", "1 month minus first") for p in PERIODS], [False, False, True, True])
        self.assertTrue(all(spans(p, "batteries", "1 month minus first") for p in PERIODS[:2]))
        self.assertIn("above 0 in 2022-2025 and January to August 2026, and includes 0 in 2016-2019 and 2020-2021, "
                      "when the one-month cell had %s and %s plants." % (
                          t[("2016-01", "2019-12", "batteries", "1 month minus first")].group(8),
                          t[("2020-01", "2021-12", "batteries", "1 month minus first")].group(8)), self.doc)
        for g in ("wind", "gas"):
            for p in PERIODS + (POOL, RECENT):
                self.assertTrue(spans(p, g, "first minus 1 month"))
        m = t[("2020-01", "2021-12", "wind", "first minus 1 month")]
        self.assertIn("the interval includes 0 in every period. In 2020-2021, the held-out period of the thirty-ninth "
                      "result, wind's is %s (%s to %s)." % m.group(5, 6, 7), self.doc)
        self.assertIn("| held | 0.350 (64 of 183) against 0.462 (66 of 143) |", read("docs", "gapwin.md"))
        self.assertIn("(W5 held in generator-months, 0.350 against 0.462)", self.doc)
        self.assertEqual([above(p, "solar", "1 month minus 2-3 months") for p in PERIODS], [False, False, True, False])
        m, r = (t[("2022-01", "2025-12", "solar", "1 month minus 2-3 months")],
                t[("2026-01", "2026-08", "solar", "1 month minus 2-3 months")])
        self.assertIn("above 0 only in 2022-2025 (%s to %s) among the four periods; in January to August 2026 its lower "
                      "end is %s." % (m.group(6), m.group(7), r.group(6)), self.doc)
        for p in PERIODS + (POOL, RECENT):
            self.assertTrue(spans(p, "all", "1 month minus first"))
        self.assertIn("pooled 2016-2025 (%s, %s to %s)" % t[("2016-01", "2025-12", "all", "1 month minus first")].group(
            5, 6, 7), self.doc)
        x, y = self.pick(PERIODS[3], None, "1 month"), self.pick(PERIODS[3], None, "first")
        m = t[("2026-01", "2026-08", "all", "1 month minus first")]
        self.assertIn("The thirty-seventh result's 2026 comparison (%.3f against %.3f) is %s (%s to %s) here." % (
            sum(1 for r in x if r["ok"]) / len(x), sum(1 for r in y if r["ok"]) / len(y), m.group(5), m.group(6),
            m.group(7)), self.doc)

    def test_order_of_events(self):
        log = read("docs", "clusterboot-v1-stdout.txt").splitlines()
        self.assertEqual(log[0], "2026-10-25T07:27:41Z plan served: "
                                 "https://raw.githubusercontent.com/munimtechnologies/eia860m-slip/main/docs/"
                                 "clusterboot-plan.md")
        self.assertEqual(log[1], "cohort file 950816 bytes, md5 1681df9fdee9878ca2c359d1239c6467, 14807 rows")
        self.assertFalse(any("plan not served yet" in x for x in log))
        self.assertLess("2026-10-25T07:02:13Z", log[0][:20])
        self.assertIn("The plan was committed at 07:02:13 UTC on 25 October 2026 (commit 9d72b7d).", self.doc)
        self.assertIn("The job's first poll of the plan's address, at 07:27:41 UTC, was served the plan.", self.doc)
        self.assertIn("(950,816 bytes, md5 1681df9fdee9878ca2c359d1239c6467, 14,807 rows)", self.doc)
        self.assertIn("ea63c150a8ed41cc1fcad901ccab51686c924d46/data/nexttech_cohort.csv", self.out)
        self.assertIn("2000 resamples, seed 20261025.", self.out)
        unit = read("docs", "clusterboot-v1-unittests.txt")
        self.assertIn("Ran 12 tests", unit)
        self.assertTrue(unit.rstrip().endswith("OK"))
        self.assertIn("after its 12 unit tests passed", self.doc)
        plan = read("docs", "clusterboot-plan.md")
        for s in ("Status: pre-registered, not yet scored.", "random.Random(20261025).choices",
                  "from the 51st to the 1,950th"):
            self.assertIn(s, plan)
        code = read("tools", "annual-flows-candidate", "clusterboot.py")
        for s in ('__version__ = "0.1.0"', "RESAMPLES = 2000", "SEED = 20261025", "MIN_PLANTS = 30",
                  "return d[n * 25 // 1000], d[n * 975 // 1000 - 1]"):
            self.assertIn(s, code)

    def test_readme(self):
        self.assertIn("| 41 | Resampling whole plants, the one-month-slip gaps over first listings in solar and batteries "
                      "and the 2-3 month cost in solar since 2022 stay above 0; the wind and gas intervals include 0 "
                      "(5 of 5 held) | [`clusterboot.md`](docs/clusterboot.md) |", self.readme)
        self.assertIn("(forty-first result, scored against [`docs/clusterboot-plan.md`](docs/clusterboot-plan.md); "
                      "5 of 5 held)", self.readme)
        self.assertIn("**Resampling whole plants, the solar and battery gaps hold and the wind and gas reversals do not "
                      "stand out from plant-to-plant noise.**", self.readme)
        t = self.table
        for g, lab in (("solar", "1 month minus first"), ("batteries", "1 month minus first"),
                       ("wind", "first minus 1 month"), ("gas", "first minus 1 month")):
            self.assertIn("%s (%s to %s)" % t[("2016-01", "2025-12", g, lab)].group(5, 6, 7), self.readme)
        self.assertIn("%s (%s to %s)" % t[("2022-01", "2026-08", "solar", "1 month minus 2-3 months")].group(5, 6, 7),
                      self.readme)


if __name__ == "__main__":
    unittest.main()
