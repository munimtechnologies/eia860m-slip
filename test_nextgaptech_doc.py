"""Doc test: every number in docs/nextgaptech.md (thirty-eighth result) is recomputed from
data/nexttech_cohort.csv, and the job's raw output (docs/nextgaptech-v2-output.md), log and unit-test
log agree with the recomputation.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import collections
import csv
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EARLY, LATE, HELD = ("2016-01", "2019-12"), ("2022-01", "2025-12"), ("2026-01", "2026-08")
PERIODS = ((EARLY, "2016-2019"), (LATE, "2022-2025"), (HELD, "January-August 2026"))
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


class NextgaptechDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs", "nextgaptech.md")
        cls.out = read("docs", "nextgaptech-v2-output.md")
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
        self.assertEqual([cell(self.sel(p)) for p, _ in PERIODS], [(1980, 4223), (2110, 6047), (366, 1194)])
        self.assertEqual((self.c(LATE, "solar", "first"), self.c(LATE, "batteries", "first")), ((536, 1483), (143, 514)))
        self.assertIn("| held | 14,807 rows; 1,980 of 4,223, 2,110 of 6,047 and 366 of 1,194; solar 536 of 1,483, "
                      "batteries 143 of 514 |", self.doc)
        self.assertIn("| C0 | held | 14807 rows; 1980 of 4223, 2110 of 6047, 366 of 1194; first listings 2022-2025: "
                      "solar 536 of 1483, batteries 143 of 514 |", self.out)

    def test_bars(self):
        bars = (("G1", LATE, "solar", "1 month", "first"), ("G2", LATE, "solar", "1 month", "2-3 months"),
                ("G3", HELD, "solar", "1 month", "2-3 months"), ("G4", LATE, "batteries", "1 month", "first"))
        margins = []
        for pid, p, g, x, y in bars:
            a, b = self.c(p, g, x), self.c(p, g, y)
            self.assertGreater(s(a), s(b))
            self.assertGreaterEqual(min(a[1], b[1]), 30)
            self.assertIn("| held | %s against %s |" % (f(a), f(b)), self.doc)
            self.assertIn("| %s | held | %s: %d of %d; %s: %d of %d |" % (pid, x, a[0], a[1], y, b[0], b[1]), self.out)
            margins.append("%.3f" % (s(a) - s(b)))
        self.assertEqual(margins, ["0.043", "0.131", "0.098", "0.071"])
        self.assertIn("The margins were 0.043 (G1), 0.131 (G2), 0.098 (G3) and 0.071 (G4).", self.doc)
        self.assertIn("Held: 4 of 4 scored", self.out)
        self.assertIn("4 of 4 predictions held, and the reproduction check C0 held.", self.doc)
        one = cell(self.sel(LATE, lambda r: r["group"] == "solar" and r["prior"] == 1))
        self.assertEqual(one, (312, 860))
        self.assertEqual(("%.3f" % s(one), "%.3f" % s(self.c(LATE, "solar", "first"))), ("0.363", "0.361"))
        self.assertIn("about as often as a new one (0.363 against 0.361)", self.doc)

    def test_plants(self):
        got = [gp(self.rows_of(p, g, x)) for p, g, x in (
            (LATE, "solar", "1 month"), (LATE, "solar", "2-3 months"), (HELD, "solar", "1 month"),
            (HELD, "solar", "2-3 months"), (LATE, "batteries", "1 month"), (LATE, "gas", "1 month"))]
        self.assertEqual(got, [(682, 662), (386, 370), (156, 145), (81, 77), (303, 287), (67, 32)])
        self.assertIn("solar's 2022-2025 one-month cell has %d generators at %d plants and its 2-3 month cell %d at %d; "
                      "in 2026 they have %d at %d and %d at %d; batteries' 2022-2025 one-month cell has %d at %d." % (
                          got[0] + got[1] + got[2] + got[3] + got[4]), self.doc)
        self.assertIn("gas's 2022-2025 one-month cell has %d generators at %d plants" % got[5], self.doc)

    def test_table(self):
        for g in ("solar", "batteries", "gas", "wind"):
            for p, name in PERIODS:
                self.assertIn("| %s | %s | %s | %s | %s |" % (
                    g, name, f(self.c(p, g, "first")), f(self.c(p, g, "1 month")), f(self.c(p, g, "2-3 months"))),
                    self.doc)
        lines = 0
        for p, _ in PERIODS:
            for g in (None,) + GROUPS:
                for name in CELLS:
                    rows = self.rows_of(p, g, name)
                    if not rows:
                        continue
                    c, k = cell(rows), gp(rows)
                    self.assertIn("| %s to %s | %s | %s | %d | %d | %.4f | %d | %d |" % (
                        p[0], p[1], g or "all", name, c[1], c[0], s(c), k[0], k[1]), self.out)
                    lines += 1
        self.assertEqual(lines, self.out.count("\n| 20"))

    def test_not_bars(self):
        d = lambda p, g, x, y: "%.3f" % (s(self.c(p, g, x)) - s(self.c(p, g, y)))
        self.assertEqual((d(HELD, "solar", "1 month", "first"), d(HELD, "batteries", "1 month", "first")),
                         ("0.036", "0.122"))
        self.assertIn("solar's one-month cell was above its first listings by 0.036 and batteries' by 0.122", self.doc)
        self.assertEqual((d(EARLY, "solar", "1 month", "2-3 months"), d(LATE, "solar", "1 month", "2-3 months")),
                         ("0.030", "0.131"))
        self.assertIn("by only 0.030, against 0.131 in 2022-2025", self.doc)
        gas = [d(p, "gas", "first", "1 month") for p in (EARLY, LATE)]
        wind = [d(p, "wind", "first", "1 month") for p in (EARLY, LATE)]
        self.assertEqual((gas, wind), (["0.092", "0.190"], ["0.014", "0.071"]))
        self.assertIn("by 0.092 in 2016-2019 and 0.190 in 2022-2025; wind, by 0.014 and 0.071", self.doc)
        sb = cell(self.sel(LATE, lambda r: r["group"] in ("solar", "batteries")))[1] / len(self.sel(LATE))
        self.assertEqual("%.0f%%" % (100 * sb), "85%")
        self.assertIn("(85% of the generator-months of 2022-2025)", self.doc)

    def test_reader(self):
        pct = lambda c: "%.0f%%" % (100 * s(c))
        sol = [pct(self.c(LATE, "solar", x)) for x in ("1 month", "first", "2-3 months")]
        bat = [pct(self.c(LATE, "batteries", x)) for x in ("1 month", "first", "2-3 months")]
        self.assertEqual((sol, bat), (["40%", "36%", "27%"], ["35%", "28%", "22%"]))
        self.assertIn("listed as operating in that month 40% of the time, a new solar listing 36% of the time, and one "
                      "back after a slip of 2-3 months 27%", self.doc)
        self.assertIn("For batteries the three were 35%, 28% and 22%.", self.doc)

    def test_order_of_events(self):
        log = read("docs", "nextgaptech-v2-stdout.txt").splitlines()
        self.assertEqual([i for i, x in enumerate(log) if " plan served: " in x], [28])
        self.assertTrue(all(x.endswith(" plan not served yet: HTTPError: HTTP Error 404: Not Found") for x in log[:28]))
        self.assertEqual((log[0][:20], log[27][:20]), ("2026-10-24T18:07:29Z", "2026-10-24T22:37:31Z"))
        self.assertEqual(log[28], "2026-10-24T22:47:32Z plan served: "
                                  "https://raw.githubusercontent.com/munimtechnologies/eia860m-slip/main/docs/nextgaptech-plan.md")
        self.assertEqual(log[29], "cohort file 950816 bytes, md5 1681df9fdee9878ca2c359d1239c6467, 14807 rows")
        self.assertLess("2026-10-24T22:39:37Z", log[28][:20])
        self.assertIn("The plan was committed at 22:39:37 UTC on 24 October 2026 (commit 85fd467).", self.doc)
        self.assertIn("refused at each of its 28 polls up to 22:37:31 UTC. Its next poll, at 22:47:32 UTC, was served "
                      "the plan", self.doc)
        self.assertIn("(950,816 bytes, md5 1681df9fdee9878ca2c359d1239c6467, 14,807 rows)", self.doc)
        unit = read("docs", "nextgaptech-v2-unittests.txt")
        self.assertIn("Ran 11 tests", unit)
        self.assertTrue(unit.rstrip().endswith("OK"))
        self.assertIn("after its 11 unit tests passed", self.doc)
        self.assertIn("Status: pre-registered, not yet scored.", read("docs", "nextgaptech-plan.md"))

    def test_readme(self):
        self.assertIn("| 38 | Within solar and within batteries, a generator planned for the next month right after a "
                      "one-month slip was on time more often than a new listing, and in solar more often than one back "
                      "after a 2-3 month slip (4 of 4 held) | [`nextgaptech.md`](docs/nextgaptech.md) |", self.readme)
        self.assertIn("(thirty-eighth result, scored against [`docs/nextgaptech-plan.md`](docs/nextgaptech-plan.md); "
                      "4 of 4 held)", self.readme)
        for s_ in ("**Within solar and batteries, a one-month slip is a mildly good sign.**",
                   "were on time 0.404, new solar listings 0.361, and those back after a slip of 2-3 months 0.273",
                   "in January to August 2026, 0.326 against 0.229", "Batteries: 0.349 against 0.278",
                   "was on time 0.320 in 2022-2025, a new one 0.510"):
            self.assertIn(s_, self.readme)


if __name__ == "__main__":
    unittest.main()
