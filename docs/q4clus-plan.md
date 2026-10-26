# Pre-registration: in October to December 2026, months EIA has not yet published, do the solar and battery one-month-slip gaps point the same way, with whole plants resampled?

Status: pre-registered, not yet scored.

Fixed in October 2026, before EIA publishes its October 2026 EIA-860M workbook (EIA's page says "Next Release Date: November 24, 2026"), so none of the data this plan scores existed when it was fixed. The scoring job runs `q4clus.py --require-plan`, which polls this file's address on GitHub and scores nothing until it is served, so the commit time of this file is the record of when the bars below were fixed. They will not be moved.

Made by MV2 of Munim, Inc. with AI agents working in his name. Text: CC BY 4.0. Code: [`tools/annual-flows-candidate/q4clus.py`](../tools/annual-flows-candidate/q4clus.py) 0.1.0 (Apache-2.0), with its tests. It takes its rows and its checks from [`q4held.py`](../tools/annual-flows-candidate/q4held.py) 0.1.0 and its cells and plant resampling from [`clusterboot.py`](../tools/annual-flows-candidate/clusterboot.py) 0.1.0, both unchanged, and uses only Python's standard library.

## Why

The forty-first result ([`docs/clusterboot.md`](clusterboot.md)) resampled whole plants and left three readings standing, all on months that were already published: for solar and for batteries, a generator planned for the next month again right after a one-month slip was on time more often than a first listing (2016-2025 pooled), and for solar since 2022 more often than one back after a slip of 2-3 months. The wind and gas reversals and the all-technology gap were not shown. This plan asks whether the three readings that stand point the same way in the next-month groups of October, November and December 2026, and says in advance how likely that is if nothing has changed.

[`docs/q4held-plan.md`](q4held-plan.md) already scores the same three months for all technologies together, in generator-months. This plan uses the same rows, so the two are not independent tests; it splits them by technology and adds plant-clustered intervals.

## The rule

- Rows: those of `q4held.py` 0.1.0. Base: [`data/nexttech_cohort.csv`](../data/nexttech_cohort.csv) at commit ea63c15 (950,816 bytes, md5 1681df9fdee9878ca2c359d1239c6467, 14,807 rows; next-month groups from August 2015 to September 2026). Each scored month's group is the `monthrun_cohort.csv` that [`monthrun.py`](../tools/annual-flows-candidate/monthrun.py) 0.1.0 writes for that month, appended in month order after the cohort's rows up to September 2026.
- Cells: those of `clusterboot.py` 0.1.0. A row is a first listing (no earlier next-month listing of that generator since August 2015) or a repeat listing by the months since the generator's last one (1, 2-3, 4-12, more than 12). It is on time if that month's workbook lists the generator as operating. A plant is the part of the generator key before the slash (EIA's plant ID). Technology groups are the cohort file's `group` column.
- Resampling: for each bar, the plants with rows in either compared cell, 2,000 resamples of them with replacement, seed 20261025, as in the forty-first result; the 95% interval runs from the 51st to the 1,950th sorted difference.
- Scored period: October, November and December 2026 pooled. December's status comes from EIA's December 2026 workbook, expected in late January 2027. Tables for October and November alone are reported as they arrive, not scored.

## What was known when this plan was fixed

- The forty-first result, pooled with whole plants resampled: B1, solar, 2016-2025, 1 month after the last listing minus first listings +0.0498 (+0.0200 to +0.0795), from 1,230 of 2,657 against 1,474 of 3,568; B2, batteries, the same, +0.0824 (+0.0275 to +0.1405), from 297 of 816 against 205 of 728; B5, solar, January 2022 to August 2026, 1 month after minus 2-3 months after +0.1251 (+0.0798 to +0.1686), from 639 of 1,636 against 171 of 644.
- Those intervals were 1.19 (B1), 1.22 (B2) and 1.07 (B5) times as wide as a normal interval that treats every generator-month as independent.
- September 2026, from the practice job q4clus-practice-v1 (26 October 2026), which ran `q4clus.py` on September's rows from monthrun.py's own output ([`docs/q4clus-practice-v1-output.md`](q4clus-practice-v1-output.md)); its 170 appended rows equal the cohort's September rows, and C1 and C2 held: solar, 1 month after the last listing 14 of 35 at 34 plants, first listings 16 of 41 at 40 plants, 2-3 months after 5 of 24 at 24 plants; batteries, 1 month after the last listing 5 of 11 at 11 plants, first listings 6 of 16 at 16 plants, 2-3 months after 3 of 10.
- On September alone, R1 would have held (+0.0098, 95% interval -0.2158 to +0.2452), R2 and R3 would not have been scored (cells of 11 and 24 rows), K1 would have held, and K2 and K3 would not have been scored.
- No row of October, November or December 2026 was known.

## Checks (not predictions)

- **C1.** Each scored month's group size and on-time count equal monthrun.py's own numbers for that month, as in [`docs/q4held-plan.md`](q4held-plan.md).
- **C2.** For every scored row, monthrun.py's `listing` column says "first" exactly when the row has no earlier listing, as in [`docs/q4held-plan.md`](q4held-plan.md).

If C1 or C2 fails, no bar is scored.

## Direction bars (October to December 2026 pooled)

- **R1.** Solar: 1 month after the last listing minus first listings is above 0.
- **R2.** Batteries: 1 month after the last listing minus first listings is above 0.
- **R3.** Solar: 1 month after the last listing minus 2-3 months after is above 0.

"Above 0" means the point difference of the two cells' shares (on-time generator-months over generator-months) is above 0. Every cell a bar compares needs at least 30 rows; a bar with a smaller cell is reported as not scored. Results are reported as "N of the scored direction bars held".

## Consistency bars (reported separately, not added to the direction count)

- **K1.** R1's 95% interval contains the forty-first result's B1 difference, +0.0498.
- **K2.** R2's 95% interval contains the forty-first result's B2 difference, +0.0824.
- **K3.** R3's 95% interval contains the forty-first result's B5 difference, +0.1251.

A consistency bar is scored only if its direction bar's cells have at least 30 rows and at least 10 plants each. These are weak bars: with three months of rows the intervals will be wide, so they fail only if the three months are far from the history.

## Expected size, and the chance of each direction bar if history repeats

Expected cell sizes are three times September's. The chance is a normal approximation: the historical shares, these cell sizes, and intervals 1.2 times as wide as row-independent ones.

| bar | expected rows (cell, compared cell) | earlier difference | chance the point is above 0 |
|---|---|---|---|
| R1 | 105, 123 | +0.0498 | 0.74 |
| R2 | 33, 48 | +0.0824 | 0.74 |
| R3 | 105, 72 | +0.1251 | 0.93 |

## How each could fail

Three months can easily miss a real gap of +0.05: even if nothing has changed, R1 and R2 each fail about one time in four, so a failure of either is not by itself evidence that the pattern changed. R2's one-month cell is expected to have about 33 rows and may fall under 30, in which case R2 and K2 are not scored. R3 is the strongest: a failure there would be the clearest sign that the cost of a 2-3 month slip for solar has changed. The chances assume the plant factor of 1.2 seen in the forty-first result; in three months a few large plants may carry more of a cell, which would widen the intervals and lower the chances.

## Also reported, not scored

Each month's and the pooled differences, with intervals and plants, for the three bars and for wind and gas (1 month after the last listing minus first listings) and all technologies together.

## Limits

- Three months. Resampling plants handles dependence between rows of one plant, not between plants of one developer, region or year.
- A percentile interval from 2,000 resamples; its ends move a little with the seed.
- Generator-months. "On time" is the next workbook's status: one listed as operating a month late is not on time, and one that leaves the file is not on time.
- Each month is counted from its workbook as first published, by this repository's own code; C1 and C2 are reproducibility checks, not independent ones.
- This is an association, not a cause.
