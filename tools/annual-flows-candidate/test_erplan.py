"""Tests for erplan.py on hand-built rows (no network, no workbooks). MV2 of Munim, Inc. (made with
AI agents). Apache-2.0."""

import unittest

import erplan as ep

HEAD = ("Utility ID", "Plant Code", "Plant Name", "Generator ID", "Status", "Current Month",
        "Current Year")
OP_HEAD = ("Utility ID", "Plant Code", "Plant Name", "Generator ID", "Status")
YEARS = (2022, 2023, 2024, 2025)


def book():
    """A generator workbook as read_sheets returns it."""
    return {
        "Operable": [("Early Release data, subject to change",), OP_HEAD,
                     (1, 10.0, "P1", 1.0, "OP"), (1, 11, "P2", " gt1 ", "OP"),
                     (None, None, None, None, None), ("NOTE: footer",)],
        "Proposed": [("Early Release",), HEAD,
                     (1, 12, "P3", "PV", "P", 5, 2022.0),
                     (1, 13, "P4", "WT", "T", 1, 2023),
                     (1, 10, "P1", 1, "V", 3, 2022),
                     (1, 14, "P5", "B1", "P", None, None)],
        "Retired and Canceled": [OP_HEAD, (1, 15, "P6", "ST1", "RE"), (1, 11, "P2", "GT1", "RE")],
        "Notes": [("anything",)],
    }


def r(year, s, k, mw, bucket, er, final="plan_y", group="solar"):
    return {"year": year, "set": s, "key": k, "group": group, "mw": mw, "bucket": bucket,
            "span": ep.span(bucket), "er": er, "final": final}


def year_rows(late, early):
    """Per year: late A rows (plan_y MW, absent MW) and early A rows, if given."""
    rows = []
    for y in YEARS:
        lp, la = late[y]
        rows += [r(y, "A", "%d/L1" % y, lp, "m07", "plan_y"),
                 r(y, "A", "%d/L2" % y, la, "m08", "absent")]
        if early is not None:
            ep_, ea = early
            rows += [r(y, "A", "%d/E1" % y, ep_, "m02", "plan_y"),
                     r(y, "A", "%d/E2" % y, ea, "m03", "absent")]
    return rows


class ParseTests(unittest.TestCase):
    def test_key(self):
        self.assertEqual(ep.key(1234.0, 1.0), "1234/1")
        self.assertEqual(ep.key("56", " gt1 "), "56/GT1")
        self.assertEqual(ep.key(7, "01"), "7/01")
        self.assertIsNone(ep.key(None, "1"))
        self.assertIsNone(ep.key("x", "1"))
        self.assertIsNone(ep.key(5, ""))
        self.assertIsNone(ep.key(5, "  "))

    def test_as_year(self):
        self.assertEqual(ep.as_year(2022.0), 2022)
        self.assertEqual(ep.as_year("2022"), 2022)
        self.assertIsNone(ep.as_year(" "))
        self.assertIsNone(ep.as_year(None))

    def test_sheet_kind(self):
        self.assertEqual(ep.sheet_kind("Operable"), "operable")
        self.assertEqual(ep.sheet_kind(" Proposed "), "proposed")
        self.assertEqual(ep.sheet_kind("Retired and Canceled"), "retired")
        self.assertIsNone(ep.sheet_kind("Notes"))

    def test_generator_members(self):
        names = ["eia860/3_1_Generator_Y2021.xlsx", "3_2_Wind_Y2021.xlsx", "2___Plant_Y2021.xlsx",
                 "3_1_Generator_Y2021_Early_Release.xlsx", "x/3_1_generator_y2021.xls"]
        self.assertEqual(ep.generator_members(names),
                         ["eia860/3_1_Generator_Y2021.xlsx",
                          "3_1_Generator_Y2021_Early_Release.xlsx"])

    def test_header_found_and_missing(self):
        i, cells = ep.header([("x",), HEAD])
        self.assertEqual(i, 1)
        self.assertEqual(cells[1], "plant code")
        self.assertEqual(ep.header([("x",)] * 12 + [HEAD]), (None, None))

    def test_index_classes(self):
        self.assertEqual(ep.index(book(), 2022),
                         {"10/1": "plan_y", "11/GT1": "operable", "12/PV": "plan_y",
                          "13/WT": "proposed_other", "14/B1": "proposed_other",
                          "15/ST1": "retired"})

    def test_index_needs_year_column(self):
        self.assertEqual(ep.index({"Proposed": [OP_HEAD, (1, 12, "x", "PV", "P")]}, 2022), {})

    def test_structure(self):
        st, problems = ep.structure(book())
        self.assertEqual(problems, [])
        self.assertEqual(sorted(st), ["Operable", "Proposed", "Retired and Canceled"])
        self.assertEqual(st["Proposed"]["header_row"], 1)
        self.assertEqual(st["Operable"]["above"], [["Early Release data, subject to change"]])
        self.assertEqual(st["Retired and Canceled"]["above"], [])

    def test_structure_problems(self):
        _, p = ep.structure({"Operable": [OP_HEAD], "Proposed": [OP_HEAD]})
        self.assertEqual(p, ["no current-year column in sheet 'Proposed'"])
        _, p = ep.structure({"Operable": [OP_HEAD]})
        self.assertEqual(p, ["no usable proposed sheet"])

    def test_early_marked(self):
        st, _ = ep.structure(book())
        above = [x for v in st.values() for x in v["above"]]
        self.assertTrue(ep.early_marked("3_1_Generator_Y2021.xlsx", above))
        self.assertTrue(ep.early_marked("eia8602021/3_1_Generator_Y2021_Early_Release.xlsx", []))
        self.assertFalse(ep.early_marked("3_1_Generator_Y2021.xlsx", [["Plant data"]]))

    def test_span(self):
        self.assertEqual([ep.span(b) for b in ("m02", "m06", "m08", "after", "m01", "unlisted")],
                         ["early", "mid", "late", "edge", "other", "other"])

    def test_read_sets_and_classify(self):
        text = ("year,set,key,group,mw,first_listed,bucket\n"
                "2022,A,6283/7,oil,1.0,2022-08,m08\n"
                "2022,A,10/pv,solar,2.5,2022-03,m03\n"
                "2018,B,9/X,solar,4.0,2018-10,m10\n")
        rows = ep.read_sets(text)
        self.assertEqual([x["key"] for x in rows], ["6283/7", "10/PV", "9/X"])
        self.assertEqual([x["span"] for x in rows], ["late", "early", "edge"])
        ep.classify(rows, {2022: ({"6283/7": "plan_y"},
                                  {"6283/7": "plan_y", "10/PV": "proposed_other"})})
        self.assertEqual((rows[0]["er"], rows[0]["final"]), ("plan_y", "plan_y"))
        self.assertEqual((rows[1]["er"], rows[1]["final"]), ("absent", "proposed_other"))
        self.assertNotIn("er", rows[2])


class ScoreTests(unittest.TestCase):
    def test_tally_share(self):
        rows = [r(2022, "A", "1/A", 60.0, "m07", "plan_y"), r(2022, "A", "2/B", 40.0, "m08", "absent"),
                r(2022, "A", "3/C", 50.0, "m02", "plan_y"), r(2022, "B", "4/D", 30.0, "m09", "absent"),
                r(2023, "A", "5/E", 10.0, "m07", "plan_y"),
                {"year": 2018, "set": "A", "key": "6/F", "group": "solar", "mw": 9.0,
                 "bucket": "m07", "span": "late"}]
        self.assertAlmostEqual(ep.share(ep.tally(rows, (2022,), "A", "late")), 0.6)
        self.assertAlmostEqual(ep.share(ep.tally(rows, (2022,), "A", "late"), ep.CLASSES[:4]), 0.6)
        self.assertAlmostEqual(ep.share(ep.tally(rows, (2022, 2023), "A", "late")), 7 / 11)
        self.assertAlmostEqual(ep.share(ep.tally(rows, (2022,), "A")), 110 / 150)
        self.assertAlmostEqual(ep.share(ep.tally(rows, (2022,), "A", field="final")), 1.0)
        self.assertIsNone(ep.share(ep.tally(rows, (2024,), "A")))
        self.assertIsNone(ep.share(ep.tally(rows, (2018,), "A")))

    def test_predictions_r1(self):
        p = ep.predictions(year_rows({y: (120.0, 30.0) for y in YEARS}, (90.0, 10.0)), YEARS)
        self.assertAlmostEqual(p["late"], 0.8)
        self.assertAlmostEqual(p["early"], 0.9)
        self.assertEqual((p["P1"], p["P2"], p["P3"], p["years_ok"]), (True, True, True, 4))
        self.assertTrue(p["reading"].startswith("most late entrants were in the early release"))

    def test_predictions_r2(self):
        p = ep.predictions(year_rows({y: (20.0, 130.0) for y in YEARS}, (90.0, 10.0)), YEARS)
        self.assertAlmostEqual(p["late"], 20 / 150)
        self.assertEqual((p["P1"], p["P2"], p["P3"], p["years_ok"]), (False, False, False, 0))
        self.assertTrue(p["reading"].endswith("(R2 for most)"))

    def test_predictions_few_years(self):
        late = {2022: (120.0, 30.0), 2023: (120.0, 30.0), 2024: (50.0, 0.0), 2025: (50.0, 0.0)}
        p = ep.predictions(year_rows(late, None), YEARS)
        self.assertEqual(sorted(p["late_by_year"]), [2022, 2023])
        self.assertAlmostEqual(p["late"], 340 / 400)
        self.assertTrue(p["P1"])
        self.assertIsNone(p["P2"])
        self.assertIsNone(p["early"])
        self.assertIsNone(p["P3"])

    def test_reading(self):
        self.assertEqual(ep.reading(0.5), "mixed")
        self.assertEqual(ep.reading(None), "no data")
        self.assertTrue(ep.reading(0.75).endswith("(R1 for most)"))
        self.assertTrue(ep.reading(0.2).endswith("(R2 for most)"))

    def test_check_c1(self):
        rows = [r(2018, "A", "1/A", 13082.3, "m07", "plan_y"),
                r(2019, "A", "2/B", 42181.2, "m02", "plan_y"),
                r(2020, "A_built", "3/C", 36998.4, "m05", "plan_y"),
                r(2021, "B", "4/D", 32937.3, "m09", "absent"),
                r(2017, "A", "5/E", 999.0, "m07", "plan_y")]
        c = ep.check_c1(rows)
        self.assertTrue(c["pass"])
        self.assertEqual(c["a_late"], 13082.3)
        rows[3]["mw"] = 32900.0
        self.assertFalse(ep.check_c1(rows)["pass"])

    def test_check_f(self):
        ok = [r(2022, "A", "1/A", 95.0, "m07", "absent", "plan_y"),
              r(2022, "A", "2/B", 3.0, "m07", "absent", "operable"),
              r(2022, "A", "3/C", 2.0, "m07", "absent", "absent")]
        f = ep.check_f(ok, (2022,))
        self.assertAlmostEqual(f["f1"], 0.98)
        self.assertAlmostEqual(f["f2"], 0.95)
        self.assertTrue(f["f1_pass"] and f["f2_pass"])
        bad = [r(2022, "A", "1/A", 80.0, "m07", "absent", "plan_y"),
               r(2022, "A", "2/B", 10.0, "m07", "absent", "proposed_other"),
               r(2022, "A", "3/C", 10.0, "m07", "absent", "absent")]
        f = ep.check_f(bad, (2022,))
        self.assertFalse(f["f1_pass"])
        self.assertFalse(f["f2_pass"])

    def test_check_f3(self):
        final = {"1/A": "operable", "2/B": "operable", "3/C": "plan_y", "4/D": "operable",
                 "5/E": "operable"}
        er = {"1/A": "operable", "2/B": "retired", "4/D": "operable"}
        self.assertAlmostEqual(ep.check_f3(er, final), 0.75)
        self.assertIsNone(ep.check_f3({}, {"3/C": "plan_y"}))


class CopyTests(unittest.TestCase):
    def test_copies(self):
        self.assertEqual(sorted(ep.COPIES), list(YEARS))
        recs = set()
        for y, c in ep.COPIES.items():
            er, final = c["er"], c["final"]
            self.assertLess(er[3], final[3])
            self.assertLess(er[3], "%d-08-25" % y)
            self.assertEqual(len(er[2]), 32)
            self.assertEqual(len(final[2]), 32)
            recs.update((er[0], final[0]))
        self.assertEqual(len(recs), 8)

    def test_copy_urls(self):
        self.assertEqual(ep.copy_urls("6954131", "eia860-2021.zip")[0],
                         "https://zenodo.org/records/6954131/files/eia860-2021.zip?download=1")


if __name__ == "__main__":
    unittest.main()
