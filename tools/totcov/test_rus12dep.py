# Copyright 2026 Munim, Inc.
# Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working in the name of MV2 of Munim, Inc. (mv2@munimtech.com).
"""Tests for rus12dep. The DuckDB tests are skipped when duckdb is not installed."""
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import rus12dep as R  # noqa: E402

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
        self.assertEqual(len(R.existing_specs(True)), 8)
        self.assertEqual(len(R.existing_specs(False)), 8)
        self.assertEqual(len(R.proposed_specs()), 8)
        self.assertEqual(len(R.all_specs()), 8 + 8 + 8 + 8 + 1)

    def test_existing_as_in_pudl(self):
        s = R.existing_specs(True)[0]
        self.assertEqual(s["cols"], ["depreciation_and_amortization_group"])
        self.assertEqual(s["total"], "total_depreciation")
        self.assertEqual(s["group_by"], ["borrower_id_rus", "report_date"])
        self.assertEqual(s["row_condition"],
                         "depreciation_and_amortization_group='electric_plant_in_service'")
        self.assertEqual(s["tolerance"], 0.01)
        self.assertIsNone(s["min_cov"])
        self.assertEqual(s["value"], "accruals")
        self.assertIsNone(R.existing_specs(False)[0]["row_condition"])

    def test_total_label_is_not_a_group(self):
        self.assertEqual(R.GROUPS, ["electric_plant_in_service",
                                    "provision_for_depreciation_and_amortization"])
        self.assertNotIn("total_depreciation", R.GROUPS)

    def test_proposed_uses_items(self):
        for s in R.proposed_specs():
            self.assertEqual(s["cols"], ["depreciation_and_amortization_item"])
            self.assertEqual(s["group_by"], ["borrower_id_rus", "report_date"])
            self.assertEqual(s["tolerance"], 10.0)
            self.assertEqual(len(s["subs"]), 8)
            self.assertIn("retirement_work_in_progress", s["subs"])
        for s in R.proposed_specs(R.PLANT_ITEMS, "proposed_no_rwip", "_no_rwip"):
            self.assertEqual(len(s["subs"]), 7)
            self.assertNotIn("retirement_work_in_progress", s["subs"])
            self.assertTrue(s["name"].endswith("_no_rwip"))

    def test_negative_negates_every_item(self):
        s = R.negative_spec()
        self.assertEqual(s["negs"], R.EPIS_ITEMS)
        self.assertEqual(s["subs"], ["__none__"])
        self.assertNotIn("total_depreciation", s["negs"])
        self.assertEqual(s["value"], "ending_balance")

    def test_provision_specs_from_pairs(self):
        pairs = [(R.EPIS, "depreciation_steam_production_plant"), (R.EPIS, "total_depreciation"),
                 (R.PROV, "amortization_leased_plant"), (R.PROV, "total")]
        specs = R.provision_specs(pairs, "t")
        self.assertEqual(len(specs), 8)
        self.assertEqual(specs[0]["subs"], [[R.PROV, "amortization_leased_plant"]])
        self.assertEqual(specs[0]["total"], [R.PROV, "total"])
        self.assertEqual(specs[4]["subs"], [[R.PROV, "amortization_leased_plant"],
                                            [R.EPIS, "total_depreciation"]])
        self.assertEqual(R.provision_specs(pairs[:3], "t"), [])


class EvaluateTests(unittest.TestCase):
    def test_held(self):
        res = ([rec("existing", n_groups=5, n_with_total=0)] * 8
               + [rec("existing_norc", n_groups=5, n_with_total=0)] * 8
               + [rec("proposed", n_with_subs=10, n_subs_no_total=1)] * 8
               + [rec("negative", n_material=10, n_material_fail=9)])
        self.assertEqual(R.evaluate(res), {"D1": "held", "D2": "held", "D3": "held"})

    def test_failed(self):
        res = ([rec("existing", n_groups=5, n_with_total=0)] * 8
               + [rec("existing_norc", n_groups=5, n_with_total=0)] * 7
               + [rec("existing_norc", n_groups=5, n_with_total=1)]
               + [rec("proposed", n_with_subs=10, n_subs_no_total=2)] * 8
               + [rec("negative", n_material=10, n_material_fail=8)])
        self.assertEqual(R.evaluate(res), {"D1": "failed", "D2": "failed", "D3": "failed"})

    def test_not_tested(self):
        self.assertEqual(R.evaluate([]), {"D1": "not tested", "D2": "not tested",
                                          "D3": "not tested"})
        res = [rec("negative", n_material=0, n_material_fail=0)]
        self.assertEqual(R.evaluate(res)["D3"], "not tested")


ROWS = [  # borrower, group, item, ending_balance (other value columns 0)
    ("A", "electric_plant_in_service", "depreciation_steam_production_plant", 100.0),
    ("A", "electric_plant_in_service", "depreciation_distribution_plant", 50.0),
    ("A", "electric_plant_in_service", "retirement_work_in_progress", -20.0),
    ("A", "electric_plant_in_service", "total_depreciation", 130.0),  # 100 + 50 - 20
    ("A", "provision_for_depreciation_and_amortization", "amortization_leased_plant", 3.0),
    ("A", "provision_for_depreciation_and_amortization", "total", 133.0),  # 130 + 3
    ("B", "electric_plant_in_service", "depreciation_steam_production_plant", 10.0),
    ("B", "electric_plant_in_service", "total_depreciation", 40.0),  # deliberate mismatch
]


@unittest.skipUnless(HAVE_DUCKDB, "duckdb not installed")
class SqlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import duckdb  # noqa: PLC0415
        cls.tmp = tempfile.mkdtemp()
        cls.path = os.path.join(cls.tmp, "dep.parquet")
        cls.con = duckdb.connect()
        cls.con.execute(
            "CREATE TABLE t (borrower_id_rus VARCHAR, report_date DATE, "
            "depreciation_and_amortization_group VARCHAR, "
            "depreciation_and_amortization_item VARCHAR, accruals DOUBLE, "
            "retirements_less_net_salvage DOUBLE, adjustments_and_transfers DOUBLE, "
            "ending_balance DOUBLE)")
        for b, g, i, v in ROWS:
            cls.con.execute("INSERT INTO t VALUES (?, DATE '2020-01-01', ?, ?, 0, 0, 0, ?)",
                            [b, g, i, v])
        cls.con.execute("COPY t TO '%s' (FORMAT PARQUET)" % cls.path.replace("'", "''"))

    @classmethod
    def tearDownClass(cls):
        cls.con.close()
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def spec(self, specs, value="ending_balance"):
        return [s for s in specs if s["value"] == value][0]

    def test_existing_tests_are_vacuous(self):
        for with_rc in (True, False):
            r = R.measure(self.con, self.path, self.spec(R.existing_specs(with_rc)))
            self.assertNotIn("error", r)
            self.assertEqual(r["n_groups"], 2)
            self.assertEqual(r["n_with_subs"], 2)
            self.assertEqual(r["n_with_total"], 0)
            self.assertEqual(r["n_fail"], 0)  # B's mismatch is invisible
            self.assertEqual(r["absent_labels"], ["total_depreciation"])

    def test_proposed_test_finds_mismatch(self):
        r = R.measure(self.con, self.path, self.spec(R.proposed_specs()))
        self.assertNotIn("error", r)
        self.assertEqual(r["n_groups"], 2)
        self.assertEqual(r["n_with_total"], 2)
        self.assertEqual(r["n_fail"], 1)
        self.assertEqual(r["n_subs_no_total"], 0)

    def test_without_rwip_fails_more(self):
        specs = R.proposed_specs(R.PLANT_ITEMS, "proposed_no_rwip", "_no_rwip")
        r = R.measure(self.con, self.path, self.spec(specs))
        self.assertEqual(r["n_fail"], 2)

    def test_negative_control_fails(self):
        r = R.measure(self.con, self.path, R.negative_spec())
        self.assertNotIn("error", r)
        self.assertEqual(r["n_material"], 2)
        self.assertEqual(r["n_material_fail"], 2)

    def test_provision_total(self):
        pairs = sorted(set((g, i) for _, g, i, _ in ROWS))
        specs = R.provision_specs(pairs, "t")
        own = [s for s in specs if s["name"] == "provision_own_items_ending_balance"][0]
        plus = [s for s in specs if s["name"] == "provision_own_items_plus_epis_ending_balance"][0]
        r_own = R.measure(self.con, self.path, own)
        r_plus = R.measure(self.con, self.path, plus)
        self.assertNotIn("error", r_own)
        self.assertNotIn("error", r_plus)
        self.assertEqual(r_own["n_with_total"], 1)
        self.assertEqual(r_own["n_fail"], 1)
        self.assertEqual(r_plus["n_fail"], 0)


if __name__ == "__main__":
    unittest.main()
