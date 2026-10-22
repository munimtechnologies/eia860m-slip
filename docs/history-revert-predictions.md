# Twenty-ninth test, predictions fixed in advance: how far back does PUDL's changelog keep stale values?

Status: predictions fixed on 2026-10-22, before any workbook of 2015-2025 was read. Code and the full pre-registration follow after the structure check (job layouts-v1). The predictions and bars below will not change; if the structure check shows a year cannot be read, that year is reported as not scored, never dropped silently.

MV2 of Munim, Inc. Made with AI agents working in his name. Apache-2.0 (code), CC BY 4.0 (text).

## Background

The twenty-eighth test (docs/changelog-revert.md, 4 of 4 predictions held) found that PUDL's EIA-860M changelog (core_eia860m__changelog_generators, built by pudl.helpers.make_changelog) drops a generator's monthly record when it equals any earlier record of that generator, so a value that changes and comes back (A, B, A) is lost and B stays in force. That test covered January to August 2026 only, and it seeded the simulation from PUDL's own pre-2026 records.

## What the twenty-ninth test does

It reads every monthly EIA-860M workbook in PUDL's own raw archive (Zenodo record 22995197, version 50.0.0, eia860m-2015.zip to eia860m-2026.zip, each md5-checked) with the reader of workbook.py (all sheets but Canceled or Postponed and the Puerto Rico sheets, keys as PUDL keys them), and compares each month with PUDL's record in force for that month, on three fields: status, planned month (planned statuses only) and nameplate MW (within 0.05 MW), exactly as revert.py 0.1.0 compares them.

The rule is simulated on the three fields from the first workbook month onward, fed only EIA's workbooks (no PUDL record is used to seed it). A generator-month is a hit when the simulation keeps a value the workbook no longer has, PUDL's record in force is that value, and PUDL disagrees with the workbook (revert.is_hit).

## Predictions (bars fixed now)

- **P1 reach:** at least 50 hit generator-months in each calendar year 2016 to 2025.
- **P2 coverage:** over all months, at least 0.90 of the generator-months where the workbook and PUDL disagree are hits.
- **P3 precision:** over all months, at least 0.50 of the generator-months where the simulation keeps a stale value are hits.
- **P4 accumulation:** the mean number of hits per month in 2025 is greater than in 2017.
- **P5 every year:** coverage is at least 0.80 in each calendar year 2016 to 2025.

## Checks (a failed check means not scored)

- **C1 workbooks:** every zip matches its listed md5, and every month used is readable by the criteria set in layouts.py before its first run.
- **C2 PUDL:** PUDL's changelog holds report months through 2026-08.
- **C3 keys:** in each year, at least 0.95 of the workbook's generator-months have a PUDL record in force (the reader keys old layouts as PUDL does).
- **C4 links:** overall, at least 100 disagreeing generator-months and at least 100 simulated stale generator-months.

## How each prediction could fail

- If the rule mattered only recently (for example, if PUDL's changelog were rebuilt differently for older months), P1, P4 and P5 fail.
- If older disagreements have another cause (reader errors on old layouts, revised workbooks, PUDL fixes for specific years), P2 and P5 fail.
- If stale values were corrected quickly rather than piling up, P4 fails.
