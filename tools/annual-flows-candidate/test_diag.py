"""Tests for diag.py on a hand-traced fixture. MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Reports run 2017-01 to 2019-03.
- 1/A: planned (U) for 2018-06, last record from 2017-11 with valid_until 2018-01, so 0.3.0
  reads it as listed in January 2018 (inclusive end) and 0.2.0 did not (exclusive end).
  Never operates and is gone by February 2019: not_listed in 2018.
- 1/B: same plant, first listed 2018-02, operating from 2018-04: new_entry in 2018.
- 2/C: operating throughout, still listed at the last report.
- 3/D: operating, last listed 2018-06: an exit under every rule.
- 4/E: a retired record, then operating, last listed 2018-03: an exit the id check counts
  and 0.3.0's detection count leaves out.
"""

import os
import tempfile
import unittest

import numpy as np
import pandas as pd

import diag
import eia860m_slip as es


def fixture():
    cols = ["report_date", "valid_until_date", "plant_id_eia", "generator_id", "capacity_mw",
            "current_planned_generator_operating_date", "generator_operating_date",
            "operational_status_code", "technology_description", "plant_name_eia"]
    rows = [
        ("2017-11-01", "2018-01-01", 1, "A", 100.0, "2018-06-01", None, "U",
         "Solar Photovoltaic", "Alpha"),
        ("2018-02-01", "2018-05-01", 1, "B", 100.0, "2018-04-01", None, "U",
         "Solar Photovoltaic", "Alpha"),
        ("2018-05-01", "2019-03-01", 1, "B", 100.0, None, "2018-04-01", "OP",
         "Solar Photovoltaic", "Alpha"),
        ("2017-01-01", "2019-03-01", 2, "C", 50.0, None, "2010-01-01", "OP",
         "Natural Gas Fired Combined Cycle", "Beta"),
        ("2019-03-01", "2019-04-01", 2, "C", 55.0, None, "2010-01-01", "OP",
         "Natural Gas Fired Combined Cycle", "Beta"),
        ("2017-01-01", "2018-06-01", 3, "D", 20.0, None, None, "OP",
         "Conventional Steam Coal", "Gamma"),
        ("2017-01-01", "2017-06-01", 4, "E", 10.0, None, None, "RE",
         "Petroleum Liquids", "Delta"),
        ("2017-06-01", "2018-03-01", 4, "E", 10.0, None, None, "OP",
         "Petroleum Liquids", "Delta"),
    ]
    df = es.prepare(pd.DataFrame(rows, columns=cols))
    old = df.copy()
    old["until_m"] = diag.old_until(df)
    return df, old


class DiagTests(unittest.TestCase):
    def test_old_until(self):
        df, old = fixture()
        a = old[old["key"] == "1/A"].iloc[0]
        self.assertEqual(es.month_str(a["until_m"]), "2017-12")
        self.assertEqual(es.month_str(df[df["key"] == "1/A"].iloc[0]["until_m"]), "2018-01")

    def test_plan_diff(self):
        df, old = fixture()
        rows, gens = diag.plan_diff(df, old, years=(2018,))
        self.assertEqual(rows[0]["planned_030"], 100.0)
        self.assertEqual(rows[0]["planned_020_rule"], 0.0)
        self.assertEqual(rows[0]["ref_020"], 34723.5)
        self.assertEqual((rows[0]["only_030_n"], rows[0]["only_020_n"]), (1, 0))
        g = gens[0]
        self.assertEqual((g["kind"], g["key"], g["plant"], g["mw"]), ("only_030", "1/A", "Alpha",
                                                                      100.0))
        self.assertEqual((g["record_from"], g["valid_until"]), ("2017-11", "2018-01"))
        self.assertTrue(g["last_record"])
        self.assertFalse(g["one_month"])

    def test_rekey(self):
        df, _ = fixture()
        rows, gens = diag.rekey(df, years=(2018,))
        r = rows[0]
        self.assertEqual((r["not_listed_mw"], r["not_listed_at_shared_plant_mw"]), (100.0, 100.0))
        self.assertEqual((r["new_entry_mw"], r["new_entry_at_shared_plant_mw"]), (100.0, 100.0))
        self.assertEqual(r["shared_plants"], 1)
        self.assertEqual(sorted((g["kind"], g["key"]) for g in gens),
                         [("new_entry", "1/B"), ("not_listed", "1/A")])

    def test_exits(self):
        df, _ = fixture()
        ex = diag.exits(df)
        self.assertEqual((ex["idcheck_rule"], ex["v030_exits"], ex["v030_without_retired_record"]),
                         (2, 2, 1))
        self.assertEqual(ex["idcheck_not_v030"], ["4/E"])
        self.assertEqual(ex["v030_not_idcheck"], [])
        self.assertEqual(ex["idcheck_with_retired_record"], ["4/E"])

    def test_text(self):
        self.assertEqual(diag._text(np.nan), "")
        self.assertEqual(diag._text(None), "")
        self.assertEqual(diag._text(pd.NaT), "")
        self.assertEqual(diag._text(pd.NA), "")
        self.assertEqual(diag._text(pd.Timestamp("2018-02-01")), "2018-02-01")
        self.assertEqual(diag._text(50.0), "50.0")
        self.assertEqual(diag._text("Beta"), "Beta")

    def test_records(self):
        df, _ = fixture()
        recs = diag.records(df, plants=(2,))
        self.assertEqual(len(recs), 2)
        self.assertEqual(recs[0]["report_date"], "2017-01-01")
        self.assertEqual(recs[0]["plant_name_eia"], "Beta")
        self.assertEqual(recs[0]["current_planned_generator_operating_date"], "")
        self.assertEqual(len(diag.records(df, plants=(2,), since=2019 * 12 + 2)), 1)
        self.assertEqual(diag.records(df, plants=(728,)), [])

    def test_run_and_render(self):
        df, old = fixture()
        res = diag.run(df, old)
        self.assertEqual(res["report_max"], "2019-03")
        self.assertIn("diag 0.1.2 on eia860m_slip 0.3.0", res["version"])
        text = diag.render(res)
        self.assertIn("## 3. Operating exits", text)
        self.assertIn("In the id check's count only: 4/E", text)


if __name__ == "__main__":
    unittest.main()
