"""Unit tests for coalsep.py on hand-built sheets (no network).

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import unittest

import coalsep as cs

OP_HEADER = ["Entity ID", "Entity Name", "Plant ID", "Plant Name", "Plant State", "Generator ID",
             "Nameplate Capacity (MW)", "Net Summer Capacity (MW)", "Technology", "Energy Source Code",
             "Operating Month", "Operating Year", "Planned Retirement Month", "Planned Retirement Year", "Status"]
RET_HEADER = ["Entity ID", "Entity Name", "Plant ID", "Plant Name", "Plant State", "Generator ID",
              "Nameplate Capacity (MW)", "Net Summer Capacity (MW)", "Technology", "Energy Source Code",
              "Operating Month", "Operating Year", "Retirement Month", "Retirement Year"]


def sheet(header, *data):
    return [["U.S. Energy Information Administration"], [None], header] + [list(r) for r in data]


def op(pid, gid, month, year, mw=100.0, summer=90.0, esc="SUB", tech="Conventional Steam Coal", name="X"):
    return [1, "Owner", pid, name, "MN", gid, mw, summer, tech, esc, 1, 1970, month, year, "(OP) Operating"]


def ret(pid, gid, month, year, mw=100.0, summer=90.0, esc="BIT", name="Y"):
    return [1, "Owner", pid, name, "IN", gid, mw, summer, "Conventional Steam Coal", esc, 1, 1960, month, year]


def rec(key, kind, month, mw=100.0, name="P"):
    return {"sheet": kind.capitalize(), "kind": kind, "key": key, "plant_id": key.split("/")[0],
            "plant_name": name, "state": "XX", "status": "", "esc": "SUB", "ym": month, "mw": mw}


def plan_aug():
    """August records that match PUDL for all 16 plan generators."""
    return [rec(k, "operating", m, mw) for k, (mw, m) in cs.PLAN.items()]


class HelperTests(unittest.TestCase):
    def test_norm_and_ym(self):
        self.assertEqual(cs.norm_id(6090.0), "6090")
        self.assertEqual(cs.norm_id("17.0"), "17")
        self.assertEqual(cs.ym(2026, 12), "2026-12")
        self.assertEqual(cs.ym(None, 12), "")
        self.assertEqual(cs.ym(2026, 0), "")

    def test_to_float(self):
        self.assertEqual(cs.to_float("12.5"), 12.5)
        self.assertIsNone(cs.to_float(" "))
        self.assertIsNone(cs.to_float(None))
        self.assertIsNone(cs.to_float(float("nan")))

    def test_sheet_kind(self):
        self.assertEqual(cs.sheet_kind("Operating"), "operating")
        self.assertEqual(cs.sheet_kind("Operating_PR"), "operating")
        self.assertEqual(cs.sheet_kind("Retired"), "retired")
        self.assertIsNone(cs.sheet_kind("Planned"))
        self.assertIsNone(cs.sheet_kind("Canceled or Postponed"))

    def test_is_coal(self):
        self.assertTrue(cs.is_coal("SUB", "anything"))
        self.assertTrue(cs.is_coal(" bit ", None))
        self.assertFalse(cs.is_coal("NG", "Conventional Steam Coal"))
        self.assertTrue(cs.is_coal(None, "Conventional Steam Coal"))
        self.assertFalse(cs.is_coal("", "Natural Gas Steam Turbine"))

    def test_plan_constants(self):
        self.assertEqual(len(cs.PLAN), 16)
        self.assertAlmostEqual(sum(mw for mw, _ in cs.PLAN.values()), 6354.4, places=6)
        self.assertEqual(cs.PLAN["165/2"][1], "")
        self.assertEqual(len(cs.ORDER_PLANTS), 8)
        for k in cs.S2_STILL_2026:
            self.assertIn(k, cs.PLAN)


class CoalRowsTests(unittest.TestCase):
    def test_operating(self):
        rows = sheet(OP_HEADER, op(6090, 1, 12, 2026), op(6090.0, 3.0, 12, 2030, summer=None),
                     op(55, "GT1", 6, 2027, esc="NG", tech="Natural Gas Fired Combustion Turbine"),
                     op(470, "2", None, None, summer=0), ["Note: totals"], [None, None, None])
        found, info = cs.coal_rows("Operating", rows)
        self.assertEqual([r["key"] for r in found], ["6090/1", "6090/3", "470/2"])
        self.assertEqual(found[0]["ym"], "2026-12")
        self.assertEqual(found[0]["mw"], 90.0)
        self.assertEqual(found[1]["mw"], 100.0)
        self.assertEqual(found[2]["mw"], 100.0)
        self.assertEqual(found[2]["ym"], "")
        self.assertEqual(found[0]["kind"], "operating")
        self.assertEqual(found[0]["state"], "MN")
        self.assertEqual(found[0]["status"], "(OP) Operating")
        self.assertEqual(info["header_row"], 2)
        self.assertEqual(info["coal_rows"], 3)
        self.assertEqual(info["columns_missing"], [])

    def test_retired(self):
        found, info = cs.coal_rows("Retired", sheet(RET_HEADER, ret(1, "A", 10, 2025), ret(2, "B", 3, 2026)))
        self.assertEqual([(r["key"], r["ym"], r["kind"]) for r in found],
                         [("1/A", "2025-10", "retired"), ("2/B", "2026-03", "retired")])
        self.assertEqual(info["columns_missing"], ["status"])

    def test_other_sheets_skipped(self):
        self.assertEqual(cs.coal_rows("Planned", sheet(OP_HEADER, op(1, "1", 1, 2027))), ([], None))
        self.assertEqual(cs.coal_rows("Operating", [["no header"]]), ([], None))


class GateTests(unittest.TestCase):
    def test_held(self):
        g = cs.gate(plan_aug() + [rec("9/1", "retired", "2025-11")])
        self.assertTrue(g["held"])
        self.assertEqual(g["plan_match"], 16)

    def test_one_miss_still_held(self):
        aug = [r for r in plan_aug() if r["key"] != "6090/1"]
        g = cs.gate(aug)
        self.assertEqual(g["plan_match"], 15)
        self.assertTrue(g["held"])
        miss = [r for r in g["plan_rows"] if not r["match"]]
        self.assertEqual(miss[0]["august"], "(not on Operating sheet)")

    def test_two_misses_fail(self):
        aug = plan_aug()
        aug[0] = dict(aug[0], ym="2030-01")
        aug[1] = dict(aug[1], ym="2030-01")
        self.assertFalse(cs.gate(aug)["held"])

    def test_retired_2026_fails(self):
        self.assertFalse(cs.gate(plan_aug() + [rec("9/1", "retired", "2026-04")])["held"])

    def test_blank_matches_blank_only(self):
        aug = [r for r in plan_aug() if r["key"] != "165/2"] + [rec("165/2", "operating", "2026-06")]
        g = cs.gate(aug)
        self.assertEqual(g["plan_match"], 15)


def sep_base():
    """September records like the August record: four order plants and Sherco/Comanche in the window."""
    return [rec("1710/1", "operating", "2026-11", 1330.5), rec("6085/17", "operating", "2026-12", 722.0),
            rec("6021/1", "operating", "2026-12", 427.0), rec("1012/2", "operating", "2026-12", 90.0),
            rec("6090/1", "operating", "2026-12", 680.0), rec("470/2", "operating", "2026-12", 335.0),
            rec("3399/2", "operating", "2034-12", 1231.0), rec("165/2", "operating", "", 478.9),
            rec("9/1", "retired", "2025-11", 50.0)]


class PredictionTests(unittest.TestCase):
    def test_all_held(self):
        p = cs.predictions(sep_base())
        self.assertTrue(p["S1"]["held"])
        self.assertTrue(p["S2"]["held"])
        self.assertTrue(p["S3"]["held"])
        self.assertEqual(p["S3"]["mw"], 3584.5)
        self.assertEqual(p["S3"]["mw_under_orders"], 2569.5)
        self.assertEqual(p["S3"]["units"], 6)
        self.assertEqual(p["S3"]["share"], round(2569.5 / 3584.5, 4))

    def test_s1_fails_on_2026_retirement(self):
        p = cs.predictions(sep_base() + [rec("8/1", "retired", "2026-09", 20.0)])
        self.assertFalse(p["S1"]["held"])
        self.assertTrue(p["S2"]["held"])

    def test_s2_fails_when_comanche_moves(self):
        s = [r for r in sep_base() if r["key"] != "470/2"] + [rec("470/2", "operating", "2028-03", 335.0)]
        p = cs.predictions(s)
        self.assertFalse(p["S2"]["held"])
        self.assertEqual(p["S2"]["still"]["470/2"], "2028-03")

    def test_s2_fails_when_plan_unit_retired(self):
        p = cs.predictions(sep_base() + [rec("4041/7", "retired", "2025-12", 306.5)])
        self.assertFalse(p["S2"]["held"])
        self.assertEqual(p["S2"]["plan_retired"], ["4041/7"])

    def test_s3_range_and_share(self):
        small = [r for r in sep_base() if r["key"] not in ("1710/1",)]
        p = cs.predictions(small)
        self.assertFalse(p["S3"]["held"])
        self.assertEqual(p["S3"]["mw"], 2254.0)
        p = cs.predictions(sep_base() + [rec("77/1", "operating", "2026-10", 600.0)])
        self.assertEqual(p["S3"]["mw"], 4184.5)
        self.assertTrue(p["S3"]["held"])
        p = cs.predictions(sep_base() + [rec("77/1", "operating", "2026-10", 900.0)])
        self.assertEqual(p["S3"]["mw"], 4484.5)
        self.assertLess(p["S3"]["share"], 0.60)
        self.assertFalse(p["S3"]["held"])
        p = cs.predictions(sep_base() + [rec("564/1", "operating", "2026-11", 950.0)])
        self.assertEqual(p["S3"]["mw"], 4534.5)
        self.assertGreater(p["S3"]["share"], 0.60)
        self.assertFalse(p["S3"]["held"])

    def test_s3_empty(self):
        p = cs.predictions([rec("1/1", "operating", "2030-01")])
        self.assertEqual(p["S3"]["mw"], 0)
        self.assertIsNone(p["S3"]["share"])
        self.assertFalse(p["S3"]["held"])


class DescribeTests(unittest.TestCase):
    def test_ahead(self):
        s = sep_base() + [rec("1710/2", "operating", "2026-11", 10.0), rec("77/1", "operating", "2027-06", 200.0),
                          rec("78/1", "operating", "2028-01", 300.0)]
        rows = cs.ahead(s)
        self.assertEqual([a["plant_id"] for a in rows], ["1710", "6085", "6090", "6021", "470", "1012", "77"])
        self.assertEqual(rows[0]["units"], "1, 2")
        self.assertEqual(rows[0]["mw"], 1340.5)
        self.assertEqual(rows[0]["doe_order"], "yes")
        self.assertEqual(rows[2]["doe_order"], "no")

    def test_overdue(self):
        s = sep_base() + [rec("5/1", "operating", "2026-06"), rec("5/2", "retired", "2026-06")]
        self.assertEqual([r["key"] for r in cs.overdue(s)], ["5/1"])

    def test_changes(self):
        aug = [rec("1/1", "operating", "2026-09"), rec("2/1", "operating", "2026-12"), rec("3/1", "retired", "2024-05"),
               rec("4/1", "operating", "")]
        sep = [rec("1/1", "operating", "2026-12"), rec("2/1", "operating", "2026-12"), rec("4/1", "retired", "2026-09"),
               rec("5/1", "operating", "2027-01")]
        ch = cs.changes(aug, sep)
        self.assertEqual([(c["key"], c["august"], c["september"]) for c in ch],
                         [("1/1", "operating 2026-09", "operating 2026-12"),
                          ("4/1", "operating no date", "retired 2026-09"),
                          ("5/1", "absent", "operating 2027-01")])

    def test_state_retired_wins(self):
        st = cs.state_of([rec("1/1", "operating", "2026-09"), rec("1/1", "retired", "2026-09")])
        self.assertEqual(st["1/1"], "retired 2026-09")


class RenderTests(unittest.TestCase):
    def test_render(self):
        res = {"files": {}, "counts": {"september": 1234, "august": 1230},
               "sheets": {"september": {"Operating": {"header_row": 2, "rows": 10, "coal_rows": 3,
                                                      "columns_missing": []}, "Planned": None},
                          "august": {}}}
        f = {"url": "u", "size": 14013970, "md5": "m", "same_as_recorded": True}
        res["files"] = {"september": f, "august": f}
        res.update(cs.analyse(sep_base(), plan_aug()))
        md = cs.render(res)
        self.assertIn("- G1: **held**", md)
        self.assertIn("14,013,970 bytes", md)
        self.assertIn("| S1 | no coal row on the Retired sheet with retirement year 2026 | 0 rows | held |", md)
        self.assertIn("at least 60% of it at plants under DOE orders | 3,584.5 MW in 6 units; 2,569.5 MW", md)
        self.assertIn("retired: none; 6090/1: 2026-12; 470/2: 2026-12 | held |", md)
        self.assertIn("| P | XX | 6090 | 1 | 680.0 | 2026-12 | no |", md)
        self.assertIn("| 9/1 | P | XX | 2025-11 | 50.0 |", md)
        self.assertIn("- september / Planned: not read", md)
        self.assertNotIn("{", md)

    def test_render_gate_failed(self):
        res = {"counts": {"september": 1, "august": 1}, "sheets": {"september": {}, "august": {}}}
        f = {"url": "u", "size": 1, "md5": "m", "same_as_recorded": False}
        res["files"] = {"september": f, "august": f}
        res.update(cs.analyse(sep_base(), []))
        md = cs.render(res)
        self.assertIn("- G1: **FAILED**", md)
        self.assertIn("| not scored (G1 failed) |", md)


if __name__ == "__main__":
    unittest.main()
