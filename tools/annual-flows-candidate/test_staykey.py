"""Tests for staykey.py on a hand-built changelog, every expected value traced by hand (the
arithmetic is in the comments). MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import json
import os
import tempfile
import unittest

import numpy as np
import pandas as pd

import staykey as st


def m(year, month):
    return year * 12 + month - 1


LAST = m(2020, 12)
CC = "Natural Gas Fired Combined Cycle"
CT = "Natural Gas Fired Combustion Turbine"
PV = "Solar Photovoltaic"
WT = "Onshore Wind Turbine"


def changelog():
    """EIA-860M records: report, valid until (a generator's last record runs to that report,
    inclusive; an earlier record to the month before), plant, generator, MW, status, technology,
    planned operating month, operating date. Last report: December 2020 (9/Z).

    1/CC  gas CC 300 MW, U from Jan 2017 planned 2018-06, then V from Jan 2019 planned 2019-06,
          still listed: a stayer. Its twins:
    1/CT1 gas CT 150 MW, V from Jul 2017 planned 2018-06, OP from Aug 2018.
    1/CT2 gas CC 170 MW, V from Jul 2017 planned 2018-06, OP from Sep 2018.
          150 + 170 = 320 against 300 (difference 20): linked; replacement month 2018-09.
    2/PV1 solar 100 MW, P from Jan 2016 planned 2017-12, still listed: a stayer.
    2/PV2 solar 60 MW, U from Jan 2017 planned 2017-12, OP from Dec 2017: a twin, but 60 against
          100 (difference 40): not linked; bound B.
    3/W   wind 80 MW, V from Jan 2016 planned 2017-01, still listed: a stayer, nothing else.
    4/A   wind 100 MW, P Jan-Dec 2016 planned 2017-12, then gone: rule S's leaver.
    4/B   wind 100 MW, U from Jan 2017 planned 2017-12, OP from Feb 2018: 4/A's rule S arrival.
    5/L   solar 40 MW, U from Jun 2016 planned 2017-01, OP from Jun 2018: online 17 months late.
    6/S   solar 50 MW, P from Jun 2017 planned 2018-06, still listed: a stayer.
    6/E   solar 50 MW, OP from Jan 2018, never planned: not a twin (bound B counts it).
    6/F   solar 50 MW, U from Jan 2016 planned 2017-06, OP from Jun 2017: first listed before
          6/S, not a twin.
    9/Z   1 MW, OP from Dec 2020: sets the last report; never planned.
    """
    recs = [
        ("2017-01-01", "2019-01-01", 1, "CC", 300.0, "U", CC, "2018-06-01", None),
        ("2019-01-01", None, 1, "CC", 300.0, "V", CC, "2019-06-01", None),
        ("2017-07-01", "2018-08-01", 1, "CT1", 150.0, "V", CT, "2018-06-01", None),
        ("2018-08-01", None, 1, "CT1", 150.0, "OP", CT, None, "2018-08-01"),
        ("2017-07-01", "2018-09-01", 1, "CT2", 170.0, "V", CC, "2018-06-01", None),
        ("2018-09-01", None, 1, "CT2", 170.0, "OP", CC, None, "2018-09-01"),
        ("2016-01-01", None, 2, "PV1", 100.0, "P", PV, "2017-12-01", None),
        ("2017-01-01", "2017-12-01", 2, "PV2", 60.0, "U", PV, "2017-12-01", None),
        ("2017-12-01", None, 2, "PV2", 60.0, "OP", PV, None, "2017-12-01"),
        ("2016-01-01", None, 3, "W", 80.0, "V", WT, "2017-01-01", None),
        ("2016-01-01", "2016-12-01", 4, "A", 100.0, "P", WT, "2017-12-01", None),
        ("2017-01-01", "2018-02-01", 4, "B", 100.0, "U", WT, "2017-12-01", None),
        ("2018-02-01", None, 4, "B", 100.0, "OP", WT, None, "2018-02-01"),
        ("2016-06-01", "2018-06-01", 5, "L", 40.0, "U", PV, "2017-01-01", None),
        ("2018-06-01", None, 5, "L", 40.0, "OP", PV, None, "2018-06-01"),
        ("2017-06-01", None, 6, "S", 50.0, "P", PV, "2018-06-01", None),
        ("2018-01-01", None, 6, "E", 50.0, "OP", PV, None, "2018-01-01"),
        ("2016-01-01", "2017-06-01", 6, "F", 50.0, "U", PV, "2017-06-01", None),
        ("2017-06-01", None, 6, "F", 50.0, "OP", PV, None, "2017-06-01"),
        ("2020-12-01", None, 9, "Z", 1.0, "OP", PV, None, None)]
    raw = pd.DataFrame(recs, columns=["report_date", "valid_until_date", "plant_id_eia",
                                      "generator_id", "capacity_mw", "operational_status_code",
                                      "technology_description",
                                      "current_planned_generator_operating_date",
                                      "generator_operating_date"])
    return st.es.prepare(raw)


def built():
    df = changelog()
    online = st.es.online_months(df)
    info = st.sk.generators(df, online)
    status = st.last_status(df)
    stay = st.stayers(info, status, LAST)
    return df, info, status, stay, st.groups(stay)


class StayKeyTests(unittest.TestCase):
    def test_stayers_and_groups(self):
        _, info, status, stay, gr = built()
        self.assertEqual(len(info), 13)
        self.assertEqual(status["1/CC"], "V")
        # Still listed as planned and never online: 1/CC, 2/PV1, 3/W, 6/S. 4/A left; the rest
        # came online.
        self.assertEqual(sorted(stay.index), ["1/CC", "2/PV1", "3/W", "6/S"])
        self.assertEqual([(x["plant"], x["family"], x["stayers"], x["first"], x["mw"])
                          for x in gr],
                         [("1", "gas", ["1/CC"], m(2017, 1), 300.0),
                          ("2", "solar", ["2/PV1"], m(2016, 1), 100.0),
                          ("3", "wind_onshore", ["3/W"], m(2016, 1), 80.0),
                          ("6", "solar", ["6/S"], m(2017, 6), 50.0)])
        # A generator whose last record is not planned (3/W set to OS here) is not a stayer.
        s2 = status.copy()
        s2["3/W"] = "OS"
        self.assertEqual(sorted(st.stayers(info, s2, LAST).index), ["1/CC", "2/PV1", "6/S"])

    def test_link(self):
        _, info, _, _, gr = built()
        # Plant 1: twins 1/CT1 and 1/CT2 (first listed 2017-07 > 2017-01), 320 vs 300, 20 <= 60.
        # Plant 2: 2/PV2, 60 vs 100, 40 > 20. Plant 3: no candidate. Plant 6: 6/E never
        # planned, 6/F first listed 2016-01 <= 2017-06.
        links = st.link(info, gr)
        self.assertEqual([(x["stayers"], x["twins"], x["twins_mw"], x["month"]) for x in links],
                         [(["1/CC"], ["1/CT1", "1/CT2"], 320.0, m(2018, 9))])
        self.assertEqual(st.credit(links), {"1/CC": m(2018, 9)})
        # At 0.05: 20 > 15 drops plant 1. At 0.40: 40 <= 40 links plant 2 too (month 2017-12).
        self.assertEqual(st.link(info, gr, 0.05), [])
        self.assertEqual([(x["stayers"], x["month"]) for x in st.link(info, gr, 0.40)],
                         [(["1/CC"], m(2018, 9)), (["2/PV1"], m(2017, 12))])

    def test_possible(self):
        _, info, _, _, gr = built()
        # Latest first listing of an online generator: plant 1 gas 2017-07, plant 2 solar
        # 2017-01, plant 6 solar 2018-01 (6/E); each after its group's first listing. Plant 3
        # has none.
        self.assertEqual(st.possible_keys(info, gr), {"1/CC", "2/PV1", "6/S"})

    def test_fates(self):
        df = changelog()
        c = st.es.cohorts(df, LAST)
        # Not-online rows: 1/CC 19 x 300 = 5,700; 2/PV1 13 x 100 = 1,300; 3/W 13 x 80 = 1,040;
        # 4/A 1 x 100; 5/L 8 x 40 = 320; 6/S 13 x 50 = 650: 9,110. Stayers 8,690 = 0.9539;
        # leaver 100 = 0.0110; online later 320 = 0.0351.
        f = st.fates(c, {"5/L", "1/CT1"}, {"1/CC", "2/PV1", "3/W", "6/S"}, {"4/A"})
        self.assertEqual((f["not_online_mw"], f["stayer_mw"], f["leaver_mw"],
                          f["online_later_mw"], f["other_mw"]),
                         (9110.0, 8690.0, 100.0, 320.0, 0.0))
        self.assertEqual(round(f["stayer_share"], 4), 0.9539)
        self.assertEqual(round(f["leaver_share"], 4), 0.011)
        self.assertEqual(round(f["online_later_share"], 4), 0.0351)
        # Without the leaver set, 4/A's 100 is "other".
        self.assertEqual(st.fates(c, {"5/L"}, {"1/CC", "2/PV1", "3/W", "6/S"}, set())["other_mw"],
                         100.0)
        # No not-online rows: shares are None.
        self.assertIsNone(st.fates(c[c["outcome"] == "on_time"], set(), set(), set())
                          ["stayer_share"])

    def test_advanced_and_planned_at(self):
        df = changelog()
        # 1/CC is U in force at 2018-09 and V from 2019-01: advanced. 3/W stays V.
        self.assertTrue(st.advanced(df, "1/CC", m(2018, 9)))
        self.assertFalse(st.advanced(df, "1/CC", m(2019, 1)))
        self.assertFalse(st.advanced(df, "3/W", m(2017, 1)))
        # Before any record (2016-06), 1/CC's base is its first record (U); V later: advanced.
        self.assertTrue(st.advanced(df, "1/CC", m(2016, 6)))
        # 1/CC's planned month in records reported before 2017-07: 2018-06; before 2019-02:
        # 2019-06; before 2017-01: none.
        self.assertEqual(st.planned_at(df, ["1/CC"], m(2017, 7)), m(2018, 6))
        self.assertEqual(st.planned_at(df, ["1/CC"], m(2019, 2)), m(2019, 6))
        self.assertTrue(np.isnan(st.planned_at(df, ["1/CC"], m(2017, 1))))

    def test_run(self):
        df = changelog()
        res, hand = st.run(df, LAST)
        self.assertEqual(res["counts"], {
            "stayers": 4, "stayer_mw": 530.0, "groups": 4, "linked_groups": 1,
            "linked_stayers": 1, "linked_stayer_mw": 300.0, "twins": 2, "twin_mw": 320.0,
            "possible_stayers": 3, "possible_stayer_mw": 450.0, "rule_s_replaced_leavers": 1,
            "twins_also_rule_s_arrivals": 0})
        # 0-12-month rows: 1/CC 13 x 300 (planned 2018-06) + 6 x 300 (planned 2019-06), 1/CT1
        # 12 x 150, 1/CT2 12 x 170, 2/PV1 13 x 100, 2/PV2 11 x 60, 3/W 13 x 80, 4/A 1 x 100,
        # 4/B 12 x 100, 5/L 8 x 40, 6/S 13 x 50, 6/F 12 x 50: 126 rows, 15,410 MW. On time:
        # 2/PV2 660 + 6/F 600 = 1,260 = 0.0818; not online 9,110 = 0.5912. Rule T credits 1/CC
        # with 2018-09: its 2018-06 rows 3 months late, its 2019-06 rows on time (+1,800):
        # on time 3,060 = 0.1986; not online 3,410 = 0.2213. With rule S too (4/A credited
        # 2018-02, 2 months late): not online 3,310 = 0.2148. Replaced 5,700 / 9,110 = 0.6257;
        # possible 5,700 + 1,300 + 650 = 7,650 = 0.8397.
        self.assertEqual(res["cohort"], {
            "rows": 126, "mw": 15410.0, "not_online_mw": 9110.0, "linked_mw": 5700.0,
            "replaced_mw": 5700.0, "possible_mw": 7650.0, "replaced_share": 0.6257,
            "possible_share": 0.8397, "on_time_before": 0.0818, "on_time_after": 0.1986,
            "not_online_before": 0.5912, "not_online_after": 0.2213,
            "online_later_mw": 320.0, "online_later_share": 0.0351, "stayer_mw": 8690.0,
            "stayer_share": 0.9539, "leaver_mw": 100.0, "leaver_share": 0.011,
            "other_mw": 0.0, "other_share": 0.0, "on_time_both": 0.1986,
            "not_online_both": 0.2148})
        g = {r["part"]: r for r in res["by_group"]}
        # gas_cc: 1/CC 5,700 + 1/CT2 2,040 = 7,740 MW; on time after 1,800 / 7,740 = 0.2326.
        self.assertEqual((g["gas_cc"]["rows"], g["gas_cc"]["mw"], g["gas_cc"]["replaced_share"],
                          g["gas_cc"]["on_time_before"], g["gas_cc"]["on_time_after"],
                          g["gas_cc"]["not_online_after"]), (31, 7740.0, 1.0, 0.0, 0.2326, 0.0))
        # solar: 57 rows, 3,530 MW, not online 2,270; stayers 2/PV1 + 6/S 1,950 = 0.8590,
        # online later 5/L 320 = 0.1410; nothing replaced.
        self.assertEqual((g["solar"]["rows"], g["solar"]["mw"], g["solar"]["not_online_mw"],
                          g["solar"]["stayer_share"], g["solar"]["online_later_share"],
                          g["solar"]["replaced_share"]), (57, 3530.0, 2270.0, 0.859, 0.141, 0.0))
        # battery: no rows; gas_ct: 1/CT1 is late, nothing not online.
        self.assertEqual((g["battery"]["rows"], g["battery"]["stayer_share"],
                          g["gas_ct"]["replaced_share"]), (0, None, None))
        k = res["checks"]
        self.assertFalse(k["K1"]["pass"])          # the fixture is not the published data
        self.assertTrue(k["K2"]["pass"])
        # Rows changed: cohort 1/CC 19; lead rows (report months 2016-01 to 2017-10) 1/CC
        # 2017-01..2017-10 = 10; both rules 19 + 4/A 1 = 20.
        self.assertEqual((k["K3"]["cohort"]["rows_changed"], k["K3"]["cohort"]["pass"]),
                         (19, True))
        self.assertEqual((k["K3"]["leadtime"]["rows_changed"], k["K3"]["leadtime"]["pass"]),
                         (10, True))
        self.assertEqual((k["K3"]["cohort_both"]["rows_changed"],
                          k["K3"]["cohort_both"]["pass"]), (20, True))
        self.assertFalse(k["all_pass"])
        p = res["predictions"]
        # T1 0.9539 outside 0.10-0.40; T2 0.6257 not below 0.0235; T3 rise 0.1168; T4 0.2148
        # >= 0.17.
        self.assertEqual((p["T1"]["held"], p["T2"]["held"], p["T3"]["held"], p["T4"]["held"]),
                         (False, False, False, True))
        self.assertEqual(p["T3"]["rise"], 0.1168)
        self.assertEqual([(s["tolerance"], s["linked_groups"], s["replaced_share"],
                           s["not_online_after"]) for s in res["sensitivity_tolerance"]],
                         [(0.05, 0, 0.0, 0.5912), (0.1, 1, 0.6257, 0.2213),
                          (0.2, 1, 0.6257, 0.2213), (0.3, 1, 0.6257, 0.2213)])
        # The one link: twins first listed 2017-07; 1/CC's planned month before then 2018-06,
        # the twins' 2018-06: (a) 0. 1/CC moved U -> V after 2018-09: (b) 1. Lead rows of 1/CC
        # not online: 10 x 300.
        row = res["links"][0]
        self.assertEqual(len(res["links"]), 1)
        self.assertEqual({c: row[c] for c in st.LINK_COLS}, {
            "plant": "1", "name": "", "state": "", "family": "gas", "stayers": "1/CC",
            "stayer_mw": 300.0, "twins": "1/CT1; 1/CT2", "twin_mw": 320.0,
            "first_listed": "2017-01", "twins_listed": "2017-07",
            "planned_at_arrival": "2018-06", "twins_planned": "2018-06", "a_months": 0,
            "online_all": "2018-09", "stayer_planned_last": "2019-06", "b_advanced": 1,
            "not_online_mw_rows": 5700.0, "lt_not_online_mw_rows": 3000.0})
        self.assertEqual(sorted(set(hand)), ["1/CC", "1/CT1", "1/CT2"])
        json.dumps(res, default=str)

    def test_k2(self):
        _, info, status, _, gr = built()
        links = st.link(info, gr)
        months = st.credit(links)
        possible = st.possible_keys(info, gr)
        self.assertTrue(st.k2(info, status, links, months, possible, LAST)["pass"])
        # A twin that never ran, a twin listed before the group, and a replaced stayer outside
        # bound B all fail.
        bad = links + [{"plant": "6", "family": "solar", "stayers": ["6/S"],
                        "twins": ["6/F"], "twins_mw": 50.0, "mw": 50.0, "first": m(2017, 6),
                        "month": m(2017, 6)},
                       {"plant": "3", "family": "wind_onshore", "stayers": ["3/W"],
                        "twins": ["4/A"], "twins_mw": 100.0, "mw": 80.0, "first": m(2015, 1),
                        "month": 1.0}]
        out = st.k2(info, status, bad, dict(months, **{"3/W": 1.0}), possible, LAST)
        # 4/A never ran (twins_not_built 1) and is at plant 4 (wrong 1); 6/F was first listed
        # 2016-01, not after 2017-06 (too early 1; 4/A's 2016-01 is after 2015-01); 4/A's 100
        # against 80 differs by 20 > 0.2 x 80 = 16 (outside 1); 3/W is outside bound B.
        self.assertEqual((out["twins_not_built"], out["wrong_plant_or_family"],
                          out["twin_listed_too_early"], out["outside_tolerance"],
                          out["replaced_outside_bound"], out["stayers_not_staying"],
                          out["pass"]), (1, 1, 1, 1, 1, 0, False))

    def test_predictions(self):
        cohort = {"stayer_share": 0.25, "replaced_share": 0.01, "on_time_before": 0.3247,
                  "on_time_after": 0.33, "not_online_before": 0.1916, "not_online_both": 0.18}
        before = {"L1": {"held": False}, "L2": {"held": True}}
        p = st.predictions(cohort, before, {"L1": {"held": False}, "L2": {"held": False}})
        self.assertEqual([p[t]["held"] for t in ("T1", "T2", "T3", "T4", "T5")],
                         [True, True, True, True, False])
        self.assertEqual(p["T5"]["unchanged"], {"L1": True, "L2": False})
        # Edges: 0.10 and 0.40 are inside T1; 0.0235 is not below itself; a rise of exactly
        # 0.01 (0.0 to 0.01) fails T3; 0.17 holds T4; a missing share leaves T1 open.
        e = dict(cohort, stayer_share=0.40, replaced_share=0.0235, on_time_before=0.0,
                 on_time_after=0.01, not_online_both=0.17)
        p2 = st.predictions(e, before, before)
        self.assertEqual([p2[t]["held"] for t in ("T1", "T2", "T3", "T4", "T5")],
                         [True, False, False, True, True])
        self.assertTrue(st.predictions(dict(e, stayer_share=0.10), before, before)["T1"]["held"])
        self.assertFalse(st.predictions(dict(e, stayer_share=0.0999), before,
                                        before)["T1"]["held"])
        self.assertIsNone(st.predictions(dict(e, stayer_share=None), before, before)["T1"]["held"])
        self.assertFalse(st.predictions(dict(e, not_online_both=0.1699), before,
                                        before)["T4"]["held"])

    def test_write_md(self):
        df = changelog()
        res, _ = st.run(df, LAST)
        meta = {"version": st.__version__, "eia860m_slip": st.es.__version__,
                "leadtime": st.lt.__version__, "splitkey": st.sk.__version__,
                "source": "x.parquet", "report_max": "2020-12"}
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "staykey.md")
            st.write_md(path, meta, res)
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
        self.assertIn("## Every linked group", text)
        self.assertIn("1 links.", text)
        # part, rows, mw, not online, online later, stayer, leaver, other, replaced MW, possible
        # MW, replaced share, possible share, ...
        self.assertIn("| all | 126 | 15410.0 | 9110.0 | 0.035 | 0.954 | 0.011 | 0.000 | 5700.0 | "
                      "7650.0 | 0.626 | 0.840 |", text)


if __name__ == "__main__":
    unittest.main()
