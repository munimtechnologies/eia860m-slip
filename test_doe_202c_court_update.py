"""Checks the dated update of 28 October 2026 in docs/doe-202c-court.md (DOE's petition for rehearing in
Michigan v. DOE, No. 25-1159): its dates by arithmetic and the order expiries it quotes against
data/doe_202c_orders.csv. MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import csv
import datetime as dt
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
HEADING = "## Update of 28 October 2026: DOE asked for rehearing on the last day"
DECIDED = dt.date(2026, 9, 11)
NEXT = (("202-26-39", "campbell", "2026-11-14"), ("202-26-25A", "wagner", "2026-11-17"),
        ("202-26-40", "eddystone", "2026-11-20"), ("202-26-42", "stanton", "2026-11-30"))


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8") as fh:
        return fh.read()


def day(s):
    return dt.date.fromisoformat(s)


class CourtUpdateDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = read("docs", "doe-202c-court.md")
        cls.before, cls.update = cls.text.split(HEADING)
        with open(os.path.join(HERE, "data", "doe_202c_orders.csv"), encoding="utf-8-sig", newline="") as fh:
            cls.orders = {r["order"]: r for r in csv.DictReader(fh)}

    def test_earlier_text_kept(self):
        self.assertEqual(self.text.count(HEADING), 1)
        self.assertIn("DOE's time to ask the full D.C. Circuit to rehear *Michigan v. DOE* runs to 26 October 2026. "
                      "On 19 October we found no report of a filing.", self.before)
        self.assertTrue(self.before.rstrip().endswith("Data: CC BY 4.0. Code: Apache-2.0."))
        self.assertIn("Status: dated update; description only, nothing is scored.", self.update)
        self.assertIn("`data/doe_202c_petitions.csv` is still as of 19 October.", self.update)

    def test_filing_date(self):
        due = DECIDED + dt.timedelta(days=45)
        self.assertEqual(due, dt.date(2026, 10, 26))
        self.assertEqual(due.strftime("%A"), "Monday")
        self.assertIn("on Monday, 26 October 2026", self.update)
        self.assertIn("11 September plus 45 days is 26 October.", self.update)
        self.assertIn("We have not read the petition or the docket entry itself.", self.update)

    def test_mandate_and_craig(self):
        self.assertEqual(dt.date(2026, 10, 26) + dt.timedelta(days=7), dt.date(2026, 11, 2))
        self.assertIn("would have issued on 2 November 2026 (26 October plus 7 days)", self.update)
        self.assertEqual(DECIDED + dt.timedelta(days=60), dt.date(2026, 11, 10))
        self.assertIn("counted from 11 September is 10 November 2026", self.update)
        for group in ("2026-08-26 | 4 |", "2026-02-18 | 3 |", "2026-06-08 | 3 |"):
            self.assertIn(group, self.before)

    def test_next_expiries(self):
        for order, plant, expires in NEXT:
            r = self.orders[order]
            self.assertEqual((r["plant_key"], r["expires"]), (plant, expires))
            self.assertIn(order, self.update)
            self.assertIn("%d November" % day(expires).day, self.update)
        self.assertIn("Campbell's sixth order, 202-26-39, expires 14 November 2026", self.update)

    def test_campbell_renewals(self):
        rows = sorted((r for r in self.orders.values() if r["kind"] == "plant" and r["plant_key"] == "campbell"),
                      key=lambda r: r["issued"])
        self.assertEqual([r["order"] for r in rows],
                         ["202-25-3", "202-25-7", "202-25-9", "202-26-16", "202-26-22", "202-26-39"])
        for prev, nxt in zip(rows, rows[1:]):
            self.assertLessEqual(day(nxt["issued"]), day(prev["expires"]), nxt["order"])
        self.assertIn("The orders table holds six Campbell orders, each of the last five issued no later than the "
                      "day the one before it expired", self.update)

    def test_no_newer_plant_order(self):
        nums = [int(k.split("-")[2].rstrip("ABCDE")) for k in self.orders if k.startswith("202-26-")]
        self.assertEqual(max(nums), 50)
        r = self.orders["202-26-50"]
        self.assertEqual((r["plant_key"], r["issued"], r["effective"], r["expires"]),
                         ("", "2026-10-12", "2026-10-13", "2026-10-16"))
        self.assertIn("lists nothing after 202-26-50 (PJM, 12 October 2026, in force 13 to 16 October)", self.update)

    def test_scope(self):
        self.assertIn("this section only records dates and filings", self.update)
        self.assertNotIn("MIT", self.text)


if __name__ == "__main__":
    unittest.main()
