"""Unit tests for phdecade.py on made-up rows (no data, no polars needed).

Apache-2.0. MV2 of Munim, Inc. (made with AI agents)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import phdecade  # noqa: E402


def row(year, rid, op, dec, mains, services, com="natural_gas", state="IA"):
    return {"year": year, "report_id": rid, "operator_id_phmsa": op, "commodity": com,
            "operating_state": state, "install_decade": dec, "mains_miles": mains,
            "services": services}


def rows():
    return [
        # A (op 1): an old bucket loses 2 miles, the current one gains 2
        row(2015, "a15", 1, "2010s", 10, 5), row(2015, "a15", 1, "1950s", 100, 50),
        row(2015, "a15", 1, "unknown_decade", 4, 0),
        row(2016, "a16", 1, "2010s", 12, 6), row(2016, "a16", 1, "1950s", 98, 50),
        row(2016, "a16", 1, "unknown_decade", 4, 0),
        # B (op 2): only the current bucket changes
        row(2015, "b15", 2, "2010s", 5, 1), row(2015, "b15", 2, "1990s", 50, 20),
        row(2016, "b16", 2, "2010s", 6, 2), row(2016, "b16", 2, "1990s", 50, 20),
        # C (op 3): nothing changes
        row(2016, "c16", 3, "1970s", 7, 3), row(2017, "c17", 3, "1970s", 7, 3),
        # D (op 4): two reports in 2016, so no pair uses 2016
        row(2015, "d15", 4, "1980s", 1, 0), row(2016, "d16a", 4, "1980s", 1, 0),
        row(2016, "d16b", 4, "1980s", 2, 0), row(2017, "d17", 4, "1980s", 3, 0),
        # E (op 5): 2019 -> 2020, small old-bucket changes and an old services change
        row(2019, "e19", 5, "2010s", 20, 10), row(2019, "e19", 5, "pre_1940", 200, 100),
        row(2020, "e20", 5, "2010s", 20.5, 10), row(2020, "e20", 5, "2020s", 1, 1),
        row(2020, "e20", 5, "pre_1940", 199.5, 98),
        # F (op 1, propane): another commodity is another key; one year only
        row(2015, "f15", 1, "1950s", 3, 3, com="propane_gas"),
        # outside the window
        row(2014, "a14", 1, "1950s", 101, 50), row(None, "x", 9, "1950s", 1, 1),
    ]


class ConstantTests(unittest.TestCase):
    def test_constants(self):
        self.assertEqual(phdecade.TABLE, "core_phmsagas__yearly_distribution_by_install_decade")
        self.assertTrue(phdecade.URL.endswith(phdecade.TABLE + ".parquet"))
        self.assertEqual(phdecade.OLD4, ("pre_1940", "1940s", "1950s", "1960s"))
        self.assertEqual((phdecade.FIRST_T, phdecade.LAST_T1), (2015, 2025))
        self.assertEqual((phdecade.MAINS_TOL, phdecade.SERVICES_TOL, phdecade.MATERIAL_MILES,
                          phdecade.MATERIAL_SHARE), (0.001, 0.0, 1.0, 0.01))
        self.assertEqual((phdecade.G2_MIN_PAIRS, phdecade.G2_MIN_PER_YEAR, phdecade.G2_MIN_YEARS),
                         (2000, 100, 8))
        self.assertEqual((phdecade.P1_MIN, phdecade.P2_MIN, phdecade.P4_MIN, phdecade.P5_MIN_YEARS,
                          phdecade.P6_MIN), (0.40, 0.80, 0.25, 8, 0.40))


class HelperTests(unittest.TestCase):
    def test_helpers(self):
        self.assertEqual(phdecade.key(None), phdecade.NULL)
        self.assertEqual(phdecade.key(float("nan")), phdecade.NULL)
        self.assertEqual(phdecade.key(12), "12")
        self.assertEqual(phdecade.fnum(None), 0.0)
        self.assertEqual(phdecade.fnum(float("nan")), 0.0)
        self.assertEqual(phdecade.fnum("2.5"), 2.5)
        self.assertEqual(phdecade.share(1, 4), 0.25)
        self.assertIsNone(phdecade.share(1, 0))

    def test_decade_of(self):
        self.assertEqual(phdecade.decade_of(1939), "pre_1940")
        self.assertEqual(phdecade.decade_of(1940), "1940s")
        self.assertEqual(phdecade.decade_of(2019), "2010s")
        self.assertEqual(phdecade.decade_of(2020), "2020s")
        self.assertEqual(phdecade.decade_of(2025), "2020s")


class MatchTests(unittest.TestCase):
    def test_build_and_match(self):
        idx = phdecade.build(rows())
        self.assertEqual(len(idx), 6)
        self.assertNotIn(2014, idx[("1", "natural_gas", "IA")])
        self.assertEqual(idx[("1", "natural_gas", "IA")][2015]["a15"]["1950s"], (100.0, 50.0))
        pairs, amb = phdecade.match(idx)
        self.assertEqual(amb, {"2016": 1})
        self.assertEqual([(p["t"], p["key"][0]) for p in pairs],
                         [(2015, "1"), (2015, "2"), (2016, "3"), (2019, "5")])

    def test_nulls(self):
        idx = phdecade.build([row(2015, 7, 8, None, None, float("nan"))])
        self.assertEqual(idx[("8", "natural_gas", "IA")][2015]["7"], {phdecade.NULL: (0.0, 0.0)})


class StudyTests(unittest.TestCase):
    def make(self):
        pairs, _ = phdecade.match(phdecade.build(rows()))
        return phdecade.Study(pairs)

    def test_compare(self):
        st = self.make()
        a, b, c, e = st.c
        self.assertEqual((a["cur"], a["m0_total"], a["m1_total"], a["cur_dm"], a["old_net_dm"],
                          a["old_gross_dm"], a["old_m"], a["old_m_material"], a["old_s"],
                          a["any_change"]),
                         ("2010s", 114.0, 114.0, 2.0, -2.0, 2.0, 1, 1, 0, True))
        self.assertEqual((b["old_m"], b["cur_dm"], b["m0_total"], b["m1_total"]),
                         (0, 1.0, 55.0, 56.0))
        self.assertEqual((c["t"], c["any_change"], c["old_m"]), (2016, False, 0))
        self.assertEqual((e["cur"], e["m0_total"], e["m1_total"], e["cur_dm"], e["old_net_dm"],
                          e["old_gross_dm"], e["old_m"], e["old_m_material"], e["old_s"]),
                         ("2020s", 220.0, 221.0, 1.0, 0.0, 1.0, 2, 0, 1))

    def test_score(self):
        m, s = self.make().score()
        self.assertEqual((m["pairs"], m["pairs_old_mains_changed"], m["share_old_mains_changed"],
                          m["pairs_old_mains_material"], m["pairs_old_services_changed"],
                          m["pairs_static"]), (4, 2, 0.5, 1, 1, 1))
        self.assertEqual((m["miles_t_all"], m["miles_t_old_changed"]), (396.0, 334.0))
        self.assertEqual(m["share_miles_old_changed"], round(334 / 396, 6))
        self.assertEqual((m["net_old_dm"], m["gross_old_dm"], m["net_cur_dm"], m["gross_cur_dm"],
                          m["ratio_gross_old_to_cur"], m["pairs_cur_negative"],
                          m["net_total_dm"]), (-2.0, 3.0, 4.0, 4.0, 0.75, 0, 2.0))
        self.assertEqual(m["old_by_decade"]["1950s"], [1, 1, 1, 0, -2.0, 2.0, 0.0])
        self.assertEqual(m["old_by_decade"]["2010s"], [1, 1, 1, 0, 0.5, 0.5, 0.0])
        self.assertEqual(m["old_by_decade"]["pre_1940"], [1, 1, 1, 1, -0.5, 0.5, -2.0])
        self.assertEqual(sorted(m["old_by_decade"]),
                         ["1950s", "1970s", "1990s", "2010s", "pre_1940", "unknown_decade"])
        self.assertEqual(m["old4_net_dm_by_t"], {"2015": -2.0, "2019": -0.5})
        self.assertEqual(m["years_old4_net_negative"], 2)
        self.assertEqual(s, {"P1": True, "P2": True, "P3": True, "P4": True, "P5": False,
                             "P6": False})

    def test_by_t_decade_and_top(self):
        st = self.make()
        self.assertEqual(st.by_t_decade()[(2015, "2010s")], [True, 2, 2, 2, 2, 3.0, 3.0, 2.0])
        top = st.top_old()
        self.assertEqual(len(top), 3)
        self.assertEqual((top[0][0], top[0][1], top[0][3]), (2.0, 2015, "1950s"))
        self.assertEqual([x[3] for x in top[1:]], ["2010s", "pre_1940"])

    def test_gates(self):
        st = self.make()
        g, gm = phdecade.gates({"bytes": 10, "missing_cols": []}, st)
        self.assertEqual(g, {"G1": True, "G2": False})
        self.assertEqual(gm["pairs_by_t"], {"2015": 2, "2016": 1, "2019": 1})
        self.assertEqual(gm["years_with_enough_pairs"], 0)
        g, _ = phdecade.gates({"bytes": 10, "missing_cols": ["services"]}, st)
        self.assertFalse(g["G1"])

    def test_current_negative(self):
        pairs, _ = phdecade.match(phdecade.build([row(2015, 1, 6, "2010s", 10, 2),
                                                  row(2016, 2, 6, "2010s", 9, 2)]))
        m, s = phdecade.Study(pairs).score()
        self.assertEqual((m["pairs"], m["pairs_cur_negative"], m["net_cur_dm"], m["pairs_static"]),
                         (1, 1, -1.0, 0))
        self.assertEqual(m["share_miles_old_changed"], 0.0)
        self.assertEqual(m["ratio_gross_old_to_cur"], 0.0)
        self.assertEqual(set(s.values()), {False})

    def test_nothing_to_test(self):
        m, s = phdecade.Study([]).score()
        self.assertEqual(m["pairs"], 0)
        self.assertIsNone(m["share_old_mains_changed"])
        self.assertIsNone(m["ratio_gross_old_to_cur"])
        self.assertEqual(set(s.values()), {False})


if __name__ == "__main__":
    unittest.main()
