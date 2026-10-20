"""Tests for stagemoves.py on a hand-built changelog. MV2 of Munim, Inc. (made with AI agents).
Apache-2.0."""

import unittest

import numpy as np
import pandas as pd

import stagemoves as sm


def m(year, month):
    return year * 12 + month - 1


def changelog():
    """EIA-860M records: report, valid until, plant, generator, MW, status, technology.

    1/A  building Jan-Feb 2016, approved Mar-Apr, building May-Jul, operating from Aug
    2/B  early Feb-Mar 2016, approved Apr-May, building from Jun
    3/C  early Mar-Apr 2016, building from May
    4/D  building Jan-Apr 2016, then no longer listed
    5/E  other (OT) from Feb 2016
    6/F  building Jan 2016, cancelled (CN) from Feb
    9/Z  operating from Jun 2017 (never planned; sets the last report)
    """
    recs = [("2016-01-01", "2016-03-01", 1, "A", 100.0, "U", "Solar Photovoltaic"),
            ("2016-03-01", "2016-05-01", 1, "A", 100.0, "T", "Solar Photovoltaic"),
            ("2016-05-01", "2016-08-01", 1, "A", 100.0, "U", "Solar Photovoltaic"),
            ("2016-08-01", None, 1, "A", 100.0, "OP", "Solar Photovoltaic"),
            ("2016-02-01", "2016-04-01", 2, "B", 50.0, "P", "Onshore Wind Turbine"),
            ("2016-04-01", "2016-06-01", 2, "B", 50.0, "T", "Onshore Wind Turbine"),
            ("2016-06-01", None, 2, "B", 50.0, "U", "Onshore Wind Turbine"),
            ("2016-03-01", "2016-05-01", 3, "C", 20.0, "L", "Batteries"),
            ("2016-05-01", None, 3, "C", 20.0, "V", "Batteries"),
            ("2016-01-01", "2016-04-01", 4, "D", 30.0, "U", "Solar Photovoltaic"),
            ("2016-02-01", None, 5, "E", 5.0, "OT", "Solar Photovoltaic"),
            ("2016-01-01", "2016-02-01", 6, "F", 10.0, "U", "Solar Photovoltaic"),
            ("2016-02-01", None, 6, "F", 10.0, "CN", "Solar Photovoltaic"),
            ("2017-06-01", None, 9, "Z", 1.0, "OP", "Solar Photovoltaic")]
    raw = pd.DataFrame(recs, columns=["report_date", "valid_until_date", "plant_id_eia",
                                      "generator_id", "capacity_mw", "operational_status_code",
                                      "technology_description"])
    return sm.es.prepare(raw)


LAST = m(2017, 6)


def built():
    df = changelog()
    t = sm.timeline(df, sm.START_M, LAST)
    s, left = sm.steps(t, LAST)
    return df, t, s, left


def moves(s, key):
    f = s[s["key"] == key].sort_values("m")
    return [(int(a), b) for a, b in zip(f["m"], f["move"])]


class StageTests(unittest.TestCase):
    def test_band(self):
        self.assertEqual([sm.band(x) for x in ("OP", "SB", "U", "V", "TS", "T", "P", "L", "OT",
                                               "CN", "IP", "RE")],
                         ["operating", "operating", "building", "building", "building",
                          "approved", "early", "early", "other", "other", "other", "other"])

    def test_move(self):
        self.assertEqual([sm.move(*x) for x in (("building", "approved"), ("approved", "early"),
                                                ("early", "building"), ("approved", "approved"),
                                                ("building", "operating"), ("building", "other"))],
                         ["backward", "backward", "forward", "held", "to_operating", "exit_other"])

    def test_rekeyed(self):
        df = pd.DataFrame({"key": ["1/A", "7/A", "8/B"], "mw": [1.0, 2.0, 3.0]})
        out = sm.rekeyed(df, [{"plan_key": "1/A", "entry_key": "7/A"}])
        self.assertEqual(list(out["key"]), ["1/A", "1/A", "8/B"])
        self.assertEqual(list(df["key"]), ["1/A", "7/A", "8/B"])

    def test_timeline(self):
        _, t, _, _ = built()
        self.assertEqual(sorted(set(t["key"])), ["1/A", "2/B", "3/C", "4/D", "5/E", "6/F"])
        a = t[t["key"] == "1/A"].sort_values("m")
        self.assertEqual(list(a["band"])[:8], ["building", "building", "approved", "approved",
                                               "building", "building", "building", "operating"])
        self.assertEqual(int(a["m"].min()), sm.START_M)
        self.assertEqual(int(t["m"].max()), LAST)
        self.assertEqual(int(t.duplicated(["m", "key"]).sum()), 0)
        d = t[t["key"] == "4/D"]
        self.assertEqual(sorted(int(x) for x in d["m"]), [m(2016, i) for i in range(1, 5)])

    def test_steps(self):
        _, _, s, left = built()
        self.assertEqual(moves(s, "1/A"),
                         [(m(2016, 1), "held"), (m(2016, 2), "backward"), (m(2016, 3), "held"),
                          (m(2016, 4), "forward"), (m(2016, 5), "held"), (m(2016, 6), "held"),
                          (m(2016, 7), "to_operating")])
        self.assertEqual(moves(s, "6/F"), [(m(2016, 1), "exit_other")])
        self.assertEqual(moves(s, "5/E"), [])
        self.assertEqual(moves(s, "4/D"), [(m(2016, i), "held") for i in (1, 2, 3)])
        self.assertEqual([(r.key, int(r.m), r.band) for r in left.itertuples()],
                         [("4/D", m(2016, 4), "building")])
        self.assertEqual(int(s["m"].max()), LAST - 1)

    def test_online(self):
        _, _, s, _ = built()
        a = s[s["key"] == "1/A"].set_index("m")["online_12"]
        self.assertEqual(a[m(2016, 2)], 1.0)
        self.assertTrue(np.isnan(a[m(2016, 7)]))
        b = s[s["key"] == "2/B"].set_index("m")["online_12"]
        self.assertEqual(b[m(2016, 6)], 0.0)
        self.assertTrue(np.isnan(b[m(2016, 7)]))

    def test_matrix(self):
        _, _, s, left = built()
        rows = {r["band"]: r for r in sm.matrix(s[s["year"] == 2016], left[left["year"] == 2016],
                                                 {"year": 2016})}
        b = rows["building"]
        self.assertEqual((b["steps"], b["step_mw"], b["held_mw"], b["backward_mw"],
                          b["to_operating_mw"], b["exit_other_mw"], b["forward_mw"], b["left_mw"],
                          b["backward_share"], b["adds_up"]),
                         (22, 1040.0, 830.0, 100.0, 100.0, 10.0, 0.0, 30.0, 0.0962, True))
        a = rows["approved"]
        self.assertEqual((a["steps"], a["step_mw"], a["forward_mw"], a["held_mw"]),
                         (4, 300.0, 150.0, 150.0))
        e = rows["early"]
        self.assertEqual((e["steps"], e["step_mw"], e["forward_mw"], e["held_mw"]),
                         (4, 140.0, 70.0, 70.0))

    def test_pooled_and_groups(self):
        _, _, s, left = built()
        p = {r["band"]: r for r in sm.pooled(s, left)}["building"]
        self.assertEqual((p["step_mw"], p["building_mw"], p["approved_mw"], p["operating_mw"],
                          p["other_mw"], p["early_mw"], p["left_mw"]),
                         (1390.0, 1180.0, 100.0, 100.0, 10.0, 0.0, 30.0))
        g = {r["group"]: r for r in sm.by_group(s)}
        self.assertEqual((g["solar"]["building_step_mw"], g["solar"]["building_backward_share"]),
                         (600.0, 0.1667))
        self.assertEqual(g["wind_onshore"]["building_backward_share"], 0.0)
        self.assertEqual(g["battery"]["building_step_mw"], 240.0)
        self.assertIsNone(g["gas_cc"]["building_backward_share"])

    def test_outcomes(self):
        _, _, s, _ = built()
        o = {(r["band"], r["move"]): r for r in sm.outcomes(s)}
        self.assertEqual((o[("building", "held")]["scored_mw"], o[("building", "held")]["online_mw"],
                          o[("building", "held")]["online_share"]), (480.0, 300.0, 0.625))
        self.assertEqual(o[("building", "backward")]["online_share"], 1.0)
        self.assertIsNone(o[("early", "backward")]["online_share"])

    def test_flicker_and_paths(self):
        _, t, s, _ = built()
        self.assertEqual(sm.flicker(t, s, LAST),
                         {"generators": 1, "returned": 1, "mw": 100.0, "share": 1.0})
        self.assertEqual(sm.paths(t), {"generators": 2, "mw": 70.0, "through_approved_n": 1,
                                       "through_approved_mw": 50.0, "share": 0.7143})

    def test_top_backward(self):
        _, _, s, _ = built()
        self.assertEqual(sm.top_backward(s),
                         [{"key": "1/A", "plant": None, "group": "solar", "mw": 100.0,
                           "moved_in": "2016-03", "from_status": "U", "to_status": "T",
                           "online_12": "yes"}])

    def test_checks(self):
        df, t, s, left = built()
        rows = sm.matrix(s, left, {"year": 0})
        c = sm.checks(t, sm.sample_check(df, s, (m(2016, 1),)), rows, [], sm.START_M, LAST)
        self.assertEqual(c["S1"]["months"]["2016-01"],
                         {"expected_mw": 140.0, "expected_n": 3, "got_mw": 140.0, "got_n": 3})
        self.assertEqual([c[k]["pass"] for k in ("S1", "S2", "S3", "S4")],
                         [True, True, False, True])
        self.assertFalse(c["all_pass"])

    def test_predictions(self):
        _, t, s, _ = built()
        p = sm.predictions(s, sm.flicker(t, s, LAST), sm.paths(t))
        self.assertEqual((p["M1"]["building_backward_share"], p["M1"]["held"]), (0.0719, False))
        self.assertEqual((p["M2"]["returned_share"], p["M2"]["held"]), (1.0, True))
        self.assertEqual((p["M3"]["held_online_share"], p["M3"]["backward_online_share"],
                          p["M3"]["gap"], p["M3"]["held"]), (0.625, 1.0, -0.375, False))
        self.assertEqual((p["M4"]["through_approved_share"], p["M4"]["held"]), (0.7143, False))


if __name__ == "__main__":
    unittest.main()
