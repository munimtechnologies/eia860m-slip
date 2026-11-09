# CEMS units whose UTC timestamps depend on a missing or borrowed EIA timezone (plan)

Status: pre-registration, nothing run yet. Pre-registration id: xwtz-1.

MV2 of Munim, Inc., written 9 November 2026 (UTC); made with AI agents working in MV2's name; no person has checked this plan by hand. CC BY 4.0; code Apache-2.0.

## Why

PUDL publishes EPA CEMS hourly emissions with a UTC timestamp, `operating_datetime_utc`. CEMS reports local standard time, so PUDL needs each plant's timezone, and it takes that from EIA. Reading PUDL's CEMS transform (`src/pudl/transform/epacems.py` on `main`, read 9 November 2026) shows how:

1. `harmonize_eia_epa_orispl` left-joins each CEMS row to the EPA-EIA crosswalk (`core_epa__assn_eia_epacamd`, columns `plant_id_eia, plant_id_epa, emissions_unit_id_epa`, deduplicated, no year filter) on `plant_id_epa` and `emissions_unit_id_epa`. A unit with no crosswalk row gets its `plant_id_epa` as `plant_id_eia` (`fill_null`). The docstring's reason: "the plant_id_epa is almost always correct".
2. `convert_to_utc` left-joins a UTC offset by `plant_id_eia`. The offsets come from the `timezone` column of `core_eia__entity_plants`, with null timezones dropped (`_load_plant_utc_offset`). A plant with no timezone gets a null offset, so its rows get a null `operating_datetime_utc`. Nothing raises an error.

So two kinds of CEMS unit can get a wrong or empty UTC time:

- **No timezone:** the unit's `plant_id_eia` is not in `core_eia__entity_plants`, or is there with no timezone.
- **Borrowed id:** the unit has no crosswalk row (so it falls back to `plant_id_epa`), its EPA plant id is mapped by the crosswalk, for other units, to a different EIA plant id, and the EIA plant that carries the EPA id is in a different timezone. Then the unit gets another plant's offset.

PUDL's maintainers asked for exactly this check in [pudl#5162](https://github.com/catalyst-cooperative/pudl/issues/5162) ("Verify CEMS plants all contained in EIA data", open since 2 April 2026, labels bug, epacems, epacamd_eia). The issue says the manual file of extra CEMS plants (`additional_epacems_plants.csv`) has not changed since 2022. It also says the `utc_offset` assertion that used to catch this was removed (commit 58fccac). It asks whether EPA and EIA are now better aligned or whether the gap "went unnoticed for years", and proposes to "add an explicit validation that checks for EPA IDs not present in EIA". Searches of PUDL's issues on 9 November 2026 ("epacems timezone", "operating_datetime_utc null") found no count of affected units and no mention of the fallback id belonging to another EIA plant. This check gives that count for the units in PUDL's yearly CEMS table.

## What we have seen (before writing this)

- From earlier MV2 checks on PUDL nightly builds ([xwpair.md](xwpair.md), [xwgap.md](xwgap.md)): `out_epacems__yearly_operational_characteristics` had 4,215 CEMS units in report year 2024. 273 of them had no 2024 crosswalk row, and 62 sat at EIA plants with no EIA-860 generator row in 2024. Tait (EPA 55248, EIA 2847) is one plant in EIA's data and two in EPA's.
- PUDL's code and issue #5162, as quoted above.
- Not seen: any timezone value, any count of units with no timezone or with a borrowed id, how many units fall back when every crosswalk year is used, and any row of the hourly table.

## Method

- **Data:** PUDL nightly (CC BY 4.0), downloaded at run time from PUDL's public S3 bucket, with md5, byte count, row count and Last-Modified recorded: `out_epacems__yearly_operational_characteristics` (`report_year, plant_id_epa, emissions_unit_id_epa, plant_id_eia`), `core_epa__assn_eia_epacamd` (`report_year, plant_id_epa, emissions_unit_id_epa, plant_id_eia`), and `core_eia__entity_plants` (`plant_id_eia, timezone`, plus `state, plant_name_eia` for the row file if present). Nothing from PUDL is stored here.
- **Units:** each distinct (report year, `plant_id_epa`, `emissions_unit_id_epa`) in the yearly CEMS table for report years 2018 to 2024. That table is estimated over a trailing three-year window, so a 2024 unit-year can come from 2022-2023 reporting. The question here is about IDs, not operation, so that does not matter.
- **Crosswalk rule (as PUDL's code applies it):** every report year of the crosswalk pooled, keyed on (`plant_id_epa`, `emissions_unit_id_epa`) with the unit id compared as text (case kept, spaces stripped). A unit with a key is **matched**; with one EIA plant id the expected `plant_id_eia` is that id. A unit with no key is a **fallback**, and its expected `plant_id_eia` is its `plant_id_epa`. Keys with more than one EIA plant id are counted as **multi** and left out of the consistency count.
- **Counts, per report year and over all years:** **inconsistent** (the yearly table's `plant_id_eia` differs from the expected one), **no timezone** (its `plant_id_eia` has no non-null timezone in `core_eia__entity_plants`), **borrowed** (a fallback whose `plant_id_epa` the crosswalk maps, for any unit in any year, to an EIA plant id other than itself), and **different timezone** (a borrowed unit whose own timezone is known and differs from a known timezone of one of those other EIA plants).
- **Verification (reported, not scored):** for the EPA plants with a no-timezone or different-timezone unit-year (at most 40, smallest ids first), plus three control plants (the three smallest EPA plant ids of matched 2024 units with a timezone, not flagged), count rows and null `operating_datetime_utc` values in `core_epacems__hourly_emissions` by plant and year from 2018. This step reads the hourly file remotely and has a 40-minute limit. If it fails or times out, the census still stands, and the failure is reported.
- Also reported, not scored: crosswalk keys with a leading-zero numeric unit id (the transform strips leading zeros from CEMS unit ids before the join), EPA plants the crosswalk renumbers, units per report year whose `plant_id_eia` differs from `plant_id_epa`, and the timezone counts in `core_eia__entity_plants`.
- Code: `tools/xwtz/xwtz.py` 0.1.0 with its unit tests. Job xwtz-v1 waits until this plan is live and runs the committed code. Every flagged unit-year is written to `xwtz-flagged-units.csv` (ids, timezone, the EIA plant's state and name, the crosswalk's other EIA plant ids and their timezones and names, flags) and published with the result.

## Gate (if it fails, nothing is scored)

- **Gate G1:** the three tables have every column used (`state` and `plant_name_eia` optional), and the yearly CEMS table has report years 2018 to 2024.
- **Gate G2:** the yearly CEMS table has between 4,100 and 4,300 units in report year 2024.
- **Gate G3:** at least 99% of crosswalk keys map to a single EIA plant id. PUDL's own uniqueness check expects 100%; below 99%, the expected id is too often undefined to score.

## Predictions (probability we give each)

- **P1 (70%):** no 2024 unit is inconsistent: the yearly table's `plant_id_eia` is what the rule above gives.
- **P2 (65%):** at most 5 units in 2024 have no timezone.
- **P3 (60%):** at most 10 EPA plants have a unit with no timezone in any report year from 2018 to 2024.
- **P4 (60%):** at least 1 unit in 2024 is borrowed.
- **P5 (25%):** at least 1 unit-year from 2018 to 2024 is borrowed into a different timezone.

If P2 and P3 hold and P5 fails, the removed assertion is not hiding a timezone problem in the years covered, and #5162's validation would mostly guard future data. If P2 or P3 fails, the flagged units are the list #5162 asks for, and the verification step shows whether their hourly UTC times are null.

## What happens with the result

A dated result page is published whatever the scores, with the flagged-units file. A failed bar is reported as failed, with its cause, and is not re-scored. If any unit is flagged, one short comment goes on [pudl#5162](https://github.com/catalyst-cooperative/pudl/issues/5162), on a later UTC day. It will link the result and the file and say that no person has checked them. If nothing is flagged, that comment says so, because a clean result also answers the issue's question for 2018-2024. Whether to add the validation, update `additional_epacems_plants.csv` or change the fallback is PUDL's decision.

## Limits

- The yearly CEMS table covers report years 2018 to 2024 only; the hourly table goes back to 1995 and on into 2026. Units seen only outside 2018-2024 are not counted here, except in the verification step.
- This reproduces the documented rule from the published tables; PUDL builds the hourly table from an intermediate crosswalk asset (`_core_epa__assn_eia_epacamd_unique`) that is not published. P1 checks the two agree for 2024.
- A timezone in `core_eia__entity_plants` is taken as right; this check does not test EIA's timezone values or locations.
- "Different timezone" counts a possible wrong offset. Which EIA plant the unit really belongs to needs a person to check.
- PUDL's tables change nightly; the run records which build it read.
