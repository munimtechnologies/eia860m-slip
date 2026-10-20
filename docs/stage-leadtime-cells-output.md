# Which generators make up the stage-by-lead cells

cellmakeup 0.1.0 on leadtime 0.1.0 and eia860m-slip 0.3.1; data core_eia860m__changelog_generators.parquet (latest report 2026-08), report months 2016-01 to 2023-06. MV2 of Munim, Inc. (made with AI agents). Description, not a scored check. Code Apache-2.0; tables CC BY 4.0.

MW is summed over a cell's rows (one row per generator and report month), as in docs/stage-leadtime.md, so a generator listed in many reports weighs more.

## K1: the cells match the published ones

```
{
 "cells": {
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
  },
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
  }
 },
 "pass": true
}
```

## U, 13-24 months

506 generators at 315 plants, 636740.1 MW over rows. The ten largest generators hold 0.2229 of it, the ten largest plants 0.308, the largest plant 0.0553.

### By technology group

| group | rows | generators | mw | mw_share | on_time_share |
|---|---|---|---|---|---|
| gas_cc | 993 | 127 | 293722.4 | 0.4613 | 0.3651 |
| wind_onshore | 1021 | 61 | 144378.9 | 0.2267 | 0.1217 |
| solar | 840 | 160 | 109822.1 | 0.1725 | 0.2358 |
| nuclear | 35 | 3 | 38500.0 | 0.0605 | 0.0 |
| gas_ct | 214 | 33 | 25817.4 | 0.0405 | 0.0464 |
| battery | 197 | 33 | 14865.6 | 0.0233 | 0.1802 |
| other | 583 | 38 | 4326.3 | 0.0068 | 0.0 |
| gas_ice | 197 | 38 | 3916.3 | 0.0062 | 0.4749 |
| coal | 15 | 2 | 1164.0 | 0.0018 | 0.0 |
| gas_other | 35 | 8 | 204.9 | 0.0003 | 0.0 |
| oil | 8 | 3 | 22.2 | 0.0 | 0.0 |

### Ten largest generators

| key | plant | state | group | capacity_mw | rows | mw | mw_share | planned_first | planned_last | online | on_time_share | not_online_share |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 59246/GOOD1 | Goodnight | TX | wind_onshore | 500.0 | 73 | 35000.0 | 0.055 | 2017-10 | 2023-06 | 2024-04 | 0.0 | 0.9 |
| 649/3 | Vogtle | GA | nuclear | 1100.0 | 24 | 26400.0 | 0.0415 | 2019-06 | 2021-11 | 2023-07 | 0.0 | 1.0 |
| 60356/SFECC | South Field Energy | OH | gas_cc | 1105.0 | 12 | 13260.0 | 0.0208 | 2021-01 | 2021-01 |  | 0.0 | 1.0 |
| 60589/GEN1 | CPV Fairview Energy Center | PA | gas_cc | 1100.0 | 12 | 13200.0 | 0.0207 | 2020-03 | 2020-03 | 2019-12 | 1.0 | 0.0 |
| 58406/1 | Chilocco Wind Farm | OK | wind_onshore | 200.0 | 65 | 11333.2 | 0.0178 | 2018-12 | 2024-12 |  | 0.0 | 1.0 |
| 62954/GEN1 | Alle-Catt Wind Energy LLC | NY | wind_onshore | 340.0 | 26 | 8840.0 | 0.0139 | 2021-12 | 2025-05 |  | 0.0 | 1.0 |
| 649/4 | Vogtle | GA | nuclear | 1100.0 | 8 | 8800.0 | 0.0138 | 2022-11 | 2022-11 | 2024-04 | 0.0 | 1.0 |
| 59971/ESTR1 | Easter | TX | wind_onshore | 300.0 | 32 | 8700.0 | 0.0137 | 2017-10 | 2020-12 |  | 0.0 | 1.0 |
| 63352/ARBE1 | Gemini Solar Hybrid | NV | solar | 690.0 | 12 | 8280.0 | 0.013 | 2023-11 | 2023-11 | 2024-03 | 0.0 | 0.0 |
| 62947/GEN1 | Canisteo Wind Farm | NY | wind_onshore | 290.7 | 28 | 8139.6 | 0.0128 | 2021-06 | 2023-04 |  | 0.0 | 1.0 |

### Ten largest plants

| plant_id | plant | state | generators | rows | mw | mw_share | on_time_share |
|---|---|---|---|---|---|---|---|
| 649 | Vogtle | GA | 2 | 32 | 35200.0 | 0.0553 | 0.0 |
| 59246 | Goodnight | TX | 1 | 73 | 35000.0 | 0.055 | 0.0 |
| 60138 | Citrus County Combined Cycle Plant | FL | 6 | 72 | 23647.2 | 0.0371 | 0.0 |
| 60357 | Lackawanna Energy Center | PA | 3 | 34 | 18870.0 | 0.0296 | 1.0 |
| 63931 | CPV Three Rivers Energy Center | IL | 2 | 24 | 15600.6 | 0.0245 | 0.0 |
| 62192 | Blue Water Energy Center | MI | 3 | 36 | 15208.8 | 0.0239 | 0.0 |
| 55460 | Indeck Niles Energy Center | MI | 3 | 36 | 13311.6 | 0.0209 | 0.0 |
| 60356 | South Field Energy | OH | 1 | 12 | 13260.0 | 0.0208 | 0.0 |
| 60589 | CPV Fairview Energy Center | PA | 1 | 12 | 13200.0 | 0.0207 | 1.0 |
| 63352 | Gemini Solar Hybrid | NV | 2 | 24 | 12840.0 | 0.0202 | 0.0 |

## V, 13-24 months

79 generators at 51 plants, 57078.8 MW over rows. The ten largest generators hold 0.6543 of it, the ten largest plants 0.7636, the largest plant 0.3123.

### By technology group

| group | rows | generators | mw | mw_share | on_time_share |
|---|---|---|---|---|---|
| gas_cc | 85 | 28 | 17878.0 | 0.3132 | 0.198 |
| nuclear | 16 | 2 | 17824.0 | 0.3123 | 0.0 |
| solar | 139 | 32 | 13927.8 | 0.244 | 0.2111 |
| gas_ct | 33 | 8 | 6042.0 | 0.1059 | 0.1414 |
| wind_onshore | 6 | 2 | 776.0 | 0.0136 | 0.7474 |
| other | 26 | 3 | 544.4 | 0.0095 | 0.0 |
| gas_other | 2 | 1 | 51.0 | 0.0009 | 0.0 |
| battery | 8 | 3 | 35.6 | 0.0006 | 0.3371 |

### Ten largest generators

| key | plant | state | group | capacity_mw | rows | mw | mw_share | planned_first | planned_last | online | on_time_share | not_online_share |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 649/4 | Vogtle | GA | nuclear | 1114.0 | 15 | 16710.0 | 0.2928 | 2022-11 | 2024-03 | 2024-04 | 0.0 | 0.2667 |
| 7277/17 | Lincoln Combustion | NC | gas_ct | 536.4 | 9 | 4827.6 | 0.0846 | 2024-10 | 2024-10 | 2024-12 | 0.0 | 0.0 |
| 55486/ST1 | Washington Parish Energy Center | LA | gas_cc | 255.0 | 12 | 3060.0 | 0.0536 | 2019-06 | 2019-06 |  | 0.0 | 1.0 |
| 66157/GEN1 | Red Tailed Hawk Solar LLC | TX | solar | 350.0 | 7 | 2450.0 | 0.0429 | 2024-07 | 2024-07 | 2024-09 | 0.0 | 0.0 |
| 55486/CTG1 | Washington Parish Energy Center | LA | gas_cc | 200.0 | 12 | 2400.0 | 0.042 | 2019-06 | 2019-06 |  | 0.0 | 1.0 |
| 55486/CTG2 | Washington Parish Energy Center | LA | gas_cc | 200.0 | 12 | 2400.0 | 0.042 | 2019-06 | 2019-06 |  | 0.0 | 1.0 |
| 65034/CSBS1 | Bernard Creek Solar | TX | solar | 230.0 | 7 | 1610.0 | 0.0282 | 2024-06 | 2024-06 | 2023-12 | 1.0 | 0.0 |
| 57960/1 | Rugged Solar LLC | CA | solar | 80.0 | 18 | 1440.0 | 0.0252 | 2020-11 | 2023-12 |  | 0.0 | 1.0 |
| 63840/1111 | Sparta Solar | TX | solar | 250.0 | 5 | 1250.0 | 0.0219 | 2023-04 | 2024-04 | 2024-04 | 0.2 | 0.0 |
| 63985/FBS | Fort Bend Solar LLC | TX | solar | 240.0 | 5 | 1200.0 | 0.021 | 2023-06 | 2023-09 | 2023-10 | 0.0 | 0.0 |

### Ten largest plants

| plant_id | plant | state | generators | rows | mw | mw_share | on_time_share |
|---|---|---|---|---|---|---|---|
| 649 | Vogtle | GA | 2 | 16 | 17824.0 | 0.3123 | 0.0 |
| 55486 | Washington Parish Energy Center | LA | 3 | 36 | 7860.0 | 0.1377 | 0.0 |
| 7277 | Lincoln Combustion | NC | 1 | 9 | 4827.6 | 0.0846 | 0.0 |
| 57185 | Cricket Valley Energy | NY | 6 | 9 | 2914.1 | 0.0511 | 0.0 |
| 66157 | Red Tailed Hawk Solar LLC | TX | 1 | 7 | 2450.0 | 0.0429 | 0.0 |
| 59764 | Oregon Clean Energy Center | OH | 3 | 12 | 2120.0 | 0.0371 | 0.0 |
| 65034 | Bernard Creek Solar | TX | 1 | 7 | 1610.0 | 0.0282 | 1.0 |
| 57960 | Rugged Solar LLC | CA | 1 | 18 | 1440.0 | 0.0252 | 0.0 |
| 991 | Eagle Valley (IN) | IN | 3 | 6 | 1288.0 | 0.0226 | 1.0 |
| 63840 | Sparta Solar | TX | 1 | 5 | 1250.0 | 0.0219 | 0.2 |

## U, 00-03 months

1774 generators at 1434 plants, 190762.7 MW over rows. The ten largest generators hold 0.1557 of it, the ten largest plants 0.2064, the largest plant 0.0575.

### By technology group

| group | rows | generators | mw | mw_share | on_time_share |
|---|---|---|---|---|---|
| wind_onshore | 643 | 220 | 70961.3 | 0.372 | 0.3428 |
| solar | 3153 | 1170 | 64970.8 | 0.3406 | 0.2641 |
| gas_cc | 78 | 25 | 30745.9 | 0.1612 | 0.3987 |
| battery | 724 | 188 | 17758.3 | 0.0931 | 0.1485 |
| gas_ct | 83 | 27 | 3800.1 | 0.0199 | 0.1123 |
| gas_ice | 175 | 73 | 1581.5 | 0.0083 | 0.4453 |
| other | 139 | 27 | 630.2 | 0.0033 | 0.0249 |
| gas_other | 58 | 19 | 191.3 | 0.001 | 0.0261 |
| oil | 78 | 26 | 123.3 | 0.0006 | 0.1119 |

### Ten largest generators

| key | plant | state | group | capacity_mw | rows | mw | mw_share | planned_first | planned_last | online | on_time_share | not_online_share |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 62949/GPS1 | Guernsey Power Station | OH | gas_cc | 685.0 | 6 | 4110.0 | 0.0215 | 2022-11 | 2023-02 | 2023-02 | 0.3333 | 0.0 |
| 65028/ROSES | Roseland Solar Project, LLC | TX | solar | 500.0 | 8 | 4000.0 | 0.021 | 2021-12 | 2022-08 | 2023-07 | 0.0 | 0.625 |
| 62949/GPS2 | Guernsey Power Station | OH | gas_cc | 685.0 | 5 | 3425.0 | 0.018 | 2022-11 | 2023-02 | 2023-02 | 0.4 | 0.0 |
| 62949/GPS3 | Guernsey Power Station | OH | gas_cc | 685.0 | 5 | 3425.0 | 0.018 | 2023-02 | 2023-04 | 2023-04 | 0.2 | 0.0 |
| 59906/GEN1 | Moxie Freedom Generation Plant | PA | gas_cc | 529.0 | 6 | 3174.0 | 0.0166 | 2018-05 | 2018-08 | 2018-08 | 0.1667 | 0.0 |
| 59906/GEN2 | Moxie Freedom Generation Plant | PA | gas_cc | 529.0 | 6 | 3174.0 | 0.0166 | 2018-05 | 2018-08 | 2018-09 | 0.0 | 0.0 |
| 62564/ELKHO | Elkhorn Battery Energy Storage System | CA | battery | 182.5 | 12 | 2190.0 | 0.0115 | 2021-07 | 2022-04 | 2022-04 | 0.0833 | 0.0 |
| 60270/WT1 | Blue Cloud Wind Energy LLC | TX | wind_onshore | 350.0 | 6 | 2100.0 | 0.011 | 2018-08 | 2018-12 | 2018-12 | 0.5 | 0.0 |
| 55524/STG2 | York Energy Center | PA | gas_cc | 419.6 | 5 | 2098.0 | 0.011 | 2018-12 | 2019-03 | 2019-03 | 0.2 | 0.0 |
| 63479/GEN1 | Traverse Wind Project, LLC | OK | wind_onshore | 999.0 | 2 | 1998.0 | 0.0105 | 2020-12 | 2022-01 | 2022-04 | 0.0 | 0.5 |

### Ten largest plants

| plant_id | plant | state | generators | rows | mw | mw_share | on_time_share |
|---|---|---|---|---|---|---|---|
| 62949 | Guernsey Power Station | OH | 3 | 16 | 10960.0 | 0.0575 | 0.3125 |
| 59906 | Moxie Freedom Generation Plant | PA | 2 | 12 | 6348.0 | 0.0333 | 0.0833 |
| 55524 | York Energy Center | PA | 3 | 15 | 4447.0 | 0.0233 | 0.2 |
| 65028 | Roseland Solar Project, LLC | TX | 2 | 9 | 4059.1 | 0.0213 | 0.0 |
| 1378 | Paradise | KY | 4 | 12 | 3480.0 | 0.0182 | 1.0 |
| 62564 | Elkhorn Battery Energy Storage System | CA | 1 | 12 | 2190.0 | 0.0115 | 0.0833 |
| 60270 | Blue Cloud Wind Energy LLC | TX | 1 | 6 | 2100.0 | 0.011 | 0.5 |
| 63502 | Oso Grande Wind Farm | NM | 2 | 16 | 1998.4 | 0.0105 | 0.0 |
| 63479 | Traverse Wind Project, LLC | OK | 1 | 2 | 1998.0 | 0.0105 | 0.0 |
| 63574 | Atchison County Wind | MO | 1 | 6 | 1791.6 | 0.0094 | 0.1667 |

## V, 00-03 months

3421 generators at 2662 plants, 627147.3 MW over rows. The ten largest generators hold 0.0648 of it, the ten largest plants 0.107, the largest plant 0.0137.

### By technology group

| group | rows | generators | mw | mw_share | on_time_share |
|---|---|---|---|---|---|
| wind_onshore | 1221 | 369 | 199945.7 | 0.3188 | 0.4663 |
| solar | 6522 | 2060 | 185266.3 | 0.2954 | 0.4272 |
| gas_cc | 557 | 144 | 136276.2 | 0.2173 | 0.3981 |
| battery | 1272 | 272 | 46395.3 | 0.074 | 0.2504 |
| gas_ct | 551 | 126 | 43503.7 | 0.0694 | 0.3087 |
| other | 715 | 151 | 6179.8 | 0.0099 | 0.2555 |
| nuclear | 5 | 2 | 4611.9 | 0.0074 | 0.2754 |
| gas_ice | 560 | 198 | 3829.1 | 0.0061 | 0.4215 |
| oil | 271 | 77 | 596.7 | 0.001 | 0.2966 |
| gas_other | 119 | 23 | 482.6 | 0.0008 | 0.0719 |
| wind_offshore | 2 | 1 | 60.0 | 0.0001 | 0.0 |

### Ten largest generators

| key | plant | state | group | capacity_mw | rows | mw | mw_share | planned_first | planned_last | online | on_time_share | not_online_share |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 63209/AVTOR | Aviator Wind | TX | wind_onshore | 525.0 | 13 | 6825.0 | 0.0109 | 2020-08 | 2021-06 | 2021-06 | 0.0769 | 0.0 |
| 65028/ROSES | Roseland Solar Project, LLC | TX | solar | 500.0 | 9 | 4500.0 | 0.0072 | 2022-11 | 2023-06 | 2023-07 | 0.0 | 0.0 |
| 64672/BLUEJ | Blue Jay Solar I, LLC | TX | solar | 210.0 | 21 | 4410.0 | 0.007 | 2021-12 | 2023-07 | 2023-06 | 0.1429 | 0.2381 |
| 64672/BLUJS | Blue Jay Solar I, LLC | TX | battery | 210.0 | 20 | 4200.0 | 0.0067 | 2021-12 | 2023-06 | 2023-06 | 0.1 | 0.25 |
| 62416/WT1 | Cranell Wind Farm LLC | TX | wind_onshore | 220.0 | 18 | 3960.0 | 0.0063 | 2020-06 | 2022-03 | 2022-01 | 0.0556 | 0.3889 |
| 62853/MVRCK | Maverick Creek Wind | TX | wind_onshore | 491.6 | 8 | 3932.8 | 0.0063 | 2021-10 | 2022-03 | 2022-03 | 0.125 | 0.0 |
| 62562/HILO | High Lonesome Wind Power, LLC Hybrid | TX | wind_onshore | 449.5 | 8 | 3596.0 | 0.0057 | 2019-12 | 2020-06 | 2021-07 | 0.0 | 1.0 |
| 649/3 | Vogtle | GA | nuclear | 1114.0 | 3 | 3342.0 | 0.0053 | 2023-03 | 2023-06 | 2023-07 | 0.0 | 0.0 |
| 63479/GEN1 | Traverse Wind Project, LLC | OK | wind_onshore | 999.0 | 3 | 2997.0 | 0.0048 | 2022-04 | 2022-04 | 2022-04 | 1.0 | 0.0 |
| 3264/ST10 | W S Lee | SC | gas_cc | 362.0 | 8 | 2896.0 | 0.0046 | 2017-11 | 2018-04 | 2018-04 | 0.125 | 0.0 |

### Ten largest plants

| plant_id | plant | state | generators | rows | mw | mw_share | on_time_share |
|---|---|---|---|---|---|---|---|
| 64672 | Blue Jay Solar I, LLC | TX | 2 | 41 | 8610.0 | 0.0137 | 0.122 |
| 60356 | South Field Energy | OH | 4 | 24 | 7262.4 | 0.0116 | 0.0833 |
| 55460 | Indeck Niles Energy Center | MI | 3 | 18 | 7046.4 | 0.0112 | 0.1667 |
| 63209 | Aviator Wind | TX | 1 | 13 | 6825.0 | 0.0109 | 0.0769 |
| 60903 | Salem Harbor Power Development LP | MA | 4 | 34 | 6784.7 | 0.0108 | 0.0 |
| 3264 | W S Lee | SC | 3 | 24 | 6784.0 | 0.0108 | 0.125 |
| 60376 | Middletown- Ohio | OH | 3 | 21 | 6734.0 | 0.0107 | 0.1429 |
| 60368 | Hummel Station LLC | PA | 4 | 21 | 6432.0 | 0.0103 | 0.0 |
| 60357 | Lackawanna Energy Center | PA | 3 | 10 | 5550.0 | 0.0088 | 0.5 |
| 65028 | Roseland Solar Project, LLC | TX | 2 | 19 | 5091.0 | 0.0081 | 0.0116 |
