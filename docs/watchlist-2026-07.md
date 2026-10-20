# EIA-860M watchlist: report 2026-07

watchlist 0.1.0 on stagemoves 0.1.0 and eia860m-slip 0.3.1; data core_eia860m__changelog_generators.parquet (latest report 2026-08). MV2 of Munim, Inc. (made with AI agents). Code Apache-2.0; tables CC BY 4.0.

Every planned generator whose stage band, status or planned operating month changed from report 2026-06 to report 2026-07 (PUDL report months: the month the data describes). Bands: early (P, L), approved (T), building (U, V, TS). Each change is set beside the 36 report pairs 2023-06 to 2026-06. A change can be a correction of an earlier report, not an event; statuses are self-reported.

## Changes in this report, beside the earlier report pairs

| change | n | mw | median_n | max_n | median_mw | max_mw | pairs |
|---|---|---|---|---|---|---|---|
| forward | 17 | 4613.9 | 28.0 | 80 | 2521.9 | 9924.2 | 36 |
| backward | 1 | 5.000 | 1.000 | 12 | 35.0 | 2107.9 | 36 |
| to_operating | 58 | 3273.5 | 56.5 | 177 | 3936.2 | 9551.8 | 36 |
| exit_other | 0 | 0 | 0.000 | 1 | 0.000 | 400.0 | 36 |
| left | 8 | 707.3 | 9.000 | 43 | 926.5 | 5409.0 | 36 |
| within_band | 81 | 9472.1 | 50.5 | 93 | 4072.3 | 10743.8 | 36 |
| delayed | 264 | 27075.9 |  |  |  |  | 0 |
| advanced | 5 | 707.4 |  |  |  |  | 0 |
| new | 103 | 8140.2 | 83.0 | 439 | 6881.7 | 38541.9 | 36 |
| into_planned | 0 | 0 | 0.000 | 4 | 0.000 | 500.0 | 36 |

## Largest backward moves

| key | plant | state | group | mw | status_prev | status_now | planned_prev | planned_now | shift_months | backward_before | possible_rekey |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 68520/MNDA4 | Madena 4 | CA | battery | 5.000 | U | L | 2026-11 | 2027-04 | 5 | 0 |  |

## Largest exits (exit_other and left)

| key | plant | state | group | mw | status_prev | status_now | planned_prev | planned_now | shift_months | backward_before | possible_rekey |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 63798/ATLB1 | Atlas | AZ | battery | 300.0 | V |  | 2026-07 |  |  | 0 |  |
| 66744/BRNMN | Brenneman Solar Project | GA | solar | 150.0 | T |  | 2026-10 |  |  | 0 |  |
| 7526/5 | Solano Wind | CA | wind_onshore | 108.0 | P |  | 2029-09 |  |  | 0 |  |
| 67934/VERNP | Vernon Solar and Storage | TX | solar | 104.0 | P |  | 2028-02 |  |  | 0 |  |
| 67934/VERNB | Vernon Solar and Storage | TX | battery | 38.0 | P |  | 2028-02 |  |  | 0 |  |
| 65136/VCPS1 | Royalston Solar One | MA | battery | 2.500 | P |  | 2027-06 |  |  | 0 |  |
| 61592/WT4 | Cody Road Wind Farm | NY | wind_onshore | 2.400 | U |  | 2027-07 |  |  | 0 |  |
| 61592/WT5 | Cody Road Wind Farm | NY | wind_onshore | 2.400 | U |  | 2027-07 |  |  | 0 |  |

## Largest delays (same status, later planned month)

| key | plant | state | group | mw | status_prev | status_now | planned_prev | planned_now | shift_months | backward_before | possible_rekey |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 58987/II-A | Chokecherry and Sierra Madre Wind | WY | wind_onshore | 1303.2 | U | U | 2030-12 | 2032-12 | 24 | 0 |  |
| 68367/PEHA1 | Pepper Hammock Solar and Storage | GA | solar | 1200.0 | L | L | 2027-08 | 2029-09 | 25 | 0 |  |
| 67435/SRWND | Sunrise Wind | NY | wind_offshore | 924.0 | U | U | 2027-07 | 2027-10 | 3 | 0 |  |
| 68367/PEHA | Pepper Hammock Solar and Storage | GA | solar | 900.0 | L | L | 2028-10 | 2029-09 | 11 | 0 |  |
| 58987/I-B | Chokecherry and Sierra Madre Wind | WY | wind_onshore | 849.6 | U | U | 2029-12 | 2031-12 | 24 | 0 |  |
| 58987/I-A | Chokecherry and Sierra Madre Wind | WY | wind_onshore | 844.2 | U | U | 2029-12 | 2031-12 | 24 | 0 |  |
| 66914/DAN | Danish Fields Solar, LLC | TX | solar | 600.0 | TS | TS | 2026-07 | 2026-08 | 1 | 0 |  |
| 58987/II-B | Chokecherry and Sierra Madre Wind | WY | wind_onshore | 553.5 | U | U | 2031-12 | 2033-12 | 24 | 0 |  |
| 65028/ROSES | Roseland Solar Project, LLC | TX | solar | 500.0 | TS | TS | 2026-07 | 2026-09 | 2 | 0 |  |
| 68351/CLAPV | Clairemont Solar | TX | solar | 500.0 | P | P | 2027-07 | 2029-07 | 24 | 0 |  |
| 68353/LSBS1 | La Salle ESS | TX | battery | 500.0 | P | P | 2027-07 | 2029-07 | 24 | 0 |  |
| 68354/LSPV1 | La Salle Solar | TX | solar | 500.0 | P | P | 2027-07 | 2028-09 | 14 | 0 |  |
| 69060/SNFA | Snowflake A Solar and BESS | AZ | solar | 475.0 | L | L | 2027-06 | 2027-08 | 2 | 0 |  |
| 69060/SNFBA | Snowflake A Solar and BESS | AZ | battery | 475.0 | L | L | 2027-06 | 2027-08 | 2 | 0 |  |
| 3399/CTG1 | Cumberland (TN) | TN | gas_cc | 454.8 | U | U | 2026-12 | 2034-12 | 96 | 0 |  |
| 66871/SOLAR | GulfStar Power, LLC | TX | solar | 451.6 | TS | TS | 2026-07 | 2026-10 | 3 | 0 |  |
| 68369/STMO | Starfire Mountain Solar | KY | solar | 410.0 | L | L | 2027-09 | 2029-09 | 24 | 0 |  |
| 66912/HS1 | Hill Solar 1 | TX | solar | 405.0 | TS | TS | 2026-07 | 2026-08 | 1 | 0 |  |
| 68367/PEHA2 | Pepper Hammock Solar and Storage | GA | battery | 400.0 | L | L | 2028-12 | 2029-09 | 9 | 0 |  |
| 66915/CTW | Cottonwood Bayou Solar | TX | solar | 350.0 | TS | TS | 2026-07 | 2026-08 | 1 | 0 |  |

## Largest new planned generators

| key | plant | state | group | mw | status_prev | status_now | planned_prev | planned_now | shift_months | backward_before | possible_rekey |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 70359/SYRVS | Sycamore Riverside Energy, LLC | IN | gas_ct | 964.0 |  | P |  | 2029-03 |  | 0 |  |
| 70397/SRSP1 | Steel River Solar Phase 1 | AR | solar | 500.0 |  | U |  | 2028-08 |  | 0 |  |
| 70398/SRSP2 | Steel River Solar Phase 2 | AR | solar | 500.0 |  | U |  | 2029-07 |  | 0 |  |
| 70399/SRSP3 | Steel River Solar Phase 3 | AR | solar | 500.0 |  | U |  | 2030-07 |  | 0 |  |
| 70331/MRASL | Mirasol Energy Center, LLC. | CO | solar | 400.0 |  | T |  | 2028-12 |  | 0 |  |
| 70330/BRSPV | Bighorn Ridge Solar | TX | solar | 300.0 |  | T |  | 2027-12 |  | 0 |  |
| 70367/OBAES | O'Bannion Energy Storage | TX | battery | 300.0 |  | T |  | 2028-12 |  | 0 |  |
| 70419/RSBA | Royal Slope | WA | battery | 260.0 |  | T |  | 2027-10 |  | 0 |  |
| 70419/RSPV | Royal Slope | WA | solar | 260.0 |  | T |  | 2027-10 |  | 0 |  |
| 70299/814 | Pioneer Creek Wind, LLC | KS | wind_onshore | 252.0 |  | V |  | 2027-03 |  | 0 |  |
| 70397/SRSB1 | Steel River Solar Phase 1 | AR | battery | 250.0 |  | U |  | 2028-08 |  | 0 |  |
| 70398/SRSB2 | Steel River Solar Phase 2 | AR | battery | 250.0 |  | U |  | 2029-07 |  | 0 |  |
| 70399/SRSB3 | Steel River Solar Phase 3 | AR | battery | 250.0 |  | U |  | 2030-07 |  | 0 |  |
| 70300/USADC | Adams Creek Solar Project | TX | solar | 240.0 |  | T |  | 2027-06 |  | 0 |  |
| 70237/MULE1 | Mule Shoe Energy Storage | TX | battery | 207.0 |  | T |  | 2028-08 |  | 0 |  |
| 70297/BWTS | Blackwater Solar Center - NM | NM | solar | 200.0 |  | T |  | 2027-12 |  | 0 |  |
| 70341/TW200 | Thunder Wolf II, LLC | CO | solar | 200.0 |  | T |  | 2027-12 |  | 0 |  |
| 70344/RSPV | Rush Springs Solar | OK | solar | 200.0 |  | V |  | 2026-10 |  | 0 |  |
| 70400/BEE1A | Bee Branch IA | TX | battery | 200.0 |  | P |  | 2027-06 |  | 0 |  |
| 70236/SLRN1 | Sierra Luna Energy Storage | AZ | battery | 150.0 |  | P |  | 2030-12 |  | 0 |  |

## Earlier moves: MW listed as operating within 12 reports

Steps with m from 2023-06 to 2025-07 (their 12 following reports are all in the file), by starting band and move: a recent base rate for the moves above, not a forecast for any one generator.

| band | move | steps | scored_mw | online_mw | online_share |
|---|---|---|---|---|---|
| early | forward | 425 | 39944.1 | 17768.9 | 0.445 |
| early | held | 19390 | 2789650.4 | 39393.9 | 0.014 |
| early | backward | 0 | 0.000 | 0.000 |  |
| early | to_operating | 9 | 25.0 | 25.0 | 1.000 |
| early | exit_other | 2 | 500.0 | 0.000 | 0.000 |
| approved | forward | 345 | 32042.9 | 15791.1 | 0.493 |
| approved | held | 4970 | 633565.5 | 35322.4 | 0.056 |
| approved | backward | 26 | 3338.2 | 0.000 | 0.000 |
| approved | to_operating | 15 | 610.7 | 610.7 | 1.000 |
| approved | exit_other | 0 | 0.000 | 0.000 |  |
| building | forward | 0 | 0.000 | 0.000 |  |
| building | held | 18883 | 1562611.0 | 884239.6 | 0.566 |
| building | backward | 17 | 2409.1 | 80.0 | 0.033 |
| building | to_operating | 1523 | 100663.7 | 100663.7 | 1.000 |
| building | exit_other | 2 | 245.0 | 0.000 | 0.000 |

## Checks

```
{
 "C1": {
  "rows": 537,
  "pass": true
 },
 "C2": {
  "planned_mw": 288056.7,
  "moves_mw": 288056.7,
  "pass": true
 },
 "C3": {
  "ours": {
   "forward": 17,
   "held": 2222,
   "backward": 1,
   "to_operating": 58,
   "exit_other": 0,
   "left": 8
  },
  "stagemoves": {
   "forward": 17,
   "held": 2222,
   "backward": 1,
   "to_operating": 58,
   "exit_other": 0,
   "left": 8
  },
  "pass": true
 },
 "C4": {
  "row_counts": {
   "forward": 17,
   "backward": 1,
   "to_operating": 58,
   "exit_other": 0,
   "left": 8,
   "within_band": 81,
   "delayed": 264,
   "advanced": 5,
   "new": 103,
   "into_planned": 0
  },
  "pass": true
 },
 "all_pass": true
}
```
