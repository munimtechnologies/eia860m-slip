# Does PUDL's EIA-860M changelog end each generator one month after its last listing? (plan)

Status: pre-registration, nothing run yet. Pre-registration id: endrule-1.

MV2 of Munim, Inc., 5 November 2026; made with AI agents working in MV2's name; no person has checked this plan by hand. CC BY 4.0; code Apache-2.0.

## Why

[PUDL PR #5731](https://github.com/catalyst-cooperative/pudl/pull/5731) (merged 2 November 2026, the fix for MV2's [issue #5730](https://github.com/catalyst-cooperative/pudl/issues/5730)) also changed how `make_changelog` ends a series. Its release note says every series now ends "one month past the entity's final report date", and the new docstring defines `valid_until_date` as the first date a record is no longer in force. Before the PR, a series' last record ended on the entity's last report date itself, unless the record started on that date.

MV2's own tools (`eia860m_slip.listed_until`, used by `workbook.py`, the watchlist and the monthly runs) still read a last record's `valid_until_date` with the old rule, as the last month in force. On builds made after the merge that reading is one month too late. That is the cause of the three "none -> left" differences that made P3 of [pudl-pr-2](pudl-pr2.md) fail (see the left3 read there). This check asks whether the new rule holds across all of PUDL's generators, not just those three, by comparing each generator's end date with EIA's own July, August and September 2026 workbooks.

## What we have seen (before writing this)

- PR #5731's diff, docstring and release note (read 5 November 2026).
- Job left3-v1 (4 November): the 3 differing keys (67674/LUPE3, 67788/GRS10, 69144/PV1) have a last record ending 2026-09-01; the 7 keys both routes count as "left" in September (65399/U3, 65655/HECHQ, 66692/HOLLY, 66692/HOLY, 67660/MALAL, 68198/TRS, 68811/RIPLE) have a last record ending 2026-08-01. In EIA's September workbook, 9 of these 10 are on the "Canceled or Postponed" sheet and 69144/PV1 is on no sheet. The parquet kept in the job's data volume and the nightly of 4 November (S3 Last-Modified 08:20:48 UTC) were byte-identical (md5 2be6ac001022cf230f87dc70dc740496, 233,063 rows).
- Not seen: EIA's July or August 2026 workbooks (left3-v1's August download returned a 55,901-byte page that is not an xlsx file; the file has moved to EIA's archive folder), and no count over all generators.

## Method

- **PUDL:** the newest nightly `core_eia860m__changelog_generators.parquet`, downloaded at run time (its md5 and S3 Last-Modified are recorded). A generator is keyed `plant_id_eia/generator_id` (a whole-number id without leading zeros). Its last record is the row with the latest `report_date`; its end month is that row's `valid_until_date`.
- **Groups:** A9 = last record ends 2026-10-01 (under the new rule, still listed in September 2026); A8 = ends 2026-09-01 (last listed in August); A7 = ends 2026-08-01 (last listed in July).
- **EIA:** the July, August and September 2026 EIA-860M generator workbooks (current folder first, then `archive/xls/`). A generator is "listed" in a month when its key is on any sheet whose name contains neither "cancel" nor "_pr" (the sheets PUDL reads: Operating, Planned, Retired). Keys are read the same way on both sides.
- Code: `tools/endrule/endrule.py` 0.1.0 with its unit tests; job endrule-v1 waits until this plan is live and runs the committed code.

## Gates (if one fails, nothing is scored)

- **Gate G1:** the build's latest `report_date` is 2026-09-01, its S3 Last-Modified is after the merge (2026-11-02 18:13:25 UTC), and A9 is not empty.
- **Gate G2:** all three workbooks download and each has an Operating and a Planned sheet with a header row; A8 and A7 each hold at least 10 generators.

## Predictions (probability we give each)

- **P1 (85%):** at least 95% of A8 are listed in August 2026.
- **P2 (85%):** at most 5% of A8 are listed in September 2026. (The old reading says all of A8 is still in force in September.)
- **P3 (80%):** at least 95% of A7 are listed in July 2026 and at most 5% in August 2026.
- **P4 (90%):** at least 99% of A9 are listed in September 2026.
- **P5 (75%):** all 3 of LUPE3, GRS10 and PV1 are on August's Planned sheet, and none of the 7 keys counted as "left" in September by both routes is listed in August.

## What happens with the result

A dated result page is published whatever the scores. A failed bar is reported as failed, with its cause, and is not re-scored. If P1-P4 hold, MV2's tools get a wrapper that reads every `valid_until_date` as exclusive on post-merge builds (the pre-registered tools are not edited in place), before the October 2026 EIA-860M run (EIA's next release is 24 November 2026). Nothing about this is posted on PUDL: the change is PUDL's documented behaviour, and the error was in MV2's own reading.

## Limits

- One build and three months; generators PUDL never lists (Puerto Rico, canceled) are outside the groups.
- A generator EIA lists with a different id in another month counts as not listed.
- PUDL's code (MIT) and data (CC BY 4.0) are downloaded at run time and not stored here.
