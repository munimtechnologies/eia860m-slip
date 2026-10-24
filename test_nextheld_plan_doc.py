"""Doc test: what docs/nextheld-plan.md says was known is recomputed from data/monthcheck_months_2026-09.csv,
data/nexttech_cohort.csv and docs/monthrun-practice-v1-output.md, and its bars match
tools/annual-flows-candidate/nextheld.py.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import collections
import csv
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EARLY, LATE = ("2016-01", "2019-12"), ("2022-01", "2025-12")


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8") as fh:
        return fh.read()


def mi(month):
    return int(month[:4]) * 12 + int(month[5:7]) - 1


class NextheldPlanDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = read("docs", "nextheld-plan.md")
        cls.code = read("tools", "annual-flows-candidate", "nextheld.py")
        with open(os.path.join(HERE, "data", "monthcheck_months_2026-09.csv"), newline="", encoding="utf-8") as fh:
            cls.months = {r["month"]: r for r in csv.DictReader(fh)}

    def test_status(self):
        self.assertIn("Status: pre-registered, not yet scored.", self.plan)
        for s in ("**C1.**", "**H1.**", "**H2.**", "**H3.**", "at least 30 rows", "at commit ea63c15"):
            self.assertIn(s, self.plan)

    def test_known_months(self):
        held = ["2026-0%d" % i for i in range(1, 9)]
        got = {m: (int(self.months[m]["cohort_operating"]), int(self.months[m]["cohort"])) for m in held}
        self.assertIn('KNOWN_MONTHS = {"2026-01": ', self.code)
        for m in held:
            self.assertEqual(self.code.count('"%s": (' % m), 1)
            self.assertIn('"%s": (%d, %d)' % (m, got[m][0], got[m][1]), self.code)
        op, n = sum(v[0] for v in got.values()), sum(v[1] for v in got.values())
        self.assertEqual((op, n), (366, 1194))
        self.assertEqual("%.3f" % (op / n), "0.307")
        self.assertIn("January to August 2026 have 1,194 generator-months in their next-month groups, 366 of them on "
                      "time (0.307)", self.plan)
        self.assertIn("(366 of 1,194 in all)", self.plan)
        self.assertIn('HELD = ("2026-01", "2026-08")', self.code)

    def test_september_left_out(self):
        out = read("docs", "monthrun-practice-v1-output.md")
        self.assertIn("| all | first | 61 | 26 | 0.4262 |", out)
        self.assertIn("| all | repeat | 109 | 31 | 0.2844 |", out)
        self.assertIn("26 of 61 first listings on time, 0.4262, and 31 of 109 repeat listings, 0.2844", self.plan)

    def test_thirty_sixth(self):
        with open(os.path.join(HERE, "data", "nexttech_cohort.csv"), newline="", encoding="utf-8") as fh:
            co = list(csv.DictReader(fh))
        count, last, cells = collections.Counter(), {}, collections.defaultdict(lambda: [0, 0])
        for r in sorted(co, key=lambda r: (r["month"], r["key"])):
            k = r["key"]
            gap = None if k not in last else mi(r["month"]) - mi(last[k])
            name = "0" if count[k] == 0 else ("1 month" if gap == 1 else "2-3 months" if gap in (2, 3) else None)
            three = count[k] >= 3
            count[k] += 1
            last[k] = r["month"]
            for p in (EARLY, LATE):
                if p[0] <= r["month"] <= p[1]:
                    for c in [name] + (["3+"] if three else []):
                        if c is not None:
                            cells[p, c][0] += r["now"] == "Operating"
                            cells[p, c][1] += 1
        sh = lambda p, c: cells[p, c][0] / cells[p, c][1]
        self.assertEqual({c: tuple(cells[LATE, c]) for c in ("0", "3+", "1 month", "2-3 months")},
                         {"0": (866, 2393), "3+": (428, 1398), "1 month": (878, 2254), "2-3 months": (231, 890)})
        self.assertIn("no earlier listing 0.362 (866 of 2,393), 3 or more 0.306 (428 of 1,398); repeat listings 1 "
                      "month after the last one 0.390 (878 of 2,254), 2-3 months after 0.260 (231 of 890).", self.plan)
        self.assertIn("In 2016-2019 the same comparisons were %.3f against %.3f, and %.3f against %.3f." % (
            sh(EARLY, "0"), sh(EARLY, "3+"), sh(EARLY, "1 month"), sh(EARLY, "2-3 months")), self.plan)
        self.assertEqual("%.3f" % (sh(LATE, "0") - sh(LATE, "3+")), "0.056")
        self.assertEqual("%.3f" % (sh(EARLY, "1 month") - sh(EARLY, "2-3 months")), "0.007")
        self.assertEqual("%.3f" % (sh(LATE, "1 month") - sh(LATE, "0")), "0.028")
        for s in ("In 2022-2025 the gap was 0.056", "when the two were 0.007 apart",
                  "one-month slips led first listings by only 0.028"):
            self.assertIn(s, self.plan)

    def test_code_matches_plan(self):
        for s in ('PLAN_URL = nc.BASE + "docs/nextheld-plan.md"', 'gap_cell(a, "1 month"), gap_cell(a, "2-3 months")',
                  'lambda: s(b["3+"]) < s(b["0"])', "lambda: s(one) > s(two)", 'lambda: s(one) > s(b["0"])',
                  "import nextcount as nc", '__version__ = "0.1.0"'):
            self.assertIn(s, self.code)
        nextcount = read("tools", "annual-flows-candidate", "nextcount.py")
        for s in ("MIN_COHORT = 30", 'GAPS = ((1, 1, "1 month"), (2, 3, "2-3 months")', '__version__ = "0.1.0"'):
            self.assertIn(s, nextcount)


if __name__ == "__main__":
    unittest.main()
