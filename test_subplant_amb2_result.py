"""Checks that docs/subplant-amb2.md scores the gates and four predictions of
docs/subplant-amb2-plan.md with the counts job subplant-amb2-v1 wrote. Reads text only, so it
needs no pandas.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))

# Copied from compete-results/subplant-amb2-v1/out/subplant_amb2.json, by_year.*.rules:
# covered, single, name, unit, unresolved, unresolved_rule1, ambiguous_subplants,
# ambiguous_after_rule1, ambiguous_after_rule2, resolved_by_rule2, rule2_linked_mmbtu,
# rule2_gap_mmbtu, rule2_gap_hrsg_mmbtu.
YEARS = {
    2018: (67, 179, 956, 313, 146, 459, 617, 172, 36, 136, 2143718131.589,
           109727258.12200001, 53066502.666),
    2019: (67, 176, 967, 313, 146, 459, 619, 172, 36, 136, 2270620162.638,
           118470953.75999999, 67465143.518),
    2020: (67, 169, 961, 311, 140, 451, 613, 171, 35, 136, 2342245242.7809997,
           115872038.46499999, 74617194.70199999),
    2021: (70, 174, 963, 316, 144, 460, 617, 173, 36, 137, 2314681817.251,
           100567552.64199999, 56641123.482),
    2022: (68, 171, 965, 311, 130, 441, 608, 164, 31, 133, 2374883348.3809996,
           126454914.61500001, 71793864.65499999),
    2023: (68, 170, 963, 307, 128, 435, 605, 161, 30, 131, 2420538390.293,
           126546167.097, 66921392.096),
    2024: (68, 170, 958, 307, 128, 435, 602, 160, 30, 130, 2431598896.5480003,
           131347693.28400001, 72414595.125),
}
RULE2_GAP_PLANTS_2024 = 64
# by_year."2024".revised.strict: subplants with boilers, gap boilers, gap plants, gap, linked.
STRICT_2024 = (1298, 190, 97, 202183890.927, 18807053117.358)
# subplant-amb-1's published 2024 strict count after the first rule (docs/subplant-amb.md).
RULE1_STRICT_2024 = (1168, 78, 33, 70836197.643, 16375454220.810001)
# top_rule2_gap_subplants, first ten: plant, subplant, boilers, gap boilers, total_mmbtu,
# gap_mmbtu, gap_top_fuel, gap_boiler_ids.
TOP_2024 = [
    (58215, 1, 4, 1, 47100023.324, 11041724.659, "NG", "ST1"),
    (59326, 1, 2, 1, 25125425.436, 7998410.915, "NG", "HRSG"),
    (1912, 3, 3, 1, 20345514.792000003, 7913689.318000001, "NG", "9"),
    (7845, 1, 3, 1, 23556039.0, 7875516.0, "NG", "HRSG"),
    (50397, 1, 7, 1, 10148381.74, 6591453.92, "BLQ", "REC037"),
    (55470, 1, 6, 3, 46130505.052, 5265097.96, "OG", "HRSG3;HRSG2;HRSG1"),
    (3264, 9, 4, 1, 40163798.331999995, 5245555.679, "NG", "HRSG1"),
    (50006, 1, 12, 5, 53580962.640999995, 5164942.118, "NG", "HRSG5;HRSG4;HRSG1;HRSG3;HRSG2"),
    (55736, 3, 4, 2, 33249199.028999995, 5145519.744, "NG", "2HR2;2HR1"),
    (2723, 11, 4, 1, 32878976.341999996, 4947599.153, "NG", "HRSG1"),
]


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class SubplantAmb2ResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/subplant-amb2.md")
        cls.plan = read("docs/subplant-amb2-plan.md")

    def test_scores_follow_the_bars(self):
        y = YEARS[2024]
        unit, unres1, amb, amb1, amb2 = y[3], y[5], y[6], y[7], y[8]
        linked, gap, hrsg = y[10], y[11], y[12]
        g1 = 400 <= unres1 <= 470 and 420 <= amb - amb1 <= 465
        scores = (unit * 2 >= unres1, amb2 <= 100, gap < 0.10 * linked, hrsg * 2 >= gap)
        self.assertTrue(g1)
        self.assertEqual(scores, (True, True, True, True))
        self.assertIn("Both gates held and 4 of 4 predictions held.", self.doc)
        for text in (
                "| held: %d and %d |" % (unres1, amb - amb1),
                "| held: %d of %d (%.1f%%) |" % (unit, unres1, 100.0 * unit / unres1),
                "| held: %d |" % amb2,
                "| held: {:,.0f} of {:,.0f} MMBtu ({:.2f}%) |".format(gap, linked,
                                                                     100.0 * gap / linked),
                "| held: {:,.0f} of {:,.0f} MMBtu ({:.1f}%) |".format(hrsg, gap,
                                                                     100.0 * hrsg / gap)):
            self.assertIn(text, self.doc)
        for text in ("Pre-registration id: subplant-amb-2.", "**Q1 (60%):**", "**Q2 (55%):**",
                     "**Q3 (60%):**", "**Q4 (55%):**", "between 400 and 470 unresolved rows",
                     "between 420 and 465 resolved subplants"):
            self.assertIn(text, self.plan)

    def test_class_table(self):
        y = YEARS[2024]
        rows = sum(y[0:5])
        self.assertEqual(rows, 1631)
        self.assertEqual(y[3] + y[4], y[5])
        for n in y[0:5]:
            self.assertIn("| %d | %.1f%% |" % (n, 100.0 * n / rows), self.doc)
        self.assertIn("| {:,} | |".format(rows), self.doc)
        named = y[1] + y[2]
        self.assertIn("Only the single and name classes name a boiler ({:,} rows).".format(named),
                      self.doc)
        self.assertIn("{:,} ({:.1f}%) can be given a `boiler_id`".format(
            named, 100.0 * named / rows), self.doc)
        self.assertIn("%d (%.1f%%) are redundant" % (y[3], 100.0 * y[3] / rows), self.doc)
        self.assertIn("%d (%.1f%%) stay unknown" % (y[4], 100.0 * y[4] / rows), self.doc)
        self.assertIn("That leaves %d of the %d ambiguous subplants (%.1f%%)"
                      % (y[8], y[6], 100.0 * y[8] / y[6]), self.doc)

    def test_year_rows(self):
        shares = []
        for year, (cov, single, name, unit, unres, unres1, amb, amb1, amb2, new, linked, gap,
                   hrsg) in YEARS.items():
            self.assertEqual(unit + unres, unres1)
            self.assertEqual(amb1 - amb2, new)
            row = ("| {} | {} | {} ({:.1f}%) | {} | {} | {} | {} | {} | {:,.1f} | {:,.1f} | "
                   "{:.2f}% | {:.1f}% |").format(year, unres1, unit, 100.0 * unit / unres1, unres,
                                                 amb, amb1, amb2, new, linked / 1e6, gap / 1e6,
                                                 100.0 * gap / linked, 100.0 * hrsg / gap)
            self.assertIn(row, self.doc)
            shares.append(100.0 * (amb - amb2) / amb)
        self.assertIn("between %.1f%% and %.1f%% of the ambiguous subplants are resolved in "
                      "every year" % (min(shares), max(shares)), self.doc)
        y18 = YEARS[2018]
        self.assertLess(y18[12] * 2, y18[11])
        self.assertIn("below half only in 2018 (%.1f%%)" % (100.0 * y18[12] / y18[11]), self.doc)

    def test_strict_counts(self):
        subs, boilers, plants, gap, linked = STRICT_2024
        r_subs, r_boilers, r_plants, r_gap, r_linked = RULE1_STRICT_2024
        y = YEARS[2024]
        self.assertEqual(subs - r_subs, y[9])
        self.assertAlmostEqual(gap - r_gap, y[11], places=2)
        self.assertAlmostEqual(linked - r_linked, y[10], places=2)
        self.assertEqual(plants - r_plants, RULE2_GAP_PLANTS_2024)
        for s, b, p, g, lk in (STRICT_2024, RULE1_STRICT_2024):
            self.assertIn("| {:,} | {} | {} | {:,.0f} | {:.2f}% |".format(
                s, b, p, g, 100.0 * g / lk), self.doc)
        self.assertIn("The %d newly resolved subplants add %d gap boilers at %d plants."
                      % (y[9], boilers - r_boilers, RULE2_GAP_PLANTS_2024), self.doc)

    def test_top_subplants(self):
        for plant, sub, n, gaps, total, gap, fuel, ids in TOP_2024:
            row = "| {} | {} | {} | {} | {:,.0f} | {:,.0f} | {:.1f}% | {} | {} |".format(
                plant, sub, n, gaps, total, gap, 100.0 * gap / total, fuel,
                ids.replace(";", "; "))
            self.assertIn(row, self.doc)
        gaps = [r[5] for r in TOP_2024]
        self.assertEqual(gaps, sorted(gaps, reverse=True))

    def test_disclosure(self):
        self.assertIn("PUDL's data (CC BY 4.0) was downloaded at run time and is not stored "
                      "here.", self.doc)
        self.assertIn("made with AI agents working in MV2's name", self.doc)
        self.assertIn("an upper bound on fuel burned outside CEMS", self.doc)


if __name__ == "__main__":
    unittest.main()
