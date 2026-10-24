"""Doc test: the numbers in docs/nexttechonce.md match the raw output of job nexttechonce-v1
(docs/nexttechonce-v1-output.md, docs/nexttechonce-v1-stdout.txt, docs/nexttechonce-v1-unittests.txt,
data/nexttechonce_first.csv), and every share, count and split in it is recomputed from
data/nexttech_cohort.csv.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import csv
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EARLY, LATE = ("2016-01", "2019-12"), ("2022-01", "2025-12")
GROUPS = ("solar", "batteries", "gas", "wind", "other")
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


def name(period):
    return "%s to %s" % period


class NexttechonceDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs", "nexttechonce.md")
        cls.plan = read("docs", "nexttechonce-plan.md")
        cls.out = read("docs", "nexttechonce-v1-output.md")
        cls.log = read("docs", "nexttechonce-v1-stdout.txt")
        cls.ut = read("docs", "nexttechonce-v1-unittests.txt")
        cls.co = rows("data", "nexttech_cohort.csv")
        cls.first = rows("data", "nexttechonce_first.csv")
        cls.firsts = {}
        for p in (EARLY, LATE):
            seen = {}
            for r in sorted((r for r in cls.co if p[0] <= r["month"] <= p[1]), key=lambda r: r["month"]):
                seen.setdefault(r["key"], r)
            cls.firsts[p] = list(seen.values())

    def gm(self, period, group=None):
        return [r for r in self.co if period[0] <= r["month"] <= period[1] and (group is None or r["group"] == group)]

    def once(self, period, group=None, keep=None):
        return [r for r in self.firsts[period] if (group is None or r["group"] == group) and (keep is None or keep(r))]

    def test_status(self):
        self.assertIn("Status: pre-registered, not yet scored.", self.plan)
        self.assertIn("Held: 3 of 4 scored (C0 is a check, not counted).", self.out)
        for s in ("| C0 | held |", "| O1 | held |", "| O2 | held |", "| O3 | failed |", "| O4 | held |"):
            self.assertIn(s, self.out)
        self.assertIn("3 of 4 predictions held, and the reproduction check C0 held. O3 failed: gas's share rose by "
                      "0.057, just outside the band of 0.05.", self.doc)
        for s in ("GAS_BAND = 0.05", "MIN_COHORT = 30"):
            self.assertIn(s, read("tools", "annual-flows-candidate", "nexttechonce.py"))

    def test_order(self):
        self.assertTrue(self.log.startswith("2026-10-24T00:19:12Z plan not served yet: HTTPError: HTTP Error 404"))
        self.assertIn("2026-10-24T00:29:12Z plan served: ", self.log)
        cohort = "cohort file 950816 bytes, md5 1681df9fdee9878ca2c359d1239c6467, 14807 rows"
        self.assertLess(self.log.index("plan served:"), self.log.index(cohort))
        self.assertIn("(950816 bytes, md5 1681df9fdee9878ca2c359d1239c6467; 14807 rows)", self.out)
        for s in ("committed at 00:22:03 UTC on 24 October 2026 (commit 470e60f)", "at 00:19:12 UTC, found no plan",
                  "at 00:29:12 UTC, was served the plan", "(950,816 bytes, md5 1681df9fdee9878ca2c359d1239c6467, "
                  "14,807 rows)", "after its 10 unit tests passed"):
            self.assertIn(s, self.doc)
        self.assertIn("Ran 10 tests", self.ut)
        self.assertIn("\nOK", self.ut)

    def test_first_file(self):
        self.assertEqual(len(self.co), 14807)
        self.assertEqual(len(self.first), 4711)
        mine = {(name(p), r["month"], r["key"], r["group"], r["now"]) for p in (EARLY, LATE) for r in self.firsts[p]}
        theirs = {(r["period"], r["month"], r["key"], r["group"], r["now"]) for r in self.first}
        self.assertEqual(mine, theirs)
        self.assertEqual((len(self.firsts[EARLY]), len(self.firsts[LATE])), (2179, 2532))
        self.assertIn("4,711 rows", self.doc)

    def test_c0(self):
        self.assertEqual((frac(self.gm(EARLY)), frac(self.gm(LATE))), ((1980, 4223), (2110, 6047)))
        self.assertIn("| held | 14,807 rows; 1,980 of 4,223 and 2,110 of 6,047 |", self.doc)

    def test_groups(self):
        for g in GROUPS + (None,):
            e, l = self.once(EARLY, g), self.once(LATE, g)
            per = ["%.2f" % (len(self.gm(p, g)) / len(self.once(p, g))) for p in (EARLY, LATE)]
            self.assertIn("| %s | %s | %s | %s | %s |" % (g or "all", cell(e), cell(l), per[0], per[1]), self.doc)
            for p, sel in ((EARLY, e), (LATE, l)):
                op, k = frac(sel)
                self.assertIn("| %s | %s | %d | %d |" % (name(p), g or "all", k, op), self.out)
        for g, outcome in (("solar", "held"), ("batteries", "held")):
            e, l = self.once(EARLY, g), self.once(LATE, g)
            self.assertEqual(share(l) < share(e), outcome == "held")
            self.assertIn("| %s | %s to %s |" % (outcome, cell(e), cell(l)), self.doc)
        e, l = self.once(EARLY, "gas"), self.once(LATE, "gas")
        self.assertGreaterEqual(abs(share(l) - share(e)), 0.05)
        self.assertEqual("%.3f" % (share(l) - share(e)), "0.057")
        self.assertIn("| failed | %s to %s |" % (cell(e), cell(l)), self.doc)
        self.assertIn("gas's share rose from 0.443 to 0.500, by 0.057", self.doc)

    def test_o4(self):
        e, l = self.firsts[EARLY], self.firsts[LATE]
        std = sum(len(self.once(EARLY, g)) / len(e) * share(self.once(LATE, g)) for g in GROUPS)
        within, total = share(e) - std, share(e) - share(l)
        self.assertTrue(within >= total / 2)
        self.assertTrue(0.69 < within / total < 0.70)
        self.assertEqual(("%.3f" % std, "%.3f" % within, "%.3f" % total), ("0.392", "0.070", "0.100"))
        self.assertIn("within 0.0697 of total 0.1003 (shares 0.4617 to 0.3614; standardized 0.3920)", self.out)
        for s in ("| held | 0.070 of 0.100 |", "fell from 0.462 to 0.361, by 0.100", "gives 0.392",
                  "would have fallen by 0.070. That is a little under 70% of the fall",
                  "`docs/nexttech.md` found 79%"):
            self.assertIn(s, self.doc)
        self.assertIn("That is 79% of the fall.", read("docs", "nexttech.md"))

        def mix(g):
            return tuple("%.1f%%" % (100 * len(self.once(p, g)) / len(self.firsts[p])) for p in (EARLY, LATE))
        self.assertIn("batteries were %s of the 2016-2019 generators and %s of the 2022-2025 ones" % mix("batteries"),
                      self.doc)
        self.assertIn("gas went from %s to %s, wind from %s to %s, other technologies from %s to %s, and solar from "
                      "%s to %s." % (mix("gas") + mix("wind") + mix("other") + mix("solar")), self.doc)

    def test_repeat(self):
        gm_fall = share(self.gm(EARLY)) - share(self.gm(LATE))
        once_fall = share(self.firsts[EARLY]) - share(self.firsts[LATE])
        self.assertEqual(("%.3f" % gm_fall, "%.3f" % once_fall), ("0.120", "0.100"))
        per = {p: len(self.gm(p)) / len(self.firsts[p]) for p in (EARLY, LATE)}
        self.assertEqual(("%.2f" % per[EARLY], "%.2f" % per[LATE]), ("1.94", "2.39"))

        def ratio(g):
            return tuple("%.2f" % (len(self.gm(p, g)) / len(self.once(p, g))) for p in (EARLY, LATE))
        self.assertEqual((ratio("batteries"), ratio("solar")), (("2.00", "2.77"), ("1.82", "2.36")))
        for s in ("Counted in generator-months the share fell by 0.120; counted once per generator it fell by 0.100.",
                  "in 2.39 monthly reports on average, against 1.94 in 2016-2019",
                  "Batteries went from 2.00 to 2.77 and solar from 1.82 to 2.36.",
                  "repeat listings rose from 1.94 to 2.39 per generator"):
            self.assertIn(s, self.doc)
        cells = []
        for p in (EARLY, LATE):
            (op_gm, k_gm), (op_1, k_1) = frac(self.gm(p)), frac(self.firsts[p])
            cells.append("%.3f (%s of %s)" % ((op_gm - op_1) / (k_gm - k_1), n(op_gm - op_1), n(k_gm - k_1)))
        self.assertEqual(cells, ["0.477 (974 of 2,044)", "0.340 (1,195 of 3,515)"])
        self.assertIn("were on time %s in 2016-2019 and %s in 2022-2025, against %.3f and %.3f for first listings." % (
            cells[0], cells[1], share(self.firsts[EARLY]), share(self.firsts[LATE])), self.doc)

    def test_gas_plant(self):
        plant = self.once(EARLY, keep=lambda r: r["key"].startswith(PLANT))
        self.assertEqual(len(plant), 12)
        self.assertEqual(self.once(LATE, keep=lambda r: r["key"].startswith(PLANT)), [])
        self.assertEqual({r["group"] for r in plant}, {"gas"})
        self.assertEqual([r for r in plant if r["now"] == "Operating"], [])
        months = {r["key"][len(PLANT):]: r["month"] for r in plant}
        self.assertEqual(months, dict([("CLGT%d" % i, "2016-06") for i in range(1, 7)] +
                                      [("BCGT%d" % i, "2017-01") for i in range(1, 7)]))
        self.assertEqual(len(self.once(EARLY, "gas")), 325)
        rest = self.once(EARLY, "gas", lambda r: not r["key"].startswith(PLANT))
        self.assertEqual(cell(rest), "0.460 (144 of 313)")
        rise = share(self.once(LATE, "gas")) - share(rest)
        self.assertLess(rise, 0.05)
        self.assertEqual("%.3f" % rise, "0.040")
        for s in ("Plant 60264's 12 combustion turbines are now 12 of the 325 gas generators of 2016-2019",
                  "June 2016 for CLGT1 to CLGT6, January 2017 for BCGT1 to BCGT6",
                  "gas's 2016-2019 share is 0.460 (144 of 313), and the rise is 0.040, inside the band",
                  "so O3 failed as scored"):
            self.assertIn(s, self.doc)
        self.assertIn("Gas's two highest years are 2025 and 2026", read("docs", "nexttech.md"))

    def test_prior_art(self):
        for s in ("https://www.eia.gov/todayinenergy/detail.php?id=66604", "8 May 2024 and of 10 November 2025",
                  "[`docs/nexttechonce-plan.md`](nexttechonce-plan.md)"):
            self.assertIn(s, self.doc)


if __name__ == "__main__":
    unittest.main()
