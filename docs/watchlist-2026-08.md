# EIA-860M watchlist: report 2026-08

watchlist 0.1.0 on stagemoves 0.1.0 and eia860m-slip 0.3.1; data core_eia860m__changelog_generators.parquet (latest report 2026-08). MV2 of Munim, Inc. (made with AI agents). Code Apache-2.0; tables CC BY 4.0.

Every planned generator whose stage band, status or planned operating month changed from report 2026-07 to report 2026-08 (PUDL report months: the month the data describes). Bands: early (P, L), approved (T), building (U, V, TS). Each change is set beside the 36 report pairs 2023-07 to 2026-07. A change can be a correction of an earlier report, not an event; statuses are self-reported.

## Changes in this report, beside the earlier report pairs

| change | n | mw | median_n | max_n | median_mw | max_mw | pairs |
|---|---|---|---|---|---|---|---|
| forward | 22 | 2118.4 | 27.5 | 80 | 2521.9 | 9924.2 | 36 |
| backward | 0 | 0 | 1.000 | 12 | 35.0 | 2107.9 | 36 |
| to_operating | 50 | 3084.1 | 56.5 | 177 | 3898.2 | 9551.8 | 36 |
| exit_other | 0 | 0 | 0.000 | 1 | 0.000 | 400.0 | 36 |
| left | 9 | 1194.5 | 9.000 | 43 | 926.5 | 5409.0 | 36 |
| within_band | 63 | 6373.3 | 52.5 | 93 | 4168.8 | 10743.8 | 36 |
| delayed | 238 | 17371.6 |  |  |  |  | 0 |
| advanced | 8 | 279.5 |  |  |  |  | 0 |
| new | 28 | 1509.4 | 83.0 | 439 | 7124.4 | 38541.9 | 36 |
| into_planned | 0 | 0 | 0.000 | 4 | 0.000 | 500.0 | 36 |

## Largest backward moves

| key | plant | state | group | mw | status_prev | status_now | planned_prev | planned_now | shift_months | backward_before | possible_rekey |
|---|---|---|---|---|---|---|---|---|---|---|---|

## Largest exits (exit_other and left)

| key | plant | state | group | mw | status_prev | status_now | planned_prev | planned_now | shift_months | backward_before | possible_rekey |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 70257/H2SLR | Hawkeye Solar, LLC | IA | solar | 250.0 | L |  | 2028-03 |  |  | 0 |  |
| 66692/HOLLY | Holly Branch Solar, LLC | TX | solar | 230.0 | L |  | 2027-08 |  |  | 0 |  |
| 68198/TRS | Two Rivers Solar | TX | solar | 214.0 | P |  | 2027-08 |  |  | 0 |  |
| 67660/MALAL | Malala | TX | battery | 200.0 | L |  | 2028-04 |  |  | 0 |  |
| 66692/HOLY | Holly Branch Solar, LLC | TX | battery | 100.0 | L |  | 2027-08 |  |  | 0 |  |
| 68811/RIPLE | Ripley Solar | OH | solar | 100.0 | P |  | 2027-12 |  |  | 0 |  |
| 65655/HECHQ | Chiquito Grid, LLC | CA | battery | 80.0 | P |  | 2027-03 |  |  | 1 |  |
| 67223/SUNYF | USNY - Markham Hollow Rd - 001 | NY | solar | 20.0 | P |  | 2027-01 |  |  | 0 |  |
| 65399/U3 | Mill Pond Hydro | NY | other | 0.500 | P |  | 2027-07 |  |  | 0 |  |

## Largest delays (same status, later planned month)

| key | plant | state | group | mw | status_prev | status_now | planned_prev | planned_now | shift_months | backward_before | possible_rekey |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 68982/SGG01 | Singing Grass Wind | CO | wind_onshore | 603.0 | U | U | 2026-08 | 2027-09 | 13 | 0 |  |
| 66914/DAN | Danish Fields Solar, LLC | TX | solar | 600.0 | TS | TS | 2026-08 | 2026-09 | 1 | 0 |  |
| 64209/26SBA | Bellefield 2 Solar & Energy Storage Farm | CA | solar | 500.0 | V | V | 2026-09 | 2026-12 | 3 | 0 |  |
| 64209/26SBB | Bellefield 2 Solar & Energy Storage Farm | CA | battery | 500.0 | V | V | 2026-11 | 2026-12 | 1 | 0 |  |
| 728/8 | Yates | GA | gas_ct | 482.8 | V | V | 2026-12 | 2027-02 | 2 | 0 |  |
| 66621/1A | Orange County Advanced Power Station | TX | gas_cc | 453.0 | TS | TS | 2026-08 | 2026-09 | 1 | 0 |  |
| 66621/1B | Orange County Advanced Power Station | TX | gas_cc | 453.0 | TS | TS | 2026-08 | 2026-09 | 1 | 0 |  |
| 69873/CRW02 | Cheyenne Ridge II | CO | wind_onshore | 438.0 | U | U | 2026-08 | 2027-06 | 10 | 0 |  |
| 68759/IPQ1B | Quantum BESS | TX | battery | 422.4 | TS | TS | 2026-09 | 2026-11 | 2 | 0 |  |
| 68761/IPQ2B | Quantum II BESS | TX | battery | 422.4 | TS | TS | 2026-09 | 2026-11 | 2 | 0 |  |
| 67262/RP1 | Ripley Energy Center | OK | gas_ct | 419.0 | V | V | 2026-12 | 2027-03 | 3 | 0 |  |
| 66912/HS1 | Hill Solar 1 | TX | solar | 405.0 | TS | TS | 2026-08 | 2026-09 | 1 | 0 |  |
| 66621/1C | Orange County Advanced Power Station | TX | gas_cc | 400.0 | TS | TS | 2026-08 | 2026-09 | 1 | 0 |  |
| 68760/IPQ1S | Quantum Solar | TX | solar | 362.8 | TS | TS | 2026-09 | 2026-11 | 2 | 0 |  |
| 68762/IPQ2S | Quantum II Solar | TX | solar | 362.8 | TS | TS | 2026-09 | 2026-11 | 2 | 0 |  |
| 66915/CTW | Cottonwood Bayou Solar | TX | solar | 350.0 | TS | TS | 2026-08 | 2026-09 | 1 | 0 |  |
| 66910/MYR | Myrtle Solar, LLC | TX | solar | 313.0 | TS | TS | 2026-09 | 2026-10 | 1 | 0 |  |
| 66546/MMTHC | Mammoth Central Solar Project | IN | solar | 300.0 | U | U | 2026-08 | 2026-11 | 3 | 0 |  |
| 68847/PV1 | 1000 Mile Solar | TX | solar | 300.0 | TS | TS | 2026-08 | 2026-09 | 1 | 0 |  |
| 63202/701 | TREX US Red Holly | TX | solar | 250.0 | L | L | 2027-02 | 2027-12 | 10 | 0 |  |

## Largest new planned generators

| key | plant | state | group | mw | status_prev | status_now | planned_prev | planned_now | shift_months | backward_before | possible_rekey |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 70407/RSS | Roy Solar | OK | solar | 258.0 |  | U |  | 2027-12 |  | 0 |  |
| 70408/WCB | Willow Creek Energy Storage | OK | battery | 200.0 |  | U |  | 2026-12 |  | 0 |  |
| 70441/PALO2 | Palo Duro Energy Storage II | TX | battery | 165.7 |  | P |  | 2029-05 |  | 0 |  |
| 70450/PV1 | Wheatridge Optimization II | OR | solar | 130.0 |  | U |  | 2027-12 |  | 0 |  |
| 70420/PV1 | Wheatridge Optimization I | OR | solar | 110.0 |  | U |  | 2027-12 |  | 0 |  |
| 70443/MAMM2 | Mammoth Plains Energy Storage II | OK | battery | 101.2 |  | P |  | 2029-05 |  | 0 |  |
| 70405/BA-1 | Winchester Solar I, LLC | AZ | battery | 87.8 |  | V |  | 2027-03 |  | 0 |  |
| 70405/PV-1 | Winchester Solar I, LLC | AZ | solar | 87.8 |  | V |  | 2027-03 |  | 0 |  |
| 70406/BA-2 | Winchester Solar II, LLC | AZ | battery | 87.8 |  | V |  | 2027-05 |  | 0 |  |
| 70406/PV-2 | Winchester Solar II, LLC | AZ | solar | 87.8 |  | V |  | 2027-05 |  | 0 |  |
| 70420/BA1 | Wheatridge Optimization I | OR | battery | 65.0 |  | U |  | 2027-12 |  | 0 |  |
| 70450/BA1 | Wheatridge Optimization II | OR | battery | 60.0 |  | U |  | 2027-12 |  | 0 |  |
| 70409/ENX41 | Hera Solar | VA | solar | 13.3 |  | L |  | 2028-06 |  | 0 |  |
| 70410/ENX42 | Willow Solar | VA | solar | 12.0 |  | L |  | 2027-06 |  | 0 |  |
| 70437/GROTN | Groton Flanders Road Landfill | CT | solar | 5.000 |  | U |  | 2027-07 |  | 0 |  |
| 70440/BRACE | NL IL Braceville | IL | solar | 5.000 |  | TS |  | 2026-10 |  | 0 |  |
| 70446/33699 | Dragon's Breath Solar LLC PV | IL | solar | 5.000 |  | U |  | 2026-09 |  | 0 |  |
| 70442/11224 | KN216 | IL | solar | 4.900 |  | V |  | 2026-11 |  | 0 |  |
| 70444/11131 | Cottonwood - IL | IL | solar | 4.900 |  | V |  | 2026-08 |  | 0 |  |
| 70439/PV1 | SR 415 - NY Avoca I | NY | solar | 3.300 |  | U |  | 2027-06 |  | 0 |  |

## Earlier moves: MW listed as operating within 12 reports

Steps with m from 2023-07 to 2025-08 (their 12 following reports are all in the file), by starting band and move: a recent base rate for the moves above, not a forecast for any one generator.

| band | move | steps | scored_mw | online_mw | online_share |
|---|---|---|---|---|---|
| early | forward | 425 | 40626.4 | 17805.3 | 0.438 |
| early | held | 19661 | 2860551.6 | 39883.7 | 0.014 |
| early | backward | 0 | 0.000 | 0.000 |  |
| early | to_operating | 9 | 25.0 | 25.0 | 1.000 |
| early | exit_other | 2 | 500.0 | 0.000 | 0.000 |
| approved | forward | 329 | 31221.5 | 15498.2 | 0.496 |
| approved | held | 5031 | 634179.0 | 34023.4 | 0.054 |
| approved | backward | 27 | 3352.2 | 0.000 | 0.000 |
| approved | to_operating | 14 | 595.5 | 595.5 | 1.000 |
| approved | exit_other | 0 | 0.000 | 0.000 |  |
| building | forward | 0 | 0.000 | 0.000 |  |
| building | held | 18935 | 1586411.4 | 896042.1 | 0.565 |
| building | backward | 18 | 2489.1 | 80.0 | 0.032 |
| building | to_operating | 1501 | 98626.6 | 98626.6 | 1.000 |
| building | exit_other | 2 | 245.0 | 0.000 | 0.000 |

## Checks

```
{
 "C1": {
  "rows": 418,
  "pass": true
 },
 "C2": {
  "planned_mw": 291407.9,
  "moves_mw": 291407.9,
  "pass": true
 },
 "C3": {
  "ours": {
   "forward": 22,
   "held": 2262,
   "backward": 0,
   "to_operating": 50,
   "exit_other": 0,
   "left": 9
  },
  "stagemoves": {
   "forward": 22,
   "held": 2262,
   "backward": 0,
   "to_operating": 50,
   "exit_other": 0,
   "left": 9
  },
  "pass": true
 },
 "C4": {
  "row_counts": {
   "forward": 22,
   "backward": 0,
   "to_operating": 50,
   "exit_other": 0,
   "left": 9,
   "within_band": 63,
   "delayed": 238,
   "advanced": 8,
   "new": 28,
   "into_planned": 0
  },
  "pass": true
 },
 "all_pass": true
}
```
