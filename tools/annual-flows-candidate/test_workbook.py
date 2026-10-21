"""Unit tests for workbook (hand-built sheets and records; every expected value is traced in the
comments).

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.
"""

import math
import unittest

import pandas as pd

import eia860m_slip as es
import workbook as wk

HEAD = ["Plant ID", "Plant Name", "Plant State", "Generator ID", "Nameplate Capacity (MW)",
        "Technology", "Status", "Planned Operation Month", "Planned Operation Year"]


def planned_sheet():
    # Row 0 a title, row 1 the header, rows 2-4 generators, row 5 a note.
    return pd.DataFrame([
        ["Planned generators"] + [None] * 8,
        HEAD,
        [3, "Alpha", "CA", 1, 10.5, "Solar Photovoltaic",
         "(P) Planned for installation, but regulatory approvals not initiated", 8, 2027],
        [3.0, "Alpha", "CA", "GT2", 4.0, "Batteries",
         "(V) Under construction, more than 50 percent complete", 12.0, 2026.0],
        [4, "Beta", "TX", None, 7.0, "Batteries", "(U) Under construction", 1, 2027],
        ["NOTE: a footnote"] + [None] * 8,
    ])


def operating_sheet():
    return pd.DataFrame([
        ["Plant ID", "Generator ID", "Nameplate Capacity (MW)", "Status",
         "Planned Retirement Month", "Planned Retirement Year"],
        [5, "A", 20.0, "(OP) Operating", 6, 2030],
        [3, 1, 1.0, "(OP) Operating", None, None],
    ])


class Sheets(unittest.TestCase):
    def test_planned_sheet(self):
        out = wk.sheet_rows("Planned", planned_sheet())
        # The note's plant id is not a number (dropped); plant 4's blank generator id is kept
        # as "nan", PUDL's key for a missing id.
        self.assertEqual(list(out["key"]), ["3/1", "3/GT2", "4/nan"])   # 3 and 3.0 read "3"
        self.assertEqual(list(out["plant_id_eia"]), [3, 3, 4])
        self.assertEqual(list(out["generator_id"]), ["1", "GT2", "nan"])
        self.assertEqual(list(out["status"]), ["P", "V", "U"])
        self.assertEqual(list(out["capacity_mw"]), [10.5, 4.0, 7.0])
        # 2027 * 12 + 8 - 1 = 24331; 2026 * 12 + 12 - 1 = 24323; 2027 * 12 + 1 - 1 = 24324.
        self.assertEqual(list(out["planned_m"]), [24331.0, 24323.0, 24324.0])
        self.assertEqual(list(out["plant_name_eia"]), ["Alpha", "Alpha", "Beta"])
        self.assertEqual(list(out["state"]), ["CA", "CA", "TX"])
        self.assertEqual(list(out["technology_description"]),
                         ["Solar Photovoltaic", "Batteries", "Batteries"])
        self.assertEqual(list(out["sheet"]), ["Planned", "Planned", "Planned"])

    def test_operating_sheet(self):
        out = wk.sheet_rows("Operating", operating_sheet())
        self.assertEqual(list(out["key"]), ["5/A", "3/1"])
        # Only retirement months: "planned" + "month" is excluded by "retire" -> no planned month.
        self.assertTrue(math.isnan(out["planned_m"].iloc[0]))
        # No plant name, state or technology column.
        self.assertTrue(pd.isna(out["state"].iloc[0]))
        self.assertTrue(pd.isna(out["technology_description"].iloc[0]))
        self.assertEqual(list(out["status"]), ["OP", "OP"])

    def test_no_ids(self):
        self.assertIsNone(wk.sheet_rows("Notes", pd.DataFrame([["text only"]])))

    def test_workbook_frame(self):
        sheets = {"Planned": planned_sheet(), "Operating": operating_sheet(),
                  "Canceled or Postponed": planned_sheet(), "Notes": pd.DataFrame([["text only"]])}
        wb, info, dup = wk.workbook_frame(sheets)
        self.assertEqual(info, {"Planned": 3, "Operating": 2, "Canceled or Postponed": "skipped",
                                "Notes": "no generator ids"})
        # 3/1 is on Planned and Operating: the first (Planned, status P) is kept.
        self.assertEqual(dup, 1)
        self.assertEqual(list(wb["key"]), ["3/1", "3/GT2", "4/nan", "5/A"])
        self.assertEqual(list(wb["status"]), ["P", "V", "U", "OP"])

    def test_puerto_rico_skipped(self):
        # "planned_pr" contains "_pr"; "planned" does not.
        wb, info, dup = wk.workbook_frame({"Planned": planned_sheet(),
                                           "Planned_PR": planned_sheet()})
        self.assertEqual(info, {"Planned": 3, "Planned_PR": "skipped"})
        self.assertEqual((len(wb), dup), (3, 0))

    def test_gen_ids(self):
        # Whole-number ids lose leading zeros, at least one digit stays; others pass unchanged.
        self.assertEqual(wk.gen_id("0011"), "11")
        self.assertEqual(wk.gen_id("06"), "6")
        self.assertEqual(wk.gen_id("0"), "0")
        self.assertEqual(wk.gen_id("00"), "0")
        self.assertEqual(wk.gen_id(6.0), "6")          # norm_id: "6.0" -> "6"
        self.assertEqual(wk.gen_id("06A"), "06A")
        self.assertEqual(wk.gen_id(" GT2 "), "GT2")
        self.assertEqual(wk.gen_id(None), "nan")
        self.assertEqual(wk.gen_id(float("nan")), "nan")
        self.assertEqual(wk.gen_id(""), "nan")

    def test_empty_workbook(self):
        wb, info, dup = wk.workbook_frame({"Notes": pd.DataFrame([["text only"]])})
        self.assertEqual((len(wb), dup), (0, 0))
        self.assertIn("planned_m", wb.columns)


def prepared(rows):
    cols = ["key", "report_m", "until_m", "status", "capacity_mw", "plant_id_eia",
            "generator_id", "plant_name_eia", "state", "technology_description", "planned_m",
            "group"]
    return pd.DataFrame(rows, columns=cols)


def wb_frame(rows):
    return pd.DataFrame(rows, columns=list(wk.NEW_COLS))


class Extend(unittest.TestCase):
    def setUp(self):
        nan = float("nan")
        # r = 100. 1/A is in force through 100 in the full file; 1/B ended at 99; 2/X has a
        # record of month 100 itself (dropped) and an older one in force to 99.
        self.df = prepared([
            ["1/A", 98.0, 100.0, "U", 10.0, 1, "A", "P1", "CA", "Solar Photovoltaic", 103.0, "solar"],
            ["1/B", 97.0, 99.0, "P", 5.0, 1, "B", "P1", "CA", "Batteries", 110.0, "battery"],
            ["2/X", 95.0, 99.0, "T", 3.0, 2, "X", "P2", "TX", "Batteries", 104.0, "battery"],
            ["2/X", 100.0, 100.0, "OP", 3.0, 2, "X", "P2", "TX", "Batteries", nan, "battery"],
        ])
        self.wb = wb_frame([
            ["1/A", 1, "A", "P1", "CA", "Solar Photovoltaic", "U", 10.0, 105.0],
            ["3/N", 3, "N", "P3", "NY", "Batteries", "P", 2.0, 112.0],
        ])

    def test_rows(self):
        ext = wk.extend(self.df, self.wb, 100)
        # 3 old records (2/X's month-100 record dropped) + 2 new.
        self.assertEqual(len(ext), 5)
        old = ext[ext["report_m"] < 100]
        self.assertEqual(list(old["until_m"]), [99.0, 99.0, 99.0])   # 100 capped at 99
        new = ext[ext["report_m"] == 100]
        self.assertEqual(list(new["key"]), ["1/A", "3/N"])
        self.assertEqual(list(new["until_m"]), [100.0, 100.0])
        self.assertEqual(list(new["group"]), ["solar", "battery"])   # es.tech_group

    def test_snapshots(self):
        ext = wk.extend(self.df, self.wb, 100)
        # Report 100: the two workbook generators; 1/B and 2/X end at 99.
        s100 = es.snapshot(ext, 100)
        self.assertEqual(sorted(s100["key"]), ["1/A", "3/N"])
        self.assertEqual(float(s100.loc[s100["key"] == "1/A", "planned_m"].iloc[0]), 105.0)
        # Report 99: PUDL's records; 3/N is first reported in 100.
        s99 = es.snapshot(ext, 99)
        self.assertEqual(sorted(s99["key"]), ["1/A", "1/B", "2/X"])
        self.assertEqual(s99.loc[s99["key"] == "2/X", "status"].iloc[0], "T")


def raw_pudl():
    # Report months 2026-06 to 2026-08, all batteries. 1/A: U, planned 2026-10, re-filed in
    # August with planned 2026-12 (delayed). 1/B: P, last listed July (left in August).
    # 2/C: T, first listed August (new). 3/D: V in June, operating from July.
    cols = ["report_date", "valid_until_date", "plant_id_eia", "generator_id", "capacity_mw",
            "current_planned_generator_operating_date", "operational_status_code",
            "technology_description", "state", "plant_name_eia"]
    rows = [
        ["2026-06-01", "2026-08-01", 1, "A", 100.0, "2026-10-01", "U", "Batteries", "CA", "One"],
        ["2026-08-01", None, 1, "A", 100.0, "2026-12-01", "U", "Batteries", "CA", "One"],
        ["2026-06-01", "2026-07-01", 1, "B", 50.0, "2027-06-01", "P", "Batteries", "CA", "One"],
        ["2026-08-01", None, 2, "C", 30.0, "2027-01-01", "T", "Batteries", "TX", "Two"],
        ["2026-06-01", "2026-07-01", 3, "D", 20.0, "2026-07-01", "V", "Batteries", "NY", "Three"],
        ["2026-07-01", None, 3, "D", 20.0, None, "OP", "Batteries", "NY", "Three"],
    ]
    return pd.DataFrame(rows, columns=cols)


class Edition(unittest.TestCase):
    def test_same_as_pudl(self):
        df = es.prepare(raw_pudl())
        r = 2026 * 12 + 7  # August 2026 = 24319
        self.assertEqual(int(df["report_m"].max()), r)
        # August's workbook: 1/A (planned 2026-12 = 24323), 2/C (2027-01 = 24324), 3/D operating.
        wb = wb_frame([
            ["1/A", 1, "A", "One", "CA", "Batteries", "U", 100.0, 24323.0],
            ["2/C", 2, "C", "Two", "TX", "Batteries", "T", 30.0, 24324.0],
            ["3/D", 3, "D", "Three", "NY", "Batteries", "OP", 20.0, float("nan")],
        ])
        ref, _, _ = wk.edition(df, r, "PUDL")
        got, res, meta = wk.edition(wk.extend(df, wb, r), r, "test")
        want = {"1/A": "delayed", "1/B": "left", "2/C": "new"}
        self.assertEqual({x["key"]: x["change"] for x in ref}, want)
        self.assertEqual({x["key"]: x["change"] for x in got}, want)
        # 1/A moved from 2026-10 (24321) to 2026-12 (24323).
        self.assertEqual([x["shift_months"] for x in got if x["key"] == "1/A"], [2])
        self.assertTrue(res["checks"]["all_pass"])
        self.assertEqual((meta["report"], meta["previous"], meta["rekey_pairs"]),
                         ("2026-08", "2026-07", 0))   # 1/B's generator id B is not C
        c = wk.compare_editions(ref, got)
        self.assertEqual((c["union"], c["same_change"], c["same_share"], c["usable"]),
                         (3, 3, 1.0, True))
        self.assertEqual(c["pudl_rows_same_share"], 1.0)

    def test_detail(self):
        df = es.prepare(raw_pudl())
        r = 2026 * 12 + 7  # 24319; records reported 24316 (May) to 24319 are shown
        wb = wb_frame([["1/A", 1, "A", "One", "CA", "Batteries", "U", 100.0, 24323.0]])
        d = wk.detail(df, wb, ["1/A", "9/Z"], r)
        self.assertEqual([x["key"] for x in d], ["1/A", "9/Z"])
        # 1/A's June record ends at its successor's report (August, exclusive) -> until July;
        # its August record has no end and runs to the last report, August.
        self.assertEqual(d[0]["pudl"], [
            {"report": "2026-06", "valid_until": "2026-08", "until": "2026-07", "status": "U",
             "planned": "2026-10", "mw": 100.0},
            {"report": "2026-08", "valid_until": None, "until": "2026-08", "status": "U",
             "planned": "2026-12", "mw": 100.0}])
        # wb_frame has no sheet column -> None; 24323 = 2026-12.
        self.assertEqual(d[0]["workbook"], {"sheet": None, "status": "U", "planned": "2026-12",
                                            "mw": 100.0})
        self.assertEqual(d[1], {"key": "9/Z", "pudl": [], "workbook": None})


class Compare(unittest.TestCase):
    def test_differences(self):
        ref = [{"key": "1/A", "change": "delayed", "mw": 10.0},
               {"key": "1/B", "change": "left", "mw": 5.0},
               {"key": "2/C", "change": "new", "mw": 3.0}]
        got = [{"key": "1/A", "change": "delayed", "mw": 10.0},
               {"key": "1/B", "change": "exit_other", "mw": 5.0},
               {"key": "2/C", "change": "new", "mw": 3.2},
               {"key": "4/D", "change": "new", "mw": 1.0}]
        c = wk.compare_editions(ref, got)
        # Union 4; 1/A and 2/C have the same change, 1/B and 4/D do not.
        self.assertEqual((c["pudl_rows"], c["workbook_rows"], c["union"]), (3, 4, 4))
        self.assertEqual((c["same_change"], c["same_share"], c["usable"]), (2, 0.5, False))
        # 2 of PUDL's 3 rows have the same change: round(0.6666..., 4) = 0.6667.
        self.assertEqual(c["pudl_rows_same_share"], 0.6667)
        # 2/C: 3.2 - 3.0 = 0.2 > 0.05.
        self.assertEqual(c["same_change_mw_differs"], 1)
        self.assertEqual(c["mw_sample"], [{"key": "2/C", "pudl": 3.0, "workbook": 3.2}])
        self.assertEqual(c["differences"], {"left -> exit_other": 1, "none -> new": 1})
        self.assertEqual([x["key"] for x in c["difference_sample"]], ["1/B", "4/D"])
        self.assertEqual(c["by_change"]["new"], [1, 2])
        self.assertEqual(c["by_change"]["left"], [1, 0])
        self.assertEqual(c["by_change"]["delayed"], [1, 1])

    def test_edges(self):
        rows = [{"key": "1/A", "change": "new", "mw": 1.0}]
        self.assertTrue(wk.compare_editions(rows, rows)["usable"])
        self.assertEqual(wk.compare_editions(rows, rows)["pudl_rows_same_share"], 1.0)
        c = wk.compare_editions([], [])
        self.assertEqual((c["union"], c["same_share"], c["usable"]), (0, None, False))
        self.assertIsNone(c["pudl_rows_same_share"])


if __name__ == "__main__":
    unittest.main()
