"""Unit tests for flank_check.py on hand-made frames (need polars, blank_check.py 0.1.0 and the
pinned tools/cems-mindown files; no PUDL, no network).

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.).
"""

import random
import types
import unittest
from datetime import date, datetime, timedelta

import polars as pl

import blank_check as bc
import fill_isolated as fi
import flank_check as fc
import mindown_check as mc

BASE = datetime(2024, 1, 1)
U = {"left": 0.5, "right": 0.6}
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


def flanks(df):
    return fc.flank_table(df).to_dicts()


class BucketTests(unittest.TestCase):
    def test_op_bucket_edges(self):
        got = [fc.op_bucket(v) for v in (None, float("nan"), -0.0, 0.0, 0.25, 0.4999, 0.5,
                                         0.998, 0.999, 1.0)]
        self.assertEqual(got, ["null", "null", "zero", "zero", "lt_half", "lt_half",
                               "half_to_full", "half_to_full", "full", "full"])

    def test_bucket_counts(self):
        self.assertEqual(fc.bucket_counts([None, 0.0, 0.25, 0.75, 1.0, 1.0]),
                         {"null": 1, "zero": 1, "lt_half": 1, "half_to_full": 1, "full": 2,
                          "n": 6, "partial": 2, "partial_share": 0.3333})
        self.assertEqual(fc.bucket_counts([])["partial_share"], None)

    def test_describe(self):
        runs = pl.DataFrame({"before": [True, False, True], "after": [True, True, False],
                             "op_before": [0.5, None, None], "op_after": [1.0, 0.0, None]},
                            schema={"before": pl.Boolean, "after": pl.Boolean,
                                    "op_before": pl.Float64, "op_after": pl.Float64})
        d = fc.describe(runs)
        self.assertEqual(d["runs"], 3)
        self.assertEqual((d["before"]["n"], d["before"]["null"], d["before"]["half_to_full"]),
                         (2, 1, 1))
        self.assertEqual((d["after"]["n"], d["after"]["full"], d["after"]["zero"]), (2, 1, 1))
        self.assertEqual((d["both"]["n"], d["both"]["partial"], d["both"]["partial_share"]),
                         (4, 1, 0.25))


class FlankTableTests(unittest.TestCase):
    def test_two_hour_run(self):
        (r,) = flanks(frame([U, None, None, U], op=[0.5, 0.0, 0.0, 1.0]))
        self.assertEqual((r["length"], r["before"], r["after"]), (2, True, True))
        self.assertEqual((r["op_before"], r["op_after"]), (0.5, 1.0))

    def test_edge_run(self):
        (r,) = flanks(frame([None, U, U], op=[0.0, 0.3, 1.0]))
        self.assertEqual((r["before"], r["op_before"]), (False, None))
        self.assertEqual((r["after"], r["op_after"]), (True, 0.3))

    def test_gap_splits_runs(self):
        a, b = flanks(frame([U, None, None, U], hours=[0, 1, 3, 4], op=[0.2, 0.0, 0.0, 0.9]))
        self.assertEqual((a["length"], a["before"], a["op_before"], a["after"], a["op_after"]),
                         (1, True, 0.2, False, None))
        self.assertEqual((b["length"], b["before"], b["op_before"], b["after"], b["op_after"]),
                         (1, False, None, True, 0.9))

    def test_flank_hour_with_null_operating_time(self):
        (r,) = flanks(frame([U, None, U], op=[None, 0.0, 0.7]))
        self.assertEqual((r["before"], r["op_before"], r["op_after"]), (True, None, 0.7))

    def test_units_do_not_mix_and_order_does_not_matter(self):
        df = pl.concat([frame([U, None, U], unit=(1, "A")),
                        frame([None, None, U], unit=(1, "B"))]).reverse()
        rows = [(r["emissions_unit_id_epa"], r["length"], r["before"], r["op_before"],
                 r["after"], r["op_after"]) for r in flanks(df)]
        self.assertEqual(rows, [("A", 1, True, 1.0, True, 1.0), ("B", 2, False, None, True, 1.0)])

    def test_k1_agrees_with_blank_check_on_random_frames(self):
        rng = random.Random(20261101)
        choices = [None, 0.0, 0.3, 0.6, 0.999, 1.0]
        for _ in range(100):
            df = mc.cems_frame(mc.random_rows(rng))
            df = df.with_columns(
                pl.Series("operating_time_hours", [rng.choice(choices) for _ in range(df.height)],
                          dtype=pl.Float64),
                pl.lit(None, dtype=pl.Float64).alias("heat_content_mmbtu"))
            for d in (df, fi.fill_isolated_null_bins(df, UNIT)):
                k = fc.k1_check(fc.flank_table(d), bc.run_table(d))
                self.assertEqual(k["mismatch"], 0)
                self.assertEqual((k["ft"], k["joined"]), (k["rt"], k["rt"]))

    def test_subsets(self):
        a = frame([U, None, None, U] + [None] * 10 + [U], unit=(1, "A"))
        b = frame([U, None, None, U, None, None, None, U], unit=(1, "B"))
        c = frame([U, None, U], unit=(1, "C"))
        units = output([(1, "A"), (1, "B")], [2.0, 5.0])
        subs, n_at2 = fc.subsets({"fill": fc.flank_table(pl.concat([a, b])),
                                  "none": fc.flank_table(c)}, {"fill": units, "none": units})
        self.assertEqual(n_at2, 1)
        self.assertEqual({k: v.height for k, v in subs.items()},
                         {"two_at2": 1, "two_all": 2, "iso1": 1, "mid3_9": 1, "long10": 1})


class WorkingTests(unittest.TestCase):
    def setUp(self):
        self.w = pl.DataFrame(
            {"plant_id_epa": [1] * 6, "emissions_unit_id_epa": ["A"] * 4 + ["B"] * 2,
             "load_factor_nunique": [3, 3, 3, 3, 0, 0],
             "gross_load_mw": [10.0, None, 20.0, None, None, None],
             "operating_time_hours": [1.0, 0.0, 1.0, 0.5, 1.0, 1.0],
             "heat_content_mmbtu": [5.0, None, 6.0, 2.0, 7.0, 8.0]},
            schema={"plant_id_epa": pl.Int64, "emissions_unit_id_epa": pl.String,
                    "load_factor_nunique": pl.UInt32, "gross_load_mw": pl.Float64,
                    "operating_time_hours": pl.Float64, "heat_content_mmbtu": pl.Float64})

    def test_summary_and_totals(self):
        ws = fc.working_summary(self.w)
        a, b = ws.to_dicts()
        self.assertEqual((a["nunique"], a["hours"], a["null_load_hours"],
                          a["null_load_heat_hours"], a["null_load_op_hours"]), (3, 4, 2, 1, 1))
        self.assertEqual((a["heat_mmbtu"], a["null_load_heat_mmbtu"]), (13.0, 2.0))
        self.assertEqual((b["nunique"], b["hours"], b["null_load_hours"],
                          b["null_load_heat_hours"], b["null_load_op_hours"]), (0, 2, 2, 2, 2))
        self.assertEqual((b["heat_mmbtu"], b["null_load_heat_mmbtu"]), (15.0, 15.0))
        self.assertEqual(fc.working_totals(ws), {
            "units": 2, "units_nunique_le1": 1, "units_nunique_le1_with_heat": 1,
            "null_load_hours": 4, "null_load_heat_hours": 3, "null_load_heat_hours_valid": 1,
            "null_load_op_hours": 3, "heat_mmbtu": 28.0, "heat_mmbtu_nunique_le1": 15.0,
            "null_load_heat_mmbtu": 17.0})

    def test_wrapper_keeps_binning_frame_and_restores(self):
        oc = types.SimpleNamespace()

        def assign(cems_working, unit_cols, load_factor_col):
            return cems_working

        def calc(output_df, cems_with_stable_bins, unit_cols, up_or_down):
            return output_df

        def filt(lf, final_year_quarter, num_quarters, states):
            return lf

        def est(cems, min_stable_consecutive_hours):
            w = oc.assign_groupwise_load_factor_bins(cems_working=cems, unit_cols=UNIT,
                                                     load_factor_col="load_factor")
            return oc.calculate_min_up_or_down_times(output([(1, "A")], [None]), w, UNIT, "down")

        oc.assign_groupwise_load_factor_bins = assign
        oc.calculate_min_up_or_down_times = calc
        oc.filter_cems_for_heat_rate_analysis = filt
        oc.estimate_operational_characteristics_by_unit = est
        df = frame([U, None, U]).with_columns(
            pl.lit(2, dtype=pl.UInt32).alias("load_factor_nunique"),
            pl.Series("gross_load_mw", [5.0, None, 6.0], dtype=pl.Float64))
        sink = []
        out, down = fc.estimate_with_working(oc, df, "CO", "none", sink)
        self.assertEqual(len(sink), 1)
        self.assertEqual(sink[0].columns, fc.WORKING_COLS)
        self.assertEqual(down.height, 3)
        self.assertEqual(out["min_down_time_hours"].to_list(), [None])
        self.assertIs(oc.assign_groupwise_load_factor_bins, assign)
        self.assertIs(oc.calculate_min_up_or_down_times, calc)

    def test_wrapper_restores_on_error(self):
        def assign(*a, **k):
            return None

        def calc(*a, **k):
            return None

        oc = types.SimpleNamespace(assign_groupwise_load_factor_bins=assign,
                                   calculate_min_up_or_down_times=calc)
        with self.assertRaises(AttributeError):
            fc.estimate_with_working(oc, None, "CO", "none", [])
        self.assertIs(oc.assign_groupwise_load_factor_bins, assign)
        self.assertIs(oc.calculate_min_up_or_down_times, calc)


class TypeTests(unittest.TestCase):
    def setUp(self):
        self.xw = pl.DataFrame(
            {"report_year": [2024, 2024, 2024, 2023, 2024],
             "plant_id_epa": [10, 10, 10, 10, 11],
             "emissions_unit_id_epa": ["1", "1", "2", "3", "A"],
             "plant_id_eia": [100, 100, 100, 100, 101],
             "generator_id": ["G1", "G2", "G3", "G4", None]},
            schema={"report_year": pl.Int64, "plant_id_epa": pl.Int64,
                    "emissions_unit_id_epa": pl.String, "plant_id_eia": pl.Int64,
                    "generator_id": pl.String})
        self.gens = pl.DataFrame(
            {"plant_id_eia": [100, 100, 100, 100, 100],
             "generator_id": ["G1", "G1", "G2", "G3", "G3"],
             "report_date": [date(2023, 1, 1), date(2024, 1, 1), date(2024, 1, 1),
                             date(2024, 1, 1), date(2025, 1, 1)],
             "prime_mover_code": ["CT", "CT", "CA", "GT", "ST"],
             "time_cold_shutdown_full_load_code": ["1H", None, "12H", "10M", "OVER"]},
            schema={"plant_id_eia": pl.Int64, "generator_id": pl.String,
                    "report_date": pl.Date, "prime_mover_code": pl.String,
                    "time_cold_shutdown_full_load_code": pl.String})
        self.types = fc.unit_types(self.xw, self.gens, 2024)

    def test_unit_class(self):
        self.assertEqual([fc.unit_class(c) for c in (["GT", "GT"], ["CT", "CA"], ["ST"],
                                                     ["ST", "GT"], [None], [], ["IC"],
                                                     ["GT", None])],
                         ["GT", "CC", "ST", "other", "unmatched", "unmatched", "IC", "GT"])

    def test_start_class(self):
        self.assertEqual([fc.start_class(c) for c in (["10M", "1H"], ["1H", "12H"],
                                                      [None, "XX"], ["OVER"], [])],
                         ["fast", "slow", "unknown", "slow", "unknown"])

    def test_choose_year(self):
        self.assertEqual((fc.choose_year(self.xw, 2025), fc.choose_year(self.xw, 2023)),
                         (2024, 2023))

    def test_clean_casts_ids(self):
        df = pl.DataFrame({"plant_id_epa": [1], "emissions_unit_id_epa": ["**5"]},
                          schema={"plant_id_epa": pl.Int32,
                                  "emissions_unit_id_epa": pl.Categorical})
        self.assertEqual(fc.clean(df).schema,
                         pl.Schema({"plant_id_epa": pl.Int64, "emissions_unit_id_epa": pl.String}))
        self.assertEqual(fc.clean(df)["emissions_unit_id_epa"].to_list(), ["**5"])

    def test_unit_types(self):
        self.assertEqual(self.types.to_dicts(), [
            {"plant_id_epa": 10, "emissions_unit_id_epa": "1", "unit_class": "CC",
             "start_class": "slow", "prime_movers": "CA;CT", "cold_codes": "12H;1H",
             "generators": 2},
            {"plant_id_epa": 10, "emissions_unit_id_epa": "2", "unit_class": "GT",
             "start_class": "fast", "prime_movers": "GT", "cold_codes": "10M",
             "generators": 1}])

    def test_attach_and_summary(self):
        units = output([(10, "1"), (10, "2"), (10, "9"), (10, "8")], [2.0, 3.0, 2.0, None])
        u = fc.attach_types(units, self.types)
        cls = {r["emissions_unit_id_epa"]: (r["unit_class"], r["start_class"])
               for r in u.to_dicts()}
        self.assertEqual(cls, {"1": ("CC", "slow"), "2": ("GT", "fast"),
                               "9": ("unmatched", "unknown"), "8": ("unmatched", "unknown")})
        t = fc.type_summary(u)
        self.assertEqual({k: t[k] for k in ("units_with_min", "unmatched", "at2_units", "ct_at2",
                                            "ge3_units", "ct_ge3", "st_units", "st_at2",
                                            "slow_units", "slow_le2")},
                         {"units_with_min": 3, "unmatched": 1, "at2_units": 1, "ct_at2": 1,
                          "ge3_units": 1, "ct_ge3": 1, "st_units": 0, "st_at2": 0,
                          "slow_units": 1, "slow_le2": 1})
        self.assertEqual(t["by_class"]["CC"],
                         {"units": 1, "at2": 1, "le2": 1, "ge3": 0, "median": 2.0})
        self.assertEqual(t["by_class"]["unmatched"]["units"], 1)
        self.assertEqual((t["by_start"]["fast"]["units"], t["by_start"]["unknown"]["units"]),
                         (1, 1))


class ScoreTests(unittest.TestCase):
    def test_score(self):
        k = {"ft": 5, "rt": 5, "joined": 5, "mismatch": 0}
        result = {
            "k1": {"none": k, "fill": k},
            "counts": {"two_at2_runs": 760, "at2_units": 175},
            "working": {"null_load_heat_hours_valid": 0, "null_load_heat_hours": 12000,
                        "units_nunique_le1_with_heat": 4},
            "flank": {"two_at2": {"both": {"n": 100, "partial": 80}},
                      "iso1": {"both": {"n": 100, "partial": 71}},
                      "long10": {"both": {"n": 10, "partial": 6}}},
            "types": {"units_with_min": 10, "unmatched": 1, "at2_units": 5, "ct_at2": 4,
                      "ge3_units": 3, "ct_ge3": 1, "st_units": 5, "st_at2": 3,
                      "slow_units": 4, "slow_le2": 4},
        }
        self.assertEqual(fc.score(result), {
            "K1": True, "K2": True, "K3": True, "D1": True, "D2": False, "F1": True,
            "F2": True, "F3": False, "U0": True, "U1": True, "U2": True})

    def test_score_bad_k1_and_far_counts(self):
        k = {"ft": 5, "rt": 5, "joined": 5, "mismatch": 1}
        s = fc.score({"k1": {"none": k, "fill": k},
                      "counts": {"two_at2_runs": 700, "at2_units": 178}})
        self.assertEqual(s, {"K1": False, "K2": False})

    def test_score_empty(self):
        self.assertEqual(fc.score({}), {})


if __name__ == "__main__":
    unittest.main()
