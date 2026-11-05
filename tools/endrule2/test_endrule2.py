"""Unit tests for endrule2.py (pre-registration endrule-2). No network, no pandas.

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.)."""

import unittest

import endrule2 as e2

FRESH = ("2026-02", "2026-03", "2026-04", "2026-05", "2026-06", "2026-07")


class GroupTests(unittest.TestCase):
    def test_end_groups(self):
        ends = {"1/A": "2026-03", "2/B": "2026-03", "3/C": "2026-07", "4/D": "2025-12",
                "5/E": None, "6/F": "2026-10"}
        self.assertEqual(e2.end_groups(ends, ("2026-03", "2026-07", "2026-10")),
                         {"2026-03": ["1/A", "2/B"], "2026-07": ["3/C"], "2026-10": ["6/F"]})
        self.assertEqual(e2.end_groups({}, ("2026-02",)), {"2026-02": []})

    def test_cancel_keys(self):
        sheets = {"Operating": {"1/A"}, "Canceled or Postponed": {"2/B", "3/C"},
                  "Canceled_PR": {"4/D"}, "Notes": None}
        self.assertEqual(e2.cancel_keys(sheets), {"2/B", "3/C"})

    def test_tally_uses_previous_month(self):
        groups = {"2026-03": ["1/A", "2/B", "3/C"]}
        pools = {"2026-02": {"1/A", "2/B", "9/Z"}, "2026-03": {"3/C"}}
        cancels = {"2026-03": {"1/A"}}
        self.assertEqual(e2.tally(groups, pools, cancels),
                         {"2026-03": {"n": 3, "in_prev": 2, "in_end": 1, "cancel_end": 1}})

    def test_pooled(self):
        rows = {"2026-02": {"n": 3, "in_prev": 3, "in_end": 0, "cancel_end": 2},
                "2026-03": {"n": 1, "in_prev": 0, "in_end": 1, "cancel_end": 0}}
        self.assertEqual(e2.pooled(rows, ("2026-02", "2026-03")),
                         {"n": 4, "in_prev": 3, "in_prev_share": 0.75, "in_end": 1,
                          "in_end_share": 0.25, "cancel_end": 2, "cancel_end_share": 0.5})
        self.assertEqual(e2.pooled({"2026-02": {"n": 0, "in_prev": 0, "in_end": 0,
                                                "cancel_end": 0}}, ("2026-02",))["in_prev_share"],
                         None)


class ScoreTests(unittest.TestCase):
    def metrics(self, by_end=None, **fresh):
        f = {"n": 200, "in_prev": 190, "in_prev_share": 0.95, "in_end": 10,
             "in_end_share": 0.05, "cancel_end": 120, "cancel_end_share": 0.6}
        f.update(fresh)
        rows = by_end or {e: {"n": 10, "in_prev": 9, "in_end": 1, "cancel_end": 6}
                          for e in FRESH}
        return {"latest_report": "2026-09", "build_after_merge": True, "workbooks_ok": True,
                "fresh": f, "by_end": rows}

    def test_all_hold_at_the_bars(self):
        self.assertEqual(e2.score(self.metrics()),
                         {"G1": True, "G2": True, "Q1": True, "Q2": True, "Q3": True,
                          "Q4": True})

    def test_fail_just_past_the_bars(self):
        rows = {e: {"n": 10, "in_prev": 9, "in_end": 1, "cancel_end": 6} for e in FRESH}
        rows["2026-05"] = {"n": 12, "in_prev": 10, "in_end": 0, "cancel_end": 6}
        s = e2.score(self.metrics(by_end=rows, in_prev_share=0.945, in_end_share=0.055,
                                  cancel_end_share=0.595))
        self.assertEqual(s, {"G1": True, "G2": True, "Q1": False, "Q2": False, "Q3": False,
                             "Q4": False})

    def test_q3_fails_on_one_month_listed_at_the_end(self):
        rows = {e: {"n": 10, "in_prev": 10, "in_end": 0, "cancel_end": 6} for e in FRESH}
        rows["2026-07"] = {"n": 10, "in_prev": 10, "in_end": 2, "cancel_end": 6}
        self.assertFalse(e2.score(self.metrics(by_end=rows))["Q3"])

    def test_gates_stop_scoring(self):
        m = self.metrics()
        m["latest_report"] = "2026-10"
        self.assertEqual(e2.score(m), {"G1": False, "G2": True})
        m = self.metrics()
        m["build_after_merge"] = False
        self.assertEqual(e2.score(m), {"G1": False, "G2": True})
        self.assertEqual(e2.score(self.metrics(n=99)), {"G1": True, "G2": False})
        m = self.metrics()
        m["workbooks_ok"] = False
        self.assertEqual(e2.score(m), {"G1": True, "G2": False})


if __name__ == "__main__":
    unittest.main()
