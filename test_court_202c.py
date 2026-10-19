"""Tests for court_202c.py. MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

The fixture tests use hand-built tables. The table tests check data/doe_202c_petitions.csv
and data/doe_202c_orders.csv against counts made by hand from CourtListener's dockets; they
run wherever those files sit beside this one (the repo root).
"""

import datetime as dt
import os
import unittest

import court_202c as ct
import orders_202c as oc

AS_OF = dt.date(2026, 10, 19)


def order(o, kind, key, issued, expires):
    return {"order": o, "kind": kind, "plant_key": key, "plant": key.upper(),
            "issued": oc._date(issued), "effective": oc._date(issued),
            "expires": oc._date(expires)}


def pet(d, court, filed, o, ev, key, lead, status, on=""):
    return {"docket": d, "court": court, "case_name": "C v. DOE", "filed": oc._date(filed),
            "petitioners": "A; B", "order": o, "order_evidence": ev, "plant_key": key,
            "lead": lead, "status": status, "status_date": oc._date(on), "source": "",
            "note": ""}


def orders():
    return [
        order("P1", "plant", "x", "2026-01-01", "2026-03-31"),
        order("P2", "plant", "y", "2026-02-01", "2026-05-01"),
        order("E1", "event", "", "2026-01-10", "2026-01-12"),
    ]


def petitions():
    return [
        pet("1", "cadc", "2026-03-01", "P1", "petition", "x", "1", "decided", "2026-09-01"),
        pet("2", "cadc", "2026-04-10", "P1", "filing", "x", "1", "decided", "2026-09-01"),
        pet("3", "ca9", "2026-05-11", "P2", "petition", "y", "", "abeyance", "2026-06-01"),
        pet("4", "cadc", "", "", "", "x-y", "3", "abeyance", "2026-06-01"),
        pet("5", "cadc", "2026-04-20", "", "", "y", "", "no later order seen"),
    ]


class FixtureTests(unittest.TestCase):
    def test_join_clean(self):
        rows, bad = ct.join(petitions(), orders())
        self.assertEqual(bad, [])
        self.assertEqual([r["docket"] for r in rows], ["1", "2", "3", "4", "5"])
        self.assertEqual((rows[0]["issued"], rows[0]["expires"]),
                         (dt.date(2026, 1, 1), dt.date(2026, 3, 31)))
        self.assertEqual((rows[3]["issued"], rows[3]["expires"]), (None, None))

    def test_join_problems(self):
        def problems(rows):
            return ct.join(rows, orders())[1]

        def changed(i, **kw):
            rows = petitions()
            rows[i] = dict(rows[i], **kw)
            return problems(rows)
        base = petitions()
        self.assertIn("duplicate docket 1", problems(base + [base[0]]))
        self.assertIn("3: court 'ca5'", changed(2, court="ca5"))
        self.assertIn("4: status 'stayed'", changed(3, status="stayed"))
        self.assertIn("5: status date does not fit status 'no later order seen'",
                      changed(4, status_date=dt.date(2026, 6, 1)))
        self.assertIn("1: status date does not fit status 'decided'",
                      changed(0, status_date=None))
        self.assertIn("3: status dated before the petition",
                      changed(2, status_date=dt.date(2026, 5, 1)))
        self.assertIn("4: plant_key 'x-z' not in the orders table", changed(3, plant_key="x-z"))
        self.assertIn("4: lead docket 9 not in the table", changed(3, lead="9"))
        self.assertIn("5: order '' with evidence 'petition'", changed(4, order_evidence="petition"))
        self.assertIn("1: order 'P1' with evidence 'blog'", changed(0, order_evidence="blog"))
        self.assertIn("1: E1 is not a plant order in the orders table", changed(0, order="E1"))
        self.assertIn("2: plant_key 'y', the orders table says 'x'", changed(1, plant_key="y"))
        self.assertIn("3: petition before the order", changed(2, filed=dt.date(2026, 1, 15)))

    def test_summary_and_render(self):
        res = ct.run(petitions(), orders(), dt.date(2026, 10, 1))
        s = res["summary"]
        self.assertEqual(res["problems"], [])
        self.assertEqual(s["petitions"], 5)
        self.assertEqual(s["courts"], {"ca9": 1, "cadc": 4})
        self.assertEqual(s["status"], {"decided": 2, "abeyance": 2, "briefing": 0,
                                       "no later order seen": 1})
        self.assertEqual(s["order_evidence"], {"filing": 1, "none": 2, "petition": 2})
        self.assertEqual(s["orders_named"], ["P1", "P2"])
        # 1: 30 days before P1 expired; 2: 10 days after; 3: 10 days after P2 expired.
        self.assertEqual(s["filed_vs_expiry"], [-30, 10, 10])
        self.assertEqual(s["filed_vs_expiry_spread"], {"n": 3, "min": -30, "median": 10,
                                                       "max": 10})
        self.assertEqual((s["filed_in_force"], s["filed_after_expiry"]), (1, 2))
        # 1 March to 1 September 2026 is 184 days; 31 March to 1 September is 154.
        self.assertEqual(s["decided"], [{"order": "P1", "petitions": 2, "decided": "2026-09-01",
                                         "days_after_first_petition": 184,
                                         "days_after_expiry": 154}])
        self.assertEqual(s["abeyance_orders"], {"2026-06-01": 2})
        # 5 (20 April) is older than 3 (11 May); 4 has no filing date.
        self.assertEqual(s["oldest_open"], {"docket": "5", "filed": "2026-04-20",
                                            "status": "no later order seen", "days_open": 164})
        self.assertEqual([(p["plant_key"], p["petitions"], p["orders_named"], p["decided"],
                           p["abeyance"]) for p in s["plants"]],
                         [("x", 2, "P1", 2, 0), ("x-y", 1, "", 0, 1), ("y", 2, "P2", 0, 1)])
        d = {r["docket"]: r for r in res["detail"]}
        self.assertEqual((d["1"]["days_after_expiry"], d["4"]["days_after_expiry"],
                          d["5"]["days_after_expiry"]), (-30, "", ""))
        text = ct.render(res)
        self.assertIn("Problems found in the tables: none", text)
        self.assertIn("- Petitions: 5 (ca9 1, cadc 4).", text)
        self.assertIn("- Status: decided 2, abeyance 2, briefing 0, no later order seen 1.", text)
        self.assertIn("- Plant orders named in the record: 2 (P1, P2).", text)
        self.assertIn("- Days from the named order's expiry to the petition: -30 to 10 "
                      "(median 10); 1 filed while the order was in force, 2 after it expired.",
                      text)
        self.assertIn("- Decided: P1 (2 petitions) on 2026-09-01, 184 days after the first "
                      "petition and 154 days after the order expired.", text)
        self.assertIn("- Oldest open petition: 5, filed 2026-04-20, 164 days open "
                      "(no later order seen).", text)


class TableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (os.path.exists(ct.CSV) and os.path.exists(oc.CSV)):
            raise unittest.SkipTest("data/doe_202c_petitions.csv or doe_202c_orders.csv "
                                    "not beside this file")
        cls.res = ct.run(ct.load(), oc.load(), AS_OF)
        cls.s = cls.res["summary"]
        cls.d = {r["docket"]: r for r in cls.res["detail"]}

    def test_clean(self):
        self.assertEqual(self.res["problems"], [])

    def test_counts(self):
        """Every count in docs/doe-202c-court.md."""
        s = self.s
        self.assertEqual(s["petitions"], 35)
        self.assertEqual(s["courts"], {"ca9": 3, "cadc": 32})
        self.assertEqual(s["status"], {"decided": 3, "abeyance": 21, "briefing": 3,
                                       "no later order seen": 8})
        self.assertEqual(s["order_evidence"], {"filing": 7, "none": 13, "petition": 14,
                                               "secondary": 1})
        self.assertEqual(s["orders_named"], [
            "202-25-11", "202-25-12", "202-25-13", "202-25-14", "202-25-3", "202-25-4",
            "202-25-7", "202-25-8", "202-25-9", "202-26-22"])

    def test_timing(self):
        s = self.s
        self.assertEqual(s["filed_vs_expiry"], [-41, -34, -28, -28, -27, -26, -21, -19, -13,
                                                -13, -12, -12, -7, -7, 10, 10, 10, 22, 25, 27,
                                                28, 29])
        self.assertEqual(s["filed_vs_expiry_spread"], {"n": 22, "min": -41, "median": -12,
                                                       "max": 29})
        self.assertEqual((s["filed_in_force"], s["filed_after_expiry"]), (14, 8))
        self.assertEqual(s["decided"], [{"order": "202-25-3", "petitions": 3,
                                         "decided": "2026-09-11",
                                         "days_after_first_petition": 414,
                                         "days_after_expiry": 386}])
        self.assertEqual(s["oldest_open"], {"docket": "25-1193", "filed": "2025-09-25",
                                            "status": "abeyance", "days_open": 389})

    def test_abeyance(self):
        self.assertEqual(self.s["abeyance_orders"], {
            "2026-02-18": 3, "2026-03-13": 1, "2026-06-08": 3, "2026-07-28": 10,
            "2026-08-26": 4})
        self.assertEqual(sorted(k for k, r in self.d.items() if r["status"] == "briefing"),
                         ["26-1252", "26-1261", "26-3781"])
        self.assertEqual(sorted(k for k, r in self.d.items()
                                if r["status"] == "no later order seen"),
                         ["26-1024", "26-1028", "26-1167", "26-1224", "26-1233", "26-1255",
                          "26-1256", "26-1273"])

    def test_plants(self):
        got = {p["plant_key"]: (p["petitions"], p["orders_named"], p["decided"], p["abeyance"])
               for p in self.s["plants"]}
        self.assertEqual(got, {
            "campbell": (9, "202-25-3, 202-25-7, 202-25-9, 202-26-22", 3, 3),
            "centralia": (3, "202-25-11", 0, 0),
            "craig": (6, "202-25-14", 0, 3),
            "culley": (2, "202-25-13", 0, 2),
            "eddystone": (6, "202-25-4, 202-25-8", 0, 5),
            "schahfer": (3, "202-25-12", 0, 3),
            "schahfer-culley": (5, "", 0, 5),
            "stanton": (1, "", 0, 0)})

    def test_rows(self):
        self.assertEqual((self.d["25-1159"]["order"], self.d["25-1159"]["days_after_expiry"]),
                         ("202-25-3", -28))
        self.assertEqual((self.d["26-1233"]["order"], self.d["26-1233"]["days_after_expiry"],
                          self.d["26-1233"]["status"]), ("202-26-22", 25, "no later order seen"))
        self.assertEqual(self.d["26-1101"]["filed"], "")

    def test_sources(self):
        for r in ct.load():
            self.assertTrue(r["source"].startswith("https://www.courtlistener.com/"), r["docket"])


if __name__ == "__main__":
    unittest.main()
