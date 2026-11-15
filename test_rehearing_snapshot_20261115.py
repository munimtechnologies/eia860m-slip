"""Checks data/doe_202c_rehearing_2026-11-15.csv, the 15 November 2026 snapshot of the
rehearing record of every DOE Federal Power Act 202(c) plant order.

MV2 of Munim, Inc. (made with AI agents working in MV2's name). Apache-2.0.

Standard library only and self-contained: the snapshot carries each order's issue and expiry
dates, so this file does not need orders_202c.py or rehearing_202c.py. The counts below were
made by hand from DOE's order pages (read 2026-11-15) and are the figures quoted in
docs/doe-202c-rehearing-2026-11-15.md. The 19 October 2026 table (data/doe_202c_rehearing.csv)
is left unchanged as the base of the predictions stated on that day.
"""

import csv
import datetime as dt
import os
import statistics
import unittest
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "data", "doe_202c_rehearing_2026-11-15.csv")
AS_OF = dt.date(2026, 11, 15)
WINDOW_DAYS = 30  # Federal Power Act section 313(a)
DATES = ("issued", "expires", "first_request", "notice", "rehearing_order_date")
COLUMNS = ["order", "plant_key", "issued", "expires", "first_request", "requesters", "notice",
           "notice_order", "rehearing_order_date", "rehearing_order", "page", "note"]
PAGE_PREFIX = "https://www.energy.gov/ceser/federal-power-act-section-202c-"


def load(path=CSV):
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        header = reader.fieldnames
        rows = list(reader)
    for r in rows:
        for c in DATES:
            r[c] = dt.date.fromisoformat(r[c]) if r[c] else None
    return header, rows


def window_closed(r, as_of=AS_OF):
    return (as_of - r["issued"]).days > WINDOW_DAYS


def status(r, as_of=AS_OF):
    if r["first_request"] is None:
        return "window open" if not window_closed(r, as_of) else "no request"
    if r["rehearing_order_date"] is not None:
        if r["rehearing_order_date"] <= r["expires"]:
            return "addressed in force"
        return "addressed after expiry"
    if r["expires"] < as_of:
        return "expired, not addressed"
    return "in force, notice" if r["notice"] is not None else "in force, no notice"


def problems(rows):
    bad = []
    seen = Counter(r["order"] for r in rows)
    bad += ["duplicate order %s" % o for o, n in sorted(seen.items()) if n > 1]
    for r in rows:
        o, fr, nt, ro = r["order"], r["first_request"], r["notice"], r["rehearing_order_date"]
        if r["expires"] <= r["issued"]:
            bad.append("%s: expires before it is issued" % o)
        if fr is not None and fr < r["issued"]:
            bad.append("%s: request before the order" % o)
        if fr is not None and (fr - r["issued"]).days > WINDOW_DAYS:
            bad.append("%s: first request more than 30 days after the order" % o)
        if bool(fr) != bool(r["requesters"]):
            bad.append("%s: request date and requesters disagree" % o)
        if nt is not None and (fr is None or nt < fr):
            bad.append("%s: notice without an earlier request" % o)
        if ro is not None and (nt is None or ro < nt):
            bad.append("%s: order on rehearing without an earlier notice" % o)
        if nt is not None and nt > AS_OF or ro is not None and ro > AS_OF:
            bad.append("%s: date after the snapshot" % o)
    return bad


def spread(xs):
    return {"n": len(xs), "min": min(xs), "median": statistics.median(xs), "max": max(xs)}


class SnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.header, cls.rows = load()
        cls.d = {r["order"]: r for r in cls.rows}
        cls.asked = [r for r in cls.rows if r["first_request"] is not None]

    def test_shape(self):
        self.assertEqual(self.header, COLUMNS)
        self.assertEqual(len(self.rows), 35)
        self.assertEqual(problems(self.rows), [])
        for r in self.rows:
            self.assertTrue(r["page"].startswith(PAGE_PREFIX), r["order"])

    def test_plants(self):
        got = {}
        for key in sorted({r["plant_key"] for r in self.rows}):
            sel = [r for r in self.rows if r["plant_key"] == key]
            got[key] = (len(sel), sum(window_closed(r) for r in sel),
                        sum(r["first_request"] is not None for r in sel),
                        sum(r["notice"] is not None for r in sel),
                        sum(r["rehearing_order_date"] is not None for r in sel))
        self.assertEqual(got, {"campbell": (7, 6, 6, 6, 2), "centralia": (4, 4, 4, 4, 1),
                               "craig": (4, 4, 4, 3, 1), "culley": (4, 4, 4, 3, 2),
                               "eddystone": (6, 6, 6, 6, 2), "schahfer": (4, 4, 4, 3, 2),
                               "stanton": (2, 2, 2, 2, 0), "wagner": (4, 4, 0, 0, 0)})

    def test_counts(self):
        closed = [r for r in self.rows if window_closed(r)]
        self.assertEqual(len(closed), 34)
        self.assertEqual(sum(r["first_request"] is not None for r in closed), 30)
        # Every plant order with a closed window drew a request, except the four Wagner
        # orders, which PJM itself applied for.
        no_req = sorted(r["order"] for r in closed if r["first_request"] is None)
        self.assertEqual(no_req, ["202-25-6", "202-25-6A", "202-26-25", "202-26-25A"])
        self.assertEqual({self.d[o]["plant_key"] for o in no_req}, {"wagner"})
        notices = [r for r in self.asked if r["notice"] is not None]
        self.assertEqual(len(notices), 27)
        self.assertEqual(sum(r["notice"] <= r["expires"] for r in notices), 27)
        self.assertEqual(sum(r["rehearing_order_date"] is not None for r in self.rows), 10)

    def test_timing(self):
        to_request = [(r["first_request"] - r["issued"]).days for r in self.asked]
        self.assertEqual(spread(to_request), {"n": 30, "min": 19, "median": 28, "max": 30})
        to_notice = sorted((r["notice"] - r["first_request"]).days for r in self.asked
                           if r["notice"] is not None)
        self.assertEqual(to_notice, [31] * 4 + [32] * 5 + [33] * 3 + [34] * 7 + [35] * 2 +
                         [36] * 3 + [37, 40, 46])
        self.assertEqual(spread(to_notice), {"n": 27, "min": 31, "median": 34, "max": 46})
        vs_expiry = sorted((r["rehearing_order_date"] - r["expires"]).days for r in self.rows
                           if r["rehearing_order_date"] is not None)
        self.assertEqual(vs_expiry, [18, 63, 70, 70, 86, 86, 99, 117, 117, 135])

    def test_new_since_19_october(self):
        """The rows that changed since the 19 October 2026 table."""
        d = self.d
        self.assertEqual((d["202-26-40"]["notice"], d["202-26-40"]["notice_order"]),
                         (dt.date(2026, 10, 22), "202-26-40A"))
        self.assertEqual((d["202-26-40"]["notice"] - d["202-26-40"]["first_request"]).days, 35)
        self.assertEqual((d["202-26-42"]["first_request"], d["202-26-42"]["notice"],
                          d["202-26-42"]["notice_order"]),
                         (dt.date(2026, 10, 1), dt.date(2026, 11, 3), "202-26-42A"))
        self.assertEqual((d["202-26-42"]["first_request"] - d["202-26-42"]["issued"]).days, 30)
        self.assertEqual((d["202-26-44"]["first_request"], d["202-26-44"]["requesters"],
                          d["202-26-44"]["notice"], d["202-26-44"]["notice_order"]),
                         (dt.date(2026, 10, 8), "WA; PIOs", dt.date(2026, 11, 10),
                          "202-26-44A"))
        for o in ("202-26-46", "202-26-47"):
            self.assertEqual((d[o]["first_request"], d[o]["requesters"], d[o]["notice"]),
                             (dt.date(2026, 10, 16), "MN+IL+WI+MI; PIOs", None))
        self.assertEqual((d["202-26-49"]["first_request"], d["202-26-49"]["requesters"],
                          d["202-26-49"]["notice"]),
                         (dt.date(2026, 10, 23), "Tri-State+Platte River; CO; PIOs", None))
        self.assertEqual((d["202-26-51"]["issued"], d["202-26-51"]["expires"],
                          d["202-26-51"]["first_request"]),
                         (dt.date(2026, 11, 13), dt.date(2027, 2, 12), None))

    def test_status(self):
        st = Counter(status(r) for r in self.rows)
        self.assertEqual(dict(st), {"no request": 4, "window open": 1,
                                    "addressed after expiry": 10,
                                    "expired, not addressed": 14, "in force, notice": 3,
                                    "in force, no notice": 3})
        by = lambda s: sorted(r["order"] for r in self.rows if status(r) == s)
        self.assertEqual(by("in force, notice"), ["202-26-40", "202-26-42", "202-26-44"])
        self.assertEqual(by("in force, no notice"), ["202-26-46", "202-26-47", "202-26-49"])
        self.assertEqual(by("window open"), ["202-26-51"])
        self.assertIn("202-26-39", by("expired, not addressed"))
        # The 19 October snapshot day: 202-26-39 was then in force with a notice.
        self.assertEqual(status(self.d["202-26-39"], dt.date(2026, 10, 19)), "in force, notice")

    def test_status_rules(self):
        r = {"issued": dt.date(2026, 1, 1), "expires": dt.date(2026, 3, 31),
             "first_request": None, "notice": None, "rehearing_order_date": None}
        self.assertEqual(status(r, dt.date(2026, 1, 31)), "window open")
        self.assertEqual(status(r, dt.date(2026, 2, 1)), "no request")
        r = dict(r, first_request=dt.date(2026, 1, 20))
        self.assertEqual(status(r, dt.date(2026, 2, 1)), "in force, no notice")
        r = dict(r, notice=dt.date(2026, 2, 25))
        self.assertEqual(status(r, dt.date(2026, 3, 1)), "in force, notice")
        self.assertEqual(status(r, dt.date(2026, 4, 1)), "expired, not addressed")
        self.assertEqual(status(dict(r, rehearing_order_date=dt.date(2026, 3, 30)),
                                dt.date(2026, 4, 1)), "addressed in force")
        self.assertEqual(status(dict(r, rehearing_order_date=dt.date(2026, 5, 1)),
                                dt.date(2026, 6, 1)), "addressed after expiry")


if __name__ == "__main__":
    unittest.main()
