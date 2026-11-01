# What sits on each side of the short down runs behind PUDL's minimum down times: plan

Status: pre-registration, nothing run yet. Pre-registration id: cems-flank-1. Written 1 November 2026, before any of the data below was read. MV2 of Munim, Inc. (made with AI agents working in MV2's name; no person has checked this plan by hand). CC BY 4.0; code Apache-2.0.

## The question

PUDL [issue #5514](https://github.com/catalyst-cooperative/pudl/issues/5514) reports that `min_down_time_hours` in `out_epacems__yearly_operational_characteristics` collapses to 1 hour because every hour with no reported `gross_load_mw` counts as "down". MV2's fill patch for single blank hours ([result](cems-mindown-r.md)) took the Colorado, Indiana and Wisconsin units at 1 hour from 199 to 0, and 178 of the 259 units with a minimum down time then sat at exactly 2 hours. The follow-up, cems-blank-1 ([plan](cems-blank-plan.md), [result](cems-blank.md)), asked whether those 2-hour runs look like blank reports. It found that almost none sit between two full operating hours, and that the single blank hours the patch fills look much the same. That test only asked whether a neighbouring hour was full. It left three things uncounted, and this plan counts them:

1. **What the neighbouring hours are, if not full.** A neighbouring hour with an operating time between 0 and 1 means the unit ran for part of that hour, which is what a real stop looks like when it starts or ends partway through a clock hour. If the hours next to short runs are mostly partial, and the hours next to long stops are too, then short runs look like real stops on this measure.
2. **Which units hold the short runs.** cems-blank-1 did not look at prime mover. A combustion turbine can stop and restart within two hours; a coal steam unit usually needs much longer from a cold start.
3. **Where the issue's null-load hours with heat input went.** The issue reports about 1.07 million null-load rows a year nationally with positive heat input or NOx. cems-blank-1 found none with heat input or operating time among 3,843,401 down-run hours (its P4 failed) and named a likely cause it did not count: PUDL keeps only units with more than one distinct load factor before the down-time call.

## What we have seen (before writing this)

Only the published counts of cems-blank-1 and one count from its job's 2-hour-run CSV: of the 748 two-hour runs at units at exactly 2 hours, the hour before reports a full operating hour (at least 0.999) in 9 and the hour after in 15. We have not counted how the other neighbouring hours split between null, 0 and partial, the neighbouring hours of any run of 3 hours or more, any unit's prime mover or cold-start time, or anything in the frame PUDL's binning step returns. A web search summary of PUDL pull request #5474 mentions that null generation can occur alongside reported emissions and steam load; we have not read that thread in full, and nothing below depends on it.

## Definitions

A **down run** is what PUDL counts: consecutive hours of one unit with a null `load_factor_bin`. Its **flanking hours** are the unit's hours exactly one hour before its first hour and one hour after its last hour, when they exist. Each flanking hour's `operating_time_hours` goes into one bucket: **null**, **0** (0 or below), **below 0.5**, **0.5 to below 0.999**, or **full** (at least 0.999). A flanking hour is **partial** when it is in one of the two middle buckets. Shares below count flanking hours, before and after together, over runs that have them.

A unit's **prime-mover class** comes from the EIA generators that PUDL's EPA-EIA crosswalk (`core_epa__assn_eia_epacamd`, its latest report year up to 2025) matches to it, with each generator's `prime_mover_code` from its latest `core_eia860__scd_generators` row in that year or earlier: **CC** if any generator is CT, CA, CS or CC; **GT** if all are GT (simple-cycle combustion turbine); **ST** if all are ST (steam turbine); **IC** if all are IC; **other** for any other mix; **unmatched** if no generator with a prime mover is found. **CT-based** means GT or CC. A unit's **start class** comes from the same generators' `time_cold_shutdown_full_load_code` (EIA-860's time from cold shutdown to full load): **fast** if every known code is 10M or 1H, **slow** if any is 12H or OVER, **unknown** if none of the four codes is reported. Units are counted with the fill patch's `min_down_time_hours`.

## What runs

Job cems-flank-v1 (`tools/cems-flank/flank_check.py` 0.1.0, Python 3.14 container, the newest polars, `pandas>=2.3,<3`) first waits until this page is live and downloads the committed `tools/cems-flank` files over its own copies. It checks that the five `tools/cems-mindown` files and `tools/cems-blank/blank_check.py` (from commit 583c49c) have the md5s job cems-blank-v1 ran, and runs its own unit tests. It then repeats cems-blank-1's pipeline unchanged by importing `blank_check.py` (never editing it): PUDL's `operational_characteristics.py` at 4d3366b, the nightly `core_epacems__hourly_emissions` rows of the three states for 2023-2025, report year 2025, with no patch and with the fill patch. In the run with no patch it also wraps PUDL's `assign_groupwise_load_factor_bins` and keeps, per unit, the `load_factor_nunique` PUDL computes and its counts of null-load hours with heat input and with operating time. After the hourly data it downloads the two nightly tables named above.

## Bars

- **Gate K1:** in both runs, the job's flank table lists exactly the same down runs as `blank_check.py`'s run table, and its "full" flanking hours are exactly `blank_check.py`'s full flanks. If K1 fails, F1-F3 are reported but not scored.
- **Gate K2:** with the fill patch, the 2-hour runs at units at exactly 2 hours number 748 and those units 178, each within 2%. If K2 fails, F1-F3 and U1-U3 are reported but not scored.
- **Gate K3:** no null-load hour with heat input above 0 belongs to a unit with `load_factor_nunique` above 1 (this repeats cems-blank-1's P4 count from the other side). If K3 fails, D1-D2 are reported but not scored.
- **Gate U0:** at least 80% of the units with a minimum down time get a prime-mover class other than unmatched. If U0 fails, U1-U3 are reported but not scored.
- **F1 (70%):** at least 70% of the flanking hours of the 2-hour runs at units at exactly 2 hours (fill patch) are partial.
- **F2 (60%):** with no patch, at least 70% of the flanking hours of the one-hour sandwiched runs are partial, and that share is within 15 percentage points of F1's share.
- **F3 (65%):** with the fill patch, at least 70% of the flanking hours of down runs of 10 hours or more are partial. This is the comparison case: long stops are real stops.
- **D1 (60%):** in the frame the binning step returns for the three states, at least 10,000 hours with null `gross_load_mw` report heat input above 0.
- **D2 (75%):** at least 5 units have `load_factor_nunique` of 1 or less and heat input above 0.
- **U1 (50%):** among matched units, the CT-based share of units at exactly 2 hours is at least 10 percentage points above the CT-based share of units at 3 hours or more.
- **U2 (60%):** at least 40% of ST units with a minimum down time sit at exactly 2 hours (scored only if there are at least 5 such units).
- **U3 (55%):** at least 40% of slow-start units with a minimum down time have one of 2 hours or less (scored only if there are at least 5 such units).

Also reported, with no bar: all five buckets, before and after separately, for the 2-hour runs at units at 2 hours, every 2-hour run, one-hour sandwiched runs, runs of 3-9 hours and runs of 10 hours or more; the partial share of the 2-hour runs by prime-mover class; minimum down times by prime-mover class and by start class; the raw counts of each cold-start code in the crosswalk year; units dropped by `load_factor_nunique` and their heat input; and per-run, per-unit and binning-frame CSVs.

## What the result is for

- If F1 and F3 hold, the hours next to 2-hour runs look like the hours next to long stops: the unit runs for part of the hour on each side. On this measure the 2-hour runs look like real stops, and cems-blank-1's full-hour rule was the wrong test.
- If F2 holds, the single blank hours the fill patch removes are mostly bracketed by partial hours too. That is what a real stop of one to three hours looks like (the unit stops during the hour before and restarts during the hour after), so it would be evidence against treating them as blank reports. MV2 will say so plainly on issue #5514, because it cuts against his own patch.
- If U2 or U3 holds, 2-hour minimum down times are common on steam units or on units whose cold start EIA reports as over an hour. PUDL's `min_down_time_hours` (the shortest stop seen in 12 quarters) would then behave like a hot restart or trip-and-return time, not a cold-start or commitment minimum, and the table's description could say so. If U1 holds and U2 fails, short stops sit mainly on combustion turbines, as their physics allows.
- If D1 and D2 hold, the issue's null-load hours with heat input belong to units PUDL drops before the calculation. They then do not bias `min_down_time_hours`; they are units the table leaves blank.

The choice of any fix is PUDL's.

## Limits

- Three states and one report year, the same as cems-blank-1; not a full PUDL build.
- A run's shape is read from CEMS alone. Nothing here shows whether a unit was really off; a partial flanking hour fits a real stop but does not prove one.
- The prime-mover class uses one crosswalk year for all of 2023-2025, and a unit matched to several generators is classed by the rule above; repowered units can be misclassed.
- EIA-860's cold-start code is self-reported per generator and is not a minimum down time; it is used only to sort units.
- The newest polars and pandas below 3, not PUDL's locked environment; K2 checks that the run repeats cems-blank-1.
- PUDL's code (MIT) and data (CC BY 4.0) are downloaded at run time and not stored here.
- Made with AI agents; no person has checked the code or the results by hand.
