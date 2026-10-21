"""Checks the Detail sections of docs/er-plan.md against the raw output of compete job
erdetail-v1 (data/erdetail_v1.json, docs/erdetail-v1-output.md, docs/erdetail-v1-unittests.txt),
and that output against erplan-v1's (data/erplan_v1.json) and the structure report's copy
dates (docs/erplan-structure-v1-output.md). MV2 of Munim, Inc. (made with AI agents).
Apache-2.0.

The raw-output tests check erdetail's numbers against each other and against erplan-v1's
tables, so they do not depend on what the note says; the note's tables, prose claims and
STATED() follow."""

import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
YEARS = (2022, 2023, 2024, 2025)
MONTHS = ("m02", "m03", "m04", "m05", "m06", "m07", "m08", "later")
MONTH_NAMES = ("February", "March", "April", "May", "June", "July", "August", "later")
SPAN_MONTHS = (("early", ("m02", "m03")), ("mid", ("m04", "m05", "m06")),
               ("late", ("m07", "m08")), ("edge", ("later",)))
PLANT_SPANS = ("all", "early", "mid", "late", "edge")
STEP = 0.50
SAMPLE = 20
UNIT_TESTS = 9
F3_HEAD = "Detail: counts behind check F3"
MONTH_HEAD = "Detail: set A's share in the early release's plan for Y, by report month of first listing"
PLANT_HEAD = "Detail: plants of A's generators absent from the early release, pooled 2022-2025"
MW_DELTA = 0.05 + 1e-6


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8") as fh:
        return fh.read()


def tables(text):
    """Map each '## ' heading to the tables under it, each a list of {column: cell} rows."""
    out, head, cols = {}, None, None
    for line in text.splitlines():
        if line.startswith("## "):
            head, cols = line[3:].strip(), None
            out[head] = []
        elif line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if cols is None:
                cols = cells
                out.setdefault(head, []).append([])
            elif not all(c and set(c) <= set("-:") for c in cells):
                out[head][-1].append(dict(zip(cols, cells)))
        else:
            cols = None
    return out


def fmt(x):
    return "{:,.1f}".format(x)


def f4(x):
    return "%.4f" % x


def first_below(months):
    """Index in MONTHS of the first month with capacity whose plan share is below STEP."""
    for i, m in enumerate(MONTHS):
        if m in months and months[m]["er_plan_share"] < STEP:
            return i
    return None


class ErPlanDetailDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = read("docs", "er-plan.md")
        cls.doc = tables(cls.text)
        cls.out = json.loads(read("data", "erdetail_v1.json"))
        cls.raw_text = read("docs", "erdetail-v1-output.md")
        cls.log = read("docs", "erdetail-v1-unittests.txt")
        cls.plan = json.loads(read("data", "erplan_v1.json"))
        cls.structure = read("docs", "erplan-structure-v1-output.md")
        cls.tab = {(str(r["year"]), r["set"], r["span"], r["group"]): r
                   for r in cls.plan["tables"]}
        cls.months = cls.out["months"]
        cls.steps = {s: {y: first_below(cls.months[s][str(y)]) for y in YEARS}
                     for s in ("A", "A_built")}

    def table(self, head):
        self.assertIn(head, self.doc, head)
        return self.doc[head][0]

    def er_dates(self):
        """{plan year: the early-release copy's archive date} from the structure report."""
        out = {}
        for line in self.structure.splitlines():
            for y in YEARS:
                if line.startswith("| %d-er |" % y):
                    cells = [c.strip() for c in line.strip().strip("|").split("|")]
                    out[y] = cells[2]
        return out

    # ---- raw output ----

    def test_years(self):
        self.assertEqual(tuple(self.out["years"]), YEARS)
        self.assertEqual(tuple(self.plan["meta"]["years"]), YEARS)

    def test_f3_counts(self):
        for y in YEARS:
            d = self.out["f3"][str(y)]
            self.assertEqual(d["found"] + d["missing"], d["final_operable"], y)
            self.assertAlmostEqual(d["share"], d["found"] / d["final_operable"], delta=1e-12)
            self.assertAlmostEqual(d["share"], self.plan["checks"]["F3"][str(y)], delta=0.00005)
            self.assertEqual(self.out["counts"][str(y)]["final"]["operable"], d["final_operable"])
            self.assertEqual(len(d["missing_sample"]), min(SAMPLE, d["missing"]))
            self.assertEqual(d["missing_sample"], sorted(d["missing_sample"]))

    def test_months_add_up_to_spans(self):
        """Set A's single months, recombined, give erplan-v1's span MW and plan shares."""
        for y in ("pooled",) + tuple(str(y) for y in YEARS):
            ms = self.months["A"][y]
            for span, parts in SPAN_MONTHS:
                have = [ms[m] for m in parts if m in ms]
                key = (y, "A", span, "all")
                if not have:
                    self.assertNotIn(key, self.tab)
                    continue
                tot = sum(d["mw"] for d in have)
                ref = self.tab[key]
                self.assertAlmostEqual(tot, ref["mw"], delta=0.25, msg=str(key))
                share = sum(d["mw"] * d["er_plan_share"] for d in have) / tot
                self.assertAlmostEqual(share, ref["er_plan_share"], delta=0.0003, msg=str(key))

    def test_plants(self):
        p = self.out["plants"]
        self.assertEqual(list(p), list(PLANT_SPANS))
        self.assertEqual(sum(p[s]["generators"] for s in PLANT_SPANS[1:]), p["all"]["generators"])
        self.assertAlmostEqual(sum(p[s]["absent_mw"] for s in PLANT_SPANS[1:]),
                               p["all"]["absent_mw"], delta=0.25)
        for s in PLANT_SPANS:
            d = p[s]
            self.assertAlmostEqual(d["absent_mw"], self.tab[("pooled", "A", s, "all")]["er_absent"],
                                   delta=MW_DELTA, msg=s)
            self.assertLessEqual(d["plant_in_er_mw"], d["absent_mw"])
            self.assertAlmostEqual(d["plant_in_er_share"], d["plant_in_er_mw"] / d["absent_mw"],
                                   delta=0.0002, msg=s)

    def test_raw_md_matches_json(self):
        for y in YEARS:
            d = self.out["f3"][str(y)]
            self.assertIn("| %d | %d | %d | %d | %s |" % (y, d["final_operable"], d["found"],
                                                          d["missing"], d["share"]), self.raw_text)
        for s, d in self.out["plants"].items():
            self.assertIn("| %s | %d | %.1f | %.1f | %s |" % (
                s, d["generators"], d["absent_mw"], d["plant_in_er_mw"], d["plant_in_er_share"]),
                self.raw_text)

    def test_unit_tests(self):
        ran = int(re.search(r"Ran (\d+) tests", self.log).group(1))
        self.assertEqual(ran, UNIT_TESTS)
        self.assertEqual(len(re.findall(r" \.\.\. ok$", self.log, re.M)), ran)
        self.assertTrue(self.log.rstrip().endswith("OK"))

    # ---- the note ----

    def test_f3_table(self):
        got = [(x["year"], x["final release Operable"], x["in the early release"], x["missing"],
                x["share"]) for x in self.table(F3_HEAD)]
        want = []
        for y in YEARS:
            d = self.out["f3"][str(y)]
            want.append((str(y), "{:,}".format(d["final_operable"]), "{:,}".format(d["found"]),
                         str(d["missing"]), "%.6f" % d["share"]))
        self.assertEqual(got, want)

    def test_month_table(self):
        rows = self.table(MONTH_HEAD)
        self.assertEqual([x["year"] for x in rows], ["pooled"] + [str(y) for y in YEARS])
        for x in rows:
            ms = self.months["A"][x["year"]]
            for m, name in zip(MONTHS, MONTH_NAMES):
                want = f4(ms[m]["er_plan_share"]) if m in ms else "-"
                self.assertEqual(x[name], want, "%s %s" % (x["year"], name))

    def test_plant_table(self):
        got = [(x["span"], x["generators"], x["absent MW"], x["MW at a plant in the early release"],
                x["share"]) for x in self.table(PLANT_HEAD)]
        p = self.out["plants"]
        want = [(s, str(p[s]["generators"]), fmt(p[s]["absent_mw"]), fmt(p[s]["plant_in_er_mw"]),
                 f4(p[s]["plant_in_er_share"])) for s in PLANT_SPANS]
        self.assertEqual(got, want)

    def test_prose_claims(self):
        f3 = [self.out["f3"][str(y)] for y in YEARS]
        # "The counts differ every year" ... "they agree only to four"
        self.assertEqual(len({d["missing"] for d in f3}), 4)
        self.assertEqual(len({d["final_operable"] for d in f3}), 4)
        self.assertEqual(len({f4(d["share"]) for d in f3}), 1)
        self.assertEqual(len({"%.6f" % d["share"] for d in f3}), 4)
        # "the first 20 missing generators of each year in text order"
        for d in f3:
            self.assertEqual(len(d["missing_sample"]), SAMPLE)
        # "0.0000 for July and August"
        pooled = self.months["A"]["pooled"]
        self.assertEqual(f4(pooled["m07"]["er_plan_share"]), f4(pooled["m08"]["er_plan_share"]))
        # "which is April in 2022, May in 2023 and 2024 and June in 2025"
        names = {y: MONTH_NAMES[i] for y, i in self.steps["A"].items()}
        self.assertEqual(names, {2022: "April", 2023: "May", 2024: "May", 2025: "June"})
        # "After that month no month reaches 0.50, except June 2022"
        late_high = [(y, m) for y in YEARS for i, m in enumerate(MONTHS)
                     if i > self.steps["A"][y] and m in self.months["A"][str(y)]
                     and self.months["A"][str(y)][m]["er_plan_share"] >= STEP]
        self.assertEqual(late_high, [(2022, "m06")])
        # "A_built's first month below 0.50 is the same as A's in each of the four years"
        self.assertEqual(self.steps["A_built"], self.steps["A"])
        # "in 2025 the cut-off came one report later than in 2023 and 2024"
        st = self.steps["A"]
        self.assertEqual(st[2025], st[2023] + 1)
        self.assertEqual(st[2025], st[2024] + 1)
        # "the 2022 copy, with the earliest cut-off, was archived latest in its year"
        dates = self.er_dates()
        self.assertEqual(sorted(dates), list(YEARS))
        self.assertEqual(min(st, key=lambda y: (st[y], y)), 2022)
        self.assertEqual([y for y in YEARS if st[y] == st[2022]], [2022])
        self.assertEqual(max(dates, key=lambda y: dates[y][5:]), 2022)
        # "rose from the early to the final release in every year"; plan_y "fell in 2022 ...
        # and rose in the other three years"
        for y in YEARS:
            c = self.out["counts"][str(y)]
            self.assertGreater(c["final"]["proposed_other"], c["er"]["proposed_other"], y)
            if y == 2022:
                self.assertLess(c["final"]["plan_y"], c["er"]["plan_y"])
            else:
                self.assertGreater(c["final"]["plan_y"], c["er"]["plan_y"], y)

    def test_stated_numbers(self):
        for s in [s % v for s, v in STATED(self)]:
            self.assertIn(s, self.text, s)


def STATED(t):
    """(format, values) for every number stated in the Detail prose, computed from the raw
    output the same way the note computes them."""
    f3 = [t.out["f3"][str(y)] for y in YEARS]
    pooled = t.months["A"]["pooled"]
    plants = t.out["plants"]
    before = [t.months["A"][str(y)][m]["er_plan_share"] for y in YEARS
              for i, m in enumerate(MONTHS) if i < t.steps["A"][y]]
    june = t.months["A"]["2022"]["m06"]
    dates = t.er_dates()
    counts = [t.out["counts"][str(y)] for y in YEARS]
    ran = int(re.search(r"Ran (\d+) tests", t.log).group(1))
    return [
        ("%d of %d unit tests passed", (ran, ran)),
        ("the early release lacks %d of the final release's %s Operable generators for 2022, "
         "%d of %s for 2023, %d of %s for 2024 and %d of %s for 2025",
         tuple(v for d in f3 for v in (d["missing"], "{:,}".format(d["final_operable"])))),
        ("To six decimals the shares are %s, %s, %s and %s",
         tuple("%.6f" % d["share"] for d in f3)),
        ("the first %d missing generators of each year", (SAMPLE,)),
        ("set A's share is %s for the February report, %s for March, %s for April, %s for May, "
         "%s for June and %s for July and August",
         tuple(f4(pooled[m]["er_plan_share"]) for m in MONTHS[:6])),
        ("the share is at least %s in every month before", (f4(min(before)),)),
        ("first month below %.2f, which is", (STEP,)),
        ("except June 2022 (%s MW, %s)", (fmt(june["mw"]), f4(june["er_plan_share"]))),
        ("(%s, %s, %s and %s)", tuple(dates[y] for y in YEARS)),
        ("Of A's %s MW absent from the early release (%d generators), %s MW (%s)",
         (fmt(plants["all"]["absent_mw"]), plants["all"]["generators"],
          fmt(plants["all"]["plant_in_er_mw"]), f4(plants["all"]["plant_in_er_share"]))),
        ("for July-August it is %s of %s MW (%s)",
         (fmt(plants["late"]["plant_in_er_mw"]), fmt(plants["late"]["absent_mw"]),
          f4(plants["late"]["plant_in_er_share"]))),
        ("(%s to %s for 2022, %s to %s for 2023, %s to %s for 2024, %s to %s for 2025)",
         tuple("{:,}".format(c[k]["proposed_other"]) for c in counts for k in ("er", "final"))),
        ("fell in 2022 (%s to %s)", ("{:,}".format(counts[0]["er"]["plan_y"]),
                                     "{:,}".format(counts[0]["final"]["plan_y"]))),
    ]


if __name__ == "__main__":
    unittest.main()
