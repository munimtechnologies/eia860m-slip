"""Unit tests for step1d_look.py (no network). Apache-2.0. Made with AI agents working in MV2's
name (MV2, Munim, Inc.)."""

import unittest

import step1d_look as L


def pair(camd_plant, camd_gen, eia_plant, eia_gen, step, camd_mw, eia_mw, state="TX"):
    r = L.s1.ratio(camd_mw, eia_mw)
    return {"camd_plant": camd_plant, "camd_gen": camd_gen, "eia_plant": eia_plant,
            "eia_gen": eia_gen, "step": step, "camd_mw": camd_mw, "eia_mw": eia_mw,
            "ratio": round(r, 3),
            "prefix_clash": bool(L.s1.prefix(camd_gen) and L.s1.prefix(eia_gen)
                                 and L.s1.prefix(camd_gen) != L.s1.prefix(eia_gen)),
            "extra": {"CAMD_STATE": state, "CAMD_FACILITY_NAME": "X", "CAMD_UNIT_ID": "1",
                      "EIA_UNIT_TYPE": "IC"}}


def rec(plant, gen, mw, state="TX", sheet="Operating", pm="GT"):
    return {"sheet": sheet, "plant": plant, "gen": gen, "name": "P%d" % plant, "state": state,
            "mw": mw, "pm": pm, "tech": "", "status": "(OP)"}


class IdTests(unittest.TestCase):
    def test_norm_gen(self):
        self.assertEqual(L.norm_gen(1.0), "1")
        self.assertEqual(L.norm_gen(12), "12")
        self.assertEqual(L.norm_gen("01"), "01")
        self.assertEqual(L.norm_gen(" elk1 "), "ELK1")
        self.assertEqual(L.norm_gen(None), "")
        self.assertEqual(L.norm_gen(float("nan")), "")
        self.assertEqual(L.norm_gen("NA"), "")

    def test_plant_int(self):
        self.assertEqual(L.plant_int("57865"), 57865)
        self.assertEqual(L.plant_int(58835.0), 58835)
        self.assertIsNone(L.plant_int("NOTE: x"))
        self.assertIsNone(L.plant_int(None))


class SheetTests(unittest.TestCase):
    def test_column_map_first_prefix_wins(self):
        header = ("Entity ID", "Plant ID", "Plant Name", "Plant State", "Generator ID",
                  "Nameplate Capacity (MW)", "Net Summer Capacity (MW)", "Technology",
                  "Prime Mover Code", "Status", "Nameplate Energy Capacity (MWh)")
        m = L.column_map(header)
        self.assertEqual(m["plant_id"], 1)
        self.assertEqual(m["plant_name"], 2)
        self.assertEqual(m["state"], 3)
        self.assertEqual(m["gen_id"], 4)
        self.assertEqual(m["mw"], 5)
        self.assertEqual(m["tech"], 7)
        self.assertEqual(m["pm"], 8)
        self.assertEqual(m["status"], 9)

    def test_records_skip_title_and_notes(self):
        rows = [("Title row", None, None, None, None),
                ("Plant ID", "Plant Name", "Plant State", "Generator ID",
                 "Nameplate Capacity (MW)"),
                (58835, "Elk Station", "TX", "ELK1", 202.5),
                (57865.0, "Antelope Station", "tx", 1.0, "9.3"),
                ("NOTE: data are preliminary", None, None, None, None),
                (1, "Short row")]
        recs = L.records_from_sheet("Operating", rows)
        self.assertEqual([(r["plant"], r["gen"], r["state"], r["mw"]) for r in recs],
                         [(58835, "ELK1", "TX", 202.5), (57865, "1", "TX", 9.3)])
        self.assertEqual(L.records_from_sheet("Other", [("a", "b")]), [])


class LookTests(unittest.TestCase):
    def setUp(self):
        records = [rec(57865, "E01", 9.3, pm="IC"), rec(57865, "E02", 9.3, pm="IC"),
                   rec(58835, "ELK1", 202.0), rec(58835, "ELK2", 202.0),
                   rec(99999, "ELK1", 200.0, state="OK")]
        self.by_plant, self.by_gen_state = L.build_index(records)

    def test_elk_case(self):
        p = pair("57865", "ELK1", "57865", "E01", "1d", 202.0, 9.3)
        x = L.look(p, self.by_plant, self.by_gen_state, {(57865, "E01")}, {})
        self.assertEqual(x["group"], "1d far apart")
        self.assertEqual([r["gen"] for r in x["linked_in_sep_2026"]], ["E01"])
        self.assertEqual(x["eia_at_linked_plant_n"], 2)
        # Only the same-state ELK1 counts: the Oklahoma ELK1 is another state.
        self.assertEqual([(r["plant"], r["gen"]) for r in x["same_id_same_state"]],
                         [(58835, "ELK1")])
        self.assertEqual(len(x["closer_candidates"]), 1)
        c = x["closer_candidates"][0]
        self.assertEqual((c["plant"], c["gen"], c["ratio"]), (58835, "ELK1", 1.0))
        self.assertFalse(c["linked_by_crosswalk"])
        self.assertTrue(c["same_id_same_state"])
        self.assertFalse(c["at_linked_plant"])
        self.assertEqual(x["unlinked_closer_n"], 1)

    def test_linked_candidate_is_marked(self):
        p = pair("57865", "ELK1", "57865", "E01", "1d", 202.0, 9.3)
        x = L.look(p, self.by_plant, self.by_gen_state, {(57865, "E01"), (58835, "ELK1")}, {})
        self.assertTrue(x["closer_candidates"][0]["linked_by_crosswalk"])
        self.assertEqual(x["unlinked_closer_n"], 0)

    def test_groups(self):
        self.assertEqual(L.group_of(pair("1", "CTG10", "1", "GT10", "1d", 36.5, 50.9)),
                         "1d letters differ")
        self.assertIsNone(L.group_of(pair("1", "4", "1", "CT004", "1d", 45.0, 60.5)))
        self.assertEqual(L.group_of(pair("1", "1", "1", "1", "1a", 30.0, 60.0)),
                         "1a far apart")
        self.assertEqual(L.group_of(pair("1", "1", "1", "1", "1c", 30.0, 60.0)),
                         "1b/1c far apart")
        self.assertIsNone(L.group_of(pair("1", "1", "1", "1", "1a", 30.0, 40.0)))

    def test_summary_and_markdown(self):
        p = pair("57865", "ELK1", "57865", "E01", "1d", 202.0, 9.3)
        x = L.look(p, self.by_plant, self.by_gen_state, {(57865, "E01")},
                   {"57865": [{"unit": "1", "gen": "ELK1", "mw": 202.0, "eia_plant": "57865",
                               "eia_gen": "E01", "eia_mw": 9.3, "step": "1d"}]})
        s = L.summarize([x])
        self.assertEqual(s["1d far apart"], {"n": 1, "linked_gen_in_sep_2026": 1,
                                             "with_unlinked_closer": 1,
                                             "with_same_id_same_state": 1})
        md = L.markdown({"eia": {"url": "u", "md5": "m"}, "looks": [x]})
        self.assertIn("closer (r=1.0, UNLINKED, same id same state): 58835/ELK1", md)
        self.assertIn("CAMD plant rows: ELK1->57865/E01(1d)", md)


if __name__ == "__main__":
    unittest.main()
