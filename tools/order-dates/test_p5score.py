"""Unit tests for p5score.py on hand-built sheets (no network).

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import unittest

import p5score as ps

HEADER = ["Entity ID", "Entity Name", "Plant ID", "Plant Name", "Plant State", "Generator ID",
          "Nameplate Capacity (MW)", "Operating Month", "Operating Year", "Planned Retirement Month",
          "Planned Retirement Year", "Status"]


def sheet(*data):
    return [["U.S. Energy Information Administration"], [None], HEADER] + [list(r) for r in data]


def row(pid, gid, month, year, name="X", mw=100.0):
    return [1, "Owner", pid, name, "MI", gid, mw, 1, 1970, month, year, "(OP) Operating"]


class HelperTests(unittest.TestCase):
    def test_norm_id(self):
        self.assertEqual(ps.norm_id(1710.0), "1710")
        self.assertEqual(ps.norm_id(1710), "1710")
        self.assertEqual(ps.norm_id(" C1 "), "C1")
        self.assertEqual(ps.norm_id("17.0"), "17")
        self.assertEqual(ps.norm_id(None), "")
        self.assertEqual(ps.norm_id(float("nan")), "")

    def test_ym(self):
        self.assertEqual(ps.ym(2026, 11), "2026-11")
        self.assertEqual(ps.ym("2026", "9"), "2026-09")
        self.assertEqual(ps.ym(2026.0, 12.0), "2026-12")
        self.assertEqual(ps.ym(None, 3), "")
        self.assertEqual(ps.ym(2026, 13), "")
        self.assertEqual(ps.ym(2026, " "), "")

    def test_find_header(self):
        self.assertEqual(ps.find_header(sheet()), 2)
        self.assertIsNone(ps.find_header([["a", "b"], ["Plant ID", "x"]]))

    def test_wanted(self):
        self.assertEqual(ps.WANTED[("1710", "3")], "campbell")
        self.assertEqual(ps.WANTED[("6021", "C1")], "craig")
        self.assertNotIn(("6021", "2"), ps.WANTED)
        self.assertEqual(len(ps.UNITS), 8)
        self.assertEqual(sorted(ps.P5_TARGETS), sorted(ps.W1_TARGETS))
        self.assertEqual(ps.P5_NEED, 3)


class MatchTests(unittest.TestCase):
    def test_match_rows(self):
        rows = sheet(row(1710, "1", 11, 2026), row(1710.0, 2.0, 11, 2026), row(6021, "c1", 12, 2026),
                     row(6021, "2", 12, 2028), row(9999, "1", 1, 2027), ["Note: totals", None])
        found, info = ps.match_rows("Operating", rows)
        self.assertEqual([r["key"] for r in found], ["1710/1", "1710/2", "6021/c1"])
        self.assertEqual([r["plant"] for r in found], ["campbell", "campbell", "craig"])
        self.assertEqual(found[0]["retirement_ym"], "2026-11")
        self.assertEqual(found[0]["status"], "(OP) Operating")
        self.assertEqual(found[0]["mw"], 100.0)
        self.assertEqual(info["header_row"], 2)
        self.assertEqual(info["retirement_columns"], ["Planned Retirement Year", "Planned Retirement Month"])

    def test_sheet_without_header(self):
        self.assertEqual(ps.match_rows("Notes", [["About this file"], ["x"]]), ([], None))

    def test_short_rows(self):
        found, _ = ps.match_rows("Operating", sheet([1, "Owner", 1710, "X", "MI", "1"]))
        self.assertEqual(found[0]["retirement_ym"], "")
        self.assertIsNone(found[0]["mw"])


def rec(plant, sheet_name, month):
    return {"plant": plant, "sheet": sheet_name, "key": plant, "plant_name": "", "status": "",
            "retirement_ym": month, "mw": None}


class JudgeTests(unittest.TestCase):
    def test_exact(self):
        self.assertEqual(ps.judge([rec("c", "Operating", "2026-11"), rec("c", "Operating", "2026-11")], "2026-11"),
                         ("exact", ["2026-11"]))

    def test_undated_unit_ignored(self):
        self.assertEqual(ps.judge([rec("c", "Operating", "2026-11"), rec("c", "Operating", "")], "2026-11")[0],
                         "exact")

    def test_mixed_is_other(self):
        self.assertEqual(ps.judge([rec("c", "Operating", "2026-11"), rec("c", "Operating", "2027-02")], "2026-11"),
                         ("other", ["2026-11", "2027-02"]))

    def test_retired_sheet_not_counted(self):
        self.assertEqual(ps.judge([rec("c", "Retired", "2026-09")], "2026-09"), ("no month", []))
        self.assertEqual(ps.judge([], "2026-09"), ("no month", []))


class ScoreTests(unittest.TestCase):
    def aug(self):
        return [rec(p, "Operating", t) for p, t in ps.W1_TARGETS.items()]

    def test_held(self):
        sep = [rec("campbell", "Operating", "2026-11"), rec("schahfer", "Operating", "2027-01"),
               rec("culley", "Operating", "2026-12"), rec("craig", "Operating", "2026-12")]
        s = ps.score(sep, self.aug())
        self.assertTrue(s["w1_held"])
        self.assertEqual((s["p5_exact"], s["p5_verdict"]), (3, "held"))
        self.assertEqual(s["p5"]["schahfer"]["class"], "other")
        self.assertEqual(s["other"]["stanton"]["class"], "no month")

    def test_failed(self):
        sep = [rec("campbell", "Operating", "2026-11"), rec("craig", "Retired", "2026-09")]
        s = ps.score(sep, self.aug())
        self.assertEqual((s["p5_exact"], s["p5_verdict"]), (1, "failed"))

    def test_w1_gates(self):
        sep = [rec(p, "Operating", t) for p, t in ps.P5_TARGETS.items()]
        aug = self.aug()[1:]
        s = ps.score(sep, aug)
        self.assertFalse(s["w1_held"])
        self.assertEqual(s["p5_verdict"], "not scored (W1 failed)")
        self.assertEqual(s["p5_exact"], 4)

    def test_render(self):
        sep = [rec(p, "Operating", t) for p, t in ps.P5_TARGETS.items()]
        s = ps.score(sep, self.aug())
        f = {"url": "u", "size": 1234, "md5": "m", "same_as_recorded": True}
        s.update({"files": {"september": f, "august": f}, "rows": {"september": sep, "august": self.aug()}})
        md = ps.render(s)
        self.assertIn("P5: 4 of 4 exact (needs 3): **held**", md)
        self.assertIn("| campbell | 2026-11 | exact | 2026-11 |", md)
        self.assertIn("1,234 bytes", md)


if __name__ == "__main__":
    unittest.main()
