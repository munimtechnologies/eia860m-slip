# CEMS units with load, no crosswalk row and nothing to link to: why? (plan)

Status: pre-registration, nothing run yet. Pre-registration id: xwgap-1.

MV2 of Munim, Inc., 8 November 2026; made with AI agents working in MV2's name; no person has checked this plan by hand. CC BY 4.0; code Apache-2.0.

## Why

To use hourly CEMS emissions with EIA data, each EPA emissions unit has to be tied to EIA generators through EPA's CAMD-EIA crosswalk, which PUDL re-runs for each EIA year (`core_epa__assn_eia_epacamd`). [xwpair.md](xwpair.md) (pre-registration xwpair-1) counted the CEMS units with no row in it. In report year 2024, 273 of 4,215 CEMS units had no row. Of those, 186 had no CEMS peak load, 12 had a right-sized unlinked EIA generator at their plant (all at 5 plants whose whole block is unlinked), and **75 had a peak load above zero but no "candidate"**: no operating, unlinked combustion generator at their EIA plant that a new row could point to. A size rule can say nothing about these 75, so they are the part of the gap nobody has explained.

This check sorts every such unit, in every report year, by reason:

- **absent:** the unit's EIA plant has no EIA-860 generator row at all that year (for example when PUDL gives the unit no EIA plant id and the EPA plant id is not an EIA plant id);
- **not_operating:** the plant has generator rows, but none is an operating combustion generator with a nameplate above zero (for example all retired or on standby);
- **all_linked:** the plant has operating combustion generators, and every one is already linked by some crosswalk row that year, to other CEMS units.

**Prior art.** EPA's own tracker has an open issue to "Perform manual matches on all remaining unmatched plants and units, including retired units" ([camd-eia-crosswalk#44](https://github.com/USEPA/camd-eia-crosswalk/issues/44), opened April 2025). PUDL's [#1769](https://github.com/catalyst-cooperative/pudl/issues/1769) notes that CEMS units missing from the crosswalk get no `subplant_id`, and [pudl/pull/5543](https://github.com/catalyst-cooperative/pudl/pull/5543) adds match-rate tests. A search of PUDL's issues for "crosswalk unmatched CEMS" and of EPA's for "unmatched" on 8 November 2026 found no breakdown of unmatched units by reason. Open Grid Emissions' manual crosswalk (pull request [open-grid-emissions/pull/476](https://github.com/singularity-energy/open-grid-emissions/pull/476)) fixes units by hand, one by one.

## What we have seen (before writing this)

- xwpair-1's yearly counts of unmatched units with a peak above zero and no candidate (class `no_candidate` in `data/xwpair-units-2018-2024.csv`), from PUDL's nightly build of 5-7 November 2026: 24 (2018), 34 (2019), 41 (2020), 46 (2021), 44 (2022), 53 (2023), 75 (2024). We have not read those rows one by one, and no count of their reasons has been made by us or reported to us.
- The five whole unlinked blocks of xwpair-1 (Okeechobee 60345, York 55524 block 2, Frontera 55098, Tait 55248/2847, plant 6061); their units have candidates, so they are not in this check.
- Open Grid Emissions' `epa_eia_crosswalk_manual.csv` at the head commit of pull request 476 (`e6d1e3f`), read for single plants only (Frontera, and the rows that fix Okeechobee, York, Tait and 6061).

## Method

- **Data:** PUDL nightly `core_epa__assn_eia_epacamd`, `out_epacems__yearly_operational_characteristics` and `core_eia860__scd_generators` (CC BY 4.0), downloaded at run time from PUDL's public S3 bucket, with md5, byte counts, row counts and Last-Modified recorded; Open Grid Emissions' `epa_eia_crosswalk_manual.csv` (MIT) at the pinned commit `e6d1e3f487f338829108b348919eb9a37aa82616`, every row whatever its note. Nothing is stored here.
- **Definitions** are those of xwpair-1: a CEMS unit is a (`plant_id_epa`, `emissions_unit_id_epa`) row of the yearly CEMS table, its EIA plant is `plant_id_eia` (`plant_id_epa` when empty) and its peak is `max_gross_load_mw`; an unmatched unit has no crosswalk row of that year naming an EIA generator; an operating combustion generator has status OP, a nameplate above zero and prime mover CA, CS, CT, GT, IC or ST; a candidate is one linked by no crosswalk row of that year. Unit ids are compared after trimming, upper-casing and removing leading zeros; generator ids after trimming and upper-casing.
- **Population ("gap units"):** for each report year in both PUDL tables, every unmatched unit with a peak above zero and no candidate. Each gets one reason (absent, not_operating, all_linked) and these leads: the linked operating combustion generators at its plant whose nameplate is 0.5 to 1.5 times its peak (a **fit**), and the CEMS units they are linked to; any generator at the plant whose id equals the unit id (**same-id**); other EIA plants that its EPA plant links to that year; the EIA status codes at the plant; whether OGE's manual table has a row for the unit; and whether the unit was also unmatched the year before.
- The newest report year is the one scored. Every gap unit of every year is written to `xwgap-units.csv` and published with the result, as a regression list to re-run on each new PUDL build ("crosswalk lint").
- Code: `tools/xwgap/xwgap.py` 0.1.0 with its unit tests; job xwgap-v1 waits until this plan is live and runs the committed code.

## Gate (if it fails, nothing is scored)

- **Gate G1:** all three PUDL tables have every column used; the newest report year in both is 2023 or later; and that year has at least 2,000 CEMS units.
- **Gate G2:** the newest year has at least 40 gap units.
- **Gate G3 (for P5 only):** OGE's file at the pinned commit downloads and has at least 150 rows with a plant and unit id.

## Predictions (probability we give each)

All about the newest report year; N is its number of gap units.

- **P1 (45%):** all_linked is the most common reason: more gap units are all_linked than absent, and more than not_operating.
- **P2 (40%):** at least 20% of gap units are absent.
- **P3 (50%):** at least half of the all_linked gap units have a fit. Scored only if there are at least 10 all_linked gap units.
- **P4 (35%):** at least 10 gap units have a same-id generator at their plant.
- **P5 (35%):** OGE's manual table has a row for at least 25% of gap units.
- **P6 (70%):** at least 70% of gap units were also unmatched the year before. Scored only if every gap unit's previous year is in both PUDL tables.

## What happens with the result

A dated result page is published whatever the scores, with every gap unit listed. A failed bar is reported as failed, with its cause, and is not re-scored. The reasons say which fix each group needs: a plant id mapping (absent), a retired-unit match of the kind EPA's issue #44 asks for (not_operating), or a second unit on an already-linked generator (all_linked with a fit). The list is offered to PUDL alongside our open issue there, saying that no person has checked it; PUDL, EPA and OGE decide what to change.

## Limits

- A reason is a description, not a diagnosis: an all_linked unit with a fit may share a generator with another unit (common in combined cycles and shared stacks), or may be a different unit altogether.
- The yearly CEMS table is PUDL's estimate over a trailing three-year window, so a unit retired in an earlier year may still carry a peak.
- "Absent" depends on the EIA plant id PUDL gives the unit; where PUDL leaves it empty we use the EPA plant id, as xwpair-1 did.
- OGE's rows are a check, not ground truth, and pull request 476 was not merged when this plan was written.
- PUDL's tables change nightly; the run records which build it read.
