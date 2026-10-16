"""Tests for coal25.py (MV2 of Munim, Inc., made with AI agents). Apache-2.0. Needs pandas and openpyxl."""

import tempfile
import unittest

try:
    import openpyxl  # noqa: F401
    import coal25 as c25
    import eia860_final as ef
    from test_eia860_final import OP_HEAD, OPERABLE, sheet, write_zip
except ImportError:  # no pandas or openpyxl on this host
    c25 = None

needs_pandas = unittest.skipIf(c25 is None, "pandas or openpyxl is not installed")


@needs_pandas
class TestCoal25(unittest.TestCase):
    def test_over_nameplate(self):
        rows = OPERABLE + [[1, 14, "E", 100.0, 105.0, 2030, "NG", "OP"]]
        o = c25.over_nameplate(ef.with_header(sheet(OP_HEAD, rows)))
        self.assertEqual((o["rows"], o["over"]), (5, 1))
        self.assertEqual(o["by_group"], {"gas": {"n": 1, "excess_mw": 5.0}})
        self.assertEqual(o["largest"][0]["generator id"], "E")
        self.assertEqual(o["largest"][0]["plant code"], 14)
        self.assertAlmostEqual(o["largest"][0]["excess_mw"], 5.0)

    def test_year_result(self):
        with tempfile.TemporaryDirectory() as d:
            over, coal = c25.year_result(write_zip(d), 2030)
        self.assertEqual([r["generator id"] for r in coal], ["E"])
        self.assertEqual(coal[0]["nameplate capacity (mw)"], 200.0)
        self.assertEqual(over["operable"]["over"], 0)
        self.assertEqual(over["retired_in_year"]["rows"], 2)

    def test_clean(self):
        self.assertIsNone(c25.clean(float("nan")))
        self.assertIsNone(c25.clean(None))
        self.assertEqual(c25.clean("x"), "x")


if __name__ == "__main__":
    unittest.main()
