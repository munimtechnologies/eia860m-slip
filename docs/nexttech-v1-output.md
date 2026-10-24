# nexttech 0.1.0: the next-month share of EIA-860M by technology

Scores docs/nexttech-plan.md (T0 to T4). MV2 of Munim, Inc. (made with AI agents).

## Files

Changelog: https://raw.githubusercontent.com/munimtechnologies/eia860m-slip/a3ce0851c47d820ba5f8a0556358b4abef960909/data/eia860m_changelog_from_workbooks.csv.gz (1054060 bytes, md5 4fb178fbed7052b9e6618b481cab94f8; 117756 rows). Expected 1054060 bytes and 117756 rows: True.

Workbooks read: 134. With errors: none.

## Predictions

| id | outcome | value | bar |
|---|---|---|---|
| T0 | held | 2016-2019 1980 of 4223; 2022-2025 2110 of 6047; without a technology 32 and 25 | reproduces 1980 of 4223 and 2110 of 6047, with at most 1% of each period's cohort without a technology |
| T1 | held | 0.5059 to 0.3536 (1243 of 2457 to 1292 of 3654) | solar share lower in 2022-2025 than in 2016-2019 (at least 30 in each) |
| T2 | failed | 0.4011 to 0.4548 (298 of 743 to 191 of 420) | gas share lower in 2022-2025 than in 2016-2019 (at least 30 in each) |
| T3 | held | 0.4420 to 0.2990 (61 of 138 to 453 of 1515) | batteries share lower in 2022-2025 than in 2016-2019 (at least 30 in each) |
| T4 | held | within 0.0945 of total 0.1199 (standardized 0.3744) | within-technology fall (2016-2019 share minus mix-standardized 2022-2025 share) at least half the total fall |

Held: 3 of 4 scored (T0 is a check, not counted).

## By period and technology

| period | technology | cohort | operating | share | MW | MW operating | MW share |
|---|---|---|---|---|---|---|---|
| 2016-01 to 2019-12 | solar | 2457 | 1243 | 0.5059 | 31117.0 | 16823.5 | 0.5407 |
| 2016-01 to 2019-12 | batteries | 138 | 61 | 0.4420 | 946.7 | 429.1 | 0.4533 |
| 2016-01 to 2019-12 | gas | 743 | 298 | 0.4011 | 85713.2 | 38597.1 | 0.4503 |
| 2016-01 to 2019-12 | wind | 461 | 217 | 0.4707 | 42000.9 | 24369.6 | 0.5802 |
| 2016-01 to 2019-12 | other | 424 | 161 | 0.3797 | 4948.8 | 2685.7 | 0.5427 |
| 2016-01 to 2019-12 | all | 4223 | 1980 | 0.4689 | 164726.6 | 82905.0 | 0.5033 |
| 2022-01 to 2025-12 | solar | 3654 | 1292 | 0.3536 | 181777.4 | 68573.2 | 0.3772 |
| 2022-01 to 2025-12 | batteries | 1515 | 453 | 0.2990 | 88430.9 | 30842.9 | 0.3488 |
| 2022-01 to 2025-12 | gas | 420 | 191 | 0.4548 | 32249.5 | 18111.7 | 0.5616 |
| 2022-01 to 2025-12 | wind | 268 | 108 | 0.4030 | 47352.7 | 20709.1 | 0.4373 |
| 2022-01 to 2025-12 | other | 190 | 66 | 0.3474 | 5936.1 | 4303.1 | 0.7249 |
| 2022-01 to 2025-12 | all | 6047 | 2110 | 0.3489 | 355746.6 | 142540.0 | 0.4007 |

## By year and technology

| year | technology | cohort | operating | share |
|---|---|---|---|---|
| 2015 | batteries | 12 | 4 | 0.3333 |
| 2015 | gas | 33 | 17 | 0.5152 |
| 2015 | other | 23 | 12 | 0.5217 |
| 2015 | solar | 227 | 118 | 0.5198 |
| 2015 | wind | 52 | 36 | 0.6923 |
| 2016 | batteries | 14 | 6 | 0.4286 |
| 2016 | gas | 205 | 74 | 0.3610 |
| 2016 | other | 152 | 59 | 0.3882 |
| 2016 | solar | 459 | 256 | 0.5577 |
| 2016 | wind | 121 | 62 | 0.5124 |
| 2017 | batteries | 33 | 15 | 0.4545 |
| 2017 | gas | 195 | 76 | 0.3897 |
| 2017 | other | 107 | 45 | 0.4206 |
| 2017 | solar | 746 | 367 | 0.4920 |
| 2017 | wind | 90 | 54 | 0.6000 |
| 2018 | batteries | 30 | 15 | 0.5000 |
| 2018 | gas | 219 | 103 | 0.4703 |
| 2018 | other | 89 | 28 | 0.3146 |
| 2018 | solar | 610 | 335 | 0.5492 |
| 2018 | wind | 118 | 46 | 0.3898 |
| 2019 | batteries | 61 | 25 | 0.4098 |
| 2019 | gas | 124 | 45 | 0.3629 |
| 2019 | other | 76 | 29 | 0.3816 |
| 2019 | solar | 642 | 285 | 0.4439 |
| 2019 | wind | 132 | 55 | 0.4167 |
| 2020 | batteries | 89 | 31 | 0.3483 |
| 2020 | gas | 108 | 46 | 0.4259 |
| 2020 | other | 60 | 16 | 0.2667 |
| 2020 | solar | 774 | 366 | 0.4729 |
| 2020 | wind | 229 | 81 | 0.3537 |
| 2021 | batteries | 255 | 72 | 0.2824 |
| 2021 | gas | 267 | 104 | 0.3895 |
| 2021 | other | 74 | 28 | 0.3784 |
| 2021 | solar | 826 | 320 | 0.3874 |
| 2021 | wind | 144 | 62 | 0.4306 |
| 2022 | batteries | 316 | 76 | 0.2405 |
| 2022 | gas | 155 | 58 | 0.3742 |
| 2022 | other | 57 | 25 | 0.4386 |
| 2022 | solar | 729 | 241 | 0.3306 |
| 2022 | wind | 69 | 28 | 0.4058 |
| 2023 | batteries | 389 | 96 | 0.2468 |
| 2023 | gas | 84 | 37 | 0.4405 |
| 2023 | other | 60 | 20 | 0.3333 |
| 2023 | solar | 886 | 303 | 0.3420 |
| 2023 | wind | 91 | 34 | 0.3736 |
| 2024 | batteries | 422 | 143 | 0.3389 |
| 2024 | gas | 74 | 34 | 0.4595 |
| 2024 | other | 40 | 12 | 0.3000 |
| 2024 | solar | 1047 | 382 | 0.3649 |
| 2024 | wind | 42 | 21 | 0.5000 |
| 2025 | batteries | 388 | 138 | 0.3557 |
| 2025 | gas | 107 | 62 | 0.5794 |
| 2025 | other | 33 | 9 | 0.2727 |
| 2025 | solar | 992 | 366 | 0.3690 |
| 2025 | wind | 66 | 25 | 0.3788 |
| 2026 | batteries | 380 | 114 | 0.3000 |
| 2026 | gas | 79 | 44 | 0.5570 |
| 2026 | other | 49 | 14 | 0.2857 |
| 2026 | solar | 818 | 237 | 0.2897 |
| 2026 | wind | 38 | 14 | 0.3684 |

Cohort generators without a technology, by month: 2015-12 1; 2016-06 1; 2016-07 1; 2017-01 2; 2017-03 6; 2017-04 2; 2017-05 2; 2017-07 2; 2017-08 5; 2017-09 2; 2017-10 1; 2017-11 3; 2017-12 1; 2018-01 2; 2018-02 2; 2021-04 1; 2021-05 3; 2021-06 1; 2021-08 1; 2021-09 2; 2021-10 2; 2022-05 2; 2022-06 2; 2022-07 2; 2022-08 3; 2022-09 1; 2023-01 1; 2023-04 1; 2023-05 1; 2023-07 2; 2023-08 1; 2024-02 1; 2024-03 1; 2024-04 1; 2024-05 1; 2024-06 1; 2024-09 1; 2025-04 1; 2025-05 1; 2025-06 1.
