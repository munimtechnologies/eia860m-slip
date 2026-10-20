"""Checks the numbers in docs/annual-flows-eia860-entry.md against the raw output of compete job
entry860-v1 (data/entry860_v1.json and docs/entry860-v1-unittests.txt). The figures quoted from
docs/annual-flows.md and docs/annual-flows-eia860-baseline.md are checked by those notes' own
tests, not here. MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Written 19 October 2026 while job entry860-v1 was still queued, from the shape of entry860.py
0.1.0's output; STATED() and test_prose_claims were filled in on 20 October 2026 with the note,
after the job had run, with every number the note's prose states, computed the way the note
computed it."""

import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
YEARS = list(range(2017, 2026))
GROUPS = ("all", "wind_onshore", "solar", "gas_cc", "battery", "gas_ct")
ENTRY = ("in_january_not_planned", "in_january_other_month", "entered_after_january",
         "listed_before_not_in_january", "never_in_860m")
BANDS = ("operating", "building", "approved", "early", "other")
QUARTERS = (("2017-Q1", "2017-Q1"), ("2017-Q2", "2017-Q2"), ("2017-Q3", "2017-Q3"),
            ("2017-Q4", "2017-Q4"), ("after_2017", "after 2017"))


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


def share(x):
    return "n/a" if x is None else "%.3f" % x


def text(v):
    return "" if v is None else str(v)


def verdict(held):
    return {True: "held", False: "failed"}[held]


def ratio(num, den):
    return num / den if den > 0 else None


class EntryDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = read("docs", "annual-flows-eia860-entry.md")
        cls.doc = tables(cls.text)
        cls.out = json.loads(read("data", "entry860_v1.json"))
        cls.log = read("docs", "entry860-v1-unittests.txt")
        cls.rows = {(r["year"], r["group"]): r for r in cls.out["rows"]}

    def r(self, year, group="all"):
        return self.rows[(year, group)]

    def table(self, head):
        self.assertIn(head, self.doc, head)
        return self.doc[head][0]

    def test_checks(self):
        c = self.out["checks"]
        self.assertTrue(c["all_pass"])
        for k in ("E1", "E2", "E3", "E4"):
            self.assertTrue(c[k]["pass"], k)
        ran = int(re.search(r"Ran (\d+) tests", self.log).group(1))
        self.assertEqual(len(re.findall(r" \.\.\. ok$", self.log, re.M)), ran)
        self.assertTrue(self.log.rstrip().endswith("OK"))
        got, want = c["E1"]["got"], c["E1"]["expected"]
        self.assertEqual(sorted(got), sorted(want))
        for y in want:
            self.assertLessEqual(abs(got[y][0] - want[y][0]), 0.1, y)
            self.assertLessEqual(abs(got[y][1] - want[y][1]), 0.1, y)
        self.assertEqual(c["E1"]["missing_columns"], [])
        stray = c["E3"]["in_january_planned_in_year_mw"]
        self.assertEqual(sorted(int(y) for y in stray), YEARS)
        expected = {
            "E1": "none missing; 2017 annual plan %s MW, annual only %s MW; every year to 0.1 MW"
                  % (fmt(got["2017"][0]), fmt(got["2017"][1])),
            "E2": "%d rows, %d not adding up" % (c["E2"]["rows"], c["E2"]["not_adding_up"]),
            "E3": "largest %s MW" % fmt(max(stray.values())),
            "E4": "%s MW" % fmt(c["E4"]["new_entry_2017_mw"]),
            "unit tests": "%d of %d passed" % (ran, ran),
        }
        rows = {x["check"]: x["result"] for x in self.table("Checks (all passed)")}
        self.assertEqual(rows, expected)

    def test_predictions(self):
        p = self.out["predictions"]
        a = self.r(2017)
        heads = [h for h in self.doc if h.startswith("Predictions")]
        self.assertEqual(len(heads), 1)
        rows = {x["prediction"]: x for x in self.table(heads[0])}
        self.assertEqual(sorted(rows), ["A1", "A2", "A3", "A4"])
        expected = {
            "A1": "%.4f (%s of %s MW)" % (p["A1"]["after_share"],
                                          fmt(a["entered_after_january"]), fmt(a["annual_only_mw"])),
            "A2": "%.4f (%s of %s MW)" % (p["A2"]["op_or_building_share"],
                                          fmt(a["after_operating"] + a["after_building"]),
                                          fmt(a["entered_after_january"])),
            "A3": "%d of %d years" % (len(p["A3"]["years_after_share_at_least_half"]),
                                      len(p["A3"]["years"])),
            "A4": "%.4f (%s of %s MW)" % (p["A4"]["new_entry_in_annual_plan_share"],
                                          fmt(a["new_entry_in_annual_plan_mw"]),
                                          fmt(a["new_entry_mw"])),
        }
        self.assertEqual({k: x["result"] for k, x in rows.items()}, expected)
        self.assertEqual(p["A3"]["years"], list(range(2017, 2025)))
        held = {k: p[k]["held"] for k in rows}
        self.assertEqual({k: x["verdict"] for k, x in rows.items()},
                         {k: verdict(v) for k, v in held.items()})
        # The verdicts follow from the rows' MW, unrounded shares.
        self.assertEqual(held["A1"], a["entered_after_january"] / a["annual_only_mw"] >= 0.60)
        self.assertEqual(held["A2"], (a["after_operating"] + a["after_building"])
                         / a["entered_after_january"] >= 0.80)
        half = [y for y in range(2017, 2025)
                if self.r(y)["entered_after_january"] / self.r(y)["annual_only_mw"] >= 0.50]
        self.assertEqual(half, p["A3"]["years_after_share_at_least_half"])
        self.assertEqual(held["A3"], len(half) >= 6)
        self.assertEqual(held["A4"], a["new_entry_in_annual_plan_mw"] / a["new_entry_mw"] >= 0.50)
        # The status line states the tally.
        self.assertIn("All checks passed; all four predictions held." if all(held.values())
                      else "%d of 4 predictions held." % sum(held.values()), self.text)

    def test_year_table(self):
        rows = self.table("Every year, all technologies (MW)")
        self.assertEqual([int(x["year"]) for x in rows], YEARS)
        for x in rows:
            o = self.r(int(x["year"]))
            self.assertEqual(
                (x["annual plan"], x["annual only"], x["in January, not planned"],
                 x["in January, other month"], x["entered after January"],
                 x["listed before, not in January"], x["never in EIA-860M"], x["after_share"]),
                (fmt(o["baseline_mw"]), fmt(o["annual_only_mw"]),
                 fmt(o["in_january_not_planned"]), fmt(o["in_january_other_month"]),
                 fmt(o["entered_after_january"]), fmt(o["listed_before_not_in_january"]),
                 fmt(o["never_in_860m"]), share(o["after_share"])),
                x["year"])
            # in_january_planned_in_year is at most 0.05 MW (E3) and is left out of the table.
            self.assertLessEqual(o["in_january_planned_in_year"], 0.05)

    def test_band_table(self):
        rows = self.table("Every year: what entered after January, by its first EIA-860M band (MW)")
        self.assertEqual([int(x["year"]) for x in rows], YEARS)
        for x in rows:
            o = self.r(int(x["year"]))
            self.assertEqual(
                (x["entered after January"], x["operating"], x["building"], x["approved"],
                 x["early"], x["other"], x["operating or building share"], x["in-year share"]),
                (fmt(o["entered_after_january"]), fmt(o["after_operating"]),
                 fmt(o["after_building"]), fmt(o["after_approved"]), fmt(o["after_early"]),
                 fmt(o["after_other"]), share(o["after_op_or_building_share"]),
                 share(o["after_in_year_share"])),
                x["year"])

    def test_new_entry_table(self):
        rows = self.table("Every year: EIA-860M new entries found in the annual plan (MW)")
        self.assertEqual([int(x["year"]) for x in rows], YEARS)
        for x in rows:
            o = self.r(int(x["year"]))
            self.assertEqual(
                (x["new entries"], x["in the annual plan"], x["share"]),
                (fmt(o["new_entry_mw"]), fmt(o["new_entry_in_annual_plan_mw"]),
                 share(o["new_entry_in_annual_plan_share"])),
                x["year"])

    def test_2017_table(self):
        rows = self.table("2017 by technology (MW)")
        shown = [g for g in GROUPS if (2017, g) in self.rows]
        self.assertEqual([x["group"] for x in rows], shown)
        for x in rows:
            o = self.r(2017, x["group"])
            self.assertEqual(
                (x["annual only"], x["entered after January"], x["after_share"],
                 x["operating or building share"], x["in-year share"], x["new entries"],
                 x["in the annual plan"], x["share"]),
                (fmt(o["annual_only_mw"]), fmt(o["entered_after_january"]),
                 share(o["after_share"]), share(o["after_op_or_building_share"]),
                 share(o["after_in_year_share"]), fmt(o["new_entry_mw"]),
                 fmt(o["new_entry_in_annual_plan_mw"]),
                 share(o["new_entry_in_annual_plan_share"])),
                x["group"])

    def test_timing_table(self):
        t = self.out["timing_2017"]
        rows = self.table("2017: entered after January, by quarter of first report (MW)")
        self.assertEqual([x["first report"] for x in rows], [label for _, label in QUARTERS])
        for x, (key, _) in zip(rows, QUARTERS):
            self.assertEqual((x["all"], x["onshore wind"]),
                             (fmt(t["all"][key]), fmt(t["wind_onshore"][key])), key)
        for g in ("all", "wind_onshore"):
            self.assertLessEqual(abs(sum(t[g].values()) - self.r(2017, g)["entered_after_january"]),
                                 0.05 * len(t[g]) + 0.05, g)

    def test_named_projects(self):
        lists = self.out["lists_2017"]["wind_onshore"]
        rows = self.table("2017 onshore wind in the annual plan only (largest 5)")
        want = lists["annual_only"][:5]
        self.assertEqual(len(rows), len(want))
        for x, y in zip(rows, want):
            self.assertEqual(
                (x["plant"], x["key"], x["MW"], x["entry"], x["first listed"], x["first band"],
                 x["annual fate"]),
                (y["plant"] or "(no name)", y["key"], fmt(y["mw"]), y["entry"],
                 text(y["first_listed"]), text(y["first_band"]), y["cls"]), y["key"])
        rows = self.table("2017 onshore wind new entries not in the annual plan (largest 5)")
        want = lists["new_not_in_annual"][:5]
        self.assertEqual(len(rows), len(want))
        for x, y in zip(rows, want):
            self.assertEqual((x["key"], x["MW"]), (y["key"], fmt(y["mw"])), y["key"])

    def test_stated_numbers(self):
        meta = self.out["meta"]
        mc, kept = meta["annual_maturity_counts"], meta["annual_rows_kept"]
        stated = [
            "{:,} bytes".format(meta["annual_bytes"]),
            "{:,} rows were kept".format(kept),
            "reports to %s" % meta["report_max"],
            "{:,} `monthly_update` and {:,} `incremental_ytd` rows".format(mc["monthly_update"],
                                                                           mc["incremental_ytd"]),
        ] + [s % v for s, v in STATED(self)]
        for s in stated:
            self.assertIn(s, self.text, s)
        # value_counts leaves out rows with no data_maturity, which are kept.
        self.assertGreaterEqual(kept, mc["final"])

    def test_prose_claims(self):
        """The prose's claims that are not single numbers."""
        t = self.out["timing_2017"]["all"]
        # "none from October on"
        self.assertEqual((t["2017-Q4"], t["after_2017"]), (0.0, 0.0))
        meta = self.out["meta"]["annual_report_years"]
        self.assertIn("report years %d-%d" % (min(meta), max(meta)), self.text)
        top = {y["plant"]: y for y in self.out["lists_2017"]["wind_onshore"]["annual_only"][:5]}
        # "Four of the five largest ... (Red Dirt, Thunder Ranch, Red Pine, Beaver Creek) are
        # entrants after January; Bethel ... was in January's report with a status that was not
        # planned."
        after = sorted(p for p, y in top.items() if y["entry"] == "entered_after_january")
        self.assertEqual(after, ["Beaver Creek Wind", "Red Dirt Wind Project", "Red Pine Wind Project",
                                 "Thunder Ranch Wind Project"])
        self.assertEqual(top["Bethel Wind Farm LLC"]["entry"], "in_january_not_planned")
        # "Beaver Creek Wind ... at an early stage and came online in 2017."
        beaver = top["Beaver Creek Wind"]
        self.assertEqual((beaver["first_band"], beaver["cls"]), ("early", "in_year"))
        # "None of the five named onshore wind annual-only generators reads never in EIA-860M;
        # in 2017 only 8.8 MW does, all of it solar."
        self.assertNotIn("never_in_860m", [y["entry"] for y in top.values()])
        self.assertEqual(self.r(2017, "solar")["never_in_860m"], self.r(2017)["never_in_860m"])
        # "after_share was at least 0.50 in all 8 years 2017-2024"
        self.assertEqual(self.out["predictions"]["A3"]["years_after_share_at_least_half"],
                         list(range(2017, 2025)))


def low_high(t, key):
    """(lowest value, its year, highest value, its year) of a share over 2017-2025, all groups."""
    vals = {y: t.r(y)[key] for y in YEARS}
    lo, hi = min(YEARS, key=vals.get), max(YEARS, key=vals.get)
    return (share(vals[lo]), lo, share(vals[hi]), hi)


def STATED(t):
    """(format, values) for every other number stated in the note's prose, computed from the
    raw output the same way the note computed them."""
    a, w, s = t.r(2017), t.r(2017, "wind_onshore"), t.r(2017, "solar")
    q = t.out["timing_2017"]["all"]
    wind = t.out["lists_2017"]["wind_onshore"]
    top = {y["plant"]: y for y in wind["annual_only"][:5]}
    new = wind["new_not_in_annual"]
    a18, a19 = t.r(2018), t.r(2019)
    return [
        ("Of the %s MW of the 2017 annual plan", (fmt(a["annual_only_mw"]),)),
        ("%s MW (%s) was first listed in an EIA-860M report after January 2017",
         (fmt(a["entered_after_january"]), share(a["after_share"]))),
        ("%s MW in February-March, %s MW in April-June and %s MW in July-September, and none from "
         "October on", (fmt(q["2017-Q1"]), fmt(q["2017-Q2"]), fmt(q["2017-Q3"]))),
        ("%s MW was in January's report with a status that was not planned, %s MW was planned there "
         "for a month outside 2017, and %s MW was never listed",
         (fmt(a["in_january_not_planned"]), fmt(a["in_january_other_month"]),
          fmt(a["never_in_860m"]))),
        ("Bethel (%s MW)", (fmt(top["Bethel Wind Farm LLC"]["mw"]),)),
        ("Of the %s MW that entered after January, %s MW (%s) was operating or under construction",
         (fmt(a["entered_after_january"]), fmt(a["after_operating"] + a["after_building"]),
          share(a["after_op_or_building_share"]))),
        ("%s MW was first listed at the earliest stages (P, L) and %s MW as approved",
         (fmt(a["after_early"]), fmt(a["after_approved"]))),
        ("Even so, %s of it came online in 2017", (share(a["after_in_year_share"]),)),
        ("Beaver Creek Wind (%s MW) was first listed in the %s report at an early stage",
         (fmt(top["Beaver Creek Wind"]["mw"]), top["Beaver Creek Wind"]["first_listed"])),
        ("after_share was at least 0.50 in all %d years 2017-2024",
         (len(t.out["predictions"]["A3"]["years_after_share_at_least_half"]),)),
        ("over 2017-2025 it ranges from %s (%d) to %s (%d)", low_high(t, "after_share")),
        ("ranges from %s (%d) to %s (%d): in 2018", low_high(t, "after_op_or_building_share")),
        ("in 2018, %s of the %s MW was first listed as approved, and in 2019, %s of the %s MW",
         (fmt(a18["after_approved"]), fmt(a18["entered_after_january"]),
          fmt(a19["after_approved"]), fmt(a19["entered_after_january"]))),
        ("Of the %s MW that EIA-860M added to its 2017 list after January, %s MW (%s) is in the 2017 "
         "annual plan; onshore wind %s of %s MW (%s)",
         (fmt(a["new_entry_mw"]), fmt(a["new_entry_in_annual_plan_mw"]),
          share(a["new_entry_in_annual_plan_share"]), fmt(w["new_entry_in_annual_plan_mw"]),
          fmt(w["new_entry_mw"]), share(w["new_entry_in_annual_plan_share"]))),
        ("Over 2017-2025 the share ranges from %s (%d) to %s (%d)",
         low_high(t, "new_entry_in_annual_plan_share")),
        ("is %s (%s MW); the next is %s MW", (new[0]["key"], fmt(new[0]["mw"]), fmt(new[1]["mw"]))),
        ("In 2017, %s MW of them was first listed at an early stage and %s MW as approved, and %s of "
         "all the after-January MW still came online in 2017",
         (fmt(a["after_early"]), fmt(a["after_approved"]), share(a["after_in_year_share"]))),
        ("%s of what EIA-860M added to its 2017 list after January",
         (share(a["new_entry_in_annual_plan_share"]),)),
        ("in 2017 only %s MW does, all of it solar", (fmt(s["never_in_860m"]),)),
    ]


if __name__ == "__main__":
    unittest.main()
