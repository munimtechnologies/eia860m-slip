# How often does the crosswalk fold a combined cycle's steam generator onto its gas turbine? (plan)

Status: pre-registration, nothing run yet. Pre-registration id: ccsplit-1.

MV2 of Munim, Inc., 6 November 2026; made with AI agents working in MV2's name; no person has checked this plan by hand. CC BY 4.0; code Apache-2.0.

## Why

A combined cycle has a gas (combustion) turbine part, EIA prime mover CT, and a steam part, prime mover CA, which burns no fuel of its own and has no stack. CEMS reports emissions per turbine unit, so the EPA-EIA crosswalk has to tie the steam generator to a CEMS unit; if it does not, the steam part's output is missing from the unit's generation and any per-MWh rate built on the link is off.

[xwpudl.md](xwpudl.md) found one shape of this at two plants, in every report year 2018 to 2024 of PUDL's crosswalk table: CAMD lists both a turbine generator and a steam generator under one unit (Glenarm: CTG5 and STG5 under unit GT5; LEPA Unit No. 1: CTG1 and STG1 under unit CC01), the crosswalk links **both** to the one EIA CT generator (EIA 422/GT5; 58478/LEPA1), and the plant's operating CA generator (422/ST1; 58478/LEPA2) is linked by no row. We call this a **collapsed combined cycle**. This census asks how common the shape is across all of PUDL's crosswalk, so that a list of fixable rows (one proposed link per case) can be offered to PUDL, which plans to rebuild the crosswalk in early 2027 ([camd-eia-crosswalk-latest#7](https://github.com/catalyst-cooperative/camd-eia-crosswalk-latest/issues/7)) and to bring Open Grid Emissions' hand-made crosswalk fixes into PUDL ([pudl#5439](https://github.com/catalyst-cooperative/pudl/issues/5439)).

**Prior art.** Open Grid Emissions checks that each of its subplants holds both parts of a combined cycle ([open-grid-emissions#297](https://github.com/singularity-energy/open-grid-emissions/pull/297)); its 2022 data update reported "259 subplants that only contain one part of a combined cycle system" as a known open problem ([#322](https://github.com/singularity-energy/open-grid-emissions/pull/322)). We found no count, in PUDL's or Open Grid Emissions' issues, of the specific collapsed shape, and no list of proposed links for it. The broader count below (orphan-CA plants) is close in spirit to OGE's warning but is not the same measure (plants, not subplants, and PUDL's crosswalk, not OGE's).

## What we have seen (before writing this)

- The two cases above (Glenarm and LEPA), from job xwpudl-v1. They are known to be in the newest year, so they are a gate here (a check that the code finds what we know is there), not a prediction.
- [xwcap.md](xwcap.md): in 2024, 29 crosswalk groups had a CEMS peak at least 1.5 times the linked nameplate, 10 of them containing a combined-cycle generator, in 17 plants (Glenarm and LEPA are not among them). Whether any of those 10 is a collapsed combined cycle was not read.
- No other PUDL crosswalk or EIA-860 row has been read for this question. No count of collapsed combined cycles, orphan CA generators or CC plants has been made by us or reported to us.

## Method

- **Data:** PUDL nightly `core_epa__assn_eia_epacamd` (the crosswalk, every report year) and `core_eia860__scd_generators` (prime mover, status code and nameplate per generator and report year), CC BY 4.0, downloaded at run time from PUDL's public S3 bucket; md5, byte counts, row counts and Last-Modified recorded. Nothing is stored here.
- Ids are compared after trimming spaces and upper-casing. For each report year:
  - **linked:** an EIA (plant, generator) that at least one crosswalk row of that year links;
  - **operating CA:** an EIA-860 generator of that year with prime mover CA, status code OP and a nameplate above zero; an **orphan CA** is an operating CA that is not linked;
  - **CC plant:** an EIA plant with at least one linked CT generator and at least one operating CA;
  - **orphan-CA plant:** a CC plant with at least one orphan CA;
  - **hit (collapsed combined cycle):** a CAMD unit (`plant_id_epa`, `emissions_unit_id_epa`) with two or more distinct CAMD generator ids linked to the same EIA generator, where that EIA generator's prime mover is CT and its plant has at least one orphan CA. A **hit plant** is an EIA plant with at least one hit.
- The newest report year is the one scored. Every year's hits and orphan-CA plants are written out (`ccsplit-hits.csv`, `ccsplit-orphans.csv`) and published with the result.
- Code: `tools/ccsplit/ccsplit.py` 0.1.0 with its unit tests; job ccsplit-v1 waits until this plan is live and runs the committed code.

## Gate (if it fails, nothing is scored)

- **Gate G1:** both tables have every column used; the newest crosswalk report year is 2023 or later; at least 95% of that year's EIA-860 generators at plants in that year's crosswalk have a prime mover code; and there are at least 200 CC plants in that year.
- **Gate G2:** Glenarm (EIA 422) and LEPA Unit No. 1 (EIA 58478) are both hit plants in the newest year.

## Predictions (probability we give each)

All about the newest report year unless said otherwise. The hit-plant count includes Glenarm and LEPA.

- **P1 (70%):** there are at least 5 hit plants (that is, at least 3 beyond the two known).
- **P2 (75%):** there are at most 50 hit plants.
- **P3 (55%):** there are at least 2 times as many orphan-CA plants as hit plants (most unlinked steam parts have some other cause).
- **P4 (60%):** of the hit plants that have any crosswalk row in report year 2019, at least 70% are hit plants in 2019 too (the shape persists). Scored only if there are at least 3 such plants.
- **P5 (55%):** in at least 60% of hits, one of the collapsed CAMD generator ids contains "ST" (as STG5 and STG1 do).
- **P6 (65%):** in at least 70% of hit plants, the orphan CA nameplate is between 0.1 and 1.2 times the nameplate of the CT generator(s) its hits are linked to (a plausible steam-to-turbine size).

## What happens with the result

A dated result page is published whatever the scores, with every hit and orphan-CA plant listed. A failed bar is reported as failed, with its cause, and is not re-scored. If the gates hold, the newest year's hits become a list of proposed crosswalk rows (CAMD unit and steam generator to the orphan CA), offered to PUDL in one issue that says no person has checked them; PUDL decides what to change. The same check is meant to be re-run on each new PUDL build and on EPA's development branch as a regression case ("crosswalk lint").

## Limits

- A hit is a pattern, not proof: some steam generators may be tied to a CEMS unit in another way (for example a plant-level arrangement), and someone who knows each plant has to confirm it.
- The rule sees only CA steam parts; single-shaft units (CS) and plants whose steam part EIA reports another way are not counted.
- PUDL's tables change nightly; the run records which build it read. PUDL's data is downloaded at run time and not stored here.
