"""Checks the H2 score note (docs/doe-202c-rehearing-h2.md): the dates it states and the day
counts it derives from them. Reads no outside data.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import datetime as dt
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


class H2ScoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(HERE, "docs", "doe-202c-rehearing-h2.md"), encoding="utf-8") as fh:
            cls.doc = fh.read()

    def test_held(self):
        notice = dt.date(2026, 10, 22)
        self.assertLessEqual(notice, dt.date(2026, 11, 2))
        self.assertIn("**H2 held.**", self.doc)
        self.assertIn("| 22 October 2026 | DOE |", self.doc)

    def test_day_counts(self):
        self.assertEqual((dt.date(2026, 10, 22) - dt.date(2026, 9, 17)).days, 35)
        self.assertIn("It came 35 days after the request.", self.doc)
        self.assertEqual((dt.date(2026, 10, 15) - dt.date(2026, 9, 11)).days, 34)
        self.assertIn("dated 15 October 2026 (202-26-39A), 34 days later", self.doc)

    def test_disclosure(self):
        self.assertIn("made with AI agents working in MV2's name", self.doc)
        self.assertIn("[doe-202c-rehearing.md](doe-202c-rehearing.md)", self.doc)


if __name__ == "__main__":
    unittest.main()
