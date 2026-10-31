"""Unit tests for blank_check.py on hand-made frames (need polars and the pinned
tools/cems-mindown files; no PUDL, no network).

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.).
"""

import os
import random
import tempfile
import unittest
from datetime import datetime, timedelta

import polars as pl

import blank_check as bc
import fill_isolated as fi
import mindown_check as mc
import reference as ref

BASE = datetime(2024, 1, 1)
U = {"left": 0.5, "right": 0.6}
LO = {"left": 0.1, "right": 0.2}
MS = {"left": 0.3, "right": 0.4}
BIN = pl.Struct({"left": pl.Float64, "right": pl.Float64})
UNIT = ["plant_id_epa", "emissions_unit_id_epa"]


def frame(bins, op=None, heat=None, hours=None, unit=(1, "A"), ms=MS):
    n = len(bins)
    hours = list(range(n)) if hours is None else hours
    op = [1.0 if b is not None else 0.0 for b in bins] if op is None else op
    heat = [100.0 if b is not None else None for b in bins] if heat is None else heat
    return pl.DataFrame(
        {"plant_id_epa": [unit[0]] * n, "emissions_unit_id_epa": [unit[1]] * n,
         "operating_datetime_utc": [BASE + timedelta(hours=h) for h in hours],
         "load_factor_bin": bins, "min_stable_bin": [ms] * n,
         "operating_time_hours": op, "heat_content_mmbtu": heat},
        schema={"plant_id_epa": pl.Int64, "emissions_unit_id_epa": pl.String,
                "operating_datetime_utc": pl.Datetime("us"), "load_factor_bin": BIN,
                "min_stable_bin": BIN, "operating_time_hours": pl.Float64,
                "heat_content_mmbtu": pl.Float64})


def output(units, mins):
    return pl.DataFrame(
        {"plant_id_epa": [u[0] for u in units], "emissions_unit_id_epa": [u[1] for u in units],
         "min_down_time_hours": mins},
        schema={"plant_id_epa": pl.Int64, "emissions_unit_id_epa": pl.String,
                "min_down_time_hours": pl.Float64})


def runs_of(df):
    return bc.run_table(df).to_dicts()


class UpTests(unittest.TestCase):
    def test_up_matches_pudl_rule(self):
        df = frame([U, LO, None, MS]).with_columns(
            pl.Series("min_stable_bin", [MS, MS, MS, None], dtype=BIN))
        self.assertEqual(df.select(bc.up_expr())[:, 0].to_list(), [True, False, False, False])


class RunTableTests(unittest.TestCase):
    def test_isolated_hour(self):
        (r,) = runs_of(frame([U, None, U]))
        self.assertEqual(r["length"], 1)
        self.assertTrue(r["before"] and r["after"] and r["before_up"] and r["after_up"])
        self.assertTrue(r["before_full"] and r["after_full"])
        self.assertEqual((r["op_hours"], r["heat_hours"]), (0, 0))
        self.assertEqual(bc.run_table(frame([U, None, U])).filter(bc.ISOLATED).height, 1)

    def test_two_hours_up_flanked(self):
        (r,) = runs_of(frame([U, None, None, U]))
        self.assertEqual(r["length"], 2)
        self.assertEqual(bc.run_table(frame([U, None, None, U])).filter(bc.STRICT).height, 1)
        self.assertEqual(bc.run_table(frame([U, None, None, U])).filter(bc.ISOLATED).height, 0)

    def test_edge_run_has_no_before(self):
        (r,) = runs_of(frame([None, U, U]))
        self.assertFalse(r["before"] or r["before_up"] or r["before_full"])
        self.assertTrue(r["after"] and r["after_up"])

    def test_gap_splits_runs(self):
        a, b = runs_of(frame([U, None, None, U], hours=[0, 1, 3, 4]))
        self.assertEqual((a["length"], b["length"]), (1, 1))
        self.assertEqual((a["before"], a["after"]), (True, False))
        self.assertEqual((b["before"], b["after"]), (False, True))

    def test_low_flanks_are_not_up(self):
        (r,) = runs_of(frame([LO, None, None, LO]))
        self.assertTrue(r["before"] and r["after"])
        self.assertFalse(r["before_up"] or r["after_up"])

    def test_partial_hour_flank_is_not_full(self):
        (r,) = runs_of(frame([U, None, None, U], op=[0.5, 0.0, 0.0, 1.0]))
        self.assertEqual((r["before_full"], r["after_full"]), (False, True))
        self.assertTrue(r["before_up"] and r["after_up"])

    def test_op_and_heat_hours(self):
        (r,) = runs_of(frame([U, None, None, U], op=[1.0, 1.0, 0.0, 1.0],
                             heat=[9.0, 5.0, None, 9.0]))
        self.assertEqual((r["op_hours"], r["heat_hours"]), (1, 1))

    def test_units_do_not_mix_and_order_does_not_matter(self):
        df = pl.concat([frame([U, None, U], unit=(1, "A")),
                        frame([None, None, U], unit=(1, "B"))]).reverse()
        rows = runs_of(df)
        self.assertEqual([(r["emissions_unit_id_epa"], r["length"], r["before"]) for r in rows],
                         [("A", 1, True), ("B", 2, False)])

    def test_matches_reference_on_random_frames(self):
        rng = random.Random(20261031)
        for _ in range(100):
            rows = mc.random_rows(rng)
            df = mc.cems_frame(rows).with_columns(
                pl.lit(0.0).alias("operating_time_hours"),
                pl.lit(None, dtype=pl.Float64).alias("heat_content_mmbtu"))
            for fill in (False, True):
                want = ref.min_up_down(
                    [((r[0], r[1]), BASE + timedelta(hours=r[2]),
                      None if r[3] is None else (r[3]["left"], r[3]["right"]),
                      None if r[4] is None else (r[4]["left"], r[4]["right"])) for r in rows],
                    fill=fill)
                d = fi.fill_isolated_null_bins(df, UNIT) if fill else df
                got = {(r["plant_id_epa"], r["emissions_unit_id_epa"]): r["length"]
                       for r in bc.run_table(d).group_by(UNIT).agg(
                           pl.col("length").min()).to_dicts()}
                for unit, (_, down) in want.items():
                    self.assertEqual(got.get(unit), down)


class UnitTableTests(unittest.TestCase):
    def setUp(self):
        a = frame([U, None, None, U, None, None, None, None, None, U], unit=(1, "A"))
        b = frame([U, None, None, U], unit=(1, "B"), op=[0.5, 0.0, 0.0, 1.0])
        c = frame([U, U, U], unit=(1, "C"))
        d = frame([U, None, None, U], unit=(1, "D"))
        self.runs = bc.run_table(pl.concat([a, b, c, d]))
        self.out = output([(1, "A"), (1, "B"), (1, "C"), (1, "D")], [2.0, 2.0, None, 2.0])
        self.units = {r["emissions_unit_id_epa"]: r
                      for r in bc.unit_table(self.runs, self.out).to_dicts()}

    def test_counterfactual(self):
        a, b, c, d = (self.units[k] for k in "ABCD")
        self.assertEqual((a["run_min"], a["cf_min"], a["cf_up_min"]), (2, 5, 5))
        self.assertEqual((b["run_min"], b["cf_min"], b["cf_up_min"]), (2, 2, None))
        self.assertIsNone(c["run_min"])
        self.assertEqual((d["cf_min"], d["strict_2h"], d["upflank_2h"]), (None, True, True))
        self.assertEqual((b["strict_2h"], b["upflank_2h"]), (False, True))

    def test_summary_and_score(self):
        s = bc.summarize(bc.unit_table(self.runs, self.out), self.runs)
        self.assertEqual((s["units"], s["run_min_equal"], s["units_with_min"]), (4, 4, 3))
        self.assertEqual((s["at2"], s["le2"], s["at2_upflank"], s["at2_strict"]), (3, 3, 3, 2))
        self.assertEqual((s["cf_strict_le2"], s["cf_upflank_le2"]), (1, 0))
        self.assertEqual(s["cf_strict_buckets"], {"1": 0, "2": 1, "3": 0, "4-9": 1, "10+": 0,
                                                  "none": 1})
        self.assertEqual((s["two_runs"], s["two_runs_hours"], s["two_runs_no_op_hours"]),
                         (3, 6, 6))
        self.assertEqual((s["two_runs_upflank"], s["two_runs_strict"]), (3, 2))
        self.assertEqual((s["runs"], s["run_hours"], s["run_op_hours"]), (4, 11, 0))
        self.assertEqual(s["units_min_runs_op"], 0)
        self.assertEqual(s["isolated_runs"], 0)
        n = dict(s, isolated_runs=10, isolated_no_op_no_heat=10,
                 isolated_counted_by_fill_isolated=10)
        v3 = {"rows": 4, "found": 4, "equal": 4, "units_now": 4}
        sc = bc.score({"modes": {"none": n, "fill": s}, "v3": {"none": v3, "fill": v3}})
        self.assertEqual(sc, {"B0": True, "B1": True, "P0": True, "P1": True, "P2": True,
                              "P3": True, "P4": False, "P5": True})

    def test_score_needs_both_modes(self):
        self.assertEqual(bc.score({"modes": {"fill": {}}}), {})


class V3Tests(unittest.TestCase):
    def test_compare_reads_unit_ids_as_text(self):
        path = os.path.join(tempfile.mkdtemp(prefix="mv2-blank-"), "v3.csv")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("plant_id_epa,emissions_unit_id_epa,state_run,min_down_time_hours,"
                     "min_up_time_hours,min_down_time_hours_fill,min_up_time_hours_fill\n"
                     "1,4,CO,1.0,1.0,2.0,1.0\n1,**5,CO,,,,\n2,B,CO,3.0,1.0,3.0,1.0\n")
        v3 = bc.read_v3(path)
        self.assertEqual(v3["emissions_unit_id_epa"].to_list(), ["4", "**5", "B"])
        now = output([(1, "4"), (1, "**5")], [2.0, None])
        self.assertEqual(bc.compare_v3(now, v3, "min_down_time_hours_fill"),
                         {"rows": 3, "found": 2, "equal": 2, "units_now": 2})
        self.assertEqual(bc.compare_v3(now, v3, "min_down_time_hours")["equal"], 1)


if __name__ == "__main__":
    unittest.main()
