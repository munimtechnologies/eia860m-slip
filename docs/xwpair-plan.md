# CEMS units with no crosswalk row: is there one right-sized EIA generator waiting for each? (plan)

Status: pre-registration, nothing run yet. Pre-registration id: xwpair-1.

MV2 of Munim, Inc., 6 November 2026; made with AI agents working in MV2's name; no person has checked this plan by hand. CC BY 4.0; code Apache-2.0.

## Why

Hourly CEMS data reports emissions and gross load per EPA emissions unit. To use it with EIA data (fuel, generation, plant attributes), each unit has to be tied to EIA generators through EPA's CAMD-EIA crosswalk, which PUDL re-runs for each EIA year (`core_epa__assn_eia_epacamd`) and which Open Grid Emissions (OGE) extends with a hand-made table. A CEMS unit with no crosswalk row at all drops out of anything built on that link.

On 6 November 2026 OGE opened [open-grid-emissions#476](https://github.com/singularity-energy/open-grid-emissions/pull/476), which reads EPA's CAMPD facility file and proposes 171 new manual crosswalk rows (notes "CAMPD Facility database mapping") for CEMS units that have no generator in OGE's subplant crosswalk. Its description reports that CEMS units with no generator drop "from 488 to 349", that "25 units still need manual matching", and that CAMPD often uses its own generator labels ("`CCT10` for EIA's `GT10`"), so it is not used as an automatic backstop.

This census asks a different, label-free question: for each CEMS unit that PUDL's crosswalk does not link, is there exactly one operating, unlinked EIA combustion generator at the same plant whose nameplate fits the unit's CEMS peak load? Such a "unique pair" is a proposed row for a person to check. OGE's 171 rows, chosen from CAMPD's own generator lists and reviewed by a person before they go in, are an independent check of how often the size rule picks the same generator.

**Prior art.** OGE #476 and its notebook (`manually_identify_crosswalk_updates.ipynb`) match by CAMPD's generator labels, not by size, and only for units with no generator. PUDL's documentation says it "imports all matched rows of the crosswalk", so unmatched CEMS units have no row in `core_epa__assn_eia_epacamd`; [pudl#5543](https://github.com/catalyst-cooperative/pudl/pull/5543) adds match-rate tests but we did not read any rate from it. We found no size-based pairing of unmatched CEMS units with unlinked EIA generators in PUDL's or OGE's issues, and no comparison of such a rule with CAMPD's lists.

## What we have seen (before writing this)

- OGE #476's description (counts quoted above) and the 171 added rows in its diff, read at head commit `e6d1e3f` (for example `55373,CT1,55373,CT1` to `CT8`, `10522,CC1,10522,GEN1` and `GEN2`). We did not compare any of them with PUDL's tables.
- [xwcap.md](xwcap.md): in 2024 PUDL's crosswalk formed 4,060 groups from 6,328 links, and no unlinked same-plant generator fit the size gap of any of the 39 linked groups whose CEMS peak and nameplate disagree. That check looked only at units that **have** a crosswalk row.
- No count of CEMS units without a crosswalk row in PUDL's tables, of their candidate generators, or of unique pairs has been made by us or reported to us.

## Method

- **Data:** PUDL nightly `core_epa__assn_eia_epacamd` (the crosswalk), `out_epacems__yearly_operational_characteristics` (one row per CEMS unit and report year, with `plant_id_eia` and `max_gross_load_mw`) and `core_eia860__scd_generators` (prime mover, status, nameplate), CC BY 4.0, downloaded at run time from PUDL's public S3 bucket; md5, byte counts, row counts and Last-Modified recorded. OGE's `epa_eia_crosswalk_manual.csv` (MIT) is downloaded at run time at the pinned commit `e6d1e3f487f338829108b348919eb9a37aa82616`. Nothing is stored here.
- Unit ids are compared after trimming, upper-casing and removing leading zeros (as OGE does); EIA generator ids after trimming and upper-casing. For each report year in both PUDL tables:
  - **CEMS unit:** a (`plant_id_epa`, `emissions_unit_id_epa`) row of the yearly CEMS table; its EIA plant is `plant_id_eia` (`plant_id_epa` when empty); its peak is `max_gross_load_mw`;
  - **unmatched unit:** a CEMS unit with no crosswalk row of that year that names an EIA generator;
  - **candidate:** an EIA-860 generator of that year at the unit's EIA plant with status OP, nameplate above zero, prime mover CA, CS, CT, GT, IC or ST, and linked by no crosswalk row of that year;
  - **size match:** CEMS peak divided by the candidate's nameplate between 0.5 and 1.5;
  - **unique pair:** the unit has exactly one size-matched candidate, and that candidate size-matches no other unmatched unit of the plant.
  - Each unmatched unit gets one class: `no_load` (no peak), `no_candidate`, `no_size_match`, `ambiguous` (several matches, or a shared match) or `unique_pair`.
- The newest report year is the one scored. Every unmatched unit of every year is written to `xwpair-units.csv` with its class, candidates, proposed generator and OGE's generators, and published with the result.
- Code: `tools/xwpair/xwpair.py` 0.1.0 with its unit tests; job xwpair-v1 waits until this plan is live and runs the committed code.

## Gate (if it fails, nothing is scored)

- **Gate G1:** all three PUDL tables have every column used; the newest report year in both is 2023 or later; and that year has at least 2,000 CEMS units.
- **Gate G2 (for P4 to P7 only):** OGE's file at the pinned commit downloads and has at least 150 rows with the CAMPD note.

## Predictions (probability we give each)

All about the newest report year.

- **P1 (60%):** unmatched units are between 2% and 10% of that year's CEMS units.
- **P2 (65%):** at least 30% of unmatched units have at least one candidate at their EIA plant.
- **P3 (55%):** there are at least 25 unique pairs.
- **P4 (70%):** of OGE's CAMPD units that are CEMS units that year, at least 80% are unmatched in PUDL's crosswalk that year. Scored only if there are at least 20 such units.
- **P5 (55%):** of those unmatched OGE units, in at least 60% every generator OGE names is among our candidates. Scored only if there are at least 10 such units.
- **P6 (60%):** of our unique pairs at OGE's units, at least 75% name a generator that OGE's rows also name for that unit. Scored only if there are at least 5 such pairs.
- **P7 (50%):** at least 10 unique pairs are at units that OGE's CAMPD rows do not cover.

## What happens with the result

A dated result page is published whatever the scores, with every unmatched unit listed. A failed bar is reported as failed, with its cause, and is not re-scored. If the gates hold, P6 says how far the size rule can be trusted; the unique pairs OGE does not cover become a list of proposed rows offered to OGE and PUDL, saying that no person has checked them. They decide what to change. The check is meant to be re-run on each new PUDL build as a regression case ("crosswalk lint"), alongside [ccsplit-plan.md](ccsplit-plan.md).

## Limits

- A size match is a lead, not proof: a CEMS unit can serve several generators, a generator can be fed by several units (combined cycles, common stacks), and CEMS gross load for a combined cycle may or may not include the steam part.
- The yearly CEMS table is PUDL's estimate over a trailing three-year window, so units with too little CEMS history may be missing and a peak may come from an earlier year.
- OGE's rows are a check, not ground truth: OGE's own notebook says each suggestion is reviewed before it is pasted in, and the pull request was not merged when this plan was written.
- PUDL's tables change nightly; the run records which build it read. Nothing from PUDL or OGE is stored here.
