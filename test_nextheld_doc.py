"""Doc test: every number in docs/nextheld.md (thirty-seventh result) is recomputed from
data/nexttech_cohort.csv, and the 2026 rows of data/nextcount_rows.csv, the month totals of
data/monthcheck_months_2026-09.csv, the job's raw output (docs/nextheld-v1-output.md), log and
unit-test log agree with the recomputation.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import collections
import csv
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EARLY, LATE, HELD = ("2016-01", "2019-12"), ("2022-01", "2025-12"), ("2026-01", "2026-08")
FINE = ((0, 0, "0"), (1, 1, "1"), (2, 2, "2"), (3, 3, "3"), (4, 4, "4"), (5, 9, "5-9"), (10, None, "10+"))
GAPS = ((1, 1, "1 month"), (2, 3, "2-3 months"), (4, 12, "4-12 months"), (13, None, "more than 12 months"))
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


def cell(rows):
    return sum(r["now"] == "Operating" for r in rows), len(rows)


def s(c):
    return c[0] / c[1]


def f(c):
    return "%.3f (%s of %s)" % (s(c), n(c[0]), n(c[1]))


def gp(rows):
    keys = set(r["key"] for r in rows)
    return len(keys), len(set(k.split("/")[0] for k in keys))


class NextheldDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs", "nextheld.md")
        cls.out = read("docs", "nextheld-v1-output.md")
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

    def first(self, p):
        return cell(self.sel(p, lambda r: r["prior"] == 0))

    def three(self, p):
        return cell(self.sel(p, lambda r: r["prior"] >= 3))

    def gap(self, p, name):
        return cell(self.sel(p, lambda r: r["gap"] is not None and label(r["gap"], GAPS) == name))

    def test_job_rows(self):
        with open(os.path.join(HERE, "data", "nextcount_rows.csv"), newline="", encoding="utf-8") as fh:
            job = [(x["month"], x["key"], x["now"], x["prior"], x["gap"]) for x in csv.DictReader(fh)
                   if HELD[0] <= x["month"] <= HELD[1]]
        mine = [(r["month"], r["key"], r["now"], str(r["prior"]), "" if r["gap"] is None else str(r["gap"]))
                for r in self.sel(HELD)]
        self.assertEqual(len(mine), 1194)
        self.assertEqual(job, mine)

    def test_c1(self):
        with open(os.path.join(HERE, "data", "monthcheck_months_2026-09.csv"), newline="", encoding="utf-8") as fh:
            known = {r["month"]: (int(r["cohort_operating"]), int(r["cohort"])) for r in csv.DictReader(fh)
                     if HELD[0] <= r["month"] <= HELD[1]}
        got = {m: cell(self.sel((m, m))) for m in known}
        self.assertEqual(len(got), 8)
        self.assertEqual(got, known)
        for m in sorted(got):
            self.assertIn("| %s | %d | %d |" % (m, got[m][0], got[m][1]), self.doc)
            self.assertIn("| %s | %d | %d |" % (m, got[m][0], got[m][1]), self.out)
        self.assertEqual(cell(self.sel(HELD)), (366, 1194))
        self.assertIn("| held | 366 of 1,194 in 8 months, each month equal |", self.doc)
        self.assertIn("| C1 | held | 366 of 1194 generator-months in 8 months |", self.out)
        self.assertEqual(("%.3f" % s(cell(self.sel(HELD))), "%.3f" % s(cell(self.sel(LATE)))), ("0.307", "0.349"))
        self.assertIn("as is the share of the whole group (0.307, against 0.349)", self.doc)

    def test_bars(self):
        z, t, one, two = self.first(HELD), self.three(HELD), self.gap(HELD, "1 month"), self.gap(HELD, "2-3 months")
        self.assertEqual((z, t, one, two), ((144, 473), (66, 244), (166, 479), (43, 173)))
        self.assertLess(s(t), s(z))
        self.assertGreater(s(one), s(two))
        self.assertGreater(s(one), s(z))
        self.assertGreaterEqual(min(c[1] for c in (z, t, one, two)), 30)
        self.assertIn("| held | %s against %s |" % (f(t), f(z)), self.doc)
        self.assertIn("| held | %s against %s |" % (f(one), f(two)), self.doc)
        self.assertIn("| held | %s against %s |" % (f(one), f(z)), self.doc)
        for s_ in ("| H1 | held | 0: 144 of 473; 3+: 66 of 244 |", "| H2 | held | 1 month: 166 of 479; 2-3 months: 43 of 173 |",
                   "| H3 | held | 1 month: 166 of 479; 0: 144 of 473 |", "Held: 3 of 3 scored",
                   "(950816 bytes, md5 1681df9fdee9878ca2c359d1239c6467; 14807 rows)."):
            self.assertIn(s_, self.out)
        self.assertIn("3 of 3 predictions held, and the reproduction check C1 held.", self.doc)

    def test_periods(self):
        cells = {"first listing (no earlier one)": self.first, "3 or more earlier listings": self.three,
                 "1 month after the last listing": lambda p: self.gap(p, "1 month"),
                 "2-3 months after the last listing": lambda p: self.gap(p, "2-3 months")}
        for name, fn in cells.items():
            self.assertIn("| %s | %s | %s | %s |" % (name, f(fn(EARLY)), f(fn(LATE)), f(fn(HELD))), self.doc)
            self.assertLess(s(fn(HELD)), s(fn(LATE)))
        h1 = ["%.3f" % (s(self.first(p)) - s(self.three(p))) for p in (LATE, HELD)]
        h2 = ["%.3f" % (s(self.gap(p, "1 month")) - s(self.gap(p, "2-3 months"))) for p in (EARLY, LATE, HELD)]
        h3 = ["%.3f" % (s(self.gap(p, "1 month")) - s(self.first(p))) for p in (LATE, HELD)]
        self.assertEqual((h1, h2, h3), (["0.056", "0.034"], ["0.007", "0.130", "0.098"], ["0.028", "0.042"]))
        for s_ in ("H2's margin was 0.098 in 2026, against 0.130 in 2022-2025 and 0.007 in 2016-2019.",
                   "H3's margin was 0.042 in 2026, larger than the 0.028 of 2022-2025",
                   "H1's margin was 0.034, against 0.056 in 2022-2025."):
            self.assertIn(s_, self.doc)

    def test_gaps(self):
        got = [self.gap(HELD, name) for _, _, name in GAPS]
        for (_, _, name), c in zip(GAPS, got):
            self.assertIn("| %s | %d | %d | %.3f |" % (name, c[1], c[0], s(c)), self.doc)
            keys = gp(self.sel(HELD, lambda r: r["gap"] is not None and label(r["gap"], GAPS) == name))
            self.assertIn("| 2026-01 to 2026-08 | %s | %d | %d | %.4f | %d | %d |" % (
                name, c[1], c[0], s(c), keys[0], keys[1]), self.out)
        self.assertTrue(all(s(got[i]) > s(got[i + 1]) for i in range(3)))
        self.assertEqual(got[3][1], 12)
        rep = cell(self.sel(HELD, lambda r: r["prior"] >= 1))
        self.assertEqual(rep, (sum(c[0] for c in got), sum(c[1] for c in got)))
        self.assertIn("0.308 (222 of 721) against 0.304", self.doc)
        self.assertEqual("%.3f" % s(rep), "0.308")

    def test_fine(self):
        for lo, hi, name in FINE:
            rows = self.sel(HELD, lambda r: label(r["prior"], ((lo, hi, name),)) == name)
            c, k = cell(rows), gp(rows)
            self.assertIn("| %s | %d | %d | %.3f | %d (%d) |" % (name, c[1], c[0], s(c), k[0], k[1]), self.doc)
            self.assertIn("| 2026-01 to 2026-08 | %s | %d | %d | %.4f | %d | %d |" % (
                name, c[1], c[0], s(c), k[0], k[1]), self.out)
        z = s(self.first(HELD))
        for a in (1, 2, 3, 4):
            self.assertGreaterEqual(s(cell(self.sel(HELD, lambda r, a=a: r["prior"] == a))), z)
        mid, five = cell(self.sel(HELD, lambda r: 3 <= r["prior"] <= 4)), cell(self.sel(HELD, lambda r: r["prior"] >= 5))
        self.assertIn("generators with 3 or 4 were on time %s" % f(mid), self.doc)
        self.assertIn("The H1 gap comes from 5 or more earlier listings: %s." % f(five), self.doc)
        self.assertEqual(("%.3f" % s(mid), "%.3f" % s(five)), ("0.336", "0.163"))

    def test_tech(self):
        z, t = {}, {}
        for g in GROUPS:
            z[g] = cell(self.sel(HELD, lambda r, g=g: r["group"] == g and r["prior"] == 0))
            t[g] = cell(self.sel(HELD, lambda r, g=g: r["group"] == g and r["prior"] >= 3))
            self.assertIn("| %s | %s | %s |" % (g, f(z[g]), f(t[g])), self.doc)
        n0, n3 = sum(z[g][1] for g in GROUPS), sum(t[g][1] for g in GROUPS)
        self.assertEqual((n0, n3), (473, 244))
        all0, all3 = sum(z[g][0] for g in GROUPS) / n0, sum(t[g][0] for g in GROUPS) / n3
        std3 = sum(z[g][1] / n0 * s(t[g]) for g in GROUPS)
        alt0 = sum(t[g][1] / n3 * s(z[g]) for g in GROUPS)
        part = {g: z[g][1] / n0 * (s(z[g]) - s(t[g])) for g in GROUPS}
        self.assertAlmostEqual(all0 - std3, sum(part.values()))
        self.assertEqual(["%.3f" % x for x in (std3, all0 - std3, alt0, alt0 - all3)], ["0.266", "0.039", "0.279", "0.009"])
        self.assertIn("by its part of the rows with none gives 0.266, so with that mix the gap is 0.039. With the mix "
                      "of the rows with 3 or more, the share with none would be 0.279 and the gap only 0.009.", self.doc)
        self.assertEqual(["%.3f" % x for x in (part["solar"], part["gas"] + part["wind"], -part["batteries"],
                                                -part["other"])], ["0.025", "0.044", "0.016", "0.014"])
        self.assertIn("Of the 0.039, solar gives 0.025 and gas and wind 0.044, while batteries take away 0.016 and "
                      "other technologies 0.014", self.doc)
        self.assertEqual((t["gas"][1], t["wind"][1], t["other"][1]), (6, 11, 8))
        self.assertIn("the gas, wind and other cells with 3 or more have 6, 11 and 8 rows", self.doc)
        self.assertEqual(gp(self.sel(HELD, lambda r: r["group"] == "gas" and r["prior"] == 0))[1], 13)
        self.assertIn("Gas first listings (%s, at 13 plants)" % f(z["gas"]).replace(" (", ", ", 1)[:-1], self.doc)
        self.assertGreater(s(t["batteries"]), s(z["batteries"]))
        late = [cell(self.sel(LATE, lambda r, c=c: r["group"] == "batteries" and c(r["prior"])))
                for c in (lambda p: p == 0, lambda p: p >= 3)]
        self.assertGreater(s(late[1]), s(late[0]))
        self.assertIn("as in 2022-2025 (%s with none against %s with 3 or more)" % (
            "%.3f" % s(late[0]), "%.3f" % s(late[1])), self.doc)
        self.assertEqual("%.3f" % (s(z["solar"]) - s(t["solar"])), "0.041")
        self.assertIn("For solar, the largest group, the gap is 0.041.", self.doc)

    def test_reader(self):
        pct = lambda c: "%.0f%%" % (100 * s(c))
        got = [pct(c) for c in (self.gap(HELD, "1 month"), self.first(HELD), self.gap(HELD, "2-3 months"),
                                self.gap(HELD, "4-12 months"), cell(self.sel(HELD, lambda r: r["prior"] >= 5)))]
        self.assertEqual(got, ["35%", "30%", "25%", "21%", "16%"])
        for s_ in ("right after a one-month slip was listed as operating in that month 35% of the time, and a first "
                   "listing 30% of the time", "after a slip of 2-3 months was listed 25% of the time, after 4-12 "
                   "months 21%, and one planned for the next month five or more times before 16%"):
            self.assertIn(s_, self.doc)

    def test_order_of_events(self):
        log = read("docs", "nextheld-v1-stdout.txt").splitlines()
        self.assertEqual(log[0], "2026-10-24T09:20:31Z plan served: "
                                 "https://raw.githubusercontent.com/munimtechnologies/eia860m-slip/main/docs/nextheld-plan.md")
        self.assertEqual(log[1], "cohort file 950816 bytes, md5 1681df9fdee9878ca2c359d1239c6467, 14807 rows")
        self.assertGreater("2026-10-24T09:20:31Z", "2026-10-24T08:58:33Z")
        self.assertIn("The plan was committed at 08:58:33 UTC on 24 October 2026 (commit f72579e).", self.doc)
        self.assertIn("The job's first poll, at 09:20:31 UTC, was served the plan", self.doc)
        self.assertIn("(950,816 bytes, md5 1681df9fdee9878ca2c359d1239c6467, 14,807 rows)", self.doc)
        unit = read("docs", "nextheld-v1-unittests.txt")
        self.assertIn("Ran 11 tests", unit)
        self.assertTrue(unit.rstrip().endswith("OK"))
        self.assertIn("after its 11 unit tests passed", self.doc)
        self.assertIn("Status: pre-registered, not yet scored.", read("docs", "nextheld-plan.md"))

    def test_readme(self):
        self.assertIn("| 37 | In January to August 2026, generators planned for the next month right after a one-month "
                      "slip were on time more often than new listings, and those back after a longer slip less often "
                      "(3 of 3 held) | [`nextheld.md`](docs/nextheld.md) |", self.readme)
        self.assertIn("(thirty-seventh result, scored against [`docs/nextheld-plan.md`](docs/nextheld-plan.md); "
                      "3 of 3 held)", self.readme)
        for s_ in ("**In 2026, the months since the last listing matter most.**",
                   "were on time 0.347, first listings 0.304, and those back after a slip of 2-3 months 0.249",
                   "Generators with 3 or more earlier listings were on time 0.270",
                   "Repeat listings as a whole were on time about as often as first listings (0.308 against 0.304).",
                   "comes from 5 or more earlier listings (0.163)", "shrinks to 0.009"):
            self.assertIn(s_, self.readme)


if __name__ == "__main__":
    unittest.main()
