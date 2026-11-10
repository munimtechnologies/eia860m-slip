# Can the 2024 EPA-EIA crosswalk be carried forward to EPA's 2025 file, and how far does matching on the same ids go? (plan)

Status: pre-registration, nothing run yet. Pre-registration id: easeyx-3.

MV2 of Munim, Inc., 10 November 2026 (UTC); made with AI agents working in MV2's name; no person has checked this plan by hand. Text CC BY 4.0; code Apache-2.0.

## Why

PUDL's crosswalk update for the next data year ([pudl#5705](https://github.com/catalyst-cooperative/pudl/issues/5705), "Update EPACAMD-EIA crosswalk") lists as its first item the upstream problem in [camd-eia-crosswalk-latest#7](https://github.com/catalyst-cooperative/camd-eia-crosswalk-latest/issues/7): the crosswalk's EPA side came from EPA's FACT API, which no longer works. MV2's checks easeyx-1 ([result](easeyx.md)) and easeyx-2 ([result](easeyx2.md)) found that EPA's public yearly facility files rebuild the EPA side of the published 2024 crosswalk closely: keys to within 3.44%, and state, name, capacity, fuel and coordinates almost exactly.

A short-term update needs the EIA side as well. The cheapest path is to keep every link the 2024 crosswalk already has and link only the EPA keys it lacks. The crosswalk's first matching step pairs a CAMD generator with the EIA generator of the same plant id and generator id ("Step 1a: Exact match"). This check measures three things: how much of EPA's 2025 file the 2024 links already cover, how much of the 2024 crosswalk that simplest rule reproduces, and how many of the uncovered keys it could link from PUDL's EIA-860 table.

## What we have seen (before writing this)

- Everything on [easeyx.md](easeyx.md) and [easeyx2.md](easeyx2.md) and in their data files, including the counts of [data/easeyx-epa-side-2025.csv](../data/easeyx-epa-side-2025.csv): 7,187 keys, 36 first seen in 2025.
- Rows of `easeyx-epa-side-2025.csv` for 17 plants, read while writing easeyx2.md (1364, 2494, 2718, 2951, 3006, 3406, 4014, 7902, 8027, 1554, 3148, 3149, 54915, 55088, 6193, 6195, 645). Among them, 10 of the 36 keys first seen in 2025 are at Johnsonville (3406, units JCT21-JCT30). Whether the reference has them was not looked at.
- The header of the published crosswalk (33 columns, including EIA_PLANT_ID, EIA_GENERATOR_ID and MATCH_TYPE_GEN) and its first data row: Barry unit 1, CAMD plant 3 generator 1, linked to EIA plant 3 generator 1, match type "3_1_Generator (generators) match on plant and gen IDs Step 1a: Exact match". Earlier, the CAMD columns of its first three rows.
- PUDL's `core_eia860__scd_generators` was read by MV2's earlier jobs (xwback-1, 9 November) for retired plants, not for these keys.
- Not seen: any EIA-side value of the crosswalk past the first row, any match type count, which keys are unlinked, and any PUDL row for the 148 or so EPA-side keys the reference lacks.

## Data

- Reference: `epa_eia_crosswalk.csv` of camd-eia-crosswalk-latest at commit `e52a3a533f745b98b88f0556473fee0d4cbcf96d` (md5 `106d813fd9b850f11a0be088f317ef13`), as in easeyx-1 and easeyx-2.
- EPA side: `data/easeyx-epa-side-2025.csv` from this repository's main branch (easeyx-1's build from EPA's yearly facility files 2010-2025; one row per CAMD key; md5 recorded).
- EIA side: PUDL's nightly `core_eia860__scd_generators` (`https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/core_eia860__scd_generators.parquet`, CC BY 4.0, Catalyst Cooperative), columns plant_id_eia, generator_id, report_date and operational_status_code, all report years (md5 and Last-Modified recorded).

## Method

`tools/easeyx/easeyx3.py` 0.1.0, built on `tools/easeyx/easeyx.py` 0.1.0 (standard library, plus polars only to read the parquet file; its unit tests run first):

1. **Keys** as in easeyx-1: (CAMD plant id, unit id, generator id). A reference key's **links** are every (EIA_PLANT_ID, EIA_GENERATOR_ID) pair on any of its rows with both values present ("NA" counts as empty). A key with at least one link is **linked**.
2. **Same ids**: a key's CAMD plant id and CAMD generator id, compared with EIA ids after trimming and upper-casing generator ids. A linked key "keeps the same ids" if one of its links is that pair.
3. **PUDL pairs**: every (plant_id_eia, generator_id) in `core_eia860__scd_generators` in any report year, with its latest report year and status.
4. **EPA-side classes** are easeyx-1's latest status classes (OPR, RET, LTCS, ...).

**Gate G1:** the reference has the md5 above and the columns CAMD_PLANT_ID, CAMD_UNIT_ID, CAMD_GENERATOR_ID, CAMD_STATUS, EIA_PLANT_ID, EIA_GENERATOR_ID and MATCH_TYPE_GEN.
**Gate G2:** the EPA-side file has 7,187 data rows and the columns plant_id, unit_id, generator_id, latest_class, first_year and latest_year.
**Gate G3:** the PUDL table has plant_id_eia, generator_id and report_date, at least 20,000 distinct (plant, generator) pairs, and report year 2024.

## Gate (if it fails, nothing is scored)

If any of G1-G3 fails, no prediction is scored; the result page says which gate failed and why.

## Predictions (probability we give each)

- **P1 (65%):** of the EPA-side keys whose latest class is OPR, at least 90% are linked reference keys (the 2024 links carry forward).
- **P2 (70%):** at least 80% of linked reference keys keep the same ids.
- **P3 (70%):** of the linked reference keys whose same-id pair is a PUDL pair, the reference links at least 95% to that pair.
- **P4 (45%):** of the EPA-side keys not in the reference whose latest class is OPR, at least 60% have their same-id pair among the PUDL pairs.
- **P5 (40%):** at least 10 reference keys are first seen in the 2025 file (keys FACT had that no 2010-2024 file lists).

Reported, not scored:

- The EPA-side keys by latest class and by whether the reference has them linked, unlinked or not at all.
- The reference keys missing from the EPA side, the unlinked reference keys by status, and keys with more than one link.
- Same ids with leading zeros ignored as well; the 20 most common match types among linked keys and among keys that do not keep the same ids; how many of the latter have a same-id PUDL pair that the reference did not choose.
- For the new OPR keys: first year seen, and the latest PUDL status of those with a same-id pair.
- **Files:** every EPA-side key the reference lacks, with its same-id PUDL pair if any (a candidate list, not links), and every linked reference key that does not keep the same ids, with its links and match types.

## What happens with the result

A result page `docs/easeyx3.md` in this repository, with every number checked by a test against the job's output, whatever it shows. MV2 will not post it on camd-eia-crosswalk-latest#7 or pudl#5705 unless a maintainer asks a question it answers. The candidate list is a starting point, not a set of links: whether and how to update the crosswalk is Catalyst's and EPA's decision. A failed bar is reported as failed, with its cause, and is not re-scored.

## Limits

- The published 2024 crosswalk stands in for FACT and for the matching EPA's R scripts would do; FACT itself can no longer be read.
- Same ids is only the first of the crosswalk's matching steps; boiler-based and manual steps are not rebuilt here.
- PUDL's nightly table changes from night to night; the md5 and Last-Modified are recorded.
- A same-id pair in PUDL is a candidate only: the EIA generator may be a different unit, retired or planned.
- The probabilities are our own before-the-fact guesses.

The job (`easeyx3-v1`, 1 CPU, 2 GB) waits until this plan is live on the main branch, then downloads `tools/easeyx/` from it and runs it, within a 420-minute limit (most of it the wait).
