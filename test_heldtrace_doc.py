"""Checks the numbers in docs/heldtrace.md (descriptive follow-up to the twenty-ninth result,
22 October 2026) against the raw output of compete job heldtrace-v2 (data/heldtrace_v2.json,
data/heldtrace_pudl_rows.csv, docs/heldtrace-v2-output.md, docs/heldtrace-v2-unittests.txt),
history-v1's yearly counts (data/history_v1_years.csv), the status line of
docs/history-revert.md and, for the dated updates, compete jobs keptreturn-v1
(data/keptreturn_v1.json, docs/keptreturn-v1-output.md, docs/keptreturn-v1-unittests.txt),
retiredgap-v1 (data/retiredgap_v1.json, docs/retiredgap-v1-output.md,
docs/retiredgap-v1-unittests.txt), gapcensus-v1 (data/gapcensus_v1.json,
data/gapcensus_left_events.csv, docs/gapcensus-v1-output.md, docs/gapcensus-v1-unittests.txt)
and retiredscope-v1 (data/retiredscope_v1.json, data/retiredscope_leavers.csv,
data/retiredscope_2017_03_left.csv, docs/retiredscope-v1-output.md,
docs/retiredscope-v1-unittests.txt), whose dated lines in
docs/eia860m-changelog-from-workbooks.md are checked too.
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
KR_COLUMNS = ("winter_capacity_mw", "utility_name_eia", "summer_capacity_mw")
KR_SETS = ("summer_capacity_mw+winter_capacity_mw", "utility_name_eia", "longitude",
           "utility_id_eia+utility_name_eia")
KR_LONGITUDE = ("3075/11", "3082/2", "3925/1")
OLMSTEAD = "3655/1"
RG_MONTHS = ("2024-10", "2024-11", "2024-12")
RG_STATES = {"ME": "Maine", "CA": "California", "TX": "Texas"}
RG_RECENT = ("2011", "2012", "2013", "2014")
GC_DATASET = "e4ecb0d748bf7dc4738c27811e5fc07775eb72a3"
GC_LATER, GC_GONE = "67691/731", ("59806/SOLAR", "67190/FBESS")
GC_SCOPE, GC_PLANT = "2017-03", ("2024-01", "1439")
RS_COMPARE = ("2017-02", "2017-03", "2023-12", "2024-01")
RS_STATES = {"LA": "Louisiana", "MD": "Maryland", "IL": "Illinois"}
RS_PLANT, RS_COAL, RS_IL = "1439", ("1571", "1572"), "955"
RS_CP, RS_RENAMED = "63740/ONT6", "7922/6"


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


def tally(entries):
    return {x["value"]: x["n"] for x in entries}


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
        cls.kr = json.loads(read("data", "keptreturn_v1.json"))
        cls.krout = read("docs", "keptreturn-v1-output.md")
        cls.krlog = read("docs", "keptreturn-v1-unittests.txt")
        cls.rg = json.loads(read("data", "retiredgap_v1.json"))
        cls.rgout = read("docs", "retiredgap-v1-output.md")
        cls.rglog = read("docs", "retiredgap-v1-unittests.txt")
        cls.dataset = read("docs", "eia860m-changelog-from-workbooks.md")
        cls.gap = cls.rg["gaps"]["archive"]
        cls.files = {f["month"]: f for f in cls.rg["files"]}
        cls.gc = json.loads(read("data", "gapcensus_v1.json"))
        cls.gcout = read("docs", "gapcensus-v1-output.md")
        cls.gclog = read("docs", "gapcensus-v1-unittests.txt")
        cls.gcleft = rows("data", "gapcensus_left_events.csv")
        cls.rs = json.loads(read("data", "retiredscope_v1.json"))
        cls.rsout = read("docs", "retiredscope-v1-output.md")
        cls.rslog = read("docs", "retiredscope-v1-unittests.txt")
        cls.rsleft = rows("data", "retiredscope_leavers.csv")
        cls.rs17 = rows("data", "retiredscope_2017_03_left.csv")

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

    def test_census_run(self):
        kr, res = self.kr, self.kr["result"]
        self.assertEqual((kr["pudl"]["bytes"], kr["pudl"]["max_report"]),
                         (self.raw["pudl"]["bytes"], self.raw["pudl"]["max_report"]))
        self.assertEqual(res["records"], kr["pudl"]["rows"])
        self.assertIn("Kept returns: %d (no differing column: %d; the generator's last record: %d)." % (
            res["returns"], res["no_diff"], res["last_record"]), self.krout)
        ran = int(re.search(r"Ran (\d+) tests", self.krlog).group(1))
        self.assertEqual(len(re.findall(r"(?:^| \.\.\. )ok$", self.krlog, re.M)), ran)
        self.assertTrue(self.krlog.rstrip().endswith("OK"))

    def test_census(self):
        res = self.kr["result"]
        self.assertEqual(res["no_diff"], 0)
        self.assertEqual(sum(y["n"] for y in res["years"]), res["returns"])
        self.assertEqual(tuple(x["value"] for x in res["columns"][:3]), KR_COLUMNS)
        self.assertEqual(tuple(x["value"] for x in res["sets"][:4]), KR_SETS)
        self.assertEqual(res["months"][0]["value"], "2026-01")
        years = {y["year"]: y["n"] for y in res["years"]}
        self.assertGreater(min(years["2025"], years["2026"]), max(v for y, v in years.items() if y < "2025"))

    def test_census_traced(self):
        ex = self.kr["result"]["examples"]
        for k in KR_LONGITUDE + (OLMSTEAD, GRANITE):
            self.assertEqual(len(ex[k]), 1, k)
        for k in KR_LONGITUDE:
            self.assertEqual(ex[k], ex[BONNEVILLE], k)
        self.assertEqual(ex[BONNEVILLE][0]["diff"], ["longitude"])
        self.assertEqual(ex[OLMSTEAD][0]["diff"], ["longitude"])
        self.assertEqual(ex[GRANITE][0]["diff"], ["summer_capacity_mw", "winter_capacity_mw"])
        self.assertEqual(self.trace(BONNEVILLE)["2017-04"]["pudl_reported"], ex[BONNEVILLE][0]["month"])
        self.assertEqual(self.trace(GRANITE)["2019-12"]["pudl_reported"], ex[GRANITE][0]["month"])
        old = [r for r in self.prows(BONNEVILLE) if r["report_date"] < "2017-03" and r["longitude"]]
        self.assertEqual(old[-1]["report_date"][:7], ex[BONNEVILLE][0]["earlier"])
        g = [r for r in self.prows(GRANITE) if r["report_date"][:7] == ex[GRANITE][0]["earlier"]]
        self.assertEqual(len(g), 1)
        self.assertEqual((g[0]["operational_status_code"], g[0]["summer_capacity_mw"], g[0]["winter_capacity_mw"]),
                         ("OA", "135.0", "135.0"))

    def test_gap_run(self):
        rg, g = self.rg, self.gap
        self.assertEqual(tuple(sorted(self.files)), RG_MONTHS)
        for f in self.files.values():
            self.assertIs(f["same_file"], True, f["month"])
            self.assertEqual(f["errors"], [], f["month"])
            self.assertEqual((f["archive_bytes"], f["archive_md5"]), (f["eia_bytes"], f["eia_md5"]))
            self.assertEqual(f["sheets"]["archive"], f["sheets"]["eia"])
        self.assertEqual(rg["gaps"]["archive"], rg["gaps"]["eia"])
        self.assertEqual(rg["archive_gap_in_eia_middle"], 0)
        self.assertEqual(g["left"], self.ev["2024-11"]["left"])
        self.assertEqual(len(g["back_keys"]), g["back"])
        self.assertIn("Of the archive's %d, listed in EIA's own 2024-11 file: 0." % g["back"], self.rgout)
        ran = int(re.search(r"Ran (\d+) tests", self.rglog).group(1))
        self.assertEqual(len(re.findall(r"(?:^| \.\.\. )ok$", self.rglog, re.M)), ran)
        self.assertTrue(self.rglog.rstrip().endswith("OK"))

    def test_gap_sheets(self):
        g = self.gap
        before, after, years = tally(g["sheet_before"]), tally(g["sheet_after"]), tally(g["retirement_year"])
        self.assertEqual(set(before), {"Retired", "Planned"})
        self.assertEqual(set(after), {"Retired", "Operating"})
        self.assertEqual(before["Retired"], after["Retired"])
        for t in (before, after, years):
            self.assertEqual(sum(t.values()), g["back"])
        self.assertEqual(years["-"], after["Operating"])
        self.assertEqual(sum(v for y, v in years.items() if y != "-"), after["Retired"])
        self.assertLessEqual(max(int(y) for y in years if y != "-"), 2014)

    def test_gapcensus_run(self):
        gc = self.gc
        pub, eia = gc["published"], gc["eia"]
        self.assertEqual(gc["months_unreadable"], [])
        self.assertEqual(len(gc["months"]), self.raw["months_read"])
        self.assertTrue(all(z["ok"] and z["md5_matches_page"] for z in gc["zips"]))
        self.assertIs(pub["same"], True)
        self.assertIsNone(pub["first_difference"])
        self.assertEqual(pub["lines_published"], pub["lines_rebuilt"])
        self.assertEqual(pub["lines_published"], gc["log_rows"] + 1)
        self.assertIn(GC_DATASET, pub["url"])
        self.assertEqual((eia["plan"], eia["month"], eia["month"]), ("compare", pub["through"], gc["months"][-1]))
        self.assertIs(eia["same_file"], True)
        self.assertEqual((eia["bytes"], eia["md5"]), (eia["archive_bytes"], eia["archive_md5"]))
        self.assertIn("Same text through %s: True." % pub["through"], self.gcout)
        ran = int(re.search(r"Ran (\d+) tests", self.gclog).group(1))
        self.assertEqual(len(re.findall(r"(?:^| \.\.\. )ok$", self.gclog, re.M)), ran)
        self.assertTrue(self.gclog.rstrip().endswith("OK"))

    def test_gapcensus_counts(self):
        res, left = self.gc["result"], self.gcleft
        by = res["by_sheet"]
        self.assertEqual(sum(r["left"] for r in by), len(left))
        for r in by:
            self.assertEqual(r["left"], sum(r[o] for o in ("back_1", "back_2_12", "back_13_plus", "not_back")))
            self.assertEqual(r["not_back"], sum(1 for x in left if x["sheet_before"] == r["sheet"]
                                                and x["outcome"] == "not_back"))
        gaps = res["gap_months"]
        total = sum(g["n"] for g in gaps)
        self.assertEqual(total, sum(r["back_1"] for r in by))
        self.assertEqual(total, sum(1 for x in left if x["outcome"] == "back_1"))
        self.assertEqual(res["pudl_counts"], {"in force": total})
        others = [g["n"] for g in gaps if g["month"] != "2024-11"]
        self.assertEqual(others.count(max(others)), 1)
        nov = res["nov"]
        self.assertEqual(nov["left"], self.ev["2024-11"]["left"])
        self.assertEqual(nov["outcomes"]["back_1"], self.gap["back"])
        self.assertEqual(nov["outcomes"].get("back_2_12"), 1)
        self.assertEqual([g["Retired"] for g in gaps if g["month"] == "2024-11"], [tally(self.gap["sheet_before"])["Retired"]])
        odd = set(nov["keys"]) - {r["key"] for r in nov["rows"] if r["report_month"] == "2024-12" and r["event"] == "back"}
        self.assertEqual(odd, {GC_LATER} | set(GC_GONE))
        self.assertEqual(len(odd), nov["left"] - nov["outcomes"]["back_1"])
        out = {x["key"]: x["outcome"] for x in left if x["month_left"] == "2024-11"}
        self.assertEqual((out[GC_LATER], out[GC_GONE[0]], out[GC_GONE[1]]), ("back_2_12", "not_back", "not_back"))
        later = [r["sheet"] for r in nov["rows"] if r["key"] == GC_LATER and r["event"] in ("first", "changed", "back")]
        gone = [r["sheet"] for r in nov["rows"] if r["key"] == GC_GONE[0] and r["event"] != "left"]
        self.assertEqual((set(later), set(gone)), ({"Planned"}, {"Planned"}))

    def test_retiredscope_run(self):
        rs, L = self.rs, self.rs["leavers"]
        self.assertTrue(all(f["errors"] == [] for f in rs["files"]))
        eia = [f for f in rs["files"] if f.get("eia_md5")]
        self.assertEqual(tuple(f["month"] for f in eia), RS_COMPARE)
        for f in eia:
            self.assertIs(f["same_file"], True, f["month"])
            self.assertEqual((f["eia_bytes"], f["eia_md5"]), (f["bytes"], f["md5"]))
        self.assertIn("Errors: none.", self.rsout)
        ran = int(re.search(r"Ran (\d+) tests", self.rslog).group(1))
        self.assertEqual(len(re.findall(r"(?:^| \.\.\. )ok$", self.rslog, re.M)), ran)
        self.assertTrue(self.rslog.rstrip().endswith("OK"))
        gone = {(x["month_left"], x["key"]) for x in self.gcleft if x["sheet_before"] == "Retired"
                and x["outcome"] == "not_back" and x["month_left"] != GC_SCOPE}
        self.assertEqual({(e["month"], e["key"]) for e in L}, gone)
        self.assertEqual(len(L), len(gone))
        self.assertEqual([(r["month_left"], r["key"]) for r in self.rsleft], [(e["month"], e["key"]) for e in L])
        self.assertTrue(all(e["consistent"] and e["sheet_before"] == "Retired" and not e["listed_after"] for e in L))
        scope = sum(1 for x in self.gcleft if x["sheet_before"] == "Retired" and x["outcome"] == "not_back"
                    and x["month_left"] == GC_SCOPE)
        self.assertEqual((len(self.rs17), rs["scope"]["left"]["n"]), (scope, scope))

    def test_retiredscope_scope(self):
        s = self.rs["scope"]
        feb, mar = tally(s["retired_bins"][0]), tally(s["retired_bins"][1])
        self.assertEqual(s["retired_rows"], s["retired_keys"])
        self.assertEqual(set(mar), {"2002 or later"})
        self.assertEqual(tally(s["left"]["bins"]), {"before 2002": s["left"]["n"]})
        self.assertEqual(feb["before 2002"], s["left"]["n"])
        self.assertEqual(tally(s["left_where"]), {"not listed": s["left"]["n"]})
        self.assertEqual(tally(s["entered"]["bins"]), {"2002 or later": s["entered"]["n"]})
        self.assertEqual(s["retired_keys"][1] - s["entered"]["n"] - s["moved_in"], feb["2002 or later"])
        self.assertEqual({r["where_listed_2017_03"] for r in self.rs17}, {"not listed"})
        self.assertTrue(all(int(r["retirement_year"]) < 2002 for r in self.rs17))
        for m in GC_SCOPE, RS_COMPARE[0]:
            self.assertTrue(self.rs["titles"][m][0].startswith("Inventory of Retired Generators as of"))

    def test_retiredscope_leavers(self):
        f = rs_facts(self)
        L = self.rs["leavers"]
        cp = [e for e in L if e["where_after"] != "not listed"]
        self.assertEqual([(e["key"], e["where_after"], e["technology"]) for e in cp],
                         [(RS_CP, "Canceled or Postponed", "Solar Photovoltaic")])
        self.assertEqual([e["key"] for e in L if e["new_at_plant"]], [RS_RENAMED])
        self.assertEqual(f["renamed"]["plant_keys"][1], 1)
        self.assertEqual(len(f["renamed"]["new_at_plant"]), 1)
        self.assertEqual([e["key"] for e in L if e["nameplate_mw"] is None], [e["key"] for e in f["plant"]])
        for g in ("plant", "coal", "il"):
            self.assertEqual(len({e["month"] for e in f[g]}), 1, g)
            self.assertEqual(len({e["state"] for e in f[g]}), 1, g)
        for g in ("plant", "coal"):
            self.assertEqual(len({e["technology"] for e in f[g]}), 1, g)
        self.assertEqual(len({(e["retirement_year"], e["retirement_month"]) for e in f["plant"]}), 1)
        self.assertEqual(len(f["coal_years"]), 2)
        self.assertEqual(len(f["coal"]), 5)
        self.assertGreater(f["coal_mw"], f["total"] / 2)
        self.assertEqual(sum(1 for e in f["coal"] if e["key"].startswith("1572/") and e["nameplate_mw"] == 196), 3)
        for e in f["rest"]:
            self.assertEqual(sum(1 for x in L if x["month"] == e["month"]), 1, e["key"])

    def test_stated_numbers(self):
        for s in [s % v for s, v in STATED(self) + KR_STATED(self) + RG_STATED(self) + GC_STATED(self)
                  + RS_STATED(self)]:
            self.assertIn(s, self.text, s)

    def test_dataset_line(self):
        for s in [s % v for s, v in RG_DATASET(self) + GC_DATASET_LINES(self) + RS_DATASET(self)]:
            self.assertIn(s, self.dataset, s)


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


def KR_STATED(t):
    kr, res = t.kr, t.kr["result"]
    ran = int(re.search(r"Ran (\d+) tests", t.krlog).group(1))
    cols = {x["value"]: x["n"] for x in res["columns"]}
    sets = {x["value"]: x["n"] for x in res["sets"]}
    years = {y["year"]: y["n"] for y in res["years"]}
    months = {x["value"]: x["n"] for x in res["months"]}
    ex = res["examples"]
    names = {r["plant_id_eia"]: r["plant_name_eia"] for r in t.pudl}
    b, o, g = ex[BONNEVILLE][0], ex[OLMSTEAD][0], ex[GRANITE][0]
    return [
        ("keptreturn.py` 0.1.0 (%d of %d unit tests passed first) on the same PUDL file", (ran, ran)),
        ('not the %s "held before" generator-months they lead to', (n(t.tot["held_before"]),)),
        ("**%d kept returns** in %s records of %s generators",
         (res["returns"], n(res["records"]), n(res["generators"]))),
        ("(%d with none)", (res["no_diff"],)),
        ("%d of them are the generator's last record in the table", (res["last_record"],)),
        ("Longitude differs in %d of the %d", (cols["longitude"], res["returns"])),
        ("The most common columns are winter capacity (%d), utility name (%d) and summer capacity (%d)",
         tuple(cols[c] for c in KR_COLUMNS)),
        ("The most common sets are summer and winter capacity together (%d), utility name alone (%d), "
         "longitude alone (%d) and utility ID and name together (%d)", tuple(sets[s] for s in KR_SETS)),
        ("%s 11 (3075/11), %s 2 (3082/2) and %s 1 (3925/1) each have one kept return, %s in %s, that differs "
         "from their %s record in longitude only",
         (names["3075"], names["3082"], names["3925"], b["status"], month_name(b["month"]),
          month_name(b["earlier"]))),
        ("%s 1 (3655/1) has one, %s in %s, also longitude only against %s",
         (names["3655"], o["status"], month_name(o["month"]), month_name(o["earlier"]))),
        ("%s 2 (6175/2) has one, %s in %s, that differs from its %s record in summer and winter capacity",
         (names["6175"], g["status"], month_name(g["month"]), month_name(g["earlier"]))),
        ("2025 and 2026 (to %s) hold %d and %d of the %d, more than any earlier year",
         (month_name(kr["pudl"]["max_report"]), years["2025"], years["2026"], res["returns"])),
        ("January 2026 alone holds %d, the most of any month", (months["2026-01"],)),
        ("2017 holds %d, April 2017 %d of them", (years["2017"], months["2017-04"])),
    ]


def rg_years(g):
    years = tally(g["retirement_year"])
    dated = [int(y) for y in years if y != "-"]
    return min(dated), max(dated), sum(years[y] for y in RG_RECENT), years


def RG_STATED(t):
    g, files = t.gap, t.files
    ran = int(re.search(r"Ran (\d+) tests", t.rglog).group(1))
    nov = files["2024-11"]
    retired = [[s["rows"] for s in files[m]["sheets"]["eia"] if s["sheet"] == "Retired"][0] for m in RG_MONTHS]
    before, after = tally(g["sheet_before"]), tally(g["sheet_after"])
    lo, hi, recent, years = rg_years(g)
    tech, states = g["technology"][:4], g["state"][:3]
    others = [m for m in t.ev if m != "2024-12"]
    most = max(others, key=lambda m: t.ev[m]["back"])
    return [
        ("In the other %d months of the rebuilt changelog, at most %d generators come back in a month (%s); "
         "December 2024 has %d", (len(others), t.ev[most]["back"], month_name(most), t.ev["2024-12"]["back"])),
        ("retiredgap.py` 0.1.0 (%d of %d unit tests passed first)", (ran, ran)),
        ("(November 2024: %s bytes, md5 %s)", (n(nov["eia_bytes"]), nov["eia_md5"])),
        ("**%d generators listed in October 2024 are not in November's file; %d are listed again in December.**",
         (g["left"], g["back"])),
        ("None of the %d is in EIA's own November file", (g["back"],)),
        ("The %d equals heldtrace-v2's count from the archive", (t.ev["2024-11"]["left"],)),
        ("On October's sheets, %d of the %d are Retired and %d Planned; on December's, %d Retired and %d Operating",
         (before["Retired"], g["back"], before["Planned"], after["Retired"], after["Operating"])),
        ("The Retired sheet has %s rows in October, %s in November and %s in December",
         tuple(n(x) for x in retired)),
        ("these %d retired between %d and %d, %d of them in 2011 to 2014 (2013: %d; 2014: %d); "
         "the %d operating ones have none",
         (after["Retired"], lo, hi, recent, years["2013"], years["2014"], years["-"])),
        ("**About %.1f GW.** The %d sum to %s MW of nameplate capacity",
         (g["mw"] / 1000.0, g["back"], "{:,.1f}".format(g["mw"]))),
        ("The most common technologies are %s (%d), %s (%d), %s (%d) and %s (%d)",
         tuple(x for e in tech for x in (e["value"].lower(), e["n"]))),
        ("the most common states are %s (%d), %s (%d) and %s (%d)",
         tuple(x for e in states for x in (RG_STATES[e["value"]], e["n"]))),
        ("what became of the other %d of the %d", (g["left"] - g["back"], g["left"])),
    ]


def RG_DATASET(t):
    g = t.gap
    before, after = tally(g["sheet_before"]), tally(g["sheet_after"])
    lo, hi, recent, years = rg_years(g)
    return [
        ("it lacks %d generators that EIA's October and December 2024 files list: %d retired between %d and %d "
         "and %d that went from planned to operating",
         (g["back"], after["Retired"], lo, hi, after["Operating"])),
        ("The other %d of the %d that left in November", (g["left"] - g["back"], g["left"])),
        ("(%s MW of nameplate capacity in December's rows)", ("{:,.1f}".format(g["mw"]),)),
    ]


def gc_facts(t):
    """The gapcensus-v1 numbers the update and the dataset line state, computed from its raw output."""
    gc, res = t.gc, t.gc["result"]
    by = {r["sheet"]: r for r in res["by_sheet"]}
    gaps = res["gap_months"]
    nov = res["nov"]
    nov_gap = [g for g in gaps if g["month"] == "2024-11"][0]
    other = max((g for g in gaps if g["month"] != "2024-11"), key=lambda g: g["n"])
    rws = nov["rows"]

    def of(key, event):
        return [r for r in rws if r["key"] == key and r["event"] == event]

    def last_mw(key):
        return [r["nameplate_mw"] for r in rws if r["key"] == key and r["nameplate_mw"] != ""][-1]

    back = of(GC_LATER, "back")[-1]["report_month"]
    again = [r["report_month"] for r in of(GC_LATER, "left") if r["report_month"] > back][0]
    op = [r["report_month"] for r in rws if r["key"] == GC_GONE[1] and r["sheet"] == "Operating"][0]
    gone = [x for x in t.gcleft if x["sheet_before"] == "Retired" and x["outcome"] == "not_back"]
    scope = sum(1 for x in gone if x["month_left"] == GC_SCOPE)
    plant = sum(1 for x in gone if x["month_left"] == GC_PLANT[0] and x["key"].split("/")[0] == GC_PLANT[1])
    return {"by": by, "gaps": gaps, "nov": nov, "nov_gap": nov_gap, "other": other, "back": back, "again": again,
            "op": op, "gone": gone, "scope": scope, "plant": plant, "last": month_name(gc["months"][-1]),
            "mw": {k: mw(last_mw(k)) for k in (GC_LATER,) + GC_GONE},
            "odd": nov["left"] - nov["outcomes"]["back_1"],
            "where": {x["where"]: x["n"] for x in nov["where"]}}


def GC_STATED(t):
    gc, res, f = t.gc, t.gc["result"], gc_facts(t)
    ran = int(re.search(r"Ran (\d+) tests", t.gclog).group(1))
    pub, eia, by, nov = gc["published"], gc["eia"], f["by"], f["nov"]
    ret = by["Retired"]
    return [
        ("gapcensus.py` 0.1.0 (%d of %d unit tests passed first) on the same %d monthly workbooks",
         (ran, ran, len(gc["months"]))),
        ("its text equals the published copy line for line: %s lines, %s rows",
         (n(pub["lines_published"]), n(gc["log_rows"]))),
        ("EIA's own %s file (%s bytes, md5 %s) is byte-identical to the archive's copy",
         (month_name(eia["month"]), n(eia["bytes"]), eia["md5"])),
        ("**%s times a generator left the workbook**: from the Operating sheet %s, Planned %s and Retired %s",
         (n(sum(r["left"] for r in by.values())), n(by["Operating"]["left"]), n(by["Planned"]["left"]),
          n(ret["left"]))),
        ("%s of them were not listed again by %s", (n(sum(r["not_back"] for r in by.values())), f["last"])),
        ("missing for exactly one month %d times, in %d different months",
         (sum(g["n"] for g in f["gaps"]), len(f["gaps"]))),
        ("November 2024 holds %d of them; no other month more than %d (%s)",
         (f["nov_gap"]["n"], f["other"]["n"], month_name(f["other"]["month"]))),
        ("In all %d, PUDL's changelog has a record in force", (res["pudl_counts"]["in force"],)),
        ("**The other %d of November 2024's %d.**", (f["odd"], nov["left"])),
        ("November's file lists %d of the %d on no sheet at all and %d on the Canceled or Postponed sheet",
         (f["where"]["not listed"], nov["left"], f["where"]["Canceled or Postponed"])),
        ("%s (%s MW, planned) was listed again in %s and left again in %s",
         (GC_LATER, f["mw"][GC_LATER], month_name(f["back"]), month_name(f["again"]))),
        ("%s (%s MW, planned) and %s (%s MW, operating in %s) were not listed again by %s",
         (GC_GONE[0], f["mw"][GC_GONE[0]], GC_GONE[1], f["mw"][GC_GONE[1]], month_name(f["op"]), f["last"])),
        ("A generator left the Retired sheet %d times: %d times it was back the next month (%d of them in "
         "December 2024) and %d times it was not listed again by %s",
         (ret["left"], ret["back_1"], f["nov_gap"]["Retired"], ret["not_back"], f["last"])),
        ("%d of those %d left in %s", (f["scope"], len(f["gone"]), month_name(GC_SCOPE))),
        ("The other %d left later, %d of them at one plant (%s) in %s",
         (len(f["gone"]) - f["scope"], f["plant"], GC_PLANT[1], month_name(GC_PLANT[0]))),
    ]


def GC_DATASET_LINES(t):
    f = gc_facts(t)
    return [
        ("Of the other %d, one was listed again in %s and %d were not listed again by %s",
         (f["odd"], month_name(f["back"]), f["odd"] - 1, f["last"])),
        ("No other month has more than %d generators missing for exactly one month", (f["other"]["n"],)),
        ("In %s, %d generators left the Retired sheet and were not listed again by %s",
         (month_name(GC_SCOPE), f["scope"], f["last"])),
    ]


def rs_facts(t):
    """The retiredscope-v1 numbers the update and the dataset line state, computed from its raw output."""
    s, L = t.rs["scope"], t.rs["leavers"]
    years = {int(x["value"]): x["n"] for x in s["left"]["years"]}
    plant = lambda e: e["key"].split("/")[0]
    groups = {"plant": [e for e in L if plant(e) == RS_PLANT], "coal": [e for e in L if plant(e) in RS_COAL],
              "il": [e for e in L if plant(e) == RS_IL]}
    grouped = {e["key"] for g in groups.values() for e in g}
    total = sum(float(e["nameplate_mw"]) for e in L if e["nameplate_mw"] is not None)
    return dict(groups, years=years, total=total, rest=[e for e in L if e["key"] not in grouped],
                feb=tally(s["retired_bins"][0]), ry=[e["retirement_year"] for e in L],
                renamed=[e for e in L if e["key"] == RS_RENAMED][0],
                cp=[e for e in L if e["key"] == RS_CP][0],
                coal_mw=sum(float(e["nameplate_mw"]) for e in groups["coal"]),
                coal_years=sorted({e["retirement_year"] for e in groups["coal"]}),
                il_years=[e["retirement_year"] for e in groups["il"]])


def RS_STATED(t):
    rs, s, L, f = t.rs, t.rs["scope"], t.rs["leavers"], rs_facts(t)
    ran = int(re.search(r"Ran (\d+) tests", t.rslog).group(1))
    years, feb, ry, e, cp = f["years"], f["feb"], f["ry"], f["renamed"], f["cp"]
    new = e["new_at_plant"][0]
    p, c, il = f["plant"][0], f["coal"][0], f["il"][0]
    return [
        ("retiredscope.py` 0.1.0 (%d of %d unit tests passed first)", (ran, ran)),
        ("on %d workbooks from the same archive", (len(rs["files"]),)),
        ("For %d of them (February and March 2017, December 2023 and January 2024) it also downloaded EIA's own "
         "file; each is byte-identical to the archive's copy", (sum(1 for x in rs["files"] if x.get("eia_md5")),)),
        ("February 2017's Retired sheet has %s generators, %d of them retired before 2002; March 2017's has %s, "
         "none retired before 2002", (n(s["retired_keys"][0]), feb["before 2002"], n(s["retired_keys"][1]))),
        ("The %d that left are exactly February's pre-2002 ones (retired %d to %d, %d of them in %d; %s MW)",
         (s["left"]["n"], min(years), max(years), years[max(years)], max(years), "{:,.1f}".format(s["left"]["mw"]))),
        ("In the same month %d generators retired in 2002 or later (%s MW) entered the Retired sheet from no sheet, "
         "and %d moved to it from another sheet; all %s of February's others are still on it",
         (s["entered"]["n"], "{:,.1f}".format(s["entered"]["mw"]), s["moved_in"],
          n(s["retired_keys"][1] - s["entered"]["n"] - s["moved_in"]))),
        ("**The %d later departures are inside that scope.** All %d retired in 2002 or later (%d to %d)",
         (len(L), len(L), min(ry), max(ry))),
        ("%d of them are on no sheet of that month's file; 1 (%s, a %s MW solar unit retired in %d) moved to the "
         "Canceled or Postponed sheet",
         (sum(1 for x in L if x["where_after"] == "not listed"), cp["key"], mw(cp["nameplate_mw"]),
          cp["retirement_year"])),
        ("They sum to %s MW of nameplate capacity on the sheet the month before (%d have no MW there)",
         ("{:,.1f}".format(f["total"]), sum(1 for x in L if x["nameplate_mw"] is None))),
        ("In %d of the %d, the plant has no generator in the later month that it did not have the month before",
         (sum(1 for x in L if not x["new_at_plant"]), len(L))),
        ("The exception is %s (%s MW %s, retired %d, left %s): that month its plant's only listed generator is a "
         "new %s (%s, %s MW)",
         (e["key"], mw(e["nameplate_mw"]), e["technology"].lower(), e["retirement_year"], month_name(e["month"]),
          new["key"], new["sheet"], mw(new["nameplate_mw"]))),
        ("%d generators at plant %s (%ss, %s, retired %s by the sheet, no MW given) left in %s",
         (len(f["plant"]), RS_PLANT, p["technology"].lower(), RS_STATES[p["state"]],
          month_name("%d-%02d" % (p["retirement_year"], p["retirement_month"])), month_name(p["month"]))),
        ("%d at plants %s and %s (%s, %s, retired in %d and %d; %s MW) left in %s",
         (len(f["coal"]), RS_COAL[0], RS_COAL[1], c["technology"].lower(), RS_STATES[c["state"]],
          f["coal_years"][0], f["coal_years"][1], mw(f["coal_mw"]), month_name(c["month"]))),
        ("%d at plant %s (%s, retired %d to %d) left in %s",
         (len(f["il"]), RS_IL, RS_STATES[il["state"]], min(f["il_years"]), max(f["il_years"]),
          month_name(il["month"]))),
        ("The other %d left one at a time, in %d different months",
         (len(f["rest"]), len({x["month"] for x in f["rest"]}))),
        ("For %d of the %d, no generator of the plant is listed on the changelog's sheets in the month it left",
         (sum(1 for x in L if x["plant_keys"][1] == 0), len(L))),
        ("misses about %.2f GW, most of it five Maryland coal units", (f["total"] / 1000.0,)),
        ("Three %s MW units at plant %s", (mw(196), RS_COAL[1])),
    ]


def RS_DATASET(t):
    s, f, g = t.rs["scope"], rs_facts(t), gc_facts(t)
    return [
        ("All %d retired before 2002 (%d to %d)", (s["left"]["n"], min(f["years"]), max(f["years"]))),
        ("%d generators retired in 2002 or later left the Retired sheet after March 2017 and were not listed "
         "again by %s (%s MW on the sheet the month before; %d have no MW)",
         (len(t.rs["leavers"]), g["last"], "{:,.1f}".format(f["total"]),
          sum(1 for e in t.rs["leavers"] if e["nameplate_mw"] is None))),
    ]


if __name__ == "__main__":
    unittest.main()
