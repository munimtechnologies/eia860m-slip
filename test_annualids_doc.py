"""Checks the numbers in docs/annualids.md (the scored annualids follow-up) against the raw output of compete
job annualids-v1 (data/annualids_v1.json, the data/annualids_*.csv files, docs/annualids-v1-output.md,
docs/annualids-v1-unittests.txt), its pre-registration docs/annualids-plan.md, and annual860-v1's census
(data/annual860_v1.json). MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import csv
import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
YEARS = tuple(range(2016, 2026))
MONTHS = ("2020-01", "2021-11", "2022-12", "2023-12", "2025-02", "2025-12", "2026-08")
FOCUS = ("1439", "55526", "1571", "1572", "955", "7922")
EXAMPLE = "10764/GEN1"
GONE955 = ("955/16", "955/17", "955/GT1", "955/HC1", "955/HC2", "955/HC3", "955/HC4")


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


def tally(entries):
    return {x["value"]: x["n"] for x in entries}


def joined(items):
    return ", ".join(items[:-1]) + " and " + items[-1]


class AnnualidsDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = read("docs", "annualids.md")
        cls.js = json.loads(read("data", "annualids_v1.json"))
        cls.out = read("docs", "annualids-v1-output.md")
        cls.log = read("docs", "annualids-v1-unittests.txt")
        cls.plan = read("docs", "annualids-plan.md")
        cls.a860 = json.loads(read("data", "annual860_v1.json"))
        cls.ex, cls.lo = cls.js["extra"], cls.js["late_operating"]
        cls.by = {e["key"]: {r["year"]: r for r in e["years"]} for e in cls.js["leavers"]}
        cls.F = cls.js["focus"]

    def keys(self, p, src, when, sheet=None):
        return {r["key"] for r in self.F[p][src][when] if sheet is None or r["sheet"] == sheet}

    def row(self, p, src, when, key):
        return [r for r in self.F[p][src][when] if r["key"] == key][0]

    def where(self, key, w):
        return [y for y in YEARS if self.by[key][y]["where"] == w]

    def test_status(self):
        lines = self.text.splitlines()
        self.assertTrue(lines[2].startswith("Status: scored against its pre-registration"))
        held = int(self.ex["p1"]["held"]) + int(self.lo["p2"]["held"])
        self.assertIn("%d of 2 predictions held." % held, lines[2])
        self.assertTrue(self.plan.splitlines()[2].startswith("Status: pre-registered on 22 October 2026, before"))
        self.assertIn("more than half are at plants the annual 2025 file lists on no sheet", self.plan)
        self.assertIn("more than half retired in 2025 by the annual file", self.plan)

    def test_run(self):
        ran = int(re.search(r"Ran (\d+) tests", self.log).group(1))
        self.assertEqual(len(re.findall(r" \.\.\. ok$", self.log, re.M)), ran)
        self.assertTrue(self.log.rstrip().endswith("OK"))
        files = self.js["files"]
        self.assertEqual(tuple(f["year"] for f in files), YEARS)
        for f in files:
            self.assertTrue(f["member"].startswith("3_1_Generator_Y%d" % f["year"]), f["year"])
            self.assertEqual([s["sheet"] for s in f["sheets"]], ["Operable", "Proposed", "Retired and Canceled"])
            if f["year"] == YEARS[-1]:
                self.assertEqual(f["errors"], [])
            else:
                self.assertEqual(len(f["errors"]), 1, f["year"])
                self.assertIn("/archive/xls/", f["url"])
        self.assertEqual(tuple(m["month"] for m in self.js["monthly_files"]), MONTHS)
        for m in self.js["monthly_files"]:
            self.assertEqual(m["errors"], [])
            self.assertIs(m["zip_md5_matches_page"], True)
        self.assertEqual(tuple(sorted(self.F)), tuple(sorted(FOCUS)))
        self.assertIn("P1 (more than half at plants the annual 2025 file lists on no sheet): 2703 of 2703; held.",
                      self.out)

    def test_census(self):
        ex, lo = self.ex, self.lo
        self.assertEqual(tally(ex["plant_listed"]), {"False": ex["n"]})
        self.assertEqual((ex["plant_not_listed"], ex["mw_plant_not_listed"], ex["years_plant_listed"]),
                         (ex["n"], ex["mw"], []))
        self.assertEqual(sum(tally(ex["last_year"]).values()), ex["n"])
        self.assertEqual(tally(ex["last_where"]),
                         {"-": tally(ex["last_year"])["-"], "Retired and Canceled RE": ex["n"] - tally(ex["last_year"])["-"]})
        self.assertEqual(len(ex["rows"]), ex["n"])
        self.assertEqual(len(rows("data", "annualids_extra.csv")), ex["n"])
        self.assertEqual(tally(lo["where_last"]), {"Retired": lo["n"]})
        self.assertEqual(sum(tally(lo["years"]).values()), lo["n"])
        self.assertEqual(sum(tally(lo["status"]).values()), lo["n"])
        self.assertEqual(len(rows("data", "annualids_late_operating.csv")), lo["n"])
        self.assertEqual(lo["n"] % 2, 0)
        c8 = self.a860["census"]["2026-08"]
        self.assertEqual((c8["same_year"], c8["monthly_not_annual"]), (c8["annual_retired"]["n"], ex["n"]))

    def test_leavers(self):
        by, w = self.by, self.where
        ab = [k for k in by if k.startswith("1439/")]
        self.assertEqual(len(by), 41)
        self.assertTrue(all(by[k][y]["where"] == "not listed" for k in ab for y in YEARS))
        self.assertEqual(w("55526/GEN5", "Operable OP"), [2016, 2017])
        self.assertEqual(w("55526/GEN5", "Retired and Canceled RE"), [2018])
        self.assertEqual(by["55526/GEN5"][2018]["retirement_year"], 2018)
        self.assertEqual(w("55526/GEN5", "not listed"), list(range(2019, 2026)))
        for y in range(2019, 2026):
            self.assertEqual(by["55526/GEN5"][y]["plant"], {"Operable": 0, "Proposed": 0, "Retired and Canceled": 5})
        self.assertEqual(w("57693/ALSTO", "Operable OP"), [2016, 2017])
        self.assertEqual(w("57693/ALSTO", "Retired and Canceled RE"), [2018, 2019])
        self.assertEqual({by["57693/ALSTO"][y]["retirement_year"] for y in (2018, 2019)}, {2018})
        self.assertEqual(w("57693/ALSTO", "not listed"), list(range(2020, 2026)))
        self.assertEqual(w("57692/ALSTO", "not listed"), list(YEARS))
        self.assertEqual(w("7922/6", "Operable OP"), [2016, 2017])
        self.assertEqual(w("7922/6", "Retired and Canceled RE"), [2018, 2019, 2020, 2021])
        self.assertEqual({by["7922/6"][y]["retirement_year"] for y in range(2018, 2022)}, {2011})
        for y in range(2022, 2026):
            self.assertEqual(self.keys("7922", "annual", str(y)), {"7922/7"})
            self.assertEqual(self.keys("7922", "annual", str(y), "Operable"), {"7922/7"})
        for m in ("2025-12", "2026-08"):
            self.assertEqual(self.keys("7922", "monthly", m, "Operating"), {"7922/7"})
        for k in ("1571/ST1", "1571/ST2"):
            self.assertEqual(w(k, "Operable OP"), list(range(2016, 2021)))
            self.assertEqual(w(k, "not listed"), list(range(2021, 2026)))
        for k in ("1572/2", "1572/3", "1572/ST1"):
            self.assertEqual(w(k, "Operable OP"), list(range(2016, 2020)))
            self.assertEqual(w(k, "Retired and Canceled RE"), [2020])
            self.assertEqual(by[k][2020]["retirement_year"], 2020)
            self.assertEqual(w(k, "not listed"), list(range(2021, 2026)))
        self.assertEqual(w("423/3A", "Operable OP"), list(range(2016, 2024)))
        self.assertEqual(w("423/3A", "Retired and Canceled RE"), [2024])
        self.assertEqual(by["423/3A"][2024]["retirement_year"], 2018)
        self.assertEqual(w("423/3A", "not listed"), [2025])

    def test_focus(self):
        ab = {k for k in self.by if k.startswith("1439/")}
        base = self.keys("1439", "annual", "2016")
        for y in YEARS:
            self.assertEqual(self.keys("1439", "annual", str(y)), base)
        ops = sorted(self.keys("1439", "annual", "2016", "Operable"))
        self.assertEqual(ops, ["1439/14", "1439/15", "1439/16"])
        ret = [r for r in self.F["1439"]["annual"]["2016"] if r["sheet"] == "Retired and Canceled"]
        self.assertEqual({r["key"] for r in ret}, {"1439/%d" % i for i in range(6, 13)})
        self.assertEqual({(r["status"], r["retirement_year"]) for r in ret}, {("RE", 2010)})
        self.assertEqual(self.keys("1439", "monthly", "2023-12"), base | ab)
        abrows = [r for r in self.F["1439"]["monthly"]["2023-12"] if r["key"] in ab]
        self.assertEqual({(r["sheet"], r["retirement_year"], r["nameplate_mw"]) for r in abrows},
                         {("Retired", 2023, None)})
        self.assertEqual(self.keys("1439", "monthly", "2025-12"), base)
        for y in range(2016, 2024):
            self.assertTrue(set(GONE955) <= self.keys("955", "annual", str(y), "Operable"), y)
        self.assertEqual(self.keys("955", "annual", "2023", "Operable") - self.keys("955", "annual", "2024"),
                         set(GONE955))
        for y in (2024, 2025):
            self.assertFalse(set(GONE955) & self.keys("955", "annual", str(y)), y)
        self.assertTrue(set(GONE955) <= self.keys("955", "monthly", "2025-02", "Operating"))
        for m in ("2025-12", "2026-08"):
            self.assertFalse(set(GONE955) & self.keys("955", "monthly", m), m)
        sgt = [y for y in YEARS if "1571/SGT1" in self.keys("1571", "annual", str(y))]
        self.assertEqual(sgt, [2016])
        gt1 = [y for y in YEARS if "1571/GT1" in self.keys("1571", "annual", str(y), "Operable")]
        self.assertEqual(gt1, [2016, 2017, 2018, 2019, 2020, 2023, 2024, 2025])
        self.assertEqual([y for y in YEARS if "1571/GT1" in self.keys("1571", "annual", str(y))], gt1)

    def test_stated_numbers(self):
        for s in [s % v for s, v in STATED(self)]:
            self.assertIn(s, self.text, s)


def STATED(t):
    ex, lo, by, F = t.ex, t.lo, t.by, t.F
    ran = int(re.search(r"Ran (\d+) tests", t.log).group(1))
    files = t.js["files"]
    a = t.a860["census"]["2026-08"]["annual_retired"]["n"]
    ly = tally(lo["years"])
    other = {int(y): c for y, c in ly.items() if y not in ("2024", "2025")}
    yp = sorted(ex["years_plant_not_listed"], key=lambda e: -e["n"])
    yrs = [int(e["value"]) for e in ex["years_plant_not_listed"]]
    last = tally(ex["last_year"])
    top = max((e for e in ex["last_year"] if e["value"] != "-"), key=lambda e: e["n"])
    tech = tally(ex["technology"])
    planned = [e for e in lo["planned_years"] if e["value"] != "-"]
    exm = [r for r in lo["rows"] if r["key"] == EXAMPLE][0]
    ab = [k for k in by if k.startswith("1439/")]
    ops = sorted((r for r in F["1439"]["annual"]["2016"] if r["sheet"] == "Operable"), key=lambda r: r["key"])
    ret = [r for r in F["1439"]["annual"]["2016"] if r["sheet"] == "Retired and Canceled"]
    gone = [t.row("955", "annual", "2023", k) for k in GONE955]
    held = lambda x: "held" if x else "failed"
    return [
        ("EIA-860M's August 2026 Retired sheet lists %s generators retired in 2002 to 2025 that the annual EIA-860 "
         "2025 file lists on no sheet (%s MW)", (n(ex["n"]), mw(ex["mw"]))),
        ("Every one of the %s is at a plant that the annual 2025 file lists on no sheet", (n(ex["plant_not_listed"]),)),
        ("all %s generators the annual 2025 file lists as retired in 2002 to 2025 are on the monthly Retired sheet "
         "with the same retirement year", (n(a),)),
        ("among them %d conventional steam coal generators", (tech["Conventional Steam Coal"],)),
        ("leaves out of the 2025 file (%s generators, %s MW) and finds no exception to it",
         (n(ex["plant_not_listed"]), mw(ex["mw_plant_not_listed"]))),
        ("Of the %d generators the annual 2025 file lists as retired that EIA-860M's December 2025 file still listed "
         "on its Operating sheet, %d retired in 2025 by the annual file and %d in 2024",
         (lo["n"], ly["2025"], ly["2024"])),
        ("The other %d retired from %d to %d by the annual file", (sum(other.values()), min(other), max(other))),
        ("By August 2026 the monthly file lists all %d on its Retired sheet", (tally(lo["where_last"])["Retired"],)),
        ("| P1 | more than half of the %s at plants the annual 2025 file lists on no sheet | %s of %s | %s |",
         (n(ex["n"]), n(ex["plant_not_listed"]), n(ex["n"]), held(ex["p1"]["held"]))),
        ("| P2 | more than half of the %d retired in 2025 by the annual file | %d of %d | %s |",
         (lo["n"], lo["in_census_year"], lo["n"], held(lo["p2"]["held"]))),
        ("half of %d is %d, and %d retired in 2025", (lo["n"], lo["n"] // 2, lo["in_census_year"])),
        ("(%d of %d unit tests passed first)", (ran, ran)),
        ("annual EIA-860 files for %d to %d from eia.gov", (files[0]["year"], files[-1]["year"])),
        ("for the %d years before 2025 EIA's current-data path returned a web page",
         (sum(1 for f in files if f["errors"]),)),
        ("It read the EIA-860M workbooks for %s from PUDL's archive",
         (joined([m["month"] for m in t.js["monthly_files"]]),)),
        ("every row at %s focus plants", ({6: "six"}[len(F)],)),
        ("Retirement years run from %d to %d (none in 2025); the most are %d (%d) and %d (%d)",
         (min(yrs), max(yrs), int(yp[0]["value"]), yp[0]["n"], int(yp[1]["value"]), yp[1]["n"])),
        ("%s of them are on no annual file from 2016 to 2024. The other %s were last listed on an annual Retired and "
         "Canceled sheet as retired (RE); the last year that lists them is %s for the most (%d)",
         (n(last["-"]), n(tally(ex["last_where"])["Retired and Canceled RE"]), top["value"], top["n"])),
        ("Technologies: %s.", (", ".join("%s %d" % (e["value"], e["n"]) for e in ex["technology"][:5]),)),
        ("%s MW in all. By the annual file: %d retired in 2025, %d in 2024, %d from %d to %d.",
         (mw(lo["mw"]), ly["2025"], ly["2024"], sum(other.values()), min(other), max(other))),
        ("Status on the December 2025 Operating sheet: %s.", (", ".join("%s %d" % (e["value"], e["n"])
                                                                         for e in lo["status"]),)),
        ("That sheet gives no planned retirement year for %d of them, %s for %d and %s for %d",
         (tally(lo["planned_years"])["-"], planned[0]["value"], planned[0]["n"], planned[1]["value"], planned[1]["n"])),
        ("Technologies: %s.", (", ".join("%s %d" % (e["value"], e["n"]) for e in lo["technology"][:3]),)),
        ("%s (%s, %s MW) is retired in %d by the annual 2025 file and on the December 2025 Operating sheet as %s",
         (EXAMPLE, exm["technology"], mw(exm["annual_mw"]), exm["annual_year"], exm["late_status"])),
        ("**Plant 1439 (%d of the %d).**", (len(ab), len(by))),
        ("lists any of the %d IDs with an A or B suffix", (len(ab),)),
        ("lists the same %d generators at the plant: %d on the Operable sheet (%s; %s MW) and %d retired in %d "
         "(1439/6 to 1439/12)",
         (len(ops) + len(ret), len(ops), joined([r["key"] for r in ops]), joined([mw(r["nameplate_mw"]) for r in ops]),
          len(ret), ret[0]["retirement_year"])),
        ("December 2023 file lists those %d and the %d, all %d retired in %d with no nameplate MW; its December 2025 "
         "file lists only the %d", (len(ops) + len(ret), len(ab), len(ab),
                                    t.row("1439", "monthly", "2023-12", ab[0])["retirement_year"], len(ops) + len(ret))),
        ("while the plant's other %d generators stay on the Retired and Canceled sheet",
         (by["55526/GEN5"][2025]["plant"]["Retired and Canceled"],)),
        ("only listed generator is 7922/7 (Operable, %s MW)", (mw(t.row("7922", "annual", "2022", "7922/7")["nameplate_mw"]),)),
        ("**1571/ST1 and 1571/ST2** (%s MW each)", (mw(by["1571/ST1"][2016]["nameplate_mw"]),)),
        ("**1572/2, 1572/3 and 1572/ST1** (%s MW each)", (mw(by["1572/ST1"][2016]["nameplate_mw"]),)),
        ("%d generators (955/16, 955/17, 955/GT1 and 955/HC1 to 955/HC4; %s MW)",
         (len(gone), mw(round(sum(r["nameplate_mw"] for r in gone), 1)))),
        ("1571/SGT1 (%s MW)", (mw(t.row("1571", "annual", "2016", "1571/SGT1")["nameplate_mw"]),)),
        ("1571/GT1 (%s MW)", (mw(t.row("1571", "annual", "2016", "1571/GT1")["nameplate_mw"]),)),
    ]


if __name__ == "__main__":
    unittest.main()
