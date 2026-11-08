# Gap units at plants missing from EIA-860: retired before the report year? (result)

Result of pre-registration xwstale-1 ([plan](xwstale-plan.md), commit 22e8ad3, published 8 November 2026 at 12:46 UTC, before any data was read). MV2 of Munim, Inc., 8 November 2026; made with AI agents working in MV2's name; no person has checked these results by hand. CC BY 4.0; code Apache-2.0.

**All three gates held; 3 of the 5 predictions held and 2 failed.** [xwgap-1](xwgap.md) found 65 CEMS units in report year 2024 with a peak load, no row in PUDL's crosswalk (`core_epa__assn_eia_epacamd`) and no EIA-860 generator they could be linked to, because their EIA plant had no generator row that year ("absent", 62) or no operating one ("not_operating", 3). **33 of the 65 (50.8%) are at plants whose combustion generators had all retired before 2024, every one of them in 2022 or 2023**, inside the three-year trailing window of PUDL's yearly CEMS table. We expected at least 60% (P1). The rule missed that bar because of one plant: Astoria Gas Turbines (EIA 55243, 24 units), where 1 of the 21 combustion generators in its last EIA-860 listing carries no retirement date.

Read after scoring (below): with Astoria, whose closure on 1 May 2023 was reported in the press, the rest of the 2024 group is 8 units at 3 plants that EIA does not list as power plants today: the Cove Point LNG Terminal in Maryland (EIA 59073, a non-EGU site in EPA's lists, last listed in EIA-860 for 2020) and two plants with EPA-only 88 ids. So nothing in the 2024 "absent" group looks like a crosswalk row someone forgot.

## How it ran

- Job xwstale-v1 ran on 8 November 2026 (17:39 to 17:43 UTC). It first checked that the plan was live (it was, at the first poll, 17:41:18 UTC), then downloaded the committed `tools/xwstale/xwstale.py` 0.1.0 (md5 7edad4f7ef506b1ec9bae56cfd7d8cb0) and its tests (md5 fc34515c864e1a38db8a952f094a11f0); all 16 unit tests passed. Python 3.12.15, polars 2.1.0.
- **Population:** `data/xwgap-units-2018-2024.csv` from this repository's main branch, 18,669 bytes, md5 797c74d1722c533ae0c7f266148f05c5 (317 rows; 228 of them absent or not_operating).
- **EIA-860:** PUDL nightly `core_eia860__scd_generators`, 7,718,170 bytes, md5 6c4372366df319de1888d8fc6ea1ec0e, 667,073 rows, Last-Modified 8 November 2026 08:13:25 GMT (the same bytes xwgap-1 read); report years 2001 to 2026.

## Scores

N = 65 absent and not_operating gap units in 2024, at 17 EIA plants.

| Bar | Probability given | Result | What the data shows |
|---|---|---|---|
| G1 | gate | held | Every column present; report years 2001 to 2026 |
| G2 | gate | held | 317 rows; 65 absent or not_operating units in 2024 |
| G3 | gate | held | W. H. Zimmer (EIA 6019, unit 1, 2024) is retired_before, latest retirement 2022 |
| P1 | 60% | failed | 33 of 65 units (50.8%) are retired_before; at least 60% (39 units) were needed |
| P2 | 55% | held | 33 of the 33 retired_before units (100%) had their latest retirement in 2022 or 2023; at least 90% were needed |
| P3 | 60% | held | 4 of 65 units are never_listed; at most 10 were allowed |
| P4 | 40% | failed | 11 of the 35 absent units at plants 563, 2866 and 55243 are retired_before with latest retirement 2023; the 24 at 55243 are other (undated) |
| P5 | 40% | held | retired_before share: 2019 23 of 27, 2020 21 of 28, 2021 14 of 28, 2022 13 of 23, 2023 30 of 39; at least half was needed each year |

**Why P1 and P4 failed.** The rule calls a plant retired only if every combustion generator in its last EIA-860 listing has a retirement date. At Astoria Gas Turbines (EIA 55243), last listed for 2023, 20 of the 21 combustion generators have one and none falls after 2024, but one has no retirement date on that row or any earlier row. So all 24 of its CEMS units are classed other (cause: undated). They are 24 of the 65 units, enough to sink P1, and all of P4 depended on them. The bars are reported as failed and are not re-scored.

P5 held at the bar in 2021: exactly 14 of 28.

## Classes by report year

"Inside the window" means the latest retirement fell in the report year or one of the two years before it. "Listed again later" means the EIA plant has generator rows in PUDL's EIA-860 table for a year after the report year.

| Report year | Units | never_listed | retired_before | retired_in_year | other | retired_before inside the window | At plants listed again later | EIA plants |
|---|---|---|---|---|---|---|---|---|
| 2018 | 18 | 4 | 14 | 0 | 0 | 14 | 14 | 8 |
| 2019 | 27 | 4 | 23 | 0 | 0 | 21 | 23 | 13 |
| 2020 | 28 | 4 | 21 | 0 | 3 | 19 | 24 | 16 |
| 2021 | 28 | 4 | 14 | 0 | 10 | 12 | 20 | 17 |
| 2022 | 23 | 4 | 13 | 0 | 6 | 11 | 15 | 16 |
| 2023 | 39 | 4 | 30 | 0 | 5 | 30 | 31 | 19 |
| 2024 | 65 | 4 | 33 | 0 | 28 | 33 | 57 | 17 |

## Every 2024 unit, by plant

| EIA plant | CEMS units | xwgap reason | Class | Last EIA-860 listing | Combustion generators | Undated | Latest retirement | Name (where we looked it up) |
|---|---|---|---|---|---|---|---|---|
| 356 | 3 | not_operating | retired_before | 2024 | 3 | 0 | 2023 | |
| 563 | 8 | absent | retired_before | 2023 | 4 | 0 | 2023 | |
| 856 | 2 | absent | retired_before | 2023 | 2 | 0 | 2022 | |
| 887 | 6 | absent | retired_before | 2022 | 6 | 0 | 2022 | |
| 1642 | 2 | absent | retired_before | 2022 | 6 | 0 | 2022 | |
| 2401 | 1 | absent | retired_before | 2022 | 13 | 0 | 2022 | |
| 2836 | 2 | absent | retired_before | 2022 | 4 | 0 | 2022 | |
| 2866 | 3 | absent | retired_before | 2023 | 12 | 0 | 2023 | |
| 6019 | 1 | absent | retired_before | 2022 | 1 | 0 | 2022 | W. H. Zimmer (gate G3) |
| 8226 | 1 | absent | retired_before | 2022 | 1 | 0 | 2022 | |
| 10099 | 1 | absent | retired_before | 2022 | 2 | 0 | 2022 | |
| 50385 | 2 | absent | retired_before | 2022 | 3 | 0 | 2022 | |
| 52056 | 1 | absent | retired_before | 2022 | 2 | 0 | 2022 | |
| 55243 | 24 | absent | other | 2023 | 21 | 1 | none | Astoria Gas Turbines, Queens, New York |
| 59073 | 4 | absent | other | 2020 | 9 | 9 | none | Cove Point LNG Terminal, Maryland |
| 880079 | 2 | absent | never_listed | none | 0 | 0 | none | EPA-only id |
| 880102 | 2 | absent | never_listed | none | 0 | 0 | none | EPA-only id |

Every unit of every year, with its class, is in [`data/xwstale-units-2018-2024.csv`](../data/xwstale-units-2018-2024.csv).

## What else the rows show (read after scoring, not pre-registered)

- **Astoria Gas Turbines closed in 2023.** NRG's peaker plant in Queens shut down on 1 May 2023 under New York's peaker NOx rule ([T&D World](https://www.tdworld.com/overhead-transmission/article/21265433/new-con-edison-transmission-line-energized-to-support-grid-reliability-and-reduce-emissions)). Its 24 CEMS units were linked or absent from 2023's CEMS table (none was unmatched in 2023, see xwgap.md) and are absent gap units in 2024, the first report year after the closure. We have not looked up which of its 21 generators has no retirement date, or why. If Astoria is counted as retired, 57 of the 65 units of 2024 (87.7%) sit at plants that retired in 2022 or 2023. This is a reading after scoring, not a re-score.
- **Cove Point is an LNG terminal.** EPA's NOx SIP Call support document lists units 214JA and GT501A at Cove Point LNG Terminal, facility 59073, Calvert County, Maryland, as non-EGU units ([EPA-HQ-OAR-2018-0595-0030](https://downloads.regulations.gov/EPA-HQ-OAR-2018-0595-0030/content.pdf)). PUDL's EIA-860 table lists 9 combustion generators there up to 2020, none with a retirement date, and no row in any later year. Its 4 CEMS units are absent gap units from 2021 to 2024. We have not checked why the plant left EIA-860.
- **EPA-only ids.** Plants 880079 and 880102 are never_listed in every year from 2018 to 2024, as expected for ids EPA assigns when EIA has none (see xwgap.md).
- **Frontera is "retired" in EIA-860 but kept running.** Frontera (EIA 55098) is classed retired_before in 2018 to 2022, with its 3 combustion generators retired in 2016 and its last listing in 2016. The plant kept running and sold its power into Mexico in those years (see [xwpair.md](xwpair.md)), and its generators are listed as operating again from 2023. In 2019 to 2022 its 2 units are the only retired_before units whose retirement falls outside the trailing window. So a retirement date in EIA-860 can mean "left the U.S. grid", not "stopped burning fuel"; the plan's first limit says the same.
- **Plants come back.** 57 of the 65 units of 2024 are at plants that have no generator row in PUDL's 2024 EIA-860 table but do have rows for 2025 or 2026; Zimmer, for example, has rows up to 2022 and again after 2024, and none for 2023 or 2024. We have not checked where PUDL's later rows come from or why the plants are missing in between. Anyone using "absent from EIA-860" as a sign of retirement should know that.
- **Not operating, undated.** Earlier years' other units are at plants whose generators have no operating status and some no retirement date: 60925 (2020), 10350 and 63259 (2021), 60910 (2021 to 2023), 6061 (2022), and absent plant 2378 (2020). We have not looked them up.

## What this means for the crosswalk

The units in the 2024 gap that a person could fix by adding a crosswalk row are the 10 all_linked units xwgap-1 found, and Open Grid Emissions' hand-made table already covers all 10. The 65 others are retired plants still inside the trailing window (33, or 57 counting Astoria), an LNG terminal EPA lists as non-EGU (4) and EPA-only ids (4). So the rise in the yearly count of unmatched units, from 24 in 2018 to 75 in 2024, mostly reflects which units the yearly table keeps, not a crosswalk that is getting worse. Whether retired units belong in the yearly table, or in a match-rate count, is PUDL's decision.

## What happens next

- This result, xwgap-1's list and a correction to our issue go to PUDL as one comment on [pudl#5752](https://github.com/catalyst-cooperative/pudl/issues/5752), saying plainly that no person has checked them. The correction: the issue says the Chalk Point SMECO link stands in every report year from 2018 to 2024, but PUDL has no SMECO row in 2021 and 2022, and Open Grid Emissions maps SMECO to EIA 65285/GT1 for those two years (see [xwpudl.md](xwpudl.md)).
- The retirement class of each gap unit goes into the [cems-eia-crosswalk](https://github.com/munimtechnologies/cems-eia-crosswalk) agent skill, so its checker can say whether a flagged unit's plant had already retired.

## Limits

- A retirement date in EIA-860 is what the plant reported, not proof the unit stopped burning fuel (Frontera above). CEMS hours inside the window are not checked here.
- The rule is strict: one undated combustion generator puts a whole plant in other, as at Astoria.
- A plant can change its EIA plant id; a unit at a renumbered plant would look never_listed or retired here.
- The population is xwgap-1's list from PUDL's 8 November 2026 build; PUDL's tables change nightly, and this run read the build named above. Nothing from PUDL is stored here except the derived list.
- Plant names come from the sources linked above, not from PUDL, and were looked up only for the plants named.
- No person has checked the code or the results by hand.

## Files

- [`data/xwstale-units-2018-2024.csv`](../data/xwstale-units-2018-2024.csv) (228 rows): every absent and not_operating gap unit of every report year with its class, cause, last EIA-860 listing, number of combustion generators, undated generators and latest retirement year, as job xwstale-v1 wrote it. CC BY 4.0, derived from PUDL (CC BY 4.0, Catalyst Cooperative).
- [`tools/xwstale/xwstale.py`](../tools/xwstale/xwstale.py) 0.1.0, its tests and the plan-gated fetch; the plan: [xwstale-plan.md](xwstale-plan.md).
