"""Tests for watchlist.py on hand-built records and steps. MV2 of Munim, Inc. (made with AI
agents). Apache-2.0."""

import unittest

import pandas as pd

import stagemoves as sm
import watchlist as wl


def m(year, month):
    return year * 12 + month - 1


def rec(status, mw, planned=None, group="solar", gen="1", plant_id=1):
    return {"plant_id_eia": plant_id, "generator_id": gen, "plant": "Plant %d" % plant_id,
            "state": "TX", "group": group, "status": status, "band": sm.band(status), "mw": mw,
            "planned_m": planned}


def report_pair():
    """Records in force in reports r - 1 (a) and r (b). The change each key should get:
    1/1 backward (U -> T, planned 6 months later), 2/1 left, 3/1 delayed by 3, 4/1 none
    (operating both times), 5/1 to_operating, 6/A left (battery, no match), 7/1 new (matches
    2/1 on rule R's terms), 8/1 new (0.2 MW off 2/1), 9/B into_planned (OT -> U)."""
    a = {"1/1": rec("U", 100.0, m(2026, 9)),
         "2/1": rec("P", 50.0, m(2027, 6), plant_id=2),
         "3/1": rec("T", 20.0, m(2026, 12), plant_id=3),
         "4/1": rec("OP", 30.0, plant_id=4),
         "5/1": rec("U", 8.0, m(2026, 8), plant_id=5),
         "6/A": rec("L", 12.0, m(2028, 1), group="battery", gen="A", plant_id=6),
         "9/B": rec("OT", 15.0, gen="B", plant_id=9)}
    b = {"1/1": rec("T", 100.0, m(2027, 3)),
         "3/1": rec("T", 20.0, m(2027, 3), plant_id=3),
         "4/1": rec("OP", 30.0, plant_id=4),
         "5/1": rec("OP", 8.0, m(2026, 8), plant_id=5),
         "7/1": rec("P", 50.03, m(2027, 6), plant_id=7),
         "8/1": rec("P", 50.2, m(2027, 6), plant_id=8),
         "9/B": rec("U", 15.0, m(2026, 11), gen="B", plant_id=9)}
    return a, b


def frame(recs, cols):
    return pd.DataFrame(recs, columns=cols)


class ClassifyTests(unittest.TestCase):
    def test_classify(self):
        cases = [((rec("U", 1), rec("TS", 1)), "within_band"),
                 ((rec("U", 1, 100), rec("T", 1, 106)), "backward"),
                 ((rec("P", 1), rec("T", 1)), "forward"),
                 ((rec("T", 1), rec("OP", 1)), "to_operating"),
                 ((rec("L", 1), rec("IP", 1)), "exit_other"),
                 ((rec("P", 1), None), "left"),
                 ((None, rec("L", 1)), "new"),
                 ((rec("OT", 1), rec("U", 1)), "into_planned"),
                 ((rec("U", 1, 100), rec("U", 1, 103)), "delayed"),
                 ((rec("U", 1, 100), rec("U", 1, 98)), "advanced"),
                 ((rec("U", 1, 100), rec("U", 1, 100)), None),
                 ((rec("U", 1, None), rec("U", 1, 103)), None),
                 ((rec("OP", 1), rec("OP", 1)), None),
                 ((None, rec("OP", 1)), None),
                 ((rec("OT", 1), rec("OT", 1)), None),
                 ((rec("OP", 1), None), None)]
        self.assertEqual([wl.classify(*x) for x, _ in cases], [want for _, want in cases])

    def test_parse_month(self):
        self.assertEqual(wl.parse_month("2026-08"), 2026 * 12 + 7)
        self.assertEqual(wl.parse_month(" 2016-01 "), m(2016, 1))


class RowTests(unittest.TestCase):
    def setUp(self):
        a, b = report_pair()
        self.a, self.b = a, b
        self.rows = wl.changes(a, b, {"1/1": 2, "4/1": 5})

    def test_changes(self):
        got = [(r["key"], r["change"], r["mw"], r["shift_months"]) for r in self.rows]
        self.assertEqual(got, [("1/1", "backward", 100.0, 6), ("2/1", "left", 50.0, None),
                               ("3/1", "delayed", 20.0, 3), ("5/1", "to_operating", 8.0, 0),
                               ("6/A", "left", 12.0, None), ("7/1", "new", 50.03, None),
                               ("8/1", "new", 50.2, None), ("9/B", "into_planned", 15.0, None)])
        r = self.rows[0]
        self.assertEqual((r["status_prev"], r["status_now"], r["band_prev"], r["band_now"],
                          r["planned_prev"], r["planned_now"], r["backward_before"]),
                         ("U", "T", "building", "approved", "2026-09", "2027-03", 2))
        r = self.rows[1]
        self.assertEqual((r["status_now"], r["mw_now"], r["planned_now"], r["plant"],
                          r["backward_before"]), (None, None, None, "Plant 2", 0))
        r = self.rows[7]
        self.assertEqual((r["status_prev"], r["band_prev"], r["mw_prev"], r["planned_prev"],
                          r["band_now"], r["plant_id_eia"]),
                         ("OT", "other", 15.0, None, "building", 9))

    def test_flag_rekeys(self):
        self.assertEqual(wl.flag_rekeys(self.rows), 1)
        self.assertEqual({r["key"]: r["possible_rekey"] for r in self.rows if r["possible_rekey"]},
                         {"2/1": "7/1", "7/1": "2/1"})

    def test_partition(self):
        p = wl.partition(self.a, self.b)
        self.assertEqual({k: (v["n"], v["mw"]) for k, v in p.items()},
                         {"forward": (0, 0.0), "held": (1, 20.0), "backward": (1, 100.0),
                          "to_operating": (1, 8.0), "exit_other": (0, 0.0), "left": (2, 62.0)})

    def test_top_and_out(self):
        self.assertEqual([r["key"] for r in wl.top(self.rows, ("new",))], ["8/1", "7/1"])
        self.assertEqual([r["key"] for r in wl.top(self.rows, ("exit_other", "left"))],
                         ["2/1", "6/A"])
        o = wl._out(self.rows[5])
        self.assertEqual((o["mw"], o["mw_prev"], o["mw_now"]), (50.0, None, 50.0))

    def test_summary(self):
        zero = {c: (0, 0.0) for c in wl.CHANGES if c not in wl.UNTIMED}
        hist = [dict(zero, m=0, forward=(1, 10.0), left=(1, 4.0), new=(3, 30.0)),
                dict(zero, m=1, backward=(2, 40.0), left=(3, 9.0), new=(1, 10.0)),
                dict(zero, m=2, backward=(1, 5.0), left=(2, 1.0), new=(2, 70.0))]
        s = {r["change"]: r for r in wl.summary(self.rows, hist)}
        self.assertEqual([r["change"] for r in wl.summary(self.rows, hist)], list(wl.CHANGES))
        cols = ("n", "mw", "median_n", "max_n", "median_mw", "max_mw", "pairs")
        self.assertEqual(tuple(s["backward"][c] for c in cols), (1, 100.0, 1, 2, 5.0, 40.0, 3))
        self.assertEqual(tuple(s["left"][c] for c in cols), (2, 62.0, 2, 3, 4.0, 9.0, 3))
        self.assertEqual(tuple(s["new"][c] for c in cols), (2, 100.2, 2, 3, 30.0, 70.0, 3))
        self.assertEqual(tuple(s["forward"][c] for c in cols), (0, 0.0, 0, 1, 0.0, 10.0, 3))
        self.assertEqual(tuple(s["delayed"][c] for c in cols),
                         (1, 20.0, None, None, None, None, 0))
        self.assertEqual(s["within_band"]["pairs"], 3)


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.t = frame([(10, "A", "U", "building", 10.0), (10, "B", "P", "early", 5.0),
                        (10, "C", "OT", "other", 7.0),
                        (11, "A", "TS", "building", 10.0), (11, "B", "P", "early", 5.0),
                        (11, "C", "U", "building", 7.0), (11, "D", "L", "early", 3.0),
                        (12, "A", "OP", "operating", 10.0), (12, "B", "T", "approved", 5.0),
                        (12, "D", "L", "early", 3.0), (12, "E", "P", "early", 4.0)],
                       ["m", "key", "status", "band", "mw"])
        self.s = frame([(10, "A", "building", "held", "U", "TS", 10.0),
                        (10, "B", "early", "held", "P", "P", 5.0),
                        (11, "A", "building", "to_operating", "U", "OP", 10.0),
                        (11, "B", "early", "forward", "P", "T", 5.0),
                        (11, "D", "early", "held", "L", "L", 3.0)],
                       ["m", "key", "band", "move", "status", "status1", "mw"])
        self.left = frame([(11, "C", "building", 7.0)], ["m", "key", "band", "mw"])

    def test_history(self):
        h = wl.history(self.t, self.s, self.left, 10, 13)
        self.assertEqual([x["m"] for x in h], [10, 11])
        want = [{"forward": (0, 0.0), "backward": (0, 0.0), "to_operating": (0, 0.0),
                 "exit_other": (0, 0.0), "within_band": (1, 10.0), "left": (0, 0.0),
                 "new": (1, 3.0), "into_planned": (1, 7.0)},
                {"forward": (1, 5.0), "backward": (0, 0.0), "to_operating": (1, 10.0),
                 "exit_other": (0, 0.0), "within_band": (0, 0.0), "left": (1, 7.0),
                 "new": (1, 4.0), "into_planned": (0, 0.0)}]
        self.assertEqual([{k: v for k, v in x.items() if k != "m"} for x in h], want)

    def test_backward_before(self):
        s = frame([(9, "X", "backward"), (10, "X", "backward"), (11, "Y", "backward"),
                   (12, "X", "backward"), (11, "Z", "held")], ["m", "key", "move"])
        self.assertEqual(wl.backward_before(s, 10, 13), {"X": 1, "Y": 1})


class CheckTests(unittest.TestCase):
    def test_checks(self):
        a, b = report_pair()
        rows = wl.changes(a, b, {})
        part = wl.partition(a, b)
        cols = ["m", "key", "band", "move", "mw"]
        s = frame([(12, "1/1", "building", "backward", 100.0),
                   (12, "3/1", "approved", "held", 20.0),
                   (12, "5/1", "building", "to_operating", 8.0),
                   (11, "1/1", "building", "held", 100.0)], cols)
        left = frame([(12, "2/1", "early", 50.0), (12, "6/A", "early", 12.0)],
                     ["m", "key", "band", "mw"])
        c = wl.checks(rows, part, a, s, left, 13)
        self.assertEqual((c["C2"]["planned_mw"], c["C2"]["moves_mw"]), (190.0, 190.0))
        self.assertEqual([c[k]["pass"] for k in ("C1", "C2", "C3", "C4")], [True] * 4)
        self.assertTrue(c["all_pass"])
        bad = wl.checks(rows, part, a, s[s["key"] != "3/1"], left, 13)
        self.assertEqual([bad[k]["pass"] for k in ("C1", "C2", "C3", "C4")],
                         [True, True, False, True])
        self.assertFalse(bad["all_pass"])


if __name__ == "__main__":
    unittest.main()
