"""Checks docs/history-revert-preregistration.md against the predictions fixed before it
(docs/history-revert-predictions.md), the code it pre-registers (tools/annual-flows-candidate/
history.py, test_history.py, layouts.py) and job layouts-v1's raw output
(docs/layouts-v1-output.md).
MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = ("tools", "annual-flows-candidate")
ID = "Pre-registration id: history-revert-29 (22 October 2026)."


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8") as fh:
        return fh.read()


def const(src, name):
    return re.search(r"^%s = (.+?)\s*(#.*)?$" % name, src, re.M).group(1)


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


class HistoryPreregDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = read("docs", "history-revert-preregistration.md")
        cls.pred = read("docs", "history-revert-predictions.md")
        cls.out = read("docs", "layouts-v1-output.md")
        cls.src = read(*TOOLS, "history.py")
        cls.tests = read(*TOOLS, "test_history.py")
        cls.ly = read(*TOOLS, "layouts.py")
        a, b = re.match(r"tuple\(range\((\d+), (\d+)\)\)", const(cls.src, "SCORED")).groups()
        cls.first, cls.last = int(a), int(b) - 1
        cls.p4 = [int(x) for x in re.findall(r"\d{4}", const(cls.src, "P4_YEARS"))]

    def test_id_near_top(self):
        self.assertIn(ID, self.text.splitlines()[2])

    def test_bars_match_the_code_and_the_fixed_predictions(self):
        f, l = self.first, self.last
        p1 = int(const(self.src, "P1_MIN"))
        cov, prec = float(const(self.src, "COVERAGE")), float(const(self.src, "PRECISION"))
        ycov, keys = float(const(self.src, "YEAR_COVERAGE")), float(const(self.src, "KEYS_MIN"))
        units = int(const(self.src, "MIN_UNITS"))
        both = ["at least %d hit generator-months in each calendar year %d to %d" % (p1, f, l),
                "per month in %d is greater than in %d" % (self.p4[1], self.p4[0]),
                "at least %.2f in each calendar year %d to %d" % (ycov, f, l),
                "at least %.2f of the workbook's generator-months have a PUDL record in force" % keys,
                "at least %d disagreeing generator-months and at least %d simulated stale" % (units, units)]
        for s in both:
            self.assertIn(s, self.pred.replace("At least", "at least"), s)
            self.assertIn(s, self.text.replace("At least", "at least"), s)
        self.assertIn("at least %.2f of the generator-months where the workbook and PUDL disagree "
                      "are hits" % cov, self.pred)
        self.assertIn("at least %.2f of disagreeing generator-months are hits" % cov, self.text)
        self.assertIn("at least %.2f of the generator-months where the simulation keeps a stale "
                      "value are hits" % prec, self.pred)
        self.assertIn("at least %.2f of simulated stale generator-months are hits" % prec, self.text)
        self.assertIn("latest report is %s or later" % const(self.src, "LAST").strip('"'), self.text)

    def test_version_tests_gate(self):
        self.assertIn("`tools/annual-flows-candidate/history.py` %s (written" %
                      const(self.src, "__version__").strip('"'), self.text)
        n = len(re.findall(r"^    def test_", self.tests, re.M))
        self.assertIn("with %d unit tests" % n, self.text)
        minutes = re.search(r'"--minutes", type=float, default=([0-9.]+)', self.src).group(1)
        self.assertIn("for at most %d minutes" % int(float(minutes)), self.text)
        self.assertIn('FILES = ("history.py", "test_history.py")', self.src)
        self.assertEqual(const(self.src, "PREREG").strip('"'), "docs/history-revert-preregistration.md")
        md5 = re.findall(r'^    (\d{4}): "[0-9a-f]{32}",', self.ly, re.M)
        self.assertIn("All %d zips match a listed md5. Every year %s to %s has workbooks" % (
            len(md5), md5[0], md5[-1]), self.text)
        self.assertIn("In each calendar year read (%s to %s)" % (md5[0], md5[-1]), self.text)

    def test_layouts_output(self):
        rows = [cells(l) for l in self.out.splitlines() if re.match(r"^\| \d{4}-\d{2} \| ", l)]
        found = re.search(r"Readable: (\d+) of (\d+) workbooks found \((\S+) to (\S+),", self.out)
        self.assertEqual(found.group(1), found.group(2))
        self.assertEqual(len(rows), int(found.group(2)))
        self.assertTrue(all(r[6] == "True" for r in rows))
        self.assertEqual({r[4] for r in rows}, {"1"})
        self.assertIn("Every month has one duplicate key", self.text)
        self.assertIn("All %s monthly workbooks, %s to %s, are readable" % found.group(2, 3, 4), self.text)
        summer = [cells(l) for l in self.out.splitlines()
                  if l.startswith("| ") and "| Net Summer Capacity (MW) |" in l]
        self.assertEqual(len({(r[6], r[7], r[8]) for r in summer}), 1)
        m, a, b = summer[0][6:9]
        self.assertIn("Net Summer Capacity in the %s months %s to %s" % (m, a, b), self.text)
        self.assertIn("In the %s months %s to %s, the sheets have no such column" % (m, a, b), self.text)
        self.assertIn("in those months MW is missing on both sides", self.text)
        hdr = [cells(l) for l in self.out.splitlines()
               if re.match(r"^\| (operating|planned|retired) \| 2 \| ", l)]
        self.assertIn("From %s the header row index moves from 1 to 2" % min(r[7] for r in hdr), self.text)
        pr = [cells(l) for l in self.out.splitlines() if l.startswith("| Operating, ") and "_PR" in l]
        self.assertIn("The Puerto Rico sheets start in %s" % min(r[2] for r in pr), self.text)


if __name__ == "__main__":
    unittest.main()
