"""Checks that docs/subplant-amb.md scores the gates and four predictions of
docs/subplant-amb-plan.md with the counts job subplant-amb-v1 wrote. Reads text only, so it
needs no pandas.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))

# Copied from compete-results/subplant-amb-v1/out/subplant_amb.json, by_year:
# rule rows, covered, single, name, unresolved, ambiguous_subplants, resolved_subplants;
# subplant_gap strict gap_plants and gap_mmbtu; revised strict gap_plants, gap_mmbtu and
# total_mmbtu_linked_boilers.
YEARS = {
    2018: (1661, 67, 179, 956, 459, 617, 445, 11, 47402332.427, 33, 74814115.369,
           19843647411.253998),
    2019: (1669, 67, 176, 967, 459, 619, 447, 11, 44365909.048, 35, 64762720.819,
           18451285326.841003),
    2020: (1648, 67, 169, 961, 451, 613, 442, 11, 40638672.528, 36, 64973976.20799999,
           16569894698.579002),
    2021: (1667, 70, 174, 963, 460, 617, 444, 8, 38340029.78500001, 30, 55261195.967,
           17518217942.666),
    2022: (1645, 68, 171, 965, 441, 608, 444, 8, 37554813.914000005, 33, 63062825.492000006,
           17471452668.483),
    2023: (1636, 68, 170, 963, 435, 605, 444, 9, 38416704.053, 31, 68148571.268,
           16380499071.607002),
    2024: (1631, 68, 170, 958, 435, 602, 442, 8, 39280974.865, 33, 70836197.643,
           16375454220.810001),
}
ROWS_GENERATOR_WITHOUT_BOILER_2024 = 35
RESOLVED_LINKED_2024 = 7646909176.724999
RESOLVED_GAP_2024 = 31555222.777999997
RESOLVED_GAP_PLANTS_2024 = 25
# Copied from top_revised_gap_subplants, the rows not among subplant-gap-1's 9 strict ones:
# plant, subplant, boilers, gap boilers, total_mmbtu, gap_mmbtu, gap_top_fuel.
ADDED_2024 = [
    (55259, 1, 4, 2, 26491699.303999998, 5394553.432, "NG"),
    (60589, 1, 4, 2, 49687564.309, 3859926.023, "NG"),
    (628, 4, 4, 1, 41689287.85299999, 2176118.26, "NG"),
    (55518, 1, 6, 3, 33496671.446000002, 2039136.253, "NG"),
    (628, 2, 4, 1, 41719448.721, 2009884.117, "NG"),
    (55089, 1, 6, 3, 37574960.536, 1998844.9960000003, "OG"),
    (2406, 4, 4, 2, 19532179.994999997, 1871500.687, "NG"),
    (8031, 1, 4, 2, 18544932.753, 1664153.9579999999, "NG"),
    (1403, 5, 4, 2, 26050562.019999996, 1270194.284, "NG"),
    (56349, 2, 4, 2, 13245692.623, 1191695.2489999998, "NG"),
    (55933, 1, 4, 2, 8425893.625, 1145120.151, "NG"),
    (54537, 1, 4, 2, 14227549.019, 1078619.7880000002, "NG"),
    (55418, 1, 4, 2, 15100855.737999998, 856046.4820000001, "NG"),
    (2070, 1, 3, 1, 7135467.973, 788499.599, "NG"),
    (56349, 1, 4, 2, 12838119.446, 765570.948, "NG"),
    (1391, 1, 6, 1, 14309842.601000002, 612184.861, "OG"),
    (2070, 2, 3, 1, 6365955.217999999, 573464.691, "NG"),
    (7242, 2, 10, 1, 42549130.147999994, 519742.276, "NG"),
    (2406, 2, 4, 2, 15737754.917, 515017.3609999999, "NG"),
    (55137, 1, 6, 3, 35917611.118, 354466.082, "NG"),
    (55271, 1, 6, 2, 12892190.410999998, 336668.403, "NG"),
    (55270, 1, 14, 1, 17102928.064, 234195.804, "NG"),
    (55177, 1, 4, 2, 21680255.724999998, 90034.424, "NG"),
    (56350, 2, 4, 2, 10927328.112999998, 77873.16, "NG"),
    (56046, 1, 2, 1, 11718874.773, 60919.922, "NG"),
    (56350, 1, 4, 2, 9229391.367999997, 58459.081999999995, "NG"),
    (7784, 1, 2, 1, 128192.48, 10537.28, "NG"),
    (7546, 1, 2, 1, 105610.05, 1089.9, "NG"),
    (7238, 3, 2, 1, 10832541.968, 401.887, "NG"),
    (55406, 1, 5, 1, 11813782.644, 303.418, "NG"),
]
STRICT_GAP_BOILERS_2024 = (27, 78)  # subplant-gap-1, then revised


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class SubplantAmbResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/subplant-amb.md")
        cls.plan = read("docs/subplant-amb-plan.md")

    def test_scores_follow_the_bars(self):
        y = YEARS[2024]
        g1 = 580 <= y[5] <= 625 and 6 <= y[7] <= 10
        scores = (y[6] * 2 >= y[5], ROWS_GENERATOR_WITHOUT_BOILER_2024 >= 0.6 * y[0],
                  RESOLVED_GAP_2024 < 0.01 * RESOLVED_LINKED_2024, y[3] >= 100)
        self.assertTrue(g1)
        self.assertEqual(scores, (True, False, True, True))
        self.assertIn("Both gates held and 3 of 4 predictions held; P2 missed.", self.doc)
        for text in (
                "| held: %d and %d |" % (y[5], y[7]),
                "| held: %d of %d (%.1f%%) |" % (y[6], y[5], 100.0 * y[6] / y[5]),
                "| **missed**: {} of {:,} ({:.1f}%) |".format(
                    ROWS_GENERATOR_WITHOUT_BOILER_2024, y[0],
                    100.0 * ROWS_GENERATOR_WITHOUT_BOILER_2024 / y[0]),
                "| held: {:,.0f} of {:,.0f} MMBtu ({:.2f}%) |".format(
                    RESOLVED_GAP_2024, RESOLVED_LINKED_2024,
                    100.0 * RESOLVED_GAP_2024 / RESOLVED_LINKED_2024),
                "| held: %d rows |" % y[3]):
            self.assertIn(text, self.doc)
        for text in ("Pre-registration id: subplant-amb-1.", "**P1 (60%):**", "**P2 (65%):**",
                     "**P3 (55%):**", "**P4 (50%):**", "between 580 and 625 ambiguous subplants",
                     "between 6 and 10 strict gap plants"):
            self.assertIn(text, self.plan)

    def test_class_table(self):
        y = YEARS[2024]
        self.assertEqual(sum(y[1:5]), y[0])
        for n in y[1:5]:
            self.assertIn("| %d | %.1f%% |" % (n, 100.0 * n / y[0]), self.doc)
        self.assertIn("| {:,} | |".format(y[0]), self.doc)
        with_boiler = y[0] - ROWS_GENERATOR_WITHOUT_BOILER_2024
        self.assertIn("{:,} of the {:,} ambiguous rows ({:.1f}%)".format(
            with_boiler, y[0], 100.0 * with_boiler / y[0]), self.doc)
        named = y[2] + y[3]
        self.assertIn("{:,} of the {:,} ambiguous rows of 2024 ({:.1f}%; single {}, name {})"
                      .format(named, y[0], 100.0 * named / y[0], y[2], y[3]), self.doc)

    def test_year_rows(self):
        shares = []
        for year, (rows, cov, single, name, unres, amb, res, gp0, g0, gp1, g1, lk) in \
                YEARS.items():
            self.assertEqual(cov + single + name + unres, rows)
            row = ("| {} | {:,} | {} | {} | {} | {} | {} | {} | {} | {} | {:,.1f} | {:,.1f} | "
                   "{:,.1f} | {:.2f}% |").format(year, rows, cov, single, name, unres, amb, res,
                                                 gp0, gp1, g0 / 1e6, g1 / 1e6, lk / 1e6,
                                                 100.0 * g1 / lk)
            self.assertIn(row, self.doc)
            shares.append(100.0 * res / amb)
        self.assertIn("between %.1f%% and %.1f%% of the ambiguous subplants in every year"
                      % (min(shares), max(shares)), self.doc)

    def test_added_subplants(self):
        gap_total = 0.0
        for plant, sub, n, gaps, total, gap, fuel in ADDED_2024:
            row = "| {} | {} | {} | {} | {:,.0f} | {:,.0f} | {:.1f}% | {} |".format(
                plant, sub, n, gaps, total, gap, 100.0 * gap / total, fuel)
            self.assertIn(row, self.doc)
            gap_total += gap
        self.assertAlmostEqual(gap_total, RESOLVED_GAP_2024, places=2)
        self.assertAlmostEqual(gap_total, YEARS[2024][10] - YEARS[2024][8], places=2)
        boilers = sum(r[3] for r in ADDED_2024)
        self.assertEqual(boilers, STRICT_GAP_BOILERS_2024[1] - STRICT_GAP_BOILERS_2024[0])
        plants = len({r[0] for r in ADDED_2024})
        self.assertEqual(plants, RESOLVED_GAP_PLANTS_2024)
        self.assertEqual(plants + YEARS[2024][7], YEARS[2024][9])
        self.assertIn("These %d subplants at %d plants hold the %d gap boilers and {:,.0f} MMBtu"
                      .format(RESOLVED_GAP_2024) % (len(ADDED_2024), plants, boilers), self.doc)
        top = max(100.0 * r[5] / r[4] for r in ADDED_2024)
        self.assertLess(top, 50.0)
        self.assertIn("the largest is %.1f%%" % top, self.doc)

    def test_no_data_stored(self):
        self.assertIn("PUDL's data (CC BY 4.0) was downloaded at run time and is not stored "
                      "here.", self.doc)
        self.assertIn("made with AI agents working in MV2's name", self.doc)


if __name__ == "__main__":
    unittest.main()
