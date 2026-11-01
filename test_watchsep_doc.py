"""Checks docs/watchlist-2026-09-note.md against the September 2026 watchlist edition that job
watchsep-v2 wrote (docs/watchlist-2026-09.md, data/watchlist_2026-09.csv) and its self-check
against PUDL's own changelog (docs/watchlist-2026-09-check.md). MV2 of Munim, Inc. (made with AI
agents). Apache-2.0."""

import collections
import csv
import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SUMMARY = "Changes in this report, beside the earlier report pairs"
DELAYS = "Largest delays (same status, later planned month)"
NEW = "Largest new planned generators"
BACKWARD = "Largest backward moves"
# From compete-results/watchsep-v2/logs/run-07-python.stderr.txt ("Ran 44 tests ... OK").
UNIT_TESTS = 44
# From compete-results/watchsep-v2/out/raw/rawcheck.md.
ZENODO = ("23639605", "25 October 2026", "4c741eb77a5ccad5aca32ffe43f398af")


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8") as fh:
        return fh.read()


def tables(text):
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


class WatchSepDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ed_text = read("docs", "watchlist-2026-09.md")
        cls.ed = tables(cls.ed_text)
        cls.checks = json.loads(cls.ed_text.split("## Checks", 1)[1].split("```")[1])
        cls.check = read("docs", "watchlist-2026-09-check.md")
        cls.note = read("docs", "watchlist-2026-09-note.md")
        with open(os.path.join(HERE, "data", "watchlist_2026-09.csv"), encoding="utf-8",
                  newline="") as fh:
            cls.rows = list(csv.DictReader(fh))
        cls.s = {x["change"]: x for x in cls.ed[SUMMARY][0]}

    def test_edition_is_consistent(self):
        c = self.checks
        self.assertIn("# EIA-860M watchlist: report 2026-09", self.ed_text)
        self.assertIn("september_generator2026.xlsx (latest report 2026-09)", self.ed_text)
        self.assertTrue(c["all_pass"])
        for k in ("C1", "C2", "C3", "C4"):
            self.assertTrue(c[k]["pass"], k)
        counts = {k: int(x["n"]) for k, x in self.s.items()}
        self.assertEqual(counts, c["C4"]["row_counts"])
        self.assertEqual(sum(counts.values()), c["C1"]["rows"])
        self.assertEqual(len(self.rows), c["C1"]["rows"])
        self.assertEqual(dict(collections.Counter(x["change"] for x in self.rows)),
                         {k: v for k, v in counts.items() if v})

    def test_note_numbers(self):
        s = self.s
        self.assertIn("Report 2026-09: %d changed generators: %s delayed (%s MW), %s within a "
                      "band, %s to operating (%s MW), %s new (%s MW), %s forward, %s left, %s "
                      "advanced and %s backward."
                      % (len(self.rows), s["delayed"]["n"], fmt(s["delayed"]["mw"]),
                         s["within_band"]["n"], s["to_operating"]["n"],
                         fmt(s["to_operating"]["mw"]), s["new"]["n"], fmt(s["new"]["mw"]),
                         s["forward"]["n"], s["left"]["n"], s["advanced"]["n"],
                         s["backward"]["n"]), self.note)
        d = self.ed[DELAYS][0][0]
        self.assertEqual(float(d["mw"]), max(float(x["mw"]) for x in self.ed[DELAYS][0]))
        self.assertIn("The largest delay is %s (%s, %s, %s MW, status %s), moved %s month, from "
                      "%s to %s." % (d["plant"], d["state"], d["group"], fmt(d["mw"]),
                                     d["status_now"], d["shift_months"], d["planned_prev"],
                                     d["planned_now"]), self.note)
        n = self.ed[NEW][0][0]
        self.assertEqual(float(n["mw"]), max(float(x["mw"]) for x in self.ed[NEW][0]))
        self.assertIn("The largest new planned generator is %s (%s, %s, %s MW, status %s), "
                      "planned for %s." % (n["plant"], n["state"], n["group"], fmt(n["mw"]),
                                           n["status_now"], n["planned_now"]), self.note)
        b = self.ed[BACKWARD][0]
        self.assertEqual(len(b), 1)
        self.assertIn("The one backward move is %s (%s, %s, %s MW), from %s to %s."
                      % (b[0]["plant"], b[0]["state"], b[0]["group"], fmt(b[0]["mw"]),
                         b[0]["status_prev"], b[0]["status_now"]), self.note)
        self.assertIn("%d of %d unit tests passed, and checks C1 to C4 passed"
                      % (UNIT_TESTS, UNIT_TESTS), self.note)

    def test_self_check(self):
        m = re.search(r"PUDL rows (\d+), workbook rows (\d+), union (\d+), same change (\d+): "
                      r"same_share ([0-9.]+), usable True; share of PUDL's rows reproduced 1\.0\.",
                      self.check)
        self.assertIsNotNone(m)
        pudl, wb, union, same = (int(m.group(i)) for i in range(1, 5))
        self.assertEqual(wb, len(self.rows))
        self.assertEqual(union, wb)
        self.assertEqual(same, pudl)
        diffs = json.loads(re.search(r"Differences: (\{[^\n]*\})", self.check).group(1))
        self.assertEqual(sum(diffs.values()), wb - pudl)
        self.assertIn("PUDL's changelog gives %d changes for report 2026-09; the workbook route "
                      "reproduces all %d and finds %d, so %d changes (%d delayed, %d advanced, %d "
                      "within a band) are missing from PUDL's changelog."
                      % (pudl, pudl, wb, wb - pudl, diffs["none -> delayed"],
                         diffs["none -> advanced"], diffs["none -> within_band"]), self.note)
        keys = re.findall(r"^\| (\d+/[A-Z0-9]+) \| none \| (\w+) \|", self.check, re.M)
        self.assertEqual(len(keys), wb - pudl)
        by_key = {x["key"]: x for x in self.rows}
        for key, change in keys:
            self.assertIn(key, by_key)
            self.assertEqual(by_key[key]["change"], change, key)
        self.assertEqual((by_key["68149/RAVEB"]["planned_now"],
                          by_key["70202/PS56"]["planned_now"]), ("2026-10", "2027-01"))
        self.assertIn("2026-07: V, 2026-10, 2026-07; 2026-08: V, 2026-11, 2026-09", self.check)
        self.assertIn("2026-07: V, 2027-01, 2026-07; 2026-08: V, 2027-02, 2026-09", self.check)
        self.assertIn("Zenodo (record %s, %s) is byte-identical to EIA's file (md5 %s)" % ZENODO,
                      self.note)

    def test_disclosure(self):
        self.assertIn("made with AI agents working in MV2's name; no person has checked these "
                      "tables by hand", self.note)
        self.assertIn("[pudl-pr2-plan.md](pudl-pr2-plan.md)", self.note)


if __name__ == "__main__":
    unittest.main()
