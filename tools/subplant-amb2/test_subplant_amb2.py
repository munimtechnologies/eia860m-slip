"""Unit tests for subplant_amb2.py on small hand-made frames (no network, no PUDL data).
Needs subplant_amb.py 0.1.0 and subplant_gap.py 0.1.0 next to it (or in ../subplant-amb/ and
../subplant-gap/).

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.)."""

import unittest

import pandas as pd

import subplant_amb2 as s2

sa = s2.sa
sg = s2.sg
D = pd.Timestamp("2024-01-01")


def frames():
    xw = pd.DataFrame([
        # plant 11: the generator has one boiler (single under rule 1)
        (2024, 911, "U1", 11, None, "G1"),
        # plant 12: two turbines, HRSG ids match nothing, units have no other row (unresolved)
        (2024, 912, "CT1", 12, None, "GT1"), (2024, 912, "CT2", 12, None, "GT2"),
        # plant 17: each turbine unit is tied to its own turbine (name under rule 1) and to the
        # block's steam turbine ST1 (unresolved under rule 1, "unit" under rule 2)
        (2024, 917, "1A", 17, None, "CT1A"), (2024, 917, "1A", 17, None, "ST1"),
        (2024, 917, "2A", 17, None, "CT1B"), (2024, 917, "2A", 17, None, "ST1"),
        # plant 18: unit U1 has a crosswalk boiler B1, and a blank row to G2 (two boilers)
        (2024, 918, "U1", 18, "B1", "G1"), (2024, 918, "U1", 18, None, "G2"),
    ], columns=sg.COLUMNS["xw"])
    sp = pd.DataFrame([
        (11, 911, 1, "U1", "G1"),
        (12, 912, 1, "CT1", "GT1"), (12, 912, 1, "CT2", "GT2"), (12, 912, 1, None, "ST1"),
        (17, 917, 1, "1A", "CT1A"), (17, 917, 1, "2A", "CT1B"), (17, 917, 1, None, "ST1"),
        (18, 918, 1, "U1", "G1"), (18, 918, 1, "U1", "G2"),
    ], columns=sg.COLUMNS["sp"])
    bga = pd.DataFrame([
        (11, D, "G1", "B1"),
        (12, D, "ST1", "HRSG1"), (12, D, "ST1", "HRSG2"),
        (17, D, "CT1A", "CT1A"), (17, D, "CT1A", "HRSG1"),
        (17, D, "CT1B", "CT1B"), (17, D, "CT1B", "HRSG2"),
        (17, D, "ST1", "CT1A"), (17, D, "ST1", "CT1B"),
        (17, D, "ST1", "HRSG1"), (17, D, "ST1", "HRSG2"),
        (18, D, "G1", "B1"), (18, D, "G2", "B2"), (18, D, "G2", "B3"),
    ], columns=sg.COLUMNS["bga"])
    heat = {(11, "B1"): 50, (12, "HRSG1"): 10, (12, "HRSG2"): 10,
            (17, "CT1A"): 100, (17, "CT1B"): 100, (17, "HRSG1"): 10, (17, "HRSG2"): 5,
            (18, "B1"): 50, (18, "B2"): 20, (18, "B3"): 5}
    bf = pd.DataFrame([(p, b, "NG", D, float(v), 1.0) for (p, b), v in heat.items()],
                      columns=sg.COLUMNS["bf"])
    return xw, sp, bga, bf


class UnitRuleTests(unittest.TestCase):
    def setUp(self):
        self.xw, self.sp, self.bga, self.bf = frames()
        self.rows1, _ = sa.classify(self.xw, self.sp, self.bga, 2024)
        self.m, self.rev, self.rows2, self.subs1, self.subs2 = s2.one_year(
            self.xw, self.sp, self.bga, self.bf, 2024)

    def cls(self, rows, plant, unit, gen):
        r = rows[(rows["plant_id_eia"] == plant) & (rows["emissions_unit_id_epa"] == unit)
                 & (rows["generator_id"] == gen)]
        self.assertEqual(len(r), 1, (plant, unit, gen))
        return r.iloc[0]["class"]

    def test_rule1_unchanged(self):
        want = {(11, "U1", "G1"): "single", (12, "CT1", "GT1"): "unresolved",
                (12, "CT2", "GT2"): "unresolved", (17, "1A", "CT1A"): "name",
                (17, "2A", "CT1B"): "name", (17, "1A", "ST1"): "unresolved",
                (17, "2A", "ST1"): "unresolved", (18, "U1", "G2"): "unresolved"}
        self.assertEqual(len(self.rows1), len(want))
        for key, c in want.items():
            self.assertEqual(self.cls(self.rows1, *key), c, key)

    def test_rule2_classes(self):
        want = {(11, "U1", "G1"): "single", (12, "CT1", "GT1"): "unresolved",
                (12, "CT2", "GT2"): "unresolved", (17, "1A", "CT1A"): "name",
                (17, "2A", "CT1B"): "name", (17, "1A", "ST1"): "unit",
                (17, "2A", "ST1"): "unit", (18, "U1", "G2"): "unit"}
        self.assertEqual(len(self.rows2), len(want))
        for key, c in want.items():
            self.assertEqual(self.cls(self.rows2, *key), c, key)
        self.assertTrue(self.rows2[self.rows2["class"] == "unit"]["boiler_id"].isna().all())

    def test_metrics(self):
        m = self.m
        self.assertEqual(m["rows"], 8)
        self.assertEqual(m["rows_by_class"],
                         {"covered": 0, "single": 1, "name": 2, "unit": 3, "unresolved": 2})
        self.assertEqual(m["unresolved_rule1"], 5)
        self.assertEqual(m["ambiguous_subplants"], 4)
        self.assertEqual(m["ambiguous_after_rule1"], 3)
        self.assertEqual(m["ambiguous_after_rule2"], 1)
        self.assertEqual(m["resolved_by_rule2"], 2)
        self.assertEqual(m["rule2_linked_mmbtu"], 290.0)
        self.assertEqual(m["rule2_gap_mmbtu"], 40.0)
        self.assertEqual(m["rule2_gap_plants"], 2)
        self.assertEqual(m["rule2_gap_hrsg_mmbtu"], 15.0)
        self.assertEqual(m["rows_outside_subplants_with_boilers"], 0)

    def test_revised_counts(self):
        self.assertEqual(self.rev["ambiguous_subplants"], 1)  # plant 12
        self.assertEqual(self.rev["strict"]["gap_plants"], 2)  # 17 and 18
        self.assertEqual(self.rev["strict"]["gap_mmbtu"], 40.0)

    def test_score(self):
        got = s2.score(True, True, self.m)
        # Q1 3*2 >= 5; Q2 1 <= 100; Q3 40 < 29 fails; Q4 15*2 >= 40 fails
        self.assertEqual([got[k] for k in ("Q1", "Q2", "Q3", "Q4")], [True, True, False, False])

    def test_gate(self):
        base = {"unresolved_rule1": 435, "ambiguous_subplants": 602, "ambiguous_after_rule1": 160}
        self.assertTrue(s2.gate_g1(base))
        self.assertFalse(s2.gate_g1(dict(base, unresolved_rule1=471)))
        self.assertFalse(s2.gate_g1(dict(base, ambiguous_after_rule1=183)))


if __name__ == "__main__":
    unittest.main()
