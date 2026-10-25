"""Doc test: every number in docs/plantw.md (fortieth result) is recomputed from
data/nexttech_cohort.csv, and the job's raw output (docs/plantw-v1-output.md), log and unit-test
log agree with the recomputation.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import csv
import hashlib
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
POOL, RECENT = ("2016-01", "2025-12"), ("2022-01", "2026-08")
PERIODS = (("2016-01", "2019-12"), ("2020-01", "2021-12"), ("2022-01", "2025-12"), ("2026-01", "2026-08"))
GAPS = ((1, 1, "1 month"), (2, 3, "2-3 months"), (4, 12, "4-12 months"), (13, None, "more than 12 months"))
CELLS = ("first",) + tuple(x[2] for x in GAPS)
TECHS = ("solar", "batteries", "gas", "wind")


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


def cell(rows):
    """-> (on time, rows, plants, mean of the plants' shares), as plantw.py 0.1.0 computes it."""
    by = {}
    for r in rows:
        p = by.setdefault(r["plant"], [0, 0])
        p[0] += 1 if r["ok"] else 0
        p[1] += 1
    return (sum(v[0] for v in by.values()), sum(v[1] for v in by.values()), len(by),
            sum(v[0] / v[1] for v in by.values()) / len(by))


class PlantwDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs", "plantw.md")
        cls.out = read("docs", "plantw-v1-output.md")
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

    def c(self, period, group, name):
        return cell([r for r in self.rows if period[0] <= r["month"] <= period[1]
                     and (group is None or r["group"] == group) and r["cell"] == name])

    def test_c0(self):
        self.assertEqual((self.n_rows, self.md5), (14807, "1681df9fdee9878ca2c359d1239c6467"))
        self.assertEqual((self.c(POOL, "solar", "first")[:2], self.c(POOL, "solar", "1 month")[:2]),
                         ((1474, 3568), (1230, 2657)))
        self.assertIn("| held | 14,807 rows, md5 1681df9fdee9878ca2c359d1239c6467; solar first listings 1,474 of 3,568, "
                      "1 month after the last listing 1,230 of 2,657 |", self.doc)
        self.assertIn("| C0 | held | 14807 rows, md5 1681df9fdee9878ca2c359d1239c6467; 2016-2025: solar first 1474 of "
                      "3568; solar 1 month 1230 of 2657 |", self.out)

    def test_bars(self):
        bars = (("P1", POOL, "solar", "1 month", "first", 1), ("P2", POOL, "batteries", "1 month", "first", 1),
                ("P3", POOL, "wind", "1 month", "first", -1), ("P4", POOL, "gas", "1 month", "first", -1),
                ("P5", RECENT, "solar", "1 month", "2-3 months", 1))
        outcomes = []
        for pid, period, g, x, y, way in bars:
            a, b = self.c(period, g, x), self.c(period, g, y)
            self.assertGreaterEqual(min(a[2], b[2]), 30)
            o = "held" if way * (a[3] - b[3]) > 0 else "failed"
            outcomes.append(o)
            self.assertIn("| %s | %.3f over %s plants against %.3f over %s plants |" % (
                o, a[3], n(a[2]), b[3], n(b[2])), self.doc)
            self.assertIn("| %s | %s | %s: %.4f over %d plants (generator-months %d of %d); %s: %.4f over %d plants "
                          "(generator-months %d of %d) |" % (pid, o, x, a[3], a[2], a[0], a[1], y, b[3], b[2], b[0],
                                                             b[1]), self.out)
        self.assertEqual(outcomes, ["held", "held", "failed", "failed", "held"])
        self.assertIn("Held: 3 of 5 scored", self.out)
        self.assertIn("3 of 5 predictions held, and the reproduction check C0 held. P3 and P4 failed.", self.doc)
        self.assertIn("Every compared cell has at least 30 plants, so all five were scored.", self.doc)

    def test_lift(self):
        for g in TECHS + (None,):
            f, m = self.c(POOL, g, "first"), self.c(POOL, g, "1 month")
            self.assertIn("| %s | %.3f | %.3f | %.3f | %.3f |" % (
                g or "all technologies", f[0] / f[1], f[3], m[0] / m[1], m[3]), self.doc)
        first = [abs(self.c(POOL, g, "first")[3] - self.c(POOL, g, "first")[0] / self.c(POOL, g, "first")[1])
                 for g in TECHS]
        month = [self.c(POOL, g, "1 month")[3] - self.c(POOL, g, "1 month")[0] / self.c(POOL, g, "1 month")[1]
                 for g in TECHS]
        self.assertEqual(("%.3f" % max(first), "%.3f" % min(month), "%.3f" % max(month)), ("0.029", "0.155", "0.254"))
        self.assertIn("Weighting each plant once moves first listings by at most 0.029 in any of the four technologies, "
                      "and lifts the one-month cell by 0.155 to 0.254 in every one of them.", self.doc)
        for p in PERIODS:
            f, m = self.c(p, None, "first"), self.c(p, None, "1 month")
            self.assertGreater(m[3] - m[0] / m[1], max(0, f[3] - f[0] / f[1]))
        self.assertIn("For all technologies together the one-month cell is lifted more than first listings in each of "
                      "2016-2019, 2020-2021, 2022-2025 and January to August 2026.", self.doc)

    def test_out_rows(self):
        for period, groups, cells in ((POOL, (None,) + TECHS, CELLS), (RECENT, ("solar",), ("1 month", "2-3 months")),
                                      (PERIODS[0], (None,), ("first", "1 month")),
                                      (PERIODS[1], (None,), ("first", "1 month")),
                                      (PERIODS[2], (None,), ("first", "1 month")),
                                      (PERIODS[3], (None,), ("first", "1 month"))):
            for g in groups:
                for name in cells:
                    on, rows, plants, pw = self.c(period, g, name)
                    self.assertIn("| %s to %s | %s | %s | %d | %d | %.4f | %d | %.4f |" % (
                        period[0], period[1], g or "all", name, rows, on, on / rows, plants, pw), self.out)

    def test_order_of_events(self):
        log = read("docs", "plantw-v1-stdout.txt").splitlines()
        self.assertEqual(log[0], "2026-10-25T05:22:50Z plan served: "
                                 "https://raw.githubusercontent.com/munimtechnologies/eia860m-slip/main/docs/plantw-plan.md")
        self.assertEqual(log[1], "cohort file 950816 bytes, md5 1681df9fdee9878ca2c359d1239c6467, 14807 rows")
        self.assertFalse(any("plan not served yet" in x for x in log))
        self.assertLess("2026-10-25T03:35:47Z", log[0][:20])
        self.assertIn("The plan was committed at 03:35:47 UTC on 25 October 2026 (commit c3520c3).", self.doc)
        self.assertIn("The job's first poll of the plan's address, at 05:22:50 UTC, was served the plan.", self.doc)
        self.assertIn("(950,816 bytes, md5 1681df9fdee9878ca2c359d1239c6467, 14,807 rows)", self.doc)
        self.assertIn("ea63c150a8ed41cc1fcad901ccab51686c924d46/data/nexttech_cohort.csv", self.out)
        unit = read("docs", "plantw-v1-unittests.txt")
        self.assertIn("Ran 11 tests", unit)
        self.assertTrue(unit.rstrip().endswith("OK"))
        self.assertIn("after its 11 unit tests passed", self.doc)
        self.assertIn("Status: pre-registered, not yet scored.", read("docs", "plantw-plan.md"))
        code = read("tools", "annual-flows-candidate", "plantw.py")
        self.assertIn('__version__ = "0.1.0"', code)
        self.assertIn("pw = sum(v[0] / v[1] for v in by.values()) / len(by) if by else None", code)

    def test_readme(self):
        self.assertIn("| 40 | Weighting each plant once, every technology's one-month cell is above its first listings, "
                      "because that weighting lifts repeat-listing cells (3 of 5 held) | [`plantw.md`](docs/plantw.md) |",
                      self.readme)
        self.assertIn("(fortieth result, scored against [`docs/plantw-plan.md`](docs/plantw-plan.md); 3 of 5 held)",
                      self.readme)
        for s in ("**Weighting each plant once lifts every repeat-listing cell, so it cannot settle the wind and gas "
                  "reversals.**", "solar's one-month cell was 0.624 against 0.417 for first listings and batteries' "
                  "0.519 against 0.279", "wind's (0.665 against 0.495) and gas's (0.586 against 0.425)",
                  "lifts the one-month cell by 0.155 to 0.254 in every technology and first listings by at most 0.029"):
            self.assertIn(s, self.readme)


if __name__ == "__main__":
    unittest.main()
