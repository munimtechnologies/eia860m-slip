"""Tests for docs/annual-flows.md. MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Every number the note states about this run is checked against the output of compete job
eia860m-slip-031-v1, published unchanged beside it: docs/annual-flows-run2-output.md
(flows.md), docs/annual-flows-run2-checks.json (checks.json) and docs/annual-flows-run2-unittests.txt
(the job's unit-test log). EIA's 2017 figures in the
comparison table are quoted from EIA and are not checked here. The tests run wherever docs/
sits beside this file (the repo root).
"""

import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(HERE, "docs")
YEARS = [str(y) for y in range(2017, 2026)]
POOLED = "2017-2025"
PLAN_COLS = {"planned": "planned_mw", "online in year": "online_in_year",
             "rekeyed online": "rekeyed_online", "online before year": "online_before_year",
             "online next months": "online_next_months", "slipped": "slipped", "stale": "stale",
             "not listed": "not_listed", "delivered share": "delivered_share"}
BUILT_COLS = {"built": "built_mw", "in plan": "in_plan_mw", "new entry": "new_entry",
              "rekeyed": "rekeyed", "pulled forward": "pulled_forward",
              "carried over": "carried_over", "listed, not planned": "listed_not_planned",
              "joined share": "joined_share"}


def read(name):
    with open(os.path.join(DOCS, name), encoding="utf-8") as f:
        return f.read()


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


def num(cell):
    return float(cell.replace(",", "")) if cell else None


def fmt(x):
    return f"{x:,.1f}"


def pct(a, b):
    return f"{100 * a / b:.1f}%"


class AnnualFlowsDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = read("annual-flows.md")
        cls.doc = tables(cls.text)
        cls.out_text = read("annual-flows-run2-output.md")
        out = tables(cls.out_text)
        cls.plan = {(r["year"], r["group"]): r
                    for r in out["January's plan by fate, by technology group"][0]}
        cls.built = {(r["year"], r["group"]): r for r in
                     out["The year's additions by where they stood in January, by technology group"][0]}
        pooled_plan, pooled_built = out["Pooled over 2017-2025"]
        cls.pooled_plan = {(r["group"], r["band"]): r for r in pooled_plan}
        cls.pooled_built = {r["group"]: r for r in pooled_built}
        cls.links = out["Every re-key link"][0]
        cls.checks = json.loads(read("annual-flows-run2-checks.json"))
        cls.log = read("annual-flows-run2-unittests.txt")

    def p(self, col, group="all", band="all"):
        return num(self.pooled_plan[(group, band)][col])

    def b(self, col, group="all"):
        return num(self.pooled_built[group][col])

    def assert_row(self, doc_row, out_row, cols):
        for d, o in cols.items():
            self.assertAlmostEqual(num(doc_row[d]), num(out_row[o]), places=6,
                                   msg=f"{doc_row} {d}")

    def test_job_and_checks(self):
        self.assertTrue(self.checks["all_pass"])
        self.assertTrue(all(self.checks[k]["pass"] for k in ("K2", "K3", "K4", "L1", "L2", "L3")))
        ran = int(re.search(r"Ran (\d+) tests", self.log).group(1))
        self.assertEqual(len(re.findall(r" \.\.\. ok$", self.log, re.M)), ran)
        self.assertTrue(self.log.rstrip().endswith("OK"))
        c = self.checks
        expected = {
            "K1": f"{ran} of {ran} passed",
            "K2": f"report max {c['K2']['report_max']}; {c['K2']['operating_exits']} exits",
            "K3": (f"max plan difference {c['K3']['max_planned_mw_diff']:.1f} MW; "
                   f"on time {c['K3']['on_time']:.4f}; not online {c['K3']['not_online_12']:.4f}"),
            "K4": (f"{c['K4']['rows']} rows, {c['K4']['rows_not_adding_up']} not adding up; "
                   f"years {c['K4']['years'][0]}-{c['K4']['years'][-1]}"),
            "L1": (f"{c['L1']['links_2018']} links, {fmt(c['L1']['mw_2018'])} MW, "
                   f"{len(c['L1']['unexpected'])} unexpected"),
            "L2": (f"{c['L2']['links']} links, {len(c['L2']['missing'])} missing, "
                   f"{len(c['L2']['extra_links'])} extra"),
            "L3": f"{c['L3']['years_checked']} years, {len(c['L3']['years_off'])} off",
        }
        rows = {r["check"]: r["result"] for r in self.doc["Checks (all passed)"][0]}
        self.assertEqual(rows, expected)
        self.assertIn("reports 2015-07 to 2026-08", self.out_text)
        self.assertIn("reports 2015-07 to 2026-08", self.text)

    def test_plan_table(self):
        rows = self.doc["January's plan by year (all technologies, MW)"][0]
        self.assertEqual([r["year"] for r in rows], YEARS + [POOLED])
        for r in rows:
            out = self.pooled_plan[("all", "all")] if r["year"] == POOLED else self.plan[(r["year"], "all")]
            self.assert_row(r, out, PLAN_COLS)
            self.assertEqual(num(out["other_status"]), 0.0)

    def test_built_table(self):
        rows = self.doc["The year's additions by where they stood in January (all technologies, MW)"][0]
        self.assertEqual([r["year"] for r in rows], YEARS + [POOLED])
        for r in rows:
            out = self.pooled_built["all"] if r["year"] == POOLED else self.built[(r["year"], "all")]
            self.assert_row(r, out, BUILT_COLS)

    def test_pooled_tables(self):
        rows = self.doc["Pooled 2017-2025, by technology (MW)"][0]
        self.assertEqual([r["group"] for r in rows],
                         ["all", "solar", "wind_onshore", "gas_cc", "battery", "gas_ct"])
        for r in rows:
            self.assert_row(r, self.pooled_plan[(r["group"], "all")],
                            {k: PLAN_COLS[k] for k in ("planned", "delivered share", "slipped",
                                                       "not listed", "rekeyed online")})
            self.assert_row(r, self.pooled_built[r["group"]],
                            {k: BUILT_COLS[k] for k in ("built", "in plan", "joined share")})
        rows = self.doc["Pooled 2017-2025, by stage in January (all technologies, MW)"][0]
        self.assertEqual([r["band"] for r in rows], ["building", "approved", "early", "other"])
        for r in rows:
            self.assert_row(r, self.pooled_plan[("all", r["band"])],
                            {k: PLAN_COLS[k] for k in ("planned", "online in year", "rekeyed online",
                                                       "slipped", "not listed", "delivered share")})

    def test_links_table(self):
        rows = self.doc["Links found"][0]
        out = {r["plan_key"]: r for r in self.links}
        self.assertEqual(len(rows), len(self.links))
        self.assertEqual({r["old key"] for r in rows}, set(out))
        for r in rows:
            o = out[r["old key"]]
            self.assertEqual((r["year"], r["new key"], r["old plant"], r["new plant"], r["technology"],
                              r["last listed"], r["first listed"]),
                             (o["year"], o["entry_key"], o["plan_plant"], o["entry_plant"], o["group"],
                              o["last_listed"], o["first_listed"]))
            self.assertEqual(num(r["MW"]), num(o["plan_mw"]))
            self.assertEqual(num(r["MW"]), num(o["entry_mw"]))
        self.assertIn(f"exactly the {len(rows)} links", self.text)
        self.assertIn(f"all {2 * len(rows)} keys", self.text)

    def test_stated_numbers(self):
        plan, built, in_plan = self.p("planned_mw"), self.b("built_mw"), self.b("in_plan_mw")
        rekeyed = self.p("rekeyed_online")
        delivered = self.p("online_in_year") + rekeyed
        joined = built - in_plan
        stated = [fmt(plan), fmt(delivered), pct(delivered, plan), fmt(rekeyed)]
        for fate in ("slipped", "online_next_months", "not_listed", "stale", "online_before_year"):
            stated += [fmt(self.p(fate)), pct(self.p(fate), plan)]
        for band in ("building", "approved", "early"):
            stated.append(self.pooled_plan[("all", band)]["delivered_share"])
        # The five largest technology groups by planned MW over 2017-2025.
        totals = {}
        for (year, group), r in self.plan.items():
            if year in YEARS and group != "all":
                totals[group] = totals.get(group, 0.0) + num(r["planned_mw"])
        top5 = sorted(totals, key=totals.get, reverse=True)[:5]
        self.assertEqual(set(top5), {"solar", "wind_onshore", "gas_cc", "battery", "gas_ct"})
        shares = {g: self.p("delivered_share", g) for g in top5}
        self.assertEqual(min(shares, key=shares.get), "battery")
        self.assertEqual(max(shares, key=shares.get), "gas_cc")
        stated += [f"{min(shares.values()):.3f} (battery)", f"{max(shares.values()):.3f} (gas combined cycle)"]
        js = [num(self.built[(y, "all")]["joined_share"]) for y in YEARS]
        stated.append(f"joined share {min(js):.3f} to {max(js):.3f}")
        stated += [fmt(built), fmt(in_plan), pct(in_plan, built), fmt(joined), pct(joined, built)]
        stated += [fmt(self.b(c)) for c in ("new_entry", "listed_not_planned", "pulled_forward",
                                             "rekeyed", "carried_over")]
        run1_not_listed = self.p("not_listed") + rekeyed
        stated.append(f"from {fmt(run1_not_listed)} MW to {fmt(self.p('not_listed'))} MW")
        y18 = self.plan[("2018", "all")]
        stated.append(f"to {y18['delivered_share']} ({num(y18['online_in_year']) / num(y18['planned_mw']):.3f} "
                      "without the links)")
        for s in stated:
            self.assertIn(s, self.text, s)

    def test_eia_comparison_side(self):
        rows = self.doc["A comparison with EIA's own count for 2017"][0]
        ours = {r[""]: r["this run (baseline: January 2017 EIA-860M)"] for r in rows}
        a, g, w, s = (self.plan[("2017", k)] for k in ("all", "gas_cc", "wind_onshore", "solar"))
        self.assertEqual(ours["planned for 2017"], f"{fmt(num(a['planned_mw']))} MW")
        self.assertEqual(ours["came online in 2017"],
                         f"{fmt(num(a['online_in_year']))} MW "
                         f"({pct(num(a['online_in_year']), num(a['planned_mw']))})")
        self.assertEqual(ours["delayed"], f"{fmt(num(a['slipped']))} MW slipped")
        self.assertEqual(ours["gas combined cycle"],
                         f"{fmt(num(g['planned_mw']))} MW planned, {fmt(num(g['online_in_year']))} MW online")
        wind = (f"{fmt(num(w['planned_mw']))} MW planned, {fmt(num(w['online_in_year']))} MW online "
                f"({pct(num(w['online_in_year']), num(w['planned_mw']))})")
        self.assertEqual(ours["onshore wind"], wind)
        self.assertEqual(ours["solar PV"],
                         f"{fmt(num(s['planned_mw']))} MW planned, {fmt(num(s['online_in_year']))} MW online, "
                         f"{fmt(num(s['slipped']))} MW slipped")
        self.assertIn(f"(86% against {pct(num(w['online_in_year']), num(w['planned_mw']))})", self.text)
        for k in ("all", "gas_cc", "wind_onshore", "solar"):
            self.assertEqual(num(self.plan[("2017", k)]["rekeyed_online"]), 0.0)

    def test_predictions_seen_in_run1(self):
        slipped, not_listed, rekeyed = self.p("slipped"), self.p("not_listed"), self.p("rekeyed_online")
        solar_years = sum(num(self.plan[(y, "solar")]["slipped"]) > num(self.plan[(y, "solar")]["not_listed"])
                          for y in YEARS)
        building = (self.p("online_in_year", band="building") + self.p("rekeyed_online", band="building")) \
            / self.p("planned_mw", band="building")
        early = (self.p("online_in_year", band="early") + self.p("rekeyed_online", band="early")) \
            / self.p("planned_mw", band="early")
        new_entry = self.b("new_entry")
        unplanned = self.b("built_mw") - self.b("in_plan_mw") - self.b("rekeyed")
        others = [self.b(c) for c in ("pulled_forward", "carried_over", "listed_not_planned")]
        self.assertGreater(new_entry, max(others))
        stated = [
            f"this run {fmt(slipped)} MW slipped against {fmt(not_listed)} MW not listed "
            f"({slipped / not_listed:.1f} times); in run 1, not listed was {fmt(not_listed + rekeyed)} MW",
            f"this run {solar_years} of {len(YEARS)}",
            f"this run {fmt(self.p('other_status'))} MW",
            f"this run {building:.3f} against {early:.3f} ({building / early:.2f} times, below 3); "
            f"run 1 had {self.p('online_in_year', band='building') / self.p('planned_mw', band='building'):.3f} "
            f"against {early:.3f}",
            f"this run {fmt(new_entry)} MW of {fmt(unplanned)} MW unplanned ({pct(new_entry, unplanned)})",
            f"run 1 had {fmt(new_entry + self.b('rekeyed'))} MW of new entry",
        ]
        for s in stated:
            self.assertIn(s, self.text, s)


if __name__ == "__main__":
    unittest.main()
