"""Checks that docs/cems-mindown.md (part 1 of the cems-mindown-1 result) reports the job's
numbers and failed bars as recorded, and that the re-run wrapper changes only the one
attribute the page names. Reads every file as text, so it needs no polars.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
OLD = "md.schema.column(j).path_in_schema"
NEW = "md.schema.column(j).path"


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class CemsMindownResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/cems-mindown.md")
        cls.check = read("tools/cems-mindown/mindown_check.py")
        cls.wrapper = read("tools/cems-mindown/mindown_v2.py")
        cls.wrapper_tests = read("tools/cems-mindown/test_mindown_v2.py")

    def test_status_and_ids(self):
        self.assertIn("Status: partly scored against its pre-registration. 3 of 6 scored bars "
                      "held; G1, T1 and T2 failed as written", self.doc)
        self.assertIn("Pre-registration id: cems-mindown-1", self.doc)
        self.assertIn("Re-run id: cems-mindown-1-R.", self.doc)

    def test_failed_bars_stay_failed(self):
        for row in ("| Gate G1 | failed as written |", "| T1 (95%) | failed as written |",
                    "| T2 (90%) | failed as written |", "| T3 (95%) | held |",
                    "| T4 (90%) | held |", "| N1 (90%) | held |",
                    "| Gate R0, F1-F4 | not run |"):
            self.assertIn(row, self.doc)
        self.assertIn("They are not re-scored.", self.doc)
        self.assertIn("G1, T1 and T2 stay scored as above.", self.doc)
        # the scoring code still asks for 29 collected tests
        self.assertIn('t.get("none", {}).get("collected") == 29', self.check)

    def test_numbers(self):
        for text in ("34 tests collected in every mode, not 29", "34 of 34 passed with no patch",
                     "34 of 34 passed with the fill patch", "(3, 3 and 2 cases)",
                     "300 frames, 21,207 rows, 2,364 isolated null hours",
                     "2,879 of 4,173 report-year 2025 units (69.0%)",
                     "118,117 rows", "md5 984f855eb1c8c883459813ca295adc9a",
                     "md5 5eba4a6b6114eb813471417724e2b060",
                     "md5 385b36020533c406fb72ca63ee56f847",
                     "between 60.8% (2004) and 70.9% (2001) in every one of the 26 report years",
                     "| 2025 | 4,173 | 2,879 | 69.0% |", "| 2004 | 4,621 | 2,808 | 60.8% |",
                     "| 2001 | 3,424 | 2,427 | 70.9% |"):
            self.assertIn(text, self.doc)
        self.assertEqual(self.doc.count("\n| 20"), 26)

    def test_cause_and_fix(self):
        self.assertIn("no attribute 'path_in_schema'", self.doc)
        self.assertIn("replaces `%s` with `%s` and nothing else" % (OLD, NEW), self.doc)
        self.assertEqual(self.check.count(OLD), 1)
        self.assertIn('VERSION = "0.1.0"', self.check)
        self.assertIn('OLD = "%s"' % OLD, self.wrapper)
        self.assertIn('NEW = "%s"' % NEW, self.wrapper)
        self.assertIn('VERSION = "0.1.0"', self.wrapper)
        self.assertIn("`tools/cems-mindown/mindown_v2.py` 0.1.0", self.doc)
        self.assertIn("src.count(OLD) != 1", self.wrapper)
        self.assertIn("mc.main(argv)", self.wrapper)

    def test_wrapper_tests_cover_both_paths(self):
        self.assertIn("with self.assertRaises(AttributeError):", self.wrapper_tests)
        self.assertIn('self.assertEqual(info["row_groups_read"], 1)', self.wrapper_tests)

    def test_disclosure_and_licence(self):
        self.assertIn("made with AI agents working in MV2's name; no person has checked these "
                      "results by hand", self.doc)
        self.assertIn("PUDL's code (MIT) and data (CC BY 4.0) are downloaded at run time and "
                      "not stored here.", self.doc)
        for text in (self.wrapper, self.wrapper_tests):
            self.assertIn("Apache-2.0", text)
            self.assertNotIn("def calculate_min_up_or_down_times(output, cems", text)


if __name__ == "__main__":
    unittest.main()
