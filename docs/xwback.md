# Retired plants that leave PUDL's EIA-860 table and come back (result, xwback-1)

Status: result of pre-registration xwback-1 ([plan](xwback-plan.md), published before any of the rows below was read). Gates G1-G3 passed. **3 of the 5 predictions held (P1, P2, P4); P3 and P5 failed.**

MV2 of Munim, Inc., 9 November 2026 (UTC); made with AI agents working in MV2's name; no person has checked these results by hand. Text and data CC BY 4.0; code Apache-2.0.

## What was run

- Job `xwback-v1`, 9 November 2026 10:06:50-10:06:55 UTC, `tools/xwback/xwback.py` 0.1.0 (fetched from this repository's main branch once the plan was live; its 10 unit tests passed first), Python 3.12.15, polars 2.1.0.
- Data: PUDL nightly `core_eia860__scd_generators`, 667,073 rows, 7,718,170 bytes, md5 `6c4372366df319de1888d8fc6ea1ec0e`, Last-Modified Sun, 08 Nov 2026 08:13:25 GMT; population file `data/xwstale-units-2018-2024.csv`, md5 `7a35cb9cd87baa463506903cb42b8eb5`.
- Report years 2001 to 2026 are present. 2018-2025 rows are `final` (plus 35-43 rows a year with no maturity value in 2023-2025); 2026 rows are `monthly_update` (35,805) and `incremental_ytd` (2,604).
- Outputs, unchanged: [data/xwback-plants.csv](../data/xwback-plants.csv) (population A), [data/xwback-retired-plants.csv](../data/xwback-retired-plants.csv) (population C), [data/xwback-run.json](../data/xwback-run.json) (everything the tool printed). [test_xwback_result.py](../test_xwback_result.py) checks every count on this page against them.

## Gates

| Gate | Bar | Measured | Held |
|---|---|---|---|
| G1 | every column used; report years 2018-2026 | no missing columns; 2001-2026 | yes |
| G2 | population A = 14 plants, 57 units | 14 plants, 57 units | yes |
| G3 | each of the 14 listed in some year after 2024 | all 14 listed in 2026 | yes |

## Predictions

| | Probability | Bar | Measured | Held |
|---|---|---|---|---|
| P1 | 70% | at least 13 of the 14 plants listed in 2026, every 2026 row `monthly_update` | 14 of 14; all 81 rows `monthly_update` | yes |
| P2 | 80% | at least 95% of the 14 plants' 2025-2026 rows have status RE | 81 of 81 (100%); no 2025 rows at all | yes |
| P3 | 55% | at most 10% of population C persist (listed 3+ years after first fully retired) | 753 of 1,350 (55.8%) | **no** |
| P4 | 60% | at least 80% of population C listed in 2026 | 1,312 of 1,350 (97.2%) | yes |
| P5 | 55% | at most 10% of population C listed in 2025 | 497 of 1,350 (36.8%) | **no** |

## What it means

**The 14 crosswalk-gap plants (population A).** All 14 drop out of the annual years after retiring (last annual listing 2022, 2023 or, for plant 356, 2024), have no rows in the 2025 final data, and come back in report year 2026 only, every row filled from EIA-860M (`monthly_update`) with status RE. So the "listed again later" that [xwstale.md](xwstale.md) left unexplained is the EIA-860M year listing retired generators that the annual EIA-860 no longer carries, the mechanism PUDL's maintainers found for 2023 in [pudl#3684](https://github.com/catalyst-cooperative/pudl/issues/3684).

**Every plant fully retired in 2002-2021 (population C, 1,350 plants).** The plan bet that almost all of them drop out of the annual years. They split into two groups instead:

| Last annual year listed (up to 2024) | Plants | Share |
|---|---|---|
| 2024: listed in every annual year (496 also in 2025) | 497 | 36.8% |
| 2009 | 237 | 17.6% |
| 2010-2014 | 214 | 15.9% |
| 2015-2019 | 243 | 18.0% |
| 2020-2023 | 158 | 11.7% |
| 2002-2008 | 1 | 0.1% |

- 853 plants (63.2%) leave the annual years at some point before 2024; 497 (36.8%) are carried as retired in every annual year through 2024, and 496 of those also in 2025. This build does not say why one plant is carried and another dropped; this check did not look for a cause.
- P3 failed because the carried 497 count as persisting, and so do 256 plants that dropped out three or more years after retiring (for example plants 155, 334, 569 and 596, first fully retired in 2002-2004, are last listed in 2009).
- P5 failed because the 2025 final data lists the same carried group, not because it lists old retirements broadly: 496 of the 497 plants listed in 2025 are plants already listed in 2024. **The plan's sentence "If P5 fails, the 2025 annual data lists old retirements too, and the gap is in 2023-2024 only" does not describe what was found**: the drop-outs span 2009-2023, and 2025 behaves like 2024. (This reading is after the fact, not pre-registered.)
- 1,312 plants (97.2%) are listed in 2026. 38 are not; 23 of those are in neither 2025 nor 2026.

**For anyone using PUDL's generator table:** a fully retired plant missing from an annual report year is the common case, not a data error. Of plants fully retired in 2002-2021, 63% drop out of the annual years before 2024, and the EIA-860M year brings 97% of all of them back. "Not in PUDL's EIA-860 in year Y" does not mean "not retired by year Y", and "listed again later" does not mean "came back into service".

## Astoria Gas Turbines' undated generator (reported, not scored)

The one combustion generator at Astoria Gas Turbines (plant 55243) listed in 2023 with no retirement date on any row up to 2023 is **CTG01**, prime mover GT: status L in 2020 and 2021, CN in 2022 and 2023, no retirement date in any year. In EIA-860's codes L is a planned unit with regulatory approvals pending and CN a cancelled planned unit. So it is a proposed generator that was cancelled, not an operating unit missing its retirement date. This is why two predictions of xwstale-1 failed at Astoria ("one undated generator").

## Limits

- EIA-860M rows are preliminary; PUDL's docs say they are not considered as reliable as the annual form.
- Plant renumbering is not followed; a reused plant id is left out of population C by rule.
- RE is the reported status, not proof the units stopped running.
- PUDL's tables change nightly; this is the 8 November 2026 build named above.
- "Listed" means any generator row of the plant in that report year; the table is PUDL's slowly-changing-dimension generator table, not EIA's raw files, and EIA's raw files were not read.
- Probabilities were our own before-the-fact guesses; two failed bars are reported as failed and not re-scored.

## What happens next

The result goes into trap 2 of the [cems-eia-crosswalk](https://github.com/munimtechnologies/cems-eia-crosswalk) agent skill, and, in one short comment saying no person has checked it, onto [pudl#5752](https://github.com/catalyst-cooperative/pudl/issues/5752). Whether PUDL should carry retired generators forward in the annual years is PUDL's decision.
