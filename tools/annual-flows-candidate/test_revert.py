"""Unit tests for revert.py. MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import json
import os
import tempfile
import unittest

import pandas as pd

import eia860m_slip as es
import revert as rv
import watchlist as wl

M = wl.parse_month
A = ("OP", None, 10.0)
B = ("OA", None, 10.0)
C = ("SB", None, 10.0)


class FieldTests(unittest.TestCase):
    def test_proj(self):
        self.assertEqual(rv.proj("op", 5, 10), ("OP", None, 10.0))
        self.assertEqual(rv.proj("U", 24320.0, 5), ("U", 24320, 5.0))
        self.assertEqual(rv.proj(float("nan"), None, None), ("", None, None))
        self.assertEqual(rv.proj("nan", 3, 1), ("", None, 1.0))

    def test_w_proj_retired_reads_re(self):
        self.assertEqual(rv.w_proj(None, "Retired", None, 50.0), ("RE", None, 50.0))
        self.assertEqual(rv.w_proj("", "Retired", None, 50.0), ("RE", None, 50.0))
        self.assertEqual(rv.w_proj("OP", "Operating", 3, 5), ("OP", None, 5.0))
        self.assertEqual(rv.w_proj(None, "Operating", None, 5), ("", None, 5.0))

    def test_match(self):
        self.assertTrue(rv.match(A, A))
        self.assertFalse(rv.match(A, B))
        self.assertTrue(rv.match(("", None, 10.0), B))
        self.assertFalse(rv.match(("U", 1, 5.0), ("U", 2, 5.0)))
        self.assertTrue(rv.match(("U", 1, 5.0), ("U", None, 5.0)))
        self.assertTrue(rv.match(("OP", None, 10.0), ("OP", None, 10.04)))
        self.assertFalse(rv.match(("OP", None, 10.0), ("OP", None, 10.1)))

    def test_differs(self):
        self.assertEqual(rv.differs(("OP", None, 10.0), ("OA", None, 12.0)), ["status", "MW"])
        self.assertEqual(rv.differs(("U", 5, 1.0), ("U", 6, 1.0)), ["planned month"])


class SimulateTests(unittest.TestCase):
    def test_value_held_before_is_dropped(self):
        self.assertEqual(rv.simulate([A, B], B, [A, A, C]), [B, B, C])

    def test_a_b_a_within_the_months(self):
        self.assertEqual(rv.simulate([A], A, [B, A]), [B, B])

    def test_absent_months(self):
        self.assertEqual(rv.simulate([], None, [None, A, None, A]), [None, A, A, A])


class ScoreTests(unittest.TestCase):
    def test_score(self):
        units = [{"w": A, "p": B, "sim": B}, {"w": A, "p": A, "sim": B},
                 {"w": A, "p": C, "sim": A}, {"w": A, "p": A, "sim": None}]
        self.assertEqual(rv.score(units), {"units": 4, "disagree": 2, "sim_stale": 2, "hits": 1,
                                           "coverage": 0.5, "precision": 0.5})

    def test_classify(self):
        hit = {"w": A, "p": B, "sim": B}
        miss = {"w": A, "p": C, "sim": A}
        self.assertEqual(rv.classify(hit, [], []), "predicted")
        self.assertEqual(rv.classify(miss, [A], []), "pudl_later")
        self.assertEqual(rv.classify(miss, [], [A]), "held_before")
        self.assertEqual(rv.classify(miss, [], []), "other")
        self.assertEqual(rv.classify(miss, [C], [B]), "other")

    def test_verdict(self):
        res = {"score": {"hits": 10, "disagree": 11, "sim_stale": 21}, "repeats": {"repeats": 0},
               "named": [{"held": True}, {"held": False}]}
        v = rv.verdict(res, {"C1": {"ok": True}})
        self.assertEqual(v["predictions"], {"P1": True, "P2": True, "P3": False, "P4": False})
        self.assertEqual(v["held"], 2)
        self.assertTrue(v["scored"])
        self.assertFalse(rv.verdict(res, {"C1": {"ok": False}})["scored"])


class RepeatTests(unittest.TestCase):
    def test_repeat_count_treats_missing_as_equal(self):
        df = pd.DataFrame({
            "report_date": pd.to_datetime(["2024-01-01", "2024-02-01", "2024-03-01",
                                           "2024-01-01", "2024-02-01"]),
            "valid_until_date": pd.to_datetime(["2024-02-01", "2024-03-01", "2024-04-01",
                                                "2024-02-01", "2024-03-01"]),
            "plant_id_eia": [1, 1, 1, 2, 2],
            "generator_id": ["A", "A", "A", "B", "B"],
            "operational_status_code": ["OP", "OA", "OP", "OP", "OP"],
            "capacity_mw": [10.0, 10.0, 10.0, float("nan"), float("nan")]})
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "x.parquet")
            df.to_parquet(path, index=False)
            r = rv.repeat_count(path)
        self.assertEqual(r["columns"], 4)
        self.assertEqual(r["rows"], 5)
        self.assertEqual(r["repeats"], 2)
        self.assertEqual(r["generators_with_repeats"], 2)
        self.assertEqual(r["sample"], [{"key": "1/A", "report": "2024-03"},
                                       {"key": "2/B", "report": "2024-02"}])


class GateTests(unittest.TestCase):
    def test_waits_until_live(self):
        texts = iter(["nope", "has TOKEN here"])
        g = rv.wait_for("u", "TOKEN", 10, fetch=lambda url: next(texts), clock=lambda: 0,
                        pause=lambda s: None)
        self.assertTrue(g["live"])
        self.assertEqual(g["checks"], 2)

    def test_gives_up_at_deadline(self):
        def bad(url):
            raise OSError("down")
        clock = iter([0, 10000])
        g = rv.wait_for("u", "TOKEN", 1, fetch=bad, clock=lambda: next(clock),
                        pause=lambda s: None)
        self.assertFalse(g["live"])
        self.assertEqual(g["checks"], 1)
        self.assertIn("OSError", g["error"])

    def test_commit_of(self):
        body = json.dumps([{"sha": "abc", "commit": {"committer": {"date": "2026-10-21T22:00:00Z"}}}])
        self.assertEqual(rv.commit_of(fetch=lambda url: body),
                         {"sha": "abc", "date": "2026-10-21T22:00:00Z"})
        self.assertIn("error", rv.commit_of(fetch=lambda url: "[]"))


class RunTests(unittest.TestCase):
    def setUp(self):
        self.saved = (rv.MONTHS, rv.LAST, rv.NAMED)
        rv.MONTHS, rv.LAST = ("2026-01", "2026-02", "2026-03"), "2026-03"
        rv.NAMED = (("1/A", "2026-02"),)
        rows = [
            # 1/A: OP, then OA in 2025-06; back to OP in 2026, which PUDL dropped
            ("2025-01-01", "2025-06-01", 1, "A", 10.0, None, "OP"),
            ("2025-06-01", "2026-03-01", 1, "A", 10.0, None, "OA"),
            # 2/B: a new planned month each month, all taken in
            ("2026-01-01", "2026-02-01", 2, "B", 5.0, "2026-09-01", "U"),
            ("2026-02-01", "2026-03-01", 2, "B", 5.0, "2026-10-01", "U"),
            ("2026-03-01", "2026-04-01", 2, "B", 5.0, "2026-11-01", "U"),
            # 3/C: a change PUDL takes in a month after the workbook shows it
            ("2025-01-01", "2026-03-01", 3, "C", 20.0, "2027-01-01", "P"),
            ("2026-03-01", "2026-04-01", 3, "C", 20.0, "2027-06-01", "P")]
        raw = pd.DataFrame(rows, columns=["report_date", "valid_until_date", "plant_id_eia",
                                          "generator_id", "capacity_mw",
                                          "current_planned_generator_operating_date",
                                          "operational_status_code"])
        raw["technology_description"] = "Batteries"
        raw["state"] = "TX"
        self.df = es.prepare(raw)

        def frame(rows):
            return pd.DataFrame(rows, columns=["key", "sheet", "status", "planned_m", "capacity_mw"])

        self.frames = {
            "2026-01": frame([["1/A", "Operating", "OP", None, 10.0],
                              ["2/B", "Planned", "U", float(M("2026-09")), 5.0],
                              ["3/C", "Planned", "P", float(M("2027-01")), 20.0]]),
            "2026-02": frame([["1/A", "Operating", "OP", None, 10.0],
                              ["2/B", "Planned", "U", float(M("2026-10")), 5.0],
                              ["3/C", "Planned", "P", float(M("2027-06")), 20.0]]),
            "2026-03": frame([["1/A", "Operating", "OP", None, 10.0],
                              ["2/B", "Planned", "U", float(M("2026-11")), 5.0],
                              ["3/C", "Planned", "P", float(M("2027-06")), 20.0]])}
        self.repeats = {"repeats": 0, "rows": 7, "columns": 5, "generators_with_repeats": 0,
                        "column_names": [], "sample": []}

    def tearDown(self):
        rv.MONTHS, rv.LAST, rv.NAMED = self.saved

    def test_run(self):
        r = rv.run(self.df, self.frames, self.repeats)
        self.assertEqual(r["score"], {"units": 9, "disagree": 4, "sim_stale": 3, "hits": 3,
                                      "coverage": 0.75, "precision": 1.0})
        self.assertEqual(r["by_month"]["2026-02"], {"units": 3, "predicted": 1, "pudl_later": 1,
                                                    "held_before": 0, "other": 0})
        self.assertEqual(r["pairs"], [{"field": "status", "workbook": "OP", "pudl": "OA", "n": 3}])
        self.assertEqual(r["august"], [{"key": "1/A", "fields": "status",
                                        "workbook": "OP, -, 10.0 MW", "pudl": "OA, -, 10.0 MW",
                                        "pudl_reported": "2025-06", "differs_since": "2026-01",
                                        "workbook_mw": 10.0}])
        self.assertEqual(r["named"], [{"key": "1/A", "month": "2026-02", "workbook": "OP, -, 10.0 MW",
                                       "records_before": 2, "matching_reports": ["2025-01"],
                                       "held": True}])
        self.assertEqual(r["august_workbook_only"], 0)

    def test_render(self):
        r = rv.run(self.df, self.frames, self.repeats)
        checks = {"C1 workbooks": {"ok": True, "detail": "x"}}
        md = rv.render({"checks": checks, "verdict": rv.verdict(r, checks), "result": r})
        self.assertIn("Scored: 3 of 4 predictions held.", md)
        self.assertIn("| P2 coverage | 0.90 | 0.75 (3 of 4) | False |", md)
        self.assertIn("| 2026-02 | 3 | 1 | 1 | 0 | 0 |", md)
        self.assertIn("| 1/A | status | OP, -, 10.0 MW | OA, -, 10.0 MW | 2025-06 | 2026-01 |", md)
        self.assertIn("1 generators, 10.0 MW by the workbook.", md)
        self.assertIn("Not run: x", rv.render({"error": "x"}))
        self.assertIn("Not scored: a check failed.",
                      rv.render({"checks": {"C1": {"ok": False, "detail": "y"}},
                                 "verdict": {"scored": False}}))


if __name__ == "__main__":
    unittest.main()
