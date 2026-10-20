# How planned generators move between stages in EIA-860M

stagemoves 0.1.0 on eia860m-slip 0.3.1; data core_eia860m__changelog_generators.parquet (reports 2016-01 to 2026-08). MV2 of Munim, Inc. (made with AI agents).

A step: a generator planned in report m with band early (P, L), approved (T) or building (U, V, TS) that has a record in force in report m + 1. Moves: forward, held, backward (to an earlier band), to_operating, exit_other (any other status). left: planned in m, no record in force in m + 1 (not a step). Rule R re-keys are one generator. MW is the capacity in report m. online_12: listed as operating in a report m + 1 to m + 12, scored only when m + 12 is at or before the last report.

## Pooled 2016-2025: the band in the next report (MW)

| band | steps | step_mw | early_mw | approved_mw | building_mw | operating_mw | other_mw | left_mw |
|---|---|---|---|---|---|---|---|---|
| early | 68958 | 8374086.2 | 8201333.3 | 40260.4 | 129933.1 | 1555.8 | 1003.6 | 66712.2 |
| approved | 24379 | 2288249.9 | 8366.2 | 2168647.9 | 109381.3 | 1599.5 | 255.0 | 16309.4 |
| building | 70416 | 5952841.7 | 4748.0 | 2872.0 | 5608238.5 | 336192.8 | 790.4 | 16280.8 |

## Every year: steps by starting band and move (MW)

| year | band | steps | step_mw | forward_mw | held_mw | backward_mw | to_operating_mw | exit_other_mw | left_mw | backward_share |
|---|---|---|---|---|---|---|---|---|---|---|
| 2016 | early | 4896 | 442084.1 | 8002.7 | 433941.0 | 0.000 | 140.4 | 0.000 | 1730.7 | 0.000 |
| 2016 | approved | 1910 | 138051.7 | 3895.9 | 134003.8 | 147.0 | 5.000 | 0.000 | 250.8 | 0.001 |
| 2016 | building | 5519 | 390119.6 | 0.000 | 370239.5 | 135.3 | 19744.8 | 0.000 | 1748.6 | 0.000 |
| 2017 | early | 5811 | 627610.0 | 15532.5 | 611929.1 | 0.000 | 33.1 | 115.3 | 6033.9 | 0.000 |
| 2017 | approved | 2259 | 206151.7 | 8270.5 | 197203.7 | 635.5 | 42.0 | 0.000 | 701.3 | 0.003 |
| 2017 | building | 5478 | 510381.2 | 0.000 | 488341.1 | 113.6 | 21926.5 | 0.000 | 1005.9 | 0.000 |
| 2018 | early | 5043 | 537637.7 | 11235.3 | 525733.6 | 0.000 | 651.0 | 17.8 | 7099.3 | 0.000 |
| 2018 | approved | 1849 | 202432.7 | 10849.3 | 190037.7 | 1313.0 | 227.7 | 5.000 | 1766.9 | 0.006 |
| 2018 | building | 4740 | 454881.9 | 0.000 | 419940.7 | 1443.7 | 33281.4 | 216.1 | 5693.9 | 0.003 |
| 2019 | early | 6159 | 616302.1 | 18987.4 | 597147.2 | 0.000 | 93.0 | 74.5 | 2552.8 | 0.000 |
| 2019 | approved | 2899 | 216144.3 | 10858.0 | 204954.1 | 41.5 | 40.7 | 250.0 | 840.1 | 0.000 |
| 2019 | building | 5050 | 401652.5 | 0.000 | 377449.4 | 844.4 | 23246.5 | 112.2 | 1150.2 | 0.002 |
| 2020 | early | 6425 | 640671.3 | 23238.0 | 617301.3 | 0.000 | 92.0 | 40.0 | 7204.9 | 0.000 |
| 2020 | approved | 2811 | 223406.6 | 12958.9 | 208705.9 | 1597.5 | 144.3 | 0.000 | 2545.5 | 0.007 |
| 2020 | building | 6649 | 554817.7 | 0.000 | 522316.6 | 585.0 | 31753.0 | 163.1 | 2179.7 | 0.001 |
| 2021 | early | 6661 | 694534.0 | 19348.9 | 674938.9 | 0.000 | 75.2 | 171.0 | 5260.0 | 0.000 |
| 2021 | approved | 2811 | 208585.2 | 11193.2 | 196999.7 | 156.3 | 236.0 | 0.000 | 1172.9 | 0.001 |
| 2021 | building | 7305 | 637756.7 | 0.000 | 601261.1 | 479.2 | 35962.4 | 54.0 | 491.0 | 0.001 |
| 2022 | early | 6589 | 812461.7 | 15207.0 | 796833.6 | 0.000 | 336.1 | 85.0 | 2063.9 | 0.000 |
| 2022 | approved | 2468 | 221799.7 | 8637.8 | 212070.6 | 1063.2 | 28.1 | 0.000 | 3801.5 | 0.005 |
| 2022 | building | 7685 | 634066.0 | 0.000 | 604877.9 | 846.1 | 28342.0 | 0.000 | 1096.5 | 0.001 |
| 2023 | early | 7621 | 994124.5 | 17858.5 | 975866.0 | 0.000 | 0.000 | 400.0 | 13385.9 | 0.000 |
| 2023 | approved | 2098 | 254910.7 | 14509.6 | 238755.8 | 1363.8 | 281.5 | 0.000 | 1918.1 | 0.005 |
| 2023 | building | 8779 | 709468.4 | 0.000 | 668407.7 | 296.6 | 40759.1 | 5.000 | 62.2 | 0.000 |
| 2024 | early | 8678 | 1160742.5 | 16453.3 | 1144264.2 | 0.000 | 25.0 | 0.000 | 7388.4 | 0.000 |
| 2024 | approved | 2358 | 305095.6 | 7855.4 | 295054.6 | 1597.0 | 588.6 | 0.000 | 981.7 | 0.005 |
| 2024 | building | 9549 | 736591.9 | 0.000 | 685216.6 | 2037.9 | 49337.4 | 0.000 | 1239.1 | 0.003 |
| 2025 | early | 11075 | 1847918.3 | 24329.9 | 1823378.4 | 0.000 | 110.0 | 100.0 | 13992.4 | 0.000 |
| 2025 | approved | 2916 | 311671.7 | 20352.7 | 290862.0 | 451.4 | 5.600 | 0.000 | 2330.6 | 0.001 |
| 2025 | building | 9662 | 923105.8 | 0.000 | 870187.9 | 838.2 | 51839.7 | 240.0 | 1613.7 | 0.001 |
| 2026 | early | 7142 | 1124379.1 | 16839.0 | 1106869.7 | 0.000 | 670.4 | 0.000 | 14803.6 | 0.000 |
| 2026 | approved | 1697 | 186820.9 | 9099.3 | 176514.2 | 1200.9 | 6.500 | 0.000 | 420.0 | 0.006 |
| 2026 | building | 6549 | 654916.0 | 0.000 | 623039.4 | 991.8 | 30884.8 | 0.000 | 1254.8 | 0.002 |

## Pooled 2016-2025: backward share by technology group

| group | building_step_mw | building_backward_mw | building_backward_share | approved_step_mw | approved_backward_mw | approved_backward_share |
|---|---|---|---|---|---|---|
| all | 5952841.7 | 7620.0 | 0.001 | 2288249.9 | 8366.2 | 0.004 |
| solar | 1953731.2 | 4408.3 | 0.002 | 801748.9 | 2826.7 | 0.004 |
| wind_onshore | 1325912.1 | 2734.9 | 0.002 | 296685.3 | 941.7 | 0.003 |
| battery | 648615.9 | 303.3 | 0.001 | 146688.0 | 658.0 | 0.004 |
| gas_cc | 1303711.1 | 35.0 | 0.000 | 755054.8 | 1841.5 | 0.002 |
| gas_ct | 297896.8 | 100.0 | 0.000 | 119506.9 | 1317.8 | 0.011 |

## Listed as operating within 12 reports, by starting band and move (closed windows)

| band | move | steps | scored_mw | online_mw | online_share |
|---|---|---|---|---|---|
| early | forward | 2040 | 161121.5 | 60439.3 | 0.375 |
| early | held | 63117 | 7582451.4 | 150932.5 | 0.020 |
| early | backward | 0 | 0.000 | 0.000 |  |
| early | to_operating | 81 | 1445.8 | 1445.8 | 1.000 |
| early | exit_other | 21 | 1003.6 | 97.3 | 0.097 |
| approved | forward | 1718 | 104786.8 | 48228.2 | 0.460 |
| approved | held | 21589 | 2084202.9 | 94810.0 | 0.045 |
| approved | backward | 96 | 8366.2 | 155.4 | 0.019 |
| approved | to_operating | 73 | 1599.5 | 1599.5 | 1.000 |
| approved | exit_other | 2 | 255.0 | 0.000 | 0.000 |
| building | forward | 0 | 0.000 | 0.000 |  |
| building | held | 61233 | 5300216.6 | 2798352.9 | 0.528 |
| building | backward | 96 | 6965.2 | 369.0 | 0.053 |
| building | to_operating | 5844 | 312851.9 | 312851.9 | 1.000 |
| building | exit_other | 17 | 790.4 | 352.3 | 0.446 |

## Largest backward steps from building

| key | plant | group | mw | moved_in | from_status | to_status | online_12 |
|---|---|---|---|---|---|---|---|
| 63488/OBSLR | Obsidian Solar Center | solar | 400.0 | 2021-01 | U | P | no |
| 62954/GEN1 | Alle-Catt Wind Energy LLC | wind_onshore | 340.0 | 2024-12 | U | T | no |
| 59971/ESTR1 | Easter | wind_onshore | 300.0 | 2019-01 | U | P | no |
| 68079/STAS1 | Stagecoach LRE | solar | 300.0 | 2024-12 | U | T | no |
| 59243/CHAN1 | Changing Winds | wind_onshore | 288.0 | 2018-02 | U | P | no |
| 65822/CRAS0 | Cradle Solar | solar | 225.0 | 2023-01 | U | T | no |
| 65822/CRAS0 | Cradle Solar | solar | 225.0 | 2024-06 | U | T | no |
| 69198/ATL10 | ATLAS Solar X, LLC | solar | 225.0 | 2025-10 | V | P |  |
| 61837/MV | Minco Wind V, LLC | wind_onshore | 220.0 | 2018-11 | V | P | no |
| 69589/BEEK1 | Beekman Solar | solar | 206.8 | 2026-02 | U | T |  |
| 63269/CRW2 | Crowned Ridge Wind II Energy Center | wind_onshore | 200.6 | 2019-12 | U | L | no |
| 57622/GEN1 | Bright Stalk Wind Farm II | wind_onshore | 200.0 | 2019-06 | U | P | no |
| 58406/1 | Chilocco Wind Farm | wind_onshore | 200.0 | 2021-10 | U | T | no |
| 65664/GEN02 | Sandrini Solar 100 | solar | 200.0 | 2022-07 | U | L | no |
| 66968/BFW00 | Blackford Wind | wind_onshore | 200.0 | 2024-06 | U | L | no |

## Back in building or operating within 6 reports of a backward move (M2)

```
{
 "generators": 102,
 "returned": 38,
 "mw": 7746.9,
 "share": 0.3725
}
```

## From early to building: through approved? (M4)

```
{
 "generators": 1823,
 "mw": 151028.8,
 "through_approved_n": 395,
 "through_approved_mw": 26372.4,
 "share": 0.1746
}
```

## Checks

```
{
 "S1": {
  "months": {
   "2017-01": {
    "expected_mw": 109382.3,
    "expected_n": 1024,
    "got_mw": 109382.3,
    "got_n": 1024
   },
   "2020-01": {
    "expected_mw": 111807.9,
    "expected_n": 1273,
    "got_mw": 111807.9,
    "got_n": 1273
   },
   "2024-01": {
    "expected_mw": 160368.0,
    "expected_n": 1537,
    "got_mw": 160368.0,
    "got_n": 1537
   }
  },
  "pass": true
 },
 "S2": {
  "rows": 33,
  "not_adding_up": 0,
  "pass": true
 },
 "S3": {
  "links": 11,
  "expected": 11,
  "pass": true
 },
 "S4": {
  "duplicate_key_months": 0,
  "missing_months": [],
  "pass": true
 },
 "all_pass": true
}
```

## Predictions

```
{
 "M1": {
  "building_backward_share": 0.0013,
  "below": 0.02,
  "held": true
 },
 "M2": {
  "returned_share": 0.3725,
  "floor": 0.25,
  "held": true
 },
 "M3": {
  "held_online_share": 0.528,
  "backward_online_share": 0.053,
  "gap": 0.475,
  "floor": 0.2,
  "held": true
 },
 "M4": {
  "through_approved_share": 0.1746,
  "below": 0.5,
  "held": true
 }
}
```
