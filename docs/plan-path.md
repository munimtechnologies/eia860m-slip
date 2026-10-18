# The 2026 solar figure, month by month: the developers' plan held, the STEO held, and they are still 10 GW apart

MV2 of Munim, Inc., 18 October 2026. Made with AI agents working in his name. Text and data CC BY 4.0; code in [`tools/plan-path/`](../tools/plan-path/) Apache-2.0.

**Status: scored.** The checks and predictions were published before the job ran ([`plan-path-preregistration.md`](plan-path-preregistration.md), commit 90c60dd). Job `plan-path-v1` ran in a sealed container on 2026-10-18 (10:04-10:07Z); its 11 unit tests passed first. All three checks passed. **2 of the 5 predictions held.** Raw output: [`plan-path-output.md`](plan-path-output.md); one row per report: [`../data/plan_path.csv`](../data/plan_path.csv).

## Question

[`steo-vs-plan.md`](steo-vs-plan.md) found that in January 2026 EIA's Short-Term Energy Outlook (STEO) put 2026 utility-scale solar additions at 32.1 GW, 26% below the 43.4 GW that developers had scheduled in EIA-860M. Both numbers are restated every month. As 2026 goes on, does the developers' plan shrink toward the STEO, does the STEO rise toward the plan, or neither?

## Method (as pre-registered)

- **Plan side.** Every monthly EIA-860M report from November 2025 to August 2026 (PUDL's changelog). *Added* = solar generators online with an operating month in 2026, up to the report month. *Planned* = solar generators in a planned status with a planned operating month in 2026. *Implied 2026 total* = added + planned. Net summer capacity (check C1 chose it; nameplate differs by under 0.2 GW in every month).
- **STEO side.** The capacity table (Table 7e, electric power sector) of every edition from January to October 2026: end-2026 solar minus end-2025 solar. All 20 figures (solar and wind, ten editions) were read again by hand in the extracted page text and all match the code's.
- **Pairing.** Each edition with the EIA-860M report two months earlier, the latest one available when the edition was finished.

## Results

| report | added so far | still planned | implied 2026 total | paired STEO edition | STEO 2026 | gap |
|---|---:|---:|---:|---|---:|---:|
| 2025-11 | 0.00 | 41.37 | 41.37 | Jan | 32.1 | 9.27 |
| 2025-12 | 0.00 | 43.65 | 43.65 | Feb | 31.5 | 12.15 |
| 2026-01 | 2.55 | 39.93 | 42.48 | Mar | 31.5 | 10.98 |
| 2026-02 | 3.05 | 38.71 | 41.77 | Apr | 31.3 | 10.47 |
| 2026-03 | 4.36 | 38.85 | 43.21 | May | 30.4 | 12.81 |
| 2026-04 | 7.38 | 35.71 | 43.09 | Jun | 31.7 | 11.39 |
| 2026-05 | 9.05 | 33.76 | 42.81 | Jul | 31.8 | 11.01 |
| 2026-06 | 11.61 | 30.01 | 41.62 | Aug | 32.0 | 9.62 |
| 2026-07 | 13.37 | 27.63 | 41.00 | Sep | 29.1 | 11.90 |
| 2026-08 | 14.66 | 26.47 | 41.13 | Oct | 30.7 | 10.43 |

GW of solar photovoltaic capacity. Gap = implied total minus the STEO figure.

- **Neither side moved much.** The developers' implied 2026 total stayed between 41.0 and 43.7 GW in all ten reports; in August it was 41.1 GW, 94% of December's 43.7. The STEO's 2026 figure stayed between 29.1 and 32.0 GW; the October edition says 30.7. The gap was 9.3 to 12.8 GW in every pair and is 10.4 GW (34% of the STEO figure) in the latest.
- **The year is back-loaded.** By the August report 14.7 GW had come online, 36% of the implied total; 26.5 GW is still scheduled for September to December. Monthly additions ranged from 0.5 GW (February) to 3.0 GW (April).
- **Missed months are re-dated, not left behind.** In no report was more than 0.21 GW of 2026 solar still planned for a month that had already passed. Projects that miss their month get a later one; the year total barely changes while the year runs out.
- **The October STEO implies about 16.0 GW in September-December** (30.7 minus the 14.7 GW already online), against 26.5 GW the developers still have scheduled for those months: about 60%. Its own history agrees with the inventory: the October edition's end-June 2026 solar is 11.5 GW above end-2025, against 11.6 GW added by the June report here.
- **Wind is different.** The STEO's 2026 wind figure (9.7 in January, then 11.4-11.7 GW) stayed within 1.2 GW of the developers' implied total (10.4-12.1 GW) in all ten pairs, and in five of them was at or above it. This matches the seventh result: the STEO follows the wind schedule and discounts only solar.

## Checks (all passed)

| check | rule | result |
|---|---|---|
| C1 | December 2025 planned-for-2026 solar within 5% of 43.4 GW | 43.65 GW summer (0.6%), 43.72 nameplate (0.7%); summer used |
| C2 | at least 8 of 10 editions give end-2025 solar between 130 and 150 GW; January reproduces 139.2 / 171.3 (solar) and 160.4 / 170.1 (wind) | 10 parsed, 8 in range (September 150.1 and October 150.4 are just above it; see below); January reproduced exactly |
| C3 | added-in-2026 never falls by more than 0.5 GW between reports | it never falls |

## Predictions (2 of 5 held)

| | prediction | result | |
|---|---|---|---|
| P1 | implied 2026 solar falls by at least 4 GW from December 2025 to the latest report | 43.65 to 41.13: 2.52 GW | **missed** |
| P2 | implied total above the STEO figure in every pair | 10 of 10 | **held** |
| P3 | latest gap less than half the February gap | 10.43 against 12.15 (half would be 6.08) | **missed** |
| P4 | latest STEO figure within 4 GW of January's 32.1 | 30.7 (-1.4) | **held** |
| P5 | added by the latest report at least 40% of its implied total | 14.66 of 41.13 = 35.6% | **missed** |

We expected the developers' plan to shrink toward the STEO as the year went on. It did not. The STEO held its discount (P4) and stayed below the plan (P2), but the plan shed only 2.5 GW, so the gap barely narrowed (P1 and P3 missed). And more of the year is still ahead than we expected (P5 missed). With four months left, one of EIA's two 2026 solar numbers will be off by at least 5 GW.

## Other things seen (not pre-registered)

- **The May 2026 STEO raised its whole 2025 solar history by about 9-10 GW** (end-2025: 138.3 GW in April, 148.3 in May; end of Q1 2025: 119.7 to 128.4). The 2026 increment stayed about the same (31.3 to 30.4 GW). The table's notes give no reason we could find. That is why the end-2025 figures of the September and October editions sit just above check C2's 150 GW bound.
- The March 2026 edition's electric-power solar and wind rows are identical to February's in every quarter.
- The number of solar generators planned for 2026 fell from 537 (December) to 388 (August) while the implied capacity barely moved. These are net totals: this check does not separate projects that slipped into 2027 or were cancelled from projects that were added to 2026 or moved into it.

## Stated in advance for the rest of 2026

Written 2026-10-18, before the September 2026 EIA-860M is released. Scored with `plan_path.py` 0.1.0, unchanged, on net summer capacity.

- **Y1.** In the September 2026 report the implied 2026 solar total is within 1.5 GW of August's 41.13 GW (39.63-42.63). Basis: it moved by at most 2.3 GW between consecutive reports this year.
- **Y2.** Solar added in 2026 by the September report is at least 16.0 GW. Basis: monthly additions averaged 1.8 GW in January-August.
- **Y3.** Solar added in 2026 by the December 2026 report (EIA's first count, out about February 2027) is below 35.9 GW, that is, closer to the October STEO's 30.7 than to the August implied total of 41.13. Basis: in 2020-2024 the developers' solar plan was never met (51-87% built); 2025 was the one year the STEO came in under the final. This is a close call, stated as one.
- **Y4.** Solar added in 2026 by the December 2026 report is at least 28.0 GW (14.7 GW online by August plus half of the 26.5 GW still scheduled).

## Limits

- An implied total takes every plan at face value. Neither number is "right" until the 2026 EIA-860 final (late 2027).
- EIA-860M covers all utility-scale generators; the STEO row is the electric power sector only. For solar the difference is well under 1 GW a year.
- PUDL's changelog is a reconstruction of the monthly files; a generator that changes its id between reports can be counted twice or dropped (earlier work in this repo found this changes shares by under 0.001).
- The pairing (edition with the report two months earlier) follows the date each edition was finished. The conclusions do not rest on it: the implied total never fell below 41.0 GW and the STEO never rose above 32.0 GW in any month.

## Files

- [`plan-path-preregistration.md`](plan-path-preregistration.md): checks and predictions, published before the run.
- [`plan-path-output.md`](plan-path-output.md): the job's raw output (both sides, all pairs, checks and prediction aids).
- [`../data/plan_path.csv`](../data/plan_path.csv): one row per report, solar and wind, nameplate and summer.
- [`../tools/plan-path/`](../tools/plan-path/): `plan_path.py` 0.1.0, `steo_text.py` and the tests.

```
cd tools/plan-path
python -m unittest -v test_plan_path
pip install pandas pyarrow pypdf
python steo_text.py --data-dir=steo --out-dir=out jan26 feb26 mar26 apr26 may26 jun26 jul26 aug26 sep26 oct26
python plan_path.py --data-dir DATA --steo-dir out --out-dir out
```

`DATA` holds PUDL's `core_eia860m__changelog_generators.parquet` (downloaded if missing).
