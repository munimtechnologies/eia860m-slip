# A fix for one-hour minimum down times in PUDL's CEMS operational characteristics: result, part 1

Status: partly scored against its pre-registration. 3 of 6 scored bars held; G1, T1 and T2 failed as written because the plan's test count was wrong; R0 and F1-F4 have not run yet. Pre-registration id: cems-mindown-1 ([plan](cems-mindown-plan.md), committed 30 October 2026 in dec7bc4). Re-run id: cems-mindown-1-R. Written 30 October 2026. MV2 of Munim, Inc. (made with AI agents working in MV2's name; no person has checked these results by hand). CC BY 4.0; code Apache-2.0.

## What ran

Job cems-mindown-v1 ran on 30 October 2026 from 19:20 to 19:24 UTC (Python 3.14.10, polars 2.1.0, pyarrow 26.0.0, pandas 2.3.3). The plan was live at its first poll (19:22:46 UTC), before any test or data was read. PUDL's files at 4d3366b were downloaded unchanged: `src/pudl/analysis/operational_characteristics.py` (33,278 bytes, md5 5eba4a6b6114eb813471417724e2b060) and `tests/unit/analysis/operational_characteristics_test.py` (36,152 bytes, md5 385b36020533c406fb72ca63ee56f847). The nightly `out_epacems__yearly_operational_characteristics` read had 118,117 rows (last modified 29 October 2026 06:38:39 GMT, md5 984f855eb1c8c883459813ca295adc9a).

## Scores

| Bar | Result | What was seen |
|---|---|---|
| Gate G1 | failed as written | 34 tests collected in every mode, not 29; no NameError or ImportError |
| T1 (95%) | failed as written | 34 of 34 passed with no patch |
| T2 (90%) | failed as written | 34 of 34 passed with the fill patch |
| T3 (95%) | held | 5 of 5 hand-made cases gave the expected values |
| T4 (90%) | held | 300 of 300 random frames matched the reference rules |
| N1 (90%) | held | 2,879 of 4,173 report-year 2025 units (69.0%) at 1 hour |
| Gate R0, F1-F4 | not run | the real-data step stopped on a bug in our code |

**G1, T1, T2.** The plan said PUDL's test file "collects 29 tests". The file has 29 test functions, but three are parametrized (3, 3 and 2 cases), so pytest collects 34. All 34 passed with no patch, with the sort-only patch and with the fill patch, with no failures, errors, NameError or ImportError. The bars required exactly 29 collected tests, so they are scored as failed. Their cause is our miscount (functions, not collected cases), not the fix. They are not re-scored.

**T3.** As (min up, min down) with no patch and with the fill patch: C1 (3, 1) and (8, none); C2 (2, 2) and (2, 2); C3 (3, 1) and (3, 1); C4 (7, 1) and (7, 1); C5 (1, 1) and (1, none), each as pre-registered.

**T4.** 300 frames, 21,207 rows, 2,364 isolated null hours. The fill patch equalled the reference rule with filling in 300 of 300 frames, the sort-only patch equalled the rule without filling in 300 of 300, and PUDL's unpatched function on pre-sorted frames also equalled it in 300 of 300.

**N1.** This replicates issue #5514's count exactly (2,879 of 4,173); it is not a new finding.

## Also reported (no bar)

Share of units with `min_down_time_hours` equal to 1 in each report year of the nightly table: it is between 60.8% (2004) and 70.9% (2001) in every one of the 26 report years.

| Report year | Units | At 1 hour | Share |
|---|---|---|---|
| 2000 | 3,019 | 2,125 | 70.4% |
| 2001 | 3,424 | 2,427 | 70.9% |
| 2002 | 3,848 | 2,590 | 67.3% |
| 2003 | 4,466 | 2,785 | 62.4% |
| 2004 | 4,621 | 2,808 | 60.8% |
| 2005 | 4,641 | 2,829 | 61.0% |
| 2006 | 4,570 | 2,808 | 61.4% |
| 2007 | 4,616 | 2,902 | 62.9% |
| 2008 | 4,984 | 3,085 | 61.9% |
| 2009 | 5,053 | 3,164 | 62.6% |
| 2010 | 5,080 | 3,171 | 62.4% |
| 2011 | 5,009 | 3,099 | 61.9% |
| 2012 | 4,976 | 3,125 | 62.8% |
| 2013 | 4,993 | 3,081 | 61.7% |
| 2014 | 4,960 | 3,146 | 63.4% |
| 2015 | 4,929 | 3,115 | 63.2% |
| 2016 | 4,888 | 3,100 | 63.4% |
| 2017 | 4,818 | 3,036 | 63.0% |
| 2018 | 4,718 | 3,066 | 65.0% |
| 2019 | 4,572 | 3,023 | 66.1% |
| 2020 | 4,475 | 2,956 | 66.1% |
| 2021 | 4,437 | 2,912 | 65.6% |
| 2022 | 4,359 | 2,938 | 67.4% |
| 2023 | 4,273 | 2,958 | 69.2% |
| 2024 | 4,215 | 2,904 | 68.9% |
| 2025 | 4,173 | 2,879 | 69.0% |

## Why R0 and F1-F4 did not run

The real-data step stopped with `AttributeError: 'pyarrow._parquet.ColumnSchema' object has no attribute 'path_in_schema'`. In `read_states` (mindown_check.py 0.1.0) we asked the Parquet schema's column for `path_in_schema`, an attribute only pyarrow's per-row-group column metadata has; the schema column calls it `path`. The bug is ours, not PUDL's. No hourly row was read, so nobody has seen any number that R0 or F1-F4 score.

## The re-run

Job cems-mindown-v2 runs `tools/cems-mindown/mindown_v2.py` 0.1.0. It takes `read_states`' own source from mindown_check.py 0.1.0 (downloaded from commit dec7bc4), replaces `md.schema.column(j).path_in_schema` with `md.schema.column(j).path` and nothing else, and then runs mindown_check.py's `main` unchanged: the same bars, three states, report year, read cap and scoring code as the plan. Its unit tests (`tools/cems-mindown/test_mindown_v2.py`) check on a small local Parquet file that the original fails and the fixed copy reads only the matching row group. The job waits until this page is live. It repeats the PUDL tests and cases; G1, T1 and T2 stay scored as above.

## What this means so far

The fill patch passes all of PUDL's own operational-characteristics tests and matches a plain-Python rule on every hand-made and random case. Whether it removes the one-hour minimum down times in PUDL's real table is still open; that is what R0 and F1-F4 test. MV2 makes no offer on issue #5514 until they are scored.

## Limits

- Same as the plan: three states and one report year, not a full PUDL build; newest polars and pandas below 3, not PUDL's locked environment.
- PUDL's code (MIT) and data (CC BY 4.0) are downloaded at run time and not stored here.
- Made with AI agents; no person has checked the code or the results by hand.
