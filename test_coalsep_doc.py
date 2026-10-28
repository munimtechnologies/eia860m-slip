"""Doc test: docs/coalsep.md (the plan in docs/coalsep-plan.md scored on EIA's September 2026 workbook) and the
2026-10-28 update to docs/coal-rows.md say what job coalsep-v1 found (docs/coalsep-2026-09.md,
data/coalsep_2026-09.json), and coal-rows.md's earlier text is kept.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))

UPDATE = "## Update, 2026-10-28: September 2026, still no coal retirement"
# EIA plant ID -> plant name in coal-rows.md's table of 2025 coal retirements
NAMES_2025 = {"594": "Indian River", "113": "Cholla", "2367": "Schiller", "6481": "Intermountain Power Project",
              "1073": "Prairie Creek"}
WORDS = {6: "six", 10: "ten"}


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8") as fh:
        return fh.read()


def mw(x):
    return "{:,.1f}".format(x)


class CoalsepDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = read("docs", "coalsep.md")
        cls.plan = read("docs", "coalsep-plan.md")
        cls.out = read("docs", "coalsep-2026-09.md")
        cls.res = json.loads(read("data", "coalsep_2026-09.json"))
        cls.units = read("docs", "coalsep-v1-unittests.txt")
        cls.md5 = read("docs", "coalsep-v1-md5.txt")
        cls.rows = read("docs", "coal-rows.md")
        cls.old, cls.new = cls.rows.split(UPDATE)

    def test_job_result(self):
        r = self.res
        self.assertEqual(r["version"], "0.1.0")
        self.assertTrue(r["gate"]["held"])
        self.assertEqual((r["gate"]["plan_match"], r["gate"]["need"]), (16, 15))
        self.assertEqual(r["gate"]["retired_2026"], [])
        for k in ("S1", "S2", "S3"):
            self.assertTrue(r["predictions"][k]["held"], k)
        self.assertIn("- G1: **held**", self.out)
        self.assertIn("| S1 | no coal row on the Retired sheet with retirement year 2026 | 0 rows | held |", self.out)
        for f in r["files"].values():
            self.assertTrue(f["same_as_recorded"])
            self.assertEqual(f["errors"], [])
            self.assertIn("(%s bytes, md5 %s)" % ("{:,}".format(f["size"]), f["md5"]), self.page)
            self.assertIn("%s bytes, md5 %s" % ("{:,}".format(f["size"]), f["md5"]), self.plan)

    def test_status_and_table(self):
        p = self.res["predictions"]
        self.assertIn("Status: scored against its pre-registration. The gate held and 3 of 3 predictions held.",
                      self.page)
        self.assertIn("Status: pre-registered, not yet scored.", self.plan)
        self.assertIn("| 0 coal rows retired in %d; 16 of 16 plan generators match | held |" % 2026, self.page)
        self.assertIn("| about 85% | 0 rows | held |", self.page)
        self.assertEqual(p["S1"]["retired_2026"], [])
        self.assertEqual(p["S2"]["plan_retired"], [])
        self.assertEqual(p["S2"]["still"], {"6090/1": "2026-12", "470/2": "2026-12"})
        self.assertIn("| about 75% | none retired; 6090/1 and 470/2 both 2026-12 | held |", self.page)
        s3 = p["S3"]
        self.assertAlmostEqual(s3["mw_under_orders"] / s3["mw"], s3["share"], places=4)
        self.assertIn("| about 85%% | %s MW in %d units; %s MW under orders (share %.4f) | held |"
                      % (mw(s3["mw"]), s3["units"], mw(s3["mw_under_orders"]), s3["share"]), self.page)

    def test_chances_and_brier(self):
        chances = dict(re.findall(r"^\| (S\d) \| .+ \| about (\d+)% \|", self.plan, re.M))
        self.assertEqual(chances, {"S1": "85", "S2": "75", "S3": "85"})
        briers = {k: ((100 - int(c)) / 100.0) ** 2 for k, c in chances.items()}
        expected = sum(int(c) for c in chances.values())
        self.assertIn("The three chances add up to %d.%02d predictions expected to hold; 3 held." %
                      (expected // 100, expected % 100), self.page)
        self.assertIn("Brier scores: %.4f (S1), %.4f (S2) and %.4f (S3), mean %.4f." %
                      (briers["S1"], briers["S2"], briers["S3"], sum(briers.values()) / 3), self.page)

    def test_changes(self):
        ch = {c["key"]: c for c in self.res["changes"]}
        self.assertEqual(sorted(ch), ["1012/2", "6021/1", "6085/17", "6085/18"])
        for key, before in (("1012/2", "2026-09"), ("6021/1", "2026-09"), ("6085/17", "2026-10"),
                            ("6085/18", "2026-10")):
            self.assertEqual(ch[key]["august"], "operating " + before)
            self.assertEqual(ch[key]["september"], "operating 2026-12")
        self.assertIn("Culley 2 (%s MW) and Craig 1 (%s MW) moved from 2026-09 to 2026-12, and Schahfer 17 and 18 "
                      "(%s MW each) moved from 2026-10 to 2026-12." % (mw(ch["1012/2"]["mw"]), mw(ch["6021/1"]["mw"]),
                                                                        mw(ch["6085/17"]["mw"])), self.page)
        self.assertIn("Culley 2 and Craig 1 moved from 2026-09 to 2026-12, and Schahfer 17-18 from 2026-10 to "
                      "2026-12, the months their DOE orders now expire.", self.new)

    def test_ahead(self):
        ahead = self.res["ahead"]
        self.assertEqual(self.res["overdue"], [])
        self.assertFalse(any("2026-10" in a["months"] for a in ahead))
        first = min(ahead, key=lambda a: a["first"])
        self.assertEqual((first["plant"], first["first"], first["mw"]), ("J H Campbell", "2026-11", 1330.5))
        self.assertIn("the earliest is Campbell 1-3 (%s MW), dated 2026-11" % mw(first["mw"]), self.page)
        total = sum(a["mw"] for a in ahead)
        under = sum(a["mw"] for a in ahead if a["doe_order"] == "yes")
        self.assertIn("%d plants, %s MW, of which %s MW is at plants under DOE orders." % (len(ahead), mw(total),
                                                                                         mw(under)), self.page)
        self.assertIn("%d plants, %s MW; %s MW at plants under DOE orders." % (len(ahead), mw(total), mw(under)),
                      self.out)
        y26 = [a for a in ahead if a["months"].startswith("2026")]
        y27 = [a for a in ahead if a["months"] == "2027-12"]
        self.assertEqual(len(y26) + len(y27), len(ahead))
        self.assertEqual(mw(sum(a["mw"] for a in y26)), mw(self.res["predictions"]["S3"]["mw"]))
        self.assertIn("**Dated 2026:** %s MW in %s plants." % (mw(sum(a["mw"] for a in y26)), WORDS[len(y26)]),
                      self.page)
        self.assertEqual(sum(a["doe_order"] == "yes" for a in y26), 4)
        self.assertFalse(any(a["doe_order"] == "yes" for a in y27))
        self.assertIn("**Dated 2027-12:** %s MW in %s plants, none under a DOE order" %
                      (mw(sum(a["mw"] for a in y27)), WORDS[len(y27)]), self.page)
        top = sorted(y27, key=lambda a: -a["mw"])[:3]
        self.assertEqual([a["plant_id"] for a in top], ["889", "876", "6073"])
        self.assertIn("led by Baldwin (%s MW) and Kincaid (%s MW) in Illinois and Victor J Daniel (%s MW) in "
                      "Mississippi." % tuple(mw(a["mw"]) for a in top), self.page)

    def test_2025_retirements_match_coal_rows(self):
        recent = self.res["retired_recent"]
        self.assertEqual(len(recent), 8)
        lines = self.old.splitlines()
        for r in recent:
            self.assertTrue(r["ym"].startswith("2025"), r["key"])
            pid, gen = r["key"].split("/")
            head = "| %s | %s | %s |" % (NAMES_2025[pid], r["state"], gen)
            hits = [ln for ln in lines if ln.startswith(head)]
            self.assertEqual(len(hits), 1, r["key"])
            self.assertTrue(hits[0].endswith("| %s |" % r["ym"]), r["key"])
        self.assertIn("The final 2025 EIA-860 (generator file, retired sheet) lists 8 coal generators retired in "
                      "2025.", self.old)
        self.assertIn("The eight coal generators on the September Retired sheet with retirement year 2025 are the "
                      "same eight", self.page)

    def test_tests_and_md5(self):
        self.assertIn("Ran 25 tests", self.units)
        self.assertEqual(self.units.count(" ... ok"), 25)
        self.assertTrue(self.units.rstrip().endswith("OK"))
        self.assertIn("its 25 unit tests, which passed in the sealed job on 2026-10-28", self.page)
        self.assertIn("coalsep.py b36246dcb0c041e996802c4a077148bc", self.md5)
        self.assertIn("test_coalsep.py 6cc8a9577036704da95b2b5e05d931c3", self.md5)

    def test_coal_rows_update(self):
        self.assertEqual(self.rows.count(UPDATE), 1)
        self.assertTrue(self.old.startswith("# Coal retirements against EIA's plan, row by row (2016-2026)\n"))
        self.assertTrue(self.old.endswith("The numbers here come from the copy downloaded on 2026-10-15.\n\n"))
        self.assertIn("| 2026 (to Aug) | 2025-12 | 6.4 | 6.35 | 0.00 | 0.00 |", self.old)
        self.assertIn("so EIA-860M now records **no coal retirement from January to September 2026**.", self.new)
        self.assertIn("(16 of 16 plan generators with the same month, and no 2026 coal retirement)", self.new)
        self.assertIn("The gate and all three predictions held; details in [`coalsep.md`](coalsep.md).", self.new)
        self.assertIn("Sherburne County 1 and Comanche 2 are still dated 2026-12.", self.new)
        self.assertNotIn("MIT", self.new + self.page)


if __name__ == "__main__":
    unittest.main()
