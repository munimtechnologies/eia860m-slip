"""Doc test: what README.md says about the thirtieth to thirty-third results, the plans not yet
scored and the changelog matches the notes themselves (docs/annualids.md, docs/sep2026-plan.md,
docs/sep2026.md, docs/sepretired-plan.md, docs/sepretired.md, docs/retiredentry-plan.md,
docs/retiredentry.md, docs/eia860m-changelog-from-workbooks.md).

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8") as fh:
        return fh.read()


class ReadmeIndexTests(unittest.TestCase):
    def setUp(self):
        self.readme = read("README.md")

    def test_annualids(self):
        doc = read("docs", "annualids.md")
        self.assertIn("2 of 2 predictions held.", doc)
        self.assertIn("| 30 | Retired generators only the monthly file lists are at plants the annual file "
                      "no longer lists (2 of 2 held) | [`annualids.md`](docs/annualids.md) |", self.readme)
        self.assertIn("(thirtieth result, scored; 2 of 2 held)", self.readme)
        for s in ("2,703 generators retired in 2002 to 2025", "(87,678.1 MW)", "2,703 of 2,703"):
            self.assertIn(s, doc)
        self.assertIn("lists 2,703 generators retired in 2002 to 2025 (87,678.1 MW)", self.readme)
        self.assertIn("Every one of the 2,703 is at a plant that the annual 2025 file lists on no sheet.", doc)

    def test_sep2026(self):
        plan, doc = read("docs", "sep2026-plan.md"), read("docs", "sep2026.md")
        self.assertIn("Status: pre-registered, not yet scored.", plan)
        self.assertIn("3 of 4 predictions held. P3 failed.", doc)
        self.assertIn("| 31 | EIA's September 2026 workbook, scored on release against four bars fixed before it was "
                      "published (3 of 4 held) | [`sep2026.md`](docs/sep2026.md) |", self.readme)
        self.assertIn("(thirty-first result, scored; 3 of 4 held)", self.readme)
        self.assertIn("**Each new month, scored on release: September 2026, 3 of 4 held.**", self.readme)
        for s in ("At most 50 generators leave in September 2026.",
                  "Fewer than 10 of the generators that leave in September 2026 were on the Retired sheet"):
            self.assertIn(s, plan)
        for s in ("(+0.40%)", "| P2. At most 50 generators leave | held | 20 |",
                  "| P3. Fewer than 10 of them leave from the Retired sheet | failed | 16 |",
                  "| held | 0.3353 (57 of 170) |", "The 16 are at 15 plants",
                  "only two months had more generators leave the Retired sheet: November 2024"):
            self.assertIn(s, doc)
        for s in ("listed 0.40% more generators than August's", "20 generators left (at most 50 allowed)",
                  "57 of the 170 generators planned for September were listed as operating in it (0.3353",
                  "16 generators left the Retired sheet, at 15 plants, against a bar of fewer than 10",
                  "only November 2024 and January 2024 had more"):
            self.assertIn(s, self.readme)

    def test_sepretired(self):
        doc = read("docs", "sepretired.md")
        self.assertIn("1 of 2 scored predictions held. S2 failed.", doc)
        self.assertIn("| 32 | The 16 generators that left the Retired sheet in September 2026 are nuclear units retired "
                      "before 2002 (1 of 2 held; one bar waits for October 2026) | [`sepretired.md`](docs/sepretired.md) |",
                      self.readme)
        self.assertIn("(thirty-second result, scored against [`docs/sepretired-plan.md`](docs/sepretired-plan.md); "
                      "1 of 2 held so far, one bar waits for October)", self.readme)
        self.assertIn("**The 16 that left are nuclear units retired before 2002.**", self.readme)
        for s in ("all 16 are nuclear units that August 2026's sheet lists as retired between 1972 and 1998, "
                  "8,663.1 MW in all", "September's sheet lists none retired before 2002"):
            self.assertIn(s, self.readme)
        for s in ("All 16 are nuclear. August 2026's Retired sheet lists them as retired between 1972 and 1998.",
                  "8,663.1 MW of nameplate capacity", "| 1517/1 | Maine Yankee |", "| 885/2 | Zion |",
                  "None is retired before 2002 and none has a missing year."):
            self.assertIn(s, doc)

    def test_retiredentry(self):
        doc = read("docs", "retiredentry.md")
        self.assertIn("3 of 4 predictions held. R4 failed: August 2026's workbook has 28 such rows, not 16.", doc)
        self.assertIn("| 33 | August 2026 added 28 nuclear reactors retired before 2002 to the Retired sheet for one "
                      "month (3 of 4 held) | [`retiredentry.md`](docs/retiredentry.md) |", self.readme)
        self.assertIn("(thirty-third result, scored; 3 of 4 held)", self.readme)
        self.assertIn("**August 2026 added 28 reactors retired before 2002, and September removed them all.**",
                      self.readme)
        for s in ("none of the 16 was in any workbook before August 2026",
                  "28 nuclear rows retired from 1963 to 1998 (10,446.1 MW), 12 of them with no plant ID",
                  "September's workbook has none of the 28.", "Catalyst Cooperative had already documented"):
            self.assertIn(s, self.readme)
        for s in ("By the changelog, none of the 16 was listed in any workbook from July 2015 to July 2026",
                  "Together the 28 are 10,446.1 MW", "12 have no plant ID",
                  "Their retirement years run from 1963 to 1998.", "September's has the 11 and none of the 28",
                  "we missed that when we wrote the plan"):
            self.assertIn(s, doc)

    def test_plans_not_scored(self):
        for name in ("dec2026-plan.md", "sepretired-plan.md", "retiredentry-plan.md", "nexttech-plan.md"):
            self.assertIn("Status: pre-registered, not yet scored.", read("docs", name))
        self.assertIn("Pre-registered, not yet scored: [`dec2026-plan.md`](docs/dec2026-plan.md)", self.readme)
        self.assertIn("and [`nexttech-plan.md`](docs/nexttech-plan.md) (whether the fall in the next-month share is "
                      "inside technologies or a change of mix, four predictions and a reproduction check", self.readme)
        nexttech = read("docs", "nexttech-plan.md")
        for s in ("**T0.**", "**T1.**", "**T2.**", "**T3.**", "**T4.**", "1,980 of 4,223", "2,110 of 6,047"):
            self.assertIn(s, nexttech)
        code = read("tools", "annual-flows-candidate", "nexttech.py")
        self.assertIn("KNOWN = {EARLY: (1980, 4223), LATE: (2110, 6047)}", code)
        self.assertIn('EARLY, LATE = ("2016-01", "2019-12"), ("2022-01", "2025-12")', code)
        self.assertNotIn("and [`retiredentry-plan.md`](docs/retiredentry-plan.md) (when the 16", self.readme)
        self.assertIn("was pre-registered in [`docs/retiredentry-plan.md`](docs/retiredentry-plan.md) and is scored "
                      "in the thirty-third result", self.readme)
        self.assertIn("Bar S3 of [`sepretired-plan.md`](docs/sepretired-plan.md) (whether any of the 16 generators "
                      "that left the Retired sheet in September 2026 is listed again in October 2026)", self.readme)
        self.assertIn("**S3.** At most 3 of the 16 are listed again", read("docs", "sepretired-plan.md"))
        self.assertIn("**R4.**", read("docs", "retiredentry-plan.md"))

    def test_links_kept(self):
        for name in ("changelog-revert.md", "history-revert.md", "heldtrace.md", "annualids.md", "sep2026-plan.md",
                     "sep2026.md", "sepretired-plan.md", "sepretired.md", "retiredentry-plan.md", "retiredentry.md",
                     "eia860m-changelog-from-workbooks.md"):
            self.assertIn("(docs/%s)" % name, self.readme)
        self.assertIn("117,756 rows from July 2015 to September 2026 (version 0.1.1", self.readme)
        self.assertIn("117,756 rows in all.", read("docs", "eia860m-changelog-from-workbooks.md"))


if __name__ == "__main__":
    unittest.main()
