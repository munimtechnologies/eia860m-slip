"""Unit tests for fill_isolated.py and reference.py (need polars; no PUDL).

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.).
"""

import unittest
from datetime import datetime, timedelta

import polars as pl

import fill_isolated as fi
import reference as ref

BASE = datetime(2024, 1, 1)
U = {"left": 0.5, "right": 0.6}
L = {"left": 0.1, "right": 0.2}
BIN = pl.Struct({"left": pl.Float64, "right": pl.Float64})
UNIT = ["plant_id_epa", "emissions_unit_id_epa"]


def frame(bins, hours=None, unit=(1, "A")):
    hours = list(range(len(bins))) if hours is None else hours
    return pl.DataFrame(
        {"plant_id_epa": [unit[0]] * len(bins),
         "emissions_unit_id_epa": [unit[1]] * len(bins),
         "operating_datetime_utc": [BASE + timedelta(hours=h) for h in hours],
         "load_factor_bin": bins},
        schema={"plant_id_epa": pl.Int64, "emissions_unit_id_epa": pl.String,
                "operating_datetime_utc": pl.Datetime("us"), "load_factor_bin": BIN})


def nulls(df):
    return df["load_factor_bin"].is_null().to_list()


class FillTests(unittest.TestCase):
    def test_none_is_a_null_struct(self):
        self.assertEqual(nulls(frame([U, None, U])), [False, True, False])

    def test_isolated_null_takes_previous_bin(self):
        out = fi.fill_isolated_null_bins(frame([U, None, L]), UNIT)
        self.assertEqual(out["load_factor_bin"].to_list(), [U, U, L])

    def test_two_null_hours_stay(self):
        out = fi.fill_isolated_null_bins(frame([U, None, None, U]), UNIT)
        self.assertEqual(nulls(out), [False, True, True, False])

    def test_edges_stay(self):
        out = fi.fill_isolated_null_bins(frame([None, U, U, None]), UNIT)
        self.assertEqual(nulls(out), [True, False, False, True])

    def test_hour_gap_stays(self):
        out = fi.fill_isolated_null_bins(frame([U, None, U], hours=[0, 2, 3]), UNIT)
        self.assertEqual(nulls(out), [False, True, False])

    def test_units_do_not_mix(self):
        df = pl.concat([frame([U, U], unit=(1, "A")), frame([None, U], unit=(1, "B"))])
        out = fi.fill_isolated_null_bins(df.reverse(), UNIT)
        self.assertEqual(nulls(out), [False, False, True, False])
        self.assertEqual(fi.count_isolated_null_bins(df, UNIT), 0)

    def test_shuffled_input_is_sorted_then_filled(self):
        df = frame([U, None, U, None, None, U]).reverse()
        self.assertFalse(fi.is_sorted_hours(df, UNIT))
        out = fi.fill_isolated_null_bins(df, UNIT)
        self.assertTrue(fi.is_sorted_hours(out, UNIT))
        self.assertEqual(nulls(out), [False, False, False, True, True, False])
        self.assertEqual(fi.count_isolated_null_bins(df, UNIT), 1)


class ReferenceTests(unittest.TestCase):
    def rows(self, bins, hours=None, ms=(0.3, 0.4)):
        hours = list(range(len(bins))) if hours is None else hours
        return [("A", BASE + timedelta(hours=h), b, ms) for h, b in zip(hours, bins)]

    def test_cases(self):
        u, lo, n = (0.5, 0.6), (0.1, 0.2), None
        cases = [
            # bins, hours, (min_up, min_down) without fill, with fill
            ([u, u, u, n, u, u, u, u], None, (3, 1), (8, None)),
            ([u, u, n, n, u, u, u, u], None, (2, 2), (2, 2)),
            ([u, u, u, n, u, u, u, u], [0, 1, 2, 4, 5, 6, 7, 8], (3, 1), (3, 1)),
            ([n, u, u, u, u, u, u, u], None, (7, 1), (7, 1)),
            ([u, lo, n, lo, u, u, u, u], None, (1, 1), (1, None)),
        ]
        for bins, hours, plain, filled in cases:
            rows = self.rows(bins, hours)
            self.assertEqual(ref.min_up_down(rows, fill=False)["A"], plain)
            self.assertEqual(ref.min_up_down(rows, fill=True)["A"], filled)

    def test_no_stable_bin_means_no_up_runs(self):
        rows = self.rows([(0.5, 0.6), None, (0.5, 0.6)], ms=None)
        self.assertEqual(ref.min_up_down(rows, fill=False)["A"], (None, 1))


if __name__ == "__main__":
    unittest.main()
