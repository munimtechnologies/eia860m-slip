"""Unit tests for xwstale.py on made-up rows (no downloads).

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import copy
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import xwstale as xs  # noqa: E402


def gen(pm, ret=None, status="OP"):
    return {"pm": pm, "status": status, "ret": ret}


def unit(year, plant=7, u="1", reason="absent"):
    return {"year": year, "plant": plant, "plant_epa": plant, "unit": u, "reason": reason}


class ConstantTests(unittest.TestCase):
    def test_constants(self):
        self.assertEqual(xs.VERSION, "0.1.0")
        self.assertEqual(xs.COMB, ("CA", "CS", "CT", "GT", "IC", "ST"))
        self.assertEqual(xs.REASONS_IN, ("absent", "not_operating"))
        self.assertEqual((xs.POP_ROWS, xs.POP_NEWEST, xs.NEWEST), (317, 65, 2024))
        self.assertEqual(xs.ZIMMER, (2024, 6019, "1"))
        self.assertEqual(xs.ZIMMER_YEAR, 2022)
        self.assertEqual((xs.P1_SHARE, xs.P2_SHARE, xs.P3_MAX), (0.6, 0.9, 10))
        self.assertEqual((xs.P4_PLANTS, xs.P4_UNITS, xs.P4_YEAR), ((563, 2866, 55243), 35, 2023))
        self.assertEqual((xs.P5_YEARS, xs.P5_SHARE), ((2019, 2020, 2021, 2022, 2023), 0.5))
        self.assertIn("generator_retirement_date", xs.GEN_COLS)
        self.assertTrue(xs.POP_URL.endswith("/main/data/xwgap-units-2018-2024.csv"))


class HelperTests(unittest.TestCase):
    def test_ids_and_dates(self):
        self.assertEqual(xs.gid(" st "), "ST")
        self.assertEqual(xs.gid(1.0), "1")
        self.assertEqual(xs.gid(float("nan")), "")
        self.assertEqual(xs.pint("6019.0"), 6019)
        self.assertIsNone(xs.pint(""))
        self.assertEqual(xs.iso("2022-05-31 00:00:00"), "2022-05-31")
        self.assertIsNone(xs.iso(None))
        self.assertIsNone(xs.iso(""))
        self.assertIsNone(xs.iso(float("nan")))
        self.assertIsNone(xs.iso("None"))

    def test_read_population(self):
        text = ("report_year,plant_id_epa,emissions_unit_id_epa,plant_id_eia,reason\n"
                "2024,6019,1,6019,absent\n"
                "2024,356,5,356,not_operating\n"
                "2024,315,CT1,315,all_linked\n")
        n, pop = xs.read_population(text)
        self.assertEqual(n, 3)
        self.assertEqual(pop, [
            {"year": 2024, "plant": 6019, "plant_epa": 6019, "unit": "1", "reason": "absent"},
            {"year": 2024, "plant": 356, "plant_epa": 356, "unit": "5",
             "reason": "not_operating"}])

    def test_index_gens(self):
        rows = [
            {"plant_id_eia": 7, "generator_id": "1", "report_date": "2022-01-01",
             "prime_mover_code": "ST", "operational_status_code": None,
             "generator_retirement_date": None},
            {"plant_id_eia": 7, "generator_id": "1", "report_date": "2022-01-01",
             "prime_mover_code": "ST", "operational_status_code": "RE",
             "generator_retirement_date": "2022-05-31"},
            {"plant_id_eia": 7, "generator_id": "1", "report_date": "2022-01-01",
             "prime_mover_code": "GT", "operational_status_code": "OP",
             "generator_retirement_date": "2030-01-01"},
            {"plant_id_eia": 7, "generator_id": " 2 ", "report_date": "2021-01-01",
             "prime_mover_code": "gt", "operational_status_code": "op",
             "generator_retirement_date": None},
            {"plant_id_eia": None, "generator_id": "3", "report_date": "2021-01-01"},
            {"plant_id_eia": 8, "generator_id": "3", "report_date": None},
        ]
        got = xs.index_gens(rows)
        self.assertEqual(got, {7: {2022: {"1": gen("ST", "2022-05-31", "RE")},
                                   2021: {"2": gen("GT", None, "OP")}}})


class ClassifyTests(unittest.TestCase):
    def test_never_listed(self):
        r = xs.classify(unit(2024), {})
        self.assertEqual((r["class"], r["last_listed"], r["listed_later"]),
                         ("never_listed", None, False))
        r = xs.classify(unit(2024), {2025: {"1": gen("CT")}})
        self.assertEqual((r["class"], r["listed_later"]), ("never_listed", True))

    def test_retired_before_uses_last_listing(self):
        py = {2021: {"1": gen("ST")},
              2022: {"1": gen("ST", "2022-05-31", "RE"), "PV1": gen("PV")}}
        r = xs.classify(unit(2024), py)
        self.assertEqual(r["class"], "retired_before")
        self.assertEqual((r["last_listed"], r["retired_year"], r["combustion"], r["cause"]),
                         (2022, 2022, 1, ""))
        self.assertFalse(r["listed_later"])
        self.assertEqual(r["unit"], "1")

    def test_fallback_to_older_row(self):
        py = {2021: {"1": gen("ST", "2021-12-01", "RE")},
              2022: {"1": gen("ST", None, "RE"), "2": gen("GT", "2022-03-01", "RE")}}
        r = xs.classify(unit(2023), py)
        self.assertEqual((r["class"], r["retired_year"]), ("retired_before", 2022))
        py[2022]["2"] = gen("GT", "2020-03-01", "RE")
        r = xs.classify(unit(2023), py)
        self.assertEqual((r["class"], r["retired_year"]), ("retired_before", 2021))

    def test_later_listing_not_used(self):
        py = {2020: {"1": gen("ST")}, 2025: {"1": gen("ST", "2019-01-01", "RE")}}
        r = xs.classify(unit(2023), py)
        self.assertEqual((r["class"], r["cause"], r["last_listed"], r["listed_later"]),
                         ("other", "undated", 2020, True))

    def test_retired_in_year(self):
        py = {2022: {"1": gen("ST", "2022-05-31", "RE"), "2": gen("CT", "2021-01-01", "RE")}}
        r = xs.classify(unit(2022), py)
        self.assertEqual((r["class"], r["retired_year"]), ("retired_in_year", 2022))

    def test_after_year(self):
        r = xs.classify(unit(2021), {2021: {"1": gen("GT", "2023-01-01")}})
        self.assertEqual((r["class"], r["cause"], r["after_year"], r["retired_year"]),
                         ("other", "after_year", 1, 2023))

    def test_undated(self):
        py = {2024: {"5": gen("ST", None, ""), "6": gen("ST", "2020-01-01", "RE")}}
        r = xs.classify(unit(2024, u="5", reason="not_operating"), py)
        self.assertEqual((r["class"], r["cause"], r["undated"], r["combustion"]),
                         ("other", "undated", 1, 2))
        self.assertIsNone(r["retired_year"])

    def test_no_combustion(self):
        r = xs.classify(unit(2020), {2020: {"W1": gen("WT")}})
        self.assertEqual((r["class"], r["cause"], r["combustion"]), ("other", "no_combustion", 0))


class SummaryTests(unittest.TestCase):
    def test_summarize(self):
        us = [xs.classify(unit(2024, plant=1), {2022: {"1": gen("ST", "2022-05-01")}}),
              xs.classify(unit(2024, plant=2), {2020: {"1": gen("ST", "2020-05-01")}}),
              xs.classify(unit(2024, plant=3), {}),
              xs.classify(unit(2024, plant=3, u="2"), {2026: {"1": gen("CT")}}),
              xs.classify(unit(2024, plant=4), {2024: {"1": gen("CT")}})]
        c = xs.summarize(us)
        self.assertEqual(c, {"n": 5, "never_listed": 2, "retired_before": 2,
                             "retired_in_year": 0, "other": 1,
                             "retired_before_in_window": 1, "listed_later": 1, "plants": 4})


def good_res():
    summary = {str(y): {"n": 10, "retired_before": 5} for y in xs.P5_YEARS}
    summary["2024"] = {"n": 65, "retired_before": 40, "retired_before_in_window": 36,
                       "never_listed": 10}
    return {"g1": {"missing_cols": [], "years": list(range(2001, 2025))},
            "g2": {"rows": 317, "newest_units": 65},
            "g3": {"class": "retired_before", "retired_year": 2022},
            "summary": summary,
            "p4_units": [{"class": "retired_before", "retired_year": 2023}] * 35}


class ScoreTests(unittest.TestCase):
    def test_all_hold(self):
        self.assertEqual(xs.score(good_res()), {"G1": True, "G2": True, "G3": True, "P1": True,
                                                "P2": True, "P3": True, "P4": True, "P5": True})

    def test_gates(self):
        self.assertEqual(xs.score({}), {})
        r = good_res()
        r["g1"]["missing_cols"] = ["generator_retirement_date"]
        self.assertEqual(xs.score(r), {"G1": False})
        r = good_res()
        r["g1"]["years"] = list(range(2001, 2024))
        self.assertEqual(xs.score(r), {"G1": False})
        r = good_res()
        r["g2"]["rows"] = 316
        self.assertEqual(xs.score(r), {"G1": True, "G2": False})
        r = good_res()
        r["g2"]["newest_units"] = 64
        self.assertEqual(xs.score(r), {"G1": True, "G2": False})
        r = good_res()
        r["g3"] = {"class": "retired_before", "retired_year": 2021}
        self.assertEqual(xs.score(r), {"G1": True, "G2": True, "G3": False})
        r = good_res()
        r["g3"] = {"found": 0}
        self.assertEqual(xs.score(r), {"G1": True, "G2": True, "G3": False})

    def test_bars(self):
        def one(change, key):
            r = good_res()
            change(r)
            return xs.score(r)[key]

        self.assertTrue(one(lambda r: r["summary"]["2024"].update(retired_before=39), "P1"))
        self.assertFalse(one(lambda r: r["summary"]["2024"].update(retired_before=38), "P1"))
        self.assertFalse(one(lambda r: r["summary"]["2024"].update(
            retired_before_in_window=35), "P2"))
        self.assertFalse(one(lambda r: r["summary"]["2024"].update(
            retired_before=0, retired_before_in_window=0), "P2"))
        self.assertFalse(one(lambda r: r["summary"]["2024"].update(never_listed=11), "P3"))
        self.assertFalse(one(lambda r: r.update(p4_units=r["p4_units"][:34]), "P4"))

        def p4_off(r):
            r["p4_units"] = copy.deepcopy(r["p4_units"])
            r["p4_units"][0]["retired_year"] = 2022
        self.assertFalse(one(p4_off, "P4"))
        self.assertFalse(one(lambda r: r["summary"]["2021"].update(retired_before=4), "P5"))
        self.assertFalse(one(lambda r: r["summary"].pop("2019"), "P5"))


if __name__ == "__main__":
    unittest.main()
