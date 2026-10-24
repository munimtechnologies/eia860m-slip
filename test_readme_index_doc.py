"""Doc test: what README.md says about the thirtieth to thirty-seventh results, the plans not yet
scored and the changelog matches the notes themselves (docs/annualids.md, docs/sep2026-plan.md,
docs/sep2026.md, docs/sepretired-plan.md, docs/sepretired.md, docs/retiredentry-plan.md,
docs/retiredentry.md, docs/nexttech-plan.md, docs/nexttech.md, docs/nexttechonce-plan.md,
docs/nexttechonce.md, docs/nextcount-plan.md, docs/nextcount.md, docs/nextheld-plan.md,
docs/nextheld.md, docs/eia860m-changelog-from-workbooks.md).

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import csv
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

    def test_nexttech(self):
        doc = read("docs", "nexttech.md")
        self.assertIn("3 of 4 predictions held, and the reproduction check T0 held. T2 failed", doc)
        self.assertIn("| 34 | Most of the fall in the next-month share is inside technologies: solar and batteries "
                      "fell, gas did not (3 of 4 held) | [`nexttech.md`](docs/nexttech.md) |", self.readme)
        self.assertIn("(thirty-fourth result, scored against [`docs/nexttech-plan.md`](docs/nexttech-plan.md); "
                      "3 of 4 held)", self.readme)
        self.assertIn("**Most of that fall is inside technologies.**", self.readme)
        for s in ("Solar fell from 0.506 to 0.354 and batteries from 0.442 to 0.299.",
                  "the share would still have fallen from 0.469 to 0.374",
                  "about 79% of the fall is inside technologies and 21% is the change of mix",
                  "gas rose from 0.401 to 0.455", "12 turbines", "without it gas is flat"):
            self.assertIn(s, self.readme)
        for s in ("| solar | 0.506 (1,243 of 2,457) | 0.354 (1,292 of 3,654) |",
                  "| batteries | 0.442 (61 of 138) | 0.299 (453 of 1,515) |",
                  "the share would have fallen from 0.469 to 0.374", "That is 79% of the fall.",
                  "The other 21% is the change of mix", "| failed | 0.401 (298 of 743) to 0.455 (191 of 420) |",
                  "from 12 generators", "| Natural Gas Fired Combustion Turbine |",
                  "0.456 (292 of 641) in 2016-2019 and 0.455 (191 of 420) in 2022-2025: flat."):
            self.assertIn(s, doc)
        self.assertIn("## Update, 24 October 2026: counting each generator once", doc)
        self.assertIn("is scored in [`docs/nexttechonce.md`](nexttechonce.md) (thirty-fifth result): 3 of 4 "
                      "predictions held.", doc)

    def test_nexttechonce(self):
        doc = read("docs", "nexttechonce.md")
        self.assertIn("3 of 4 predictions held, and the reproduction check C0 held. O3 failed", doc)
        self.assertIn("| 35 | Counting each generator once, solar and batteries still fall and most of the fall is "
                      "inside technologies; gas rises (3 of 4 held) | [`nexttechonce.md`](docs/nexttechonce.md) |",
                      self.readme)
        self.assertIn("(thirty-fifth result, scored against [`docs/nexttechonce-plan.md`](docs/nexttechonce-plan.md); "
                      "3 of 4 held)", self.readme)
        self.assertIn("**Counting each generator once, the split holds, and repeat listings grew.**", self.readme)
        for s in ("Solar fell from 0.476 to 0.360 and batteries from 0.362 to 0.282",
                  "a little under 70% of the fall is inside technologies", "gas rose by 0.057, against a band of 0.05",
                  "the rise is 0.040", "in 2.39 monthly reports on average, against 1.94 in 2016-2019"):
            self.assertIn(s, self.readme)
        for s in ("| O1. Solar's share, each generator once, is lower in 2022-2025 | held | 0.476 (642 of 1,348) to "
                  "0.360 (557 of 1,549) |", "| held | 0.362 (25 of 69) to 0.282 (154 of 547) |",
                  "That is a little under 70% of the fall", "by 0.057", "and the rise is 0.040, inside the band",
                  "in 2.39 monthly reports on average, against 1.94 in 2016-2019"):
            self.assertIn(s, doc)

    def test_nextcount(self):
        doc = read("docs", "nextcount.md")
        self.assertIn("2 of 3 predictions held, and the reproduction check C0 held. K2 failed", doc)
        self.assertIn("| 36 | After three or more earlier misses, a generator planned for the next month is on time less "
                      "often, and that gap is new since 2016-2019 (2 of 3 held) | [`nextcount.md`](docs/nextcount.md) |",
                      self.readme)
        for s in ("| 0 | 0.459 (969 of 2,110) | 0.362 (866 of 2,393) |", "| 1 | 0.489 (532 of 1,087) | 0.365 (515 of 1,412) |",
                  "| 2 | 0.484 (253 of 523) | 0.357 (301 of 844) |", "| 3+ | 0.449 (226 of 503) | 0.306 (428 of 1,398) |",
                  "| held | 0.010 against 0.056 |", "| 1 month | 0.499 (746 of 1,494) | 0.390 (878 of 2,254) |",
                  "| 2-3 months | 0.492 (225 of 457) | 0.260 (231 of 890) |", "gas and wind give 0.042"):
            self.assertIn(s, doc)
        self.assertIn("the gas plant that skews 2016-2019 does not cause that", self.readme)
        self.assertIn("It works the other way: its 66 generator-months there were on time 6 times.", doc)
        self.assertIn("for solar it is small, and batteries go the other way. These splits were reported, not scored.",
                      self.readme)
        self.assertIn("| solar | 0.361 (536 of 1,483) | 0.332 (265 of 797) |", doc)
        self.assertIn("| batteries | 0.278 (143 of 514) | 0.309 (129 of 417) |", doc)

    def test_nextheld(self):
        doc = read("docs", "nextheld.md")
        self.assertIn("3 of 3 predictions held, and the reproduction check C1 held.", doc)
        self.assertIn("(thirty-seventh result, scored against [`docs/nextheld-plan.md`](docs/nextheld-plan.md); "
                      "3 of 3 held)", self.readme)
        for s in ("| held | 0.270 (66 of 244) against 0.304 (144 of 473) |",
                  "| held | 0.347 (166 of 479) against 0.249 (43 of 173) |", "0.308 (222 of 721) against 0.304",
                  "The H1 gap comes from 5 or more earlier listings: 0.163 (15 of 92).", "the gap only 0.009"):
            self.assertIn(s, doc)

    def test_plans_not_scored(self):
        for name in ("dec2026-plan.md", "sepretired-plan.md", "retiredentry-plan.md", "nexttech-plan.md",
                     "nexttechonce-plan.md", "nextcount-plan.md", "nextheld-plan.md"):
            self.assertIn("Status: pre-registered, not yet scored.", read("docs", name))
        self.assertIn("Pre-registered, not yet scored: [`dec2026-plan.md`](docs/dec2026-plan.md) (whether December "
                      "2026 has the largest next-month group of 2026 and a share above the year's, two bars) and "
                      "[`oct2026-plan.md`](docs/oct2026-plan.md) (EIA's October 2026 workbook, due 24 November 2026, "
                      "scored on release against five bars", self.readme)
        self.assertNotIn("and [`nexttechonce-plan.md`](docs/nexttechonce-plan.md) (whether", self.readme)
        self.assertNotIn("and [`nexttech-plan.md`](docs/nexttech-plan.md) (whether the fall", self.readme)
        self.assertNotIn("Also [`nextcount-plan.md`](docs/nextcount-plan.md) (whether", self.readme)
        # Scored on 24 October 2026 (docs/nextheld.md), so it left the README's list of plans not yet scored.
        self.assertNotIn("Also [`nextheld-plan.md`](docs/nextheld-plan.md) (whether", self.readme)
        self.assertIn("was pre-registered in [`docs/nextheld-plan.md`](docs/nextheld-plan.md) and is scored in the "
                      "thirty-seventh result.", self.readme)
        once = read("docs", "nexttechonce-plan.md")
        for s in ("**C0.**", "**O1.**", "**O2.**", "**O3.**", "**O4.**", "1,980 of 4,223", "2,110 of 6,047",
                  "(0.456, then 0.455)", "102 of the 743 gas generator-months", "14,807 rows", "within 0.05"):
            self.assertIn(s, once)
        code = read("tools", "annual-flows-candidate", "nexttechonce.py")
        for s in ("KNOWN = {EARLY: (1980, 4223), LATE: (2110, 6047)}",
                  'EARLY, LATE = ("2016-01", "2019-12"), ("2022-01", "2025-12")', "COHORT_ROWS = 14807",
                  "GAS_BAND = 0.05", "MIN_COHORT = 30"):
            self.assertIn(s, code)
        self.assertIn('EARLY, LATE = ("2016-01", "2019-12"), ("2022-01", "2025-12")',
                      read("tools", "annual-flows-candidate", "nexttech.py"))
        self.assertIn("was pre-registered in [`docs/retiredentry-plan.md`](docs/retiredentry-plan.md) and is scored "
                      "in the thirty-third result", self.readme)
        self.assertIn("Bar S3 of [`sepretired-plan.md`](docs/sepretired-plan.md) (whether any of the 16 generators "
                      "that left the Retired sheet in September 2026 is listed again in October 2026)", self.readme)
        self.assertIn("**S3.** At most 3 of the 16 are listed again", read("docs", "sepretired-plan.md"))
        self.assertIn("**R4.**", read("docs", "retiredentry-plan.md"))

    def test_oct2026_plan(self):
        plan = read("docs", "oct2026-plan.md")
        self.assertIn("Status: pre-registered, not yet scored.", plan)
        self.assertIn('"Next Release Date: November 24, 2026"', plan)
        with open(os.path.join(HERE, "data", "monthcheck_months_2026-09.csv"), newline="", encoding="utf-8") as fh:
            months = {r["month"]: r for r in csv.DictReader(fh)}
        self.assertIn("within 3%% of September 2026's (%s)" % "{:,}".format(int(months["2026-09"]["listed"])), plan)
        last12 = ["%d-%02d" % (2025 + (9 + i) // 12, (9 + i) % 12 + 1) for i in range(12)]
        self.assertEqual((last12[0], last12[-1]), ("2025-10", "2026-09"))
        left = [months[m]["left"] for m in last12]
        self.assertIn("in the 12 months from October 2025 to September 2026, %s and %s generators left." % (
            ", ".join(left[:-1]), left[-1]), plan)
        self.assertEqual(max(int(x) for x in left), 50)
        retired = {y: sum(int(r["left_retired"]) for m, r in months.items() if lo <= m <= hi)
                   for y, (lo, hi) in (("2025", ("2025-01", "2025-12")), ("2026", ("2026-01", "2026-08")))}
        self.assertEqual((retired["2025"], retired["2026"], months["2026-09"]["left_retired"]), (6, 1, "16"))
        self.assertIn("6 such generators in all of 2025, 1 in January to August 2026, and 16 in September 2026", plan)
        band = sorted((float(r["share_operating"]), m) for m, r in months.items() if "2024-10" <= m <= "2026-09")
        self.assertEqual(len(band), 24)
        self.assertEqual((band[1][1], band[-2][1]), ("2024-10", "2025-12"))
        self.assertIn("that band is %.6f (October 2024) to %.6f (December 2025)" % (band[1][0], band[-2][0]), plan)
        self.assertIn("0.219512 in October 2024 and %s in October 2025" % months["2025-10"]["share_operating"], plan)
        for s in ("**P1.**", "**P2.**", "**P3.**", "**P4.**", "**P5.**", '"N of 5 held"', "Bar S3 of"):
            self.assertIn(s, plan)

    def test_links_kept(self):
        for name in ("changelog-revert.md", "history-revert.md", "heldtrace.md", "annualids.md", "sep2026-plan.md",
                     "sep2026.md", "sepretired-plan.md", "sepretired.md", "retiredentry-plan.md", "retiredentry.md",
                     "nexttech-plan.md", "nexttech.md", "nexttechonce-plan.md", "nexttechonce.md",
                     "nextcount-plan.md", "nextcount.md", "nextheld-plan.md", "nextheld.md",
                     "eia860m-changelog-from-workbooks.md"):
            self.assertIn("(docs/%s)" % name, self.readme)
        self.assertIn("117,756 rows from July 2015 to September 2026 (version 0.1.1", self.readme)
        self.assertIn("117,756 rows in all.", read("docs", "eia860m-changelog-from-workbooks.md"))


if __name__ == "__main__":
    unittest.main()
