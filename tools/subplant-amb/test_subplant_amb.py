"""Unit tests for subplant_amb.py on small hand-made frames (no network, no PUDL data).
Needs subplant_gap.py 0.1.0 next to it (or in ../subplant-gap/).

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.)."""

import unittest

import pandas as pd

import subplant_amb as sa
import subplant_gap as sg

D = pd.Timestamp("2024-01-01")


def frames():
    xw = pd.DataFrame([
        # plant 10: two turbines, no boiler of their own; HRSG ids match the unit ids (name)
        (2024, 910, "CT1", 10, None, "CT1"), (2024, 910, "CT2", 10, None, "CT2"),
        # plant 11: the generator has one boiler (single)
        (2024, 911, "U1", 11, None, "G1"),
        # plant 12: two turbines, HRSG ids match nothing (unresolved)
        (2024, 912, "CT1", 12, None, "GT1"), (2024, 912, "CT2", 12, None, "GT2"),
        # plant 13: one matched boiler, one turbine whose subplant has one other boiler (single)
        (2024, 913, "B7", 13, "B7", "G7"), (2024, 913, "CT9", 13, None, "CT9"),
        # plant 14: unit id matches one of the generator's two boilers (name); AUX stays a gap
        (2024, 914, "B4", 14, None, "G4"),
        # plant 15: the generator's only boiler is matched by another row (covered)
        (2024, 915, "U5", 15, "B5", "G5"), (2024, 915, "U6", 15, None, "G5"),
        # plant 16: strict subplant with a gap boiler
        (2024, 916, "U8", 16, "B8", "G8"),
    ], columns=sg.COLUMNS["xw"])
    sp = pd.DataFrame([
        (10, 910, 1, "CT1", "CT1"), (10, 910, 1, "CT2", "CT2"), (10, 910, 1, None, "ST1"),
        (11, 911, 1, "U1", "G1"),
        (12, 912, 1, "CT1", "GT1"), (12, 912, 1, "CT2", "GT2"), (12, 912, 1, None, "ST1"),
        (13, 913, 1, "B7", "G7"), (13, 913, 1, "CT9", "CT9"), (13, 913, 1, None, "ST9"),
        (14, 914, 1, "B4", "G4"),
        (15, 915, 1, "U5", "G5"), (15, 915, 1, "U6", "G5"),
        (16, 916, 1, "U8", "G8"),
    ], columns=sg.COLUMNS["sp"])
    bga = pd.DataFrame([
        (10, D, "ST1", "CT-1"), (10, D, "ST1", "CT-2"),
        (11, D, "G1", "B1"),
        (12, D, "ST1", "HRSG1"), (12, D, "ST1", "HRSG2"),
        (13, D, "G7", "B7"), (13, D, "ST9", "HR9X"),
        (14, D, "G4", "B4"), (14, D, "G4", "AUX"),
        (15, D, "G5", "B5"),
        (16, D, "G8", "B8"), (16, D, "G8", "B8X"),
    ], columns=sg.COLUMNS["bga"])
    heat = {(10, "CT-1"): 100, (10, "CT-2"): 200, (11, "B1"): 50, (12, "HRSG1"): 10,
            (12, "HRSG2"): 10, (13, "B7"): 30, (13, "HR9X"): 40, (14, "B4"): 90, (14, "AUX"): 10,
            (15, "B5"): 20, (16, "B8"): 10, (16, "B8X"): 30}
    bf = pd.DataFrame([(p, b, "NG", D, float(v), 1.0) for (p, b), v in heat.items()],
                      columns=sg.COLUMNS["bf"])
    return xw, sp, bga, bf


class NormTests(unittest.TestCase):
    def test_norm(self):
        self.assertEqual(sa.norm("CT-1"), "CT1")
        self.assertEqual(sa.norm("ct 01"), "CT01")
        self.assertEqual(sa.norm("01"), "1")
        self.assertEqual(sa.norm("0"), "0")
        self.assertNotEqual(sa.norm("HRSG1"), sa.norm("CT1"))


class ClassifyTests(unittest.TestCase):
    def setUp(self):
        self.xw, self.sp, self.bga, self.bf = frames()
        self.rows, self.outside = sa.classify(self.xw, self.sp, self.bga, 2024)
        self.b, _ = sg.find_gaps(self.xw, self.sp, self.bga, self.bf, 2024)
        self.subs = sg.subplant_table(self.b)
        self.b2 = sa.revise(self.b, self.rows)
        self.subs2 = sg.subplant_table(self.b2)

    def row(self, plant, gen):
        r = self.rows[(self.rows["plant_id_eia"] == plant) & (self.rows["generator_id"] == gen)]
        self.assertEqual(len(r), 1, (plant, gen))
        return r.iloc[0]

    def test_classes(self):
        want = {(10, "CT1"): ("name", "CT-1", "subplant"), (10, "CT2"): ("name", "CT-2", "subplant"),
                (11, "G1"): ("single", "B1", "generator"),
                (12, "GT1"): ("unresolved", None, "subplant"),
                (12, "GT2"): ("unresolved", None, "subplant"),
                (13, "CT9"): ("single", "HR9X", "subplant"),
                (14, "G4"): ("name", "B4", "generator"), (15, "G5"): ("covered", None, "generator")}
        self.assertEqual(len(self.rows), len(want))
        self.assertEqual(self.outside, 0)
        for (plant, gen), (cls, boiler, source) in want.items():
            r = self.row(plant, gen)
            self.assertEqual(r["class"], cls, (plant, gen))
            self.assertEqual(r["boiler_id"], boiler, (plant, gen))
            self.assertEqual(r["source"], source, (plant, gen))

    def test_matched_boiler_is_not_a_candidate(self):
        self.assertEqual(self.row(13, "CT9")["candidates"], "HR9X")
        self.assertEqual(self.row(15, "G5")["candidates"], "")

    def test_revise(self):
        orig = sg.summarize(self.b, self.subs, self.xw, self.sp, 2024)
        self.assertEqual(orig["ambiguous_subplants"], 6)
        self.assertEqual(orig["strict"]["gap_plants"], 1)  # plant 16 only
        rev = sg.summarize(self.b2, self.subs2, self.xw, self.sp, 2024)
        self.assertEqual(rev["ambiguous_subplants"], 1)  # plant 12
        self.assertEqual(rev["strict"]["gap_plants"], 2)  # 14 (AUX) and 16 (B8X)
        self.assertEqual(rev["strict"]["gap_mmbtu"], 40.0)
        b2 = self.b2.set_index(["plant_id_eia", "boiler_id"])
        self.assertTrue(b2.loc[(10, "CT-1"), "inferred"])
        self.assertFalse(b2.loc[(14, "AUX"), "covered"])
        self.assertTrue(b2.loc[(12, "HRSG1"), "gap"])
        self.assertTrue(b2.loc[(12, "HRSG1"), "ambiguous"])

    def test_metrics_and_score(self):
        m = sa.metrics(self.rows, self.subs, self.subs2)
        self.assertEqual(m["rows"], 8)
        self.assertEqual(m["rows_by_class"], {"covered": 1, "single": 2, "name": 3, "unresolved": 2})
        self.assertEqual(m["rows_generator_without_boiler"], 5)
        self.assertEqual(m["ambiguous_subplants"], 6)
        self.assertEqual(m["ambiguous_subplants_with_a_row"], 6)
        self.assertEqual(m["resolved_subplants"], 5)
        self.assertEqual(m["resolved_linked_mmbtu"], 540.0)
        self.assertEqual(m["resolved_gap_mmbtu"], 10.0)
        self.assertEqual(m["resolved_gap_plants"], 1)
        got = sa.score(True, True, m)
        # P1 5*2 >= 6; P2 5 >= 4.8; P3 10 < 5.4 fails; P4 3 < 100
        self.assertEqual([got[k] for k in ("P1", "P2", "P3", "P4")], [True, True, False, False])

    def test_gate(self):
        self.assertTrue(sa.gate_g1({"ambiguous_subplants": 602, "strict": {"gap_plants": 8}}))
        self.assertFalse(sa.gate_g1({"ambiguous_subplants": 626, "strict": {"gap_plants": 8}}))
        self.assertFalse(sa.gate_g1({"ambiguous_subplants": 602, "strict": {"gap_plants": 11}}))


if __name__ == "__main__":
    unittest.main()
