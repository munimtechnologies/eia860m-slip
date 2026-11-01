"""Checks that docs/cems-blank.md scores Gates B0-B1 and P0-P5 of docs/cems-blank-plan.md
(pre-registration cems-blank-1) with the counts job cems-blank-v1 wrote, using the plan's own
thresholds, and reports the failed bars as failed. Reads text only, so it needs no polars.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))

# Copied from compete-results/cems-blank-v1/out/blank_check.json, "modes" and "v3".
NONE = {"units": 305, "run_min_equal": 305, "units_with_min": 259, "at1": 199, "at2": 25,
        "isolated_runs": 810, "isolated_no_op_no_heat": 810, "isolated_upflank": 105,
        "isolated_strict": 5, "isolated_counted_by_fill_isolated": 810, "runs": 46952,
        "run_hours": 3844211, "run_op_hours": 0, "run_heat_hours": 0,
        "buckets": {"1": 199, "2": 25, "3": 11, "4-9": 18, "10+": 6}}
FILL = {"units": 305, "run_min_equal": 305, "units_with_min": 259, "at1": 0, "at2": 178,
        "le2": 178, "at2_upflank": 33, "at2_strict": 0, "cf_strict_le2": 178,
        "cf_upflank_le2": 175, "two_runs": 748, "two_runs_hours": 1496,
        "two_runs_no_op_hours": 1496, "two_runs_heat_hours": 0, "two_runs_sandwiched": 744,
        "two_runs_upflank": 71, "two_runs_strict": 0, "runs": 46142, "run_hours": 3843401,
        "run_op_hours": 0, "run_heat_hours": 0, "units_min_runs_op": 0,
        "buckets": {"1": 0, "2": 178, "3": 38, "4-9": 36, "10+": 7},
        "cf_upflank_buckets": {"1": 0, "2": 175, "3": 40, "4-9": 37, "10+": 7}}
V3 = {"none": (305, 305), "fill": (305, 305)}  # rows, equal
SCORES = {"B0": True, "B1": True, "P0": True, "P1": False, "P2": True, "P3": False,
          "P4": False, "P5": True}
ISOLATED = {"Colorado": 404, "Indiana": 260, "Wisconsin": 146}
# Counted in compete-results/cems-blank-v1/out/two_hour_runs_fill.csv (not committed):
# 2-hour runs whose hour before / after reports a full operating hour.
BEFORE_FULL, AFTER_FULL = 9, 15


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


def pct(a, b):
    return 100.0 * a / b


class CemsBlankResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/cems-blank.md")
        cls.plan = read("docs/cems-blank-plan.md")

    def test_scores_follow_the_plan_thresholds(self):
        n, f = NONE, FILL
        s = {
            "B0": all(m["run_min_equal"] >= 0.99 * m["units"] for m in (n, f))
            and n["isolated_runs"] == n["isolated_counted_by_fill_isolated"],
            "B1": all(eq >= 0.99 * rows for rows, eq in V3.values()),
            "P0": n["isolated_runs"] > 0
            and n["isolated_no_op_no_heat"] >= 0.99 * n["isolated_runs"],
            "P1": f["at2_upflank"] >= 0.5 * f["at2"],
            "P2": f["two_runs_no_op_hours"] >= 0.90 * f["two_runs_hours"],
            "P3": f["cf_strict_le2"] <= 0.60 * f["le2"],
            "P4": 0.01 <= f["run_op_hours"] / f["run_hours"] <= 0.10,
            "P5": f["units_min_runs_op"] < 0.20 * f["units_with_min"],
        }
        self.assertEqual(s, SCORES)
        held = [k for k in ("P0", "P1", "P2", "P3", "P4", "P5") if s[k]]
        failed = [k for k in ("P0", "P1", "P2", "P3", "P4", "P5") if not s[k]]
        self.assertEqual(failed, ["P1", "P3", "P4"])
        self.assertIn("Both gates held and %d of 6 predictions held; P1, P3 and P4 failed."
                      % len(held), self.doc)
        for text in ("If B0 or B1 fails, P0-P5 are reported but not scored.",
                     "If P1 and P3 both fail, the 2-hour values mostly look like real short stops",
                     "**P1 (55%):**", "**P3 (55%):**", "**P4 (65%):**"):
            self.assertIn(text, self.plan)

    def test_table_rows(self):
        n, f = NONE, FILL
        self.assertEqual(sum(ISOLATED.values()), n["isolated_runs"])
        rows = [
            "| Gate B0 | held | shortest down run = PUDL's `min_down_time_hours` for %d of %d "
            "units in both runs; %d one-hour sandwiched runs, and `fill_isolated.py` counts %d "
            "isolated null hours |" % (f["run_min_equal"], f["units"], n["isolated_runs"],
                                       n["isolated_counted_by_fill_isolated"]),
            "| Gate B1 | held | %d of %d of cems-mindown-v3's units found with the same "
            "`min_down_time_hours`, with no patch and with the fill patch |" % V3["fill"][::-1],
            "| P0 (85%%) | held | %d of %d one-hour sandwiched runs report no operating time and "
            "no heat input (%.0f%%) |" % (n["isolated_no_op_no_heat"], n["isolated_runs"],
                                          pct(n["isolated_no_op_no_heat"], n["isolated_runs"])),
            "| P1 (55%%) | failed | %d of the %d units at exactly 2 hours (%.1f%%) have an "
            "up-flanked 2-hour down run; the bar was at least half |"
            % (f["at2_upflank"], f["at2"], pct(f["at2_upflank"], f["at2"])),
            "| P2 (75%) | held | {:,} of {:,} hours in those units' {:,} two-hour runs report no "
            "operating time ({:.0f}%) |".format(f["two_runs_no_op_hours"], f["two_runs_hours"],
                                                f["two_runs"],
                                                pct(f["two_runs_no_op_hours"],
                                                    f["two_runs_hours"])),
            "| P3 (55%%) | failed | units at 2 hours or less: %d, and still %d after setting "
            "aside strictly flanked runs of 1 or 2 hours (no fall;" % (f["le2"], f["cf_strict_le2"]),
            "| P4 (65%) | failed | {:,} of {:,} down-run hours report operating time above 0 "
            "({:.0f}%); the band was 1% to 10% |".format(f["run_op_hours"], f["run_hours"],
                                                         pct(f["run_op_hours"], f["run_hours"])),
            "| P5 (65%%) | held | %d of the %d units with a minimum down time have an hour with "
            "operating time above 0 in a shortest down run |"
            % (f["units_min_runs_op"], f["units_with_min"]),
        ]
        for row in rows:
            self.assertIn(row, self.doc)
        self.assertEqual(2 * f["two_runs"], f["two_runs_hours"])

    def test_run_totals(self):
        n, f = NONE, FILL
        self.assertEqual(n["runs"] - f["runs"], n["isolated_runs"])
        self.assertEqual(n["run_hours"] - f["run_hours"], n["isolated_runs"])
        self.assertIn("With no patch there are {:,} down runs covering {:,} hours; with the fill "
                      "patch, {:,} runs covering {:,} hours, exactly {} fewer of each."
                      .format(n["runs"], n["run_hours"], f["runs"], f["run_hours"],
                              n["isolated_runs"]), self.doc)
        self.assertIn("%d in Colorado, %d in Indiana and %d in Wisconsin"
                      % (ISOLATED["Colorado"], ISOLATED["Indiana"], ISOLATED["Wisconsin"]),
                      self.doc)

    def test_shape_counts(self):
        n, f = NONE, FILL
        up2 = pct(f["two_runs_upflank"], f["two_runs"])
        up1 = pct(n["isolated_upflank"], n["isolated_runs"])
        st1 = pct(n["isolated_strict"], n["isolated_runs"])
        self.assertEqual(f["two_runs_strict"], 0)
        self.assertIn("Only %d of the %d (%.1f%%) have an hour at or above"
                      % (f["two_runs_upflank"], f["two_runs"], up2), self.doc)
        self.assertIn("go from %d to %d (a %.1f%% fall)"
                      % (f["le2"], f["cf_upflank_le2"],
                         pct(f["le2"] - f["cf_upflank_le2"], f["le2"])), self.doc)
        self.assertIn("in %d of %d runs and the hour after in %d of %d"
                      % (BEFORE_FULL, f["two_runs"], AFTER_FULL, f["two_runs"]), self.doc)
        self.assertIn("%d of the %d one-hour sandwiched runs (%.1f%%) are up-flanked and %d "
                      "(%.1f%%) are strictly flanked"
                      % (n["isolated_upflank"], n["isolated_runs"], up1, n["isolated_strict"],
                         st1), self.doc)
        self.assertIn("(%.1f%% up-flanked against %.1f%%; strict flanks %.1f%% against 0%%)"
                      % (up1, up2, st1), self.doc)
        self.assertIn("%d of the %d two-hour runs are sandwiched; the other %d"
                      % (f["two_runs_sandwiched"], f["two_runs"],
                         f["two_runs"] - f["two_runs_sandwiched"]), self.doc)
        self.assertEqual(f["run_heat_hours"] + n["run_heat_hours"] + n["run_op_hours"], 0)

    def test_distributions(self):
        n, f = NONE, FILL
        for m in (n["buckets"], f["buckets"], f["cf_upflank_buckets"]):
            self.assertEqual(sum(m.values()), f["units_with_min"])
        b, c, z = f["buckets"], f["cf_upflank_buckets"], n["buckets"]
        self.assertIn("%d at 2 hours, %d at 3, %d at 4-9, %d at 10 or more (%d units; median 2)"
                      % (b["2"], b["3"], b["4-9"], b["10+"], f["units_with_min"]), self.doc)
        self.assertIn("After setting aside up-flanked short runs: %d, %d, %d and %d."
                      % (c["2"], c["3"], c["4-9"], c["10+"]), self.doc)
        self.assertIn("%d at 1 hour, %d at 2, %d at 3, %d at 4-9, %d at 10 or more (median 1)"
                      % (z["1"], z["2"], z["3"], z["4-9"], z["10+"]), self.doc)

    def test_run_facts_and_disclosure(self):
        for text in ("committed 31 October 2026 at 17:25 UTC as 583c49c",
                     "passed its own 14 unit tests", "all 5 pinned `tools/cems-mindown` files",
                     "Last-Modified Sat, 31 Oct 2026 08:10:56 GMT", "Peak memory was 1.88 GB.",
                     "that is the pre-registered reading",
                     "made with AI agents working in MV2's name; no person has checked these "
                     "results by hand",
                     "PUDL's code (MIT) and data (CC BY 4.0) are downloaded at run time and not "
                     "stored here."):
            self.assertIn(text, self.doc)
        self.assertIn("[plan](cems-blank-plan.md)", self.doc)


if __name__ == "__main__":
    unittest.main()
