"""Checks the numbers in docs/split-rekey.md against the raw output of compete job splitkey-v1
(data/splitkey_v1.json, docs/splitkey-v1-output.md, docs/splitkey-v1-unittests.txt and
data/splitkey_v1_handread.csv) and the hand-readings in data/splitkey_v1_readings.csv. MV2 of
Munim, Inc. (made with AI agents). Apache-2.0.

Drafted 20 October 2026 before job splitkey-v1 had run, from the shape of splitkey.py 0.1.0's
output (commit 7bd3f30); STATED(), HAND_READ_SAME and test_prose_claims were filled in with the
note, after the job had run and the ten links had been read by hand. The readings' (a) and (b)
counts are recomputed here from the records file."""

import csv
import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
PREDICTIONS = ("S1", "S2", "S3", "S4", "S5")
LEADTIME = ("L1", "L2", "L3", "L4", "L5", "L6")
GROUPS = ("solar", "wind_onshore", "gas_cc", "battery", "gas_ct")
STAGES = ("approved", "construction", "other", "permitting", "planning", "testing")
TOLERANCES = (0.05, 0.10, 0.20, 0.30)
HAND_READ = 10
GATE = 7            # fewer than 7 of 10 read as the same project: rule S over-links
HAND_READ_SAME = 10     # how many of the 10 read as one project (data/splitkey_v1_readings.csv)
A_LIMIT, B_LIMIT = 24, 6
SHARED = "Re-scored shares, 0-12-month rows (MW)"
CELLS = "Re-scored stage-by-lead cells, 0-24-month rows (MW)"
TOLERANCE = "Capacity tolerance (reported, never used to choose the rule)"
SHARE_COLS = ("rows", "not online MW", "replaced MW", "replaced share", "on time before",
              "on time after", "not online before", "not online after")


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8") as fh:
        return fh.read()


def read_csv(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


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


def ym(s):
    """Month number of 'YYYY-MM' or 'YYYY-MM-DD'."""
    return int(s[:4]) * 12 + int(s[5:7]) - 1


def share_row(r):
    return ("{:,}".format(r["rows"]), fmt(r["not_online_mw"]), fmt(r["replaced_mw"]),
            f4(r["replaced_share"]), f4(r["on_time_before"]), f4(r["on_time_after"]),
            f4(r["not_online_before"]), f4(r["not_online_after"]))


class SplitRekeyDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = read("docs", "split-rekey.md")
        cls.doc = tables(cls.text)
        cls.out = json.loads(read("data", "splitkey_v1.json"))
        cls.raw = tables(read("docs", "splitkey-v1-output.md"))
        cls.log = read("docs", "splitkey-v1-unittests.txt")
        cls.records = read_csv("data", "splitkey_v1_handread.csv")
        cls.readings = read_csv("data", "splitkey_v1_readings.csv")
        cls.groups = {r["part"]: r for r in cls.out["by_group"]}
        cls.stages = {r["part"]: r for r in cls.out["by_stage"]}
        cls.cells = {r["part"]: r for r in cls.out["cells"]}
        cls.by_key = {}
        for r in sorted(cls.records, key=lambda r: r["report_date"]):
            cls.by_key.setdefault(r["key"], []).append(r)

    def table(self, head):
        self.assertIn(head, self.doc, head)
        return self.doc[head][0]

    def test_raw_output_is_consistent(self):
        """The job's sections agree with each other before any of them is quoted."""
        k = self.out["checks"]
        self.assertEqual(k["all_pass"], bool(k["K1"]["pass"] and k["K2"]["pass"]
                                             and k["K3"]["cohort"]["pass"]
                                             and k["K3"]["leadtime"]["pass"]))
        p, c = self.out["predictions"], self.out["cohort"]
        self.assertEqual(p["S1"]["replaced_share"], c["replaced_share"])
        self.assertEqual(p["S2"]["on_time_before"], c["on_time_before"])
        self.assertEqual(p["S2"]["on_time_after"], c["on_time_after"])
        self.assertEqual(p["S3"]["U_13_24"], self.cells["U 13-24"]["replaced_share"])
        self.assertEqual(p["S3"]["cohort"], c["replaced_share"])
        for g in ("gas_cc", "solar", "wind_onshore", "battery"):
            self.assertEqual(p["S4"]["replaced_share"][g], self.groups[g]["replaced_share"], g)
        lp = self.out["leadtime_predictions"]
        self.assertEqual(p["S5"]["before"], {x: lp["before"][x]["held"] for x in LEADTIME})
        self.assertEqual(p["S5"]["after"], {x: lp["after"][x]["held"] for x in LEADTIME})
        self.assertEqual([s["tolerance"] for s in self.out["sensitivity_tolerance"]],
                         list(TOLERANCES))
        n = self.out["counts"]
        self.assertEqual(n["linked_clusters"], len(self.out["links"]))
        self.assertLessEqual(n["replaced_leavers"], n["linked_leavers"])
        self.assertLessEqual(n["replaced_leaver_mw"], n["possible_leaver_mw"] + 0.05)
        # Rows re-scored: only not-online MW moves, so the published cohort size is unchanged.
        self.assertEqual(c["rows"], self.out["checks"]["K1"]["cohort"]["got"][0])
        # The link table's not-online MW adds up to the cohort's linked and replaced MW.
        links = self.out["links"]
        self.assertAlmostEqual(sum(x["not_online_mw_rows"] for x in links), c["linked_mw"],
                               delta=0.05)
        self.assertAlmostEqual(sum(x["not_online_mw_rows"] for x in links if x["online_all"]),
                               c["replaced_mw"], delta=0.05)
        # Links are listed by not-online MW in the 0-12-month rows, largest first.
        mw = [x["not_online_mw_rows"] for x in links]
        self.assertEqual(mw, sorted(mw, reverse=True))

    def test_raw_md_lists_the_same_links(self):
        rows = self.raw["Every linked cluster"][0]
        self.assertEqual([(x["plant"], x["leavers"]) for x in rows],
                         [(x["plant"], x["leavers"]) for x in self.out["links"]])

    def test_unit_tests(self):
        ran = int(re.search(r"Ran (\d+) tests", self.log).group(1))
        self.assertEqual(ran, 12)
        self.assertEqual(len(re.findall(r" \.\.\. ok$", self.log, re.M)), ran)
        self.assertTrue(self.log.rstrip().endswith("OK"))

    def test_checks(self):
        k = self.out["checks"]
        self.assertTrue(k["all_pass"])
        k1, k2, k3 = k["K1"], k["K2"], k["K3"]
        self.assertTrue(all(v["pass"] for v in k1["cells"].values()))
        g = k1["cohort"]["got"]
        violations = {x: v for x, v in k2.items() if x != "pass"}
        self.assertEqual(len(violations), 6)
        for part in ("cohort", "leadtime"):
            self.assertEqual(k3[part]["rows"][0], k3[part]["rows"][1], part)
            self.assertEqual(k3[part]["mw"][0], k3[part]["mw"][1], part)
        ran = int(re.search(r"Ran (\d+) tests", self.log).group(1))
        expected = {
            "K1": "cohort %s rows, %s MW, on time %s, not online %s; cells %s match" % (
                "{:,}".format(g[0]), fmt(g[1]), f4(g[2]), f4(g[3]), ", ".join(k1["cells"])),
            "K2": "%d violations of the 6 conditions" % sum(violations.values()),
            "K3": "cohort %s rows, %d changed, %d stray; lead-time rows %s, %d changed, %d stray" % (
                "{:,}".format(k3["cohort"]["rows"][0]), k3["cohort"]["rows_changed"],
                k3["cohort"]["stray_changes"], "{:,}".format(k3["leadtime"]["rows"][0]),
                k3["leadtime"]["rows_changed"], k3["leadtime"]["stray_changes"]),
            "unit tests": "%d of %d passed" % (ran, ran),
        }
        rows = {x["check"]: x["result"] for x in self.table("Checks (all passed)")}
        self.assertEqual(rows, expected)

    def test_handread_records(self):
        """The records file holds every key of the ten largest links, and nothing else."""
        keys = set()
        for row in self.out["links"][:HAND_READ]:
            keys.update(row["leavers"].split("; ") + row["arrivals"].split("; "))
        self.assertEqual({r["key"] for r in self.records}, keys)

    def test_readings(self):
        """The readings cover the ten links in order, and their (a) and (b) counts are what the
        records give."""
        self.assertEqual(len(self.readings), HAND_READ)
        for i, (r, x) in enumerate(zip(self.readings, self.out["links"][:HAND_READ])):
            self.assertEqual(int(r["rank"]), i + 1)
            self.assertEqual((r["plant"], r["name"], r["state"], r["leavers"], r["arrivals"]),
                             (x["plant"], x["name"], x["state"], x["leavers"], x["arrivals"]))
            self.assertEqual(r["replacement_month"], x["online_all"] or "", x["name"])
            a, b = gap_a(self, x), side_by_side(self, x)
            self.assertEqual((int(r["a_months"]), int(r["b_months"])), (a, b), x["name"])
            if r["same_project"] == "yes":
                self.assertLessEqual(a, A_LIMIT, x["name"])
                self.assertLessEqual(b, B_LIMIT, x["name"])
        same = sum(r["same_project"] == "yes" for r in self.readings)
        self.assertEqual(same, HAND_READ_SAME)
        self.assertTrue(all(r["same_project"] in ("yes", "no") for r in self.readings))

    def test_handread_table(self):
        heads = [h for h in self.doc if h.startswith("Hand-reading")]
        self.assertEqual(len(heads), 1)
        self.assertIn("(%d of 10 one project)" % HAND_READ_SAME, heads[0])
        rows = self.table(heads[0])
        want = [(r["rank"], r["plant"], r["name"], r["a_months"], r["b_months"], r["change"],
                 r["same_project"], r["replacement_month"] or "none") for r in self.readings]
        got = [(x["rank"], x["plant"], x["name"], x["(a) months"], x["(b) months"], x["change"],
                x["one project"], x["replacement month"]) for x in rows]
        self.assertEqual(got, want)

    def test_predictions(self):
        p = self.out["predictions"]
        heads = [h for h in self.doc if h.startswith("Predictions")]
        self.assertEqual(len(heads), 1)
        rows = {x["prediction"]: x for x in self.table(heads[0])}
        self.assertEqual(sorted(rows), list(PREDICTIONS))
        held = {k: p[k]["held"] for k in PREDICTIONS}
        self.assertEqual({k: x["verdict"] for k, x in rows.items()},
                         {k: verdict(v) for k, v in held.items()})
        s4 = p["S4"]["replaced_share"]
        expected = {
            "S1": f4(p["S1"]["replaced_share"]),
            "S2": "%s to %s (rise %s)" % (f4(p["S2"]["on_time_before"]),
                                          f4(p["S2"]["on_time_after"]), f4(p["S2"]["rise"])),
            "S3": "U 13-24 %s, cohort %s" % (f4(p["S3"]["U_13_24"]), f4(p["S3"]["cohort"])),
            "S4": "gas_cc %s; solar %s; wind %s; battery %s" % (
                f4(s4["gas_cc"]), f4(s4["solar"]), f4(s4["wind_onshore"]), f4(s4["battery"])),
            "S5": "%d of 6 unchanged" % sum(p["S5"]["unchanged"].values()),
        }
        self.assertEqual({k: x["result"] for k, x in rows.items()}, expected)
        n = sum(held.values())
        self.assertIn("(%d of 5 held)" % n, heads[0])
        # S1 failed low, not high: the pre-registration's caveat rule does not apply.
        self.assertFalse(held["S1"])
        self.assertLess(p["S1"]["replaced_share"], p["S1"]["range"][0])

    def test_status_line(self):
        """The status line states the checks, the hand-reading gate and the tally."""
        n = sum(self.out["predictions"][k]["held"] for k in PREDICTIONS)
        self.assertIsNotNone(HAND_READ_SAME)
        gate = HAND_READ_SAME >= GATE
        if self.out["checks"]["all_pass"] and gate:
            self.assertIn("All checks passed; %d of 10 links read as one project; %d of 5 "
                          "predictions held." % (HAND_READ_SAME, n), self.text)
        else:
            self.assertIn("description only", self.text)

    def test_share_tables(self):
        rows = self.table(SHARED)
        want = ([("all",) + share_row(self.out["cohort"])]
                + [(g,) + share_row(self.groups[g]) for g in GROUPS]
                + [(s,) + share_row(self.stages[s]) for s in STAGES])
        self.assertEqual([(x["part"],) + tuple(x[c] for c in SHARE_COLS) for x in rows], want)
        rows = self.table(CELLS)
        want = [(r["part"],) + share_row(r) for r in self.out["cells"]]
        self.assertEqual(len(want), 16)
        self.assertEqual([(x["part"],) + tuple(x[c] for c in SHARE_COLS) for x in rows], want)

    def test_tolerance_table(self):
        rows = self.table(TOLERANCE)
        want = [("%.2f" % s["tolerance"], str(s["linked_clusters"]), str(s["replaced_leavers"]),
                 f4(s["replaced_share"]), f4(s["on_time_after"]), f4(s["not_online_after"]))
                for s in self.out["sensitivity_tolerance"]]
        got = [(x["tolerance"], x["linked clusters"], x["replaced leavers"], x["replaced share"],
                x["on time after"], x["not online after"]) for x in rows]
        self.assertEqual(got, want)

    def test_stated_numbers(self):
        for s in [s % v for s, v in STATED(self)]:
            self.assertIn(s, self.text, s)

    def test_prose_claims(self):
        """The prose's claims that are not single numbers."""
        c, links = self.out["cohort"], self.out["links"]
        # "The failure does not hang on the rule's settings": bound B and the widest tolerance
        # are below S1's floor too.
        floor = self.out["predictions"]["S1"]["range"][0]
        self.assertLess(c["possible_share"], floor)
        self.assertLess(max(s["replaced_share"] for s in self.out["sensitivity_tolerance"]), floor)
        # "most of the moved MW became late, not on time": only not-online rows of replaced
        # leavers change, so the fall in not online splits into on time and late. Bound both
        # with half a unit of the fourth decimal.
        fall_lo = (c["not_online_before"] - 0.00005) - (c["not_online_after"] + 0.00005)
        rise_hi = (c["on_time_after"] + 0.00005) - (c["on_time_before"] - 0.00005)
        self.assertGreater(fall_lo - rise_hi, rise_hi)
        # "No on-time share in the breakdowns below rises by more than 0.003 (the largest
        # rise: approved, 13-24 months)"
        rises = rise_by_part(self, "on_time")
        self.assertLess(max(rises.values()), 0.003)
        self.assertEqual(max(rises, key=rises.get), "approved 13-24")
        # "all six stage-by-lead verdicts are unchanged"
        self.assertTrue(all(self.out["predictions"]["S5"]["unchanged"].values()))
        # "The largest falls in a not-online share are U at 13-24 months, gas combined cycle
        # and U at 7-12 months"
        falls = {k: -v for k, v in rise_by_part(self, "not_online").items()}
        self.assertEqual(sorted(falls, key=falls.get, reverse=True)[:3],
                         ["U 13-24", "gas_cc", "U 07-12"])
        # "Three links carry ... of the replaced MW": the three largest links all have a
        # replacement month, and they are South Field, La Joya and Bacliff.
        self.assertTrue(all(x["online_all"] for x in links[:3]))
        self.assertEqual([x["plant"] for x in links[:3]], ["60356", "61044", "60264"])
        # "Gas combined cycle's whole replaced MW is South Field's, and onshore wind's is La
        # Joya's"
        self.assertAlmostEqual(self.groups["gas_cc"]["replaced_mw"], links[0]["not_online_mw_rows"],
                               delta=0.05)
        self.assertAlmostEqual(self.groups["wind_onshore"]["replaced_mw"],
                               links[1]["not_online_mw_rows"], delta=0.05)
        # S4 held: gas CC above solar, wind and battery.
        s4 = self.out["predictions"]["S4"]["replaced_share"]
        self.assertTrue(all(s4["gas_cc"] > s4[g] for g in ("solar", "wind_onshore", "battery")))
        # "their rows stay 'not online' after re-scoring (gas CT's not-online share is ...
        # before and after)": Bacliff is gas CT's only replaced MW.
        ct = self.groups["gas_ct"]
        self.assertEqual(ct["not_online_before"], ct["not_online_after"])
        self.assertAlmostEqual(ct["replaced_mw"], links[2]["not_online_mw_rows"], delta=0.05)
        self.assertGreater(ym(links[2]["online_all"]) - ym(links[2]["planned_was"]), 12)
        # "Four of the ten (Tesla Reno GigaFactory, Holley Road Solar, Hop Bottom and Bayles)"
        # have no replacement month.
        self.assertEqual([x["name"] for x in links[:HAND_READ] if not x["online_all"]],
                         ["Tesla Reno GigaFactory", "Holley Road Solar", "Hop Bottom", "Bayles"])
        # Hop Bottom and Bayles: five engines to three of the same technology.
        for plant in ("58800", "58816"):
            x = [x for x in links[:HAND_READ] if x["plant"] == plant][0]
            old, new = x["leavers"].split("; "), x["arrivals"].split("; ")
            self.assertEqual((len(old), len(new)), (5, 3))
            tech = {self.by_key[k][-1]["technology_description"] for k in old + new}
            self.assertEqual(len(tech), 1)
        # Colby: the new key arrived already operating, before the old key was listed, and it
        # is replaced (so its rows count as on time).
        colby = self.colby()
        self.assertGreater(ym(colby["arrived"]), ym(colby["online_first"]))
        self.assertGreater(ym(colby["planned_was"]) - ym(colby["online_first"]), A_LIMIT)
        self.assertTrue(colby["online_all"])
        self.assertLess(colby["not_online_mw_rows"] / c["not_online_mw"], 0.0001)
        # "For the other twelve links outside the ten, ... planned month within 3 months"
        rest = [x for x in links[HAND_READ:] if x["plant"] != "1272"]
        self.assertEqual(len(rest), 12)
        for x in rest:
            self.assertIsNotNone(x["planned_new"], x["name"])
            self.assertLessEqual(abs(ym(x["planned_new"]) - ym(x["planned_was"])), 3, x["name"])
        # Tolerance 0.05 drops South Field: its arrivals are more than 5% above the old key.
        sf = links[0]
        self.assertGreater(sf["arrival_mw"] / sf["leaver_mw"] - 1, 0.05)

    def colby(self):
        return [x for x in self.out["links"] if x["plant"] == "1272"][0]


def gap_a(t, link):
    """(a): the largest gap in months between a new key's first planned month (its operating
    month if it arrived operating) and the old keys' last planned month."""
    last = max(ym(t.by_key[k][-1]["current_planned_generator_operating_date"])
               for k in link["leavers"].split("; "))
    firsts = []
    for k in link["arrivals"].split("; "):
        r = t.by_key[k][0]
        firsts.append(ym(r["current_planned_generator_operating_date"]
                         or r["generator_operating_date"]))
    return max(abs(f - last) for f in firsts)


def listed(t, keys):
    """Report months a set of keys was listed: each key from its first report to its last
    record's valid-until month."""
    out = set()
    for k in keys:
        rs = t.by_key[k]
        out.update(range(ym(rs[0]["report_date"]), ym(rs[-1]["valid_until_date"]) + 1))
    return out


def side_by_side(t, link):
    """(b): report months in which an old and a new key were both listed."""
    return len(listed(t, link["leavers"].split("; ")) & listed(t, link["arrivals"].split("; ")))


def rise_by_part(t, measure):
    """after - before of a share, for every part of the two re-scored tables."""
    parts = ([("all", t.out["cohort"])] + [(g, t.groups[g]) for g in GROUPS]
             + [(s, t.stages[s]) for s in STAGES] + [(r["part"], r) for r in t.out["cells"]])
    return {p: r[measure + "_after"] - r[measure + "_before"] for p, r in parts}


def STATED(t):
    """(format, values) for every number stated in the note's prose, computed from the raw
    output the same way the note computed them."""
    n, c, links = t.out["counts"], t.out["cohort"], t.out["links"]
    k3 = t.out["checks"]["K3"]
    sens = t.out["sensitivity_tolerance"]
    first = t.out["sensitivity_first_online"]
    sf, lj, bc = links[0], links[1], links[2]
    top3 = sum(x["not_online_mw_rows"] for x in links[:3]) / c["replaced_mw"]
    turbine = t.by_key["60264/CLGT1"][-1]["capacity_mw"]
    old_engine = t.by_key["58800/GEN1"][-1]["capacity_mw"]
    new_engine = t.by_key["58800/1"][0]["capacity_mw"]
    readings = [(gap_a(t, x), side_by_side(t, x)) for x in links[:HAND_READ]]
    colby = t.colby()
    rises = rise_by_part(t, "on_time")
    top = max(rises, key=rises.get)
    cell = {r["part"]: r for r in t.out["cells"]}
    g = t.groups
    return [
        ("reports to %s", (t.out["meta"]["report_max"],)),
        ("(%s rows, %s MW summed over rows)", ("{:,}".format(c["rows"]), fmt(c["mw"]))),
        ("(%s rows). Job", ("{:,}".format(k3["leadtime"]["rows"][0]),)),
        ("The 0-12-month rows hold %s MW of not-online rows", (fmt(c["not_online_mw"]),)),
        ("Rule S replaces %s MW of it, a share of %s",
         (fmt(c["replaced_mw"]), f4(c["replaced_share"]))),
        ("came online, reaches %s", (f4(c["possible_share"]),)),
        ("a capacity tolerance of 0.30 instead of 0.20 gives %s", (f4(sens[3]["replaced_share"]),)),
        ("rule S found %s leavers", ("{:,}".format(n["leavers"]),)),
        ("%s MW) in %d clusters", (fmt(n["leaver_mw"]), n["clusters"])),
        ("Of these, %d clusters link, holding %d leavers, and %d leavers (%s MW) have a "
         "replacement month", (n["linked_clusters"], n["linked_leavers"], n["replaced_leavers"],
                               fmt(n["replaced_leaver_mw"]))),
        ("Bound B covers %d leavers (%s MW): for %s of the leavers' MW",
         (n["possible_leavers"], fmt(n["possible_leaver_mw"]),
          share(1 - n["possible_leaver_mw"] / n["leaver_mw"]))),
        ("by the %s report", (t.out["meta"]["report_max"],)),
        ("moves the overall on-time share from %s to %s (S2 held) and the not-online share from "
         "%s to %s", (f4(c["on_time_before"]), f4(c["on_time_after"]),
                      f4(c["not_online_before"]), f4(c["not_online_after"]))),
        ("(the largest rise: approved, 13-24 months, %s to %s)",
         (f4(cell[top]["on_time_before"]), f4(cell[top]["on_time_after"]))),
        ("U at 13-24 months (%s to %s), gas combined cycle (%s to %s) and U at 7-12 months (%s to "
         "%s)", (f4(cell["U 13-24"]["not_online_before"]), f4(cell["U 13-24"]["not_online_after"]),
                 f4(g["gas_cc"]["not_online_before"]), f4(g["gas_cc"]["not_online_after"]),
                 f4(cell["U 07-12"]["not_online_before"]), f4(cell["U 07-12"]["not_online_after"]))),
        ("Three links carry %s of the replaced MW", (share(top3),)),
        ("one %s MW combined-cycle key", (fmt(sf["leaver_mw"]),)),
        ("which came online in %s and %s", (sf["online_first"], sf["online_all"])),
        ("one %s MW wind key", (fmt(lj["leaver_mw"]),)),
        ("six %s MW combustion turbines", (fmt(float(turbine)),)),
        ("Gas combined cycle's whole replaced MW (%s) is South Field's, and onshore wind's (%s)",
         (fmt(g["gas_cc"]["replaced_mw"]), fmt(g["wind_onshore"]["replaced_mw"]))),
        ("(gas CC's replaced share, %s,", (f4(g["gas_cc"]["replaced_share"]),)),
        ("has a replaced share of %s, against %s overall (S3 held)",
         (f4(cell["U 13-24"]["replaced_share"]), f4(c["replaced_share"]))),
        ("Bacliff's turbines came online in %s, %d months after",
         (bc["online_all"], ym(bc["online_all"]) - ym(bc["planned_was"]))),
        ("(gas CT's not-online share is %s before and after)", (f4(g["gas_ct"]["not_online_before"]),)),
        ("first planned month is at most %d months from", (max(a for a, b in readings),)),
        ("listed side by side for at most %d report months", (max(b for a, b in readings),)),
        ("five %s MW gas engines were re-filed as three %s MW gas engines",
         ("%.1f" % float(old_engine), "%.1f" % float(new_engine))),
        ("the %s MW new key %s was first listed in %s with an operating month of %s, %d months "
         "before the old key's last planned month (%s)",
         (fmt(colby["arrival_mw"]), colby["arrivals"].split("/")[1], colby["arrived"],
          colby["online_first"], ym(colby["planned_was"]) - ym(colby["online_first"]),
          colby["planned_was"])),
        ("They hold %s MW of the 0-12-month not-online MW", (fmt(colby["not_online_mw_rows"]),)),
        ("and %s MW of the stage-by-lead rows", (fmt(colby["lt_not_online_mw_rows"]),)),
        ("the share falls to %s", (f4(sens[0]["replaced_share"]),)),
        ("total %s%% more than the old key (%s against %s MW)",
         ("%.1f" % (100 * (sf["arrival_mw"] / sf["leaver_mw"] - 1)), fmt(sf["arrival_mw"]),
          fmt(sf["leaver_mw"]))),
        ("instead of the last: on time %s, not online %s",
         (f4(first["on_time_after"]), f4(first["not_online_after"]))),
    ]


if __name__ == "__main__":
    unittest.main()
