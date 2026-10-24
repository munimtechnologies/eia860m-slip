"""Tests for nexttechonce.py. MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import csv
import os
import tempfile
import unittest

import nexttechonce as nto

FIELDS = ["month", "key", "technology", "group", "now", "nameplate_mw", "found"]


def r(month, key, group, where):
    return {"month": month, "key": key, "technology": group, "group": group, "now": where,
            "nameplate_mw": "1.0", "found": "True"}


def gens(month, prefix, group, n_op, n):
    return [r(month, "%s/%d" % (prefix, i), group, "Operating" if i < n_op else "Planned") for i in range(n)]


def falling():
    """Early: solar 30/40, batteries 20/40, gas 20/40 plus one gas generator planned four months running.
    Late: solar 10/40, batteries 10/40, gas 21/40."""
    return (gens("2017-05", "1", "solar", 30, 40) + gens("2017-05", "2", "batteries", 20, 40)
            + gens("2017-05", "3", "gas", 20, 40) + [r("2017-0%d" % m, "9/G1", "gas", "Planned") for m in (6, 7, 8, 9)]
            + gens("2023-05", "4", "solar", 10, 40) + gens("2023-05", "5", "batteries", 10, 40)
            + gens("2023-05", "6", "gas", 21, 40))


FALLING_KNOWN = {nto.EARLY: (70, 124), nto.LATE: (41, 120)}


class FirstRowTests(unittest.TestCase):
    def test_first_rows(self):
        rows = [r("2016-02", "1/A", "gas", "Operating"), r("2016-01", "1/A", "gas", "Planned"),
                r("2016-03", "2/B", "solar", "Planned"), r("2022-01", "1/A", "gas", "Operating"),
                r("2021-06", "3/C", "solar", "Operating")]
        self.assertEqual({(x["key"], x["month"], x["now"]) for x in nto.first_rows(rows, nto.EARLY)},
                         {("1/A", "2016-01", "Planned"), ("2/B", "2016-03", "Planned")})
        self.assertEqual([(x["key"], x["month"]) for x in nto.first_rows(rows, nto.LATE)], [("1/A", "2022-01")])

    def test_frac_share(self):
        rows = [r("2016-01", "1/A", "gas", "Operating"), r("2016-01", "1/B", "gas", "absent"),
                r("2016-01", "2/A", "solar", "Operating")]
        self.assertEqual(nto.frac(rows), (2, 3))
        self.assertEqual(nto.frac(rows, "gas"), (1, 2))
        self.assertIsNone(nto.share((0, 0)))
        self.assertEqual(nto.share((1, 4)), 0.25)

    def test_standardized(self):
        early = [r("2016-01", "1/%d" % i, "solar", "Planned") for i in range(3)] + [r("2016-01", "2/A", "gas", "Planned")]
        late = [r("2022-01", "3/A", "solar", "Operating"), r("2022-01", "3/B", "solar", "Planned"),
                r("2022-01", "4/A", "gas", "Operating")]
        self.assertAlmostEqual(nto.standardized(early, late), 0.75 * 0.5 + 0.25 * 1.0)
        self.assertIsNone(nto.standardized(early + [r("2016-01", "5/A", "wind", "Planned")], late))

    def test_top_plant(self):
        rows = [r("2016-01", "5/A", "gas", "Planned"), r("2016-02", "5/B", "gas", "Planned"),
                r("2016-01", "6/A", "gas", "Operating"), r("2016-01", "7/A", "solar", "Operating")]
        self.assertEqual(nto.top_plant(rows, "gas"), ("5", 2))
        self.assertEqual(nto.top_plant(rows, "wind"), (None, 0))


class ScoreTests(unittest.TestCase):
    def test_score_holds(self):
        res = nto.score(falling(), known=FALLING_KNOWN, n_rows=244)
        self.assertEqual([p["id"] for p in res], ["C0", "O1", "O2", "O3", "O4"])
        self.assertEqual([p["outcome"] for p in res], ["held"] * 5)
        self.assertEqual(res[3]["value"], "0.4878 to 0.5250 (20 of 41 to 21 of 40)")
        self.assertIn("standardized 0.3432", res[4]["value"])

    def test_c0_fails(self):
        res = nto.score(falling())
        self.assertEqual(res[0]["outcome"], "failed")
        self.assertEqual({p["outcome"] for p in res[1:]}, {"not scored"})

    def test_failures(self):
        rows = (gens("2017-05", "1", "solar", 10, 40) + gens("2017-05", "2", "gas", 10, 40)
                + gens("2023-05", "3", "solar", 30, 40) + gens("2023-05", "4", "gas", 30, 40))
        res = {p["id"]: p for p in nto.score(rows, known={nto.EARLY: (20, 80), nto.LATE: (60, 80)}, n_rows=160)}
        self.assertEqual(res["C0"]["outcome"], "held")
        self.assertEqual(res["O1"]["outcome"], "failed")
        self.assertEqual(res["O2"]["outcome"], "not scored")
        self.assertTrue(res["O2"]["value"].startswith("too few; "))
        self.assertEqual(res["O3"]["outcome"], "failed")
        self.assertEqual(res["O4"]["outcome"], "failed")


class RunTests(unittest.TestCase):
    def test_wait_plan(self):
        replies = iter([b"404: Not Found", nto.PLAN_MARK.encode()])
        slept = []
        self.assertTrue(nto.wait_plan(10, get=lambda url: next(replies), sleep=slept.append, clock=lambda: 0))
        self.assertEqual(slept, [600])
        self.assertFalse(nto.wait_plan(10, get=lambda url: b"404: Not Found", sleep=slept.append, clock=lambda: 99))
        self.assertEqual(slept, [600])

    def test_main_local(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "cohort.csv")
            with open(path, "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, FIELDS)
                w.writeheader()
                w.writerows(falling())
            out = os.path.join(tmp, "out")
            self.assertEqual(nto.main(["--cohort", path, "--out-dir", out]), 0)
            with open(os.path.join(out, "nexttechonce.md"), encoding="utf-8") as fh:
                md = fh.read()
            self.assertIn("| C0 | failed | 244 rows;", md)
            self.assertIn("Held: 0 of 0 scored", md)
            self.assertIn("| 2016-01 to 2019-12 | gas | 41 | 20 | 0.4878 | 44 | 20 | 0.4545 |", md)
            self.assertIn("| 2016-01 to 2019-12 | gas | 3 | 40 | 0.0000 |", md)
            with open(os.path.join(out, "nexttechonce_first.csv"), newline="", encoding="utf-8") as fh:
                first = list(csv.DictReader(fh))
            self.assertEqual(len(first), 241)

    def test_main_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "out")
            self.assertEqual(nto.main(["--cohort", os.path.join(tmp, "missing.csv"), "--out-dir", out]), 2)
            with open(os.path.join(out, "nexttechonce.md"), encoding="utf-8") as fh:
                self.assertIn("Not run: cohort file not read: FileNotFoundError", fh.read())


if __name__ == "__main__":
    unittest.main()
