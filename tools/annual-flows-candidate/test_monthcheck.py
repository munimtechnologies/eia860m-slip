"""Tests for monthcheck.py on a hand-built changelog of three months: two generators planned for
February (one comes online, one slips to April), one planned for March that leaves, a retired one
that leaves and comes back. MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import unittest

import gapcensus as gc
import monthcheck as mc


def row(month, key, event, sheet="", status="", planned="", mw=""):
    pid, gid = key.split("/", 1)
    return {"report_month": month, "key": key, "plant_id_eia": pid, "generator_id": gid, "event": event,
            "sheet": sheet, "status": status, "planned_month": planned, "nameplate_mw": mw}


ROWS = [row("2026-01", "1/A", "first", "Planned", "U", "2026-02", "10.0"),
        row("2026-01", "2/B", "first", "Planned", "V", "2026-02", "5.0"),
        row("2026-01", "3/C", "first", "Planned", "U", "2026-03", "2.0"),
        row("2026-01", "4/D", "first", "Retired", "RE", "", "1.0"),
        row("2026-01", "5/E", "first", "Operating", "OP", "", "7.0"),
        row("2026-02", "1/A", "changed", "Operating", "OP", "", "10.0"),
        row("2026-02", "2/B", "changed", "Planned", "V", "2026-04", "5.0"),
        row("2026-02", "4/D", "left"),
        row("2026-03", "3/C", "left"),
        row("2026-03", "4/D", "back", "Retired", "RE", "", "1.0"),
        row("2026-03", "6/F", "first", "Planned", "P", "2026-04", "nan")]


def fake(i, share, listed=1000, left=3, retired=0):
    """A month's stats as replay writes them, i months after 2024-08."""
    return {"month": gc.m_str(gc.m_index("2024-08") + i), "listed": listed, "events": {"left": left},
            "left_by_sheet": {"Retired": retired} if retired else {}, "cohort": 100,
            "cohort_by": {"Operating": 0 if share is None else int(round(share * 100))},
            "share_operating": share}


def history(target_share, **kw):
    """24 prior months with shares 0.10 to 0.33, then the target month 2026-08."""
    return [fake(i, (i + 10) / 100) for i in range(24)] + [fake(24, target_share, **kw)]


class HelperTests(unittest.TestCase):
    def test_mw(self):
        self.assertEqual([mc.mw(x) for x in ("1.5", "", "nan", None, "x")], [1.5, 0.0, 0.0, 0.0, 0.0])

    def test_band(self):
        self.assertEqual(mc.band([0.3, 0.1, 0.5, 0.2]), (0.2, 0.3))
        self.assertIsNone(mc.band([1, 2]))

    def test_bars_match_plan(self):
        self.assertEqual((mc.KEYS_TOL, mc.LEFT_MAX, mc.RETIRED_LEFT_BELOW, mc.BAND_MONTHS), (0.03, 50, 10, 24))


class ReplayTests(unittest.TestCase):
    def test_months(self):
        s = mc.replay(ROWS)
        self.assertEqual([x["month"] for x in s], ["2026-01", "2026-02", "2026-03"])
        self.assertEqual([x["listed"] for x in s], [5, 4, 5])
        self.assertEqual(s[0]["events"], {"first": 5})
        self.assertEqual((s[0]["cohort"], s[0]["share_operating"]), (0, None))

    def test_february(self):
        f = mc.replay(ROWS)[1]
        self.assertEqual(f["events"], {"changed": 2, "left": 1})
        self.assertEqual(f["left_by_sheet"], {"Retired": 1})
        self.assertEqual(f["cohort"], 2)
        self.assertEqual(f["cohort_by"], {"Operating": 1, "Planned": 1, "Retired": 0, "other": 0, "absent": 0})
        self.assertEqual(f["cohort_mw_by"]["Operating"], 10.0)
        self.assertEqual(f["cohort_mw"], 15.0)
        self.assertEqual(f["planned_later"], 1)
        self.assertEqual(f["share_operating"], 0.5)

    def test_march(self):
        s = mc.replay(ROWS, detail_for="2026-03")
        m = s[2]
        self.assertEqual(m["events"], {"left": 1, "back": 1, "first": 1})
        self.assertEqual(m["left_by_sheet"], {"Planned": 1})
        self.assertEqual((m["cohort"], m["cohort_by"]["absent"], m["share_operating"]), (1, 1, 0.0))
        self.assertEqual(m["detail"], [{"key": "3/C", "status_before": "U", "nameplate_mw": "2.0",
                                        "now": "absent", "status_now": "", "planned_month_now": ""}])
        self.assertNotIn("detail", s[1])


class ScoreTests(unittest.TestCase):
    def held(self, stats, eia=None):
        return [p["held"] for p in mc.score(stats, "2026-08", eia)["predictions"]]

    def test_all_held(self):
        r = mc.score(history(0.25, listed=1020), "2026-08", {"plan": "append", "readable": True})
        self.assertEqual([p["held"] for p in r["predictions"]], [True, True, True, True])
        self.assertEqual(r["band"], (0.11, 0.32))
        self.assertEqual(r["band_months"], ["2024-08", "2026-07"])
        self.assertEqual((r["held"], r["scored"]), (4, 4))

    def test_failures(self):
        self.assertEqual(self.held(history(0.40, listed=1040, left=51, retired=10)), [False, False, False, False])
        self.assertEqual(self.held(history(0.25, left=50, retired=9)), [True, True, True, True])
        self.assertEqual(self.held(history(0.25), {"plan": "append", "readable": False}), [False, True, True, True])

    def test_not_scored(self):
        short = [fake(i, (i + 10) / 100) for i in range(10)] + [fake(10, 0.2)]
        self.assertEqual([p["held"] for p in mc.score(short, short[-1]["month"])["predictions"]],
                         [True, True, True, None])
        self.assertEqual(self.held(history(None)), [True, True, True, None])

    def test_missing_target(self):
        stats = [fake(i, 0.2) for i in range(3)]
        r = mc.score(stats, "2026-09", {"plan": "append", "errors": ["404"]})
        self.assertEqual([p["held"] for p in r["predictions"]], [None, None, None, None])
        self.assertEqual(r["scored"], 0)
        r = mc.score(stats, "2026-09", {"plan": "append", "md5": "x", "readable": False})
        self.assertEqual([p["held"] for p in r["predictions"]], [False, None, None, None])


class RenderTests(unittest.TestCase):
    def test_render(self):
        s = mc.replay(ROWS, detail_for="2026-02")
        r = {"target": "2026-02", "mode": "practice", "months": s, "score": mc.score(s, "2026-02"),
             "target_stats": s[1]}
        md = mc.render(r)
        self.assertIn("| P2 | held | 1 left | at most 50 |", md)
        self.assertIn("| P4 | not scored |", md)
        self.assertIn("| Operating | 1 | 10.0 |", md)
        self.assertIn("| 2026-02 | 4 | 0 | 2 | 1 | 0 | 1 | 2 | 1 | 0.5000 |", md)
        self.assertIn("Not run: x", mc.render({"target": "2026-09", "error": "x"}))


if __name__ == "__main__":
    unittest.main()
