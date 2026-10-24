"""Tests for q4held.py. MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import hashlib
import os
import tempfile
import unittest
from unittest import mock

import nextcount as nc
import q4held as q

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
MONTHS = ("month,cohort,cohort_operating\n2026-08,1,0\n2026-09,3,2\n")


def rows_of(text):
    return nc.load(text.encode("utf-8"))


class BuildTests(unittest.TestCase):
    def test_month_rows(self):
        r = q.month_rows("2026-09", MONTH.encode("utf-8"))
        self.assertEqual([(x["month"], x["key"], x["now"], x["group"], x["listing"]) for x in r][2],
                         ("2026-09", "2/C", "Operating", "batteries", "first"))

    def test_annotate_and_identity(self):
        rows, ident = q.build(rows_of(COHORT), q.month_rows("2026-09", MONTH.encode("utf-8")), ("2026-09",))
        sep = {r["key"]: (r["prior"], r["gap"]) for r in rows if r["month"] == "2026-09"}
        self.assertEqual(sep, {"1/A": (2, 1), "1/B": (1, 3), "2/C": (0, None)})
        self.assertEqual(ident["2026-09"], {"rows_equal": True, "cohort_rows": 3, "appended_rows": 3, "group_differs": 0})
        self.assertEqual(len(rows), 6)
        other = MONTH.replace("1/B,V,1.0,Planned", "1/B,V,1.0,Operating")
        _, ident = q.build(rows_of(COHORT), q.month_rows("2026-09", other.encode("utf-8")), ("2026-09",))
        self.assertFalse(ident["2026-09"]["rows_equal"])

    def test_no_identity_for_new_months(self):
        new = q.month_rows("2026-10", MONTH.encode("utf-8"))
        rows, ident = q.build(rows_of(COHORT), new, ("2026-10",))
        self.assertEqual(ident, {})
        self.assertEqual({r["key"]: (r["prior"], r["gap"]) for r in rows if r["month"] == "2026-10"},
                         {"1/A": (3, 1), "1/B": (2, 1), "2/C": (1, 1)})

    def test_checks(self):
        rows, _ = q.build(rows_of(COHORT), q.month_rows("2026-09", MONTH.encode("utf-8")), ("2026-09",))
        c1, c2 = q.checks(rows, ("2026-09",), q.known_months(MONTHS.encode("utf-8")))
        self.assertTrue(c1["held"])
        self.assertTrue(c2["held"])
        c1, _ = q.checks(rows, ("2026-09",), {"2026-09": (1, 3)})
        self.assertFalse(c1["held"])
        c1, _ = q.checks(rows, ("2026-09",), {})
        self.assertFalse(c1["held"])
        wrong = MONTH.replace("Batteries,batteries,first", "Batteries,batteries,repeat")
        rows, _ = q.build(rows_of(COHORT), q.month_rows("2026-09", wrong.encode("utf-8")), ("2026-09",))
        _, c2 = q.checks(rows, ("2026-09",), {})
        self.assertFalse(c2["held"])
        self.assertEqual(c2["disagree"], 1)


class ScoreTests(unittest.TestCase):
    def rows(self):
        out = []
        for i in range(10):   # first listings: 3 of 10 on time
            out.append({"month": "2026-10", "key": "f%d" % i, "now": "Operating" if i < 3 else "Planned",
                        "group": "solar", "prior": 0, "gap": None, "listing": "first"})
        for i in range(10):   # 1 month after: 5 of 10
            out.append({"month": "2026-11", "key": "o%d" % i, "now": "Operating" if i < 5 else "Planned",
                        "group": "solar", "prior": 1, "gap": 1, "listing": "repeat"})
        for i in range(10):   # 2-3 months after and 5 or more earlier: 1 of 10
            out.append({"month": "2026-12", "key": "t%d" % i, "now": "Operating" if i < 1 else "Planned",
                        "group": "batteries", "prior": 6, "gap": 2, "listing": "repeat"})
        return out

    def known(self):
        return {"2026-10": (3, 10), "2026-11": (5, 10), "2026-12": (1, 10)}

    def test_holds(self):
        s = q.score(self.rows(), q.SCORED, self.known(), min_cell=10)
        self.assertEqual([p["outcome"] for p in s["predictions"]], ["held", "held", "held"])
        self.assertEqual((s["held"], s["scored"]), (3, 3))
        self.assertEqual(s["cells"]["5 or more earlier"], (1, 10))

    def test_fails(self):
        rows = self.rows()
        for r in rows:
            if r["key"].startswith("o"):
                r["now"] = "Planned"
        known = dict(self.known(), **{"2026-11": (0, 10)})
        s = q.score(rows, q.SCORED, known, min_cell=10)
        self.assertEqual([p["outcome"] for p in s["predictions"]], ["failed", "failed", "held"])

    def test_not_scored(self):
        s = q.score(self.rows(), q.SCORED, self.known(), min_cell=11)
        self.assertEqual(s["scored"], 0)
        s = q.score(self.rows(), q.SCORED, dict(self.known(), **{"2026-12": (2, 10)}), min_cell=10)
        self.assertFalse(s["c1"]["held"])
        self.assertEqual([p["outcome"] for p in s["predictions"]], ["not scored"] * 3)

    def test_tables(self):
        t = q.tables(self.rows(), q.SCORED)
        pooled = {x["cell"]: (x["on_time"], x["rows"]) for x in t["months"] if x["month"] == "pooled"}
        self.assertEqual(pooled["first"], (3, 10))
        self.assertEqual(pooled["2-3 months"], (1, 10))
        self.assertEqual(len(t["tech"]), len(nc.GROUPS) * len(q.TECH_CELLS))


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
                "2026-09=" + p["month.csv"], "--months", p["months.csv"], "--scored", scored]

    def test_main_practice(self):
        with tempfile.TemporaryDirectory() as d:
            p = self.files(d)
            md5 = hashlib.md5(COHORT.encode("utf-8")).hexdigest()
            with mock.patch.object(q, "COHORT_MD5", md5), mock.patch.object(nc, "COHORT_ROWS", 6):
                self.assertEqual(q.main(self.argv(p, d)), 0)
            md = open(os.path.join(d, "out", "q4held.md"), encoding="utf-8").read()
            self.assertIn("| C1 | held | 2026-09: 2 of 3 against 2 of 3 |", md)
            self.assertIn("| C2 | held | 3 rows, 0 disagree |", md)
            self.assertIn("Held: 0 of 0 scored", md)
            self.assertIn("| 2026-09 | True | 3 | 3 | 0 |", md)
            rows = open(os.path.join(d, "out", "q4held_rows.csv"), encoding="utf-8").read().splitlines()
            self.assertEqual(rows[0], "month,key,group,now,listing,prior,gap")
            self.assertEqual(len(rows), 4)

    def test_main_errors(self):
        with tempfile.TemporaryDirectory() as d:
            p = self.files(d)
            self.assertEqual(q.main(self.argv(p, d)), 2)   # md5 is not the published file's
            self.assertIn("not the one at commit ea63c15", open(os.path.join(d, "out", "q4held.md"), encoding="utf-8").read())
            md5 = hashlib.md5(COHORT.encode("utf-8")).hexdigest()
            with mock.patch.object(q, "COHORT_MD5", md5), mock.patch.object(nc, "COHORT_ROWS", 6):
                self.assertEqual(q.main(self.argv(p, d, scored="2026-09,2026-10")), 2)

    def test_require_plan(self):
        with tempfile.TemporaryDirectory() as d:
            p = self.files(d)
            self.assertEqual(q.main(self.argv(p, d) + ["--require-plan"], get=lambda url: b"404: Not Found"), 3)
            ok, why = q.plan_served(get=lambda url: b"x\nStatus: pre-registered, not yet scored.\n")
            self.assertTrue(ok)


if __name__ == "__main__":
    unittest.main()
