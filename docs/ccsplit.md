# How often does the crosswalk fold a combined cycle's steam generator onto its gas turbine? (result)

Result of pre-registration ccsplit-1 ([plan](ccsplit-plan.md), commit 90832cd, published 6 November 2026 at 16:41 UTC, before any data was read). MV2 of Munim, Inc., 7 November 2026; made with AI agents working in MV2's name; no person has checked these results by hand. CC BY 4.0; code Apache-2.0.

**Both gates held; 4 of 6 predictions held, 2 failed.** In the newest report year of PUDL's crosswalk (2024), the "collapsed combined cycle" shape, where a CAMD unit's turbine and steam generators are both linked to one EIA combustion-turbine generator while the plant's operating steam (CA) generator is linked by no row, occurs at **3 plants**: the two already known (Glenarm and LEPA Unit No. 1) and one new one, **CPV Fairview Energy Center (EIA 60589)**, a 2x1 combined cycle whose 453 MW steam turbine `GEN3` has no crosswalk row in any report year from 2019 to 2024. P1 failed because we expected at least 5 hit plants. P6 failed because our size rule assumed one turbine per steam part, and CPV Fairview has two.

Unlinked steam parts are rare overall: of 442 plants in 2024 with a linked CT generator and an operating CA generator, 9 have a CA generator that no crosswalk row links, and 3 of those 9 are collapsed combined cycles.

## How it ran

- Job ccsplit-v1 ran on 7 November 2026 (00:01 to 00:04 UTC). It first checked that the plan was live (it was, at the first poll, 00:02:42 UTC), then downloaded the committed `tools/ccsplit/ccsplit.py` 0.1.0 (md5 59829bbe7e62f3f10ca73c34b5e6e5d8) and its tests (md5 cd39f269a8b3616cb58aa4fc70cca1d6); all 14 unit tests passed. Python 3.12.15, polars 2.1.0.
- **Crosswalk:** PUDL nightly `core_epa__assn_eia_epacamd`, 190,240 bytes, md5 420d50a7e4d066d29eee909eab73d932, 44,833 rows, Last-Modified 5 November 2026 08:15:03 GMT; report years 2018 to 2024.
- **EIA-860:** PUDL nightly `core_eia860__scd_generators`, 7,718,170 bytes, md5 6c4372366df319de1888d8fc6ea1ec0e, 667,073 rows, Last-Modified 5 November 2026 08:14:53 GMT.

## Scores

| Bar | Probability given | Result | What the data shows (2024 unless said) |
|---|---|---|---|
| G1 | gate | held | Every column present; newest report year 2024; 100% of generators at crosswalk plants have a prime mover; 442 CC plants (at least 200 needed) |
| G2 | gate | held | Glenarm (422) and LEPA Unit No. 1 (58478) are both hit plants |
| P1 | 70% | failed | 3 hit plants; at least 5 were needed. Only one plant beyond the two known has the shape |
| P2 | 75% | held | 3 hit plants (at most 50) |
| P3 | 55% | held | 9 orphan-CA plants, 3 times the 3 hit plants (at least 2 times needed) |
| P4 | 60% | held | All 3 hit plants have crosswalk rows in 2019, and all 3 are hit plants in 2019 too (at least 70% needed; at least 3 plants needed to score) |
| P5 | 55% | held | 3 of 3 hits have a collapsed CAMD generator id containing "ST" (`STG5`, `STG1`, `ST-1`) |
| P6 | 65% | failed | Orphan CA nameplate over the nameplate of the CT its hit is linked to: 0.2254 (422), 0.3 (58478), 1.2177 (60589). 2 of 3 plants (67%) are between 0.1 and 1.2; at least 70% were needed |

**Why P6 failed.** The ratio compares the steam generator with the CT generator(s) its collapsed CAMD unit is linked to. CPV Fairview is a 2x1 plant (two gas turbines feeding one steam turbine, per [CPV](https://cpv.com/our-fleet/cpv-fairview-energy-center/) and [Kiewit](https://www.kiewit.com/projects/fairview-energy-center/)): CAMD lists the steam generator `ST-1` under turbine unit `CT-1` only, so the rule set the 453 MW steam turbine against one 372 MW turbine. The bar is reported as failed and is not re-scored.

## The hits (2024)

| EIA plant | CAMD unit | CAMD generators (both linked to the CT) | Linked EIA CT generator | CT nameplate (MW) | Unlinked CA generator | CA nameplate (MW) |
|---|---|---|---|---|---|---|
| 422 Glenarm | GT5 | CTG5;STG5 | GT5 | 71.0 | ST1 | 16.0 |
| 58478 LEPA Unit No. 1 | CC01 | CTG1;STG1 | LEPA1 | 57.0 | LEPA2 | 17.1 |
| 60589 CPV Fairview Energy Center | CT-1 | CTGEN1;ST-1 | GEN1 | 372.0 | GEN3 | 453.0 |

Glenarm and LEPA are hits in all seven report years (2018 to 2024); CPV Fairview in all six from 2019 (the plant began operating in December 2019) to 2024.

## Orphan-CA plants and hits by year

| Report year | CC plants | Orphan-CA plants | Hit plants |
|---|---|---|---|
| 2018 | 439 | 6 | 2 |
| 2019 | 444 | 10 | 3 |
| 2020 | 445 | 10 | 3 |
| 2021 | 444 | 8 | 3 |
| 2022 | 444 | 8 | 3 |
| 2023 | 444 | 8 | 3 |
| 2024 | 442 | 9 | 3 |

The six 2024 orphan-CA plants without a hit (EIA plant: unlinked CA generator, MW) are 7242: 1CA, 133.4; 7307: 4, 26.8; 10682: ST2, 37.0; 52176: GEN3, 75.0; 55419: ST6 and ST7, 48.9 each; 55524: STG2, 419.6. Why their steam parts are unlinked was not read. Every year's list is in the data files below.

## What else the rows show (read after scoring, not pre-registered)

- **The three hits are real combined cycles of the shape the rows suggest.** Public sources agree with the EIA rows: Glenarm GT-5 is a 1x1 combined cycle (a GE LM6000 with a 14.7 MW steam turbine, ST-5, per South Coast AQMD's [BACT determination](https://www.aqmd.gov/docs/default-source/bact/laer-bact-determinations/aqmd-laer-bact/part-b-section_1-2-1-19-combined-cycle-gas-turbine.pdf?sfvrsn=10becf61_14)); LEPA Unit No. 1 is an LM6000 with a Siemens steam turbine ([Power Engineering](https://www.power-eng.com/gas/combined-cycle/natural-gas-fired-combined-cycle-project-gains-epc-contractor/)); CPV Fairview is 2x1, as above. EIA lists 16 MW for Glenarm's steam generator where the permit lists 14.7 MW. No person has checked the crosswalk rows against the plants' own records.
- **Open Grid Emissions' hand-made crosswalk has CPV Fairview rows, but not for the steam turbine.** Both on `main` and at the head of [open-grid-emissions#476](https://github.com/singularity-energy/open-grid-emissions/pull/476) (read 7 November 2026), `epa_eia_crosswalk_manual.csv` maps CAMD 60589 `CT-1` to EIA `GEN1` and `CT-2` to `GEN2` ("Matched based on generator ID and prime mover code"), and has no row for `GEN3`. It has no row for plants 422 or 58478.
- **Prior art, compared.** Open Grid Emissions reports 47 plants with orphaned combined-cycle parts after #476. Our 9 orphan-CA plants are a different measure: PUDL's crosswalk alone, the 2024 report year, steam (CA) parts only, and only at plants with a linked CT. The two counts are not expected to agree.
- **Ratio against both turbines.** If CPV Fairview's second turbine `GEN2` is also 372 MW, as the 1,197 MW plant total that third-party plant profiles report implies (this run did not read `GEN2`'s nameplate), the steam turbine is about 0.61 times the two turbines together.

## Proposed rows, for a person to check

One row per hit, in the CAMD unit / EIA generator form that PUDL's and Open Grid Emissions' crosswalk tables use:

| plant_id_epa | emissions_unit_id_epa | plant_id_eia | generator_id |
|---|---|---|---|
| 422 | GT5 | 422 | ST1 |
| 58478 | CC01 | 58478 | LEPA2 |
| 60589 | CT-1 | 60589 | GEN3 |

At CPV Fairview the steam turbine is fed by both turbines, so a second row (`60589, CT-2, 60589, GEN3`) may also be right; that depends on how the crosswalk's users split a shared steam part, which is for them to decide.

## What happens next

Before these rows are offered to PUDL, a follow-up check ([ccsub-plan.md](ccsub-plan.md), id ccsub-1) asks whether PUDL's subplant table, which groups generators through EIA's boiler-generator units as well as through the crosswalk, already puts each unlinked steam generator in the same subplant as its turbines. If it does, totals built on subplants (as Open Grid Emissions' are) already include the steam output, and the wrong rows matter mainly to users of the crosswalk itself. The PUDL issue will say which is the case. The same census is meant to be re-run on each new PUDL build as a regression case.

## Limits

- A hit is a pattern, not proof; someone who knows each plant has to confirm it.
- The rule sees only CA steam parts; single-shaft units (CS) are not counted.
- "Orphan" here means no crosswalk row; the steam generator may still be grouped with its turbines elsewhere (see ccsub-1).
- PUDL's tables change nightly; this run read the builds named above. PUDL's data is downloaded at run time; the derived lists below are published, not PUDL's tables.
- No person has checked the code or the results by hand.

## Files

- [`data/ccsplit-hits-2018-2024.csv`](../data/ccsplit-hits-2018-2024.csv) (20 rows) and [`data/ccsplit-orphans-2018-2024.csv`](../data/ccsplit-orphans-2018-2024.csv) (59 rows): every year's hits and orphan-CA plants as job ccsplit-v1 wrote them, CC BY 4.0, derived from PUDL (CC BY 4.0, Catalyst Cooperative).
- [`tools/ccsplit/ccsplit.py`](../tools/ccsplit/ccsplit.py) 0.1.0, its tests and the plan-gated fetch; the plan: [ccsplit-plan.md](ccsplit-plan.md).
