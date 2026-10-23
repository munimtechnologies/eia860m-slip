"""Tests for nexttech.py. MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import unittest

import nexttech as nt


def row(month, key, event, sheet, planned="", mw="1"):
    return {"report_month": month, "key": key, "event": event, "sheet": sheet, "status": "",
            "planned_month": planned, "nameplate_mw": mw}


def many(month, group, n, op):
    return [(month, group, "Operating" if i < op else "Planned", 1.0) for i in range(n)]


class GroupTests(unittest.TestCase):
    def test_tech_group(self):
        for tech, g in (("Solar Photovoltaic", "solar"), ("Batteries", "batteries"),
                        ("Natural Gas Fired Combined Cycle", "gas"), ("Natural Gas Internal Combustion Engine", "gas"),
                        ("Other Natural Gas", "gas"), ("Onshore Wind Turbine", "wind"),
                        ("Offshore Wind Turbine", "wind"), ("Conventional Hydroelectric", "other"),
                        ("Solar Thermal without Energy Storage", "other"), (None, "other"), ("", "other")):
            self.assertEqual(nt.tech_group(tech), g, tech)

    def test_every(self):
        self.assertTrue("2020-01" == nt._Every())
        self.assertFalse("2020-01" != nt._Every())


class CohortTests(unittest.TestCase):
    def test_cohorts(self):
        rows = [row("2020-01", "1/A", "first", "Planned", "2020-02", "10"),
                row("2020-01", "1/B", "first", "Planned", "2020-02", "5"),
                row("2020-01", "1/C", "first", "Operating"),
                row("2020-02", "1/A", "changed", "Operating", "", "10"),
                row("2020-02", "1/D", "first", "Planned", "2020-05", "2")]
        self.assertEqual(nt.cohorts(rows), {"2020-02": [("1/A", "Operating", 10.0), ("1/B", "Planned", 5.0)]})

    def test_tally(self):
        t = nt.tally([("2017-06", "solar", "Operating", 2.0), ("2017-07", "solar", "Planned", 3.0),
                      ("2018-01", "gas", "absent", 4.0)])
        self.assertEqual(t, {("2017", "solar"): [2, 1, 5.0, 2.0], ("2018", "gas"): [1, 0, 4.0, 0.0]})

    def test_period_sum(self):
        rows = many("2015-12", "solar", 5, 5) + many("2016-01", "solar", 4, 1) + many("2019-12", "gas", 2, 2)
        self.assertEqual(nt.period_sum(rows, nt.EARLY), (3, 6))
        self.assertEqual(nt.period_sum(rows, nt.EARLY, "solar"), (1, 4))
        self.assertEqual(nt.period_sum(rows, nt.LATE), (0, 0))
        self.assertIsNone(nt.share((0, 0)))


class ScoreTests(unittest.TestCase):
    def known(self):
        return (many("2017-06", "solar", 2000, 1000) + many("2017-06", "gas", 2223, 980) +
                many("2023-06", "solar", 4000, 1300) + many("2023-06", "gas", 2047, 810))

    def test_score(self):
        p = {x["id"]: x for x in nt.score(self.known(), {})}
        self.assertEqual([p[k]["outcome"] for k in ("T0", "T1", "T2", "T3", "T4")],
                         ["held", "held", "held", "not scored", "held"])
        self.assertTrue(p["T1"]["value"].startswith("0.5000 to 0.3250 (1000 of 2000 to 1300 of 4000)"))
        self.assertTrue(p["T3"]["value"].startswith("too few; 0 of 0 to 0 of 0"))
        self.assertIn("2016-2019 1980 of 4223; 2022-2025 2110 of 6047; without a technology 0 and 0", p["T0"]["value"])

    def test_score_t0_fails(self):
        p = {x["id"]: x for x in nt.score(self.known(), {nt.EARLY: 50})}
        self.assertEqual(p["T0"]["outcome"], "failed")
        self.assertEqual({p[k]["outcome"] for k in ("T1", "T2", "T3", "T4")}, {"not scored"})
        p = {x["id"]: x for x in nt.score(self.known()[1:], {})}
        self.assertEqual(p["T0"]["outcome"], "failed")

    def test_standardized(self):
        rows = (many("2017-01", "solar", 2, 1) + many("2017-01", "gas", 2, 2) +
                many("2023-01", "solar", 6, 3) + many("2023-01", "gas", 2, 2))
        self.assertAlmostEqual(nt.standardized(rows), 0.75)
        self.assertIsNone(nt.standardized(rows + many("2018-01", "wind", 1, 0)))

    def test_t4_fails_when_mix_drives_the_fall(self):
        # same shares inside each technology in both periods; only the mix moves
        rows = (many("2017-01", "solar", 2, 2) + many("2017-01", "gas", 2, 0) +
                many("2023-01", "solar", 1, 1) + many("2023-01", "gas", 3, 0))
        nt_known = nt.KNOWN
        try:
            nt.KNOWN = {nt.EARLY: (2, 4), nt.LATE: (1, 4)}
            p = {x["id"]: x for x in nt.score(rows, {})}
        finally:
            nt.KNOWN = nt_known
        self.assertEqual(p["T0"]["outcome"], "held")
        self.assertEqual(p["T4"]["outcome"], "failed")
        self.assertIn("within 0.0000 of total 0.2500", p["T4"]["value"])


class WaitTests(unittest.TestCase):
    def test_wait_plan(self):
        pages = [b"404: Not Found", b"# Plan\n\nStatus: pre-registered, not yet scored.\n"]
        slept = []
        self.assertTrue(nt.wait_plan(10 ** 12, get=lambda url: pages.pop(0), sleep=slept.append,
                                     clock=lambda: 0))
        self.assertEqual(slept, [600])
        self.assertFalse(nt.wait_plan(5, get=lambda url: b"404", sleep=slept.append, clock=lambda: 10))

    def test_render_error(self):
        self.assertIn("Not run: changelog not read", nt.render({"error": "changelog not read: x"}))


if __name__ == "__main__":
    unittest.main()
