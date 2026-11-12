# Copyright 2026 Munim, Inc.
# Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working in the name of MV2 of Munim, Inc. (mv2@munimtech.com).
"""Unit tests for vcefips (stdlib only; DuckDB is not needed)."""
import unittest

import vcefips

# A small table shaped like the predicted real one.
GOOD = [
    ("46011", "brookings", 100),
    ("46013", "brown", 100),
    ("46102", "oglala lakota", 100),
    (None, "lake st clair", 50),
    (None, "lake huron", 50),
]


class TestInSet(unittest.TestCase):
    def test_as_written_selects_nothing(self):
        self.assertEqual(vcefips.in_set_failures(GOOD, "46012", ["oglala lakota"]), (0, 0))

    def test_corrected_passes(self):
        self.assertEqual(vcefips.in_set_failures(GOOD, "46102", ["oglala lakota"]), (100, 0))

    def test_wrong_name_fails_only_when_rows_selected(self):
        self.assertEqual(vcefips.in_set_failures(GOOD, "46102", ["shannon"]), (100, 100))
        self.assertEqual(vcefips.in_set_failures(GOOD, "46012", ["shannon"]), (0, 0))

    def test_null_name_counts_as_failure(self):
        g = [("46102", None, 7)]
        self.assertEqual(vcefips.in_set_failures(g, "46102", ["oglala lakota"]), (7, 7))


class TestNotInSet(unittest.TestCase):
    def test_underscore_forms_never_match(self):
        self.assertEqual(vcefips.not_in_set_failures(GOOD, vcefips.NOT_IN_SET), 0)

    def test_space_forms_match_lake_st_clair(self):
        self.assertEqual(
            vcefips.not_in_set_failures(GOOD, vcefips.spaced(vcefips.NOT_IN_SET)), 50)


class TestScore(unittest.TestCase):
    def test_all_hold_on_predicted_shape(self):
        res = vcefips.score(GOOD)
        for k in ["V1", "V2", "V3", "V4", "C1", "C1b", "C2"]:
            self.assertTrue(res[k]["held"], k)
        self.assertEqual(res["explore"]["rows_null_fips"], 100)
        self.assertEqual(res["explore"]["n_fips"], 3)

    def test_v1_fails_if_46012_present(self):
        res = vcefips.score(GOOD + [("46012", "x", 3)])
        self.assertFalse(res["V1"]["held"])
        self.assertEqual(res["V1"]["failing_rows_as_written"], 3)

    def test_v2_fails_on_old_name(self):
        res = vcefips.score([("46102", "shannon", 5)] + GOOD[3:])
        self.assertFalse(res["V2"]["held"])
        self.assertFalse(res["C1"]["held"])  # 'shannon' matches, so the control cannot fail

    def test_v3_fails_on_underscore(self):
        res = vcefips.score(GOOD + [(None, "lake_st_clair", 2)])
        self.assertFalse(res["V3"]["held"])
        self.assertEqual(res["V3"]["failing_rows_as_written"], 2)

    def test_v4_fails_if_bedford_city_present(self):
        res = vcefips.score(GOOD + [("51515", "bedford city", 1)])
        self.assertFalse(res["V4"]["held"])

    def test_v4_fails_if_st_clair_has_fips(self):
        res = vcefips.score([g for g in GOOD if g[1] != "lake st clair"]
                            + [("26099", "lake st clair", 5)])
        self.assertFalse(res["V4"]["held"])

    def test_spaced(self):
        self.assertEqual(vcefips.spaced(["a_b_c", "d"]), ["a b c", "d"])


if __name__ == "__main__":
    unittest.main()
