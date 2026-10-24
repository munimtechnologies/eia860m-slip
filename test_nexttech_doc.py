"""Doc test: the numbers in docs/nexttech.md match the raw output of job nexttech-v1
(docs/nexttech-v1-output.md, docs/nexttech-v1-stdout.txt, docs/nexttech-v1-unittests.txt,
data/nexttech_years.csv), and every share, count and split in it is recomputed from
data/nexttech_cohort.csv.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import csv
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EARLY, LATE = ("2016-01", "2019-12"), ("2022-01", "2025-12")
GROUPS = ("solar", "batteries", "gas", "wind", "other")
GAS = ("Natural Gas Internal Combustion Engine", "Natural Gas Fired Combustion Turbine",
       "Natural Gas Fired Combined Cycle")
PLANT = "60264/"


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8") as fh:
        return fh.read()


def rows(*parts):
    with open(os.path.join(HERE, *parts), newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def n(x):
    return "{:,}".format(x)


def frac(sel):
    return sum(1 for r in sel if r["now"] == "Operating"), len(sel)


def share(sel):
    op, k = frac(sel)
    return op / k


def cell(sel):
    op, k = frac(sel)
    return "%.3f (%s of %s)" % (op / k, n(op), n(k))


def mw_share(sel):
    return sum(float(r["nameplate_mw"]) for r in sel if r["now"] == "Operating") / sum(
        float(r["nameplate_mw"]) for r in sel)


class NexttechDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs", "nexttech.md")
        cls.plan = read("docs", "nexttech-plan.md")
        cls.out = read("docs", "nexttech-v1-output.md")
        cls.log = read("docs", "nexttech-v1-stdout.txt")
        cls.ut = read("docs", "nexttech-v1-unittests.txt")
        cls.co = rows("data", "nexttech_cohort.csv")
        cls.years = rows("data", "nexttech_years.csv")

    def per(self, period, group=None, keep=None):
        return [r for r in self.co if period[0] <= r["month"] <= period[1]
                and (group is None or r["group"] == group) and (keep is None or keep(r))]

    def year(self, y, group):
        return [r for r in self.co if r["month"][:4] == y and r["group"] == group]

    def test_status(self):
        self.assertIn("Status: pre-registered, not yet scored.", self.plan)
        self.assertIn("Held: 3 of 4 scored (T0 is a check, not counted).", self.out)
        for s in ("| T0 | held |", "| T1 | held |", "| T2 | failed |", "| T3 | held |", "| T4 | held |"):
            self.assertIn(s, self.out)
        self.assertIn("3 of 4 predictions held, and the reproduction check T0 held. T2 failed: natural gas's "
                      "share rose.", self.doc)

    def test_order(self):
        self.assertTrue(self.log.startswith("2026-10-23T22:29:24Z plan served: "))
        self.assertNotIn("not served yet", self.log)
        self.assertLess(self.log.index("plan served:"), self.log.index("changelog 1054060 bytes, 117756 rows"))
        self.assertIn("cohort months 134, generators 14807", self.log)
        self.assertEqual(len(self.co), 14807)
        self.assertEqual((min(r["month"] for r in self.co), max(r["month"] for r in self.co)), ("2015-08", "2026-09"))
        self.assertIn("Expected 1054060 bytes and 117756 rows: True.", self.out)
        self.assertIn("Workbooks read: 134. With errors: none.", self.out)
        for s in ("was served the plan on its first poll at 22:29:24 UTC", "(1,054,060 bytes, 117,756 rows, the "
                  "expected file) and 134 workbooks", "with no read errors", "14,807 rows",
                  "after its 11 unit tests passed"):
            self.assertIn(s, self.doc)
        self.assertIn("Ran 11 tests", self.ut)
        self.assertIn("\nOK", self.ut)

    def test_t0(self):
        self.assertEqual((frac(self.per(EARLY)), frac(self.per(LATE))), ((1980, 4223), (2110, 6047)))
        miss = [len(self.per(p, keep=lambda r: r["found"] == "False")) for p in (EARLY, LATE)]
        self.assertEqual(miss, [32, 25])
        self.assertEqual({r["group"] for r in self.co if r["found"] == "False"}, {"other"})
        self.assertIn("| held | 1,980 of 4,223 and 2,110 of 6,047; 32 and 25 without a technology |", self.doc)
        self.assertIn("are %.2f%% and %.2f%% of their periods' cohorts" % (100 * 32 / 4223, 100 * 25 / 6047), self.doc)

    def test_groups(self):
        for g in GROUPS + (None,):
            e, l = self.per(EARLY, g), self.per(LATE, g)
            self.assertIn("| %s | %s | %s |" % (g or "all", cell(e), cell(l)), self.doc)
            for p, sel in ((EARLY, e), (LATE, l)):
                op, k = frac(sel)
                self.assertIn("| %s to %s | %s | %d | %d |" % (p[0], p[1], g or "all", k, op), self.out)
        for g, outcome in (("solar", "held"), ("gas", "failed"), ("batteries", "held")):
            e, l = self.per(EARLY, g), self.per(LATE, g)
            self.assertEqual(share(l) < share(e), outcome == "held")
            self.assertIn("| %s | %s to %s |" % (outcome, cell(e), cell(l)), self.doc)

    def test_t4(self):
        n_early, n_late = len(self.per(EARLY)), len(self.per(LATE))
        std = sum(len(self.per(EARLY, g)) / n_early * share(self.per(LATE, g)) for g in GROUPS)
        s_e, s_l = share(self.per(EARLY)), share(self.per(LATE))
        within, total = s_e - std, s_e - s_l
        self.assertTrue(within >= total / 2)
        self.assertEqual(("%.3f" % std, "%.3f" % within, "%.3f" % total), ("0.374", "0.094", "0.120"))
        pct = round(100 * within / total)
        self.assertEqual(pct, 79)
        self.assertIn("within 0.0945 of total 0.1199 (standardized 0.3744)", self.out)
        for s in ("| held | 0.094 of 0.120 |", "gives 0.374", "the share would have fallen from 0.469 to 0.374",
                  "a within-technology fall of 0.094, against a total fall of 0.120. That is %d%% of the fall." % pct,
                  "The other %d%% is the change of mix" % (100 - pct)):
            self.assertIn(s, self.doc)

        def mix(g):
            return ("%.1f%%" % (100 * len(self.per(EARLY, g)) / n_early),
                    "%.1f%%" % (100 * len(self.per(LATE, g)) / n_late))
        self.assertIn("Batteries were %s of the 2016-2019 cohort and %s of the 2022-2025 cohort." % mix("batteries"),
                      self.doc)
        self.assertIn("Gas went from %s to %s, wind from %s to %s, other technologies from %s to %s, and solar from "
                      "%s to %s." % (mix("gas") + mix("wind") + mix("other") + mix("solar")), self.doc)

    def test_mw(self):
        def pair(g):
            return "%.3f to %.3f" % (mw_share(self.per(EARLY, g)), mw_share(self.per(LATE, g)))
        self.assertIn("solar went from %s, batteries from %s, gas from %s, and all technologies from %s." % (
            pair("solar"), pair("batteries"), pair("gas"), pair(None)), self.doc)
        zero = [r for r in self.co if r["month"] <= "2016-04"]
        self.assertTrue(all(float(r["nameplate_mw"]) == 0 for r in zero))
        self.assertEqual(len([r for r in zero if r["month"] >= "2016-01"]), 259)
        self.assertIn("0.0 MW for all 259 cohort generators of January to April 2016 (and for every one of 2015)",
                      self.doc)

    def test_gas(self):
        for name in GAS:
            sel = [self.per(p, "gas", lambda r: r["technology"] == name) for p in (EARLY, LATE)]
            self.assertIn("| %s | %s | %s |" % (name, cell(sel[0]), cell(sel[1])), self.doc)
        rest = [self.per(p, "gas", lambda r: r["technology"] not in GAS) for p in (EARLY, LATE)]
        self.assertIn("| other gas technologies | %s | %s |" % (cell(rest[0]), cell(rest[1])), self.doc)
        plant = [r for r in self.co if r["key"].startswith(PLANT)]
        self.assertEqual(len(plant), 102)
        self.assertEqual(plant, self.per(EARLY, keep=lambda r: r["key"].startswith(PLANT)))
        self.assertEqual({r["technology"] for r in plant}, {GAS[1]})
        self.assertEqual(len({r["key"] for r in plant}), 12)
        self.assertEqual((min(r["month"] for r in plant), max(r["month"] for r in plant)), ("2016-06", "2018-07"))
        op = [r for r in plant if r["now"] == "Operating"]
        self.assertEqual({r["key"] for r in op}, {PLANT + "BCGT%d" % i for i in range(1, 7)})
        self.assertEqual(({r["month"] for r in op}, len(op)), ({"2018-07"}, 6))
        self.assertEqual(len(self.per(EARLY, keep=lambda r: r["technology"] == GAS[1])), 265)
        self.assertIn("Plant 60264 has 102 of the 265 combustion-turbine generator-months of 2016-2019, from 12 "
                      "generators that were planned for the next month again and again from June 2016 to July 2018. "
                      "Only 6 of the 102 were listed as operating in the planned month: generators BCGT1 to BCGT6, "
                      "in July 2018.", self.doc)
        without = [self.per(p, "gas", lambda r: not r["key"].startswith(PLANT)) for p in (EARLY, LATE)]
        self.assertIn("Without plant 60264, gas's share is %s in 2016-2019 and %s in 2022-2025: flat." % (
            cell(without[0]), cell(without[1])), self.doc)
        self.assertEqual((cell(without[0]), cell(without[1])), ("0.456 (292 of 641)", "0.455 (191 of 420)"))

    def test_years(self):
        ys = ["%d" % y for y in range(2015, 2027)]
        for y in ys:
            self.assertIn("| %s | %s | %s | %s |" % (y, cell(self.year(y, "solar")), cell(self.year(y, "batteries")),
                                                    cell(self.year(y, "gas"))), self.doc)
        for r in self.years:
            self.assertEqual(frac(self.year(r["year"], r["group"]))[::-1], (int(r["cohort"]), int(r["operating"])))
        solar = {y: share(self.year(y, "solar")) for y in ys}
        self.assertLess(max(solar[y] for y in ys[6:]), min(solar[y] for y in ys[:6]))
        self.assertEqual(min(solar, key=solar.get), "2026")
        batt = {y: share(self.year(y, "batteries")) for y in ys}
        gas = {y: share(self.year(y, "gas")) for y in ys}
        self.assertEqual(sorted(batt, key=batt.get)[:2], ["2022", "2023"])
        self.assertEqual(sorted(gas, key=gas.get)[-2:], ["2026", "2025"])
        for s in ("Solar's share in every year from 2021 to 2026 is below its share in every year from 2015 to 2020.",
                  "January to September 2026 is solar's lowest year in the series.",
                  "Batteries were lowest in 2022 and 2023.", "Gas's two highest years are 2025 and 2026"):
            self.assertIn(s, self.doc)

    def test_prior_art(self):
        self.assertIn("id=62003", self.plan)
        self.assertNotIn("66604", self.plan)
        for s in ("https://www.eia.gov/todayinenergy/detail.php?id=66604", "a later EIA article that the plan did not "
                  "cite", "These delays are typically only for a month or two.",
                  "[`docs/nexttechonce-plan.md`](nexttechonce-plan.md)"):
            self.assertIn(s, self.doc)
        self.assertIn("Status: pre-registered, not yet scored.", read("docs", "nexttechonce-plan.md"))


if __name__ == "__main__":
    unittest.main()
