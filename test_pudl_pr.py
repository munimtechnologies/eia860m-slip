"""Checks that docs/pudl-pr.md scores the gates and ten predictions of docs/pudl-pr-plan.md
with the counts job pudl-pr-v1 wrote. Reads text only, so it needs no pandas.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))

# Copied from compete-results/pudl-pr-v1/out/pr_check.json.
TESTS = {  # label: (collected, passed, name_errors)
    "pr_on_pr": (17, 17, 0),
    "main_on_pr": (8, 8, 0),
    "pr_on_main": (17, 11, 0),
}
Q4 = {"frames": 200, "rows": 3723, "ref_match": 200, "no_dup_rows": 200,
      "order_independent": 200, "noreturn_frames": 100, "noreturn_same_as_main": 100}
Q5 = {"frames": 200, "rows": 5699, "ref_match": 200, "no_dup_rows": 200,
      "order_independent": 200, "zero_or_backwards": 0, "rows_kept": 4573,
      "rows_kept_by_value_rule": 3186}
Q7 = {"numpy_consecutive_count": 38229, "main_seconds": 0.297, "main_rows_kept": 37659,
      "pr_seconds": 9.391, "pr_rows_kept": 38229, "ratio": 31.62}
S1 = {
    "unchanged": (["2026-01-01 OP until 2026-03-01"], ["2026-01-01 OP until 2026-03-01"]),
    "changed_middle": (["2026-01-01 OP until 2026-02-01", "2026-02-01 OA until 2026-03-01"],
                       ["2026-01-01 OP until 2026-02-01", "2026-02-01 OA until 2026-03-01"]),
    "changed_last": (["2026-01-01 OP until 2026-02-01", "2026-02-01 OA until 2026-03-01",
                      "2026-03-01 OP until 2026-04-01"],
                     ["2026-01-01 OP until 2026-02-01", "2026-02-01 OA until 2026-03-01"]),
}
NIGHTLY = {"rows": 224408, "generators": 39903, "last_report_date": "2026-08-01",
           "missing_columns": 0, "last_starts_on_last_date": 577,
           "last_until_last_date_started_before_month_before": 36710,
           "last_until_last_date_started_month_before": 709,
           "generators_covered_on_last_date": 577, "L1_share": 0.9845,
           "md5": "ee7132321f9a882956a515d1632e0b1e"}


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class PudlPrScoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/pudl-pr.md")
        cls.plan = read("docs/pudl-pr-plan.md")

    def test_plan_bars_exist(self):
        self.assertIn("Pre-registration id: pudl-pr-1.", self.plan)
        for text in ("**Gate:**", "**Q1 (95%):**", "**Q2 (95%):**", "**Q3 (90%):**",
                     "**Q4 (85%):**", "**Q5 (80%):**", "**Q6 (90%):**", "**Q7 (95%):**",
                     "**S1 (90%):**", "**Nightly gate:**", "**L1 (85%):**", "**L2 (90%):**"):
            self.assertIn(text, self.plan)

    def test_scores_follow_the_bars(self):
        gate = all(c[0] > 0 and c[2] == 0 for c in TESTS.values())
        q1 = TESTS["pr_on_pr"][0] == TESTS["pr_on_pr"][1]
        q2 = TESTS["main_on_pr"][0] == TESTS["main_on_pr"][1]
        q3 = TESTS["pr_on_main"][1] < TESTS["pr_on_main"][0]
        q4 = (Q4["ref_match"] == Q4["no_dup_rows"] == Q4["order_independent"]
              == Q4["frames"] == 200 and Q4["noreturn_same_as_main"] == Q4["noreturn_frames"])
        q5 = Q5["ref_match"] == Q5["no_dup_rows"] == Q5["order_independent"] == Q5["frames"]
        q6 = Q5["zero_or_backwards"] == 0
        q7 = Q7["pr_rows_kept"] == Q7["numpy_consecutive_count"] == 38229
        s1 = (S1["unchanged"][0] == S1["unchanged"][1] == ["2026-01-01 OP until 2026-03-01"]
              and S1["changed_middle"][0][-1] == S1["changed_middle"][1][-1]
              == "2026-02-01 OA until 2026-03-01"
              and S1["changed_last"][0][-1] == "2026-03-01 OP until 2026-04-01")
        nightly = NIGHTLY["missing_columns"] == 0
        a = NIGHTLY["last_until_last_date_started_before_month_before"]
        b = NIGHTLY["last_starts_on_last_date"]
        l1 = a / (a + b) >= 0.8
        l2 = NIGHTLY["generators_covered_on_last_date"] == b
        self.assertTrue(gate and nightly)
        held = [q1, q2, q3, q4, q5, q6, q7, s1, l1, l2]
        self.assertEqual(sum(held), 10)
        self.assertIn("Both gates held and 10 of 10 predictions held.", self.doc)

    def test_score_rows(self):
        for text in ("held: 17, 8 and 17 cases collected, 0 NameErrors",
                     "| Q1 (95%) |", "held: 17 of 17", "held: 8 of 8",
                     "held: %d of 17 fail" % (17 - TESTS["pr_on_main"][1]),
                     "held: 200, 200, 200 of 200; 100 of 100",
                     "| Q6 (90%) |", "held: 0 such records", "held: 38,229",
                     "| S1 (90%) |", "| Nightly gate |",
                     "held: 224,408 rows, 39,903 generators",
                     "held: 577 = 577"):
            self.assertIn(text, self.doc)

    def test_l1_numbers(self):
        a = NIGHTLY["last_until_last_date_started_before_month_before"]
        b = NIGHTLY["last_starts_on_last_date"]
        self.assertEqual(round(a / (a + b), 4), NIGHTLY["L1_share"])
        self.assertIn("held: %.2f%% ({:,} against {:,})".format(a, b) % (100.0 * a / (a + b)),
                      self.doc)
        self.assertIn("{:,} generators have a last record that started before July".format(a),
                      self.doc)
        self.assertIn("{:,} more have a last record that started in July".format(
            NIGHTLY["last_until_last_date_started_month_before"]), self.doc)
        self.assertIn("returns {:,} generators, {:.1f}% of the {:,}".format(
            b, 100.0 * b / (a + b), a + b), self.doc)
        self.assertIn(NIGHTLY["md5"], self.doc)

    def test_s1_text(self):
        for name, (pr, main) in S1.items():
            self.assertIn('"%s"' % pr[-1], self.doc)
        self.assertIn('"%s"' % S1["unchanged"][1][0], self.doc)

    def test_run_times(self):
        self.assertEqual(round(Q7["pr_seconds"] / Q7["main_seconds"], 2), Q7["ratio"])
        self.assertEqual(Q7["pr_rows_kept"] - Q7["main_rows_kept"], 570)
        self.assertIn("main keeps 37,659, so 570 fewer", self.doc)
        self.assertIn("main 0.297 s, the PR 9.391 s, 31.62 times main", self.doc)
        self.assertIn("the PR kept 4,573 rows, where a per-value rule", self.doc)
        self.assertIn("would keep 3,186", self.doc)

    def test_nothing_of_pudl_stored(self):
        self.assertIn("PUDL's code (MIT) and data (CC BY 4.0) were downloaded at run time and "
                      "are not stored here.", self.doc)
        self.assertIn("https://github.com/catalyst-cooperative/pudl/pull/5731", self.doc)


if __name__ == "__main__":
    unittest.main()
