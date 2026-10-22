"""Checks the numbers in docs/history-revert.md (the twenty-ninth result, scored 22 October 2026)
against the raw output of compete job history-v1 (data/history_v1.json, data/history_v1_hits.csv,
data/history_v1_years.csv, data/history_v1_months.csv, docs/history-v1-output.md,
docs/history-v1-unittests.txt).
MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import calendar
import csv
import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
STATUS = "Status: scored against its pre-registration"
SCORED = tuple(range(2016, 2026))
P1_MIN = 50
COVERAGE = 0.90
PRECISION = 0.50
YEAR_COVERAGE = 0.80
KEYS_MIN = 0.95
MIN_UNITS = 100
LAST = "2026-08"
MISSED = (2017, 2018, 2019)
OUT_OF_SERVICE = ("OA", "OS", "SB", "RE")
KINDS = ("hits", "pudl_later", "held_before", "other")
EXAMPLE = ("3084/13", "3895/3", "3921/3", "6174/1", "6174/2")
SB_EXAMPLE = "1134/5"


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8") as fh:
        return fh.read()


def rows(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def n(x):
    return "{:,}".format(x)


def mw(x):
    s = "{:,.1f}".format(x)
    return s[:-2] if s.endswith(".0") else s


def month_name(m):
    return "%s %s" % (calendar.month_name[int(m[5:7])], m[:4])


def status(cell):
    return cell.split(", ")[0]


def cell_mw(cell):
    return float(cell.split(", ")[2].split()[0])


class HistoryRevertDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = read("docs", "history-revert.md")
        cls.raw = json.loads(read("data", "history_v1.json"))
        cls.res = cls.raw["result"]
        cls.years = {int(k): v for k, v in cls.res["years"].items()}
        cls.total = cls.res["total"]
        cls.out = read("docs", "history-v1-output.md")
        cls.log = read("docs", "history-v1-unittests.txt")
        cls.hits = rows("data", "history_v1_hits.csv")
        cls.aug = {r["key"]: r for r in cls.hits if r["month"] == LAST}

    def test_status_line(self):
        v = self.raw["verdict"]
        line = self.text.splitlines()[2]
        self.assertTrue(line.startswith(STATUS))
        self.assertTrue(v["scored"])
        self.assertIn("all checks passed and %d of %d predictions held." % (v["held"], len(v["predictions"])),
                      line)
        self.assertTrue(all(c["ok"] for c in self.raw["checks"].values()))

    def test_verdict_recomputed(self):
        ys, t = self.years, self.total
        p = {"P1": all(ys[y]["hits"] >= P1_MIN for y in SCORED),
             "P2": t["hits"] >= COVERAGE * t["disagree"],
             "P3": t["hits"] >= PRECISION * t["sim_stale"],
             "P4": ys[2025]["hits"] * ys[2017]["months"] > ys[2017]["hits"] * ys[2025]["months"],
             "P5": all(ys[y]["hits"] >= YEAR_COVERAGE * ys[y]["disagree"] for y in SCORED)}
        self.assertEqual(p, self.raw["verdict"]["predictions"])
        self.assertEqual([y for y in SCORED if ys[y]["hits"] < YEAR_COVERAGE * ys[y]["disagree"]],
                         list(MISSED))
        table = [l for l in self.text.splitlines() if l.startswith("| P")]
        self.assertEqual([l[2:4] for l in table], sorted(p))
        for l in table:
            self.assertTrue(l.endswith("| %s |" % ("yes" if p[l[2:4]] else "no")), l)
        self.assertIn("| at least %d |" % P1_MIN, self.text)
        for bar in (COVERAGE, PRECISION, YEAR_COVERAGE):
            self.assertIn("| at least %.2f |" % bar, self.text)

    def test_checks_recomputed(self):
        raw, ys, t = self.raw, self.years, self.total
        self.assertTrue(all(z["ok"] and z["md5_matches_page"] and z["md5_matches_datapackage"]
                            for z in raw["zips"]))
        self.assertEqual(sorted(ys), list(range(2015, 2027)))
        self.assertTrue(all(m["readable"] for m in raw["months"]))
        self.assertEqual(len(raw["months"]), t["months"])
        self.assertGreaterEqual(raw["pudl"]["max_report"], LAST)
        self.assertTrue(all(y["with_pudl"] >= KEYS_MIN * y["workbook"] for y in ys.values()))
        self.assertGreaterEqual(min(t["disagree"], t["sim_stale"]), MIN_UNITS)
        self.assertTrue(raw["gate"]["live"])
        self.assertLess(raw["prereg_commit"]["date"], raw["gate"]["at"])

    def test_unit_tests_and_copies(self):
        ran = int(re.search(r"Ran (\d+) tests", self.log).group(1))
        self.assertEqual(len(re.findall(r" \.\.\. ok$", self.log, re.M)), ran)
        self.assertTrue(self.log.rstrip().endswith("OK"))
        pub = self.raw["published"]
        self.assertTrue(pub["same"])
        self.assertEqual(sorted(pub["files"]), ["history.py", "test_history.py"])
        self.assertTrue(all(f["same"] for f in pub["files"].values()))
        self.assertIn("Published copies same as run copies: True", self.out)
        self.assertIn("Scored: %d of 5 predictions held." % self.raw["verdict"]["held"], self.out)

    def test_counts_add_up(self):
        ys, t = self.years, self.total
        for y in list(ys.values()) + [t]:
            self.assertEqual(sum(y[k] for k in KINDS), y["disagree"])
            self.assertEqual(y["units"], y["with_pudl"])
            self.assertEqual(y["with_pudl"] + y["workbook_only"], y["workbook"])
        for c in ("months", "units", "disagree", "sim_stale", "workbook_only") + KINDS:
            self.assertEqual(sum(y[c] for y in ys.values()), t[c], c)
        bm = self.res["by_month"]
        self.assertEqual(len(bm), t["months"])
        self.assertEqual(sum(m["hits"] for m in bm), t["hits"])
        self.assertEqual(sum(m["disagree"] for m in bm), t["disagree"])
        self.assertEqual(len(self.hits), t["hits"])
        for yr, y in ys.items():
            self.assertEqual(sum(1 for r in self.hits if r["month"][:4] == str(yr)), y["hits"], yr)
        self.assertEqual(len(self.aug), [m for m in bm if m["month"] == LAST][0]["hits"])
        csv_years = {int(r["year"]): r for r in rows("data", "history_v1_years.csv")}
        for yr, y in ys.items():
            self.assertEqual((int(csv_years[yr]["disagree"]), int(csv_years[yr]["hits"])),
                             (y["disagree"], y["hits"]))
        csv_months = rows("data", "history_v1_months.csv")
        self.assertEqual(sum(int(r["hits"]) for r in csv_months), t["hits"])

    def test_year_table(self):
        lines = self.text.splitlines()
        for label, y in [(str(yr), y) for yr, y in sorted(self.years.items())] + [("all", self.total)]:
            want = "| %s | %d | %s | %s | %s | %.4f | %s | %s | %s | %.2f |" % (
                label, y["months"], n(y["units"]), n(y["disagree"]), n(y["hits"]), y["coverage"],
                n(y["pudl_later"]), n(y["held_before"]), n(y["other"]), y["hits_per_month"])
            self.assertIn(want, lines)

    def test_examples(self):
        for k in EXAMPLE:
            r = self.aug[k]
            self.assertEqual((status(r["workbook"]), status(r["pudl"]), r["pudl_reported"], r["differs_since"]),
                             ("OP", "OA", "2017-03", "2018-03"), k)
        r = self.aug[SB_EXAMPLE]
        self.assertEqual((status(r["workbook"]), status(r["pudl"])), ("SB", "OP"))
        s = [x for x in self.res["samples"] if x["year"] == 2017 and x["kind"] == "held_before"][0]
        got = {x["key"]: x for x in s["rows"] if x["month"] == "2017-08"}
        for k, w, p in (("3075/11", "OP", "OA"), ("3075/12", "OA", "OP")):
            self.assertEqual((status(got[k]["workbook"]), status(got[k]["pudl"]), got[k]["pudl_reported"]),
                             (w, p, "2017-04"), k)

    def test_stated_numbers(self):
        for s in [s % v for s, v in STATED(self)]:
            self.assertIn(s, self.text, s)


def STATED(t):
    ys, tot, raw, res = t.years, t.total, t.raw, t.res
    aug = list(t.aug.values())
    oos = [r for r in aug if status(r["workbook"]) == "OP" and status(r["pudl"]) in OUT_OF_SERVICE]
    old = [r for r in aug if r["pudl_reported"] < "2020"]
    long = [r for r in aug if r["differs_since"] < "2020"]
    missed = sum(ys[y]["disagree"] - ys[y]["hits"] for y in MISSED)
    held3 = sum(ys[y]["held_before"] for y in MISSED)
    late = sum(ys[y]["disagree"] for y in ys if y >= 2020)
    low = min(SCORED, key=lambda y: (ys[y]["hits"], y))
    others = min(ys[y]["coverage"] for y in SCORED if y not in MISSED)
    ran = int(re.search(r"Ran (\d+) tests", t.log).group(1))
    gate, pudl = raw["gate"], raw["pudl"]
    ex = [t.aug[k] for k in EXAMPLE]
    sb = t.aug[SB_EXAMPLE]
    ev = res["events"]
    back_others = [e["back"] for yr, e in ev.items() if yr != "2024"]
    return [
        ("disagree on status, planned month or MW in %s of %s generator-months.",
         (n(tot["disagree"]), n(tot["units"]))),
        ("gives PUDL's value in %s of them (coverage %.4f).", (n(tot["hits"]), tot["coverage"])),
        ("in every year from %d (at least %d a year)", (SCORED[0], ys[low]["hits"])),
        ("%.2f a month in 2017, %.2f a month in 2025.", (ys[2017]["hits_per_month"], ys[2025]["hits_per_month"])),
        ("In August 2026, %d generators carry such a value. In %d of them", (len(aug), len(oos))),
        ("For %d the PUDL record in force was reported before 2020, and %d have disagreed with the workbook "
         "in every month since a month before 2020.", (len(old), len(long))),
        ("It was %.4f in 2017, %.4f in 2018 and %.4f in 2019.", tuple(ys[y]["coverage"] for y in MISSED)),
        ("In those three years, %d of the %d disagreements the simulation misses", (held3, missed)),
        ("which passed %d of %d unit tests", (ran, ran)),
        ("at its first check (%s UTC, commit %s)", (gate["at"][11:19], raw["prereg_commit"]["sha"][:7])),
        ("(%s bytes, %s rows, file time %d %s, latest report %s)",
         (n(pudl["bytes"]), n(pudl["rows"]), int(pudl["mtime"][8:10]), month_name(pudl["mtime"][:7]),
          pudl["max_report"])),
        ("in %d yearly zips", (len(raw["zips"]),)),
        ("This one replayed all %d monthly EIA-860M workbooks", (tot["months"],)),
        ("passed (%d of %d zips, %d months, none unreadable)",
         (sum(1 for z in raw["zips"] if z["ok"]), len(raw["zips"]), len(raw["months"]))),
        ("passed (%s) |", (pudl["max_report"],)),
        ("passed (lowest %.4f) |", (min(y["keys_share"] for y in ys.values()),)),
        ("passed (%s and %s) |", (n(tot["disagree"]), n(tot["sim_stale"]))),
        ("passed (%d of %d) |", (ran, ran)),
        ("| lowest %d (%d) |", (ys[low]["hits"], low)),
        ("| %.4f (%s of %s) |", (tot["coverage"], n(tot["hits"]), n(tot["disagree"]))),
        ("| %.4f (%s of %s) |", (tot["precision"], n(tot["hits"]), n(tot["sim_stale"]))),
        ("| %.2f against %.2f |", (ys[2025]["hits_per_month"], ys[2017]["hits_per_month"])),
        ("| %.4f (2017), %.4f (2018), %.4f (2019); every other year at least %.4f |",
         tuple(ys[y]["coverage"] for y in MISSED) + (others,)),
        ("%d generators have disagreed with the workbook in every month since before 2020.", (len(long),)),
        ("%s of the %s disagreeing generator-months fall in 2020 to 2026.", (n(late), n(tot["disagree"]))),
        ("The simulation marks %s more stale generator-months than it hits (%s less %s).",
         (n(tot["sim_stale"] - tot["hits"]), n(tot["sim_stale"]), n(tot["hits"]))),
        ("in a later PUDL record (%d generator-months, all years) or in an earlier one (%s).",
         (tot["pudl_later"], n(tot["held_before"]))),
        ('the "held before" kind is %d of the %d misses.', (held3, missed)),
        ("(%s MW together) are operating in EIA's August 2026 workbook. Each has disagreed with PUDL in every "
         "month since %s. PUDL's record in force, reported in %s,",
         (mw(sum(cell_mw(r["workbook"]) for r in ex)), month_name(ex[0]["differs_since"]),
          month_name(ex[0]["pudl_reported"]))),
        ("1134/5 (%s MW) is on standby (SB) in EIA's August 2026 workbook and has disagreed with PUDL in every "
         "month since %s. PUDL's record in force, reported in %s,",
         (mw(cell_mw(sb["workbook"])), month_name(sb["differs_since"]), month_name(sb["pudl_reported"]))),
        ("In 2026, %d workbook generator-months have no PUDL record in force.", (ys[2026]["workbook_only"],)),
        ('2016 has %s "changed" rows', (n(ev["2016"]["changed"]),)),
        ('2024 has %d "back" rows, against %d to %d in every other year.',
         (ev["2024"]["back"], min(back_others), max(back_others))),
    ]


if __name__ == "__main__":
    unittest.main()
