"""Tests for plantw.py. MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import csv
import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

import plantw as pw

FIELDS = ("month", "key", "technology", "group", "now", "nameplate_mw", "found")


def gen(group, plant, months, nows):
    return [{"month": m, "key": "%s/G1" % plant, "technology": "x", "group": group, "now": s, "nameplate_mw": "0.0",
             "found": "True"} for m, s in zip(months, nows)]


def fixture(n_solar=30, solar_nows=("Planned", "Operating")):
    """Solar plants listed in 2016-01 and again in 2016-02; wind plants in 2017-01 and 2017-02."""
    rows = []
    for i in range(n_solar):
        rows += gen("solar", 1000 + i, ("2016-01", "2016-02"), solar_nows)
    for i in range(30):
        rows += gen("wind", 2000 + i, ("2017-01", "2017-02"), ("Operating", "Planned"))
    return rows


def known_of(rows):
    a = pw.annotate(rows)
    out = {}
    for k in pw.KNOWN:
        c = pw.cell(pw.pick(a, pw.POOL, k[0], k[1]))
        out[k] = (c["on"], c["rows"])
    return out


class HelperTests(unittest.TestCase):
    def test_constants(self):
        self.assertTrue(pw.PLAN_URL.endswith("/main/docs/plantw-plan.md"))
        self.assertIn("ea63c150a8ed41cc1fcad901ccab51686c924d46/data/nexttech_cohort.csv", pw.COHORT_URL)
        self.assertEqual((pw.COHORT_ROWS, pw.MIN_PLANTS), (14807, 30))
        self.assertEqual([b[0] for b in pw.BARS], ["P1", "P2", "P3", "P4", "P5"])
        self.assertEqual(pw.CELLS, ("first", "1 month", "2-3 months", "4-12 months", "more than 12 months"))

    def test_cells_of_gaps(self):
        rows = gen("solar", 7, ("2016-01", "2016-02", "2016-05", "2017-06", "2017-10"),
                   ("Planned", "Planned", "Planned", "Planned", "Operating"))
        a = pw.annotate(list(reversed(rows)))
        self.assertEqual([r["cell"] for r in a], ["first", "1 month", "2-3 months", "more than 12 months",
                                                  "4-12 months"])
        self.assertEqual([r["ok"] for r in a], [False, False, False, False, True])
        self.assertEqual(a[0]["plant"], "7")

    def test_plant_weighting(self):
        rows = [{"plant": "1", "ok": True}, {"plant": "1", "ok": True}, {"plant": "1", "ok": True},
                {"plant": "2", "ok": False}]
        c = pw.cell(rows)
        self.assertEqual((c["on"], c["rows"], c["plants"], c["pw"]), (3, 4, 2, 0.5))
        self.assertEqual(pw.cell([])["pw"], None)
        self.assertEqual(pw.fmt(pw.cell([])), "no rows")
        self.assertEqual(pw.fmt(c), "0.5000 over 2 plants (generator-months 3 of 4)")


class ScoreTests(unittest.TestCase):
    def score(self, rows, md5="m"):
        return {p["id"]: p["outcome"] for p in pw.score(pw.annotate(rows), len(rows), md5, known=known_of(rows),
                                                        rows_expected=len(rows), md5_expected="m")}

    def test_score_holds(self):
        got = self.score(fixture())
        self.assertEqual(got, {"C0": "held", "P1": "held", "P2": "not scored", "P3": "held", "P4": "not scored",
                               "P5": "not scored"})

    def test_failures(self):
        got = self.score(fixture(solar_nows=("Operating", "Planned")))
        self.assertEqual((got["P1"], got["P3"]), ("failed", "held"))

    def test_c0_fails(self):
        got = self.score(fixture(), md5="other")
        self.assertEqual(got["C0"], "failed")
        self.assertTrue(all(v == "not scored" for k, v in got.items() if k != "C0"))

    def test_too_few_plants(self):
        self.assertEqual(self.score(fixture(n_solar=29))["P1"], "not scored")

    def test_ties_fail(self):
        rows = fixture(solar_nows=("Planned", "Planned"))
        self.assertEqual(self.score(rows)["P1"], "failed")


class RunTests(unittest.TestCase):
    def test_wait_plan(self):
        answers = iter([b"404: Not Found", b"# Plan\n\nStatus: pre-registered, not yet scored.\n"])
        log = io.StringIO()
        with redirect_stdout(log):
            self.assertTrue(pw.wait_plan(10 ** 12, get=lambda url: next(answers), sleep=lambda s: None))
            self.assertFalse(pw.wait_plan(0, get=lambda url: b"404", sleep=lambda s: None, clock=lambda: 1))
        lines = log.getvalue().splitlines()
        self.assertTrue(lines[0].endswith("plan not served yet: 404: Not Found"))
        self.assertTrue(lines[1].endswith("plan served: " + pw.PLAN_URL))
        self.assertTrue(lines[2].endswith("deadline passed; plan not served"))

    def test_main_local(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "cohort.csv")
            with open(path, "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=FIELDS)
                w.writeheader()
                w.writerows(fixture())
            with redirect_stdout(io.StringIO()):
                self.assertEqual(pw.main(["--cohort", path, "--out-dir", os.path.join(d, "out")]), 0)
            with open(os.path.join(d, "out", "plantw.md"), encoding="utf-8") as fh:
                md = fh.read()
        self.assertIn("| C0 | failed |", md)
        self.assertIn("| P1 | not scored | 1 month: 1.0000 over 30 plants (generator-months 30 of 30); first: "
                      "0.0000 over 30 plants (generator-months 0 of 30) |", md)
        self.assertIn("| 2016-01 to 2019-12 | solar | 1 month | 30 | 30 | 1.0000 | 30 | 1.0000 |", md)
        self.assertIn("| 2016-01 to 2025-12 | wind | first | 30 | 30 | 1.0000 | 30 | 1.0000 |", md)
        self.assertIn("Held: 0 of 0 scored", md)

    def test_main_error(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(pw.main(["--cohort", os.path.join(d, "missing.csv"), "--out-dir", d]), 2)
            with open(os.path.join(d, "plantw.md"), encoding="utf-8") as fh:
                self.assertIn("Not run: cohort file not read", fh.read())


if __name__ == "__main__":
    unittest.main()
