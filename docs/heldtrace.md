# Where the twenty-ninth test's misses come from (heldtrace, 22 October 2026)

Status: descriptive follow-up, no prediction tested. The twenty-ninth result ([`history-revert.md`](history-revert.md)) is unchanged: 4 of 5 predictions held and P5 stays failed.

MV2 of Munim, Inc. (made with AI agents working in his name). Code: Apache-2.0. Text and data: CC BY 4.0.

## Question

The twenty-ninth result found that PUDL's EIA-860M changelog (`core_eia860m__changelog_generators`) and EIA's own monthly workbooks disagree on status, planned month or MW in 17,193 generator-months from July 2015 to August 2026, and that a simulation of `make_changelog`'s rule (drop a record equal to any earlier record of the generator), fed only the workbooks, gives PUDL's value in 15,901 of them. Of the rest, most (1,151 generator-months) are values PUDL held in an earlier record. They made P5 fail in 2017-2019. This note asks where they come from.

## What ran

Compete job `heldtrace-v2` ran `tools/annual-flows-candidate/heldtrace.py` 0.1.0 (6 of 6 unit tests passed first) with `history.py` 0.1.0's reader and simulation on the same 134 monthly workbooks (Zenodo record 22995197) and the same PUDL file (2,631,992 bytes, file time 15 October 2026, latest report 2026-08). The first job, `heldtrace-v1`, stopped at its unit tests on a test-fixture error and read no data.

Raw output, unchanged: [`heldtrace-v2-output.md`](heldtrace-v2-output.md), [`../data/heldtrace_v2.json`](../data/heldtrace_v2.json), [`../data/heldtrace_pudl_rows.csv`](../data/heldtrace_pudl_rows.csv) (PUDL's full rows for the traced generators) and the unit-test log [`heldtrace-v2-unittests.txt`](heldtrace-v2-unittests.txt). [`../test_heldtrace_doc.py`](../test_heldtrace_doc.py) checks every number here against them.

The replay reproduces history-v1: its counts by kind equal history-v1's in all 12 years (15,901 reproduced by the simulation, 141 with the workbook's value in a later PUDL record, 1,151 held before, 0 other).

## Findings

**1. Every stale value is a value EIA published.** In all 17,193 disagreeing generator-months, the workbook for the month in which PUDL's record in force was reported showed that record's status, planned month and MW (a field missing on either side is not compared). PUDL does not show values EIA never published; it keeps one EIA published earlier and later changed.

**2. The "held before" misses come from the same rule, applied to more columns.** `make_changelog` drops a record that equals an earlier record of the generator in every column except `report_date`; the table's columns include coordinates, balancing authority and summer and winter capacity. The simulation compared only status, planned month and nameplate MW. So when a generator returns to an earlier status while some other column has changed, PUDL keeps the record (as a whole it is new) and the simulation drops it. When the status later flips back to one whose full row PUDL already holds, PUDL drops that record and the earlier status stays in force. In all 1,151 "held before" generator-months, an earlier PUDL record of the generator equals the workbook's value. In 1,103 of them the simulation holds the workbook's value itself, so it marks nothing stale; in 48 it is stale at a third value.

Two of the 11 traced generators, month by month in the raw output:

- **Bonneville unit 11** (plant 3075, generator 11; 66.5 MW hydro, Oregon). PUDL's records from December 2015 (the first with coordinates) to the one reported in July 2016 give its longitude as -121.941009; from March 2017 on, -121.941. The March 2017 record is OP. In April 2017 the workbook went back to OA: the simulation dropped it as a return, but PUDL kept it because the longitude was new. The workbook then lists the unit as OP in 92 of the 109 months from August 2017 to August 2026, and PUDL has no record for any of them, which is what `make_changelog` does when the row equals its March 2017 record in every column. PUDL's April 2017 OA record is still in force at the latest report (2026-08): 92 "held before" generator-months for this one unit.
- **Lower Granite unit 2** (plant 6175, generator 2; 135 MW hydro, Washington). PUDL's March 2018 record is OP with summer capacity 127 MW; every earlier record gives 135 MW. In December 2019 the workbook went back to OA with the same status, planned month and nameplate MW as in February 2018, so the simulation dropped it, but OA with a 127 MW summer rating was new, so PUDL kept it. PUDL has no record after December 2019, though the workbook lists the unit as OP again from January 2021: 53 "held before" generator-months.

**3. A few hydro plants hold most of them.** Four plants of the U.S. Army Corps of Engineers' Northwestern Division, John Day (3082), Bonneville (3075), Ice Harbor (3925) and Lower Granite (6175), account for 585 of the 1,151 "held before" generator-months; with plants 57949 and 3655 (Olmstead), the top six account for 789.

## Two notes on the rebuilt changelog

The same run counted the rows of the rebuilt changelog ([`eia860m-changelog-from-workbooks.md`](eia860m-changelog-from-workbooks.md)) month by month.

- **April 2016 holds 24,427 of 2016's 27,603 "changed" rows.** It is the first workbook with nameplate MW: the traced units have no MW through March 2016 and their nameplate MW from April (Bonneville 11: 66.5 MW). Those rows record the column appearing, not changes at the plants.
- **283 of 2024's 313 "back" rows are in December 2024**, after 282 generators left the November 2024 workbook. Why they were missing from that workbook as read is not yet known; it has not been checked against EIA's own site.

## Limits

- The mechanism in finding 2 is shown for the traced generators and follows from the rule; the columns that differ have not yet been counted for all 1,151 generator-months.
- Only status, planned month and nameplate MW are compared with the workbooks. PUDL's other columns were read only for the traced generators, which were chosen from the plants with most "held before" generator-months and from earlier examples, not at random.
- This says nothing about why EIA's coordinates or ratings changed.

## What it means for users of the changelog

In every disagreement, PUDL's record matches EIA's workbook for the month it was reported; what goes wrong is which record stays in force afterwards. A changelog that compares each record only with the previous record of the same generator would keep these returns. Until then, the rebuilt changelog in this repository gives month-to-month values from EIA's own workbooks.

## Update, 22 October 2026: which columns let a returning value back in

Compete job `keptreturn-v1` ran `tools/annual-flows-candidate/keptreturn.py` 0.1.0 (3 of 3 unit tests passed first) on the same PUDL file. It reads PUDL's table only, no workbooks. A kept return is a record whose status, planned month and nameplate MW differ from the previous record's but equal an earlier record's; `make_changelog` can only have kept it because some other column differs. For each one, the job lists the columns that differ from the latest earlier record with the same three values. Raw output, unchanged: [`keptreturn-v1-output.md`](keptreturn-v1-output.md), [`../data/keptreturn_v1.json`](../data/keptreturn_v1.json) and the unit-test log [`keptreturn-v1-unittests.txt`](keptreturn-v1-unittests.txt).

This answers the first limit above only in part. It counts the kept returns, not the 1,151 "held before" generator-months they lead to, and one kept return can lead to none or to many.

- **442 kept returns** in 224,408 records of 39,903 generators. Every one differs from that earlier record in at least one other column (0 with none), as the rule requires; this is a consistency check, not a new finding. 196 of them are the generator's last record in the table.
- **The rounded longitude is not the usual cause.** Longitude differs in 63 of the 442. The most common columns are winter capacity (137), utility name (117) and summer capacity (115); a return can count under several. The most common sets are summer and winter capacity together (86), utility name alone (55), longitude alone (34) and utility ID and name together (32).
- **The traced generators match the trace above.** Bonneville 11 (3075/11), John Day 2 (3082/2) and Ice Harbor 1 (3925/1) each have one kept return, OA in April 2017, that differs from their July 2016 record in longitude only. Olmstead 1 (3655/1) has one, OP in July 2017, also longitude only against July 2016. Lower Granite 2 (6175/2) has one, OA in December 2019, that differs from its March 2017 record in summer and winter capacity.
- **They keep happening.** 2025 and 2026 (to August 2026) hold 71 and 81 of the 442, more than any earlier year; January 2026 alone holds 37, the most of any month. 2017 holds 44, April 2017 16 of them. Why January 2026 has so many has not been checked.

What this adds: a returning status, planned month or MW gets back into PUDL's table only when some unrelated column changes in the same month, most often a capacity rating or the utility's name. When nothing else changes, the return is dropped and the earlier value stays in force (the case the simulation reproduces); when a return was kept, a later return to a full row the table already holds is dropped instead (finding 2). Kept returns run through 2025 and 2026, so this is not a one-off from the coordinates rounded in 2017.
