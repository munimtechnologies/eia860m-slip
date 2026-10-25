"""Tests for clusterboot.py. MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import csv
import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

import clusterboot as cb

FIELDS = ("month", "key", "technology", "group", "now", "nameplate_mw", "found")


def gen(group, plant, months, nows):
    return [{"month": m, "key": "%s/G1" % plant, "technology": "x", "group": group, "now": s, "nameplate_mw": "0.0",
             "found": "True"} for m, s in zip(months, nows)]


def fixture(n_solar=30, solar_nows=("Planned", "Operating"), wind_mixed=False):
    """Solar plants listed in 2016-01 and again in 2016-02; wind plants in 2017-01 and 2017-02."""
    rows = []
    for i in range(n_solar):
        rows += gen("solar", 1000 + i, ("2016-01", "2016-02"), solar_nows)
    for i in range(30):
        nows = ("Planned", "Operating") if wind_mixed and i % 2 else ("Operating", "Planned")
        rows += gen("wind", 2000 + i, ("2017-01", "2017-02"), nows)
    return rows


def known_of(rows):
    a = cb.annotate(rows)
    return {k: cb.count(cb.pick(a, k[0], k[1], k[2])) for k in cb.KNOWN}


class HelperTests(unittest.TestCase):
    def test_constants(self):
        self.assertTrue(cb.PLAN_URL.endswith("/main/docs/clusterboot-plan.md"))
        self.assertIn("ea63c150a8ed41cc1fcad901ccab51686c924d46/data/nexttech_cohort.csv", cb.COHORT_URL)
        self.assertEqual((cb.COHORT_ROWS, cb.MIN_PLANTS, cb.RESAMPLES, cb.SEED), (14807, 30, 2000, 20261025))
        self.assertEqual([b[0] for b in cb.BARS], ["B1", "B2", "B3", "B4", "B5"])
        self.assertEqual([b[6] for b in cb.BARS], ["above", "above", "spans", "spans", "above"])
        self.assertEqual(cb.CELLS, ("first", "1 month", "2-3 months", "4-12 months", "more than 12 months"))
        self.assertEqual(len(cb.KNOWN), 10)

    def test_ends(self):
        self.assertEqual(cb.ends(list(range(2000))), (50, 1949))
        self.assertEqual(cb.ends(list(range(200))), (5, 194))

    def test_clusters_and_diff(self):
        a = cb.annotate(list(reversed(gen("solar", 7, ("2016-01", "2016-02"), ("Planned", "Operating")))))
        self.assertEqual([(r["cell"], r["ok"], r["plant"]) for r in a], [("first", False, "7"), ("1 month", True, "7")])
        by = cb.clusters(a, cb.POOL, "solar", "1 month", "first")
        self.assertEqual(by, {"7": [1, 1, 0, 1]})
        self.assertEqual((cb.diff([1, 1, 0, 1], 1), cb.diff([1, 1, 0, 1], -1), cb.diff([0, 0, 1, 1], 1)),
                         (1.0, -1.0, 0.0))
        self.assertEqual(cb.label("1 month", "first", -1), "first minus 1 month")

    def test_boot(self):
        by = {"1": [1, 1, 0, 1], "2": [0, 1, 1, 1]}
        d = cb.boot(by, 1, resamples=50)
        self.assertEqual(d, cb.boot(by, 1, resamples=50))
        self.assertEqual(len(d), 50)
        self.assertEqual(d, sorted(d))
        self.assertTrue(set(d) <= {-1.0, 0.0, 1.0})


class ScoreTests(unittest.TestCase):
    def score(self, rows, md5="m"):
        return {p["id"]: p["outcome"] for p in cb.score(cb.annotate(rows), len(rows), md5, known=known_of(rows),
                                                        rows_expected=len(rows), md5_expected="m", resamples=200)}

    def test_score(self):
        self.assertEqual(self.score(fixture()), {"C0": "held", "B1": "held", "B2": "not scored", "B3": "failed",
                                                 "B4": "not scored", "B5": "not scored"})

    def test_spans(self):
        self.assertEqual(self.score(fixture(wind_mixed=True))["B3"], "held")

    def test_above_fails(self):
        self.assertEqual(self.score(fixture(solar_nows=("Operating", "Planned")))["B1"], "failed")

    def test_c0_fails(self):
        got = self.score(fixture(), md5="other")
        self.assertEqual(got["C0"], "failed")
        self.assertTrue(all(v == "not scored" for k, v in got.items() if k != "C0"))

    def test_too_few_plants(self):
        self.assertEqual(self.score(fixture(n_solar=29))["B1"], "not scored")


class RunTests(unittest.TestCase):
    def test_wait_plan(self):
        answers = iter([b"404: Not Found", b"# Plan\n\nStatus: pre-registered, not yet scored.\n"])
        log = io.StringIO()
        with redirect_stdout(log):
            self.assertTrue(cb.wait_plan(10 ** 12, get=lambda url: next(answers), sleep=lambda s: None))
            self.assertFalse(cb.wait_plan(0, get=lambda url: b"404", sleep=lambda s: None, clock=lambda: 1))
        lines = log.getvalue().splitlines()
        self.assertTrue(lines[0].endswith("plan not served yet: 404: Not Found"))
        self.assertTrue(lines[1].endswith("plan served: " + cb.PLAN_URL))
        self.assertTrue(lines[2].endswith("deadline passed; plan not served"))

    def test_main_local(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "cohort.csv")
            with open(path, "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=FIELDS)
                w.writeheader()
                w.writerows(fixture())
            with redirect_stdout(io.StringIO()):
                self.assertEqual(cb.main(["--cohort", path, "--out-dir", os.path.join(d, "out"), "--resamples", "200"]),
                                 0)
            with open(os.path.join(d, "out", "clusterboot.md"), encoding="utf-8") as fh:
                md = fh.read()
        self.assertIn("| C0 | failed |", md)
        self.assertIn("| B1 | not scored | not computed |", md)
        self.assertIn("200 resamples, seed 20261025.", md)
        self.assertIn("| 2016-01 to 2025-12 | solar | 1 month minus first | +1.0000 | +1.0000 to +1.0000 | 30, 30 |", md)
        self.assertIn("| 2016-01 to 2025-12 | wind | first minus 1 month | +1.0000 | +1.0000 to +1.0000 | 30, 30 |", md)
        self.assertIn("| 2022-01 to 2026-08 | solar | 1 month minus 2-3 months | +0.0000 | not computed | 0, 0 "
                      "(under 30 plants) |", md)
        self.assertIn("Held: 0 of 0 scored", md)

    def test_main_error(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(cb.main(["--cohort", os.path.join(d, "missing.csv"), "--out-dir", d]), 2)
            with open(os.path.join(d, "clusterboot.md"), encoding="utf-8") as fh:
                self.assertIn("Not run: cohort file not read", fh.read())


if __name__ == "__main__":
    unittest.main()
