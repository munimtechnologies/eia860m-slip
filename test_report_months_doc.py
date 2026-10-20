"""Checks the numbers in docs/report-months.md against the raw output of compete job monthsteps-v1
(data/monthsteps_v1.json and docs/monthsteps-v1-unittests.txt). MV2 of Munim, Inc. (made with AI
agents). Apache-2.0.

Written 20 October 2026 with the note, after the job had run; every number the note states is
computed here from the raw output the way the note computed it."""

import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
KINDS = ("backward", "backward_building", "forward", "exit_other", "to_operating")
WINDOW = (12, 1, 2, 3)
PREDICTIONS = ("W1", "W2", "W3", "W4")


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


def n(x):
    return "{:,}".format(x)


def f4(x):
    return "n/a" if x is None else "%.4f" % x


def verdict(held):
    return {True: "held", False: "failed"}[held]


class ReportMonthsDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = read("docs", "report-months.md")
        cls.doc = tables(cls.text)
        cls.out = json.loads(read("data", "monthsteps_v1.json"))
        cls.log = read("docs", "monthsteps-v1-unittests.txt")
        cls.cmp = {r["kind"]: r for r in cls.out["compare"]}
        cls.months = {r["month"]: r for r in cls.out["months"]}

    def table(self, head):
        self.assertIn(head, self.doc, head)
        return self.doc[head][0]

    def test_raw_output_is_consistent(self):
        """The month table adds up to the inside/outside comparison before either is quoted."""
        self.assertEqual(sorted(self.cmp), sorted(KINDS))
        self.assertEqual(sorted(self.months), list(range(1, 13)))
        for m, r in self.months.items():
            self.assertEqual(r["window"], "yes" if m in WINDOW else "no", m)
        for k in KINDS:
            inside = sum(r[k + "_n"] for m, r in self.months.items() if m in WINDOW)
            outside = sum(r[k + "_n"] for m, r in self.months.items() if m not in WINDOW)
            self.assertEqual((inside, outside), (self.cmp[k]["in_n"], self.cmp[k]["out_n"]), k)
        self.assertEqual(sum(r["steps"] for r in self.months.values()),
                         self.out["meta"]["pooled_steps"])
        p = self.out["predictions"]
        for w, k in (("W1", "backward"), ("W2", "forward"), ("W4", "exit_other")):
            self.assertEqual(p[w]["kind"], k)
            self.assertEqual(p[w]["ratio"], self.cmp[k]["ratio"], w)
        self.assertEqual(p["W3"]["years_higher"], sum(y["higher"] for y in self.out["years"]))

    def test_checks(self):
        c = self.out["checks"]
        self.assertTrue(c["all_pass"])
        for k in ("C1", "C2", "C3"):
            self.assertTrue(c[k]["pass"], k)
        self.assertTrue(self.out["meta"]["stagemoves_checks"]["all_pass"])
        ran = int(re.search(r"Ran (\d+) tests", self.log).group(1))
        self.assertEqual(len(re.findall(r" \.\.\. ok$", self.log, re.M)), ran)
        self.assertTrue(self.log.rstrip().endswith("OK"))
        c1 = c["C1"]
        self.assertEqual(c1["steps"], c1["pooled_steps"])
        self.assertLessEqual(abs(c1["step_mw"] - c1["pooled_step_mw"]), 1.0)
        self.assertLessEqual(abs(c1["backward_building_mw"] - c1["pooled_backward_building_mw"]),
                             1.0)
        # C4, read by hand: the twenty-first result's backward-from-building MW.
        self.assertEqual(c1["pooled_backward_building_mw"], 7620.0)
        self.assertEqual(c["C2"]["months_without_10_reports"], [])
        self.assertEqual({r["reports"] for r in self.months.values()}, {10})
        expected = {
            "C1": "%s steps; %s MW; backward from building %s MW; all equal to stagemoves' "
                  "pooled table" % (n(c1["pooled_steps"]), fmt(c1["pooled_step_mw"]),
                                    fmt(c1["pooled_backward_building_mw"])),
            "C2": "12 months, each with 10 reports",
            "C3": "stagemoves' checks S1-S4 pass",
            "C4": "backward from building %s MW, as in the twenty-first result"
                  % fmt(c1["pooled_backward_building_mw"]),
            "C5": "%d of %d unit tests passed" % (ran, ran),
        }
        rows = {x["check"]: x["result"] for x in self.table("Checks (all passed)")}
        self.assertEqual(rows, expected)

    def test_predictions(self):
        p = self.out["predictions"]
        heads = [h for h in self.doc if h.startswith("Predictions")]
        self.assertEqual(len(heads), 1)
        rows = {x["prediction"]: x for x in self.table(heads[0])}
        self.assertEqual(sorted(rows), list(PREDICTIONS))
        expected = {"W1": f4(p["W1"]["ratio"]), "W2": f4(p["W2"]["ratio"]),
                    "W3": "%d of %d" % (p["W3"]["years_higher"], p["W3"]["years"]),
                    "W4": f4(p["W4"]["ratio"])}
        self.assertEqual({k: x["result"] for k, x in rows.items()}, expected)
        held = {k: p[k]["held"] for k in PREDICTIONS}
        self.assertEqual({k: x["verdict"] for k, x in rows.items()},
                         {k: verdict(v) for k, v in held.items()})
        # The verdicts follow from the floors.
        self.assertEqual(held["W1"], p["W1"]["ratio"] >= 1.5)
        self.assertEqual(held["W2"], p["W2"]["ratio"] >= 1.25)
        self.assertEqual(held["W3"], p["W3"]["years_higher"] >= 7)
        self.assertEqual(held["W4"], p["W4"]["ratio"] >= 1.5)
        k = sum(held.values())
        self.assertIn("(%d of 4 held)" % k, heads[0])
        self.assertIn("All checks passed; all four predictions held." if k == 4
                      else "All checks passed; %d of 4 predictions held." % k, self.text)

    def test_compare_table(self):
        rows = self.table("Inside and outside the window, pooled 2016-2025")
        self.assertEqual([x["kind"] for x in rows], list(KINDS))
        for x in rows:
            o = self.cmp[x["kind"]]
            self.assertEqual(
                tuple(x[c] for c in ("inside moves", "inside steps", "inside rate",
                                     "outside moves", "outside steps", "outside rate", "ratio",
                                     "MW ratio")),
                (n(o["in_n"]), n(o["in_steps"]), f4(o["in_rate"]), n(o["out_n"]),
                 n(o["out_steps"]), f4(o["out_rate"]), f4(o["ratio"]), f4(o["mw_ratio"])),
                x["kind"])

    def test_month_table(self):
        rows = self.table("By calendar month of report m + 1")
        self.assertEqual([int(x["month"]) for x in rows], list(range(1, 13)))
        for x in rows:
            o = self.months[int(x["month"])]
            self.assertEqual(
                tuple(x[c] for c in ("window", "steps", "backward", "backward rate",
                                     "backward from building", "forward rate", "exit_other",
                                     "to operating", "to operating rate")),
                (o["window"], n(o["steps"]), n(o["backward_n"]), f4(o["backward_rate"]),
                 n(o["backward_building_n"]), f4(o["forward_rate"]), n(o["exit_other_n"]),
                 n(o["to_operating_n"]), f4(o["to_operating_rate"])), x["month"])

    def test_year_table(self):
        rows = self.table("Backward rate inside and outside the window, by year of m (W3)")
        want = self.out["years"]
        self.assertEqual([int(x["year"]) for x in rows], [y["year"] for y in want])
        for x, y in zip(rows, want):
            self.assertEqual((x["inside rate"], x["outside rate"], x["higher"]),
                             (f4(y["in_rate"]), f4(y["out_rate"]),
                              {True: "yes", False: "no"}[y["higher"]]), x["year"])

    def test_stated_numbers(self):
        meta = self.out["meta"]
        stated = [
            "reports %s to %s" % (meta["first_step"], meta["report_max"]),
            "%s steps in all" % n(meta["pooled_steps"]),
        ] + [s % v for s, v in STATED(self)]
        for s in stated:
            self.assertIn(s, self.text, s)

    def test_prose_claims(self):
        """The prose's claims that are not single numbers."""
        b, f = self.cmp["backward"], self.cmp["forward"]
        # "forward moves ... were slightly rarer inside the window"
        self.assertLess(f["in_rate"], f["out_rate"])
        self.assertTrue(0.85 < f["ratio"] < 1.0)
        # "about twice as common"
        self.assertTrue(1.8 < b["ratio"] < 2.2)
        # "By MW the backward ratio is larger still"
        self.assertGreater(b["mw_ratio"], b["ratio"])
        # "Within the window, January and December carry most of it."
        m = self.months
        self.assertGreater(m[1]["backward_n"] + m[12]["backward_n"], b["in_n"] / 2)
        # "highest in January ... lowest in August and September"
        rates = {k: r["backward_rate"] for k, r in m.items()}
        self.assertEqual(max(rates, key=rates.get), 1)
        low = min(rates.values())
        self.assertEqual(sorted(k for k, v in rates.items() if v == low), [8, 9])
        # "on about twice as many steps outside"
        e = self.cmp["exit_other"]
        self.assertTrue(1.9 < e["out_steps"] / e["in_steps"] < 2.1)
        # "December is when plants enter service": the highest month by count, rate and MW.
        for c in ("to_operating_n", "to_operating_rate", "to_operating_mw"):
            self.assertEqual(max(m, key=lambda k: m[k][c]), 12, c)
        # "in 2020 the two rates are close"
        y = {r["year"]: r for r in self.out["years"]}
        self.assertLess(y[2020]["in_rate"] - y[2020]["out_rate"], 0.001)


def STATED(t):
    """(format, values) for every other number stated in the note's prose, computed from the
    raw output the same way the note computed them."""
    c, m, p = t.cmp, t.months, t.out["predictions"]
    b, bb, f, e = c["backward"], c["backward_building"], c["forward"], c["exit_other"]
    other = [r for k, r in m.items() if k != 12]
    not_higher = [str(y["year"]) for y in t.out["years"] if not y["higher"]]
    y2020 = [y for y in t.out["years"] if y["year"] == 2020][0]
    low = min(r["backward_rate"] for r in m.values())
    return [
        ("%s of %s steps from approved or building inside the window moved back a stage (%s), "
         "against %s of %s outside it (%s): a ratio of %s",
         (n(b["in_n"]), n(b["in_steps"]), f4(b["in_rate"]), n(b["out_n"]), n(b["out_steps"]),
          f4(b["out_rate"]), f4(b["ratio"]))),
        ("From building alone the ratio is %s (%d against %d moves)",
         (f4(bb["ratio"]), bb["in_n"], bb["out_n"])),
        ("%s against %s, a ratio of %s, so W2", (f4(f["in_rate"]), f4(f["out_rate"]),
                                                 f4(f["ratio"]))),
        ("higher in %d of the %d years (W3 held)", (p["W3"]["years_higher"], p["W3"]["years"])),
        ("The exceptions are %s, %s and %s", tuple(not_higher)),
        ("in 2020 the two rates are close (%s against %s)",
         (f4(y2020["in_rate"]), f4(y2020["out_rate"]))),
        ("January holds %d of the %d backward moves and %d of the %d from building; December %d "
         "and %d", (m[1]["backward_n"], b["in_n"] + b["out_n"], m[1]["backward_building_n"],
                    bb["in_n"] + bb["out_n"], m[12]["backward_n"], m[12]["backward_building_n"])),
        ("highest in January (%s) and lowest in August and September (%s)",
         (f4(m[1]["backward_rate"]), f4(low))),
        ("%d inside the window and %d outside", (e["in_n"], e["out_n"])),
        ("a ratio of %s (W4 held), on %d moves in ten years", (f4(e["ratio"]),
                                                               e["in_n"] + e["out_n"])),
        ("The December report lists %s steps to operating, a rate of %s, against %s to %s in "
         "every other month; %s MW, against at most %s MW in any other month",
         (n(m[12]["to_operating_n"]), f4(m[12]["to_operating_rate"]),
          f4(min(r["to_operating_rate"] for r in other)),
          f4(max(r["to_operating_rate"] for r in other)), fmt(m[12]["to_operating_mw"]),
          fmt(max(r["to_operating_mw"] for r in other)))),
        ("By MW the backward ratio is larger still (%s)", (f4(b["mw_ratio"]),)),
        ("W4 rests on %d moves", (e["in_n"] + e["out_n"],)),
    ]


if __name__ == "__main__":
    unittest.main()
