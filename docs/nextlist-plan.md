# Next-month list for October 2026: pre-registration

Status: pre-registered, not yet scored. Fixed before EIA publishes its October 2026 EIA-860M workbook (expected 24 November 2026). MV2 of Munim, Inc. (made with AI agents). CC BY 4.0.

## What is tested

[`nextlist-2026-10.md`](nextlist-2026-10.md) lists the 161 generators at 136 plants (11,460.2 MW) that EIA's September 2026 workbook plans to start operating in October 2026: 107 solar, 31 batteries, 10 gas, 2 wind and 11 other. Each has p, the share of earlier generators in the same technology group and listing cell that were listed as operating in their planned month, over the 48 group months before October 2026 (nextlist.py 0.1.0; a cell with fewer than 30 generator-months falls back to its group's share, then to broader shares). The cell is "first" (in no next-month group since August 2015) or the months since the generator's last next-month group. For example, p is 0.3884 for the 45 solar generators planned for next month again one month after their last listing, and 0.3602 for the 37 solar generators listed for the first time. Two plainer references use the same window: r0, the share of all rows, and r1, the technology group's share.

Outcome: a generator counts as on time when EIA's October 2026 workbook lists it as operating (monthrun.py 0.1.0's `now`, written to monthrun_cohort.csv). Generators with no outcome are counted and left out.

## Predictions (scored once)

- **N1.** The Brier score of p on the October list is lower than r0's.
- **N2.** The Brier score of p on the October list is lower than r1's.

Each is a point comparison on one month. The plant-resampled 95% intervals of p minus r0 and p minus r1 are reported and not scored, and so are the on-time count against p's expected count and the calibration.

How it is scored: after EIA's release, a job runs nextlist.py exactly as published with this plan (version 0.1.0, md5 8b32a645ab321fc7231f907dc892e2fc) with `--target 2026-10 --practice '' --score-file 2026-10=monthrun_cohort.csv`. Check S1: the list it rebuilds from the same September workbook (md5 4c741eb77a5ccad5aca32ffe43f398af) and the same cohort file (commit ea63c15) must have the same keys and the same p as [`data/nextlist_2026-10.csv`](../data/nextlist_2026-10.csv). If S1 fails, nothing is scored and the reason is published.

## What was already known when this was written

The backtest (every month from January 2020 to September 2026, each from the 48 months before it only; 10,237 generator-months at 3,531 plants) and the October list itself were computed before this plan, by job nextlist-v1 on 27 October 2026: [`nextlist-2026-10.md`](nextlist-2026-10.md). Only October's outcome was unknown.

Pooled over the backtest, p's Brier score was 0.2295, r0's 0.2311 and r1's 0.2300: p minus r0 was -0.0016 (95% interval -0.0034 to +0.0003) and p minus r1 -0.0004 (-0.0019 to +0.0010). Both intervals include zero, so the backtest does not show that the cells add anything beyond the plain shares; this plan tests the list on a month nobody has seen, it does not assume it is better.

p's Brier score was below r0's in 43 of 81 months and below r1's in 47 of 81. Those month shares are the honest chance of each bar holding in a single month, about 53% and 58%. In the six earlier Octobers (2020 to 2025) the counts were 2 of 6 and 3 of 6; in the latest 12 backtest months (October 2025 to September 2026), 8 of 12 and 8 of 12. A miss on one month is a failed bar, said plainly; it does not by itself undo the backtest, and a hit does not prove the list is better.

p also expected more than happened: 3,659 generator-months were on time against 3,941.2 expected, and among generator-months with high p (p from 0.5 to 0.6; 810 generator-months, mean p 0.5357) the on-time share was 0.4407.

## Expected sizes

p expects 56.8 of the 161 generators on time (4,116.5 of 11,460.2 MW). The practice list for September 2026, built from EIA's August workbook with the same code, had the same keys as the cohort file's September rows (C1 held) and the same Brier scores as the backtest's September (C2 held; p 0.2147, r0 0.2230, r1 0.2256). The job passed 16 of 16 unit tests.

## Limits

p describes earlier generators like each one; it is not a forecast made with knowledge of any plant, and it is not advice. One month is a small sample, and generators at the same plant tend to move together: the 161 generators sit at only 136 plants. The bars are set so that one month can pass or fail them.
