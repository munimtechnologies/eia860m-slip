# Copyright 2026 Munim, Inc.
# Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working in the name of MV2 of Munim, Inc. (mv2@munimtech.com).
"""Tests for rus12upc. The DuckDB tests are skipped when duckdb is not installed."""
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import rus12upc as R  # noqa: E402

try:
    import duckdb  # noqa: F401
    HAVE_DUCKDB = True
except ImportError:
    HAVE_DUCKDB = False


def rec(kind, **kw):
    d = {"kind": kind}
    d.update(kw)
    return d


class SpecTests(unittest.TestCase):
    def test_counts(self):
        self.assertEqual(len(R.existing_specs()), 8)
        self.assertEqual(len(R.proposed_specs()), 8)

    def test_existing_as_in_pudl(self):
        s = R.existing_specs()[0]
        self.assertEqual(s["cols"], ["utility_plant_group"])
        self.assertEqual(s["total"], "total")
        self.assertEqual(s["group_by"], ["borrower_id_rus", "report_date"])
        self.assertEqual(s["row_condition"], R.EXCL)
        self.assertEqual(s["tolerance"], 0.01)
        self.assertIsNone(s["min_cov"])

    def test_total_is_not_a_group(self):
        groups = ["intangible_plant", "production_plant", "transmission_plant",
                  "distribution_plant", "electric_plant_in_service",
                  "utility_plant_in_service", "total_utility_plant"]
        self.assertNotIn("total", groups)
        self.assertEqual(sorted(R.LOWER + [g for g, _ in R.UPPER]), sorted(groups))

    def test_proposed_groups_by_plant_group(self):
        for s in R.proposed_specs():
            self.assertEqual(s["group_by"], ["borrower_id_rus", "report_date",
                                             "utility_plant_group"])
            self.assertEqual(s["cols"], ["utility_plant_item"])
            self.assertEqual(s["tolerance"], 10.0)

    def test_negative_negates_every_item(self):
        s = R.negative_spec()
        self.assertEqual(s["subs"], [])
        self.assertEqual(len(s["negs"]), 16)
        self.assertNotIn("total", s["negs"])
        self.assertEqual(s["value"], "ending_balance")

    def test_upper_specs_from_pairs(self):
        pairs = [("production_plant", "total"), ("transmission_plant", "total"),
                 ("electric_plant_in_service", "general_plant"),
                 ("electric_plant_in_service", "total"),
                 ("utility_plant_in_service", "total"),
                 ("total_utility_plant", "construction_work_in_progress")]
        specs = R.upper_specs(pairs, "t")
        self.assertEqual(len(specs), 8)  # EPIS and UPIS x 4 values; TUP has no total
        epis = specs[0]
        self.assertEqual(epis["total"], ["electric_plant_in_service", "total"])
        self.assertEqual(epis["subs"], [["production_plant", "total"],
                                        ["transmission_plant", "total"],
                                        ["electric_plant_in_service", "general_plant"]])
        upis = specs[4]
        self.assertEqual(upis["subs"], [["electric_plant_in_service", "total"]])


class EvaluateTests(unittest.TestCase):
    def test_held(self):
        res = ([rec("existing", n_groups=5, n_with_total=0)] * 8
               + [rec("proposed", n_with_subs=10, n_subs_no_total=1)] * 8
               + [rec("negative", n_material=10, n_material_fail=9)])
        self.assertEqual(R.evaluate(res), {"Q1": "held", "Q2": "held", "Q3": "held"})

    def test_failed(self):
        res = ([rec("existing", n_groups=5, n_with_total=0)] * 7
               + [rec("existing", n_groups=5, n_with_total=1)]
               + [rec("proposed", n_with_subs=10, n_subs_no_total=2)] * 8
               + [rec("negative", n_material=10, n_material_fail=8)])
        self.assertEqual(R.evaluate(res), {"Q1": "failed", "Q2": "failed", "Q3": "failed"})

    def test_not_tested(self):
        self.assertEqual(R.evaluate([]), {"Q1": "not tested", "Q2": "not tested",
                                          "Q3": "not tested"})
        res = [rec("negative", n_material=0, n_material_fail=0)]
        self.assertEqual(R.evaluate(res)["Q3"], "not tested")


ROWS = [  # group, item, ending_balance (other value columns 0)
    ("production_plant", "steam", 100.0),
    ("production_plant", "nuclear", 50.0),
    ("production_plant", "total", 150.0),
    ("transmission_plant", "station_equipment", 40.0),
    ("transmission_plant", "other", 10.0),
    ("transmission_plant", "total", 75.0),  # deliberate mismatch: items sum to 50
    ("electric_plant_in_service", "general_plant", 5.0),
    ("electric_plant_in_service", "total", 230.0),  # 150 + 75 + 5
]


@unittest.skipUnless(HAVE_DUCKDB, "duckdb not installed")
class SqlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import duckdb  # noqa: PLC0415
        cls.tmp = tempfile.mkdtemp()
        cls.path = os.path.join(cls.tmp, "upc.parquet")
        cls.con = duckdb.connect()
        cls.con.execute(
            "CREATE TABLE t (borrower_id_rus VARCHAR, report_date DATE, "
            "utility_plant_group VARCHAR, utility_plant_item VARCHAR, retirements DOUBLE, "
            "additions DOUBLE, adjustments_and_transfers DOUBLE, ending_balance DOUBLE)")
        for g, i, v in ROWS:
            cls.con.execute("INSERT INTO t VALUES ('A', DATE '2020-01-01', ?, ?, 0, 0, 0, ?)",
                            [g, i, v])
        cls.con.execute("COPY t TO '%s' (FORMAT PARQUET)" % cls.path.replace("'", "''"))

    @classmethod
    def tearDownClass(cls):
        cls.con.close()
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def spec(self, specs, value="ending_balance"):
        return [s for s in specs if s["value"] == value][0]

    def test_existing_test_is_vacuous(self):
        r = R.measure(self.con, self.path, self.spec(R.existing_specs()))
        self.assertEqual(r["n_groups"], 1)
        self.assertEqual(r["n_with_subs"], 1)
        self.assertEqual(r["n_with_total"], 0)
        self.assertEqual(r["n_fail"], 0)  # the mismatch is invisible
        self.assertEqual(r["absent_labels"], ["total"])

    def test_proposed_test_finds_mismatch(self):
        r = R.measure(self.con, self.path, self.spec(R.proposed_specs()))
        self.assertEqual(r["n_groups"], 2)
        self.assertEqual(r["n_with_total"], 2)
        self.assertEqual(r["n_fail"], 1)
        self.assertEqual(r["n_subs_no_total"], 0)

    def test_negative_control_fails(self):
        r = R.measure(self.con, self.path, R.negative_spec())
        self.assertNotIn("error", r)
        self.assertEqual(r["n_material"], 2)
        self.assertEqual(r["n_material_fail"], 2)

    def test_upper_total_holds(self):
        pairs = [(g, i) for g, i, _ in ROWS]
        upper = R.upper_specs(pairs, "t")
        self.assertEqual(len(upper), 4)  # only EPIS has a total here
        r = R.measure(self.con, self.path, self.spec(upper))
        self.assertEqual(r["n_groups"], 1)
        self.assertEqual(r["n_with_total"], 1)
        self.assertEqual(r["n_fail"], 0)


if __name__ == "__main__":
    unittest.main()
