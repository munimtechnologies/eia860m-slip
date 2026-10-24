"""Doc test: the practice run of monthrun.py on September 2026 (docs/monthrun-practice-v1-output.md)
reproduced the published changelog and every published September number it checks, and README.md says
no more than that.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8") as fh:
        return fh.read()


class MonthrunPracticeDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = read("docs", "monthrun-practice-v1-output.md")
        cls.readme = read("README.md")

    def test_header(self):
        self.assertIn("# monthrun 0.1.0: EIA-860M 2026-09", self.out)
        self.assertIn("Mode: practice (the month is in the published changelog).", self.out)
        self.assertIn("Archive replayed through 2026-07 (133 months; not readable: none).", self.out)

    def test_c0(self):
        self.assertIn("Same text through 2026-09: True. Lines: published 117757, rebuilt 117757. "
                      "First difference: none.", self.out)

    def test_august_same_as_archive(self):
        row = [l for l in self.out.splitlines() if l.startswith("| 2026-08 |")][0]
        self.assertIn("| 9727ac867236faab7d5503175dacdf38 | 9727ac867236faab7d5503175dacdf38 | True | True | 38011 |",
                      row)
        row = [l for l in self.out.splitlines() if l.startswith("| 2026-09 |")][0]
        self.assertIn("/xls/september_generator2026.xlsx | 14013970 |", row)
        self.assertIn("| True | 38162 | 646 |", row)

    def test_all_same(self):
        for item, value in (("listed", "38162"), ("listed_before", "38011"), ("left", "20"), ("left_retired", "16"),
                            ("cohort", "170"), ("operating", "57"),
                            ("held", "[True, True, False, True]"), ("p5", "0"), ("p5_before", "28"), ("s3", "0")):
            self.assertIn("| %s | %s | %s | True |" % (item, value, value), self.out)
        self.assertIn("All the same: True.", self.out)
        self.assertNotIn("| False |\n", self.out.split("## Practice check")[1])

    def test_expect_is_published(self):
        sep = read("docs", "sep2026.md")
        for s in ("(+0.40%)", "| P2. At most 50 generators leave | held | 20 |",
                  "| P3. Fewer than 10 of them leave from the Retired sheet | failed | 16 |",
                  "| held | 0.3353 (57 of 170) |"):
            self.assertIn(s, sep)
        self.assertIn("Together the 28 are 10,446.1 MW", read("docs", "retiredentry.md"))
        code = read("tools", "annual-flows-candidate", "monthrun.py")
        self.assertIn('EXPECT = {"2026-09": {"listed": 38162, "listed_before": 38011, "left": 20, "left_retired": 16, '
                      '"cohort": 170,', code)
        self.assertIn('"operating": 57, "held": [True, True, False, True], "p5": 0, "p5_before": 28, "s3": 0}}', code)
        self.assertIn('__version__ = "0.1.0"', code)

    def test_unit_tests_passed(self):
        log = read("docs", "monthrun-practice-v1-unittests.txt")
        self.assertIn("Ran 25 tests", log)
        self.assertTrue(log.rstrip().endswith("OK"))

    def test_readme(self):
        for s in ("[`tools/annual-flows-candidate/monthrun.py`](tools/annual-flows-candidate/monthrun.py) 0.1.0",
                  "was practised on September 2026 before October's release",
                  "matched the published changelog's text line for line, and reproduced all ten published September "
                  "numbers it checks ([`docs/monthrun-practice-v1-output.md`](docs/monthrun-practice-v1-output.md))",
                  "EIA's own August 2026 file has the same md5 as the copy in PUDL's archive.",
                  "This is a check of the code, not a result."):
            self.assertIn(s, self.readme)


if __name__ == "__main__":
    unittest.main()
