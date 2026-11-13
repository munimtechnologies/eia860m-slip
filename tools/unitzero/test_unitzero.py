"""Unit tests for unitzero.py (no network, no pandas needed).

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unitzero as uz  # noqa: E402


class NormalizationTests(unittest.TestCase):
    def test_pudl_helper_matches_pudl_unit_test_cases(self):
        # The cases in PUDL's tests/unit/helpers_test.py (read 2026-11-13).
        for raw, want in (("0001", "1"), ("26", "26"), ("100", "100"), ("100.0", "100.0"),
                          ("01-A", "01-A"), ("HRSG-01", "HRSG-01"), ("0A1", "0A1")):
            self.assertEqual(uz.pudl_helper(raw), want, raw)

    def test_pudl_helper_all_zero_ids(self):
        self.assertEqual(uz.pudl_helper("0"), "0")
        self.assertEqual(uz.pudl_helper("00"), "")
        self.assertEqual(uz.pudl_helper("000"), "")
        self.assertEqual(uz.pudl_helper("007"), "7")
        self.assertEqual(uz.pudl_helper(""), "")
        self.assertIsNone(uz.pudl_helper(None))

    def test_cems_strip(self):
        for raw, want in (("0", ""), ("00", ""), ("007", "7"), ("10", "10"), ("0A", "0A"),
                          ("**1", "**1"), ("CT01", "CT01"), ("", "")):
            self.assertEqual(uz.cems_strip(raw), want, raw)

    def test_the_two_disagree_only_on_single_zero(self):
        samples = ["0", "00", "000", "01", "001", "1", "10", "0A", "A0", "", "100.0", "0-1"]
        differ = [s for s in samples if uz.pudl_helper(s) != uz.cems_strip(s)]
        self.assertEqual(differ, ["0"])

    def test_keep_one_zero(self):
        for raw, want in (("0", "0"), ("00", "0"), ("000", "0"), ("007", "7"), ("10", "10"),
                          ("0A", "0A")):
            self.assertEqual(uz.keep_one_zero(raw), want, raw)

    def test_all_zero(self):
        self.assertTrue(uz.all_zero("0"))
        self.assertTrue(uz.all_zero("000"))
        self.assertFalse(uz.all_zero(""))
        self.assertFalse(uz.all_zero("01"))
        self.assertFalse(uz.all_zero(None))

    def test_isnull(self):
        self.assertTrue(uz.isnull(None))
        self.assertTrue(uz.isnull(float("nan")))
        self.assertFalse(uz.isnull(""))
        self.assertFalse(uz.isnull("0"))
        self.assertFalse(uz.isnull(3))

        class NA:  # behaves like pd.NA: comparisons give NA, bool() raises
            def __ne__(self, other):
                return self

            def __bool__(self):
                raise TypeError("boolean value of NA is ambiguous")
        self.assertTrue(uz.isnull(NA()))


class CountTests(unittest.TestCase):
    def test_collisions(self):
        pairs = [(1, "1"), (1, "01"), (1, "2"), (2, "1"), (3, "0"), (3, "00"), (4, "A"),
                 (4, "A"), (5, ""), (5, None)]
        col = uz.collisions(pairs)
        self.assertEqual(col, {(1, "1"): ["01", "1"]})
        col_cems = uz.collisions(pairs, norm=uz.cems_strip)
        self.assertEqual(col_cems, {(1, "1"): ["01", "1"], (3, ""): ["0", "00"]})

    def test_id_profile(self):
        p = uz.id_profile([None, "", "0", "00", "007", "7", "A"])
        self.assertEqual(p, {"values": 7, "null": 1, "empty": 1, "zero": 1, "multi_zero": 1,
                             "leading_zero": 1})


def measured(**kw):
    prof = {"values": 10, "null": 0, "empty": 0, "zero": 0, "multi_zero": 0, "leading_zero": 0}
    m = {
        "downloads_ok": True,
        "cems": {"rows_scanned": 1000, "rows_in_metadata": 1000, "plants_epa": 1500,
                 "empty_unit_rows": 0},
        "epa_crosswalk": {"CAMD_UNIT_ID": dict(prof)},
        "epa_crosswalk_collisions": {"CAMD_UNIT_ID": 0, "EIA_GENERATOR_ID": 0},
        "pudl": {"core_eia__entity_generators": {"generator_id": dict(prof)},
                 "core_eia__entity_boilers": {"boiler_id": dict(prof)}},
    }
    for k, v in kw.items():
        exec("m%s = v" % k, {"m": m, "v": v})
    return m


class ScoreTests(unittest.TestCase):
    def test_nothing_found(self):
        s = uz.score(measured())
        self.assertTrue(s["gate_G1"])
        self.assertEqual(s["predictions"], {"P1": False, "P2": False, "P3": True, "P4": False,
                                            "P5": True})
        self.assertEqual((s["held"], s["of"]), (2, 5))

    def test_cases_found(self):
        s = uz.score(measured(**{'["epa_crosswalk"]["CAMD_UNIT_ID"]["zero"]': 1,
                                 '["cems"]["empty_unit_rows"]': 2,
                                 '["epa_crosswalk_collisions"]["EIA_GENERATOR_ID"]': 1,
                                 '["pudl"]["core_eia__entity_boilers"]["boiler_id"]["empty"]': 1}))
        # 2 empty rows of 1,000 is 0.2%, above the 0.1% bar, so P5 fails here.
        self.assertEqual(s["predictions"], {"P1": True, "P2": True, "P3": False, "P4": True,
                                            "P5": False})

    def test_p5_bar(self):
        # P5: empty-unit rows are fewer than 0.1% of the CEMS rows scanned.
        s = uz.score(measured(**{'["cems"]["empty_unit_rows"]': 1}))
        self.assertFalse(s["predictions"]["P5"])  # 1 is not < 0.001 * 1000
        s = uz.score(measured(**{'["cems"]["empty_unit_rows"]': 1,
                                 '["cems"]["rows_scanned"]': 1001,
                                 '["cems"]["rows_in_metadata"]': 1001}))
        self.assertTrue(s["predictions"]["P5"])  # 1 < 1.001
        s = uz.score(measured(**{'["cems"]["empty_unit_rows"]': 0}))
        self.assertTrue(s["predictions"]["P5"])

    def test_gate(self):
        self.assertFalse(uz.score(measured(**{'["cems"]["rows_scanned"]': 999}))["gate_G1"])
        self.assertFalse(uz.score(measured(**{'["cems"]["plants_epa"]': 999}))["gate_G1"])
        self.assertFalse(uz.score(measured(**{'["downloads_ok"]': False}))["gate_G1"])


if __name__ == "__main__":
    unittest.main()
