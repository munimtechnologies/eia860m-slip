"""Checks that docs/xwtz-plan.md is a complete pre-registration (id, what was seen, gates,
predictions with probabilities, what happens with the result, limits), that its bars match the
constants in tools/xwtz/xwtz.py, and runs the tool's own unit tests (tools/xwtz/test_xwtz.py) on
made-up rows. Reads no outside data.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "tools", "xwtz"))

from test_xwtz import (BuildTests, ClassifyTests, ConstantTests,  # noqa: E402,F401
                       HelperTests, ScoreTests)


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class XwtzPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = read("docs/xwtz-plan.md")
        cls.code = read("tools/xwtz/xwtz.py")
        cls.fetch = read("tools/xwtz/fetch_plan_code.py")

    def test_structure(self):
        for text in ("Status: pre-registration, nothing run yet. Pre-registration id: xwtz-1.",
                     "## What we have seen (before writing this)", "## Method",
                     "## Gate (if it fails, nothing is scored)",
                     "## Predictions (probability we give each)",
                     "## What happens with the result", "## Limits",
                     "made with AI agents working in MV2's name",
                     "no person has checked this plan by hand",
                     "A failed bar is reported as failed, with its cause, and is not re-scored.",
                     "pudl/issues/5162", "harmonize_eia_epa_orispl", "convert_to_utc",
                     "_load_plant_utc_offset", "the plant_id_epa is almost always correct",
                     "Not seen: any timezone value"):
            self.assertIn(text, self.plan)

    def test_predictions(self):
        for text in ("**P1 (70%):** no 2024 unit is inconsistent",
                     "**P2 (65%):** at most 5 units in 2024 have no timezone.",
                     "**P3 (60%):** at most 10 EPA plants have a unit with no timezone in any "
                     "report year from 2018 to 2024.",
                     "**P4 (60%):** at least 1 unit in 2024 is borrowed.",
                     "**P5 (25%):** at least 1 unit-year from 2018 to 2024 is borrowed into a "
                     "different timezone.",
                     "**Gate G1:**", "report years 2018 to 2024.",
                     "**Gate G2:** the yearly CEMS table has between 4,100 and 4,300 units in "
                     "report year 2024.",
                     "**Gate G3:** at least 99% of crosswalk keys map to a single EIA plant id.",
                     "(at most 40, smallest ids first)", "three control plants",
                     "40-minute limit", "`tools/xwtz/xwtz.py` 0.1.0"):
            self.assertIn(text, self.plan)

    def test_bars_match_code(self):
        for text in ('VERSION = "0.1.0"', "YEARS = tuple(range(2018, 2025))", "FOCUS = 2024",
                     "G2_MIN = 4100", "G2_MAX = 4300", "G3_UNIQUE = 0.99", "P1_MAX = 0",
                     "P2_MAX_UNITS = 5", "P3_MAX_PLANTS = 10", "P4_MIN_UNITS = 1",
                     "P5_MIN_UNITS = 1", "VERIFY_MAX_PLANTS = 40", "VERIFY_FROM_YEAR = 2018",
                     "CONTROLS = 3",
                     'OPS_TABLE = "out_epacems__yearly_operational_characteristics"',
                     'XW_TABLE = "core_epa__assn_eia_epacamd"',
                     'PL_TABLE = "core_eia__entity_plants"',
                     'HOURLY_TABLE = "core_epacems__hourly_emissions"'):
            self.assertIn(text, self.code)
        self.assertIn('TOKEN = "Pre-registration id: xwtz-1."', self.fetch)


if __name__ == "__main__":
    unittest.main()
