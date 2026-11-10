"""Checks that every count stated in docs/easeyx.md (result of pre-registration easeyx-1) is what
data/easeyx-run.json and the three CSV files in data/ (the job's outputs, unchanged) say.
Reads no outside data.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import csv
import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def path(rel):
    return os.path.join(HERE, rel)


def fmt(n):
    return f"{n:,}"


def pct(a, b):
    return f"{100.0 * a / b:.2f}%"


def read_csv(rel):
    with open(path(rel), encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


class EaseyxResultTests(unittest.TestCase):
    # The job's JSON is kept as `res`: naming it `run` would hide unittest's TestCase.run.
    @classmethod
    def setUpClass(cls):
        with open(path("docs/easeyx.md"), encoding="utf-8") as fh:
            cls.doc = fh.read()
        with open(path("data/easeyx-run.json"), encoding="utf-8") as fh:
            cls.res = json.load(fh)
        cls.ref_minus = read_csv("data/easeyx-ref-minus-f-2024.csv")
        cls.f_minus = read_csv("data/easeyx-f-minus-ref-2024.csv")
        cls.side25 = read_csv("data/easeyx-epa-side-2025.csv")

    def test_scores(self):
        self.assertEqual(self.res["scores"], {"G1": True, "G2": True, "G3": True, "P1": True,
                                              "P2": True, "P3": True, "P4": True, "P5": False})
        self.assertIn("**4 of the 5 predictions held (P1, P2, P3, P4); P5 failed.**", self.doc)
        self.assertEqual(self.res["tool"], "easeyx.py 0.1.0")
        self.assertIn("`tools/easeyx/easeyx.py` 0.1.0", self.doc)
        self.assertIn("02:13:09-02:13:23 UTC", self.doc)
        self.assertEqual((self.res["started"], self.res["finished"]),
                         ("2026-11-10T02:13:09Z", "2026-11-10T02:13:23Z"))

    def test_reference(self):
        r = self.res["reference"]
        self.assertEqual((r["rows"], r["keys"], r["duplicate_key_rows"], r["keys_conflicting_status"],
                          r["rows_no_camd_key"], r["missing_cols"]), (7182, 7174, 8, 0, 0, []))
        self.assertIn(r["md5"], self.doc)
        self.assertIn("e52a3a533f745b98b88f0556473fee0d4cbcf96d", r["url"])
        self.assertIn("7,182 data rows", self.doc)
        self.assertIn("7,174 distinct CAMD keys (8 rows repeat a key", self.doc)

    def test_files_table(self):
        self.assertEqual(sorted(self.res["files"]), [str(y) for y in range(2010, 2026)])
        for year, info in self.res["files"].items():
            md5 = self.res["downloads"][year]["md5"]
            line = f"| {year} | {fmt(info['rows'])} | {fmt(info['keys'])} | `{md5}` |"
            self.assertIn(line, self.doc)
            self.assertEqual(info["missing_cols"], [])
        scored = [self.res["files"][str(y)] for y in range(2010, 2025)]
        self.assertEqual(sum(i["rows"] for i in scored), 68020)
        self.assertEqual(sum(i["keys"] for i in scored), 87727)
        self.assertIn("68,020 unit rows, or 87,727 keys counted file by file", self.doc)

    def test_gates(self):
        g = self.res["gate_measures"]
        self.assertEqual((g["ref_rows"], g["rows_last_file"]), (7182, 4092))
        self.assertIn("| G3 | `facility-2024.csv` at least 3,000 rows; at least 50% of reference "
                      "keys in some file | 4,092 rows; 98.12% | yes |", self.doc)

    def test_predictions(self):
        m = self.res["measures"]
        self.assertEqual(m["ref_keys"], 7174)
        self.assertIn(f"{fmt(m['p1_keys_in_last_file'])} of 7,174 ({pct(m['p1_keys_in_last_file'], 7174)})", self.doc)
        self.assertEqual(m["p2_missing_from_last_file"], 7174 - m["p1_keys_in_last_file"])
        self.assertIn(f"{fmt(m['p2_missing_ret_or_ltcs'])} of {fmt(m['p2_missing_from_last_file'])} "
                      f"({pct(m['p2_missing_ret_or_ltcs'], m['p2_missing_from_last_file'])})", self.doc)
        self.assertIn(f"{fmt(m['p3_keys_in_union'])} of 7,174 ({pct(m['p3_keys_in_union'], 7174)})", self.doc)
        self.assertEqual(m["p4_symmetric_difference"], m["p4_f_minus_ref"] + m["p4_ref_minus_f"])
        self.assertIn(f"{m['p4_f_minus_ref']} + {m['p4_ref_minus_f']} = {m['p4_symmetric_difference']} "
                      f"({pct(m['p4_symmetric_difference'], 7174)})", self.doc)
        self.assertIn(f"{fmt(m['p5_retire_year_match'])} of {fmt(m['p5_ref_ret_keys_in_union'])} "
                      f"({pct(m['p5_retire_year_match'], m['p5_ref_ret_keys_in_union'])})", self.doc)
        self.assertEqual((m["union_keys"], m["rule_f_keys"]), (7152, 7151))
        self.assertIn("only 7,152 distinct keys", self.doc)
        self.assertIn("keeps 7,151 keys", self.doc)
        # every reference key found in a file is in rule F
        self.assertEqual(m["rule_f_keys"] - m["p4_f_minus_ref"], m["p3_keys_in_union"])
        self.assertEqual(m["ref_keys"] - m["p4_ref_minus_f"], m["p3_keys_in_union"])

    def test_differences(self):
        rep = self.res["reported"]
        self.assertEqual(rep["ref_minus_f"], {"OPR|not_in_files": 47, "RET|not_in_files": 88})
        self.assertIn("135 reference keys are in no file at all (47 OPR, 88 RET", self.doc)
        u = rep["unit_level"]
        self.assertEqual((u["ref_units"], u["in_union"]), (5637, 5515))
        self.assertIn("122 of the reference's 5,637 (plant, unit) pairs", self.doc)
        self.assertIn(f"5,515 do, {pct(5515, 5637)}", self.doc)
        self.assertIn("at least 122 of the 135", self.doc)
        self.assertIn("at most 13 are units", self.doc)
        self.assertEqual(rep["f_minus_ref_by_latest_class"], {"OPR": 94, "RET": 18})
        self.assertEqual(rep["f_minus_ref_by_latest_year"]["2024"], 66)
        self.assertIn("112 rule-F keys are not in the reference (94 latest-class OPR, 18 RET); "
                      "66 of them", self.doc)
        self.assertEqual(len(self.ref_minus), 135)
        self.assertEqual(len(self.f_minus), 112)
        refkeys = {(r["plant_id"], r["unit_id"], r["generator_id"]) for r in self.ref_minus}
        fkeys = {(r["plant_id"], r["unit_id"], r["generator_id"]) for r in self.f_minus}
        for k in (("2070", "1", ""), ("2070", "2", "")):
            self.assertIn(k, refkeys)
        for k in (("2070", "1", "1"), ("2070", "2", "2")):
            self.assertIn(k, fkeys)
        self.assertEqual(sum(1 for r in self.ref_minus if r["ref_status"] == "OPR"), 47)
        self.assertEqual(sum(1 for r in self.f_minus if r["latest_year"] == "2024"), 66)

    def test_status_and_dates(self):
        rep = self.res["reported"]
        self.assertEqual(rep["status_confusion_ref_vs_latest_class"],
                         {"LTCS|LTCS": 12, "LTCS|OPR": 23, "OPR|OPR": 5358, "OPR|RET": 1,
                          "RET|OPR": 390, "RET|RET": 1255})
        self.assertEqual(sum(rep["status_confusion_ref_vs_latest_class"].values()), 7039)
        self.assertIn("OPR/OPR 5,358, RET/RET 1,255, RET/OPR 390, LTCS/OPR 23, LTCS/LTCS 12, "
                      "OPR/RET 1", self.doc)
        self.assertEqual(rep["ret_retire_year_diff"], {"0": 1231, "derived_0": 390, "+1": 24})
        self.assertIn("1,231 get the reference's retirement year, 24 get one year later, and 390 get "
                      "none", self.doc)
        self.assertIn(f"1,231 of 1,255 ({pct(1231, 1255)})", self.doc)
        d = rep["opr_status_date_vs_commercial_operation_days"]
        self.assertEqual(d, {"0": 4013, ">7": 757, "2-7": 330, "1": 112, "unparsed": 36})
        total = sum(d.values())
        self.assertEqual(total, 5248)
        self.assertIn(f"5,248 reference OPR keys in the 2024 file, CAMD_STATUS_DATE equals the file's "
                      f"commercial operation date for 4,013 ({pct(4013, total)})", self.doc)
        self.assertIn("by 1 day for 112, by 2-7 days for 330 and by more for 757; 36 could not",
                      self.doc)

    def test_2025_build(self):
        r = self.res["reported"]["rule_f_2025"]
        self.assertEqual(r, {"keys": 7187, "new_vs_2024_rule_f": 36, "dropped_vs_2024_rule_f": 0,
                             "keys_first_seen_2025": 36})
        self.assertEqual(len(self.side25), 7187)
        self.assertEqual(7151 + 36, 7187)
        self.assertIn("7,187 keys: all 7,151 of the 2024 build plus 36 first seen in 2025, none dropped",
                      self.doc)
        self.assertEqual(sum(1 for r in self.side25 if r["first_year"] == "2025"), 36)

    def test_disclosure(self):
        for text in ("made with AI agents working in MV2's name",
                     "no person has checked these results by hand",
                     "[plan](easeyx-plan.md)", "camd-eia-crosswalk-latest/issues/7",
                     "Text and data CC BY 4.0; code Apache-2.0."):
            self.assertIn(text, self.doc)


if __name__ == "__main__":
    unittest.main()
