"""Checks the numbers in the follow-up section of docs/workbook-route.md (added 21 October 2026)
against the raw output of compete job keyhist-v1 (data/keyhist_v1.json,
docs/keyhist-v1-output.md, docs/keyhist-v1-unittests.txt).
MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
HEAD = "## Follow-up (added 21 October 2026)"
UNIT_TESTS = 9
ZIP_MD5 = "380a9824a20be96d182fea793c299e91"
MW_TOL = 0.05
EXAMPLE = "67836/GSP1"


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8") as fh:
        return fh.read()


def canceled(w):
    return w is not None and "cancel" in str(w["sheet"]).lower()


def same(w, p):
    """keyhist.same: a workbook row against a record (status, planned month on a Planned sheet,
    MW within 0.05); a Canceled or Postponed row counts as absent."""
    if canceled(w):
        w = None
    if w is None or p is None:
        return w is None and p is None
    if w["status"] != p["status"]:
        return False
    if "plan" in str(w["sheet"]).lower() and w["planned"] != p["planned"]:
        return False
    return abs(float(w["mw"] or 0.0) - float(p["mw"] or 0.0)) <= MW_TOL


def kind(h):
    """'left' (no workbook row in the first month that differs), 'back' (the workbook row then
    equals an earlier 2026 month's) or 'new'."""
    rows = h["months"]
    i = next(j for j, r in enumerate(rows) if not r["same"])
    w = None if canceled(rows[i]["workbook"]) else rows[i]["workbook"]
    if w is None:
        return "left"
    if any(r["workbook"] is not None and not canceled(r["workbook"]) and same(r["workbook"], w)
           for r in rows[:i]):
        return "back"
    return "new"


def joined(keys):
    return " and ".join(keys) if len(keys) <= 2 else ", ".join(keys[:-1]) + " and " + keys[-1]


class FollowupDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.full = read("docs", "workbook-route.md")
        cls.text = cls.full[cls.full.index(HEAD):]
        cls.raw = json.loads(read("data", "keyhist_v1.json"))
        cls.out = read("docs", "keyhist-v1-output.md")
        cls.log = read("docs", "keyhist-v1-unittests.txt")
        cls.keys = {h["key"]: h for h in cls.raw["keys"]}
        cls.months = {m["month"]: m for m in cls.raw["months"]}
        cls.kinds = {k: kind(h) for k, h in cls.keys.items()}

    def by_kind(self, k):
        return sorted(x for x, v in self.kinds.items() if v == k)

    def test_unit_tests(self):
        ran = int(re.search(r"Ran (\d+) tests", self.log).group(1))
        self.assertEqual(ran, UNIT_TESTS)
        self.assertEqual(len(re.findall(r" \.\.\. ok$", self.log, re.M)), ran)
        self.assertTrue(self.log.rstrip().endswith("OK"))

    def test_source(self):
        self.assertEqual(sorted(self.months), ["2026-%02d" % k for k in range(1, 9)])
        self.assertEqual(self.raw["pudl_max"], "2026-08")
        self.assertTrue(all(m.get("compare") for m in self.raw["months"]))
        self.assertIn("md5 %s" % ZIP_MD5, self.out)
        self.assertIn("md5 %s" % ZIP_MD5, self.text)
        self.assertIn("22995197", self.out)

    def test_every_difference_is_an_earlier_workbook(self):
        for h in self.raw["keys"]:
            for r in h["months"]:
                if not r["same"]:
                    self.assertIsNotNone(r["pudl"], h["key"])
                    self.assertTrue(r["pudl_as_workbook_of"], (h["key"], r["month"]))
                    self.assertTrue(all(m < r["month"] for m in r["pudl_as_workbook_of"]))

    def test_kinds(self):
        self.assertEqual(len(self.by_kind("back")), 11)
        self.assertEqual(self.by_kind("new"), ["69338/LEAKY", "69372/KNOXS"])
        self.assertEqual(self.by_kind("left"), ["67223/SUNYF", "68334/EVCRK", "70257/H2SLR"])
        self.assertIn("For 2 (%s) the workbook's new value" % joined(self.by_kind("new")), self.text)
        self.assertIn("For the other 3 (%s) the generator left" % joined(self.by_kind("left")),
                      self.text)

    def test_left_ones_start_the_month_before(self):
        for k in self.by_kind("left"):
            rows = self.keys[k]["months"]
            i = next(j for j, r in enumerate(rows) if not r["same"])
            self.assertEqual(rows[i]["pudl"]["report"], rows[i - 1]["month"], k)
            self.assertEqual(self.keys[k]["months_differ"], 1, k)
        sunyf = self.keys["67223/SUNYF"]["months"]
        i = next(j for j, r in enumerate(sunyf) if not r["same"])
        self.assertTrue(canceled(sunyf[i]["workbook"]))

    def test_example(self):
        rows = {r["month"]: r for r in self.keys[EXAMPLE]["months"]}
        self.assertEqual([rows[m]["workbook"]["planned"] for m in ("2026-01", "2026-02", "2026-03")],
                         ["2027-12", "2026-12", "2027-12"])
        for m in ("2026-03", "2026-08"):
            self.assertEqual((rows[m]["pudl"]["planned"], rows[m]["pudl"]["report"]),
                             ("2026-12", "2026-02"))
        self.assertIn("67836/GSP1's planned month went from 2027-12 in January to 2026-12 in "
                      "February and back to 2027-12 in March; PUDL has shown 2026-12 since February",
                      self.text)

    def test_status_samples(self):
        pairs = [(s["workbook"], s["pudl"]) for m in self.raw["months"]
                 for s in m["compare"]["mismatch_samples"]["status"]]
        out_of_service = sum(1 for p in pairs if p[0] == "OP" and p[1] in ("OA", "OS"))
        self.assertGreater(out_of_service, len(pairs) / 2)
        for m in self.raw["months"]:
            re_ = sorted(s["key"] for s in m["compare"]["mismatch_samples"]["status"]
                         if (s["workbook"], s["pudl"]) == ("OP", "RE"))
            self.assertEqual(re_, ["320/1", "320/2"], m["month"])

    def test_august_retired(self):
        aug = self.months["2026-08"]["compare"]
        self.assertEqual(aug["workbook_only_by_sheet"], {"Retired": aug["workbook_only"]})
        for mo, m in self.months.items():
            if mo != "2026-08":
                self.assertEqual(m["compare"]["workbook_only"], 0, mo)

    def test_stated_numbers(self):
        for s in [s % v for s, v in STATED(self)]:
            self.assertIn(s, self.text, s)

    def test_old_text_kept(self):
        self.assertIn("We do not yet know which side reads the file correctly (answered for these "
                      "generators on 21 October 2026; see the follow-up below).", self.full)
        self.assertIn("if it matches no month, the two read the file differently. (Ran 21 October "
                      "2026; see the follow-up below.)", self.full)


def STATED(t):
    diffs = [(h["key"], r["month"]) for h in t.raw["keys"] for r in h["months"] if not r["same"]]
    status = [m["compare"]["fields"]["status"] for m in t.raw["months"]]
    bad = [f["compared"] - f["agree"] for f in status]
    compared = [f["compared"] for f in status]
    aug = t.months["2026-08"]["compare"]
    ran = int(re.search(r"Ran (\d+) tests", t.log).group(1))
    return [
        ("which passed %d of %d unit tests", (ran, ran)),
        ("The %d generators disagree in %d generator-months. In each of the %d",
         (len(t.keys), len(diffs), len(diffs))),
        ("For %d of the %d, the workbook went back", (len(t.by_kind("back")), len(t.keys))),
        ("These %d are not missed changes", (len(t.by_kind("left")),)),
        ("The rule accounts for the %d returns directly", (len(t.by_kind("back")),)),
        ("between %d and %d of the %s to %s generators compared on status disagree",
         (min(bad), max(bad), "{:,}".format(min(compared)), "{:,}".format(max(compared)))),
        ("In August 2026, %d generators on the workbook's Retired sheet, %s MW,",
         (aug["workbook_only"], "{:,.1f}".format(aug["workbook_only_mw_by_sheet"]["Retired"]))),
        ("It is not only these %d.", (len(t.keys),)),
        ("The %d generators behind the July and August shortfall", (len(t.keys),)),
    ]


if __name__ == "__main__":
    unittest.main()
