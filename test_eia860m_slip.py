"""Tests for eia860m_slip on hand-built changelogs. Apache-2.0.

Plans (RECORDS):
A  solar 100 MW: under construction (planned 2020-06) from 2020-01, testing from
   2020-04, operating from 2020-07 with operating date 2020-06-15: on time.
B  battery 50 MW: approved, planned 2020-03, in 2020-01; under construction,
   planned 2020-08, from 2020-02; operating 2020-09.
C  gas combined cycle 500 MW: permitting, planned 2020-12, from 2020-01; never built.
D  hydro, operating since 2010, reported 2022-03 (sets the last report month).

Retirements (RETIRE_RECORDS, plus D):
E  coal 600 MW: operating, planned retirement 2020-06, from 2020-01; retired
   record from 2020-07 with retirement date 2020-06-30: retired by plan.
F  gas steam 200 MW: planned retirement 2020-03 from 2020-01, pushed to 2021-01
   from 2020-03; never retires.
G  oil 50 MW: planned retirement 2020-02 from 2020-01; retired record from
   2020-11 with no date: retired 2020-11, 9 months late.
H  gas turbine 100 MW: planned retirement 2020-04 from 2020-01; leaves EIA-860M
   after the 2020-04 report (valid until 2020-05) with no retired record.

The tests need pandas (the tool does too). Where it is not installed they are
skipped, so a test host without pandas reports them as skipped, not failed.
"""

import unittest

try:
    import pandas as pd
    import eia860m_slip as s
except ImportError:  # no pandas on this host
    pd = None
    s = None

needs_pandas = unittest.skipIf(pd is None, "pandas is not installed")


def rec(plant, gen, report, valid, status, planned=None, op=None, mw=100.0,
        tech="Solar Photovoltaic", planned_ret=None, ret=None):
    return {"report_date": report, "valid_until_date": valid, "plant_id_eia": plant,
            "generator_id": gen, "capacity_mw": mw,
            "current_planned_generator_operating_date": planned,
            "generator_operating_date": op, "operational_status_code": status,
            "operational_status": None, "technology_description": tech,
            "fuel_type_code_pudl": None, "state": "CT",
            "planned_generator_retirement_date": planned_ret,
            "generator_retirement_date": ret}


RECORDS = [
    rec(1, "A", "2020-01-01", "2020-04-01", "U", planned="2020-06-01"),
    rec(1, "A", "2020-04-01", "2020-07-01", "TS", planned="2020-06-01"),
    rec(1, "A", "2020-07-01", None, "OP", op="2020-06-15"),
    rec(2, "B", "2020-01-01", "2020-02-01", "T", planned="2020-03-01", mw=50.0, tech="Batteries"),
    rec(2, "B", "2020-02-01", "2020-09-01", "U", planned="2020-08-01", mw=50.0, tech="Batteries"),
    rec(2, "B", "2020-09-01", None, "OP", op="2020-09-01", mw=50.0, tech="Batteries"),
    rec(3, "C", "2020-01-01", None, "L", planned="2020-12-01", mw=500.0,
        tech="Natural Gas Fired Combined Cycle"),
    rec(4, "D", "2022-03-01", None, "OP", op="2010-05-01", mw=20.0,
        tech="Conventional Hydroelectric"),
]

COAL, STEAM, OIL, CT = ("Conventional Steam Coal", "Natural Gas Steam Turbine",
                        "Petroleum Liquids", "Natural Gas Fired Combustion Turbine")
RETIRE_RECORDS = [
    rec(5, "E", "2020-01-01", "2020-07-01", "OP", op="1975-01-01", mw=600.0, tech=COAL,
        planned_ret="2020-06-01"),
    rec(5, "E", "2020-07-01", None, "RE", op="1975-01-01", mw=600.0, tech=COAL,
        ret="2020-06-30"),
    rec(6, "F", "2020-01-01", "2020-03-01", "OP", op="1980-01-01", mw=200.0, tech=STEAM,
        planned_ret="2020-03-01"),
    rec(6, "F", "2020-03-01", None, "OP", op="1980-01-01", mw=200.0, tech=STEAM,
        planned_ret="2021-01-01"),
    rec(7, "G", "2020-01-01", "2020-11-01", "OP", op="1970-01-01", mw=50.0, tech=OIL,
        planned_ret="2020-02-01"),
    rec(7, "G", "2020-11-01", None, "RE", op="1970-01-01", mw=50.0, tech=OIL),
    rec(8, "H", "2020-01-01", "2020-05-01", "OP", op="1990-01-01", mw=100.0, tech=CT,
        planned_ret="2020-04-01"),
    RECORDS[7],
]

JAN20 = 2020 * 12


def frame():
    return s.prepare(pd.DataFrame(RECORDS))


def retire_frame():
    return s.prepare(pd.DataFrame(RETIRE_RECORDS))


def by_group(rows):
    return {r["group"]: r for r in rows}


@needs_pandas
class HelperTests(unittest.TestCase):
    def test_months(self):
        m = s.months(["2020-01-01", None, "2021-12-31"])
        self.assertEqual(m[0], JAN20)
        self.assertTrue(m[1] != m[1])
        self.assertEqual(m[2], JAN20 + 23)
        self.assertEqual(s.month_str(JAN20 + 23), "2021-12")

    def test_outcome_edges(self):
        self.assertEqual(s.outcome(-3), "on_time")
        self.assertEqual(s.outcome(0), "on_time")
        self.assertEqual(s.outcome(1), "late_1_3")
        self.assertEqual(s.outcome(3), "late_1_3")
        self.assertEqual(s.outcome(4), "late_4_6")
        self.assertEqual(s.outcome(7), "late_7_12")
        self.assertEqual(s.outcome(12), "late_7_12")
        self.assertEqual(s.outcome(13), "not_online_12")
        self.assertEqual(s.outcome(float("nan")), "not_online_12")

    def test_tech_group_and_lead(self):
        self.assertEqual(s.tech_group("Solar Photovoltaic"), "solar")
        self.assertEqual(s.tech_group(" Onshore Wind Turbine "), "wind_onshore")
        self.assertEqual(s.tech_group("Natural Gas Steam Turbine"), "gas_other")
        self.assertEqual(s.tech_group("Conventional Steam Coal"), "coal")
        self.assertEqual(s.tech_group("Petroleum Liquids"), "oil")
        self.assertEqual(s.tech_group(None), "other")
        self.assertEqual(s.lead_bucket(0), "00-02")
        self.assertEqual(s.lead_bucket(5), "03-05")
        self.assertEqual(s.lead_bucket(12), "09-12")
        self.assertIsNone(s.lead_bucket(13))

    def test_table_labels(self):
        lines = s.table([{"a": 1, "b": None}], ["a", "b"], ["A", "B"])
        self.assertEqual(lines, ["| A | B |", "|---|---|", "| 1 |  |"])


@needs_pandas
class ChangelogTests(unittest.TestCase):
    def test_snapshot(self):
        snap = s.snapshot(frame(), JAN20 + 1)  # February 2020
        self.assertEqual(sorted(snap["key"]), ["1/A", "2/B", "3/C"])
        self.assertEqual(snap.set_index("key").loc["2/B", "status"], "U")

    def test_online_months(self):
        on = s.online_months(frame())
        self.assertEqual(on["1/A"], JAN20 + 5)
        self.assertEqual(on["2/B"], JAN20 + 8)
        self.assertEqual(on["4/D"], 2010 * 12 + 4)
        self.assertNotIn("3/C", on.index)

    def test_cohort_rows(self):
        c = s.cohorts(frame())
        # A: Jan-Mar (U) and Apr-Jun (TS); B: Jan (T) and Feb-Aug (U); C: Jan-Dec.
        self.assertEqual(len(c), 6 + 8 + 12)
        counts = c.groupby("key")["outcome"].value_counts().to_dict()
        self.assertEqual(counts[("1/A", "on_time")], 6)
        self.assertEqual(counts[("2/B", "late_4_6")], 1)
        self.assertEqual(counts[("2/B", "late_1_3")], 7)
        self.assertEqual(counts[("3/C", "not_online_12")], 12)
        a = c[c["key"] == "1/A"].set_index("report_m")
        self.assertEqual(a.loc[JAN20, "lead"], 5)
        self.assertEqual(a.loc[JAN20, "stage"], "construction")
        self.assertEqual(a.loc[JAN20 + 5, "stage"], "testing")
        self.assertEqual(a.loc[JAN20 + 5, "lead"], 0)

    def test_unresolved_plans_dropped(self):
        df = frame()
        # With the data ending 2021-12 instead of 2022-03, C's planned month
        # (2020-12) + 12 + 2 = 2022-02 has not resolved; A and B have.
        c = s.cohorts(df, last_m=JAN20 + 23)
        self.assertNotIn("3/C", set(c["key"]))
        self.assertEqual(len(c), 14)

    def test_summaries(self):
        c = s.cohorts(frame())
        overall = s.summarize(c)[0]
        self.assertEqual(overall["mw"], 7000.0)
        self.assertAlmostEqual(overall["on_time"], round(600 / 7000, 4))
        self.assertAlmostEqual(overall["late_1_3"], 0.05)
        self.assertAlmostEqual(overall["late_4_6"], round(50 / 7000, 4))
        self.assertAlmostEqual(overall["not_online_12"], round(6000 / 7000, 4))
        self.assertEqual(overall["generators"], 3)
        stage = by_group(s.summarize(c, "stage"))
        self.assertEqual(stage["construction"]["mw"], 650.0)
        self.assertAlmostEqual(stage["construction"]["on_time"], round(300 / 650, 4))
        self.assertEqual(stage["permitting"]["not_online_12"], 1.0)
        both = by_group(s.summarize(c, ["group", "stage"]))
        self.assertEqual(both["battery/approved"]["late_4_6"], 1.0)
        self.assertEqual(both["battery/construction"]["median_months_late_if_late"], 1.0)

    def test_annual(self):
        rows = s.annual(frame())
        y20 = {r["group"]: r for r in rows if r["year"] == 2020}
        self.assertEqual(y20["all"]["planned_mw"], 650.0)
        self.assertEqual(y20["all"]["planned_online_same_year_mw"], 150.0)
        self.assertEqual(y20["all"]["built_mw"], 150.0)
        self.assertEqual(y20["gas_cc"]["planned_online_share"], 0.0)
        self.assertEqual(y20["gas_cc"]["built_mw"], 0.0)
        y21 = [r for r in rows if r["year"] == 2021]
        self.assertEqual([r["group"] for r in y21], ["all"])
        self.assertEqual(y21[0]["planned_mw"], 0.0)
        self.assertIsNone(y21[0]["planned_online_share"])
        # 2022 has not closed (data end 2022-03).
        self.assertFalse([r for r in rows if r["year"] == 2022])

    def test_profile(self):
        df = frame()
        p = s.profile(list(pd.DataFrame(RECORDS).columns), df)
        self.assertEqual(p["generators"], 4)
        self.assertEqual(p["report_min"], "2020-01")
        self.assertEqual(p["report_max"], "2022-03")
        self.assertEqual(p["status_counts"]["OP"], 3)
        self.assertEqual(p["last_record_valid_until_set"], 0)
        self.assertEqual(p["operating_rows_with_planned_retirement"], 0)
        self.assertEqual(p["retired_rows"], 0)
        # C is still "permitting" for 2020-12, but that is only 15 months
        # before 2022-03, inside the 24-month grace; a 2019-12 plan would be stale.
        self.assertEqual(p["stale_planned_generators"], 0)
        old = pd.DataFrame(RECORDS[:6] + [rec(3, "C", "2019-01-01", None, "L",
                                              planned="2019-12-01", mw=500.0)] + RECORDS[7:])
        self.assertEqual(s.profile([], s.prepare(old))["stale_planned_generators"], 1)

    def test_no_retirements_in_plan_fixture(self):
        df = frame()
        self.assertTrue(s.retired_months(df).empty)
        self.assertEqual(len(s.retire_cohorts(df)), 0)


@needs_pandas
class RetirementTests(unittest.TestCase):
    def test_retired_months(self):
        ret = s.retired_months(retire_frame())
        self.assertEqual(ret["5/E"], JAN20 + 5)    # retirement date 2020-06-30
        self.assertEqual(ret["7/G"], JAN20 + 10)   # first retired report, 2020-11
        self.assertEqual(ret["8/H"], JAN20 + 3)    # last listed 2020-04, then left
        self.assertNotIn("6/F", ret.index)
        self.assertNotIn("4/D", ret.index)

    def test_detection(self):
        d = s.retire_detection(retire_frame())
        self.assertEqual(d, {"generators_with_retired_record": 2,
                             "retired_record_with_retirement_date": 1,
                             "operating_exits_without_retired_record": 1})

    def test_retire_cohort_rows(self):
        c = s.retire_cohorts(retire_frame())
        # E: Jan-Jun 2020; F: Jan-Feb (plan 2020-03) and Mar 2020-Jan 2021 (plan 2021-01);
        # G: Jan-Feb; H: Jan-Apr.
        self.assertEqual(len(c), 6 + 2 + 11 + 2 + 4)
        counts = c.groupby("key")["outcome"].value_counts().to_dict()
        self.assertEqual(counts[("5/E", "on_time")], 6)
        self.assertEqual(counts[("6/F", "not_online_12")], 13)
        self.assertEqual(counts[("7/G", "late_7_12")], 2)
        self.assertEqual(counts[("8/H", "on_time")], 4)
        e = c[c["key"] == "5/E"].set_index("report_m")
        self.assertEqual(e.loc[JAN20, "lead"], 5)
        self.assertEqual(e.loc[JAN20 + 5, "slip"], 0)

    def test_retire_unresolved_dropped(self):
        # Ending 2022-02, F's 2021-01 plan (+12 +2 = 2022-03) has not resolved.
        c = s.retire_cohorts(retire_frame(), last_m=JAN20 + 25)
        self.assertEqual(len(c), 6 + 2 + 2 + 4)

    def test_retire_summaries(self):
        c = s.retire_cohorts(retire_frame())
        overall = s.summarize(c)[0]
        self.assertEqual(overall["mw"], 6700.0)
        self.assertEqual(overall["generators"], 4)
        self.assertAlmostEqual(overall["on_time"], round(4000 / 6700, 4))
        self.assertAlmostEqual(overall["late_7_12"], round(100 / 6700, 4))
        self.assertAlmostEqual(overall["not_online_12"], round(2600 / 6700, 4))
        groups = by_group(s.summarize(c, "group"))
        self.assertEqual(groups["coal"]["on_time"], 1.0)
        self.assertEqual(groups["oil"]["median_months_late_if_late"], 9.0)
        self.assertEqual(groups["gas_other"]["not_online_12"], 1.0)

    def test_retire_annual(self):
        rows = s.retire_annual(retire_frame())
        y20 = by_group([r for r in rows if r["year"] == 2020])
        self.assertEqual(sorted(y20), ["all", "coal", "gas_ct", "gas_other", "oil"])
        self.assertEqual(y20["all"]["planned_mw"], 950.0)
        self.assertEqual(y20["all"]["planned_retired_same_year_mw"], 750.0)
        self.assertEqual(y20["all"]["planned_retired_share"], round(750 / 950, 4))
        self.assertEqual(y20["all"]["retired_mw"], 750.0)
        self.assertEqual(y20["gas_other"]["planned_retired_share"], 0.0)
        y21 = by_group([r for r in rows if r["year"] == 2021])
        self.assertEqual(sorted(y21), ["all", "gas_other"])
        self.assertEqual(y21["all"]["planned_mw"], 200.0)
        self.assertEqual(y21["all"]["retired_mw"], 0.0)
        self.assertFalse([r for r in rows if r["year"] == 2022])

    def test_retired_text_status(self):
        recs = [dict(r) for r in RETIRE_RECORDS]
        recs[1]["operational_status_code"] = None
        recs[1]["operational_status"] = "Retired"
        ret = s.retired_months(s.prepare(pd.DataFrame(recs)))
        self.assertEqual(ret["5/E"], JAN20 + 5)


if __name__ == "__main__":
    unittest.main()
