"""Checks every number in docs/nextlist-plan.md (the October 2026 next-month list pre-registration)
against the raw output of compete job nextlist-v1 (data/nextlist_v1.json, data/nextlist_2026-10.csv,
data/nextlist_2026-09.csv, data/nextlist_backtest_months.csv, docs/nextlist-2026-10.md,
docs/nextlist-v1-unittests.txt, docs/nextlist-v1-md5.txt) and the published nextlist.py.
MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import collections
import csv
import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
UNIT_TESTS = 16
TARGET, PRACTICE = "2026-10", "2026-09"


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8") as fh:
        return fh.read()


def rows(*parts):
    with open(os.path.join(HERE, *parts), newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def mw(x):
    return "{:,.1f}".format(x)


class NextlistPlanDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = read("docs", "nextlist-plan.md")
        cls.res = json.loads(read("data", "nextlist_v1.json"))
        cls.list = rows("data", "nextlist_2026-10.csv")
        cls.practice = rows("data", "nextlist_2026-09.csv")
        cls.months = rows("data", "nextlist_backtest_months.csv")
        cls.out = read("docs", "nextlist-2026-10.md")
        cls.log = read("docs", "nextlist-v1-unittests.txt")
        cls.md5s = dict(line.split() for line in read("docs", "nextlist-v1-md5.txt").splitlines() if line.strip())
        cls.code = read("tools", "annual-flows-candidate", "nextlist.py")

    def test_status(self):
        self.assertIn("Status: pre-registered, not yet scored. Fixed before EIA publishes its October 2026 "
                      "EIA-860M workbook (expected 24 November 2026).", self.text)

    def test_unit_tests(self):
        ran = int(re.search(r"Ran (\d+) tests", self.log).group(1))
        self.assertEqual(ran, UNIT_TESTS)
        self.assertEqual(len(re.findall(r" \.\.\. ok$", self.log, re.M)), ran)
        self.assertTrue(self.log.rstrip().endswith("OK"))
        self.assertIn("passed %d of %d unit tests" % (ran, ran), self.text)

    def test_code(self):
        version = re.search(r'^__version__ = "([^"]+)"', self.code, re.M).group(1)
        self.assertEqual(version, self.res["version"])
        self.assertIn("nextlist.py %s;" % version, self.text)
        self.assertIn("(version %s, md5 %s)" % (version, self.md5s["nextlist.py"]), self.text)
        self.assertIn("WINDOW = %d " % self.res["window"], self.code)
        self.assertIn("MIN_ROWS = %d " % self.res["min_rows"], self.code)
        self.assertIn("over the %d group months before October 2026" % self.res["window"], self.text)
        self.assertIn("fewer than %d generator-months" % self.res["min_rows"], self.text)

    def test_inputs(self):
        wb = {w["month"]: w for w in self.res["workbooks"]}
        self.assertTrue(wb[PRACTICE]["same_as_expected"])
        self.assertIn("September workbook (md5 %s)" % wb[PRACTICE]["md5"], self.text)
        self.assertTrue(self.res["cohort"]["same"])
        self.assertIn("/ea63c15", self.res["cohort"]["source"])
        self.assertIn("the same cohort file (commit ea63c15)", self.text)

    def test_list(self):
        t = self.res["target"]
        self.assertEqual(t["month"], TARGET)
        s = t["summary"]
        self.assertEqual(len(self.list), s["rows"])
        self.assertEqual(len(set(r["key"] for r in self.list)), s["rows"])
        self.assertEqual(len(set(r["key"].split("/")[0] for r in self.list)), s["plants"])
        self.assertEqual({r["key"]: float(r["p"]) for r in self.list}, {r["key"]: r["p"] for r in t["rows"]})
        self.assertIn("lists the %d generators at %d plants (%s MW)" % (s["rows"], s["plants"], mw(s["mw"])),
                      self.text)
        g = collections.Counter(r["group"] for r in self.list)
        self.assertEqual(sum(g.values()), s["rows"])
        self.assertIn("%d solar, %d batteries, %d gas, %d wind and %d other." % (
            g["solar"], g["batteries"], g["gas"], g["wind"], g["other"]), self.text)
        cells = {(c["group"], c["cell"]): c for c in t["cells"]}
        a, b = cells[("solar", "1 month")], cells[("solar", "first")]
        self.assertIn("p is %.4f for the %d solar generators planned for next month again one month after their "
                      "last listing, and %.4f for the %d solar generators listed for the first time" % (
                          a["p"], a["generators"], b["p"], b["generators"]), self.text)
        self.assertIn("## The list: %s (from EIA's %s workbook)" % (TARGET, PRACTICE), self.out)
        self.assertIn("%d generators at %d plants, %.1f MW." % (s["rows"], s["plants"], s["mw"]), self.out)
        self.assertIn("p expects %.1f of the %d generators on time (%s of %s MW)" % (
            s["expected"], s["rows"], mw(s["mw_expected"]), mw(s["mw"])), self.text)
        self.assertIn("the %d generators sit at only %d plants" % (s["rows"], s["plants"]), self.text)

    def test_backtest_pooled(self):
        bt = self.res["backtest"]
        self.assertEqual((bt["from"], bt["to"]), ("2020-01", PRACTICE))
        self.assertIn("every month from January 2020 to September 2026", self.text)
        p = bt["pooled"]
        self.assertEqual(sum(int(m["rows"]) for m in self.months), p["rows"])
        self.assertIn("{:,} generator-months at {:,} plants".format(p["rows"], p["plants"]), self.text)
        self.assertIn("p's Brier score was %.4f, r0's %.4f and r1's %.4f" % (
            p["brier_p"], p["brier_r0"], p["brier_r1"]), self.text)
        i0, i1 = bt["interval_minus_r0"], bt["interval_minus_r1"]
        self.assertIn("p minus r0 was %+.4f (95%% interval %+.4f to %+.4f) and p minus r1 %+.4f (%+.4f to %+.4f)" % (
            p["m_minus_r0"], i0[0], i0[1], p["m_minus_r1"], i1[0], i1[1]), self.text)
        self.assertTrue(i0[0] < 0 < i0[1] and i1[0] < 0 < i1[1])
        self.assertIn("Both intervals include zero", self.text)
        self.assertIn("{:,} generator-months were on time against {:,.1f} expected".format(
            p["on_time"], p["expected"]), self.text)
        self.assertLess(p["on_time"], p["expected"])
        top = [c for c in bt["calibration"] if c["p_from"] == 0.5][0]
        self.assertIn("(p from 0.5 to 0.6; {:,} generator-months, mean p {:.4f}) the on-time share was {:.4f}".format(
            top["rows"], top["mean_p"], top["on_time"]), self.text)

    def test_backtest_months(self):
        ms = [(m["month"], float(m["brier_p"]), float(m["brier_r0"]), float(m["brier_r1"])) for m in self.months]
        self.assertEqual(len(ms), 81)
        self.assertEqual((ms[0][0], ms[-1][0]), ("2020-01", PRACTICE))
        n0 = sum(1 for m in ms if m[1] < m[2])
        n1 = sum(1 for m in ms if m[1] < m[3])
        bt = self.res["backtest"]
        self.assertEqual((n0, n1), (bt["months_below_r0"], bt["months_below_r1"]))
        self.assertIn("below r0's in %d of %d months and below r1's in %d of %d" % (n0, len(ms), n1, len(ms)),
                      self.text)
        self.assertIn("about %d%% and %d%%." % (round(100.0 * n0 / len(ms)), round(100.0 * n1 / len(ms))), self.text)
        octs = [m for m in ms if m[0].endswith("-10")]
        self.assertEqual([m[0][:4] for m in octs], ["2020", "2021", "2022", "2023", "2024", "2025"])
        self.assertIn("the counts were %d of %d and %d of %d;" % (
            sum(1 for m in octs if m[1] < m[2]), len(octs), sum(1 for m in octs if m[1] < m[3]), len(octs)), self.text)
        last = ms[-12:]
        self.assertEqual(last[0][0], "2025-10")
        self.assertIn("(October 2025 to September 2026), %d of 12 and %d of 12." % (
            sum(1 for m in last if m[1] < m[2]), sum(1 for m in last if m[1] < m[3])), self.text)

    def test_practice(self):
        self.assertTrue(self.res["c1"]["held"])
        self.assertEqual(self.res["c1"]["month"], PRACTICE)
        self.assertEqual(len(self.practice), self.res["c1"]["list_rows"])
        self.assertIn("(C1 held)", self.text)
        pb = self.res["practice_vs_backtest"]
        self.assertTrue(pb["held"])
        sc = self.res["practice"]["score"]
        self.assertIn("(C2 held; p %.4f, r0 %.4f, r1 %.4f)" % (sc["brier_p"], sc["brier_r0"], sc["brier_r1"]),
                      self.text)


if __name__ == "__main__":
    unittest.main()
