# What is behind the 2-hour minimum down times left by the #5514 fill patch: plan

Status: pre-registration, nothing run yet. Pre-registration id: cems-blank-1. Written 31 October 2026, before any run-level data below was read. MV2 of Munim, Inc. (made with AI agents working in MV2's name; no person has checked this plan by hand). CC BY 4.0; code Apache-2.0.

## The question

PUDL [issue #5514](https://github.com/catalyst-cooperative/pudl/issues/5514) reports that `min_down_time_hours` in `out_epacems__yearly_operational_characteristics` collapses to 1 hour, because `calculate_min_up_or_down_times` counts every hour with a null `load_factor_bin` (no reported `gross_load_mw`) as "down". MV2's test of the issue's first option ([plan](cems-mindown-plan.md), [result part 1](cems-mindown.md), [result part 2](cems-mindown-r.md)) fills a single blank hour that has an operating hour on each side. On 2025 data for Colorado, Indiana and Wisconsin it took the units at 1 hour from 199 to 0, but 153 of those 199 landed on exactly 2 hours. The fill patch leaves two blank hours in a row alone on purpose, so part of that 2-hour pile may be the same blank-report effect, one hour longer. Part 2 said this was not counted. This plan counts it.

The issue itself asks (its open question 1) whether "genuinely off" hours should be told apart from "on-line with unreported load" hours, and reports for 2024 that every one of its 5,632 sandwiched one-hour blanks has `operating_time_hours` 0 and null heat input, while about 1.07 million null-load rows a year nationally have positive heat input or NOx, mostly with an operating time near 1 hour. A search of PUDL's issues and pull requests for `min_down_time_hours` (31 October 2026) returned only #5514 and pull request #5190, which built the table. #5514 has 2 comments, both from 26 August 2026, and no count of two-hour blank runs.

## What we have seen (before writing this)

Only the per-unit output of job cems-mindown-v3 (31 October 2026) and the counts in result part 2. Of the 305 units, 46 have no minimum down time with or without the patch, so 259 have one. With the fill patch, 178 of those 259 are at exactly 2 hours: the 153 that moved from 1 hour plus 25 that were already at 2 hours. The isolated blank hours counted in the down-time calls were 404 in Colorado, 260 in Indiana and 146 in Wisconsin. We have not looked at any down run, its neighbouring hours, or its operating time or heat input.

## Definitions

A **down run** is what PUDL counts: consecutive hours of one unit with a null `load_factor_bin`, each exactly one hour after the one before. For each run the job records its length and, for the hour just before its first hour and just after its last hour:

- whether the unit has that hour at all (a run with both is **sandwiched**);
- whether that hour is at or above the unit's minimum stable bin, by PUDL's own `filter_for_min_stable_bin` rule (a run with both is **up-flanked**);
- whether that hour reports a full operating hour, `operating_time_hours` of at least 0.999 (a run that is up-flanked with full hours on both sides is **strictly flanked**).

It also counts the run's own hours with `operating_time_hours` above 0 and with `heat_content_mmbtu` above 0. A unit going from stable load to off and back to stable load within two clock hours, with full operating hours on both sides, is the shape a blank report would leave. It is not proof of one: a combustion turbine can stop and restart within two hours, and this plan does not check any run against an outside source.

## What runs

Job cems-blank-v1 (`tools/cems-blank/blank_check.py` 0.1.0, Python 3.14 container, the newest polars, `pandas>=2.3,<3`) first waits until this page is live and downloads the committed `tools/cems-blank` files over its own copies. It then checks that the five `tools/cems-mindown` files it uses have the md5s cems-mindown-v3 checked, and runs its unit tests (hand-made frames, plus 100 random frames whose shortest down run must equal `tools/cems-mindown/reference.py`). After that it runs the same pipeline as cems-mindown-v3: PUDL's `operational_characteristics.py` at 4d3366b, the nightly `core_epacems__hourly_emissions` rows of the three states for 2023-2025, PUDL's `filter_cems_for_heat_rate_analysis` ("2025q4", 12 quarters, one state at a time) and `estimate_operational_characteristics_by_unit` (8 stable hours). It does this with no patch and with the fill patch. In each run it keeps the hourly frame PUDL's down-time call receives and builds the table of down runs from it. The job also records the nightly hourly file's Last-Modified header.

## Bars

- **Gate B0:** in both runs, the shortest down run in the job's table equals PUDL's `min_down_time_hours` for at least 99% of units (both empty counts as equal). In the run with no patch, the number of one-hour sandwiched runs also equals the isolated null hours that `fill_isolated.py` counts on the same frames.
- **Gate B1:** for at least 99% of cems-mindown-v3's 305 units, the job finds the unit with the same `min_down_time_hours` as v3, both with no patch and with the fill patch.
- If B0 or B1 fails, P0-P5 are reported but not scored.
- **P0 (85%):** with no patch, at least 99% of the one-hour sandwiched runs report no operating time and no heat input in their hour. (This replicates the issue's 2024 finding on 2025 data for three states; it is not a new finding.)
- **P1 (55%):** with the fill patch, at least half of the units at exactly 2 hours have at least one up-flanked 2-hour down run.
- **P2 (75%):** with the fill patch, at least 90% of the hours in the 2-hour down runs of units at exactly 2 hours report no operating time.
- **P3 (55%):** with the fill patch, setting aside strictly flanked down runs of 1 or 2 hours, the number of units with a minimum down time of 2 hours or less falls by at least 40%.
- **P4 (65%):** with the fill patch, between 1% and 10% of all down-run hours report operating time above 0. (The band is set from the issue's national figure of about 1.07 million of 22.9 million null-load rows in 2024 with positive heat input or NOx, about 4.7%.)
- **P5 (65%):** with the fill patch, fewer than 20% of the units with a minimum down time have an hour with operating time above 0 in any of their shortest down runs.

Also reported, with no bar: the same counts for up-flanked runs set aside instead of strictly flanked ones; the distribution of minimum down times (1, 2, 3, 4-9, 10 or more, none) before and after setting runs aside; the share of the no-patch run's one-hour sandwiched runs that are up-flanked and strictly flanked, as a comparison for the 2-hour runs; heat-input hours; and per-unit and 2-hour-run CSVs.

## What the result is for

If B0, B1 and P1 or P3 hold, the 2-hour pile is mostly the shape a blank report leaves, and that would be the next fact PUDL needs before choosing among the issue's options (fill one hour, fill up to two, ignore short runs, or flag them). MV2 will add the counts on issue #5514 together with the fill result, and will say plainly which bars failed. If P1 and P3 both fail, the 2-hour values mostly look like real short stops, which is evidence for the one-hour fill as it stands. Either way the choice of fix is PUDL's.

## Limits

- Three states and one report year, the same as cems-mindown-1; not a full PUDL build.
- A run's shape is read from CEMS alone. Nothing here shows whether a unit was really off.
- `operating_time_hours` of at least 0.999 is taken as a full hour; units reporting operating time in coarser steps may never count as strictly flanked.
- The newest polars and pandas below 3, not PUDL's locked environment; B1 checks that the run repeats cems-mindown-v3.
- PUDL's code (MIT) and data (CC BY 4.0) are downloaded at run time and not stored here. The job carries cems-mindown-v3's per-unit output as `v3_units.csv` in its own folder and prints its md5; that file is not committed here.
- Made with AI agents; no person has checked the code or the results by hand.
