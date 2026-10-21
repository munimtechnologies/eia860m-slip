"""Unit tests for erdetail.py on hand-built rows. MV2 of Munim, Inc. (made with AI agents).
Apache-2.0. Needs erplan.py (commit b73dc6a) next to it."""

import unittest

import erdetail as ed


def row(year, set_name, key, mw, bucket, er, span=None):
    spans = {"m02": "early", "m03": "early", "m04": "mid", "m05": "mid", "m06": "mid",
             "m07": "late", "m08": "late"}
    return {"year": year, "set": set_name, "key": key, "group": "solar", "mw": mw,
            "bucket": bucket, "span": span or spans.get(bucket, "edge"), "er": er,
            "final": "plan_y"}


class F3Tests(unittest.TestCase):
    def test_counts(self):
        final = {"1/A": "operable", "1/B": "operable", "2/A": "operable", "3/A": "operable",
                 "4/A": "plan_y"}
        er = {"1/A": "operable", "2/A": "retired", "4/A": "plan_y"}
        d = ed.f3_detail(er, final)
        self.assertEqual((d["final_operable"], d["found"], d["missing"]), (4, 2, 2))
        self.assertEqual(d["share"], 0.5)
        self.assertEqual(d["missing_sample"], ["1/B", "3/A"])

    def test_no_operable(self):
        d = ed.f3_detail({}, {"1/A": "plan_y"})
        self.assertIsNone(d["share"])
        self.assertEqual(d["final_operable"], 0)

    def test_class_counts(self):
        c = ed.class_counts({"1/A": "plan_y", "1/B": "plan_y", "2/A": "retired"})
        self.assertEqual(c, {"plan_y": 2, "proposed_other": 0, "operable": 0, "retired": 1})


class MonthTests(unittest.TestCase):
    def test_month_of(self):
        self.assertEqual(ed.month_of("m05"), "m05")
        self.assertEqual(ed.month_of("m11"), ed.LATER)
        self.assertEqual(ed.month_of("after"), ed.LATER)

    def test_by_month(self):
        rows = [row(2022, "A", "1/A", 30.0, "m02", "plan_y"),
                row(2022, "A", "1/B", 10.0, "m02", "absent"),
                row(2022, "A", "2/A", 20.0, "m07", "proposed_other"),
                row(2022, "A", "3/A", 5.0, "m10", "absent"),
                row(2023, "A", "4/A", 99.0, "m02", "absent"),
                row(2022, "B", "5/A", 7.0, "m02", "plan_y")]
        got = ed.by_month(rows, (2022,), "A")
        self.assertEqual(sorted(got), ["later", "m02", "m07"])
        self.assertEqual(got["m02"], {"mw": 40.0, "er_plan_share": 0.75, "er_any_share": 0.75})
        self.assertEqual(got["m07"], {"mw": 20.0, "er_plan_share": 0.0, "er_any_share": 1.0})
        self.assertEqual(got["later"], {"mw": 5.0, "er_plan_share": 0.0, "er_any_share": 0.0})
        pooled = ed.by_month(rows, (2022, 2023), "A")
        self.assertEqual(pooled["m02"]["mw"], 139.0)

    def test_rows_without_class_skipped(self):
        r = row(2022, "A", "1/A", 30.0, "m02", "plan_y")
        del r["er"]
        self.assertEqual(ed.by_month([r], (2022,), "A"), {})


class PlantTests(unittest.TestCase):
    def test_plant_of(self):
        self.assertEqual(ed.plant_of("65763/WYOUN"), "65763")

    def test_presence(self):
        rows = [row(2022, "A", "10/A", 40.0, "m07", "absent"),
                row(2022, "A", "11/A", 60.0, "m08", "absent"),
                row(2022, "A", "10/B", 5.0, "m02", "plan_y"),
                row(2023, "A", "11/B", 25.0, "m04", "absent"),
                row(2022, "B", "10/C", 9.0, "m07", "absent")]
        er_plants = {2022: {"10", "12"}, 2023: {"11"}}
        got = ed.plant_presence(rows, er_plants, (2022, 2023))
        self.assertEqual(got["late"], {"absent_mw": 100.0, "plant_in_er_mw": 40.0,
                                       "plant_in_er_share": 0.4, "generators": 2})
        self.assertEqual(got["mid"], {"absent_mw": 25.0, "plant_in_er_mw": 25.0,
                                      "plant_in_er_share": 1.0, "generators": 1})
        self.assertEqual(got["all"]["absent_mw"], 125.0)
        self.assertEqual(got["all"]["plant_in_er_mw"], 65.0)
        self.assertNotIn("early", got)
        self.assertNotIn("edge", got)


class RenderTests(unittest.TestCase):
    def test_render(self):
        res = {"years": [2022],
               "f3": {"2022": {"final_operable": 4, "found": 3, "missing": 1, "share": 0.75,
                               "missing_sample": ["1/B"]}},
               "counts": {"2022": {"er": {"plan_y": 1, "proposed_other": 0, "operable": 3,
                                          "retired": 0},
                                   "final": {"plan_y": 2, "proposed_other": 0, "operable": 4,
                                             "retired": 0}}},
               "months": {"A": {"pooled": {"m02": {"mw": 40.0, "er_plan_share": 0.75,
                                                   "er_any_share": 0.75}}},
                          "A_built": {"pooled": {}}},
               "plants": {"all": {"absent_mw": 10.0, "plant_in_er_mw": 0.0,
                                  "plant_in_er_share": 0.0, "generators": 1}}}
        md = ed.render(res)
        self.assertIn("| 2022 | 4 | 3 | 1 | 0.75 |", md)
        self.assertIn("| 2022 | final | 2 | 0 | 4 | 0 |", md)
        self.assertIn("| pooled | m02 | 40.0 | 0.75 | 0.75 |", md)
        self.assertIn("| all | 1 | 10.0 | 0.0 | 0.0 |", md)
        self.assertIn("- 2022: 1/B", md)


if __name__ == "__main__":
    unittest.main()
