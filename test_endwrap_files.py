"""Checks that tools/endwrap is published with its unit tests and check script, wraps
eia860m_slip at run time instead of editing it, and carries the licence and disclosure.
Reads text only (the unit tests in tools/endwrap need pandas and run in the check job).

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class EndwrapFileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.code = read("tools/endwrap/endwrap.py")
        cls.tests = read("tools/endwrap/test_endwrap.py")
        cls.check = read("tools/endwrap/endwrap_check.py")

    def test_rule_and_reader(self):
        for text in ('VERSION = "0.1.0"', "def detect_rule(df):",
                     'rule = "exclusive" if n_next > n_at else "inclusive"',
                     "until = df[\"valid_m\"] - 1",
                     "es.listed_until = make_reader(current)",
                     "runpy.run_path(argv[0], run_name=\"__main__\")"):
            self.assertIn(text, self.code)
        self.assertNotIn("open(\"eia860m_slip.py\"", self.code)

    def test_tests_cover_both_rules(self):
        for text in ("def test_new_rule", "def test_old_rule",
                     "def test_tie_keeps_the_original_reader",
                     "def test_install_dispatches_and_is_idempotent"):
            self.assertIn(text, self.tests)

    def test_licence_and_disclosure(self):
        for text in (self.code, self.tests, self.check):
            self.assertIn("Apache-2.0", text)
            self.assertIn("Made with AI agents working in MV2's name", text)
            self.assertNotIn("MIT License", text)
        self.assertIn("not pre-registered", self.check)


if __name__ == "__main__":
    unittest.main()
