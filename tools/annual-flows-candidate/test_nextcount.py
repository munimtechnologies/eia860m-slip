"""Tests for nextcount.py. MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import csv
import os
import tempfile
import unittest

import nextcount as nc

FIELDS = ["month", "key", "technology", "group", "now", "nameplate_mw", "found"]


def r(month, key, where, group="solar"):
    return {"month": month, "key": key, "technology": group, "group": group, "now": where,
            "nameplate_mw": "1.0", "found": "True"}


def ms(i):
    return "%d-%02d" % (i // 12, i % 12 + 1)


def slip(start, prefix, n, ops):
    """n generators planned for the next month in consecutive months from start: at their j-th listing
    the first ops[j] of those still waiting are listed as operating; the rest wait on."""
    rows, waiting = [], ["%s/%d" % (prefix, i) for i in range(n)]
    for j, k in enumerate(ops):
        month = ms(nc.m_index(start) + j)
        rows += [r(month, key, "Operating" if i < k else "Planned") for i, key in enumerate(waiting)]
        waiting = waiting[k:]
    return rows


def falling():
    """Late: 0 earlier listings 30 of 120, 1: 16 of 80, 2: 8 of 64, 3+: 4 of 56.
    Early: 0: 20 of 80, 1: 0 of 40, 2: 0 of 40, 3+: 20 of 40."""
    return (slip("2023-01", "5", 40, [30]) + slip("2023-02", "6", 80, [0, 16, 8, 4])
            + slip("2017-01", "7", 40, [20]) + slip("2017-02", "8", 40, [0, 0, 0, 20]))


FALLING_KNOWN = {nc.EARLY: (40, 200), nc.LATE: (58, 320)}


class HelperTests(unittest.TestCase):
    def test_slip_fixture(self):
        rows = falling()
        self.assertEqual(len(rows), 520)
        self.assertEqual(nc.frac([x for x in rows if nc.in_period(x["month"], nc.LATE)]), (58, 320))

    def test_annotate(self):
        rows = [r("2016-03", "1/A", "Planned"), r("2016-01", "1/A", "Planned"), r("2016-02", "2/B", "Planned"),
                r("2017-01", "1/A", "Operating")]
        got = [(x["month"], x["key"], x["prior"], x["gap"]) for x in nc.annotate(rows)]
        self.assertEqual(got, [("2016-01", "1/A", 0, None), ("2016-02", "2/B", 0, None), ("2016-03", "1/A", 1, 2),
                               ("2017-01", "1/A", 2, 10)])

    def test_months(self):
        self.assertEqual(nc.m_index("2017-01") - nc.m_index("2016-12"), 1)
        self.assertEqual(ms(nc.m_index("2016-12") + 1), "2017-01")

    def test_bins(self):
        self.assertEqual([nc.bin_of(p) for p in (0, 1, 2, 3, 11)], ["0", "1", "2", "3+", "3+"])
        self.assertEqual(nc.label(7, nc.FINE), "5-9")
        self.assertEqual(nc.label(10, nc.FINE), "10+")
        self.assertEqual(nc.label(1, nc.GAPS), "1 month")
        self.assertEqual(nc.label(3, nc.GAPS), "2-3 months")
        self.assertEqual(nc.label(13, nc.GAPS), "more than 12 months")
        self.assertIsNone(nc.label(0, nc.GAPS))

    def test_by_bin(self):
        a = nc.annotate(falling())
        self.assertEqual(nc.by_bin(a, nc.LATE), {"0": (30, 120), "1": (16, 80), "2": (8, 64), "3+": (4, 56)})
        self.assertEqual(nc.by_bin(a, nc.EARLY), {"0": (20, 80), "1": (0, 40), "2": (0, 40), "3+": (20, 40)})


class ScoreTests(unittest.TestCase):
    def test_score_holds(self):
        res = nc.score(falling(), known=FALLING_KNOWN, n_rows=520)
        self.assertEqual([p["id"] for p in res], ["C0", "K1", "K2", "K3"])
        self.assertEqual([p["outcome"] for p in res], ["held"] * 4)
        self.assertEqual(res[1]["value"], "0: 30 of 120; 3+: 4 of 56")
        self.assertEqual(res[3]["value"], "2016-2019 0: 20 of 80, 3+: 20 of 40; 2022-2025 0: 30 of 120, 3+: 4 of 56")

    def test_c0_fails(self):
        res = nc.score(falling())
        self.assertEqual(res[0]["outcome"], "failed")
        self.assertEqual({p["outcome"] for p in res[1:]}, {"not scored"})

    def test_failures(self):
        rows = slip("2023-01", "4", 40, [0, 0, 0, 20]) + slip("2017-02", "8", 40, [0, 0, 0, 20])
        res = {p["id"]: p for p in nc.score(rows, known={nc.EARLY: (20, 160), nc.LATE: (20, 160)}, n_rows=320)}
        self.assertEqual(res["C0"]["outcome"], "held")
        self.assertEqual(res["K1"]["outcome"], "failed")
        self.assertEqual(res["K2"]["outcome"], "failed")
        self.assertEqual(res["K3"]["outcome"], "failed")

    def test_too_few(self):
        rows = slip("2023-01", "4", 10, [5]) + slip("2017-02", "8", 40, [0, 0, 0, 20])
        res = {p["id"]: p for p in nc.score(rows, known={nc.EARLY: (20, 160), nc.LATE: (5, 10)}, n_rows=170)}
        self.assertEqual(res["C0"]["outcome"], "held")
        self.assertEqual({res[k]["outcome"] for k in ("K1", "K2", "K3")}, {"not scored"})


class TableTests(unittest.TestCase):
    def test_tables(self):
        t = nc.tables(nc.annotate(falling()))
        late = "2022-01 to 2025-12"
        row = [x for x in t["bins"] if x["period"] == late and x["cell"] == "3+"][0]
        self.assertEqual((row["months"], row["operating"], row["generators"], row["plants"]), (56, 4, 56, 1))
        gap = [x for x in t["gaps"] if x["period"] == late and x["cell"] == "1 month"][0]
        self.assertEqual((gap["months"], gap["operating"], gap["generators"], gap["plants"]), (200, 28, 80, 1))
        self.assertEqual(t["without_gas_plant"], t["bins"])
        self.assertEqual(sum(x["months"] for x in t["tech"] if x["group"] == "solar"), 520)
        self.assertEqual(sum(x["months"] for x in t["fine"]), 520)


class RunTests(unittest.TestCase):
    def test_wait_plan(self):
        replies = iter([b"404: Not Found", nc.PLAN_MARK.encode()])
        slept = []
        self.assertTrue(nc.wait_plan(10, get=lambda url: next(replies), sleep=slept.append, clock=lambda: 0))
        self.assertEqual(slept, [600])
        self.assertFalse(nc.wait_plan(10, get=lambda url: b"404: Not Found", sleep=slept.append, clock=lambda: 99))
        self.assertEqual(slept, [600])

    def test_main_local(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "cohort.csv")
            with open(path, "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, FIELDS)
                w.writeheader()
                w.writerows(falling())
            out = os.path.join(tmp, "out")
            self.assertEqual(nc.main(["--cohort", path, "--out-dir", out]), 0)
            with open(os.path.join(out, "nextcount.md"), encoding="utf-8") as fh:
                md = fh.read()
            self.assertIn("| C0 | failed | 520 rows;", md)
            self.assertIn("repeated generator and month rows: 0", md)
            self.assertIn("Held: 0 of 0 scored", md)
            self.assertIn("| 2022-01 to 2025-12 | 3+ | 56 | 4 | 0.0714 | 56 | 1 |", md)
            self.assertIn("| 2022-01 to 2025-12 | solar | 3+ | 56 | 4 | 0.0714 | 56 | 1 |", md)
            self.assertIn("| 2022-01 to 2025-12 | 1 month | 200 | 28 | 0.1400 | 80 | 1 |", md)
            with open(os.path.join(out, "nextcount_rows.csv"), newline="", encoding="utf-8") as fh:
                rows = list(csv.DictReader(fh))
            self.assertEqual(len(rows), 520)
            self.assertEqual((rows[0]["month"], rows[0]["prior"], rows[0]["gap"]), ("2017-01", "0", ""))

    def test_main_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "out")
            self.assertEqual(nc.main(["--cohort", os.path.join(tmp, "missing.csv"), "--out-dir", out]), 2)
            with open(os.path.join(out, "nextcount.md"), encoding="utf-8") as fh:
                self.assertIn("Not run: cohort file not read: FileNotFoundError", fh.read())


if __name__ == "__main__":
    unittest.main()
