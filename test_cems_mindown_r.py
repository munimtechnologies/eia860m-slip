"""Checks that docs/cems-mindown-r.md (part 2 of the cems-mindown-1 result) scores R0 and F1-F4
of docs/cems-mindown-plan.md with the counts job cems-mindown-v3 wrote, and keeps part 1's
failed bars failed. Reads every file as text, so it needs no polars.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))

# Copied from compete-results/cems-mindown-v3/out/mindown_check.json, "real".
UNITS = {"CO": 76, "IN": 137, "WI": 92}
R0_FOUND = 305
R0_EQUAL_DOWN = 304
R0_EQUAL_UP = 304
DOWN_EQ_1 = (199, 0)  # counts_none, counts_fill
UP_EQ_1 = (187, 184)
DOWN_NULL = (46, 46)
FILL_EQUAL = {"plant_id_eia": 305, "state": 305, "max_gross_load_mw": 305,
              "min_stable_load_factor": 305, "min_up_time_hours": 299,
              "min_down_time_hours": 106,
              "heat_rate_at_max_load_factor_mmbtu_per_mwh": 305,
              "heat_rate_at_min_stable_load_factor_mmbtu_per_mwh": 305,
              "ramp_up_rate_per_min": 305, "ramp_down_rate_per_min": 305}
SORT_EQUAL = 305  # every column of sort_vs_none
ISOLATED = {"CO": 404, "IN": 260, "WI": 146}
ROW_GROUPS = {"CO": (693, 123490948), "IN": (812, 142166915), "WI": (446, 80064895)}
# Counted in out/units_none_vs_fill.csv: units at 1 hour without the patch, by state and by
# their value with the fill patch.
AT_ONE_BY_STATE = {"CO": 68, "IN": 83, "WI": 48}
AT_ONE_BECOMES = {"2": 153, "3": 27, "4-9": 18, "10+": 1}


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class CemsMindownPart2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/cems-mindown-r.md")
        cls.plan = read("docs/cems-mindown-plan.md")

    def test_status(self):
        self.assertIn("Gate R0 and F1-F4 held on real hourly data. With [part 1](cems-mindown.md), "
                      "8 of 11 bars held; G1, T1 and T2 stay failed as written", self.doc)
        self.assertIn("Pre-registration id: cems-mindown-1", self.doc)
        self.assertIn("Re-run id: cems-mindown-1-R.", self.doc)
        self.assertIn("| Gate G1, T1, T2 | failed as written (part 1) |", self.doc)

    def test_r0(self):
        units = sum(UNITS.values())
        self.assertEqual(units, R0_FOUND)
        both = R0_EQUAL_DOWN + R0_EQUAL_UP - units
        self.assertTrue(R0_FOUND >= 0.95 * units and both >= 0.95 * R0_FOUND)
        self.assertIn("| Gate R0 | held | %d of %d units found; %d of %d same `min_down_time_hours`, "
                      "%d of %d same `min_up_time_hours` |"
                      % (R0_FOUND, units, R0_EQUAL_DOWN, R0_FOUND, R0_EQUAL_UP, R0_FOUND),
                      self.doc)
        self.assertIn("(Colorado %d, Indiana %d, Wisconsin %d)" % (UNITS["CO"], UNITS["IN"],
                                                                    UNITS["WI"]), self.doc)
        self.assertIn("at least %d of %d (%.1f%%) match on both" % (both, units,
                                                                     100.0 * both / units),
                      self.doc)
        self.assertIn("at least 95% of its units are found", self.plan)

    def test_f_bars(self):
        n0, n1 = DOWN_EQ_1
        self.assertTrue(n0 >= 20 and n1 <= 0.25 * n0)
        self.assertIn("| F1 (85%%) | held | units at 1 hour: %d with no patch, %d with the fill "
                      "patch (a %.0f%% fall) |" % (n0, n1, 100.0 * (n0 - n1) / n0), self.doc)
        u0, u1 = UP_EQ_1
        self.assertTrue(abs(u1 - u0) <= 0.10 * u0)
        self.assertIn("| F2 (80%%) | held | units with `min_up_time_hours` 1: %d with no patch, %d "
                      "with the fill patch (%d, %.1f%%) |"
                      % (u0, u1, u0 - u1, 100.0 * (u0 - u1) / u0), self.doc)
        others = [v for k, v in FILL_EQUAL.items()
                  if k not in ("min_up_time_hours", "min_down_time_hours")]
        self.assertEqual(others, [R0_FOUND] * 8)
        self.assertIn("| F3 (95%%) | held | the %d other output columns identical for %d of %d "
                      "units |" % (len(others), R0_FOUND, R0_FOUND), self.doc)
        self.assertEqual(SORT_EQUAL, R0_FOUND)
        self.assertIn("| F4 (80%%) | held | sort-only patch identical to no patch in all %d "
                      "columns for %d of %d units;" % (len(FILL_EQUAL), SORT_EQUAL, R0_FOUND),
                      self.doc)
        for text in ("**F1 (85%):**", "**F2 (80%):**", "**F3 (95%):**", "**F4 (80%):**",
                     "falls by at least 75%", "changes by at most 10% of its unpatched count"):
            self.assertIn(text, self.plan)

    def test_what_changes(self):
        n0 = DOWN_EQ_1[0]
        self.assertEqual(R0_FOUND - FILL_EQUAL["min_down_time_hours"], n0)
        self.assertEqual(sum(AT_ONE_BY_STATE.values()), n0)
        self.assertEqual(sum(AT_ONE_BECOMES.values()), n0)
        self.assertIn("exactly the %d units that were at 1 hour (Colorado %d of %d, Indiana %d of "
                      "%d, Wisconsin %d of %d)" % (n0, AT_ONE_BY_STATE["CO"], UNITS["CO"],
                                                   AT_ONE_BY_STATE["IN"], UNITS["IN"],
                                                   AT_ONE_BY_STATE["WI"], UNITS["WI"]), self.doc)
        self.assertIn("%d now show 2 hours, %d show 3 hours, %d show 4 to 9 hours and %d shows 10 "
                      "hours or more" % (AT_ONE_BECOMES["2"], AT_ONE_BECOMES["3"],
                                         AT_ONE_BECOMES["4-9"], AT_ONE_BECOMES["10+"]), self.doc)
        self.assertEqual(DOWN_NULL[0], DOWN_NULL[1])
        self.assertIn("%d units have no minimum down time with and without the patch"
                      % DOWN_NULL[0], self.doc)
        self.assertIn("`min_up_time_hours` changed for %d units."
                      % (R0_FOUND - FILL_EQUAL["min_up_time_hours"]), self.doc)
        self.assertIn("%d in Colorado, %d in Indiana and %d in Wisconsin"
                      % (ISOLATED["CO"], ISOLATED["IN"], ISOLATED["WI"]), self.doc)
        self.assertIn("(%d of %d)" % (AT_ONE_BECOMES["2"], n0), self.doc)

    def test_read_size(self):
        groups = sum(g for g, _ in ROW_GROUPS.values())
        size = sum(b for _, b in ROW_GROUPS.values())
        self.assertLess(size, 2.5e9)
        self.assertIn("({:,} row groups, {:,} compressed bytes".format(groups, size), self.doc)

    def test_disclosure_and_licence(self):
        self.assertIn("made with AI agents working in MV2's name; no person has checked these "
                      "results by hand", self.doc)
        self.assertIn("PUDL's code (MIT) and data (CC BY 4.0) are downloaded at run time and "
                      "not stored here.", self.doc)
        self.assertIn("say plainly that those three bars failed as written", self.doc)


if __name__ == "__main__":
    unittest.main()
