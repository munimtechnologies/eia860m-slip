"""Checks that docs/cems-flank.md scores Gates K1-K3, U0 and F1-F3, D1-D2, U1-U3 of
docs/cems-flank-plan.md (pre-registration cems-flank-1) with the counts job cems-flank-v1
wrote, using the plan's own thresholds, and reports the failed bar as failed. Reads text only,
so it needs no polars.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))

# Copied from compete-results/cems-flank-v1/out/flank_check.json.
K1 = {"none": {"ft": 46952, "rt": 46952, "joined": 46952, "mismatch": 0},
      "fill": {"ft": 46142, "rt": 46142, "joined": 46142, "mismatch": 0}}
COUNTS = {"two_at2_runs": 748, "at2_units": 178, "units": 305, "units_with_min": 259}
WORKING = {"units": 305, "units_nunique_le1": 46, "units_nunique_le1_with_heat": 43,
           "null_load_heat_hours": 384478, "null_load_heat_hours_valid": 0,
           "heat_mmbtu": 4651889820.486, "heat_mmbtu_nunique_le1": 118105398.166,
           "null_load_heat_mmbtu": 118105398.166}
# "both" (before and after together): runs, n, partial, full
TWO_AT2 = {"runs": 748, "n": 1492, "partial": 1468, "full": 24, "null": 0, "zero": 0}
ISO1 = {"runs": 810, "n": 1620, "partial": 1575, "full": 45, "null": 0, "zero": 0}
MID3_9 = {"runs": 12543, "n": 25073, "partial": 24773, "full": 300, "null": 0, "zero": 0}
LONG10 = {"runs": 32851, "n": 65405, "partial": 64424, "full": 981, "null": 0, "zero": 0}
TYPES = {"units_with_min": 259, "unmatched": 10, "at2_units": 172, "ct_at2": 132,
         "ge3_units": 77, "ct_ge3": 54, "st_units": 63, "st_at2": 40, "slow_units": 112,
         "slow_le2": 81}
BY_CLASS = {"GT": (135, 89), "CC": (51, 43), "ST": (63, 40), "unmatched": (10, 6)}
BY_START = {"fast": (137, 91), "slow": (112, 81), "unknown": (10, 6)}
PARTIAL_BY_CLASS = {"GT": (758, 774), "CC": (481, 486), "ST": (211, 214)}
COLD = {"10M": 9041, "1H": 6643, "12H": 3947, "OVER": 1646, "None": 13637}
GENS_2024 = 34914  # minload-v1 coverage, same nightly core_eia860__scd_generators (md5 6c4372...)
SCORES = {"K1": True, "K2": True, "K3": True, "U0": True, "F1": True, "F2": True, "F3": True,
          "D1": True, "D2": True, "U1": False, "U2": True, "U3": True}


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


def pct(a, b):
    return 100.0 * a / b


def share(g):
    return g["partial"] / g["n"]


class CemsFlankResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/cems-flank.md")
        cls.plan = read("docs/cems-flank-plan.md")

    def test_scores_follow_the_plan_thresholds(self):
        t, w, c = TYPES, WORKING, COUNTS
        s = {
            "K1": all(m["ft"] == m["rt"] == m["joined"] and m["mismatch"] == 0
                      for m in K1.values()),
            "K2": abs(c["two_at2_runs"] - 748) <= 0.02 * 748
            and abs(c["at2_units"] - 178) <= 0.02 * 178,
            "K3": w["null_load_heat_hours_valid"] == 0,
            "U0": t["units_with_min"] - t["unmatched"] >= 0.80 * t["units_with_min"],
            "F1": TWO_AT2["partial"] >= 0.70 * TWO_AT2["n"],
            "F2": ISO1["partial"] >= 0.70 * ISO1["n"]
            and abs(share(ISO1) - share(TWO_AT2)) <= 0.15,
            "F3": LONG10["partial"] >= 0.70 * LONG10["n"],
            "D1": w["null_load_heat_hours"] >= 10000,
            "D2": w["units_nunique_le1_with_heat"] >= 5,
            "U1": t["ct_at2"] / t["at2_units"] >= t["ct_ge3"] / t["ge3_units"] + 0.10,
            "U2": t["st_units"] >= 5 and t["st_at2"] >= 0.40 * t["st_units"],
            "U3": t["slow_units"] >= 5 and t["slow_le2"] >= 0.40 * t["slow_units"],
        }
        self.assertEqual(s, SCORES)
        preds = ("F1", "F2", "F3", "D1", "D2", "U1", "U2", "U3")
        held = [k for k in preds if s[k]]
        self.assertEqual([k for k in preds if not s[k]], ["U1"])
        self.assertIn("All four gates held and %d of 8 predictions held; U1 failed." % len(held),
                      self.doc)
        for text in ("If K1 fails, F1-F3 are reported but not scored.", "**F1 (70%):**",
                     "**F2 (60%):**", "**F3 (65%):**", "**U1 (50%):**", "**U2 (60%):**",
                     "**U3 (55%):**", "**D1 (60%):**", "**D2 (75%):**",
                     "MV2 will say so plainly on issue #5514, because it cuts against his own "
                     "patch."):
            self.assertIn(text, self.plan)

    def test_table_rows(self):
        t, w = TYPES, WORKING
        matched = t["units_with_min"] - t["unmatched"]
        rows = [
            "| Gate K1 | held | in both runs the flank table lists the same down runs as "
            "`blank_check.py` ({:,} with no patch, {:,} with the fill patch), with 0 mismatched "
            "full flanks |".format(K1["none"]["ft"], K1["fill"]["ft"]),
            "| Gate K2 | held | %d two-hour runs at %d units at exactly 2 hours"
            % (COUNTS["two_at2_runs"], COUNTS["at2_units"]),
            "| Gate U0 | held | %d of the %d units with a minimum down time (%.1f%%) get a "
            "prime-mover class |" % (matched, t["units_with_min"],
                                     pct(matched, t["units_with_min"])),
            "| F1 (70%) | held | {:,} of {:,} flanking hours of the 2-hour runs at units at exactly "
            "2 hours ({:.1f}%) are partial |".format(TWO_AT2["partial"], TWO_AT2["n"],
                                                     100 * share(TWO_AT2)),
            "| F2 (60%) | held | with no patch, {:,} of {:,} flanking hours of the {} one-hour "
            "sandwiched runs ({:.1f}%) are partial, {:.1f} points from F1's share |".format(
                ISO1["partial"], ISO1["n"], ISO1["runs"], 100 * share(ISO1),
                100 * (share(TWO_AT2) - share(ISO1))),
            "| F3 (65%) | held | with the fill patch, {:,} of {:,} flanking hours of the {:,} down "
            "runs of 10 hours or more ({:.1f}%) are partial |".format(
                LONG10["partial"], LONG10["n"], LONG10["runs"], 100 * share(LONG10)),
            "| D1 (60%) | held | {:,} hours in the binning frame have null `gross_load_mw` and "
            "heat input above 0 |".format(w["null_load_heat_hours"]),
            "| D2 (75%%) | held | %d units have `load_factor_nunique` of 1 or less and heat input "
            "above 0 |" % w["units_nunique_le1_with_heat"],
            "| U1 (50%%) | failed | CT-based share: %d of %d matched units at exactly 2 hours "
            "(%.1f%%) against %d of %d at 3 hours or more (%.1f%%), %.1f points apart; the bar "
            "was 10 |" % (t["ct_at2"], t["at2_units"], pct(t["ct_at2"], t["at2_units"]),
                          t["ct_ge3"], t["ge3_units"], pct(t["ct_ge3"], t["ge3_units"]),
                          pct(t["ct_at2"], t["at2_units"]) - pct(t["ct_ge3"], t["ge3_units"])),
            "| U2 (60%%) | held | %d of %d ST units (%.1f%%) sit at exactly 2 hours |"
            % (t["st_at2"], t["st_units"], pct(t["st_at2"], t["st_units"])),
            "| U3 (55%%) | held | %d of %d slow-start units (%.1f%%) have a minimum down time of 2 "
            "hours or less |" % (t["slow_le2"], t["slow_units"],
                                 pct(t["slow_le2"], t["slow_units"])),
        ]
        for row in rows:
            self.assertIn(row, self.doc)

    def test_groups_add_up(self):
        for g in (TWO_AT2, ISO1, MID3_9, LONG10):
            self.assertEqual(g["null"] + g["zero"], 0)
            self.assertLessEqual(g["partial"] + g["full"], g["n"])
            self.assertLessEqual(g["n"], 2 * g["runs"])
        self.assertEqual(TWO_AT2["partial"] + TWO_AT2["full"], TWO_AT2["n"])
        t = TYPES
        self.assertEqual(t["at2_units"] + t["ge3_units"], t["units_with_min"] - t["unmatched"])
        self.assertEqual(sum(u for u, _ in BY_CLASS.values()), t["units_with_min"])
        self.assertEqual(sum(a for _, a in BY_CLASS.values()), COUNTS["at2_units"])
        self.assertEqual(BY_CLASS["GT"][1] + BY_CLASS["CC"][1], t["ct_at2"])
        self.assertEqual(sum(u for u, _ in BY_START.values()), t["units_with_min"])
        self.assertEqual(sum(COLD.values()), GENS_2024)

    def test_counts_in_text(self):
        d = self.doc
        self.assertIn("98.8% for runs of 3 to 9 hours ({:,} of {:,} flanking hours, {:,} runs)"
                      .format(MID3_9["partial"], MID3_9["n"], MID3_9["runs"]), d)
        self.assertEqual("%.1f" % (100 * share(MID3_9)), "98.8")
        self.assertIn("%d of %s (%.1f%%) for the one-hour runs, %d of %s (%.1f%%) for the 2-hour "
                      "runs and %d of %s (%.1f%%) for the long runs"
                      % (ISO1["full"], "{:,}".format(ISO1["n"]), pct(ISO1["full"], ISO1["n"]),
                         TWO_AT2["full"], "{:,}".format(TWO_AT2["n"]),
                         pct(TWO_AT2["full"], TWO_AT2["n"]), LONG10["full"],
                         "{:,}".format(LONG10["n"]), pct(LONG10["full"], LONG10["n"])), d)
        g, c, s = PARTIAL_BY_CLASS["GT"], PARTIAL_BY_CLASS["CC"], PARTIAL_BY_CLASS["ST"]
        self.assertIn("partial shares of %.1f%% (%d of %d flanking hours) for GT units, %.1f%% "
                      "(%d of %d) for combined-cycle units and %.1f%% (%d of %d) for ST units"
                      % (pct(*g), g[0], g[1], pct(*c), c[0], c[1], pct(*s), s[0], s[1]), d)
        b = BY_CLASS
        self.assertIn("%d of %d GT units, %d of %d combined-cycle units and %d of %d ST units"
                      % (b["GT"][1], b["GT"][0], b["CC"][1], b["CC"][0], b["ST"][1],
                         b["ST"][0]), d)
        self.assertIn("%d of %d fast-start units and %d of %d slow-start units"
                      % (BY_START["fast"][1], BY_START["fast"][0], BY_START["slow"][1],
                         BY_START["slow"][0]), d)
        self.assertIn("10M {:,}, 1H {:,}, 12H {:,}, OVER {:,} and none {:,}".format(
            COLD["10M"], COLD["1H"], COLD["12H"], COLD["OVER"], COLD["None"]), d)
        self.assertIn("(%d of %d matched)" % (b["GT"][0] + b["CC"][0],
                                              TYPES["units_with_min"] - TYPES["unmatched"]), d)

    def test_working_frame(self):
        w = WORKING
        self.assertEqual(w["heat_mmbtu_nunique_le1"], w["null_load_heat_mmbtu"])
        self.assertIn("All {:,} such hours in the binning frame belong to units with at most one "
                      "distinct load factor ({} of {} units; {} of them with heat input)".format(
                          w["null_load_heat_hours"], w["units_nunique_le1"], w["units"],
                          w["units_nunique_le1_with_heat"]), self.doc)
        self.assertIn("%.1f million MMBtu (%.1f%% of the frame's %s million)"
                      % (w["null_load_heat_mmbtu"] / 1e6,
                         pct(w["null_load_heat_mmbtu"], w["heat_mmbtu"]),
                         "{:,.1f}".format(w["heat_mmbtu"] / 1e6)), self.doc)

    def test_run_facts_and_disclosure(self):
        for text in ("committed 1 November 2026 at 13:34 UTC as 6561eff",
                     "first poll (16:38:43 UTC)", "passed its own 22 unit tests",
                     "all 6 pinned files", "Last-Modified Sun, 01 Nov 2026 08:02:15 GMT",
                     "Peak memory was 1.75 GB.", "That is the pre-registered reading.",
                     "this result cuts against MV2's own fill patch for PUDL issue #5514",
                     "made with AI agents working in MV2's name; no person has checked these "
                     "results by hand",
                     "PUDL's code (MIT) and data (CC BY 4.0) are downloaded at run time and not "
                     "stored here.", "[plan](cems-flank-plan.md)"):
            self.assertIn(text, self.doc)


if __name__ == "__main__":
    unittest.main()
