"""Unit tests for check_changelog.py (Apache-2.0)."""

import json
import os
import tempfile
import unittest

import check_changelog as cc

TOY = (
    "import os\n"
    "\n"
    "@decorator\n"
    "def make_changelog(df, idx):\n"
    "    return pd.DataFrame()\n"
    "\n"
    "def other():\n"
    "    pass\n"
)

GLOBAL_DEDUP = (
    "def make_changelog(df_all, idx):\n"
    "    return df_all.sort_values(\"report_date\").drop_duplicates(\n"
    "        subset=[c for c in df_all if c != \"report_date\"], keep=\"first\")\n"
)


def consecutive(df, idx):
    df = df.sort_values("report_date")
    s = df["operational_status_code"]
    return df[s.ne(s.shift())]


class ExtractTests(unittest.TestCase):
    def test_extract_without_decorator(self):
        self.assertEqual(cc.extract(TOY),
                         "def make_changelog(df, idx):\n    return pd.DataFrame()")

    def test_missing(self):
        with self.assertRaises(LookupError):
            cc.extract("def other():\n    pass\n")

    def test_load_runs(self):
        fn = cc.load(TOY)
        self.assertEqual(len(fn(None, None)), 0)


class CheckTests(unittest.TestCase):
    def test_global_dedup_drops_return(self):
        r = cc.check(GLOBAL_DEDUP)
        self.assertTrue(r["return_dropped"])
        self.assertEqual(r["last_status_kept"], "OA")
        self.assertEqual(r["cases"]["return"]["dates_kept"], ["2026-01-01", "2026-02-01"])
        self.assertFalse(r["cases"]["return"]["matches_consecutive_rule"])
        self.assertTrue(r["cases"]["no_return"]["matches_consecutive_rule"])
        self.assertTrue(r["cases"]["repeat"]["matches_consecutive_rule"])

    def test_consecutive_keeps_return(self):
        r = cc.check("", fn=consecutive)
        self.assertFalse(r["return_dropped"])
        self.assertEqual(r["last_status_kept"], "OP")
        for case in r["cases"].values():
            self.assertTrue(case["matches_consecutive_rule"])

    def test_repeat_rows(self):
        r = cc.check("", fn=consecutive)
        self.assertEqual(r["cases"]["repeat"]["dates_kept"], ["2026-01-01", "2026-03-01"])
        self.assertEqual(r["cases"]["repeat"]["statuses_kept"], ["OP", "OA"])


class MainTests(unittest.TestCase):
    def test_main_writes_json(self):
        with tempfile.TemporaryDirectory() as d:
            src = os.path.join(d, "helpers_src.txt")
            with open(src, "w", encoding="utf-8", newline="\n") as f:
                f.write(GLOBAL_DEDUP)
            out = os.path.join(d, "out")
            cc.main(["--src", src, "--sha", "abc", "--out-dir", out])
            with open(os.path.join(out, "changelog_check.json"), encoding="utf-8") as f:
                r = json.load(f)
            self.assertEqual(r["pudl_commit"], "abc")
            self.assertEqual(r["helpers_bytes"], len(GLOBAL_DEDUP))
            self.assertTrue(r["return_dropped"])
            self.assertIn("drop_duplicates", r["make_changelog_source"])


if __name__ == "__main__":
    unittest.main()
