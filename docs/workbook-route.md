# Building the EIA-860M watchlist from EIA's own workbook on release day

Status: descriptive, not a scored result; nothing was predicted. By the bar set before the first run (at least 0.98 of the generators listed in either edition have the same change), the route is not usable yet: 0.9744 for August 2026 and 0.9764 for July. MV2 of Munim, Inc. (made with AI agents). CC BY 4.0.

## What this is

The EIA-860M watchlist ([`watchlist.md`](watchlist.md)) is built from Catalyst Cooperative's PUDL changelog of EIA-860M generators, which takes in a new monthly report some weeks after EIA publishes it. [`workbook.py`](../tools/annual-flows-candidate/workbook.py) would build an edition on EIA's release day instead: PUDL's records through the month before, plus the new month read from EIA's own workbook. Its self-check rebuilds a month PUDL already holds both ways and compares the two editions generator by generator. This note records why the route is not used yet and what is being checked next.

Data: job `wbcheck-v2` (sealed container, 21 October 2026) took workbook.py 0.1.1, xlsxprobe.py 0.1.1 and rawcheck.py 0.1.0 from commit 5e7097a, passed 24 of 24 unit tests, repeated the self-check of job `wbcheck-v1` ([`wbcheck-v1-workbook-output.md`](wbcheck-v1-workbook-output.md)) for August and July 2026, and ran [`rawcheck.py`](../tools/annual-flows-candidate/rawcheck.py). Raw output: [`wbcheck-v2-workbook-output.md`](wbcheck-v2-workbook-output.md), [`../data/wbcheck_v2_workbook.json`](../data/wbcheck_v2_workbook.json), [`wbcheck-v2-rawcheck-output.md`](wbcheck-v2-rawcheck-output.md), [`../data/wbcheck_v2_rawcheck.json`](../data/wbcheck_v2_rawcheck.json); unit tests: [`wbcheck-v2-unittests.txt`](wbcheck-v2-unittests.txt).

## What we found

**The self-check gave the same result again.** August: 418 of 429 generators have the same change (0.9744); July: 537 of 550 (0.9764), as in `wbcheck-v1`. Every one of PUDL's own rows is reproduced with the same change. Each difference is a generator the workbook route lists with a change and PUDL's edition does not list at all: 11 in August, 13 in July.

**EIA did not change the files after PUDL archived them.** On 21 October 2026 rawcheck downloaded EIA's July and August 2026 workbooks and PUDL's archive copy of them (Zenodo record 22995197, version 50.0.0, first published 2026-09-27; its md5 matched Zenodo's). In each month the archived workbook is byte for byte EIA's file: md5 9727ac867236faab7d5503175dacdf38 for August and md5 909590b91dbda698d0e63d813ced377c for July. So the differences come from how the same file is read, in PUDL's processing into its changelog or in workbook.py's reading of the workbook, not from a later EIA revision.

**Most of August's differences are standing ones.** 8 of August's 11 differing generators are also among July's 13, and for each of the 8 the workbook gives the same status, planned month and MW in both months. For 6 of the 8, PUDL has a record in force through August that differs from the workbook: in 4 the workbook's planned month is 1 or 2 months later than PUDL's, with the same status; in the other 2 the status differs and the planned month is the same. For the other 2, PUDL's records include none reported from April to August 2026.

**What that means for the route.** workbook.py starts from PUDL's records for the month before, so a generator on which PUDL and the workbook disagree is listed as changed in every month the disagreement lasts. We do not yet know which side reads the file correctly. The bar of 0.98 stays where it was set.

## Generators that differ in both July and August

| generator | EIA workbook, July and August | PUDL record in force through August |
|---|---|---|
| 61912/MHSOL | U, 2027-01, 14.0 MW | T, 2027-01 (reported 2026-06) |
| 65710/PTNM | L, 2027-03, 4.0 MW | L, 2027-01 (reported 2026-05) |
| 66893/TXJS2 | U, 2027-03, 200.0 MW | V, 2027-03 (reported 2026-05) |
| 67836/GSP1 | T, 2027-12, 13.0 MW | none reported 2026-04 to 2026-08 |
| 67836/GSP2 | T, 2027-12, 13.0 MW | none reported 2026-04 to 2026-08 |
| 68514/MC201 | U, 2026-10, 300.0 MW | U, 2026-09 (reported 2026-04) |
| 69372/KNOXS | V, 2026-11, 5.0 MW | V, 2026-10 (reported 2026-06) |
| 69825/MADCR | T, 2027-04, 5.0 MW | T, 2027-03 (reported 2026-05) |

Status codes are EIA's: L regulatory approvals pending, T approvals received but not under construction, U under construction, 50 percent complete or less, V under construction, more than 50 percent complete. Planned months are the planned operating month. The raw output shows every PUDL record reported in the four months up to each report. August's other 3 differences are 66545/MMTHS, 68334/EVCRK and 69338/LEAKY; July's other 5 are 66546/MMTHC, 67223/SUNYF, 69579/HMWT, 69589/BEEK1 and 70257/H2SLR.

## Limits

Only the archive copy first published on or after 24 September 2026 was compared with EIA's file; an earlier archive copy of the July workbook could differ. The workbook side of every comparison is read with workbook.py's reader, so a fault in that reader for a few rows would look the same as a gap in PUDL's changelog. The generators are few, and a reading of so few is a description, not a measure of how often the two sources disagree.

## Next

- Job `keyhist-v1` (queued, descriptive) reads all eight 2026 workbooks from the same archive copy, compares each month whole with PUDL's records in force, and sets these 16 generators' workbook rows beside PUDL's records month by month. If PUDL's record matches an earlier month's workbook, PUDL's changelog has not taken in a later change; if it matches no month, the two read the file differently.
- Until the route passes 0.98 on a month it was not adjusted on, watchlist editions come from PUDL alone. With workbook.py 0.1.1 unchanged, the September 2026 self-check, once PUDL holds September, is such a month.
