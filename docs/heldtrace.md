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

## Update, 22 October 2026: the November 2024 gap is in EIA's own file

Compete job `retiredgap-v1` ran `tools/annual-flows-candidate/retiredgap.py` 0.1.0 (7 of 7 unit tests passed first). It read the October, November and December 2024 workbooks from PUDL's archive (`eia860m-2024.zip`, Zenodo record 22995197) and downloaded the same three months from EIA's own archive pages on 22 October 2026. Raw output, unchanged: [`retiredgap-v1-output.md`](retiredgap-v1-output.md), [`../data/retiredgap_v1.json`](../data/retiredgap_v1.json) and the unit-test log [`retiredgap-v1-unittests.txt`](retiredgap-v1-unittests.txt). This answers the open question in the second note on the rebuilt changelog above.

- **PUDL's copies are EIA's files, byte for byte.** For each of the three months the archived workbook and EIA's have the same size and md5 (November 2024: 12,251,506 bytes, md5 fc902dbcf91640cb465edbda03a9ed7d). The gap is in the November 2024 workbook that EIA still serves, not in PUDL's archive or in this repository's reader.
- **282 generators listed in October 2024 are not in November's file; 279 are listed again in December.** None of the 279 is in EIA's own November file. The 282 equals heldtrace-v2's count from the archive.
- **No other month comes close.** In the other 133 months of the rebuilt changelog, at most 14 generators come back in a month (August 2021); December 2024 has 283.
- **Nearly all are long-retired generators.** On October's sheets, 277 of the 279 are Retired and 2 Planned; on December's, 277 Retired and 2 Operating. The Retired sheet has 6,715 rows in October, 6,445 in November and 6,746 in December. By December's retirement years, these 277 retired between 2002 and 2014, 241 of them in 2011 to 2014 (2013: 120; 2014: 75); the 2 operating ones have none.
- **About 5.5 GW.** The 279 sum to 5,543.6 MW of nameplate capacity in December's rows (the two operating ones included). The most common technologies are petroleum liquids (71), conventional hydroelectric (36), landfill gas (36) and conventional steam coal (34); the most common states are Maine (30), California (25) and Texas (24).

EIA's EIA-860M page says that from March 2017 data the Retired tab "includes a comprehensive list of generators which retired since 2002", and that estimates "will be corrected without specific acknowledgment or explanation in subsequent month's inventory". The December 2024 file lists these generators again; the November 2024 file, as EIA served it on 22 October 2026, does not.

What it means for users: a count or sum of retired generators taken from the November 2024 workbook alone leaves these 277 out (and the 2 planned units drop out of that month's planned list); October's or December's file lists them. In the rebuilt changelog, their November 2024 "left" rows and December 2024 "back" rows record this gap in EIA's file, not changes at the plants.

Limits: why EIA's November file leaves them out, and what became of the other 3 of the 282, has not been checked. How PUDL's changelog treats these two months has not been checked either. No person has yet opened the November 2024 file by hand to confirm a sample of the 279; the job's key lists are in the raw output for anyone who wants to.

## Update, 22 October 2026 (evening): every generator that left the workbook, 2015-2026

Compete job `gapcensus-v1` ran `tools/annual-flows-candidate/gapcensus.py` 0.1.0 (12 of 12 unit tests passed first) on the same 134 monthly workbooks with `history.py` 0.1.0's reader and event rule, and on the same PUDL file. Raw output, unchanged: [`gapcensus-v1-output.md`](gapcensus-v1-output.md), [`../data/gapcensus_v1.json`](../data/gapcensus_v1.json), every left event in [`../data/gapcensus_left_events.csv`](../data/gapcensus_left_events.csv) and the unit-test log [`gapcensus-v1-unittests.txt`](gapcensus-v1-unittests.txt). It answers two of the limits of the update above.

- **The rebuilt changelog reproduces.** Rebuilt from the workbooks, its text equals the published copy line for line: 117,111 lines, 117,110 rows. The same code wrote both, so this is a reproducibility check, not an independent one. EIA's own August 2026 file (13,955,142 bytes, md5 9727ac867236faab7d5503175dacdf38) is byte-identical to the archive's copy.
- **2,521 times a generator left the workbook**: from the Operating sheet 441, Planned 1,517 and Retired 563 (its sheet the month before). 1,908 of them were not listed again by August 2026. "Left" means listed on no sheet the changelog reads, so a planned unit moved to the Canceled or Postponed sheet counts as left.
- **November 2024 is the only large one-month gap.** Generators were missing for exactly one month 439 times, in 73 different months. November 2024 holds 279 of them; no other month more than 13 (July 2021). In all 439, PUDL's changelog has a record in force for the generator in the missing month, so it carries the generator through the gap.
- **The other 3 of November 2024's 282.** November's file lists 280 of the 282 on no sheet at all and 2 on the Canceled or Postponed sheet (which 2 has not been checked). 67691/731 (18.9 MW, planned) was listed again in July 2025 and left again in August 2025. 59806/SOLAR (101 MW, planned) and 67190/FBESS (100 MW, operating in October 2024) were not listed again by August 2026.
- **Some generators leave the Retired sheet for good.** A generator left the Retired sheet 563 times: 281 times it was back the next month (277 of them in December 2024) and 279 times it was not listed again by August 2026. 238 of those 279 left in March 2017, the month from which EIA's page says the Retired tab "includes a comprehensive list of generators which retired since 2002". The other 41 left later, 23 of them at one plant (1439) in January 2024.

Limits: whether the 238 retired before 2002, which would make March 2017 EIA's documented change of scope rather than a loss, and whether the 41 later ones were renamed rather than dropped, have not been checked; job `retiredscope-v1` reads their rows. "Not listed again" is by plant and generator ID, so a renamed generator counts as not listed again. No person has opened the workbooks by hand to confirm these counts.

## Update, 22 October 2026 (night): the generators that leave the Retired sheet for good

Compete job `retiredscope-v1` ran `tools/annual-flows-candidate/retiredscope.py` 0.1.0 (6 of 6 unit tests passed first) with `retiredgap.py` 0.1.0's sheet reader on 22 workbooks from the same archive: February and March 2017, and the month before and the month of each later departure. For 4 of them (February and March 2017, December 2023 and January 2024) it also downloaded EIA's own file; each is byte-identical to the archive's copy. Raw output, unchanged: [`retiredscope-v1-output.md`](retiredscope-v1-output.md), [`../data/retiredscope_v1.json`](../data/retiredscope_v1.json), [`../data/retiredscope_leavers.csv`](../data/retiredscope_leavers.csv), [`../data/retiredscope_2017_03_left.csv`](../data/retiredscope_2017_03_left.csv) and the unit-test log [`retiredscope-v1-unittests.txt`](retiredscope-v1-unittests.txt). It answers the limits of the update above.

- **March 2017 is EIA's documented change of scope, not a loss.** February 2017's Retired sheet has 3,380 generators, 238 of them retired before 2002; March 2017's has 4,147, none retired before 2002. The 238 that left are exactly February's pre-2002 ones (retired 1950 to 2001, 121 of them in 2001; 3,208.4 MW), and March's file lists none of them on any sheet. In the same month 930 generators retired in 2002 or later (12,249.8 MW) entered the Retired sheet from no sheet, and 75 moved to it from another sheet; all 3,142 of February's others are still on it. This is what EIA's page describes: from March 2017 data the tab "includes a comprehensive list of generators which retired since 2002".
- **The 41 later departures are inside that scope.** All 41 retired in 2002 or later (2002 to 2023) by the sheet's own retirement years, and each was on the Retired sheet the month before it left. 40 of them are on no sheet of that month's file; 1 (63740/ONT6, a 2.2 MW solar unit retired in 2020) moved to the Canceled or Postponed sheet, which the changelog does not read. None is listed again on the changelog's sheets by August 2026. They sum to 1,350.3 MW of nameplate capacity on the sheet the month before (23 have no MW there).
- **Few look like renamings.** In 40 of the 41, the plant has no generator in the later month that it did not have the month before. The exception is 7922/6 (2 MW petroleum liquids, retired 2011, left January 2023): that month its plant's only listed generator is a new 7922/7 (Operating, 2.3 MW). Whether that is the same unit under a new ID has not been checked.
- **They cluster in a few plants and months.** 23 generators at plant 1439 (natural gas internal combustion engines, Louisiana, retired November 2023 by the sheet, no MW given) left in January 2024. 5 at plants 1571 and 1572 (conventional steam coal, Maryland, retired in 2020 and 2021; 1,316 MW) left in December 2021. 5 at plant 955 (Illinois, retired 2002 to 2011) left in March 2025. The other 8 left one at a time, in 8 different months. For 6 of the 41, no generator of the plant is listed on the changelog's sheets in the month it left.

What it means for users: March 2017's 238 are EIA's documented change of scope. The 41 are not explained by it: a count of generators retired since 2002 taken from a monthly Retired sheet after they left misses about 1.35 GW, most of it five Maryland coal units. EIA's page says estimates "will be corrected without specific acknowledgment or explanation in subsequent month's inventory", so some of these may be corrections; the files do not say.

Limits: whether EIA's annual EIA-860 (final 2025 data, released 10 September 2026) still lists the 41 as retired, and whether they appear under another plant ID, has not been checked; job `annual860-v1` is queued to read the annual files for 2020 to 2025. Three 196 MW units at plant 1572 and the paired A and B units at plant 1439 could be duplicate entries that EIA removed; that has not been checked either. No person has opened the workbooks by hand.
