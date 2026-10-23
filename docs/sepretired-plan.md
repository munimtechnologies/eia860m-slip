# Pre-registration: the 16 generators that left EIA-860M's Retired sheet in September 2026

Status: pre-registered, not yet scored.

Fixed on 23 October 2026, before job sepretired-v1 read anything about these 16 generators beyond their keys. The job's first step polls this file's address on GitHub and computes nothing until it is served, so the commit time of this file is the record of when the bars below were fixed. They will not be moved after the job runs.

Made by MV2 of Munim, Inc. with AI agents working in his name. Text: CC BY 4.0. Code: [`tools/annual-flows-candidate/sepretired.py`](../tools/annual-flows-candidate/sepretired.py) 0.1.0 (Apache-2.0), with its tests. It reuses the readers of `annual860.py` 0.1.0, `retiredgap.py` 0.1.0 and `layouts.py` 0.1.0 unchanged.

## Why

Bar P3 of [`docs/sep2026-plan.md`](sep2026-plan.md) failed: 16 generators that EIA's August 2026 EIA-860M workbook listed on its Retired sheet are on no sheet the rebuilt changelog reads in the September 2026 workbook (scored in [`docs/sep2026.md`](sep2026.md)). They are at 15 plants. The changelog keeps only key, sheet, status, planned month and MW, so it cannot say what these generators are. This plan asks three questions that could each come out either way.

## What was known when this plan was fixed

- The 16 keys: 1517/1, 1645/1, 1697/1, 1729/1, 246/3, 3166/1, 360/1, 4143/5, 558/1, 566/1, 6107/1, 6176/1, 8011/2, 869/1, 885/1 and 885/2 (job monthcheck-sep2026-v1, `data/gapcensus_left_events_2026-09.csv`).
- None of them is among the 2,703 generators that August 2026's Retired sheet lists as retired in 2002 to 2025 and that the annual EIA-860 2025 file does not list as retired (job annual860-v1, `data/annual860_monthly_not_annual.csv`). That job also counted 7,324 generators on August's Retired sheet, 7,268 of them retired in 2002 to 2025, and all 4,565 that the annual 2025 file lists as retired in those years are among them. So each of the 16 is either listed as retired by the annual EIA-860 2025 file, or one of the 56 on August's sheet whose retirement year is not in 2002 to 2025 (later, earlier or missing). Which, for each of them, is not known.
- Nothing else about them: not their plants, technologies, retirement years or MW.

## What the job does

`sepretired.py` 0.1.0 reads three files: EIA-860M August 2026 from PUDL's raw archive (Zenodo record 22995197, md5-checked as before), EIA's own September 2026 file (downloaded again with an honest User-Agent; its size and md5 are compared with the file job monthcheck-sep2026-v1 read: 14,013,970 bytes, md5 4c741eb77a5ccad5aca32ffe43f398af), and the annual EIA-860 2025 generator workbook (`3_1_Generator_Y2025`, the copy annual860-v1 downloaded). For each of the 16 it reports August's Retired-sheet row (plant name, state, technology, retirement month and year, nameplate MW), every sheet of the September workbook that lists it, how many generators of its plant each sheet lists in August and in September, and every sheet of the annual file that lists it, with its status code. It also compares the August and September Retired sheets as wholes and repeats annual860's census on both months.

## Predictions

- **S1.** All 16 are on no sheet of the September 2026 workbook at all, the Canceled or Postponed sheet and the Puerto Rico sheets (`*_PR`) included. One of them listed anywhere in September fails this bar.
- **S2.** At least 12 of the 16 are listed as retired by the annual EIA-860 2025 file (status RE on its Retired sheet, retirement year 2002 to 2025). The other possibility is that most of them are among the 56 whose retirement year on August's sheet is outside 2002 to 2025, which would point to EIA tidying the sheet's documented scope ("generators which retired since 2002") rather than dropping generators it lists as retired elsewhere.
- **S3.** At most 3 of the 16 are listed again, on any sheet the changelog reads, in EIA's October 2026 workbook. This is scored later, by the job that scores the October 2026 workbook, and added to the scored note as a dated section. A repeat of November 2024, when 277 generators were left out of one file and all came back the next month, would fail this bar.

Each bar is counted separately and reported as "N of 3 held" once S3 is scored. A bar the job cannot score (a file not served or not readable) is reported as not scored, and the job is run again under a new version.

## Limits

- S1 and S3 are about the workbook, not the plants: a generator can leave a list for many reasons (a correction, a re-keyed unit, a change of scope, a mistake).
- S2 compares with EIA's annual file for data year 2025, which is the latest EIA has published. It says nothing about generators retired in 2026.
- The 16 are not independent: two are at one plant, and one edit at EIA can move many rows at once.
- The changelog is rebuilt by this repository's own code; that is a reproducibility check, not an independent one.
