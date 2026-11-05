"""Unit tests for endrule.py (pre-registration endrule-1). No network, no pandas.

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.)."""

import unittest

import endrule as er


class KeyTests(unittest.TestCase):
    def test_gen_id(self):
        self.assertEqual(er.gen_id(10.0), "10")
        self.assertEqual(er.gen_id(" A1 "), "A1")
        self.assertEqual(er.gen_id("0011"), "11")
        self.assertEqual(er.gen_id("0"), "0")
        self.assertEqual(er.gen_id("00"), "0")
        self.assertEqual(er.gen_id(None), "nan")
        self.assertEqual(er.gen_id(float("nan")), "nan")
        self.assertEqual(er.gen_id(""), "nan")
        self.assertEqual(er.gen_id("GT-1"), "GT-1")
        self.assertEqual(er.gen_id(7), "7")

    def test_make_key(self):
        self.assertEqual(er.make_key("67674", "LUPE3"), "67674/LUPE3")
        self.assertEqual(er.make_key(67674.0, " LUPE3"), "67674/LUPE3")
        self.assertEqual(er.make_key("69144", "PV1"), "69144/PV1")
        self.assertIsNone(er.make_key("<NA>", "X"))
        self.assertIsNone(er.make_key(None, "X"))

    def test_months(self):
        self.assertEqual(er.month_of("2026-09-01"), "2026-09")
        self.assertEqual(er.month_of("2026-09-01 00:00:00"), "2026-09")
        self.assertIsNone(er.month_of("NaT"))
        self.assertIsNone(er.month_of(None))
        self.assertEqual(er.month_add("2026-09", 1), "2026-10")
        self.assertEqual(er.month_add("2026-12", 1), "2027-01")
        self.assertEqual(er.month_add("2026-01", -1), "2025-12")


class GroupTests(unittest.TestCase):
    def test_last_ends_takes_latest_report(self):
        rows = [("1/A", "2024-05", "2025-07"), ("1/A", "2025-07", "2026-06"),
                ("1/A", "2026-06", "2026-09"), ("2/B", "2022-01", "2026-08"),
                ("3/C", "2026-08", "2026-10"), ("3/C", "2025-01", "2026-08"),
                (None, "2026-01", "2026-02")]
        self.assertEqual(er.last_ends(rows), {"1/A": "2026-09", "2/B": "2026-08",
                                              "3/C": "2026-10"})

    def test_group_keys(self):
        ends = {"1/A": "2026-09", "2/B": "2026-08", "3/C": "2026-10", "4/D": "2026-10",
                "5/E": "2025-03", "6/F": None}
        groups, other = er.group_keys(ends)
        self.assertEqual(groups, {"A9": ["3/C", "4/D"], "A8": ["1/A"], "A7": ["2/B"]})
        self.assertEqual(other, {"2025-03": 1, "None": 1})

    def test_listed_until_exclusive(self):
        self.assertEqual(er.listed_until_exclusive([10, 12], [13, None]), [12, None])


class SheetTests(unittest.TestCase):
    ROWS = [("EIA-860M title", None, None), (None, None, None),
            ("Entity ID", "Plant ID", "Generator ID", "Status"),
            ("1", "67674", "LUPE3", "P"), ("1", "69144", "PV1", "V"),
            ("2", 65399, 3.0, "P"), ("3", None, "X", "P"), ("short",)]

    def test_find_header_and_keys(self):
        self.assertEqual(er.find_header(self.ROWS), 2)
        self.assertEqual(er.sheet_keys(self.ROWS), {"67674/LUPE3", "69144/PV1", "65399/3"})
        self.assertIsNone(er.sheet_keys([("no", "header")]))

    def test_listed_skips_canceled_and_pr(self):
        sheets = {"Operating": {"1/A"}, "Planned": {"2/B"}, "Retired": {"3/C"},
                  "Canceled or Postponed": {"4/D"}, "Planned_PR": {"5/E"}, "Notes": None}
        self.assertEqual(er.listed(sheets), {"1/A", "2/B", "3/C"})
        self.assertTrue(er.skipped("Canceled or Postponed"))
        self.assertTrue(er.skipped("Operating_PR"))
        self.assertFalse(er.skipped("Retired"))

    def test_count_in(self):
        self.assertEqual(er.count_in(["1/A", "2/B", "3/C", "4/D"], {"1/A", "3/C", "9/Z"}),
                         {"n": 4, "in": 2, "share": 0.5})
        self.assertEqual(er.count_in([], {"1/A"}), {"n": 0, "in": 0, "share": None})


class ScoreTests(unittest.TestCase):
    def metrics(self, **kw):
        m = {"latest_report": "2026-09", "build_after_merge": True, "workbooks_ok": True,
             "groups": {"A9": 30000, "A8": 40, "A7": 20},
             "A8_in_2026-08": {"n": 40, "in": 39, "share": 0.975},
             "A8_in_2026-09": {"n": 40, "in": 2, "share": 0.05},
             "A7_in_2026-07": {"n": 20, "in": 19, "share": 0.95},
             "A7_in_2026-08": {"n": 20, "in": 1, "share": 0.05},
             "A9_in_2026-09": {"n": 30000, "in": 29700, "share": 0.99},
             "diff_on_aug_planned": 3, "left_both_listed_aug": 0}
        m.update(kw)
        return m

    def test_all_hold_at_the_bars(self):
        self.assertEqual(er.score(self.metrics()),
                         {"G1": True, "G2": True, "P1": True, "P2": True, "P3": True,
                          "P4": True, "P5": True})

    def test_fail_just_past_the_bars(self):
        s = er.score(self.metrics(**{
            "A8_in_2026-08": {"n": 40, "in": 37, "share": 0.925},
            "A8_in_2026-09": {"n": 40, "in": 3, "share": 0.075},
            "A7_in_2026-08": {"n": 20, "in": 2, "share": 0.1},
            "A9_in_2026-09": {"n": 30000, "in": 29600, "share": 0.9867},
            "left_both_listed_aug": 1}))
        self.assertEqual(s, {"G1": True, "G2": True, "P1": False, "P2": False, "P3": False,
                             "P4": False, "P5": False})

    def test_gates_stop_scoring(self):
        self.assertEqual(er.score(self.metrics(latest_report="2026-10")),
                         {"G1": False, "G2": True})
        self.assertEqual(er.score(self.metrics(build_after_merge=False)),
                         {"G1": False, "G2": True})
        self.assertEqual(er.score(self.metrics(groups={"A9": 1, "A8": 9, "A7": 20})),
                         {"G1": True, "G2": False})
        self.assertEqual(er.score(self.metrics(workbooks_ok=False)),
                         {"G1": True, "G2": False})


if __name__ == "__main__":
    unittest.main()
