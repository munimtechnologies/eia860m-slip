# Where the 2026 natural gas plan went (gas_flows 0.1.0, plan_flows 0.1.0)

EIA-860M (PUDL changelog), GW net summer capacity, read exactly as plan_flows reads solar. Natural gas = natural gas fired combined cycle, natural gas fired combustion turbine, natural gas internal combustion engine, natural gas steam turbine, other natural gas. The 2026 book = online in 2026 by the report month + still planned for a 2026 month. change = entries - exits + resize.

Technology names containing 'natural gas' in the changelog (records): {"Natural Gas Fired Combined Cycle": 17912, "Natural Gas Fired Combustion Turbine": 20922, "Natural Gas Internal Combustion Engine": 11020, "Natural Gas Steam Turbine": 6611, "Natural Gas with Compressed Air Storage": 30, "Other Natural Gas": 950}

## Four technologies: the 2025-12 2026 book in 2026-08

| technology | 2025-12 book | online 2026 | still 2026 | 2027+ | blank/pre-2026 | online outside 2026 | other status | not listed | left the year | joined since | 2026-08 book |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| solar | 43.65 | 12.58 | 20.71 | 7.63 | 0.00 | 0.45 | 0.00 | 2.29 | 23.7% | 7.94 | 41.13 |
| wind | 12.12 | 6.48 | 2.85 | 2.39 | 0.00 | 0.40 | 0.00 | 0.00 | 23.0% | 1.03 | 10.39 |
| batteries | 24.28 | 9.57 | 8.69 | 3.65 | 0.00 | 0.50 | 0.00 | 1.88 | 24.8% | 4.51 | 22.77 |
| gas | 6.26 | 2.30 | 2.36 | 1.53 | 0.00 | 0.00 | 0.00 | 0.08 | 25.6% | 1.11 | 5.77 |

Sum of the four 2025-12 books: 86.32 GW.

## The 2025-12 natural gas book in 2026-08

6.26 GW in 2025-12; 5.77 GW in 2026-08.

| state in 2026-08 | GW (at 2025-12 capacity) | generators |
|---|---:|---:|
| online_2026 | 2.30 | 43 |
| planned_2026 | 2.36 | 29 |
| planned_later | 1.53 | 8 |
| planned_other | 0.00 | 0 |
| online_other | 0.00 | 0 |
| other_status | 0.00 | 0 |
| not_listed | 0.08 | 2 |

Joined the book since 2025-12 (GW at 2026-08 capacity, by state in 2025-12): planned_later 0.45, planned_other 0.00, online_other 0.00, other_status 0.00, not_listed 0.66; total 1.11 GW in 28 generators, 0.62 GW of it already online. Resize of generators in both books: -0.01 GW.

Other statuses (GW): {}

By status in 2025-12:

| status | GW | generators | online_2026 | planned_2026 | planned_later | planned_other | online_other | other_status | not_listed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| L | 0.08 | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.08 |
| P | 0.45 | 4 | 0.00 | 0.03 | 0.42 | 0.00 | 0.00 | 0.00 | 0.00 |
| T | 0.16 | 14 | 0.00 | 0.13 | 0.02 | 0.00 | 0.00 | 0.00 | 0.00 |
| TS | 0.11 | 7 | 0.11 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| U | 1.89 | 29 | 0.80 | 0.00 | 1.08 | 0.00 | 0.00 | 0.00 | 0.00 |
| V | 3.58 | 26 | 1.38 | 2.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |

| stage in 2025-12 | GW | online | still 2026 | 2027+ | not listed or other status |
|---|---:|---:|---:|---:|---:|
| building | 5.58 | 41.2% | 39.4% | 19.4% | 0.0% |
| early | 0.53 | 0.0% | 5.7% | 79.9% | 14.4% |

## By prime mover (cc = combined cycle, ct = combustion turbine, other = engines, steam, other)

| group | 2025-12 book | generators | online 2026 | still 2026 | 2027+ | online outside 2026 | not listed | other status | joined since | 2026-08 book |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| cc | 3.28 | 11 | 0.90 | 1.70 | 0.69 | 0.00 | 0.00 | 0.00 | 0.00 | 2.60 |
| ct | 2.79 | 30 | 1.35 | 0.53 | 0.83 | 0.00 | 0.08 | 0.00 | 0.87 | 2.74 |
| other | 0.19 | 41 | 0.05 | 0.14 | 0.01 | 0.00 | 0.00 | 0.00 | 0.24 | 0.43 |

## Month by month (natural gas)

| report | book | change | entries | from not listed | from 2027+ | exits | to 2027+ | to not listed | to other status | resize | came online |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2025-12 | 6.26 | +0.28 | 0.29 | 0.00 | 0.00 | 0.01 | 0.00 | 0.01 | 0.00 | +0.00 | 0.00 |
| 2026-01 | 6.37 | +0.11 | 0.19 | 0.19 | 0.00 | 0.08 | 0.08 | 0.00 | 0.00 | +0.00 | 0.03 |
| 2026-02 | 7.38 | +1.00 | 1.01 | 0.56 | 0.45 | 0.00 | 0.00 | 0.00 | 0.00 | -0.01 | 0.22 |
| 2026-03 | 7.58 | +0.20 | 0.45 | 0.45 | 0.00 | 0.25 | 0.25 | 0.00 | 0.00 | +0.00 | 0.11 |
| 2026-04 | 7.16 | -0.42 | 0.00 | 0.00 | 0.00 | 0.42 | 0.42 | 0.00 | 0.00 | +0.00 | 1.52 |
| 2026-05 | 7.16 | +0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | +0.00 | 0.45 |
| 2026-06 | 7.27 | +0.11 | 0.13 | 0.13 | 0.00 | 0.02 | 0.02 | 0.00 | 0.00 | +0.00 | 0.25 |
| 2026-07 | 6.60 | -0.67 | 0.00 | 0.00 | 0.00 | 0.67 | 0.67 | 0.00 | 0.00 | +0.00 | 0.01 |
| 2026-08 | 5.77 | -0.83 | 0.00 | 0.00 | 0.00 | 0.83 | 0.83 | 0.00 | 0.00 | +0.00 | 0.20 |

## Largest generators that left the 2025-12 book by 2026-08

| plant | generator | group | 2025-12 status | 2025-12 planned | MW | 2026-08 state | 2026-08 planned |
|---|---|---|---|---|---:|---|---|
| 728 | 8 | ct | P | 2026-12 | 418.4 | planned_later | 2027-02 |
| 67262 | RP1 | ct | U | 2026-10 | 411.4 | planned_later | 2027-03 |
| 3399 | CTG1 | cc | U | 2026-12 | 372.9 | planned_later | 2034-12 |
| 3399 | STG1 | cc | U | 2026-12 | 296.6 | planned_later | 2034-12 |
| 160 | GT7 | ct | L | 2026-12 | 38.0 | not_listed |  |
| 160 | GT8 | ct | L | 2026-12 | 38.0 | not_listed |  |
| 1024 | 8 | cc | T | 2026-10 | 16.3 | planned_later | 2027-03 |
| 52021 | GEN3 | other | T | 2026-10 | 4.1 | planned_later | 2027-03 |
| 52021 | GEN4 | other | T | 2026-10 | 4.1 | planned_later | 2027-03 |
| 54808 | STG1 | cc | P | 2026-10 | 1.8 | planned_later | 2027-05 |

## The two plants EIA named, by raw record

### trumbull (plant_name_eia contains 'trumbull energy'): plants {"66918": "Trumbull Energy Center"}

| plant | generator | group | 2025-12 state | 2025-12 status | 2025-12 planned | MW | 2026-08 state | 2026-08 status | 2026-08 planned | 2026-08 online |
|---|---|---|---|---|---|---:|---|---|---|---|
| 66918 | GT11 | cc | planned_2026 | V | 2026-01 | 275.6 | online_2026 | OP |  | 2026-04 |
| 66918 | GT12 | cc | planned_2026 | V | 2026-01 | 275.6 | online_2026 | OP |  | 2026-04 |
| 66918 | STG | cc | planned_2026 | V | 2026-01 | 349.2 | online_2026 | OP |  | 2026-04 |

| report_date | valid_until_date | plant_id_eia | generator_id | capacity_mw | summer_capacity_mw | current_planned_generator_operating_date | generator_operating_date | operational_status_code | technology_description | plant_name_eia |
|---|---|---|---|---|---|---|---|---|---|---|
| 2023-08-01 | 2025-01-01 | 66918 | GT11 | 350.0 | 350.0 | 2026-01-01 |  | U | Natural Gas Fired Combined Cycle | Trumbull Energy Center |
| 2025-01-01 | 2025-02-01 | 66918 | GT11 | 350.0 | 350.0 | 2026-01-01 |  | V | Natural Gas Fired Combined Cycle | Trumbull Energy Center |
| 2025-02-01 | 2026-01-01 | 66918 | GT11 | 343.0 | 275.6 | 2026-01-01 |  | V | Natural Gas Fired Combined Cycle | Trumbull Energy Center |
| 2026-01-01 | 2026-04-01 | 66918 | GT11 | 308.7 | 275.6 | 2026-04-01 |  | V | Natural Gas Fired Combined Cycle | Trumbull Energy Center |
| 2026-04-01 | 2026-08-01 | 66918 | GT11 | 308.7 | 275.6 |  | 2026-04-01 | OP | Natural Gas Fired Combined Cycle | Trumbull Energy Center |
| 2023-08-01 | 2025-01-01 | 66918 | GT12 | 350.0 | 350.0 | 2026-01-01 |  | U | Natural Gas Fired Combined Cycle | Trumbull Energy Center |
| 2025-01-01 | 2025-02-01 | 66918 | GT12 | 350.0 | 350.0 | 2026-01-01 |  | V | Natural Gas Fired Combined Cycle | Trumbull Energy Center |
| 2025-02-01 | 2026-01-01 | 66918 | GT12 | 343.0 | 275.6 | 2026-01-01 |  | V | Natural Gas Fired Combined Cycle | Trumbull Energy Center |
| 2026-01-01 | 2026-04-01 | 66918 | GT12 | 308.7 | 275.6 | 2026-04-01 |  | V | Natural Gas Fired Combined Cycle | Trumbull Energy Center |
| 2026-04-01 | 2026-08-01 | 66918 | GT12 | 308.7 | 275.6 |  | 2026-04-01 | OP | Natural Gas Fired Combined Cycle | Trumbull Energy Center |
| 2023-08-01 | 2025-01-01 | 66918 | STG | 250.0 | 250.0 | 2026-01-01 |  | U | Natural Gas Fired Combined Cycle | Trumbull Energy Center |
| 2025-01-01 | 2025-02-01 | 66918 | STG | 250.0 | 250.0 | 2026-01-01 |  | V | Natural Gas Fired Combined Cycle | Trumbull Energy Center |
| 2025-02-01 | 2026-01-01 | 66918 | STG | 400.0 | 349.2 | 2026-01-01 |  | V | Natural Gas Fired Combined Cycle | Trumbull Energy Center |
| 2026-01-01 | 2026-04-01 | 66918 | STG | 360.0 | 349.2 | 2026-04-01 |  | V | Natural Gas Fired Combined Cycle | Trumbull Energy Center |
| 2026-04-01 | 2026-08-01 | 66918 | STG | 360.0 | 349.2 |  | 2026-04-01 | OP | Natural Gas Fired Combined Cycle | Trumbull Energy Center |

### orange_county (plant_name_eia contains 'orange county advanced power'): plants {"66621": "Orange County Advanced Power Station"}

| plant | generator | group | 2025-12 state | 2025-12 status | 2025-12 planned | MW | 2026-08 state | 2026-08 status | 2026-08 planned | 2026-08 online |
|---|---|---|---|---|---|---:|---|---|---|---|
| 66621 | 1A | cc | planned_2026 | V | 2026-06 | 396.6 | planned_2026 | TS | 2026-09 |  |
| 66621 | 1B | cc | planned_2026 | V | 2026-06 | 396.6 | planned_2026 | TS | 2026-09 |  |
| 66621 | 1C | cc | planned_2026 | V | 2026-06 | 365.0 | planned_2026 | TS | 2026-09 |  |

| report_date | valid_until_date | plant_id_eia | generator_id | capacity_mw | summer_capacity_mw | current_planned_generator_operating_date | generator_operating_date | operational_status_code | technology_description | plant_name_eia |
|---|---|---|---|---|---|---|---|---|---|---|
| 2023-05-01 | 2025-06-01 | 66621 | 1A | 453.0 | 396.6 | 2026-06-01 |  | T | Natural Gas Fired Combined Cycle | Orange County Advanced Power Station |
| 2025-06-01 | 2026-02-01 | 66621 | 1A | 453.0 | 396.6 | 2026-06-01 |  | V | Natural Gas Fired Combined Cycle | Orange County Advanced Power Station |
| 2026-02-01 | 2026-06-01 | 66621 | 1A | 453.0 | 396.6 | 2026-07-01 |  | V | Natural Gas Fired Combined Cycle | Orange County Advanced Power Station |
| 2026-06-01 | 2026-07-01 | 66621 | 1A | 453.0 | 396.6 | 2026-08-01 |  | V | Natural Gas Fired Combined Cycle | Orange County Advanced Power Station |
| 2026-07-01 | 2026-08-01 | 66621 | 1A | 453.0 | 396.6 | 2026-08-01 |  | TS | Natural Gas Fired Combined Cycle | Orange County Advanced Power Station |
| 2026-08-01 | 2026-09-01 | 66621 | 1A | 453.0 | 396.6 | 2026-09-01 |  | TS | Natural Gas Fired Combined Cycle | Orange County Advanced Power Station |
| 2023-05-01 | 2025-06-01 | 66621 | 1B | 453.0 | 396.6 | 2026-06-01 |  | T | Natural Gas Fired Combined Cycle | Orange County Advanced Power Station |
| 2025-06-01 | 2026-02-01 | 66621 | 1B | 453.0 | 396.6 | 2026-06-01 |  | V | Natural Gas Fired Combined Cycle | Orange County Advanced Power Station |
| 2026-02-01 | 2026-06-01 | 66621 | 1B | 453.0 | 396.6 | 2026-07-01 |  | V | Natural Gas Fired Combined Cycle | Orange County Advanced Power Station |
| 2026-06-01 | 2026-07-01 | 66621 | 1B | 453.0 | 396.6 | 2026-08-01 |  | V | Natural Gas Fired Combined Cycle | Orange County Advanced Power Station |
| 2026-07-01 | 2026-08-01 | 66621 | 1B | 453.0 | 396.6 | 2026-08-01 |  | TS | Natural Gas Fired Combined Cycle | Orange County Advanced Power Station |
| 2026-08-01 | 2026-09-01 | 66621 | 1B | 453.0 | 396.6 | 2026-09-01 |  | TS | Natural Gas Fired Combined Cycle | Orange County Advanced Power Station |
| 2023-05-01 | 2025-06-01 | 66621 | 1C | 400.0 | 365.0 | 2026-06-01 |  | T | Natural Gas Fired Combined Cycle | Orange County Advanced Power Station |
| 2025-06-01 | 2026-02-01 | 66621 | 1C | 400.0 | 365.0 | 2026-06-01 |  | V | Natural Gas Fired Combined Cycle | Orange County Advanced Power Station |
| 2026-02-01 | 2026-06-01 | 66621 | 1C | 400.0 | 365.0 | 2026-07-01 |  | V | Natural Gas Fired Combined Cycle | Orange County Advanced Power Station |
| 2026-06-01 | 2026-07-01 | 66621 | 1C | 400.0 | 365.0 | 2026-08-01 |  | V | Natural Gas Fired Combined Cycle | Orange County Advanced Power Station |
| 2026-07-01 | 2026-08-01 | 66621 | 1C | 400.0 | 365.0 | 2026-08-01 |  | TS | Natural Gas Fired Combined Cycle | Orange County Advanced Power Station |
| 2026-08-01 | 2026-09-01 | 66621 | 1C | 400.0 | 365.0 | 2026-09-01 |  | TS | Natural Gas Fired Combined Cycle | Orange County Advanced Power Station |

## Checks and prediction aids (scored by hand against the pre-registration)

```
{
 "checks": {
  "K1": {
   "pairs": 9,
   "largest_residual_gw": 0.0,
   "passed": true
  },
  "K2": {
   "fate_sum_gw": 6.2635,
   "base_book_gw": 6.2635,
   "passed": true
  },
  "K3": {
   "differences_gw": {
    "solar": {
     "base_book": 0.0037,
     "online_2026": -0.0011,
     "planned_2026": 0.0,
     "planned_later": -0.0027,
     "not_listed": -0.0021
    },
    "wind": {
     "base_book": 0.002,
     "online_2026": 0.0006,
     "planned_2026": 0.0009,
     "planned_later": 0.0005,
     "not_listed": 0.0
    },
    "batteries": {
     "base_book": 0.0027,
     "online_2026": 0.0006,
     "planned_2026": -0.0026,
     "planned_later": -0.0016,
     "not_listed": -0.0037
    }
   },
   "passed": true
  },
  "K4": {
   "base_book_gw": 6.264,
   "eia_gw": 6.3,
   "relative_difference": -0.0058,
   "passed": true
  }
 },
 "predictions": {
  "G1": {
   "online_gw": 2.299,
   "share": 0.367,
   "held": true
  },
  "G2": {
   "planned_later_gw": 1.526,
   "share": 0.2436,
   "held": false
  },
  "G3": {
   "cancelled_or_unlisted_gw": 0.076,
   "share": 0.0121,
   "held": true
  },
  "G4": {
   "cc_base_gw": 3.284,
   "cc_online_share": 0.2741,
   "ct_base_gw": 2.785,
   "ct_online_share": 0.4841,
   "held": false
  },
  "G5": {
   "early_left_share": 0.943,
   "building_later_share": 0.1938,
   "held": false
  },
  "G6": {
   "trumbull": [
    [
     "GT11",
     "online_2026",
     "2026-04"
    ],
    [
     "GT12",
     "online_2026",
     "2026-04"
    ],
    [
     "STG",
     "online_2026",
     "2026-04"
    ]
   ],
   "orange_county": [
    [
     "1A",
     "planned_2026",
     "2026-09"
    ],
    [
     "1B",
     "planned_2026",
     "2026-09"
    ],
    [
     "1C",
     "planned_2026",
     "2026-09"
    ]
   ],
   "held": true
  }
 }
}
```
