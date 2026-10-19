"""Tests for rehearing_202c.py. MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

The fixture tests use hand-built tables. The table tests check data/doe_202c_rehearing.csv
and data/doe_202c_orders.csv against counts made by hand from DOE's pages; they run wherever
those files sit beside this one (the repo root).
"""

import datetime as dt
import os
import unittest

import orders_202c as oc
import rehearing_202c as rh

AS_OF = dt.date(2026, 10, 19)


def order(o, kind, key, issued, expires):
    return {"order": o, "kind": kind, "plant_key": key, "plant": key.upper(),
            "issued": oc._date(issued), "effective": oc._date(issued),
            "expires": oc._date(expires)}


def reh(o, key, first="", notice="", addressed=""):
    return {"order": o, "plant_key": key, "first_request": oc._date(first),
            "requesters": "A; B" if first else "", "notice": oc._date(notice),
            "notice_order": "", "rehearing_order_date": oc._date(addressed),
            "rehearing_order": "", "page": "", "note": ""}


def orders():
    return [
        order("P1", "plant", "x", "2026-01-01", "2026-03-31"),
        order("P2", "plant", "x", "2026-03-30", "2026-06-28"),
        order("P3", "plant", "y", "2026-05-01", "2026-07-29"),
        order("P4", "plant", "y", "2026-06-20", "2026-09-17"),
        order("E1", "event", "", "2026-01-10", "2026-01-12"),
    ]


def rehearing():
    return [
        reh("P1", "x", "2026-01-25", "2026-03-01", "2026-05-10"),  # addressed 40 days late
        reh("P2", "x", "2026-04-20", "2026-05-25", "2026-06-01"),  # addressed while in force
        reh("P3", "y"),
        reh("P4", "y", "2026-07-15"),
    ]


class FixtureTests(unittest.TestCase):
    def test_join_clean(self):
        rows, bad = rh.join(rehearing(), orders())
        self.assertEqual(bad, [])
        self.assertEqual([r["order"] for r in rows], ["P1", "P2", "P3", "P4"])
        self.assertEqual((rows[0]["issued"], rows[0]["expires"], rows[0]["plant"]),
                         (dt.date(2026, 1, 1), dt.date(2026, 3, 31), "X"))

    def test_join_problems(self):
        def problems(rows):
            return rh.join(rows, orders())[1]
        base = rehearing()
        self.assertIn("duplicate order P1", problems(base + [base[0]]))
        self.assertIn("P3: plant order with no rehearing row",
                      problems([r for r in base if r["order"] != "P3"]))
        self.assertIn("E1: not a plant order in the orders table",
                      problems(base + [reh("E1", "")]))
        rows = rehearing()
        rows[1]["plant_key"] = "y"
        self.assertIn("P2: plant_key 'y', the orders table says 'x'", problems(rows))
        rows = rehearing()
        rows[1] = reh("P2", "x", "2026-03-29")
        self.assertIn("P2: request before the order", problems(rows))
        rows = rehearing()
        rows[3] = reh("P4", "y", "2026-07-21")  # 31 days after 20 June
        self.assertIn("P4: first request more than 30 days after the order", problems(rows))
        rows = rehearing()
        rows[2] = reh("P3", "y", notice="2026-06-15")
        self.assertIn("P3: notice without an earlier request", problems(rows))
        rows = rehearing()
        rows[0] = reh("P1", "x", "2026-01-25", "2026-03-01", "2026-02-01")
        self.assertIn("P1: order on rehearing without an earlier notice", problems(rows))

    def test_status_and_window(self):
        rows, _ = rh.join(rehearing(), orders())
        p1, p2, p3, p4 = rows
        on = dt.date(2026, 7, 20)
        self.assertEqual([rh.status(r, on) for r in rows],
                         ["addressed after expiry", "addressed in force", "no request",
                          "in force, no notice"])
        # 30 days after the order the window is still open; 31 days after it has closed.
        self.assertFalse(rh.window_closed(p4, on))
        self.assertTrue(rh.window_closed(p4, dt.date(2026, 7, 21)))
        self.assertEqual(rh.status(p3, dt.date(2026, 5, 31)), "window open")
        self.assertEqual(rh.status(p4, dt.date(2026, 10, 1)), "expired, not addressed")
        p4n = dict(p4, notice=dt.date(2026, 8, 20))
        self.assertEqual(rh.status(p4n, dt.date(2026, 9, 1)), "in force, notice")

    def test_summary_and_render(self):
        res = rh.run(rehearing(), orders(), dt.date(2026, 7, 20))
        s = res["summary"]
        self.assertEqual(res["problems"], [])
        self.assertEqual((s["orders"], s["window_closed"], s["requested"],
                          s["requested_window_closed"], s["notices"],
                          s["notices_before_expiry"], s["addressed"]), (4, 3, 3, 2, 2, 2, 2))
        # P1 24 days, P2 21, P4 25; both notices came 35 days after the request.
        self.assertEqual(s["days_to_request"], {"n": 3, "min": 21, "median": 24, "max": 25})
        self.assertEqual(s["days_to_notice"], {"n": 2, "min": 35, "median": 35, "max": 35})
        self.assertEqual(s["addressed_vs_expiry"], [-27, 40])
        self.assertEqual(s["status"]["addressed after expiry"], 1)
        self.assertEqual(s["status"]["window open"], 0)
        self.assertEqual(sum(s["status"].values()), 4)
        self.assertEqual([(p["plant_key"], p["orders"], p["window_closed"], p["requested"],
                           p["notices"], p["addressed"]) for p in s["plants"]],
                         [("x", 2, 2, 2, 2, 2), ("y", 2, 1, 1, 0, 0)])
        d = {r["order"]: r for r in res["detail"]}
        self.assertEqual((d["P1"]["days_after_expiry"], d["P2"]["days_after_expiry"],
                          d["P3"]["days_after_expiry"]), (40, -27, ""))
        text = rh.render(res)
        self.assertIn("Problems found in the tables: none", text)
        self.assertIn("- Plant orders: 4; 30-day window closed: 3; with a request for "
                      "rehearing: 3 (2 of them with the window closed).", text)
        self.assertIn("- Days from order to first request: 21 to 25 (median 24).", text)
        self.assertIn("days after the expiry of the order addressed: -27, 40 (median 6.5).",
                      text)


class TableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (os.path.exists(rh.CSV) and os.path.exists(oc.CSV)):
            raise unittest.SkipTest("data/doe_202c_rehearing.csv or doe_202c_orders.csv "
                                    "not beside this file")
        cls.res = rh.run(rh.load(), oc.load(), AS_OF)
        cls.s = cls.res["summary"]
        cls.d = {r["order"]: r for r in cls.res["detail"]}

    def test_clean(self):
        self.assertEqual(self.res["problems"], [])

    def test_counts(self):
        s = self.s
        self.assertEqual((s["orders"], s["window_closed"], s["requested"],
                          s["requested_window_closed"], s["notices"],
                          s["notices_before_expiry"], s["addressed"]),
                         (34, 33, 25, 25, 24, 24, 10))

    def test_timing(self):
        """Every timing figure in docs/doe-202c-rehearing.md."""
        self.assertEqual(self.s["days_to_request"], {"n": 25, "min": 19, "median": 28, "max": 30})
        self.assertEqual(self.s["days_to_notice"], {"n": 24, "min": 31, "median": 34, "max": 46})
        self.assertEqual(self.s["addressed_vs_expiry"], [18, 63, 70, 70, 86, 86, 99, 117, 117, 135])
        self.assertEqual(self.s["addressed_vs_expiry_spread"]["median"], 86)

    def test_status(self):
        self.assertEqual(self.s["status"], {
            "no request": 8, "window open": 1, "addressed in force": 0,
            "addressed after expiry": 10, "expired, not addressed": 13,
            "in force, notice": 1, "in force, no notice": 1})
        self.assertEqual(sorted(o for o, r in self.d.items() if r["status"] == "no request"),
                         ["202-25-6", "202-25-6A", "202-26-25", "202-26-25A", "202-26-42",
                          "202-26-44", "202-26-46", "202-26-47"])
        self.assertEqual(self.d["202-26-49"]["status"], "window open")
        self.assertEqual(self.d["202-26-39"]["status"], "in force, notice")
        self.assertEqual(self.d["202-26-40"]["status"], "in force, no notice")

    def test_plants(self):
        got = {p["plant_key"]: (p["orders"], p["window_closed"], p["requested"], p["notices"],
                                p["addressed"]) for p in self.s["plants"]}
        self.assertEqual(got, {"campbell": (6, 6, 6, 6, 2), "centralia": (4, 4, 3, 3, 1),
                               "craig": (4, 3, 3, 3, 1), "culley": (4, 4, 3, 3, 2),
                               "eddystone": (6, 6, 6, 5, 2), "schahfer": (4, 4, 3, 3, 2),
                               "stanton": (2, 2, 1, 1, 0), "wagner": (4, 4, 0, 0, 0)})

    def test_rows(self):
        c = self.d["202-25-3"]
        self.assertEqual((c["first_request"], c["notice"], c["addressed"],
                          c["days_after_expiry"], c["status"]),
                         ("2025-06-18", "2025-07-28", "2025-09-08", 18,
                          "addressed after expiry"))
        e = self.d["202-25-4"]
        self.assertEqual((e["expires"], e["addressed"], e["days_after_expiry"]),
                         ("2025-08-28", "2026-01-10", 135))
        for o in ("202-26-19", "202-26-20"):
            self.assertEqual((self.d[o]["addressed"], self.d[o]["days_after_expiry"]),
                             ("2026-10-16", 117))

    def test_pages(self):
        for r in rh.load():
            self.assertTrue(r["page"].startswith(
                "https://www.energy.gov/ceser/federal-power-act-section-202c-"), r["order"])


if __name__ == "__main__":
    unittest.main()
