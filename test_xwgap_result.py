"""Checks that docs/xwgap.md reports job xwgap-v1 honestly: the gates and every prediction scored
as the job scored them (four failed, with their cause), the year table and the 2024 scores
recomputed from data/xwgap-units-2018-2024.csv, every 2024 gap unit listed by plant as that file
has it, the provenance, the post-hoc reading marked as not pre-registered, and the limits.
Reads local files only.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import csv
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))

# Copied from job xwgap-v1's xwgap.json "scores" (8 November 2026).
SCORES = {"G1": True, "G2": True, "P1": False, "P2": True, "P3": True, "P4": False,
          "G3": True, "P5": False, "P6": False}
PROBS = {"P1": "45%", "P2": "40%", "P3": "50%", "P4": "35%", "P5": "35%", "P6": "70%"}
# xwgap.json "g1" and "oge_rows" (not in the data file).
CEMS_2024, OGE_ROWS = 4215, 729
# Bars from tools/xwgap/xwgap.py 0.1.0.
MIN_GAP, MIN_OGE_ROWS, P2_SHARE, P3_MIN_N, P3_SHARE, P4_MIN, P5_SHARE, P6_SHARE = (
    40, 150, 0.2, 10, 0.5, 10, 0.25, 0.7)
REASONS = ("absent", "not_operating", "all_linked")


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


def rows(path):
    with open(os.path.join(HERE, path), encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def counts(ys):
    al = [r for r in ys if r["reason"] == "all_linked"]
    c = {"n": len(ys)}
    for reason in REASONS:
        c[reason] = sum(1 for r in ys if r["reason"] == reason)
    c["fit"] = sum(1 for r in al if r["linked_generators_that_fit"])
    c["same_id"] = sum(1 for r in ys if r["same_id_generators"])
    c["oge"] = sum(1 for r in ys if r["in_oge_manual"] == "True")
    c["prev_known"] = sum(1 for r in ys if r["unmatched_prev_year"] != "")
    c["prev"] = sum(1 for r in ys if r["unmatched_prev_year"] == "True")
    c["plants"] = len({r["plant_id_eia"] for r in ys})
    return c


class XwgapResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/xwgap.md")
        cls.rows = rows("data/xwgap-units-2018-2024.csv")
        cls.r24 = [r for r in cls.rows if r["report_year"] == "2024"]

    def test_headline(self):
        self.assertIn("**All three gates held; 2 of the 6 predictions held and 4 failed.**",
                      self.doc)
        self.assertIn("Result of pre-registration xwgap-1 ([plan](xwgap-plan.md), commit "
                      "c4bdc1a", self.doc)
        self.assertIn("made with AI agents working in MV2's name", self.doc)
        self.assertIn("no person has checked these results by hand", self.doc)
        self.assertIn("**62 of the 75 (83%) are at EIA plants with no EIA-860 generator row at "
                      "all in 2024**", self.doc)

    def test_score_rows(self):
        for g in ("G1", "G2", "G3"):
            self.assertTrue(SCORES[g])
            self.assertIn("| %s | gate | held |" % g, self.doc)
        for p, prob in PROBS.items():
            word = "held" if SCORES[p] else "failed"
            self.assertIn("| %s | %s | %s |" % (p, prob, word), self.doc)
        self.assertIn("**Why P1, P4 and P6 failed.**", self.doc)
        self.assertIn("**Why P5 failed.**", self.doc)
        self.assertIn("The bars are reported as failed and are not re-scored.", self.doc)

    def test_newest_scores_recomputed(self):
        c = counts(self.r24)
        self.assertEqual(c["n"], 75)
        self.assertEqual(c["n"] >= MIN_GAP, SCORES["G2"])
        self.assertEqual(c["all_linked"] > c["absent"] and c["all_linked"] > c["not_operating"],
                         SCORES["P1"])
        self.assertEqual(c["absent"] / c["n"] >= P2_SHARE, SCORES["P2"])
        self.assertGreaterEqual(c["all_linked"], P3_MIN_N)
        self.assertEqual(c["fit"] / c["all_linked"] >= P3_SHARE, SCORES["P3"])
        self.assertEqual(c["same_id"] >= P4_MIN, SCORES["P4"])
        self.assertEqual(OGE_ROWS >= MIN_OGE_ROWS, SCORES["G3"])
        self.assertEqual(c["oge"] / c["n"] >= P5_SHARE, SCORES["P5"])
        self.assertEqual(c["prev_known"], c["n"])
        self.assertEqual(c["prev"] / c["n"] >= P6_SHARE, SCORES["P6"])
        for text in ("all_linked 10, absent 62, not_operating 3",
                     "62 of 75 gap units (82.7%) are absent",
                     "6 of the 10 all_linked gap units (60%)",
                     "3 gap units have a same-id generator",
                     "729 rows in OGE's file",
                     "a row for 10 of 75 gap units (13.3%)",
                     "37 of 75 gap units (49.3%) were also unmatched in 2023",
                     "4,215 CEMS units (at least 2,000 needed)",
                     "N = 75 gap units in 2024, at 23 EIA plants."):
            self.assertIn(text, self.doc)
        self.assertEqual(c["plants"], 23)

    def test_year_table(self):
        self.assertEqual(len(self.rows), 317)
        self.assertIn("(317 rows)", self.doc)
        years = sorted({r["report_year"] for r in self.rows})
        self.assertEqual(years, [str(y) for y in range(2018, 2025)])
        for y in years:
            c = counts([r for r in self.rows if r["report_year"] == y])
            prev = str(c["prev"]) if c["prev_known"] else "n/a"
            cells = [y, c["n"], c["absent"], c["not_operating"], c["all_linked"], c["fit"],
                     c["same_id"], c["oge"], prev, c["plants"]]
            self.assertIn("| " + " | ".join(str(x) for x in cells) + " |", self.doc)

    def test_every_2024_unit_listed(self):
        plants = {}
        for r in self.r24:
            self.assertEqual(r["plant_id_epa"], r["plant_id_eia"])
            self.assertEqual(r["other_eia_plants_of_epa_plant"], "")
            plants.setdefault(r["plant_id_eia"], []).append(r)
        lines = self.doc.splitlines()
        for pi, rs in plants.items():
            units = ", ".join(r["emissions_unit_id_epa"] for r in rs).replace("*", "\\*")
            peaks = ["%g" % float(r["max_gross_load_mw"]) for r in rs]
            peak_txt = (peaks[0] + " each") if len(rs) > 3 and len(set(peaks)) == 1 \
                else ", ".join(peaks)
            reasons = {r["reason"] for r in rs}
            self.assertEqual(len(reasons), 1)
            prefix = "| %s | %s | %s | %s |" % (pi, units, peak_txt, reasons.pop())
            hits = [ln for ln in lines if ln.startswith(prefix)]
            self.assertEqual(len(hits), 1, prefix)
            oge = {r["in_oge_manual"] for r in rs}
            prev = {r["unmatched_prev_year"] for r in rs}
            self.assertEqual(len(oge), 1)
            self.assertEqual(len(prev), 1)
            yes = {"True": "yes", "False": "no"}
            self.assertTrue(hits[0].endswith("| %s | %s |" % (yes[oge.pop()], yes[prev.pop()])),
                            hits[0])
        self.assertEqual(len(plants), 23)

    def test_post_hoc_claims_from_data(self):
        # OGE covers exactly the all_linked units of 2024.
        self.assertEqual({r["reason"] for r in self.r24 if r["in_oge_manual"] == "True"},
                         {"all_linked"})
        self.assertEqual(sum(1 for r in self.r24 if r["reason"] == "all_linked"), 10)
        # 38 units not unmatched in 2023; 35 of them absent at 563, 2866, 55243.
        new = [r for r in self.r24 if r["unmatched_prev_year"] == "False"]
        self.assertEqual(len(new), 38)
        absent_new = [r for r in new if r["reason"] == "absent"]
        self.assertEqual(len(absent_new), 35)
        self.assertEqual({r["plant_id_eia"] for r in absent_new}, {"563", "2866", "55243"})
        # 16 absent plants in 2024; 53 -> 75; absent 36 -> 62; all_linked 14 -> 10.
        self.assertEqual(len({r["plant_id_eia"] for r in self.r24 if r["reason"] == "absent"}), 16)
        r23 = [r for r in self.rows if r["report_year"] == "2023"]
        self.assertEqual(counts(r23)["n"], 53)
        self.assertEqual(counts(r23)["absent"], 36)
        self.assertEqual(counts(r23)["all_linked"], 14)
        # Zimmer: absent in 2023 and 2024, peak 1427 -> 1313.
        z = {r["report_year"]: r for r in self.rows if r["plant_id_eia"] == "6019"}
        self.assertEqual(sorted(z), ["2023", "2024"])
        self.assertEqual((z["2023"]["max_gross_load_mw"], z["2024"]["max_gross_load_mw"]),
                         ("1427.0", "1313.0"))
        self.assertTrue(all(r["reason"] == "absent" for r in z.values()))
        # 88-prefixed plants absent in every year.
        for pi in ("880079", "880102"):
            ys = {r["report_year"] for r in self.rows if r["plant_id_eia"] == pi}
            self.assertEqual(ys, {str(y) for y in range(2018, 2025)})
            self.assertTrue(all(r["reason"] == "absent" for r in self.rows
                                if r["plant_id_eia"] == pi))
        # Long-standing all_linked plants.
        for pi, first in (("315", 2020), ("335", 2020), ("7063", 2018), ("55641", 2020),
                          ("55699", 2018)):
            ys = {int(r["report_year"]) for r in self.rows if r["plant_id_eia"] == pi}
            self.assertEqual(ys, set(range(first, 2025)), pi)

    def test_provenance(self):
        for text in ("md5 f64238c37b2c6cd7eb1bbe91f6404635",
                     "md5 029ec84bb995cecf201e4ebfdcddd2f5",
                     "all 15 unit tests passed",
                     "190,240 bytes, md5 420d50a7e4d066d29eee909eab73d932, 44,833 rows",
                     "3,298,243 bytes, md5 a0a3345e0f0d143bf216f2323548a8d6, 118,117 rows",
                     "7,718,170 bytes, md5 6c4372366df319de1888d8fc6ea1ec0e, 667,073 rows",
                     "45,943 bytes, md5 d1275db58bd4cc9767c9ec0548d47ef7"):
            self.assertIn(text, self.doc)

    def test_post_hoc_and_limits(self):
        for text in ("## What else the rows show (read after scoring, not pre-registered)",
                     "We have not checked when each of the 16 absent plants stopped running.",
                     "A reason is a description, not a diagnosis.",
                     "this check does not tell them apart",
                     "No person has checked the code or the results by hand."):
            self.assertIn(text, self.doc)


if __name__ == "__main__":
    unittest.main()
