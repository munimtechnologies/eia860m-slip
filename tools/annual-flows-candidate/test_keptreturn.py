"""Tests for keptreturn.py on a hand-built changelog with known kept returns.
MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import tempfile
import unittest

import pandas as pd

import keptreturn as kr

NAN = float("nan")


def frame():
    t = pd.Timestamp
    rows = [
        # 1/A: OP, OA, then OP again with a new longitude -> kept return, longitude differs.
        (1, "A", "2020-01-01", "OP", None, 10.0, -1.0, NAN),
        (1, "A", "2020-02-01", "OA", None, 10.0, -1.0, NAN),
        (1, "A", "2020-03-01", "OP", None, 10.0, -1.5, NAN),
        # 2/B: summer 5 -> 4 (same projection, not a return), OA, OP again with summer 3:
        # latest earlier OP record is the summer-4 one -> summer_capacity_mw differs.
        (2, "B", "2021-01-01", "OP", None, 5.0, NAN, 5.0),
        (2, "B", "2021-02-01", "OP", None, 5.0, NAN, 4.0),
        (2, "B", "2021-03-01", "OA", None, 5.0, NAN, 4.0),
        (2, "B", "2021-04-01", "OP", None, 5.0, NAN, 3.0),
        # 3/C: planned month changes and comes back while longitude goes from missing to 2.0.
        (3, "C", "2022-01-01", "P", "2023-01-01", 7.0, NAN, NAN),
        (3, "C", "2022-02-01", "P", "2023-06-01", 7.0, NAN, NAN),
        (3, "C", "2022-03-01", "P", "2023-01-01", 7.0, 2.0, NAN),
        # 4/D: one record.
        (4, "D", "2020-01-01", "OP", None, 1.0, NAN, NAN),
    ]
    df = pd.DataFrame(rows, columns=["plant_id_eia", "generator_id", "report_date", "operational_status_code",
                                     "current_planned_generator_operating_date", "capacity_mw", "longitude",
                                     "summer_capacity_mw"])
    df["report_date"] = pd.to_datetime(df["report_date"])
    df["valid_until_date"] = df["report_date"] + pd.DateOffset(months=1)
    df["current_planned_generator_operating_date"] = pd.to_datetime(df["current_planned_generator_operating_date"])
    # Shuffled, so census must sort.
    return df.iloc[::-1].reset_index(drop=True)


class SameTests(unittest.TestCase):
    def test_same(self):
        self.assertTrue(kr.same(NAN, NAN))
        self.assertTrue(kr.same(pd.NaT, None))
        self.assertFalse(kr.same(NAN, 1.0))
        self.assertFalse(kr.same(None, "a"))
        self.assertTrue(kr.same("a", "a"))
        self.assertTrue(kr.same(pd.Timestamp("2020-01-01"), pd.Timestamp("2020-01-01")))
        self.assertFalse(kr.same(-121.941009, -121.941))


class CensusTests(unittest.TestCase):
    def test_counts(self):
        r = kr.census(frame(), ("2/B", "9/Z"))
        self.assertEqual((r["records"], r["generators"], r["returns"], r["no_diff"], r["last_record"]),
                         (11, 4, 3, 0, 3))
        self.assertEqual(r["columns"], [{"value": "longitude", "n": 2}, {"value": "summer_capacity_mw", "n": 1}])
        self.assertEqual(r["sets"], [{"value": "longitude", "n": 2}, {"value": "summer_capacity_mw", "n": 1}])
        self.assertEqual(r["years"], [{"year": "2020", "n": 1}, {"year": "2021", "n": 1}, {"year": "2022", "n": 1}])
        self.assertEqual(r["months"], [{"value": "2020-03", "n": 1}, {"value": "2021-04", "n": 1},
                                       {"value": "2022-03", "n": 1}])
        self.assertEqual(r["examples"], {"2/B": [{"month": "2021-04", "status": "OP", "earlier": "2021-02",
                                                  "diff": ["summer_capacity_mw"]}], "9/Z": []})

    def test_main_and_render(self):
        with tempfile.TemporaryDirectory() as d:
            data, out = os.path.join(d, "data"), os.path.join(d, "out")
            os.makedirs(data)
            frame().to_parquet(os.path.join(data, "core_eia860m__changelog_generators.parquet"))
            res = kr.main(["--data-dir", data, "--out-dir", out, "--key", "1/A"])
            self.assertEqual(res["pudl"]["max_report"], "2022-03")
            self.assertEqual(res["pudl"]["rows"], 11)
            md = open(os.path.join(out, "keptreturn.md"), encoding="utf-8").read()
            self.assertIn("Kept returns: 3 (no differing column: 0; the generator's last record: 3).", md)
            self.assertIn("| 2020-03 | OP | 2020-01 | longitude |", md)
            self.assertTrue(os.path.exists(os.path.join(out, "keptreturn.json")))
        with tempfile.TemporaryDirectory() as d:
            res = kr.main(["--data-dir", d, "--out-dir", d])
            self.assertIn("error", res)
            self.assertIn("Not run:", kr.render(res))


if __name__ == "__main__":
    unittest.main()
