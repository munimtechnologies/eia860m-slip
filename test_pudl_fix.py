"""Checks that docs/pudl-fix.md scores the plan's seven expectations with the numbers job
pudl-fix-v1 wrote, and that the E2 re-run it fixes matches tools/pudl-fix/check_fix2.py and
get_pinned.py. Reads all of them as text, so it needs no pandas.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class PudlFixScoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/pudl-fix.md")
        cls.plan = read("docs/pudl-fix-plan.md")
        cls.check2 = read("tools/pudl-fix/check_fix2.py")
        cls.pinned = read("tools/pudl-fix/get_pinned.py")

    def test_status(self):
        self.assertIn("Status: scored against its pre-registration (docs/pudl-fix-plan.md, "
                      "id pudl-fix-1). 6 of 7 expectations held; E2 missed", self.doc)
        self.assertIn("Pre-registration id: pudl-fix-1.", self.plan)

    def test_every_expectation_scored(self):
        rows = [line for line in self.doc.splitlines() if line.startswith("| E")]
        self.assertEqual([r.split("|")[1].strip() for r in rows],
                         ["E1", "E2", "E3", "E4", "E5", "E6", "E7"])
        held = [r for r in rows if "| held" in r]
        missed = [r for r in rows if "**missed**" in r]
        self.assertEqual(len(held), 6)
        self.assertEqual([r.split("|")[1].strip() for r in missed], ["E2"])

    def test_numbers(self):
        # Copied from compete-results/pudl-fix-v1/out/fix_check.json.
        for text in ("400 of 400", "100 of 100", "9,816 input rows", "232 frames",
                     "1,147 records", "38,229 records kept", "37,659 records",
                     "0.900 s against 0.447 s", "2.01 times",
                     "eaa3055629b66bdd5746304dfd948981", "7 of the 8 cases"):
            self.assertIn(text, self.doc)
        self.assertEqual(38229 - 37659, 570)
        self.assertIn("570 fewer", self.doc)
        self.assertEqual(round(0.9 / 0.447, 2), 2.01)

    def test_rerun_matches_code(self):
        self.assertIn("Re-run id: pudl-fix-1-E2.", self.doc)
        self.assertIn('VERSION = "0.2.0"', self.check2)
        self.assertIn("`tools/pudl-fix/check_fix2.py` 0.2.0", self.doc)
        self.assertIn('SHA = "840ac280dd1a7d70d4124bc405f7c7a3ab4e39d9"', self.pinned)
        self.assertIn("committed in 840ac28", self.doc)
        self.assertIn('"check_fix.py": "5054a0486fc87ea1a1d789b7a2a78c96"', self.pinned)
        self.assertIn('"keep_changes.py": "4ffb24b50db7641e3ba91dea7ea7e064"', self.pinned)
        self.assertIn('e2["name_errors"]', self.check2)
        self.assertIn('node.module.split(".")[0] != "pudl"', self.check2)

    def test_no_pudl_code_stored(self):
        self.assertIn("PUDL's code (MIT) is downloaded at run time and not stored here.", self.doc)
        self.assertNotIn("def make_changelog", self.check2)


if __name__ == "__main__":
    unittest.main()
