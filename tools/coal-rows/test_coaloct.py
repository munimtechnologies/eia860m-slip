"""Unit tests for coaloct.py on hand-built sheets (no network).

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import unittest

import coaloct as co

OP_HEADER = ["Entity ID", "Entity Name", "Plant ID", "Plant Name", "Plant State", "Generator ID",
             "Nameplate Capacity (MW)", "Net Summer Capacity (MW)", "Technology", "Energy Source Code",
             "Operating Month", "Operating Year", "Planned Retirement Month", "Planned Retirement Year", "Status"]
RET_HEADER = ["Entity ID", "Entity Name", "Plant ID", "Plant Name", "Plant State", "Generator ID",
              "Nameplate Capacity (MW)", "Net Summer Capacity (MW)", "Technology", "Energy Source Code",
              "Operating Month", "Operating Year", "Retirement Month", "Retirement Year"]

# Per-unit MW of the 9 units job coalsep-v1 found dated 2026-10 to 2026-12 (PLAN's MW; they add to 3,584.5).
SEP_MW = {"1710/1": 260.0, "1710/2": 279.8, "1710/3": 790.7, "6085/17": 361.0, "6085/18": 361.0,
          "6090/1": 680.0, "6021/1": 427.0, "470/2": 335.0, "1012/2": 90.0}


def sheet(header, *data):
    return [["U.S. Energy Information Administration"], [None], header] + [list(r) for r in data]


def op(pid, gid, month, year, mw=100.0, summer=90.0, esc="SUB", tech="Conventional Steam Coal", name="X"):
    return [1, "Owner", pid, name, "MN", gid, mw, summer, tech, esc, 1, 1970, month, year, "(OP) Operating"]


def ret(pid, gid, month, year, mw=100.0, summer=90.0, esc="BIT", name="Y"):
    return [1, "Owner", pid, name, "IN", gid, mw, summer, "Conventional Steam Coal", esc, 1, 1960, month, year]


def rec(key, kind, month, mw=100.0, name="P"):
    return {"sheet": kind.capitalize(), "kind": kind, "key": key, "plant_id": key.split("/")[0],
            "plant_name": name, "state": "XX", "status": "", "esc": "SUB", "ym": month, "mw": mw}


def sep_base():
    """September records as job coalsep-v1 found them: the 9 units dated 2026-10..12, others later or retired."""
    out = [rec(k, "operating", m, SEP_MW[k]) for k, m in co.G2_UNITS.items()]
    return out + [rec("3399/2", "operating", "2034-12", 1231.0), rec("165/2", "operating", "", 478.9),
                  rec("889/1", "operating", "2027-12", 578.5), rec("9/1", "retired", "2025-11", 50.0),
                  rec("8/1", "retired", "2025-02", 40.0), rec("7/1", "retired", "2019-06", 30.0)]


def oct_base():
    """October records with nothing changed from September."""
    return sep_base()


class HelperTests(unittest.TestCase):
    def test_norm_and_ym(self):
        self.assertEqual(co.norm_id(6090.0), "6090")
        self.assertEqual(co.norm_id("17.0"), "17")
        self.assertEqual(co.ym(2026, 12), "2026-12")
        self.assertEqual(co.ym(None, 12), "")
        self.assertEqual(co.ym(2026, 13), "")

    def test_to_float(self):
        self.assertEqual(co.to_float("12.5"), 12.5)
        self.assertIsNone(co.to_float(" "))
        self.assertIsNone(co.to_float(float("nan")))

    def test_sheet_kind_and_coal(self):
        self.assertEqual(co.sheet_kind("Operating_PR"), "operating")
        self.assertEqual(co.sheet_kind("Retired"), "retired")
        self.assertIsNone(co.sheet_kind("Planned"))
        self.assertTrue(co.is_coal("SUB", "anything"))
        self.assertFalse(co.is_coal("NG", "Conventional Steam Coal"))
        self.assertTrue(co.is_coal(None, "Conventional Steam Coal"))

    def test_constants(self):
        self.assertEqual(co.__version__, "0.2.0")
        self.assertEqual(co.OCT, ("october_generator2026.xlsx", None, None))
        self.assertEqual(co.SEPT[1:], ("4c741eb77a5ccad5aca32ffe43f398af", 14013970))
        self.assertEqual(len(co.PLAN), 16)
        self.assertAlmostEqual(sum(mw for mw, _ in co.PLAN.values()), 6354.4, places=6)
        self.assertEqual(len(co.G2_UNITS), 9)
        self.assertEqual(round(sum(SEP_MW.values()), 1), co.G2_MW)
        for k in co.G2_UNITS:
            self.assertEqual(co.PLAN[k][0], SEP_MW[k])
        self.assertEqual(sorted(k for k, m in co.G2_UNITS.items() if m == "2026-11"), list(co.CAMPBELL))
        for k in co.O3_STILL_2026:
            self.assertIn(k, co.PLAN)
        self.assertEqual(co.O2_BEFORE, "2026-11")
        self.assertEqual(co.AHEAD, ("2026-11", "2027-12"))


class CoalRowsTests(unittest.TestCase):
    def test_operating(self):
        rows = sheet(OP_HEADER, op(6090, 1, 12, 2026), op(6090.0, 3.0, 12, 2030, summer=None),
                     op(55, "GT1", 6, 2027, esc="NG", tech="Natural Gas Fired Combustion Turbine"),
                     op(470, "2", None, None, summer=0), ["Note: totals"])
        found, info = co.coal_rows("Operating", rows)
        self.assertEqual([r["key"] for r in found], ["6090/1", "6090/3", "470/2"])
        self.assertEqual([r["mw"] for r in found], [90.0, 100.0, 100.0])
        self.assertEqual([r["ym"] for r in found], ["2026-12", "2030-12", ""])
        self.assertEqual(info["coal_rows"], 3)
        self.assertEqual(info["columns_missing"], [])

    def test_retired(self):
        found, info = co.coal_rows("Retired", sheet(RET_HEADER, ret(1, "A", 10, 2026)))
        self.assertEqual([(r["key"], r["ym"], r["kind"]) for r in found], [("1/A", "2026-10", "retired")])
        self.assertEqual(info["columns_missing"], ["status"])


class GateTests(unittest.TestCase):
    def test_held(self):
        g = co.gate(sep_base())
        self.assertTrue(g["held"])
        self.assertEqual((g["units"], g["mw"]), (9, 3584.5))
        self.assertEqual(len(g["unit_rows"]), 9)

    def test_month_moved_fails(self):
        s = [r for r in sep_base() if r["key"] != "6090/1"] + [rec("6090/1", "operating", "2026-11", 680.0)]
        g = co.gate(s)
        self.assertFalse(g["held"])
        self.assertTrue(g["mw_match"])
        miss = [r for r in g["unit_rows"] if not r["match"]]
        self.assertEqual([(r["key"], r["recorded"], r["september"]) for r in miss], [("6090/1", "2026-12", "2026-11")])

    def test_missing_and_extra_unit_fail(self):
        s = [r for r in sep_base() if r["key"] != "1012/2"]
        g = co.gate(s)
        self.assertFalse(g["held"])
        self.assertEqual(g["mw"], 3494.5)
        g = co.gate(sep_base() + [rec("77/1", "operating", "2026-10", 50.0)])
        self.assertFalse(g["held"])
        self.assertIn({"key": "77/1", "recorded": "(not recorded)", "september": "2026-10", "match": False},
                      g["unit_rows"])

    def test_mw_changed_fails(self):
        s = [r for r in sep_base() if r["key"] != "470/2"] + [rec("470/2", "operating", "2026-12", 325.0)]
        g = co.gate(s)
        self.assertTrue(g["units_match"])
        self.assertEqual(g["mw"], 3574.5)
        self.assertFalse(g["held"])

    def test_retired_2026_fails(self):
        g = co.gate(sep_base() + [rec("8/2", "retired", "2026-05", 20.0)])
        self.assertTrue(g["units_match"])
        self.assertFalse(g["held"])


class PredictionTests(unittest.TestCase):
    def test_all_held(self):
        p = co.predictions(oct_base())
        self.assertEqual([p[k]["held"] for k in ("O1", "O2", "O3")], [True, True, True])
        self.assertEqual(p["O3"]["still"], {"6090/1": "2026-12", "470/2": "2026-12"})

    def test_o1_and_o3_fail_on_plan_unit_retired_2026(self):
        o = [r for r in oct_base() if r["key"] != "6085/17"] + [rec("6085/17", "retired", "2026-10", 361.0)]
        p = co.predictions(o)
        self.assertFalse(p["O1"]["held"])
        self.assertEqual([r["key"] for r in p["O1"]["retired_2026"]], ["6085/17"])
        self.assertTrue(p["O2"]["held"])
        self.assertFalse(p["O3"]["held"])
        self.assertEqual(p["O3"]["plan_retired"], ["6085/17"])

    def test_o1_fails_alone_for_other_unit(self):
        p = co.predictions(oct_base() + [rec("55/1", "retired", "2026-07", 25.0)])
        self.assertEqual([p[k]["held"] for k in ("O1", "O2", "O3")], [False, True, True])

    def test_o2_overdue(self):
        o = [r for r in oct_base() if r["key"] != "1012/2"] + [rec("1012/2", "operating", "2026-10", 90.0)]
        p = co.predictions(o)
        self.assertFalse(p["O2"]["held"])
        self.assertEqual([r["key"] for r in p["O2"]["overdue"]], ["1012/2"])
        p = co.predictions(oct_base() + [rec("56/1", "operating", "2025-06", 10.0)])
        self.assertFalse(p["O2"]["held"])
        p = co.predictions(oct_base() + [rec("56/1", "retired", "2025-06", 10.0)])
        self.assertTrue(p["O2"]["held"])

    def test_o3_fails_when_comanche_moves_or_vanishes(self):
        o = [r for r in oct_base() if r["key"] != "470/2"] + [rec("470/2", "operating", "2028-03", 335.0)]
        p = co.predictions(o)
        self.assertFalse(p["O3"]["held"])
        self.assertEqual(p["O3"]["still"]["470/2"], "2028-03")
        p = co.predictions([r for r in oct_base() if r["key"] != "6090/1"])
        self.assertFalse(p["O3"]["held"])
        self.assertEqual(p["O3"]["still"]["6090/1"], "(not on Operating sheet)")

    def test_o3_plan_unit_retired_earlier_year(self):
        p = co.predictions(oct_base() + [rec("4041/7", "retired", "2025-12", 306.5)])
        self.assertTrue(p["O1"]["held"])
        self.assertFalse(p["O3"]["held"])


class DescribeTests(unittest.TestCase):
    def test_campbell(self):
        self.assertEqual(co.campbell(oct_base()), {"1710/1": "operating 2026-11", "1710/2": "operating 2026-11",
                                                   "1710/3": "operating 2026-11"})
        o = [r for r in oct_base() if r["key"] != "1710/3"] + [rec("1710/3", "operating", "2027-05", 790.7)]
        self.assertEqual(co.campbell(o)["1710/3"], "operating 2027-05")
        self.assertEqual(co.campbell([])["1710/1"], "absent")

    def test_ahead(self):
        rows = co.ahead(oct_base())
        self.assertEqual([a["plant_id"] for a in rows], ["1710", "6085", "6090", "6021", "470", "1012", "889"])
        self.assertEqual(rows[0]["units"], "1, 2, 3")
        self.assertEqual(rows[0]["mw"], 1330.5)
        self.assertEqual((rows[0]["doe_order"], rows[2]["doe_order"]), ("yes", "no"))
        self.assertEqual(round(sum(a["mw"] for a in rows), 1), 4163.0)

    def test_ahead_starts_in_november(self):
        rows = co.ahead(oct_base() + [rec("77/1", "operating", "2026-10", 50.0)])
        self.assertNotIn("77", [a["plant_id"] for a in rows])

    def test_changes(self):
        sep = [rec("1/1", "operating", "2026-12"), rec("2/1", "operating", "2026-12"), rec("3/1", "retired", "2024-05"),
               rec("4/1", "operating", "")]
        octo = [rec("1/1", "operating", "2027-03"), rec("2/1", "operating", "2026-12"),
                rec("4/1", "retired", "2026-10"), rec("5/1", "operating", "2027-01")]
        ch = co.changes(sep, octo)
        self.assertEqual([(c["key"], c["september"], c["october"]) for c in ch],
                         [("1/1", "operating 2026-12", "operating 2027-03"),
                          ("4/1", "operating no date", "retired 2026-10"),
                          ("5/1", "absent", "operating 2027-01")])

    def test_recent(self):
        self.assertEqual([r["key"] for r in co.recent(oct_base())], ["8/1", "9/1"])


class RenderTests(unittest.TestCase):
    def res(self, octo, sep, same=True):
        f_oct = {"url": "u", "size": 14100000, "md5": "m", "same_as_recorded": None}
        f_sep = {"url": "u", "size": 14013970, "md5": "m", "same_as_recorded": same}
        res = {"files": {"october": f_oct, "september": f_sep}, "counts": {"october": 1357, "september": 1356},
               "sheets": {"october": {"Operating": {"header_row": 2, "rows": 10, "coal_rows": 3,
                                                    "columns_missing": []}, "Planned": None},
                          "september": {}}}
        res.update(co.analyse(octo, sep))
        return res

    def test_render(self):
        md = co.render(self.res(oct_base(), sep_base()))
        self.assertIn("(coaloct 0.2.0)", md)
        self.assertIn("14,013,970 bytes", md)
        self.assertIn("(same as recorded earlier: not recorded in advance)", md)
        self.assertIn("Coal rows read: October 1,357, September 1,356.", md)
        self.assertIn("9 units, 3,584.5 MW (recorded: 9 units, 3,584.5 MW)", md)
        self.assertIn("- G2: **held**", md)
        self.assertIn("| 6090/1 | 2026-12 | 2026-12 | yes |", md)
        self.assertIn("| O1 | no coal row on the Retired sheet has retirement year 2026 | 0 rows | held |", md)
        self.assertIn("| O2 | no coal unit on the Operating sheet is dated before 2026-11 | 0 units | held |", md)
        self.assertIn("retired: none; 6090/1: 2026-12; 470/2: 2026-12 | held |", md)
        self.assertIn("| 1710/3 | operating 2026-11 |", md)
        self.assertIn("| P | XX | 889 | 1 | 578.5 | 2027-12 | no |", md)
        self.assertIn("7 plants, 4,163.0 MW; 2,569.5 MW at plants under DOE orders.", md)
        self.assertIn("| 9/1 | P | XX | 2025-11 | 50.0 |", md)
        self.assertIn("October: 2 rows; September: 2 rows.", md)
        self.assertIn("- october / Planned: not read", md)
        self.assertEqual(md.count("| none |"), 2)
        self.assertIn("| none | | | | | |", md)
        self.assertNotIn("{", md)

    def test_render_failed_bars(self):
        o = [r for r in oct_base() if r["key"] != "6085/17"] + [rec("6085/17", "retired", "2026-10", 361.0)]
        md = co.render(self.res(o, sep_base()))
        self.assertIn("| O1 | no coal row on the Retired sheet has retirement year 2026 | 1 rows | failed |", md)
        self.assertIn("| 6085/17 | P | XX | 2026-10 | 361.0 |", md)
        self.assertIn("| 6085/17 | P | XX | 361.0 | operating 2026-12 | retired 2026-10 |", md)
        self.assertIn("retired: 6085/17; 6090/1: 2026-12; 470/2: 2026-12 | failed |", md)

    def test_render_gate_failed(self):
        md = co.render(self.res(oct_base(), [], same=False))
        self.assertIn("- G2: **FAILED**", md)
        self.assertIn("| not scored (G2 failed) |", md)
        self.assertIn("(same as recorded earlier: False)", md)


if __name__ == "__main__":
    unittest.main()
