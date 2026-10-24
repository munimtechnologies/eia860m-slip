"""Doc test: every number in docs/nextcount.md (thirty-sixth result) is recomputed from
data/nexttech_cohort.csv, and the job's rows (data/nextcount_rows.csv), raw output
(docs/nextcount-v1-output.md), log and unit-test log agree with the recomputation.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import collections
import csv
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EARLY, LATE = ("2016-01", "2019-12"), ("2022-01", "2025-12")
BINS = ("0", "1", "2", "3+")
FINE = ((3, 3, "3"), (4, 4, "4"), (5, 9, "5-9"), (10, None, "10+"))
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


def coarse(prior):
    return "3+" if prior >= 3 else str(prior)


def cell(rows):
    return sum(r["now"] == "Operating" for r in rows), len(rows)


def s(c):
    return c[0] / c[1]


def f(c):
    return "%.3f (%s of %s)" % (s(c), n(c[0]), n(c[1]))


class NextcountDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs", "nextcount.md")
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

    def bins(self, period, test=lambda r: True):
        return {b: cell(self.sel(period, lambda r, b=b: coarse(r["prior"]) == b and test(r))) for b in BINS}

    def test_job_rows(self):
        with open(os.path.join(HERE, "data", "nextcount_rows.csv"), newline="", encoding="utf-8") as fh:
            job = [(x["month"], x["key"], x["group"], x["now"], x["prior"], x["gap"]) for x in csv.DictReader(fh)]
        mine = [(r["month"], r["key"], r["group"], r["now"], str(r["prior"]), "" if r["gap"] is None else str(r["gap"]))
                for r in self.rows]
        self.assertEqual(len(mine), 14807)
        self.assertEqual(job, mine)
        self.assertIn("(one row per generator and cohort month, 14,807 rows,", self.doc)

    def test_c0(self):
        for p, k in ((EARLY, (1980, 4223)), (LATE, (2110, 6047))):
            self.assertEqual(cell(self.sel(p)), k)
        self.assertIn("| C0 (check). 14,807 rows that reproduce 1,980 of 4,223 and 2,110 of 6,047 generator-months | "
                      "held | 14,807 rows; 1,980 of 4,223 and 2,110 of 6,047 |", self.doc)

    def test_bars(self):
        e, l = self.bins(EARLY), self.bins(LATE)
        self.assertEqual(e, {"0": (969, 2110), "1": (532, 1087), "2": (253, 523), "3+": (226, 503)})
        self.assertEqual(l, {"0": (866, 2393), "1": (515, 1412), "2": (301, 844), "3+": (428, 1398)})
        self.assertGreater(s(l["0"]), s(l["3+"]))
        self.assertIn("| held | %s against %s |" % (f(l["0"]), f(l["3+"])), self.doc)
        self.assertGreater(s(l["1"]), s(l["0"]))
        self.assertGreater(s(l["1"]), s(l["2"]))
        self.assertGreater(s(l["2"]), s(l["3+"]))
        self.assertIn("| failed | %s |" % ", ".join("%.3f" % s(l[b]) for b in BINS), self.doc)
        self.assertEqual("%.3f" % (s(l["1"]) - s(l["0"])), "0.003")
        self.assertIn("the share rises by 0.003 from no earlier listing to one", self.doc)
        self.assertIn("from 0.362 with no earlier listing to 0.365 with one, by 0.003", self.doc)
        ge, gl = s(e["0"]) - s(e["3+"]), s(l["0"]) - s(l["3+"])
        self.assertLess(ge, gl)
        self.assertEqual(("%.3f" % ge, "%.3f" % gl), ("0.010", "0.056"))
        self.assertIn("| held | 0.010 against 0.056 |", self.doc)
        self.assertIn("the gap was 0.010 in 2016-2019 and 0.056 in 2022-2025", self.doc)
        for b in BINS:
            self.assertIn("| %s | %s | %s |" % (b, f(e[b]), f(l[b])), self.doc)
        out = read("docs", "nextcount-v1-output.md")
        for s_ in ("| C0 | held |", "| K1 | held |", "| K2 | failed |", "| K3 | held |", "Held: 2 of 3 scored",
                   "md5 1681df9fdee9878ca2c359d1239c6467; 14807 rows; repeated generator and month rows: 0"):
            self.assertIn(s_, out)
        self.assertIn("2 of 3 predictions held, and the reproduction check C0 held. K2 failed", self.doc)

    def test_fine(self):
        for lo, hi, name in FINE:
            got = [cell(self.sel(p, lambda r: label(r["prior"], ((lo, hi, name),)) == name)) for p in (EARLY, LATE)]
            self.assertIn("| %s | %s | %s |" % (name, f(got[0]), f(got[1])), self.doc)
        for p, k in ((EARLY, (7, 2)), (LATE, (20, 15))):
            g = self.sel(p, lambda r: r["prior"] >= 10)
            keys = set(r["key"] for r in g)
            self.assertEqual((len(keys), len(set(x.split("/")[0] for x in keys))), k)
        self.assertIn("7 generators at 2 plants in 2016-2019 and 20 generators at 15 plants in 2022-2025", self.doc)
        three, four, mid = (cell(self.sel(LATE, lambda r, a=a, b=b: a <= r["prior"] <= b)) for a, b in ((3, 3), (4, 4), (5, 9)))
        self.assertEqual("%.3f" % s(three), "0.348")
        self.assertTrue(0.295 < s(mid) < s(four) < 0.31)
        self.assertIn("(0.348 with 3, about 0.30 with 4 to 9)", self.doc)
        e0 = s(self.bins(EARLY)["0"])
        for a, b in ((1, 1), (2, 2), (3, 3), (4, 4)):
            self.assertGreaterEqual(s(cell(self.sel(EARLY, lambda r, a=a: r["prior"] == a))), e0)
        self.assertLess(s(cell(self.sel(EARLY, lambda r: 5 <= r["prior"] <= 9))), e0)
        self.assertIn("In 2016-2019 the share was flat or higher up to 4 earlier listings and lower only from 5.",
                      self.doc)

    def test_plant(self):
        plant = lambda r: r["key"].split("/")[0] == "60264"
        p3 = cell(self.sel(EARLY, lambda r: plant(r) and r["prior"] >= 3))
        self.assertEqual(p3, (6, 66))
        self.assertEqual(len(self.sel(LATE, plant)), 0)
        w = self.bins(EARLY, lambda r: not plant(r))
        self.assertEqual((w["0"], w["3+"]), ((969, 2098), (220, 437)))
        self.assertGreater(s(w["3+"]), s(w["0"]))
        self.assertIn("its 66 generator-months there were on time 6 times", self.doc)
        self.assertIn("is %s, above %s with none" % (f(w["3+"]), f(w["0"])), self.doc)
        self.assertIn("The plant has no rows in 2022-2025.", self.doc)

    def test_gaps(self):
        firsts = [cell(self.sel(p, lambda r: r["gap"] is None)) for p in (EARLY, LATE)]
        self.assertEqual(firsts, [self.bins(EARLY)["0"], self.bins(LATE)["0"]])
        self.assertIn("| first listing (no earlier one) | %s | %s |" % (f(firsts[0]), f(firsts[1])), self.doc)
        got = {}
        for lo, hi, name in GAPS:
            got[name] = [cell(self.sel(p, lambda r: r["gap"] is not None and label(r["gap"], GAPS) == name))
                         for p in (EARLY, LATE)]
            self.assertIn("| %s | %s | %s |" % (name, f(got[name][0]), f(got[name][1])), self.doc)
        one, two = got["1 month"], got["2-3 months"]
        self.assertGreater(s(one[1]), s(firsts[1]))
        self.assertIn("(0.390 against 0.362)", self.doc)
        self.assertIn("after a gap of 2-3 months: 0.260", self.doc)
        self.assertIn("(0.492 against 0.499)", self.doc)
        self.assertEqual(("%.3f" % s(two[0]), "%.3f" % s(one[0])), ("0.492", "0.499"))
        falls = ["%.3f" % (s(c[0]) - s(c[1])) for c in (firsts, one, two)]
        self.assertEqual(falls, ["0.097", "0.110", "0.233"])
        self.assertIn("the share fell by 0.097 for first listings, by 0.110 for one-month slips and by 0.233 for "
                      "slips of 2-3 months", self.doc)
        longer = []
        for i in (0, 1):
            rep = sum(got[name][i][1] for name in got)
            self.assertEqual(rep, sum(self.bins((EARLY, LATE)[i])[b][1] for b in ("1", "2", "3+")))
            longer.append("%.1f%%" % (100 * (rep - one[i][1]) / rep))
        self.assertEqual(longer, ["29.3%", "38.3%"])
        self.assertIn("grew from 29.3% to 38.3% of all repeat listings", self.doc)
        self.assertIn("36% to 39% of the time", self.doc)
        self.assertEqual(("%.0f" % (100 * s(firsts[1])), "%.0f" % (100 * s(one[1]))), ("36", "39"))
        self.assertEqual(("%.0f" % (100 * s(self.bins(LATE)["3+"])), "%.0f" % (100 * s(two[1]))), ("31", "26"))
        self.assertIn("listed 31% of the time, and one back after a slip of 2-3 months 26% of the time", self.doc)

    def test_tech(self):
        z, t, gp = {}, {}, {}
        for g in GROUPS:
            z[g] = cell(self.sel(LATE, lambda r, g=g: r["group"] == g and r["prior"] == 0))
            rows3 = self.sel(LATE, lambda r, g=g: r["group"] == g and r["prior"] >= 3)
            t[g] = cell(rows3)
            keys = set(r["key"] for r in rows3)
            gp[g] = (len(keys), len(set(k.split("/")[0] for k in keys)))
            self.assertIn("| %s | %s | %s | %d (%d) |" % (g, f(z[g]), f(t[g]), gp[g][0], gp[g][1]), self.doc)
        n0, n3 = sum(z[g][1] for g in GROUPS), sum(t[g][1] for g in GROUPS)
        self.assertEqual((n0, n3), (2393, 1398))
        all0, all3 = sum(z[g][0] for g in GROUPS) / n0, sum(t[g][0] for g in GROUPS) / n3
        part = {g: z[g][1] / n0 * (s(z[g]) - s(t[g])) for g in GROUPS}
        std3 = sum(z[g][1] / n0 * s(t[g]) for g in GROUPS)
        gap = all0 - std3
        self.assertAlmostEqual(gap, sum(part.values()))
        self.assertEqual(("%.3f" % std3, "%.3f" % gap, "%.3f" % (all0 - all3)), ("0.303", "0.059", "0.056"))
        alt0 = sum(t[g][1] / n3 * s(z[g]) for g in GROUPS)
        self.assertEqual(("%.3f" % alt0, "%.3f" % (alt0 - all3)), ("0.352", "0.046"))
        self.assertIn("by its part of the rows with none gives 0.303, so with the same mix the gap is 0.059, a little "
                      "more than the 0.056 measured; with the mix of the rows with 3 or more, the share with none "
                      "would be 0.352 and the gap 0.046.", self.doc)
        self.assertEqual(["%.3f" % x for x in (part["gas"] + part["wind"], part["solar"], part["other"], -part["batteries"])],
                         ["0.042", "0.018", "0.006", "0.007"])
        self.assertIn("Of the 0.059, gas and wind give 0.042, solar 0.018 and other technologies 0.006, and "
                      "batteries take away 0.007", self.doc)
        self.assertGreater(s(t["batteries"]), s(z["batteries"]))
        self.assertEqual("%.1f%%" % (100 * (z["gas"][1] + z["wind"][1]) / n0), "13.2%")
        self.assertIn("Gas and wind are 13.2% of the rows with no earlier listing", self.doc)
        self.assertEqual((gp["gas"], gp["wind"]), ((26, 16), (18, 16)))
        self.assertIn("26 gas generators at 16 plants and 18 wind generators at 16 plants", self.doc)

    def test_order_of_events(self):
        log = read("docs", "nextcount-v1-stdout.txt").splitlines()
        self.assertEqual(log[0], "2026-10-24T07:28:19Z plan served: "
                                 "https://raw.githubusercontent.com/munimtechnologies/eia860m-slip/main/docs/nextcount-plan.md")
        self.assertEqual(log[1], "cohort file 950816 bytes, md5 1681df9fdee9878ca2c359d1239c6467, 14807 rows")
        self.assertGreater("2026-10-24T07:28:19Z", "2026-10-24T07:20:25Z")
        self.assertIn("The plan was committed at 07:20:25 UTC on 24 October 2026 (commit bdd4b8b).", self.doc)
        self.assertIn("its first poll, at 07:28:19 UTC, was served the plan", self.doc)
        self.assertIn("(950,816 bytes, md5 1681df9fdee9878ca2c359d1239c6467, 14,807 rows,", self.doc)
        unit = read("docs", "nextcount-v1-unittests.txt")
        self.assertIn("Ran 13 tests", unit)
        self.assertTrue(unit.rstrip().endswith("OK"))
        self.assertIn("after its 13 unit tests passed", self.doc)
        self.assertIn("Status: pre-registered, not yet scored.", read("docs", "nextcount-plan.md"))

    def test_readme(self):
        self.assertIn("| 36 | After three or more earlier misses, a generator planned for the next month is on time less "
                      "often, and that gap is new since 2016-2019 (2 of 3 held) | [`nextcount.md`](docs/nextcount.md) |",
                      self.readme)
        self.assertIn("(thirty-sixth result, scored against [`docs/nextcount-plan.md`](docs/nextcount-plan.md); "
                      "2 of 3 held)", self.readme)
        for s_ in ("**After three or more misses, a generator planned for the next month is on time less often.**",
                   "In 2022-2025 the share was 0.362 with none, 0.365 with one, 0.357 with two and 0.306 with three "
                   "or more", "the gap between none and three or more was 0.010 in 2016-2019, against 0.056",
                   "K2 failed: the share rises by 0.003 from none to one.",
                   "right after a one-month slip were on time 0.390 in 2022-2025; those back after a slip of 2-3 "
                   "months, 0.260, against 0.492 in 2016-2019", "Most of the 2022-2025 gap is in gas and wind"):
            self.assertIn(s_, self.readme)


if __name__ == "__main__":
    unittest.main()
