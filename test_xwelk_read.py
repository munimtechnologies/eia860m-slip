"""Checks that the "xwelk read" section of docs/xwcap.md reports what job xwelk-v1 wrote
(compete-results/xwelk-v1: stdout.txt and out/xwelk_*.csv), that it stays marked as not
pre-registered, and that the earlier scored text is kept. Reads text only, so it needs no polars.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))

# Copied from compete-results/xwelk-v1/stdout.txt (the job's summary print).
DOWNLOADS = [
    ("`core_eia860__scd_generators`", 7718170, "6c4372366df319de1888d8fc6ea1ec0e",
     "Tue, 03 Nov 2026 08:16:43 GMT"),
    ("`core_epa__assn_eia_epacamd`", 190240, "420d50a7e4d066d29eee909eab73d932",
     "Tue, 03 Nov 2026 08:16:48 GMT"),
    ("`out_epacems__yearly_operational_characteristics`", 3293502,
     "5c48a28ea3f927310b46dc673e392cf5", "Tue, 03 Nov 2026 08:19:15 GMT"),
    ("`core_eia923__monthly_generation`", 2629949, "3858b293a170f49cce21227da81a2718",
     "Tue, 03 Nov 2026 08:16:45 GMT"),
]
EPA_CSV = (2298091, "b7ec4b014ab66c2926f77ea86fa1ea16")
COUNTS = {"crosswalk_links": 21, "cems_operational": 31, "eia923_monthly": 0, "epa_rows": 3}
LINK_YEARS = (2018, 2024)
# From out/xwelk_cems_operational.csv, report year 2024: (unit, max_gross_load_mw, factor).
OPS_2024 = [(1, 204.0, 0.4), (2, 204.0, 0.4), (3, 205.0, 0.4)]
# Every max_gross_load_mw in out/xwelk_cems_operational.csv (31 rows).
MAX_LOADS = [197,  # 2015
             202, 199, 203, 202, 199, 203,  # 2016, 2017
             202, 205, 207, 207, 202, 205,  # 2018, 2019
             207, 204, 205, 202, 204, 204,  # 2020, 2021
             204, 204, 204, 203, 204, 204,  # 2022, 2023
             204, 204, 205, 204, 204, 205]  # 2024, 2025
# From out/xwelk_eia860_generators.csv, report year 2024.
ELK_MW, ELK_MIN, ENGINE_MIN = 199.8, 85.0, 3.7


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


class XwelkReadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs/xwcap.md")
        start = cls.doc.index("## The xwelk read (4 November 2026, not pre-registered)")
        cls.sec = cls.doc[start:cls.doc.index("## Limits")]

    def test_section_order_and_old_text_kept(self):
        self.assertLess(self.doc.index("## After scoring (not pre-registered)"),
                        self.doc.index("## The xwelk read"))
        for text in ("**All three gates held and 3 of 5 predictions held; P3 and P4 failed.**",
                     "plant 58835, \"Elk Station\"", "[Open Grid Emissions issue #262]"):
            self.assertIn(text, self.doc)

    def test_download_table(self):
        for name, size, md5, when in DOWNLOADS:
            self.assertIn("| %s | {:,} | %s | %s |".format(size) % (name, md5, when), self.sec)
        self.assertIn("| EPA `epa_eia_crosswalk.csv` at 3c7d672 | {:,} | {} | (pinned commit) |"
                      .format(*EPA_CSV), self.sec)

    def test_counts(self):
        years = LINK_YEARS[1] - LINK_YEARS[0] + 1
        self.assertEqual(3 * years, COUNTS["crosswalk_links"])
        self.assertIn("All %d crosswalk rows PUDL publishes for either plant"
                      % COUNTS["crosswalk_links"], self.sec)
        self.assertIn("one row per unit for each year %d to %d" % LINK_YEARS, self.sec)
        self.assertIn("No row links any CEMS unit to EIA plant 58835.", self.sec)
        self.assertIn("EPA's crosswalk file has exactly %d rows naming either plant"
                      % COUNTS["epa_rows"], self.sec)
        self.assertEqual(len(MAX_LOADS), COUNTS["cems_operational"])
        self.assertIn("have %d rows for EPA plant 57865" % COUNTS["cems_operational"], self.sec)
        self.assertIn("between %d and %d MW" % (min(MAX_LOADS), max(MAX_LOADS)), self.sec)
        self.assertEqual(COUNTS["eia923_monthly"], 0)
        self.assertIn("had no rows for either plant", self.sec)

    def test_turbine_figures(self):
        mins = [round(f * m, 1) for _, m, f in OPS_2024]
        self.assertIn("is %.1f to %.1f MW" % (min(mins), max(mins)), self.sec)
        self.assertIn("%.1f MW nameplate each" % ELK_MW, self.sec)
        self.assertIn("`minimum_load_mw` of %.1f MW for each of ELK1-ELK3 in 2024, and %.1f MW "
                      "for each of E01-E03" % (ELK_MIN, ENGINE_MIN), self.sec)
        self.assertAlmostEqual(345104.711 / 25581.5, 13.49, places=2)
        self.assertIn("about 13.5 times EIA's (345,104.7 against 25,581.5 MWh)", self.sec)

    def test_disclosure(self):
        self.assertIn("It tests no prediction; it only lists rows.", self.sec)
        self.assertIn("No person has checked this by hand", self.sec)
        self.assertNotIn("MIT License", self.doc)


if __name__ == "__main__":
    unittest.main()
