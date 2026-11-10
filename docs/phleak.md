# What is in PUDL's uncleaned PHMSA gas distribution leaks table? (result of phleak-1)

Result of pre-registration phleak-1 ([plan](phleak-plan.md), live on this repository's main branch from 16:00:18 UTC on 10 November 2026, before the job read any data). The job `phleak-v1` ran `tools/phleak/phleak.py` 0.1.0 from the plan's commit on 10 November 2026, 21:46:36-21:46:42 UTC; its unit tests passed first.

MV2 of Munim, Inc., 10 November 2026 (UTC); made with AI agents working in MV2's name; no person has checked these results by hand. Text and data CC BY 4.0; code Apache-2.0.

**6 of the 7 predictions held (P1, P2, P4-P7); P3 failed, because there was nothing to test.** The sum test that [pudl#5435](https://github.com/catalyst-cooperative/pudl/issues/5435) asks for (the `total` leak source equals the sum of the other sources, for both severities) has no pairs to compare in the table as published. The `total` source has 10,085 rows, all from report years 1978-1983, and every one of them has a services count and no mains count. In those same reports and severities, no other source has a services count. So no report has both a total and any part in the same column, and the test could not be run once.

## Input

PUDL's nightly `_core_phmsagas__yearly_distribution_leaks` (CC BY 4.0, Catalyst Cooperative): md5 `59a2bf535b080bbd02043951227894cf`, 1,734,682 bytes, Last-Modified 10 Nov 2026 08:52:05 GMT. It has 633,659 rows in 89,114 reports, from report years 1970-2025. Values are PHMSA's, as operators reported them.

## Gates

| Gate | Measured | Held |
|---|---|---|
| G1 file and nine columns | no missing columns | yes |
| G2 rows and years | 633,659 rows; report years 1970-2025 | yes |
| G3 severity and source values | 2 severities; 13 sources, all in `LEAK_SOURCE_PHMSAGAS` | yes |

## Predictions

| Prediction (probability) | Bar | Measured | Held |
|---|---|---|---|
| P1 (70%) commodity only from 2015 | none before 2015; at most 1% missing from 2015 | 0 before 2015; 0 of 145,719 missing from 2015 | yes |
| P2 (75%) PUDL's install-decade commodity map covers every value | no unmapped value | 10 values, none unmapped | yes |
| P3 (55%) totals equal the sum of their sources within 1 | at least 95% of tested totals | 0 tested | no |
| P4 (80%) hazardous leaks do not exceed all leaks | at least 99% | 195,026 of 195,128 (99.95%) | yes |
| P5 (70%) the proposed primary key is unique | no duplicate rows | 0 duplicate rows | yes |
| P6 (70%) multi-state `operating_state` is an early problem | at least 100 rows, at least 95% up to 2003 | 2,544 rows, all 1984-2003 | yes |
| P7 (45%) no negative mains or services | no negative rows | 0 rows | yes |

**P3.** The sum test found 100,342 report-severity mains counts and 73,651 services counts with parts but no total, and 10,085 services totals with no part. A failed bar is reported as failed, so P3 counts as failed. The plan did not say what happens when nothing can be tested. The plan's limits section expected form changes to matter here, but not that the total and its parts are never reported in the same column.

## What else the table shows (reported, not scored)

- **Leak sources by era.** `construction_defect` 1970-2003; `material_defect` and `third_party` 1984-2003; `outside_force` 1990-2003; `equipment_failure`, `excavation_damage`, `incorrect_operation` and `natural_force_damage` 2004-2025; `corrosion_failure`, `other`, `other_outside_force` and `pipe_weld_joint_failure` 1970-2025; `total` 1978-1983.
- **Commodity values** (rows from 2015 on): Natural Gas 140,678; Propane Gas 4,126; Landfill Gas 363; Synthetic Gas 325; Hydrogen Gas 192; `OTHER GAS: Natural Gas` 25; `OTHER GAS: Propane` 4; `OTHER GAS: City of York` 3; `OTHER GAS: Other Gas - Propane` 2; `OTHER GAS: Nitrogen` 1. Two of them are newer than the list in #5435: `OTHER GAS: Propane` and `OTHER GAS: Other Gas - Propane`, both only in report year 2025. PUDL's existing install-decade map already sends both to `propane_gas`.
- **Null `operating_state`: 97,919 rows.** That is every row from 1970 to 1977, and also 15,140 of 15,158 rows in 1978 and 15,320 of 15,368 in 1979. After that come smaller counts, up to 1999 (most in 1991, 894 rows, and 1992, 852 rows). So the state is missing almost entirely through 1979, not only before 1978.
- **Other state values: 96 rows.** These are lower-case codes (`ar` 48, `az` 24, `ak` 6), `ky` with trailing spaces (6), `2` (6) and `PA7` (6).
- **Multi-state reports.** The 2,544 rows belong to 424 reports, listed in [data/phleak-multistate-reports.csv](../data/phleak-multistate-reports.csv).
- **Hazardous above all leaks: 102 cases, all from report years 2011-2014** (3 in 2011, 50 in 2012, 24 in 2013, 25 in 2014). They are listed in [data/phleak-hazardous-gt-all.csv](../data/phleak-hazardous-gt-all.csv). In 59 of them the all-leaks count is 0 and the hazardous count is above 0.
- **Operator id 0: 12,771 rows**, in 1976 (60), 1978 (15), 1980 (3,006), 1981 (2,916), 1982 (2,532) and 1983 (4,242). No operator id is null.
- **Severities.** `all_leaks` has 532,205 rows and `hazardous_leaks` 101,454. No row has both mains and services null.
- **Rows by year.** These are 11,500-14,300 from 2004 on, except 2010 (17,423) and 2011 (22,930). Why was not looked at.

## What this means for #5435

- The `subcomponents_sum_to_total` test cannot be written as #5435 describes for this table. There is no total next to its parts. In 1978-1983 the services counts exist only as a total. If they were dropped as "totals", those years would lose every services count. Documenting them in the metadata looks safer than dropping them.
- A dbt test that hazardous leaks do not exceed all leaks would fail 102 times, all in 2011-2014. That is a candidate for an `error_if` threshold or a metadata note.
- The commodity map, the proposed primary key and the negative-value check need no extra work on today's table. The `operating_state` cleanup covers 1978-1979 as well, and it also needs to cover the 96 lower-case or malformed codes.
- None of this has been checked against PHMSA's raw files or forms.

## Limits

- This profiles PUDL's intermediate table as published. It does not check PUDL's melt against PHMSA's raw files, so a missing total could come from the forms or from the extraction.
- PUDL's nightly table changes from night to night; the md5 and Last-Modified are above.
- The probabilities were our own before-the-fact guesses.

## Files

- [data/phleak-run.json](../data/phleak-run.json): the job's full output, unchanged.
- [data/phleak-hazardous-gt-all.csv](../data/phleak-hazardous-gt-all.csv), [data/phleak-multistate-reports.csv](../data/phleak-multistate-reports.csv) and [data/phleak-commodity.csv](../data/phleak-commodity.csv): the job's lists, unchanged. The sum-failure, duplicate-key and negative-row lists are empty and not added.
- [test_phleak_result.py](../test_phleak_result.py) checks every count on this page against those files.
