"""Tests for entrytime.py on hand-built tables. MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import math
import unittest

import pandas as pd

import entrytime as et


def m(year, month):
    return float(year * 12 + month - 1)


def frame(recs):
    return pd.DataFrame(recs, columns=["key", "group", "mw", "first_m"])


def first():
    """First EIA-860M report month per key, as entry860.entries returns it."""
    return pd.DataFrame({"first_m": [m(2018, 4), m(2017, 5), m(2019, 2), m(2018, 11),
                                     m(2017, 9)]},
                        index=["1/A", "2/B", "3/C", "5/E", "6/F"])


def sets_2018():
    b = pd.DataFrame({"key": ["1/A", "2/B", "3/C", "4/D"]})
    f = pd.DataFrame({"key": ["1/A", "2/B", "3/C"], "group": ["solar", "solar", "wind_onshore"],
                      "mw": [10.0, 20.0, 30.0],
                      "entry": ["entered_after_january", "in_january_other_month",
                                "entered_after_january"],
                      "first_m": [m(2018, 4), m(2017, 5), m(2019, 2)]})
    new = pd.DataFrame({"year": [2018] * 4, "nkey": ["1/A", "5/E", "6/F", None],
                        "group": ["solar", "solar", "battery", "solar"],
                        "mw": [10.0, 7.0, 8.0, 2.0]})
    return et.sets(b, f, new, first())


def sets_2019():
    return {"A": frame([("9/X", "solar", 50.0, m(2019, 3))]),
            "A_built": frame([("9/X", "solar", 50.0, m(2019, 3))]),
            "B": frame([("8/Y", "solar", 25.0, m(2019, 8))])}


def trow(year, s, group, total, **kw):
    r = {"year": year, "set": s, "group": group, "total_mw": total}
    r.update({k: 0.0 for k in et.BUCKETS})
    r.update(kw)
    return r


def published_rows():
    """'all' and 'solar' rows whose totals equal the published figures, keyed for editing."""
    rows = {}
    for y, (ea, ne, nin) in et.PUBLISHED.items():
        for s, v in (("A", ea), ("A_built", nin), ("B", round(ne - nin, 1))):
            for g in ("all", "solar"):
                rows[(y, s, g)] = trow(y, s, g, v, m05=v)
    return rows


class SetTests(unittest.TestCase):
    def test_bucket(self):
        self.assertEqual([et.bucket(x, 2018) for x in (float("nan"), None, m(2017, 12),
                                                       m(2018, 1), m(2018, 3), m(2018, 12),
                                                       m(2019, 1))],
                         ["unlisted", "unlisted", "before", "m01", "m03", "m12", "after"])

    def test_first_month(self):
        got = et.first_month(["1/A", None, "zz"], first())
        self.assertEqual(got[0], m(2018, 4))
        self.assertTrue(math.isnan(got[1]) and math.isnan(got[2]))

    def test_sets(self):
        s = sets_2018()
        self.assertEqual(list(s["A"]["key"]), ["1/A", "3/C"])
        self.assertEqual(list(s["A_built"]["key"]), ["1/A"])
        self.assertEqual(list(s["B"]["mw"]), [7.0, 8.0, 2.0])
        self.assertEqual(list(s["B"]["first_m"][:2]), [m(2018, 11), m(2017, 9)])
        self.assertTrue(math.isnan(s["B"]["first_m"].iloc[2]))

    def test_timing(self):
        s = sets_2018()
        a, b = et.timing(s["A"], 2018), et.timing(s["B"], 2018)
        self.assertEqual({k: v for k, v in a.items() if v}, {"m04": 10.0, "after": 30.0})
        self.assertEqual({k: v for k, v in b.items() if v},
                         {"before": 8.0, "m11": 7.0, "unlisted": 2.0})
        self.assertEqual(sorted(a), sorted(et.BUCKETS))


class SummaryTests(unittest.TestCase):
    def rows(self):
        return {(x["year"], x["set"], x["group"]): x
                for x in et.summarize({2018: sets_2018(), 2019: sets_2019()})}

    def test_keys(self):
        r = self.rows()
        self.assertEqual(len(r), 22)
        self.assertIn((2018, "B", "battery"), r)
        self.assertIn((et.POOLED, "A", "wind_onshore"), r)
        self.assertNotIn((et.POOLED, "A_built", "battery"), r)

    def test_year_rows(self):
        r = self.rows()
        a = r[(2018, "A", "all")]
        self.assertEqual((a["m04"], a["after"], a["total_mw"], a["mar_jun_share"],
                          a["oct_dec_share"]), (10.0, 30.0, 40.0, 1.0, 0.0))
        b = r[(2018, "B", "all")]
        self.assertEqual((b["before"], b["m11"], b["unlisted"], b["total_mw"], b["mar_jun_share"],
                          b["oct_dec_share"]), (8.0, 7.0, 2.0, 17.0, 0.0, 1.0))
        w = r[(2018, "A", "wind_onshore")]
        self.assertEqual((w["total_mw"], w["mar_jun_share"], w["oct_dec_share"]),
                         (30.0, None, None))  # nothing listed in February-December

    def test_pooled(self):
        r = self.rows()
        a = r[(et.POOLED, "A", "all")]
        self.assertEqual((a["m03"], a["m04"], a["after"], a["total_mw"], a["mar_jun_share"]),
                         (50.0, 10.0, 30.0, 90.0, 1.0))
        b = r[(et.POOLED, "B", "all")]
        self.assertEqual((b["m08"], b["m11"], b["total_mw"], b["mar_jun_share"]),
                         (25.0, 7.0, 42.0, 0.0))
        self.assertAlmostEqual(b["oct_dec_share"], 7.0 / 32.0, places=3)
        pooled = [k for k in r if k[0] == et.POOLED]
        self.assertEqual([k[1:] for k in pooled],
                         [("A", "all"), ("A", "solar"), ("A", "wind_onshore"),
                          ("A_built", "all"), ("A_built", "solar"), ("B", "all"),
                          ("B", "battery"), ("B", "solar")])

    def test_checks_on_summary(self):
        c = et.checks(et.summarize({2018: sets_2018(), 2019: sets_2019()}))
        # Totals are not the published ones and the groups add up; B's 2018 'unlisted' 2.0 MW
        # is above its limit, max(0.05, 1% of 17.0).
        self.assertFalse(c["U1"]["pass"])
        self.assertTrue(c["U2"]["pass"])
        self.assertEqual(c["U3"]["stray_mw"], {"2018 B": 2.0})


class CheckTests(unittest.TestCase):
    def test_all_pass(self):
        self.assertTrue(et.checks(list(published_rows().values()))["all_pass"])

    def test_u1(self):
        rows = published_rows()
        for g in ("all", "solar"):
            rows[(2018, "B", g)]["total_mw"] += 0.12  # within B's tolerance of 0.15
        self.assertTrue(et.checks(list(rows.values()))["all_pass"])
        for g in ("all", "solar"):
            rows[(2020, "A", g)]["total_mw"] += 0.2
        c = et.checks(list(rows.values()))
        self.assertEqual((c["U1"]["pass"], c["U2"]["pass"], c["all_pass"]), (False, True, False))
        del rows[(2025, "A_built", "all")]
        self.assertIsNone(et.checks(list(rows.values()))["U1"]["got"][2025]["A_built"])

    def test_u2(self):
        rows = published_rows()
        rows[(2018, "B", "solar")]["total_mw"] += 1.0
        c = et.checks(list(rows.values()))
        self.assertEqual((c["U2"]["groups_not_adding_up"], c["all_pass"]), (["2018 B"], False))

    def test_u3(self):
        rows = published_rows()
        rows[(2019, "B", "all")]["unlisted"] = 20.0  # B 2019 is 2,143.7 MW: limit 21.4
        self.assertTrue(et.checks(list(rows.values()))["U3"]["pass"])
        rows[(2019, "B", "all")]["unlisted"] = 25.0
        rows[(2019, "A", "all")]["m01"] = 3.0
        c = et.checks(list(rows.values()))
        self.assertEqual(c["U3"]["stray_mw"], {"2019 A": 3.0, "2019 B": 25.0})
        self.assertFalse(c["all_pass"])


class PredictionTests(unittest.TestCase):
    def test_pooled(self):
        rows = [trow(et.POOLED, "A", "all", 95.0, m03=30.0, m04=30.0, m08=30.0, m10=5.0),
                trow(et.POOLED, "A_built", "all", 40.0, m05=10.0, m11=30.0),
                trow(et.POOLED, "B", "all", 40.0, m03=10.0, m09=30.0)]
        p = et.predictions(rows)
        self.assertEqual((p["P1"]["A_mar_jun_share"], p["P1"]["held"]), (0.6316, True))
        self.assertEqual((p["P2"]["difference"], p["P2"]["held"]), (0.3816, True))
        self.assertEqual((p["P3"]["years"], p["P3"]["held"]), ([], None))  # not scorable
        self.assertEqual((p["P4"]["difference"], p["P4"]["held"]), (0.0, False))
        self.assertEqual((p["P5"]["A_oct_dec_share"], p["P5"]["held"]), (0.0526, True))

    def test_p3(self):
        def rows(n):
            out = []
            for i, y in enumerate(et.SCORED):
                out.append(trow(y, "A", "all", 10.0, m03=6.0 if i < n else 4.0,
                                m08=4.0 if i < n else 6.0))
                out.append(trow(y, "B", "all", 10.0, m03=5.0, m08=5.0))
            return out
        p = et.predictions(rows(5))
        self.assertEqual((p["P3"]["years_A_above_B"], p["P3"]["held"]),
                         ([2018, 2019, 2020, 2021, 2022], False))
        self.assertTrue(et.predictions(rows(6))["P3"]["held"])
        self.assertIsNone(et.predictions(rows(6))["P1"]["held"])

    def test_empty(self):
        p = et.predictions([])
        self.assertEqual([p[k]["held"] for k in ("P1", "P2", "P3", "P4", "P5")], [None] * 5)


if __name__ == "__main__":
    unittest.main()
