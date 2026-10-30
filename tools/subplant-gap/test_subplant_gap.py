"""Unit tests for subplant_gap.py on small hand-made frames (no network, no PUDL data).

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.)."""

import unittest

import pandas as pd

import subplant_gap as sg

D = pd.Timestamp("2023-01-01")


def frames():
    xw = pd.DataFrame([
        # plant 50472: two EPA units matched to BLR1/BLR2 only (the issue #5681 pattern)
        (2023, 9001, "R1B01", 50472, "BLR1", "GEN1"),
        (2023, 9001, "R1B02", 50472, "BLR2", "GEN2"),
        # plant 2: unit matched to a generator with no boiler (ambiguous)
        (2023, 9002, "U9", 2, None, "G9"),
        # plant 3: matched only in 2022, so not a CEMS subplant in 2023
        (2022, 9003, "U5", 3, "B5", "G5"),
        # plant 4: one covered boiler, one boiler that burned nothing
        (2023, 9004, "U7", 4, "B7", "G7"),
        # plant 5: gap boiler that was matched in another year
        (2023, 9005, "U1", 5, "B1", "G1"),
        (2021, 9005, "U2", 5, "B2", "G1"),
    ], columns=sg.COLUMNS["xw"])
    sp = pd.DataFrame([
        (50472, 9001, 1, "R1B01", "GEN1"),
        (50472, 9001, 1, "R1B02", "GEN2"),
        (50472, 9001, 2, "BLR05", None),
        (2, 9002, 1, "U9", "G9"),
        (3, 9003, 1, "U5", "G5"),
        (4, 9004, 1, "U7", "G7"),
        (5, 9005, 1, "U1", "G1"),
    ], columns=sg.COLUMNS["sp"])
    bga = pd.DataFrame([
        (50472, D, "GEN1", "BLR1"), (50472, D, "GEN1", "BLR3"),
        (50472, D, "GEN2", "BLR2"), (50472, D, "GEN2", "BLR4"),
        (2, D, "G9", "B9"), (3, D, "G5", "B5"),
        (4, D, "G7", "B7"), (4, D, "G7", "B8"),
        (5, D, "G1", "B1"), (5, D, "G1", "B2"),
    ], columns=sg.COLUMNS["bga"])
    bf = pd.DataFrame([
        (50472, "BLR1", "NG", D, 100.0, 1.0),
        (50472, "BLR2", "NG", D, 100.0, 1.0),
        (50472, "BLR3", "MSW", D, 300_000.0, 10.0),
        (50472, "BLR3", None, D, 100_000.0, 10.0),
        (50472, "BLR4", "MSW", D, 410_000.0, 10.0),
        (2, "B9", "NG", D, 50.0, 1.0),
        (3, "B5", "NG", D, 10.0, 1.0),
        (4, "B7", "NG", D, 10.0, 1.0),
        (4, "B8", "NG", D, 0.0, 1.0),
        (5, "B1", "BIT", D, 10.0, 20.0),
        (5, "B2", "WDS", D, 30.0, 10.0),
    ], columns=sg.COLUMNS["bf"])
    return xw, sp, bga, bf


class FindGapsTests(unittest.TestCase):
    def setUp(self):
        self.xw, self.sp, self.bga, self.bf = frames()
        self.b, self.n_cems = sg.find_gaps(self.xw, self.sp, self.bga, self.bf, 2023)

    def row(self, plant, boiler):
        r = self.b[(self.b["plant_id_eia"] == plant) & (self.b["boiler_id"] == boiler)]
        self.assertEqual(len(r), 1, (plant, boiler))
        return r.iloc[0]

    def test_cems_subplants(self):
        # 50472/1, 2/1, 4/1, 5/1; plant 3 is matched only in 2022
        self.assertEqual(self.n_cems, 4)
        self.assertNotIn(3, set(self.b["plant_id_eia"]))

    def test_issue_5681_pattern(self):
        for boiler in ("BLR1", "BLR2"):
            self.assertTrue(self.row(50472, boiler)["covered"])
            self.assertFalse(self.row(50472, boiler)["gap"])
        for boiler in ("BLR3", "BLR4"):
            self.assertTrue(self.row(50472, boiler)["gap"])
        self.assertEqual(self.row(50472, "BLR3")["mmbtu"], 4_000_000.0)
        self.assertEqual(self.row(50472, "BLR3")["top_fuel"], "MSW")

    def test_zero_heat_is_not_a_gap(self):
        self.assertFalse(self.row(4, "B8")["covered"])
        self.assertFalse(self.row(4, "B8")["gap"])

    def test_ambiguous(self):
        self.assertTrue(self.row(2, "B9")["ambiguous"])
        self.assertTrue(self.row(2, "B9")["gap"])
        self.assertFalse(self.row(50472, "BLR3")["ambiguous"])

    def test_subplants_and_summary(self):
        subs = sg.subplant_table(self.b)
        s = subs[(subs["plant_id_eia"] == 50472) & (subs["subplant_id"] == 1)].iloc[0]
        self.assertEqual(s["gap_boilers"], 2)
        self.assertAlmostEqual(s["gap_share"], 8_100_000 / 8_100_200)
        self.assertEqual(s["gap_boiler_ids"], "BLR4;BLR3")
        summ = sg.summarize(self.b, subs, self.xw, self.sp, 2023)
        strict, every = summ["strict"], summ["all"]
        self.assertEqual(strict["gap_plants"], 2)  # 50472 and 5
        self.assertEqual(strict["gap_boilers"], 3)  # BLR3, BLR4, plant 5's B2
        self.assertEqual(strict["gap_mmbtu"], 8_100_300.0)
        self.assertEqual(every["gap_plants"], 3)
        self.assertEqual(strict["subplants_gap_share_over_half"], 2)  # 50472/1 and 5/1 (300/500)
        self.assertEqual(strict["subplants_gap_share_over_half_not_msw"], 1)  # 5/1, WDS
        self.assertEqual(strict["gap_boilers_matched_in_another_year"], 1)  # plant 5's B2 in 2021
        self.assertEqual(strict["gap_plants_with_an_unmatched_epa_unit"], 1)  # 50472's BLR05
        self.assertEqual(summ["ambiguous_subplants"], 1)

    def test_gate(self):
        g = sg.gate_g1(self.b)
        self.assertTrue(g["held"])
        self.assertEqual(g["gap_mmbtu"], 8_100_000.0)
        bga = self.bga[self.bga["boiler_id"] != "BLR4"]
        b, _ = sg.find_gaps(self.xw, self.sp, bga, self.bf, 2023)
        self.assertFalse(sg.gate_g1(b)["held"])

    def test_choose_years(self):
        months = pd.date_range("2023-01-01", periods=12, freq="MS")
        bf = pd.concat([self.bf.assign(report_date=m) for m in months]
                       + [self.bf.assign(report_date=pd.Timestamp("2024-01-01"))])
        years, main = sg.choose_years(self.xw, self.bga, bf)
        self.assertEqual(years, [2023])
        self.assertEqual(main, 2023)

    def test_score(self):
        s = {"strict": {"gap_plants": 20, "gap_mmbtu": 25_000_000.0,
                        "subplants_gap_share_over_half": 9,
                        "subplants_gap_share_over_half_not_msw": 3}}
        got = sg.score(True, True, s)
        self.assertEqual([got[k] for k in ("P1", "P2", "P3", "P4")], [True, True, False, True])


if __name__ == "__main__":
    unittest.main()
