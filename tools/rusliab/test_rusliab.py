# Tests for rusliab.py's re-implementation of PUDL's subcomponents_sum_to_total semantics.
# By MV2 of Munim, Inc. Made with AI agents working in MV2's name. Apache-2.0.
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rusliab as R  # noqa: E402


def rows(*items):
    return [{"borrower_id_rus": b, "report_date": d, "liability_type": lab, "ending_balance": v}
            for b, d, lab, v in items]


class TestMacro(unittest.TestCase):
    def test_pass_and_fail_with_tolerance(self):
        s = R.sum_by_label(rows(
            ("A", "2020-12-01", "x", 5.0), ("A", "2020-12-01", "y", 5.0),
            ("A", "2020-12-01", "t", 20.0),   # diff 10 -> not > 10, passes
            ("B", "2020-12-01", "x", 5.0), ("B", "2020-12-01", "t", 16.0),  # diff 11 fails
        ))
        n, nt, ns, f = R.check(s, ["x", "y"], [], "t", tol=10)
        self.assertEqual((n, nt, ns, len(f)), (2, 0, 0, 1))
        self.assertEqual(f[0]["key"], ["B", "2020-12-01"])
        self.assertEqual(f[0]["absolute_diff"], 11.0)

    def test_negative_and_nulls(self):
        s = R.sum_by_label(rows(
            ("A", "2020", "x", 100.0), ("A", "2020", "n", 30.0), ("A", "2020", "t", 70.0),
            ("B", "2020", "x", None), ("B", "2020", "t", 5.0),     # no subs -> skipped
            ("C", "2020", "x", 1.0), ("C", "2020", "t", None),     # no total -> skipped
            ("D", "2020", None, 9.0), ("D", "2020", "x", 1.0), ("D", "2020", "t", 1.0),
        ))
        n, nt, ns, f = R.check(s, ["x"], ["n"], "t", tol=10)
        self.assertEqual((n, nt, ns, len(f)), (2, 1, 1, 0))

    def test_label_in_both_lists_is_subtracted(self):
        s = R.sum_by_label(rows(("A", "2020", "x", 50.0), ("A", "2020", "t", -50.0)))
        n, nt, ns, f = R.check(s, ["x"], ["x"], "t", tol=10)
        self.assertEqual(len(f), 0)

    def test_duplicate_label_rows_are_summed(self):
        s = R.sum_by_label(rows(("A", "2020", "x", 2.0), ("A", "2020", "x", 3.0),
                                ("A", "2020", "x", None)))
        self.assertEqual(s[("A", "2020")]["x"], 5.0)

    def test_tests_cover_every_non_total_label_once_in_grand_total_tree(self):
        leaves = R.MARGINS + R.LTD + R.NONCURRENT + R.CURRENT
        self.assertEqual(len(leaves), len(set(leaves)))
        self.assertEqual(len(R.TESTS), 7)
        self.assertEqual(R.TOL, 10)


if __name__ == "__main__":
    unittest.main()
