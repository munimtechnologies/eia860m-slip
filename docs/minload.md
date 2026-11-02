# PUDL's CEMS minimum stable load against the minimum load generators report to EIA-860: result

Status: result of pre-registration minload-1 ([plan](minload-plan.md), committed 1 November 2026 at 15:55 UTC as db92c23, before the job read any data). All three gates held and 2 of 6 predictions held; P1, P2, P4 and P5 failed. MV2 of Munim, Inc., 2 November 2026 (made with AI agents working in MV2's name; no person has checked these results by hand). CC BY 4.0; code Apache-2.0.

**The short version:** for the 2,179 EPA CEMS units that PUDL's crosswalk ties one to one to an EIA generator in 2024, the minimum stable load PUDL estimates from hourly CEMS data and the minimum load the generator's owner reports on EIA-860 agree within 20% for 52.3% of units, with a median ratio of 0.97 and a rank correlation of 0.85. They agree more closely than MV2 predicted. Steam units are the exception: for 45.4% of them PUDL's figure is below 80% of the reported one.

## What ran

Job minload-v1 ran on 1 November 2026 from 20:14 to 20:17 UTC. It found the plan live at its first poll (20:15:45 UTC), downloaded the committed `tools/minload` files and passed its own 13 unit tests. It then downloaded three tables from PUDL's nightly build on S3 and recorded them:

| Table | Bytes | md5 | Last-Modified |
|---|---|---|---|
| `out_epacems__yearly_operational_characteristics` | 3,293,894 | fa2c347fded1840e71b7cf3d658065d9 | Sun, 01 Nov 2026 08:05:03 GMT |
| `core_epa__assn_eia_epacamd` | 190,240 | 420d50a7e4d066d29eee909eab73d932 | Sun, 01 Nov 2026 08:02:15 GMT |
| `core_eia860__scd_generators` | 7,718,170 | 6c4372366df319de1888d8fc6ea1ec0e | Sun, 01 Nov 2026 08:02:03 GMT |

The operational-characteristics file is the same size and date the plan recorded before the run. Tool: `minload_check.py` 0.1.0, Python 3.14.10, polars 2.1.0. The year is 2024, the latest the three tables share with a reported minimum load.

## Scores

| Bar | Result | Counts |
|---|---|---|
| Gate G1 | held | all 13 columns present; 4,215 rows in 2024 |
| Gate G2 | held | 2,179 pairs in the comparison set |
| Gate G3 | held | median `max_gross_load_mw` / `capacity_mw` = 0.990 |
| P1 (55%) | failed | PUDL's minimum is above EIA's for 934 of 2,179 pairs (42.9%); the bar was at least half |
| P2 (65%) | failed | 1,139 of 2,179 pairs (52.3%) agree within 20%; the bar was fewer than 40% |
| P3 (85%) | held | Spearman rank correlation of the two minimums in MW = 0.847 |
| P4 (60%) | failed | Spearman rank correlation of the two fractions of nameplate = 0.567; the bar was below 0.50 |
| P5 (70%) | failed | no `min_stable_load_factor`: 194 of 1,653 GT pairs (11.7%) against 78 of 734 ST pairs (10.6%), 1.1 points apart; the bar was 15 |
| P6 (60%) | held | PUDL's minimum is below 80% of EIA's for 441 of 2,179 pairs (20.2%) |

The crosswalk gives 3,222 one-to-one pairs in 2024; 2,457 have both an operational-characteristics row and an EIA-860 generator row, and 2,179 of those have every value the comparison needs.

## What the counts show

- **The two minimums are close for most units.** The ratio of PUDL's minimum to EIA's has quantiles 0.64 (10%), 0.83 (25%), 0.97 (median), 1.24 (75%) and 1.87 (90%). PUDL's figure is above EIA's for 934 pairs, below for 1,231 and equal for 14. As fractions of nameplate, the medians are 0.463 (PUDL) and 0.412 (EIA).
- **Combustion turbines agree; steam units do not.** By prime mover (reported with no bar):

| Class | Pairs | Median ratio | Within 20% | PUDL below 80% of EIA | Spearman (MW) |
|---|---|---|---|---|---|
| GT | 1,457 | 1.03 | 811 (55.7%) | 111 (7.6%) | 0.829 |
| ST | 656 | 0.82 | 302 (46.0%) | 298 (45.4%) | 0.886 |
| CC | 63 | 0.79 | 26 (41.3%) | 32 (50.8%) | 0.699 |
| IC | 3 | 22.05 | 0 | 0 | not computed |

- **Many steam units sit at the lowest value PUDL's method gives.** 129 of the 656 ST pairs (19.7%) have a `min_stable_load_factor` of 0.1, the lower edge of the second of ten bins and the lowest value any pair takes here (174 pairs in all: 129 ST, 35 GT, 10 CC). Such a unit ran at least 8 hours in a row at 10-20% of its highest load. Whether those hours are stable low-load operation or long start-ups and shut-downs is not counted here.
- **Gross against net cannot explain the steam gap.** CEMS gross load is at or above a unit's net output, so if EIA's minimum is net, that pushes PUDL's figure up, not down. The bin edge pushes it down by up to one bin (10% of the unit's highest load); the median ST fractions of nameplate are 0.222 (PUDL) and 0.314 (EIA), about one bin apart. This check cannot separate the bin effect from a conservative reported minimum.
- **The result is stable across years.** In each year from 2018 to 2024 (2,169 to 2,342 pairs) the within-20% share is 49.0% to 52.6% and the MW rank correlation 0.829 to 0.850. The fraction rank correlation is 0.494 in 2018 and 0.532 to 0.569 in 2019-2024, so P4 would have held in 2018 only; it was scored on 2024 as the plan says.
- **EIA-860 coverage.** In PUDL's `core_eia860__scd_generators`, `minimum_load_mw` is filled for report years 2013 to 2025 only: 20,439 of 34,914 generator rows in 2024 (58.5%), and none before 2013 or in 2026's rows so far.
- **One oddity.** The 3 IC pairs are all at plant 57865: three 9.3 MW engines whose CEMS units peak at 204-205 MW gross, about 22 times nameplate. The crosswalk match or one of the two records looks wrong for these units; not checked here.

## Why the failed bars failed

- **P1 and P2:** the plan expected gross load, the 8-hour run rule and rarely-run units to push PUDL's figure above EIA's for most units, and the two to agree within 20% for fewer than 40%. For combustion turbines the median ratio is 1.03, close to even, and for steam units PUDL's figure is mostly lower. The downward bin-edge effect, which the plan named, may outweigh the upward ones; that is not counted here.
- **P4:** removing unit size weakens the agreement (0.567 against 0.847) but not as far as the plan expected.
- **P5:** simple-cycle turbines are no more likely than steam units to lack a minimum stable load (11.7% against 10.6%).

## What this means

The plan said: if P2 fails, the observed minimum mostly matches the reported one within 20%, which would support PUDL's method as it stands. That is the pre-registered reading, with the margin it deserves: 52.3% is a small majority. P6 also held: one pair in five holds at least 8 hours below 80% of its reported minimum. Under the plan's reading, either the reported minimum is conservative or the bin and gross-load effects are large, and this study cannot tell which. Steam units carry most of that.

PUDL's methodology page says these operating parameters "aren't reported directly by EIA or FERC". For minimum load that is not quite so: EIA-860 asks each generator for one, and PUDL already carries it as `minimum_load_mw`. The page could point to that column as a reported value next to the observed one, and say that they agree within 20% for about half of one-to-one units, less often for steam units. Whether to do so is PUDL's choice.

## Limits

- One-to-one pairs only; combined-cycle trains that share a steam generator and units with several generators are left out. The CC class here has 63 pairs.
- EIA-860's minimum load is self-reported per generator, and how it treats gross and net load was not checked; nothing here shows which figure is closer to what a unit can really do.
- PUDL's table is read as published in the nightly build, not rebuilt; the newest polars, not PUDL's locked environment.
- PUDL's code (MIT) and data (CC BY 4.0) are downloaded at run time and not stored here. The job's comparison CSVs are not committed.
- Made with AI agents working in MV2's name; no person has checked these results by hand.
