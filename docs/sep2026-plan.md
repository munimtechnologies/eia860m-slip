# Pre-registration: EIA's September 2026 EIA-860M workbook, scored on release

Status: pre-registered, not yet scored.

Fixed on 23 October 2026, before EIA published its September 2026 workbook. At about 10:30 UTC that day EIA's EIA-860M page (https://www.eia.gov/electricity/data/eia860m/) still showed August 2026 data, with "Next Release Date: October 23, 2026", and the address of the September file did not serve a workbook. The commit time of this file on GitHub is the record of when the bars below were fixed. They will not be moved after the job runs.

Made by MV2 of Munim, Inc. with AI agents working in his name. Text: CC BY 4.0. Code: [`tools/annual-flows-candidate/monthcheck.py`](../tools/annual-flows-candidate/monthcheck.py) 0.1.0 (Apache-2.0), with its tests.

## Why

The rebuilt changelog in [`data/eia860m_changelog_from_workbooks.csv.gz`](../data/eia860m_changelog_from_workbooks.csv.gz) (0.1.0, July 2015 to August 2026) is meant to grow by one month each time EIA publishes a new workbook. This plan turns the first such update into a test that could fail, rather than upkeep: four bars, fixed before the data exist.

## What the job does

1. `gapcensus.py` 0.1.0, unchanged, replays the 134 archived workbooks (PUDL's raw archive, Zenodo record 22995197, md5-checked) with `history.py` 0.1.0's reader. With `--eia-month 2026-09` it downloads EIA's own September 2026 file (honest User-Agent; first bytes, size and md5 recorded), reads it with the same reader and appends its rows to the rebuilt changelog.
2. `monthcheck.py` 0.1.0 replays that changelog once more and counts, for every month, the events (first, changed, left, back), the sheet each generator that left was on the month before, the number of generators listed, and the next-month cohort defined below.

## Definitions

- **Listed:** generators on the Operating, Planned or Retired sheet at the end of a month (the sheets the changelog reads).
- **Left:** a generator listed the month before and not listed this month. This includes moves to the Canceled or Postponed sheet, which the changelog does not read.
- **Next-month cohort of month M:** generators that the month before M listed on the Planned sheet with a planned operating month equal to M.
- **Share to Operating:** the share of the cohort, by count, that month M lists on the Operating sheet.

## Predictions for September 2026

- **P1.** EIA's September 2026 file is downloaded, read with no problems, and the number of generators listed is within 3% of August 2026's.
- **P2.** At most 50 generators leave in September 2026. The record: in the 12 months from September 2025 to August 2026, 9, 5, 7, 23, 26, 50, 30, 34, 25, 31, 11 and 9 generators left (counted from job gapcensus-v1's `gapcensus_left_events.csv`). The most was 50, in February 2026.
- **P3.** Fewer than 10 of the generators that leave in September 2026 were on the Retired sheet in August. The record: gapcensus-v1 counted 6 such generators in all of 2025 and 1 in January to August 2026. EIA's November 2024 file left out 277 of them; a repeat of that gap would fail this bar.
- **P4.** September 2026's share to Operating lies between the second lowest and the second highest of the shares of the 24 months before it (M from September 2024 to August 2026), both ends included. If the 25 months were interchangeable, a new month would land inside this band with probability 21 in 25 (84%).

The four bars are counted separately and reported as "N of 4 held". A prediction the job cannot score (for example, if EIA's file is not yet served when the job runs) is reported as not scored and the job is run again under a new version; a file that is served but cannot be read fails P1.

## Context, not a bar

- The band in P4 is a rule, not a number: its two ends are computed by the job from the 24 months before September 2026. A practice run (job monthcheck-dry-v1, on August 2026, already in the archive) checks the code and prints the monthly shares first; it does not change the rule.
- [`docs/stage-leadtime.md`](stage-leadtime.md) found that generators planned 0 to 3 months ahead were online by their planned month for 0.197 to 0.444 of rows by count, depending on construction stage (report months January 2016 to June 2023). That measure differs from this one (online by the planned month against listed as Operating the next month) and was built on PUDL's changelog, so it is context only.
- A web search on 23 October 2026 found no published monthly series of how many generators planned for the next month are listed as operating in it. EIA's documentation, as read in earlier notes, describes the sheets but gives no such rate.

## Limits

- The changelog is rebuilt by the same code that wrote it; that is a reproducibility check, not an independent one.
- Generators are not independent: one plant can have many generators that move together, so one large project can swing the share.
- P4 is a statistical bar. A miss says September 2026 is unusual against the two years before it, not that EIA's data are wrong.
- "Left" mixes real removals, moves to the Canceled or Postponed sheet and gaps in a file (as in November 2024); P2 and P3 do not tell them apart.

## After the job

The scored note will be a new file, `docs/sep2026.md`, with the job's raw output. If P1 holds, the changelog with September 2026 appended will be published as dataset 0.1.1, with a dated line naming EIA's file, its size and its md5. This plan will not be edited after its run.
