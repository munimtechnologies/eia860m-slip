"""Unit tests for patch_title.py and compare_title.py (MV2 of Munim, Inc.; made with AI agents). Apache-2.0."""

import unittest

import compare_title as ct
import patch_title as pt

TOOL = ('"""doc"""\n__version__ = "0.1.0"\n\n\ndef render(res):\n' + pt.OLD_TITLE + '\n        "x"]\n'
        '    return "\\n".join(md)\n')
TESTS = 'import unittest\n\n\nclass A(unittest.TestCase):\n    pass\n\n\nif __name__ == "__main__":\n    unittest.main()\n'


class Patch(unittest.TestCase):
    def test_tool(self):
        out = pt.patch_tool(TOOL)
        self.assertIn('__version__ = "0.1.1"', out)
        self.assertIn('__version__, target), "",', out)
        self.assertNotIn('res["target"]), "",', out)
        self.assertEqual(out.count("\n") - TOOL.count("\n"), 1)

    def test_twice_refused(self):
        with self.assertRaises(SystemExit):
            pt.patch_tool(pt.patch_tool(TOOL))

    def test_tests(self):
        out = pt.patch_tests(TESTS)
        self.assertIn("class Title(unittest.TestCase):", out)
        self.assertTrue(out.endswith('\n\n\nif __name__ == "__main__":\n    unittest.main()\n'))
        self.assertLess(out.index("class A"), out.index("class Title"))


class Compare(unittest.TestCase):
    def test_pages(self):
        self.assertTrue(ct.compare_pages("# {'month': ...}\n\nbody\n", ct.TITLE + "\n\nbody\n")["held"])
        self.assertFalse(ct.compare_pages("# old\n\nbody\n", ct.TITLE + "\n\nbody2\n")["held"])
        self.assertFalse(ct.compare_pages("# old\n\nbody\n", "# other\n\nbody\n")["held"])
        self.assertFalse(ct.compare_pages("# old\nbody\n", ct.TITLE + "\nbody\nmore\n")["held"])

    def test_json(self):
        a = {"version": "0.1.0", "started_at": 1, "finished_at": 2, "backtest": {"x": 1}}
        b = {"version": "0.1.1", "started_at": 3, "finished_at": 4, "backtest": {"x": 1}}
        self.assertTrue(ct.compare_json(a, b)["held"])
        b["backtest"] = {"x": 2}
        self.assertEqual(ct.compare_json(a, b), {"keys_differ": ["backtest", "finished_at", "started_at", "version"],
                                                 "held": False})


if __name__ == "__main__":
    unittest.main()
