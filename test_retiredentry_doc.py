"""Doc test: the numbers in docs/retiredentry.md match the raw output of job retiredentry-v1
(docs/retiredentry-v1-output.md, docs/retiredentry-v1-stdout.txt, docs/retiredentry-v1-unittests.txt,
data/retiredentry_keys.csv, data/retiredentry_log_rows.csv, data/retiredentry_nuclear.csv), and the
plant names it compares match data/sepretired_rows.csv.

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


def year(x):
    return int(x) if x.strip().isdigit() else None


def old(r):
    """A nuclear row retired before 2002, or on a Retired sheet with no year (as retiredentry.old_nuclear)."""
    y = year(r["retirement_year"])
    return "nuclear" in r["technology"].lower() and (
        (y is not None and y < 2002) or (y is None and r["sheet"].lower().startswith("retired")))


def mw(rs):
    return "{:,.1f}".format(sum(float(r["nameplate_mw"]) for r in rs))


class RetiredentryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs", "retiredentry.md")
        cls.plan = read("docs", "retiredentry-plan.md")
        cls.out = read("docs", "retiredentry-v1-output.md")
        cls.log = read("docs", "retiredentry-v1-stdout.txt")
        cls.ut = read("docs", "retiredentry-v1-unittests.txt")
        cls.keys = rows("data", "retiredentry_keys.csv")
        cls.hist = rows("data", "retiredentry_log_rows.csv")
        cls.nuc = rows("data", "retiredentry_nuclear.csv")
        cls.sep = rows("data", "sepretired_rows.csv")

    def month(self, m):
        return [r for r in self.nuc if r["month"] == m]

    def test_status(self):
        self.assertIn("Status: pre-registered, not yet scored.", self.plan)
        self.assertIn("gives exactly 16.", self.plan)
        self.assertIn("Held: 3 of 4 scored.", self.out)
        for s in ("| R1 | held | 16 of 16 reach it; month(s): 2026-08 |", "| R2 | held | 16 of 16 |",
                  "| R3 | held | 16 of 16 on it every month from arrival to 2026-08 |", "| R4 | failed | 28 rows |"):
            self.assertIn(s, self.out)
        self.assertIn("3 of 4 predictions held. R4 failed: August 2026's workbook has 28 such rows, not 16.", self.doc)
        for s in ("| held | 16 of 16, all in August 2026 |", "| held | 16 of 16 |", "| failed | 28 |"):
            self.assertIn(s, self.doc)

    def test_order(self):
        self.assertTrue(self.log.startswith("2026-10-23T21:05:41Z plan served: "))
        self.assertNotIn("not served yet", self.log)
        self.assertLess(self.log.index("plan served:"), self.log.index("changelog 1054060 bytes, 117756 rows"))
        self.assertIn("was served the plan on its first poll at 21:05:41 UTC", self.doc)
        self.assertIn("Expected 1054060 bytes and 117756 rows: True.", self.out)
        self.assertIn("(1,054,060 bytes, 117,756 rows, the expected file)", self.doc)
        self.assertIn("September file is the one monthcheck-sep2026-v1 read (14013970 bytes, md5 "
                      "4c741eb77a5ccad5aca32ffe43f398af): True.", self.out)
        self.assertIn("(14,013,970 bytes, md5 4c741eb77a5ccad5aca32ffe43f398af, the same file", self.doc)
        self.assertIn("Ran 11 tests", self.ut)
        self.assertIn("\nOK", self.ut)
        self.assertIn("after its 11 unit tests passed", self.doc)

    def test_keys(self):
        k = self.keys
        self.assertEqual(len(k), 16)
        self.assertEqual({(x["arrival_month"], x["arrival_event"], x["arrival_from"], x["where_before"],
                           x["other_rows"], x["left_sep"], x["technology_then"]) for x in k},
                         {("2026-08", "first", "never listed", "not listed", "0", "True", "Nuclear")})
        self.assertTrue(all(x["retirement_year_then"] == x["retirement_year_aug"] for x in k))
        self.assertEqual(mw([{"nameplate_mw": x["nameplate_mw_then"]} for x in k]), "8,663.1")
        by = collections.defaultdict(list)
        for r in self.hist:
            by[r["key"]].append((r["report_month"], r["event"], r["sheet"]))
        self.assertEqual(set(by), {x["key"] for x in k})
        self.assertEqual({tuple(v) for v in by.values()},
                         {(("2026-08", "first", "Retired"), ("2026-09", "left", ""))})
        self.assertIn('Each has exactly two changelog rows: "first" in August 2026 and "left" in September 2026.',
                      self.doc)

    def test_r4(self):
        aug = [r for r in self.month("2026-08") if old(r)]
        self.assertEqual(len(aug), 28)
        self.assertEqual({r["sheet"] for r in aug}, {"Retired"})
        keyed = [r for r in aug if r["plant_id"] != "-"]
        bare = [r for r in aug if r["plant_id"] == "-"]
        self.assertEqual((len(keyed), len(bare)), (16, 12))
        self.assertEqual({"%s/%s" % (r["plant_id"], r["generator_id"]) for r in keyed},
                         {x["key"] for x in self.keys})
        self.assertEqual((mw(keyed), mw(bare), mw(aug)), ("8,663.1", "1,783.0", "10,446.1"))
        years = [year(r["retirement_year"]) for r in aug]
        self.assertEqual((min(years), max(years)), (1963, 1998))
        self.assertIn("Together the 28 are 10,446.1 MW of nameplate capacity as the sheet gives it: 8,663.1 MW "
                      "with plant IDs and 1,783.0 MW without. Their retirement years run from 1963 to 1998.", self.doc)
        self.assertEqual({r["generator_id"] for r in bare}, {"1"})
        for r in bare:
            self.assertIn("| %s | %s | %s |" % (r["plant_name"], r["retirement_year"], r["nameplate_mw"]), self.doc)
        for m in ("2026-07", "2026-09"):
            self.assertEqual([r for r in self.month(m) if old(r)], [])

    def test_months(self):
        def ret(m):
            return [r for r in self.month(m) if r["sheet"].lower().startswith("retired")
                    and "nuclear" in r["technology"].lower()]
        self.assertEqual([len(ret(m)) for m in ("2026-07", "2026-08", "2026-09")], [11, 39, 11])
        jul = {(r["plant_id"], r["generator_id"], r["retirement_year"]) for r in ret("2026-07")}
        sep = {(r["plant_id"], r["generator_id"], r["retirement_year"]) for r in ret("2026-09")}
        self.assertEqual(jul, sep)
        self.assertEqual((min(int(y) for _, _, y in jul), max(int(y) for _, _, y in jul)), (2013, 2021))
        self.assertTrue(jul <= {(r["plant_id"], r["generator_id"], r["retirement_year"]) for r in ret("2026-08")})
        for s in ("| 2026-07 | 7299 | 2002 or later 7299 | 0 | none |",
                  "| 2026-08 | 7324 | 2002 or later 7308; before 2002 16 | 16 | none |",
                  "| 2026-09 | 7321 | 2002 or later 7321 | 0 | none |",
                  "| 2026-08 | Operating 96; Retired 39; Canceled or Postponed 16; Planned 5 | 28 |"):
            self.assertIn(s, self.out)
        for s in ("| July 2026 | 11 | 0 | 7,299, all retired 2002 or later |",
                  "| August 2026 | 39 | 28 | 7,324: 7,308 retired 2002 or later and 16 before 2002 |",
                  "| September 2026 | 11 | 0 | 7,321, all retired 2002 or later |",
                  "all retired from 2013 to 2021"):
            self.assertIn(s, self.doc)

    def test_names(self):
        aug = {"%s/%s" % (r["plant_id"], r["generator_id"]): r["plant_name"]
               for r in self.month("2026-08") if old(r) and r["plant_id"] != "-"}
        diff = sorted((k.split("/")[0], aug[k], x["plant_name"]) for x in self.sep for k in [x["key"]]
                      if aug[k] != x["plant_name"])
        self.assertEqual(diff, [("4143", "Genoa (Lacrosse)", "Genoa"),
                                ("8011", "Three Mile Island", "Crane Clean Energy Center"),
                                ("869", "Dresden", "Dresden Generating Station")])
        self.assertIn("Three Mile Island (plant 8011, given there as Crane Clean Energy Center), Dresden (869, "
                      "Dresden Generating Station) and Genoa (Lacrosse) (4143, Genoa)", self.doc)

    def test_prior_art(self):
        self.assertIn("No EIA source we found says this", self.plan)
        for s in ('The plan said "No EIA source we found says this"', "we missed that when we wrote the plan",
                  "Notable Irregularities", "https://github.com/catalyst-cooperative/pudl/issues/5677",
                  "for the first time lists 21 historically retired reactors"):
            self.assertIn(s, self.doc)
        self.assertIn("for the first time lists 21 historically retired reactors", self.plan)


if __name__ == "__main__":
    unittest.main()
