"""Checks the numbers in docs/er-plan.md against the raw output of compete job erplan-v1
(data/erplan_v1.json, docs/erplan-v1-output.md, docs/erplan-v1-unittests.txt and
data/erplan_rows.csv). MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

The first part was written 21 October 2026, before job erplan-v1 had run, from
test_entry_timing_doc.py: it tests the raw output against itself and against the rules of
erplan.py 0.1.0 (b73dc6a), so it does not depend on the result. The tests of the note's tables,
its prose claims and STATED() were added with the note, after the run."""

import csv
import io
import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
CLASSES = ("plan_y", "proposed_other", "operable", "retired", "absent")
SETS = ("A", "A_built", "B")
SPANS = ("all", "early", "mid", "late", "edge")
ROW_COLS = ["year", "set", "key", "group", "mw", "bucket", "span", "er", "final"]
EXPECTED_SETS = {"A": 55263.5, "A_built": 36998.4, "B": 32937.3}
EXPECTED_A_LATE = 13082.3
F1_MIN, F2_MIN, F3_MIN = 0.95, 0.90, 0.95
P1_MIN, P3_MAX, R2_MAX = 0.70, 0.20, 0.30
YEAR_MIN_MW = 100.0
TOP = 15
UNIT_TESTS = 22
PREDICTIONS = ("P1", "P2", "P3")
TABLES_HEAD = "Tables (all groups: erplan.json; every generator: erplan_rows.csv)"
TOP_HEAD = "Largest late A generators not in the early release's plan for Y"
SPAN_TABLE = "Set A by span of first EIA-860M listing, pooled 2022-2025"
YEAR_TABLE = "Share in the early release's plan for Y, set A, by year"
SPAN_REPORTS = (("early", "February-March"), ("mid", "April-June"), ("late", "July-August"),
                ("edge", "September-December or after Y"), ("all", "February-December or after Y"))
MW_DELTA = 0.05 + 1e-6      # each MW in the json is rounded to 0.1
SHARE_DELTA = 0.00005 + 1e-9  # each share in the json is rounded to 4 places


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


def mw(rows, field=None, classes=()):
    return sum(r["mw"] for r in rows if field is None or r[field] in classes)


def frac(rows, field, classes):
    tot = mw(rows)
    return mw(rows, field, classes) / tot if tot > 0 else None


def fmt(x):
    return "{:,.1f}".format(x)


def f4(x):
    return "n/a" if x is None else "%.4f" % x


def verdict(held):
    return {True: "held", False: "failed"}[held]


def reading(late):
    """erplan.reading(), copied: the outcome map's words for A late's share."""
    if late is None:
        return "no data"
    if late >= P1_MIN:
        return "most late entrants were in the early release (R1 for most)"
    if late <= R2_MAX:
        return "most late entrants were not in the early release's plan (R2 for most)"
    return "mixed"


class ErPlanDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = read("docs", "er-plan.md")
        cls.doc = tables(cls.text)
        cls.out = json.loads(read("data", "erplan_v1.json"))
        cls.raw_text = read("docs", "erplan-v1-output.md")
        cls.raw = tables(cls.raw_text)
        cls.log = read("docs", "erplan-v1-unittests.txt")
        reader = csv.DictReader(io.StringIO(read("data", "erplan_rows.csv")))
        cls.rows = list(reader)
        cls.row_cols = reader.fieldnames
        for r in cls.rows:
            r["year"], r["mw"] = int(r["year"]), float(r["mw"])
        cls.years = tuple(cls.out["meta"]["years"])
        cls.tab = {(str(r["year"]), r["set"], r["span"], r["group"]): r
                   for r in cls.out["tables"]}

    def pick(self, years, set_name, span="all", group="all"):
        return [r for r in self.rows if r["year"] in years and r["set"] == set_name
                and (span == "all" or r["span"] == span) and (group == "all" or r["group"] == group)]

    def a(self, span, year="pooled", set_name="A"):
        return self.tab[(str(year), set_name, span, "all")]

    def table(self, head):
        self.assertIn(head, self.doc, head)
        return self.doc[head][0]

    # ---- raw output, written before the run ----

    def test_rows_csv(self):
        self.assertEqual(self.row_cols, ROW_COLS)
        self.assertEqual({r["year"] for r in self.rows}, set(self.years))
        for r in self.rows:
            self.assertIn(r["set"], SETS)
            self.assertIn(r["span"], SPANS[1:] + ("other",))
            self.assertIn(r["er"], CLASSES)
            self.assertIn(r["final"], CLASSES)

    def test_tables_match_rows(self):
        """Every table row adds up from the generator list, and no row with MW is missing."""
        groups = ("all",) + tuple(sorted({r["group"] for r in self.rows}))
        want = set()
        for s in SETS:
            for sp in SPANS:
                for g in groups:
                    for y in ("pooled",) + self.years:
                        ys = self.years if y == "pooled" else (y,)
                        if mw(self.pick(ys, s, sp, g)) > 0:
                            want.add((str(y), s, sp, g))
        self.assertEqual(set(self.tab), want)
        self.assertEqual(len(self.tab), len(self.out["tables"]))
        for k, r in self.tab.items():
            ys = self.years if k[0] == "pooled" else (int(k[0]),)
            rows = self.pick(ys, *k[1:])
            self.assertAlmostEqual(mw(rows), r["mw"], delta=MW_DELTA, msg=str(k))
            for c in CLASSES:
                self.assertAlmostEqual(mw(rows, "er", (c,)), r["er_" + c], delta=MW_DELTA,
                                       msg="%s %s" % (k, c))
            self.assertAlmostEqual(frac(rows, "er", ("plan_y",)), r["er_plan_share"],
                                   delta=SHARE_DELTA, msg=str(k))
            self.assertAlmostEqual(frac(rows, "er", CLASSES[:4]), r["er_any_share"],
                                   delta=SHARE_DELTA, msg=str(k))
            self.assertAlmostEqual(frac(rows, "final", ("plan_y",)), r["final_plan_share"],
                                   delta=SHARE_DELTA, msg=str(k))

    def test_checks_follow_rules(self):
        k = self.out["checks"]
        c1 = k["C1"]
        ok = (all(abs(c1["got"][s] - v) <= 0.15 for s, v in EXPECTED_SETS.items())
              and abs(c1["a_late"] - EXPECTED_A_LATE) <= 0.15)
        self.assertEqual(c1["pass"], ok)
        f, a = k["F"], self.pick(self.years, "A")
        self.assertAlmostEqual(f["f1"], frac(a, "final", CLASSES[:4]), delta=1e-9)
        self.assertAlmostEqual(f["f2"], frac(a, "final", ("plan_y",)), delta=1e-9)
        self.assertEqual(f["f1_pass"], f["f1"] >= F1_MIN)
        self.assertEqual(f["f2_pass"], f["f2"] >= F2_MIN)
        self.assertEqual(sorted(k["F3"]), sorted(str(y) for y in self.years))
        self.assertEqual(k["F3_pass"], bool(k["F3"]) and all(
            v is not None and v >= F3_MIN for v in k["F3"].values()))
        self.assertEqual(k["scored"], bool(c1["pass"] and f["f1_pass"] and f["f2_pass"]
                                           and k["F3_pass"] and len(self.years) >= 3))

    def test_predictions_follow_rules(self):
        p = self.out["predictions"]
        late = frac(self.pick(self.years, "A", "late"), "er", ("plan_y",))
        early = frac(self.pick(self.years, "A", "early"), "er", ("plan_y",))
        self.assertAlmostEqual(p["late"], late, delta=SHARE_DELTA)
        self.assertAlmostEqual(p["early"], early, delta=SHARE_DELTA)
        self.assertEqual(p["late"], self.tab[("pooled", "A", "late", "all")]["er_plan_share"])
        self.assertEqual(p["early"], self.tab[("pooled", "A", "early", "all")]["er_plan_share"])
        by_year = {str(y): frac(self.pick((y,), "A", "late"), "er", ("plan_y",))
                   for y in self.years if mw(self.pick((y,), "A", "late")) >= YEAR_MIN_MW}
        self.assertEqual(sorted(p["late_by_year"]), sorted(by_year))
        for y, v in by_year.items():
            self.assertAlmostEqual(p["late_by_year"][y], v, delta=SHARE_DELTA, msg=y)
        n_ok = sum(1 for v in by_year.values() if v >= P1_MIN)
        self.assertEqual(p["years_ok"], n_ok)
        self.assertEqual(p["P1"], None if late is None else late >= P1_MIN)
        self.assertEqual(p["P2"], None if len(by_year) < 3 else n_ok >= 3)
        self.assertEqual(p["P3"], None if late is None or early is None
                         else early - late <= P3_MAX)
        self.assertEqual(p["reading"], reading(late))

    def test_top_list(self):
        want = sorted((r for r in self.rows if r["set"] == "A" and r["span"] == "late"
                       and r["er"] != "plan_y"), key=lambda r: (-r["mw"], r["key"]))[:TOP]
        got = self.out["top_late_not_in_er_plan"]

        def cells(rs):
            return [(r["year"], r["key"], r["mw"], r["er"], r["final"]) for r in rs]

        self.assertEqual(cells(got), cells(want))
        md = self.raw[TOP_HEAD][0] if self.raw.get(TOP_HEAD) else []
        self.assertEqual([(x["year"], x["key"], x["mw"]) for x in md],
                         [(str(r["year"]), r["key"], "%.1f" % r["mw"]) for r in got])

    def test_raw_md_matches_json(self):
        k, p = self.out["checks"], self.out["predictions"]
        self.assertIn("Plan years scored: %s. Scored: %s." % (list(self.years), k["scored"]),
                      self.raw_text)
        for line in ("- P1 (late >= %.2f): %s" % (P1_MIN, p["P1"]),
                     "- P3 (early - late <= %.2f): %s" % (P3_MAX, p["P3"]),
                     "- reading: %s" % p["reading"]):
            self.assertIn(line, self.raw_text)
        md = self.raw[TABLES_HEAD][0]
        want = [r for r in self.out["tables"] if r["group"] == "all"]
        self.assertEqual(len(md), len(want))
        for x, r in zip(md, want):
            self.assertEqual((x["year"], x["set"], x["span"], x["mw"]),
                             (str(r["year"]), r["set"], r["span"], "%.1f" % r["mw"]))
            for c in ("er_plan_share", "er_any_share", "final_plan_share"):
                self.assertEqual(x[c], "%s" % r[c], msg="%s %s" % (x, c))
            for c in CLASSES:
                self.assertEqual(x[c], "%.1f" % r["er_" + c], msg="%s %s" % (x, c))

    def test_unit_tests(self):
        ran = int(re.search(r"Ran (\d+) tests", self.log).group(1))
        self.assertEqual(ran, UNIT_TESTS)
        self.assertEqual(len(re.findall(r" \.\.\. ok$", self.log, re.M)), ran)
        self.assertTrue(self.log.rstrip().endswith("OK"))

    # ---- the note, written after the run ----

    def test_status_line(self):
        p = self.out["predictions"]
        n = sum(1 for k in PREDICTIONS if p[k])
        self.assertTrue(self.out["checks"]["scored"])
        self.assertIn("All checks passed; %d of 3 predictions held." % n, self.text)
        self.assertEqual(p["reading"], reading(p["late"]))
        self.assertIn("R2 for most", p["reading"])
        self.assertIn("On the terms fixed in advance that means R2 (revision) for most", self.text)

    def test_checks_table(self):
        k = self.out["checks"]
        c1, f = k["C1"], k["F"]
        ran = int(re.search(r"Ran (\d+) tests", self.log).group(1))
        expected = {
            "D1, D2, E1": "all %d copies passed; plan years %d-%d scored" % (
                2 * len(self.years), self.years[0], self.years[-1]),
            "C1": "A %s, A_built %s, B %s MW; A July-August %s MW" % (
                fmt(c1["got"]["A"]), fmt(c1["got"]["A_built"]), fmt(c1["got"]["B"]),
                fmt(c1["a_late"])),
            "F1": "%s (floor %.2f)" % (f4(f["f1"]), F1_MIN),
            "F2": "%s (floor %.2f)" % (f4(f["f2"]), F2_MIN),
            "F3": "%s (floor %.2f)" % (", ".join("%s %s" % (y, f4(k["F3"][y]))
                                                 for y in sorted(k["F3"])), F3_MIN),
            "unit tests": "%d of %d passed" % (ran, ran),
        }
        rows = {x["check"]: x["result"] for x in self.table("Checks (all passed)")}
        self.assertEqual(rows, expected)
        self.assertEqual(self.years, (2022, 2023, 2024, 2025))
        self.assertTrue(c1["pass"] and f["f1_pass"] and f["f2_pass"] and k["F3_pass"])

    def test_predictions_table(self):
        p = self.out["predictions"]
        heads = [h for h in self.doc if h.startswith("Predictions")]
        self.assertEqual(len(heads), 1)
        rows = {x["prediction"]: x for x in self.table(heads[0])}
        self.assertEqual(sorted(rows), list(PREDICTIONS))
        self.assertEqual({k: x["verdict"] for k, x in rows.items()},
                         {k: verdict(p[k]) for k in PREDICTIONS})
        expected = {
            "P1": f4(p["late"]),
            "P2": "%d of %d years" % (p["years_ok"], len(p["late_by_year"])),
            "P3": "%s - %s = %s" % (f4(p["early"]), f4(p["late"]), f4(p["early"] - p["late"])),
        }
        self.assertEqual({k: x["result"] for k, x in rows.items()}, expected)
        self.assertIn("(%d of 3 held)" % sum(1 for k in PREDICTIONS if p[k]), heads[0])

    def test_span_table(self):
        rows = self.table(SPAN_TABLE)
        want = []
        for sp, reports in SPAN_REPORTS:
            r = self.a(sp)
            want.append((sp, reports, fmt(r["mw"]), f4(r["er_plan_share"]),
                         f4(r["er_any_share"]), fmt(r["er_absent"]), f4(r["final_plan_share"])))
        got = [(x["span"], x["reports"], x["MW"], x["in the early release's plan for Y"],
                x["in the early release at all"], x["absent from the early release (MW)"],
                x["in the final release's plan for Y"]) for x in rows]
        self.assertEqual(got, want)

    def test_year_table(self):
        rows = self.table(YEAR_TABLE)
        want = [(str(y), f4(self.a("early", y)["er_plan_share"]),
                 f4(self.a("mid", y)["er_plan_share"]), f4(self.a("late", y)["er_plan_share"]),
                 fmt(self.a("late", y)["mw"]), f4(self.a("all", y)["er_plan_share"]))
                for y in self.years]
        got = [(x["year"], x["early"], x["mid"], x["late"], x["late MW"], x["all"]) for x in rows]
        self.assertEqual(got, want)

    def test_prose_claims(self):
        """The prose's claims that are not single numbers, checked on the generator list."""
        late = self.pick(self.years, "A", "late")
        # "none of it is in the early release on any sheet. That is so in every year"
        self.assertTrue(late)
        self.assertTrue(all(r["er"] == "absent" for r in late))
        # "and all of A late" (planned for Y by the final release)
        self.assertTrue(all(r["final"] == "plan_y" for r in late))
        # "all 4 years have at least 100 MW of A late"
        for y in self.years:
            self.assertGreaterEqual(mw(self.pick((y,), "A", "late")), YEAR_MIN_MW, y)
        # "No generator of A is on the early release's Operable or Retired and Canceled sheet."
        self.assertFalse([r for r in self.pick(self.years, "A")
                          if r["er"] in ("operable", "retired")])
        # "falls with the span", "follows the same order"
        for s in ("A", "A_built"):
            e, m, l = (self.a(sp, set_name=s)["er_plan_share"] for sp in ("early", "mid", "late"))
            self.assertTrue(e > m > l, s)
        # "from 0.1766 in 2022 to 0.8716 in 2025": the lowest and the highest year
        mids = {y: self.a("mid", y)["er_plan_share"] for y in self.years}
        self.assertEqual(min(mids, key=mids.get), 2022)
        self.assertEqual(max(mids, key=mids.get), 2025)
        # "came out 0.9977 in all four years"
        self.assertEqual(len(set(self.out["checks"]["F3"].values())), 1)
        self.assertEqual(len(self.out["checks"]["F3"]), 4)
        # "with the 15 largest late generators of A not in the early release's plan"
        self.assertEqual(len(self.out["top_late_not_in_er_plan"]), TOP)

    def test_stated_numbers(self):
        for s in [s % v for s, v in STATED(self)]:
            self.assertIn(s, self.text, s)


def STATED(t):
    """(format, values) for every number stated in the note's prose, computed from the raw
    output the same way the note computes them."""
    p, k = t.out["predictions"], t.out["checks"]
    early, mid, late, edge, every = (t.a(sp) for sp in ("early", "mid", "late", "edge", "all"))
    built = [f4(t.a(sp, set_name="A_built")["er_plan_share"]) for sp in ("early", "mid", "late")]
    f3 = sorted(set(k["F3"].values()))
    return [
        ("For plan years %d-%d it reads", (t.years[0], t.years[-1])),
        ("(%s rows, one per generator, year and set)", ("{:,}".format(len(t.rows)),)),
        ("A late holds %s MW", (fmt(late["mw"]),)),
        ("Its share in the early release's plan for Y is %s, against P1's floor of %.2f",
         (f4(p["late"]), P1_MIN)),
        ("all %d years have at least 100 MW of A late, and %d of %d reach 0.70 (P2)",
         (len(p["late_by_year"]), p["years_ok"], len(p["late_by_year"]))),
        ("A early, %s MW, is %s in the early release's plan for Y and %s in the early release "
         "on some sheet", (fmt(early["mw"]), f4(early["er_plan_share"]), f4(early["er_any_share"]))),
        ("so A early's share minus A late's is %s, against P3's ceiling of %.2f",
         (f4(p["early"] - p["late"]), P3_MAX)),
        ("The final release plans %s of A's MW for Y (check F2)", (f4(k["F"]["f2"]),)),
        ("under another year either (%s MW)", (fmt(late["er_proposed_other"]),)),
        ("%s for the February-March reports, %s for April-June (%s MW), %s for July-August, and "
         "%s for September-December or after Y (%s MW)",
         (f4(early["er_plan_share"]), f4(mid["er_plan_share"]), fmt(mid["mw"]),
          f4(late["er_plan_share"]), f4(edge["er_plan_share"]), fmt(edge["mw"]))),
        ("follows the same order: %s, %s and %s for the first three spans", tuple(built)),
        ("from %s in 2022 to %s in 2025", (f4(t.a("mid", 2022)["er_plan_share"]),
                                           f4(t.a("mid", 2025)["er_plan_share"]))),
        ("In 2023, %s MW of A early was on the early release's Proposed sheet",
         (fmt(t.a("early", 2023)["er_proposed_other"]),)),
        ("for set A it holds %s MW (of %s MW, %d-%d)",
         (fmt(every["er_absent"]), fmt(every["mw"]), t.years[0], t.years[-1])),
        ("came out %s in all four years", (f4(f3[0]),)),
        ("was found in them at %s", (f4(early["er_any_share"]),)),
    ]


if __name__ == "__main__":
    unittest.main()
