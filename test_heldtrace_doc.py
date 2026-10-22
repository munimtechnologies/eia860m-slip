"""Checks the numbers in docs/heldtrace.md (descriptive follow-up to the twenty-ninth result,
22 October 2026) against the raw output of compete job heldtrace-v2 (data/heldtrace_v2.json,
data/heldtrace_pudl_rows.csv, docs/heldtrace-v2-output.md, docs/heldtrace-v2-unittests.txt),
history-v1's yearly counts (data/history_v1_years.csv) and the status line of
docs/history-revert.md.
MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import calendar
import csv
import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
STATUS = "Status: descriptive follow-up, no prediction tested."
KINDS = ("predicted", "pudl_later", "held_before", "other")
V1 = {"predicted": "hits", "pudl_later": "pudl_later", "held_before": "held_before", "other": "other"}
BONNEVILLE, GRANITE = "3075/11", "6175/2"
USACE = ("3082", "3075", "3925", "6175")
UTILITY = "USACE Northwestern Division"
STATE = {"OR": "Oregon", "WA": "Washington"}
TOP = 6


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8") as fh:
        return fh.read()


def rows(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def n(x):
    return "{:,}".format(x)


def mw(x):
    s = "{:,.1f}".format(float(x))
    return s[:-2] if s.endswith(".0") else s


def status(cell):
    return cell.split(", ")[0]


def cell_mw(cell):
    return cell.split(", ")[2].split()[0]


def month_name(m):
    return "%s %s" % (calendar.month_name[int(m[5:7])], m[:4])


class HeldtraceDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = read("docs", "heldtrace.md")
        cls.raw = json.loads(read("data", "heldtrace_v2.json"))
        cls.res = cls.raw["result"]
        cls.out = read("docs", "heldtrace-v2-output.md")
        cls.log = read("docs", "heldtrace-v2-unittests.txt")
        cls.pudl = rows("data", "heldtrace_pudl_rows.csv")
        cls.v1 = {int(r["year"]): r for r in rows("data", "history_v1_years.csv")}
        cls.revert = read("docs", "history-revert.md")
        cls.kinds = {y["year"]: y for y in cls.res["kinds"]}
        cls.tot = {k: sum(y[k] for y in cls.res["kinds"]) for k in KINDS}
        cls.ev = {e["month"]: e for e in cls.res["events"]}

    def prows(self, key):
        return [r for r in self.pudl if r["key"] == key]

    def trace(self, key):
        return {x["month"]: x for x in self.res["keys"][key]}

    def test_status_line(self):
        self.assertTrue(self.text.splitlines()[2].startswith(STATUS))
        self.assertTrue(self.revert.splitlines()[2].startswith("Status: scored against its pre-registration"))

    def test_run(self):
        raw = self.raw
        self.assertEqual(raw["months_unreadable"], [])
        self.assertTrue(all(z["ok"] and z["md5_matches_page"] for z in raw["zips"]))
        self.assertIn("Workbook months read: %d." % raw["months_read"], self.out)
        ran = int(re.search(r"Ran (\d+) tests", self.log).group(1))
        self.assertEqual(len(re.findall(r" \.\.\. ok$", self.log, re.M)), ran)
        self.assertTrue(self.log.rstrip().endswith("OK"))

    def test_kinds_equal_history_v1(self):
        self.assertEqual(sorted(self.kinds), sorted(self.v1))
        for yr, y in self.kinds.items():
            for k in KINDS:
                self.assertEqual(y[k], int(self.v1[yr][V1[k]]), (yr, k))
            self.assertEqual(sum(y[k] for k in KINDS), int(self.v1[yr]["disagree"]), yr)

    def test_where_all_same(self):
        where = self.res["where"]
        self.assertTrue(all(x["at"] == "same" for x in where))
        self.assertEqual(sum(x["n"] for x in where), sum(self.tot.values()))
        for yr, y in self.kinds.items():
            for k in KINDS:
                self.assertEqual(sum(x["n"] for x in where if x["year"] == yr and x["kind"] == k), y[k])

    def test_held(self):
        held = self.res["held"]
        self.assertEqual(sum(x["n"] for x in held), self.tot["held_before"])
        self.assertTrue(all(x["strict"] is True and x["at"] == "same" for x in held))
        self.assertEqual(sorted({x["simulated"] for x in held}), ["equals workbook", "stale elsewhere"])

    def test_plants(self):
        top = [p["plant"] for p in self.res["plants"][:TOP]]
        self.assertEqual(tuple(top[:4]), USACE)
        for p in USACE:
            r = [x for x in self.pudl if x["plant_id_eia"] == p]
            self.assertTrue(r, p)
            self.assertEqual({x["utility_name_eia"] for x in r}, {UTILITY})
            self.assertEqual({x["fuel_type_code_pudl"] for x in r}, {"hydro"})

    def test_bonneville(self):
        pr = self.prows(BONNEVILLE)
        old = [r for r in pr if r["report_date"] < "2017-03" and r["longitude"]]
        new = [r for r in pr if r["report_date"] >= "2017-03"]
        self.assertEqual(len({r["longitude"] for r in old}), 1)
        self.assertEqual(len({r["longitude"] for r in new}), 1)
        self.assertNotEqual(old[0]["longitude"], new[0]["longitude"])
        self.assertEqual([r["longitude"] for r in pr if r["report_date"] < old[0]["report_date"]],
                         [""] * (len(pr) - len(old) - len(new)))
        self.assertEqual([(r["report_date"][:7], r["operational_status_code"]) for r in new],
                         [("2017-03", "OP"), ("2017-04", "OA")])
        self.assertEqual(new[-1]["valid_until_date"][:7], self.raw["pudl"]["max_report"])
        t = self.trace(BONNEVILLE)
        a = t["2017-04"]
        self.assertEqual((status(a["workbook"]), status(a["simulated"]), status(a["pudl"]), a["pudl_reported"]),
                         ("OA", "OP", "OA", "2017-04"))
        self.assertTrue(all(x["workbook"].endswith(", - MW") for m, x in t.items() if m < "2016-04"))
        later = [x for m, x in t.items() if m >= "2017-08"]
        op = [x for x in later if status(x["workbook"]) == "OP"]
        self.assertTrue(all(x["result"] == "held_before" for x in op))
        self.assertEqual(len(op), sum(1 for x in t.values() if x["result"] == "held_before"))
        last = t[max(t)]
        self.assertEqual((max(t), last["pudl_reported"]), (self.raw["pudl"]["max_report"], "2017-04"))

    def test_granite(self):
        pr = self.prows(GRANITE)
        r18 = [r for r in pr if r["report_date"][:7] == "2018-03"][0]
        r19 = [r for r in pr if r["report_date"][:7] == "2019-12"][0]
        self.assertEqual(r18["operational_status_code"], "OP")
        self.assertEqual({r["summer_capacity_mw"] for r in pr if r["report_date"] < "2018-03"}, {"135.0"})
        self.assertEqual((r19["operational_status_code"], r19["summer_capacity_mw"]), ("OA", r18["summer_capacity_mw"]))
        self.assertEqual(pr[-1]["report_date"][:7], "2019-12")
        self.assertEqual(r19["capacity_mw"], "135.0")
        t = self.trace(GRANITE)
        self.assertEqual(t["2019-12"]["workbook"], t["2018-02"]["workbook"])
        self.assertEqual((status(t["2019-12"]["simulated"]), t["2019-12"]["pudl_reported"]), ("OP", "2019-12"))
        self.assertTrue(all(status(t[m]["workbook"]) == "OA" for m in t if "2019-12" <= m < "2021-01"))
        self.assertEqual(status(t["2021-01"]["workbook"]), "OP")
        self.assertEqual(t["2021-01"]["result"], "held_before")
        self.assertEqual(t[max(t)]["pudl_reported"], "2019-12")

    def test_events(self):
        y16 = [e for m, e in self.ev.items() if m[:4] == "2016"]
        self.assertEqual(max(e["changed"] for e in y16), self.ev["2016-04"]["changed"])
        t = self.trace(BONNEVILLE)
        self.assertEqual(cell_mw(t["2016-04"]["workbook"]), "66.5")

    def test_stated_numbers(self):
        for s in [s % v for s, v in STATED(self)]:
            self.assertIn(s, self.text, s)


def STATED(t):
    raw, res, tot = t.raw, t.res, t.tot
    pudl = raw["pudl"]
    ran = int(re.search(r"Ran (\d+) tests", t.log).group(1))
    held = res["held"]
    eq = sum(x["n"] for x in held if x["simulated"] == "equals workbook")
    stale = sum(x["n"] for x in held if x["simulated"] == "stale elsewhere")
    plants = res["plants"]
    names = {r["plant_id_eia"]: r["plant_name_eia"] for r in t.pudl}
    usace = sum(p["n"] for p in plants if p["plant"] in USACE)
    top = plants[:TOP]
    bon, gra = t.prows(BONNEVILLE), t.prows(GRANITE)
    bt, gt = t.trace(BONNEVILLE), t.trace(GRANITE)
    old = [r for r in bon if r["report_date"] < "2017-03" and r["longitude"]]
    new = [r for r in bon if r["report_date"] >= "2017-03"]
    later = [x for m, x in bt.items() if m >= "2017-08"]
    b_op = sum(1 for x in later if status(x["workbook"]) == "OP")
    b_held = sum(1 for x in bt.values() if x["result"] == "held_before")
    g_held = sum(1 for x in gt.values() if x["result"] == "held_before")
    g18 = [r for r in gra if r["report_date"][:7] == "2018-03"][0]
    g_old = [r for r in gra if r["report_date"] < "2018-03"][0]
    ev = t.ev
    m = re.search(r"(\d+) of (\d+) predictions held", t.revert.splitlines()[2])
    return [
        ("%s of %s predictions held and P5 stays failed", m.groups()),
        ("disagree on status, planned month or MW in %s generator-months", (n(sum(tot.values())),)),
        ("gives PUDL's value in %s of them", (n(tot["predicted"]),)),
        ("Of the rest, most (%s generator-months) are values PUDL held in an earlier record",
         (n(tot["held_before"]),)),
        ("(%d of %d unit tests passed first)", (ran, ran)),
        ("on the same %d monthly workbooks", (raw["months_read"],)),
        ("(%s bytes, file time %d %s, latest report %s)",
         (n(pudl["bytes"]), int(pudl["mtime"][8:10]), month_name(pudl["mtime"][:7]), pudl["max_report"])),
        ("equal history-v1's in all %d years (%s reproduced by the simulation, %d with the workbook's value "
         "in a later PUDL record, %s held before, %d other)",
         (len(t.kinds), n(tot["predicted"]), tot["pudl_later"], n(tot["held_before"]), tot["other"])),
        ("In all %s disagreeing generator-months", (n(sum(x["n"] for x in res["where"])),)),
        ('In all %s "held before" generator-months, an earlier PUDL record',
         (n(sum(x["n"] for x in held if x["strict"])),)),
        ("In %s of them the simulation holds the workbook's value itself", (n(eq),)),
        ("in %d it is stale at a third value", (stale,)),
        ("Two of the %d traced generators", (len(res["keys"]),)),
        ("(plant 3075, generator 11; %s MW hydro, %s)", (mw(bon[-1]["capacity_mw"]), STATE[bon[-1]["state"]])),
        ("PUDL's records from %s (the first with coordinates) to the one reported in %s give its longitude "
         "as %s; from %s on, %s.",
         (month_name(old[0]["report_date"][:7]), month_name(old[-1]["report_date"][:7]), old[0]["longitude"],
          month_name(new[0]["report_date"][:7]), new[0]["longitude"])),
        ("lists the unit as OP in %d of the %d months from August 2017 to August 2026", (b_op, len(later))),
        ('still in force at the latest report (%s): %d "held before" generator-months for this one unit',
         (pudl["max_report"], b_held)),
        ("(plant 6175, generator 2; %s MW hydro, %s)", (mw(gra[-1]["capacity_mw"]), STATE[gra[-1]["state"]])),
        ("PUDL's March 2018 record is OP with summer capacity %s MW; every earlier record gives %s MW",
         (mw(g18["summer_capacity_mw"]), mw(g_old["summer_capacity_mw"]))),
        ("OA with a %s MW summer rating was new", (mw(g18["summer_capacity_mw"]),)),
        ('as OP again from January 2021: %d "held before" generator-months', (g_held,)),
        ("%s (%s), %s (%s), %s (%s) and %s (%s), account for %d of the %s \"held before\" generator-months",
         tuple(x for p in USACE for x in (names[p], p)) + (usace, n(tot["held_before"]))),
        ("with plants %s and %s (%s), the top six account for %d",
         (top[4]["plant"], top[5]["plant"], names[top[5]["plant"]], sum(p["n"] for p in top))),
        ("April 2016 holds %s of 2016's %s \"changed\" rows",
         (n(ev["2016-04"]["changed"]), n(sum(e["changed"] for mm, e in ev.items() if mm[:4] == "2016")))),
        ("(Bonneville 11: %s MW)", (cell_mw(bt["2016-04"]["workbook"]),)),
        ("%d of 2024's %d \"back\" rows are in December 2024",
         (ev["2024-12"]["back"], sum(e["back"] for mm, e in ev.items() if mm[:4] == "2024"))),
        ("after %d generators left the November 2024 workbook", (ev["2024-11"]["left"],)),
    ]


if __name__ == "__main__":
    unittest.main()
