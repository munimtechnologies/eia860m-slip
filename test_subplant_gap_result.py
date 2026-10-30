"""Checks that docs/subplant-gap.md scores the gates and four predictions of
docs/subplant-gap-plan.md with the counts job subplant-gap-v1 wrote. Reads text only, so it
needs no pandas.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))

# Copied from compete-results/subplant-gap-v1/out/subplant_gap.json, "strict" counts:
# cems_subplants_with_boilers, ambiguous_subplants, gap_boilers, gap_plants, gap_mmbtu,
# total_mmbtu_linked_boilers, subplants_gap_share_over_half, ..._not_msw.
YEARS = {
    2018: (1017, 617, 32, 11, 47402332.427, 13232322523.148, 6, 5),
    2019: (960, 619, 31, 11, 44365909.048, 11365469351.839, 6, 5),
    2020: (896, 613, 31, 11, 40638672.528, 9451421648.459, 6, 5),
    2021: (845, 617, 28, 8, 38340029.78500001, 10664400443.04, 5, 4),
    2022: (803, 608, 27, 8, 37554813.914000005, 10274305626.167, 4, 3),
    2023: (786, 605, 28, 9, 38416704.053, 8819652277.315, 4, 3),
    2024: (726, 602, 27, 8, 39280974.865, 8728545044.085, 5, 4),
}
G1_MMBTU = 8179710.879000001
# Copied from out/subplants_2024.csv, rows with ambiguous False and gap_boilers > 0.
SUBPLANTS_2024 = [
    (992, 1, 8, 2, 2798368.81, 214611.39, "NG"),
    (2098, 1, 7, 5, 3814082.122, 3281522.57, "NG"),
    (10252, 1, 2, 1, 4610764.4969999995, 1962943.1439999999, "WDS"),
    (10328, 1, 5, 1, 4299994.426, 47316.123, "NG"),
    (50472, 1, 4, 2, 8278041.641999999, 8125256.641999999, "MSN"),
    (50481, 1, 10, 8, 9755948.512, 4962355.806, "BIT"),
    (50481, 2, 5, 1, 21103185.900000002, 4537193.2, "NG"),
    (52193, 4, 6, 4, 9034669.28, 6408953.2, "OG"),
    (54216, 5, 7, 3, 9740822.790000001, 9740822.790000001, "BLQ"),
]


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class SubplantGapResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/subplant-gap.md")
        cls.plan = read("docs/subplant-gap-plan.md")

    def test_scores_follow_the_bars(self):
        s = YEARS[2024]
        scores = (s[3] >= 20, s[4] >= 25_000_000, s[6] >= 10, s[7] >= 3)
        self.assertEqual(scores, (False, True, False, True))
        self.assertTrue(7_000_000 <= G1_MMBTU <= 9_500_000)
        self.assertIn("Both gates held and 2 of 4 predictions held; P1 and P3 missed.", self.doc)
        for text in (
                "held: 8,179,711 MMBtu |",
                "| P1 (75%) | at least 20 plants have a gap boiler in 2024 | **missed**: 8 plants |",
                "| P2 (70%) | gap boilers burn at least 25 million MMBtu in 2024 | held: "
                "{:,.0f} MMBtu |".format(s[4]),
                "| P3 (60%) | at least 10 strict CEMS subplants have a gap share above 50% | "
                "**missed**: 5 subplants |",
                "| P4 (70%) | at least 3 of P3's subplants have a largest gap boiler not burning "
                "mainly MSW | held: 4 of the 5 |"):
            self.assertIn(text, self.doc)
        for text in ("Pre-registration id: subplant-gap-1.", "**P1 (75%):**", "**P2 (70%):**",
                     "**P3 (60%):**", "**P4 (70%):**", "at least 20 plants",
                     "at least 25 million MMBtu", "at least 10 strict CEMS subplants",
                     "at least 3 have a largest gap boiler"):
            self.assertIn(text, self.plan)

    def test_year_rows(self):
        for year, (sub, amb, gb, gp, gap, linked, half, non_msw) in YEARS.items():
            row = "| {} | {:,} | {:,} | {} | {} | {:,.1f} | {:,.1f} | {:.2f}% | {} | {} |".format(
                year, sub, amb, gb, gp, gap / 1e6, linked / 1e6, 100.0 * gap / linked, half,
                non_msw)
            self.assertIn(row, self.doc)

    def test_subplant_rows(self):
        gap_total = 0.0
        for plant, sub, n, gaps, total, gap, fuel in SUBPLANTS_2024:
            row = "| {} | {} | {} | {} | {:,.0f} | {:,.0f} | {:.1f}% | {} |".format(
                plant, sub, n, gaps, total, gap, 100.0 * gap / total, fuel)
            self.assertIn(row, self.doc)
            gap_total += gap
        self.assertAlmostEqual(gap_total, YEARS[2024][4], places=2)
        self.assertEqual(sum(r[3] for r in SUBPLANTS_2024), YEARS[2024][2])
        self.assertEqual(len({r[0] for r in SUBPLANTS_2024}), YEARS[2024][3])
        over_half = [r for r in SUBPLANTS_2024 if r[5] / r[4] > 0.5]
        self.assertEqual(len(over_half), YEARS[2024][6])
        self.assertEqual(len([r for r in over_half if r[6] not in ("MSW", "MSB", "MSN")]),
                         YEARS[2024][7])

    def test_ambiguous_share(self):
        s = YEARS[2024]
        self.assertEqual(s[0] + s[1], 1328)
        self.assertIn("602 of the 1,328 CEMS subplants with linked boilers in 2024 (%d%%)"
                      % round(100.0 * s[1] / (s[0] + s[1])), self.doc)

    def test_no_data_stored(self):
        self.assertIn("PUDL's data (CC BY 4.0) was downloaded at run time and is not stored "
                      "here.", self.doc)


if __name__ == "__main__":
    unittest.main()
