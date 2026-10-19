"""Tests for checks.py (standard library only). Apache-2.0."""

import copy
import unittest

import checks as k

PROFILE = {"report_max": "2026-08"}
SLIP = {"overall": [{"on_time": 0.327, "not_online_12": 0.186}],
        "annual": [{"year": y, "group": "all", "planned_mw": v * 1.005}
                   for y, v in k.REF_PLANNED_ALL.items()]}
RETIRE = {"detection": {"operating_exits_without_retired_record": 379}}
FLOWS = {"years": list(range(2016, 2026)),
         "by_group": [{"plan_identity_ok": True, "built_identity_ok": True}],
         "by_band": [{"plan_identity_ok": True}],
         "pooled": [{"plan_identity_ok": True, "built_identity_ok": True}]}


class CheckTests(unittest.TestCase):
    def test_all_pass(self):
        r = k.evaluate(PROFILE, SLIP, RETIRE, FLOWS)
        self.assertTrue(r["K2"]["pass"] and r["K3"]["pass"] and r["K4"]["pass"])
        self.assertTrue(r["all_pass"])
        self.assertEqual(r["K3"]["max_planned_mw_change"], 0.005)

    def test_each_check_can_fail(self):
        retire = {"detection": {"operating_exits_without_retired_record": 28705}}
        self.assertFalse(k.evaluate(PROFILE, SLIP, retire, FLOWS)["K2"]["pass"])
        self.assertFalse(k.evaluate({"report_max": "2026-09"}, SLIP, RETIRE, FLOWS)["K2"]["pass"])
        slip = copy.deepcopy(SLIP)
        slip["overall"][0]["on_time"] = 0.335
        self.assertFalse(k.evaluate(PROFILE, slip, RETIRE, FLOWS)["K3"]["pass"])
        slip = copy.deepcopy(SLIP)
        slip["annual"][3]["planned_mw"] *= 1.02
        self.assertFalse(k.evaluate(PROFILE, slip, RETIRE, FLOWS)["K3"]["pass"])
        flows = copy.deepcopy(FLOWS)
        flows["by_band"][0]["plan_identity_ok"] = False
        r = k.evaluate(PROFILE, SLIP, RETIRE, flows)
        self.assertFalse(r["K4"]["pass"])
        self.assertFalse(r["all_pass"])


if __name__ == "__main__":
    unittest.main()
