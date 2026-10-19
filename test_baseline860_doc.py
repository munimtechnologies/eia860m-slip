"""Checks the numbers in docs/annual-flows-eia860-baseline.md against the raw output of compete job
baseline860-v2 (data/baseline860_v2.json and docs/baseline860-v2-unittests.txt). EIA's figures are
quoted from EIA and are not checked here. MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
YEARS = list(range(2017, 2026))
GROUPS = ("all", "wind_onshore", "solar", "gas_cc", "battery", "gas_ct")


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


def verdict(held):
    return {True: "held", False: "failed"}[held]


class BaselineDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = read("docs", "annual-flows-eia860-baseline.md")
        cls.doc = tables(cls.text)
        cls.out = json.loads(read("data", "baseline860_v2.json"))
        cls.log = read("docs", "baseline860-v2-unittests.txt")
        cls.rows = {(r["year"], r["group"]): r for r in cls.out["rows"]}

    def r(self, year, group="all"):
        return self.rows[(year, group)]

    def table(self, head):
        self.assertIn(head, self.doc, head)
        return self.doc[head][0]

    def test_checks(self):
        c = self.out["checks"]
        self.assertTrue(c["all_pass"])
        for k in ("D1", "D2", "D3", "D4"):
            self.assertTrue(c[k]["pass"], k)
        ran = int(re.search(r"Ran (\d+) tests", self.log).group(1))
        self.assertEqual(len(re.findall(r" \.\.\. ok$", self.log, re.M)), ran)
        self.assertTrue(self.log.rstrip().endswith("OK"))
        years = self.out["meta"]["annual_report_years"]
        got = c["D2"]["got"]
        expected = {
            "D1": "none missing; report years %d-%d" % (years[0], years[-1]),
            "D2": "%s MW; onshore wind %s MW" % (fmt(got["all"]), fmt(got["wind_onshore"])),
            "D3": "%d rows, %d not adding up" % (c["D3"]["rows"], c["D3"]["not_adding_up"]),
            "D4": "%s MW" % fmt(c["D4"]["baseline_2017_mw"]),
            "unit tests": "%d of %d passed" % (ran, ran),
        }
        rows = {x["check"]: x["result"] for x in self.table("Checks (all passed)")}
        self.assertEqual(rows, expected)

    def test_predictions(self):
        p = self.out["predictions"]
        a, w = self.r(2017), self.r(2017, "wind_onshore")
        heads = [h for h in self.doc if h.startswith("Predictions")]
        self.assertEqual(len(heads), 1)
        rows = {x["prediction"]: x for x in self.table(heads[0])}
        self.assertEqual(sorted(rows), ["B1", "B2", "B3", "B4", "B5"])
        expected = {
            "B1": "%s MW, %.1f%% from 25,100 MW" % (fmt(a["baseline_mw"]), 100 * p["B1"]["off"]),
            "B2": "%.4f (%s of %s MW)" % (p["B2"]["share_in_year"], fmt(a["in_year"]),
                                          fmt(a["baseline_mw"])),
            "B3": "%.4f (%s of %s MW)" % (p["B3"]["share_in_year"], fmt(w["in_year"]),
                                          fmt(w["baseline_mw"])),
            "B4": "%.4f (%s of %s MW)" % (p["B4"]["both_share"], fmt(w["both_mw"]),
                                          fmt(w["baseline_mw"])),
            "B5": "%d of %d years" % (len(p["B5"]["years_annual_above_860m"]),
                                      len(p["B5"]["years"])),
        }
        self.assertEqual({k: x["result"] for k, x in rows.items()}, expected)
        self.assertEqual(p["B5"]["years"], list(range(2017, 2025)))
        held = {k: p[k]["held"] for k in rows}
        self.assertEqual({k: x["verdict"] for k, x in rows.items()},
                         {k: verdict(v) for k, v in held.items()})
        # The verdicts follow from the unrounded MW.
        self.assertEqual(held["B1"], abs(a["baseline_mw"] - 25100.0) / 25100.0 <= 0.10)
        self.assertEqual(held["B2"], a["in_year"] / a["baseline_mw"] >= 0.75)
        self.assertEqual(held["B3"], w["in_year"] / w["baseline_mw"] >= 0.80)
        self.assertEqual(held["B4"], w["both_mw"] / w["baseline_mw"] <= 0.80)
        above = [y for y in range(2017, 2025) if self.r(y)["in_year"] / self.r(y)["baseline_mw"]
                 > self.r(y)["delivered_860m_mw"] / self.r(y)["plan_860m_mw"]]
        self.assertEqual(above, p["B5"]["years_annual_above_860m"])
        self.assertEqual(held["B5"], len(above) >= 6)
        # The status line states the tally.
        self.assertIn("All checks passed; all five predictions held." if all(held.values())
                      else "%d of 5 predictions held." % sum(held.values()), self.text)

    def test_year_table(self):
        rows = self.table("Every year, all technologies (MW)")
        self.assertEqual([int(x["year"]) for x in rows], YEARS)
        for x in rows:
            o = self.r(int(x["year"]))
            self.assertEqual(
                (x["annual plan"], x["in year"], x["share_in_year"], x["both"], x["annual only"],
                 x["January EIA-860M plan"], x["delivered"], x["share_860m"], x["EIA-860M only"]),
                (fmt(o["baseline_mw"]), fmt(o["in_year"]), share(o["share_in_year"]),
                 fmt(o["both_mw"]), fmt(o["annual_only_mw"]), fmt(o["plan_860m_mw"]),
                 fmt(o["delivered_860m_mw"]), share(o["share_860m"]), fmt(o["m_only_mw"])),
                x["year"])

    def test_2017_table(self):
        rows = self.table("2017 by technology (MW)")
        shown = [g for g in GROUPS if (2017, g) in self.rows]
        self.assertEqual([x["group"] for x in rows], shown)
        for x in rows:
            o = self.r(2017, x["group"])
            self.assertEqual(
                (x["annual plan"], x["share_in_year"], x["both"], x["both: share in year"],
                 x["annual only"], x["annual only: share in year"], x["January EIA-860M plan"],
                 x["share_860m"], x["EIA-860M only"], x["EIA-860M only: delivered share"]),
                (fmt(o["baseline_mw"]), share(o["share_in_year"]), fmt(o["both_mw"]),
                 share(o["both_share_in_year"]), fmt(o["annual_only_mw"]),
                 share(o["annual_only_share_in_year"]), fmt(o["plan_860m_mw"]),
                 share(o["share_860m"]), fmt(o["m_only_mw"]), share(o["m_only_share_860m"])),
                x["group"])

    def test_named_projects(self):
        lists = self.out["lists_2017"]["wind_onshore"]
        for head, side in (("2017 onshore wind in the annual plan only (largest 5)", "annual_only"),
                           ("2017 onshore wind in January's EIA-860M plan only (largest 5)",
                            "m_only")):
            rows = self.table(head)
            want = lists[side][:5]
            self.assertEqual(len(rows), len(want), head)
            for x, y in zip(rows, want):
                self.assertEqual((x["plant"], x["key"], x["MW"], x["fate"]),
                                 (y["plant"] or "(no name)", y["key"], fmt(y["mw"]),
                                  y["cls"] if side == "annual_only" else
                                  "%s (%s)" % (y["state"], y["cls"])), head)

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


def STATED(t):
    """(format, values) for every other number stated in the note's prose, computed from the
    raw output the same way the note computed them."""
    a, w = t.r(2017), t.r(2017, "wind_onshore")
    rows = {y: t.r(y) for y in YEARS}
    gap = {y: r["in_year"] / r["baseline_mw"] - r["delivered_860m_mw"] / r["plan_860m_mw"]
           for y, r in rows.items() if y <= 2024}
    lo, hi = min(gap, key=gap.get), max(gap, key=gap.get)
    m_only = t.out["lists_2017"]["wind_onshore"]["m_only"]
    annual_only = t.out["lists_2017"]["wind_onshore"]["annual_only"]
    return [
        ("%s MW as planned for 2017, %.1f%% above EIA's 25.1 GW",
         (fmt(a["baseline_mw"]), 100 * (a["baseline_mw"] - 25100.0) / 25100.0)),
        ("%s MW of it (%.1f%%) came online in 2017",
         (fmt(a["in_year"]), 100 * a["in_year"] / a["baseline_mw"])),
        ("lists %s MW, of which %s MW (%.1f%%) came online in 2017",
         (fmt(w["baseline_mw"]), fmt(w["in_year"]), 100 * w["in_year"] / w["baseline_mw"])),
        ("%s MW of the annual plan is also in January's EIA-860M plan", (fmt(a["both_mw"]),)),
        ("%s MW (%.1f%%) is not, and %.1f%% of that came online in 2017",
         (fmt(a["annual_only_mw"]), 100 * a["annual_only_mw"] / a["baseline_mw"],
          100 * a["annual_only_share_in_year"])),
        ("%s MW of January's %s MW plan (%.1f%%) is not in the annual plan, and %.1f%% of that "
         "was delivered",
         (fmt(a["m_only_mw"]), fmt(a["plan_860m_mw"]), 100 * a["m_only_mw"] / a["plan_860m_mw"],
          100 * a["m_only_share_860m"])),
        ("%.1f%% of the overlap came online in 2017 by the annual date",
         (100 * a["both_share_in_year"],)),
        ("%s MW (%.1f%%) of the annual plan's onshore wind is in January's plan too",
         (fmt(w["both_mw"]), 100 * w["both_mw"] / w["baseline_mw"])),
        ("the %s MW that is not came online in 2017 at %.1f%%",
         (fmt(w["annual_only_mw"]), 100 * w["annual_only_share_in_year"])),
        ("%s MW of onshore wind that the annual plan does not, and %.1f%% of it was delivered",
         (fmt(w["m_only_mw"]), 100 * w["m_only_share_860m"])),
        ("led by %s, %s and %s",
         tuple(x["plant"] for x in annual_only[:3])),
        ("%s (%s MW)", (m_only[0]["plant"], fmt(m_only[0]["mw"]))),
        ("%s (%s MW) and %s (%s MW)",
         (m_only[1]["plant"], fmt(m_only[1]["mw"]), m_only[2]["plant"], fmt(m_only[2]["mw"]))),
        ("smallest in %d (%s against %s) and largest in %d (%s against %s)",
         (lo, share(rows[lo]["share_in_year"]), share(rows[lo]["share_860m"]),
          hi, share(rows[hi]["share_in_year"]), share(rows[hi]["share_860m"]))),
        ("2025, outside B5, is %s against %s",
         (share(rows[2025]["share_in_year"]), share(rows[2025]["share_860m"]))),
    ]


if __name__ == "__main__":
    unittest.main()
