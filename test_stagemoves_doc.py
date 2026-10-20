"""Checks the numbers in docs/stage-moves.md against the raw output of compete job stagemoves-v2
(data/stagemoves_v2.json and docs/stagemoves-v2-unittests.txt). MV2 of Munim, Inc. (made with AI
agents). Apache-2.0.

Written 20 October 2026 while job stagemoves-v2 was still queued (it replaced stagemoves-v1,
which never started), from the shape of stagemoves.py 0.1.0's output; STATED() and
test_prose_claims were filled in with the note, after the job had run, with every number the
note's prose states, computed the way the note computed it."""

import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
BANDS = ("early", "approved", "building")
TO = BANDS + ("operating", "other")
MOVES = ("forward", "held", "backward", "to_operating", "exit_other")
GROUPS = ("all", "solar", "wind_onshore", "battery", "gas_cc", "gas_ct")
SAMPLE = ("2017-01", "2020-01", "2024-01")


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


class StageMovesDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = read("docs", "stage-moves.md")
        cls.doc = tables(cls.text)
        cls.out = json.loads(read("data", "stagemoves_v2.json"))
        cls.log = read("docs", "stagemoves-v2-unittests.txt")
        cls.years = {(r["year"], r["band"]): r for r in cls.out["matrix"]}
        cls.pool = {r["band"]: r for r in cls.out["pooled"]}
        cls.groups = {r["group"]: r for r in cls.out["groups"]}

    def table(self, head):
        self.assertIn(head, self.doc, head)
        return self.doc[head][0]

    def test_checks(self):
        c = self.out["checks"]
        self.assertTrue(c["all_pass"])
        for k in ("S1", "S2", "S3", "S4"):
            self.assertTrue(c[k]["pass"], k)
        ran = int(re.search(r"Ran (\d+) tests", self.log).group(1))
        self.assertEqual(len(re.findall(r" \.\.\. ok$", self.log, re.M)), ran)
        self.assertTrue(self.log.rstrip().endswith("OK"))
        months = c["S1"]["months"]
        self.assertEqual(sorted(months), list(SAMPLE))
        for k, v in months.items():
            self.assertLessEqual(abs(v["expected_mw"] - v["got_mw"]), 0.1, k)
            self.assertEqual(v["expected_n"], v["got_n"], k)
        expected = {
            "S1": "; ".join("%s %s MW, %s steps" % (k, fmt(months[k]["got_mw"]),
                                                     "{:,}".format(months[k]["got_n"]))
                            for k in SAMPLE),
            "S2": "%d rows, %d not adding up" % (c["S2"]["rows"], c["S2"]["not_adding_up"]),
            "S3": "%d links" % c["S3"]["links"],
            "S4": "%d duplicates, %d missing months" % (c["S4"]["duplicate_key_months"],
                                                        len(c["S4"]["missing_months"])),
            "unit tests": "%d of %d passed" % (ran, ran),
        }
        rows = {x["check"]: x["result"] for x in self.table("Checks (all passed)")}
        self.assertEqual(rows, expected)

    def test_predictions(self):
        p = self.out["predictions"]
        g, f, path = self.groups["all"], self.out["flicker"], self.out["paths"]
        heads = [h for h in self.doc if h.startswith("Predictions")]
        self.assertEqual(len(heads), 1)
        rows = {x["prediction"]: x for x in self.table(heads[0])}
        self.assertEqual(sorted(rows), ["M1", "M2", "M3", "M4"])
        expected = {
            "M1": "%.4f (%s of %s MW)" % (p["M1"]["building_backward_share"],
                                          fmt(g["building_backward_mw"]),
                                          fmt(g["building_step_mw"])),
            "M2": "%.4f (%d of %d generators)" % (p["M2"]["returned_share"], f["returned"],
                                                  f["generators"]),
            "M3": "gap %.4f (held %.4f, backward %.4f)" % (p["M3"]["gap"],
                                                           p["M3"]["held_online_share"],
                                                           p["M3"]["backward_online_share"]),
            "M4": "%.4f (%s of %s MW)" % (p["M4"]["through_approved_share"],
                                          fmt(path["through_approved_mw"]), fmt(path["mw"])),
        }
        self.assertEqual({k: x["result"] for k, x in rows.items()}, expected)
        held = {k: p[k]["held"] for k in rows}
        self.assertEqual({k: x["verdict"] for k, x in rows.items()},
                         {k: verdict(v) for k, v in held.items()})
        # M2 follows exactly from its counts; the others from unrounded MW in the job.
        self.assertEqual(held["M2"], f["returned"] / f["generators"] >= 0.25)
        self.assertEqual(held["M3"], p["M3"]["gap"] >= 0.20)
        # The status line states the tally.
        self.assertIn("All checks passed; all four predictions held." if all(held.values())
                      else "%d of 4 predictions held." % sum(held.values()), self.text)
        self.assertIn("## Predictions (%d of 4 held)" % sum(held.values()), self.text)

    def test_pooled_table(self):
        rows = self.table("Pooled 2016-2025: the band in the next report (MW)")
        self.assertEqual([x["from"] for x in rows], list(BANDS))
        for x in rows:
            o = self.pool[x["from"]]
            self.assertEqual(
                tuple(x[c] for c in ("steps", "step MW") + TO + ("left",)),
                ("{:,}".format(o["steps"]), fmt(o["step_mw"]))
                + tuple(fmt(o[b + "_mw"]) for b in TO) + (fmt(o["left_mw"]),), x["from"])

    def year_table(self, head, band):
        rows = self.table(head)
        years = sorted(y for (y, b) in self.years if b == band)
        self.assertEqual([int(x["year"]) for x in rows], years)
        for x in rows:
            o = self.years[(int(x["year"]), band)]
            self.assertEqual(
                tuple(x[c] for c in ("steps", "step MW") + MOVES + ("left", "backward share")),
                ("{:,}".format(o["steps"]), fmt(o["step_mw"]))
                + tuple(fmt(o[m + "_mw"]) for m in MOVES)
                + (fmt(o["left_mw"]), share(o["backward_share"])), x["year"])

    def test_building_years(self):
        self.year_table("Every year: steps from building (MW)", "building")

    def test_approved_years(self):
        self.year_table("Every year: steps from approved (MW)", "approved")

    def test_group_table(self):
        rows = self.table("Pooled 2016-2025: backward share by technology")
        self.assertEqual([x["group"] for x in rows], list(GROUPS))
        for x in rows:
            o = self.groups[x["group"]]
            self.assertEqual(
                (x["building steps MW"], x["backward MW"], x["building share"],
                 x["approved steps MW"], x["approved backward MW"], x["approved share"]),
                (fmt(o["building_step_mw"]), fmt(o["building_backward_mw"]),
                 share(o["building_backward_share"]), fmt(o["approved_step_mw"]),
                 fmt(o["approved_backward_mw"]), share(o["approved_backward_share"])), x["group"])

    def test_outcome_table(self):
        rows = self.table("Listed as operating within 12 reports (closed windows, MW)")
        want = [o for o in self.out["outcomes"] if o["steps"] > 0]
        self.assertEqual([(x["from"], x["move"]) for x in rows],
                         [(o["band"], o["move"]) for o in want])
        for x, o in zip(rows, want):
            self.assertEqual((x["steps"], x["scored MW"], x["online MW"], x["share"]),
                             ("{:,}".format(o["steps"]), fmt(o["scored_mw"]), fmt(o["online_mw"]),
                              share(o["online_share"])), (o["band"], o["move"]))
        # "Rows with no steps (backward from early, forward from building) are left out."
        self.assertEqual(sorted((o["band"], o["move"]) for o in self.out["outcomes"]
                                if o["steps"] == 0),
                         [("building", "forward"), ("early", "backward")])

    def test_top_table(self):
        rows = self.table("Largest backward steps from building")
        want = self.out["top_backward"][:10]
        self.assertEqual(len(rows), len(want))
        for x, y in zip(rows, want):
            self.assertEqual(
                (x["plant"], x["key"], x["group"], x["MW"], x["moved in"], x["from"], x["to"],
                 x["operating within 12"]),
                (y["plant"] or "(no name)", y["key"], y["group"], fmt(y["mw"]), y["moved_in"],
                 y["from_status"], y["to_status"], text(y["online_12"]) or "not yet known"),
                y["key"])

    def test_stated_numbers(self):
        meta = self.out["meta"]
        stated = [
            "reports %s to %s" % (meta["first_step"], meta["report_max"]),
            "{:,} steps".format(meta["steps"]),
            "{:,} generators".format(meta["generators"]),
        ] + [s % v for s, v in STATED(self)]
        for s in stated:
            self.assertIn(s, self.text, s)

    def test_prose_claims(self):
        """The prose's claims that are not single numbers."""
        top = self.out["top_backward"][:10]
        # "all solar or onshore wind projects of 200 MW or more; five went back to P and five to T"
        self.assertLessEqual({y["group"] for y in top}, {"solar", "wind_onshore"})
        self.assertGreaterEqual(min(y["mw"] for y in top), 200)
        self.assertIn("all solar or onshore wind projects of 200 MW or more", self.text)
        to = [y["to_status"] for y in top]
        self.assertEqual((to.count("P"), to.count("T"), len(to)), (5, 5, 10))
        self.assertIn("five went back to P and five to T", self.text)
        # "None of the 8 whose 12-report window has closed was listed as operating within it."
        self.assertEqual({y["online_12"] for y in top if y["online_12"] is not None}, {"no"})
        # "The ten largest of all years 2016-2026; the raw output lists fifteen."
        self.assertEqual(len(self.out["top_backward"]), 15)
        # "Almost all of it is solar and onshore wind."
        g = self.groups
        both = g["solar"]["building_backward_mw"] + g["wind_onshore"]["building_backward_mw"]
        self.assertGreater(both / g["all"]["building_backward_mw"], 0.9)
        # Backward MW from building goes to early or approved; from approved only to early.
        b = self.pool["building"]
        self.assertLessEqual(abs(b["early_mw"] + b["approved_mw"]
                                 - g["all"]["building_backward_mw"]), 0.05)
        self.assertLessEqual(abs(self.pool["approved"]["early_mw"]
                                 - g["all"]["approved_backward_mw"]), 0.05)
        # "Step MW is the sum of the five columns from early to other"
        for band, o in self.pool.items():
            self.assertLessEqual(abs(sum(o[c + "_mw"] for c in TO) - o["step_mw"]), 0.25, band)
        # "nothing can move backward from early"; nothing moves forward from building.
        for (y, band), r in self.years.items():
            if band == "early":
                self.assertEqual(r["backward_mw"], 0, y)
            if band == "building":
                self.assertEqual(r["forward_mw"], 0, y)
        # "About a third flicker back"; "Most capacity skips the approved code".
        self.assertTrue(0.3 <= self.out["flicker"]["share"] < 0.4)
        self.assertLess(self.out["paths"]["share"], 0.5)
        # "2026 holds only the steps from January to July 2026"
        self.assertEqual(self.out["meta"]["report_max"], "2026-08")
        self.assertIn("2026 holds only the steps from January to July 2026", self.text)


def top_max(t, band):
    """(highest backward share, its year) over every year's steps from a band."""
    rows = [r for (y, b), r in sorted(t.years.items()) if b == band]
    r = max(rows, key=lambda r: r["backward_share"])
    return (r["backward_share"], r["year"])


def STATED(t):
    """(format, values) for every other number stated in the note's prose, computed from the
    raw output the same way the note computed them."""
    p, g, pool = t.out["predictions"], t.groups, t.pool
    a, so, wi, cc = g["all"], g["solar"], g["wind_onshore"], g["gas_cc"]
    o = {(x["band"], x["move"]): x for x in t.out["outcomes"]}
    f, path = t.out["flicker"], t.out["paths"]
    top = t.out["top_backward"][:10]
    cradle = [y for y in top if y["plant"] == "Cradle Solar"]
    return [
        ("Of the %s MW of building steps with m in 2016-2025, %s MW (%.4f) moved to an earlier "
         "band in the next report: %s MW to early and %s MW to approved",
         (fmt(a["building_step_mw"]), fmt(a["building_backward_mw"]),
          p["M1"]["building_backward_share"], fmt(pool["building"]["early_mw"]),
          fmt(pool["building"]["approved_mw"]))),
        ("From approved, %s of %s MW (%.4f) moved back to early",
         (fmt(a["approved_backward_mw"]), fmt(a["approved_step_mw"]),
          a["approved_backward_share"])),
        ("did more than %.4f of building MW move backward (%d), or more than %.4f of approved MW "
         "(%d)", top_max(t, "building") + top_max(t, "approved")),
        ("They make up %s of the %s MW that moved back from building in 2016-2025 (solar %s MW, "
         "onshore wind %s MW)",
         (fmt(so["building_backward_mw"] + wi["building_backward_mw"]),
          fmt(a["building_backward_mw"]), fmt(so["building_backward_mw"]),
          fmt(wi["building_backward_mw"]))),
        ("gas combined cycle moved back %s of %s MW",
         (fmt(cc["building_backward_mw"]), fmt(cc["building_step_mw"]))),
        ("None of the %d whose 12-report window has closed",
         (sum(1 for y in top if y["online_12"] is not None),)),
        ("Cradle Solar (%s MW) moved back from building in %s and again in %s",
         (fmt(cradle[0]["mw"]), cradle[0]["moved_in"], cradle[1]["moved_in"])),
        ("%s of the MW held in building was listed as operating within 12 reports, against %s "
         "after a backward move (%s of %s MW): a gap of %s, against the 0.20 predicted",
         (share(o[("building", "held")]["online_share"]),
          share(o[("building", "backward")]["online_share"]),
          fmt(o[("building", "backward")]["online_mw"]),
          fmt(o[("building", "backward")]["scored_mw"]), share(p["M3"]["gap"]))),
        ("%s of the MW that moved forward out of early was operating within 12 reports, against "
         "%s of the MW that stayed early; from approved, %s after a forward move against %s held",
         (share(o[("early", "forward")]["online_share"]),
          share(o[("early", "held")]["online_share"]),
          share(o[("approved", "forward")]["online_share"]),
          share(o[("approved", "held")]["online_share"]))),
        ("Of the %d generators whose first backward move from building can be followed for six "
         "reports, %d (%.4f) were listed as building or operating again within those six "
         "reports; the other %d were not",
         (f["generators"], f["returned"], f["share"], f["generators"] - f["returned"])),
        ("Of the %s generators first listed at an early stage after January 2016 that later "
         "reached building, %d (%s of %s MW, %.4f of the MW)",
         ("{:,}".format(path["generators"]), path["through_approved_n"],
          fmt(path["through_approved_mw"]), fmt(path["mw"]), path["share"])),
        ("%s MW moved straight from early to building and %s MW from early to approved",
         (fmt(pool["early"]["building_mw"]), fmt(pool["early"]["approved_mw"]))),
    ]


if __name__ == "__main__":
    unittest.main()
