"""Checks that every count stated in docs/easeyx3.md (result of pre-registration easeyx-3) is what
data/easeyx3-run.json and the two easeyx3 CSV files in data/ (the job's outputs, unchanged) say.
Reads no outside data.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import csv
import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def path(rel):
    return os.path.join(HERE, rel)


def fmt(n):
    return f"{n:,}"


def pct(a, b):
    return f"{100.0 * a / b:.2f}%"


def read_csv(rel):
    with open(path(rel), encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


class Easeyx3ResultTests(unittest.TestCase):
    # The job's JSON is kept as `res`: naming it `run` would hide unittest's TestCase.run.
    @classmethod
    def setUpClass(cls):
        with open(path("docs/easeyx3.md"), encoding="utf-8") as fh:
            cls.doc = fh.read()
        with open(path("data/easeyx3-run.json"), encoding="utf-8") as fh:
            cls.res = json.load(fh)
        cls.new = read_csv("data/easeyx3-new-keys.csv")
        cls.notsame = read_csv("data/easeyx3-ref-not-same-ids.csv")

    def test_run_and_scores(self):
        self.assertEqual(self.res["tool"], "easeyx3.py 0.1.0 (easeyx.py 0.1.0)")
        self.assertEqual((self.res["started"], self.res["finished"]),
                         ("2026-11-10T20:28:33Z", "2026-11-10T20:28:36Z"))
        self.assertIn("20:28:33-20:28:36 UTC", self.doc)
        self.assertEqual(self.res["scores"], {"G1": True, "G2": True, "G3": True, "P1": True,
                                              "P2": True, "P3": True, "P4": True, "P5": False})
        self.assertIn("**4 of the 5 predictions held (P1-P4); P5 failed.**", self.doc)

    def test_inputs(self):
        r = self.res["reference"]
        self.assertEqual((r["rows"], r["keys"], r["linked_keys"], r["multi_link_keys"]),
                         (7182, 7174, 6332, 6))
        self.assertEqual(r["missing_cols"], [])
        self.assertIn(r["md5"], self.doc)
        self.assertIn("e52a3a533f745b98b88f0556473fee0d4cbcf96d", r["url"])
        self.assertIn("7,182 rows, 7,174 keys, 6,332 of them linked (6 with more than one link)",
                      self.doc)
        s = self.res["side"]
        self.assertEqual((s["rows"], s["keys"], s["missing_cols"]), (7187, 7187, []))
        self.assertIn(s["md5"], self.doc)
        p = self.res["pudl"]
        self.assertEqual((p["rows"], p["pairs"], p["missing_cols"]), (667073, 43417, []))
        self.assertIn(p["md5"], self.doc)
        self.assertEqual(p["last_modified"], "Tue, 10 Nov 2026 08:52:08 GMT")
        self.assertIn("Last-Modified 10 Nov 2026 08:52:08 GMT, 667,073 rows, 43,417", self.doc)
        self.assertEqual(self.res["gate_measures"]["pudl_years"], [2001, 2026])
        self.assertIn("| 43,417 pairs; report years 2001-2026 | yes |", self.doc)
        self.assertIn("| 7,187 rows; no missing columns | yes |", self.doc)

    def test_predictions(self):
        m = self.res["measures"]
        c = m["carry_forward"]
        self.assertEqual((c["opr_linked"], c["opr_keys"]), (5431, 5882))
        self.assertIn(f"| 5,431 of 5,882 ({pct(5431, 5882)}) | yes |", self.doc)
        e = m["exact_in_ref"]
        self.assertEqual((e["same_ids"], e["linked_keys"], e["same_ids_loose"]), (6003, 6332, 6017))
        self.assertIn(f"| 6,003 of 6,332 ({pct(6003, 6332)}) | yes |", self.doc)
        self.assertIn(f"6,017 of 6,332 linked keys ({pct(6017, 6332)})", self.doc)
        x = m["exact_precision"]
        self.assertEqual((x["ref_links_to_it"], x["linked_keys_with_pair_in_pudl"]), (5926, 5973))
        self.assertIn(f"| 5,926 of 5,973 ({pct(5926, 5973)}) | yes |", self.doc)
        self.assertEqual(self.doc.count(pct(5926, 5973)), 3)
        self.assertEqual(self.doc.count(pct(5431, 5882)), 3)
        n = m["new_opr"]
        self.assertEqual((n["pair_in_pudl"], n["keys"]), (75, 122))
        self.assertIn(f"| 75 of 122 ({pct(75, 122)}) | yes |", self.doc)
        f = m["ref_first_seen_2025"]
        self.assertEqual((f["keys"], f["by_status"]), (8, {"OPR": 8}))
        self.assertIn("| at least 10 | 8 | no |", self.doc)

    def test_first_seen_2025(self):
        keys = self.res["reported"]["ref_first_seen_2025_keys"]
        self.assertEqual(keys, ["3406|JCT25|G25", "3406|JCT26|G26", "3406|JCT27|G27",
                                "3406|JCT28|G28", "64547|CT-1|1", "64547|CT-2|2",
                                "65372|CT-8|CTG-8", "66604|CT-7|CTG-7"])
        self.assertIn("Johnsonville (3406) units JCT25-JCT28, plant 64547 units CT-1 and CT-2, "
                      "65372 unit CT-8 and 66604 unit CT-7", self.doc)
        first25 = [r for r in self.new if r["first_year"] == "2025"]
        self.assertEqual(len(first25), 28)
        self.assertEqual(len(first25) + len(keys), 36)
        self.assertTrue(all(r["latest_class"] == "OPR" for r in first25))
        yes = [r for r in first25 if r["same_ids_in_pudl"] == "yes"]
        no = [r for r in first25 if r["same_ids_in_pudl"] != "yes"]
        self.assertEqual((len(yes), len(no)), (20, 8))
        self.assertTrue(all(r["pudl_last_status"] == "OP" for r in yes))
        self.assertEqual(sorted({r["plant_id"] for r in yes}),
                         sorted(["160", "3291", "3406", "55522", "6137", "6481", "66918"]))
        self.assertEqual(sorted(r["unit_id"] for r in yes if r["plant_id"] == "3406"),
                         ["JCT21", "JCT22", "JCT23", "JCT24", "JCT29", "JCT30"])
        self.assertEqual(sorted((r["plant_id"], r["generator_id"]) for r in no),
                         [("57881", "04"), ("57881", "05")] + [("68386", f"MPP-{i}") for i in range(1, 7)])
        self.assertEqual(len({r["plant_id"] for r in first25}), 9)
        self.assertIn("**28 OPR keys are first seen in 2025.** 20 have", self.doc)
        self.assertIn("are units at 9 plants; 20 of them", self.doc)

    def test_classes(self):
        b = self.res["measures"]["carry_forward"]["by_class"]
        self.assertEqual(b, {"LTCS|linked": 4, "LTCS|unlinked": 8, "OPR|linked": 5431,
                             "OPR|new": 122, "OPR|unlinked": 329, "RET|linked": 846,
                             "RET|new": 18, "RET|unlinked": 429})
        self.assertEqual(sum(b.values()), 7187)
        self.assertIn("| OPR | 5,431 | 329 | 122 |", self.doc)
        self.assertIn("| RET | 846 | 429 | 18 |", self.doc)
        self.assertIn("| LTCS | 4 | 8 | 0 |", self.doc)
        self.assertEqual(self.res["measures"]["ref_first_seen_2025"]["ref_keys_not_in_side"], 127)
        self.assertIn("127 reference keys are not on the EPA side at all", self.doc)
        u = self.res["reported"]["ref_unlinked_by_status"]
        self.assertEqual(u, {"LTCS": 19, "OPR": 258, "RET": 565})
        self.assertEqual(sum(u.values()), 7174 - 6332)
        self.assertIn("The 842 unlinked reference keys are 258 OPR, 565 RET and 19 LTCS", self.doc)

    def test_new_keys(self):
        self.assertEqual(len(self.new), 140)
        self.assertEqual(self.res["reported"]["new_by_class"], {"OPR": 122, "RET": 18})
        opr = [r for r in self.new if r["latest_class"] == "OPR"]
        self.assertEqual(len(opr), 122)
        in25 = [r for r in opr if r["latest_year"] == "2025"]
        self.assertEqual(len(in25), 94)
        self.assertEqual(sum(r["same_ids_in_pudl"] == "yes" for r in in25), 62)
        self.assertIn("**94 of the 122 OPR keys are in the 2025 file**, and 62 of those", self.doc)
        self.assertIn("The other 28 OPR keys were last seen before 2025", self.doc)
        with_pair = [r for r in opr if r["same_ids_in_pudl"] == "yes"]
        self.assertEqual(len(with_pair), 75)
        st = {}
        for r in with_pair:
            st[r["pudl_last_status"]] = st.get(r["pudl_last_status"], 0) + 1
        self.assertEqual(st, {"OP": 53, "OS": 3, "RE": 19})
        self.assertEqual(self.res["measures"]["new_opr"]["pudl_last_status"], st)
        self.assertIn("PUDL's latest status is OP for 53, OS for 3 and RE for 19", self.doc)
        self.assertEqual(122 - 75, 47)
        self.assertIn("122 operating keys the reference lacks (47 with no same-id pair in PUDL)",
                      self.doc)
        self.assertIn("lists all 140 (122 OPR, 18 RET)", self.doc)

    def test_not_same(self):
        self.assertEqual(len(self.notsame), 329)
        self.assertEqual(self.res["reported"]["not_same_by_status"], {"OPR": 307, "RET": 22})
        self.assertIn("lists them (307 OPR, 22 RET)", self.doc)
        self.assertEqual(sum(r["same_ids_in_pudl"] == "yes" for r in self.notsame), 47)
        self.assertEqual(self.res["reported"]["not_same_pair_in_pudl"], 47)
        self.assertEqual(5973 - 5926, 47)
        self.assertIn("47 of them have a same-id PUDL pair the reference did not choose", self.doc)
        t = self.res["reported"]["match_types_not_same_top20"]
        pre = "3_1_Generator (generators) match on plant and gen IDs  "
        self.assertEqual(t, {pre + "Step 1d: Modify IDs; remove leading letters": 161,
                             pre + "Step 1a: Exact match": 71, "Manual Match": 56,
                             pre + "Step 1b: Modify IDs; remove special chars": 27,
                             pre + "Step 1c: Modify IDs; convert to numeric": 14})
        self.assertEqual(sum(t.values()), 329)
        self.assertIn("Step 1d (remove leading letters) 161, Step 1a (exact match) 71, Manual Match "
                      "56, Step 1b (remove special characters) 27, Step 1c (convert to numeric) 14",
                      self.doc)
        a = self.res["reported"]["match_types_linked_top20"]
        self.assertEqual(sorted(a.values(), reverse=True), [6064, 161, 64, 29, 14])
        self.assertEqual(sum(a.values()), 6332)
        self.assertIn("Step 1a 6,064, Step 1d 161, Manual Match 64, Step 1b 29 and Step 1c 14",
                      self.doc)

    def test_exact_match_other_plant(self):
        rows = [r for r in self.notsame if "Step 1a" in r["match_types"]]
        self.assertEqual(len(rows), 71)
        for r in rows:
            links = r["eia_links"].split("|")
            self.assertEqual(len(links), 1, r)
            plant, gen = links[0].split(":", 1)
            self.assertNotEqual(plant, r["plant_id"], r)
            self.assertEqual(gen.strip().upper(), r["generator_id"].strip().upper(), r)
        self.assertEqual(len({r["plant_id"] for r in rows}), 18)
        pairs = {(r["plant_id"], r["eia_links"].split(":")[0]) for r in rows}
        for p in (("10619", "7784"), ("1416", "56565"), ("7765", "7709")):
            self.assertIn(p, pairs)
        self.assertIn("all 71 \"Step 1a: Exact match\" keys that fail our same-ids rule keep the "
                      "generator id but link to a different EIA plant id**, at 18 CAMD plants", self.doc)

    def test_disclosure(self):
        for text in ("made with AI agents working in MV2's name",
                     "no person has checked these results by hand",
                     "[plan](easeyx3-plan.md)", "camd-eia-crosswalk-latest/issues/7",
                     "pudl/issues/5705", "Text and data CC BY 4.0; code Apache-2.0.",
                     "(not pre-registered)", "14:21:58 UTC on 10 November 2026"):
            self.assertIn(text, self.doc)


if __name__ == "__main__":
    unittest.main()
