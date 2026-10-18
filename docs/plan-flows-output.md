# Where the 2026 solar plan went (plan_flows 0.1.0)

EIA-860M (PUDL changelog), GW net summer capacity. The 2026 book = online in 2026 by the report month + still planned for a 2026 month. Entries are counted at their new capacity, by where they were the report before; exits at their old capacity, by where they went. change = entries - exits + resize.

## Month by month (solar)

| report | book | change | entries | from not listed | from 2027+ | from blank/pre-2026 | from online other | from other status | exits | to 2027+ | to blank/pre-2026 | to online other | to other status | to not listed | resize | came online | entered online |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2025-12 | 43.65 | +2.28 | 6.27 | 3.07 | 0.00 | 3.20 | 0.00 | 0.00 | 3.99 | 3.35 | 0.00 | 0.58 | 0.00 | 0.06 | +0.00 | 0.00 | 0.00 |
| 2026-01 | 42.48 | -1.17 | 1.93 | 1.58 | 0.35 | 0.00 | 0.00 | 0.00 | 3.10 | 2.23 | 0.00 | 0.12 | 0.00 | 0.76 | -0.00 | 2.54 | 0.01 |
| 2026-02 | 41.77 | -0.71 | 0.62 | 0.00 | 0.62 | 0.00 | 0.00 | 0.00 | 1.33 | 1.03 | 0.00 | 0.00 | 0.00 | 0.30 | +0.00 | 0.51 | 0.00 |
| 2026-03 | 43.21 | +1.44 | 2.51 | 2.51 | 0.00 | 0.00 | 0.00 | 0.00 | 1.07 | 0.69 | 0.00 | 0.00 | 0.00 | 0.39 | +0.00 | 1.30 | 0.00 |
| 2026-04 | 43.09 | -0.12 | 0.81 | 0.81 | 0.00 | 0.00 | 0.00 | 0.00 | 0.93 | 0.59 | 0.00 | 0.33 | 0.00 | 0.01 | +0.00 | 3.01 | 0.01 |
| 2026-05 | 42.81 | -0.28 | 0.84 | 0.57 | 0.00 | 0.00 | 0.27 | 0.00 | 1.02 | 0.53 | 0.00 | 0.00 | 0.00 | 0.49 | -0.11 | 1.65 | 0.02 |
| 2026-06 | 41.62 | -1.19 | 0.75 | 0.75 | 0.00 | 0.00 | 0.00 | 0.00 | 1.94 | 1.77 | 0.00 | 0.00 | 0.00 | 0.16 | +0.00 | 2.55 | 0.01 |
| 2026-07 | 41.00 | -0.62 | 1.04 | 0.48 | 0.55 | 0.00 | 0.00 | 0.00 | 1.66 | 1.51 | 0.00 | 0.00 | 0.00 | 0.15 | -0.00 | 1.72 | 0.04 |
| 2026-08 | 41.13 | +0.13 | 0.21 | 0.21 | 0.00 | 0.00 | 0.00 | 0.00 | 0.08 | 0.07 | 0.00 | 0.00 | 0.00 | 0.01 | +0.00 | 1.13 | 0.17 |

Other statuses of exits, by report (GW): 

## The 2025-12 book in 2026-08 (solar)

43.65 GW in 2025-12; 41.13 GW in 2026-08.

| state in 2026-08 | GW (at 2025-12 capacity) | generators |
|---|---:|---:|
| online_2026 | 12.58 | 178 |
| planned_2026 | 20.71 | 228 |
| planned_later | 7.63 | 99 |
| planned_other | 0.00 | 0 |
| online_other | 0.45 | 4 |
| other_status | 0.00 | 0 |
| not_listed | 2.29 | 28 |

Joined the book since 2025-12 (GW at 2026-08 capacity, by state in 2025-12): planned_later 1.37, planned_other 0.00, online_other 0.27, other_status 0.00, not_listed 6.30; total 7.94 GW in 266 generators, 2.08 GW of it already online. Resize of generators in both books: -0.11 GW.

Other statuses (GW): {}

By status in 2025-12:

| status | GW | generators | online_2026 | planned_2026 | planned_later | planned_other | online_other | other_status | not_listed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| L | 4.12 | 44 | 0.08 | 0.30 | 2.91 | 0.00 | 0.00 | 0.00 | 0.82 |
| OT | 0.10 | 1 | 0.00 | 0.00 | 0.10 | 0.00 | 0.00 | 0.00 | 0.00 |
| P | 4.73 | 44 | 0.10 | 1.65 | 2.00 | 0.00 | 0.11 | 0.00 | 0.88 |
| T | 2.61 | 39 | 0.04 | 0.96 | 1.44 | 0.00 | 0.00 | 0.00 | 0.17 |
| TS | 7.01 | 64 | 2.26 | 4.75 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| U | 13.17 | 182 | 3.55 | 8.70 | 0.72 | 0.00 | 0.00 | 0.00 | 0.20 |
| V | 11.90 | 163 | 6.56 | 4.34 | 0.45 | 0.00 | 0.34 | 0.00 | 0.21 |

Wind, same reading: 12.12 GW in 2025-12; in 2026-08: online_2026 6.48, planned_2026 2.85, planned_later 2.39, planned_other 0.00, online_other 0.40, other_status 0.00, not_listed 0.00; joined 1.03 GW.

## Checks and prediction aids (scored by hand against the pre-registration)

```
{
 "checks": {
  "C1": {
   "pairs": 9,
   "largest_residual_gw": 0.0,
   "passed": true
  },
  "C2": {
   "reports_compared": 10,
   "differences_gw": {
    "2025-11": -0.001,
    "2025-12": 0.0037,
    "2026-01": 0.0022,
    "2026-02": -0.0004,
    "2026-03": -0.0003,
    "2026-04": -0.001,
    "2026-05": -0.0019,
    "2026-06": -0.0003,
    "2026-07": -0.0028,
    "2026-08": -0.0024
   },
   "passed": true
  },
  "C3": {
   "fate_sum_gw": 43.6537,
   "base_book_gw": 43.6537,
   "passed": true
  }
 },
 "predictions": {
  "F1": {
   "planned_later_gw": 7.627,
   "held": false
  },
  "F2": {
   "entries_gw": 7.945,
   "held": true
  },
  "F3": {
   "online_gw": 12.579,
   "share": 0.2882,
   "held": true
  },
  "F4": {
   "cancelled_or_unlisted_gw": 2.288,
   "planned_later_gw": 7.627,
   "held": true
  },
  "F5": {
   "building_gw": 32.086,
   "building_online_share": 0.3854,
   "early_gw": 8.854,
   "early_online_share": 0.0198,
   "held": false
  }
 }
}
```
