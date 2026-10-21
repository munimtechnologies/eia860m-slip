"""Checks the numbers in docs/workbook-route.md against the raw output of compete jobs
wbcheck-v2 (data/wbcheck_v2_workbook.json, data/wbcheck_v2_rawcheck.json,
docs/wbcheck-v2-unittests.txt) and wbcheck-v1 (data/wbcheck_v1_workbook.json).
MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
MONTHS = ("2026-08", "2026-07")
USABLE = 0.98
UNIT_TESTS = 24
TABLE = "Generators that differ in both July and August"
WINDOW = ("2026-04", "2026-08")


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8") as fh:
        return fh.read()


def tables(text):
    """Map each '## ' heading to the tables under it, each a list of {column: cell} rows."""
    out, head, cols = {}, None, None
    for line in text.splitlines():
        if line.startswith("## "):
            head, cols = line[3:].strip(), None
            out[head] = []
        elif line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if cols is None:
                cols = cells
                out.setdefault(head, []).append([])
            elif not all(c and set(c) <= set("-:") for c in cells):
                out[head][-1].append(dict(zip(cols, cells)))
        else:
            cols = None
    return out


def month_n(text):
    y, m = text.split("-")
    return int(y) * 12 + int(m) - 1


def wcell(w):
    return "%s, %s, %.1f MW" % (w["status"], w["planned"], w["mw"])


class WorkbookRouteDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = read("docs", "workbook-route.md")
        cls.doc = tables(cls.text)
        v2 = json.loads(read("data", "wbcheck_v2_workbook.json"))
        v1 = json.loads(read("data", "wbcheck_v1_workbook.json"))
        cls.raw = json.loads(read("data", "wbcheck_v2_rawcheck.json"))
        cls.log = read("docs", "wbcheck-v2-unittests.txt")
        cls.v2 = {m["report"]: m for m in v2["months"]}
        cls.v1 = {m["report"]: m for m in v1["months"]}
        cls.detail = {mo: {d["key"]: d for d in cls.v2[mo]["difference_detail"]} for mo in MONTHS}
        aug, jul = (set(cls.detail[mo]) for mo in MONTHS)
        cls.standing = sorted(aug & jul)
        cls.aug_only, cls.jul_only = sorted(aug - jul), sorted(jul - aug)

    def pudl_in_force(self, key):
        """The latest PUDL record shown for key in either month's detail that is in force
        through August, or None."""
        recs = [r for mo in MONTHS for r in self.detail[mo][key]["pudl"] if r["until"] == "2026-08"]
        return max(recs, key=lambda r: r["report"]) if recs else None

    # ---- raw output ----

    def test_self_check_rules(self):
        for mo in MONTHS:
            c = self.v2[mo]["self_check"]
            self.assertEqual(c["same_share"], round(c["same_change"] / c["union"], 4))
            self.assertEqual(c["usable"], c["same_change"] >= USABLE * c["union"])
            self.assertFalse(c["usable"])
            self.assertEqual(c["pudl_rows_same_share"], 1.0)
            self.assertEqual(c["same_change"], c["pudl_rows"])
            self.assertEqual(c["union"], c["workbook_rows"])
            self.assertEqual(sum(c["differences"].values()), c["union"] - c["same_change"])
            self.assertTrue(all(k.startswith("none -> ") for k in c["differences"]))
            self.assertEqual(len(c["difference_sample"]), c["union"] - c["same_change"])
            self.assertEqual(sorted(d["key"] for d in c["difference_sample"]),
                             sorted(self.detail[mo]))

    def test_same_as_v1(self):
        for mo in MONTHS:
            a, b = self.v1[mo]["self_check"], self.v2[mo]["self_check"]
            for k in ("pudl_rows", "workbook_rows", "union", "same_change", "same_share"):
                self.assertEqual(a[k], b[k], "%s %s" % (mo, k))

    def test_rawcheck(self):
        self.assertEqual(len(self.raw["copies"]), 1)
        copy = self.raw["copies"][0]
        self.assertEqual((copy["first_id"], copy["first_version"], copy["first_date"]),
                         ("22995197", "50.0.0", "2026-09-27"))
        self.assertTrue(copy["checksum_ok"])
        self.assertEqual(self.raw["since"], "2026-09-24")
        months = {m["month"]: m for m in self.raw["months"]}
        self.assertEqual(sorted(months), sorted(MONTHS))
        for mo, m in months.items():
            self.assertEqual(len(m["copies"]), 1)
            self.assertTrue(m["copies"][0]["same_file"])
            self.assertEqual(m["copies"][0]["md5"], m["eia_md5"])
            self.assertIn("md5 %s" % m["eia_md5"], self.text)
            self.assertIsNone(m["eia_error"])
            self.assertEqual([k["key"] for k in m["keys"]],
                             [d["key"] for d in self.v2[mo]["self_check"]["difference_sample"]])

    def test_unit_tests(self):
        ran = int(re.search(r"Ran (\d+) tests", self.log).group(1))
        self.assertEqual(ran, UNIT_TESTS)
        self.assertEqual(len(re.findall(r" \.\.\. ok$", self.log, re.M)), ran)
        self.assertTrue(self.log.rstrip().endswith("OK"))

    # ---- the note ----

    def test_standing_table(self):
        rows = self.table_rows()
        self.assertEqual([x["generator"] for x in rows], self.standing)
        for x in rows:
            k = x["generator"]
            aug, jul = (self.detail[mo][k]["workbook"] for mo in MONTHS)
            self.assertEqual(aug, jul, k)
            self.assertEqual(x["EIA workbook, July and August"], wcell(aug))
            p = self.pudl_in_force(k)
            if p is None:
                self.assertFalse([r for mo in MONTHS for r in self.detail[mo][k]["pudl"]])
                want = "none reported %s to %s" % WINDOW
            else:
                want = "%s, %s (reported %s)" % (p["status"], p["planned"], p["report"])
            self.assertEqual(x["PUDL record in force through August"], want, k)

    def table_rows(self):
        self.assertIn(TABLE, self.doc)
        return self.doc[TABLE][0]

    def test_prose_claims(self):
        later = same_planned = none = 0
        for k in self.standing:
            w, p = self.detail["2026-08"][k]["workbook"], self.pudl_in_force(k)
            if p is None:
                none += 1
            elif p["status"] == w["status"] and 1 <= month_n(w["planned"]) - month_n(p["planned"]) <= 2:
                later += 1
            elif p["status"] != w["status"] and p["planned"] == w["planned"]:
                same_planned += 1
        self.assertEqual((later, same_planned, none), (4, 2, 2))
        self.assertEqual(later + same_planned + none, len(self.standing))
        # the windows of the two months' detail together run from April to August
        self.assertEqual(month_n("2026-07") - 3, month_n(WINDOW[0]))
        # "August's other 3 differences are ...; July's other 5 are ..."
        self.assertIn("August's other %d differences are %s" % (
            len(self.aug_only), ", ".join(self.aug_only[:-1]) + " and " + self.aug_only[-1]), self.text)
        self.assertIn("July's other %d are %s" % (
            len(self.jul_only), ", ".join(self.jul_only[:-1]) + " and " + self.jul_only[-1]), self.text)

    def test_stated_numbers(self):
        for s in [s % v for s, v in STATED(self)]:
            self.assertIn(s, self.text, s)


def STATED(t):
    aug, jul = (t.v2[mo]["self_check"] for mo in MONTHS)
    ran = int(re.search(r"Ran (\d+) tests", t.log).group(1))
    return [
        ("the route is not usable yet: %s for August 2026 and %s for July",
         (aug["same_share"], jul["same_share"])),
        ("at least %.2f of the generators listed in either edition", (USABLE,)),
        ("passed %d of %d unit tests", (ran, ran)),
        ("August: %d of %d generators have the same change (%s); July: %d of %d (%s)",
         (aug["same_change"], aug["union"], aug["same_share"], jul["same_change"], jul["union"],
          jul["same_share"])),
        ("does not list at all: %d in August, %d in July",
         (aug["union"] - aug["same_change"], jul["union"] - jul["same_change"])),
        ("%d of August's %d differing generators are also among July's %d",
         (len(t.standing), len(t.detail["2026-08"]), len(t.detail["2026-07"]))),
        ("For %d of the %d, PUDL has a record in force through August",
         (sum(1 for k in t.standing if t.pudl_in_force(k)), len(t.standing))),
        ("For the other %d, PUDL's records include none reported from April to August 2026",
         (sum(1 for k in t.standing if t.pudl_in_force(k) is None),)),
        ("sets these %d generators' workbook rows beside",
         (len(set(t.detail["2026-08"]) | set(t.detail["2026-07"])),)),
        ("version %s, first published %s", (t.raw["copies"][0]["first_version"],
                                           t.raw["copies"][0]["first_date"])),
    ]


if __name__ == "__main__":
    unittest.main()
