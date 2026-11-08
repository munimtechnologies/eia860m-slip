"""Checks that docs/xwstale.md reports job xwstale-v1 honestly: the gates and every prediction
scored as the job scored them (two failed, with their cause), the class table by year and the
2024 scores recomputed from data/xwstale-units-2018-2024.csv, every 2024 plant listed as that
file has it, the provenance, the post-hoc reading marked as not pre-registered, and the limits.
Reads local files only: docs/xwstale.md and data/xwstale-units-2018-2024.csv.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import csv
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))

# Copied from job xwstale-v1's xwstale.json "scores" (8 November 2026).
SCORES = {"G1": True, "G2": True, "G3": True, "P1": False, "P2": True, "P3": True,
          "P4": False, "P5": True}
PROBS = {"P1": "60%", "P2": "55%", "P3": "60%", "P4": "40%", "P5": "40%"}
# Bars from tools/xwstale/xwstale.py 0.1.0.
P1_SHARE, P2_SHARE, P3_MAX, P4_PLANTS, P4_UNITS, P4_YEAR, P5_SHARE = (
    0.6, 0.9, 10, ("563", "2866", "55243"), 35, "2023", 0.5)
CLASSES = ("never_listed", "retired_before", "retired_in_year", "other")


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


def rows(path):
    with open(os.path.join(HERE, path), encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def summary(ys):
    c = {"n": len(ys)}
    for k in CLASSES:
        c[k] = sum(1 for r in ys if r["class"] == k)
    rb = [r for r in ys if r["class"] == "retired_before"]
    c["window"] = sum(1 for r in rb
                      if int(r["latest_retirement_year"]) >= int(r["report_year"]) - 2)
    c["later"] = sum(1 for r in ys if r["listed_later"] == "True")
    c["plants"] = len({r["plant_id_eia"] for r in ys})
    return c


class XwstaleResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/xwstale.md")
        cls.rows = rows("data/xwstale-units-2018-2024.csv")
        cls.r24 = [r for r in cls.rows if r["report_year"] == "2024"]

    def test_headline(self):
        self.assertIn("**All three gates held; 3 of the 5 predictions held and 2 failed.**",
                      self.doc)
        self.assertIn("Result of pre-registration xwstale-1 ([plan](xwstale-plan.md), commit "
                      "22e8ad3", self.doc)
        self.assertIn("made with AI agents working in MV2's name", self.doc)
        self.assertIn("no person has checked these results by hand", self.doc)
        self.assertIn("**33 of the 65 (50.8%) are at plants whose combustion generators had all "
                      "retired before 2024, every one of them in 2022 or 2023**", self.doc)

    def test_score_rows(self):
        for g in ("G1", "G2", "G3"):
            self.assertTrue(SCORES[g])
            self.assertIn("| %s | gate | held |" % g, self.doc)
        for p, prob in PROBS.items():
            word = "held" if SCORES[p] else "failed"
            self.assertIn("| %s | %s | %s |" % (p, prob, word), self.doc)
        self.assertIn("**Why P1 and P4 failed.**", self.doc)
        self.assertIn("The bars are reported as failed and are not re-scored.", self.doc)

    def test_scores_recomputed(self):
        self.assertEqual(len(self.rows), 228)
        c = summary(self.r24)
        self.assertEqual(c["n"], 65)
        self.assertEqual(c["plants"], 17)
        self.assertEqual(c["retired_before"] / c["n"] >= P1_SHARE, SCORES["P1"])
        self.assertEqual(c["retired_before"], 33)
        rb = [r for r in self.r24 if r["class"] == "retired_before"]
        in_22_23 = sum(1 for r in rb if r["latest_retirement_year"] in ("2022", "2023"))
        self.assertEqual(in_22_23, 33)
        self.assertEqual(len(rb) > 0 and in_22_23 / len(rb) >= P2_SHARE, SCORES["P2"])
        self.assertEqual(c["never_listed"] <= P3_MAX, SCORES["P3"])
        self.assertEqual(c["never_listed"], 4)
        p4 = [r for r in self.r24 if r["plant_id_eia"] in P4_PLANTS and r["xwgap_reason"] == "absent"]
        self.assertEqual(len(p4), P4_UNITS)
        ok = [r for r in p4 if r["class"] == "retired_before"
              and r["latest_retirement_year"] == P4_YEAR]
        self.assertEqual(len(ok), 11)
        self.assertEqual(len(ok) == P4_UNITS, SCORES["P4"])
        shares = []
        for y in range(2019, 2024):
            s = summary([r for r in self.rows if r["report_year"] == str(y)])
            shares.append(s["retired_before"] / s["n"] >= P5_SHARE)
            self.assertIn("%d %d of %d" % (y, s["retired_before"], s["n"]), self.doc)
        self.assertEqual(all(shares), SCORES["P5"])
        for text in ("33 of 65 units (50.8%) are retired_before",
                     "33 of the 33 retired_before units (100%)",
                     "4 of 65 units are never_listed",
                     "11 of the 35 absent units at plants 563, 2866 and 55243",
                     "N = 65 absent and not_operating gap units in 2024, at 17 EIA plants.",
                     "57 of the 65 units of 2024 (87.7%)"):
            self.assertIn(text, self.doc)

    def test_year_table(self):
        years = sorted({r["report_year"] for r in self.rows})
        self.assertEqual(years, [str(y) for y in range(2018, 2025)])
        for y in years:
            c = summary([r for r in self.rows if r["report_year"] == y])
            cells = [y, c["n"], c["never_listed"], c["retired_before"], c["retired_in_year"],
                     c["other"], c["window"], c["later"], c["plants"]]
            self.assertIn("| " + " | ".join(str(x) for x in cells) + " |", self.doc)

    def test_every_2024_plant_listed(self):
        plants = {}
        for r in self.r24:
            self.assertEqual(r["plant_id_epa"], r["plant_id_eia"])
            plants.setdefault(r["plant_id_eia"], []).append(r)
        self.assertEqual(len(plants), 17)
        lines = self.doc.splitlines()
        for pi, rs in plants.items():
            for col in ("xwgap_reason", "class", "last_listed_year", "combustion_generators",
                        "undated", "latest_retirement_year"):
                self.assertEqual(len({r[col] for r in rs}), 1, (pi, col))
            r = rs[0]
            cells = [pi, len(rs), r["xwgap_reason"], r["class"], r["last_listed_year"] or "none",
                     r["combustion_generators"], r["undated"],
                     r["latest_retirement_year"] or "none"]
            prefix = "| " + " | ".join(str(x) for x in cells) + " |"
            hits = [ln for ln in lines if ln.startswith(prefix)]
            self.assertEqual(len(hits), 1, prefix)

    def test_post_hoc_claims_from_data(self):
        # Astoria: 24 units, other/undated, 1 of 21 undated, last listed 2023.
        a = [r for r in self.r24 if r["plant_id_eia"] == "55243"]
        self.assertEqual(len(a), 24)
        self.assertEqual({(r["class"], r["cause"], r["combustion_generators"], r["undated"],
                           r["retiring_after_year"], r["last_listed_year"]) for r in a},
                         {("other", "undated", "21", "1", "0", "2023")})
        # Cove Point: 4 units 2021-2024, last listed 2020, 9 of 9 undated, never listed later.
        cp = [r for r in self.rows if r["plant_id_eia"] == "59073"]
        self.assertEqual(sorted({r["report_year"] for r in cp}), ["2021", "2022", "2023", "2024"])
        self.assertEqual({(r["last_listed_year"], r["combustion_generators"], r["undated"],
                           r["listed_later"]) for r in cp}, {("2020", "9", "9", "False")})
        # The rest of 2024: retired_before + Astoria + Cove Point + 2 EPA-only plants.
        rest = {r["plant_id_eia"] for r in self.r24 if r["class"] != "retired_before"}
        self.assertEqual(rest, {"55243", "59073", "880079", "880102"})
        self.assertEqual(sum(1 for r in self.r24 if r["plant_id_eia"] in rest) - 24, 8)
        # Frontera: retired_before (2016) 2018-2022; the only out-of-window ones 2019-2022.
        fr = [r for r in self.rows if r["plant_id_eia"] == "55098"]
        self.assertEqual(sorted({r["report_year"] for r in fr}),
                         ["2018", "2019", "2020", "2021", "2022"])
        self.assertEqual({(r["class"], r["latest_retirement_year"], r["last_listed_year"])
                          for r in fr}, {("retired_before", "2016", "2016")})
        for y in range(2019, 2023):
            out = [r for r in self.rows if r["report_year"] == str(y)
                   and r["class"] == "retired_before"
                   and int(r["latest_retirement_year"]) < y - 2]
            self.assertEqual({r["plant_id_eia"] for r in out}, {"55098"}, y)
            self.assertEqual(len(out), 2)
        # Zimmer: last listed 2022 for 2023 and 2024, listed later.
        z = [r for r in self.rows if r["plant_id_eia"] == "6019"]
        self.assertEqual({(r["report_year"], r["last_listed_year"], r["listed_later"]) for r in z},
                         {("2023", "2022", "True"), ("2024", "2022", "True")})
        # 88 ids never listed every year.
        for pi in ("880079", "880102"):
            ys = {r["report_year"] for r in self.rows if r["plant_id_eia"] == pi}
            self.assertEqual(ys, {str(y) for y in range(2018, 2025)})
            self.assertTrue(all(r["class"] == "never_listed" for r in self.rows
                                if r["plant_id_eia"] == pi))
        # Not-operating / undated plants named in the doc.
        named = {("2020", "60925"), ("2021", "10350"), ("2021", "63259"), ("2021", "60910"),
                 ("2022", "60910"), ("2023", "60910"), ("2022", "6061"), ("2020", "2378")}
        undated_other = {(r["report_year"], r["plant_id_eia"]) for r in self.rows
                         if r["class"] == "other" and r["plant_id_eia"] not in ("55243", "59073")}
        self.assertEqual(undated_other, named)
        # 2021 held exactly at the bar.
        s21 = summary([r for r in self.rows if r["report_year"] == "2021"])
        self.assertEqual((s21["retired_before"], s21["n"]), (14, 28))

    def test_provenance(self):
        for text in ("md5 7edad4f7ef506b1ec9bae56cfd7d8cb0",
                     "md5 fc34515c864e1a38db8a952f094a11f0",
                     "all 16 unit tests passed",
                     "18,669 bytes, md5 797c74d1722c533ae0c7f266148f05c5",
                     "7,718,170 bytes, md5 6c4372366df319de1888d8fc6ea1ec0e, 667,073 rows"):
            self.assertIn(text, self.doc)

    def test_post_hoc_and_limits(self):
        for text in ("## What else the rows show (read after scoring, not pre-registered)",
                     "This is a reading after scoring, not a re-score.",
                     "We have not checked why the plant left EIA-860.",
                     "The rule is strict: one undated combustion generator puts a whole plant "
                     "in other",
                     "No person has checked the code or the results by hand.",
                     "but PUDL has no SMECO row in 2021 and 2022"):
            self.assertIn(text, self.doc)
        self.assertIn("(228 rows)", self.doc)


if __name__ == "__main__":
    unittest.main()
