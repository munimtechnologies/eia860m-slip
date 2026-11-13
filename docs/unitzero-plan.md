# Does PUDL turn an all-zero unit or generator ID into an empty string? (plan)

Status: pre-registration, nothing run yet.
Pre-registration id: unitzero-1.

Made with AI agents working in MV2's name (MV2, Munim, Inc., mv2@munimtech.com). Code
Apache-2.0, text CC BY 4.0. PUDL is MIT-licensed and its data CC BY 4.0; this check only reads it.
PUDL's data (CC BY 4.0) is downloaded at run time and not stored here.

## Why

PUDL strips leading zeros from plant-part IDs so that "0001" and "1" match across years and
datasets. It does this in two places, with two different rules (code read on main on 2026-11-13):

- `pudl.helpers.remove_leading_zeros_from_numeric_strings`, used on EIA-860, EIA-860M, EIA-861
  and EIA-923 IDs at extract time and on the EPA-EIA crosswalk's `generator_id`, `boiler_id` and
  `emissions_unit_id_epa` in `src/pudl/dagster/assets/core/glue.py`: where a value matches
  `^0+\d+$` it removes `^0+`. So "007" becomes "7" and "0" stays "0", but "00" and "000" become
  "" (an empty string, not a null).
- `transform_epacems` in `src/pudl/transform/epacems.py`, on EPA CEMS `emissions_unit_id_epa`:
  where a value is all digits it strips every leading "0". So "007" becomes "7", and "0", "00"
  and "000" all become "".

The two rules agree on every value except "0", which the crosswalk keeps and CEMS empties. Both
also merge two different raw IDs at one plant that differ only by leading zeros (for example "1"
and "01"). PUDL's helper test (`tests/unit/helpers_test.py`) has no all-zero case. Earlier PUDL
issues dealt with leading zeros in general (#964, #2366, and #3992, which asked for
`emissions_unit_id_epa` to be stripped like boiler and generator IDs), but a search of PUDL's
issues for "leading zeros" (18 results, 2026-11-13) found none about all-zero IDs. Whether any of
this touches real data is unknown; this check counts it.

## Data

- EPA's own crosswalk, `epa_eia_crosswalk.csv` on the master branch of
  [USEPA/camd-eia-crosswalk](https://github.com/USEPA/camd-eia-crosswalk), read as text (its commit
  is recorded). Columns `CAMD_UNIT_ID`, `CAMD_GENERATOR_ID` (within `CAMD_PLANT_ID`) and
  `EIA_GENERATOR_ID`, `EIA_BOILER_ID` (within `EIA_PLANT_ID`).
- PUDL nightly tables from `https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/`:
  `core_epa__assn_eia_epacamd`, `core_epa__assn_eia_epacamd_subplant_ids`,
  `core_eia__entity_generators` and `core_eia__entity_boilers`.
- `core_epacems__hourly_emissions` (nightly, one parquet file): only `plant_id_epa`,
  `plant_id_eia`, `emissions_unit_id_epa` and `year` are read, batch by batch, and only counts
  per plant and unit are kept.

## Method (`tools/unitzero/unitzero.py` 0.1.0)

For every ID column above, count nulls, empty strings, "0", other all-zero values ("00", "000")
and values with leading zeros. In EPA's crosswalk, also count **collisions**: two distinct raw
IDs at the same plant that PUDL's helper maps to one value. In CEMS, count rows and plant-units
whose unit ID is "" or "0", and list the plants where CEMS has a "" unit while PUDL's crosswalk
has a "0" unit (the one value the two rules treat differently). Every case is listed in
`unitzero-cases.csv`. The two rules are re-implemented value by value in the script and checked
against PUDL's own helper test cases in `tools/unitzero/test_unitzero.py`.

## Gate and predictions

- **Gate G1:** every download works, EPA's crosswalk has all six columns named above, the CEMS
  scan reads as many rows as the parquet metadata reports, and CEMS has 1,000 or more distinct
  `plant_id_epa`. If G1 fails, nothing below is reported as measured.
- **P1 (40%):** EPA's crosswalk has at least one all-zero `CAMD_UNIT_ID` ("0", "00", ...).
- **P2 (35%):** PUDL's nightly CEMS has at least one row whose `emissions_unit_id_epa` is "".
- **P3 (75%):** neither `core_eia__entity_generators` nor `core_eia__entity_boilers` has an
  empty-string ID.
- **P4 (55%):** EPA's crosswalk has at least one collision in `CAMD_UNIT_ID` or
  `EIA_GENERATOR_ID` (two raw IDs at one plant that differ only by leading zeros).
- **P5 (85%):** CEMS rows with an empty `emissions_unit_id_epa` are fewer than 0.1% of all CEMS
  rows read.

## Outputs

`unitzero.json` (every count, the gate and the scores) and `unitzero-cases.csv` (source, table,
column, plant, raw value, detail, rows).

## Limits

EPA's GitHub crosswalk is the current release, which may differ from the archived copy PUDL
reads; CEMS IDs are read after PUDL's transform, so a "" there is the only sign of an all-zero raw
ID, and "1"/"01" pairs in CEMS cannot be seen at all once merged. A count of cases is not by
itself a bug in PUDL's outputs: whether a merged or emptied ID changes any join is reported only
for the "" versus "0" case above. Nightly tables change; the run records each file's
Last-Modified and ETag. No person has checked these results by hand.
