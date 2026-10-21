"""Checks the numbers in docs/changelog-revert.md (the twenty-eighth result, scored 21 October 2026)
against the raw output of compete job revert-v1 (data/revert_v1.json, data/revert_v1_august.csv,
docs/revert-v1-output.md, docs/revert-v1-unittests.txt, docs/revert-v1-md5.txt).
MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import calendar
import csv
import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
STATUS = "Status: scored against its pre-registration"
COVERAGE = 0.90
PRECISION = 0.50
MIN_UNITS = 100
OUT_OF_SERVICE = ("OA", "OS", "SB", "RE")
EXAMPLES = (("55098/GEN1", "55098/GEN2", "55098/GEN3"), ("2828/1", "2828/2", "2828/3"))


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8") as fh:
        return fh.read()


def n(x):
    return "{:,}".format(x)


def mw(x):
    s = "{:,.1f}".format(x)
    return s[:-2] if s.endswith(".0") else s


def month_name(m):
    return "%s %s" % (calendar.month_name[int(m[5:])], m[:4])


def status(cell):
    return cell.split(", ")[0]


class ChangelogRevertDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = read("docs", "changelog-revert.md")
        cls.raw = json.loads(read("data", "revert_v1.json"))
        cls.res = cls.raw["result"]
        cls.out = read("docs", "revert-v1-output.md")
        cls.log = read("docs", "revert-v1-unittests.txt")
        cls.md5 = read("docs", "revert-v1-md5.txt")
        with open(os.path.join(HERE, "data", "revert_v1_august.csv"), encoding="utf-8", newline="") as fh:
            cls.csv = list(csv.DictReader(fh))
        cls.aug = {r["key"]: r for r in cls.res["august"]}

    def test_status_line(self):
        v = self.raw["verdict"]
        line = self.text.splitlines()[2]
        self.assertTrue(line.startswith(STATUS))
        self.assertTrue(v["scored"])
        self.assertIn("all checks passed and %d of %d predictions held." % (v["held"], len(v["predictions"])),
                      line)
        self.assertTrue(all(c["ok"] for c in self.raw["checks"].values()))

    def test_verdict_recomputed(self):
        sc = self.res["score"]
        self.assertEqual(self.res["repeats"]["repeats"], 0)
        self.assertGreaterEqual(sc["hits"], COVERAGE * sc["disagree"])
        self.assertGreaterEqual(sc["hits"], PRECISION * sc["sim_stale"])
        self.assertTrue(all(x["held"] for x in self.res["named"]))
        self.assertGreaterEqual(min(sc["disagree"], sc["sim_stale"]), MIN_UNITS)
        self.assertIn("at least %.2f" % COVERAGE, self.text)
        self.assertIn("at least %.2f" % PRECISION, self.text)
        self.assertIn("each at least %d generator-months" % MIN_UNITS, self.text)

    def test_unit_tests_and_copies(self):
        ran = int(re.search(r"Ran (\d+) tests", self.log).group(1))
        self.assertEqual(len(re.findall(r" \.\.\. ok$", self.log, re.M)), ran)
        self.assertTrue(self.log.rstrip().endswith("OK"))
        lines = self.md5.strip().splitlines()
        self.assertEqual([l.split()[0] for l in lines], ["revert.py", "test_revert.py", "keyhist.py"])
        self.assertTrue(all("published copy same as run copy: True" in l for l in lines))

    def test_counts_add_up(self):
        sc = self.res["score"]
        self.assertEqual(sum(p["n"] for p in self.res["pairs"]), sc["hits"])
        self.assertEqual(sum(m["predicted"] for m in self.res["by_month"].values()), sc["hits"])
        for m, b in self.res["by_month"].items():
            self.assertEqual((b["pudl_later"], b["held_before"], b["other"]), (0, 0, 0), m)
        self.assertEqual(len(self.res["august"]), self.res["by_month"]["2026-08"]["predicted"])
        self.assertEqual([r["key"] for r in self.csv], [r["key"] for r in self.res["august"]])
        self.assertIn("Scored: %d of 4 predictions held." % self.raw["verdict"]["held"], self.out)

    def test_examples(self):
        for keys in EXAMPLES:
            rows = [self.aug[k] for k in keys]
            self.assertEqual(len({(r["pudl"].split(", ")[0], r["pudl_reported"], r["differs_since"])
                                  for r in rows}), 1, keys)
            self.assertTrue(all(status(r["workbook"]) == "OP" for r in rows))
        for k in ("6481/1", "6481/2"):
            r = self.aug[k]
            self.assertEqual((status(r["workbook"]), status(r["pudl"]), r["pudl_reported"], r["differs_since"]),
                             ("RE", "OS", "2026-03", "2026-07"))
        self.assertEqual(status(self.aug["55098/GEN1"]["pudl"]), "RE")
        self.assertEqual(status(self.aug["2828/1"]["pudl"]), "OS")

    def test_stated_numbers(self):
        for s in [s % v for s, v in STATED(self)]:
            self.assertIn(s, self.text, s)


def STATED(t):
    sc, res, raw = t.res["score"], t.res, t.raw
    rep = res["repeats"]
    aug = res["august"]
    oos = [r for r in aug if status(r["workbook"]) == "OP" and status(r["pudl"]) in OUT_OF_SERVICE]
    old = [r for r in aug if r["pudl_reported"] < "2020"]
    months = res["by_month"].values()
    by_field = {}
    for p in res["pairs"]:
        by_field[p["field"]] = by_field.get(p["field"], 0) + p["n"]
    op_out = sum(p["n"] for p in res["pairs"]
                 if p["field"] == "status" and p["workbook"] == "OP" and p["pudl"] in OUT_OF_SERVICE)
    named = {x["key"]: x for x in res["named"]}
    gone_mw = sum(float(x["sheet_status"].split(", ")[2].split()[0]) for x in res["august_workbook_only_trace"])
    ran = int(re.search(r"Ran (\d+) tests", t.log).group(1))
    gate, pudl = raw["gate"], raw["pudl"]
    ex = [[t.aug[k] for k in keys] for keys in EXAMPLES]
    return [
        ("(%d of %s rows)", (rep["repeats"], n(rep["rows"]))),
        ("In %s of %s generator-months (January to August 2026)", (n(sc["disagree"]), n(sc["units"]))),
        ("gives PUDL's value in all %s.", (n(sc["hits"]),)),
        ("In August 2026 that is %d generators, %s MW by the workbook. %d of them",
         (len(aug), "{:,.1f}".format(sum(r["workbook_mw"] or 0 for r in aug)), len(oos))),
        ("(%d retired). For %d the PUDL record in force was reported before 2020, the earliest in %s.",
         (sum(1 for r in oos if status(r["pudl"]) == "RE"), len(old), min(r["pudl_reported"] for r in aug)[:4])),
        ("which passed %d of %d unit tests", (ran, ran)),
        ("at its first check (%s UTC, commit %s)", (gate["at"][11:19], raw["prereg_commit"]["sha"][:7])),
        ("(%s bytes, file time %d %s, latest report %s)",
         (n(pudl["bytes"]), int(pudl["mtime"][8:10]), month_name(pudl["mtime"][:7]), pudl["max_report"])),
        ("passed (D %s, S %s)", (n(sc["disagree"]), n(sc["sim_stale"]))),
        ("passed (%d of %d) |", (ran, ran)),
        ("| 0 of %s rows (%d columns compared) |", (n(rep["rows"]), rep["columns"])),
        ("| %s (%s of %s) |", (sc["coverage"], n(sc["hits"]), n(sc["disagree"]))),
        ("| %s (%s of %s) |", (sc["precision"], n(sc["hits"]), n(sc["sim_stale"]))),
        ("69338/LEAKY matches its %s record, 69372/KNOXS its %s record",
         (named["69338/LEAKY"]["matching_reports"][0], named["69372/KNOXS"]["matching_reports"][0])),
        ("over-predicts by %d generator-months (%s less %s)",
         (sc["sim_stale"] - sc["hits"], n(sc["sim_stale"]), n(sc["hits"]))),
        ("between %d and %d such generator-months, out of %s to %s generators",
         (min(m["predicted"] for m in months), max(m["predicted"] for m in months),
          n(min(m["units"] for m in months)), n(max(m["units"] for m in months)))),
        ("status in %s generator-months, MW in %d and planned month in %d. In %s of them",
         (n(by_field["status"]), by_field["MW"], by_field["planned month"], n(op_out))),
        ("(%s MW together) are operating in EIA's August 2026 workbook and have disagreed with PUDL in every "
         "month since %s; PUDL's record in force, which shows them retired, was reported in %s.",
         (mw(sum(r["workbook_mw"] for r in ex[0])), month_name(ex[0][0]["differs_since"]),
          month_name(ex[0][0]["pudl_reported"]))),
        ("(%s MW together) are operating in EIA's August 2026 workbook and have disagreed with PUDL since %s; "
         "PUDL's record in force, which shows them out of service (OS), was reported in %s.",
         (mw(sum(r["workbook_mw"] for r in ex[1])), month_name(ex[1][0]["differs_since"]),
          month_name(ex[1][0]["pudl_reported"]))),
        ("6481/1 and 6481/2 (%s MW each)", (mw(t.aug["6481/1"]["workbook_mw"]),)),
        ("%d generators on the August 2026 workbook's Retired sheet (%s MW)",
         (res["august_workbook_only"], "{:,.1f}".format(gone_mw))),
        ("passed (%s) |", (pudl["max_report"],)),
    ]


if __name__ == "__main__":
    unittest.main()
