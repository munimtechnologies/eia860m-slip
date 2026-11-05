"""Unit tests for step1d.py (pre-registration step1d-1). Standard library only, no network.

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.)."""

import unittest

import step1d as sd

S = "3_1_Generator (generators) match on plant and gen IDs  Step 1"


def row(step, cp, cg, ep, eg, cmw, emw, label=None):
    return {"MATCH_TYPE_GEN": label if label is not None else S + step + ": x",
            "CAMD_PLANT_ID": cp, "CAMD_GENERATOR_ID": cg, "EIA_PLANT_ID": ep,
            "EIA_GENERATOR_ID": eg, "CAMD_NAMEPLATE_CAPACITY": cmw,
            "EIA_NAMEPLATE_CAPACITY": emw}


class ParseTests(unittest.TestCase):
    def test_step_of(self):
        self.assertEqual(sd.step_of(S + "d: Modify IDs; remove leading letters"), "1d")
        self.assertEqual(sd.step_of(S + "a: Exact match"), "1a")
        self.assertEqual(sd.step_of(S + "c: Modify IDs; convert to numeric"), "1c")
        self.assertEqual(sd.step_of("Manual Match"), "manual")
        self.assertEqual(sd.step_of("CAMD Unmatched"), "other")
        self.assertIsNone(sd.step_of(""))
        self.assertIsNone(sd.step_of("NA"))
        self.assertIsNone(sd.step_of(None))

    def test_ids_numbers_prefix(self):
        self.assertEqual(sd.clean_id(" ELK1 "), "ELK1")
        self.assertEqual(sd.clean_id("57865.0"), "57865")
        self.assertEqual(sd.clean_id("NA"), "")
        self.assertEqual(sd.clean_id(None), "")
        self.assertEqual(sd.number("202"), 202.0)
        self.assertIsNone(sd.number("NA"))
        self.assertIsNone(sd.number("nan"))
        self.assertEqual(sd.prefix("ELK1"), "ELK")
        self.assertEqual(sd.prefix("e01"), "E")
        self.assertEqual(sd.prefix("01"), "")
        self.assertEqual(sd.ratio(202.0, 9.3), 202.0 / 9.3)
        self.assertEqual(sd.ratio(10.0, 20.0), 2.0)
        self.assertIsNone(sd.ratio(0.0, 5.0))
        self.assertIsNone(sd.ratio(None, 5.0))


class PairTests(unittest.TestCase):
    ROWS = [row("d", "57865", "ELK1", "57865", "E01", "202", "9.3"),
            row("d", "57865", "ELK1", "57865", "E01", "202", "9.3"),   # same pair, unit row
            row("d", "57865", "ELK2", "57865", "E02", "202", "9.3"),
            row("a", "10", "1", "10", "1", "100", "110"),
            row("a", "10", "2", "10", "2", "100", "40"),
            row("d", "20", "GT1", "20", "1", "50", "52"),
            row("a", "30", "3", "30", "", "50", "52"),                 # no EIA generator
            row("a", "31", "3", "31", "3", "NA", "52"),                # no CAMD capacity
            row("", "40", "1", "40", "1", "5", "5", label="")]         # no step

    def test_pairs_and_skips(self):
        pairs, skipped = sd.pairs_from_rows(self.ROWS)
        self.assertEqual(len(pairs), 5)
        self.assertEqual(skipped, {"no_step": 1, "no_ids": 1, "no_capacity": 1,
                                   "conflicts": 0})
        elk = [p for p in pairs if p["camd_gen"] == "ELK1"][0]
        self.assertEqual(elk["step"], "1d")
        self.assertEqual(elk["ratio"], 21.72)
        self.assertTrue(elk["prefix_clash"])
        gt = [p for p in pairs if p["camd_gen"] == "GT1"][0]
        self.assertFalse(gt["prefix_clash"])

    def test_conflict_counted(self):
        rows = [row("d", "1", "A1", "1", "B1", "10", "10"),
                row("d", "1", "A1", "1", "B1", "10", "12")]
        pairs, skipped = sd.pairs_from_rows(rows)
        self.assertEqual(len(pairs), 1)
        self.assertEqual(skipped["conflicts"], 1)

    def test_metrics(self):
        pairs, _ = sd.pairs_from_rows(self.ROWS)
        m = sd.metrics(pairs, True)
        self.assertEqual(m["steps"]["1a"], {"n": 2, "r15": 1, "r3": 0, "share_r15": 0.5})
        self.assertEqual(m["steps"]["1d"], {"n": 3, "r15": 2, "r3": 2, "share_r15": 0.6667})
        self.assertEqual(m["steps"]["1b"]["share_r15"], None)
        self.assertEqual(m["d_r3_outside_elk"], 0)
        self.assertEqual(m["d_clash"], {"n": 2, "r15": 2, "share_r15": 1.0})


class ScoreTests(unittest.TestCase):
    def m(self, a_share=0.05, d_share=0.10, r3=3, clash_n=5, clash_share=0.30, a_n=1000,
          d_n=10, ok=True):
        return {"columns_ok": ok,
                "steps": {"1a": {"n": a_n, "share_r15": a_share},
                          "1d": {"n": d_n, "share_r15": d_share}},
                "d_r3_outside_elk": r3, "d_clash": {"n": clash_n, "share_r15": clash_share}}

    def test_all_hold_at_the_bars(self):
        self.assertEqual(sd.score(self.m()), {"G1": True, "S1": True, "S2": True,
                                              "S3": True, "S4": True})

    def test_fail_just_past_the_bars(self):
        self.assertEqual(sd.score(self.m(a_share=0.1, d_share=0.19, r3=2, clash_n=5,
                                         clash_share=0.29)),
                         {"G1": True, "S1": False, "S2": False, "S3": False, "S4": False})
        self.assertFalse(sd.score(self.m(clash_n=4, clash_share=1.0))["S4"])
        self.assertFalse(sd.score(self.m(a_share=0.0, d_share=0.0))["S1"])

    def test_gate_stops_scoring(self):
        self.assertEqual(sd.score(self.m(a_n=999)), {"G1": False})
        self.assertEqual(sd.score(self.m(d_n=9)), {"G1": False})
        self.assertEqual(sd.score(self.m(ok=False)), {"G1": False})


if __name__ == "__main__":
    unittest.main()
