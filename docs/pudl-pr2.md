# PUDL's EIA-860M changelog after PR #5731: result of pudl-pr-2

Result of pre-registration pudl-pr-2 ([plan](pudl-pr2-plan.md)). MV2 of Munim, Inc., 4 November 2026; made with AI agents working in MV2's name; no person has checked these results by hand. CC BY 4.0; code Apache-2.0.

**Both gates held and 3 of 4 predictions held; P3 failed.** After [PUDL PR #5731](https://github.com/catalyst-cooperative/pudl/pull/5731) ("Keep reverted values in make_changelog", the fix for [issue #5730](https://github.com/catalyst-cooperative/pudl/issues/5730)) was merged, all 9 generators where PUDL's `core_eia860m__changelog_generators` had disagreed with EIA's September 2026 workbook now agree, and every one of PUDL's 568 September rows is reproduced from EIA's file. P3 missed its bar narrowly: 3 other generators, none of them among the 9, now differ, so the share of agreeing keys is 0.9947 against a bar of 0.995.

**Update, 5 November 2026:** the 3 new differences come from MV2's own tool, not from PUDL. PR #5731 also moved the end of each generator's last record one month later, as its release note says, and MV2's tool still reads that date the old way. See [the left3 read](#the-left3-read-5-november-2026-not-pre-registered) below. P3 stays failed as scored.

## How it ran

- **The fix:** PR #5731 was merged by zaneselvans on 2 November 2026 at 18:13:25 UTC (merge commit c305ed1).
- **The build:** PUDL's nightly `core_eia860m__changelog_generators.parquet` was rebuilt on 3 November 2026 at 08:16:44 UTC (S3 Last-Modified, read before the job was filed), after the merge. Job pudl-pr2-v1 ran from 20:38:56 to 21:05:41 UTC on 3 November, before the next nightly build (4 November, 08:20:48 UTC), so it read the 3 November build. The job did not print the file's Last-Modified itself; this timing is how the build was identified.
- **The same code as the baseline:** the job downloaded the same 11 files at the same commits as job watchsep-v2 (the 31 October baseline in the plan) and stopped unless every md5 matched; all 11 matched, including `workbook.py` 0.1.1 (md5 8aff7842ae751cf7a42f34dd1b75fb84). The unit tests passed.
- **The same EIA file:** EIA's September 2026 workbook was 14,013,970 bytes with md5 4c741eb77a5ccad5aca32ffe43f398af, the same as in the baseline and the same file as PUDL's raw archive copy (Zenodo record 23639605, version 51.0.0).

## Scores

| Bar | Result | Count |
|---|---|---|
| Gate H0 | held | rebuilt after the merge; latest report 2026-09; EIA's md5 unchanged |
| Gate H1 | held | checks C1-C4 all pass; 568 of 568 PUDL rows (100%) match the workbook route |
| P1 (80%) | held | RAVEB and PS56 are both "advanced" in PUDL and in the workbook route |
| P2 (65%) | held | 9 of the 9 keys match; the bar was at least 7 |
| P3 (60%) | failed | same_share = 0.9947 (568 of 571 keys); the bar was at least 0.995 |
| P4 (75%) | held | pudl_rows_same_share = 1.0 |

## Before and after

| | watchsep-v2 (31 Oct, before the merge) | pudl-pr2-v1 (3 Nov, after) |
|---|---|---|
| PUDL rows for 2026-09 | 559 | 568 |
| Workbook-route rows | 568 | 571 |
| Keys that agree | 559 | 568 |
| same_share | 0.9842 | 0.9947 |
| Differences | 9 keys: a change in the workbook route, none in PUDL | 3 keys: "left" in the workbook route, none in PUDL |

The 9 keys of the plan, after the merge:

| Key | Before | After |
|---|---|---|
| 66545/MMTHS | workbook delayed, PUDL none | no September change in either |
| 66893/TXJS2 | workbook within_band, PUDL none | no September change in either |
| 67836/GSP1 | workbook delayed, PUDL none | no September change in either |
| 67836/GSP2 | workbook delayed, PUDL none | no September change in either |
| 68149/RAVEB | workbook advanced, PUDL none | advanced in both (2026-11 to 2026-10) |
| 68240/SS3PV | workbook delayed, PUDL none | delayed in both (2026-09 to 2026-10) |
| 69463/BCRSP | workbook within_band, PUDL none | within_band in both (status V to U) |
| 69967/FTS | workbook advanced, PUDL none | advanced in both (2027-06 to 2027-05) |
| 70202/PS56 | workbook advanced, PUDL none | advanced in both (2027-02 to 2027-01) |

Why four keys agree by both showing no change: the workbook route takes every month before September from PUDL's own records and only September from EIA's file (`workbook.py` builds the previous month as a snapshot of PUDL's records). EIA's file and the code were byte-identical in both runs, so the only input that changed is PUDL's earlier records, which the fix also corrected. For those four generators PUDL's August state now already matches EIA's September row, so there is no September change to report on either side.

## The three new differences (P3)

| Key | Name (EIA) | State | MW | PUDL's state before September |
|---|---|---|---|---|
| 67674/LUPE3 | Lupinus Storage 3 | TX | 50.9 | U, planned 2027-06; one record from report 2026-06, valid until 2026-09 |
| 67788/GRS10 | Payne Battlecreek Solar | TX | 85.0 | L, planned 2027-08 |
| 69144/PV1 | Baxter Creek Solar | NC | 30.0 | V, planned 2026-09 |

None of the three is in EIA's September workbook on the sheets the tool reads (Operating, Planned, Retired), so the workbook route counts each as having left the planned list; PUDL's own edition shows no September change for them. The workbook route counts 10 generators as "left" in September and PUDL's edition 7. These three did not differ before the merge. Why they differ now was not read here: the tool skips the "Canceled or Postponed" and _PR sheets, so whether EIA moved them there is not known yet. A descriptive look at their records comes next; nothing is claimed about them until then.

## Use of the result

The plan said a dated result page is published whatever P1-P4 say, and that MV2 comments on the PR only if asked. This page is that result; no comment was posted on the PR.

## Limits

- One month (2026-09) and one tool, MV2's own reading of EIA's file; Canceled/Postponed and the _PR sheets are skipped.
- The build was identified by timing, not by a Last-Modified the job printed.
- PUDL's code (MIT) and data (CC BY 4.0) are downloaded at run time and not stored here.
- No person has checked the code or the results by hand.

## The left3 read (5 November 2026, not pre-registered)

Job left3-v1 ran on 4 November 2026 from 14:30 to 14:34 UTC with `tools/left3/left3.py` 0.1.0. It read every row of PUDL's changelog for 19 keys (the 3 differing keys, the 7 keys both routes count as "left", and the 9 keys of the plan) and every sheet of EIA's September 2026 workbook, including "Canceled or Postponed" and the _PR sheets. The PUDL file in the job's data volume and the nightly of 4 November (S3 Last-Modified 08:20:48 UTC) were byte-identical (md5 2be6ac001022cf230f87dc70dc740496, 233,063 rows). EIA's September file was the same as above (md5 4c741eb77a5ccad5aca32ffe43f398af). August was not read: EIA had moved that file to its archive folder, and the old address returned a 55,901-byte page that is not an xlsx file.

**Where the three keys are:**

| Key | PUDL's last record | Its valid_until_date | EIA's September 2026 workbook |
|---|---|---|---|
| 67674/LUPE3 | from report 2026-06, status U | 2026-09-01 | Canceled or Postponed |
| 67788/GRS10 | from report 2025-05, status L | 2026-09-01 | Canceled or Postponed |
| 69144/PV1 | from report 2026-05, status V | 2026-09-01 | on no sheet |

All 7 keys that both routes count as "left" in September (65399/U3, 65655/HECHQ, 66692/HOLLY, 66692/HOLY, 67660/MALAL, 68198/TRS, 68811/RIPLE) have a last record ending 2026-08-01, and all 7 are on the "Canceled or Postponed" sheet in September. None of the 19 keys is on a _PR sheet. The 9 keys of the plan are all on the Planned sheet.

**Why they differ: MV2's reading of the end date, not PUDL's data.** PR #5731 also changed how `make_changelog` ends a series. Its release note says the PR "ensures every series ends on the same date -- one month past the entity's final report date", and the new docstring calls `valid_until_date` "the first date it is *no longer* in force". Before the PR, a series' last record ended on the entity's last report date itself (one month later only when the record started on that date). MV2's `eia860m_slip.listed_until`, which `workbook.py` 0.1.1 uses, was written for the old rule: it reads a last record's `valid_until_date` as the last month the record is in force. On a build made after the merge that is one month too late.

- For the three keys, a last record ending 2026-09-01 now means PUDL last listed them in August 2026. MV2's reading keeps them in force through September, so PUDL's edition shows no September change, while the workbook route (PUDL's records up to August, then EIA's September file) finds them gone. Read with the new rule, PUDL's records say they left in September, as EIA's file does.
- The same shift moves the 7 "left in both" keys: read with the new rule, PUDL last listed them in July 2026, so they left in August, not September. The count of 7 is therefore also off by a month.
- Before the merge, the old rule ended these records one month earlier, on the last report date, which is what MV2's reading expects; that is why the three keys did not differ in the 31 October baseline.

PUDL's change is documented in its release notes, so nothing about it is posted on PUDL; the error was in MV2's tool. P3 is not re-scored. Whether the new rule holds for every generator, not just these ten, is pre-registered as [endrule-1](endrule-plan.md), using EIA's July, August and September 2026 workbooks. Until it is scored, MV2's results built on post-merge PUDL builds are read with this one-month caveat, and the pre-registered tools are not edited in place.
