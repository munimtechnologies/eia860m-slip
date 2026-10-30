"""Checks that docs/cems-mindown-plan.md describes what tools/cems-mindown/ runs: versions,
the pinned PUDL commit, states, year, sizes and the bars. Reads every file as text, so it
needs no polars.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SHA_MAIN = "4d3366b30d05a4c1c13cd8e88ba9b7b2f9ea6db2"
TOOLS = ("fill_isolated.py", "reference.py", "stubs.py", "mindown_check.py")


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class CemsMindownPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/cems-mindown-plan.md")
        cls.tools = {name: read("tools/cems-mindown/" + name) for name in TOOLS}
        cls.code = cls.tools["mindown_check.py"]
        cls.fix = cls.tools["fill_isolated.py"]

    def test_status_and_id(self):
        self.assertIn("Status: pre-registration, nothing run yet.", self.doc)
        self.assertIn("Pre-registration id: cems-mindown-1.", self.doc)

    def test_versions_and_commit(self):
        self.assertIn('VERSION = "0.1.0"', self.fix)
        self.assertIn('VERSION = "0.1.0"', self.code)
        self.assertIn("`tools/cems-mindown/fill_isolated.py` 0.1.0", self.doc)
        self.assertIn("`tools/cems-mindown/mindown_check.py` 0.1.0", self.doc)
        self.assertIn('SHA_MAIN = "%s"' % SHA_MAIN, self.code)
        self.assertIn(SHA_MAIN, self.doc)

    def test_scope(self):
        for text in ('STATES = ["CO", "IN", "WI"]', "REPORT_YEAR = 2025", "NUM_QUARTERS = 12",
                     "MIN_STABLE_HOURS = 8", "RANDOM_FRAMES = 300", "SEED = 20261030",
                     "MAX_READ_BYTES = 2_500_000_000"):
            self.assertIn(text, self.code)
        for text in ("Colorado, Indiana and Wisconsin, 2023-2025", "seed 20261030",
                     "300 random frames", "at most 2.5 GB compressed",
                     '"2025q4", 12 quarters', "8 stable hours"):
            self.assertIn(text, self.doc)

    def test_fill_rule(self):
        self.assertIn("dt.total_seconds().eq(3600)", self.fix)
        self.assertIn("hours[i] - hours[i - 1] == HOUR and hours[i + 1] - hours[i] == HOUR",
                      self.tools["reference.py"])
        self.assertIn("exactly one hour before and exactly one hour after it", self.doc)

    def test_bars(self):
        for text in ("**Gate G1:**", "**T1 (95%):**", "**T2 (90%):**", "**T3 (95%):**",
                     "**T4 (90%):**", "**N1 (90%):**", "**Gate R0:**", "**F1 (85%):**",
                     "**F2 (80%):**", "**F3 (95%):**", "**F4 (80%):**"):
            self.assertIn(text, self.doc)
        for text in ('fill["min_down_eq_1"] <= 0.25 * none[',
                     '<= 0.10 * none["min_up_eq_1"]',
                     'n["share_min_down_eq_1"] >= 0.5',
                     '>= 0.95 * r0["rows"]', '>= 0.95 * r0["found"]',
                     'none["min_down_eq_1"] >= 20'):
            self.assertIn(text, self.code)

    def test_cases_match(self):
        for text in ('"C1_isolated_null": ([U, U, U, None, U, U, U, U], None, (3, 1), (8, None))',
                     '"C2_two_null_hours": ([U, U, None, None, U, U, U, U], None, (2, 2), (2, 2))',
                     '"C4_null_first_hour": ([None, U, U, U, U, U, U, U], None, (7, 1), (7, 1))',
                     '"C5_low_neighbours": ([U, LO, None, LO, U, U, U, U], None, (1, 1), (1, None))'):
            self.assertIn(text, self.code)
        for text in ("C1 isolated null hour (3, 1) and (8, none)",
                     "C2 two null hours (2, 2) and (2, 2)",
                     "C3 null hour after a gap (3, 1) and (3, 1)",
                     "C4 null first hour (7, 1) and (7, 1)",
                     "(1, 1) and (1, none)"):
            self.assertIn(text, self.doc)

    def test_nothing_of_pudl_stored(self):
        self.assertIn("PUDL's code (MIT) and data (CC BY 4.0) are downloaded at run time "
                      "and not stored here.", self.doc)
        for name, text in self.tools.items():
            self.assertNotIn("def assign_groupwise_load_factor_bins", text, name)
            self.assertNotIn("def _add_run_id_expr", text, name)
            self.assertIn("Apache-2.0", text, name)


if __name__ == "__main__":
    unittest.main()
