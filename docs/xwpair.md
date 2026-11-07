# CEMS units with no crosswalk row: is there one right-sized EIA generator waiting for each? (result)

Result of pre-registration xwpair-1 ([plan](xwpair-plan.md), commit 6265651, published 6 November 2026 at 21:48 UTC, before any data was read). MV2 of Munim, Inc., 7 November 2026; made with AI agents working in MV2's name; no person has checked these results by hand. CC BY 4.0; code Apache-2.0.

**Both gates held; 1 of the 4 predictions that could be scored held, 3 failed, and 3 could not be scored.** In 2024, 273 of 4,215 CEMS units (6.5%) have no row in PUDL's crosswalk (`core_epa__assn_eia_epacamd`), as P1 expected. But the size rule found almost nothing to pair: 186 of the 273 have no CEMS peak load at all, 75 have no unlinked operating combustion generator at their EIA plant, and only **1 unit has a unique right-sized partner**. The other 11 units with a size match sit in groups the rule cannot split. The comparison with Open Grid Emissions' 306 CAMPD-mapped units could not be scored: only 17 of them are 2024 CEMS units in PUDL's table, and PUDL's 2024 crosswalk already links all 17.

Read after scoring (below): the 12 size-matched units sit at **5 plants where a whole block of generators is unlinked**, including FPL's 1,723 MW Okeechobee Clean Energy Center in every year from 2019 to 2024. Open Grid Emissions' hand-made crosswalk already covers 4 of the 5; the fifth, **Frontera Generation Facility in Texas (EIA 55098)**, has no row in either.

## How it ran

- Job xwpair-v1 ran on 7 November 2026 (03:54 to 03:57 UTC). It first checked that the plan was live (it was, at the first poll, 03:56:08 UTC), then downloaded the committed `tools/xwpair/xwpair.py` 0.1.0 (md5 51589823a9d6c3ef268101ba99ef445d) and its tests (md5 cf958cb9cf6c5b9a2eec0e1c0c31b61f); all 12 unit tests passed. Python 3.12.15, polars 2.1.0.
- **Crosswalk:** PUDL nightly `core_epa__assn_eia_epacamd`, 190,240 bytes, md5 420d50a7e4d066d29eee909eab73d932, 44,833 rows, Last-Modified 5 November 2026 08:15:03 GMT.
- **CEMS units:** PUDL nightly `out_epacems__yearly_operational_characteristics`, 3,295,621 bytes, md5 689d3ac11dcb5648fc5f6519aa68740d, 118,117 rows, Last-Modified 5 November 2026 08:17:43 GMT; report years 2018 to 2024.
- **EIA-860:** PUDL nightly `core_eia860__scd_generators`, 7,718,170 bytes, md5 6c4372366df319de1888d8fc6ea1ec0e, 667,073 rows, Last-Modified 5 November 2026 08:14:53 GMT.
- **Open Grid Emissions:** `epa_eia_crosswalk_manual.csv` at commit `e6d1e3f` (the head of [open-grid-emissions#476](https://github.com/singularity-energy/open-grid-emissions/pull/476)), 45,943 bytes, md5 d1275db58bd4cc9767c9ec0548d47ef7; 346 rows with the note "CAMPD Facility database mapping", for 306 CEMS units.

## Scores

| Bar | Probability given | Result | What the data shows (2024) |
|---|---|---|---|
| G1 | gate | held | Every column present; newest report year 2024; 4,215 CEMS units (at least 2,000 needed) |
| P1 | 60% | held | 273 of 4,215 CEMS units are unmatched: 6.48% (between 2% and 10%) |
| P2 | 65% | failed | 43 of 273 unmatched units (15.75%) have at least one candidate; at least 30% were needed |
| P3 | 55% | failed | 1 unique pair; at least 25 were needed |
| G2 | gate | held | 346 rows with the CAMPD note (at least 150 needed) |
| P4 | 70% | not scored | 17 of OGE's 306 CAMPD units are 2024 CEMS units; at least 20 were needed to score (0 of the 17 are unmatched) |
| P5 | 55% | not scored | 0 of OGE's CAMPD units are unmatched in 2024; at least 10 were needed to score |
| P6 | 60% | not scored | 0 unique pairs at OGE's units; at least 5 were needed to score |
| P7 | 50% | failed | 1 unique pair at a unit OGE's CAMPD rows do not cover; at least 10 were needed |

**Why P2 and P3 failed.** Most unmatched units are not the kind the rule can help with. 186 of the 273 have no peak load in PUDL's yearly CEMS table (class `no_load`), so they could never be size-matched; of the 87 with a peak, 75 have no unlinked operating combustion generator at their EIA plant. Of the 12 that have a size match, 11 are `ambiguous`: in the combined cycles below, each CEMS unit's peak covers its gas turbine and a share of the steam turbine, so it fits the steam generator for every unit of the block, and at Tait four identical 94 MW turbines fit four identical units. The plan's limits named the combined-cycle case; we did not expect it to be nearly all of them.

**Why P4 to P6 could not be scored, and P7 failed.** OGE's CAMPD rows and PUDL's unmatched units barely overlap: only 17 of OGE's 306 units appear in PUDL's 2024 CEMS table, and all 17 already have a 2024 crosswalk row in PUDL. Across all seven report years, only 9 distinct OGE units are ever among PUDL's unmatched units (three at plant 10672 and four at 55494 in 2018 and 2019, two at 65373 in 2023). Why most of OGE's units are not in PUDL's 2024 CEMS table was not checked. The bars are reported as failed or not scored and are not re-scored.

## Unmatched CEMS units by year

| Report year | CEMS units | Unmatched | With a candidate | No load | No candidate | No size match | Ambiguous | Unique pair |
|---|---|---|---|---|---|---|---|---|
| 2018 | 4718 | 252 | 44 | 227 | 24 | 1 | 0 | 0 |
| 2019 | 4572 | 264 | 45 | 220 | 34 | 1 | 9 | 0 |
| 2020 | 4475 | 269 | 45 | 219 | 41 | 0 | 9 | 0 |
| 2021 | 4437 | 285 | 45 | 230 | 46 | 0 | 9 | 0 |
| 2022 | 4359 | 264 | 41 | 211 | 44 | 0 | 9 | 0 |
| 2023 | 4273 | 260 | 43 | 195 | 53 | 0 | 11 | 1 |
| 2024 | 4215 | 273 | 43 | 186 | 75 | 0 | 11 | 1 |

## What else the rows show (read after scoring, not pre-registered)

The 12 size-matched units of 2024, by plant. At each, every EIA generator of the block is an operating generator that no 2024 crosswalk row links.

| EPA plant / CEMS units | 2024 peaks (MW) | EIA plant and unlinked generators (MW, prime mover) | In OGE's hand-made table at `e6d1e3f`? |
|---|---|---|---|
| 60345 / OCEC1A, OCEC1B, OCEC1C | 582, 583, 579 | 60345: 1A, 1B, 1C (376.6 CT each), 1ST (593.3 CA) | yes: each unit to its CT and to `1ST` |
| 55524 / 5, 6 | 450, 448 | 55524: CTG5, CTG6 (234.9 CT each), STG2 (419.6 CA) | yes: `5` to CTG5 and STG2, `6` to CTG6 and STG2 |
| 55248 / CT4, CT5, CT6, CT7 | 93, 95, 92, 92 | 2847: GT4, GT5, GT6, GT7 (94 GT each) | yes: CT4-CT7 to 2847 GT4-GT7 from 2019 ("These units change plant ID in 2019") |
| 6061 / 3 | 591 | 6061: MOR2 (402 CT), MOR1 (156 CA) | yes: `3` to MOR1 and MOR2 ("New unit at repowered plant") |
| 55098 / 1, 2 | 264, 268 | 55098: GEN1, GEN2 (172 CT each), GEN3 (185 CA) | **no** |

- **Okeechobee Clean Energy Center (60345)** is Florida Power & Light's 3-on-1 combined cycle; EPA describes units OCEC1A to OCEC1C as turbines of 376.6 MW feeding one 593.3 MW steam turbine ([EPA letter, February 2025](https://www.epa.gov/system/files/documents/2025-04/okeechobee_clean_energy_center_oris_60345_final_response_feb_2025.pdf)), and a third-party profile reports about 12 TWh in its latest year ([gridinfo](https://www.gridinfo.com/plant/okeechobee-clean-energy-center/60345)). Its three CEMS units are unmatched in PUDL's crosswalk in every report year from 2019 to 2024. A search of PUDL's issues for "60345" on 7 November 2026 returned nothing.
- **Tait (EPA 55248, EIA 2847)** is one plant in EIA's data and two in EPA's, as EPA's eGRID documentation notes; the unit and generator ids differ only by the `CT`/`GT` prefix.
- **Frontera (55098)** is a 2-on-1 combined cycle near Mission, Texas, with two 172 MW GE 7FA turbines and a 185 MW steam turbine, per [Power Technology](https://www.power-technology.com/data-insights/power-plant-profile-frontera-power-station-us/) and [EverGen Power](https://evergenpwr.com/portfolio/frontera/), matching the EIA rows. It sold its output into Mexico from October 2016 until it reconnected to ERCOT in June 2023 ([Houlihan Lokey](https://hl.com/about-us/transactions/new-frontera-holdings/)). Its CEMS units `1` and `2` are unmatched in every report year from 2018 to 2024; in 2018 to 2022 none of its EIA generators is an operating candidate, and in 2023 and 2024 all three are.
- **The one unique pair is at plant 6061**: unit `3` (591 MW peak) to `MOR2` (402 MW CT). OGE maps unit `3` to both `MOR2` and the steam generator `MOR1`, which fits a 1-on-1 combined cycle better than our single row. The size rule's one "find" is therefore half right.
- So the size rule is a poor pairing tool but a usable alarm: every unit it flagged in 2024 is at a plant whose whole block is missing from PUDL's crosswalk, and Open Grid Emissions had already fixed 4 of the 5 plants by hand.

## Proposed rows, for a person to check

For Frontera only, in the form Open Grid Emissions uses for the other combined cycles above. Which turbine belongs to which CEMS unit is our assumption from the matching numbers; no person has checked it.

| plant_id_epa | emissions_unit_id_epa | plant_id_eia | generator_id |
|---|---|---|---|
| 55098 | 1 | 55098 | GEN1 |
| 55098 | 1 | 55098 | GEN3 |
| 55098 | 2 | 55098 | GEN2 |
| 55098 | 2 | 55098 | GEN3 |

The other four plants' rows are already in Open Grid Emissions' table; whether PUDL should carry them too (as [pudl#5439](https://github.com/catalyst-cooperative/pudl/issues/5439) plans for OGE's manual table) is PUDL's decision.

## Limits

- A size match is a lead, not proof. A CEMS unit can serve several generators and a generator can be fed by several units; the combined cycles above show how the rule breaks.
- The yearly CEMS table is PUDL's estimate over a trailing window, so a peak may come from an earlier year, and units with too little history may be missing.
- "Unmatched" means no row in PUDL's crosswalk for that year; Open Grid Emissions adds its own rows on top, so a unit unmatched here may be covered there.
- PUDL's tables change nightly; this run read the builds named above. Nothing from PUDL or Open Grid Emissions is stored here except the derived list below.
- No person has checked the code or the results by hand.

## Files

- [`data/xwpair-units-2018-2024.csv`](../data/xwpair-units-2018-2024.csv) (1867 rows): every unmatched CEMS unit of every report year with its class, candidates and OGE's generators, as job xwpair-v1 wrote it, CC BY 4.0, derived from PUDL (CC BY 4.0, Catalyst Cooperative) and Open Grid Emissions' manual crosswalk (MIT).
- [`tools/xwpair/xwpair.py`](../tools/xwpair/xwpair.py) 0.1.0, its tests and the plan-gated fetch; the plan: [xwpair-plan.md](xwpair-plan.md).
