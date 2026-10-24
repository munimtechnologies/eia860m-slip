# Pre-registration: EIA's October 2026 EIA-860M workbook, scored on release

Status: pre-registered, not yet scored.

Fixed on 24 October 2026, a month before EIA publishes its October 2026 workbook. At about 02:00 UTC that day EIA's EIA-860M page (https://www.eia.gov/electricity/data/eia860m/) showed September 2026 data, "Release Date: October 23, 2026" and "Next Release Date: November 24, 2026". The commit time of this file on GitHub is the record of when the bars below were fixed. They will not be moved after the job runs.

Made by MV2 of Munim, Inc. with AI agents working in his name. Text: CC BY 4.0. The scoring job will run this repository's `gapcensus.py`, `monthcheck.py` and `retiredentry.py` code (Apache-2.0); any change to that code will be published, with its tests, before the job runs, and the scored note will name the versions.

## Why

This is the second month scored on release. September 2026 ([`docs/sep2026.md`](sep2026.md)) held 3 of 4 bars, and the bar that failed led to a documented data event: August 2026's Retired sheet gained 28 nuclear reactors retired before 2002 and September's dropped them all ([`docs/retiredentry.md`](retiredentry.md)). October keeps the same four bars, so the two months can be compared, and adds one bar on that event.

## What the job does

It replays the archived workbooks as the September job did, reads EIA's own September and October 2026 files where PUDL's raw archive lacks them (honest User-Agent; first bytes, size and md5 recorded), appends October's rows to the rebuilt changelog, and counts events and the next-month cohort with `monthcheck.py`. For P5 it scans every row of every sheet of October's file, with or without a plant ID, as `retiredentry.py` did for August.

## Definitions

As in [`docs/sep2026-plan.md`](sep2026-plan.md): **listed** (on the Operating, Planned or Retired sheet), **left** (listed the month before and not this month, including moves to the Canceled or Postponed sheet), the **next-month cohort** of month M (generators that the month before listed on the Planned sheet with planned operating month M) and its **share to Operating** (the part of the cohort that month M lists on the Operating sheet, by count).

## Predictions for October 2026

- **P1.** EIA's October 2026 file is downloaded, read with no problems, and the number of generators listed is within 3% of September 2026's (38,162).
- **P2.** At most 50 generators leave in October 2026. The record, from [`data/monthcheck_months_2026-09.csv`](../data/monthcheck_months_2026-09.csv): in the 12 months from October 2025 to September 2026, 5, 7, 23, 26, 50, 30, 34, 25, 31, 11, 9 and 20 generators left.
- **P3.** Fewer than 10 of the generators that leave in October 2026 were on the Retired sheet in September. The record, from the same file: 6 such generators in all of 2025, 1 in January to August 2026, and 16 in September 2026. Those 16 were nuclear units retired before 2002, removed when September's sheet went back inside its documented scope ([`docs/sepretired.md`](sepretired.md)), so September's failure of this bar was a one-off cleanup, not a sign that the bar is too tight. A file that leaves out many retired generators, as November 2024's did, would fail it.
- **P4.** October 2026's share to Operating lies between the second lowest and the second highest of the shares of the 24 months before it (M from October 2024 to September 2026), both ends included. From [`data/monthcheck_months_2026-09.csv`](../data/monthcheck_months_2026-09.csv) that band is 0.219512 (October 2024) to 0.473958 (December 2025). If the 25 months were interchangeable, a new month would land inside it with probability 21 in 25 (84%).
- **P5.** October 2026's workbook has no row, on any sheet and with or without a plant ID, whose technology is nuclear and whose retirement year is before 2002. September's had none; August's had 28. This fails if EIA's nuclear shutdown list comes back onto the sheet.

The five bars are counted separately and reported as "N of 5 held". A prediction the job cannot score (for example, if EIA's file is not yet served when the job runs) is reported as not scored and the job is run again; a file that is served but cannot be read fails P1.

## Also scored with this workbook

Bar S3 of [`docs/sepretired-plan.md`](sepretired-plan.md): at most 3 of the 16 generators that left the Retired sheet in September 2026 are listed again, on any sheet the changelog reads, in October 2026. It is reported in a dated section of `docs/sepretired.md`, not counted in the five bars above.

## Also reported, not scored

October 2026's next-month cohort split by technology group (solar, batteries, gas, wind, other, as in [`docs/nexttech.md`](nexttech.md)), and split into generators named as planned for the next month for the first time since July 2015 and those named again ([`docs/nexttechonce.md`](nexttechonce.md)).

## What was known when this plan was fixed

- Everything in the notes linked above, including every monthly count to September 2026 in `data/monthcheck_months_2026-09.csv`.
- October's share to Operating was 0.219512 in October 2024 and 0.42029 in October 2025: one below and one inside this band.
- Nothing about October 2026's file: EIA had not published it.

## Limits

- The changelog is rebuilt by the same code that wrote it; that is a reproducibility check, not an independent one.
- Generators are not independent: one plant can have many generators that move together, so one large project can swing the share.
- P4 is a statistical bar. A miss says October 2026 is unusual against the two years before it, not that EIA's data are wrong.
- "Left" mixes real removals, moves to the Canceled or Postponed sheet and gaps in a file; P2 and P3 do not tell them apart.
- P5 reads the technology column. A reactor listed under another technology name would be missed.

## After the job

The scored note will be a new file, `docs/oct2026.md`, with the job's raw output. If P1 holds, the changelog with October 2026 appended will be published as dataset 0.1.2, with a dated line naming EIA's file, its size and its md5. This plan will not be edited after its run.
