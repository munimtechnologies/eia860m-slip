"""Checks that every count stated in docs/phzero.md (result of pre-registration phzero-1) is what
data/phzero-run.json and the three phzero CSV files in data/ (the job's outputs, unchanged) say.
Reads no outside data.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import csv
import json
import os
import unittest
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))


def path(rel):
    return os.path.join(HERE, rel)


def fmt(n):
    return f"{n:,}"


def pct(a, b):
    return f"{100.0 * a / b:.2f}%"


def read_csv(rel):
    with open(path(rel), encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def frac(a, b):
    return f"{fmt(a)} of {fmt(b)} ({pct(a, b)})"


class PhzeroResultTests(unittest.TestCase):
    # The job's JSON is kept as `res`: naming it `run` would hide unittest's TestCase.run.
    @classmethod
    def setUpClass(cls):
        with open(path("docs/phzero.md"), encoding="utf-8") as fh:
            cls.doc = fh.read()
        with open(path("data/phzero-run.json"), encoding="utf-8") as fh:
            cls.res = json.load(fh)
        cls.zrows = read_csv("data/phzero-zero-rows.csv")
        cls.multi = read_csv("data/phzero-multi-id-names.csv")
        cls.miss = read_csv("data/phzero-loo-misses.csv")
        cls.m = cls.res["measures"]
        cls.z = cls.m["zeros"]
        cls.loo = cls.m["loo"]

    def lc(self, rule, era):
        return (self.loo["%s|%s|correct" % (rule, era)], self.loo["%s|%s|predicted" % (rule, era)])

    def test_run_and_scores(self):
        self.assertEqual(self.res["tool"], "phzero.py 0.1.0")
        self.assertEqual((self.res["started"], self.res["finished"]),
                         ("2026-11-11T00:44:58Z", "2026-11-11T00:45:02Z"))
        self.assertIn("11 November 2026, 00:44:58-00:45:02 UTC", self.doc)
        self.assertEqual(self.res["scores"], {"G1": True, "G2": True, "G3": True, "P1": True,
                                              "P2": True, "P3": True, "P4": True, "P5": True,
                                              "P6": True, "P7": False, "P8": True})
        self.assertIn("**7 of the 8 predictions held (P1-P6, P8); P7 failed.**", self.doc)

    def test_input_and_gates(self):
        t = self.res["table"]
        self.assertEqual((t["bytes"], t["rows"], t["missing_cols"], t["missing_optional"]),
                         (2152092, 91990, [], []))
        self.assertEqual(t["last_modified"], "Tue, 10 Nov 2026 08:52:18 GMT")
        self.assertIn("md5 `%s`" % t["md5"], self.doc)
        self.assertIn("2,152,092 bytes, Last-Modified 10 Nov 2026 08:52:18 GMT", self.doc)
        g = self.res["gate_measures"]
        self.assertEqual((g["rows"], g["years"], g["kinds"], g["rows_without_year"]),
                         (91990, [1970, 2025], {"id": 89859, "zero": 2131}, 0))
        self.assertIn("It has 91,990 rows from report years 1970-2025: 89,859 with a real id and "
                      "2,131 with id 0. No id is null.", self.doc)
        self.assertEqual(self.res["gates"], {"G1": True, "G2": True, "G3": True})
        self.assertIn("| 91,990 rows; report years 1970-2025 | yes |", self.doc)
        self.assertIn("| G3 at least 500 zero rows | 2,131 | yes |", self.doc)
        self.assertEqual(sum(self.res["rows_by_year"].values()), 91990)

    def test_zero_counts_p1_p2_p3(self):
        z = self.z
        self.assertEqual((z["zero_or_null"], z["zero"], z["in_1976_1983"], z["before_1990"]),
                         (2131, 2131, 2131, 2131))
        self.assertNotIn("null", z)
        self.assertIn("| 1,500-2,800 | 2,131 | yes |", self.doc)
        self.assertIn("| at least 99%% | %s | yes |" % frac(2131, 2131), self.doc)
        self.assertEqual(z["exact|when_later"], 2)
        self.assertIn("| at most 1%% with a later exact-name id | 2 of 2,131 (%s) | yes |"
                      % pct(2, 2131), self.doc)
        zy = self.m["zeros_by_year"]
        self.assertEqual(zy, {"1976": 12, "1978": 3, "1980": 501, "1981": 486, "1982": 422,
                              "1983": 707})
        self.assertIn("1976: 12, 1978: 3, 1980: 501, 1981: 486, 1982: 422, 1983: 707", self.doc)
        self.assertEqual(len(self.zrows), 2131)
        self.assertEqual(Counter(r["report_year"] for r in self.zrows),
                         Counter({k: v for k, v in zy.items()}))

    def test_p4_p5(self):
        z = self.z
        self.assertEqual((z["exact|unique"], z["norm|unique"], z["norm_state|unique"]),
                         (347, 486, 396))
        self.assertIn("| at least 5%% with exactly one exact-name id | 347 of 2,131 (%s) | yes |"
                      % pct(347, 2131), self.doc)
        self.assertIn("347 zeros (%s) have exactly one real id" % pct(347, 2131), self.doc)
        gain = f"{100.0 * (486 - 347) / 2131:.2f}"
        self.assertIn("| 486 vs 347 (+%s points) | yes |" % gain, self.doc)
        self.assertIn("exact name 347, normalized name + office state 396, normalized name 486",
                      self.doc)
        single = [r for r in self.zrows if r["exact_ids"] and " " not in r["exact_ids"]]
        self.assertEqual(len(single), 347)
        early = [r for r in single if r["exact_when"] in ("earlier", "same_year")]
        self.assertEqual(len(early), 345)
        self.assertIn("345 of those are only in earlier or same-year reports", self.doc)
        self.assertIn("so 345 (%s) are earlier or same-year only" % pct(345, 2131), self.doc)
        self.assertIn("would fill about 345 more zeros", self.doc)

    def test_p6_p7_p8_and_loo_table(self):
        rows = [("pudl_later", "PUDL's rule: nearest later year, same exact name"),
                ("exact_earlier", "Nearest earlier year, same exact name"),
                ("unique_exact", "Exact name, only if it carries one id"),
                ("unique_norm_state", "Normalized name + office state, only if one id"),
                ("unique_norm", "Normalized name, only if one id")]
        for rule, label in rows:
            a, e = self.lc(rule, "all"), self.lc(rule, "early")
            self.assertIn("| %s | %s | %s |" % (label, frac(*a), frac(*e)), self.doc)
        self.assertEqual(self.lc("pudl_later", "all"), (75133, 76485))
        self.assertEqual(self.lc("pudl_later", "early"), (27071, 27945))
        self.assertEqual(self.lc("unique_norm", "early"), (29309, 29515))
        self.assertIn("| at least 98%% right | %s | yes |" % frac(75133, 76485), self.doc)
        self.assertIn("| at least 97%% right | %s | no |" % frac(27071, 27945), self.doc)
        self.assertIn("| at least 97%% right | %s | yes |" % frac(29309, 29515), self.doc)
        self.assertIn("right %s of the time before 1990" % pct(29910, 30116), self.doc)
        self.assertIn("right %s of the time, below P7's 97%% bar" % pct(27071, 27945), self.doc)
        self.assertIn("(%s vs %s before 1990)" % (pct(29910, 30116), pct(27071, 27945)), self.doc)

    def test_p7_ties_and_misses(self):
        self.assertEqual(len(self.miss), 3422)
        wrong = sum(p - c for c, p in (self.lc(r, "all") for r in
                    ("pudl_later", "exact_earlier", "unique_exact", "unique_norm_state",
                     "unique_norm")))
        self.assertEqual(wrong, 3422)
        self.assertIn("all 3,422 leave-one-out misses, under the 5,000 cap", self.doc)
        pl = [r for r in self.miss if r["rule"] == "pudl_later"]
        self.assertEqual(len(pl), 76485 - 75133)
        early = [r for r in pl if int(r["report_year"]) < 1990]
        self.assertEqual(len(early), 27945 - 27071)
        self.assertEqual(len(early), 874)
        ties = [r for r in early if " " in r["rule_ids"]]
        self.assertEqual(len(ties), 441)
        self.assertEqual(self.loo["pudl_later|early|tie"], 441)
        self.assertIn("Of the 874 rows before 1990 where PUDL's rule gave a wrong answer, 441 are "
                      "ties", self.doc)
        self.assertIn("441 of its 874 misses before 1990 are ties", self.doc)
        self.assertIn("right on %s" % frac(27071, 27945 - 441), self.doc)
        names = {r["operator_name_title"] for r in self.multi}
        for r in pl:
            self.assertIn(r["operator_name_phmsa"].title(), names, r)

    def test_zero_rows_detail(self):
        z = self.z
        when = Counter(r["exact_when"] for r in self.zrows)
        self.assertEqual(when, Counter({"none": 1759, "earlier": 358, "same_year": 12,
                                        "later": 2}))
        self.assertEqual((z["exact|when_none"], z["exact|when_earlier"], z["exact|when_same_year"]),
                         (1759, 358, 12))
        self.assertIn("2 later, 12 only in the same year, 358 only earlier, 1,759 none (%s)"
                      % pct(1759, 2131), self.doc)
        self.assertEqual(sum(r["operator_name_phmsa"] == "" for r in self.zrows), 24)
        self.assertIn("24 zero rows have no name at all", self.doc)
        by = Counter(r["proposed_by"] for r in self.zrows)
        self.assertEqual(by, Counter({"": 1625, "exact": 347, "norm_state": 137, "norm": 22}))
        self.assertEqual((z["proposal|exact"], z["proposal|norm_state"], z["proposal|norm"]),
                         (347, 137, 22))
        self.assertIn("proposes an id for 506 zero rows (%s): 347 by exact name, 137 by name + "
                      "state and 22 by name alone. The other 1,625 stay 0." % pct(506, 2131),
                      self.doc)
        self.assertIn("add about 159 more proposals", self.doc)
        later = sorted((r["operator_name_phmsa"], r["office_state"], r["report_year"],
                        r["exact_ids"]) for r in self.zrows if r["exact_when"] == "later")
        self.assertEqual(later, [("Air Products And Chemicals", "TX", "1983", "30760"),
                                 ("Town Of Adamsville", "TN", "1983", "49")])
        self.assertIn("Town Of Adamsville (TN, 1983, id 49) and Air Products And Chemicals "
                      "(TX, 1983, id 30760)", self.doc)

    def test_multi_id_names(self):
        self.assertEqual((len(self.multi), self.m["multi_id_exact_names"]), (355, 355))
        self.assertIn("**355 exact names carry more than one real id.**", self.doc)
        ids = Counter(int(r["ids"]) for r in self.multi)
        self.assertEqual(max(ids), 6)
        self.assertEqual((ids[6], ids[5]), (1, 5))
        top = self.multi[0]
        self.assertEqual((top["operator_name_title"], top["ids"], top["first_year"],
                          top["last_year"]), ("Peoples Gas System, Inc.", "6", "1970", "1981"))
        self.assertIn('"Peoples Gas System, Inc." carries 6 ids (1970-1981), and five names carry '
                      '5 each', self.doc)
        five = {r["operator_name_title"] for r in self.multi if r["ids"] == "5"}
        self.assertIn("Commission Of Public Works", five)
        self.assertIn("General Development Utilities", five)

    def test_disclosure(self):
        for text in ("made with AI agents working in MV2's name",
                     "no person has checked these results by hand",
                     "[plan](phzero-plan.md)", "pudl/issues/4646",
                     "Text and data CC BY 4.0; code Apache-2.0.",
                     "None of this has been checked against PHMSA's raw files or forms.",
                     "One possible cause, not checked:",
                     "After the fact, and not scored:"):
            self.assertIn(text, self.doc)


if __name__ == "__main__":
    unittest.main()
