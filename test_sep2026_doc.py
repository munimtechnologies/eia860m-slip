"""Doc test: the numbers in docs/sep2026.md, docs/sepretired-plan.md and the 0.1.1 lines of
docs/eia860m-changelog-from-workbooks.md match the raw output of job monthcheck-sep2026-v1
(docs/monthcheck-sep2026-v1-output.md, docs/monthcheck-sep2026-v1-gapcensus.md,
data/monthcheck_months_2026-09.csv, data/gapcensus_left_events_2026-09.csv and the changelog itself)
and of job annual860-v1 (docs/annual860-v1-output.md, data/annual860_monthly_not_annual.csv).

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import collections
import csv
import gzip
import io
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SEP, AUG = "2026-09", "2026-08"


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8") as fh:
        return fh.read()


def rows(*parts):
    with open(os.path.join(HERE, *parts), newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def fmt(n):
    return "{:,}".format(n)


def mw(v):
    return "{:,.1f}".format(float(v))


class Sep2026Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs", "sep2026.md")
        cls.plan = read("docs", "sep2026-plan.md")
        cls.splan = read("docs", "sepretired-plan.md")
        cls.out = read("docs", "monthcheck-sep2026-v1-output.md")
        cls.gc = read("docs", "monthcheck-sep2026-v1-gapcensus.md")
        cls.months = {r["month"]: r for r in rows("data", "monthcheck_months_2026-09.csv")}
        cls.events = rows("data", "gapcensus_left_events_2026-09.csv")
        cls.retired = collections.defaultdict(list)
        for e in cls.events:
            if e["sheet_before"] == "Retired":
                cls.retired[e["month_left"]].append(e)
        cls.keys = sorted(e["key"] for e in cls.retired[SEP])

    def test_status(self):
        self.assertIn("Status: pre-registered, not yet scored.", self.plan)
        self.assertIn("Pre-registration: docs/sep2026-plan.md. Mode: scored (EIA's own file, appended).", self.out)
        self.assertIn("Held: 3 of 4 scored.", self.out)
        self.assertIn("# EIA's September 2026 EIA-860M workbook, scored on release: 3 of 4 held", self.doc)
        self.assertIn("fixed before EIA published the file): 3 of 4 predictions held. P3 failed.", self.doc)

    def test_file(self):
        self.assertIn("Plan: append. URL: https://www.eia.gov/electricity/data/eia860m/xls/september_generator2026.xlsx."
                      " Bytes: 14013970. md5: 4c741eb77a5ccad5aca32ffe43f398af.", self.gc)
        self.assertIn("september_generator2026.xlsx, 14,013,970 bytes, md5 4c741eb77a5ccad5aca32ffe43f398af.", self.doc)
        self.assertIn("Rows appended: 646 (back 1, changed 455, first 170, left 20).", self.gc)
        m = self.months[SEP]
        self.assertEqual((int(m["first"]), int(m["changed"]), int(m["left"]), int(m["back"])), (170, 455, 20, 1))
        self.assertIn("appended 646 rows to the rebuilt changelog: 170 first, 455 changed, 20 left and 1 back.", self.doc)

    def test_p1_p2(self):
        s, a = int(self.months[SEP]["listed"]), int(self.months[AUG]["listed"])
        pct = "{:+.2f}%".format((s - a) / a * 100)
        self.assertEqual((s, a, pct), (38162, 38011, "+0.40%"))
        self.assertIn("| P1 | held | listed %d vs %d in 2026-08 (%s); readable True |" % (s, a, pct), self.out)
        self.assertIn("| held | %s against %s (%s) |" % (fmt(s), fmt(a), pct), self.doc)
        m = self.months[SEP]
        left = int(m["left"])
        self.assertEqual(left, int(m["left_operating"]) + int(m["left_planned"]) + int(m["left_retired"]))
        self.assertEqual(len([e for e in self.events if e["month_left"] == SEP]), left)
        self.assertIn("| P2 | held | %d left | at most 50 |" % left, self.out)
        self.assertIn("| P2. At most 50 generators leave | held | %d |" % left, self.doc)
        self.assertIn("Of the %d generators that left, %d were on the Retired sheet in August, %d on the Operating sheet "
                      "and %d on the Planned sheet." % (left, int(m["left_retired"]), int(m["left_operating"]),
                                                        int(m["left_planned"])), self.doc)

    def test_p3(self):
        ret = self.retired[SEP]
        self.assertEqual((len(ret), int(self.months[SEP]["left_retired"])), (16, 16))
        self.assertTrue(all(e["outcome"] == "not_back" for e in ret))
        self.assertIn("| P3 | failed | 16 left from Retired | fewer than 10 |", self.out)
        self.assertIn("| P3. Fewer than 10 of them leave from the Retired sheet | failed | 16 |", self.doc)
        self.assertEqual(len({k.split("/")[0] for k in self.keys}), 15)
        self.assertEqual([k for k in self.keys if k.startswith("885/")], ["885/1", "885/2"])
        self.assertIn("The 16 are at 15 plants (885/1 and 885/2 share one).", self.doc)

    def test_record(self):
        since = {mo: es for mo, es in self.retired.items() if mo >= "2017-04"}
        self.assertEqual(sorted(mo for mo, es in since.items() if len(es) > 16), ["2024-01", "2024-11"])
        nov, jan = since["2024-11"], since["2024-01"]
        self.assertEqual((len(nov), sum(1 for e in nov if e["outcome"] == "back_1")), (277, 277))
        self.assertEqual((len(jan), {e["key"].split("/")[0] for e in jan}), (23, {"1439"}))
        self.assertIn("November 2024 (277, the gap in EIA's own file; all 277 were back the next month) and "
                      "January 2024 (23, all at plant 1439)", self.doc)
        plants = [len({e["key"].split("/")[0] for e in es}) for mo, es in since.items() if mo not in ("2024-11", SEP)]
        self.assertEqual(max(plants), 2)
        self.assertIn("the generators that left the Retired sheet were at no more than 2 plants", self.doc)
        y2025 = sum(len(es) for mo, es in self.retired.items() if mo.startswith("2025-"))
        y2026 = sum(len(es) for mo, es in self.retired.items() if "2026-01" <= mo <= "2026-08")
        self.assertEqual((y2025, y2026), (6, 1))
        self.assertIn("The plan's record was %d in all of 2025 and %d in January to August 2026." % (y2025, y2026),
                      self.doc)
        self.assertIn("gapcensus-v1 counted 6 such generators in all of 2025 and 1 in January to August 2026", self.plan)

    def test_annual860(self):
        out = read("docs", "annual860-v1-output.md")
        self.assertIn("Monthly Retired sheet: 7324 generators, 7268 retired 2002 to 2025; of those, 4565 also annual "
                      "retired (same retirement year: 4565) and 2703 not.", out)
        self.assertIn("Annual retired (status RE, retired 2002 to 2025): 4565 (209132.0 MW).", out)
        self.assertIn("Where the 2026-08 workbook lists them: Retired 4565.", out)
        extra = {r["key"] for r in rows("data", "annual860_monthly_not_annual.csv") if r["month"] == AUG}
        self.assertEqual(len(extra), 2703)
        self.assertFalse(set(self.keys) & extra)
        self.assertEqual(7324 - 7268, 56)
        self.assertIn("none of the 16 is among the 2,703 generators that only the monthly Retired sheet lists as "
                      "retired in 2002 to 2025", self.doc)
        self.assertIn("one of the 56 generators on August's Retired sheet whose retirement year is not in 2002 to 2025 "
                      "(7,324 on the sheet, 7,268 retired in 2002 to 2025)", self.doc)
        self.assertIn("That job also counted 7,324 generators on August's Retired sheet, 7,268 of them retired in 2002 "
                      "to 2025, and all 4,565 that the annual 2025 file lists as retired in those years are among them.",
                      self.splan)
        self.assertIn("or one of the 56 on August's sheet whose retirement year is not in 2002 to 2025", self.splan)

    def test_keys(self):
        listed = re.search(r"The 16 keys: (.+?) \(job", self.splan).group(1)
        self.assertEqual(sorted(re.findall(r"\d+/\w+", listed)), self.keys)
        code = read("tools", "annual-flows-candidate", "sepretired.py")
        tup = re.search(r"^KEYS = \((.+?)\)$", code, re.M | re.S).group(1)
        self.assertEqual(sorted(re.findall(r'"([^"]+)"', tup)), self.keys)
        self.assertIn("Status: pre-registered, not yet scored.", self.splan)
        for s in ("**S1.** All 16 are on no sheet of the September 2026 workbook at all",
                  "**S2.** At least 12 of the 16 are listed as retired by the annual EIA-860 2025 file",
                  "**S3.** At most 3 of the 16 are listed again"):
            self.assertIn(s, self.splan)
        self.assertIn("S2_MIN = 12", code)
        self.assertIn("S3_MAX = 3", code)

    def test_p4_cohort(self):
        m = self.months[SEP]
        n, k = int(m["cohort"]), int(m["cohort_operating"])
        planned, absent = int(m["cohort_planned"]), int(m["cohort_absent"])
        self.assertEqual((n, k, planned, absent, int(m["cohort_retired"]), int(m["cohort_other"])),
                         (170, 57, 112, 1, 0, 0))
        self.assertEqual(k + planned + absent, n)
        self.assertIn("| P4 | held | %.4f (%d of %d) | 0.2195 to 0.4740 (2024-09 to 2026-08) |" % (k / n, k, n),
                      self.out)
        self.assertIn("| held | %.4f (%d of %d) |" % (k / n, k, n), self.doc)
        window = [r for mo, r in self.months.items() if "2024-09" <= mo <= "2026-08"]
        shares = sorted(int(r["cohort_operating"]) / int(r["cohort"]) for r in window)
        self.assertEqual((len(shares), "%.4f" % shares[1], "%.4f" % shares[-2]), (24, "0.2195", "0.4740"))
        self.assertIn("The share to Operating lies in the band 0.2195 to 0.4740", self.doc)
        self.assertIn("The month before, %d generators (%s MW) were listed as planned to start operating in "
                      "September 2026." % (n, mw(m["cohort_mw"])), self.doc)
        self.assertIn("September lists %d of them as Operating (%s MW), %d still on the Planned sheet (%s MW; %d of them "
                      "with a later planned month) and %d on no sheet the changelog reads (%s MW)." % (
                          k, mw(m["cohort_mw_operating"]), planned, mw(m["cohort_mw_planned"]),
                          int(m["planned_later"]), absent, mw(m["cohort_mw_absent"])), self.doc)
        self.assertIn("The share, %.4f, is inside the band." % (k / n), self.doc)

    def test_2026(self):
        ms = [r for mo, r in self.months.items() if mo.startswith("2026-")]
        n, k = sum(int(r["cohort"]) for r in ms), sum(int(r["cohort_operating"]) for r in ms)
        self.assertEqual((len(ms), k, n), (9, 423, 1364))
        self.assertIn("January to September 2026 pooled is %s of %s (%.3f)." % (fmt(k), fmt(n), k / n), self.doc)
        top = sorted(ms, key=lambda r: -int(r["cohort"]))[:3]
        self.assertEqual([(r["month"], int(r["cohort"])) for r in top], [("2026-06", 216), ("2026-09", 170),
                                                                          ("2026-04", 168)])
        self.assertIn("The largest next-month cohort of 2026 so far is June's 216; September's 170 is the second "
                      "largest.", self.doc)

    def test_dataset(self):
        self.assertIn("Same text through 2026-08: True. Lines: published 117111, rebuilt 117111. First difference: "
                      "none.", self.gc)
        self.assertIn("Rebuilt rows: 117756 (eia860m_changelog_from_workbooks.csv.gz).", self.gc)
        with gzip.open(os.path.join(HERE, "data", "eia860m_changelog_from_workbooks.csv.gz"), "rb") as fh:
            log = list(csv.DictReader(io.TextIOWrapper(fh, encoding="utf-8", newline="")))
        self.assertEqual(len(log), 117756)
        self.assertEqual(sum(1 for r in log if r["report_month"] <= AUG), 117110)
        sep = [r for r in log if r["report_month"] == SEP]
        self.assertEqual(collections.Counter(r["event"] for r in sep),
                         collections.Counter({"changed": 455, "first": 170, "left": 20, "back": 1}))
        self.assertEqual(max(r["report_month"] for r in log), SEP)
        left = {r["key"] for r in sep if r["event"] == "left"}
        self.assertTrue(set(self.keys) <= left)
        self.assertIn("is now version 0.1.1: 117,756 rows, July 2015 to September 2026.", self.doc)
        self.assertIn("(117,111 lines with the header)", self.doc)
        ds = read("docs", "eia860m-changelog-from-workbooks.md")
        for s in ("2015-07 to 2026-09 (preliminary, 0.1.1)",
                  "september_generator2026.xlsx, 14,013,970 bytes, md5 4c741eb77a5ccad5aca32ffe43f398af), read by "
                  "job monthcheck-sep2026-v1 with the same reader: 646 rows (170 first, 455 changed, 20 left, 1 back), "
                  "117,756 rows in all.",
                  "**0.1.0** (22 October 2026): July 2015 to August 2026, 117,110 rows",
                  "in September 2026, 16 generators at 15 plants left the Retired sheet"):
            self.assertIn(s, ds)


if __name__ == "__main__":
    unittest.main()
