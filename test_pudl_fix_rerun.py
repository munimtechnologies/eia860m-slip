"""Checks that the "E2 re-run: scored" section of docs/pudl-fix.md reports what job
pudl-fix-v2 wrote, scores E2 by the bar fixed before the job ran, and leaves the first
scoring in place. Reads text only, so it needs no pandas.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))

# Copied from compete-results/pudl-fix-v2/out/fix_check2.json.
E2 = {"orig": (8, 8), "patched": (8, 8), "name_errors": 0,
      "imports_added": ["import pandas as pd", "import pytest",
                        "from pandas.testing import assert_frame_equal"],
      "test_functions": ["test_make_changelog_handles_mixed_record_value_types",
                         "test_make_changelog_is_order_independent",
                         "test_make_changelog_valid_until_is_per_column",
                         "test_make_changelog_without_record_value_column"]}
E7 = {"original_seconds": 0.45, "patched_seconds": 0.981, "ratio": 2.18,
      "patched_rows_kept": 38229, "original_rows_kept": 37659}


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class PudlFixRerunTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/pudl-fix.md")
        cls.check2 = read("tools/pudl-fix/check_fix2.py")
        marker = "## E2 re-run: scored (30 October 2026)"
        if cls.doc.count(marker) != 1:
            raise AssertionError("section heading missing or repeated")
        cls.first, cls.rerun = cls.doc.split(marker)

    def test_bar_applied(self):
        (oc, op), (pc, pp) = E2["orig"], E2["patched"]
        held = oc == pc and oc > 0 and op == oc and pp == pc and E2["name_errors"] == 0
        self.assertTrue(held)
        self.assertIn("Re-run result: E2 held.", self.rerun)
        self.assertIn("| original `make_changelog` (4d3366b) | 8 | 8 | 0 |", self.rerun)
        self.assertIn("| patched (keep_changes.py 0.1.0) | 8 | 8 | 0 |", self.rerun)
        self.assertIn("the fix meets all 7 expectations of the plan", self.rerun)

    def test_harness_details(self):
        for line in E2["imports_added"]:
            self.assertIn("`%s`" % line, self.rerun)
        for name in E2["test_functions"]:
            self.assertIn("`%s`" % name, self.rerun)
        self.assertIn('e2["name_errors"]', self.check2)

    def test_reproduction_numbers(self):
        self.assertEqual(round(E7["patched_seconds"] / E7["original_seconds"], 2), E7["ratio"])
        self.assertIn("0.981 s against 0.450 s, 2.18 times", self.rerun)
        self.assertIn("38,229 records against the original's 37,659", self.rerun)
        self.assertIn("400 of 400, 232 frames, 1,147 records", self.rerun)
        self.assertIn("4ffb24b50db7641e3ba91dea7ea7e064", self.rerun)
        self.assertIn("5054a0486fc87ea1a1d789b7a2a78c96", self.rerun)

    def test_first_scoring_kept(self):
        self.assertIn("6 of 7 expectations held; E2 missed", self.first)
        self.assertIn("| E2 | PUDL's own tests pass under both | **missed**", self.first)
        self.assertIn("Update, 30 October 2026: the E2 re-run held", self.first)

    def test_upstream_pr_named(self):
        self.assertIn("https://github.com/catalyst-cooperative/pudl/pull/5731", self.rerun)
        self.assertIn("MV2 offers no pull request of his own", self.rerun)
        self.assertIn("[pudl-pr-plan.md](pudl-pr-plan.md)", self.rerun)


if __name__ == "__main__":
    unittest.main()
