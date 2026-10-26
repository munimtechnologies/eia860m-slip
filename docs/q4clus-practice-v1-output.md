# q4clus 0.1.0: solar and batteries by months since the last listing, 2026-09, whole plants resampled

Scores docs/q4clus-plan.md (C1, C2, R1 to R3, K1 to K3). MV2 of Munim, Inc. (made with AI agents).

Cohort file: https://raw.githubusercontent.com/munimtechnologies/eia860m-slip/ea63c150a8ed41cc1fcad901ccab51686c924d46/data/nexttech_cohort.csv (950816 bytes, md5 1681df9fdee9878ca2c359d1239c6467; 14807 rows).

Month file 2026-09: practice/monthrun_cohort_2026-09.csv (11411 bytes, md5 98ec710f00fcd36ebb300d32dfefd7f3; 170 rows).

## Checks

| id | outcome | value |
|---|---|---|
| C1 | held | 2026-09: 57 of 170 against 57 of 170 |
| C2 | held | 170 rows, 0 disagree |

## Direction bars

| id | outcome | value | bar |
|---|---|---|---|
| R1 | held | 1 month minus first: +0.0098, 95% interval -0.2158 to +0.2452; 1 month: 14 of 35 at 34 plants; first: 16 of 41 at 40 plants | Solar: 1 month after the last listing minus first listings is above 0 |
| R2 | not scored | 1 month minus first: +0.0795, 95% interval -0.3182 to +0.4835; 1 month: 5 of 11 at 11 plants; first: 6 of 16 at 16 plants | Batteries: 1 month after the last listing minus first listings is above 0 |
| R3 | not scored | 1 month minus 2-3 months: +0.1917, 95% interval -0.0463 to +0.4273; 1 month: 14 of 35 at 34 plants; 2-3 months: 5 of 24 at 24 plants | Solar: 1 month after the last listing minus 2-3 months after is above 0 |

Direction bars held: 1 of 1 scored.

## Consistency bars

| id | outcome | interval against the earlier difference | bar |
|---|---|---|---|
| K1 | held | -0.2158 to +0.2452 against +0.0498 | R1's 95% interval contains the forty-first result's B1 difference |
| K2 | not scored | -0.3182 to +0.4835 against +0.0824 | R2's 95% interval contains the forty-first result's B2 difference |
| K3 | not scored | -0.0463 to +0.4273 against +0.1251 | R3's 95% interval contains the forty-first result's B5 difference |

Consistency bars held: 1 of 1 scored. 2000 resamples, seed 20261025.

## Practice: appended rows against the cohort's own rows

| month | rows equal | cohort rows | appended rows | group differs |
|---|---|---|---|---|
| 2026-09 | True | 170 | 170 | 0 |

## Every month, reported, not scored

| month | technology | difference | point | 95% interval | cells (on time of rows, plants) |
|---|---|---|---|---|---|
| 2026-09 | solar | 1 month minus first | +0.0098 | -0.2158 to +0.2452 | 14 of 35 at 34 plants; 16 of 41 at 40 plants |
| 2026-09 | batteries | 1 month minus first | +0.0795 | -0.3182 to +0.4835 | 5 of 11 at 11 plants; 6 of 16 at 16 plants |
| 2026-09 | solar | 1 month minus 2-3 months | +0.1917 | -0.0463 to +0.4273 | 14 of 35 at 34 plants; 5 of 24 at 24 plants |
| 2026-09 | wind | 1 month minus first | +0.0000 | not computed | 0 of 0 at 0 plants; 4 of 4 at 2 plants |
| 2026-09 | gas | 1 month minus first | +0.0000 | not computed | 0 of 6 at 3 plants; 0 of 0 at 0 plants |
| 2026-09 | all | 1 month minus first | -0.0608 | -0.2560 to +0.1370 | 19 of 52 at 45 plants; 26 of 61 at 55 plants |
| pooled | solar | 1 month minus first | +0.0098 | -0.2158 to +0.2452 | 14 of 35 at 34 plants; 16 of 41 at 40 plants |
| pooled | batteries | 1 month minus first | +0.0795 | -0.3182 to +0.4835 | 5 of 11 at 11 plants; 6 of 16 at 16 plants |
| pooled | solar | 1 month minus 2-3 months | +0.1917 | -0.0463 to +0.4273 | 14 of 35 at 34 plants; 5 of 24 at 24 plants |
| pooled | wind | 1 month minus first | +0.0000 | not computed | 0 of 0 at 0 plants; 4 of 4 at 2 plants |
| pooled | gas | 1 month minus first | +0.0000 | not computed | 0 of 6 at 3 plants; 0 of 0 at 0 plants |
| pooled | all | 1 month minus first | -0.0608 | -0.2560 to +0.1370 | 19 of 52 at 45 plants; 26 of 61 at 55 plants |

## Expected size and chance of each direction bar (fixed before scoring)

| id | expected rows (cell, compared cell) | earlier difference | chance the point is above 0 |
|---|---|---|---|
| R1 | 105, 123 | +0.0498 | 0.74 |
| R2 | 33, 48 | +0.0824 | 0.74 |
| R3 | 105, 72 | +0.1251 | 0.93 |
