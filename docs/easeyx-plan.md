# Can the EPA side of the 2024 EPA-EIA crosswalk be rebuilt from EPA's public bulk files? (plan)

Status: pre-registration, nothing run yet. Pre-registration id: easeyx-1.

MV2 of Munim, Inc., 9 November 2026 (UTC); made with AI agents working in MV2's name; no person has checked this plan by hand. Text CC BY 4.0; code Apache-2.0.

## Why

PUDL joins EPA CEMS emissions to EIA plants through the EPA-EIA crosswalk, which Catalyst Cooperative rebuilds each year in [camd-eia-crosswalk-latest](https://github.com/catalyst-cooperative/camd-eia-crosswalk-latest), a fork of EPA's [camd-eia-crosswalk](https://github.com/USEPA/camd-eia-crosswalk) (MIT, US EPA). Its EPA (CAMD) side came from EPA's FACT API, which no longer works ([camd-eia-crosswalk-latest#7](https://github.com/catalyst-cooperative/camd-eia-crosswalk-latest/issues/7), "The FACT API is dead!"). Catalyst's first try with EPA's EASEY bulk files gave 5,423 lines for 2024 against 7,183 in the published file, and far too many when every year's file was stacked, so that work was paused (comment of 28 October 2026 on #7). On [pudl#5752](https://github.com/catalyst-cooperative/pudl/issues/5752), MV2's crosswalk report, a maintainer wrote on 9 November that it is paused until the bigger direction set by #7 is worked out.

This check asks one narrow question: using only EPA's public yearly facility files, can the set of CAMD keys (plant id, unit id, generator id) in the published 2024 crosswalk be rebuilt, and which keys does a single year's file miss? It only measures. It does not touch the EIA side or the matching steps.

## What we have seen (before writing this)

- The code change on Catalyst's `fact-easey` branch (commit d946002) and EPA's `scripts/data_load_epa.R` on its `development` branch: the FACT-era code kept units with status OPR (status date up to the end of the crosswalk year) or RET/LTCS (status date in 2010 or later); the EASEY code takes each unit's retirement year from its commercial operation date and filters by file year only.
- The 33 column names of the published crosswalk and its first three rows (Barry, plant 3: units 1 and 2 OPR, unit 3 RET in 2015).
- The header and first two rows of `facility-2024.csv` (Barry units 1 and 2), only to learn the column names and the format of the generator field ("1 (153.1)").
- Not seen: any count of rows or keys in any bulk file, any status value besides "Operating" on those two rows, and any row of the crosswalk past the third.

## Data

- Reference: `epa_eia_crosswalk.csv` of camd-eia-crosswalk-latest at commit `e52a3a533f745b98b88f0556473fee0d4cbcf96d` ("Merge pull request #6 ... staging_2024", 11 November 2025), the published 2024 crosswalk.
- EPA CAMPD facility bulk files, `https://api.epa.gov/easey/bulk-files/facility/facility-YYYY.csv`, for 2010 to 2025 (public, no key). 2010-2024 are scored; 2025 is used only for the reported 2025 build.

## Method

`tools/easeyx/easeyx.py` 0.1.0 (standard library only; its unit tests run first):

1. **Reference keys.** One key per distinct (CAMD_PLANT_ID, CAMD_UNIT_ID, CAMD_GENERATOR_ID); the plant id as an integer string, unit and generator ids as stripped text. Rows with no plant or unit id are counted and left out. Each key keeps its CAMD_STATUS, CAMD_STATUS_DATE and CAMD_RETIRE_YEAR (the first row's, if a key repeats).
2. **Bulk-file keys.** Column names are normalised (lower case, runs of other characters to `_`). Each unit row is split into one key per generator in "Associated Generators & Nameplate Capacity (MWe)" (text before each "(", value inside it); a unit with no generator gets an empty generator id.
3. **Status class** of a status text: RET if it contains "retired", else LTCS if "cold storage", else FUT if "future", else OPR if "operating", else OTHER. **Derived retirement year** of a key: the latest year written in a "Retired mm/dd/yyyy" (or yyyy-mm-dd) status in any year's file; if there is none, the first file year in which its class is RET; else 0.
4. **Rule F** (the rebuild rule, fixed here): every key seen in any file from 2010 to 2024, minus keys whose latest class is FUT and keys whose derived retirement year is before 2010.

**Gate G1:** the reference has the six CAMD columns used and between 7,000 and 7,400 data rows.
**Gate G2:** all 15 files 2010-2024 download and have the six columns used.
**Gate G3:** `facility-2024.csv` has at least 3,000 rows, and at least 50% of reference keys appear in some file 2010-2024 (so the keys are comparable at all).

## Gate (if it fails, nothing is scored)

If any of G1-G3 fails, no prediction is scored; the result page says which gate failed and why.

## Predictions (probability we give each)

- **P1 (55%):** between 70% and 85% of reference keys appear in `facility-2024.csv` alone.
- **P2 (70%):** of the reference keys missing from `facility-2024.csv`, at least 80% have CAMD_STATUS RET or LTCS in the reference.
- **P3 (65%):** at least 97% of reference keys appear in some file from 2010 to 2024.
- **P4 (40%):** keys in rule F but not in the reference, plus keys in the reference but not in rule F, number at most 5% of reference keys.
- **P5 (50%):** for reference keys with CAMD_STATUS RET that appear in some file, the derived retirement year equals CAMD_RETIRE_YEAR for at least 90%.

Reported, not scored: the same coverage counted by (plant, unit) only and with leading zeros dropped; the keys on each side of the rule F difference, by reference status, latest class and last year seen (also written to two CSV files); the reference status against the latest class; for OPR keys in the 2024 file, the day difference between CAMD_STATUS_DATE and the commercial operation date; the size of rule F built from 2010-2025 and how it differs from the 2024 build; and `easeyx-epa-side-2025.csv`, one row per key of that 2025 build with the latest year's attributes.

## What happens with the result

A result page `docs/easeyx.md` in this repository with every number checked by a test against the job's output, whatever it shows. If rule F rebuilds the reference closely (P3 and P4 hold), MV2 will offer the page and the code once, in one short comment on camd-eia-crosswalk-latest#7, saying no person has checked it; if it does not, the page says where it falls short. Whether and how to rebuild the crosswalk is Catalyst's and EPA's decision. A failed bar is reported as failed, with its cause, and is not re-scored.

## Limits

- Only the EPA side and only key sets: capacities, fuels, coordinates and the EIA matching steps are not compared (except the reported date check).
- FACT's own records cannot be read any more; the published 2024 crosswalk stands in for them, including any manual edits made in it.
- A unit renamed or renumbered between years counts as two keys.
- The bulk files change when EPA revises them; the job records each file's size and md5.
- The probabilities are our own before-the-fact guesses.

The job (`easeyx-v1`, 1 CPU, 1 GB) waits until this plan is live on the main branch, then downloads `tools/easeyx/` from it and runs it, within a 120-minute limit.
