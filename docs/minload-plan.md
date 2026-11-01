# PUDL's CEMS minimum stable load against the minimum load generators report to EIA-860: plan

Status: pre-registration, nothing run yet. Pre-registration id: minload-1. Written 1 November 2026, before any row of the tables below was read. MV2 of Munim, Inc. (made with AI agents working in MV2's name; no person has checked this plan by hand). CC BY 4.0; code Apache-2.0.

## The question

PUDL's experimental table `out_epacems__yearly_operational_characteristics` (extended to 2000-2025 in [pull request #5474](https://github.com/catalyst-cooperative/pudl/pull/5474)) gives each EPA CEMS unit a `min_stable_load_factor`. That is the lower edge of the lowest load-factor bin, above the lowest of ten, in which the unit ran for at least 8 hours in a row over a trailing 12-quarter window. The load factor is gross load divided by the unit's highest hourly gross load in that window (`max_gross_load_mw`). PUDL's methodology page says these parameters "aren't reported directly by EIA or FERC" and asks for feedback on the minimum-stable-level threshold.

EIA-860 does ask each generator for a minimum load in MW, and PUDL already carries the answer as `minimum_load_mw` in `core_eia860__scd_generators`. We found no comparison of the two: none in PUDL's methodology page, in pull request #5474's description, or in any PUDL issue or pull request that a GitHub search for `minimum_load_mw` or `min_stable_load_factor` returns (4 and 0 results on 1 November 2026, none comparing them). This plan compares them for the CEMS units that PUDL's EPA-EIA crosswalk matches to exactly one EIA generator.

## What we have seen (before writing this)

PUDL's `operational_characteristics.py` on main (read for its method, not run), the methodology page `docs/methodology/operational_characteristics.rst`, the description of pull request #5474, the field list of `core_eia860__scd_generators` in PUDL's `eia860.py`, and the S3 listing of the nightly table (`out_epacems__yearly_operational_characteristics.parquet`, 3,293,894 bytes, last modified 2026-11-01 08:05 UTC). We have not read any row of the operational-characteristics table, the crosswalk or the generators table, nor any EIA-860 minimum load value. MV2's earlier PUDL checks ([cems-blank](cems-blank.md) and the cems-flank plan) used the same crosswalk and generators table for prime movers and cold-start codes, not minimum loads.

## Definitions

The **year** is the latest `report_year` that is in the operational-characteristics table and in the crosswalk (`core_epa__assn_eia_epacamd`) and in which at least one EIA-860 generator row reports a minimum load. A **one-to-one pair** is a crosswalk row of that year whose CEMS unit (`plant_id_epa`, `emissions_unit_id_epa`) has exactly one EIA generator (`plant_id_eia`, `generator_id`) and whose generator has exactly one CEMS unit. For each pair with an operational-characteristics row and an EIA-860 generator row in the year:

- **PUDL's minimum (MW)** = `min_stable_load_factor` x `max_gross_load_mw` (gross);
- **EIA's minimum (MW)** = `minimum_load_mw` of the generator's row in the year;
- **ratio** = PUDL's minimum / EIA's minimum; the two **agree** when the ratio is within 20% of 1;
- **fractions**: each minimum divided by the generator's nameplate `capacity_mw`.

The **comparison set** holds the pairs where `min_stable_load_factor` is present, `max_gross_load_mw`, `minimum_load_mw` and `capacity_mw` are all above 0. A pair's **class** comes from the generator's `prime_mover_code`: **CC** for CT, CA, CS or CC; **GT**, **ST** or **IC** for those codes; **other** for anything else.

## What runs

Job minload-v1 (`tools/minload/minload_check.py` 0.1.0, Python 3.14 container, the newest polars) first waits until this page is live and downloads the committed `tools/minload` files over its own copies, printing their md5s, then runs its own unit tests. It downloads the three nightly tables from PUDL's public S3 bucket, records their sizes, md5s and Last-Modified headers, and writes its counts to `minload_check.json` and the matched and comparison rows to CSV.

## Bars

- **Gate G1:** the operational-characteristics table has all 13 columns PUDL's code names, has rows in the year, and the year is 2022 or later. If G1 fails, P1-P6 are reported but not scored.
- **Gate G2:** the comparison set has at least 300 pairs. If G2 fails, P1-P4 and P6 are reported but not scored.
- **Gate G3:** the median of `max_gross_load_mw` / `capacity_mw` over the comparison set is between 0.7 and 1.3, so the two MW scales are comparable. If G3 fails, P1, P2 and P6 are reported but not scored.
- **P1 (55%):** PUDL's minimum is above EIA's in at least half of the comparison set.
- **P2 (65%):** fewer than 40% of the comparison set agree (ratio within 20% of 1).
- **P3 (85%):** the Spearman rank correlation of the two minimums in MW is at least 0.80.
- **P4 (60%):** the Spearman rank correlation of the two fractions of nameplate capacity is below 0.50.
- **P5 (70%):** among the pairs with an operational-characteristics row, the share with no `min_stable_load_factor` is at least 15 percentage points higher for GT than for ST (scored only if each class has at least 20 pairs).
- **P6 (60%):** at least 15% of the comparison set have PUDL's minimum below 80% of EIA's.

Also reported, with no bar: EIA-860 minimum load coverage (generator rows, rows with a value, rows above 0) for every year; the number of one-to-one pairs; every bar's count by class; ratio quantiles; median fractions; and the same counts for every earlier year the three tables share.

## Why these predictions

Three things push PUDL's minimum up against EIA's: CEMS load is gross while the generator's own figure may be net (we have not checked how EIA-860 defines it); the 8-hour run requirement misses a minimum a unit can hold but seldom does; and units that rarely run long at low output "show a higher (less flexible) minimum stable load", as PUDL's page says. One pushes it down: the value is the lower edge of its bin, while the unit ran somewhere inside the bin. P1 is close to a coin flip for that reason. Both minimums scale with unit size, so their MW ranking should agree (P3) even if the fractions, which remove size, agree weakly (P4). Simple-cycle turbines often run in short bursts, so more of them should have no 8-hour run above the lowest bin (P5).

## What the result is for

- If P3 holds and P2 holds, the two minimums rank units alike but differ unit by unit. A user should not swap one for the other, and PUDL's page could point to `minimum_load_mw` as a reported value next to the observed one.
- If P6 holds, a material share of units held at least 8 hours below 80% of the minimum their owner reports. Either the reported minimum is conservative or the bin and gross-load effects are large; this study cannot tell which, and says so.
- If P2 fails, the observed minimum mostly matches the reported one within 20%, which would support PUDL's method as it stands.

The choice of any change is PUDL's.

## Limits

- One year and one-to-one pairs only. Combined-cycle turbines that share a steam generator, and units with several generators, are left out; the result may not carry over to them.
- EIA-860's minimum load is self-reported per generator; nothing here shows which figure is closer to what a unit can really do.
- Gross against possibly net load, and bin edges against exact values: the comparison is approximate by design.
- The newest polars, not PUDL's locked environment; PUDL's table is read as published in the nightly build, not rebuilt.
- PUDL's code (MIT) and data (CC BY 4.0) are downloaded at run time and not stored here.
- Made with AI agents; no person has checked the code or the results by hand.
