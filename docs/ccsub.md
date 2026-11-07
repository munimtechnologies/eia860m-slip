# Does PUDL's subplant table already group the unlinked steam generators with their turbines? (result)

Result of pre-registration ccsub-1 ([plan](ccsub-plan.md), commit 6f69ea9, published 7 November 2026 at 03:19 UTC, before the subplant table was opened). MV2 of Munim, Inc., 7 November 2026; made with AI agents working in MV2's name; no person has checked these results by hand. CC BY 4.0; code Apache-2.0.

**Gate G1 held and all 5 predictions held.** Of the 10 operating steam (CA) generators that PUDL's 2024 crosswalk links to nothing ([ccsplit.md](ccsplit.md)), **7 are already in the same subplant as a linked gas turbine** of their plant in PUDL's subplant table (`core_epa__assn_eia_epacamd_subplant_ids`), and every one of those 7 gets there by sharing a `unit_id_pudl` (EIA's boiler-generator units) with the turbine. For two of the three plants where the crosswalk folds the steam part onto the turbine, **Glenarm (422) and CPV Fairview (60589), the steam generator is already grouped with its turbine**, so subplant totals already include its output and the rows proposed in [ccsplit.md](ccsplit.md) mainly correct the crosswalk table itself. At **LEPA Unit No. 1 (58478) the steam generator `LEPA2` sits in a subplant of its own**, and neither LEPA generator has a `unit_id_pudl`, so there the missing row does split the plant.

## How it ran

- Job ccsub-v1 ran on 7 November 2026 (10:42 to 10:45 UTC). It first checked that the plan was live (it was, at the first poll, 10:43:59 UTC), then downloaded the committed `tools/ccsub/ccsub.py` 0.1.0 (md5 f91fe0220de4adb5ede0c0fc22df68aa) and its tests (md5 1e4172279d5860990a539479c3cd006a); all 16 unit tests passed. Python 3.12.15, polars 2.1.0.
- **Subplant table:** PUDL nightly `core_epa__assn_eia_epacamd_subplant_ids`, 411,998 bytes, md5 eedd186816cc3f0715ffe48538fcf35e, 45,398 rows, Last-Modified 7 November 2026 08:14:14 GMT.
- **Crosswalk:** PUDL nightly `core_epa__assn_eia_epacamd`, 190,240 bytes, md5 420d50a7e4d066d29eee909eab73d932, 44,833 rows, Last-Modified 7 November 2026 08:14:13 GMT.
- **EIA-860:** PUDL nightly `core_eia860__scd_generators`, 7,718,170 bytes, md5 6c4372366df319de1888d8fc6ea1ec0e, 667,073 rows, Last-Modified 7 November 2026 08:14:05 GMT.
- The crosswalk and EIA-860 files have the same md5 as the builds [ccsplit.md](ccsplit.md) read, so the 10 steam generators are still unlinked in this build.

## Scores

| Bar | Probability given | Result | What the data shows |
|---|---|---|---|
| G1 | gate | held | All four columns present; 45,398 rows (at least 20,000 needed); every linked CT generator of the 9 plants has a row |
| P1 | 85% | held | All 10 steam generators have a row; none is absent |
| P2 | 55% | held | 7 of 10 are joined (at least 7 needed) |
| P3 | 65% | held | 2 of the 3 at hit plants are joined (422 `ST1`, 60589 `GEN3`); 58478 `LEPA2` is apart |
| P4 | 60% | held | All 7 joined steam generators share a `unit_id_pudl` with a linked CT of their plant (7 joined; at least 3 needed to score) |
| P5 | 80% | held | 559 of 559 linked operating CA generators at CC plants in 2024 are joined (100%; at least 95% needed, at least 200 needed to score) |

P2 held with nothing to spare: 7 was the bar.

## Every steam generator

| EIA plant | Steam generator | Class | Its subplant | Linked CT generators | Their subplant | unit_id_pudl (steam / CT) | Generators in the steam generator's subplant |
|---|---|---|---|---|---|---|---|
| 422 | ST1 | joined | 5 | GT5 | 5 | 1 / 1 | GT5;ST1 |
| 7242 | 1CA | joined | 2 | 1CT;2;3;4;5 | 2 | 1 / 1 | 1CA;1CT;2;2CC;3;4;5 |
| 7307 | 4 | joined | 4 | 5;6 | 4 | 1 / 1 | 4;5;6 |
| 10682 | ST2 | apart | 3 | GT4;GT5 | 4 | 2 / 3 | GT3;ST2 |
| 52176 | GEN3 | joined | 1 | GEN1;GEN2 | 1 | 1 / 1 | GEN1;GEN2;GEN3 |
| 55419 | ST6 | joined | 1 | G500;G600;G700;G800 | 1 | 1 / 1 | G500;G600;G700;G800;ST5;ST6;ST7 |
| 55419 | ST7 | joined | 1 | G500;G600;G700;G800 | 1 | 1 / 1 | G500;G600;G700;G800;ST5;ST6;ST7 |
| 55524 | STG2 | apart | 2 | CTG1;CTG2;CTG3 | 1 | 2 / 1 | CTG5;CTG6;STG2 |
| 58478 | LEPA2 | apart | 2 | LEPA1 | 1 | none / none | LEPA2 |
| 60589 | GEN3 | joined | 1 | GEN1;GEN2 | 1 | 1 / 1 | GEN1;GEN2;GEN3 |

## What else the rows show (read after scoring, not pre-registered)

- **Two of the three "apart" steam generators belong to a different block, not to a lone steam part.** At plant 10682, `ST2` shares subplant 3 and `unit_id_pudl` 2 with `GT3`, not with the linked turbines `GT4` and `GT5`. At plant 55524 (York Energy Center, Pennsylvania), `STG2` shares subplant 2 and `unit_id_pudl` 2 with `CTG5` and `CTG6`, which third-party plant profiles ([gridinfo](https://www.gridinfo.com/plant/york-energy-center/55524)) describe as a second block that began operating in March 2019. So [ccsplit.md](ccsplit.md)'s count of "orphan-CA plants" mixes two different things: a steam part missing from an otherwise linked block, and a whole block that the crosswalk does not link.
- **At York, the whole second block has no crosswalk row.** In [xwpair.md](xwpair.md) (a separate pre-registered check, scored today), CEMS units `5` and `6` at plant 55524 have no row in PUDL's crosswalk in any report year from 2019 to 2024, with 2024 peaks of 450 and 448 MW, and `CTG5`, `CTG6` and `STG2` are all unlinked operating generators. Open Grid Emissions' hand-made crosswalk already maps them (`5` to `CTG5` and `STG2`, `6` to `CTG6` and `STG2`; read at the head of [open-grid-emissions#476](https://github.com/singularity-energy/open-grid-emissions/pull/476), commit `e6d1e3f`).
- **LEPA has no `unit_id_pudl` at all.** A third-party profile ([gridinfo](https://www.gridinfo.com/plant/lepa-unit-no-1/58478), via a search summary) says EIA gives both LEPA generators the unit code "LEPA". If so, that code did not reach `unit_id_pudl` in this build; we did not read EIA's own files to check. Open Grid Emissions also joins generators that share an EIA unit code, so its own subplants may join `LEPA2` even though PUDL's table does not.
- **Unlinked generators carry their generator id as the CEMS unit id.** In the subplant table, the "CEMS unit" of each unlinked steam generator is its generator id (for example `ST1` at 422 and `GEN3` at 60589), which suggests the table fills a missing unit id with the generator id. We did not check this in PUDL's code.

## What this changes

- The proposed rows of [ccsplit.md](ccsplit.md) for Glenarm (`422, GT5, 422, ST1`) and CPV Fairview (`60589, CT-1, 60589, GEN3`) correct the crosswalk table, but PUDL's subplant totals already include those steam generators. The LEPA row (`58478, CC01, 58478, LEPA2`) also changes PUDL's subplant grouping.
- The PUDL issue that offers these leads will say this for each generator, and that no person has checked the rows.

## Limits

- The subplant table has no report year; a generator's subplant is not tied to 2024.
- Sharing a subplant means totals are grouped together; it does not make the crosswalk row itself right.
- Open Grid Emissions builds its own subplants and does not read this table, so this is a close proxy for it, not the same thing.
- PUDL's tables change nightly; this run read the builds named above. PUDL's data is downloaded at run time; only the derived list below is published.
- No person has checked the code or the results by hand.

## Files

- [`data/ccsub-steam-2024.csv`](../data/ccsub-steam-2024.csv) (10 rows): every steam generator's class, subplants and `unit_id_pudl` values as job ccsub-v1 wrote them, CC BY 4.0, derived from PUDL (CC BY 4.0, Catalyst Cooperative).
- [`tools/ccsub/ccsub.py`](../tools/ccsub/ccsub.py) 0.1.0, its tests and the plan-gated fetch; the plan: [ccsub-plan.md](ccsub-plan.md).
