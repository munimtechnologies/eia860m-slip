"""Tests for checks.py 0.2.0 (standard library only). Apache-2.0."""

import copy
import unittest

import checks as k

PROFILE = {"report_max": "2026-08"}
SLIP = {"overall": [{"on_time": 0.3249, "not_online_12": 0.1913}],
        "annual": [{"year": y, "group": "all", "planned_mw": v} for y, v in k.REF_PLAN.items()]}
RETIRE = {"detection": {"operating_exits_without_retired_record": 377}}
MW = {"CTG1": 347.0, "CTG2": 347.0, "STG1": 476.9, "1GTA": 310.3, "1GTB": 310.3, "2GTA": 310.3,
      "2GTB": 310.3, "CC1ST": 364.7, "CC2ST": 364.7}
LINKS = ([{"year": 2018, "plan_key": "%s/%s" % (a, g), "entry_key": "%s/%s" % (b, g),
           "plan_mw": MW[g]} for a, b, g in k.L1_LINKS]
         + [{"year": y, "plan_key": p, "entry_key": e, "plan_mw": mw}
            for y, p, e, mw in k.L2_LINKS])
LINKED = {2018: 3141.5, 2019: 10.0, 2022: 145.0}


def flows_doc():
    by_group = []
    for y in k.YEARS:
        rk = LINKED.get(y, 0.0)
        by_group.append({"year": y, "group": "all", "planned_mw": k.REF_PLAN[y],
                         "built_mw": k.REF_BUILT[y],
                         "not_listed": round(k.REF_NOT_LISTED[y] - rk, 1), "rekeyed_online": rk,
                         "new_entry": round(k.REF_NEW_ENTRY[y] - rk, 1), "rekeyed": rk,
                         "plan_identity_ok": True, "built_identity_ok": True})
        by_group.append({"year": y, "group": "solar", "planned_mw": 1.0,
                         "plan_identity_ok": True, "built_identity_ok": True})
    return {"years": list(k.YEARS), "by_group": by_group,
            "by_band": [{"plan_identity_ok": True}],
            "pooled": [{"plan_identity_ok": True, "built_identity_ok": True}],
            "links": copy.deepcopy(LINKS)}


def run(profile=PROFILE, slip=SLIP, retire=RETIRE, flows=None):
    return k.evaluate(profile, slip, retire, flows or flows_doc())


class CheckTests(unittest.TestCase):
    def test_all_pass(self):
        r = run()
        for name in ("K2", "K3", "K4", "L1", "L2", "L3"):
            self.assertTrue(r[name]["pass"], name)
        self.assertTrue(r["all_pass"])
        self.assertEqual(r["K3"]["max_planned_mw_diff"], 0.0)
        self.assertEqual((r["L1"]["links_2018"], r["L1"]["mw_2018"]), (9, 3141.5))
        self.assertEqual(r["L2"]["extra_links"], [])

    def test_k2_k3_k4_can_fail(self):
        self.assertFalse(run(retire={"detection": {
            "operating_exits_without_retired_record": 379}})["K2"]["pass"])
        self.assertFalse(run(profile={"report_max": "2026-09"})["K2"]["pass"])
        slip = copy.deepcopy(SLIP)
        slip["overall"][0]["on_time"] = 0.3260
        self.assertFalse(run(slip=slip)["K3"]["pass"])
        slip = copy.deepcopy(SLIP)
        slip["annual"][4]["planned_mw"] += 0.3
        r = run(slip=slip)
        self.assertFalse(r["K3"]["pass"])
        self.assertEqual(r["K3"]["max_planned_mw_diff"], 0.3)
        flows = flows_doc()
        flows["by_group"][2]["planned_mw"] += 0.2   # 2017 on the flows side
        self.assertFalse(run(flows=flows)["K3"]["pass"])
        flows = flows_doc()
        flows["by_band"][0]["plan_identity_ok"] = False
        self.assertFalse(run(flows=flows)["K4"]["pass"])
        flows = flows_doc()
        flows["years"] = list(range(2017, 2026))
        r = run(flows=flows)
        self.assertFalse(r["K4"]["pass"])
        self.assertFalse(r["all_pass"])

    def test_l1_can_fail(self):
        flows = flows_doc()
        flows["links"] = [x for x in flows["links"] if x["plan_key"] != "60138/2GTB"]
        self.assertFalse(run(flows=flows)["L1"]["pass"])
        # A crosswise pair inside Citrus County: right plants, different generator ids.
        flows = flows_doc()
        for x in flows["links"]:
            if x["plan_key"] == "60138/CC2ST":
                x["entry_key"] = "628/CC1ST"
        self.assertFalse(run(flows=flows)["L1"]["pass"])

    def test_l2_missing_fails_and_extra_is_reported(self):
        flows = flows_doc()
        flows["links"] = [x for x in flows["links"] if x["year"] != 2022]
        r = run(flows=flows)
        self.assertFalse(r["L2"]["pass"])
        self.assertEqual(r["L2"]["missing"], [[2022, "64845/AREXP", "56336/AREXP", 145.0]])
        flows = flows_doc()
        flows["links"].append({"year": 2024, "plan_key": "1/A", "entry_key": "2/A",
                               "plan_mw": 20.0})
        r = run(flows=flows)
        self.assertTrue(r["L2"]["pass"])
        self.assertEqual([x["plan_key"] for x in r["L2"]["extra_links"]], ["1/A"])

    def test_l3_can_fail(self):
        flows = flows_doc()
        flows["by_group"][4]["new_entry"] += 1.0    # 2018
        r = run(flows=flows)
        self.assertFalse(r["L3"]["pass"])
        self.assertEqual(r["L3"]["years_off"], [{"year": 2018, "off_by": {"new_entry": 1.0}}])
        flows = flows_doc()
        flows["by_group"] = [x for x in flows["by_group"] if x["year"] != 2025]
        self.assertFalse(run(flows=flows)["L3"]["pass"])


if __name__ == "__main__":
    unittest.main()
