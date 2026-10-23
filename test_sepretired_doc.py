"""Doc test: the numbers in docs/sepretired.md match the raw output of job sepretired-v1
(docs/sepretired-v1-output.md, docs/sepretired-v1-stdout.txt, data/sepretired_rows.csv), and the
keys and years that docs/retiredentry-plan.md and tools/annual-flows-candidate/retiredentry.py take
from it are the same.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import collections
import csv
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8") as fh:
        return fh.read()


def rows(*parts):
    with open(os.path.join(HERE, *parts), newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


class SepretiredTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs", "sepretired.md")
        cls.plan = read("docs", "sepretired-plan.md")
        cls.out = read("docs", "sepretired-v1-output.md")
        cls.log = read("docs", "sepretired-v1-stdout.txt")
        cls.rows = rows("data", "sepretired_rows.csv")

    def test_status(self):
        self.assertIn("Status: pre-registered, not yet scored.", self.plan)
        self.assertIn("Held: 1 of 2 scored.", self.out)
        self.assertIn("commit a3ce085, fixed before job sepretired-v1 read anything about these generators): "
                      "1 of 2 scored predictions held. S2 failed.", self.doc)
        self.assertIn("| S1 | held | 16 of 16 on no sheet of the 2026-09 workbook |", self.out)
        self.assertIn("| S2 | failed | 0 of 16 listed as retired (RE, 2002-2025) by the annual EIA-860 2025 |", self.out)
        self.assertIn("| S3 | not scored yet |", self.out)
        self.assertIn("| held | 16 of 16 |", self.doc)
        self.assertIn("| failed | 0 of 16 |", self.doc)

    def test_order(self):
        self.assertIn("2026-10-23T19:07:11Z plan not served yet: HTTPError: HTTP Error 404", self.log)
        self.assertIn("2026-10-23T19:17:11Z plan served:", self.log)
        first = self.log.index("plan served:")
        self.assertLess(first, self.log.index("august PUDL archive"))
        self.assertIn("got a 404, and was first served the plan at 19:17:11 UTC", self.doc)
        self.assertIn("September file is the one monthcheck-sep2026-v1 read (14013970 bytes, md5 "
                      "4c741eb77a5ccad5aca32ffe43f398af): True.", self.out)
        self.assertIn("(14,013,970 bytes, md5 4c741eb77a5ccad5aca32ffe43f398af, the same file", self.doc)

    def test_rows(self):
        r = self.rows
        self.assertEqual(len(r), 16)
        self.assertEqual({x["technology"] for x in r}, {"Nuclear"})
        self.assertEqual({x["scope"] for x in r}, {"before 2002"})
        self.assertEqual({x["where_sep"] for x in r}, {"not listed"})
        self.assertEqual({(x["annual"], x["annual_retired"]) for x in r}, {("not listed", "False")})
        years = [int(x["retirement_year"]) for x in r]
        self.assertEqual((min(years), max(years)), (1972, 1998))
        self.assertEqual("{:,.1f}".format(sum(float(x["nameplate_mw"]) for x in r)), "8,663.1")
        self.assertEqual(len({x["key"].split("/")[0] for x in r}), 15)
        self.assertEqual(len({x["state"] for x in r}), 9)
        self.assertIn("lists them as retired between 1972 and 1998. Together they are 8,663.1 MW of nameplate "
                      "capacity, at 15 plants in 9 states.", self.doc)
        self.assertIn("Together: 8663.1 MW on August's Retired sheet, at 15 plants.", self.out)
        for x in r:
            self.assertIn("| %s | %s | %s | %s/%s | %s |" % (x["key"], x["plant_name"], x["state"],
                                                             x["retirement_month"], x["retirement_year"],
                                                             x["nameplate_mw"]), self.doc)

    def test_plants(self):
        by = {x["key"].split("/")[0]: x["plant_sep"] for x in self.rows}
        none = [p for p, s in by.items() if s == "none"]
        op = [p for p, s in by.items() if "Operating" in s]
        ret_only = sorted(s for p, s in by.items() if s != "none" and "Operating" not in s)
        self.assertEqual((len(none), len(op), ret_only), (7, 6, ["Retired 1", "Retired 2"]))
        self.assertIn("At 7 of the 15 plants, the September workbook lists no generator at all. The other 8", self.doc)
        self.assertIn("on the Operating sheet at 6 of them (for example 5 at Fermi and 10 at Humboldt Bay)", self.doc)
        self.assertEqual((by["1729"], by["246"], by["360"], by["4143"]),
                         ("Operating 5", "Operating 10; Retired 2", "Retired 2", "Retired 1"))
        self.assertIn("only on the Retired sheet at San Onofre (2) and Genoa (1)", self.doc)

    def test_sheet(self):
        self.assertIn("Generators on the Retired sheet: 7324 in 2026-08, 7321 in 2026-09. By retirement year, "
                      "2026-08: 2002-2025 7268; after 2025 40; before 2002 16; 2026-09: 2002-2025 7270; "
                      "after 2025 51.", self.out)
        self.assertEqual((7268 + 40 + 16, 7270 + 51), (7324, 7321))
        self.assertIn("Left the sheet: 16 (8663.1 MW). By retirement year: before 2002 16. Where September lists "
                      "them: not listed 16.", self.out)
        self.assertIn("Entered the sheet: 13 (20.5 MW). By retirement year: after 2025 11; 2002-2025 2. Where August "
                      "listed them: Operating 13.", self.out)
        for s in ("7,324 generators: 7,268 retired in 2002 to 2025, 40 after 2025 and 16 before 2002",
                  "7,321 generators: 7,270 retired in 2002 to 2025 and 51 after 2025",
                  "16 left (8,663.1 MW), all before 2002. 13 entered (20.5 MW), all from the Operating sheet: "
                  "11 retired after 2025 and 2 in 2002 to 2025."):
            self.assertIn(s, self.doc)

    def test_census(self):
        for m in ("2026-08", "2026-09"):
            self.assertIn("Annual retired (status RE, retired 2002 to 2025): 4565 (209132.0 MW). Where the %s "
                          "workbook lists them: Retired 4565. On no sheet of it: 0 (0 MW)." % m, self.out)
        self.assertIn("Monthly Retired sheet: 7324 generators, 7268 retired 2002 to 2025; of those, 4565 also annual "
                      "retired and 2703 not.", self.out)
        self.assertIn("Monthly Retired sheet: 7321 generators, 7270 retired 2002 to 2025; of those, 4565 also annual "
                      "retired and 2705 not.", self.out)
        self.assertIn("All 4,565 generators the annual file lists as retired in 2002 to 2025 are on September's "
                      "Retired sheet", self.doc)
        self.assertIn("The monthly sheet lists 2,705 more retired in those years, against 2,703 in August.", self.doc)

    def test_followup(self):
        plan = read("docs", "retiredentry-plan.md")
        code = read("tools", "annual-flows-candidate", "retiredentry.py")
        self.assertIn("Status: pre-registered, not yet scored.", plan)
        for s in ("**R1.**", "**R2.**", "**R3.**", "**R4.**", "gives exactly 16.",
                  "lists as retired between 1972 and 1998"):
            self.assertIn(s, plan)
        for x in self.rows:
            self.assertIn('"%s": %s' % (x["key"], x["retirement_year"]), code)
        self.assertEqual(collections.Counter(x["technology"] for x in self.rows), collections.Counter({"Nuclear": 16}))
        self.assertIn('SHA = "a3ce0851c47d820ba5f8a0556358b4abef960909"', code)
        self.assertIn("[`docs/retiredentry-plan.md`](retiredentry-plan.md) sets four predictions", self.doc)


if __name__ == "__main__":
    unittest.main()
