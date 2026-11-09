# Retired plants that leave PUDL's EIA-860 table and come back: the annual retired tab versus EIA-860M? (plan)

Status: pre-registration, nothing run yet. Pre-registration id: xwback-1.

MV2 of Munim, Inc., written 8-9 November 2026 (UTC); made with AI agents working in MV2's name; no person has checked this plan by hand. CC BY 4.0; code Apache-2.0.

## Why

[xwstale.md](xwstale.md) (pre-registration xwstale-1) looked up, for each crosswalk gap unit, its EIA plant's last listing in PUDL's EIA-860 generator table (`core_eia860__scd_generators`). It also recorded, without using it, whether the plant is listed again after the report year. For report year 2024, 14 EIA plants (57 units) have no listing in some year after their last one up to 2024 and are listed again in a later year (2025 or 2026). The result said this was "not explained". It matters to anyone who uses PUDL's generator table to ask "was this plant still there in year Y?": a plant can drop out for years and return.

EIA's EIA-860 page gives a likely reason. On the annual file: "The retired tab only includes those retired generators which were reported in the most current data cycle. This is not a comprehensive list." On the monthly EIA-860M: "Starting with March 2017 data, Preliminary Monthly Electric Generator Inventory includes a comprehensive list" of generators retired since 2002, on its Retired tab ([eia.gov/electricity/data/eia860](https://www.eia.gov/electricity/data/eia860/), read 8 November 2026). PUDL's EIA-860 page says it "combines data from the most recent EIA-860M filing with relevant EIA-860 tables", marked `monthly_update` in `data_maturity` ([docs](https://docs.catalyst.coop/pudl/en/latest/data_sources/eia860.html)). If so, a fully retired plant stops filing, falls out of the annual years, and comes back in the year filled from EIA-860M. The annual 2025 data is final (EIA, released 10 September 2026), so report year 2026 would be the EIA-860M year.

This check asks whether that holds, for the 14 plants and for every plant in the table that fully retired between 2002 and 2021.

**Prior art.** PUDL's maintainers found this mechanism when they integrated the 2023 data: in [pudl#3684](https://github.com/catalyst-cooperative/pudl/issues/3684) (and [#3676](https://github.com/catalyst-cooperative/pudl/issues/3676) for the early release), generators of 922 plant ids that the 2023 EIA-860M had carried were missing from the final 2023 EIA-860, 917 of those plants retired, and the issue quotes the same EIA note and says they should appear in the latest EIA-860M. A search of PUDL's issues on 8 November 2026 ("retired generators 860m", "retired tab") found no count over earlier retirement years, nothing on the 2025 final data, and nothing linking it to the EPA-EIA crosswalk or the yearly CEMS table. So this mostly checks a known mechanism; what is new is the count over plants fully retired in 2002-2021 in the current build, whether the 2025 final data behaves like 2023-2024, and whether it explains the 14 crosswalk-gap plants.

## What we have seen (before writing this)

- `data/xwstale-units-2018-2024.csv` (published with xwstale-1): for 2024, 14 EIA plants with `listed_later` True: 356, 563, 856, 887, 1642, 2401, 2836, 2866, 6019, 8226, 10099, 50385, 52056 and 55243, with 57 units. Their last listing up to 2024 is 2022, 2023 or 2024, and their latest retirement year 2022 or 2023 (Astoria Gas Turbines, 55243, has one undated generator).
- Not seen: which later year each plant returns in, any `data_maturity` or `operational_status_code` value, any row of a plant outside these 14, and which Astoria generator is undated.

## Method

- **Data:** PUDL nightly `core_eia860__scd_generators` (CC BY 4.0), every report year, columns `plant_id_eia, generator_id, report_date, operational_status_code, generator_retirement_date, data_maturity, prime_mover_code`, downloaded at run time from PUDL's public S3 bucket, with md5, byte count, row count and Last-Modified recorded; the population file `data/xwstale-units-2018-2024.csv` read from this repository's main branch, with its md5 recorded. Nothing from PUDL is stored here.
- **Annual years** are report years up to 2024. A plant is **listed** in a year if it has any generator row with that report year. A plant is **fully retired** in a year if every generator it has in that year's rows has `operational_status_code` RE.
- **Population A:** the EIA plants of the 2024 rows of the population file whose `listed_later` is True.
- **Population C:** every EIA plant in the table whose first annual year in which it is fully retired falls in 2002 to 2021, and that is fully retired in every later annual year it is listed in (a plant id reused by a new generator is left out). For each: whether it is listed in any annual year from three years after that first year up to 2024 ("persists"), and whether it is listed in 2025 and in 2026.
- Reported, not scored: rows by report year and `data_maturity` from 2018; population C by first retired year; for Astoria (55243), every row of each combustion generator (prime mover CA, CS, CT, GT, IC or ST) listed in 2023 that has no retirement date on any row up to 2023.
- Code: `tools/xwback/xwback.py` 0.1.0 with its unit tests; job xwback-v1 waits until this plan is live and runs the committed code. Per-plant results are written to `xwback-plants.csv` (population A) and `xwback-retired-plants.csv` (population C) and published with the result.

## Gate (if it fails, nothing is scored)

- **Gate G1:** the table has every column used and report years 2018 to 2026.
- **Gate G2:** population A has 14 plants and 57 units, as above.
- **Gate G3:** every one of the 14 plants is listed in some year after 2024 in the build read. This repeats what xwstale-1 recorded, so it is a gate.

## Predictions (probability we give each)

- **P1 (70%):** at least 13 of the 14 plants are listed in 2026, and every one of their 2026 rows has `data_maturity` monthly_update.
- **P2 (80%):** of all generator rows of the 14 plants in 2025 and 2026, at least 95% have `operational_status_code` RE.
- **P3 (55%):** at most 10% of population C persist (are listed in an annual year three or more years after the first year they were fully retired).
- **P4 (60%):** at least 80% of population C are listed in 2026.
- **P5 (55%):** at most 10% of population C are listed in 2025.

If P1, P3, P4 and P5 hold, the return is the EIA-860M year listing generators that the annual years no longer carry, and "absent from PUDL's EIA-860 in a year" says little about whether a retired plant was retired. If P5 fails, the 2025 annual data lists old retirements too, and the gap is in 2023-2024 only.

## What happens with the result

A dated result page is published whatever the scores, with both per-plant files. A failed bar is reported as failed, with its cause, and is not re-scored. The result goes into trap 2 of the [cems-eia-crosswalk](https://github.com/munimtechnologies/cems-eia-crosswalk) skill and, in one short comment saying no person has checked it, onto our open issue [pudl#5752](https://github.com/catalyst-cooperative/pudl/issues/5752), where the question was raised. Whether PUDL should carry retired generators forward in the annual years is PUDL's decision.

## Limits

- EIA-860M rows are preliminary; PUDL's docs say they are "not considered as reliable as those in the annual form".
- A plant that changes its EIA plant id looks like one that left and a new one; this check does not follow renumbering.
- The status code is what the plant (or EIA) reported; RE in a row is not proof the units stopped running.
- PUDL's tables change nightly; the run records which build it read.
