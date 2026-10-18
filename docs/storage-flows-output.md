# Where the 2026 battery storage plan went (storage_flows 0.1.0, plan_flows 0.1.0)

EIA-860M (PUDL changelog), technology 'Batteries', GW net summer capacity, read exactly as plan_flows reads solar. The 2026 book = online in 2026 by the report month + still planned for a 2026 month. change = entries - exits + resize.

Technology names containing 'batter' or 'stor' in the changelog (records): {"Batteries": 9555, "Hydroelectric Pumped Storage": 1089, "Natural Gas with Compressed Air Storage": 30, "Other Energy Storage": 9, "Solar Thermal with Energy Storage": 28, "Solar Thermal without Energy Storage": 148}

## The 2025-12 battery book in 2026-08

24.28 GW in 2025-12; 22.77 GW in 2026-08.

| state in 2026-08 | GW (at 2025-12 capacity) | generators |
|---|---:|---:|
| online_2026 | 9.57 | 107 |
| planned_2026 | 8.69 | 90 |
| planned_later | 3.65 | 43 |
| planned_other | 0.00 | 0 |
| online_other | 0.50 | 2 |
| other_status | 0.00 | 0 |
| not_listed | 1.88 | 21 |

Joined the book since 2025-12 (GW at 2026-08 capacity, by state in 2025-12): planned_later 0.70, planned_other 0.10, online_other 0.00, other_status 0.00, not_listed 3.71; total 4.51 GW in 75 generators, 1.20 GW of it already online. Resize of generators in both books: +0.00 GW.

Other statuses (GW): {}

By status in 2025-12:

| status | GW | generators | online_2026 | planned_2026 | planned_later | planned_other | online_other | other_status | not_listed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| L | 2.73 | 20 | 0.00 | 0.66 | 0.80 | 0.00 | 0.00 | 0.00 | 1.28 |
| P | 3.20 | 29 | 0.00 | 1.49 | 1.61 | 0.00 | 0.00 | 0.00 | 0.10 |
| T | 0.63 | 12 | 0.00 | 0.04 | 0.59 | 0.00 | 0.00 | 0.00 | 0.00 |
| TS | 3.36 | 49 | 2.10 | 0.75 | 0.00 | 0.00 | 0.50 | 0.00 | 0.01 |
| U | 8.09 | 79 | 3.73 | 3.96 | 0.32 | 0.00 | 0.00 | 0.00 | 0.08 |
| V | 6.27 | 74 | 3.74 | 1.79 | 0.33 | 0.00 | 0.00 | 0.00 | 0.41 |

| stage in 2025-12 | GW | online | still 2026 | 2027+ | not listed or other status |
|---|---:|---:|---:|---:|---:|
| building | 17.72 | 54.0% | 36.7% | 3.7% | 2.8% |
| early | 5.93 | 0.0% | 36.2% | 40.6% | 23.2% |

## Batteries beside 2026 solar

Paired (plant also has solar in the 2025-12 2026 book): 6.89 GW in 76 generators; alone: 17.39 GW in 187. Same group as the plant's lead solar generator in 2026-08: 5.41 GW (78.6%).

| battery in 2026-08 \ lead solar in 2026-08 | online_2026 | planned_2026 | planned_later | other |
|---|---:|---:|---:|---:|
| online_2026 | 1.63 | 0.35 | 0.04 | 0.05 |
| planned_2026 | 0.24 | 1.66 | 0.42 | 0.00 |
| planned_later | 0.00 | 0.00 | 2.00 | 0.00 |
| other | 0.08 | 0.30 | 0.00 | 0.13 |

Alone, by group in 2026-08 (GW): online_2026 7.50, planned_2026 6.37, planned_later 1.65, other 1.87

## Month by month (batteries)

| report | book | change | entries | from not listed | from 2027+ | exits | to 2027+ | to not listed | to other status | resize | came online |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2025-12 | 24.28 | +0.73 | 3.13 | 0.86 | 0.00 | 2.26 | 1.48 | 0.50 | 0.00 | -0.15 | 0.00 |
| 2026-01 | 23.12 | -1.17 | 0.36 | 0.14 | 0.13 | 1.53 | 1.10 | 0.12 | 0.00 | +0.00 | 0.84 |
| 2026-02 | 22.04 | -1.08 | 0.37 | 0.07 | 0.30 | 1.45 | 0.84 | 0.61 | 0.00 | +0.00 | 0.70 |
| 2026-03 | 23.69 | +1.65 | 2.24 | 2.24 | 0.00 | 0.59 | 0.25 | 0.14 | 0.00 | +0.00 | 1.25 |
| 2026-04 | 24.13 | +0.44 | 0.72 | 0.72 | 0.00 | 0.28 | 0.28 | 0.00 | 0.00 | +0.00 | 1.74 |
| 2026-05 | 23.47 | -0.66 | 0.21 | 0.21 | 0.00 | 0.88 | 0.18 | 0.70 | 0.00 | +0.01 | 0.55 |
| 2026-06 | 22.71 | -0.76 | 0.45 | 0.44 | 0.01 | 1.20 | 1.20 | 0.00 | 0.00 | +0.00 | 2.69 |
| 2026-07 | 22.85 | +0.13 | 0.50 | 0.10 | 0.40 | 0.36 | 0.06 | 0.30 | 0.00 | +0.00 | 1.40 |
| 2026-08 | 22.77 | -0.07 | 0.20 | 0.20 | 0.00 | 0.27 | 0.27 | 0.00 | 0.00 | +0.00 | 1.14 |

## Largest generators that left the 2025-12 book by 2026-08

| plant | generator | 2025-12 status | 2025-12 planned | MW | 2026-08 state | 2026-08 planned |
|---|---|---|---|---:|---|---|
| 65852 | LUNBS | L | 2026-10 | 621.4 | not_listed |  |
| 65842 | CFCBS | L | 2026-12 | 600.0 | planned_later | 2027-03 |
| 63798 | ATLB1 | V | 2026-01 | 300.0 | not_listed |  |
| 68513 | CWHBA | TS | 2026-03 | 300.0 | online_other |  |
| 67987 | MYSPB | P | 2026-12 | 250.0 | planned_later | 2028-03 |
| 69520 | AMDRB | U | 2026-03 | 220.0 | planned_later | 2027-04 |
| 67917 | CHMPN | P | 2026-09 | 202.7 | planned_later | 2027-06 |
| 67656 | FWATT | L | 2026-12 | 200.0 | not_listed |  |
| 67658 | JERBO | L | 2026-12 | 200.0 | not_listed |  |
| 67668 | WALLE | L | 2026-11 | 200.0 | not_listed |  |

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
   "fate_sum_gw": 24.2827,
   "base_book_gw": 24.2827,
   "passed": true
  },
  "K3": {
   "differences_gw": {
    "base_book": 0.0037,
    "online_2026": -0.0011,
    "planned_2026": 0.0,
    "planned_later": -0.0027,
    "not_listed": -0.0021
   },
   "passed": true
  },
  "K4": {
   "base_book_gw": 24.283,
   "eia_gw": 24.0,
   "relative_difference": 0.0118,
   "passed": true
  }
 },
 "predictions": {
  "B1": {
   "planned_later_gw": 3.648,
   "share": 0.1502,
   "held": false
  },
  "B2": {
   "online_gw": 9.571,
   "share": 0.3941,
   "held": false
  },
  "B3": {
   "cancelled_or_unlisted_gw": 1.876,
   "planned_later_gw": 3.648,
   "held": true
  },
  "B4": {
   "building_later_share": 0.0369,
   "early_later_share": 0.4056,
   "held": true
  },
  "B5": {
   "joined_gw": 4.511,
   "latest_book_gw": 22.774,
   "share": 0.1981,
   "held": true
  },
  "B6": {
   "paired_gw": 6.89,
   "agree_gw": 5.413,
   "share": 0.7856,
   "held": true
  }
 }
}
```
