"""Doc test: docs/nextmonth-series.md (descriptive summary of the thirty-fourth to forty-first
results) copies every bar row from its note unchanged, its counts of held predictions match each
note's status line, every number it quotes is in the note it comes from, and README.md points to it.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
NOTES = {34: "nexttech.md", 35: "nexttechonce.md", 36: "nextcount.md", 37: "nextheld.md",
         38: "nextgaptech.md", 39: "gapwin.md", 40: "plantw.md", 41: "clusterboot.md"}


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8") as fh:
        return fh.read()


def section(doc, start, end):
    return doc[doc.index(start):doc.index(end)]


class NextmonthSeriesTests(unittest.TestCase):
    def setUp(self):
        self.doc = read("docs", "nextmonth-series.md")
        self.notes = {k: read("docs", v) for k, v in NOTES.items()}
        self.bars = {k: [] for k in NOTES}
        for line in section(self.doc, "## Every bar", "## What still stands").splitlines():
            m = re.match(r"^\| (\d+) (\| (?!\[`).+ \|)$", line)
            if m:
                self.bars[int(m.group(1))].append(m.group(2))

    def test_status(self):
        self.assertIn("Status: descriptive summary; it tests nothing new.", self.doc)

    def test_bars_copied_from_notes(self):
        self.assertEqual(sum(len(v) for v in self.bars.values()), 41)
        for k, rows in self.bars.items():
            self.assertTrue(rows, k)
            for row in rows:
                self.assertIn(row, self.notes[k], "%d: %s" % (k, row))
            # Each note's table has exactly the rows copied: one per bar or check, none left out.
            note_rows = [l for l in self.notes[k].splitlines() if re.match(r"^\| [A-Z]\d", l)]
            self.assertEqual(note_rows, rows, k)

    def test_counts_match_status_lines(self):
        total_held = total = checks = 0
        for k, rows in self.bars.items():
            preds = [r for r in rows if "(check)" not in r.split(" | ")[0]]
            held = [r for r in preds if " | held | " in r]
            failed = [r[2:r.index(".")] for r in preds if " | failed | " in r]
            self.assertEqual(len(held) + len(failed), len(preds))
            for r in rows:
                if "(check)" in r.split(" | ")[0]:
                    checks += 1
                    self.assertIn(" | held | ", r)
            status = [l for l in self.notes[k].splitlines() if l.startswith("Status: ")][0]
            m = re.search(r"(\d+) of (\d+) predictions held", status)
            self.assertEqual((int(m.group(1)), int(m.group(2))), (len(held), len(preds)), k)
            self.assertIn("| %d | [`%s`](%s) | %d of %d | %s |" % (
                k, NOTES[k], NOTES[k], len(held), len(preds), ", ".join(failed) or "none"), self.doc)
            total_held, total = total_held + len(held), total + len(preds)
        self.assertEqual((total_held, total, checks), (27, 33, 8))
        self.assertIn("In all, %d of %d predictions held, and all %d reproduction checks held." % (
            total_held, total, checks), self.doc)

    def test_quotes(self):
        for s, k in (("0.469 (1,980 of 4,223)", 34), ("0.349 (2,110 of 6,047)", 34),
                     ("the share would have fallen from 0.469 to 0.374", None),
                     ("would have fallen from 0.469 to 0.374", 34), ("That is 79% of the fall.", 34),
                     ("a little under 70%", 35), ("12 turbines", None),
                     ("+0.0498 (+0.0200 to +0.0795)", 41), ("+0.0824 (+0.0275 to +0.1405)", 41),
                     ("+0.1251 (+0.0798 to +0.1686)", 41), ("wind's is +0.1118 (-0.0530 to +0.2323)", 41),
                     ("+0.0421 (-0.0335 to +0.1201)", 41), ("0.163 (15 of 92)", 37), ("the gap only 0.009", 37),
                     ("lifts the one-month cell by 0.155 to 0.254 in every", 40), ("by at most 0.029", 40),
                     ("0.447 against 0.451", None), ("0.347 against 0.304", 41)):
            self.assertIn(s, self.doc)
            if k is not None:
                self.assertIn(s, self.notes[k], s)
        self.assertIn("12 turbines", read("README.md"))
        self.assertIn("| failed | 0.447 (240 of 537) against 0.451 (96 of 213) |", self.notes[39])
        self.assertIn("| held | 0.400 (56 of 140) against 0.405 (68 of 168) |", self.notes[39])
        self.assertIn("W4 held by 0.005", self.doc)
        self.assertIn("All technologies together, 1 month after minus first listings:** the interval includes 0 in "
                      "every period", self.notes[41])

    def test_open_plans(self):
        for name in ("q4held-plan.md", "dec2026-plan.md", "oct2026-plan.md"):
            self.assertIn("Status: pre-registered, not yet scored.", read("docs", name))
            self.assertIn("[`%s`](%s)" % (name, name), self.doc)
        self.assertIn('"Next Release Date: November 24, 2026"', read("docs", "oct2026-plan.md"))

    def test_readme_points_here(self):
        readme = read("README.md")
        self.assertIn("**The series in one place.** [`docs/nextmonth-series.md`](docs/nextmonth-series.md) "
                      "(descriptive; it tests nothing new)", readme)
        self.assertIn("27 of its 33 predictions held", readme)


if __name__ == "__main__":
    unittest.main()
