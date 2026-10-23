"""Doc test: the numbers in docs/nextmonth-share.md, docs/dec2026-plan.md and the README's paragraph
about them match the raw output of job monthcheck-dry-v1 (data/monthcheck_months_2026-08.csv and
docs/monthcheck-dry-v1-output.md).

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import csv
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))

# year: (months, cohort, listed as Operating in the planned month), as the note's table states them
YEARS = {
    2015: (5, 347, 187),
    2016: (12, 951, 457),
    2017: (12, 1171, 557),
    2018: (12, 1066, 527),
    2019: (12, 1035, 439),
    2020: (12, 1260, 540),
    2021: (12, 1566, 586),
    2022: (12, 1326, 428),
    2023: (12, 1510, 490),
    2024: (12, 1625, 592),
    2025: (12, 1586, 600),
    2026: (8, 1194, 366),
}


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8") as fh:
        return fh.read()


def load_months():
    """(month, cohort, to Operating, share column) for every month with a non-empty cohort."""
    with open(os.path.join(HERE, "data", "monthcheck_months_2026-08.csv"), newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    out = []
    for r in rows:
        n = int(r["cohort"])
        if n > 0:
            out.append((r["month"], n, int(r["cohort_operating"]), float(r["share_operating"])))
    return out


def pooled(rows):
    return sum(r[2] for r in rows), sum(r[1] for r in rows)


def of_years(rows, first, last, december=True):
    return [r for r in rows if first <= int(r[0][:4]) <= last and (december or r[0][5:] != "12")]


def phrase(k, n):
    return "{:,} of {:,} ({:.3f})".format(k, n, k / n)


class NextMonthShareTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load_months()
        cls.doc = read("docs", "nextmonth-share.md")
        cls.plan = read("docs", "dec2026-plan.md")
        cls.readme = read("README.md")

    def test_scope(self):
        self.assertEqual(len(self.rows), 133)
        self.assertEqual(self.rows[0][0], "2015-08")
        self.assertEqual(self.rows[-1][0], "2026-08")
        self.assertIn("so the series has 133 months, August 2015 to August 2026", self.doc)

    def test_share_column(self):
        for month, n, k, share in self.rows:
            self.assertAlmostEqual(share, k / n, places=5, msg=month)

    def test_years(self):
        for year, (m, n, k) in YEARS.items():
            rs = of_years(self.rows, year, year)
            self.assertEqual((len(rs), sum(r[1] for r in rs), sum(r[2] for r in rs)), (m, n, k), year)
            self.assertIn("| %d | %d | %d | %d | %.3f |" % (year, m, n, k, k / n), self.doc)
        self.assertIn("Over all 133 months: %s." % phrase(*pooled(self.rows)), self.doc)

    def test_fall(self):
        share = {y: k / n for y, (m, n, k) in YEARS.items()}
        early = [share[y] for y in range(2016, 2021)]
        late = [share[y] for y in range(2021, 2027)]
        self.assertLess(max(late), min(early))
        self.assertEqual(min(early), share[2019])
        self.assertEqual(max(late), share[2025])
        self.assertIn("the lowest of 2016-2020 was %.3f (2019) and the highest of 2021-2026 was %.3f (2025)"
                      % (share[2019], share[2025]), self.doc)
        self.assertIn("In 2016-2019, %s generators" % phrase(*pooled(of_years(self.rows, 2016, 2019))), self.doc)
        self.assertIn("In 2022-2025 it was %s." % phrase(*pooled(of_years(self.rows, 2022, 2025))), self.doc)
        self.assertIn("Leaving out December, 2016-2019 gives %s and 2022-2025 gives %s."
                      % (phrase(*pooled(of_years(self.rows, 2016, 2019, december=False))),
                         phrase(*pooled(of_years(self.rows, 2022, 2025, december=False)))), self.doc)
        self.assertIn("from 951 in 2016 to 1,586 in 2025", self.doc)

    def test_december(self):
        for year in range(2016, 2026):
            rs = of_years(self.rows, year, year)
            dec = [r for r in rs if r[0][5:] == "12"]
            others = [r for r in rs if r[0][5:] != "12"]
            self.assertEqual((len(dec), len(others)), (1, 11), year)
            self.assertGreater(dec[0][1], max(r[1] for r in others), year)
            k, n = pooled(rs)
            self.assertGreater(dec[0][2] / dec[0][1], k / n, year)
        decs = [r for r in self.rows if r[0][5:] == "12"]
        rest = [r for r in self.rows if r[0][5:] != "12"]
        self.assertEqual((len(decs), len(rest)), (11, 122))
        self.assertIn("The 11 Decembers from 2015 to 2025 together: %s." % phrase(*pooled(decs)), self.doc)
        self.assertIn("The other 122 months: %s." % phrase(*pooled(rest)), self.doc)
        self.assertIn("In each of the ten years 2016 to 2025, December's cohort was the largest of its year", self.doc)

    def test_p4_band(self):
        window = [r for r in self.rows if "2024-09" <= r[0] <= "2026-08"]
        self.assertEqual(len(window), 24)
        ranked = sorted(window, key=lambda r: r[2] / r[1])
        lo, hi = ranked[1], ranked[-2]
        self.assertEqual((lo[0], hi[0]), ("2024-10", "2025-12"))
        self.assertIn("gives the band %.4f to %.4f. Those are October 2024 and December 2025."
                      % (lo[2] / lo[1], hi[2] / hi[1]), self.doc)

    def test_practice_output(self):
        out = read("docs", "monthcheck-dry-v1-output.md")
        self.assertIn("Mode: practice (the month was already in the archive).", out)
        self.assertIn("Held: 4 of 4 scored.", out)
        self.assertIn("| P4 | held | 0.3145 (39 of 124) | 0.2195 to 0.4740 (2024-08 to 2026-07) |", out)
        self.assertIn("on August 2026, a month already published: 4 of 4 held.", self.doc)

    def test_dec2026_plan(self):
        self.assertIn("Status: pre-registered, not yet scored.", self.plan)
        by_month = dict((r[0], r) for r in self.rows)
        dec22 = by_month["2022-12"]
        m, n, k = YEARS[2022]
        self.assertIn("In 2022 December's share was %.3f against the year's %.3f"
                      % (dec22[2] / dec22[1], k / n), self.plan)
        best_not_dec = [y for y in range(2016, 2026)
                        if max(of_years(self.rows, y, y), key=lambda r: r[2] / r[1])[0][5:] != "12"]
        self.assertEqual(best_not_dec, [2019, 2021, 2022])
        self.assertIn("In 2019, 2021 and 2022 a month other than December had the highest share", self.plan)
        top = max(of_years(self.rows, 2026, 2026), key=lambda r: r[1])
        self.assertEqual((top[0], top[1]), ("2026-06", 216))
        self.assertEqual(by_month["2025-12"][1], 192)
        self.assertIn("June 2026's 216, larger than December 2025's 192", self.plan)
        for s in ("**D1.** December 2026's next-month cohort is larger than the next-month cohort of every month "
                  "from January to November 2026.",
                  "**D2.** December 2026's share to Operating is above the pooled share to Operating of January "
                  "to November 2026"):
            self.assertIn(s, self.plan)

    def test_readme(self):
        early = phrase(*pooled(of_years(self.rows, 2016, 2019)))
        late = phrase(*pooled(of_years(self.rows, 2022, 2025)))
        self.assertIn("was %s in 2016-2019 and %s in 2022-2025" % (early[-6:-1], late[-6:-1]), self.readme)
        for name in ("nextmonth-share.md", "dec2026-plan.md", "sep2026-plan.md"):
            self.assertIn("(docs/%s)" % name, self.readme)


if __name__ == "__main__":
    unittest.main()
