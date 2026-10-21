"""Checks the numbers in docs/stale-keys.md against the raw output of compete job staykey-v1
(data/staykey_v1.json, docs/staykey-v1-output.md, docs/staykey-v1-unittests.txt and
data/staykey_v1_handread.csv). MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Written 21 October 2026 with the note, after job staykey-v1 had run, from test_split_rekey_doc.py.
Rule T linked no groups, so there are no readings to check; the records file must be empty."""

import csv
import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
PREDICTIONS = ("T1", "T2", "T3", "T4", "T5")
LEADTIME = ("L1", "L2", "L3", "L4", "L5", "L6")
GROUPS = ("solar", "wind_onshore", "gas_cc", "battery", "gas_ct")
STAGES = ("approved", "construction", "other", "permitting", "planning", "testing")
BANDS = ("00-03", "04-06", "07-12", "13-24")
TOLERANCES = (0.05, 0.10, 0.20, 0.30)
FATES = ("online_later", "stayer", "leaver", "other")
# The twenty-fourth result's published shares after rule S (docs/split-rekey.md, commit ce1bb6e).
RULE_S_ON_TIME, RULE_S_NOT_ONLINE = 0.3249, 0.1884
SPLIT = "What became of the not-online capacity, 0-12-month rows (MW)"
CELLS = "What became of the not-online capacity, stage-by-lead cells, 0-24-month rows (MW)"
TOLERANCE = "Capacity tolerance (reported, never used to choose the rule)"
SPLIT_COLS = ("rows", "not online MW", "online later", "still listed", "left the list", "other",
              "not online before", "not online, rules S and T")


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


def split_row(r):
    return ("{:,}".format(r["rows"]), fmt(r["not_online_mw"]), f4(r["online_later_share"]),
            f4(r["stayer_share"]), f4(r["leaver_share"]), f4(r["other_share"]),
            f4(r["not_online_before"]), f4(r["not_online_both"]))


class StaleKeysDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = read("docs", "stale-keys.md")
        cls.doc = tables(cls.text)
        cls.out = json.loads(read("data", "staykey_v1.json"))
        cls.raw_text = read("docs", "staykey-v1-output.md")
        cls.raw = tables(cls.raw_text)
        cls.log = read("docs", "staykey-v1-unittests.txt")
        cls.records = read("data", "staykey_v1_handread.csv")
        cls.groups = {r["part"]: r for r in cls.out["by_group"]}
        cls.stages = {r["part"]: r for r in cls.out["by_stage"]}
        cls.cells = {r["part"]: r for r in cls.out["cells"]}

    def table(self, head):
        self.assertIn(head, self.doc, head)
        return self.doc[head][0]

    def parts(self):
        return ([("all", self.out["cohort"])] + [(g, self.groups[g]) for g in GROUPS]
                + [(s, self.stages[s]) for s in STAGES] + [(r["part"], r) for r in self.out["cells"]])

    def test_raw_output_is_consistent(self):
        """The job's sections agree with each other before any of them is quoted."""
        k = self.out["checks"]
        self.assertEqual(k["all_pass"], bool(k["K1"]["pass"] and k["K2"]["pass"]
                                             and k["K3"]["cohort"]["pass"]
                                             and k["K3"]["leadtime"]["pass"]
                                             and k["K3"]["cohort_both"]["pass"]))
        p, c = self.out["predictions"], self.out["cohort"]
        self.assertEqual(p["T1"]["stayer_share"], c["stayer_share"])
        self.assertEqual(p["T2"]["replaced_share"], c["replaced_share"])
        self.assertEqual(p["T3"]["on_time_before"], c["on_time_before"])
        self.assertEqual(p["T3"]["on_time_after"], c["on_time_after"])
        self.assertEqual(p["T4"]["not_online_before"], c["not_online_before"])
        self.assertEqual(p["T4"]["not_online_both"], c["not_online_both"])
        lp = self.out["leadtime_predictions"]
        self.assertEqual(p["T5"]["before"], {x: lp["before"][x]["held"] for x in LEADTIME})
        self.assertEqual(p["T5"]["both"], {x: lp["both"][x]["held"] for x in LEADTIME})
        self.assertEqual([s["tolerance"] for s in self.out["sensitivity_tolerance"]],
                         list(TOLERANCES))
        self.assertEqual(self.out["counts"]["linked_groups"], len(self.out["links"]))
        self.assertEqual([r["part"] for r in self.out["by_stage"]], list(STAGES))
        self.assertEqual(len(self.out["cells"]), 16)
        # The four parts of the split add up to the not-online MW (each MW rounded to 0.1)
        # and their shares to 1 (each rounded to 4 dp).
        for name, r in self.parts():
            self.assertAlmostEqual(sum(r[f + "_mw"] for f in FATES), r["not_online_mw"],
                                   delta=0.25, msg=name)
            self.assertAlmostEqual(sum(r[f + "_share"] for f in FATES), 1.0, delta=0.0003,
                                   msg=name)

    def test_raw_md_lists_no_links(self):
        self.assertIn("0 links.", self.raw_text)
        self.assertEqual(self.raw["Every linked group"], [[]])

    def test_unit_tests(self):
        ran = int(re.search(r"Ran (\d+) tests", self.log).group(1))
        self.assertEqual(ran, 9)
        self.assertEqual(len(re.findall(r" \.\.\. ok$", self.log, re.M)), ran)
        self.assertTrue(self.log.rstrip().endswith("OK"))

    def test_checks(self):
        k = self.out["checks"]
        self.assertTrue(k["all_pass"])
        k1, k2, k3 = k["K1"], k["K2"], k["K3"]
        self.assertTrue(all(v["pass"] for v in k1["cells"].values()))
        g = k1["cohort"]["got"]
        violations = {x: v for x, v in k2.items() if x != "pass"}
        self.assertEqual(len(violations), 7)
        for part in ("cohort", "leadtime", "cohort_both"):
            self.assertEqual(k3[part]["rows"][0], k3[part]["rows"][1], part)
            self.assertEqual(k3[part]["mw"][0], k3[part]["mw"][1], part)
        ran = int(re.search(r"Ran (\d+) tests", self.log).group(1))
        expected = {
            "K1": "cohort %s rows, %s MW, on time %s, not online %s; cells %s match" % (
                "{:,}".format(g[0]), fmt(g[1]), f4(g[2]), f4(g[3]), ", ".join(k1["cells"])),
            "K2": "%d violations of the 7 conditions" % sum(violations.values()),
            "K3": "rule T: cohort %s rows, %d changed, %d stray; lead-time rows %s, %d changed, "
                  "%d stray; rules S and T: cohort %s rows, %d changed, %d stray" % (
                      "{:,}".format(k3["cohort"]["rows"][0]), k3["cohort"]["rows_changed"],
                      k3["cohort"]["stray_changes"], "{:,}".format(k3["leadtime"]["rows"][0]),
                      k3["leadtime"]["rows_changed"], k3["leadtime"]["stray_changes"],
                      "{:,}".format(k3["cohort_both"]["rows"][0]),
                      k3["cohort_both"]["rows_changed"], k3["cohort_both"]["stray_changes"]),
            "unit tests": "%d of %d passed" % (ran, ran),
        }
        rows = {x["check"]: x["result"] for x in self.table("Checks (all passed)")}
        self.assertEqual(rows, expected)

    def test_handread_records(self):
        """No links, so the records file is its header alone."""
        self.assertEqual(self.out["links"], [])
        lines = [x for x in self.records.splitlines() if x.strip()]
        self.assertEqual(len(lines), 1)
        self.assertEqual(next(csv.reader(lines))[0], "key")

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
            "T1": f4(p["T1"]["stayer_share"]),
            "T2": f4(p["T2"]["replaced_share"]),
            "T3": "%s to %s (rise %s)" % (f4(p["T3"]["on_time_before"]),
                                          f4(p["T3"]["on_time_after"]), f4(p["T3"]["rise"])),
            "T4": "%s to %s" % (f4(p["T4"]["not_online_before"]), f4(p["T4"]["not_online_both"])),
            "T5": "%d of 6 unchanged" % sum(p["T5"]["unchanged"].values()),
        }
        self.assertEqual({k: x["result"] for k, x in rows.items()}, expected)
        self.assertIn("(%d of 5 held)" % sum(held.values()), heads[0])

    def test_status_line(self):
        """The status line states the checks, that there was nothing to read, and the tally."""
        n = sum(self.out["predictions"][k]["held"] for k in PREDICTIONS)
        self.assertTrue(self.out["checks"]["all_pass"])
        self.assertEqual(len(self.out["links"]), 0)
        self.assertIn("All checks passed; rule T linked no groups, so there were no links to read "
                      "by hand; %d of 5 predictions held, but only T1 tests something not already "
                      "known" % n, self.text)

    def test_split_tables(self):
        rows = self.table(SPLIT)
        want = ([("all",) + split_row(self.out["cohort"])]
                + [(g,) + split_row(self.groups[g]) for g in GROUPS]
                + [(s,) + split_row(self.stages[s]) for s in STAGES])
        self.assertEqual([(x["part"],) + tuple(x[c] for c in SPLIT_COLS) for x in rows], want)
        rows = self.table(CELLS)
        want = [(r["part"],) + split_row(r) for r in self.out["cells"]]
        self.assertEqual([(x["part"],) + tuple(x[c] for c in SPLIT_COLS) for x in rows], want)

    def test_tolerance_table(self):
        rows = self.table(TOLERANCE)
        want = [("%.2f" % s["tolerance"], str(s["linked_groups"]), str(s["replaced_stayers"]),
                 f4(s["replaced_share"]), f4(s["on_time_after"]), f4(s["not_online_after"]))
                for s in self.out["sensitivity_tolerance"]]
        got = [(x["tolerance"], x["linked groups"], x["replaced stayers"], x["replaced share"],
                x["on time after"], x["not online after"]) for x in rows]
        self.assertEqual(got, want)

    def test_stated_numbers(self):
        for s in [s % v for s, v in STATED(self)]:
            self.assertIn(s, self.text, s)

    def test_prose_claims(self):
        """The prose's claims that are not single numbers."""
        c, n, g, st = self.out["cohort"], self.out["counts"], self.groups, self.stages
        # "more came online late than was dropped" and "none to anything else"
        self.assertGreater(c["online_later_share"], c["leaver_share"])
        self.assertEqual(c["other_mw"], 0.0)
        # "Gas combined cycle's not-online MW is mostly plans that left the list, and so is gas
        # combustion turbines'", "solar's is mostly delayed or still waiting"
        for x in ("gas_cc", "gas_ct"):
            self.assertGreater(g[x]["leaver_share"], 0.5, x)
        self.assertGreater(g["solar"]["online_later_share"] + g["solar"]["stayer_share"], 0.5)
        self.assertLess(g["solar"]["leaver_share"], min(g["solar"]["online_later_share"],
                                                        g["solar"]["stayer_share"]))
        # "testing ... is mostly still listed", "under construction mostly came online later",
        # "about half of the planning-stage not-online MW left the list"
        self.assertGreater(st["testing"]["stayer_share"], 0.5)
        self.assertGreater(st["construction"]["online_later_share"], 0.5)
        self.assertAlmostEqual(st["planning"]["leaver_share"], 0.5, delta=0.01)
        # "the share that left the list rises with lead time in the early, U and V cells ...
        # The approved cells do not follow that pattern."
        for sg in ("early", "U", "V"):
            s = [self.cells["%s %s" % (sg, b)]["leaver_share"] for b in BANDS]
            self.assertEqual(s, sorted(s), sg)
            self.assertEqual(len(set(s)), len(s), sg)
        s = [self.cells["approved %s" % b]["leaver_share"] for b in BANDS]
        self.assertNotEqual(s, sorted(s))
        # "None has a twin"; "rule T replaces nothing at any tolerance from 0.05 to 0.30"
        self.assertEqual((n["linked_groups"], n["twins"], n["linked_stayers"]), (0, 0, 0))
        self.assertTrue(all(s["linked_groups"] == 0 and s["replaced_stayers"] == 0
                            for s in self.out["sensitivity_tolerance"]))
        self.assertEqual(c["replaced_share"], 0.0)
        # Bound B: "less than 0.001 of the not-online MW"
        self.assertLess(c["possible_mw"] / c["not_online_mw"], 0.001)
        # "rules S and T together are rule S, and the shares are the twenty-fourth result's"
        self.assertEqual((c["on_time_both"], c["not_online_both"]),
                         (RULE_S_ON_TIME, RULE_S_NOT_ONLINE))
        self.assertTrue(all(self.out["predictions"]["T5"]["unchanged"].values()))
        # "For gas plants it mostly did mean the plan was dropped."
        self.assertTrue(all(g[x]["leaver_share"] > g[x]["online_later_share"]
                            for x in ("gas_cc", "gas_ct")))


def STATED(t):
    """(format, values) for every number stated in the note's prose, computed from the raw
    output the same way the note computed them."""
    n, c, st, g = t.out["counts"], t.out["cohort"], t.stages, t.groups
    k3 = t.out["checks"]["K3"]
    cell = t.cells
    last = t.out["meta"]["report_max"]

    def ends(sg):
        return (f4(cell[sg + " 00-03"]["leaver_share"]), f4(cell[sg + " 13-24"]["leaver_share"]))

    return [
        ("reports to %s", (last,)),
        ("(%s rows, %s MW summed over rows)", ("{:,}".format(c["rows"]), fmt(c["mw"]))),
        ("(%s rows). Job", ("{:,}".format(k3["leadtime"]["rows"][0]),)),
        ("The 0-12-month rows hold %s MW of not-online rows", (fmt(c["not_online_mw"]),)),
        ("Of it, %s (%s MW) belongs to generators that came online more than 12 months after",
         (f4(c["online_later_share"]), fmt(c["online_later_mw"]))),
        ("; %s (%s MW) to generators still listed as planned in the %s report",
         (f4(c["stayer_share"]), fmt(c["stayer_mw"]), last)),
        ("; %s (%s MW) to generators that left EIA-860M without operating",
         (f4(c["leaver_share"]), fmt(c["leaver_mw"]))),
        ("mostly plans that left the list (%s), and so is gas combustion turbines' (%s)",
         (f4(g["gas_cc"]["leaver_share"]), f4(g["gas_ct"]["leaver_share"]))),
        ("(online later %s, still listed %s, left %s)",
         (f4(g["solar"]["online_later_share"]), f4(g["solar"]["stayer_share"]),
          f4(g["solar"]["leaver_share"]))),
        ("is mostly still listed (%s)", (f4(st["testing"]["stayer_share"]),)),
        ("mostly came online later (%s)", (f4(st["construction"]["online_later_share"]),)),
        ("not-online MW left the list (%s)", (f4(st["planning"]["leaver_share"]),)),
        ("(early %s to %s, U %s to %s, V %s to %s, from 0-3 to 13-24 months)",
         ends("early") + ends("U") + ends("V")),
        ("The %s stayers (%s MW in their last records) form %s groups",
         ("{:,}".format(n["stayers"]), fmt(n["stayer_mw"]), "{:,}".format(n["groups"]))),
        ("covers %d stayer (%s MW in its last record; %s MW of not-online rows",
         (n["possible_stayers"], fmt(n["possible_stayer_mw"]), fmt(c["possible_mw"]))),
        ("the on-time share stays %s", (f4(c["on_time_after"]),)),
        ("on time %s, not online %s (T4 held)", (f4(c["on_time_both"]), f4(c["not_online_both"]))),
        ("by more than %s", (f4(c["on_time_both"] - c["on_time_before"]),)),
    ]


if __name__ == "__main__":
    unittest.main()
