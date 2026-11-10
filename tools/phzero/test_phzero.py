"""Unit tests for phzero.py on made-up rows (no download, no polars).

Apache-2.0. MV2 of Munim, Inc. (made with AI agents working in MV2's name)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import phzero as P  # noqa: E402

ROWS = [
    ("r1", "1975-01-01", "100", "PEOPLES GAS CO", "PA"),
    ("r2", "1980-01-01", "0", "Peoples Gas Co", "PA"),        # zero; exact match only earlier
    ("r3", "1981-01-01", "200", "City Gas", "OH"),
    ("r4", "1982-01-01", "200", "City Gas", "OH"),
    ("r5", "1983-01-01", "300", "City Gas", "KY"),            # same name, another id
    ("r6", "1984-01-01", None, "City Gas Company", " ky "),   # null id; state tells them apart
    ("r7", "1985-01-01", "0", "Lone Gas Inc", "TX"),          # zero; no match at all
    ("r8", "2000-01-01", "0.0", "Late Gas", "NM"),            # zero; a later exact match
    ("r9", "2001-01-01", "400", "LATE GAS", "NM"),
    ("r10", "2024-01-01", "500", "Peoples Gas Company", "PA"),
]

CLEAN = [
    ("a", "1980-01-01", "7", "Gas One", "OH"),
    ("b", "1981-01-01", "7", "GAS ONE", "OH"),
    ("c", "1982-01-01", "7", "Gas One, Inc.", "OH"),
]


def study(rows=ROWS):
    st = P.Study()
    for row in rows:
        st.add(row)
    return st


def idxs(st):
    return {w: P.index(st.rows, w) for w in P.RULES}


class ConstantTests(unittest.TestCase):
    def test_constants(self):
        self.assertEqual(P.VERSION, "0.1.0")
        self.assertEqual(P.RULES, ("exact", "norm", "norm_state"))
        self.assertEqual(P.EARLY, 1990)
        self.assertEqual(len(P.STOP), 11)
        self.assertTrue(P.URL.endswith("/nightly/core_phmsagas__yearly_distribution_operators.parquet"))


class HelperTests(unittest.TestCase):
    def test_parse_id(self):
        self.assertEqual(P.parse_id(None), (None, "null"))
        self.assertEqual(P.parse_id("x"), (None, "null"))
        self.assertEqual(P.parse_id(float("nan")), (None, "null"))
        self.assertEqual(P.parse_id("0"), (0, "zero"))
        self.assertEqual(P.parse_id("0.0"), (0, "zero"))
        self.assertEqual(P.parse_id("123"), (123, "id"))
        self.assertEqual(P.parse_id("123.0"), (123, "id"))

    def test_keys(self):
        self.assertEqual(P.exact_key("PEOPLES GAS CO"), "Peoples Gas Co")
        self.assertEqual(P.exact_key("peoples gas co"), "Peoples Gas Co")
        self.assertIsNone(P.exact_key("  "))
        self.assertIsNone(P.exact_key(None))
        self.assertEqual(P.norm_key("The Gas Co., Inc."), "gas")
        self.assertEqual(P.norm_key("Gas Company"), "gas")
        self.assertEqual(P.norm_key("A & B Gas"), "a and b gas")
        self.assertEqual(P.norm_key("City of York"), "city york")
        self.assertIsNone(P.norm_key("Inc"))
        self.assertIsNone(P.norm_key("  "))
        self.assertIsNone(P.norm_key(None))
        self.assertEqual(P.state_key(" ky "), "KY")
        self.assertIsNone(P.state_key(" "))
        self.assertEqual(P.year("1980-01-01"), 1980)
        self.assertEqual(P.year(None), 0)

    def test_share(self):
        self.assertIsNone(P.share(1, 0))
        self.assertEqual(P.share(-1, 4), -0.25)


class StudyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.st = study()
        cls.ix = idxs(cls.st)

    def test_counts(self):
        st = self.st
        self.assertEqual(len(st.rows), 10)
        self.assertEqual(st.kinds, {"id": 6, "zero": 3, "null": 1})
        self.assertEqual(st.zeros(), 4)
        self.assertEqual(st.zero_by_year, {1980: 1, 1984: 1, 1985: 1, 2000: 1})
        self.assertEqual(st.rows[5][P.STATE], "KY")

    def test_index(self):
        ix = self.ix
        self.assertEqual(ix["exact"]["City Gas"], [(1981, 200), (1982, 200), (1983, 300)])
        self.assertEqual(ix["exact"]["Late Gas"], [(2001, 400)])
        self.assertNotIn("Lone Gas Inc", ix["exact"])
        self.assertEqual(ix["norm"]["peoples gas"], [(1975, 100), (2024, 500)])
        self.assertEqual(ix["norm_state"][("city gas", "KY")], [(1983, 300)])
        self.assertEqual(len(ix["exact"]), 4)
        self.assertEqual(len(ix["norm"]), 3)
        self.assertEqual(len(ix["norm_state"]), 4)

    def test_zero_rows(self):
        zc, out = P.zero_rows(self.st.rows, self.ix)
        self.assertEqual((zc["zero_or_null"], zc["zero"], zc["null"]), (4, 3, 1))
        self.assertEqual((zc["before_1990"], zc["in_1976_1983"]), (3, 1))
        self.assertEqual((zc["exact|any"], zc["exact|unique"]), (2, 2))
        self.assertEqual((zc["norm|any"], zc["norm|unique"]), (3, 1))
        self.assertEqual((zc["norm_state|any"], zc["norm_state|unique"]), (3, 2))
        self.assertEqual((zc["exact|when_later"], zc["exact|when_earlier"],
                          zc["exact|when_none"], zc["exact|when_same_year"]), (1, 1, 2, 0))
        self.assertEqual((zc["proposal|exact"], zc["proposal|norm_state"], zc["proposal|norm"]),
                         (2, 1, 0))
        self.assertEqual(out, [
            [1980, "r2", "zero", "Peoples Gas Co", "PA", "100", "earlier", "100 500", "100 500",
             100, "exact"],
            [1984, "r6", "null", "City Gas Company", "KY", "", "none", "200 300", "300", 300,
             "norm_state"],
            [1985, "r7", "zero", "Lone Gas Inc", "TX", "", "none", "", "", "", ""],
            [2000, "r8", "zero", "Late Gas", "NM", "400", "later", "400", "400", 400, "exact"]])

    def test_loo(self):
        c, misses = P.loo(self.st.rows, self.ix)
        self.assertEqual((c["pudl_later|all|predicted"], c["pudl_later|all|correct"]), (2, 1))
        self.assertEqual((c["pudl_later|early|predicted"], c["pudl_later|early|correct"]), (2, 1))
        self.assertEqual((c["exact_earlier|all|predicted"], c["exact_earlier|all|correct"]),
                         (2, 1))
        self.assertEqual((c["unique_exact|all|predicted"], c["unique_exact|all|correct"]), (1, 0))
        self.assertEqual((c["unique_norm|all|predicted"], c["unique_norm|all|correct"]), (3, 0))
        self.assertEqual((c["unique_norm|early|predicted"], c["unique_norm|early|correct"]),
                         (2, 0))
        self.assertEqual((c["unique_norm_state|all|predicted"],
                          c["unique_norm_state|all|correct"]), (4, 2))
        self.assertEqual((c["unique_norm_state|early|predicted"],
                          c["unique_norm_state|early|correct"]), (3, 2))
        self.assertEqual(c["pudl_later|all|tie"], 0)
        self.assertEqual(P.precision(c, "pudl_later", "all"), 0.5)
        self.assertEqual(P.precision(c, "unique_norm", "early"), 0.0)
        self.assertEqual(len(misses), 8)
        self.assertEqual(misses[0], ["unique_norm", 1975, "r1", "PEOPLES GAS CO", "PA", 100, "500"])
        self.assertEqual(misses[2], ["pudl_later", 1982, "r4", "City Gas", "OH", 200, "300"])
        self.assertEqual(misses[3], ["exact_earlier", 1983, "r5", "City Gas", "KY", 300, "200"])
        self.assertEqual([m[0] for m in misses],
                         ["unique_norm", "unique_norm_state", "pudl_later", "exact_earlier",
                          "unique_exact", "unique_norm", "unique_norm", "unique_norm_state"])

    def test_tie(self):
        rows = [("x", "1980-01-01", "1", "Twin Gas", "OH"),
                ("y", "1981-01-01", "1", "Twin Gas", "OH"),
                ("z", "1981-01-01", "2", "Twin Gas", "IN")]
        st = study(rows)
        c, misses = P.loo(st.rows, idxs(st))
        self.assertEqual((c["pudl_later|all|predicted"], c["pudl_later|all|tie"],
                          c["pudl_later|all|correct"]), (1, 1, 0))
        self.assertEqual(misses[0], ["pudl_later", 1980, "x", "Twin Gas", "OH", 1, "1 2"])

    def test_multi_id_names(self):
        self.assertEqual(P.multi_id_names(self.ix), [["City Gas", 2, "200 300", 3, 1981, 1983]])

    def test_score(self):
        m, scores, tables = P.score(self.st)
        sh = m["shares"]
        self.assertEqual((sh["before_1990"], sh["in_1976_1983"], sh["exact_later"]),
                         (0.75, 0.25, 0.25))
        self.assertEqual((sh["exact_unique"], sh["norm_gain_over_exact"]), (0.5, -0.25))
        self.assertEqual(m["precision"]["unique_norm_state|early"], 0.666667)
        self.assertEqual(m["multi_id_exact_names"], 1)
        self.assertEqual(m["zeros_by_year"], {"1980": 1, "1984": 1, "1985": 1, "2000": 1})
        self.assertEqual(scores, {"P1": False, "P2": False, "P3": False, "P4": True,
                                  "P5": False, "P6": False, "P7": False, "P8": False})
        self.assertEqual(sorted(tables), ["phzero-loo-misses.csv", "phzero-multi-id-names.csv",
                                          "phzero-zero-rows.csv"])
        self.assertEqual(len(tables["phzero-zero-rows.csv"][1]), 4)

    def test_clean(self):
        st = study(CLEAN)
        c, misses = P.loo(st.rows, idxs(st))
        self.assertEqual(misses, [])
        self.assertEqual((c["pudl_later|early|predicted"], c["pudl_later|early|correct"]), (1, 1))
        self.assertEqual((c["exact_earlier|all|predicted"], c["exact_earlier|all|correct"]),
                         (1, 1))
        self.assertEqual((c["unique_exact|all|predicted"], c["unique_exact|all|correct"]), (2, 2))
        self.assertEqual((c["unique_norm|early|predicted"], c["unique_norm|early|correct"]), (3, 3))
        self.assertEqual(P.precision(c, "unique_norm", "early"), 1.0)

    def test_gates(self):
        info = {"bytes": 10, "missing_cols": []}
        g, gm = P.gates(info, self.st)
        self.assertEqual(g, {"G1": True, "G2": False, "G3": False})
        g, _ = P.gates(info, self.st, min_rows=5, min_zeros=1)
        self.assertEqual(g, {"G1": True, "G2": True, "G3": True})
        self.assertFalse(P.gates({"bytes": 10, "missing_cols": ["report_id"]}, self.st)[0]["G1"])
        self.assertEqual(gm["years"], [1975, 2024])
        self.assertEqual(gm["kinds"], {"id": 6, "null": 1, "zero": 3})


if __name__ == "__main__":
    unittest.main()
