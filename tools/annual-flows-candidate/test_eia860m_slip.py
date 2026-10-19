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
H  gas turbine 100 MW: planned retirement 2020-04 from 2020-01; last listed in
   the 2020-04 report (PUDL: valid until 2020-04, inclusive, as its last record)
   with no retired record.

Annual flows (FLOW_RECORDS = RECORDS plus), for 2020:
K  solar 30 MW: planning, planned 2020-09; from 2020-10 planned 2021-06: slipped.
M  wind 70 MW: under construction, planned 2020-05; last listed 2020-08: not listed.
N  solar 20 MW: under construction, planned 2020-11; operating 2021-01: next months.
Q  battery 10 MW: testing, planned 2020-02; cancelled (CN) from 2020-03: other status.
R  solar 5 MW: planned 2020-04 in January, then operating with date 2019-11:
   online before the year.
S  solar 60 MW: first listed 2020-05, online 2020-08: new entry.
T  gas turbine 80 MW: planned 2021-03 in January, online 2020-12: pulled forward.
W  solar 15 MW: planned 2019-10 in January, online 2020-02: carried over.
X  oil 3 MW: listed operating in January 2020 with operating date 2020-01.

Re-key rule R (REKEY_RECORDS = RECORDS plus), for 2020; each plan generator is
in the January plan and has no record in force in February 2021 (not listed):
20/GT1 -> 21/" gt1"  combined cycle 300 MW, last listed 2020-03, the entry first
                     listed 2020-04 and online 2020-06: linked across plants, the
                     id compared trimmed and in any case.
22/PV1 -> 23/PV2     solar 40 MW, one month apart, another id: not linked.
24/WT  -> 25/WT      wind 9.9 MW, same month: under 10 MW, not linked.
26/B1  -> 27/B1      battery 50 MW, last listed 2020-02, entry first listed 2020-06:
                     4 months, not linked.
30/ST, 31/ST -> 32/ST  combined cycle, two 200 MW plan generators (last listed
                     2020-04 and 2020-03) and one entry (first listed 2020-05): the
                     lower key, 30/ST, is taken first and links; 31/ST stays not listed.

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


def named(r, name):
    return dict(r, plant_name_eia=name)


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
    rec(8, "H", "2020-01-01", "2020-04-01", "OP", op="1990-01-01", mw=100.0, tech=CT,
        planned_ret="2020-04-01"),
    RECORDS[7],
]

WIND = "Onshore Wind Turbine"
FLOW_RECORDS = RECORDS + [
    rec(11, "K", "2020-01-01", "2020-10-01", "P", planned="2020-09-01", mw=30.0),
    rec(11, "K", "2020-10-01", None, "P", planned="2021-06-01", mw=30.0),
    rec(10, "M", "2020-01-01", "2020-08-01", "U", planned="2020-05-01", mw=70.0, tech=WIND),
    rec(12, "N", "2020-01-01", "2021-01-01", "U", planned="2020-11-01", mw=20.0),
    rec(12, "N", "2021-01-01", None, "OP", op="2021-01-10", mw=20.0),
    rec(13, "Q", "2020-01-01", "2020-03-01", "TS", planned="2020-02-01", mw=10.0,
        tech="Batteries"),
    rec(13, "Q", "2020-03-01", None, "CN", mw=10.0, tech="Batteries"),
    rec(14, "R", "2020-01-01", "2020-02-01", "V", planned="2020-04-01", mw=5.0),
    rec(14, "R", "2020-02-01", None, "OP", op="2019-11-01", mw=5.0),
    rec(15, "S", "2020-05-01", "2020-09-01", "U", planned="2020-08-01", mw=60.0),
    rec(15, "S", "2020-09-01", None, "OP", op="2020-08-01", mw=60.0),
    rec(16, "T", "2020-01-01", "2020-12-01", "U", planned="2021-03-01", mw=80.0, tech=CT),
    rec(16, "T", "2020-12-01", None, "OP", op="2020-12-01", mw=80.0, tech=CT),
    rec(17, "W", "2020-01-01", "2020-03-01", "U", planned="2019-10-01", mw=15.0),
    rec(17, "W", "2020-03-01", None, "OP", op="2020-02-01", mw=15.0),
    rec(18, "X", "2020-01-01", None, "OP", op="2020-01-01", mw=3.0, tech=OIL),
]

CC, BAT = "Natural Gas Fired Combined Cycle", "Batteries"
REKEY_RECORDS = RECORDS + [
    named(rec(20, "GT1", "2020-01-01", "2020-03-01", "U", planned="2020-06-01", mw=300.0,
              tech=CC), "Old Site CC"),
    named(rec(21, " gt1", "2020-04-01", "2020-07-01", "U", planned="2020-06-01", mw=300.0,
              tech=CC), "Station"),
    named(rec(21, " gt1", "2020-07-01", None, "OP", op="2020-06-01", mw=300.0, tech=CC),
          "Station"),
    rec(22, "PV1", "2020-01-01", "2020-05-01", "U", planned="2020-09-01", mw=40.0),
    rec(23, "PV2", "2020-06-01", "2020-10-01", "U", planned="2020-09-01", mw=40.0),
    rec(23, "PV2", "2020-10-01", None, "OP", op="2020-09-01", mw=40.0),
    rec(24, "WT", "2020-01-01", "2020-05-01", "U", planned="2020-08-01", mw=9.9, tech=WIND),
    rec(25, "WT", "2020-05-01", "2020-09-01", "U", planned="2020-08-01", mw=9.9, tech=WIND),
    rec(25, "WT", "2020-09-01", None, "OP", op="2020-08-01", mw=9.9, tech=WIND),
    rec(26, "B1", "2020-01-01", "2020-02-01", "U", planned="2020-10-01", mw=50.0, tech=BAT),
    rec(27, "B1", "2020-06-01", "2020-11-01", "U", planned="2020-10-01", mw=50.0, tech=BAT),
    rec(27, "B1", "2020-11-01", None, "OP", op="2020-10-01", mw=50.0, tech=BAT),
    rec(30, "ST", "2020-01-01", "2020-04-01", "U", planned="2020-07-01", mw=200.0, tech=CC),
    rec(31, "ST", "2020-01-01", "2020-03-01", "U", planned="2020-07-01", mw=200.0, tech=CC),
    rec(32, "ST", "2020-05-01", "2020-08-01", "U", planned="2020-07-01", mw=200.0, tech=CC),
    rec(32, "ST", "2020-08-01", None, "OP", op="2020-07-01", mw=200.0, tech=CC),
]

JAN20 = 2020 * 12


def frame():
    return s.prepare(pd.DataFrame(RECORDS))


def retire_frame():
    return s.prepare(pd.DataFrame(RETIRE_RECORDS))


def flow_frame():
    return s.prepare(pd.DataFrame(FLOW_RECORDS))


def rekey_frame():
    return s.prepare(pd.DataFrame(REKEY_RECORDS))


def by_group(rows):
    return {r["group"]: r for r in rows}


def states(gens, kind):
    g = gens[(gens["kind"] == kind) & (gens["year"] == 2020)]
    return dict(zip(g["key"], g["state"]))


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
        self.assertEqual(p["last_record_in_force_at_report_max"], 4)
        self.assertEqual(p["last_record_one_month_long"], 0)
        self.assertEqual(p["first_report_with_capacity"], "2020-01")
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
class ValidityTests(unittest.TestCase):
    """PUDL's validity dates: exclusive between records, inclusive on a generator's last."""

    def test_listed_until(self):
        df = flow_frame()
        until = dict(zip(zip(df["key"], df["report_m"].astype(int)), df["until_m"]))
        self.assertEqual(until[("1/A", JAN20)], JAN20 + 2)       # next record starts 2020-04
        self.assertEqual(until[("10/M", JAN20)], JAN20 + 7)      # last record, listed to 2020-08
        self.assertEqual(until[("3/C", JAN20)], 2022 * 12 + 2)   # open: runs to the last report

    def test_last_record_inclusive(self):
        df = flow_frame()
        self.assertIn("10/M", set(s.snapshot(df, JAN20 + 7)["key"]))
        self.assertNotIn("10/M", set(s.snapshot(df, JAN20 + 8)["key"]))
        # M's plan (2020-05) is scored from its January to its May report: 5 rows.
        c = s.cohorts(df)
        self.assertEqual(int((c["key"] == "10/M").sum()), 5)

    def test_dropped_plan_rows_run_to_last_listing(self):
        recs = RECORDS + [rec(9, "J", "2020-01-01", "2020-06-01", "P", planned="2020-12-01",
                              mw=40.0)]
        c = s.cohorts(s.prepare(pd.DataFrame(recs)))
        j = c[c["key"] == "9/J"]
        self.assertEqual(len(j), 6)  # January to June, the last report that lists J
        self.assertEqual(int(j["report_m"].max()), JAN20 + 5)
        self.assertTrue((j["outcome"] == "not_online_12").all())

    def test_still_listed_not_an_exit(self):
        # PUDL's convention: a still-listed generator's last record is valid until the
        # last report month (2022-03 here), not open-ended.
        recs = [dict(r) for r in RETIRE_RECORDS]
        for r in recs:
            if r["valid_until_date"] is None:
                r["valid_until_date"] = "2022-03-01"
        df = s.prepare(pd.DataFrame(recs))
        ret = s.retired_months(df)
        self.assertNotIn("6/F", ret.index)
        self.assertNotIn("4/D", ret.index)
        self.assertEqual(ret["8/H"], JAN20 + 3)
        self.assertEqual(s.retire_detection(df)["operating_exits_without_retired_record"], 1)
        self.assertEqual(s.profile([], df)["last_record_in_force_at_report_max"], 4)


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


@needs_pandas
class FlowTests(unittest.TestCase):
    def test_plan_fates(self):
        f = s.plan_fates(flow_frame(), 2020).set_index("key")
        self.assertEqual(f["fate"].to_dict(), {
            "1/A": "online_in_year", "2/B": "online_in_year", "3/C": "stale",
            "11/K": "slipped", "10/M": "not_listed", "12/N": "online_next_months",
            "13/Q": "other_status", "14/R": "online_before_year"})
        self.assertEqual(f.loc["2/B", "band"], "approved")
        self.assertEqual(f.loc["11/K", "band"], "early")
        self.assertEqual(f.loc["10/M", "band"], "building")
        self.assertEqual(float(f["mw"].sum()), 785.0)

    def test_built_sources(self):
        b = s.built_sources(flow_frame(), 2020).set_index("key")
        self.assertEqual(b["source"].to_dict(), {
            "1/A": "in_plan", "2/B": "in_plan", "15/S": "new_entry", "16/T": "pulled_forward",
            "17/W": "carried_over", "18/X": "listed_not_planned"})
        self.assertEqual(float(b["mw"].sum()), 308.0)
        self.assertEqual(b.loc["16/T", "group"], "gas_ct")

    def test_annual_flows(self):
        result, gens = s.annual_flows(flow_frame())
        self.assertEqual(result["years"], [2020, 2021])
        self.assertEqual(result["pooled_years"], [2020, 2021])
        rows = {(r["year"], r["group"]): r for r in result["by_group"]}
        a = rows[(2020, "all")]
        self.assertEqual(a["planned_mw"], 785.0)
        self.assertEqual((a["online_in_year"], a["online_before_year"], a["online_next_months"],
                          a["slipped"], a["stale"], a["other_status"], a["not_listed"],
                          a["rekeyed_online"]),
                         (150.0, 5.0, 20.0, 30.0, 500.0, 10.0, 70.0, 0.0))
        self.assertEqual(a["delivered_share"], round(150 / 785, 4))
        self.assertEqual((a["built_mw"], a["in_plan_mw"], a["new_entry"], a["rekeyed"],
                          a["pulled_forward"], a["carried_over"], a["listed_not_planned"]),
                         (308.0, 150.0, 60.0, 0.0, 80.0, 15.0, 3.0))
        self.assertEqual(a["joined_share"], round(158 / 308, 4))
        sol = rows[(2020, "solar")]
        self.assertEqual((sol["planned_mw"], sol["built_mw"]), (155.0, 175.0))
        bands = {(r["year"], r["band"]): r for r in result["by_band"]}
        self.assertEqual(bands[(2020, "early")]["planned_mw"], 530.0)
        self.assertEqual(bands[(2020, "building")]["planned_mw"], 205.0)
        self.assertEqual(bands[(2020, "approved")]["delivered_share"], 1.0)
        # 2021: K, re-dated to 2021-06, is January 2021's whole plan, still planned in
        # February 2022; N came online in January 2021, already listed as operating.
        b21 = rows[(2021, "all")]
        self.assertEqual((b21["planned_mw"], b21["stale"]), (30.0, 30.0))
        self.assertEqual((b21["built_mw"], b21["listed_not_planned"]), (20.0, 20.0))
        pooled = {(r["group"], r["band"]): r for r in result["pooled"]}
        self.assertEqual(pooled[("all", "all")]["planned_mw"], 815.0)
        self.assertEqual(pooled[("all", "all")]["built_mw"], 328.0)
        everything = result["by_group"] + result["by_band"] + result["pooled"]
        self.assertTrue(all(r["plan_identity_ok"] for r in everything))
        self.assertTrue(all(r.get("built_identity_ok", True) for r in everything))
        self.assertEqual(sorted(set(gens["kind"])), ["built", "plan"])
        self.assertEqual(len(gens), 8 + 6 + 1 + 1)
        # M (wind, 70 MW, not listed) has no new entry of its group: rule R links nothing.
        self.assertEqual(result["links"], [])
        self.assertEqual([r["links"] for r in result["links_by_year"]], [0, 0])


@needs_pandas
class RekeyTests(unittest.TestCase):
    """Rule R (docs/annual-flows-preregistration-v2.md), check K1."""

    @classmethod
    def setUpClass(cls):
        cls.result, cls.gens = s.annual_flows(rekey_frame())
        cls.plan = states(cls.gens, "plan")
        cls.built = states(cls.gens, "built")

    def test_cross_plant_rekey(self):
        self.assertEqual(self.plan["20/GT1"], "rekeyed_online")
        self.assertEqual(self.built["21/ gt1"], "rekeyed")
        link = self.result["links"][0]
        self.assertEqual(link, {"year": 2020, "plan_key": "20/GT1", "plan_plant": "Old Site CC",
                                "entry_key": "21/ gt1", "entry_plant": "Station",
                                "group": "gas_cc", "plan_mw": 300.0, "entry_mw": 300.0,
                                "last_listed": "2020-03", "first_listed": "2020-04",
                                "months_apart": 1})

    def test_same_capacity_other_id_not_linked(self):
        self.assertEqual(self.plan["22/PV1"], "not_listed")
        self.assertEqual(self.built["23/PV2"], "new_entry")

    def test_under_10_mw_not_linked(self):
        self.assertEqual(self.plan["24/WT"], "not_listed")
        self.assertEqual(self.built["25/WT"], "new_entry")
        info = s.listing(rekey_frame())
        self.assertEqual(info.loc["25/WT", "first_m"] - info.loc["24/WT", "last_m"], 0)

    def test_gap_of_4_months_not_linked(self):
        self.assertEqual(self.plan["26/B1"], "not_listed")
        self.assertEqual(self.built["27/B1"], "new_entry")
        info = s.listing(rekey_frame())
        self.assertEqual(info.loc["27/B1", "first_m"] - info.loc["26/B1", "last_m"], 4)

    def test_equal_plan_generators_compete(self):
        self.assertEqual(self.plan["30/ST"], "rekeyed_online")
        self.assertEqual(self.plan["31/ST"], "not_listed")
        self.assertEqual(self.built["32/ST"], "rekeyed")
        self.assertEqual([(x["plan_key"], x["entry_key"]) for x in self.result["links"]],
                         [("20/GT1", "21/ gt1"), ("30/ST", "32/ST")])

    def test_entry_order(self):
        # One plan generator, three free entries with its id: the smallest capacity
        # difference wins, then the smallest gap.
        fates = pd.DataFrame([(2020, "1/X", "solar", "building", 100.0, "not_listed")],
                             columns=["year", "key", "group", "band", "mw", "fate"])
        built = pd.DataFrame([(2020, "2/X", "solar", 100.04, "new_entry"),
                              (2020, "3/x", "solar", 100.0, "new_entry"),
                              (2020, "4/X", "solar", 100.0, "new_entry"),
                              (2020, "5/X", "solar", 100.0, "in_plan")],
                             columns=["year", "key", "group", "mw", "source"])
        info = pd.DataFrame({"gen": ["x"] * 5,
                             "first_m": [JAN20, JAN20 + 3, JAN20 + 5, JAN20 + 4, JAN20 + 3],
                             "last_m": [JAN20 + 2] * 5, "name": [""] * 5},
                            index=["1/X", "2/X", "3/x", "4/X", "5/X"])
        links = s.rekey_links(fates, built, info)
        self.assertEqual([(x["entry_key"], x["months_apart"]) for x in links], [("4/X", 2)])

    def test_rekey_totals(self):
        rows = {(r["year"], r["group"]): r for r in self.result["by_group"]}
        a = rows[(2020, "all")]
        self.assertEqual(a["planned_mw"], 1449.9)
        self.assertEqual((a["online_in_year"], a["stale"], a["not_listed"], a["rekeyed_online"]),
                         (150.0, 500.0, 299.9, 500.0))
        self.assertEqual(a["delivered_share"], round(650 / 1449.9, 4))
        self.assertEqual((a["built_mw"], a["in_plan_mw"], a["new_entry"], a["rekeyed"]),
                         (749.9, 150.0, 99.9, 500.0))
        cc = rows[(2020, "gas_cc")]
        self.assertEqual((cc["planned_mw"], cc["rekeyed_online"], cc["not_listed"]),
                         (1200.0, 500.0, 200.0))
        everything = self.result["by_group"] + self.result["by_band"] + self.result["pooled"]
        self.assertTrue(all(r["plan_identity_ok"] for r in everything))
        self.assertTrue(all(r.get("built_identity_ok", True) for r in everything))
        # January 2021 plans nothing here, so 2020 is the only year with fates.
        self.assertEqual(self.result["years"], [2020])
        self.assertEqual(self.result["links_by_year"],
                         [{"year": 2020, "links": 2, "plan_mw": 500.0, "entry_mw": 500.0}])

    def test_link_records(self):
        recs = s.link_records(rekey_frame(), self.result["links"])
        self.assertEqual([(r["plant_id_eia"], r["report_date"]) for r in recs],
                         [("20", "2020-01-01"), ("21", "2020-04-01"), ("21", "2020-07-01"),
                          ("30", "2020-01-01"), ("32", "2020-05-01"), ("32", "2020-08-01")])
        self.assertEqual(recs[0]["plant_name_eia"], "Old Site CC")
        self.assertEqual(recs[3]["plant_name_eia"], "")
        self.assertEqual(recs[2]["valid_until_date"], "")


if __name__ == "__main__":
    unittest.main()
