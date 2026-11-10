# Do EPA's bulk files also give the crosswalk's EPA-side attributes, and can its undated retirements be dated? (plan)

Status: pre-registration, nothing run yet. Pre-registration id: easeyx-2.

MV2 of Munim, Inc., 10 November 2026 (UTC); made with AI agents working in MV2's name; no person has checked this plan by hand. Text CC BY 4.0; code Apache-2.0.

## Why

Catalyst Cooperative's EPA-EIA crosswalk ([camd-eia-crosswalk-latest](https://github.com/catalyst-cooperative/camd-eia-crosswalk-latest), a fork of EPA's [camd-eia-crosswalk](https://github.com/USEPA/camd-eia-crosswalk), MIT, US EPA) took its EPA (CAMD) side from EPA's FACT API, which no longer works ([camd-eia-crosswalk-latest#7](https://github.com/catalyst-cooperative/camd-eia-crosswalk-latest/issues/7)). There, on 28 October 2026, a maintainer set the first step as finding out "whether the EASEY results are an exact/close match for FACT".

MV2's first check, easeyx-1 ([result](easeyx.md)), compared only the key sets. EPA's public yearly facility files for 2010-2024, stacked and kept one row per (CAMD plant id, unit id, generator id), contain 7,039 of the 7,174 keys in the published 2024 crosswalk (98.12%). That page names two open parts:

1. **Attributes.** Its build takes each key's attributes from the latest year the key appears in, and "whether the latest year's attributes are the ones FACT returned was not checked".
2. **Retirement dates.** 390 keys that are retired (RET) in the crosswalk are listed only as "Operating" in every file they appear in. The files then stop listing them, without ever giving a retirement date.

This check measures both, on the same data and code base. It does not touch the EIA side or the matching steps.

## What we have seen (before writing this)

- Everything on [easeyx.md](easeyx.md) and in its `data/easeyx-run.json`: key counts, status agreement, the retirement-year counts (1,231 match, 24 one year later, 390 none) and the status-date check. None of these counts compares state, facility name, capacity, fuel or coordinates.
- The first three rows of the published crosswalk (Barry, plant 3, Alabama: units 1 and 2 OPR, 153.1 MW, "Pipeline Natural Gas", 31.0069, -88.0103; unit 3 RET in 2015, 272 MW, an empty CAMD fuel type). We also saw the header and first two rows of `facility-2024.csv` (Barry units 1 and 2), when easeyx-1 was planned.
- The first five rows of the `epa_eia_crosswalk.csv` on EPA's `development` branch (status dates up to 2018, so an older build). Barry unit 1 shows status date 1954-02-12 there, against 1954-02-11 in the published 2024 file. That file is not used here.
- The field descriptions of the published crosswalk (`field_descriptions.csv`).
- Not seen: any attribute value of any crosswalk row past the third, any attribute value of any bulk-file row other than those two Barry rows, `data/easeyx-epa-side-2025.csv` (never opened), and the last year in which any of the 390 silent keys appears.

## Data

- Reference: `epa_eia_crosswalk.csv` of camd-eia-crosswalk-latest at commit `e52a3a533f745b98b88f0556473fee0d4cbcf96d` (md5 `106d813fd9b850f11a0be088f317ef13`), as in easeyx-1.
- EPA CAMPD facility bulk files `https://api.epa.gov/easey/bulk-files/facility/facility-YYYY.csv` for 2010-2024. The job reads the copies saved by easeyx-1 on 10 November 2026 and records whether each file's md5 still equals the one on easeyx.md.

## Method

`tools/easeyx/easeyx2.py` 0.1.0, built on `tools/easeyx/easeyx.py` 0.1.0 (standard library only; its unit tests run first):

1. **Keys and history** exactly as in easeyx-1. For each reference key found in some file 2010-2024, the **latest file row** is its row in the last year it appears in.
2. **Reference attributes** come from the first row of each key: CAMD_STATE, CAMD_FACILITY_NAME, CAMD_NAMEPLATE_CAPACITY, CAMD_FUEL_TYPE, CAMD_LATITUDE and CAMD_LONGITUDE.
3. **Comparisons**, each against the latest file row. If either side is empty or unreadable, the key is counted as "not comparable" for that attribute and left out of the share.
   - state: equal ignoring case and surrounding spaces;
   - facility name: equal after lower-casing and collapsing whitespace;
   - nameplate capacity: the file value is the one in brackets for that generator in "Associated Generators & Nameplate Capacity (MWe)"; the two values must be within 0.05 MW;
   - fuel: CAMD_FUEL_TYPE against "Primary Fuel Type", equal after lower-casing and collapsing whitespace;
   - coordinates: both latitude and longitude within 0.001 degrees.
4. **Silent retirements**: reference keys with CAMD_STATUS RET, found in some file, whose derived retirement year from easeyx-1 is 0 (no file ever shows them retired). For these, **last year** is the last file year in which the key appears.

**Gate G1:** the reference has the six CAMD columns of easeyx-1 and the six attribute columns above, and between 7,000 and 7,400 data rows.
**Gate G2:** all 15 files 2010-2024 are read and have the columns easeyx-1 needs.
**Gate G3:** at least 6,900 reference keys are found in some file, and the number of silent retirements is between 300 and 500 (so the data match easeyx-1's closely enough to build on it).

## Gate (if it fails, nothing is scored)

If any of G1-G3 fails, no prediction is scored; the result page says which gate failed and why.

## Predictions (probability we give each)

Each share is matches divided by comparable keys, over the reference keys found in some file.

- **P1 (80%):** state matches for at least 99%.
- **P2 (60%):** facility name matches for at least 90%.
- **P3 (55%):** nameplate capacity is within 0.05 MW for at least 90%.
- **P4 (50%):** fuel matches for at least 90%.
- **P5 (60%):** coordinates are within 0.001 degrees for at least 90%.
- **P6 (55%):** of the silent retirements with a nonzero CAMD_RETIRE_YEAR, the reference retirement year equals the last year or the last year plus one for at least 85%.

Reported, not scored:

- **Counts and splits.** For each attribute: matches, differences and not-comparable counts, split by reference status (OPR, or RET/LTCS). Also, for differing keys, how many match the reference in some other year's file.
- **Fuel.** The 25 most common reference-to-file fuel pairs among the differences.
- **Silent retirements in detail.** The reference year minus the last year; the silent keys by last year and by latest class.
- **Three dating rules.** For all reference RET keys with a retirement year: exact matches under easeyx-1's derived year alone, derived year else last year, and derived year else last year plus one.
- **Files.** Two CSV files: every attribute difference (key, attribute, both values, file year, years whose file matches) and every silent retirement.

## What happens with the result

A result page `docs/easeyx2.md` in this repository, with every number checked by a test against the job's output, whatever it shows. MV2 posted once on camd-eia-crosswalk-latest#7 on 10 November and said no reply was needed. He will not post there again unless a maintainer asks a question that this result answers. Whether and how to rebuild the crosswalk is Catalyst's and EPA's decision. A failed bar is reported as failed, with its cause, and is not re-scored.

## Limits

- The published 2024 crosswalk stands in for FACT, including any manual edits made in it; FACT itself can no longer be read.
- "Latest year" is one rule among several (first year, the reference's status year); other years are only reported, not scored.
- The tolerances (0.05 MW, 0.001 degrees) and text normalisation are our choices, fixed here before any data is read.
- Only the EPA side; the EIA side and the matching steps are not compared.
- The probabilities are our own before-the-fact guesses.

The job (`easeyx2-v1`, 1 CPU, 1 GB) waits until this plan is live on the main branch, then downloads `tools/easeyx/` from it and runs it, within a 420-minute limit (most of it the wait).
