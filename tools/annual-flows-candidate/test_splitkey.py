"""Tests for splitkey.py on a hand-built changelog, every expected value traced by hand (the
arithmetic is in the comments). MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import json
import os
import tempfile
import unittest

import numpy as np
import pandas as pd

import splitkey as sk


def m(year, month):
    return year * 12 + month - 1


LAST = m(2020, 12)


def changelog():
    """EIA-860M records: report, valid until (a generator's last record runs to that report,
    inclusive; an earlier record to the month before), plant, generator, MW, status, technology,
    planned operating month, operating date. Last report: December 2020 (9/Z).

    1/CC  gas CC 300 MW, U Jan-Jun 2017 planned 2018-06, then gone: a leaver.
    1/CT1 gas CT 150 MW, V from Jul 2017 planned 2018-06, OP from Aug 2018 (online 2018-08).
    1/CT2 gas CC 170 MW, V from Jul 2017 planned 2018-06, OP from Sep 2018 (online 2018-09).
          1/CC's arrivals: 150 + 170 = 320 MW against 300 (difference 20).
    2/A   wind 100 MW, P Jan-Dec 2016 planned 2017-12, then gone: a leaver.
    2/B   wind 100 MW, L Jan-Jun 2017 planned 2017-12, then gone: a leaver and 2/A's arrival.
    2/C   wind 104 MW, U from Jul 2017 planned 2018-03, OP from Apr 2018: 2/B's arrival.
          2/A's exit (2016-12) and 2/B's (2017-06) are 6 months apart: two clusters.
    3/S   solar 50 MW, P Jan-Jun 2016 planned 2016-09, then gone; nothing else at plant 3.
    4/P1  solar 200 MW, U Jan-Dec 2017 planned 2018-03, then gone: a leaver.
    4/P2  solar 50 MW, OP from Mar 2017: first listed after 4/P1 (bound B) but more than 6
          months before 4/P1's exit, so not an arrival.
    5/W   wind 80 MW, V from Jan 2016 planned 2017-01, still listed in the last report: not a
          leaver, never online.
    6/G   solar 10 MW, U Jun-Nov 2016 planned 2016-12, OP from Dec 2016: on time.
    9/Z   1 MW, OP from Dec 2020: sets the last report; never planned.
    """
    recs = [
        ("2017-01-01", "2017-06-01", 1, "CC", 300.0, "U", "Natural Gas Fired Combined Cycle",
         "2018-06-01", None),
        ("2017-07-01", "2018-08-01", 1, "CT1", 150.0, "V", "Natural Gas Fired Combustion Turbine",
         "2018-06-01", None),
        ("2018-08-01", None, 1, "CT1", 150.0, "OP", "Natural Gas Fired Combustion Turbine", None,
         "2018-08-01"),
        ("2017-07-01", "2018-09-01", 1, "CT2", 170.0, "V", "Natural Gas Fired Combined Cycle",
         "2018-06-01", None),
        ("2018-09-01", None, 1, "CT2", 170.0, "OP", "Natural Gas Fired Combined Cycle", None,
         "2018-09-01"),
        ("2016-01-01", "2016-12-01", 2, "A", 100.0, "P", "Onshore Wind Turbine", "2017-12-01", None),
        ("2017-01-01", "2017-06-01", 2, "B", 100.0, "L", "Onshore Wind Turbine", "2017-12-01", None),
        ("2017-07-01", "2018-04-01", 2, "C", 104.0, "U", "Onshore Wind Turbine", "2018-03-01", None),
        ("2018-04-01", None, 2, "C", 104.0, "OP", "Onshore Wind Turbine", None, "2018-04-01"),
        ("2016-01-01", "2016-06-01", 3, "S", 50.0, "P", "Solar Photovoltaic", "2016-09-01", None),
        ("2017-01-01", "2017-12-01", 4, "P1", 200.0, "U", "Solar Photovoltaic", "2018-03-01", None),
        ("2017-03-01", None, 4, "P2", 50.0, "OP", "Solar Photovoltaic", None, "2017-03-01"),
        ("2016-01-01", None, 5, "W", 80.0, "V", "Onshore Wind Turbine", "2017-01-01", None),
        ("2016-06-01", "2016-12-01", 6, "G", 10.0, "U", "Solar Photovoltaic", "2016-12-01", None),
        ("2016-12-01", None, 6, "G", 10.0, "OP", "Solar Photovoltaic", None, "2016-12-01"),
        ("2020-12-01", None, 9, "Z", 1.0, "OP", "Solar Photovoltaic", None, None)]
    raw = pd.DataFrame(recs, columns=["report_date", "valid_until_date", "plant_id_eia",
                                      "generator_id", "capacity_mw", "operational_status_code",
                                      "technology_description",
                                      "current_planned_generator_operating_date",
                                      "generator_operating_date"])
    return sk.es.prepare(raw)


def built():
    df = changelog()
    online = sk.es.online_months(df)
    info = sk.generators(df, online)
    cl = sk.clusters(info, LAST)
    return df, online, info, cl


class SplitKeyTests(unittest.TestCase):
    def test_family(self):
        self.assertEqual(sk.family("gas_cc", "x"), "gas")
        self.assertEqual(sk.family("gas_ct", None), "gas")
        self.assertEqual(sk.family("solar", "Solar Photovoltaic"), "solar")
        self.assertEqual(sk.family("other", " Landfill Gas "), "other:landfill gas")
        self.assertEqual(sk.family(np.nan, None), "other:")

    def test_generators(self):
        _, _, info, _ = built()
        self.assertEqual(len(info), 12)
        cc = info.loc["1/CC"]
        self.assertEqual((cc["plant"], cc["family"], cc["first_m"], cc["last_m"], cc["mw_last"],
                          bool(cc["planned"]), bool(cc["online"]), cc["planned_last"]),
                         ("1", "gas", m(2017, 1), m(2017, 6), 300.0, True, False, m(2018, 6)))
        # 1/CT1 is a gas CT and 1/CT2 a gas CC: both in family gas. 1/CT1's OP record runs to
        # the last report; its operating date makes it online 2018-08.
        ct = info.loc["1/CT1"]
        self.assertEqual((ct["family"], ct["first_m"], ct["last_m"], ct["online_m"],
                          ct["planned_first"]),
                         ("gas", m(2017, 7), LAST, m(2018, 8), m(2018, 6)))
        self.assertEqual(info.at["1/CT2", "family"], "gas")
        self.assertEqual(info.at["1/CT2", "mw_first"], 170.0)
        # 4/P2 was never planned; 5/W is still listed.
        self.assertFalse(bool(info.at["4/P2", "planned"]))
        self.assertTrue(np.isnan(info.at["4/P2", "planned_first"]))
        self.assertEqual(info.at["5/W", "last_m"], LAST)
        self.assertEqual(sorted(sk.leavers(info, LAST).index),
                         ["1/CC", "2/A", "2/B", "3/S", "4/P1"])

    def test_clusters(self):
        _, _, _, cl = built()
        got = [(x["plant"], x["family"], x["leavers"], x["lo"], x["hi"], x["first"], x["mw"])
               for x in cl]
        self.assertEqual(got, [
            ("1", "gas", ["1/CC"], m(2017, 6), m(2017, 6), m(2017, 1), 300.0),
            ("2", "wind_onshore", ["2/A"], m(2016, 12), m(2016, 12), m(2016, 1), 100.0),
            ("2", "wind_onshore", ["2/B"], m(2017, 6), m(2017, 6), m(2017, 1), 100.0),
            ("3", "solar", ["3/S"], m(2016, 6), m(2016, 6), m(2016, 1), 50.0),
            ("4", "solar", ["4/P1"], m(2017, 12), m(2017, 12), m(2017, 1), 200.0)])
        # Exits 3 months apart join one cluster; 4 months apart do not.
        info = pd.DataFrame({"plant": ["7"] * 3, "family": ["solar"] * 3,
                             "first_m": [1.0, 2.0, 3.0], "last_m": [10.0, 13.0, 17.0],
                             "mw_last": [5.0, 6.0, 7.0], "planned": [True] * 3,
                             "online": [False] * 3}, index=["7/a", "7/b", "7/c"])
        two = sk.clusters(info, 100)
        self.assertEqual([(x["leavers"], x["lo"], x["hi"], x["first"], x["mw"]) for x in two],
                         [(["7/a", "7/b"], 10.0, 13.0, 1.0, 11.0), (["7/c"], 17.0, 17.0, 3.0, 7.0)])

    def test_link(self):
        _, _, info, cl = built()
        # Order by latest exit: 3/S (2016-06) has no candidate; 2/A (2016-12) takes 2/B (first
        # listed 2017-01, inside 2016-06..2017-06; 2/C's 2017-07 is outside), 100 vs 100; 1/CC
        # (2017-06, plant "1") takes 1/CT1 and 1/CT2, 320 vs 300, 20 <= 0.2 x 300 = 60; 2/B
        # (2017-06, plant "2") takes 2/C (2017-07 inside 2016-12..2017-12), 104 vs 100; 4/P1's
        # only candidate 4/P2 was first listed 2017-03, before 2017-12 - 6 = 2017-06.
        links = sk.link(info, cl)
        self.assertEqual([(x["leavers"], x["arrivals"], x["arrivals_mw"]) for x in links],
                         [(["2/A"], ["2/B"], 100.0), (["1/CC"], ["1/CT1", "1/CT2"], 320.0),
                          (["2/B"], ["2/C"], 104.0)])
        # At 0.05: 20 > 15 drops 1/CC; 4 <= 5 keeps 2/B.
        self.assertEqual([x["leavers"] for x in sk.link(info, cl, 0.05)], [["2/A"], ["2/B"]])

    def test_replacement(self):
        _, online, info, cl = built()
        links = sk.link(info, cl)
        last, first = sk.replacement(links, online)
        # 2/A's arrival 2/B never operated but is 2/B's cluster's leaver: it takes 2/C's month.
        self.assertEqual(last, [m(2018, 4), m(2018, 9), m(2018, 4)])
        self.assertEqual(first, [m(2018, 4), m(2018, 8), m(2018, 4)])
        self.assertEqual(sk.credit(links, last),
                         {"2/A": m(2018, 4), "1/CC": m(2018, 9), "2/B": m(2018, 4)})
        # An arrival that never operated and is no leaver leaves the month unknown; the first
        # arrival's month is still known.
        x = [{"leavers": ["a"], "arrivals": ["b", "c"]}]
        last, first = sk.replacement(x, pd.Series({"b": 5.0}))
        self.assertTrue(np.isnan(last[0]))
        self.assertEqual(first, [5.0])
        self.assertEqual(sk.credit(x, last), {})
        # A cycle never resolves.
        y = [{"leavers": ["a"], "arrivals": ["b"]}, {"leavers": ["b"], "arrivals": ["a"]}]
        last, _ = sk.replacement(y, pd.Series(dtype=float))
        self.assertTrue(all(np.isnan(v) for v in last))

    def test_possible(self):
        _, _, info, cl = built()
        # Latest first listing of an online generator: plant 1 gas 2017-07, plant 2 wind 2017-07,
        # plant 4 solar 2017-03; each is after its cluster's first listing. Plant 3 has none.
        self.assertEqual(sk.possible_keys(info, cl), {"1/CC", "2/A", "2/B", "4/P1"})

    def test_rescore(self):
        c = pd.DataFrame({"key": ["a", "b", "c"], "planned_m": [10.0, 10.0, 10.0],
                          "online_m": [np.nan, 9.0, np.nan], "mw": [1.0, 1.0, 1.0]})
        c["slip"] = c["online_m"] - c["planned_m"]
        c["outcome"] = [sk.es.outcome(s) for s in c["slip"]]
        c2 = sk.rescore(c, {"a": 12.0, "b": 30.0})
        # a: 12 - 10 = 2 months late; b already online (on time) keeps its own month; c no credit.
        self.assertEqual(list(c2["outcome"]), ["late_1_3", "on_time", "not_online_12"])
        self.assertEqual(list(c["outcome"]), ["not_online_12", "on_time", "not_online_12"])
        ch = sk.k3(c, c2, {"a": 12.0, "b": 30.0})
        self.assertEqual((ch["rows_changed"], ch["stray_changes"], ch["pass"]), (1, 0, True))
        self.assertFalse(sk.k3(c, c2, {"b": 30.0})["pass"])

    def test_run(self):
        df = changelog()
        res, hand = sk.run(df, LAST)
        self.assertEqual(res["counts"], {
            "leavers": 5, "leaver_mw": 750.0, "clusters": 5, "linked_clusters": 3,
            "linked_leavers": 3, "linked_leaver_mw": 500.0, "replaced_leavers": 3,
            "replaced_leaver_mw": 500.0, "possible_leavers": 4, "possible_leaver_mw": 700.0})
        # 0-12-month rows: 1/CC 1 x 300, 1/CT1 12 x 150, 1/CT2 12 x 170, 2/A 1 x 100, 2/B 6 x 100,
        # 2/C 9 x 104, 3/S 6 x 50, 4/P1 10 x 200, 5/W 13 x 80, 6/G 6 x 10: 76 rows, 9,176 MW.
        # Not online: 300 + 100 + 600 + 300 + 2,000 + 1,040 = 4,340; replaced 1,000 (1/CC, 2/A,
        # 2/B) = 0.2304; possible adds 4/P1: 3,000 = 0.6912. On time: 6/G 60 / 9,176 = 0.0065,
        # unchanged (1/CC 3 months late, 2/A and 2/B 4). Not online 0.4730 -> 3,340 / 9,176 =
        # 0.3640.
        self.assertEqual(res["cohort"], {
            "rows": 76, "mw": 9176.0, "not_online_mw": 4340.0, "linked_mw": 1000.0,
            "replaced_mw": 1000.0, "possible_mw": 3000.0, "replaced_share": 0.2304,
            "possible_share": 0.6912, "on_time_before": 0.0065, "on_time_after": 0.0065,
            "not_online_before": 0.473, "not_online_after": 0.364})
        g = {r["part"]: r for r in res["by_group"]}
        # gas_cc: 1/CC is the only not-online row (300), replaced. wind: 100 + 600 of 1,740.
        # battery: no rows; gas_ct: 1/CT1 is late, nothing not online.
        self.assertEqual((g["gas_cc"]["replaced_share"], g["solar"]["replaced_share"],
                          g["wind_onshore"]["replaced_share"], g["battery"]["replaced_share"],
                          g["gas_ct"]["replaced_share"]), (1.0, 0.0, 0.4023, None, None))
        # 0-24-month rows (report months 2016-01 to 2017-10): U 13-24 is 1/CC's leads 17..13
        # (5 x 300) and 4/P1's 14, 13 (2 x 200): 1,500 of 1,900 replaced = 0.7895; not online
        # 1.0 -> 400 / 1,900 = 0.2105. early 13-24 is 2/A's leads 23..13 (11 x 100), replaced.
        cells = {r["part"]: r for r in res["cells"]}
        u = cells["U 13-24"]
        self.assertEqual((u["rows"], u["mw"], u["replaced_share"], u["not_online_before"],
                          u["not_online_after"]), (7, 1900.0, 0.7895, 1.0, 0.2105))
        e = cells["early 13-24"]
        self.assertEqual((e["rows"], e["mw"], e["replaced_share"], e["not_online_after"]),
                         (11, 1100.0, 1.0, 0.0))
        k = res["checks"]
        self.assertFalse(k["K1"]["pass"])          # the fixture is not the published data
        self.assertTrue(k["K2"]["pass"])
        # Rows changed: cohort 1/CC 1 + 2/A 1 + 2/B 6 = 8; lead rows 6 + 12 + 6 = 24.
        self.assertEqual((k["K3"]["cohort"]["rows_changed"], k["K3"]["cohort"]["pass"]), (8, True))
        self.assertEqual((k["K3"]["leadtime"]["rows_changed"], k["K3"]["leadtime"]["pass"]),
                         (24, True))
        self.assertFalse(k["all_pass"])
        # Tolerance 0.05 drops 1/CC: 700 / 4,340 = 0.1613; not online 3,640 / 9,176 = 0.3967.
        self.assertEqual([(s["tolerance"], s["linked_clusters"], s["replaced_share"],
                           s["not_online_after"]) for s in res["sensitivity_tolerance"]],
                         [(0.05, 2, 0.1613, 0.3967), (0.1, 3, 0.2304, 0.364),
                          (0.2, 3, 0.2304, 0.364), (0.3, 3, 0.2304, 0.364)])
        # Links, most not-online MW first: 2/B 600, 1/CC 300, 2/A 100.
        self.assertEqual([(r["leavers"], r["arrivals"], r["not_online_mw_rows"],
                           r["lt_not_online_mw_rows"], r["online_all"], r["online_first"])
                          for r in res["links"]],
                         [("2/B", "2/C", 600.0, 600.0, "2018-04", "2018-04"),
                          ("1/CC", "1/CT1; 1/CT2", 300.0, 1800.0, "2018-09", "2018-08"),
                          ("2/A", "2/B", 100.0, 1200.0, "2018-04", "2018-04")])
        cc = res["links"][1]
        self.assertEqual((cc["last_listed"], cc["arrived"], cc["planned_was"], cc["planned_new"],
                          cc["leaver_mw"], cc["arrival_mw"]),
                         ("2017-06", "2017-07", "2018-06", "2018-06", 300.0, 320.0))
        self.assertEqual(sorted(set(hand)), ["1/CC", "1/CT1", "1/CT2", "2/A", "2/B", "2/C"])
        json.dumps(res, default=str)

    def test_k1(self):
        df = changelog()
        c = sk.es.cohorts(df, LAST)
        r = sk.lt.rows(df, LAST)
        # The fixture's own values pass: on time 60 / 9,176 = 0.00654, within 0.00051 of 0.0065.
        ok = sk.k1(c, r, cohort=(76, 9176.0, 0.0065, 0.473),
                   cells={("U", "13-24"): (7, 2, 1900.0, 0.0)})
        self.assertTrue(ok["pass"])
        bad = sk.k1(c, r, cohort=(76, 9176.0, 0.0075, 0.473),
                    cells={("U", "13-24"): (7, 2, 1900.0, 0.0)})
        self.assertFalse(bad["pass"])

    def test_k2(self):
        _, online, info, cl = built()
        links = sk.link(info, cl)
        months = sk.credit(links, sk.replacement(links, online)[0])
        possible = sk.possible_keys(info, cl)
        self.assertTrue(sk.k2(info, links, months, possible, LAST)["pass"])
        # An arrival used twice, and a replaced leaver outside bound B, both fail.
        bad = links + [dict(links[0], leavers=["3/S"], plant="3", family="solar")]
        out = sk.k2(info, bad, dict(months, **{"3/S": 1.0}), possible, LAST)
        self.assertEqual((out["arrivals_reused"], out["wrong_plant_or_family"],
                          out["replaced_outside_bound"], out["pass"]), (1, 1, 1, False))

    def test_predictions(self):
        cohort = {"replaced_share": 0.05, "on_time_before": 0.325, "on_time_after": 0.335}
        groups = {"gas_cc": {"replaced_share": 0.2}, "solar": {"replaced_share": 0.01},
                  "wind_onshore": {"replaced_share": 0.05}, "battery": {"replaced_share": 0.0}}
        before = {"L1": {"held": False}, "L2": {"held": True}}
        after = {"L1": {"held": False}, "L2": {"held": False}}
        p = sk.predictions(cohort, groups, {"replaced_share": 0.1}, before, after)
        self.assertTrue(p["S1"]["held"])
        self.assertEqual((p["S2"]["rise"], p["S2"]["held"]), (0.01, True))
        self.assertTrue(p["S3"]["held"])
        self.assertTrue(p["S4"]["held"])
        self.assertEqual((p["S5"]["unchanged"], p["S5"]["held"]),
                         ({"L1": True, "L2": False}, False))
        # Edges: 0.20 is inside S1's range, 0.0299 is not; a rise of 0.02 fails S2; equal shares
        # fail S3; a missing group leaves S4 open.
        cohort2 = {"replaced_share": 0.2, "on_time_before": 0.3, "on_time_after": 0.32}
        p2 = sk.predictions(cohort2, dict(groups, battery={"replaced_share": None}),
                            {"replaced_share": 0.2}, before, before)
        self.assertTrue(p2["S1"]["held"])
        self.assertFalse(p2["S2"]["held"])
        self.assertFalse(p2["S3"]["held"])
        self.assertIsNone(p2["S4"]["held"])
        self.assertTrue(p2["S5"]["held"])
        p3 = sk.predictions(dict(cohort, replaced_share=0.0299), groups,
                            {"replaced_share": 0.1}, before, before)
        self.assertFalse(p3["S1"]["held"])

    def test_write_md(self):
        df = changelog()
        res, _ = sk.run(df, LAST)
        meta = {"version": sk.__version__, "eia860m_slip": sk.es.__version__,
                "leadtime": sk.lt.__version__, "source": "x.parquet", "report_max": "2020-12"}
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "splitkey.md")
            sk.write_md(path, meta, res)
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
        self.assertIn("## Every linked cluster", text)
        self.assertIn("3 links.", text)
        self.assertIn("| all | 76 | 9176.0 | 4340.0 | 1000.0 | 1000.0 | 3000.0 | 0.230 | 0.691 |",
                      text)


if __name__ == "__main__":
    unittest.main()
