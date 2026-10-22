"""Checks the numbers in the late-night update of 22 October 2026 in docs/heldtrace.md (EIA's annual
EIA-860 and the 41 generators that left EIA-860M's Retired sheet) against the raw output of compete job
annual860-v1 (data/annual860_v1.json, data/annual860_leavers.csv, docs/annual860-v1-output.md,
docs/annual860-v1-unittests.txt), and the counts the pre-registration docs/annualids-plan.md starts from.
MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import calendar
import csv
import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
HEAD = "## Update, 22 October 2026 (late night): EIA's annual files do not keep the 41 either"
YEARS = (2020, 2021, 2022, 2023, 2024, 2025)
CP = "63740/ONT6"
COAL, IL, PLANT, LONE = ("1571", "1572"), "955", "1439", "55526/GEN5"
GONE = ("57692/ALSTO", "57693/ALSTO")
OPS = ("1571/ST1", "1571/ST2")
PAIR = ("7922/6", "59196/IC1")
SINGLE, RETRO = "64756/EQX05", "423/3A"
OFF = ("59196/IC1", "64756/EQX05", "423/3A")


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


def month_name(m):
    return "%s %s" % (calendar.month_name[int(m[5:7])], m[:4])


def tally(entries):
    return {x["value"]: x["n"] for x in entries}


def section(text):
    part = text.split(HEAD, 1)[1]
    return part.split("\n## ", 1)[0]


def code(where):
    return None if where == "not listed" else where.rsplit(" ", 1)[1]


def facts(an):
    """The leaver groups the update describes, computed from annual860-v1's rows."""
    L = an["leavers"]
    by = {e["key"]: {r["year"]: r for r in e["years"]} for e in L}
    never = [e["key"] for e in L if all(r["where"] == "not listed" for r in e["years"])]
    cn = [e["key"] for e in L if all(r["where"] == "Retired and Canceled CN" for r in e["years"])]
    dropped = {}
    for e in L:
        hits = [r["year"] for r in e["years"] if code(r["where"]) in ("OP", "RE")]
        if not hits or max(hits) >= YEARS[-1]:
            continue
        last = max(hits)
        if all(r["where"] == "not listed" for r in e["years"] if r["year"] > last):
            dropped[e["key"]] = {"first_missing": last + 1, "month": e["month"], "last": code(by[e["key"]][last]["where"]),
                                 "plant_listed": sum(by[e["key"]][last + 1]["plant"].values()) > 0}
    return {"by": by, "never": never, "cn": cn, "dropped": dropped, "keys": [e["key"] for e in L],
            "month": {e["key"]: e["month"] for e in L}}


class Annual860DocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.full = read("docs", "heldtrace.md")
        cls.text = section(cls.full)
        cls.an = json.loads(read("data", "annual860_v1.json"))
        cls.out = read("docs", "annual860-v1-output.md")
        cls.log = read("docs", "annual860-v1-unittests.txt")
        cls.csv = rows("data", "annual860_leavers.csv")
        cls.plan = read("docs", "annualids-plan.md")
        cls.f = facts(cls.an)
        cls.c8, cls.c12 = cls.an["census"]["2026-08"], cls.an["census"]["2025-12"]

    def test_section_is_last(self):
        self.assertEqual(self.full.count(HEAD), 1)
        self.assertNotIn("\n## ", self.full.split(HEAD, 1)[1])

    def test_run(self):
        ran = int(re.search(r"Ran (\d+) tests", self.log).group(1))
        self.assertEqual(len(re.findall(r" \.\.\. ok$", self.log, re.M)), ran)
        self.assertTrue(self.log.rstrip().endswith("OK"))
        files = self.an["files"]
        self.assertEqual(tuple(f["year"] for f in files), YEARS)
        for f in files:
            self.assertTrue(f["member"].startswith("3_1_Generator_Y%d" % f["year"]), f["year"])
            self.assertTrue(f["md5"] and f["bytes"], f["year"])
            if f["year"] == YEARS[-1]:
                self.assertEqual(f["errors"], [])
                self.assertNotIn("/archive/", f["url"])
            else:
                self.assertEqual(len(f["errors"]), 1, f["year"])
                self.assertIn("not an xlsx file", f["errors"][0])
                self.assertIn("/archive/xls/", f["url"])
        for m in self.an["monthly_files"]:
            self.assertEqual(m["errors"], [])
            self.assertIs(m["zip_md5_matches_page"], True)
        self.assertIn("## Census: annual 2025 against EIA-860M 2026-08", self.out)

    def test_census(self):
        c8, c12 = self.c8, self.c12
        a = c8["annual_retired"]["n"]
        self.assertEqual(tally(c8["annual_retired"]["bins"]), {"2002 or later": a})
        self.assertEqual(tally(c8["where_in_monthly"]), {"Retired": a})
        self.assertEqual((c8["both"], c8["same_year"], c8["not_in_monthly"]["n"]), (a, a, 0))
        self.assertEqual(tally(c8["monthly_not_annual_where"]), {"not listed": c8["monthly_not_annual"]})
        self.assertEqual(c8["monthly_retired_in_scope"], c8["both"] + c8["monthly_not_annual"])
        self.assertEqual(c12["annual_retired"]["n"], a)
        w12 = tally(c12["where_in_monthly"])
        self.assertEqual(set(w12), {"Retired", "Operating"})
        self.assertEqual(sum(w12.values()), a)

    def test_leavers(self):
        f, by, d = self.f, self.f["by"], self.f["dropped"]
        self.assertEqual(len(f["keys"]), 41)
        self.assertTrue(all("+" not in r["where"] for e in by.values() for r in e.values()))
        self.assertTrue(all(sorted(e) == list(YEARS) for e in by.values()))
        groups = [set(f["never"]), set(f["cn"]), set(d)]
        self.assertEqual(sum(len(g) for g in groups), len(f["keys"]))
        self.assertEqual(set.union(*groups), set(f["keys"]))
        self.assertEqual(f["cn"], [CP])
        self.assertEqual(set(f["never"]), {k for k in f["keys"] if k.startswith(PLANT + "/")} | {LONE} | set(GONE))
        self.assertEqual(set(d), {k for k in f["keys"] if k.split("/")[0] in COAL + (IL,)} | set(PAIR) |
                         {SINGLE, RETRO})
        for k, x in d.items():
            self.assertIn(int(x["month"][:4]) - x["first_missing"], (0, 1), k)
        for g in ([k for k in d if k.split("/")[0] in COAL], [k for k in d if k.split("/")[0] == IL], list(PAIR)):
            self.assertEqual(len({d[k]["first_missing"] for k in g}), 1, g)
        self.assertEqual(len({d[k]["month"] for k in d if k.split("/")[0] in COAL}), 1)
        self.assertEqual(len({d[k]["month"] for k in d if k.split("/")[0] == IL}), 1)
        self.assertEqual(d[PAIR[0]]["month"][:4], d[PAIR[1]]["month"][:4])
        self.assertEqual(sum(1 for k in f["keys"] if by[k][YEARS[-1]]["where"] == "not listed"), len(f["keys"]) - 1)
        self.assertEqual(by[CP][YEARS[-1]]["where"], "Retired and Canceled CN")
        self.assertEqual({k for k, x in d.items() if x["last"] == "OP"}, set(OPS))
        self.assertEqual({x["last"] for k, x in d.items() if k not in OPS}, {"RE"})
        self.assertEqual(tuple(k for k in f["keys"] if k in d and not d[k]["plant_listed"]), OFF)
        for k in OPS:
            self.assertEqual(by[k][YEARS[0]]["where"], "Operable OP")
            self.assertTrue(all(sum(by[k][y]["plant"].values()) > 0 for y in YEARS[1:]), k)
        plant = {tuple(sorted(by[k][y]["plant"].items())) for k in f["never"] if k.startswith(PLANT + "/")
                 for y in YEARS}
        self.assertEqual(len(plant), 1)
        self.assertEqual(dict(next(iter(plant)))["Proposed"], 0)
        self.assertTrue(all(by[LONE][y]["plant"] == by[LONE][YEARS[0]]["plant"] for y in YEARS))
        self.assertEqual((by[LONE][YEARS[0]]["plant"]["Operable"], by[LONE][YEARS[0]]["plant"]["Proposed"]), (0, 0))
        for k in GONE:
            self.assertTrue(all(sum(by[k][y]["plant"].values()) == 0 for y in YEARS), k)
        retro = [by[RETRO][y]["where"] for y in YEARS]
        self.assertEqual(retro, ["Operable OP"] * 4 + ["Retired and Canceled RE", "not listed"])

    def test_csv(self):
        self.assertEqual(len(self.csv), 41 * len(YEARS))
        for r in self.csv:
            self.assertEqual(r["where_annual"], self.f["by"][r["key"]][int(r["year"])]["where"])
            self.assertEqual(r["month_left"], self.f["month"][r["key"]])

    def test_stated_numbers(self):
        for s in [s % v for s, v in STATED(self)]:
            self.assertIn(s, self.text, s)

    def test_plan(self):
        self.assertTrue(self.plan.splitlines()[2].startswith("Status: pre-registered on 22 October 2026, before"))
        w12 = tally(self.c12["where_in_monthly"])
        for s in ("the %d annual-retired generators that EIA-860M's December 2025 file still listed as operating"
                  % w12["Operating"],
                  "the %s generators on the August 2026 monthly Retired sheet (retired 2002 to 2025)"
                  % n(self.c8["monthly_not_annual"])):
            self.assertIn(s, self.plan, s)


def STATED(t):
    f, an, c8, c12 = t.f, t.an, t.c8, t.c12
    by, d = f["by"], f["dropped"]
    ran = int(re.search(r"Ran (\d+) tests", t.log).group(1))
    files = an["files"]
    a = c8["annual_retired"]["n"]
    w12, w8 = tally(c12["where_in_monthly"]), tally(c8["where_in_monthly"])
    coal = [k for k in f["keys"] if k in d and k.split("/")[0] in COAL]
    il = [k for k in f["keys"] if k in d and k.split("/")[0] == IL]
    off = [k for k in f["keys"] if k in d and not d[k]["plant_listed"]]
    n1439 = [k for k in f["never"] if k.startswith(PLANT + "/")]
    p = by[n1439[0]][YEARS[0]]["plant"]
    lone = by[LONE][YEARS[0]]["plant"]
    ops_later = [by[OPS[0]][y]["plant"]["Operable"] for y in YEARS[1:]]
    retro = by[RETRO]
    r_op = [y for y in YEARS if retro[y]["where"] == "Operable OP"]
    r_re = [y for y in YEARS if retro[y]["where"] == "Retired and Canceled RE"]
    no25 = sum(1 for k in f["keys"] if by[k][YEARS[-1]]["where"] == "not listed")

    def m(k):
        return month_name(d[k]["month"])

    return [
        ("annual860.py` 0.1.0 (%d of %d unit tests passed first)", (ran, ran)),
        ("annual EIA-860 files for %d to %d from eia.gov", (files[0]["year"], files[-1]["year"])),
        ("for the %d earlier years EIA's current-data path returned a web page, so they came from its archive path",
         (sum(1 for x in files if x["errors"]),)),
        ("The %d file lists %s generators as retired in 2002 to %d (status RE; %s MW)",
         (an["census_year"], n(a), an["census_year"], mw(c8["annual_retired"]["mw"]))),
        ("All %s are on the August 2026 monthly Retired sheet, each with the same retirement year", (n(c8["same_year"]),)),
        ("That sheet lists %s generators, %s of them retired in 2002 to 2025; %s of those are on no sheet of the "
         "annual 2025 file", (n(c8["monthly_retired"]), n(c8["monthly_retired_in_scope"]), n(c8["monthly_not_annual"]))),
        ("The December 2025 monthly file lists %d of the %s on its Operating sheet and the other %s on its Retired sheet",
         (w12["Operating"], n(a), n(w12["Retired"]))),
        ("by August 2026 all %s are on the Retired sheet", (n(w8["Retired"]),)),
        ("%d are on no sheet of it. %s is on its Retired and Canceled sheet as canceled (CN), as in every annual file "
         "from %d on", (no25, CP, YEARS[0])),
        ("the monthly file's move to the Canceled or Postponed sheet in %s", (month_name(f["month"][CP]),)),
        ("**For %d, the annual files dropped them in the same data year or the year before.**", (len(d),)),
        ("%d of the %d are listed as operable or retired (OP or RE) in at least one annual file from %d to %d",
         (len(d), len(f["keys"]), YEARS[0], YEARS[-2])),
        ("the %d at plants %s and %s (first missing from the %d file; left the monthly in %s)",
         (len(coal), COAL[0], COAL[1], d[coal[0]]["first_missing"], m(coal[0]))),
        ("%s and %s (%d file; %s and %s)",
         (PAIR[0], PAIR[1], d[PAIR[0]]["first_missing"], calendar.month_name[int(d[PAIR[0]]["month"][5:7])],
          m(PAIR[1]))),
        ("%s (%d file; %s)", (SINGLE, d[SINGLE]["first_missing"], m(SINGLE))),
        ("the %d at plant %s (%d file; %s)", (len(il), IL, d[il[0]]["first_missing"], m(il[0]))),
        ("and %s (%d file; %s)", (RETRO, d[RETRO]["first_missing"], m(RETRO))),
        ("For %d of the %d the plant is still listed in that first annual file without them; for the other %d (%s) "
         "the plant is on no sheet of it", (len(d) - len(off), len(d), len(off), ", ".join(off[:-1]) + " and " + off[-1])),
        ("%s is on the Operable sheet of the %d to %d files and on the Retired and Canceled sheet of the %d file, with "
         "retirement year %d", (RETRO, min(r_op), max(r_op), r_re[0], retro[r_re[0]]["retirement_year"])),
        ("%s and %s (%s MW each) are on the Operable sheet of the %d annual file and on no sheet from %d on",
         (OPS[0], OPS[1], mw(by[OPS[0]][YEARS[0]]["nameplate_mw"]), YEARS[0], YEARS[1])),
        ("(%d or %d operable generators)", (min(ops_later), max(ops_later))),
        ("The other %d of the %d were last listed as retired (RE)",
         (sum(1 for x in d.values() if x["last"] == "RE"), len(d))),
        ("**%d are never listed under their IDs from %d on.**", (len(f["never"]), YEARS[0])),
        ("The %d at plant %s, whose plant is in every annual file from %d to %d with %d generators on the Operable "
         "sheet and %d on the Retired and Canceled sheet under other IDs",
         (len(n1439), PLANT, YEARS[0], YEARS[-1], p["Operable"], p["Retired and Canceled"])),
        ("%s, whose plant's %d listed generators are all on the Retired and Canceled sheet",
         (LONE, lone["Retired and Canceled"])),
        ("%s and %s, whose plants are on no sheet of any of the %d files", (GONE[0], GONE[1], len(YEARS))),
        ("(%s more than the annual 2025 file for 2002 to 2025)", (n(c8["monthly_not_annual"]),)),
        ("the retirement years of the %d have not been tallied, and how many of the %s are at plants",
         (w12["Operating"], n(c8["monthly_not_annual"]))),
    ]


if __name__ == "__main__":
    unittest.main()
