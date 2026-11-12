"""Unit tests for spboil.py on small hand-made frames (no network, no PUDL data). They are
skipped where pandas or networkx is not installed.

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.)."""

import unittest

try:
    import networkx  # noqa: F401
    import pandas as pd

    import spboil as sb
    HAVE = True
except ImportError:  # the publish check has neither
    HAVE = False


def frames():
    xw = pd.DataFrame([
        # plant 10: one boiler B1 matched to two EPA units / two generators -> step 2 joins them
        (2023, 10, "U1", "G1", 10, "B1", "G1"),
        (2023, 10, "U2", "G2", 10, "B1", "G2"),
        # plant 20: two boilers on one unit/generator -> step 1 adds a row
        (2023, 20, "CT1", "GT1", 20, "HRSG1", "GT1"),
        (2023, 20, "CT1", "GT1", 20, "DB1", "GT1"),
        (2022, 20, "CT1", "GT1", 20, "HRSG1", "GT1"),  # same match a year earlier
        # plant 30: two separate units, no shared boiler
        (2023, 30, "A", "A", 30, "A", "A"),
        (2023, 30, "B", "B", 30, "B", "B"),
        # plant 63628 pattern: unit maps to two EIA plants in 2018 and 2019 -> drop 2018 row
        (2018, 40, "X", "X", 41, "X", "X"),
        (2019, 40, "X", "X", 42, "X", "X"),
    ], columns=sb.COLUMNS["xw"])
    gens = pd.DataFrame([(10, "G1"), (10, "G2"), (20, "GT1"), (30, "A"), (30, "B"),
                         (30, "C"), (42, "X")], columns=sb.COLUMNS["gens"])
    # plant 30: generator C shares boiler B with generator B in EIA-860 but no unit_id_pudl
    bga = pd.DataFrame([(10, "G1", "B1", None), (10, "G2", "B1", None),
                        (30, "B", "B", None), (30, "C", "B", None)],
                       columns=sb.COLUMNS["bga"])
    return sb.normalize(xw), sb.normalize(gens), sb.normalize(bga)


def published(xw, gens, bga, sp_units=None):
    """A stand-in for the published table, built with the rebuild itself."""
    unique, _ = sb.unique_crosswalk(xw)
    units = sp_units if sp_units is not None else (
        unique[unique["emissions_unit_id_epa"].notna()][["plant_id_eia", "emissions_unit_id_epa"]]
        .drop_duplicates())
    d, _ = sb.augment(unique, gens, units, bga)
    base = sb.collapse(d)
    labels, _, _ = sb.components(base)
    sp = base[["plant_id_eia", "plant_id_epa", "unit_id_pudl", "emissions_unit_id_epa",
               "generator_id"]].copy()
    sp["subplant_id"] = pd.array([x + 1 for x in labels], dtype="Int64")
    return sb.normalize(sp[sb.COLUMNS["sp"]])


@unittest.skipUnless(HAVE, "needs pandas and networkx")
class RebuildTests(unittest.TestCase):
    def test_unique_drops_2018_conflict(self):
        xw, _, _ = frames()
        unique, dropped = sb.unique_crosswalk(xw)
        self.assertEqual(dropped, 1)
        self.assertNotIn(41, set(unique["plant_id_eia"].astype(int)))
        # the 2022 duplicate of plant 20 is gone too
        self.assertEqual(len(unique[unique["plant_id_eia"] == 20]), 2)

    def test_rebuild_matches_itself(self):
        xw, gens, bga = frames()
        sp = published(xw, gens, bga)
        m, _ = sb.measure(xw, sp, bga, gens)
        self.assertEqual(m["rebuild_plants_differing"], 0)
        self.assertEqual(m["rebuild_rows"], m["published_rows"])
        self.assertTrue(sb.score(m)["G1"])

    def test_gate_catches_a_different_partition(self):
        xw, gens, bga = frames()
        sp = published(xw, gens, bga)
        sp.loc[sp["plant_id_eia"] == 30, "subplant_id"] = 7  # merge plant 30's two subplants
        m, _ = sb.measure(xw, sp, bga, gens)
        self.assertEqual(m["rebuild_plants_differing"], 1)

    def test_labels_are_ignored(self):
        xw, gens, bga = frames()
        sp = published(xw, gens, bga)
        sp["subplant_id"] = sp["subplant_id"] + 100
        m, _ = sb.measure(xw, sp, bga, gens)
        self.assertEqual(m["rebuild_plants_differing"], 0)


@unittest.skipUnless(HAVE, "needs pandas and networkx")
class StepTests(unittest.TestCase):
    def setUp(self):
        self.xw, self.gens, self.bga = frames()
        self.sp = published(self.xw, self.gens, self.bga)
        self.m, self.detail = sb.measure(self.xw, self.sp, self.bga, self.gens)

    def test_step1_extra_row_and_repeated_pair(self):
        s1 = self.m["step1"]
        self.assertEqual(s1["extra_rows"], 1)  # plant 20 HRSG1 + DB1
        self.assertEqual(s1["rows_in_repeated_pairs"], 2)
        self.assertEqual(s1["extra_rows_plants"], 1)
        self.assertGreater(s1["null_boiler_rows"], 0)  # generator C has no crosswalk boiler

    def test_step2_xw_joins_shared_boiler(self):
        xw = self.m["xw"]
        self.assertEqual(xw["plants_changed"], 1)
        self.assertEqual(self.detail["xw"]["rows"][0]["plant_id_eia"], 10)
        self.assertEqual(xw["subplants_merged_away"], 1)
        self.assertEqual(xw["bridging_boilers"], 1)
        self.assertEqual(self.detail["xw"]["bridges"][0]["boiler_id"], "B1")

    def test_step2_bga_adds_generator_c(self):
        both = self.m["xw_bga"]
        self.assertEqual(both["plants_changed"], 2)  # plants 10 and 30
        plants = [r["plant_id_eia"] for r in self.detail["xw_bga"]["rows"]]
        self.assertEqual(plants, [10, 30])

    def test_unit_id_pudl_already_links(self):
        bga = self.bga.copy()
        bga["unit_id_pudl"] = pd.array([1, 1, 2, 2], dtype="Int64")
        sp = published(self.xw, self.gens, bga)
        m, _ = sb.measure(self.xw, sp, bga, self.gens)
        self.assertEqual(m["xw"]["plants_changed"], 0)
        self.assertEqual(m["xw_bga"]["plants_changed"], 0)

    def test_manual_plant_is_one_subplant(self):
        d = sb.normalize(pd.DataFrame({
            "plant_id_eia": [1391, 1391], "plant_id_epa": [1391, 1391],
            "emissions_unit_id_epa": ["a", "b"], "generator_id": ["a", "b"],
            "unit_id_pudl": [None, None]}))
        labels, _, _ = sb.components(d)
        self.assertNotEqual(labels[0], labels[1])
        self.assertEqual(sb.with_manual(d, labels), ["manual", "manual"])

    def test_null_ids_never_merge(self):
        d = sb.normalize(pd.DataFrame({
            "plant_id_eia": [5, 5], "plant_id_epa": [5, 5],
            "emissions_unit_id_epa": ["u1", "u2"], "generator_id": [None, None],
            "unit_id_pudl": [None, None]}))
        labels, _, _ = sb.components(d)
        self.assertNotEqual(labels[0], labels[1])

    def test_scores(self):
        m = {"rebuild_plant_share_identical": 0.995, "rebuild_rows": 1000, "published_rows": 1005,
             "plants_with_crosswalk_match": 1000,
             "xw": {"plants_changed": 3}, "xw_bga": {"plants_changed": 8},
             "step1": {"extra_rows": 10, "null_boiler_share": 0.7}}
        s = sb.score(m)
        self.assertEqual(s, {"G1": True, "P1": True, "P2": True, "P3": True, "P4": True,
                             "P5": True})
        m["xw"]["plants_changed"] = 20
        m["step1"]["extra_rows"] = 9
        s = sb.score(m)
        self.assertFalse(s["P2"])
        self.assertFalse(s["P4"])
        m["rebuild_rows"] = 1020
        self.assertFalse(sb.score(m)["G1"])


if __name__ == "__main__":
    unittest.main()
