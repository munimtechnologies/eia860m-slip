"""Offline tests for left3.py. Apache-2.0. MV2 of Munim, Inc. (made with AI agents)."""

import unittest

import left3


class Left3Tests(unittest.TestCase):
    def test_norm_gen(self):
        self.assertEqual(left3.norm_gen(10.0), "10")
        self.assertEqual(left3.norm_gen(" A1 "), "A1")
        self.assertEqual(left3.norm_gen(float("nan")), "")
        self.assertEqual(left3.norm_gen(None), "")
        self.assertEqual(left3.norm_gen("LUPE3"), "LUPE3")

    def test_norm_plant(self):
        self.assertEqual(left3.norm_plant("67674"), 67674)
        self.assertEqual(left3.norm_plant(67674.0), 67674)
        self.assertIsNone(left3.norm_plant("Plant ID"))
        self.assertIsNone(left3.norm_plant(None))

    def test_find_header(self):
        rows = [["Inventory of Planned Generators", None], [None, None],
                ["Entity ID", "Plant ID", "Generator ID"], [1, 2, "A"]]
        self.assertEqual(left3.find_header(rows), 2)
        self.assertIsNone(left3.find_header([["x", "y"], [1, 2]]))

    def test_sheet_rows(self):
        rows = [["title"], ["Plant ID", "Generator ID", "Status"],
                [67674, "LUPE3", "(U) Under construction"], [67674, "LUPE4", "x"],
                [69144.0, "PV1", "y"], [1, 10.0, "z"], []]
        h, found = left3.sheet_rows(rows, ["67674/LUPE3", "69144/PV1", "1/10"])
        self.assertEqual(h, 1)
        self.assertEqual([(r["Plant ID"], r["Generator ID"]) for r in found],
                         [("67674", "LUPE3"), ("69144.0", "PV1"), ("1", "10.0")])
        self.assertEqual(found[0]["Status"], "(U) Under construction")
        self.assertEqual(left3.sheet_rows([["no header"]], ["1/1"]), (None, []))

    def test_key_lists(self):
        self.assertEqual(len(left3.DIFF), 3)
        self.assertEqual(len(left3.LEFT_BOTH), 7)
        self.assertEqual(len(left3.NINE), 9)
        self.assertEqual(len(set(left3.KEYS)), 19)
        self.assertEqual(left3.split_key("67836/GSP1"), (67836, "GSP1"))


if __name__ == "__main__":
    unittest.main()
