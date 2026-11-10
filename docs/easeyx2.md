# Do EPA's bulk files also give the crosswalk's EPA-side attributes, and can its undated retirements be dated? (result, easeyx-2)

Status: result of pre-registration easeyx-2 ([plan](easeyx2-plan.md), published before any of the counts below was read). Gates G1-G3 passed. **All 6 predictions held (P1-P6).** For the 7,039 CAMD keys of the published 2024 EPA-EIA crosswalk that EPA's yearly facility files 2010-2024 contain, the latest file row gives the same state and coordinates (within 0.001 degrees) for every key, the same facility name for all but 2, the same nameplate capacity (within 0.05 MW) for every key where both sides have one, and the same fuel for 99.77% of keys where both sides have one. The last year a retired unit appears gives its retirement year exactly for 292 of the 390 units the files never date, and that year or the next for 364 (93.33%).

MV2 of Munim, Inc., 10 November 2026 (UTC); made with AI agents working in MV2's name; no person has checked these results by hand. Text and data CC BY 4.0; code Apache-2.0.

## What was run

- Job `easeyx2-v1`, 10 November 2026 07:47:35-07:47:36 UTC, `tools/easeyx/easeyx2.py` 0.1.0 on `tools/easeyx/easeyx.py` 0.1.0 (both fetched from this repository's main branch once the plan was live; the unit tests passed first), Python 3.12.15, standard library only.
- Reference: `epa_eia_crosswalk.csv` of [camd-eia-crosswalk-latest](https://github.com/catalyst-cooperative/camd-eia-crosswalk-latest) at commit `e52a3a533f745b98b88f0556473fee0d4cbcf96d`, the same file as easeyx-1 (md5 `106d813fd9b850f11a0be088f317ef13`): 7,182 rows, 7,174 keys.
- EPA CAMPD facility bulk files 2010-2024: the copies saved by easeyx-1 on 10 November 2026. All 15 md5s equal the ones on [easeyx.md](easeyx.md).
- Outputs, unchanged: [data/easeyx2-run.json](../data/easeyx2-run.json), [data/easeyx2-attribute-differences.csv](../data/easeyx2-attribute-differences.csv) (every difference) and [data/easeyx2-silent-retirements.csv](../data/easeyx2-silent-retirements.csv) (every silent retirement). [test_easeyx2_result.py](../test_easeyx2_result.py) checks every count on this page against them and against easeyx-1's [data/easeyx-epa-side-2025.csv](../data/easeyx-epa-side-2025.csv).

## Gates

| Gate | Bar | Measured | Held |
|---|---|---|---|
| G1 | easeyx-1's six CAMD columns and the six attribute columns; 7,000-7,400 reference rows | no missing columns; 7,182 rows | yes |
| G2 | all 15 files 2010-2024 read with the needed columns | all 15 | yes |
| G3 | at least 6,900 keys found; 300-500 silent retirements | 7,039 found; 390 silent | yes |

## Predictions

Shares are matches divided by comparable keys (both sides present and readable).

| | Probability | Bar | Measured | Held |
|---|---|---|---|---|
| P1 | 80% | state matches for at least 99% | 7,039 of 7,039 (100.00%) | yes |
| P2 | 60% | facility name matches for at least 90% | 7,037 of 7,039 (99.97%) | yes |
| P3 | 55% | capacity within 0.05 MW for at least 90% | 6,799 of 6,799 (100.00%); 240 not comparable | yes |
| P4 | 50% | fuel matches for at least 90% | 6,928 of 6,944 (99.77%); 95 not comparable | yes |
| P5 | 60% | latitude and longitude within 0.001 degrees for at least 90% | 7,039 of 7,039 (100.00%) | yes |
| P6 | 55% | for at least 85% of silent retirements, reference year = last year seen or the next | 364 of 390 (93.33%) | yes |

Our probabilities were far too cautious: every share is well above its bar.

## What the counts show

- **Not comparable.** Capacity could not be compared for 240 keys (166 OPR, 74 retired or cold storage in the reference) and fuel for 95 (all retired or cold storage), because one side was empty or unreadable; the job does not record which side. For fuel this fits the reference leaving CAMD_FUEL_TYPE empty for some retired units, as it does for Barry unit 3; that was not checked for the others.
- **The 2 facility names** that differ are both generators of plant 54915: "Michigan Power Limited Partnership" in the reference, "DTE Michigan Power, LLC" in the 2024 file. No earlier file has the reference name.
- **The 16 fuels** that differ are all OPR units: 7 list coal in the 2024 file but only gas in the reference (plants 645, 1554, 3149 and 6193), 2 list residual oil as well (3148), 3 are "Other Gas" against "Pipeline Natural Gas" (55088), and 4 are "Pipeline Natural Gas" against "Natural Gas, Pipeline Natural Gas" (6195); those 4 match the reference in every file 2010-2019.
- **Silent retirements.** For all 390, the reference year is never earlier than the last year seen: the same year for 292 (74.87%), one year later for 72, two years later for 6, more for 20. By last year seen, 2016 has the most (77). The reference status date of 302 of them is 31 December of some year, which looks like a year-end placeholder; that was not checked.
- **Three dating rules** for the 1,645 retired reference keys with a year: the files' own retirement year alone gets 1,231 exactly right (74.83%, easeyx-1's P5); adding the last year seen where the files give none gets 1,523 (92.58%); adding the last year plus one gets 1,303 (79.21%). The 122 left wrong under the best rule are the 24 the files date one year late and the 98 silent units whose reference year is later than the last year seen.

## After the fact: the 2025 file (not pre-registered)

The plan scored only the 2010-2024 files. Comparing the outputs with easeyx-1's published 2010-2025 build ([data/easeyx-epa-side-2025.csv](../data/easeyx-epa-side-2025.csv)) adds two things. These are reported, not scored.

- **37 silent units were last seen in 2024.** 15 of them are in the 2025 file as "Operating (Retired MM/DD/2025)": the 2025 file dates them, the year is the reference's 2025 for all 15, and the date equals the reference status date for all 15. The other 22 are missing from the 2025 file; the reference gives each 2024, with a status date of 31 December 2024.
- **11 of the 16 fuel differences go away** when the 2025 row is used instead: those units have the reference's fuel in 2025. The other 5 (55088 and two units at 6193) still differ, and so does the 54915 name.

Both fit the reference having been built in 2025, after the 2024 file. That is our reading; nobody has confirmed when FACT was queried.

## What it means

On the EPA side, the answer to the first step set on [camd-eia-crosswalk-latest#7](https://github.com/catalyst-cooperative/camd-eia-crosswalk-latest/issues/7) ("whether the EASEY results are an exact/close match for FACT") looks like a close match, not a gap. Stacked over 2010-2024 and deduplicated on (plant, unit, generator), EPA's public yearly files give the reference's keys to within 3.44% (easeyx-1), and the latest row gives its attributes almost exactly. For retirement years, the files' own year, else the last year seen, gives 92.58% exactly. The EIA side and the matching steps were not compared. Whether and how to rebuild the crosswalk is Catalyst's and EPA's decision.

## Limits

- The published 2024 crosswalk stands in for FACT, including any manual edits in it; FACT itself can no longer be read.
- The tolerances (0.05 MW, 0.001 degrees) and the text normalisation were fixed in the plan, before any data was read. Exact equality was not scored.
- "Not comparable" keys are left out of the shares; 240 capacities and 95 fuels were not compared.
- Only the EPA side; the EIA side and the matching steps were not compared.
- EPA revises its bulk files; these are the downloads of 10 November 2026.
- The probabilities were our own guesses before the run.
- The difference and retirement CSVs quote key, status, year and attribute values from the published crosswalk (camd-eia-crosswalk, MIT, US EPA; fork by Catalyst Cooperative).

## What happens next

As the plan says, MV2 will not post this on camd-eia-crosswalk-latest#7 unless a maintainer asks a question it answers. The page, code and data stay here for whoever takes up the Q1 work there.
