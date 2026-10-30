"""Unit tests for tall_check.py (need pandas). Apache-2.0. MV2 of Munim, Inc. (made with AI agents)."""

import unittest

import pandas as pd

from tall_check import count_table, id_columns


def frame():
    # plant 1, state: AK and WA both reported in 2020 (the AK row ends the same day),
    # AK again in 2021; plant 2, county: one row per year.
    return pd.DataFrame({
        "plant_id_eia": [1, 1, 1, 2, 2],
        "report_date": pd.to_datetime(
            ["2020-01-01", "2020-01-01", "2021-01-01", "2020-01-01", "2021-01-01"]),
        "valid_until_date": pd.to_datetime(
            ["2020-01-01", "2021-01-01", "2021-02-01", "2021-01-01", "2021-02-01"]),
        "column_name": ["state", "state", "state", "county", "county"],
        "record_value": pd.Series(["AK", "WA", "AK", "X", "Y"], dtype=object),
        "entity_occurrences": [3, 3, 3, 2, 2],
        "consistent_rate": [0.5, 0.5, 1.0, 1.0, 1.0],
        "is_candidate": [False, False, True, True, True],
    })


class TallCheckTests(unittest.TestCase):
    def test_id_columns(self):
        self.assertEqual(id_columns(frame()), ["plant_id_eia"])

    def test_counts(self):
        out = count_table(frame())
        self.assertEqual(out["rows"], 5)
        self.assertEqual(out["zero_length"], 1)
        self.assertEqual(out["zero_length_sharing_series_date"], 1)
        self.assertEqual(out["zero_length_alone_on_series_date"], 0)
        self.assertEqual(out["valid_until_before_report_date"], 0)
        self.assertEqual(out["rows_sharing_series_date"], 2)
        self.assertEqual(out["series_dates"], 4)
        self.assertEqual(out["series_dates_with_several_rows"], 1)
        self.assertEqual(out["series_dates_with_several_values"], 1)
        self.assertEqual(out["zero_length_is_candidate"], 0)
        self.assertEqual(out["examples"][0]["record_value"], "AK")

    def test_zero_length_alone_and_backwards(self):
        df = frame()
        df.loc[3, "valid_until_date"] = pd.Timestamp("2020-01-01")
        df.loc[4, "valid_until_date"] = pd.Timestamp("2020-06-01")
        out = count_table(df)
        self.assertEqual(out["zero_length"], 2)
        self.assertEqual(out["zero_length_alone_on_series_date"], 1)
        self.assertEqual(out["valid_until_before_report_date"], 1)


if __name__ == "__main__":
    unittest.main()
