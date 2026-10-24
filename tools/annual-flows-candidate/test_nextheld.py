"""Tests for nextheld.py. MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import csv
import json
import os
import tempfile
import unittest

import nextcount as nc
import nextheld as nh

FIELDS = ["month", "key", "technology", "group", "now", "nameplate_mw", "found"]


def r(month, key, where, group="solar"):
    return {"month": month, "key": key, "technology": group, "group": group, "now": where,
            "nameplate_mw": "1.0", "found": "True"}


def gens(prefix, months, ops):
    """40 generators prefix/0 to prefix/39 planned for the next month in each of months: at the last
    one the first ops are listed as operating; before it none are."""
    rows = []
    for j, month in enumerate(months):
        last = j == len(months) - 1
        rows += [r(month, "%s/%d" % (prefix, i), "Operating" if last and i < ops else "Planned") for i in range(40)]
    return rows


def fixture(b_ops=2, c_ops=20):
    """January to August 2026: 0 earlier listings 12 of 120; 1: c_ops + 4 of 80; 3+: b_ops of 40.
    Repeat listings 1 month after the last: b_ops + c_ops of 80; 2-3 months after: 4 of 40."""
    return (gens("1", ["2026-03"], 12) + gens("2", ["2025-10", "2025-11", "2025-12", "2026-01"], b_ops)
            + gens("3", ["2026-02", "2026-03"], c_ops) + gens("4", ["2026-02", "2026-05"], 4))


FIX_MONTHS = {"2026-01": (2, 40), "2026-02": (0, 80), "2026-03": (32, 80), "2026-05": (4, 40)}


class HelperTests(unittest.TestCase):
    def test_fixture(self):
        rows = fixture()
        self.assertEqual(len(rows), 360)
        self.assertEqual(nh.months_of(rows), FIX_MONTHS)
        self.assertEqual(nh.months_of([r("2025-12", "9/A", "Operating"), r("2026-09", "9/A", "Operating")]), {})

    def test_cells(self):
        a = nc.annotate(fixture())
        self.assertEqual(nh.gap_cell(a, "1 month"), (22, 80))
        self.assertEqual(nh.gap_cell(a, "2-3 months"), (4, 40))
        self.assertEqual(nh.gap_cell(a, "4-12 months"), (0, 0))
        self.assertEqual(nc.by_bin(a, nh.HELD), {"0": (12, 120), "1": (24, 80), "2": (0, 0), "3+": (2, 40)})

    def test_known_months(self):
        self.assertEqual(sorted(nh.KNOWN_MONTHS), ["2026-0%d" % i for i in range(1, 9)])
        self.assertEqual(nh._total(nh.KNOWN_MONTHS), (366, 1194, 8))
        self.assertEqual(nh.PLAN_URL, nc.BASE + "docs/nextheld-plan.md")


class ScoreTests(unittest.TestCase):
    def test_score_holds(self):
        res = nh.score(fixture(), known=FIX_MONTHS)
        self.assertEqual([p["id"] for p in res], ["C1", "H1", "H2", "H3"])
        self.assertEqual([p["outcome"] for p in res], ["held"] * 4)
        self.assertEqual(res[0]["value"], "38 of 240 generator-months in 4 months")
        self.assertEqual(res[1]["value"], "0: 12 of 120; 3+: 2 of 40")
        self.assertEqual(res[2]["value"], "1 month: 22 of 80; 2-3 months: 4 of 40")
        self.assertEqual(res[3]["value"], "1 month: 22 of 80; 0: 12 of 120")

    def test_failures(self):
        known = dict(FIX_MONTHS)
        known["2026-01"] = (10, 40)
        self.assertEqual([p["outcome"] for p in nh.score(fixture(b_ops=10), known=known)],
                         ["held", "failed", "held", "held"])
        known = dict(FIX_MONTHS)
        known["2026-01"], known["2026-03"] = (0, 40), (12, 80)
        self.assertEqual([p["outcome"] for p in nh.score(fixture(b_ops=0, c_ops=0), known=known)],
                         ["held", "held", "failed", "failed"])

    def test_c1_fails(self):
        res = nh.score(fixture())
        self.assertEqual(res[0]["outcome"], "failed")
        self.assertEqual(res[0]["bar"], "each month's rows and operating rows as in "
                                        "data/monthcheck_months_2026-09.csv: 366 of 1194 in 8 months")
        self.assertEqual({p["outcome"] for p in res[1:]}, {"not scored"})

    def test_too_few(self):
        rows = gens("1", ["2026-03"], 12) + gens("3", ["2026-02", "2026-03"], 20)
        res = nh.score(rows, known={"2026-02": (0, 40), "2026-03": (32, 80)})
        self.assertEqual([p["outcome"] for p in res], ["held", "not scored", "not scored", "held"])


class TableTests(unittest.TestCase):
    def test_tables(self):
        t = nh.tables(nc.annotate(fixture()))
        held = "2026-01 to 2026-08"
        self.assertEqual({x["period"] for x in t["bins"] + t["fine"] + t["gaps"] + t["tech"]}, {held})
        row = [x for x in t["bins"] if x["cell"] == "3+"][0]
        self.assertEqual((row["months"], row["operating"], row["generators"], row["plants"]), (40, 2, 40, 1))
        row = [x for x in t["bins"] if x["cell"] == "0"][0]
        self.assertEqual((row["months"], row["operating"], row["generators"], row["plants"]), (120, 12, 120, 3))
        gap = [x for x in t["gaps"] if x["cell"] == "1 month"][0]
        self.assertEqual((gap["months"], gap["operating"], gap["generators"], gap["plants"]), (80, 22, 80, 2))
        self.assertEqual(sum(x["months"] for x in t["fine"]), 240)
        self.assertEqual(sum(x["months"] for x in t["tech"] if x["group"] == "solar"), 240)
        self.assertEqual(sum(x["months"] for x in t["gaps"]), 120)


class RunTests(unittest.TestCase):
    def test_wait_plan(self):
        urls = []

        def served(url):
            urls.append(url)
            return nh.PLAN_MARK.encode() if len(urls) > 1 else b"404: Not Found"

        slept = []
        self.assertTrue(nh.wait_plan(10, get=served, sleep=slept.append, clock=lambda: 0))
        self.assertEqual(slept, [600])
        self.assertEqual(urls, [nc.BASE + "docs/nextheld-plan.md"] * 2)
        self.assertFalse(nh.wait_plan(10, get=lambda url: b"404: Not Found", sleep=slept.append, clock=lambda: 99))
        self.assertEqual(slept, [600])

    def test_main_local(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "cohort.csv")
            with open(path, "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, FIELDS)
                w.writeheader()
                w.writerows(fixture())
            out = os.path.join(tmp, "out")
            self.assertEqual(nh.main(["--cohort", path, "--out-dir", out]), 0)
            with open(os.path.join(out, "nextheld.md"), encoding="utf-8") as fh:
                md = fh.read()
            self.assertIn("| C1 | failed | 38 of 240 generator-months in 4 months |", md)
            self.assertIn("Held: 0 of 0 scored", md)
            self.assertIn("| 2026-03 | 32 | 80 |", md)
            self.assertIn("| 2026-01 to 2026-08 | 3+ | 40 | 2 | 0.0500 | 40 | 1 |", md)
            self.assertIn("| 2026-01 to 2026-08 | 1 month | 80 | 22 | 0.2750 | 80 | 2 |", md)
            self.assertIn("| 2026-01 to 2026-08 | solar | 0 | 120 | 12 | 0.1000 | 120 | 3 |", md)
            with open(os.path.join(out, "nextheld.json"), encoding="utf-8") as fh:
                res = json.load(fh)
            self.assertEqual(res["rows"], 360)
            self.assertEqual(res["months"]["2026-05"], [4, 40])

    def test_main_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "out")
            self.assertEqual(nh.main(["--cohort", os.path.join(tmp, "missing.csv"), "--out-dir", out]), 2)
            with open(os.path.join(out, "nextheld.md"), encoding="utf-8") as fh:
                self.assertIn("Not run: cohort file not read: FileNotFoundError", fh.read())


if __name__ == "__main__":
    unittest.main()
