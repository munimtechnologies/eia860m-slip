# Planned keys still listed beside a built replacement (rule T)

staykey 0.1.0 on eia860m-slip 0.3.1, leadtime 0.1.0 and splitkey 0.1.0; data core_eia860m__changelog_generators.parquet (reports to 2026-08). MV2 of Munim, Inc. (made with AI agents). Code Apache-2.0; tables CC BY 4.0.

Rule T: stayers (planned, never operating under their key, still listed as planned in the last report) at one plant and fuel family form a group; its twins are the plant's generators of that family that were planned, came online and were first listed after the group's first listing; it is linked when the twins' capacity is within 0.20 of the group's, and re-scored with the month the last twin came online.

## Counts

```
{
 "stayers": 2307,
 "stayer_mw": 287881.0,
 "groups": 1767,
 "linked_groups": 0,
 "linked_stayers": 0,
 "linked_stayer_mw": 0.0,
 "twins": 0,
 "twin_mw": 0.0,
 "possible_stayers": 1,
 "possible_stayer_mw": 1.0,
 "rule_s_replaced_leavers": 25,
 "twins_also_rule_s_arrivals": 0
}
```

## Checks

```
{
 "K1": {
  "cohort": {
   "got": [
    78646,
    4550498.4,
    0.3247,
    0.1916
   ],
   "published": [
    78646,
    4550498.4,
    0.325,
    0.192
   ],
   "pass": true
  },
  "cells": {
   "U 00-03": {
    "got": [
     5131,
     1774,
     190762.7,
     0.3017
    ],
    "published": [
     5131,
     1774,
     190762.7,
     0.3017
    ],
    "pass": true
   },
   "U 13-24": {
    "got": [
     4138,
     506,
     636740.1,
     0.2457
    ],
    "published": [
     4138,
     506,
     636740.1,
     0.2457
    ],
    "pass": true
   },
   "V 00-03": {
    "got": [
     11795,
     3421,
     627147.3,
     0.4088
    ],
    "published": [
     11795,
     3421,
     627147.3,
     0.4088
    ],
    "pass": true
   },
   "V 13-24": {
    "got": [
     315,
     79,
     57078.8,
     0.1389
    ],
    "published": [
     315,
     79,
     57078.8,
     0.1389
    ],
    "pass": true
   }
  },
  "pass": true
 },
 "K2": {
  "stayers_not_staying": 0,
  "twins_not_built": 0,
  "wrong_plant_or_family": 0,
  "twin_listed_too_early": 0,
  "twins_reused": 0,
  "outside_tolerance": 0,
  "replaced_outside_bound": 0,
  "pass": true
 },
 "K3": {
  "cohort": {
   "rows": [
    78646,
    78646
   ],
   "mw": [
    4550498.4,
    4550498.4
   ],
   "adds_up": true,
   "rows_changed": 0,
   "stray_changes": 0,
   "pass": true
  },
  "leadtime": {
   "rows": [
    87351,
    87351
   ],
   "mw": [
    6582226.3,
    6582226.3
   ],
   "adds_up": true,
   "rows_changed": 0,
   "stray_changes": 0,
   "pass": true
  },
  "cohort_both": {
   "rows": [
    78646,
    78646
   ],
   "mw": [
    4550498.4,
    4550498.4
   ],
   "adds_up": true,
   "rows_changed": 82,
   "stray_changes": 0,
   "pass": true
  }
 },
 "all_pass": true
}
```

## Predictions

```
{
 "T1": {
  "stayer_share": 0.2615,
  "range": [
   0.1,
   0.4
  ],
  "held": true
 },
 "T2": {
  "replaced_share": 0.0,
  "rule_s_share": 0.0235,
  "held": true
 },
 "T3": {
  "on_time_before": 0.3247,
  "on_time_after": 0.3247,
  "rise": 0.0,
  "ceiling": 0.01,
  "held": true
 },
 "T4": {
  "not_online_before": 0.1916,
  "not_online_both": 0.1884,
  "floor": 0.17,
  "held": true
 },
 "T5": {
  "before": {
   "L1": false,
   "L2": true,
   "L3": false,
   "L4": true,
   "L5": true,
   "L6": true
  },
  "both": {
   "L1": false,
   "L2": true,
   "L3": false,
   "L4": true,
   "L5": true,
   "L6": true
  },
  "unchanged": {
   "L1": true,
   "L2": true,
   "L3": true,
   "L4": true,
   "L5": true,
   "L6": true
  },
  "held": true
 }
}
```

## 0-12-month cohort rows

| part | rows | mw | not_online_mw | online_later_share | stayer_share | leaver_share | other_share | replaced_mw | possible_mw | replaced_share | possible_share | on_time_before | on_time_after | not_online_before | not_online_after | on_time_both | not_online_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all | 78646 | 4550498.4 | 871839.9 | 0.435 | 0.262 | 0.303 | 0.000 | 0.000 | 55.6 | 0.000 | 0.000 | 0.325 | 0.325 | 0.192 | 0.192 | 0.325 | 0.188 |

## By technology group

| part | rows | mw | not_online_mw | online_later_share | stayer_share | leaver_share | other_share | replaced_mw | possible_mw | replaced_share | possible_share | on_time_before | on_time_after | not_online_before | not_online_after | on_time_both | not_online_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| solar | 45802 | 1758347.3 | 366047.2 | 0.437 | 0.389 | 0.174 | 0.000 | 0.000 | 55.6 | 0.000 | 0.000 | 0.309 | 0.309 | 0.208 | 0.208 | 0.309 | 0.207 |
| wind_onshore | 7104 | 1036807.7 | 177849.8 | 0.481 | 0.224 | 0.295 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.389 | 0.389 | 0.172 | 0.172 | 0.389 | 0.168 |
| gas_cc | 3090 | 814074.8 | 80690.0 | 0.186 | 0.039 | 0.775 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.399 | 0.399 | 0.099 | 0.099 | 0.399 | 0.087 |
| battery | 10382 | 527436.8 | 122916.7 | 0.462 | 0.290 | 0.248 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.230 | 0.230 | 0.233 | 0.233 | 0.230 | 0.233 |
| gas_ct | 3126 | 258493.4 | 67953.2 | 0.413 | 0.016 | 0.571 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.240 | 0.240 | 0.263 | 0.263 | 0.240 | 0.263 |

## By stage at the report

| part | rows | mw | not_online_mw | online_later_share | stayer_share | leaver_share | other_share | replaced_mw | possible_mw | replaced_share | possible_share | on_time_before | on_time_after | not_online_before | not_online_after | on_time_both | not_online_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| approved | 8691 | 295111.7 | 110033.3 | 0.413 | 0.346 | 0.241 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.219 | 0.219 | 0.373 | 0.373 | 0.219 | 0.369 |
| construction | 47440 | 3254557.9 | 380219.9 | 0.573 | 0.176 | 0.251 | 0.000 | 0.000 | 9.400 | 0.000 | 0.000 | 0.357 | 0.357 | 0.117 | 0.117 | 0.357 | 0.113 |
| other | 204 | 10555.9 | 5942.7 | 0.013 | 0.725 | 0.262 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.303 | 0.303 | 0.563 | 0.563 | 0.303 | 0.563 |
| permitting | 7467 | 249711.1 | 132288.9 | 0.389 | 0.250 | 0.361 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.128 | 0.128 | 0.530 | 0.530 | 0.128 | 0.530 |
| planning | 5939 | 315324.9 | 181809.4 | 0.237 | 0.261 | 0.502 | 0.000 | 0.000 | 1.600 | 0.000 | 0.000 | 0.153 | 0.153 | 0.577 | 0.577 | 0.153 | 0.577 |
| testing | 8905 | 425236.9 | 61545.7 | 0.352 | 0.619 | 0.029 | 0.000 | 0.000 | 44.6 | 0.000 | 0.001 | 0.397 | 0.397 | 0.145 | 0.145 | 0.397 | 0.145 |

## Stage-by-lead cells (0-24-month rows)

| part | rows | mw | not_online_mw | online_later_share | stayer_share | leaver_share | other_share | replaced_mw | possible_mw | replaced_share | possible_share | on_time_before | on_time_after | not_online_before | not_online_after | on_time_both | not_online_both |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| early 00-03 | 875 | 18497.4 | 10459.3 | 0.513 | 0.169 | 0.318 | 0.000 | 0.000 | 1.600 | 0.000 | 0.000 | 0.132 | 0.132 | 0.565 | 0.565 | 0.132 | 0.565 |
| early 04-06 | 2728 | 64322.4 | 35069.7 | 0.415 | 0.144 | 0.440 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.140 | 0.140 | 0.545 | 0.545 | 0.140 | 0.545 |
| early 07-12 | 7593 | 357996.4 | 187690.0 | 0.358 | 0.189 | 0.453 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.158 | 0.158 | 0.524 | 0.524 | 0.158 | 0.524 |
| early 13-24 | 17387 | 1875236.4 | 1311151.7 | 0.214 | 0.270 | 0.516 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.125 | 0.125 | 0.699 | 0.699 | 0.125 | 0.699 |
| approved 00-03 | 791 | 10447.0 | 5023.7 | 0.288 | 0.007 | 0.704 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.255 | 0.255 | 0.481 | 0.481 | 0.255 | 0.481 |
| approved 04-06 | 1999 | 36149.3 | 12801.5 | 0.565 | 0.091 | 0.344 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.225 | 0.225 | 0.354 | 0.354 | 0.225 | 0.354 |
| approved 07-12 | 4272 | 171988.0 | 61369.0 | 0.493 | 0.249 | 0.258 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.210 | 0.210 | 0.357 | 0.357 | 0.211 | 0.350 |
| approved 13-24 | 6665 | 630726.9 | 340002.5 | 0.216 | 0.188 | 0.596 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.176 | 0.176 | 0.539 | 0.539 | 0.179 | 0.533 |
| U 00-03 | 5131 | 190762.7 | 22232.8 | 0.794 | 0.073 | 0.133 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.302 | 0.302 | 0.117 | 0.117 | 0.302 | 0.117 |
| U 04-06 | 5316 | 311576.7 | 44900.9 | 0.708 | 0.067 | 0.225 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.285 | 0.285 | 0.144 | 0.144 | 0.285 | 0.141 |
| U 07-12 | 6247 | 649498.4 | 119775.1 | 0.611 | 0.076 | 0.314 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.322 | 0.322 | 0.184 | 0.184 | 0.323 | 0.173 |
| U 13-24 | 4138 | 636740.1 | 294236.1 | 0.377 | 0.150 | 0.473 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.246 | 0.246 | 0.462 | 0.462 | 0.246 | 0.438 |
| V 00-03 | 11795 | 627147.3 | 36237.6 | 0.707 | 0.058 | 0.235 | 0.000 | 0.000 | 5.400 | 0.000 | 0.000 | 0.409 | 0.409 | 0.058 | 0.058 | 0.409 | 0.057 |
| V 04-06 | 3599 | 356847.4 | 26518.6 | 0.459 | 0.084 | 0.457 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 | 0.425 | 0.425 | 0.074 | 0.074 | 0.425 | 0.065 |
| V 07-12 | 1901 | 323299.3 | 43201.3 | 0.457 | 0.043 | 0.499 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.368 | 0.368 | 0.134 | 0.134 | 0.368 | 0.130 |
| V 13-24 | 315 | 57078.8 | 16824.7 | 0.308 | 0.056 | 0.637 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.139 | 0.139 | 0.295 | 0.295 | 0.139 | 0.295 |

## Capacity tolerance

| tolerance | linked_groups | replaced_stayers | replaced_share | on_time_after | not_online_after |
|---|---|---|---|---|---|
| 0.050 | 0 | 0 | 0.000 | 0.325 | 0.192 |
| 0.100 | 0 | 0 | 0.000 | 0.325 | 0.192 |
| 0.200 | 0 | 0 | 0.000 | 0.325 | 0.192 |
| 0.300 | 0 | 0 | 0.000 | 0.325 | 0.192 |

## Every linked group

0 links.

| plant | name | state | family | stayers | stayer_mw | twins | twin_mw | first_listed | twins_listed | planned_at_arrival | twins_planned | a_months | online_all | stayer_planned_last | b_advanced | not_online_mw_rows | lt_not_online_mw_rows |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
