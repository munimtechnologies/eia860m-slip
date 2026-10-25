"""Tests for gapwin.py. MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import csv
import json
import os
import tempfile
import unittest

import gapwin as gw
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
    """2020-2021 solar: first 12 of 120 (80 without gap), 1 month s_ops of 40, 2-3 months 4 of 40 (none
    without gap); batteries: first 0 of 40, 1 month 30 of 40; gas: first 30 of 80, 1 month 10 of 40;
    wind: first 20 of 80, 1 month 5 of 40; and 40 solar rows of 2023, outside the period."""
    rows = (gens("1", ["2020-03"], 12) + gens("2", ["2020-05", "2020-06"], s_ops)
            + gens("4", ["2021-05", "2021-06"], 30, "batteries")
            + gens("5", ["2020-01"], 30, "gas") + gens("6", ["2020-07", "2020-08"], 10, "gas")
            + gens("7", ["2021-02"], 20, "wind") + gens("8", ["2021-08", "2021-09"], 5, "wind")
            + gens("9", ["2023-01"], 3))
    return rows + (gens("3", ["2021-01", "2021-04"], 4) if gap else [])


def known(s_ops=20, gap=True):
    return {"solar": (16 + s_ops if gap else 12 + s_ops, 200 if gap else 120), "batteries": (30, 80),
            "gas": (40, 120), "wind": (25, 120)}


class HelperTests(unittest.TestCase):
    def test_fixture(self):
        self.assertEqual(len(fixture()), 560)
        self.assertEqual(len(fixture(gap=False)), 480)

    def test_constants(self):
        self.assertEqual(gw.PLAN_URL, nc.BASE + "docs/gapwin-plan.md")
        self.assertEqual(gw.WIN, ("2020-01", "2021-12"))
        self.assertEqual(list(gw.KNOWN), ["solar", "batteries", "gas", "wind"])
        self.assertEqual([b[0] for b in gw.BARS], ["W1", "W2", "W3", "W4", "W5"])
        self.assertEqual([b[4] for b in gw.BARS], ["above", "above", "above", "below", "below"])
        self.assertTrue(all(b[2] in gt.CELLS and b[3] in gt.CELLS for b in gw.BARS))
        self.assertEqual(sum(v[1] for v in gw.KNOWN.values()), 2692)


class ScoreTests(unittest.TestCase):
    def test_score_holds(self):
        res = gw.score(fixture(), known=known(), n_rows=560)
        self.assertEqual([p["id"] for p in res], ["C0", "W1", "W2", "W3", "W4", "W5"])
        self.assertEqual([p["outcome"] for p in res], ["held"] * 6)
        self.assertEqual(res[0]["value"], "560 rows; 2020-2021: solar 36 of 200, batteries 30 of 80, gas 40 of 120, "
                                          "wind 25 of 120")
        self.assertEqual(res[1]["value"], "1 month: 20 of 40; first: 12 of 120")
        self.assertEqual(res[2]["value"], "1 month: 20 of 40; 2-3 months: 4 of 40")
        self.assertEqual(res[3]["value"], "1 month: 30 of 40; first: 0 of 40")
        self.assertEqual(res[4]["value"], "1 month: 10 of 40; first: 30 of 80")
        self.assertEqual(res[5]["value"], "1 month: 5 of 40; first: 20 of 80")

    def test_failures(self):
        res = gw.score(fixture(s_ops=2), known=known(s_ops=2), n_rows=560)
        self.assertEqual([p["outcome"] for p in res], ["held", "failed", "failed", "held", "held", "held"])

    def test_below_fails_when_above(self):
        rows = [x for x in fixture() if not x["key"].startswith("5/")] + gens("5", ["2020-01"], 0, "gas")
        k = dict(known(), gas=(10, 120))
        res = gw.score(rows, known=k, n_rows=560)
        self.assertEqual(res[4]["value"], "1 month: 10 of 40; first: 0 of 80")
        self.assertEqual(res[4]["outcome"], "failed")

    def test_c0_fails(self):
        res = gw.score(fixture())
        self.assertEqual(res[0]["outcome"], "failed")
        self.assertEqual(res[0]["bar"], "14807 rows; 2020-2021: solar 686 of 1600, batteries 103 of 344, "
                                        "gas 150 of 375, wind 143 of 373")
        self.assertEqual({p["outcome"] for p in res[1:]}, {"not scored"})
        res = gw.score(fixture(), known=dict(known(), wind=(26, 120)), n_rows=560)
        self.assertEqual(res[0]["outcome"], "failed")

    def test_too_few(self):
        res = gw.score(fixture(gap=False), known=known(gap=False), n_rows=480)
        self.assertEqual([p["outcome"] for p in res], ["held", "held", "not scored", "held", "held", "held"])


class TableTests(unittest.TestCase):
    def test_tables(self):
        t = gw.tables(nc.annotate(fixture()))
        self.assertEqual(len(t), 6 * 5)
        self.assertEqual({x["period"] for x in t}, {"2020-01 to 2021-12"})
        row = [x for x in t if x["group"] == "solar" and x["cell"] == "first"][0]
        self.assertEqual((row["months"], row["operating"], row["generators"], row["plants"]), (120, 12, 120, 3))
        row = [x for x in t if x["group"] == "all" and x["cell"] == "first"][0]
        self.assertEqual((row["months"], row["operating"], row["generators"], row["plants"]), (320, 62, 320, 8))
        self.assertEqual(sum(x["months"] for x in t if x["group"] == "all"), 520)
        self.assertEqual(sum(x["months"] for x in t if x["group"] != "all"), 520)


class RunTests(unittest.TestCase):
    def test_wait_plan(self):
        urls = []

        def served(url):
            urls.append(url)
            return gw.PLAN_MARK.encode() if len(urls) > 1 else b"404: Not Found"

        slept = []
        self.assertTrue(gw.wait_plan(10, get=served, sleep=slept.append, clock=lambda: 0))
        self.assertEqual(slept, [600])
        self.assertEqual(urls, [nc.BASE + "docs/gapwin-plan.md"] * 2)
        self.assertFalse(gw.wait_plan(10, get=lambda url: b"404: Not Found", sleep=slept.append, clock=lambda: 99))
        self.assertEqual(slept, [600])

    def test_main_local(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "cohort.csv")
            with open(path, "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, FIELDS)
                w.writeheader()
                w.writerows(fixture())
            out = os.path.join(tmp, "out")
            self.assertEqual(gw.main(["--cohort", path, "--out-dir", out]), 0)
            with open(os.path.join(out, "gapwin.md"), encoding="utf-8") as fh:
                md = fh.read()
            self.assertIn("| C0 | failed | 560 rows;", md)
            self.assertIn("Held: 0 of 0 scored", md)
            self.assertIn("| 2020-01 to 2021-12 | solar | 1 month | 40 | 20 | 0.5000 | 40 | 1 |", md)
            self.assertIn("| 2020-01 to 2021-12 | gas | first | 80 | 30 | 0.3750 | 80 | 2 |", md)
            self.assertNotIn("| other |", md)
            self.assertNotIn("2023", md.split("## By technology")[1])
            with open(os.path.join(out, "gapwin.json"), encoding="utf-8") as fh:
                res = json.load(fh)
            self.assertEqual(res["rows"], 560)
            self.assertEqual(len(res["tables"]), 30)

    def test_main_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "out")
            self.assertEqual(gw.main(["--cohort", os.path.join(tmp, "missing.csv"), "--out-dir", out]), 2)
            with open(os.path.join(out, "gapwin.md"), encoding="utf-8") as fh:
                self.assertIn("Not run: cohort file not read: FileNotFoundError", fh.read())


if __name__ == "__main__":
    unittest.main()
