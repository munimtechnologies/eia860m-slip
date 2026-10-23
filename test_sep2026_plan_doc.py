"""Doc test: the bars stated in docs/sep2026-plan.md are the ones monthcheck.py scores.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
DOC = os.path.join(HERE, "docs", "sep2026-plan.md")
CODE = os.path.join(HERE, "tools", "annual-flows-candidate", "monthcheck.py")


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


class Sep2026PlanTests(unittest.TestCase):
    def setUp(self):
        self.doc, self.code = read(DOC), read(CODE)

    def const(self, name):
        m = re.search(r"^%s = ([0-9.]+)" % name, self.code, re.M)
        self.assertIsNotNone(m, name)
        return m.group(1)

    def test_status_and_version(self):
        self.assertIn("Status: pre-registered, not yet scored.", self.doc)
        self.assertIn('__version__ = "0.1.0"', self.code)
        self.assertIn('PLAN = "docs/sep2026-plan.md"', self.code)
        self.assertIn("`monthcheck.py` 0.1.0", self.doc)

    def test_bars(self):
        self.assertEqual(self.const("KEYS_TOL"), "0.03")
        self.assertIn("within 3% of August 2026's", self.doc)
        self.assertEqual(self.const("LEFT_MAX"), "50")
        self.assertIn("**P2.** At most 50 generators leave in September 2026.", self.doc)
        self.assertEqual(self.const("RETIRED_LEFT_BELOW"), "10")
        self.assertIn("**P3.** Fewer than 10 of the generators", self.doc)
        self.assertEqual(self.const("BAND_MONTHS"), "24")
        self.assertIn("the second lowest and the second highest of the shares of the 24 months before it", self.doc)

    def test_record(self):
        left = [9, 5, 7, 23, 26, 50, 30, 34, 25, 31, 11, 9]
        self.assertIn("9, 5, 7, 23, 26, 50, 30, 34, 25, 31, 11 and 9 generators left", self.doc)
        self.assertEqual((max(left), left.index(max(left))), (50, 5))
        self.assertIn("The most was 50, in February 2026.", self.doc)
        self.assertIn("probability 21 in 25 (84%)", self.doc)


if __name__ == "__main__":
    unittest.main()
