"""Checks the numbers in docs/entry-timing.md against the raw output of compete job entrytime-v1
(data/entrytime_v1.json, docs/entrytime-v1-output.md, docs/entrytime-v1-unittests.txt and
data/entrytime_sets.csv). MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Written 21 October 2026 with the note, after job entrytime-v1 had run, from test_stale_keys_doc.py.
The readings made after the run (the edge at the August report) are computed here from the pooled
rows the same way the note computed them."""

import csv
import io
import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
PREDICTIONS = ("P1", "P2", "P3", "P4", "P5")
SETS = ("A", "A_built", "B")
GROUPS = ("solar", "wind_onshore", "battery", "gas_ct", "gas_cc")
YEARS = tuple(range(2017, 2026))
POOLED = "2018-2025"
MONTHS = tuple("m%02d" % i for i in range(1, 13))
FEB_DEC = MONTHS[1:]
FEB_AUG = MONTHS[1:8]
SEP_DEC = MONTHS[8:]
MAR_JUN = ("m03", "m04", "m05", "m06")
BUCKETS = ("before",) + MONTHS + ("after", "unlisted")
SET_COLS = ["year", "set", "key", "group", "mw", "first_listed", "bucket"]
MONTH_COLS = ("Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
POOLED_TABLE = "First EIA-860M listing by report month, pooled 2018-2025, all technologies (MW)"
YEAR_TABLE = "March-June share by year, all technologies"
TECH_TABLE = "Pooled 2018-2025 by technology (description only)"
RAW_YEARS = "Every year and pooled, all groups (MW)"


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


def fmt(mw):
    return "{:,.1f}".format(mw)


def f4(x):
    return "n/a" if x is None else "%.4f" % x


def verdict(held):
    return {True: "held", False: "failed"}[held]


def total(row, cols):
    return sum(row[k] for k in cols)


def share(row, cols, of):
    return total(row, cols) / total(row, of)


class EntryTimingDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = read("docs", "entry-timing.md")
        cls.doc = tables(cls.text)
        cls.out = json.loads(read("data", "entrytime_v1.json"))
        cls.raw_text = read("docs", "entrytime-v1-output.md")
        cls.raw = tables(cls.raw_text)
        cls.log = read("docs", "entrytime-v1-unittests.txt")
        reader = csv.DictReader(io.StringIO(read("data", "entrytime_sets.csv")))
        cls.sets = list(reader)
        cls.set_cols = reader.fieldnames
        cls.rows = {(str(r["year"]), r["set"], r["group"]): r for r in cls.out["rows"]}
        cls.pooled = {s: cls.rows[(POOLED, s, "all")] for s in SETS}

    def table(self, head):
        self.assertIn(head, self.doc, head)
        return self.doc[head][0]

    def test_raw_output_is_consistent(self):
        """The job's sections agree with each other before any of them is quoted."""
        k, p = self.out["checks"], self.out["predictions"]
        self.assertEqual(k["all_pass"], bool(k["U1"]["pass"] and k["U2"]["pass"]
                                             and k["U3"]["pass"]))
        a, ab, b = (self.pooled[s] for s in SETS)
        self.assertEqual(p["P1"]["A_mar_jun_share"], a["mar_jun_share"])
        self.assertEqual(p["P2"]["A_mar_jun_share"], a["mar_jun_share"])
        self.assertEqual(p["P2"]["B_mar_jun_share"], b["mar_jun_share"])
        self.assertEqual(p["P4"]["A_built_mar_jun_share"], ab["mar_jun_share"])
        self.assertEqual(p["P4"]["B_mar_jun_share"], b["mar_jun_share"])
        self.assertEqual(p["P5"]["A_oct_dec_share"], a["oct_dec_share"])
        self.assertEqual(p["P3"]["years"], list(range(2018, 2026)))
        for y in YEARS:
            for s in SETS:
                self.assertIn((str(y), s, "all"), self.rows)
        # The shares are of the rows' February-December MW, and the buckets add up to the total
        # (each MW rounded to 0.1).
        for s in SETS:
            r = self.pooled[s]
            self.assertAlmostEqual(share(r, MAR_JUN, FEB_DEC), r["mar_jun_share"],
                                   delta=0.0000501, msg=s)
            self.assertAlmostEqual(total(r, BUCKETS), r["total_mw"],
                                   delta=0.05 * (len(BUCKETS) + 1), msg=s)

    def test_raw_md_matches_json(self):
        rows = [x for x in self.raw[RAW_YEARS][0] if x["group"] == "all"]
        self.assertEqual(len(rows), len(YEARS) * len(SETS) + len(SETS))
        for x in rows:
            r = self.rows[(x["year"], x["set"], "all")]
            self.assertAlmostEqual(float(x["mar_jun_share"]), r["mar_jun_share"],
                                   delta=0.0005 + 1e-9, msg=str(x))
            self.assertAlmostEqual(float(x["total_mw"]), r["total_mw"], delta=0.05, msg=str(x))

    def test_unit_tests(self):
        ran = int(re.search(r"Ran (\d+) tests", self.log).group(1))
        self.assertEqual(ran, 15)
        self.assertEqual(len(re.findall(r" \.\.\. ok$", self.log, re.M)), ran)
        self.assertTrue(self.log.rstrip().endswith("OK"))

    def test_checks(self):
        k = self.out["checks"]
        self.assertTrue(k["all_pass"])
        got = k["U1"]["got"]
        self.assertEqual(sorted(got), [str(y) for y in YEARS])
        g = got["2018"]
        ran = int(re.search(r"Ran (\d+) tests", self.log).group(1))
        expected = {
            "U1": "all %d years %s-%s match the twentieth result; 2018: A %s, A_built %s, B %s MW" % (
                len(got), min(got), max(got), fmt(g["A"]), fmt(g["A_built"]), fmt(g["B"])),
            "U2": "%d groups not adding up" % len(k["U2"]["groups_not_adding_up"]),
            "U3": "%d year-set rows over the limit" % len(k["U3"]["stray_mw"]),
            "unit tests": "%d of %d passed" % (ran, ran),
        }
        rows = {x["check"]: x["result"] for x in self.table("Checks (all passed)")}
        self.assertEqual(rows, expected)

    def test_predictions(self):
        p = self.out["predictions"]
        heads = [h for h in self.doc if h.startswith("Predictions")]
        self.assertEqual(len(heads), 1)
        rows = {x["prediction"]: x for x in self.table(heads[0])}
        self.assertEqual(sorted(rows), list(PREDICTIONS))
        held = {k: p[k]["held"] for k in PREDICTIONS}
        self.assertEqual({k: x["verdict"] for k, x in rows.items()},
                         {k: verdict(v) for k, v in held.items()})
        expected = {
            "P1": f4(p["P1"]["A_mar_jun_share"]),
            "P2": "%s vs %s (difference %s)" % (f4(p["P2"]["A_mar_jun_share"]),
                                                f4(p["P2"]["B_mar_jun_share"]),
                                                f4(p["P2"]["difference"])),
            "P3": "%d of %d years" % (len(p["P3"]["years_A_above_B"]), len(p["P3"]["years"])),
            "P4": "%s vs %s (difference %s)" % (f4(p["P4"]["A_built_mar_jun_share"]),
                                                f4(p["P4"]["B_mar_jun_share"]),
                                                f4(p["P4"]["difference"])),
            "P5": f4(p["P5"]["A_oct_dec_share"]),
        }
        self.assertEqual({k: x["result"] for k, x in rows.items()}, expected)
        self.assertIn("(%d of 5 held)" % sum(held.values()), heads[0])

    def test_status_line(self):
        n = sum(self.out["predictions"][k]["held"] for k in PREDICTIONS)
        self.assertTrue(self.out["checks"]["all_pass"])
        self.assertIn("All checks passed; %d of 5 predictions held." % n, self.text)
        self.assertIn("so this result does not separate the two", self.text)

    def test_pooled_table(self):
        rows = self.table(POOLED_TABLE)
        want = [(s,) + tuple(fmt(self.pooled[s][m]) for m in FEB_DEC)
                + (fmt(self.pooled[s]["after"]), fmt(self.pooled[s]["total_mw"])) for s in SETS]
        got = [(x["set"],) + tuple(x[c] for c in MONTH_COLS) + (x["after the year"], x["total"])
               for x in rows]
        self.assertEqual(got, want)
        # "No set has MW first listed before its year or in January, and none is unlisted"
        for s in SETS:
            self.assertEqual(total(self.pooled[s], ("before", "m01", "unlisted")), 0.0, s)

    def test_year_table(self):
        rows = self.table(YEAR_TABLE)
        raw = {(x["year"], x["set"]): x["mar_jun_share"] for x in self.raw[RAW_YEARS][0]
               if x["group"] == "all"}
        want = [(str(y) + (" (description only)" if y == 2017 else ""),)
                + tuple(raw[(str(y), s)] for s in SETS) for y in YEARS]
        got = [(x["year"],) + tuple(x[s] for s in SETS) for x in rows]
        self.assertEqual(got, want)

    def test_tech_table(self):
        rows = self.table(TECH_TABLE)

        def cells(g):
            out = ()
            for s in SETS:
                r = self.rows[(POOLED, s, g)]
                out += (fmt(r["total_mw"]), f4(r["mar_jun_share"]))
            return out

        want = [(g,) + cells(g) for g in GROUPS]
        got = [(x["group"], x["A MW"], x["A March-June"], x["A_built MW"], x["A_built March-June"],
                x["B MW"], x["B March-June"]) for x in rows]
        self.assertEqual(got, want)

    def test_sets_csv(self):
        """The generator list adds up to the job's rows, bucket by bucket (each MW rounded to 0.1)."""
        self.assertEqual(self.set_cols, SET_COLS)
        sums, counts = {}, {}
        for r in self.sets:
            self.assertIn(r["bucket"], BUCKETS)
            self.assertIn(r["set"], SETS)
            k = (r["year"], r["set"], r["bucket"])
            sums[k] = sums.get(k, 0.0) + float(r["mw"])
            counts[k] = counts.get(k, 0) + 1
        self.assertEqual({(y, s) for y, s, _ in sums}, {(str(y), s) for y in YEARS for s in SETS})
        for y in YEARS:
            for s in SETS:
                row = self.rows[(str(y), s, "all")]
                for b in BUCKETS:
                    k = (str(y), s, b)
                    self.assertAlmostEqual(sums.get(k, 0.0), row[b],
                                           delta=0.05 * counts.get(k, 0) + 0.05 + 1e-6, msg=str(k))

    def test_stated_numbers(self):
        for s in [s % v for s, v in STATED(self)]:
            self.assertIn(s, self.text, s)

    def test_prose_claims(self):
        """The prose's claims that are not single numbers."""
        a, ab, b = (self.pooled[s] for s in SETS)
        # "Its largest month is February"
        self.assertEqual(max(FEB_DEC, key=lambda m: a[m]), "m02")
        # "inside the 0.50-0.83 range its published quarters allowed"
        y17 = self.rows[("2017", "A", "all")]["mar_jun_share"]
        self.assertTrue(0.50 <= y17 <= 0.83)
        # "is slightly below it", "close to the 0.5714"
        within = share(a, MAR_JUN, FEB_AUG)
        self.assertLess(within, 4 / 7)
        self.assertLess(4 / 7 - within, 0.01)
        # "B is the mirror image"
        self.assertGreater(share(b, SEP_DEC, FEB_DEC), 0.5)
        self.assertGreater(share(a, FEB_AUG, FEB_DEC), 0.5)
        # "About half of B"
        self.assertAlmostEqual(b["after"] / b["total_mw"], 0.5, delta=0.05)
        # "Solar ... onshore wind ... follow the pooled pattern, and so do batteries"
        for g in ("solar", "wind_onshore", "battery"):
            ra, rb = self.rows[(POOLED, "A", g)], self.rows[(POOLED, "B", g)]
            self.assertGreater(ra["mar_jun_share"], rb["mar_jun_share"] + 0.10, g)
        # "Gas combustion turbines differ"
        self.assertGreater(self.rows[(POOLED, "B", "gas_ct")]["mar_jun_share"], 0.3)
        # "is in the annual plan ... drops ... at the edge"
        self.assertGreater(total(ab, FEB_AUG), total(b, FEB_AUG))
        self.assertLess(total(ab, SEP_DEC), total(b, SEP_DEC))


def STATED(t):
    """(format, values) for every number stated in the note's prose, computed from the raw
    output the same way the note computed them."""
    a, ab, b = (t.pooled[s] for s in SETS)
    p, meta = t.out["predictions"], t.out["meta"]
    y17 = t.rows[("2017", "A", "all")]

    def tech(s, g):
        return f4(t.rows[(POOLED, s, g)]["mar_jun_share"])

    def inplan(cols):
        return total(ab, cols) / (total(ab, cols) + total(b, cols))

    within = f4(share(a, MAR_JUN, FEB_AUG))
    return [
        ("(reports to %s)", (meta["report_max"],)),
        ("(report years %d-%d)", (meta["annual_report_years"][0], meta["annual_report_years"][-1])),
        ("(%s rows, one per generator, year and set)", ("{:,}".format(len(t.sets)),)),
        ("A holds %s MW", (fmt(a["total_mw"]),)),
        ("Of its February-December MW, %s was first listed in the March-June reports",
         (f4(p["P1"]["A_mar_jun_share"]),)),
        ("an even spread over the 11 months would give %s", ("%.3f" % (4 / 11),)),
        ("and %s in the October-December reports", (f4(p["P5"]["A_oct_dec_share"]),)),
        ("B's March-June share is %s, so A's exceeds it by %s (P2)",
         (f4(p["P2"]["B_mar_jun_share"]), f4(p["P2"]["difference"]))),
        ("above B's in %d of the %d years (P3)",
         (len(p["P3"]["years_A_above_B"]), len(p["P3"]["years"]))),
        ("A_built, built in the same year as B, has %s, %s above B's (P4)",
         (f4(p["P4"]["A_built_mar_jun_share"]), f4(p["P4"]["difference"]))),
        ("A's share is %s, inside the 0.50-0.83 range", (f4(y17["mar_jun_share"]),)),
        ("Its largest month is February (%s MW)", (fmt(a["m02"]),)),
        ("its March-June share of the February-August MW is %s", (within,)),
        ("close to the %s (4 of 7)", (f4(4 / 7),)),
        ("%s of A's February-December MW was first listed by the August report",
         (f4(share(a, FEB_AUG, FEB_DEC)),)),
        ("%s of its February-December MW was first listed in the September-December reports",
         (f4(share(b, SEP_DEC, FEB_DEC)),)),
        ("%s of the MW first listed in February-August is in the annual plan, against %s of the "
         "MW first listed in September-December", (f4(inplan(FEB_AUG)), f4(inplan(SEP_DEC)))),
        ("Against an even spread over February-August, %s, A's March-June share of its "
         "February-August MW, %s, is slightly below it", (f4(4 / 7), within)),
        ("drops from %s to %s at the edge", (f4(inplan(FEB_AUG)), f4(inplan(SEP_DEC)))),
        ("%s of B's MW (%s of %s MW) was first listed in a report after the year",
         (f4(b["after"] / b["total_mw"]), fmt(b["after"]), fmt(b["total_mw"]))),
        ("A has %s MW first listed after its year", (fmt(a["after"]),)),
        ("Solar (A %s, B %s) and onshore wind (A %s, B %s)",
         (tech("A", "solar"), tech("B", "solar"), tech("A", "wind_onshore"),
          tech("B", "wind_onshore"))),
        ("batteries (A %s, B %s)", (tech("A", "battery"), tech("B", "battery"))),
        ("B's March-June share is %s, from %s MW first listed in May reports, against A's %s",
         (tech("B", "gas_ct"), fmt(t.rows[(POOLED, "B", "gas_ct")]["m05"]), tech("A", "gas_ct"))),
        ("Gas combined cycle A (%s MW)", (fmt(t.rows[(POOLED, "A", "gas_cc")]["total_mw"]),)),
        ("does so by the August report (%s)", (f4(share(a, FEB_AUG, FEB_DEC)),)),
    ]


if __name__ == "__main__":
    unittest.main()
