"""Checks the numbers in the September 2026 section of docs/workbook-route.md (added 27 October
2026) against the raw output of compete job watchsep-v1 (data/watchsep_v1_check.json,
data/watchsep_v1_route.json, data/watchsep_v1_rawcheck.json, docs/watchsep-v1-rawcheck-output.md,
docs/watchsep-v1-unittests.txt).
MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
HEAD = "## September 2026 (added 27 October 2026)"
UNIT_TESTS = 44
MONTH = "2026-09"
BEFORE = ("49.0.0", "50.0.0")


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8") as fh:
        return fh.read()


class SeptemberDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.full = read("docs", "workbook-route.md")
        cls.text = cls.full[cls.full.index(HEAD):]
        cls.check = json.loads(read("data", "watchsep_v1_check.json"))
        cls.route = json.loads(read("data", "watchsep_v1_route.json"))
        cls.raw = json.loads(read("data", "watchsep_v1_rawcheck.json"))
        cls.out = read("docs", "watchsep-v1-rawcheck-output.md")
        cls.log = read("docs", "watchsep-v1-unittests.txt")

    def test_unit_tests(self):
        ran = int(re.search(r"Ran (\d+) tests", self.log).group(1))
        self.assertEqual(ran, UNIT_TESTS)
        self.assertEqual(len(re.findall(r" \.\.\. ok$", self.log, re.M)), ran)
        self.assertTrue(self.log.rstrip().endswith("OK"))
        self.assertIn("passed %d of %d unit tests" % (ran, ran), self.text)

    def test_self_check_did_not_run(self):
        self.assertEqual(self.check["version"], "0.1.1")
        self.assertIn("(workbook.py %s, unchanged)" % self.check["version"], self.text)
        self.assertEqual(self.check["pudl_max"], "2026-08")
        self.assertIn("still ends with report %s" % self.check["pudl_max"], self.text)
        self.assertEqual(len(self.check["months"]), 1)
        m = self.check["months"][0]
        self.assertEqual((m["report"], m["mode"]), (MONTH, "check"))
        self.assertNotIn("self_check", m)
        self.assertIn('stopped with "%s"' % m["error"], self.text)
        self.assertIn("The bar of %.2f is neither passed nor failed" % self.check["usable_threshold"],
                      self.text)

    def test_archive_copy(self):
        self.assertEqual(self.raw["since"], "2026-10-20")
        self.assertIn("on or after 20 October 2026", self.text)
        self.assertEqual(len(self.raw["copies"]), 1)
        c = self.raw["copies"][0]
        self.assertTrue(c["checksum_ok"])
        self.assertEqual(c["checksum"], "md5:" + c["md5"])
        self.assertEqual(c["bytes"], c["size"])
        self.assertIn("Zenodo record %s, version %s, first published %s" % (
            c["first_id"], c["first_version"], c["first_date"]), self.text)
        self.assertIn("`%s`, %s bytes, md5 %s, matching Zenodo's checksum" % (
            c["key"], "{:,}".format(c["bytes"]), c["md5"]), self.text)
        months = {x["month"]: x for x in self.raw["months"]}
        self.assertEqual(sorted(months), [MONTH])
        m = months[MONTH]
        self.assertIsNone(m["eia_error"])
        self.assertEqual(len(m["copies"]), 1)
        k = m["copies"][0]
        self.assertTrue(k["same_file"])
        self.assertEqual((k["md5"], k["bytes"]), (m["eia_md5"], m["eia_bytes"]))
        self.assertIn(k["member"], c["members"])
        self.assertIn("Its member `%s` is byte for byte the file EIA serves: %s bytes, md5 %s." % (
            k["member"], "{:,}".format(m["eia_bytes"]), m["eia_md5"]), self.text)
        self.assertIn("md5 %s, same file as EIA's: True" % m["eia_md5"], self.out)

    def test_earlier_versions(self):
        hist = {h["first_version"]: h["first_date"] for h in self.raw["history"]["eia860m-2026.zip"]}
        self.assertIn("first published %s (%s) and %s (%s)" % (
            hist[BEFORE[0]], BEFORE[0], hist[BEFORE[1]], BEFORE[1]), self.text)
        # 6 and 5 days from those dates to the merges on 5 September and 2 October 2026
        self.assertEqual((hist[BEFORE[0]], hist[BEFORE[1]]), ("2026-08-30", "2026-09-27"))
        self.assertIn("6 and 5 days after those versions", self.text)

    def test_route(self):
        self.assertEqual(self.route["version"], self.check["version"])
        self.assertEqual(self.route["pudl_max"], self.check["pudl_max"])
        m = self.route["months"][0]
        self.assertEqual((m["report"], m["mode"]), (MONTH, "report"))
        self.assertEqual(m["fetch_errors"], [])
        checks = m["checks"]
        self.assertTrue(checks["all_pass"])
        self.assertEqual(sorted(k for k in checks if k != "all_pass"), ["C1", "C2", "C3", "C4"])
        self.assertIn("the route listed %d generators, and its four internal checks (C1 to C4) passed"
                      % m["rows"], self.text)

    def test_old_text_kept(self):
        self.assertIn("The bar of 0.98 stays where it was set.", self.full)
        self.assertIn("With workbook.py 0.1.1 unchanged, the September 2026 self-check, once PUDL "
                      "holds September, is such a month.", self.full)
        self.assertLess(self.full.index("## Follow-up (added 21 October 2026)"), self.full.index(HEAD))


if __name__ == "__main__":
    unittest.main()
