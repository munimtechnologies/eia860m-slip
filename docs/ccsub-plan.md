# Does PUDL's subplant table already group the unlinked steam generators with their turbines? (plan)

Status: pre-registration, nothing run yet. Pre-registration id: ccsub-1.

MV2 of Munim, Inc., 7 November 2026; made with AI agents working in MV2's name; no person has checked this plan by hand. CC BY 4.0; code Apache-2.0.

## Why

[ccsplit.md](ccsplit.md) found 10 operating steam (prime mover CA) generators at 9 combined-cycle plants that no row of PUDL's 2024 crosswalk (`core_epa__assn_eia_epacamd`) links. At 3 of those plants (Glenarm, LEPA Unit No. 1 and CPV Fairview) the crosswalk instead links the CAMD steam generator to the gas turbine, and [ccsplit.md](ccsplit.md) proposes one crosswalk row for each.

How much these wrong or missing rows cost depends on what is built on them. PUDL's subplant table (`core_epa__assn_eia_epacamd_subplant_ids`) is "an augmented version" of the crosswalk: per its metadata and the code of `make_subplant_ids` (read on 7 November 2026 at [catalyst-cooperative/pudl](https://github.com/catalyst-cooperative/pudl) `main`, `src/pudl/dagster/assets/core/glue.py`), it adds every EIA-860 generator, attaches `unit_id_pudl` from EIA's boiler-generator associations, and puts generators that share a `unit_id_pudl` into one subplant even when no crosswalk row joins them ([pudl#5543](https://github.com/catalyst-cooperative/pudl/pull/5543), merged 1 October 2026). If each unlinked steam generator is already in its turbines' subplant, subplant totals already include its output, and the proposed rows matter mainly to users of the crosswalk table itself. This check finds out before the rows are offered to PUDL.

Open Grid Emissions does not read this table: it builds its own subplant crosswalk by running PUDL's `make_subplant_ids` on its own expanded crosswalk and then joining generators that share a `unit_id_pudl` or an EIA unit code (`generate_subplant_ids` and `update_subplant_ids` in `src/oge/subplant_identification.py`, read on 7 November 2026). So for Open Grid Emissions this check is a close proxy, not the same table.

## What we have seen (before writing this)

- Everything in [ccsplit.md](ccsplit.md) and its data files, and the code and metadata named above. We have not opened the subplant table or the boiler-generator association table, and no count of subplant membership for these generators has been made by us or reported to us.
- A third-party plant profile ([gridinfo](https://www.gridinfo.com/plant/lepa-unit-no-1/58478), via a search summary) says EIA lists both of LEPA Unit No. 1's generators with the unit code "LEPA". If PUDL carries that into `unit_id_pudl`, LEPA2 is likely joined. We have seen nothing like it for the other nine.

## Method

- **Data:** PUDL nightly `core_epa__assn_eia_epacamd_subplant_ids`, `core_epa__assn_eia_epacamd` and `core_eia860__scd_generators`, CC BY 4.0, downloaded at run time from PUDL's public S3 bucket; md5, byte counts, row counts and Last-Modified recorded. Nothing is stored here.
- **The 10 steam generators** and each plant's crosswalk-linked CT generators are fixed in the code, copied from the 2024 rows of `data/ccsplit-orphans-2018-2024.csv`: 422 ST1; 7242 1CA; 7307 4; 10682 ST2; 52176 GEN3; 55419 ST6 and ST7; 55524 STG2; 58478 LEPA2; 60589 GEN3. The three at hit plants are 422 ST1, 58478 LEPA2 and 60589 GEN3.
- Ids are compared after trimming and upper-casing. For each steam generator: **joined** if it has a row whose `subplant_id` is also a `subplant_id` of at least one linked CT generator of its plant; **apart** if it has a row but shares no subplant with a linked CT; **absent** if it has no row. It **shares a unit** if its `unit_id_pudl` equals that of at least one linked CT of its plant.
- **Base rate:** in the newest crosswalk report year, with [ccsplit-plan.md](ccsplit-plan.md)'s definitions (a CC plant has a linked CT and an operating CA; operating = status OP and nameplate above zero), every operating CA at a CC plant that the crosswalk does link is classified the same way.
- Code: `tools/ccsub/ccsub.py` 0.1.0 with its unit tests; job ccsub-v1 waits until this plan is live and runs the committed code.

## Gate (if it fails, nothing is scored)

- **Gate G1:** the subplant table has the columns `plant_id_eia`, `generator_id`, `subplant_id` and `unit_id_pudl`; it has at least 20,000 rows; and every one of the 9 plants' linked CT generators has a row in it.

## Predictions (probability we give each)

- **P1 (85%):** all 10 steam generators have a row in the subplant table (none is absent).
- **P2 (55%):** at least 7 of the 10 are joined.
- **P3 (65%):** at least 2 of the 3 at hit plants (422 ST1, 58478 LEPA2, 60589 GEN3) are joined.
- **P4 (60%):** every joined steam generator shares a unit with a linked CT of its plant (the join comes through EIA's units). Scored only if at least 3 are joined.
- **P5 (80%):** at least 95% of the linked operating CA generators at CC plants in the base-rate year are joined. Scored only if there are at least 200 of them.

## What happens with the result

A dated result page is published whatever the scores, with every steam generator's subplant, its turbines' subplants and the `unit_id_pudl` values. A failed bar is reported as failed, with its cause, and is not re-scored. Then the leads of [xwpudl.md](xwpudl.md) and [xwdev.md](xwdev.md) and the proposed rows of [ccsplit.md](ccsplit.md) are offered to PUDL in one issue that says, for each steam generator, whether the subplant table already groups it with its turbines, and that no person has checked the rows. If the hit plants' steam generators are joined, the note already posted on [open-grid-emissions#476](https://github.com/singularity-energy/open-grid-emissions/pull/476) will get one short follow-up saying so, since it bears on whether those rows change Open Grid Emissions' results.

## Limits

- The subplant table has no report year; a generator's subplant is not tied to 2024.
- Sharing a subplant means totals are grouped together; it does not make the crosswalk row itself right.
- PUDL's tables change nightly; the run records which build it read. PUDL's data is downloaded at run time and not stored here.
