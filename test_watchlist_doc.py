"""Checks the numbers in docs/watchlist.md against the first two editions that compete job
watchlist-v2 wrote (docs/watchlist-2026-08.md, docs/watchlist-2026-07.md, data/watchlist_2026-08.csv,
data/watchlist_2026-07.csv) and its unit-test log (docs/watchlist-v2-unittests.txt). MV2 of Munim,
Inc. (made with AI agents). Apache-2.0.

Written 20 October 2026 with the note, after the job had run; every number the note states is
read here from the editions the way the note read it."""

import collections
import csv
import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPORTS = ("2026-08", "2026-07")
CHANGES = ("forward", "backward", "to_operating", "exit_other", "left", "within_band", "delayed",
           "advanced", "new", "into_planned")
SUMMARY = "Changes in this report, beside the earlier report pairs"
DELAYS = "Largest delays (same status, later planned month)"
EXITS = "Largest exits (exit_other and left)"
BACKWARD = "Largest backward moves"
RATES = "Earlier moves: MW listed as operating within 12 reports"
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
    return "{:,.1f}".format(float(mw))


def med(x):
    return "%g" % float(x)


class WatchlistDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = read("docs", "watchlist.md")
        cls.log = read("docs", "watchlist-v2-unittests.txt")
        cls.raw, cls.ed, cls.checks, cls.rows = {}, {}, {}, {}
        for r in REPORTS:
            t = read("docs", "watchlist-%s.md" % r)
            cls.raw[r] = t
            cls.ed[r] = tables(t)
            cls.checks[r] = json.loads(t.split("## Checks", 1)[1].split("```")[1])
            with open(os.path.join(HERE, "data", "watchlist_%s.csv" % r), encoding="utf-8",
                      newline="") as fh:
                cls.rows[r] = list(csv.DictReader(fh))

    def summary(self, r):
        return {x["change"]: x for x in self.ed[r][SUMMARY][0]}

    def top(self, r, head):
        self.assertIn(head, self.ed[r], (r, head))
        return self.ed[r][head][0]

    def test_editions_are_consistent(self):
        """Each edition's tables, checks and CSV agree before any of them is quoted."""
        for r in REPORTS:
            s, c, rows = self.summary(r), self.checks[r], self.rows[r]
            self.assertIn("# EIA-860M watchlist: report %s" % r, self.raw[r])
            self.assertIn("(latest report 2026-08)", self.raw[r])
            self.assertEqual(list(s), list(CHANGES), r)
            self.assertTrue(c["all_pass"], r)
            for k in ("C1", "C2", "C3", "C4"):
                self.assertTrue(c[k]["pass"], (r, k))
            counts = {k: int(x["n"]) for k, x in s.items()}
            self.assertEqual(counts, c["C4"]["row_counts"], r)
            self.assertEqual(sum(counts.values()), c["C1"]["rows"], r)
            self.assertEqual(len(rows), c["C1"]["rows"], r)
            self.assertEqual(dict(collections.Counter(x["change"] for x in rows)),
                             {k: v for k, v in counts.items() if v}, r)
            for k in ("forward", "backward", "to_operating", "exit_other", "left", "new",
                      "into_planned"):
                self.assertEqual(s[k]["pairs"], "36", (r, k))

    def test_unit_tests(self):
        ran = int(re.search(r"Ran (\d+) tests", self.log).group(1))
        self.assertEqual(len(re.findall(r" \.\.\. ok$", self.log, re.M)), ran)
        self.assertTrue(self.log.rstrip().endswith("OK"))
        self.assertIn("%d of %d unit tests passed" % (ran, ran), self.text)
        self.assertIn("Checks C1 to C4 passed for both reports", self.text)

    def test_stated_numbers(self):
        for s in [f % v for f, v in STATED(self)]:
            self.assertIn(s, self.text, s)

    def test_prose_claims(self):
        """The prose's claims that are not single numbers."""
        # "The largest generator delayed": the first delay row is the largest by MW, both reports.
        for r in REPORTS:
            d = self.top(r, DELAYS)
            self.assertEqual(float(d[0]["mw"]), max(float(x["mw"]) for x in d), r)
            self.assertEqual(d[0]["group"], "wind_onshore", r)
            self.assertEqual(d[0]["status_now"], "U", r)
        # "Most of the other large delays are one to three months for plants under construction
        # or testing."
        rest = self.top("2026-08", DELAYS)[1:]
        short = [x for x in rest if 1 <= int(x["shift_months"]) <= 3 and x["status_now"] in BUILDING]
        self.assertGreater(len(short), len(rest) / 2)
        # "It holds one backward move: Madena 4 (CA, battery ...)"
        self.assertEqual(self.summary("2026-07")["backward"]["n"], "1")
        b = self.top("2026-07", BACKWARD)
        self.assertEqual(len(b), 1)
        self.assertEqual(b[0]["group"], "battery")
        self.assertEqual(self.top("2026-08", BACKWARD), [])
        # "The largest exit is Atlas ... no record in force ... and no matching new row"
        self.assertEqual(self.summary("2026-07")["exit_other"]["n"], "0")
        e = self.top("2026-07", EXITS)
        self.assertEqual(float(e[0]["mw"]), max(float(x["mw"]) for x in e))
        self.assertEqual((e[0]["group"], e[0]["status_prev"], e[0]["status_now"],
                          e[0]["possible_rekey"]), ("battery", "V", "", ""))
        # "Neither edition has a possible re-key pair"
        for r in REPORTS:
            self.assertEqual([x["key"] for x in self.rows[r] if x["possible_rekey"]], [], r)
        # "point the same way as the twenty-first result (0.053 against 0.528 ...)"; the publish
        # step copies only the files of its commit, so docs/stage-moves.md is read when present.
        self.assertIn("(0.053 against 0.528 over all reports since 2016, in docs/stage-moves.md)",
                      self.text)
        if os.path.exists(os.path.join(HERE, "docs", "stage-moves.md")):
            moves = read("docs", "stage-moves.md")
            self.assertRegex(moves, r"\| building \| held \|[^\n]*\| 0\.528 \|")
            self.assertRegex(moves, r"\| building \| backward \|[^\n]*\| 0\.053 \|")
        self.assertIn("Steps with m from 2023-07 to 2025-08", self.raw["2026-08"])
        rates = {(x["band"], x["move"]): x for x in self.top("2026-08", RATES)}
        self.assertLess(float(rates[("building", "backward")]["online_share"]),
                        float(rates[("building", "held")]["online_share"]))


def STATED(t):
    """(format, values) for every number stated in the note's prose, read from the editions."""
    s8, s7 = t.summary("2026-08"), t.summary("2026-07")
    d8, d7 = t.top("2026-08", DELAYS)[0], t.top("2026-07", DELAYS)[0]
    b7, e7 = t.top("2026-07", BACKWARD)[0], t.top("2026-07", EXITS)[0]
    rates = {(x["band"], x["move"]): x for x in t.top("2026-08", RATES)}
    bb, bh = rates[("building", "backward")], rates[("building", "held")]
    c8, c7 = t.checks["2026-08"]["C1"]["rows"], t.checks["2026-07"]["C1"]["rows"]
    return [
        ("Report 2026-08: %d changed generators: %s delayed (%s MW), %s within a band, %s to "
         "operating (%s MW), %s new (%s MW; the median of the 36 earlier pairs is %s), %s forward, "
         "%s left, %s advanced and %s backward (median %s).",
         (c8, s8["delayed"]["n"], fmt(s8["delayed"]["mw"]), s8["within_band"]["n"],
          s8["to_operating"]["n"], fmt(s8["to_operating"]["mw"]), s8["new"]["n"],
          fmt(s8["new"]["mw"]), med(s8["new"]["median_n"]), s8["forward"]["n"], s8["left"]["n"],
          s8["advanced"]["n"], s8["backward"]["n"], med(s8["backward"]["median_n"]))),
        ("The largest generator delayed is %s (%s, onshore wind, %s MW, under construction), moved "
         "%s months, from %s to %s.",
         (d8["plant"], d8["state"], fmt(d8["mw"]), d8["shift_months"], d8["planned_prev"],
          d8["planned_now"])),
        ("Report 2026-07: %d changed generators, %s of them delayed (%s MW) and %s new (%s MW).",
         (c7, s7["delayed"]["n"], fmt(s7["delayed"]["mw"]), s7["new"]["n"],
          fmt(s7["new"]["mw"]))),
        ("It holds one backward move: %s (%s, battery, %s MW) from %s to %s.",
         (b7["plant"], b7["state"], fmt(b7["mw"]), b7["status_prev"], b7["status_now"])),
        ("The largest generator delayed is %s (%s, %s MW, under construction), moved %s months, "
         "from %s to %s.",
         (d7["plant"], d7["state"], fmt(d7["mw"]), d7["shift_months"], d7["planned_prev"],
          d7["planned_now"])),
        ("The largest exit is %s (%s, battery, %s MW, more than half built, planned for %s), which "
         "has no record in force in the 2026-07 report",
         (e7["plant"], e7["state"], fmt(e7["mw"]), e7["planned_prev"])),
        ("of the MW that stepped back from building in reports %s to %s, %s was listed as "
         "operating within 12 reports (%s steps), against %s for building MW that held its band.",
         ("2023-07", "2025-08", bb["online_share"], bb["steps"], bh["online_share"])),
    ]


if __name__ == "__main__":
    unittest.main()
