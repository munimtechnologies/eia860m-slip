# EIA-860M planned operating months: on-time share by stage and lead time

leadtime 0.1.0 on eia860m-slip 0.3.1; data core_eia860m__changelog_generators.parquet (reports to 2026-08; rows for report months 2016-01 to 2023-06). MV2 of Munim, Inc. (made with AI agents).

A row: a generator listed as planned (P, L, T, U, V, TS, OT) in a report with a planned operating month 0-24 months ahead, scored once its outcome window has closed (planned month + 12 + 2 months at or before the last report): on time = online by the planned month; late = online 1-12 months after it; not online = not within 12 months of it. Shares are of MW. Stage groups: early = P, L; approved = T; U; V; TS; OT. Lead = planned month minus report month. Report months end 38 months before the last report, so every lead band covers the same months.

## On-time share by stage group and lead band (MW), all generators

| group | stage | 00-03 | 04-06 | 07-12 | 13-24 |
|---|---|---|---|---|---|
| all | early | 0.132 | 0.140 | 0.158 | 0.125 |
| all | approved | 0.255 | 0.225 | 0.210 | 0.176 |
| all | U | 0.302 | 0.285 | 0.322 | 0.246 |
| all | V | 0.409 | 0.425 | 0.368 | 0.139 |

## On-time share by stage group and lead band (MW), by technology group

| group | stage | 00-03 | 04-06 | 07-12 | 13-24 |
|---|---|---|---|---|---|
| all | early | 0.132 | 0.140 | 0.158 | 0.125 |
| all | approved | 0.255 | 0.225 | 0.210 | 0.176 |
| all | U | 0.302 | 0.285 | 0.322 | 0.246 |
| all | V | 0.409 | 0.425 | 0.368 | 0.139 |
| solar | early | 0.136 | 0.112 | 0.138 | 0.091 |
| solar | approved | 0.326 | 0.182 | 0.189 | 0.143 |
| solar | U | 0.264 | 0.267 | 0.299 | 0.236 |
| solar | V | 0.427 | 0.432 | 0.257 | 0.211 |
| battery | early | 0.068 | 0.064 | 0.072 | 0.051 |
| battery | approved | 0.360 | 0.102 | 0.077 | 0.163 |
| battery | U | 0.148 | 0.141 | 0.191 | 0.180 |
| battery | V | 0.250 | 0.215 | 0.331 | 0.337 |
| wind_onshore | early | 0.103 | 0.286 | 0.262 | 0.156 |
| wind_onshore | approved | 0.590 | 0.459 | 0.338 | 0.276 |
| wind_onshore | U | 0.343 | 0.341 | 0.387 | 0.122 |
| wind_onshore | V | 0.466 | 0.482 | 0.497 | 0.747 |
| gas_cc | early | 0.727 | 1.000 | 0.033 | 0.247 |
| gas_cc | approved | 0.000 | 0.000 | 0.000 | 0.217 |
| gas_cc | U | 0.399 | 0.318 | 0.331 | 0.365 |
| gas_cc | V | 0.398 | 0.446 | 0.455 | 0.198 |
| gas_ct | early | 0.002 | 0.059 | 0.097 | 0.092 |
| gas_ct | approved | 1.000 | 0.000 | 0.016 | 0.028 |
| gas_ct | U | 0.112 | 0.136 | 0.232 | 0.046 |
| gas_ct | V | 0.309 | 0.360 | 0.395 | 0.141 |

## Every cell

| stage | band | rows | generators | mw | on_time_share | late_share | not_online_share | on_time_count_share |
|---|---|---|---|---|---|---|---|---|
| early | 00-03 | 875 | 448 | 18497.4 | 0.132 | 0.303 | 0.565 | 0.210 |
| early | 04-06 | 2728 | 963 | 64322.4 | 0.140 | 0.315 | 0.545 | 0.115 |
| early | 07-12 | 7593 | 1416 | 357996.4 | 0.158 | 0.318 | 0.524 | 0.113 |
| early | 13-24 | 17387 | 1527 | 1875236.4 | 0.125 | 0.176 | 0.699 | 0.094 |
| approved | 00-03 | 791 | 477 | 10447.0 | 0.255 | 0.265 | 0.481 | 0.197 |
| approved | 04-06 | 1999 | 831 | 36149.3 | 0.225 | 0.420 | 0.354 | 0.156 |
| approved | 07-12 | 4272 | 1042 | 171988.0 | 0.210 | 0.433 | 0.357 | 0.158 |
| approved | 13-24 | 6665 | 589 | 630726.9 | 0.176 | 0.285 | 0.539 | 0.117 |
| U | 00-03 | 5131 | 1774 | 190762.7 | 0.302 | 0.582 | 0.117 | 0.236 |
| U | 04-06 | 5316 | 2130 | 311576.7 | 0.285 | 0.571 | 0.144 | 0.245 |
| U | 07-12 | 6247 | 1552 | 649498.4 | 0.322 | 0.494 | 0.184 | 0.283 |
| U | 13-24 | 4138 | 506 | 636740.1 | 0.246 | 0.292 | 0.462 | 0.194 |
| V | 00-03 | 11795 | 3421 | 627147.3 | 0.409 | 0.533 | 0.058 | 0.366 |
| V | 04-06 | 3599 | 1470 | 356847.4 | 0.425 | 0.500 | 0.074 | 0.338 |
| V | 07-12 | 1901 | 548 | 323299.3 | 0.368 | 0.498 | 0.134 | 0.300 |
| V | 13-24 | 315 | 79 | 57078.8 | 0.139 | 0.566 | 0.295 | 0.206 |
| TS | 00-03 | 5480 | 1745 | 234061.2 | 0.444 | 0.484 | 0.071 | 0.444 |
| TS | 04-06 | 711 | 291 | 17581.9 | 0.133 | 0.679 | 0.188 | 0.340 |
| TS | 07-12 | 117 | 33 | 786.4 | 0.168 | 0.305 | 0.527 | 0.470 |
| TS | 13-24 | 30 | 4 | 96.7 | 0.736 | 0.000 | 0.264 | 0.967 |
| OT | 00-03 | 69 | 20 | 4573.0 | 0.207 | 0.133 | 0.659 | 0.159 |
| OT | 04-06 | 43 | 18 | 1767.6 | 0.424 | 0.336 | 0.240 | 0.093 |
| OT | 07-12 | 81 | 19 | 3338.8 | 0.449 | 0.064 | 0.487 | 0.074 |
| OT | 13-24 | 68 | 9 | 1706.2 | 0.146 | 0.000 | 0.854 | 0.015 |

## Checks

```
{
 "C1": {
  "months": {
   "2017-01": {
    "expected_mw": 66278.6,
    "expected_n": 833,
    "got_mw": 66278.6,
    "got_n": 833
   },
   "2019-01": {
    "expected_mw": 56235.6,
    "expected_n": 792,
    "got_mw": 56235.6,
    "got_n": 792
   },
   "2021-01": {
    "expected_mw": 80740.6,
    "expected_n": 1061,
    "got_mw": 80740.6,
    "got_n": 1061
   }
  },
  "pass": true
 },
 "C2": {
  "min_generators": 20,
  "thin_cells": [],
  "pass": true
 },
 "C3": {
  "cells": 24,
  "not_adding_up": 0,
  "rows": 87351,
  "cell_rows": 87351,
  "pass": true
 },
 "C4": {
  "duplicate_key_months": 0,
  "rows_outside_window": 0,
  "first_month": "2016-01",
  "last_month": "2023-06",
  "pass": true
 },
 "all_pass": true
}
```

## Predictions

```
{
 "L1": {
  "on_time_by_band": {
   "U": {
    "00-03": 0.3017,
    "04-06": 0.2848,
    "07-12": 0.322,
    "13-24": 0.2457
   },
   "V": {
    "00-03": 0.4088,
    "04-06": 0.4253,
    "07-12": 0.3683,
    "13-24": 0.1389
   }
  },
  "non_increasing": {
   "U": false,
   "V": false
  },
  "held": false
 },
 "L2": {
  "fall_V": 0.2699,
  "fall_early": 0.0068,
  "held": true
 },
 "L3": {
  "V_00_03_on_time": 0.4088,
  "floor": 0.45,
  "held": false
 },
 "L4": {
  "early_13_24_on_time": 0.1247,
  "ceiling": 0.2,
  "held": true
 },
 "L5": {
  "V_07_12_on_time": 0.3683,
  "early_00_03_on_time": 0.1316,
  "held": true
 },
 "L6": {
  "early_13_24_not_online": 0.6992,
  "floor": 0.5,
  "held": true
 }
}
```
