"""Unit tests for pr_check.py (need pandas and the pinned check_fix.py / check_fix2.py).
Apache-2.0. MV2 of Munim, Inc. (made with AI agents)."""

import unittest

import pandas as pd

from pr_check import last_date_counts, pr_source, same_rows, snapshot_reference, \
    zero_or_backwards

SRC = '''import pandas as pd


def _valid_until(changes, series_cols):
    return changes["report_date"]


def other():
    return 1


def make_changelog(df_all, idx):
    return _valid_until(df_all, idx)
'''


def tall(rows):
    return pd.DataFrame({
        "plant_id_eia": [1] * len(rows),
        "report_date": pd.to_datetime([d for d, _ in rows]),
        "column_name": ["state"] * len(rows),
        "record_value": pd.Series([v for _, v in rows], dtype=object),
    })


class PrCheckTests(unittest.TestCase):
    def test_pr_source_takes_both_functions(self):
        src = pr_source(SRC)
        self.assertTrue(src.startswith("def _valid_until("))
        self.assertIn("def make_changelog(", src)
        self.assertNotIn("def other(", src)

    def test_snapshot_reference_keeps_whole_changed_dates(self):
        df = tall([("2026-01-01", "a"), ("2026-01-01", "b"), ("2026-02-01", "b"),
                   ("2026-02-01", "a"), ("2026-03-01", "a"), ("2026-04-01", "a"),
                   ("2026-04-01", "b")])
        kept = snapshot_reference(df, ["plant_id_eia", "column_name"])
        dates = sorted({d.strftime("%m") for d, _ in kept})
        self.assertEqual(dates, ["01", "03", "04"])
        self.assertEqual(len(kept), 5)

    def test_snapshot_reference_missing_values_equal(self):
        df = tall([("2026-01-01", None), ("2026-02-01", float("nan")), ("2026-03-01", "a")])
        kept = snapshot_reference(df, ["plant_id_eia", "column_name"])
        self.assertEqual(sorted(d.strftime("%m") for d, _ in kept), ["01", "03"])

    def test_same_rows(self):
        a = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
        self.assertTrue(same_rows(a, a[["y", "x"]].copy()))
        self.assertFalse(same_rows(a, a.iloc[::-1]))
        self.assertFalse(same_rows(a, a.iloc[:1]))

    def test_zero_or_backwards(self):
        df = pd.DataFrame({"report_date": pd.to_datetime(["2026-01-01"] * 3),
                           "valid_until_date": pd.to_datetime(
                               ["2026-01-01", "2025-12-01", "2026-02-01"])})
        self.assertEqual(zero_or_backwards(df), 2)

    def test_last_date_counts(self):
        # Last date 2026-06-01. G1 unchanged since January: until 2026-06-01. G2 changed on
        # the last date: until 2026-07-01. G3 last seen in March: until 2026-04-01.
        # G4 changed in May, unchanged in June: until 2026-06-01 (the ambiguous month).
        df = pd.DataFrame({
            "plant_id_eia": [1, 1, 1, 1, 1],
            "generator_id": ["G1", "G2", "G2", "G3", "G4"],
            "report_date": pd.to_datetime(["2026-01-01", "2026-01-01", "2026-06-01",
                                           "2026-03-01", "2026-05-01"]),
            "valid_until_date": pd.to_datetime(["2026-06-01", "2026-06-01", "2026-07-01",
                                                "2026-04-01", "2026-06-01"]),
        })
        out = last_date_counts(df)
        self.assertEqual(out["last_report_date"], "2026-06-01")
        self.assertEqual(out["generators"], 4)
        self.assertFalse(out["has_report_date_max"])
        self.assertEqual(out["last_starts_on_last_date"], 1)
        self.assertEqual(out["last_until_last_date_started_before_month_before"], 1)
        self.assertEqual(out["last_until_last_date_started_month_before"], 1)
        self.assertEqual(out["last_until_after_last_date"], 1)
        self.assertEqual(out["generators_covered_on_last_date"], 1)
        self.assertEqual((out["L1_a"], out["L1_b"], out["L1_share"]), (1, 1, 0.5))
        self.assertEqual(out["examples"][0]["generator_id"], "G1")

    def test_last_date_counts_with_report_date_max(self):
        df = pd.DataFrame({
            "plant_id_eia": [1, 1, 1],
            "generator_id": ["G1", "G2", "G3"],
            "report_date": pd.to_datetime(["2026-01-01", "2026-06-01", "2026-05-01"]),
            "valid_until_date": pd.to_datetime(["2026-06-01", "2026-07-01", "2026-06-01"]),
            "report_date_max": pd.to_datetime(["2026-06-01", "2026-06-01", "2026-06-01"]),
        })
        out = last_date_counts(df)
        self.assertTrue(out["has_report_date_max"])
        self.assertEqual(out["reported_on_last_date"], 3)
        self.assertEqual(out["reported_on_last_date_unchanged"], 2)
        self.assertEqual(out["reported_on_last_date_unchanged_until_last_date"], 2)
        self.assertEqual((out["L1_a"], out["L1_b"]), (2, 1))
        self.assertEqual(out["L1_share"], 0.6667)


if __name__ == "__main__":
    unittest.main()
