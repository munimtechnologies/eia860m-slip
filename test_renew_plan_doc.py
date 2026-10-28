"""Checks docs/renew-plan.md against data/doe_202c_orders.csv.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import collections
import csv
import datetime
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
AS_OF = "2026-10-28"
MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December")

# (forecast, orders, chance) as stated in the plan's table.
TABLE = (
    ("R1", ("202-26-38",), "60%"),
    ("R2", ("202-25-1E", "202-25-2E"), "90%"),
    ("R3", ("202-26-39",), "85%"),
    ("R4", ("202-26-25A",), "65%"),
    ("R5", ("202-26-40",), "90%"),
    ("R6", ("202-26-42",), "85%"),
    ("R7", ("202-26-44",), "90%"),
    ("R8", ("202-26-46",), "90%"),
    ("R9", ("202-26-47",), "90%"),
    ("R10", ("202-26-49",), "90%"),
)


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


def rows(path):
    with open(os.path.join(HERE, path), encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def day(text):
    return datetime.date.fromisoformat(text)


def long_date(text):
    d = day(text)
    return "%d %s %d" % (d.day, MONTHS[d.month - 1], d.year)


def pairs(seq):
    seq = sorted(seq, key=lambda r: r["issued"])
    return [(a, b) for a, b in zip(seq, seq[1:]) if a["expires"]]


class RenewPlanDocTests(unittest.TestCase):
    def setUp(self):
        self.doc = read("docs/renew-plan.md")
        self.orders = rows("data/doe_202c_orders.csv")
        self.by_order = {r["order"]: r for r in self.orders}

    def test_status_and_newest_order(self):
        self.assertIn("Status: pre-registered, not yet scored.", self.doc)
        newest = max(self.orders, key=lambda r: r["issued"])
        self.assertEqual((newest["order"], newest["issued"]), ("202-26-50", "2026-10-12"))
        self.assertIn("the newest order on DOE's page was 202-26-50 (12 October)", self.doc)

    def test_open_orders_are_the_table(self):
        open_ = [r for r in self.orders if r["kind"] in ("plant", "island") and r["expires"] > AS_OF]
        self.assertEqual(sorted(r["order"] for r in open_), sorted(o for _, orders, _ in TABLE for o in orders))
        kinds = collections.Counter(r["kind"] for r in open_)
        self.assertEqual(kinds, {"plant": 8, "island": 3})
        self.assertIn("eleven DOE orders under section 202(c) of the Federal Power Act were still in force: "
                      "eight plant orders and three island orders", self.doc)
        for rid, orders, chance in TABLE:
            recs = [self.by_order[o] for o in orders]
            self.assertEqual(len({r["expires"] for r in recs}), 1, rid)
            names = {r["plant"] or r["recipient"] for r in recs}
            self.assertEqual(len(names), 1, rid)
            line = "| %s | %s | %s | %s | %s |" % (rid, " and ".join(orders), names.pop(), recs[0]["expires"], chance)
            self.assertIn(line, self.doc)

    def test_expected_count(self):
        total = sum(int(chance.rstrip("%")) for _, _, chance in TABLE)
        self.assertEqual(total, 835)
        self.assertIn("Our expected count is %.2f renewals in time out of 10." % (total / 100.0), self.doc)

    def test_plant_record(self):
        lines = collections.defaultdict(list)
        for r in self.orders:
            if r["kind"] == "plant":
                lines[r["plant_key"]].append(r)
        cases = [(key, a, b) for key, seq in lines.items() for a, b in pairs(seq)]
        self.assertEqual(len(cases), 26)
        late = [(key, a, b) for key, a, b in cases if b["issued"] > a["expires"]]
        self.assertEqual(len(late), 1)
        key, a, b = late[0]
        self.assertEqual((key, a["order"], b["order"]), ("wagner", "202-25-6A", "202-26-25"))
        self.assertIn("%s expired on %s, and the next Wagner order, %s, was issued on %s."
                      % (a["order"], long_date(a["expires"]), b["order"], long_date(b["issued"])), self.doc)
        leads = collections.Counter((day(a["expires"]) - day(b["issued"])).days
                                    for _, a, b in cases if b["issued"] <= a["expires"])
        self.assertEqual(leads, {0: 9, 1: 9, 2: 4, 3: 3})
        parts = "; ".join("%d %s: %d" % (d, "day" if d == 1 else "days", n) for d, n in sorted(leads.items()))
        self.assertIn("In 25 of 26 the next order was issued on or before the day the earlier one expired, "
                      "0 to 3 days before it (%s)." % parts, self.doc)
        self.assertEqual("{:.0%}".format(25 / 26), "96%")
        self.assertIn("the plant base rate, 25 of 26 (96%)", self.doc)
        self.assertIn("the constant 96% forecast", self.doc)
        self.assertIn("Wagner's is the only plant line that has lapsed", self.doc)

    def test_island_record(self):
        series = collections.defaultdict(list)
        for r in self.orders:
            if r["kind"] == "island":
                series[re.sub(r"[A-Z]$", "", r["order"])].append(r)
        self.assertEqual(sorted(series), ["202-25-1", "202-25-2", "202-26-38"])
        cases = [(a, b) for key in ("202-25-1", "202-25-2") for a, b in pairs(series[key])]
        self.assertEqual(len(cases), 8)
        for a, b in cases:
            self.assertEqual(a["recipient"], "PREPA")
            self.assertLessEqual(b["issued"], a["expires"], b["order"])
            self.assertIn((day(a["expires"]) - day(b["issued"])).days, (0, 1, 2), b["order"])
        self.assertIn("every time 0 to 2 days before expiry (8 of 8)", self.doc)
        guam = series["202-26-38"]
        self.assertEqual(len(guam), 1)
        self.assertEqual(guam[0]["recipient"], "Guam Power Authority")
        self.assertIn("202-26-38 is the first and only Guam order, issued on %s" % long_date(guam[0]["issued"]),
                      self.doc)

    def test_orders_since_ruling(self):
        since = sorted((r for r in self.orders if r["kind"] == "plant" and r["issued"] >= "2026-09-11"),
                       key=lambda r: r["order"])
        self.assertEqual([(r["plant_key"], r["issued"]) for r in since],
                         [("centralia", "2026-09-11"), ("schahfer", "2026-09-18"), ("culley", "2026-09-18"),
                          ("craig", "2026-09-25")])
        self.assertIn("Since that day DOE has issued 4 plant orders (Centralia on 11 September, Schahfer and "
                      "Culley on 18 September, Craig on 25 September)", self.doc)


if __name__ == "__main__":
    unittest.main()
