"""Checks that docs/ccsplit-plan.md is a complete pre-registration (id, what was seen, gates,
predictions with probabilities, what happens with the result, limits), that its bars match the
constants in tools/ccsplit/ccsplit.py, and that the tool finds a collapsed combined cycle in a
tiny made-up example. Reads no outside data.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import importlib.util
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


def load_tool():
    spec = importlib.util.spec_from_file_location(
        "ccsplit", os.path.join(HERE, "tools", "ccsplit", "ccsplit.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class CcsplitPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = read("docs/ccsplit-plan.md")
        cls.code = read("tools/ccsplit/ccsplit.py")
        cls.fetch = read("tools/ccsplit/fetch_plan_code.py")

    def test_structure(self):
        for text in ("Status: pre-registration, nothing run yet. Pre-registration id: ccsplit-1.",
                     "## What we have seen (before writing this)", "## Method",
                     "## Gate (if it fails, nothing is scored)",
                     "## Predictions (probability we give each)",
                     "## What happens with the result", "## Limits",
                     "made with AI agents working in MV2's name",
                     "no person has checked this plan by hand",
                     "No count of collapsed combined cycles, orphan CA generators or CC plants "
                     "has been made by us or reported to us.",
                     "A failed bar is reported as failed, with its cause, and is not re-scored.",
                     "259 subplants that only contain one part of a combined cycle system"):
            self.assertIn(text, self.plan)

    def test_predictions(self):
        for text in ("**P1 (70%):** there are at least 5 hit plants",
                     "**P2 (75%):** there are at most 50 hit plants.",
                     "**P3 (55%):** there are at least 2 times as many orphan-CA plants",
                     "**P4 (60%):** of the hit plants that have any crosswalk row in report "
                     "year 2019, at least 70%",
                     "Scored only if there are at least 3 such plants.",
                     "**P5 (55%):** in at least 60% of hits",
                     "**P6 (65%):** in at least 70% of hit plants, the orphan CA nameplate is "
                     "between 0.1 and 1.2 times",
                     "at least 95% of that year's EIA-860 generators",
                     "there are at least 200 CC plants in that year",
                     "Glenarm (EIA 422) and LEPA Unit No. 1 (EIA 58478) are both hit plants",
                     "`tools/ccsplit/ccsplit.py` 0.1.0"):
            self.assertIn(text, self.plan)

    def test_bars_match_code(self):
        for text in ('VERSION = "0.1.0"', "MIN_NEWEST = 2023", "MIN_PM_SHARE = 0.95",
                     "MIN_CC_PLANTS = 200", "KNOWN = (422, 58478)", "P1_MIN = 5", "P2_MAX = 50",
                     "P3_FACTOR = 2", "P4_YEAR = 2019", "P4_MIN_N = 3", "P4_SHARE = 0.7",
                     "P5_SHARE = 0.6", "P6_LO = 0.1", "P6_HI = 1.2", "P6_SHARE = 0.7"):
            self.assertIn(text, self.code)
        self.assertIn('TOKEN = "Pre-registration id: ccsplit-1."', self.fetch)

    def test_tool_finds_known_shape(self):
        c = load_tool()
        rows = [{"report_year": 2024, "plant_id_epa": 422, "emissions_unit_id_epa": "GT5",
                 "generator_id_epa": g, "plant_id_eia": 422, "generator_id": "GT5"}
                for g in ("CTG5", "STG5")]
        gens = [{"plant_id_eia": 422, "generator_id": g, "report_date": "2024-01-01",
                 "capacity_mw": cap, "prime_mover_code": pm, "operational_status_code": "OP"}
                for g, cap, pm in (("GT5", 71.0, "CT"), ("ST1", 16.0, "CA"))]
        lint = c.year_lint(c.index_links(rows)[2024], c.index_gens(gens)[2024])
        self.assertEqual(lint["hit_plants"], [422])
        self.assertEqual(lint["orphan_ca_plants"], [422])
        self.assertEqual(lint["cc_plants"], 1)


if __name__ == "__main__":
    unittest.main()
