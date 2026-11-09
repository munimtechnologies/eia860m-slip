"""Unit tests for xwtz.py on made-up rows. Reads no outside data.

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import xwtz as xt  # noqa: E402

# Crosswalk: (report_year, plant_id_epa, emissions_unit_id_epa, plant_id_eia)
XW = [
    (2023, 10, "1", 10), (2024, 10, "1", 10),           # plain match
    (2024, 20, "CT1", 21), (2024, 20, "CT2", 21),       # renumbered: EPA 20 is EIA 21
    (2022, 30, "A", 30), (2024, 30, "A", 31),           # one key, two EIA plants (multi)
    (2024, 40, "01", 40),                               # leading-zero unit id
    (2024, None, "X", 1), (2024, 50, "", 50), (2024, 50, "Y", None),  # skipped rows
]
# Entity plants: (plant_id_eia, timezone, state, plant_name_eia)
PLANTS = [
    (10, "America/New_York", "NY", "Ten"),
    (20, "America/Denver", "CO", "Twenty (a different EIA plant)"),
    (21, "America/Chicago", "TX", "Twenty-one"),
    (30, "America/Chicago", "TX", "Thirty"),
    (31, "America/Chicago", "TX", "Thirty-one"),
    (40, None, "", "Forty"), (40, "America/Phoenix", "AZ", "Forty again"),
    (60, float("nan"), "GU", "Sixty"),
    (None, "UTC", "", "bad"),
]
# Ops: (report_year, plant_id_epa, emissions_unit_id_epa, plant_id_eia)
OPS = [
    (2024, 10, "1", 10),     # matched, tz known
    (2024, 20, "CT1", 21),   # matched via renumbering
    (2024, 20, "CT3", 20),   # fallback at a renumbered EPA plant; EIA 20 is in Denver -> tz_diff
    (2024, 30, "A", 30),     # multi key
    (2024, 60, "G1", 60),    # fallback; EIA 60 has no timezone -> no_tz
    (2024, 70, "Z", 70),     # fallback; EIA 70 not in entity -> no_tz
    (2024, 10, "1", 10),     # duplicate unit-year, counted once
    (2023, 10, "1", 21),     # inconsistent with the crosswalk (21 has a timezone)
    (2017, 10, "1", 10),     # outside YEARS
    (2024, None, "Q", 1),    # skipped
]


class HelperTests(unittest.TestCase):
    def test_helpers(self):
        self.assertEqual(xt.pint("55243"), 55243)
        self.assertEqual(xt.pint(7.0), 7)
        self.assertIsNone(xt.pint(float("nan")))
        self.assertIsNone(xt.pint(""))
        self.assertEqual(xt.uid(" ct1 "), "ct1")
        self.assertEqual(xt.uid(1.0), "1")
        self.assertEqual(xt.uid(None), "")
        self.assertIsNone(xt.tzv(" "))
        self.assertIsNone(xt.tzv(float("nan")))
        self.assertEqual(xt.tzv("America/Chicago"), "America/Chicago")


class BuildTests(unittest.TestCase):
    def test_build_xw(self):
        um, pm, info = xt.build_xw(XW)
        self.assertEqual(um[(20, "CT1")], {21})
        self.assertEqual(um[(30, "A")], {30, 31})
        self.assertEqual(pm[20], {21})
        self.assertEqual((info["rows_used"], info["rows_skipped"], info["unit_keys"],
                          info["multi_keys"], info["leading_zero_keys"],
                          info["renumbered_plants"]), (7, 3, 5, 1, 1, 2))
        self.assertAlmostEqual(info["unique_share"], 0.8)

    def test_build_plants(self):
        p = xt.build_plants(PLANTS)
        self.assertEqual(p[40]["tz"], "America/Phoenix")
        self.assertEqual(p[40]["name"], "Forty")
        self.assertIsNone(p[60]["tz"])
        self.assertNotIn(None, p)
        self.assertEqual(len(p), 7)


class ClassifyTests(unittest.TestCase):
    def setUp(self):
        um, pm, _ = xt.build_xw(XW)
        self.plants = xt.build_plants(PLANTS)
        self.units = xt.classify(OPS, um, pm, self.plants)
        self.by = {(x["year"], x["plant_id_epa"], x["unit"]): x for x in self.units}

    def test_rows(self):
        self.assertEqual(len(self.units), 7)
        m = self.by[(2024, 10, "1")]
        self.assertFalse(m["fallback"] or m["no_tz"] or m["suspicious"] or m["inconsistent"])
        r = self.by[(2024, 20, "CT1")]
        self.assertTrue(r["renumbered"])
        self.assertFalse(r["fallback"])
        s = self.by[(2024, 20, "CT3")]
        self.assertTrue(s["fallback"] and s["suspicious"] and s["tz_diff"])
        self.assertEqual(s["alt"], [21])
        self.assertEqual(s["tz"], "America/Denver")
        self.assertTrue(self.by[(2024, 30, "A")]["multi"])
        self.assertFalse(self.by[(2024, 30, "A")]["inconsistent"])
        g = self.by[(2024, 60, "G1")]
        self.assertTrue(g["no_tz"] and g["in_entity"] and not g["suspicious"])
        z = self.by[(2024, 70, "Z")]
        self.assertTrue(z["no_tz"] and not z["in_entity"])
        self.assertTrue(self.by[(2023, 10, "1")]["inconsistent"])

    def test_summary(self):
        s = xt.summarize(self.units)
        f = s["by_year"]["2024"]
        self.assertEqual((f["units"], f["plants"], f["fallback"], f["multi"], f["inconsistent"],
                          f["no_tz"], f["no_tz_plants"], f["suspicious"], f["tz_diff"],
                          f["not_in_entity"], f["renumbered"]),
                         (6, 5, 3, 1, 0, 2, 2, 1, 1, 1, 1))
        self.assertEqual(s["by_year"]["2023"]["inconsistent"], 1)
        self.assertEqual(s["all_years"]["no_tz_plants"], 2)
        self.assertEqual(s["all_years"]["unit_years"], 7)

    def test_flagged_and_controls(self):
        flagged, n = xt.flagged_plants(self.units)
        self.assertEqual((flagged, n), ([20, 60, 70], 3))
        self.assertEqual(xt.control_plants(self.units, set(flagged)), [10, 30])


def good_res():
    by = {str(y): {"units": 4200, "inconsistent": 0, "no_tz": 0, "suspicious": 0,
                   "tz_diff": 0} for y in xt.YEARS}
    by["2024"].update(suspicious=1)
    by["2019"].update(tz_diff=1)
    return {"g1": {"missing_required": [], "years": list(range(1995, 2025))},
            "xw_info": {"unique_share": 1.0},
            "summary": {"by_year": by, "all_years": {"no_tz_plants": 0}}}


class ScoreTests(unittest.TestCase):
    def test_all_hold(self):
        self.assertEqual(xt.score(good_res()), {"G1": True, "G2": True, "G3": True, "P1": True,
                                                "P2": True, "P3": True, "P4": True,
                                                "P5": True})

    def test_bars(self):
        r = good_res()
        r["summary"]["by_year"]["2024"].update(inconsistent=1, no_tz=6, suspicious=0)
        r["summary"]["by_year"]["2019"]["tz_diff"] = 0
        r["summary"]["all_years"]["no_tz_plants"] = 11
        s = xt.score(r)
        self.assertEqual((s["P1"], s["P2"], s["P3"], s["P4"], s["P5"]),
                         (False, False, False, False, False))
        r = good_res()
        r["summary"]["by_year"]["2024"]["no_tz"] = 5
        r["summary"]["all_years"]["no_tz_plants"] = 10
        s = xt.score(r)
        self.assertTrue(s["P2"] and s["P3"])

    def test_gates(self):
        r = good_res()
        r["g1"]["years"] = list(range(2019, 2025))
        self.assertEqual(xt.score(r), {"G1": False})
        r = good_res()
        r["g1"]["missing_required"] = ["timezone"]
        self.assertEqual(xt.score(r), {"G1": False})
        r = good_res()
        r["summary"]["by_year"]["2024"]["units"] = 4301
        self.assertEqual(xt.score(r), {"G1": True, "G2": False})
        r = good_res()
        r["xw_info"]["unique_share"] = 0.98
        self.assertEqual(xt.score(r), {"G1": True, "G2": True, "G3": False})
        self.assertEqual(xt.score({}), {})


class ConstantTests(unittest.TestCase):
    def test_constants(self):
        self.assertEqual(xt.VERSION, "0.1.0")
        self.assertEqual(xt.YEARS, tuple(range(2018, 2025)))
        self.assertEqual((xt.FOCUS, xt.G2_MIN, xt.G2_MAX, xt.G3_UNIQUE), (2024, 4100, 4300, 0.99))
        self.assertEqual((xt.P1_MAX, xt.P2_MAX_UNITS, xt.P3_MAX_PLANTS, xt.P4_MIN_UNITS,
                          xt.P5_MIN_UNITS), (0, 5, 10, 1, 1))
        self.assertEqual((xt.VERIFY_MAX_PLANTS, xt.VERIFY_FROM_YEAR, xt.CONTROLS), (40, 2018, 3))


if __name__ == "__main__":
    unittest.main()
