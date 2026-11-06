# Do the four crosswalk leads stand in EPA's development-branch crosswalk? (plan)

Status: pre-registration, nothing run yet. Pre-registration id: xwdev-1.

MV2 of Munim, Inc., 6 November 2026; made with AI agents working in MV2's name; no person has checked this plan by hand. CC BY 4.0; code Apache-2.0.

## Why

[step1d-look.md](step1d-look.md) found four leads in EPA's CAMD-EIA crosswalk on the master branch of [USEPA/camd-eia-crosswalk](https://github.com/USEPA/camd-eia-crosswalk) (commit 3c7d672, October 2022), and [xwpudl.md](xwpudl.md) showed that all four also stand in every PUDL report year from 2018 to 2024. EPA's repository also has a `development` branch, 54 commits ahead of master and not released, on which `epa_eia_crosswalk.csv` was regenerated in June 2025 and `manual_matches.xlsx` was updated in September and October 2025 ("Updating manual matches with eGRID matches, adding year column and filter"; "Updating manual matches for EPA to EIA data (includes unit modification)"). Basing PUDL's next crosswalk update on that branch is one of the options Catalyst lists in [camd-eia-crosswalk-latest#7](https://github.com/catalyst-cooperative/camd-eia-crosswalk-latest/issues/7). Before offering the leads to PUDL, this check asks whether EPA's newer work already fixes them.

| Lead | CAMD plant / generator | Linked in EPA's 2022 file to | Candidate |
|---|---|---|---|
| Antelope Elk | 57865 / ELK1, ELK2, ELK3 | EIA 57865 / E01, E02, E03 | EIA 58835 / ELK1, ELK2, ELK3 |
| Chalk Point | 1571 / SGT1 | EIA 1571 / GT1 | EIA 61890 / SGT1 |
| Glenarm | 422 / STG5 | EIA 422 / GT5 | EIA 422 / ST1 |
| LEPA Unit No. 1 | 58478 / STG1 | EIA 58478 / LEPA1 | EIA 58478 / LEPA2 |

## What we have seen (before writing this)

- The branch list, the development branch's commit list, its file tree, and the change counts of commit 2b74eb4 (24 June 2025, "Updating gitignore"), which rewrote `epa_eia_crosswalk.csv` (5,811 lines added, 6,936 removed), all through GitHub's API on 6 November 2026.
- The column names of the development-branch CSV, from a web fetch that was asked only for the header line (its first columns are `sequence_number`, `epa_state`, `epa_facility_name`, `epa_plant_id`, `epa_unit_id`, `epa_generator_id`). No row of the file was reported to us, and `manual_matches.xlsx` has not been opened.
- The development-branch README (v0.3), which describes manual matches, exact matches and fuzzy matches, and a `plant_id_manual_matches` sheet copied from eGRID.
- Everything in [xwpudl.md](xwpudl.md) and the pages it cites.

## Method

- **Data:** `epa_eia_crosswalk.csv` and `manual_matches.xlsx` at development-branch commit 3423b2ab457222e1eac5d69d25a98b5f62ce5975 (8 October 2025), downloaded at run time from raw.githubusercontent.com; md5 and byte counts recorded. Nothing is stored here.
- **Columns:** EPA plant id, EPA generator id, EIA plant id and EIA generator id are looked up by name, case-insensitively (`epa_plant_id` or `camd_plant_id`, `epa_generator_id` or `camd_generator_id`, `eia_plant_id`, `eia_generator_id`); `match_type_gen` is reported if present. Ids are compared after trimming spaces and upper-casing.
- **Outcome of each lead:** *stands* when every CAMD generator of the lead is linked to the EIA generator EPA's 2022 file links it to and no row links any of the lead's candidates; *fixed* when every CAMD generator is linked to one of the lead's candidates and none to its 2022 EIA generator; *absent* when some CAMD generator has no linked row; *other* otherwise.
- **Not scored:** every row of `manual_matches.xlsx` (any sheet) with a cell equal to one of the plant ids 57865, 58835, 1571, 61890, 422 or 58478 is listed, as are the match types of the leads' rows.
- Code: `tools/xwdev/xwdev.py` 0.1.0 with its unit tests; job xwdev-v1 waits until this plan is live and runs the committed code.

## Gate (if it fails, nothing is scored)

- **Gate G1:** the CSV has the four id columns, at least 4,000 data rows, and at least one row for each of the four CAMD plants (57865, 1571, 422, 58478).

## Predictions (probability we give each)

- **P1 (50%):** the Antelope Elk lead stands.
- **P2 (65%):** the Chalk Point lead stands.
- **P3 (65%):** the Glenarm lead stands.
- **P4 (65%):** the LEPA Unit No. 1 lead stands.
- **P5 (40%):** all four leads stand.

## What happens with the result

A dated result page is published whatever the scores, with the links and match types for every lead and the manual-match rows found. A failed bar is reported as failed, with its cause, and is not re-scored. If a lead is fixed on the development branch, the PUDL issue will say so and credit EPA's newer work; if a lead stands there too, the issue will say that adopting the development branch alone would not fix it.

## Limits

- The development branch is not a release; EPA may change it.
- A lead is a size match, not proof; someone who knows the plants has to confirm it.
- EPA's files are downloaded at run time and not stored here.
