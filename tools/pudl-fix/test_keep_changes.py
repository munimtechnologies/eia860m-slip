"""Unit tests for keep_changes.py (need pandas). Apache-2.0. MV2 of Munim, Inc. (made with AI agents)."""

import unittest

import numpy as np
import pandas as pd

from keep_changes import REPLACEMENT, TARGET, keep_changes, patch_source

SERIES = ["plant_id_eia", "generator_id"]


def wide(statuses, months=None, cap=None, index=None):
    months = months or list(range(1, len(statuses) + 1))
    df = pd.DataFrame({
        "plant_id_eia": [1] * len(statuses),
        "generator_id": ["A"] * len(statuses),
        "report_date": pd.to_datetime(["2026-%02d-01" % m for m in months]),
        "operational_status_code": statuses,
    }, index=index)
    if cap is not None:
        df["capacity_mw"] = cap
    return df


def kept(df, series=SERIES):
    return keep_changes(df, series).index.tolist()


class KeepChangesTests(unittest.TestCase):
    def test_return_is_kept(self):
        self.assertEqual(kept(wide(["OP", "OA", "OP"])), [0, 1, 2])

    def test_repeat_is_dropped(self):
        self.assertEqual(kept(wide(["OP", "OP", "OA"])), [0, 2])

    def test_gap_compares_with_previous_reported_date(self):
        self.assertEqual(kept(wide(["OP", "OP"], months=[1, 3])), [0])

    def test_missing_value_that_returns(self):
        df = wide(["OP"] * 4, cap=[np.nan, np.nan, 5.0, np.nan])
        self.assertEqual(kept(df), [0, 2, 3])

    def test_string_na_that_returns(self):
        df = wide(pd.array(["OP", pd.NA, "OP", pd.NA], dtype="string"))
        self.assertEqual(kept(df), [0, 1, 2, 3])

    def test_series_are_independent(self):
        df = pd.DataFrame({
            "plant_id_eia": [1, 1, 1, 1],
            "generator_id": ["A", "B", "A", "B"],
            "report_date": pd.to_datetime(["2026-01-01", "2026-01-01", "2026-02-01", "2026-02-01"]),
            "operational_status_code": ["OP", "OA", "OA", "OA"],
        })
        self.assertEqual(kept(df), [0, 1, 2])

    def test_tall_several_records_per_date(self):
        df = pd.DataFrame({
            "plant_id_eia": [1] * 5,
            "report_date": pd.to_datetime(
                ["2026-01-01", "2026-01-01", "2026-01-01", "2026-02-01", "2026-03-01"]),
            "column_name": ["state"] * 5,
            "record_value": pd.Series(["a", "b", "a", "a", "b"], dtype=object),
        })
        self.assertEqual(kept(df, ["plant_id_eia", "column_name"]), [0, 1, 4])

    def test_index_and_columns_kept(self):
        df = wide(["OP", "OA", "OP"], index=[10, 20, 30])
        out = keep_changes(df, SERIES)
        self.assertEqual(out.index.tolist(), [10, 20, 30])
        self.assertEqual(out.columns.tolist(), df.columns.tolist())

    def test_empty_frame(self):
        df = wide(["OP"]).iloc[0:0]
        self.assertEqual(len(keep_changes(df, SERIES)), 0)

    def test_patch_source(self):
        src = "def make_changelog(df_all, idx):\n" + TARGET + "    return df_changelog\n"
        out = patch_source(src)
        self.assertIn(REPLACEMENT, out)
        self.assertNotIn("drop_duplicates", out)
        with self.assertRaises(ValueError):
            patch_source("def make_changelog(df_all, idx):\n    pass\n")


if __name__ == "__main__":
    unittest.main()
