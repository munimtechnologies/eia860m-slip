"""Tests for monthsteps.py on hand-built steps. MV2 of Munim, Inc. (made with AI agents).
Apache-2.0."""

import unittest

import pandas as pd

import monthsteps as ms


def m(year, month):
    return year * 12 + month - 1


def steps():
    """Steps as stagemoves.steps returns them (only the columns monthsteps reads).

    The month in each comment is the calendar month of report m + 1; * = inside the window.
    """
    recs = [(m(2016, 11), "1/A", "building", "backward", 100.0),    # Dec *
            (m(2016, 12), "1/A", "approved", "forward", 100.0),     # Jan *
            (m(2017, 5), "2/B", "building", "held", 50.0),          # Jun
            (m(2017, 5), "3/C", "building", "backward", 20.0),      # Jun
            (m(2017, 6), "3/C", "approved", "held", 20.0),          # Jul
            (m(2017, 1), "4/D", "early", "forward", 30.0),          # Feb *
            (m(2017, 7), "4/D", "approved", "held", 30.0),          # Aug
            (m(2017, 8), "5/E", "early", "held", 10.0),             # Sep
            (m(2017, 2), "6/F", "early", "exit_other", 5.0),        # Mar *
            (m(2026, 1), "7/G", "building", "backward", 40.0),      # Feb 2026: after the pool
            (m(2017, 9), "8/H", "building", "to_operating", 60.0),  # Oct
            (m(2016, 5), "9/I", "building", "held", 10.0)]          # Jun 2016
    s = pd.DataFrame(recs, columns=["m", "key", "band", "move", "mw"])
    s["year"] = (s["m"] // 12).astype(int)
    return s


def pooled_rows(approved_mw=120.0):
    """stagemoves.pooled rows for steps(), written out by hand."""
    return [{"band": "early", "steps": 3, "step_mw": 45.0},
            {"band": "approved", "steps": 3, "step_mw": 150.0},
            {"band": "building", "steps": 5, "step_mw": 240.0, "early_mw": 0.0,
             "approved_mw": approved_mw}]


class MonthTests(unittest.TestCase):
    def test_report_month(self):
        self.assertEqual([ms.report_month(x) for x in (m(2016, 11), m(2016, 12), m(2017, 1),
                                                       m(2025, 12))],
                         [12, 1, 2, 1])

    def test_pooled_steps(self):
        p = ms.pooled_steps(steps())
        self.assertEqual(len(p), 11)
        self.assertNotIn("7/G", set(p["key"]))
        self.assertEqual(sorted(set(int(x) for x in p["month"])), [1, 2, 3, 6, 7, 8, 9, 10, 12])

    def test_by_month(self):
        rows = {r["month"]: r for r in ms.by_month(ms.pooled_steps(steps()))}
        self.assertEqual(len(rows), 12)
        j = rows[6]
        self.assertEqual((j["window"], j["reports"], j["steps"], j["step_mw"], j["backward_n"],
                          j["backward_rate"], j["backward_building_mw"], j["forward_n"],
                          j["forward_rate"], j["exit_other_rate"]),
                         ("no", 2, 3, 80.0, 1, 0.3333, 20.0, 0, None, 0.0))
        a = rows[1]
        self.assertEqual((a["window"], a["reports"], a["steps"], a["backward_n"],
                          a["backward_rate"], a["forward_n"], a["forward_rate"]),
                         ("yes", 1, 1, 0, 0.0, 1, 1.0))
        e = rows[4]
        self.assertEqual((e["reports"], e["steps"], e["step_mw"], e["backward_rate"]),
                         (0, 0, 0.0, None))
        self.assertEqual(sum(r["steps"] for r in rows.values()), 11)

    def test_compare(self):
        c = {r["kind"]: r for r in ms.compare(ms.pooled_steps(steps()))}
        b = c["backward"]
        self.assertEqual((b["in_n"], b["in_steps"], b["in_rate"], b["out_n"], b["out_steps"],
                          b["out_rate"], b["ratio"]), (1, 2, 0.5, 1, 6, 0.1667, 3.0))
        self.assertEqual((b["in_mw_rate"], b["out_mw_rate"], b["mw_ratio"]),
                         (0.5, 0.1053, 4.75))
        bb = c["backward_building"]
        self.assertEqual((bb["in_rate"], bb["out_rate"], bb["ratio"]), (1.0, 0.25, 4.0))
        f = c["forward"]
        self.assertEqual((f["in_n"], f["in_steps"], f["in_rate"], f["out_rate"], f["ratio"]),
                         (2, 3, 0.6667, 0.0, None))
        x = c["exit_other"]
        self.assertEqual((x["in_rate"], x["out_steps"], x["out_rate"], x["ratio"]),
                         (0.25, 7, 0.0, None))
        o = c["to_operating"]
        self.assertEqual((o["in_rate"], o["out_rate"], o["ratio"]), (0.0, 0.1429, 0.0))

    def test_per_year(self):
        y = {r["year"]: r for r in ms.per_year(ms.pooled_steps(steps()), "backward")}
        self.assertEqual(sorted(y), list(range(2016, 2026)))
        self.assertEqual((y[2016]["in_rate"], y[2016]["out_rate"], y[2016]["higher"]),
                         (0.5, 0.0, True))
        self.assertEqual((y[2017]["in_rate"], y[2017]["out_rate"], y[2017]["higher"]),
                         (None, 0.2, False))
        self.assertEqual((y[2020]["in_rate"], y[2020]["higher"]), (None, False))

    def test_checks(self):
        rows = ms.by_month(ms.pooled_steps(steps()))
        c = ms.checks(rows, pooled_rows(), {"all_pass": True})
        self.assertEqual((c["C1"]["steps"], c["C1"]["step_mw"], c["C1"]["backward_building_mw"],
                          c["C1"]["pass"]), (11, 435.0, 120.0, True))
        self.assertEqual(c["C2"]["months_without_10_reports"], list(range(1, 13)))
        self.assertEqual([c[k]["pass"] for k in ("C1", "C2", "C3")], [True, False, True])
        self.assertFalse(c["all_pass"])
        bad = ms.checks(rows, pooled_rows(approved_mw=100.0), {"all_pass": False})
        self.assertEqual([bad[k]["pass"] for k in ("C1", "C2", "C3")], [False, False, False])

    def test_predictions(self):
        p = ms.pooled_steps(steps())
        w = ms.predictions(p, ms.per_year(p, "backward"))
        self.assertEqual((w["W1"]["ratio"], w["W1"]["held"]), (3.0, True))
        self.assertEqual((w["W2"]["ratio"], w["W2"]["held"]), (None, None))
        self.assertEqual((w["W3"]["years_higher"], w["W3"]["years"], w["W3"]["held"]),
                         (1, 10, False))
        self.assertEqual((w["W4"]["ratio"], w["W4"]["held"]), (None, None))


if __name__ == "__main__":
    unittest.main()
