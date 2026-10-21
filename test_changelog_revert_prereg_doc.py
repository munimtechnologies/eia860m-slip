"""Checks docs/changelog-revert-preregistration.md against the code it pre-registers
(tools/annual-flows-candidate/revert.py, test_revert.py, keyhist.py) and against job
keyhist-v1's raw output (data/keyhist_v1.json).
MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import calendar
import json
import os
import re
import unittest

from test_workbook_route_followup_doc import kind

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = ("tools", "annual-flows-candidate")
ID = "Pre-registration id: changelog-revert-28 (21 October 2026)."


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8") as fh:
        return fh.read()


def const(src, name):
    return re.search(r"^%s = (.+?)\s*(#.*)?$" % name, src, re.M).group(1)


def month_name(m):
    return "%s %s" % (calendar.month_name[int(m[5:])], m[:4])


class PreregDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = read("docs", "changelog-revert-preregistration.md")
        cls.src = read(*TOOLS, "revert.py")
        cls.tests = read(*TOOLS, "test_revert.py")
        cls.kh = read(*TOOLS, "keyhist.py")
        cls.raw = json.loads(read("data", "keyhist_v1.json"))

    def test_id_near_top(self):
        self.assertIn(ID, self.text.splitlines()[2])

    def test_bars_match_the_code(self):
        self.assertIn("**P2.** At least %.2f of D" % float(const(self.src, "COVERAGE")), self.text)
        self.assertIn("**P3.** At least %.2f of S" % float(const(self.src, "PRECISION")), self.text)
        self.assertIn("D and S each hold at least %d generator-months" % int(const(self.src, "MIN_UNITS")),
                      self.text)
        self.assertIn("MW (to %.2f MW)" % float(const(self.src, "MW_TOL")), self.text)
        self.assertIn('DATE_COLS = ("report_date", "valid_until_date", "report_date_max")', self.src)

    def test_named_generators(self):
        named = re.findall(r'\("(\d+/\w+)", "(\d{4}-\d{2})"\)', const(self.src, "NAMED"))
        self.assertEqual(len(named), 2)
        (k1, m1), (k2, m2) = named
        self.assertIn("%s's %s workbook row and %s's %s workbook row" % (
            k1, month_name(m1), k2, month_name(m2)), self.text)
        for k in (k1, k2):
            h = next(h for h in self.raw["keys"] if h["key"] == k)
            self.assertEqual(kind(h), "new", k)

    def test_months_version_tests_md5(self):
        self.assertIn('MONTHS = tuple("2026-%02d" % k for k in range(1, 9))', self.src)
        self.assertIn("all eight months 2026-01 to 2026-08 are read", self.text)
        self.assertIn("`tools/annual-flows-candidate/revert.py` %s," % const(self.src, "__version__").strip('"'),
                      self.text)
        n = len(re.findall(r"^    def test_", self.tests, re.M))
        self.assertIn("with %d unit tests" % n, self.text)
        md5 = const(self.kh, "ZIP_MD5").strip('"')
        self.assertEqual(self.text.count("md5 %s" % md5), 2)
        minutes = re.search(r'"--minutes", type=float, default=([0-9.]+)', self.src).group(1)
        self.assertIn("for at most %d minutes" % int(float(minutes)), self.text)

    def test_followup_numbers(self):
        diffs = sum(1 for h in self.raw["keys"] for r in h["months"] if not r["same"])
        back = sum(1 for h in self.raw["keys"] if kind(h) == "back")
        self.assertIn("found %d generators on which" % len(self.raw["keys"]), self.text)
        self.assertIn("in each of the %d generator-months where they disagree" % diffs, self.text)
        self.assertIn("In %d of the %d the workbook had gone back" % (back, len(self.raw["keys"])),
                      self.text)


if __name__ == "__main__":
    unittest.main()
