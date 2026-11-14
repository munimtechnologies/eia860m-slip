# Unit tests for rusops.py (no network, no polars). MV2 of Munim, Inc. (made with AI agents).
# Apache-2.0.
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rusops as r  # noqa: E402


def row(b, t, g="patronage_capital_or_margins", month=None, ytd=None, budget=None):
    return {"borrower_id_rus": b, "report_date": "2020-12-01", "opex_group": g, "opex_type": t,
            "opex_report_month": month, "opex_ytd": ytd, "opex_ytd_budget": budget}


class ColmapTests(unittest.TestCase):
    def test_regex_matches_pudl_names(self):
        m = r.PATTERN.match("opex_operating_revenue_opex_ytd")
        self.assertEqual((m.group(1), m.group(2), m.group(3)), ("opex", "operating_revenue", "opex_ytd"))
        m = r.PATTERN.match("opex_admin_opex_ytd_budget")
        self.assertEqual(m.group(2), "admin")
        self.assertEqual(m.group(3), "opex_ytd_budget")
        m = r.PATTERN.match("patronage_and_operating_margins_total_minus_opex_report_month")
        self.assertEqual(m.group(2), "total_minus")

    def test_misplaced_ytd_makes_an_orphan(self):
        header = ["year_index", "borrower_id_rus",
                  "patronage_capital_or_margins_other_capital_credits_opex_ytd",
                  "patronage_capital_or_margins_other_capital_credits_opex_ytd_budget",
                  "patronage_capital_or_margins_other_capital_credits_ytd_opex_report_month",
                  "opex_sales_opex_ytd", "opex_sales_opex_ytd_budget", "opex_sales_opex_report_month"]
        per, unmatched = r.colmap_periods(header)
        self.assertEqual(unmatched, ["year_index", "borrower_id_rus"])
        self.assertEqual(per[("opex", "sales")], ["opex_report_month", "opex_ytd", "opex_ytd_budget"])
        orph = r.orphans(per)
        self.assertEqual(orph, {
            "patronage_capital_or_margins|other_capital_credits": ["opex_ytd", "opex_ytd_budget"],
            "patronage_capital_or_margins|other_capital_credits_ytd": ["opex_report_month"]})


class ProfileTests(unittest.TestCase):
    def test_profile_counts_nulls_nan_and_tolerance(self):
        rows = [row("A", r.OCC_YTD, month=50.0), row("B", r.OCC_YTD, month=5.0),
                row("C", r.OCC_YTD, month=float("nan")), row("A", r.OCC, ytd=50.0, budget=0.0)]
        p = r.profile(rows, r.OCC_YTD)
        self.assertEqual(p["rows"], 3)
        self.assertEqual(p["keys"], 3)
        self.assertEqual(p["opex_report_month"], {"nonnull": 2, "abs_gt_tol": 1})
        self.assertEqual(p["opex_ytd"]["nonnull"], 0)
        q = r.profile(rows, r.OCC)
        self.assertEqual(q["opex_ytd"], {"nonnull": 1, "abs_gt_tol": 1})
        self.assertEqual(q["opex_ytd_budget"], {"nonnull": 1, "abs_gt_tol": 0})

    def test_isnull(self):
        self.assertTrue(r.isnull(None))
        self.assertTrue(r.isnull(math.nan))
        self.assertFalse(r.isnull(0.0))


class Line29Tests(unittest.TestCase):
    def rows(self, occ_month):
        g = "patronage_capital_or_margins"
        return [
            row("A", "total_minus", g="patronage_and_operating_margins", month=100.0, ytd=1000.0),
            row("A", "non_operating_margins_interest", month=10.0, ytd=100.0),
            row("A", r.OCC, month=None, ytd=200.0),
            row("A", r.OCC_YTD, month=occ_month, ytd=None),
            row("A", "total", month=110.0 + occ_month, ytd=1300.0),
            row("A", "total", g="opex", month=99999.0, ytd=99999.0),  # other group's 'total'
        ]

    def test_split_label_fails_only_as_labelled(self):
        rows = self.rows(40.0)
        sums = r.sums_by_key(rows, "opex_report_month")
        a = r.check(sums, r.line29_items(False), r.LINE29_TOTAL)
        b = r.check(sums, r.line29_items(True), r.LINE29_TOTAL)
        self.assertEqual((a["groups_checked"], a["failures"]), (1, 1))
        self.assertEqual((b["groups_checked"], b["failures"]), (1, 0))
        self.assertEqual(a["largest_failures"][0]["absolute_diff"], 40.0)

    def test_ytd_unaffected(self):
        sums = r.sums_by_key(self.rows(40.0), "opex_ytd")
        a = r.check(sums, r.line29_items(False), r.LINE29_TOTAL)
        b = r.check(sums, r.line29_items(True), r.LINE29_TOTAL)
        self.assertEqual(a["failures"], 0)
        self.assertEqual(b["failures"], 0)

    def test_within_tolerance_passes(self):
        sums = r.sums_by_key(self.rows(8.0), "opex_report_month")
        self.assertEqual(r.check(sums, r.line29_items(False), r.LINE29_TOTAL)["failures"], 0)

    def test_missing_total_and_missing_subs_are_not_checked(self):
        rows = [row("A", r.OCC, ytd=5.0), row("B", "total", ytd=5.0)]
        res = r.check(r.sums_by_key(rows, "opex_ytd"), r.line29_items(True), r.LINE29_TOTAL)
        self.assertEqual(res["groups_checked"], 0)
        self.assertEqual(res["groups_without_total"], 1)
        self.assertEqual(res["groups_without_subcomponents"], 1)

    def test_line29_items(self):
        items = r.line29_items(False)
        self.assertEqual(len(items), 8)
        self.assertNotIn(("patronage_capital_or_margins", r.OCC_YTD), items)
        self.assertEqual(len(r.line29_items(True)), 9)


class ScoreTests(unittest.TestCase):
    def table(self, ytd_nonnull=0, month_big=100, l29m=(1000, 120, 10), l29y=(1000, 20, 20)):
        z = {"nonnull": 0, "abs_gt_tol": 0}
        return {
            "opex_groups": list(r.GROUPS), "borrower_years": 1000,
            "profile": {
                r.OCC_YTD: {"rows": 1000, "keys": 1000,
                            "opex_report_month": {"nonnull": 1000, "abs_gt_tol": month_big},
                            "opex_ytd": {"nonnull": ytd_nonnull, "abs_gt_tol": 0},
                            "opex_ytd_budget": dict(z)},
                r.OCC: {"rows": 1000, "keys": 1000, "opex_report_month": dict(z),
                        "opex_ytd": {"nonnull": 900, "abs_gt_tol": 300},
                        "opex_ytd_budget": {"nonnull": 900, "abs_gt_tol": 300}}},
            "line29": {
                "opex_report_month": {"as_labelled": {"groups_checked": l29m[0], "failures": l29m[1]},
                                      "merged": {"groups_checked": l29m[0], "failures": l29m[2]}},
                "opex_ytd": {"as_labelled": {"groups_checked": l29y[0], "failures": l29y[1]},
                             "merged": {"groups_checked": l29y[0], "failures": l29y[2]}}}}

    def test_all_hold(self):
        res = {"colmap": {"orphans": {}}, "tables": {t: self.table() for t in r.TABLES}}
        self.assertTrue(r.gate(res))
        self.assertEqual(r.score(res), {"P1": True, "P2": True, "P3": True, "P4": True, "P5": True})

    def test_each_can_fail(self):
        res = {"colmap": {}, "tables": {r.TABLES[0]: self.table(ytd_nonnull=1, month_big=9,
                                                               l29m=(1000, 10, 10), l29y=(1000, 60, 60)),
                                       r.TABLES[1]: self.table(ytd_nonnull=1)}}
        self.assertEqual(r.score(res), {"P1": False, "P2": False, "P3": False, "P4": False, "P5": False})

    def test_gate_fails_on_error_or_groups(self):
        res = {"colmap": {"error": "x"}, "tables": {t: self.table() for t in r.TABLES}}
        self.assertFalse(r.gate(res))
        t = self.table()
        t["opex_groups"] = ["opex"]
        res = {"colmap": {}, "tables": {r.TABLES[0]: t, r.TABLES[1]: self.table()}}
        self.assertFalse(r.gate(res))


if __name__ == "__main__":
    unittest.main()
