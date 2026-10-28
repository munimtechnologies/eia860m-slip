"""Checks docs/nextlist-title-fix.md (the October 2026 list's page title, fixed on 28 October 2026) against the
raw output of compete job nltitle-v1 (data/nltitle_compare.json, data/nltitle_rebuilt.json,
docs/nextlist-2026-10.md, docs/nltitle-v1-unittests.txt, docs/nltitle-v1-title-tools-tests.txt,
docs/nltitle-v1-md5.txt) and the published 0.1.0 run record (data/nextlist_v1.json).
MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TITLE = ("# nextlist 0.1.1: EIA-860M generators planned for 2026-10, with the on-time share of earlier ones like "
         "them")
OLD_SIZE, NEW_SIZE = "55913 bytes", "55901 bytes"
CSVS = (("nextlist_2026-10.csv", 25247), ("nextlist_2026-09.csv", 26923), ("nextlist_backtest_months.csv", 7869))


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8") as fh:
        return fh.read()


def ran_ok(log):
    ran = int(re.search(r"Ran (\d+) tests", log).group(1))
    ok = len(re.findall(r" \.\.\. ok$", log, re.M))
    return ran, ok, log.rstrip().endswith("OK")


class NextlistTitleDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = read("docs", "nextlist-title-fix.md")
        cls.cmp = json.loads(read("data", "nltitle_compare.json"))
        cls.old = json.loads(read("data", "nextlist_v1.json"))
        cls.new = json.loads(read("data", "nltitle_rebuilt.json"))
        cls.page = read("docs", "nextlist-2026-10.md").split("\n")
        cls.md5s = dict(line.split() for line in read("docs", "nltitle-v1-md5.txt").splitlines() if line.strip())

    def test_status(self):
        self.assertIn("Status: correction of a display bug; nothing is scored and no number changes. The check "
                      "fixed before the rebuild (T1) failed as written; the reason is below.", self.text)
        self.assertFalse(self.cmp["held"])
        self.assertIn("So T1 failed.", self.text)

    def test_title(self):
        self.assertEqual(self.page[0], TITLE)
        self.assertEqual(self.cmp["page"]["rebuilt_title"], TITLE)
        self.assertIn("{:,} characters on line 1".format(self.cmp["page"]["published_title_chars"]), self.text)
        self.assertEqual((self.old["version"], self.new["version"]), ("0.1.0", "0.1.1"))

    def test_csvs(self):
        for name, size in CSVS:
            c = self.cmp["csv"][name]
            self.assertTrue(c["identical"])
            self.assertEqual((c["published_bytes"], c["rebuilt_bytes"]), (size, size))
            self.assertIn("%s {:,} bytes".format(size) % name, self.text)
        self.assertIn("- (b) held: the three CSV files are byte-identical", self.text)

    def test_page_lines(self):
        p = self.cmp["page"]
        self.assertEqual((p["published_lines"], p["rebuilt_lines"]), (511, 511))
        self.assertEqual(len(self.page), 511)
        self.assertEqual(p["lines_differ"], [1, 14])
        self.assertFalse(p["held"])
        self.assertIn("- (a) failed: both pages have 511 lines, and lines 1 and 14 differ.", self.text)

    def test_line_14_is_the_redirect_log(self):
        wb_new = {w["month"]: w for w in self.new["workbooks"]}
        wb_old = {w["month"]: w for w in self.old["workbooks"]}
        err_new, err_old = wb_new["2026-08"]["errors"], wb_old["2026-08"]["errors"]
        self.assertEqual(len(err_new), 1)
        self.assertEqual(self.page[13], "- 2026-08: " + err_new[0])
        self.assertIn(NEW_SIZE, err_new[0])
        self.assertIn(OLD_SIZE, err_old[0])
        self.assertEqual(err_old[0].replace(OLD_SIZE, NEW_SIZE), err_new[0])
        self.assertIn("final URL https://www.eia.gov/electricity/,", err_new[0])
        self.assertIn("The log records that page's size: 55,913 bytes on 27 October and 55,901 bytes on 28 October.",
                      self.text)
        self.assertIn('Replacing "%s" with "%s" in the published JSON' % (OLD_SIZE, NEW_SIZE), self.text)

    def test_workbooks_otherwise_identical(self):
        fixed = json.loads(json.dumps(self.old["workbooks"]).replace(OLD_SIZE, NEW_SIZE))
        self.assertEqual(fixed, self.new["workbooks"])
        for w in self.new["workbooks"]:
            self.assertTrue(w["same_as_expected"])
            self.assertIn(w["md5"], self.text)
        self.assertEqual({w["month"] for w in self.new["workbooks"]}, {"2026-08", "2026-09"})

    def test_json_keys(self):
        keys = sorted(set(self.old) | set(self.new))
        differ = [k for k in keys if self.old.get(k) != self.new.get(k)]
        self.assertEqual(differ, ["finished_at", "started_at", "version", "workbooks"])
        self.assertEqual(self.cmp["json"]["keys_differ"], differ)
        self.assertFalse(self.cmp["json"]["held"])
        self.assertIn("- (c) failed: the JSON differs in version, started_at, finished_at and workbooks.", self.text)
        self.assertTrue(self.new["started_at"].startswith("2026-10-28"))
        self.assertIn("Job nltitle-v1 ran on 28 October 2026", self.text)

    def test_unit_tests(self):
        ran, ok, passed = ran_ok(read("docs", "nltitle-v1-unittests.txt"))
        self.assertEqual((ran, ok, passed), (17, 17, True))
        self.assertIn("test_title_names_the_month (test_nextlist.Title.test_title_names_the_month) ... ok",
                      read("docs", "nltitle-v1-unittests.txt"))
        self.assertIn("The patched tool passed %d of %d unit tests" % (ok, ran), self.text)
        ran, ok, passed = ran_ok(read("docs", "nltitle-v1-title-tools-tests.txt"))
        self.assertEqual((ran, ok, passed), (5, 5, True))
        self.assertIn("the patch and compare scripts passed %d of %d." % (ok, ran), self.text)

    def test_md5s(self):
        self.assertIn("patched nextlist.py md5 %s" % self.md5s["nextlist.py"], self.text)
        self.assertIn("patch_title.py md5 %s" % self.md5s["patch_title.py"], self.text)
        code = read("tools", "nextlist-title", "patch_title.py")
        self.assertIn('NEW_VERSION = \'__version__ = "0.1.1"\'', code)
        self.assertIn("class Title(unittest.TestCase):", code)

    def test_registered_code_named(self):
        self.assertIn("`tools/annual-flows-candidate/nextlist.py` 0.1.0 is unchanged at its path", self.text)
        self.assertIn("(expected 24 November 2026)", self.text)
        self.assertNotIn("MIT", self.text)


if __name__ == "__main__":
    unittest.main()
