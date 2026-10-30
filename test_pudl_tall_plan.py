"""Checks that docs/pudl-tall-plan.md describes what tools/pudl-tall/tall_check.py counts:
version, source, the four tables and the columns left out of the id columns. Reads both as
text, so it needs no pandas.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TABLES = ("boilers", "generators", "plants", "utilities")
NOT_ID = ("report_date", "valid_until_date", "column_name", "record_value",
          "entity_occurrences", "record_occurrences", "consistent_rate", "is_candidate")


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class PudlTallPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/pudl-tall-plan.md")
        cls.code = read("tools/pudl-tall/tall_check.py")

    def test_status_and_id(self):
        self.assertIn("Status: pre-registration, nothing counted yet.", self.doc)
        self.assertIn("Pre-registration id: pudl-tall-1.", self.doc)

    def test_version_and_source(self):
        self.assertIn('VERSION = "0.1.0"', self.code)
        self.assertIn("`tools/pudl-tall/tall_check.py` 0.1.0", self.doc)
        base = "https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/"
        self.assertIn('BASE = "%s"' % base, self.code)
        self.assertIn(base, self.doc)

    def test_tables(self):
        for t in TABLES:
            self.assertIn('"_core_eia__forensics_entity_resolution_%s",' % t, self.code)
        self.assertIn("(boilers, generators, plants, utilities)", self.doc)

    def test_id_columns(self):
        for c in NOT_ID:
            self.assertIn('"%s"' % c, self.code)
            self.assertIn("`%s`" % c, self.doc)

    def test_bars(self):
        for text in ("**P1 (80%):**", "**P2 (90%):**", "**P3 (95%):**", "**Gate:**"):
            self.assertIn(text, self.doc)
        self.assertIn('"zero_length_alone_on_series_date"', self.code)
        self.assertIn('"valid_until_before_report_date"', self.code)

    def test_no_data_stored(self):
        self.assertIn("PUDL's data is downloaded at run time and not stored here.", self.doc)
        self.assertIn("os.remove(path)", self.code)


if __name__ == "__main__":
    unittest.main()
