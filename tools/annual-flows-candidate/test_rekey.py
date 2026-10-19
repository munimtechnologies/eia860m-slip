"""Tests for rekey.py on a hand-traced fixture. MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Reports run 2017-01 to 2019-03 (the last report is 2019-03, from 2/C's second record).
- 1/A: planned (U) for 2018-06, last record from 2017-11 ending 2018-01, so 0.3.0 reads it as
  listed in January 2018. Never operates: not_listed in 2018, last listed 2018-01.
- 9/B: a different plant with the same name, first listed 2018-02, operating from 2018-04,
  100.0 MW: a new_entry in 2018 one month after 1/A's last month, same capacity -> pass A.
- 5/G: planned (U) for 2018-09, 200.0 MW, last record 2017-12 ending 2018-01: not_listed.
- 6/H: first listed 2018-04, operating from 2018-10, 192.0 MW: a new_entry three months after
  5/G, 4% smaller -> pass B, not pass A.
- 7/J: operating from 2018-03, 30 MW, first listed 2018-03: a new_entry with no counterpart.
- 2/C: operating throughout; in no plan and in no year's additions.
"""

import unittest

import numpy as np
import pandas as pd

import eia860m_slip as es
import rekey

COLS = ["report_date", "valid_until_date", "plant_id_eia", "generator_id", "capacity_mw",
        "current_planned_generator_operating_date", "generator_operating_date",
        "operational_status_code", "technology_description", "plant_name_eia"]
ROWS = [
    ("2017-11-01", "2018-01-01", 1, "A", 100.0, "2018-06-01", None, "U",
     "Solar Photovoltaic", "Alpha"),
    ("2018-02-01", "2018-05-01", 9, "B", 100.0, "2018-04-01", None, "U",
     "Solar Photovoltaic", "ALPHA"),
    ("2018-05-01", "2019-03-01", 9, "B", 100.0, None, "2018-04-01", "OP",
     "Solar Photovoltaic", "ALPHA"),
    ("2017-01-01", "2019-03-01", 2, "C", 50.0, None, "2010-01-01", "OP",
     "Natural Gas Fired Combined Cycle", "Beta"),
    ("2019-03-01", "2019-04-01", 2, "C", 55.0, None, "2010-01-01", "OP",
     "Natural Gas Fired Combined Cycle", "Beta"),
    ("2017-12-01", "2018-01-01", 5, "G", 200.0, "2018-09-01", None, "U",
     "Natural Gas Fired Combined Cycle", "Gamma"),
    ("2018-04-01", "2018-11-01", 6, "H", 192.0, "2018-10-01", None, "U",
     "Natural Gas Fired Combined Cycle", "Hotel"),
    ("2018-11-01", "2019-03-01", 6, "H", 192.0, None, "2018-10-01", "OP",
     "Natural Gas Fired Combined Cycle", "Hotel"),
    ("2018-03-01", "2019-03-01", 7, "J", 30.0, None, "2018-03-01", "OP",
     "Solar Photovoltaic", "Juliet"),
]


def fixture():
    return es.prepare(pd.DataFrame(ROWS, columns=COLS))


class RekeyTests(unittest.TestCase):
    def test_listing(self):
        info = rekey.listing(fixture())
        a = info.loc["1/A"]
        self.assertEqual((es.month_str(a["first_m"]), es.month_str(a["last_m"]), a["name"]),
                         ("2017-11", "2018-01", "Alpha"))
        b = info.loc["9/B"]
        self.assertEqual((es.month_str(b["first_m"]), es.month_str(b["last_m"])),
                         ("2018-02", "2019-03"))
        self.assertEqual(es.month_str(info.loc["5/G", "last_m"]), "2018-01")
        self.assertEqual(es.month_str(info.loc["6/H", "first_m"]), "2018-04")

    def test_2018(self):
        res = rekey.run(fixture(), years=(2018,))
        r = res["years"][0]
        self.assertEqual((r["not_listed_mw"], r["not_listed_n"]), (300.0, 2))
        self.assertEqual((r["new_entry_mw"], r["new_entry_n"]), (322.0, 3))
        self.assertEqual((r["strict_pairs"], r["strict_mw"]), (1, 100.0))
        self.assertEqual((r["loose_pairs"], r["loose_mw"], r["loose_entry_mw"]), (1, 200.0, 192.0))
        self.assertEqual(r["matched_share"], 1.0)
        self.assertEqual((r["cross_plant_pairs"], r["same_name_pairs"]), (2, 1))
        pa = [p for p in res["pairs"] if p["pass"] == "A"]
        pb = [p for p in res["pairs"] if p["pass"] == "B"]
        self.assertEqual(len(pa), 1)
        self.assertEqual(len(pb), 1)
        a, b = pa[0], pb[0]
        self.assertEqual((a["dropped"], a["entry"], a["dropped_plant"], a["entry_plant"]),
                         ("1/A", "9/B", "Alpha", "ALPHA"))
        self.assertEqual((a["dropped_mw"], a["entry_mw"], a["months_apart"]), (100.0, 100.0, 1))
        self.assertEqual((a["last_listed"], a["first_listed"]), ("2018-01", "2018-02"))
        self.assertEqual((a["same_plant"], a["same_name"], a["group"]), (False, True, "solar"))
        self.assertEqual((b["dropped"], b["entry"], b["months_apart"]), ("5/G", "6/H", 3))
        self.assertEqual((b["dropped_mw"], b["entry_mw"], b["same_name"]), (200.0, 192.0, False))
        pooled = res["pooled"]
        self.assertEqual((pooled["year"], pooled["not_listed_mw"], pooled["strict_pairs"]),
                         ("all", 300.0, 1))
        self.assertEqual(pooled["matched_share"], 1.0)
        keys = sorted({r["plant_id_eia"] + "/" + r["generator_id"] for r in res["records"]})
        self.assertEqual(keys, ["1/A", "5/G", "6/H", "9/B"])
        self.assertEqual(len(res["records"]), 6)

    def test_empty_year(self):
        res = rekey.run(fixture(), years=(2017,))
        r = res["years"][0]
        self.assertEqual((r["not_listed_mw"], r["new_entry_mw"], r["strict_pairs"]), (0.0, 0.0, 0))
        self.assertIsNone(r["matched_share"])
        self.assertEqual(res["pairs"], [])
        self.assertEqual(res["records"], [])

    def test_no_name_column(self):
        df = fixture().drop(columns=["plant_name_eia"])
        res = rekey.run(df, years=(2018,))
        self.assertEqual(res["years"][0]["strict_pairs"], 1)
        self.assertEqual(res["years"][0]["same_name_pairs"], 0)

    def test_text(self):
        self.assertEqual(rekey._text(np.nan), "")
        self.assertEqual(rekey._text(pd.NaT), "")
        self.assertEqual(rekey._text(pd.Timestamp("2018-02-01")), "2018-02-01")
        self.assertEqual(rekey._text("Beta"), "Beta")

    def test_render(self):
        res = rekey.run(fixture(), years=(2018,))
        self.assertIn("rekey 0.1.0 on eia860m_slip 0.3.0", res["version"])
        self.assertEqual(res["report_max"], "2019-03")
        text = rekey.render(res)
        self.assertIn("## 1. Per year", text)
        self.assertIn("## 2. Pairs, pass A (strict)", text)
        self.assertIn("| 1/A | Alpha | 9/B | ALPHA |", text)
        self.assertIn("## 4. Raw records of the 2018 pairs", text)


if __name__ == "__main__":
    unittest.main()
