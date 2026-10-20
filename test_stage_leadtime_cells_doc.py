"""Checks the numbers in docs/stage-leadtime-cells.md against the raw output of compete job
cellmakeup-v1 (data/stage_leadtime_cells.json, docs/stage-leadtime-cells-output.md) and against
the scored note it follows (docs/stage-leadtime.md), including the correction it states. MV2 of
Munim, Inc. (made with AI agents). Apache-2.0.

Written 20 October 2026 with the note, after the job had run; every number the note states is
computed here from the raw output the way the note computed it."""

import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
CELLS = (("U", "13-24"), ("V", "13-24"), ("U", "00-03"), ("V", "00-03"))
HALF = 0.00005  # half a unit in the fourth decimal of a share
VOGTLE, PARISH, LINCOLN, SOUTH_FIELD = "649", "55486", "7277", "60356"


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
    return "%.3f" % x


def two(lo, hi):
    """A share known to lie in [lo, hi], to two decimals; both ends must round alike."""
    a, b = "%.2f" % lo, "%.2f" % hi
    assert a == b, (lo, hi)
    return a


class StageLeadTimeCellsDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = read("docs", "stage-leadtime-cells.md")
        cls.out = json.loads(read("data", "stage_leadtime_cells.json"))
        cls.raw = read("docs", "stage-leadtime-cells-output.md")
        cls.lead = read("docs", "stage-leadtime.md")
        cls.lead_doc = tables(cls.lead)
        cls.cells = {(c["stage"], c["band"]): c for c in cls.out["cells"]}
        cls.k1 = {tuple(k.split(" ")): v for k, v in cls.out["K1"]["cells"].items()}
        preds = {x["prediction"]: x["result"]
                 for x in cls.lead_doc["Predictions (4 of 6 held)"][0]}
        m = re.fullmatch(r"U (\S+), (\S+), (\S+), (\S+); V (\S+), (\S+), (\S+), (\S+)",
                         preds["L1"])
        cls.l1 = {"U": m.groups()[:4], "V": m.groups()[4:]}
        cls.l2 = re.fullmatch(r"fall V (\S+), early (\S+)", preds["L2"]).groups()
        cls.every = {(x["stage"], x["band"]): x for x in cls.lead_doc["Every cell"][0]}

    def plants(self, cell):
        return {p["plant_id"]: p for p in self.cells[cell]["top_plants"]}

    def on_time(self, cell):
        return self.k1[cell]["got"][3]

    def without(self, cell, ids):
        """(low, high) on-time share of a cell without the rows of the given plants, each of
        which was on time for none of its MW, from the cell's four-decimal on-time share."""
        c, p = self.cells[cell], self.plants(cell)
        for i in ids:
            self.assertEqual(p[i]["on_time_share"], 0.0, (cell, i))
        rest = c["mw"] - sum(p[i]["mw"] for i in ids)
        s = self.on_time(cell)
        return (s - HALF) * c["mw"] / rest, (s + HALF) * c["mw"] / rest

    def v_short_bounds(self):
        """(low, high) on-time share of V at 0-3 months with any set of Vogtle's rows taken out.
        Vogtle is not among that cell's ten largest plants, so its MW there is at most the
        tenth plant's; any on-time MW taken out lies between none and all of it."""
        c = self.cells[("V", "00-03")]
        p = c["top_plants"]
        self.assertNotIn(VOGTLE, [x["plant_id"] for x in p])
        cap, total, s = p[-1]["mw"], c["mw"], self.on_time(("V", "00-03"))
        lo = ((s - HALF) * total - cap) / (total - cap)
        hi = (s + HALF) * total / (total - cap)
        return lo, hi, cap

    def test_raw_output_is_consistent(self):
        """K1 passed and the job's sections agree with each other before any is quoted."""
        self.assertTrue(self.out["K1"]["pass"])
        self.assertEqual(sorted(self.cells), sorted(CELLS))
        self.assertEqual(sorted(self.k1), sorted(CELLS))
        for cell in CELLS:
            k, c = self.k1[cell], self.cells[cell]
            self.assertTrue(k["pass"], cell)
            self.assertEqual(k["got"][:2], k["published"][:2], cell)
            self.assertLessEqual(abs(k["got"][2] - k["published"][2]), 0.05, cell)
            self.assertEqual(k["got"][3], k["published"][3], cell)
            self.assertEqual(k["got"][1], c["generators"], cell)
            self.assertLessEqual(abs(k["got"][2] - c["mw"]), 0.05, cell)
            self.assertEqual(sum(g["rows"] for g in c["groups"]), k["got"][0], cell)
            self.assertLessEqual(abs(sum(g["mw"] for g in c["groups"]) - c["mw"]),
                                 0.05 * len(c["groups"]), cell)
            for top, key in (("top_generators", "top_generators_share"),
                             ("top_plants", "top_plants_share")):
                mws = [x["mw"] for x in c[top]]
                self.assertEqual(len(mws), 10, (cell, top))
                self.assertEqual(mws, sorted(mws, reverse=True), (cell, top))
                self.assertLessEqual(abs(sum(mws) / c["mw"] - c[key]), 0.0001, (cell, top))
            self.assertEqual(c["largest_plant_share"], c["top_plants"][0]["mw_share"], cell)
            self.assertIn("%d generators at %d plants, %s MW over rows. The ten largest generators "
                          "hold %s of it, the ten largest plants %s, the largest plant %s." % (
                              c["generators"], c["plants"], c["mw"], c["top_generators_share"],
                              c["top_plants_share"], c["largest_plant_share"]), self.raw)
        block = self.raw.split("## K1: the cells match the published ones", 1)[1].split("```")[1]
        self.assertEqual(json.loads(block), self.out["K1"])
        meta = self.out["meta"]
        self.assertEqual((meta["report_max"], meta["first_month"], meta["last_month"]),
                         ("2026-08", "2016-01", "2023-06"))

    def test_cells_are_the_published_cells(self):
        """K1's published values are the scored note's cells and L1 sequences."""
        for st, b in CELLS:
            x, k = self.every[(st, b)], self.k1[(st, b)]["published"]
            self.assertEqual((x["rows"], x["generators"], x["MW"], x["on time"]),
                             ("{:,}".format(k[0]), "{:,}".format(k[1]), fmt(k[2]), share(k[3])),
                             (st, b))
            i = {"00-03": 0, "13-24": 3}[b]
            self.assertEqual(float(self.l1[st][i]), k[3], (st, b))

    def test_stated_numbers(self):
        for s in [f % v for f, v in STATED(self)]:
            self.assertIn(s, self.text, s)

    def test_prose_claims(self):
        """The prose's claims that are not single numbers."""
        v, u = self.cells[("V", "13-24")], self.cells[("U", "13-24")]
        vp = v["top_plants"]
        # Vogtle, Washington Parish and Lincoln are V 13-24's three largest plants, in that order,
        # none on time for any of its MW; Vogtle's generators are nuclear.
        self.assertEqual([(p["plant_id"], p["plant"], p["state"]) for p in vp[:3]],
                         [(VOGTLE, "Vogtle", "GA"), (PARISH, "Washington Parish Energy Center", "LA"),
                          (LINCOLN, "Lincoln Combustion", "NC")])
        self.assertEqual([p["on_time_share"] for p in vp[:3]], [0.0, 0.0, 0.0])
        groups = {}
        for g in v["top_generators"]:
            groups.setdefault(g["key"].split("/", 1)[0], set()).add(g["group"])
        self.assertEqual(groups[VOGTLE], {"nuclear"})
        self.assertEqual(groups[PARISH], {"gas_cc"})
        self.assertEqual(groups[LINCOLN], {"gas_ct"})
        self.assertEqual(v["top_generators"][0]["key"], VOGTLE + "/4")
        self.assertEqual([g["group"] for g in v["groups"][:3]], ["gas_cc", "nuclear", "solar"])
        # U 13-24: its largest plant is Vogtle again; its largest generator is Goodnight.
        self.assertEqual(u["top_plants"][0]["plant_id"], VOGTLE)
        self.assertEqual(u["top_generators"][0]["plant"], "Goodnight")
        self.assertEqual([g["group"] for g in u["groups"][:2]], ["gas_cc", "wind_onshore"])
        # "Both are still far below V at 0-3 months"; the U cell without Vogtle "still below every
        # shorter U band as published".
        for lo_hi in (self.without(("V", "13-24"), [VOGTLE]),
                      self.without(("V", "13-24"), [VOGTLE, PARISH])):
            self.assertLess(lo_hi[1], self.on_time(("V", "00-03")) - 0.1)
        self.assertLess(self.without(("U", "13-24"), [VOGTLE])[1],
                        min(float(x) for x in self.l1["U"][:3]))
        # "taking them out could move that cell's share by less than 0.005"
        lo, hi, _ = self.v_short_bounds()
        s = self.on_time(("V", "00-03"))
        self.assertLess(max(hi - (s - HALF), (s + HALF) - lo), 0.005)
        # "V's fall from 0-3 to 13-24 months would be between 0.20 and 0.22 without it"
        vlo, vhi = self.without(("V", "13-24"), [VOGTLE])
        self.assertGreaterEqual(lo - vhi, 0.20)
        self.assertLessEqual(hi - vlo, 0.22)
        self.assertGreater(lo - vhi, float(self.l2[1]))
        # "Five of the ten largest U generators (...) and four of the ten largest V generators
        # (...) have no operating month under their plant and generator id"
        none_u = [g["plant"] for g in u["top_generators"] if g["online"] is None]
        none_v = [g["plant"] for g in v["top_generators"] if g["online"] is None]
        self.assertIn("Five of the ten largest U generators", self.text)
        self.assertIn("four of the ten largest V generators", self.text)
        self.assertEqual(len(none_u), 5)
        self.assertEqual(len(none_v), 4)
        for short, full in zip(("South Field Energy", "Chilocco Wind Farm", "Alle-Catt Wind Energy",
                                "Easter", "Canisteo Wind Farm"), none_u):
            self.assertTrue(full.startswith(short), (short, full))
            self.assertIn(short, self.text)
        self.assertEqual(none_v, ["Washington Parish Energy Center"] * 3 + ["Rugged Solar LLC"])
        # South Field: one generator in U 13-24 with no operating month; the same plant id among
        # V 00-03's ten largest plants.
        sf = [g for g in u["top_generators"] if g["key"].startswith(SOUTH_FIELD + "/")]
        self.assertEqual(len(sf), 1)
        self.assertIsNone(sf[0]["online"])
        self.assertEqual(sf[0]["state"], "OH")
        self.assertIn(SOUTH_FIELD, self.plants(("V", "00-03")))
        # The correction: V's rise is from 0-3 to 4-6 months and 13-24 is V's lowest band; U's
        # rise is from 4-6 to 7-12 months.
        vv, uu = [float(x) for x in self.l1["V"]], [float(x) for x in self.l1["U"]]
        self.assertGreater(vv[1], vv[0])
        self.assertEqual(min(vv), vv[3])
        self.assertTrue(all(vv[i] >= vv[i + 1] for i in (1, 2)))
        self.assertGreater(uu[2], uu[1])
        quoted = ("The cell behind L1's failure for V at 13-24 months is the thinnest: 79 "
                  "generators, 315 rows.")
        self.assertIn('"%s"' % quoted, self.text)
        self.assertIn(quoted, self.lead.split("## Correction and follow-up, 20 October 2026")[0])
        self.assertIn('"%s" is wrong in one part' % quoted, self.lead)
        self.assertTrue(self.lead.rstrip().split("\n## ")[-1].startswith(
            "Correction and follow-up, 20 October 2026"))
        self.assertIn("[`stage-leadtime-cells.md`](stage-leadtime-cells.md)", self.lead)


def STATED(t):
    """(format, values) for every number stated in the note's prose."""
    meta = t.out["meta"]
    v, u = t.cells[("V", "13-24")], t.cells[("U", "13-24")]
    vp, up = t.plants(("V", "13-24")), t.plants(("U", "13-24"))
    vg = {g["key"]: g for g in v["top_generators"]}
    vgr = {g["group"]: g for g in v["groups"]}
    ugr = {g["group"]: g for g in u["groups"]}
    three = sum(vp[i]["mw"] for i in (VOGTLE, PARISH, LINCOLN)) / v["mw"]
    good = u["top_generators"][0]
    lo, hi, cap = t.v_short_bounds()
    sf = [g for g in u["top_generators"] if g["key"].startswith(SOUTH_FIELD + "/")][0]
    return [
        ("(reports to %s, report months %s to %s)",
         (meta["report_max"], meta["first_month"], meta["last_month"])),
        ("The cell has %d generators at %d plants and %s MW over rows.",
         (v["generators"], v["plants"], fmt(v["mw"]))),
        ("Its ten largest generators hold %s of that MW and its ten largest plants %s.",
         (share(v["top_generators_share"]), share(v["top_plants_share"]))),
        ("One plant, Vogtle (GA, nuclear), holds %s: unit 4 alone is %s, from %d reports",
         (share(vp[VOGTLE]["mw_share"]), share(vg[VOGTLE + "/4"]["mw_share"]),
          vg[VOGTLE + "/4"]["rows"])),
        ("Washington Parish Energy Center (LA, gas combined cycle, %s) and Lincoln Combustion (NC, "
         "gas combustion turbine, %s) together hold %s.",
         (share(vp[PARISH]["mw_share"]), share(vp[LINCOLN]["mw_share"]), share(three))),
        ("By technology the cell is gas combined cycle %s, nuclear %s and solar %s.",
         (share(vgr["gas_cc"]["mw_share"]), share(vgr["nuclear"]["mw_share"]),
          share(vgr["solar"]["mw_share"]))),
        ("V's low on-time share at 13-24 months (%s)", (share(t.on_time(("V", "13-24"))),)),
        ("Without Vogtle's rows the cell would be on time for about %s of its MW, and without "
         "Vogtle and Washington Parish about %s.",
         (two(*t.without(("V", "13-24"), [VOGTLE])),
          two(*t.without(("V", "13-24"), [VOGTLE, PARISH])))),
        ("Both are still far below V at 0-3 months (%s).", (share(t.on_time(("V", "00-03"))),)),
        ("Vogtle's rows in V at 0-3 months are at most %s MW", (fmt(cap),)),
        ("(%s with it), against %s for early-stage plans.", t.l2),
        ("It has %d generators at %d plants and %s MW over rows; its ten largest generators hold "
         "%s of it, its ten largest plants %s and its largest plant, again Vogtle, %s.",
         (u["generators"], u["plants"], fmt(u["mw"]), share(u["top_generators_share"]),
          share(u["top_plants_share"]), share(up[VOGTLE]["mw_share"]))),
        ("Gas combined cycle is %s of the MW (on time for %s of it) and onshore wind %s (on time "
         "for %s).",
         (share(ugr["gas_cc"]["mw_share"]), share(ugr["gas_cc"]["on_time_share"]),
          share(ugr["wind_onshore"]["mw_share"]), share(ugr["wind_onshore"]["on_time_share"]))),
        ("The largest generator is Goodnight (%s, onshore wind, %s MW), listed %d times",
         (good["state"], fmt(good["capacity_mw"]), good["rows"])),
        ("with planned months from %s to %s and an operating month of %s; it is %s of the cell by "
         "itself.", (good["planned_first"], good["planned_last"], good["online"],
                     share(good["mw_share"]))),
        ("Without Vogtle's rows the U cell would be on time for about %s of its MW, still below "
         "every shorter U band as published (lowest %s).",
         (two(*t.without(("U", "13-24"), [VOGTLE])),
          share(min(float(x) for x in t.l1["U"][:3])))),
        ("South Field Energy (%s) is planned as one %s MW generator", (sf["state"],
                                                                       fmt(sf["capacity_mw"]))),
        ("among the ten largest plants of V at 0-3 months with %d generators",
         (t.plants(("V", "00-03"))[SOUTH_FIELD]["generators"],)),
        ("For V it rises from 0-3 to 4-6 months (%s to %s)", t.l1["V"][:2]),
        ("For U the rise is from 4-6 to 7-12 months (%s to %s).", t.l1["U"][1:3]),
        ("(%s on time for V at 13-24 months)", (t.every[("V", "13-24")]["on time (count)"],)),
    ]


class StageLeadTimeCorrectionTests(unittest.TestCase):
    """The dated section added to docs/stage-leadtime.md states the same numbers."""

    def test_correction_numbers(self):
        t = StageLeadTimeCellsDocTests
        t.setUpClass()
        lead = t.lead.split("## Correction and follow-up, 20 October 2026", 1)[1]
        vp = {p["plant_id"]: p for p in t.cells[("V", "13-24")]["top_plants"]}
        for s in ("(%s to %s)" % t.l1["V"][:2],
                  "Vogtle alone holds %s of its MW" % share(vp[VOGTLE]["mw_share"]),
                  "job `cellmakeup-v1`"):
            self.assertIn(s, lead, s)


if __name__ == "__main__":
    unittest.main()
