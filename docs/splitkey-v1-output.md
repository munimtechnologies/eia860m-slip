# Plans re-filed at the same plant under new generator ids (rule S)

splitkey 0.1.0 on eia860m-slip 0.3.1 and leadtime 0.1.0; data core_eia860m__changelog_generators.parquet (reports to 2026-08). MV2 of Munim, Inc. (made with AI agents). Code Apache-2.0; tables CC BY 4.0.

Rule S: leavers (planned, never operating under their key, gone from EIA-860M) at one plant and fuel family whose exits are at most 3 months apart form a cluster; its arrivals are the plant's generators of that family first listed after the cluster's first listing and from 6 months before its first exit to 6 months after its last; it is linked when the arrivals' capacity is within 0.20 of the cluster's, and re-scored with the month the last arrival came online.

## Counts

```
{
 "leavers": 1147,
 "leaver_mw": 119643.9,
 "clusters": 873,
 "linked_clusters": 23,
 "linked_leavers": 47,
 "linked_leaver_mw": 3971.7,
 "replaced_leavers": 25,
 "replaced_leaver_mw": 2655.4,
 "possible_leavers": 45,
 "possible_leaver_mw": 5496.1
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
  "leavers_not_leaving": 0,
  "wrong_plant_or_family": 0,
  "arrivals_reused": 0,
  "leaver_is_own_arrival": 0,
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
   "rows_changed": 82,
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
   "rows_changed": 225,
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
 "S1": {
  "replaced_share": 0.0235,
  "range": [
   0.03,
   0.2
  ],
  "held": false
 },
 "S2": {
  "on_time_before": 0.3247,
  "on_time_after": 0.3249,
  "rise": 0.0002,
  "ceiling": 0.02,
  "held": true
 },
 "S3": {
  "U_13_24": 0.0654,
  "cohort": 0.0235,
  "held": true
 },
 "S4": {
  "replaced_share": {
   "gas_cc": 0.1232,
   "solar": 0.0041,
   "wind_onshore": 0.0314,
   "battery": 0.0
  },
  "held": true
 },
 "S5": {
  "before": {
   "L1": false,
   "L2": true,
   "L3": false,
   "L4": true,
   "L5": true,
   "L6": true
  },
  "after": {
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

| part | rows | mw | not_online_mw | linked_mw | replaced_mw | possible_mw | replaced_share | possible_share | on_time_before | on_time_after | not_online_before | not_online_after |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all | 78646 | 4550498.4 | 871839.9 | 20877.4 | 20507.0 | 21976.0 | 0.024 | 0.025 | 0.325 | 0.325 | 0.192 | 0.188 |

## By technology group

| part | rows | mw | not_online_mw | linked_mw | replaced_mw | possible_mw | replaced_share | possible_share | on_time_before | on_time_after | not_online_before | not_online_after |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| solar | 45802 | 1758347.3 | 366047.2 | 1770.8 | 1510.4 | 1758.8 | 0.004 | 0.005 | 0.309 | 0.309 | 0.208 | 0.207 |
| wind_onshore | 7104 | 1036807.7 | 177849.8 | 5590.0 | 5590.0 | 5590.0 | 0.031 | 0.031 | 0.389 | 0.389 | 0.172 | 0.168 |
| gas_cc | 3090 | 814074.8 | 80690.0 | 9945.0 | 9945.0 | 9945.0 | 0.123 | 0.123 | 0.399 | 0.399 | 0.099 | 0.087 |
| battery | 10382 | 527436.8 | 122916.7 | 0.000 | 0.000 | 240.6 | 0.000 | 0.002 | 0.230 | 0.230 | 0.233 | 0.233 |
| gas_ct | 3126 | 258493.4 | 67953.2 | 3417.6 | 3417.6 | 4397.6 | 0.050 | 0.065 | 0.240 | 0.240 | 0.263 | 0.263 |

## By stage at the report

| part | rows | mw | not_online_mw | linked_mw | replaced_mw | possible_mw | replaced_share | possible_share | on_time_before | on_time_after | not_online_before | not_online_after |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| approved | 8691 | 295111.7 | 110033.3 | 1277.8 | 1233.8 | 1511.8 | 0.011 | 0.014 | 0.219 | 0.219 | 0.373 | 0.369 |
| construction | 47440 | 3254557.9 | 380219.9 | 19246.2 | 19246.2 | 19486.8 | 0.051 | 0.051 | 0.357 | 0.357 | 0.117 | 0.113 |
| other | 204 | 10555.9 | 5942.7 | 32.4 | 0.000 | 32.4 | 0.000 | 0.005 | 0.303 | 0.303 | 0.563 | 0.563 |
| permitting | 7467 | 249711.1 | 132288.9 | 214.0 | 0.000 | 918.0 | 0.000 | 0.007 | 0.128 | 0.128 | 0.530 | 0.530 |
| planning | 5939 | 315324.9 | 181809.4 | 101.0 | 21.0 | 21.0 | 0.000 | 0.000 | 0.153 | 0.153 | 0.577 | 0.577 |
| testing | 8905 | 425236.9 | 61545.7 | 6.000 | 6.000 | 6.000 | 0.000 | 0.000 | 0.397 | 0.397 | 0.145 | 0.145 |

## Stage-by-lead cells (0-24-month rows)

| part | rows | mw | not_online_mw | linked_mw | replaced_mw | possible_mw | replaced_share | possible_share | on_time_before | on_time_after | not_online_before | not_online_after |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| early 00-03 | 875 | 18497.4 | 10459.3 | 16.2 | 0.000 | 16.2 | 0.000 | 0.002 | 0.132 | 0.132 | 0.565 | 0.565 |
| early 04-06 | 2728 | 64322.4 | 35069.7 | 51.6 | 3.000 | 121.6 | 0.000 | 0.004 | 0.140 | 0.140 | 0.545 | 0.545 |
| early 07-12 | 7593 | 357996.4 | 187690.0 | 247.2 | 18.0 | 801.2 | 0.000 | 0.004 | 0.158 | 0.158 | 0.524 | 0.524 |
| early 13-24 | 17387 | 1875236.4 | 1311151.7 | 1421.2 | 1073.4 | 1836.2 | 0.001 | 0.001 | 0.125 | 0.125 | 0.699 | 0.699 |
| approved 00-03 | 791 | 10447.0 | 5023.7 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.255 | 0.255 | 0.481 | 0.481 |
| approved 04-06 | 1999 | 36149.3 | 12801.5 | 0.000 | 0.000 | 87.0 | 0.000 | 0.007 | 0.225 | 0.225 | 0.354 | 0.354 |
| approved 07-12 | 4272 | 171988.0 | 61369.0 | 1277.8 | 1233.8 | 1424.8 | 0.020 | 0.023 | 0.210 | 0.211 | 0.357 | 0.350 |
| approved 13-24 | 6665 | 630726.9 | 340002.5 | 3995.2 | 3995.2 | 4205.2 | 0.012 | 0.012 | 0.176 | 0.179 | 0.539 | 0.533 |
| U 00-03 | 5131 | 190762.7 | 22232.8 | 166.0 | 166.0 | 166.0 | 0.007 | 0.007 | 0.302 | 0.302 | 0.117 | 0.117 |
| U 04-06 | 5316 | 311576.7 | 44900.9 | 1542.9 | 1542.9 | 1542.9 | 0.034 | 0.034 | 0.285 | 0.285 | 0.144 | 0.141 |
| U 07-12 | 6247 | 649498.4 | 119775.1 | 9072.3 | 9072.3 | 9072.3 | 0.076 | 0.076 | 0.322 | 0.323 | 0.184 | 0.173 |
| U 13-24 | 4138 | 636740.1 | 294236.1 | 19254.0 | 19254.0 | 22054.0 | 0.065 | 0.075 | 0.246 | 0.246 | 0.462 | 0.438 |
| V 00-03 | 11795 | 627147.3 | 36237.6 | 4030.0 | 4030.0 | 4030.0 | 0.111 | 0.111 | 0.409 | 0.409 | 0.058 | 0.057 |
| V 04-06 | 3599 | 356847.4 | 26518.6 | 3315.0 | 3315.0 | 3315.0 | 0.125 | 0.125 | 0.425 | 0.425 | 0.074 | 0.065 |
| V 07-12 | 1901 | 323299.3 | 43201.3 | 1105.0 | 1105.0 | 1105.0 | 0.026 | 0.026 | 0.368 | 0.368 | 0.134 | 0.130 |
| V 13-24 | 315 | 57078.8 | 16824.7 | 0.000 | 0.000 | 7860.0 | 0.000 | 0.467 | 0.139 | 0.139 | 0.295 | 0.295 |

## Capacity tolerance

| tolerance | linked_clusters | replaced_leavers | replaced_share | on_time_after | not_online_after |
|---|---|---|---|---|---|
| 0.050 | 18 | 16 | 0.011 | 0.325 | 0.191 |
| 0.100 | 21 | 21 | 0.023 | 0.325 | 0.189 |
| 0.200 | 23 | 25 | 0.024 | 0.325 | 0.188 |
| 0.300 | 25 | 28 | 0.024 | 0.325 | 0.188 |

Crediting the first arrival's month instead of the last: {"on_time_after": 0.3249, "not_online_after": 0.1883}

## Every linked cluster

23 links.

| plant | name | state | family | leavers | leaver_mw | arrivals | arrival_mw | last_listed | arrived | planned_was | planned_new | online_all | online_first | not_online_mw_rows | lt_not_online_mw_rows |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 60356 | South Field Energy | OH | gas | 60356/SFECC | 1105.0 | 60356/SFCT1; 60356/SFCT2; 60356/SFST1; 60356/SFST2 | 1210.4 | 2020-09 | 2020-10 | 2021-01 | 2021-01 | 2021-10 | 2021-08 | 9945.0 | 23205.0 |
| 61044 | La Joya NM | NM | wind_onshore | 61044/WT1 | 306.2 | 61044/LAJ1; 61044/LAJ2 | 307.1 | 2020-10 | 2020-09 | 2020-12 | 2020-12 | 2021-06 | 2021-02 | 5590.0 | 11582.0 |
| 60264 | Bacliff | TX | gas | 60264/CLGT1; 60264/CLGT2; 60264/CLGT3; 60264/CLGT4; 60264/CLGT5; 60264/CLGT6 | 427.2 | 60264/BCGT1; 60264/BCGT2; 60264/BCGT3; 60264/BCGT4; 60264/BCGT5; 60264/BCGT6 | 427.2 | 2016-11 | 2016-12 | 2016-11 | 2017-01 | 2018-07 | 2018-07 | 3417.6 | 3417.6 |
| 60094 | Blythe Solar III, LLC | CA | solar | 60094/BLCK1; 60094/BLCK2; 60094/BLCK3; 60094/BLCK4 | 124.8 | 60094/BLSL3 | 136.8 | 2020-02 | 2020-02 | 2020-12 | 2020-05 | 2020-05 | 2020-05 | 655.2 | 2152.8 |
| 60095 | Blythe Solar IV, LLC | CA | solar | 60095/BLCK1; 60095/BLCK2; 60095/BLCK3; 60095/BLCK4 | 124.8 | 60095/BLS4A; 60095/BLS4B | 137.4 | 2020-02 | 2020-02 | 2020-12 | 2020-05 | 2020-11 | 2020-11 | 655.2 | 2152.8 |
| 64507 | OETN1 | TN | solar | 64507/OEALD | 100.0 | 64507/OETN1 | 100.0 | 2022-01 | 2022-02 | 2022-12 | 2022-12 | 2023-03 | 2023-03 | 200.0 | 1200.0 |
| 64098 | Tesla Reno GigaFactory | NV | solar | 64098/4 | 16.2 | 64098/RA; 64098/RB; 64098/RC; 64098/RD; 64098/RDP; 64098/RE; 64098/REP | 15.3 | 2021-10 | 2021-11 | 2021-11 | 2022-03 |  | 2022-03 | 180.4 | 207.2 |
| 64240 | Holley Road Solar | NY | solar | 64240/#0879 | 20.0 | 64240/879 | 20.0 | 2021-12 | 2022-01 | 2022-09 | 2022-09 |  |  | 80.0 | 280.0 |
| 58800 | Hop Bottom | PA | gas | 58800/GEN1; 58800/GEN2; 58800/GEN3; 58800/GEN4; 58800/GEN5 | 22.0 | 58800/1; 58800/2; 58800/3 | 21.0 | 2016-05 | 2016-04 | 2017-03 | 2017-06 |  |  | 44.0 | 44.0 |
| 58816 | Bayles | PA | gas | 58816/GEN1; 58816/GEN2; 58816/GEN3; 58816/GEN4; 58816/GEN5 | 22.0 | 58816/1; 58816/2; 58816/3 | 21.0 | 2016-05 | 2016-04 | 2017-03 | 2017-09 |  |  | 44.0 | 44.0 |
| 1272 | Colby City of | KS | oil | 1272/10 | 3.000 | 1272/3A | 3.000 | 2024-01 | 2024-02 | 2024-03 |  | 2019-08 | 2019-08 | 42.0 | 57.0 |
| 59418 | Amity Energy LLC | PA | gas | 59418/GEN1; 59418/GEN2; 59418/GEN3; 59418/GEN4; 59418/GEN5 | 22.0 | 59418/1; 59418/2; 59418/3 | 21.0 | 2016-06 | 2016-04 | 2017-06 | 2017-09 |  |  | 22.0 | 66.0 |
| 57057 | Quinhagak | AK | oil | 57057/1A | 0.500 | 57057/3A | 0.500 | 2019-04 | 2019-05 | 2019-08 | 2019-08 | 2019-08 | 2019-08 | 2.000 | 2.000 |
| 61982 | Columbia Solar Power Plant | FL | solar | 61982/PV | 74.9 | 61982/PV1 | 74.9 | 2019-01 | 2019-01 | 2020-03 | 2020-03 | 2020-03 | 2020-03 | 0.000 | 449.4 |
| 63508 | Camino Solar | CA | solar | 63508/CS1 | 44.0 | 63508/CSPV1 | 44.0 | 2020-11 | 2020-12 | 2022-05 | 2022-05 | 2025-04 | 2025-04 | 0.000 | 308.0 |
| 64974 | Daybreak Solar | OR | solar | 64974/BOS2 | 140.0 | 64974/DBS1 | 140.0 | 2021-11 | 2021-11 | 2022-12 | 2022-12 | 2025-03 | 2025-03 | 0.000 | 280.0 |
| 63508 | Camino Solar | CA | battery | 63508/CS2 | 11.0 | 63508/CSBA1 | 11.0 | 2020-11 | 2020-12 | 2022-05 | 2022-05 |  |  | 0.000 | 77.0 |
| 63168 | USS Pheasant Solar LLC | MN | solar | 63168/HNCCK | 1.000 | 63168/PHSNT | 1.000 | 2019-10 | 2019-10 | 2020-11 | 2020-11 | 2020-11 | 2020-11 | 0.000 | 2.000 |
| 10554 | Formosa Utility Venture Ltd | TX | gas | 10554/3TGB1; 10554/3TGB2 | 204.0 | 10554/3TBG1; 10554/3TBG2 | 204.0 | 2017-03 | 2017-04 | 2019-12 | 2019-12 | 2023-01 | 2023-01 | 0.000 | 0.000 |
| 67914 | Delta Blues Advanced Power Station | MS | gas | 67914/1B | 402.0 | 67914/1C | 341.7 | 2024-11 | 2024-12 | 2028-05 | 2028-05 |  |  | 0.000 | 0.000 |
| 69056 | CO Bar Solar and BESS | AZ | battery | 69056/CBCBA | 400.0 | 69056/CBBA | 400.0 | 2025-08 | 2025-08 | 2027-12 | 2027-12 |  |  | 0.000 | 0.000 |
| 69056 | CO Bar Solar and BESS | AZ | solar | 69056/CBCPV | 400.0 | 69056/CBPV | 400.0 | 2025-08 | 2025-08 | 2027-12 | 2027-12 |  |  | 0.000 | 0.000 |
| 69895 | Gateway#1&2 (Newark CA) | CA | solar | 69895/#1&2G | 1.100 | 69895/Gy1a2 | 1.100 | 2026-05 | 2026-05 | 2027-04 | 2027-04 |  |  | 0.000 | 0.000 |
