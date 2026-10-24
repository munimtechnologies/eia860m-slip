"""Tests for gaptech.py. MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import csv
import json
import os
import tempfile
import unittest

import gaptech as gt
import nextcount as nc

FIELDS = ["month", "key", "technology", "group", "now", "nameplate_mw", "found"]


def r(month, key, where, group):
    return {"month": month, "key": key, "technology": group, "group": group, "now": where,
            "nameplate_mw": "1.0", "found": "True"}


def gens(prefix, months, ops, group="solar"):
    """40 generators prefix/0 to prefix/39 planned for the next month in each of months: at the last
    one the first ops are listed as operating; before it none are."""
    rows = []
    for j, month in enumerate(months):
        last = j == len(months) - 1
        rows += [r(month, "%s/%d" % (prefix, i), "Operating" if last and i < ops else "Planned", group)
                 for i in range(40)]
    return rows


def fixture(s_ops=20, gap=True):
    """2022-2025 solar: first 12 of 120 (80 without gap), 1 month s_ops of 40, 2-3 months 4 of 40 (none
    without gap); 2022-2025 batteries: first 0 of 40, 1 month 30 of 40; 2026 solar: first 0 of 80,
    1 month 10 of 40, 2-3 months 2 of 40."""
    rows = (gens("1", ["2024-03"], 12) + gens("2", ["2024-01", "2024-02"], s_ops)
            + gens("4", ["2025-05", "2025-06"], 30, "batteries")
            + gens("5", ["2026-02", "2026-03"], 10) + gens("6", ["2026-02", "2026-05"], 2))
    return rows + (gens("3", ["2024-01", "2024-04"], 4) if gap else [])


def known(s_ops=20, gap=True):
    late = (42 + s_ops + (4 if gap else 0), 280 if gap else 200)
    return {nc.EARLY: (0, 0), nc.LATE: late, gt.HELD: (12, 160)}


def first(gap=True):
    return {"solar": (12, 120 if gap else 80), "batteries": (0, 40)}


class HelperTests(unittest.TestCase):
    def test_fixture(self):
        self.assertEqual(len(fixture()), 440)
        self.assertEqual(len(fixture(gap=False)), 360)

    def test_cells(self):
        a = nc.annotate(fixture())
        self.assertEqual(gt.cells(a, "solar", nc.LATE), {"first": (12, 120), "1 month": (20, 40), "2-3 months": (4, 40),
                                                         "4-12 months": (0, 0), "more than 12 months": (0, 0)})
        self.assertEqual(gt.cells(a, "batteries", nc.LATE)["first"], (0, 40))
        self.assertEqual(gt.cells(a, "batteries", nc.LATE)["1 month"], (30, 40))
        self.assertEqual(gt.cells(a, "solar", gt.HELD), {"first": (0, 80), "1 month": (10, 40), "2-3 months": (2, 40),
                                                         "4-12 months": (0, 0), "more than 12 months": (0, 0)})
        self.assertEqual(gt.cells(a, "gas", nc.LATE)["first"], (0, 0))

    def test_constants(self):
        self.assertEqual(gt.CELLS, ("first", "1 month", "2-3 months", "4-12 months", "more than 12 months"))
        self.assertEqual(gt.PLAN_URL, nc.BASE + "docs/nextgaptech-plan.md")
        self.assertEqual(gt.KNOWN[gt.HELD], (366, 1194))
        self.assertEqual(gt.KNOWN[nc.LATE], nc.KNOWN[nc.LATE])


class ScoreTests(unittest.TestCase):
    def test_score_holds(self):
        res = gt.score(fixture(), known=known(), first=first(), n_rows=440)
        self.assertEqual([p["id"] for p in res], ["C0", "G1", "G2", "G3", "G4"])
        self.assertEqual([p["outcome"] for p in res], ["held"] * 5)
        self.assertEqual(res[0]["value"], "440 rows; 0 of 0, 66 of 280, 12 of 160; first listings 2022-2025: "
                                          "solar 12 of 120, batteries 0 of 40")
        self.assertEqual(res[1]["value"], "1 month: 20 of 40; first: 12 of 120")
        self.assertEqual(res[2]["value"], "1 month: 20 of 40; 2-3 months: 4 of 40")
        self.assertEqual(res[3]["value"], "1 month: 10 of 40; 2-3 months: 2 of 40")
        self.assertEqual(res[4]["value"], "1 month: 30 of 40; first: 0 of 40")

    def test_failures(self):
        res = gt.score(fixture(s_ops=4), known=known(s_ops=4), first=first(), n_rows=440)
        self.assertEqual([p["outcome"] for p in res], ["held", "failed", "failed", "held", "held"])

    def test_c0_fails(self):
        res = gt.score(fixture())
        self.assertEqual(res[0]["outcome"], "failed")
        self.assertEqual(res[0]["bar"], "14807 rows; 1980 of 4223, 2110 of 6047, 366 of 1194; first listings "
                                        "2022-2025: solar 536 of 1483, batteries 143 of 514")
        self.assertEqual({p["outcome"] for p in res[1:]}, {"not scored"})
        res = gt.score(fixture(), known=known(), first={"solar": (12, 120), "batteries": (1, 40)}, n_rows=440)
        self.assertEqual(res[0]["outcome"], "failed")

    def test_too_few(self):
        res = gt.score(fixture(gap=False), known=known(gap=False), first=first(gap=False), n_rows=360)
        self.assertEqual([p["outcome"] for p in res], ["held", "held", "not scored", "held", "held"])


class TableTests(unittest.TestCase):
    def test_tables(self):
        t = gt.tables(nc.annotate(fixture()))
        self.assertEqual(len(t), 3 * 6 * 5)
        late = "2022-01 to 2025-12"
        row = [x for x in t if x["period"] == late and x["group"] == "solar" and x["cell"] == "first"][0]
        self.assertEqual((row["months"], row["operating"], row["generators"], row["plants"]), (120, 12, 120, 3))
        row = [x for x in t if x["period"] == late and x["group"] == "all" and x["cell"] == "first"][0]
        self.assertEqual((row["months"], row["operating"], row["generators"], row["plants"]), (160, 12, 160, 4))
        row = [x for x in t if x["period"] == "2026-01 to 2026-08" and x["group"] == "solar"
               and x["cell"] == "2-3 months"][0]
        self.assertEqual((row["months"], row["operating"], row["generators"], row["plants"]), (40, 2, 40, 1))
        self.assertEqual(sum(x["months"] for x in t if x["group"] == "all"), 440)
        self.assertEqual(sum(x["months"] for x in t if x["group"] != "all"), 440)


class RunTests(unittest.TestCase):
    def test_wait_plan(self):
        urls = []

        def served(url):
            urls.append(url)
            return gt.PLAN_MARK.encode() if len(urls) > 1 else b"404: Not Found"

        slept = []
        self.assertTrue(gt.wait_plan(10, get=served, sleep=slept.append, clock=lambda: 0))
        self.assertEqual(slept, [600])
        self.assertEqual(urls, [nc.BASE + "docs/nextgaptech-plan.md"] * 2)
        self.assertFalse(gt.wait_plan(10, get=lambda url: b"404: Not Found", sleep=slept.append, clock=lambda: 99))
        self.assertEqual(slept, [600])

    def test_main_local(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "cohort.csv")
            with open(path, "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, FIELDS)
                w.writeheader()
                w.writerows(fixture())
            out = os.path.join(tmp, "out")
            self.assertEqual(gt.main(["--cohort", path, "--out-dir", out]), 0)
            with open(os.path.join(out, "gaptech.md"), encoding="utf-8") as fh:
                md = fh.read()
            self.assertIn("| C0 | failed | 440 rows;", md)
            self.assertIn("Held: 0 of 0 scored", md)
            self.assertIn("| 2022-01 to 2025-12 | solar | 1 month | 40 | 20 | 0.5000 | 40 | 1 |", md)
            self.assertIn("| 2026-01 to 2026-08 | all | first | 80 | 0 | 0.0000 | 80 | 2 |", md)
            self.assertNotIn("| gas |", md)
            with open(os.path.join(out, "gaptech.json"), encoding="utf-8") as fh:
                res = json.load(fh)
            self.assertEqual(res["rows"], 440)
            self.assertEqual(len(res["tables"]), 90)

    def test_main_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "out")
            self.assertEqual(gt.main(["--cohort", os.path.join(tmp, "missing.csv"), "--out-dir", out]), 2)
            with open(os.path.join(out, "gaptech.md"), encoding="utf-8") as fh:
                self.assertIn("Not run: cohort file not read: FileNotFoundError", fh.read())


if __name__ == "__main__":
    unittest.main()
