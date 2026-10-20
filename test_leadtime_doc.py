"""Checks the numbers in docs/stage-leadtime.md against the raw output of compete job leadtime-v1
(data/leadtime_v1.json, docs/leadtime-v1-output.md and docs/leadtime-v1-unittests.txt). MV2 of
Munim, Inc. (made with AI agents). Apache-2.0.

Written 20 October 2026 before job leadtime-v1 was filed, from the shape of leadtime.py 0.1.0's
output (commit 9ee085b); STATED() and test_prose_claims were filled in with the note, after the
job had run, with every number the note's prose states, computed the way the note computed it."""

import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
BANDS = ("00-03", "04-06", "07-12", "13-24")
STAGES = ("early", "approved", "U", "V", "TS", "OT")
GRID = ("early", "approved", "U", "V")
GROUPS = ("all", "solar", "battery", "wind_onshore", "gas_cc", "gas_ct")
SAMPLE = ("2017-01", "2019-01", "2021-01")
PREDICTIONS = ("L1", "L2", "L3", "L4", "L5", "L6")
BUILDING = ("U", "V", "TS")


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


def f4(x):
    return "n/a" if x is None else "%.4f" % x


def verdict(held):
    return {True: "held", False: "failed"}[held]


class StageLeadTimeDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = read("docs", "stage-leadtime.md")
        cls.doc = tables(cls.text)
        cls.out = json.loads(read("data", "leadtime_v1.json"))
        cls.raw = tables(read("docs", "leadtime-v1-output.md"))
        cls.log = read("docs", "leadtime-v1-unittests.txt")
        cls.cells = {(r["stage"], r["band"]): r for r in cls.out["cells"]}
        cls.grids = {(r["group"], r["stage"]): r for r in cls.out["grids"]}

    def table(self, head):
        self.assertIn(head, self.doc, head)
        return self.doc[head][0]

    def test_raw_output_is_consistent(self):
        """The job's sections agree with each other before any of them is quoted."""
        self.assertEqual(sorted(self.cells), sorted((s, b) for s in STAGES for b in BANDS))
        self.assertEqual(sorted(self.grids), sorted((g, s) for g in GROUPS for s in GRID))
        for st in GRID:
            for b in BANDS:
                self.assertEqual(self.grids[("all", st)][b], self.cells[(st, b)]["on_time_share"],
                                 (st, b))
        self.assertEqual(sum(r["rows"] for r in self.out["cells"]), self.out["meta"]["rows"])
        p = self.out["predictions"]
        for st in ("U", "V"):
            self.assertEqual(p["L1"]["on_time_by_band"][st],
                             {b: self.grids[("all", st)][b] for b in BANDS}, st)
        self.assertEqual(p["L3"]["V_00_03_on_time"], self.cells[("V", "00-03")]["on_time_share"])
        self.assertEqual(p["L4"]["early_13_24_on_time"],
                         self.cells[("early", "13-24")]["on_time_share"])
        self.assertEqual(p["L5"]["V_07_12_on_time"], self.cells[("V", "07-12")]["on_time_share"])
        self.assertEqual(p["L5"]["early_00_03_on_time"],
                         self.cells[("early", "00-03")]["on_time_share"])
        self.assertEqual(p["L6"]["early_13_24_not_online"],
                         self.cells[("early", "13-24")]["not_online_share"])

    def test_raw_md_matches_json(self):
        """The job's markdown prints the same four-decimal values the JSON holds, to three
        decimals, so the note's shares can be checked against either."""
        rows = self.raw["Every cell"][0]
        self.assertEqual([(x["stage"], x["band"]) for x in rows],
                         [(s, b) for s in STAGES for b in BANDS])
        for x in rows:
            o = self.cells[(x["stage"], x["band"])]
            for c in ("on_time_share", "late_share", "not_online_share", "on_time_count_share"):
                self.assertEqual(x[c], share(o[c]), (x["stage"], x["band"], c))
        rows = self.raw["On-time share by stage group and lead band (MW), by technology group"][0]
        for x in rows:
            g = self.grids[(x["group"], x["stage"])]
            self.assertEqual(tuple(x[b] for b in BANDS), tuple(share(g[b]) for b in BANDS),
                             (x["group"], x["stage"]))

    def test_checks(self):
        c = self.out["checks"]
        self.assertTrue(c["all_pass"])
        for k in ("C1", "C2", "C3", "C4"):
            self.assertTrue(c[k]["pass"], k)
        ran = int(re.search(r"Ran (\d+) tests", self.log).group(1))
        self.assertEqual(len(re.findall(r" \.\.\. ok$", self.log, re.M)), ran)
        self.assertTrue(self.log.rstrip().endswith("OK"))
        months = c["C1"]["months"]
        self.assertEqual(sorted(months), list(SAMPLE))
        for k, v in months.items():
            self.assertLessEqual(abs(v["expected_mw"] - v["got_mw"]), 0.1, k)
            self.assertEqual(v["expected_n"], v["got_n"], k)
        fewest = min(self.cells[(st, b)]["generators"] for st in GRID for b in BANDS)
        expected = {
            "C1": "; ".join("%s %s MW, %s rows" % (k, fmt(months[k]["got_mw"]),
                                                    "{:,}".format(months[k]["got_n"]))
                            for k in SAMPLE),
            "C2": "16 cells, fewest generators %s" % "{:,}".format(fewest),
            "C3": "%d cells, %s rows, %d not adding up" % (c["C3"]["cells"],
                                                           "{:,}".format(c["C3"]["rows"]),
                                                           c["C3"]["not_adding_up"]),
            "C4": "%d duplicates, %d rows outside %s to %s" % (
                c["C4"]["duplicate_key_months"], c["C4"]["rows_outside_window"],
                c["C4"]["first_month"], c["C4"]["last_month"]),
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
        by = p["L1"]["on_time_by_band"]
        expected = {
            "L1": "U %s; V %s" % (", ".join(f4(by["U"][b]) for b in BANDS),
                                  ", ".join(f4(by["V"][b]) for b in BANDS)),
            "L2": "fall V %s, early %s" % (f4(p["L2"]["fall_V"]), f4(p["L2"]["fall_early"])),
            "L3": f4(p["L3"]["V_00_03_on_time"]),
            "L4": f4(p["L4"]["early_13_24_on_time"]),
            "L5": "V 07-12 %s, early 00-03 %s" % (f4(p["L5"]["V_07_12_on_time"]),
                                                  f4(p["L5"]["early_00_03_on_time"])),
            "L6": f4(p["L6"]["early_13_24_not_online"]),
        }
        self.assertEqual({k: x["result"] for k, x in rows.items()}, expected)
        held = {k: p[k]["held"] for k in PREDICTIONS}
        self.assertEqual({k: x["verdict"] for k, x in rows.items()},
                         {k: verdict(v) for k, v in held.items()})
        # L1 follows exactly from its two monotonicity flags; the others from unrounded MW.
        self.assertEqual(held["L1"], all(p["L1"]["non_increasing"].values()))
        n = sum(held.values())
        self.assertIn("(%d of 6 held)" % n, heads[0])
        # The status line states the tally.
        self.assertIn("All checks passed; all six predictions held." if n == 6
                      else "All checks passed; %d of 6 predictions held." % n, self.text)

    def test_all_grid(self):
        rows = self.table("On-time share by stage and lead band, all generators (MW)")
        self.assertEqual([x["stage"] for x in rows], list(GRID))
        for x in rows:
            g = self.grids[("all", x["stage"])]
            self.assertEqual(tuple(x[b] for b in BANDS), tuple(share(g[b]) for b in BANDS),
                             x["stage"])

    def test_group_grids(self):
        rows = self.table("On-time share by stage and lead band, by technology (MW)")
        want = [(g, s) for g in GROUPS if g != "all" for s in GRID]
        self.assertEqual([(x["group"], x["stage"]) for x in rows], want)
        for x in rows:
            g = self.grids[(x["group"], x["stage"])]
            self.assertEqual(tuple(x[b] for b in BANDS), tuple(share(g[b]) for b in BANDS),
                             (x["group"], x["stage"]))

    def test_every_cell(self):
        rows = self.table("Every cell")
        self.assertEqual([(x["stage"], x["band"]) for x in rows],
                         [(s, b) for s in STAGES for b in BANDS])
        for x in rows:
            o = self.cells[(x["stage"], x["band"])]
            self.assertEqual(
                (x["rows"], x["generators"], x["MW"], x["on time"], x["late"], x["not online"],
                 x["on time (count)"]),
                ("{:,}".format(o["rows"]), "{:,}".format(o["generators"]), fmt(o["mw"]),
                 share(o["on_time_share"]), share(o["late_share"]),
                 share(o["not_online_share"]), share(o["on_time_count_share"])),
                (x["stage"], x["band"]))

    def test_stated_numbers(self):
        meta = self.out["meta"]
        stated = [
            "reports to %s" % meta["report_max"],
            "report months %s to %s" % (meta["first_month"], meta["last_month"]),
            "{:,} rows".format(meta["rows"]),
            "{:,} generators".format(meta["generators"]),
            "%s MW" % fmt(meta["mw"]),
        ] + [s % v for s, v in STATED(self)]
        for s in stated:
            self.assertIn(s, self.text, s)

    def test_prose_claims(self):
        """The prose's claims that are not single numbers."""
        on = {k: c["on_time_share"] for k, c in self.cells.items()}
        # "Pooled over all stages, the on-time share falls steadily with lead time"
        p = pooled(self)
        self.assertTrue(all(p[i] > p[i + 1] for i in range(len(p) - 1)), p)
        # "only approved (T) falls band by band"
        falls = {st: all(on[(st, a)] > on[(st, b)] for a, b in zip(BANDS, BANDS[1:]))
                 for st in GRID}
        self.assertEqual(falls, {"early": False, "approved": True, "U": False, "V": False})
        # "the share hardly moves within a year ... and drops beyond it": 13-24 is the lowest
        # band for U and V, and L1 failed for both.
        for st in ("U", "V"):
            self.assertEqual(min(BANDS, key=lambda b: on[(st, b)]), "13-24", st)
        self.assertEqual(self.out["predictions"]["L1"]["non_increasing"],
                         {"U": False, "V": False})
        # "Beyond a year, what grows is ... not coming online": not-online share rises band by
        # band for U and V.
        for st in ("U", "V"):
            no = [self.cells[(st, b)]["not_online_share"] for b in BANDS]
            self.assertTrue(all(no[i] < no[i + 1] for i in range(3)), st)
        # "late more often than on time"
        v = self.cells[("V", "00-03")]
        self.assertGreater(v["late_share"], v["on_time_share"])
        # "Every U cell ... is above every early cell, and every V cell up to 12 months ... is
        # above every approved cell"
        self.assertGreater(min(on[("U", b)] for b in BANDS), max(on[("early", b)] for b in BANDS))
        self.assertGreater(min(on[("V", b)] for b in BANDS[:3]),
                           max(on[("approved", b)] for b in BANDS))
        # "In all 16 prediction cells the count-based on-time share is within 0.09 of the MW
        # share (largest gap V at 4-6 months)"
        gaps = {k: abs(self.cells[k]["on_time_count_share"] - on[k]) for k in grid_keys()}
        self.assertLess(max(gaps.values()), 0.09)
        self.assertEqual(max(gaps, key=gaps.get), ("V", "04-06"))
        # "The cell behind L1's failure for V at 13-24 months is the thinnest"
        self.assertEqual(min(grid_keys(), key=lambda k: self.cells[k]["generators"]),
                         ("V", "13-24"))
        # "The largest departure from the all-generators grid is gas combined cycle, early
        # stage, 4-6 months"
        self.assertEqual(largest_departure(self)[0], ("gas_cc", "early", "04-06"))


def grid_keys():
    return [(st, b) for st in GRID for b in BANDS]


def pooled(t):
    """On-time share of all rows in each band, from the cells' four-decimal shares and MW."""
    out = []
    for b in BANDS:
        cs = [t.cells[(st, b)] for st in STAGES]
        out.append(sum(c["on_time_share"] * c["mw"] for c in cs) / sum(c["mw"] for c in cs))
    return out


def building_share(t, b):
    """Share of a band's MW listed as U, V or TS."""
    return (sum(t.cells[(st, b)]["mw"] for st in BUILDING)
            / sum(t.cells[(st, b)]["mw"] for st in STAGES))


def largest_departure(t):
    """((group, stage, band), group share, all-generators share) of the largest absolute gap."""
    best = None
    for g in GROUPS[1:]:
        for st in GRID:
            for b in BANDS:
                x, a = t.grids[(g, st)][b], t.grids[("all", st)][b]
                if x is not None and (best is None or abs(x - a) > best[0]):
                    best = (abs(x - a), (g, st, b), x, a)
    return best[1:]


def STATED(t):
    """(format, values) for every other number stated in the note's prose, computed from the
    raw output the same way the note computed them."""
    c, g, pr = t.cells, t.grids, t.out["predictions"]
    on = {k: x["on_time_share"] for k, x in c.items()}
    no = {k: x["not_online_share"] for k, x in c.items()}
    p = pooled(t)
    early = [on[("early", b)] for b in BANDS]
    v0 = c[("V", "00-03")]
    lower = sum(c[k]["on_time_count_share"] < on[k] for k in grid_keys())
    thin = c[("V", "13-24")]
    dep = largest_departure(t)
    return [
        ("the on-time share is %s at 0-3 months, %s at 4-6, %s at 7-12 and %s at 13-24",
         tuple(share(x) for x in p)),
        ("only approved (T) falls band by band (%s, %s, %s, %s)",
         tuple(share(on[("approved", b)]) for b in BANDS)),
        ("Early-stage plans (P, L) sit between %s and %s at every lead",
         (share(min(early)), share(max(early)))),
        ("U is %s, %s and %s at 0-3, 4-6 and 7-12 months, then %s at 13-24; V is %s, %s and %s, "
         "then %s", tuple(share(on[("U", b)]) for b in BANDS)
         + tuple(share(on[("V", b)]) for b in BANDS)),
        ("at 0-3 months %s of the MW is under construction or testing (U, V, TS), at 13-24 "
         "months %s", (share(building_share(t, "00-03")), share(building_share(t, "13-24")))),
        ("is %s at 0-3 months and %s at 13-24 for U, and %s and %s for V",
         (share(no[("U", "00-03")]), share(no[("U", "13-24")]), share(no[("V", "00-03")]),
          share(no[("V", "13-24")]))),
        ("V at 0-3 months: %s on time, %s late, %s not online (%s rows of %s generators)",
         (share(v0["on_time_share"]), share(v0["late_share"]), share(v0["not_online_share"]),
          "{:,}".format(v0["rows"]), "{:,}".format(v0["generators"]))),
        ("Of that MW, %s came online by 12 months after the planned month",
         (share(v0["on_time_share"] + v0["late_share"]),)),
        ("the early on-time share falls by %s, against %s for V (L2 held)",
         (f4(pr["L2"]["fall_early"]), f4(pr["L2"]["fall_V"]))),
        ("An early plan 13-24 months out was on time for %s of its MW (L4 held, ceiling 0.20), "
         "and %s of it was not online", (share(on[("early", "13-24")]),
                                         share(no[("early", "13-24")]))),
        ("V at 7-12 months was on time for %s of its MW, against %s for early plans due within "
         "3 months (L5 held)", (share(on[("V", "07-12")]), share(on[("early", "00-03")]))),
        ("Every U cell (lowest %s) is above every early cell (highest %s), and every V cell up "
         "to 12 months (lowest %s) is above every approved cell (highest %s)",
         (share(min(on[("U", b)] for b in BANDS)), share(max(early)),
          share(min(on[("V", b)] for b in BANDS[:3])),
          share(max(on[("approved", b)] for b in BANDS)))),
        ("largest gap V at 4-6 months: %s by count, %s by MW",
         (share(c[("V", "04-06")]["on_time_count_share"]), share(on[("V", "04-06")]))),
        ("in %d of the 16 it is lower", (lower,)),
        ("is the thinnest: %d generators, %d rows", (thin["generators"], thin["rows"])),
        ("gas combined cycle, early stage, 4-6 months (%s against %s)",
         (share(dep[1]), share(dep[2]))),
        ("Battery plans at the early stages were on time for at most %s of their MW in every band",
         (share(max(g[("battery", "early")][b] for b in BANDS)),)),
        ("report months after %s are not read", (t.out["meta"]["last_month"],)),
    ]


if __name__ == "__main__":
    unittest.main()
