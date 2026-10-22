"""Unit tests for history.py. MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import json
import unittest

import pandas as pd

import history as hs
import layouts as ly
import revert as rv
import watchlist as wl

M = wl.parse_month
NAN = float("nan")
A = ("OP", None, 10.0)
B = ("OA", None, 10.0)
C = ("SB", None, 10.0)
N = ("OP", None, None)


def raw(rows):
    return pd.DataFrame(rows, dtype=object)


def frame(rows):
    return pd.DataFrame(rows, columns=["key", "sheet", "status", "planned_m", "capacity_mw"])


def pudl(rows):
    df = pd.DataFrame(rows, columns=["report_date", "valid_until_date", "plant_id_eia",
                                     "generator_id", "capacity_mw",
                                     "current_planned_generator_operating_date",
                                     "operational_status_code"])
    return hs.prepare(df)


class SimTests(unittest.TestCase):
    def test_missing_equals_only_missing(self):
        self.assertFalse(hs.sim_match(N, A))
        self.assertTrue(rv.match(N, A))
        self.assertTrue(hs.sim_match(N, N))
        self.assertTrue(hs.sim_match(A, ("OP", None, 10.04)))
        self.assertFalse(hs.sim_match(("", None, 10.0), A))

    def test_step_is_revert_simulate_when_nothing_is_missing(self):
        rows = [B, A, None, A, C, A]
        st = [[], None]
        out = [hs.step(st, w) for w in rows]
        self.assertEqual([x[0] for x in out], rv.simulate([], None, rows))
        self.assertEqual([x[0] for x in out], [B, A, A, A, C, C])
        self.assertEqual([x[1] for x in out], [False, False, False, True, False, True])

    def test_missing_mw_then_nameplate(self):
        st = [[], None]
        self.assertEqual([hs.step(st, w)[0] for w in (N, A, N)], [N, A, A])
        self.assertEqual(rv.simulate([], None, [N, A, N]), [N, N, N])


class MonthFrameTests(unittest.TestCase):
    def sheets(self):
        return {
            "Operating": raw([
                ["Monthly Generator Inventory", None, None, None, None, None],
                ["Plant ID", "Generator ID", "Plant Name", "Net Summer Capacity (MW)", "Status",
                 "Technology"],
                [1, "A", "P1", 10.0, "(OP) Operating", "Batteries"],
                [2, "01", "P2", 5.0, "OP", "Batteries"]]),
            "Planned": raw([
                ["Plant ID", "Generator ID", "Plant Name", "Nameplate Capacity (MW)", "Status",
                 "Planned Operation Month", "Planned Operation Year", "Technology"],
                [3, "B", "P3", 20.0, "(U) Under construction", 6, 2027, "Solar Photovoltaic"]]),
            "Canceled or Postponed": raw([["Plant ID", "Generator ID"], [9, "Z"]])}

    def test_nameplate_only(self):
        sheets = self.sheets()
        wb, info = hs.month_frame("2016-01", sheets)
        self.assertEqual(list(wb["key"]), ["1/A", "2/1", "3/B"])
        self.assertTrue(info["readable"])
        self.assertEqual(info["problems"], ly.month_info("2016-01", sheets)["problems"])
        self.assertEqual(info["nameplate_sheets"], ["Planned"])
        self.assertEqual(info["other_capacity_sheets"], ["Operating"])
        self.assertEqual(info["keys"], 3)
        wm = rv.w_map(wb)
        self.assertEqual(wm["1/A"], ("OP", None, None))
        self.assertEqual(wm["3/B"], ("U", 2027 * 12 + 5, 20.0))

    def test_readability_as_layouts(self):
        sheets = {"Operating": raw([["Plant ID", "Generator ID", "Nameplate Capacity (MW)"],
                                    [1, "A", 10.0]])}
        _, info = hs.month_frame("2016-01", sheets)
        self.assertFalse(info["readable"])
        self.assertEqual(info["problems"], ["Operating: no status column"])
        self.assertEqual(info["problems"], ly.month_info("2016-01", sheets)["problems"])


class ReplayTests(unittest.TestCase):
    def setUp(self):
        self.df = pudl([
            # 1/A: OP, OA, then OP again, which PUDL drops
            ("2016-01-01", "2016-02-01", 1, "A", 10.0, None, "OP"),
            ("2016-02-01", "2016-04-01", 1, "A", 10.0, None, "OA"),
            # 2/B: a new planned month each month, all taken in
            ("2016-01-01", "2016-02-01", 2, "B", 5.0, "2016-09-01", "U"),
            ("2016-02-01", "2016-03-01", 2, "B", 5.0, "2016-10-01", "U"),
            ("2016-03-01", "2016-04-01", 2, "B", 5.0, "2016-11-01", "U"),
            # 3/C: no nameplate in January, then 50 MW
            ("2016-01-01", "2016-02-01", 3, "C", NAN, None, "OP"),
            ("2016-02-01", "2016-04-01", 3, "C", 50.0, None, "OP"),
            # 4/D: listed in January, gone in February, back unchanged in March
            ("2016-01-01", "2016-02-01", 4, "D", 7.0, None, "OP")])
        self.frames = [
            ("2016-01", frame([["1/A", "Operating", "OP", None, 10.0],
                               ["2/B", "Planned", "U", float(M("2016-09")), 5.0],
                               ["3/C", "Operating", "OP", None, NAN],
                               ["4/D", "Operating", "OP", None, 7.0]])),
            ("2016-02", frame([["1/A", "Operating", "OA", None, 10.0],
                               ["2/B", "Planned", "U", float(M("2016-10")), 5.0],
                               ["3/C", "Operating", "OP", None, 50.0]])),
            ("2016-03", frame([["1/A", "Operating", "OP", None, 10.0],
                               ["2/B", "Planned", "U", float(M("2016-11")), 5.0],
                               ["3/C", "Operating", "OP", None, 50.0],
                               ["4/D", "Operating", "OP", None, 7.0]]))]

    def run_replay(self):
        log, hits = [], []
        res = hs.replay(self.df, iter(self.frames), log.append, hits.append)
        return res, log, hits

    def test_counts(self):
        res, _, _ = self.run_replay()
        y = res["years"][2016]
        want = {"months": 3, "workbook": 11, "with_pudl": 10, "units": 10, "disagree": 1,
                "sim_stale": 1, "hits": 1, "workbook_only": 1, "workbook_only_held": 1,
                "pudl_later": 0, "held_before": 0, "other": 0, "coverage": 1.0, "precision": 1.0,
                "keys_share": 0.9091, "hits_per_month": 0.33}
        self.assertEqual({k: y[k] for k in want}, want)
        self.assertEqual(res["total"]["hits"], 1)
        self.assertEqual(res["total"]["workbook"], 11)
        self.assertEqual(res["by_month"], [
            {"month": "2016-01", "units": 4, "disagree": 0, "hits": 0},
            {"month": "2016-02", "units": 3, "disagree": 0, "hits": 0},
            {"month": "2016-03", "units": 3, "disagree": 1, "hits": 1}])
        self.assertEqual(res["pairs"], [{"kind": "predicted", "field": "status", "workbook": "OP",
                                         "pudl": "OA", "n": 1}])
        self.assertEqual(res["events"], {2016: {"first": 4, "changed": 5, "left": 1, "back": 1}})
        self.assertEqual(res["samples"], [])

    def test_changelog_and_hits(self):
        _, log, hits = self.run_replay()
        self.assertEqual([(r["report_month"], r["key"], r["event"]) for r in log], [
            ("2016-01", "1/A", "first"), ("2016-01", "2/B", "first"), ("2016-01", "3/C", "first"),
            ("2016-01", "4/D", "first"), ("2016-02", "1/A", "changed"),
            ("2016-02", "2/B", "changed"), ("2016-02", "3/C", "changed"),
            ("2016-02", "4/D", "left"), ("2016-03", "1/A", "changed"),
            ("2016-03", "2/B", "changed"), ("2016-03", "4/D", "back")])
        self.assertEqual(log[1], {"report_month": "2016-01", "key": "2/B", "plant_id_eia": "2",
                                  "generator_id": "B", "event": "first", "sheet": "Planned",
                                  "status": "U", "planned_month": "2016-09", "nameplate_mw": 5.0})
        self.assertEqual(log[2]["nameplate_mw"], "")
        self.assertEqual(log[7], {"report_month": "2016-02", "key": "4/D", "plant_id_eia": "4",
                                  "generator_id": "D", "event": "left", "sheet": "", "status": "",
                                  "planned_month": "", "nameplate_mw": ""})
        self.assertEqual(hits, [{"month": "2016-03", "key": "1/A", "fields": "status",
                                 "workbook": "OP, -, 10.0 MW", "pudl": "OA, -, 10.0 MW",
                                 "pudl_reported": "2016-02", "simulated": "OA, -, 10.0 MW",
                                 "differs_since": "2016-03"}])

    def test_other_disagreement_is_sampled(self):
        df = pudl([("2016-01-01", "2016-02-01", 5, "E", 12.0, None, "OP")])
        res = hs.replay(df, iter([("2016-01", frame([["5/E", "Operating", "OP", None, 10.0]]))]))
        y = res["years"][2016]
        self.assertEqual((y["disagree"], y["hits"], y["other"], y["sim_stale"]), (1, 0, 1, 0))
        self.assertEqual(res["samples"], [{"year": 2016, "kind": "other", "rows": [
            {"key": "5/E", "month": "2016-01", "workbook": "OP, -, 10.0 MW",
             "pudl": "OP, -, 12.0 MW", "pudl_reported": "2016-01"}]}])
        self.assertEqual(res["pairs"], [{"kind": "other", "field": "MW", "workbook": "OP",
                                         "pudl": "OP", "n": 1}])

    def test_render_not_scored(self):
        res, _, _ = self.run_replay()
        checks = {"C1 workbooks": {"ok": True, "detail": "x"}}
        md = hs.render({"checks": checks, "verdict": hs.verdict(res, checks), "result": res})
        self.assertIn("Not scored: a check failed or a scored year was not read.", md)
        self.assertIn("| 2016 | 3 | 11 | 10 | 0.9091 | 10 | 1 | 1 | 1 | 1.0000 | 1.0000 | 0.33 "
                      "| 0 | 0 | 0 | 1 | 1 |", md)
        self.assertIn("| 2016 | 4 | 5 | 1 | 1 |", md)
        self.assertIn("Not run: x", hs.render({"error": "x"}))


def synthetic():
    years = {}
    for n in hs.SCORED:
        y = hs.blank_year()
        y.update(months=12, workbook=1000, with_pudl=990, units=990, disagree=100, sim_stale=150,
                 hits=100 if n == 2025 else 95, workbook_only=10)
        years[n] = hs.finish(y)
    total = hs.blank_year()
    for y in years.values():
        for c in total:
            total[c] += y[c]
    return {"years": years, "total": hs.finish(total), "by_month": [], "pairs": [],
            "events": {}, "samples": []}


class VerdictTests(unittest.TestCase):
    def test_verdict(self):
        res = synthetic()
        ok = {"C1": {"ok": True}}
        v = hs.verdict(res, ok)
        self.assertEqual(v, {"scored": True, "held": 5, "predictions": {
            "P1": True, "P2": True, "P3": True, "P4": True, "P5": True}})
        res["years"][2025]["hits"] = 95
        self.assertFalse(hs.verdict(res, ok)["predictions"]["P4"])
        res["years"][2019]["hits"] = 40
        p = hs.verdict(res, ok)["predictions"]
        self.assertFalse(p["P1"])
        self.assertFalse(p["P5"])
        self.assertFalse(hs.verdict(res, {"C1": {"ok": False}})["scored"])
        del res["years"][2016]
        self.assertFalse(hs.verdict(res, ok)["scored"])

    def test_render_scored(self):
        res = synthetic()
        checks = {"C1 workbooks": {"ok": True, "detail": "x"}}
        md = hs.render({"checks": checks, "verdict": hs.verdict(res, checks), "result": res})
        self.assertIn("Scored: 5 of 5 predictions held.", md)
        self.assertIn("| P1 hits in each year 2016-2025 | at least 50 | lowest 95 (2016) | True |", md)
        self.assertIn("| P2 coverage, all months | 0.90 | 0.9550 (955 of 1000) | True |", md)
        self.assertIn("| P4 hits per month, 2025 above 2017 | greater | 8.33 against 7.92 | True |", md)
        self.assertIn("| P5 coverage in each year 2016-2025 | 0.80 | lowest 0.9500 (2016) | True |", md)

    def test_checks(self):
        res = {"years": {2016: {"with_pudl": 96, "workbook": 100, "keys_share": 0.96},
                         2017: {"with_pudl": 90, "workbook": 100, "keys_share": 0.9}},
               "total": {"disagree": 150, "sim_stale": 99}}
        months = [{"month": "2016-01", "readable": True}, {"month": "2017-01", "readable": True}]
        c = hs.checks_for([{"ok": True}, {"ok": True}], months, res, M("2026-08"), [2016, 2017])
        self.assertEqual([x["ok"] for x in c.values()], [True, True, False, False])
        self.assertIn("2017 0.9", c["C3 keys"]["detail"])
        months[1]["readable"] = False
        c = hs.checks_for([{"ok": True}, {"ok": True}], months, None, M("2026-07"), [2016, 2017])
        self.assertEqual([x["ok"] for x in c.values()], [False, False])
        self.assertIn("not readable: 2017-01", c["C1 workbooks"]["detail"])

    def test_commit_of(self):
        body = json.dumps([{"sha": "abc", "commit": {"committer": {"date": "2026-10-22T05:00:00Z"}}}])
        self.assertEqual(hs.commit_of(fetch=lambda url: body),
                         {"sha": "abc", "date": "2026-10-22T05:00:00Z"})
        self.assertIn("error", hs.commit_of(fetch=lambda url: "[]"))


if __name__ == "__main__":
    unittest.main()
