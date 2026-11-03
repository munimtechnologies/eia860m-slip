"""Checks that docs/xwcap.md scores Gates G1-G3 and P1-P5 of docs/xwcap-plan.md
(pre-registration xwcap-1) with the counts job xwcap-v1 wrote, using the plan's own thresholds,
and reports the failed bars as failed. Reads text only, so it needs no polars.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))

# Copied from compete-results/xwcap-v1/out/xwcap_check.json.
YEAR = 2024
G1 = {"missing_cols": [], "ops_rows": 118117}
MAIN = {"groups": 4060, "study": 3030, "over": 29, "over_2x": 17, "under": 10,
        "median_ratio": 0.9872137666255314, "over_by_class": {"cc": 10, "candidate": 0,
                                                              "other": 19},
        "over_units": 39, "single_pair_study": 2324, "links": 6328}
QUANTILES = {"0.1": 0.7933884297520661, "0.25": 0.8909090909090909, "0.5": 0.9871794871794872,
             "0.75": 1.050420168067227, "0.9": 1.1098265895953756, "0.99": 1.492822966507177}
PLANT_CHECK = {"plant": 57865, "groups": 3, "study": 3, "over": 3, "candidate": 0}
PERSISTENCE = {"over_units": 39, "in_prev_study": 39, "also_over_prev": 34}
BY_YEAR = {
    2018: (4137, 3378, 25, 14, 13, 0.9829059829059829, 7, 0, 18),
    2019: (4134, 3226, 25, 14, 8, 0.9847198641765705, 7, 0, 18),
    2020: (4122, 3190, 30, 17, 13, 0.9847841745125276, 11, 0, 19),
    2021: (4103, 3136, 29, 16, 13, 0.9850298059253283, 11, 1, 17),
    2022: (4111, 3093, 29, 15, 10, 0.9878048780487805, 10, 1, 18),
    2023: (4072, 3051, 28, 16, 8, 0.989345509893455, 9, 1, 18),
    2024: (4060, 3030, 29, 17, 10, 0.9872137666255314, 10, 0, 19),
}
SCORES = {"G1": True, "G2": True, "G3": True, "P1": True, "P2": True, "P3": False,
          "P4": False, "P5": True}
# From compete-results/xwcap-v1/out/xwcap_over_2024.csv (not committed): over groups by plant.
OVER_PLANTS = [
    (1391, "Louisiana 1", "LA", 3, "other", "3.587 to 9.913"),
    (1571, "Chalk Point LLC", "MD", 1, "other", "5.312"),
    (1595, "Kendall Square Station", "MA", 1, "cc", "1.514"),
    (2079, "Hawthorn", "MO", 1, "cc", "1.737"),
    (2493, "East River", "NY", 2, "other", "1.539 to 1.711"),
    (3406, "Johnsonville", "TN", 1, "other", "1.846"),
    (7307, "Redding Power", "CA", 1, "cc", "1.525"),
    (7984, "Kalkaska CT #1", "MI", 1, "other", "1.603"),
    (8906, "Astoria Generating Station", "NY", 2, "other", "2.016 to 2.021"),
    (50625, "ExxonMobil Beaumont Refinery", "TX", 3, "other", "2.117 to 2.147"),
    (54149, "Stony Brook Cogen Plant", "NY", 1, "other", "1.766"),
    (55271, "Tenaska Lindsay Hill Generating Station", "AL", 2, "cc", "1.699 to 1.770"),
    (55419, "Plaquemine Cogeneration Plant", "LA", 1, "cc", "1.639"),
    (57185, "Cricket Valley Energy", "NY", 3, "cc", "2.222 to 2.227"),
    (57865, "Antelope Station", "TX", 3, "other", "21.935 to 22.043"),
    (60589, "CPV Fairview Energy Center", "PA", 1, "cc", "1.508"),
    (64854, "Primient", "IN", 2, "other", "2.071 to 2.201"),
]


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


def pct(a, b):
    return 100.0 * a / b


class XwcapResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/xwcap.md")
        cls.plan = read("docs/xwcap-plan.md")

    def test_scores_follow_the_plan_thresholds(self):
        m, pc, ps = MAIN, PLANT_CHECK, PERSISTENCE
        s = {
            "G1": G1["missing_cols"] == [] and YEAR >= 2022,
            "G2": m["study"] >= 1500,
            "G3": 0.7 <= m["median_ratio"] <= 1.3,
            "P1": m["over"] < 0.05 * m["study"],
            "P2": m["over"] >= 10 and m["over_by_class"]["cc"] < 0.5 * m["over"],
            "P3": m["over"] >= 10 and m["over_by_class"]["candidate"] >= 0.20 * m["over"],
            "P4": pc["study"] >= 1 and pc["over"] == pc["study"]
            and pc["candidate"] == pc["study"],
            "P5": ps["in_prev_study"] >= 10
            and ps["also_over_prev"] >= 0.70 * ps["in_prev_study"],
        }
        self.assertEqual(s, SCORES)
        preds = ("P1", "P2", "P3", "P4", "P5")
        held = [k for k in preds if s[k]]
        self.assertEqual([k for k in preds if not s[k]], ["P3", "P4"])
        self.assertIn("**All three gates held and %d of 5 predictions held; P3 and P4 failed.**"
                      % len(held), self.doc)
        for text in ("**P1 (75%):**", "**P2 (60%):**", "**P3 (55%):**", "**P4 (70%):**",
                     "**P5 (65%):**", "candidates are looked for only in the EIA plants of a "
                     "group's own generators"):
            self.assertIn(text, self.plan)

    def test_score_rows(self):
        m, ps = MAIN, PERSISTENCE
        rows = [
            "| Gate G1 | held | all 4 columns present; year {}; {:,} rows in the table |".format(
                YEAR, G1["ops_rows"]),
            "| Gate G2 | held | {:,} groups in the study set (of {:,} groups formed by {:,} "
            "links) |".format(m["study"], m["groups"], m["links"]),
            "| Gate G3 | held | median ratio over the study set = %.3f |" % m["median_ratio"],
            "| P1 (75%) | held | {} of {:,} groups ({:.1f}%) are over; the bar was fewer than "
            "5% |".format(m["over"], m["study"], pct(m["over"], m["study"])),
            "| P2 (60%) | held | {} of {} over groups ({:.1f}%) are in class cc; the bar was "
            "fewer than half |".format(m["over_by_class"]["cc"], m["over"],
                                       pct(m["over_by_class"]["cc"], m["over"])),
            "| P3 (55%) | failed | {} of {} over groups are in class candidate; the bar was at "
            "least 20% |".format(m["over_by_class"]["candidate"], m["over"]),
            "| P4 (70%) | failed | all {} study-set groups of plant 57865 are over, but none is "
            "in class candidate |".format(PLANT_CHECK["study"]),
            "| P5 (65%) | held | {} of {} units ({:.1f}%) in {} over groups were also in over "
            "groups in {}; the bar was at least 70% |".format(
                ps["also_over_prev"], ps["over_units"],
                pct(ps["also_over_prev"], ps["over_units"]), YEAR, YEAR - 1),
        ]
        for row in rows:
            self.assertIn(row, self.doc)
        self.assertEqual(ps["over_units"], m["over_units"])
        self.assertIn("In 2024, 29 of the 3,030 crosswalk groups in the study set (1.0%)",
                      self.doc)
        self.assertIn("{} of the {} over groups have a ratio of 2 or more; {} study-set groups "
                      "are under".format(m["over_2x"], m["over"], m["under"]), self.doc)
        self.assertIn("{:,} study-set groups are a single unit linked to a single generator"
                      .format(m["single_pair_study"]), self.doc)
        q = QUANTILES
        self.assertIn("10%% %.3f, 25%% %.3f, 50%% %.3f, 75%% %.3f, 90%% %.3f, 99%% %.3f"
                      % (q["0.1"], q["0.25"], q["0.5"], q["0.75"], q["0.9"], q["0.99"]),
                      self.doc)

    def test_year_table(self):
        for y, (g, st, ov, o2, un, med, cc, ca, ot) in BY_YEAR.items():
            self.assertEqual(cc + ca + ot, ov)
            row = "| {} | {:,} | {:,} | {} | {} | {} | {:.3f} | {} / {} / {} |".format(
                y, g, st, ov, o2, un, med, cc, ca, ot)
            self.assertIn(row, self.doc)
        b = BY_YEAR[YEAR]
        self.assertEqual((b[0], b[1], b[2]), (MAIN["groups"], MAIN["study"], MAIN["over"]))
        self.assertEqual(max(v[7] for v in BY_YEAR.values()), 1)
        self.assertEqual((min(v[2] for v in BY_YEAR.values()),
                          max(v[2] for v in BY_YEAR.values())), (25, 30))
        self.assertIn("25 to 30 over groups a year", self.doc)

    def test_plant_table(self):
        for row in OVER_PLANTS:
            self.assertIn("| %d | %s | %s | %d | %s | %s |" % row, self.doc)
        self.assertEqual(sum(r[3] for r in OVER_PLANTS), MAIN["over"])
        self.assertEqual(sum(r[3] for r in OVER_PLANTS if r[4] == "cc"),
                         MAIN["over_by_class"]["cc"])
        other = [r for r in OVER_PLANTS if r[4] == "other"]
        self.assertEqual(sum(r[3] for r in other), MAIN["over_by_class"]["other"])
        self.assertIn("The 19 \"other\" groups sit in %d plants." % len(other), self.doc)

    def test_after_scoring_and_disclosure(self):
        for text in ("## After scoring (not pre-registered)",
                     "3c7d6724cddee38dfb6a06debca732c33a227ed6",
                     "plant 58835, \"Elk Station\"",
                     "[Open Grid Emissions issue #262]",
                     "committed on 2 November 2026 at 15:57 UTC as a936d26",
                     "first poll (16:01:08 UTC)", "passed its own 14 unit tests",
                     "| `core_epa__assn_eia_epacamd` | 190,240 | "
                     "420d50a7e4d066d29eee909eab73d932 | Mon, 02 Nov 2026 08:08:13 GMT |",
                     "| `out_epacems__yearly_operational_characteristics` | 3,293,776 | "
                     "06968d7c96dd4edcb3fc87960aacd573 | Mon, 02 Nov 2026 08:10:58 GMT |",
                     "made with AI agents working in MV2's name; no person has checked these "
                     "results by hand",
                     "PUDL's code (MIT) and data (CC BY 4.0) are downloaded at run time and not "
                     "stored here.", "[plan](xwcap-plan.md)"):
            self.assertIn(text, self.doc)
        self.assertIn("190,240 bytes", self.plan)
        self.assertNotIn("MIT License", self.doc)


if __name__ == "__main__":
    unittest.main()
