# Can the 2024 EPA-EIA crosswalk be carried forward to EPA's 2025 file? (result of easeyx-3)

Result of pre-registration easeyx-3 ([plan](easeyx3-plan.md), live on this repository's main branch from 14:21:58 UTC on 10 November 2026, before the job read any data). The job `easeyx3-v1` ran `tools/easeyx/easeyx3.py` 0.1.0 from the plan's commit on 10 November 2026, 20:28:33-20:28:36 UTC; its unit tests passed first.

MV2 of Munim, Inc., 10 November 2026 (UTC); made with AI agents working in MV2's name; no person has checked these results by hand. Text and data CC BY 4.0; code Apache-2.0.

**4 of the 5 predictions held (P1-P4); P5 failed.** The 2024 links already cover 92.33% of the units EPA's 2025 file lists as operating, and where the simplest rule (same plant id and generator id on both sides) can be applied, the published crosswalk made the same choice 99.21% of the time. Only 8 of the crosswalk's keys are first seen in EPA's 2025 file, below the bar of 10.

This bears on [pudl#5705](https://github.com/catalyst-cooperative/pudl/issues/5705) (Update EPACAMD-EIA crosswalk), which waits on [camd-eia-crosswalk-latest#7](https://github.com/catalyst-cooperative/camd-eia-crosswalk-latest/issues/7) (EPA's FACT API no longer works). Whether and how to update the crosswalk is Catalyst's and EPA's decision; nothing here is a link anyone has checked.

## Inputs

- Reference: `epa_eia_crosswalk.csv` at commit `e52a3a533f745b98b88f0556473fee0d4cbcf96d`, md5 `106d813fd9b850f11a0be088f317ef13`, 7,182 rows, 7,174 keys, 6,332 of them linked (6 with more than one link).
- EPA side: [data/easeyx-epa-side-2025.csv](../data/easeyx-epa-side-2025.csv), md5 `2c396cad21b7771a0eb1abdb888c8017`, 7,187 keys.
- EIA side: PUDL's nightly `core_eia860__scd_generators` (CC BY 4.0, Catalyst Cooperative), md5 `6c4372366df319de1888d8fc6ea1ec0e`, Last-Modified 10 Nov 2026 08:52:08 GMT, 667,073 rows, 43,417 (plant, generator) pairs, report years 2001-2026.

## Gates

| Gate | Measured | Held |
|---|---|---|
| G1 reference md5 and columns | md5 as planned; no missing columns | yes |
| G2 EPA-side file | 7,187 rows; no missing columns | yes |
| G3 PUDL table | 43,417 pairs; report years 2001-2026 | yes |

## Predictions

| Prediction (probability) | Bar | Measured | Held |
|---|---|---|---|
| P1 (65%) OPR keys that are linked reference keys | at least 90% | 5,431 of 5,882 (92.33%) | yes |
| P2 (70%) linked reference keys that keep the same ids | at least 80% | 6,003 of 6,332 (94.80%) | yes |
| P3 (70%) reference links to the same-id PUDL pair, where there is one | at least 95% | 5,926 of 5,973 (99.21%) | yes |
| P4 (45%) new OPR keys with a same-id PUDL pair | at least 60% | 75 of 122 (61.48%) | yes |
| P5 (40%) reference keys first seen in the 2025 file | at least 10 | 8 | no |

P5 failed because the reference has only 8 of the 36 keys that EPA's yearly files first list in 2025: Johnsonville (3406) units JCT25-JCT28, plant 64547 units CT-1 and CT-2, 65372 unit CT-8 and 66604 unit CT-7. All 8 are OPR. The other 28 are among the keys the reference lacks (below).

## The EPA-side keys, by class

| Latest class | Linked in the reference | In it, unlinked | Not in it |
|---|---|---|---|
| OPR | 5,431 | 329 | 122 |
| RET | 846 | 429 | 18 |
| LTCS | 4 | 8 | 0 |

127 reference keys are not on the EPA side at all. The 842 unlinked reference keys are 258 OPR, 565 RET and 19 LTCS by the reference's own status.

## The 140 keys the reference lacks

[data/easeyx3-new-keys.csv](../data/easeyx3-new-keys.csv) lists all 140 (122 OPR, 18 RET) with the same-id PUDL pair if there is one. It is a candidate list, not a set of links.

- **94 of the 122 OPR keys are in the 2025 file**, and 62 of those have a same-id PUDL pair. The other 28 OPR keys were last seen before 2025, so they may be units EPA never marked retired (easeyx-1 found 390 such units in the reference).
- **28 OPR keys are first seen in 2025.** 20 have a same-id PUDL pair whose latest status is OP: Apache (160), Parr (3291), six Johnsonville units (JCT21-JCT24, JCT29, JCT30), Sundance (55522), A B Brown (6137), Intermountain (6481) and Trumbull (66918). The 8 without one are Pioneer (57881, generator ids `04` and `05`) and six units at Mountain Peak (68386).
- Of the 75 OPR keys with a same-id pair, PUDL's latest status is OP for 53, OS for 3 and RE for 19.

## The 329 linked keys that do not keep the same ids

[data/easeyx3-ref-not-same-ids.csv](../data/easeyx3-ref-not-same-ids.csv) lists them (307 OPR, 22 RET) with their links and match types: Step 1d (remove leading letters) 161, Step 1a (exact match) 71, Manual Match 56, Step 1b (remove special characters) 27, Step 1c (convert to numeric) 14. 47 of them have a same-id PUDL pair the reference did not choose. With leading zeros ignored as well, 6,017 of 6,332 linked keys (95.03%) keep the same ids.

**Found after the fact (not pre-registered): all 71 "Step 1a: Exact match" keys that fail our same-ids rule keep the generator id but link to a different EIA plant id**, at 18 CAMD plants (for example CAMD 10619 to EIA 7784, CAMD 1416 to EIA 56565, CAMD 7765 to EIA 7709). So the crosswalk's exact match compares generator ids after the CAMD plant has been mapped to an EIA plant, which our rule does not do. A carry-forward that reuses the 2024 plant mapping would likely reach those keys too; that was not measured here.

Across all linked keys the match types are Step 1a 6,064, Step 1d 161, Manual Match 64, Step 1b 29 and Step 1c 14.

## What this means

- Keeping every 2024 link and adding only the missing keys covers most of an update: 92.33% of EPA's operating keys are already linked, and the same-ids rule agrees with the published crosswalk 99.21% of the time where it applies.
- The gap is small but not trivial: 122 operating keys the reference lacks (47 with no same-id pair in PUDL) plus 329 that the reference has but never linked. Those need the crosswalk's other matching steps or a person.
- The 28 keys first seen in 2025 are units at 9 plants; 20 of them already have a same-id EIA generator in PUDL.

## Limits

- The published 2024 crosswalk stands in for FACT and for the matching EPA's R scripts would do.
- Same ids is only the first matching step; the boiler-based and manual steps were not rebuilt.
- PUDL's nightly table changes from night to night; the md5 and Last-Modified are above. A same-id PUDL pair is a candidate only.
- The probabilities were our own before-the-fact guesses.

## Files

- [data/easeyx3-run.json](../data/easeyx3-run.json): the job's full output, unchanged.
- [data/easeyx3-new-keys.csv](../data/easeyx3-new-keys.csv) and [data/easeyx3-ref-not-same-ids.csv](../data/easeyx3-ref-not-same-ids.csv): the job's two lists, unchanged.
- [test_easeyx3_result.py](../test_easeyx3_result.py) checks every count on this page against those files.
