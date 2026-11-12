# What would `boiler_id` change in PUDL's subplant table? (plan)

Status: pre-registration, nothing run yet.
Pre-registration id: spboil-1.

Made with AI agents working in MV2's name (MV2, Munim, Inc., mv2@munimtech.com). Code
Apache-2.0, text CC BY 4.0. PUDL is MIT-licensed and its data CC BY 4.0; this check only reads it.
PUDL's data (CC BY 4.0) is downloaded at run time and not stored here.

## Why

On PUDL issue [#5681](https://github.com/catalyst-cooperative/pudl/issues/5681) (add `boiler_id`
to `core_epa__assn_eia_epacamd_subplant_ids`), maintainer zaneselvans proposed two steps on
2026-11-12: (1) keep the `boiler_id` column in the table, and (2) add `boiler_id` to the NetworkX
analysis that assigns `subplant_id`, then ask "how often does it change the `subplant_id`
groupings?" and which generators get linked that were apart before. He also noted the table's
natural primary key already has nulls (about 2% of records) and that `boiler_id` might make that
worse. This check measures all of that on PUDL's nightly build before anyone writes a pull request.

## Data

Four nightly tables, read from `https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/`:
`core_epa__assn_eia_epacamd` (the EPA-EIA crosswalk, all years),
`core_epa__assn_eia_epacamd_subplant_ids` (the published subplant table),
`core_eia860__assn_boiler_generator` (EIA-860 boiler-generator associations with `unit_id_pudl`)
and `core_eia860__scd_generators` (only `plant_id_eia` and `generator_id`).

## Method (`tools/spboil/spboil.py` 0.1.0)

1. **Rebuild.** Follow PUDL's glue asset (`src/pudl/dagster/assets/core/glue.py`, read on
   2026-11-12): the unique crosswalk (drop rows duplicated apart from `report_year`; where one EPA
   unit maps to two EIA plants in different years, drop its 2018 rows), the three
   `augment_crosswalk_with_*` merges, the dedup on plant, EPA plant, EPA unit, generator and
   `unit_id_pudl`, then connected components of the combustor-generator graph with
   generator-`unit_id_pudl` edges folded in, and plant 1391 as one subplant. The list of EPA units
   (`_core_epacems__emissions_unit_ids`, not published) is taken from the published table, which
   holds every one of them. Groupings are compared as partitions of rows within each plant, so
   the numbering of `subplant_id` does not matter.
2. **Step 1 (keep `boiler_id`).** Dedup with `boiler_id` added and count the extra rows, the rows
   whose (EPA unit, generator) pair repeats (these would trip the current row-count assertion in
   `_subplant_ids_from_prepped_crosswalk`, which builds the output from graph edges), and the rows
   with a null `boiler_id`.
3. **Step 2 (boiler nodes).** Variant **xw**: one node per (plant, `boiler_id`) from the
   crosswalk's own `boiler_id`, joined to the row's generator (or its EPA unit when the generator
   is missing). Variant **xw_bga**: the same plus every generator-boiler pair in the EIA-860
   boiler-generator associations. For each variant, count the plants whose grouping changes, the
   subplants merged away and the **bridging boilers** (boilers whose neighbours sit in two or more
   of today's subplants). Plant 52151, the example from PR #2558, is reported as a case.

A plant **with a crosswalk match** has at least one unique-crosswalk row with both an EPA unit and
a generator.

## Gate and predictions

- **Gate G1:** the rebuild gives the same grouping as the published table at 99% or more of its
  plants, and its row count is within 1% of the published table's. If G1 fails, nothing below is
  reported as measured.
- **P1 (80%):** variant xw changes the grouping at 1 plant or more.
- **P2 (75%):** variant xw changes the grouping at fewer than 2% of plants with a crosswalk match.
- **P3 (70%):** variant xw_bga changes the grouping at no more than 5 plants beyond variant xw
  (`unit_id_pudl` already folds in the boiler-generator associations).
- **P4 (50%):** keeping `boiler_id` adds rows equal to 1% or more of the rebuilt table.
- **P5 (85%):** more than half of the rows of the step 1 table have a null `boiler_id`, so
  `boiler_id` cannot join a non-null primary key.

## Outputs

`spboil.json` (every count, the gate and the scores), `spboil-changed-xw.csv`,
`spboil-changed-xw_bga.csv` (plant, subplants before, after) and `spboil-bridges-xw.csv`,
`spboil-bridges-xw_bga.csv` (plant, boiler, subplants joined, generators).

## Limits

This is a rebuild, not PUDL's own code: G1 is there to show how close it is. A changed grouping
is not by itself right or wrong; whether generators that share a boiler belong in one subplant is
the maintainers' call. Nightly tables change; the run records each file's Last-Modified and ETag.
No person has checked these results by hand.
