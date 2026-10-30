"""Checks that docs/pudl-tall.md scores the plan's gate and three predictions with the counts
job pudl-tall-v1 wrote, by the bars in docs/pudl-tall-plan.md. Reads text only, so it needs
no pandas.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))

# Copied from compete-results/pudl-tall-v1/out/tall_check.json:
# rows, zero_length, zero_length_alone_on_series_date, valid_until_before_report_date,
# zero_length_is_candidate, md5.
COUNTS = {
    "boilers": (222640, 0, 0, 0, 0, "9d6951a7de5dad473602615410bb4261"),
    "generators": (1731400, 119, 0, 0, 73, "674c66eef6d02d401935c1e9ca2571eb"),
    "plants": (920891, 24592, 0, 0, 2926, "009bfa1b8c63569d4cf321aacf6ecf89"),
    "utilities": (281516, 2726, 0, 0, 227, "58ce74ada7d8a45c117a09553620a0e4"),
}
GATE = True


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class PudlTallScoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/pudl-tall.md")
        cls.plan = read("docs/pudl-tall-plan.md")

    def test_scores_follow_the_bars(self):
        p1 = all(c[1] > 0 for c in COUNTS.values())
        p2 = all(c[2] == 0 for c in COUNTS.values())
        p3 = all(c[3] == 0 for c in COUNTS.values())
        self.assertTrue(GATE)
        self.assertEqual((p1, p2, p3), (False, True, True))
        self.assertIn("The gate held and 2 of 3 predictions held; P1 missed", self.doc)
        self.assertIn("| P1 (80%) | each table has at least one same-day record | **missed**",
                      self.doc)
        self.assertIn("| P2 (90%) | every same-day record shares its series and date with "
                      "another record | held", self.doc)
        self.assertIn("| P3 (95%) | no record has `valid_until_date` before its "
                      "`report_date` | held", self.doc)
        for text in ("**P1 (80%):**", "**P2 (90%):**", "**P3 (95%):**",
                     "Pre-registration id: pudl-tall-1."):
            self.assertIn(text, self.plan)

    def test_table_rows(self):
        for name, (rows, zero, alone, before, cand, md5) in COUNTS.items():
            share = "%.2f%%" % (100.0 * zero / rows)
            row = "| %s | {:,} | {:,} | %s | %d | %d | {:,} |".format(rows, zero, cand) % (
                name, share, alone, before)
            self.assertIn(row, self.doc)
            self.assertIn(md5, self.doc)

    def test_totals(self):
        zero = sum(c[1] for c in COUNTS.values())
        rows = sum(c[0] for c in COUNTS.values())
        self.assertEqual((zero, rows), (27437, 3156447))
        self.assertIn("27,437 of 3,156,447 rows", self.doc)

    def test_same_numbers_as_the_pr(self):
        self.assertIn("24,592 in plants, 2,726 in utilities and 119 in generators", self.doc)
        self.assertIn("https://github.com/catalyst-cooperative/pudl/pull/5731", self.doc)

    def test_no_data_stored(self):
        self.assertIn("PUDL's data (CC BY 4.0) was downloaded at run time and is not stored "
                      "here.", self.doc)


if __name__ == "__main__":
    unittest.main()
