"""Tests for orders_202c.py. MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

The fixture tests use a hand-built table. The table tests check data/doe_202c_orders.csv
against counts made by hand from DOE's pages; they run wherever that file sits beside
this one (the repo root).
"""

import csv
import datetime as dt
import os
import unittest

import orders_202c as oc

HERE = os.path.dirname(os.path.abspath(__file__))
UNIT_ORDERS = os.path.join(HERE, "data", "doe_202c_unit_orders.csv")


def row(order, kind, area, issued, effective, expires, plant_key="", plant=""):
    return {"order": order, "kind": kind, "area": area, "recipient": area,
            "plant_key": plant_key, "plant": plant, "issued": oc._date(issued),
            "effective": oc._date(effective), "expires": oc._date(expires)}


def fixture():
    return [
        row("E1", "event", "PJM", "2026-01-10", "2026-01-10", "2026-01-12"),
        row("E2", "event", "ERCOT", "2026-01-13", "2026-01-13", "2026-01-14"),  # touches E1
        row("E3", "event", "PJM", "2026-01-16", "2026-01-16", "2026-01-16"),    # one day apart
        row("P1", "plant", "MISO", "2025-12-01", "2025-12-01", "2026-02-28", "x", "X"),
        row("P2", "plant", "MISO", "2026-02-27", "2026-03-01", "2026-05-29", "x", "X"),
        row("P3", "plant", "MISO", "2026-06-05", "2026-06-10", "2026-09-07", "x", "X"),
        row("I1", "island", "Guam", "2026-01-01", "2026-01-02", ""),
    ]


class FixtureTests(unittest.TestCase):
    def test_days(self):
        rows = fixture()
        self.assertEqual(oc.days(rows[0]), 3)
        self.assertEqual(oc.days(rows[2]), 1)
        self.assertIsNone(oc.days(rows[6]))

    def test_validate_clean(self):
        self.assertEqual(oc.validate(fixture()), [])

    def test_validate_problems(self):
        rows = fixture()
        rows.append(row("E1", "event", "PJM", "2026-02-01", "2026-02-01", "2026-03-15"))
        rows.append(row("Q1", "plant", "MISO", "2026-01-01", "2026-01-01", "2026-03-31"))
        rows.append(row("Z1", "storm", "PJM", "2026-01-05", "2026-01-04", "2026-01-03"))
        bad = oc.validate(rows)
        self.assertIn("duplicate order E1", bad)
        self.assertIn("E1: event order without an expiry within 31 days", bad)
        self.assertIn("Q1: plant_key must be set for plant orders and only for them", bad)
        self.assertIn("Z1: unknown kind 'storm'", bad)
        self.assertIn("Z1: starts before it was issued", bad)
        self.assertIn("Z1: expires before it starts", bad)

    def test_episodes(self):
        eps = oc.episodes(fixture())
        self.assertEqual([(e["start"], e["end"], e["days"], e["orders"]) for e in eps],
                         [("2026-01-10", "2026-01-14", 5, 2), ("2026-01-16", "2026-01-16", 1, 1)])
        self.assertEqual(eps[0]["areas"], "ERCOT, PJM")
        self.assertEqual(eps[0]["order_list"], "E1, E2")

    def test_days_covered(self):
        rows = fixture()
        self.assertEqual(oc.days_covered(rows, "event", dt.date(2026, 1, 1), dt.date(2026, 1, 31)), 6)
        self.assertEqual(oc.days_covered(rows, "event", dt.date(2026, 1, 12), dt.date(2026, 1, 13)), 2)
        self.assertEqual(oc.days_covered(rows, "island", dt.date(2026, 1, 1), dt.date(2026, 1, 31)), 0)

    def test_chains(self):
        (c,) = oc.chains(fixture())
        self.assertEqual((c["orders"], c["renewals"], c["first_start"], c["current_order"],
                          c["current_expiry"]), (3, 2, "2025-12-01", "P3", "2026-09-07"))
        # P1 ends 02-28, P2 starts 03-01: no gap. P2 ends 05-29, P3 starts 06-10: 05-30 to 06-09.
        self.assertEqual((c["gaps"], c["gap_days"]), (1, 11))
        self.assertEqual(c["gap_detail"], "2026-05-30 to 2026-06-09 (11 days, between P2 and P3)")
        self.assertEqual(c["span_days"], 281)

    def test_counts_and_render(self):
        res = oc.run(fixture(), dt.date(2026, 1, 31))
        self.assertEqual(res["counts"]["by_year"], {"2025": 1, "2026": 6})
        self.assertEqual(res["counts"]["event_areas"][0],
                         {"year": 2026, "area": "PJM", "orders": 2, "order_days": 4})
        self.assertEqual((res["event_days_this_year"], res["days_this_year"]), (6, 31))
        self.assertEqual(res["counts"]["plant_lengths"], {"89": 3})
        self.assertNotIn("mw", res)
        text = oc.render(res)
        self.assertIn("Plant orders by days from start to expiry: 89 days: 3.", text)
        self.assertIn("Problems found in the table: none", text)
        self.assertIn("at least one event order in force: 6 of 31.", text)
        self.assertNotIn("Summer MW", text)

    def test_mw_under_order(self):
        # Plant y (gas) is under order 06-12 to 06-20; the as-of date 06-15 cuts it to 4 days.
        rows = fixture() + [row("P4", "plant", "PJM", "2026-06-01", "2026-06-12", "2026-06-20",
                                "y", "Y")]
        mw = {"x": {"mw": 100.0, "fuel": "SUB"}, "y": {"mw": 50.5, "fuel": "NG"}}
        m = oc.mw_under_order(rows, mw, dt.date(2026, 6, 15))
        self.assertEqual([(s["date"], s["plants"], s["mw"], s["coal_mw"], s["plant_list"])
                          for s in m["steps"]],
                         [("2025-12-01", 1, 100.0, 100.0, "x"), ("2026-05-30", 0, 0.0, 0.0, ""),
                          ("2026-06-10", 1, 100.0, 100.0, "x"),
                          ("2026-06-12", 2, 150.5, 100.0, "x, y")])
        # x: 90 + 90 + 6 days; y: 4 days.
        self.assertEqual(m["plant_days"], 190)
        self.assertAlmostEqual(m["mw_days"], 18802.0, delta=0.01)
        self.assertAlmostEqual(m["coal_mw_days"], 18600.0, delta=0.01)
        self.assertEqual((m["peak_mw"], m["peak_from"], m["mw_as_of"], m["coal_mw_as_of"]),
                         (150.5, "2026-06-12", 150.5, 100.0))
        self.assertEqual((m["missing_mw"], m["gw_years"]), ([], 0.05))
        text = oc.render(oc.run(rows, dt.date(2026, 6, 15), mw))
        self.assertIn("Plants without a MW row: none", text)
        self.assertIn("Peak 150.5 MW from 2026-06-12; 150.5 MW (100.0 coal) on 2026-06-15.", text)

    def test_mw_missing_and_empty(self):
        rows = fixture() + [row("P4", "plant", "PJM", "2026-06-01", "2026-06-12", "2026-06-20",
                                "y", "Y")]
        m = oc.mw_under_order(rows, {"x": {"mw": 100.0, "fuel": "SUB"}}, dt.date(2026, 6, 15))
        self.assertEqual((m["missing_mw"], m["plant_days"], m["peak_mw"]), (["y"], 186, 100.0))
        # Before any plant order starts there is nothing to count.
        m = oc.mw_under_order(rows, {"x": {"mw": 100.0, "fuel": "SUB"}}, dt.date(2025, 11, 30))
        self.assertEqual((m["steps"], m["plant_days"], m["mw_days"], m["peak_from"]),
                         ([], 0, 0.0, None))


class TableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.path.exists(oc.CSV):
            raise unittest.SkipTest("data/doe_202c_orders.csv not beside this file")
        cls.rows = oc.load()
        cls.res = oc.run(cls.rows, dt.date(2026, 10, 18))

    def test_clean(self):
        self.assertEqual(self.res["problems"], [])

    def test_counts(self):
        c = self.res["counts"]
        self.assertEqual(c["orders"], 85)
        self.assertEqual(c["by_year"], {"2025": 19, "2026": 66})
        self.assertEqual(c["by_kind"], {"plant": 34, "event": 38, "island": 13})
        by = {(r["year"], r["kind"]): r["orders"] for r in c["by_year_kind"]}
        self.assertEqual(by, {(2025, "plant"): 12, (2025, "event"): 1, (2025, "island"): 6,
                              (2026, "plant"): 22, (2026, "event"): 37, (2026, "island"): 7})
        # Plant orders up to 202-26-16 ran 90 days, every one since 89; Wagner's 2025 extension
        # (202-25-6A) ran 66 days, to 31 December.
        self.assertEqual(c["plant_lengths"], {"66": 1, "89": 21, "90": 12})

    def test_event_areas(self):
        got = [(r["area"], r["orders"], r["order_days"]) for r in self.res["counts"]["event_areas"]
               if r["year"] == 2026]
        self.assertEqual(got, [("PJM", 13, 66), ("Duke", 8, 37), ("Florida", 7, 38),
                               ("ERCOT", 3, 10), ("SPP", 3, 18), ("ISO-NE", 2, 23),
                               ("NYISO", 1, 8)])

    def test_episodes(self):
        eps = [e for e in self.res["episodes"] if e["start"] >= "2026"]
        self.assertEqual(len(eps), 9)
        self.assertEqual((eps[0]["start"], eps[0]["end"], eps[0]["days"], eps[0]["orders"]),
                         ("2026-01-24", "2026-02-14", 22, 21))
        self.assertEqual(eps[0]["areas"], "Duke, ERCOT, Florida, ISO-NE, NYISO, PJM")
        self.assertEqual([e["days"] for e in eps], [22, 3, 2, 8, 8, 16, 8, 5, 4])
        self.assertEqual([e["orders"] for e in eps], [21, 1, 1, 5, 2, 2, 2, 2, 1])
        self.assertEqual((self.res["event_days_this_year"], self.res["days_this_year"]), (76, 291))

    def test_chains(self):
        ch = {c["plant_key"]: c for c in self.res["chains"]}
        self.assertEqual(sorted(ch), ["campbell", "centralia", "craig", "culley", "eddystone",
                                      "schahfer", "stanton", "wagner"])
        self.assertEqual(sum(c["renewals"] for c in ch.values()), 26)
        self.assertEqual([k for k, c in sorted(ch.items()) if c["gaps"]], ["wagner"])
        w = ch["wagner"]
        self.assertEqual((w["gap_days"], w["span_days"]), (141, 478))
        self.assertEqual(w["gap_detail"],
                         "2026-01-01 to 2026-05-21 (141 days, between 202-25-6A and 202-26-25)")
        self.assertEqual((ch["campbell"]["first_start"], ch["campbell"]["span_days"],
                          ch["campbell"]["orders"]), ("2025-05-23", 541, 6))
        self.assertEqual(ch["stanton"]["span_days"], 180)
        self.assertEqual({k: (c["current_order"], c["current_expiry"]) for k, c in ch.items()},
                         {"campbell": ("202-26-39", "2026-11-14"),
                          "wagner": ("202-26-25A", "2026-11-17"),
                          "eddystone": ("202-26-40", "2026-11-20"),
                          "stanton": ("202-26-42", "2026-11-30"),
                          "centralia": ("202-26-44", "2026-12-11"),
                          "schahfer": ("202-26-46", "2026-12-18"),
                          "culley": ("202-26-47", "2026-12-18"),
                          "craig": ("202-26-49", "2026-12-25")})

    def test_unit_orders_agree(self):
        """The plant rows match the table the order-dates check used, where it is present."""
        if not os.path.exists(UNIT_ORDERS):
            self.skipTest("data/doe_202c_unit_orders.csv not beside this file")
        with open(UNIT_ORDERS, newline="", encoding="utf-8") as fh:
            unit = list(csv.DictReader(fh))
        plant = {r["order"]: r for r in self.rows if r["kind"] == "plant"}
        self.assertEqual(sorted(plant), sorted(u["order"] for u in unit))
        for u in unit:
            p = plant[u["order"]]
            self.assertEqual((p["plant_key"], p["issued"].isoformat(), p["expires"].isoformat()),
                             (u["plant_key"], u["issued"], u["expires"]), u["order"])
            if u["effective"]:
                self.assertEqual(p["effective"].isoformat(), u["effective"], u["order"])

    def test_mw_under_order(self):
        """Every number in the MW section of docs/doe-202c-orders.md."""
        if not os.path.exists(oc.MW_CSV):
            self.skipTest("data/doe_202c_plant_mw.csv not beside this file")
        mw = oc.load_mw()
        self.assertEqual(sorted(mw), sorted(c["plant_key"] for c in self.res["chains"]))
        as_of = dt.date(2026, 10, 18)
        self.assertEqual({k: len(oc.plant_dates(self.rows, k, as_of)) for k in mw},
                         {"campbell": 514, "eddystone": 507, "wagner": 307, "centralia": 307,
                          "schahfer": 300, "culley": 300, "craig": 293, "stanton": 137})
        m = oc.run(self.rows, as_of, mw)["mw"]
        self.assertEqual([(s["date"], s["plants"], s["mw"], s["coal_mw"]) for s in m["steps"]],
                         [("2025-05-23", 1, 1330.5, 1330.5), ("2025-05-30", 2, 2090.5, 1330.5),
                          ("2025-07-28", 3, 2487.5, 1330.5), ("2025-12-16", 4, 3157.5, 2000.5),
                          ("2025-12-23", 6, 3969.5, 2812.5), ("2025-12-30", 7, 4396.5, 3239.5),
                          ("2026-01-01", 6, 3999.5, 3239.5), ("2026-05-22", 7, 4396.5, 3239.5),
                          ("2026-06-04", 8, 4849.9, 3692.9)])
        self.assertEqual(m["missing_mw"], [])
        self.assertEqual(m["plant_days"], 2665)
        self.assertAlmostEqual(m["mw_days"], 1827592.8, delta=0.01)
        self.assertAlmostEqual(m["coal_mw_days"], 1320393.8, delta=0.01)
        self.assertEqual(m["gw_years"], 5.01)
        self.assertEqual((m["peak_mw"], m["peak_from"], m["mw_as_of"], m["coal_mw_as_of"]),
                         (4849.9, "2026-06-04", 4849.9, 3692.9))


if __name__ == "__main__":
    unittest.main()
