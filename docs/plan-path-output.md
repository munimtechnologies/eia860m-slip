# The 2026 solar figure, month by month (plan_path 0.1.0)

Plan side: EIA-860M (PUDL changelog), GW summer capacity. Added = came online in 2026 by the report month; planned = still planned for a 2026 month; implied = added + planned; overdue = planned for a 2026 month before the report month and not yet online (nameplate).

| report | solar added | solar planned | solar implied | overdue | planned units | wind implied | solar implied (other measure) |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2025-11 | 0.00 | 41.37 | 41.37 | 0.00 | 478 | 10.89 | 41.43 |
| 2025-12 | 0.00 | 43.65 | 43.65 | 0.00 | 537 | 12.12 | 43.72 |
| 2026-01 | 2.55 | 39.93 | 42.48 | 0.00 | 518 | 11.88 | 42.55 |
| 2026-02 | 3.05 | 38.71 | 41.77 | 0.00 | 494 | 11.44 | 41.84 |
| 2026-03 | 4.36 | 38.85 | 43.21 | 0.00 | 547 | 11.68 | 43.28 |
| 2026-04 | 7.38 | 35.71 | 43.09 | 0.21 | 501 | 11.68 | 43.16 |
| 2026-05 | 9.05 | 33.76 | 42.81 | 0.00 | 501 | 11.68 | 42.98 |
| 2026-06 | 11.61 | 30.01 | 41.62 | 0.00 | 430 | 11.35 | 41.80 |
| 2026-07 | 13.37 | 27.63 | 41.00 | 0.00 | 407 | 11.43 | 41.18 |
| 2026-08 | 14.66 | 26.47 | 41.13 | 0.00 | 388 | 10.39 | 41.31 |

STEO side: capacity table, electric power sector, GW at end of period.

| edition | pairs with report | solar end-2025 | solar end-2026 | solar 2026 | wind 2026 | note |
|---|---|---:|---:|---:|---:|---|
| jan26 | 2025-11 | 139.2 | 171.3 | 32.1 | 9.7 |  |
| feb26 | 2025-12 | 139.2 | 170.7 | 31.5 | 11.7 |  |
| mar26 | 2026-01 | 139.2 | 170.7 | 31.5 | 11.7 |  |
| apr26 | 2026-02 | 138.3 | 169.6 | 31.3 | 11.6 |  |
| may26 | 2026-03 | 148.3 | 178.7 | 30.4 | 11.4 |  |
| jun26 | 2026-04 | 149.3 | 181.0 | 31.7 | 11.7 |  |
| jul26 | 2026-05 | 149.8 | 181.6 | 31.8 | 11.7 |  |
| aug26 | 2026-06 | 149.9 | 181.9 | 32.0 | 11.4 |  |
| sep26 | 2026-07 | 150.1 | 179.2 | 29.1 | 11.4 |  |
| oct26 | 2026-08 | 150.4 | 181.1 | 30.7 | 11.4 |  |

Pairs (edition with the EIA-860M report two months earlier):

| edition | report | STEO solar 2026 | implied solar 2026 | gap | STEO wind 2026 | implied wind 2026 |
|---|---|---:|---:|---:|---:|---:|
| jan26 | 2025-11 | 32.1 | 41.37 | 9.27 | 9.7 | 10.89 |
| feb26 | 2025-12 | 31.5 | 43.65 | 12.15 | 11.7 | 12.12 |
| mar26 | 2026-01 | 31.5 | 42.48 | 10.98 | 11.7 | 11.88 |
| apr26 | 2026-02 | 31.3 | 41.77 | 10.47 | 11.6 | 11.44 |
| may26 | 2026-03 | 30.4 | 43.21 | 12.81 | 11.4 | 11.68 |
| jun26 | 2026-04 | 31.7 | 43.09 | 11.39 | 11.7 | 11.68 |
| jul26 | 2026-05 | 31.8 | 42.81 | 11.01 | 11.7 | 11.68 |
| aug26 | 2026-06 | 32.0 | 41.62 | 9.62 | 11.4 | 11.35 |
| sep26 | 2026-07 | 29.1 | 41.00 | 11.90 | 11.4 | 11.43 |
| oct26 | 2026-08 | 30.7 | 41.13 | 10.43 | 11.4 | 10.39 |

## Checks and prediction aids (scored by hand against the pre-registration)

```
{
 "checks": {
  "C1": {
   "planned_2026_solar_gw": {
    "nameplate": 43.72,
    "summer": 43.65
   },
   "relative_difference": {
    "nameplate": 0.0074,
    "summer": 0.0058
   },
   "measure": "summer",
   "passed": true,
   "wind_planned_2026_gw": {
    "nameplate": 12.13,
    "summer": 12.12
   }
  },
  "C2": {
   "editions": 10,
   "parsed": 10,
   "sane": 8,
   "jan26_reproduced": true,
   "passed": true
  },
  "C3": {
   "largest_drop_gw": 0.0,
   "drops": [],
   "passed": true
  }
 },
 "predictions": {
  "P1": {
   "december_2025": 43.65,
   "latest": 41.13,
   "latest_report": "2026-08",
   "drop_gw": 2.52,
   "held": false
  },
  "P2": {
   "pairs": 10,
   "pairs_with_plan_above": 10,
   "held": true
  },
  "P3": {
   "feb26_gap": 12.15,
   "latest_edition": "oct26",
   "latest_gap": 10.43,
   "held": false
  },
  "P4": {
   "jan26": 32.1,
   "latest_edition": "oct26",
   "latest": 30.7,
   "change_gw": -1.4,
   "held": true
  },
  "P5": {
   "latest_report": "2026-08",
   "added": 14.66,
   "implied": 41.13,
   "share": 0.3564,
   "held": false
  }
 }
}
```
