# EIA-860M watchlist: report 2026-09

watchlist 0.1.0 on stagemoves 0.1.0 and eia860m-slip 0.3.1; data PUDL changelog through 2026-08 + EIA workbook september_generator2026.xlsx (latest report 2026-09). MV2 of Munim, Inc. (made with AI agents). Code Apache-2.0; tables CC BY 4.0.

Every planned generator whose stage band, status or planned operating month changed from report 2026-08 to report 2026-09 (PUDL report months: the month the data describes). Bands: early (P, L), approved (T), building (U, V, TS). Each change is set beside the 36 report pairs 2023-08 to 2026-08. A change can be a correction of an earlier report, not an event; statuses are self-reported.

## Changes in this report, beside the earlier report pairs

| change | n | mw | median_n | max_n | median_mw | max_mw | pairs |
|---|---|---|---|---|---|---|---|
| forward | 22 | 1466.6 | 27.0 | 80 | 2426.1 | 9924.2 | 36 |
| backward | 1 | 7.000 | 1.000 | 12 | 15.0 | 2107.9 | 36 |
| to_operating | 70 | 5383.4 | 56.5 | 177 | 3898.2 | 9551.8 | 36 |
| exit_other | 0 | 0 | 0.000 | 1 | 0.000 | 400.0 | 36 |
| left | 3 | 165.9 | 9.000 | 43 | 951.6 | 5409.0 | 36 |
| within_band | 62 | 5307.4 | 54.5 | 93 | 4216.6 | 10743.8 | 36 |
| delayed | 279 | 20528.6 |  |  |  |  | 0 |
| advanced | 12 | 743.3 |  |  |  |  | 0 |
| new | 119 | 6944.4 | 80.0 | 439 | 6881.7 | 38541.9 | 36 |
| into_planned | 0 | 0 | 0.000 | 4 | 0.000 | 500.0 | 36 |

## Largest backward moves

| key | plant | state | group | mw | status_prev | status_now | planned_prev | planned_now | shift_months | backward_before | possible_rekey |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 69466/GRESP | City of Detroit Greenfield | MI | solar | 7.000 | U | T | 2027-09 | 2027-09 | 0 | 0 |  |

## Largest exits (exit_other and left)

| key | plant | state | group | mw | status_prev | status_now | planned_prev | planned_now | shift_months | backward_before | possible_rekey |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 67788/GRS10 | Payne Battlecreek Solar | TX | solar | 85.0 | L |  | 2027-08 |  |  | 0 |  |
| 67674/LUPE3 | Lupinus Storage 3 | TX | battery | 50.9 | U |  | 2027-06 |  |  | 0 |  |
| 69144/PV1 | Baxter Creek Solar | NC | solar | 30.0 | V |  | 2026-09 |  |  | 0 |  |

## Largest delays (same status, later planned month)

| key | plant | state | group | mw | status_prev | status_now | planned_prev | planned_now | shift_months | backward_before | possible_rekey |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 66914/DAN | Danish Fields Solar, LLC | TX | solar | 600.0 | TS | TS | 2026-09 | 2026-10 | 1 | 0 |  |
| 64163/11111 | Hecate Energy Cider Solar LLC | NY | solar | 557.0 | U | U | 2026-10 | 2026-12 | 2 | 0 |  |
| 69684/70125 | Maricopa Solar | AZ | battery | 550.0 | U | U | 2026-09 | 2026-12 | 3 | 0 |  |
| 65028/ROSES | Roseland Solar Project, LLC | TX | solar | 500.0 | TS | TS | 2026-09 | 2026-10 | 1 | 0 |  |
| 66621/1A | Orange County Advanced Power Station | TX | gas_cc | 453.0 | TS | TS | 2026-09 | 2026-10 | 1 | 0 |  |
| 66621/1B | Orange County Advanced Power Station | TX | gas_cc | 453.0 | TS | TS | 2026-09 | 2026-10 | 1 | 0 |  |
| 69873/CRW02 | Cheyenne Ridge II | CO | wind_onshore | 438.0 | U | U | 2027-06 | 2027-07 | 1 | 0 |  |
| 68761/IPQ2B | Quantum II BESS | TX | battery | 422.4 | TS | TS | 2026-11 | 2026-12 | 1 | 0 |  |
| 67262/RP1 | Ripley Energy Center | OK | gas_ct | 419.0 | V | V | 2027-03 | 2027-04 | 1 | 0 |  |
| 67263/TN1 | Turney Energy Center | MO | gas_ct | 419.0 | U | U | 2027-07 | 2027-09 | 2 | 0 |  |
| 66912/HS1 | Hill Solar 1 | TX | solar | 405.0 | TS | TS | 2026-09 | 2026-10 | 1 | 0 |  |
| 66621/1C | Orange County Advanced Power Station | TX | gas_cc | 400.0 | TS | TS | 2026-09 | 2026-10 | 1 | 0 |  |
| 69877/CHPV1 | Charger Solar | TX | solar | 394.4 | TS | TS | 2026-09 | 2026-10 | 1 | 0 |  |
| 68760/IPQ1S | Quantum Solar | TX | solar | 362.8 | TS | TS | 2026-11 | 2026-12 | 1 | 0 |  |
| 68762/IPQ2S | Quantum II Solar | TX | solar | 362.8 | TS | TS | 2026-11 | 2026-12 | 1 | 0 |  |
| 66915/CTW | Cottonwood Bayou Solar | TX | solar | 350.0 | TS | TS | 2026-09 | 2026-10 | 1 | 0 |  |
| 68065/CHILS | Chillingham Solar | TX | solar | 350.0 | TS | TS | 2026-09 | 2026-12 | 3 | 0 |  |
| 68940/CAPV | Country Acres Clean Power LLC | CA | solar | 344.0 | U | U | 2026-12 | 2027-02 | 2 | 0 |  |
| 66910/MYR | Myrtle Solar, LLC | TX | solar | 313.0 | TS | TS | 2026-10 | 2026-12 | 2 | 0 |  |
| 63798/ATL01 | Atlas | AZ | solar | 300.0 | V | V | 2026-08 | 2026-09 | 1 | 0 |  |

## Largest new planned generators

| key | plant | state | group | mw | status_prev | status_now | planned_prev | planned_now | shift_months | backward_before | possible_rekey |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 70541/SPV | Swan Solar | MO | solar | 650.0 |  | U |  | 2028-09 |  | 0 |  |
| 70522/SSLR | Hecate Energy Sunfish Solar LLC | MI | solar | 499.0 |  | L |  | 2028-12 |  | 0 |  |
| 70583/HLS01 | Highland Solar I, LLC - (CO) | CO | solar | 300.0 |  | L |  | 2027-12 |  | 0 |  |
| 70462/PAWS | Pawnee Solar & BESS | CO | solar | 250.0 |  | U |  | 2027-12 |  | 0 |  |
| 70515/PV1 | Burt County Solar (Sandhills Energy) | NE | solar | 250.0 |  | U |  | 2028-10 |  | 0 |  |
| 70453/CT4 | Red Oak Ridge Energy Center LLC | WI | gas_ct | 242.0 |  | L |  | 2029-12 |  | 0 |  |
| 70453/CT5 | Red Oak Ridge Energy Center LLC | WI | gas_ct | 242.0 |  | L |  | 2029-12 |  | 0 |  |
| 70453/RDOR1 | Red Oak Ridge Energy Center LLC | WI | gas_ct | 242.0 |  | P |  | 2029-12 |  | 0 |  |
| 70453/RDOR2 | Red Oak Ridge Energy Center LLC | WI | gas_ct | 242.0 |  | P |  | 2029-12 |  | 0 |  |
| 70453/RDOR3 | Red Oak Ridge Energy Center LLC | WI | gas_ct | 242.0 |  | P |  | 2029-12 |  | 0 |  |
| 8224/CT3 | North Valmy | NV | gas_ct | 208.0 |  | U |  | 2028-05 |  | 0 |  |
| 8224/CT4 | North Valmy | NV | gas_ct | 208.0 |  | U |  | 2028-05 |  | 0 |  |
| 70514/GEN1 | Hoyte Solar | TX | solar | 206.8 |  | V |  | 2027-07 |  | 0 |  |
| 70462/PAWB | Pawnee Solar & BESS | CO | battery | 200.0 |  | U |  | 2027-12 |  | 0 |  |
| 70513/3988 | Delta Bobcat Solar | MO | solar | 200.0 |  | V |  | 2026-12 |  | 0 |  |
| 70584/SOSBA | SOSA Energy Center | TX | battery | 155.8 |  | U |  | 2027-07 |  | 0 |  |
| 70544/GBESS | Greer Energy Storage | MS | battery | 150.0 |  | L |  | 2027-12 |  | 0 |  |
| 70455/BES | City Breeze Energy Storage | TX | battery | 140.0 |  | V |  | 2027-06 |  | 0 |  |
| 70492/WRES1 | Willow Rock Energy Storage Center | CA | other | 125.0 |  | P |  | 2030-07 |  | 0 |  |
| 70492/WRES2 | Willow Rock Energy Storage Center | CA | other | 125.0 |  | P |  | 2030-07 |  | 0 |  |

## Earlier moves: MW listed as operating within 12 reports

Steps with m from 2023-08 to 2025-09 (their 12 following reports are all in the file), by starting band and move: a recent base rate for the moves above, not a forecast for any one generator.

| band | move | steps | scored_mw | online_mw | online_share |
|---|---|---|---|---|---|
| early | forward | 423 | 41015.0 | 17703.9 | 0.432 |
| early | held | 19924 | 2930646.2 | 40272.6 | 0.014 |
| early | backward | 0 | 0.000 | 0.000 |  |
| early | to_operating | 9 | 25.0 | 25.0 | 1.000 |
| early | exit_other | 2 | 500.0 | 0.000 | 0.000 |
| approved | forward | 312 | 29700.0 | 14141.8 | 0.476 |
| approved | held | 5095 | 636686.0 | 33446.1 | 0.052 |
| approved | backward | 23 | 2381.2 | 0.000 | 0.000 |
| approved | to_operating | 14 | 595.5 | 595.5 | 1.000 |
| approved | exit_other | 0 | 0.000 | 0.000 |  |
| building | forward | 0 | 0.000 | 0.000 |  |
| building | held | 18958 | 1610984.2 | 908514.0 | 0.564 |
| building | backward | 20 | 2914.1 | 80.0 | 0.028 |
| building | to_operating | 1532 | 101796.1 | 101796.1 | 1.000 |
| building | exit_other | 2 | 245.0 | 0.000 | 0.000 |

## Checks

```
{
 "C1": {
  "rows": 568,
  "pass": true
 },
 "C2": {
  "planned_mw": 288646.9,
  "moves_mw": 288646.9,
  "pass": true
 },
 "C3": {
  "ours": {
   "forward": 22,
   "held": 2216,
   "backward": 1,
   "to_operating": 70,
   "exit_other": 0,
   "left": 3
  },
  "stagemoves": {
   "forward": 22,
   "held": 2216,
   "backward": 1,
   "to_operating": 70,
   "exit_other": 0,
   "left": 3
  },
  "pass": true
 },
 "C4": {
  "row_counts": {
   "forward": 22,
   "backward": 1,
   "to_operating": 70,
   "exit_other": 0,
   "left": 3,
   "within_band": 62,
   "delayed": 279,
   "advanced": 12,
   "new": 119,
   "into_planned": 0
  },
  "pass": true
 },
 "all_pass": true
}
```
