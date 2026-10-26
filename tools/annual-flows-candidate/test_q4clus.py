"""Tests for q4clus.py. MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import hashlib
import os
import tempfile
import unittest
from unittest import mock

import clusterboot as cb
import nextcount as nc
import q4clus as q
import q4held as q4

HEAD = "month,key,technology,group,now,nameplate_mw,found\n"
COHORT = HEAD + (
    "2026-06,1/B,Solar Photovoltaic,solar,Planned,1.0,True\n"
    "2026-07,1/A,Solar Photovoltaic,solar,Planned,1.0,True\n"
    "2026-08,1/A,Solar Photovoltaic,solar,Planned,1.0,True\n"
    "2026-09,1/A,Solar Photovoltaic,solar,Operating,1.0,True\n"
    "2026-09,1/B,Solar Photovoltaic,solar,Planned,1.0,True\n"
    "2026-09,2/C,Batteries,batteries,Operating,1.0,True\n")
MONTH_HEAD = "key,status_before,nameplate_mw,now,status_now,planned_month_now,technology,group,listing\n"
MONTH = MONTH_HEAD + (
    "1/A,V,1.0,Operating,OP,,Solar Photovoltaic,solar,repeat\n"
    "1/B,V,1.0,Planned,V,2026-10,Solar Photovoltaic,solar,repeat\n"
    "2/C,U,1.0,Operating,OP,,Batteries,batteries,first\n")
MONTHS = "month,cohort,cohort_operating\n2026-08,1,0\n2026-09,3,2\n"
OK = {"held": True}


def cell_rows(month, group, gap, n, on, plants=None, tag="x"):
    """n rows of one cell, `on` of them on time, spread over `plants` plants (one row per plant if None)."""
    out = []
    for i in range(n):
        plant = i if plants is None else i % plants
        out.append({"month": month, "key": "%s%s%d/%d" % (tag, group[:2], plant, i), "group": group,
                    "now": "Operating" if i < on else "Planned", "prior": 0 if gap is None else 1, "gap": gap,
                    "listing": "first" if gap is None else "repeat"})
    return out


def synthetic(plants_one_month=None):
    rows = []
    rows += cell_rows("2026-10", "solar", None, 30, 9, tag="f")              # 0.3
    rows += cell_rows("2026-11", "solar", 1, 30, 15, plants_one_month, "o")  # 0.5
    rows += cell_rows("2026-12", "solar", 2, 30, 6, tag="t")                 # 0.2
    rows += cell_rows("2026-10", "batteries", None, 30, 9, tag="f")          # 0.3
    rows += cell_rows("2026-12", "batteries", 1, 30, 12, tag="o")            # 0.4
    return q.prepare(rows)


class HistoryTests(unittest.TestCase):
    def test_history_matches_published(self):
        self.assertEqual(["%+.4f" % q.history(p) for p in ("R1", "R2", "R3")], ["+0.0498", "+0.0824", "+0.1251"])

    def test_chance(self):
        e = q.expected()
        self.assertEqual((e["R1"][0], e["R1"][1]), (105, 123))
        self.assertEqual((e["R2"][0], e["R2"][1]), (33, 48))
        self.assertEqual((e["R3"][0], e["R3"][1]), (105, 72))
        for pid in ("R1", "R2", "R3"):
            self.assertTrue(0.5 < e[pid][2] < 1)
            # wider intervals, smaller chance
            self.assertLess(q.chance(pid, 105, 105, design=2.0), q.chance(pid, 105, 105, design=1.0))
        self.assertAlmostEqual(q.chance("R1", 10 ** 9, 10 ** 9), 1.0, places=6)


class PrepareTests(unittest.TestCase):
    def test_prepare(self):
        rows, _ = q4.build(nc.load(COHORT.encode("utf-8")), q4.month_rows("2026-09", MONTH.encode("utf-8")),
                           ("2026-09",))
        a = {r["key"]: (r["cell"], r["plant"], r["ok"]) for r in q.prepare(rows) if r["month"] == "2026-09"}
        self.assertEqual(a, {"1/A": ("1 month", "1", True), "1/B": ("2-3 months", "1", False),
                             "2/C": ("first", "2", True)})


class ScoreTests(unittest.TestCase):
    def test_direction_held(self):
        s = q.score(synthetic(), q4.SCORED, OK, OK, resamples=200)
        self.assertEqual([p["outcome"] for p in s["direction"]], ["held", "held", "held"])
        self.assertEqual(s["direction_held"], (3, 3))
        self.assertIn("1 month minus first: +0.2000", s["direction"][0]["value"])
        self.assertIn("1 month: 15 of 30 at 30 plants; first: 9 of 30 at 30 plants", s["direction"][0]["value"])
        self.assertIn("1 month minus 2-3 months: +0.3000", s["direction"][2]["value"])
        for k in s["consistency"]:
            self.assertIn(k["outcome"], ("held", "failed"))
        # each consistency outcome is whether the interval contains the earlier difference
        for k, (kid, pid, _) in zip(s["consistency"], q.CONSISTENCY):
            lo, hi = [float(x) for x in k["value"].split(" against ")[0].split(" to ")]
            self.assertEqual(k["outcome"] == "held", lo <= round(q.history(pid), 4) <= hi or
                             lo <= q.history(pid) <= hi)

    def test_direction_failed(self):
        a = synthetic()
        for r in a:
            if r["key"].startswith("oso"):
                r["ok"], r["now"] = False, "Planned"
        s = q.score(a, q4.SCORED, OK, OK, resamples=200)
        self.assertEqual([p["outcome"] for p in s["direction"]], ["failed", "held", "failed"])

    def test_not_scored(self):
        s = q.score(synthetic(), q4.SCORED, OK, OK, resamples=200, min_rows=31)
        self.assertEqual([p["outcome"] for p in s["direction"] + s["consistency"]], ["not scored"] * 6)
        self.assertEqual((s["direction_held"], s["consistency_held"]), ((0, 0), (0, 0)))
        s = q.score(synthetic(), q4.SCORED, {"held": False}, OK, resamples=200)
        self.assertEqual([p["outcome"] for p in s["direction"] + s["consistency"]], ["not scored"] * 6)

    def test_few_plants(self):
        # all 30 solar one-month rows at 3 plants: R1 and R3 are scored, K1 and K3 are not
        s = q.score(synthetic(plants_one_month=3), q4.SCORED, OK, OK, resamples=200)
        self.assertEqual([p["outcome"] for p in s["direction"]], ["held", "held", "held"])
        self.assertEqual(s["consistency"][0]["outcome"], "not scored")
        self.assertEqual(s["consistency"][2]["outcome"], "not scored")
        self.assertIn(s["consistency"][1]["outcome"], ("held", "failed"))

    def test_seeded(self):
        a = synthetic()
        x = cb.compare(a, ("2026-10", "2026-12"), "solar", "1 month", "first", 1, 200)
        y = cb.compare(a, ("2026-10", "2026-12"), "solar", "1 month", "first", 1, 200)
        self.assertEqual((x["lo"], x["hi"]), (y["lo"], y["hi"]))
        self.assertLess(x["lo"], 0.2)
        self.assertGreater(x["hi"], 0.2)

    def test_tables(self):
        t = q.tables(synthetic(), q4.SCORED, resamples=50)
        self.assertEqual(len(t), 4 * len(q.REPORT))
        pooled = [x for x in t if x["month"] == "pooled" and x["group"] == "solar" and x["label"] == "1 month minus first"]
        self.assertEqual(pooled[0]["cells"], [15, 30, 9, 30])
        october = [x for x in t if x["month"] == "2026-10" and x["group"] == "solar" and x["label"] == "1 month minus first"]
        self.assertEqual(october[0]["cells"], [0, 0, 9, 30])
        self.assertIsNone(october[0]["lo"])


class RunTests(unittest.TestCase):
    def files(self, d):
        paths = {}
        for name, text in (("cohort.csv", COHORT), ("month.csv", MONTH), ("months.csv", MONTHS)):
            paths[name] = os.path.join(d, name)
            with open(paths[name], "w", encoding="utf-8", newline="") as fh:
                fh.write(text)
        return paths

    def argv(self, p, d, scored="2026-09"):
        return ["--out-dir", os.path.join(d, "out"), "--cohort", p["cohort.csv"], "--month-file",
                "2026-09=" + p["month.csv"], "--months", p["months.csv"], "--scored", scored, "--resamples", "100"]

    def test_main_practice(self):
        with tempfile.TemporaryDirectory() as d:
            p = self.files(d)
            md5 = hashlib.md5(COHORT.encode("utf-8")).hexdigest()
            with mock.patch.object(q4, "COHORT_MD5", md5), mock.patch.object(nc, "COHORT_ROWS", 6):
                self.assertEqual(q.main(self.argv(p, d)), 0)
            md = open(os.path.join(d, "out", "q4clus.md"), encoding="utf-8").read()
            self.assertIn("| C1 | held | 2026-09: 2 of 3 against 2 of 3 |", md)
            self.assertIn("| C2 | held | 3 rows, 0 disagree |", md)
            self.assertIn("Direction bars held: 0 of 0 scored.", md)
            self.assertIn("Consistency bars held: 0 of 0 scored. 100 resamples, seed 20261025.", md)
            self.assertIn("| 2026-09 | True | 3 | 3 | 0 |", md)
            self.assertIn("| R1 | 105, 123 | +0.0498 |", md)
            self.assertIn("| 2026-09 | solar | 1 month minus first | +0.0000 | not computed |", md)

    def test_main_errors(self):
        with tempfile.TemporaryDirectory() as d:
            p = self.files(d)
            self.assertEqual(q.main(self.argv(p, d)), 2)   # md5 is not the published file's
            self.assertIn("not the one at commit ea63c15", open(os.path.join(d, "out", "q4clus.md"), encoding="utf-8").read())
            md5 = hashlib.md5(COHORT.encode("utf-8")).hexdigest()
            with mock.patch.object(q4, "COHORT_MD5", md5), mock.patch.object(nc, "COHORT_ROWS", 6):
                self.assertEqual(q.main(self.argv(p, d, scored="2026-09,2026-10")), 2)

    def test_require_plan(self):
        with tempfile.TemporaryDirectory() as d:
            p = self.files(d)
            self.assertEqual(q.main(self.argv(p, d) + ["--require-plan"], get=lambda url: b"404: Not Found"), 3)
            ok, why = q.plan_served(get=lambda url: b"x\nStatus: pre-registered, not yet scored.\n")
            self.assertTrue(ok)
            self.assertTrue(q.PLAN_URL.endswith("docs/q4clus-plan.md"))


if __name__ == "__main__":
    unittest.main()
