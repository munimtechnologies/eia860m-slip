"""Doc test: the 2026-10-28 update to docs/order-dates.md (P5 scored on EIA's September 2026 workbook) says
what job p5score-v1 found (docs/p5score-2026-09.md, data/p5score_2026-09.json), and the page's earlier text,
including the old P5 row, is kept.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))

UPDATE = "## Update, 2026-10-28: P5 scored on EIA's September 2026 workbook"
# plant key in p5score.json -> (name on the page, units, order in force on 30 September 2026)
PLANTS = {
    "campbell": ("J.H. Campbell (MI)", "1710/1-3", "202-26-39"),
    "schahfer": ("R.M. Schahfer (IN)", "6085/17-18", "202-26-46"),
    "culley": ("F.B. Culley (IN)", "1012/2", "202-26-47"),
    "craig": ("Craig (CO)", "6021/1", "202-26-49"),
}


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8") as fh:
        return fh.read()


class OrderDatesP5Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = read("docs", "order-dates.md")
        cls.out = read("docs", "p5score-2026-09.md")
        cls.res = json.loads(read("data", "p5score_2026-09.json"))
        cls.note = read("docs", "p5score-note.txt")
        cls.units = read("docs", "p5score-v1-unittests.txt")
        cls.md5 = read("docs", "p5score-v1-md5.txt")
        cls.old, cls.new = cls.page.split(UPDATE)

    def test_job_result(self):
        self.assertTrue(self.res["w1_held"])
        self.assertEqual(self.res["p5_verdict"], "held")
        self.assertEqual(self.res["p5_exact"], 4)
        self.assertEqual(self.res["p5_need"], 3)
        self.assertEqual(self.res["version"], "0.1.0")
        self.assertIn("W1 (August 2026 workbook reproduces order-dates' C2 months): **held**", self.out)
        self.assertIn("P5: 4 of 4 exact (needs 3): **held**", self.out)
        for f in self.res["files"].values():
            self.assertTrue(f["same_as_recorded"])
            self.assertEqual(f["errors"], [])

    def test_update_table(self):
        for key, (name, units, order) in PLANTS.items():
            p = self.res["p5"][key]
            self.assertEqual(p["class"], "exact")
            self.assertEqual(p["months"], [p["target"]])
            self.assertIn("| %s | %s | %s (%s) | %s | %s |" % (name, units, p["target"], order, p["months"][0],
                                                              p["class"]), self.new)
            self.assertIn("| %s | %s | exact | %s |" % (key, p["target"], p["target"]), self.out)
        self.assertIn("**P5 held: all 4 of 4 coal plants were dated exactly to the expiry of the order in force on 30 "
                      "September 2026** (the bar was at least 3 of 4).", self.new)
        self.assertIn("| P5 | September 2026 report: 3 of 4 coal plants exact | **held**: 4 of 4 (EIA's September "
                      "2026 workbook; gate W1 held) |", self.new)

    def test_w1_and_moves(self):
        w1 = self.res["w1"]
        self.assertEqual({k: v["target"] for k, v in w1.items()},
                         {"campbell": "2026-11", "schahfer": "2026-10", "culley": "2026-09", "craig": "2026-09"})
        self.assertTrue(all(v["class"] == "exact" for v in w1.values()))
        self.assertIn("(Campbell 2026-11, Schahfer 2026-10, Culley 2026-09, Craig 2026-09)", self.new)
        self.assertIn("(Campbell 2026-11, Schahfer 2026-10, Culley 2026-09, Craig 2026-09)", self.note)
        self.assertIn("**W1 held: all four matched.**", self.new)
        self.assertIn("In September 2026 it moved from 2026-10 to 2026-12, the month order 202-26-46 expires.", self.new)
        self.assertIn("Craig 1 and Culley 2 moved from 2026-09 to 2026-12 with their renewals; Campbell stayed at "
                      "2026-11.", self.new)

    def test_reported_not_scored(self):
        o = self.res["other"]
        self.assertEqual((o["eddystone"]["class"], o["eddystone"]["months"]), ("exact", ["2026-11"]))
        self.assertEqual(o["wagner"]["months"], ["2029-06"])
        self.assertEqual(o["centralia"]["class"], "no month")
        self.assertEqual(o["stanton"]["class"], "no month")
        self.assertIn("Eddystone 3-4 are dated 2026-11, the expiry month of the order in force (exact); Wagner 4 is "
                      "still dated 2029-06; Centralia 2 and Stanton 1 still carry no planned retirement month.", self.new)
        rows = self.res["rows"]["september"]
        self.assertEqual(len(rows), 12)
        self.assertTrue(all(r["sheet"] == "Operating" and r["status"] == "(OP) Operating" for r in rows))
        self.assertIn("All 12 matched generators at the eight plants are on the Operating sheet with status (OP) "
                      "Operating", self.new)

    def test_files_and_tests(self):
        for f in self.res["files"].values():
            self.assertIn("(%s bytes, md5 %s)" % ("{:,}".format(f["size"]), f["md5"]), self.new)
        self.assertIn("Ran 15 tests", self.units)
        self.assertTrue(self.units.rstrip().endswith("OK"))
        self.assertEqual(self.units.count(" ... ok"), 15)
        self.assertIn("whose 15 unit tests passed in the sealed job on 2026-10-27", self.new)
        self.assertIn("p5score.py 678a3ccde914b964d344c1d1baaff99b", self.md5)
        self.assertIn("Plant rule (written 2026-10-27 before reading September's rows for these units): exact when "
                      "at least one", self.note)
        self.assertIn("unit is on the Operating sheet with a planned retirement month and every such unit is dated "
                      "to the target.", self.note)

    def test_earlier_text_kept(self):
        self.assertEqual(self.page.count(UPDATE), 1)
        self.assertTrue(self.old.startswith("# EIA's planned retirement dates for the plants DOE holds open are the "
                                            "order calendar\n"))
        self.assertIn("| P5 | September 2026 report: 3 of 4 coal plants exact | not scorable | not yet scorable "
                      "(release due 2026-10-23) |", self.old)
        self.assertIn("**Status: scored (second run, 2026-10-18).**", self.old)
        self.assertIn("| R.M. Schahfer (IN) | 6085/17-18 | 2025-12 | 4 | 18 | 6 | 6 | 0 | 2026-10 |", self.old)
        self.assertLess(self.old.index("## Limits"), len(self.old))
        self.assertTrue(self.old.endswith("no new plant order had been posted by 2026-10-18.\n\n"))
        self.assertNotIn("MIT", self.new)


if __name__ == "__main__":
    unittest.main()
