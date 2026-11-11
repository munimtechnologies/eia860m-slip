"""Checks that docs/phsize-plan.md is a complete pre-registration (id, what was seen, gates,
predictions with probabilities, what happens with the result, limits), that its bars and lists
match the constants in tools/phsize/phsize.py, and runs the tool's own unit tests
(tools/phsize/test_phsize.py) on made-up grouped rows. Reads no outside data.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "tools", "phsize"))

import phsize  # noqa: E402
from test_phsize import (ConstantTests, HelperTests, StudyTests)  # noqa: E402,F401


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class PhsizePlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = read("docs/phsize-plan.md")
        cls.code = read("tools/phsize/phsize.py")
        cls.fetch = read("tools/phsize/fetch_plan_phsize.py")

    def test_structure(self):
        for text in ("Status: pre-registration, nothing run yet. Pre-registration id: phsize-1.",
                     "## What we have seen (before writing this)", "## Method",
                     "## Gate (if it fails, nothing is scored)",
                     "## Predictions (probability we give each)",
                     "## What happens with the result", "## Limits",
                     "made with AI agents working in MV2's name",
                     "no person has checked this plan by hand",
                     "A failed bar is reported as failed, with its cause, and is not re-scored.",
                     "pudl/issues/4646", "Not seen:", "6,532,003 bytes",
                     "_core_phmsagas__yearly_distribution_by_material_and_size.parquet",
                     "0 results each", "This is a reading of the code only."):
            self.assertIn(text, self.plan)

    def test_predictions(self):
        for text in ("**P1 (80%):** at least 100 services rows have a null `main_size`.",
                     "**P2 (85%):** at least 99% of the null-size services rows",
                     "If there are no null-size services rows, there is nothing to test, and P2 "
                     "counts as failed.",
                     "**P3 (70%):** at least 100 services rows are 8_in no-mains rows",
                     "**P4 (85%):** no services row has a size the services columns cannot produce",
                     "**P5 (65%):**", "less than 1% of the base",
                     "**Gate G1:**", "**Gate G2:** at least 100,000 rows and at least 1,000 "
                     "services rows.",
                     "`tools/phsize/phsize.py` 0.1.0", "240-minute limit", "up to 3,000",
                     "1 CPU, 2 GB"):
            self.assertIn(text, self.plan)

    def test_lists_match_code(self):
        p2 = ("steel, copper, cast_iron, plastic, other, all_materials, other_alt or "
              "other_material")
        self.assertIn(p2, self.plan)
        self.assertEqual(tuple(p2.replace(" or ", ", ").split(", ")), phsize.NULL_OK)
        no8 = ("cast_or_wrought_iron, pvc, pe, abs, other_plastic, other_alt, "
               "reconditioned_cast_iron")
        self.assertIn(no8, self.plan)
        self.assertEqual(tuple(no8.split(", ")), phsize.NO_MAIN8)
        over6 = "steel, copper, cast_iron, plastic, other and all_materials"
        self.assertIn("`over_6_in` appears for " + over6, self.plan)
        self.assertEqual(tuple(over6.replace(" and ", ", ").split(", ")), phsize.OVER6)
        p4 = ("0.5_in_or_less, 0.5_to_1_in, 1_in_or_less, 1_to_2_in, 2_to_4_in, 4_to_6_in, "
              "4_to_8_in, 8_in, total, unknown or null")
        self.assertIn(p4, self.plan)
        sizes = set(p4.replace(" or ", ", ").split(", "))
        sizes.discard("null")
        self.assertEqual(sizes | {phsize.NULL}, set(phsize.SERVICE_SIZES))

    def test_bars_match_code(self):
        for text in ('VERSION = "0.1.0"', "G2_MIN_ROWS = 100000", "G2_MIN_SERVICES = 1000",
                     "P1_MIN = 100", "P2_MIN = 0.99", "P3_MIN = 100", "P4_MAX_OTHER = 0",
                     "P5_MAX_SHARE = 0.01", "SAMPLE_CAP = 3000",
                     'TABLE = "_core_phmsagas__yearly_distribution_by_material_and_size"',
                     "Apache-2.0"):
            self.assertIn(text, self.code)
        self.assertIn('TOKEN = "Pre-registration id: phsize-1."', self.fetch)
        self.assertIn('FILES = ("phsize.py", "test_phsize.py")', self.fetch)


if __name__ == "__main__":
    unittest.main()
