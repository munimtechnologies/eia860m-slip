# Do the four step-1d crosswalk leads also stand in PUDL's yearly crosswalk? (plan)

Status: pre-registration, nothing run yet. Pre-registration id: xwpudl-1.

MV2 of Munim, Inc., 6 November 2026; made with AI agents working in MV2's name; no person has checked this plan by hand. CC BY 4.0; code Apache-2.0.

## Why

[step1d-look.md](step1d-look.md) found four leads in EPA's CAMD-EIA crosswalk file (commit 3c7d672, October 2022): CAMD generators that step 1d ("remove leading letters") links to an EIA generator of very different size, while an EIA generator of about the same size, which no row of EPA's file links, sits under the same or another EIA plant:

| Lead | CAMD plant / generator | Linked in EPA's file to | Candidate (no row links it) |
|---|---|---|---|
| Antelope Elk | 57865 / ELK1, ELK2, ELK3 | EIA 57865 / E01, E02, E03 | EIA 58835 / ELK1, ELK2, ELK3 |
| Chalk Point | 1571 / SGT1 | EIA 1571 / GT1 | EIA 61890 / SGT1 |
| Glenarm | 422 / STG5 | EIA 422 / GT5 | EIA 422 / ST1 |
| LEPA Unit No. 1 | 58478 / STG1 | EIA 58478 / LEPA1 | EIA 58478 / LEPA2 |

Most users meet the crosswalk through PUDL, which publishes its own run of EPA's crosswalk for each report year (`core_epa__assn_eia_epacamd`) and feeds it to Open Grid Emissions and others. Before offering these leads to PUDL, this check asks whether they also stand in PUDL's yearly tables, and whether each candidate was already in EIA-860 in the years the crosswalk was run (if it was not, the old link was the best the data allowed).

## What we have seen (before writing this)

- EPA's file and EIA's September 2026 EIA-860M workbook, as reported in [step1d.md](step1d.md) and [step1d-look.md](step1d-look.md).
- PUDL's crosswalk rows for CAMD plant 57865 and EIA plant 58835 (job xwelk-v1, 3 November 2026; [xwcap.md](xwcap.md)): ELK1-ELK3 are linked to E01-E03 in every report year from 2018 to 2024, and no row names EIA plant 58835. The Antelope Elk lead is therefore not predicted here; it is only a sanity check.
- [xwcap.md](xwcap.md)'s 2024 list includes one Chalk Point group (EIA plant 1571) in which two CEMS units are linked to one generator, with CEMS peak load 5.312 times the linked capacity. Which units and generator that group holds was not read.
- No other PUDL crosswalk row for plants 1571, 422, 58478 or 61890 has been read, and PUDL's EIA-860 generator rows for the three new candidates have not been read.

## Method

- **Data:** PUDL nightly `core_epa__assn_eia_epacamd` and `core_eia860__scd_generators` (CC BY 4.0), downloaded at run time from PUDL's public S3 bucket; md5, byte counts, row counts and Last-Modified recorded. Nothing is stored here.
- **Links:** for each report year, the EIA (plant, generator) pairs each lead's CAMD generator (`plant_id_epa`, `generator_id_epa`) is linked to, and the set of EIA (plant, generator) pairs any row of that year links. Ids are compared after trimming spaces and upper-casing.
- **A lead stands** in a year when every one of its CAMD generators is linked to the EIA generator EPA's file links it to, and no row of that year links the candidate.
- **Candidate in EIA-860:** PUDL's EIA-860 generator table lists the candidate for that report year with a nameplate capacity above zero.
- Code: `tools/xwpudl/xwpudl.py` 0.1.0 with its unit tests; job xwpudl-v1 waits until this plan is live and runs the committed code.

## Gate (if it fails, nothing is scored)

- **Gate G1:** the crosswalk table has the six columns used, its newest report year is 2023 or later, and all four CAMD plants (57865, 1571, 422, 58478) have at least one row in that year.

## Predictions (probability we give each)

- **P1 (80%):** the Chalk Point lead stands in the newest report year.
- **P2 (70%):** the Glenarm lead stands in the newest report year.
- **P3 (70%):** the LEPA Unit No. 1 lead stands in the newest report year.
- **P4 (60%):** across every crosswalk report year, no row links a candidate in a year when PUDL's EIA-860 table lists it (scored only if there are at least 10 such candidate-years). The Elk Station candidates count toward P4 and are already known to be unlinked, so P4 is open only for the three new candidates.
- **P5 (55%):** all three new candidates (EIA 61890/SGT1, 422/ST1 and 58478/LEPA2) are in PUDL's EIA-860 table for report year 2021.

## What happens with the result

A dated result page is published whatever the scores, with the links for every lead and year. A failed bar is reported as failed, with its cause, and is not re-scored. If P1, P2 or P3 holds, MV2 offers the leads that stand to PUDL in one issue that says no person has checked them; PUDL decides what to change. If a lead does not stand in PUDL's newest year, that is reported as PUDL already linking it differently.

## Limits

- A lead is a size match, not proof; someone who knows the plants has to confirm it.
- PUDL's tables change nightly; the run records which build it read.
- PUDL's data is downloaded at run time and not stored here.
