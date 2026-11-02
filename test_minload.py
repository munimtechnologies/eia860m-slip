"""Checks that docs/minload.md scores Gates G1-G3 and P1-P6 of docs/minload-plan.md
(pre-registration minload-1) with the counts job minload-v1 wrote, using the plan's own
thresholds, and reports the failed bars as failed. Reads text only, so it needs no polars.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))

# Copied from compete-results/minload-v1/out/minload_check.json.
YEAR = 2024
G1 = {"missing_cols": [], "rows_year": 4215}
C = {"n": 2179, "above": 934, "below": 1231, "within_20": 1139, "below_80": 441,
     "median_max_frac": 0.9903381642512077, "spearman_mw": 0.8469000828888567,
     "spearman_frac": 0.5672882972541338, "median_pudl_frac": 0.4628099173553719,
     "median_eia_frac": 0.4117647058823529}
NULL_BY_CLASS = {"GT": (1653, 194), "CC": (67, 1), "ST": (734, 78), "IC": (3, 0)}
BY_CLASS = {"GT": {"n": 1457, "within_20": 811, "below_80": 111, "median_ratio": 1.0294117647058822,
                   "spearman_mw": 0.8288241652221189},
            "ST": {"n": 656, "within_20": 302, "below_80": 298, "median_ratio": 0.8202564102564103,
                   "spearman_mw": 0.8855473599286788},
            "CC": {"n": 63, "within_20": 26, "below_80": 32, "median_ratio": 0.7875000000000001,
                   "spearman_mw": 0.6994474584183101},
            "IC": {"n": 3, "within_20": 0, "below_80": 0, "median_ratio": 22.054054054054056}}
PAIRS = {"one_to_one_pairs": 3222, "with_ops_and_gen": 2457}
COVERAGE_2024 = (34914, 20439)
SCORES = {"G1": True, "G2": True, "G3": True, "P1": False, "P2": False, "P3": True,
          "P4": False, "P5": False, "P6": True}
# Counted with a regex over compete-results/minload-v1/out/minload_compare_2024.csv
# (not committed): pairs with min_stable_load_factor 0.1, by prime mover.
AT_FLOOR = {"all": 174, "ST": 129, "GT": 35}


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


def pct(a, b):
    return 100.0 * a / b


class MinloadResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/minload.md")
        cls.plan = read("docs/minload-plan.md")

    def test_scores_follow_the_plan_thresholds(self):
        c = C
        gt, st = NULL_BY_CLASS["GT"], NULL_BY_CLASS["ST"]
        s = {
            "G1": G1["missing_cols"] == [] and G1["rows_year"] > 0 and YEAR >= 2022,
            "G2": c["n"] >= 300,
            "G3": 0.7 <= c["median_max_frac"] <= 1.3,
            "P1": c["above"] >= 0.5 * c["n"],
            "P2": c["within_20"] < 0.40 * c["n"],
            "P3": c["spearman_mw"] >= 0.80,
            "P4": c["spearman_frac"] < 0.50,
            "P5": gt[0] >= 20 and st[0] >= 20 and gt[1] / gt[0] >= st[1] / st[0] + 0.15,
            "P6": c["below_80"] >= 0.15 * c["n"],
        }
        self.assertEqual(s, SCORES)
        preds = ("P1", "P2", "P3", "P4", "P5", "P6")
        held = [k for k in preds if s[k]]
        self.assertEqual([k for k in preds if not s[k]], ["P1", "P2", "P4", "P5"])
        self.assertIn("All three gates held and %d of 6 predictions held; P1, P2, P4 and P5 "
                      "failed." % len(held), self.doc)
        for text in ("**P1 (55%):**", "**P2 (65%):**", "**P3 (85%):**", "**P4 (60%):**",
                     "**P5 (70%):**", "**P6 (60%):**",
                     "If P2 fails, the observed minimum mostly matches the reported one within "
                     "20%, which would support PUDL's method as it stands."):
            self.assertIn(text, self.plan)

    def test_table_rows(self):
        c = C
        gt, st = NULL_BY_CLASS["GT"], NULL_BY_CLASS["ST"]
        rows = [
            "| Gate G1 | held | all 13 columns present; {:,} rows in {} |".format(
                G1["rows_year"], YEAR),
            "| Gate G2 | held | {:,} pairs in the comparison set |".format(c["n"]),
            "| Gate G3 | held | median `max_gross_load_mw` / `capacity_mw` = %.3f |"
            % c["median_max_frac"],
            "| P1 (55%) | failed | PUDL's minimum is above EIA's for {} of {:,} pairs ({:.1f}%); "
            "the bar was at least half |".format(c["above"], c["n"], pct(c["above"], c["n"])),
            "| P2 (65%) | failed | {:,} of {:,} pairs ({:.1f}%) agree within 20%; the bar was "
            "fewer than 40% |".format(c["within_20"], c["n"], pct(c["within_20"], c["n"])),
            "| P3 (85%%) | held | Spearman rank correlation of the two minimums in MW = %.3f |"
            % c["spearman_mw"],
            "| P4 (60%%) | failed | Spearman rank correlation of the two fractions of nameplate = "
            "%.3f; the bar was below 0.50 |" % c["spearman_frac"],
            "| P5 (70%) | failed | no `min_stable_load_factor`: {} of {:,} GT pairs ({:.1f}%) "
            "against {} of {} ST pairs ({:.1f}%), {:.1f} points apart; the bar was 15 |".format(
                gt[1], gt[0], pct(gt[1], gt[0]), st[1], st[0], pct(st[1], st[0]),
                pct(gt[1], gt[0]) - pct(st[1], st[0])),
            "| P6 (60%) | held | PUDL's minimum is below 80% of EIA's for {} of {:,} pairs "
            "({:.1f}%) |".format(c["below_80"], c["n"], pct(c["below_80"], c["n"])),
        ]
        for row in rows:
            self.assertIn(row, self.doc)
        self.assertEqual(c["above"] + c["below"] + 14, c["n"])
        self.assertIn("above EIA's for 934 pairs, below for 1,231 and equal for 14", self.doc)
        self.assertEqual(sum(u for u, _ in NULL_BY_CLASS.values()), PAIRS["with_ops_and_gen"])
        self.assertIn("The crosswalk gives {:,} one-to-one pairs in 2024; {:,} have both".format(
            PAIRS["one_to_one_pairs"], PAIRS["with_ops_and_gen"]), self.doc)

    def test_class_table(self):
        for name in ("GT", "ST", "CC"):
            b = BY_CLASS[name]
            row = "| {} | {:,} | {:.2f} | {} ({:.1f}%) | {} ({:.1f}%) | {:.3f} |".format(
                name, b["n"], b["median_ratio"], b["within_20"], pct(b["within_20"], b["n"]),
                b["below_80"], pct(b["below_80"], b["n"]), b["spearman_mw"])
            self.assertIn(row, self.doc)
        self.assertIn("| IC | 3 | 22.05 | 0 | 0 | not computed |", self.doc)
        self.assertEqual(sum(b["n"] for b in BY_CLASS.values()), C["n"])
        self.assertIn("Steam units are the exception: for %.1f%% of them"
                      % pct(BY_CLASS["ST"]["below_80"], BY_CLASS["ST"]["n"]), self.doc)

    def test_text_counts(self):
        d = self.doc
        self.assertIn("%d of the %d ST pairs (%.1f%%) have a `min_stable_load_factor` of 0.1"
                      % (AT_FLOOR["ST"], BY_CLASS["ST"]["n"],
                         pct(AT_FLOOR["ST"], BY_CLASS["ST"]["n"])), d)
        self.assertIn("(%d pairs in all: %d ST, %d GT, %d CC)"
                      % (AT_FLOOR["all"], AT_FLOOR["ST"], AT_FLOOR["GT"],
                         AT_FLOOR["all"] - AT_FLOOR["ST"] - AT_FLOOR["GT"]), d)
        gens, with_min = COVERAGE_2024
        self.assertIn("{:,} of {:,} generator rows in 2024 ({:.1f}%)".format(
            with_min, gens, pct(with_min, gens)), d)
        self.assertIn("the medians are %.3f (PUDL) and %.3f (EIA)"
                      % (C["median_pudl_frac"], C["median_eia_frac"]), d)
        self.assertIn("agree within 20% for 52.3% of units, with a median ratio of 0.97 and a "
                      "rank correlation of 0.85", d)

    def test_run_facts_and_disclosure(self):
        for text in ("committed 1 November 2026 at 15:55 UTC as db92c23",
                     "first poll (20:15:45 UTC)", "passed its own 13 unit tests",
                     "| `out_epacems__yearly_operational_characteristics` | 3,293,894 | "
                     "fa2c347fded1840e71b7cf3d658065d9 | Sun, 01 Nov 2026 08:05:03 GMT |",
                     "That is the pre-registered reading",
                     "made with AI agents working in MV2's name; no person has checked these "
                     "results by hand",
                     "PUDL's code (MIT) and data (CC BY 4.0) are downloaded at run time and not "
                     "stored here.", "[plan](minload-plan.md)"):
            self.assertIn(text, self.doc)
        self.assertIn("3,293,894 bytes", self.plan)


if __name__ == "__main__":
    unittest.main()
