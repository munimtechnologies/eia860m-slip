"""Tests for leadtime.py on a hand-built changelog, every expected value traced by hand (the
arithmetic is in the comments). MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import json
import os
import tempfile
import unittest

import pandas as pd

import leadtime as lt


def m(year, month):
    return year * 12 + month - 1


def changelog():
    """EIA-860M records: report, valid until, plant, generator, MW, status, technology, planned
    operating month, operating date. Last report: December 2020 (9/Z), so the last report
    month with a closed 24-month window is 2020-12 minus 38 months = 2017-10.

    1/A  solar 100 MW: P Jan-Jun 2016 and U Jul 2016-Feb 2017, both planned 2017-06; OP from
         Mar 2017 (operating date 2017-03-15, so online 2017-03, 3 months early -> on time).
         P rows: Jan-Jun 2016, leads 17..12 (five in 13-24, one in 07-12).
         U rows: Jul 2016-Feb 2017, leads 11..4 (five in 07-12, three in 04-06).
    2/B  wind 50 MW: V Jan-Mar 2016 planned 2016-02 (rows Jan-Feb, leads 1, 0); V from Apr 2016
         planned 2016-08 (rows Apr-Aug, leads 4..0); never online -> not online.
         V rows: six in 00-03, one in 04-06.
    3/C  battery 20 MW: T May-Oct 2016 planned 2017-01 (rows May-Oct, leads 8..3: two in 07-12,
         three in 04-06, one in 00-03); U Nov 2016-May 2017 planned 2017-04 (rows Nov-Apr,
         leads 5..0: two in 04-06, four in 00-03); OP from Jun 2017 with no operating date, so
         online 2017-06: 5 months after 2017-01 (late_4_6) and 2 after 2017-04 (late_1_3).
    4/D  gas CC 500 MW: L from Jun 2017 planned 2019-06 (closed: 2019-06 + 14 = 2020-08 <=
         2020-12). Rows Jun 2017-Jun 2019 (25), but only Jun-Oct 2017 are at or before the
         window's end 2017-10: five rows, leads 24..20, all 13-24; never online.
    5/E  solar 10 MW: P from Jan 2016 planned 2020-01: 2020-01 + 14 = 2021-03 > 2020-12, the
         window is open, so no rows.
    6/F  solar 30 MW: TS Jan-Feb 2017 planned 2017-01 (one row, Jan 2017, lead 0); OP from Mar
         2017 with operating date 2017-02-10 -> online 2017-02, 1 month late (late_1_3).
    8/H  wind 40 MW: V Jan-Oct 2016 planned 2017-10 (rows Jan-Oct 2016, leads 21..12: nine in
         13-24, one in 07-12); OP from Nov 2016 (operating date 2016-11-01) -> on time.
    10/J solar 60 MW: P Mar-Jun 2016 planned 2016-05 (rows Mar-May, leads 2, 1, 0); CN from
         Jul 2016; never online -> not online.
    9/Z  1 MW, OP from Dec 2020: sets the last report; never planned.

    Rows: 1/A 14, 2/B 7, 3/C 12, 4/D 5 (of 25), 6/F 1, 8/H 10, 10/J 3 = 52; MW 1,400 + 350 +
    240 + 2,500 + 30 + 400 + 180 = 5,100; 7 generators.
    """
    recs = [
        ("2016-01-01", "2016-07-01", 1, "A", 100.0, "P", "Solar Photovoltaic", "2017-06-01", None),
        ("2016-07-01", "2017-03-01", 1, "A", 100.0, "U", "Solar Photovoltaic", "2017-06-01", None),
        ("2017-03-01", None, 1, "A", 100.0, "OP", "Solar Photovoltaic", None, "2017-03-15"),
        ("2016-01-01", "2016-04-01", 2, "B", 50.0, "V", "Onshore Wind Turbine", "2016-02-01", None),
        ("2016-04-01", None, 2, "B", 50.0, "V", "Onshore Wind Turbine", "2016-08-01", None),
        ("2016-05-01", "2016-11-01", 3, "C", 20.0, "T", "Batteries", "2017-01-01", None),
        ("2016-11-01", "2017-06-01", 3, "C", 20.0, "U", "Batteries", "2017-04-01", None),
        ("2017-06-01", None, 3, "C", 20.0, "OP", "Batteries", None, None),
        ("2017-06-01", None, 4, "D", 500.0, "L", "Natural Gas Fired Combined Cycle", "2019-06-01",
         None),
        ("2016-01-01", None, 5, "E", 10.0, "P", "Solar Photovoltaic", "2020-01-01", None),
        ("2017-01-01", "2017-03-01", 6, "F", 30.0, "TS", "Solar Photovoltaic", "2017-01-01", None),
        ("2017-03-01", None, 6, "F", 30.0, "OP", "Solar Photovoltaic", None, "2017-02-10"),
        ("2016-01-01", "2016-11-01", 8, "H", 40.0, "V", "Onshore Wind Turbine", "2017-10-01", None),
        ("2016-11-01", None, 8, "H", 40.0, "OP", "Onshore Wind Turbine", None, "2016-11-01"),
        ("2016-03-01", "2016-07-01", 10, "J", 60.0, "P", "Solar Photovoltaic", "2016-05-01", None),
        ("2016-07-01", None, 10, "J", 60.0, "CN", "Solar Photovoltaic", None, None),
        ("2020-12-01", None, 9, "Z", 1.0, "OP", "Solar Photovoltaic", None, None)]
    raw = pd.DataFrame(recs, columns=["report_date", "valid_until_date", "plant_id_eia",
                                      "generator_id", "capacity_mw", "operational_status_code",
                                      "technology_description",
                                      "current_planned_generator_operating_date",
                                      "generator_operating_date"])
    return lt.es.prepare(raw)


LAST = m(2020, 12)


def built():
    df = changelog()
    c = lt.rows(df, LAST)
    return df, c


def by_cell(cell_rows):
    return {(r["stage"], r["band"]): r for r in cell_rows}


class LeadTimeTests(unittest.TestCase):
    def test_band(self):
        self.assertEqual([lt.band(x) for x in (0, 3, 4, 6, 7, 12, 13, 24, 25, -1)],
                         ["00-03", "00-03", "04-06", "04-06", "07-12", "07-12", "13-24", "13-24",
                          None, None])

    def test_end_month(self):
        # 2020-12 minus 24 + 12 + 2 = 38 months is 2017-10.
        self.assertEqual(lt.end_month(LAST), m(2017, 10))
        self.assertEqual(lt.es.month_str(lt.end_month(LAST)), "2017-10")

    def test_rows(self):
        _, c = built()
        self.assertEqual(len(c), 52)
        self.assertEqual(round(float(c["mw"].sum()), 1), 5100.0)
        self.assertEqual(sorted(set(c["key"])), ["1/A", "10/J", "2/B", "3/C", "4/D", "6/F", "8/H"])
        # 4/D: 25 rows in the cohort, 5 inside the window (Jun-Oct 2017), leads 24..20.
        d = c[c["key"] == "4/D"].sort_values("report_m")
        self.assertEqual([int(x) for x in d["report_m"]], [m(2017, i) for i in range(6, 11)])
        self.assertEqual([int(x) for x in d["lead"]], [24, 23, 22, 21, 20])
        self.assertEqual(set(d["band"]), {"13-24"})
        self.assertEqual(set(d["stage_group"]), {"early"})
        self.assertEqual(set(d["outcome"]), {"not_online_12"})
        # 1/A: P rows Jan-Jun 2016 (leads 17..12), U rows Jul 2016-Feb 2017 (leads 11..4).
        a = c[c["key"] == "1/A"].sort_values("report_m")
        self.assertEqual([int(x) for x in a["lead"]], list(range(17, 3, -1)))
        self.assertEqual(list(a["stage_group"]), ["early"] * 6 + ["U"] * 8)
        self.assertEqual(set(a["outcome"]), {"on_time"})
        # 3/C: T rows late_4_6 (online 2017-06, planned 2017-01), U rows late_1_3 (planned 2017-04).
        cc = c[c["key"] == "3/C"]
        self.assertEqual(set(cc.loc[cc["stage_group"] == "approved", "outcome"]), {"late_4_6"})
        self.assertEqual(set(cc.loc[cc["stage_group"] == "U", "outcome"]), {"late_1_3"})
        self.assertEqual(int(c.duplicated(["key", "report_m"]).sum()), 0)
        self.assertEqual(int(c["report_m"].max()), m(2017, 10))

    def test_cells(self):
        _, c = built()
        cells = by_cell(lt.cells(c))
        self.assertEqual(len(cells), 24)
        # early 13-24: 1/A five rows x 100 MW on time + 4/D five rows x 500 MW not online:
        # 500 / 3,000 = 0.1667 on time, 2,500 / 3,000 = 0.8333 not online; 5 of 10 rows on time.
        e = cells[("early", "13-24")]
        self.assertEqual((e["rows"], e["generators"], e["mw"], e["on_time_share"],
                          e["late_share"], e["not_online_share"], e["on_time_count_share"],
                          e["adds_up"]),
                         (10, 2, 3000.0, 0.1667, 0.0, 0.8333, 0.5, True))
        # early 07-12: 1/A's lead-12 row only.
        self.assertEqual((cells[("early", "07-12")]["rows"], cells[("early", "07-12")]["mw"],
                          cells[("early", "07-12")]["on_time_share"]), (1, 100.0, 1.0))
        # early 04-06: nobody.
        self.assertEqual((cells[("early", "04-06")]["rows"], cells[("early", "04-06")]["mw"],
                          cells[("early", "04-06")]["on_time_share"],
                          cells[("early", "04-06")]["on_time_count_share"]), (0, 0.0, None, None))
        # early 00-03: 10/J three rows x 60 MW, not online.
        self.assertEqual((cells[("early", "00-03")]["rows"], cells[("early", "00-03")]["mw"],
                          cells[("early", "00-03")]["on_time_share"],
                          cells[("early", "00-03")]["not_online_share"]), (3, 180.0, 0.0, 1.0))
        # approved: 3/C's T rows, all late: 2 rows / 40 MW, 3 / 60, 1 / 20.
        for b, n, mw in (("07-12", 2, 40.0), ("04-06", 3, 60.0), ("00-03", 1, 20.0)):
            a = cells[("approved", b)]
            self.assertEqual((a["rows"], a["mw"], a["on_time_share"], a["late_share"]),
                             (n, mw, 0.0, 1.0), b)
        self.assertEqual(cells[("approved", "13-24")]["rows"], 0)
        # U 04-06: 1/A three rows x 100 on time + 3/C two rows x 20 late: 300 / 340 = 0.8824 on
        # time, 40 / 340 = 0.1176 late; 3 of 5 rows on time.
        u = cells[("U", "04-06")]
        self.assertEqual((u["rows"], u["generators"], u["mw"], u["on_time_share"], u["late_share"],
                          u["not_online_share"], u["on_time_count_share"]),
                         (5, 2, 340.0, 0.8824, 0.1176, 0.0, 0.6))
        self.assertEqual((cells[("U", "07-12")]["rows"], cells[("U", "07-12")]["mw"],
                          cells[("U", "07-12")]["on_time_share"]), (5, 500.0, 1.0))
        self.assertEqual((cells[("U", "00-03")]["rows"], cells[("U", "00-03")]["mw"],
                          cells[("U", "00-03")]["late_share"]), (4, 80.0, 1.0))
        # V: 8/H nine rows x 40 in 13-24 and one in 07-12, on time; 2/B one row x 50 in 04-06
        # and six x 50 in 00-03, not online.
        self.assertEqual((cells[("V", "13-24")]["rows"], cells[("V", "13-24")]["mw"],
                          cells[("V", "13-24")]["on_time_share"]), (9, 360.0, 1.0))
        self.assertEqual((cells[("V", "07-12")]["rows"], cells[("V", "07-12")]["mw"],
                          cells[("V", "07-12")]["on_time_share"]), (1, 40.0, 1.0))
        self.assertEqual((cells[("V", "04-06")]["rows"], cells[("V", "04-06")]["mw"],
                          cells[("V", "04-06")]["not_online_share"]), (1, 50.0, 1.0))
        self.assertEqual((cells[("V", "00-03")]["rows"], cells[("V", "00-03")]["mw"],
                          cells[("V", "00-03")]["not_online_share"]), (6, 300.0, 1.0))
        # TS 00-03: 6/F's one row, late; OT: nothing.
        self.assertEqual((cells[("TS", "00-03")]["rows"], cells[("TS", "00-03")]["mw"],
                          cells[("TS", "00-03")]["late_share"]), (1, 30.0, 1.0))
        self.assertEqual(sum(cells[("OT", b)]["rows"] for b in lt.BAND_NAMES), 0)
        self.assertEqual(sum(r["rows"] for r in cells.values()), 52)
        self.assertTrue(all(r["adds_up"] for r in cells.values()))

    def test_grids(self):
        _, c = built()
        g = {(r["group"], r["stage"]): r for r in lt.grids(c)}
        self.assertEqual(len(g), len(lt.GROUPS) * len(lt.GRID))
        self.assertEqual([g[("all", st)][b] for st in lt.GRID for b in lt.BAND_NAMES],
                         [0.0, None, 1.0, 0.1667,      # early
                          0.0, 0.0, 0.0, None,         # approved
                          0.0, 0.8824, 1.0, None,      # U
                          0.0, 0.0, 1.0, 1.0])         # V
        # solar: early 13-24 is 1/A alone (4/D is gas CC) -> 1.0; early 00-03 is 10/J -> 0.0;
        # U 04-06 is 1/A alone (3/C is a battery) -> 1.0.
        self.assertEqual((g[("solar", "early")]["13-24"], g[("solar", "early")]["00-03"],
                          g[("solar", "U")]["04-06"]), (1.0, 0.0, 1.0))
        self.assertEqual((g[("battery", "U")]["04-06"], g[("battery", "approved")]["07-12"]),
                         (0.0, 0.0))
        self.assertEqual((g[("gas_cc", "early")]["13-24"], g[("wind_onshore", "V")]["13-24"],
                          g[("wind_onshore", "V")]["00-03"]), (0.0, 1.0, 0.0))
        self.assertTrue(all(g[("gas_ct", st)][b] is None for st in lt.GRID for b in lt.BAND_NAMES))

    def test_sample_check(self):
        df, c = built()
        s = lt.sample_check(df, c, (m(2016, 7), m(2017, 8)), LAST)
        # July 2016: 1/A U (lead 11, 100), 2/B V (lead 1, 50), 3/C T (lead 6, 20), 8/H V (lead 15,
        # 40); 5/E's lead is 42 and its window open; 10/J is CN. August 2017: 4/D (lead 22, 500)
        # only; 1/A, 3/C, 6/F and 8/H are OP, 2/B's planned month has passed, 5/E is open.
        self.assertEqual(s["months"], {
            "2016-07": {"expected_mw": 210.0, "expected_n": 4, "got_mw": 210.0, "got_n": 4},
            "2017-08": {"expected_mw": 500.0, "expected_n": 1, "got_mw": 500.0, "got_n": 1}})
        self.assertTrue(s["pass"])
        bad = lt.sample_check(df, c[c["key"] != "8/H"], (m(2016, 7),), LAST)
        self.assertFalse(bad["pass"])

    def test_checks(self):
        df, c = built()
        cells = lt.cells(c)
        ch = lt.checks(c, cells, lt.sample_check(df, c, (m(2016, 7), m(2017, 8)), LAST), LAST)
        self.assertTrue(ch["C1"]["pass"])
        # Every one of the 16 prediction cells has fewer than 20 generators here.
        self.assertEqual(len(ch["C2"]["thin_cells"]), 16)
        self.assertFalse(ch["C2"]["pass"])
        self.assertEqual(ch["C3"], {"cells": 24, "not_adding_up": 0, "rows": 52, "cell_rows": 52,
                                    "pass": True})
        self.assertEqual(ch["C4"], {"duplicate_key_months": 0, "rows_outside_window": 0,
                                    "first_month": "2016-01", "last_month": "2017-10",
                                    "pass": True})
        self.assertFalse(ch["all_pass"])
        # A duplicated row fails C3 (cell rows no longer equal the rows) and C4.
        dup = pd.concat([c, c.iloc[[0]]], ignore_index=True)
        ch2 = lt.checks(dup, cells, ch["C1"], LAST)
        self.assertFalse(ch2["C3"]["pass"])
        self.assertEqual(ch2["C4"]["duplicate_key_months"], 1)

    def test_predictions(self):
        _, c = built()
        p = lt.predictions(c)
        # L1: U runs 0.0, 0.8824, 1.0 (rising) and V 0.0, 0.0, 1.0, 1.0 (rising): neither is
        # non-increasing.
        self.assertEqual(p["L1"]["non_increasing"], {"U": False, "V": False})
        self.assertEqual(p["L1"]["on_time_by_band"]["U"],
                         {"00-03": 0.0, "04-06": 0.8824, "07-12": 1.0, "13-24": None})
        self.assertFalse(p["L1"]["held"])
        # L2: V falls 0.0 - 1.0 = -1.0; early falls 0.0 - 0.1667 = -0.1667; -1.0 > -0.1667 is false.
        self.assertEqual((p["L2"]["fall_V"], p["L2"]["fall_early"], p["L2"]["held"]),
                         (-1.0, -0.1667, False))
        self.assertEqual((p["L3"]["V_00_03_on_time"], p["L3"]["held"]), (0.0, False))
        self.assertEqual((p["L4"]["early_13_24_on_time"], p["L4"]["held"]), (0.1667, True))
        self.assertEqual((p["L5"]["V_07_12_on_time"], p["L5"]["early_00_03_on_time"],
                          p["L5"]["held"]), (1.0, 0.0, True))
        self.assertEqual((p["L6"]["early_13_24_not_online"], p["L6"]["held"]), (0.8333, True))

    def test_mono(self):
        self.assertTrue(lt._mono([0.5, 0.4, 0.4, 0.1]))
        self.assertFalse(lt._mono([0.5, 0.6, 0.4]))
        self.assertTrue(lt._mono([0.5, None, 0.4]))
        self.assertIsNone(lt._mono([0.5, None, None]))
        self.assertIsNone(lt._mono([]))

    def test_write_md(self):
        df, c = built()
        cells = lt.cells(c)
        res = {"cells": cells, "grids": lt.grids(c),
               "checks": lt.checks(c, cells, lt.sample_check(df, c, (m(2016, 7),), LAST), LAST),
               "predictions": lt.predictions(c)}
        meta = {"version": lt.__version__, "eia860m_slip": lt.es.__version__, "source": "x.parquet",
                "report_max": "2020-12", "first_month": "2016-01", "last_month": "2017-10"}
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "leadtime.md")
            lt.write_md(path, meta, res)
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
        self.assertIn("## Every cell", text)
        self.assertIn("| U | 04-06 | 5 | 2 | 340.0 | 0.882 | 0.118 | 0.000 | 0.600 |", text)
        self.assertIn("| all | V | 0.000 | 0.000 | 1.000 | 1.000 |", text)
        self.assertIn("| all | early | 0.000 |  | 1.000 | 0.167 |", text)
        json.dumps(res, default=str)


if __name__ == "__main__":
    unittest.main()
