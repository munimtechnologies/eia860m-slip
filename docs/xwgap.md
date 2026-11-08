# CEMS units with load, no crosswalk row and nothing to link to: why? (result)

Result of pre-registration xwgap-1 ([plan](xwgap-plan.md), commit c4bdc1a, published 8 November 2026 at 02:43 UTC, before any data was read). MV2 of Munim, Inc., 8 November 2026; made with AI agents working in MV2's name; no person has checked these results by hand. CC BY 4.0; code Apache-2.0.

**All three gates held; 2 of the 6 predictions held and 4 failed.** In report year 2024, PUDL's crosswalk (`core_epa__assn_eia_epacamd`) has no row for 75 CEMS units that have a peak load and no unlinked operating combustion generator at their EIA plant. We expected most of them to sit at plants whose generators are all already linked to other units (P1). They do not: **62 of the 75 (83%) are at EIA plants with no EIA-860 generator row at all in 2024**, 3 are at a plant whose generators carry no operating status, and only 10 are at plants where every operating combustion generator is already linked.

Read after scoring (below): the 2024 jump, from 53 such units to 75, comes from the "absent" group (36 to 62), while all_linked fell from 14 to 10. PUDL's yearly CEMS table gives each report year a three-year trailing window, so a unit at a plant that closed in 2022 or 2023 can still have a 2024 row. W. H. Zimmer (EIA 6019, 1,426 MW, retired May 2022) is one of them. Whether retirement explains the absent group as a whole is the subject of a new pre-registered check, [xwstale-1](xwstale-plan.md).

## How it ran

- Job xwgap-v1 ran on 8 November 2026 (12:28 to 12:31 UTC). It first checked that the plan was live (it was, at the first poll, 12:30:08 UTC), then downloaded the committed `tools/xwgap/xwgap.py` 0.1.0 (md5 f64238c37b2c6cd7eb1bbe91f6404635) and its tests (md5 029ec84bb995cecf201e4ebfdcddd2f5); all 15 unit tests passed. Python 3.12.15, polars 2.1.0.
- **Crosswalk:** PUDL nightly `core_epa__assn_eia_epacamd`, 190,240 bytes, md5 420d50a7e4d066d29eee909eab73d932, 44,833 rows, Last-Modified 8 November 2026 08:13:35 GMT (the same bytes as the 5 November build xwpair-1 read).
- **CEMS units:** PUDL nightly `out_epacems__yearly_operational_characteristics`, 3,298,243 bytes, md5 a0a3345e0f0d143bf216f2323548a8d6, 118,117 rows, Last-Modified 8 November 2026 08:16:14 GMT; report years 2018 to 2024; 4,215 CEMS units in 2024.
- **EIA-860:** PUDL nightly `core_eia860__scd_generators`, 7,718,170 bytes, md5 6c4372366df319de1888d8fc6ea1ec0e, 667,073 rows, Last-Modified 8 November 2026 08:13:25 GMT.
- **Open Grid Emissions:** `epa_eia_crosswalk_manual.csv` at commit `e6d1e3f` (the head of [open-grid-emissions#476](https://github.com/singularity-energy/open-grid-emissions/pull/476)), 45,943 bytes, md5 d1275db58bd4cc9767c9ec0548d47ef7; 729 rows with a plant and unit id, every row whatever its note.

## Scores

N = 75 gap units in 2024, at 23 EIA plants.

| Bar | Probability given | Result | What the data shows (2024) |
|---|---|---|---|
| G1 | gate | held | Every column present; newest report year 2024; 4,215 CEMS units (at least 2,000 needed) |
| G2 | gate | held | 75 gap units (at least 40 needed) |
| P1 | 45% | failed | all_linked 10, absent 62, not_operating 3: absent is the most common reason, not all_linked |
| P2 | 40% | held | 62 of 75 gap units (82.7%) are absent; at least 20% were needed |
| P3 | 50% | held | 6 of the 10 all_linked gap units (60%) have a linked generator that fits their peak; at least half were needed |
| P4 | 35% | failed | 3 gap units have a same-id generator at their plant; at least 10 were needed |
| G3 | gate | held | 729 rows in OGE's file (at least 150 needed) |
| P5 | 35% | failed | OGE's manual table has a row for 10 of 75 gap units (13.3%); at least 25% were needed |
| P6 | 70% | failed | 37 of 75 gap units (49.3%) were also unmatched in 2023; at least 70% were needed |

**Why P1, P4 and P6 failed.** The plan assumed the gap was mostly a linking problem at working plants. Most of it is not: 62 of the 75 units are at EIA plants that have no generator row in PUDL's 2024 EIA-860 table, so there is nothing at the plant to link to, same-id or otherwise. P6 failed for a related reason: 38 of the 2024 gap units were not among 2023's unmatched units (they were either linked in 2023 or not in 2023's CEMS table), and 35 of those 38 are absent units at three plants (563, 2866, 55243) that have no EIA-860 generator row in 2024.

**Why P5 failed.** Open Grid Emissions' hand-made table covers exactly the 10 all_linked units and none of the 65 absent or not_operating ones. The bars are reported as failed and are not re-scored.

## Gap units by year

| Report year | Gap units | Absent | Not operating | All linked | All linked with a fit | Same-id | In OGE's table | Unmatched the year before | EIA plants |
|---|---|---|---|---|---|---|---|---|---|
| 2018 | 24 | 17 | 1 | 6 | 2 | 0 | 13 | n/a | 11 |
| 2019 | 34 | 23 | 4 | 7 | 2 | 4 | 14 | 18 | 17 |
| 2020 | 41 | 26 | 2 | 13 | 6 | 1 | 16 | 25 | 23 |
| 2021 | 46 | 22 | 6 | 18 | 11 | 6 | 22 | 21 | 26 |
| 2022 | 44 | 21 | 2 | 21 | 11 | 1 | 21 | 35 | 27 |
| 2023 | 53 | 36 | 3 | 14 | 9 | 3 | 15 | 23 | 28 |
| 2024 | 75 | 62 | 3 | 10 | 6 | 3 | 10 | 37 | 23 |

## Every 2024 gap unit, by plant

In every 2024 row the EIA plant id equals the EPA plant id, and no EPA plant links to a second EIA plant.

| EIA plant | CEMS units | 2024 peaks (MW) | Reason | Leads | In OGE's table | Unmatched in 2023 |
|---|---|---|---|---|---|---|
| 315 | CT1, CT2 | 348, 407 | all_linked | generators 3, 4, 5 fit; linked to units 3, 4, 5 | yes | yes |
| 335 | CT1, CT2 | 352, 352 | all_linked | no fit | yes | yes |
| 613 | PFL7A, PFL7B | 814, 753 | all_linked | no fit (35 generators at the plant) | yes | yes |
| 7063 | \*\*1 | 109 | all_linked | generators 2 to 5 fit; linked to units \*\*2 to \*\*5 | yes | yes |
| 55641 | CT-03, CT-04 | 379, 368 | all_linked | generator STG1 fits; linked to CT-01 and CT-02 | yes | yes |
| 55699 | 2 | 61 | all_linked | generator 1 fits; linked to unit 1 | yes | yes |
| 356 | 5, 6, 8 | 183, 179, 465 | not_operating | same-id generators 5, 6, 8; no status given for any of the 3 | no | no |
| 563 | 11A, 11B, 12A, 12B, 13A, 13B, 14A, 14B | 24, 24, 24, 24, 23, 23, 24, 24 | absent | none | no | no |
| 856 | 2, 3 | 218, 297 | absent | none | no | yes |
| 887 | 1, 2, 3, 4, 5, 6 | 169, 175, 176, 170, 177, 174 | absent | none | no | yes |
| 1642 | CTG1, CTG2 | 46, 46 | absent | none | no | yes |
| 2401 | 35001 | 81 | absent | none | no | yes |
| 2836 | 12, CT10 | 657, 32 | absent | none | no | yes |
| 2866 | 5, 6, 7 | 254, 658, 655 | absent | none | no | no |
| 6019 | 1 | 1313 | absent | none | no | yes |
| 8226 | 1 | 570 | absent | none | no | yes |
| 10099 | 1001 | 141 | absent | none | no | yes |
| 50385 | 1001, 2001 | 68, 74 | absent | none | no | yes |
| 52056 | 4 | 35 | absent | none | no | yes |
| 55243 | CT2-1A, CT2-1B, CT2-2A, CT2-2B, CT2-3A, CT2-3B, CT2-4A, CT2-4B, CT3-1A, CT3-1B, CT3-2A, CT3-2B, CT3-3A, CT3-3B, CT3-4A, CT3-4B, CT4-1A, CT4-1B, CT4-2A, CT4-2B, CT4-3A, CT4-3B, CT4-4A, CT4-4B | 23 each | absent | none | no | no |
| 59073 | 214JA, 214JB, GT501A, GT501B | 18, 20, 96, 96 | absent | none | no | yes |
| 880079 | 37, 38 | 30, 28 | absent | none | no | yes |
| 880102 | 1, 2 | 260, 260 | absent | none | no | yes |

## What else the rows show (read after scoring, not pre-registered)

- **The trailing window.** PUDL's [methodology page](https://docs.catalyst.coop/pudl/en/nightly/methodology/operational_characteristics.html) says each report year of `out_epacems__yearly_operational_characteristics` uses "the three most recently completed calendar years", so 2024 relies on 2022 to 2024. A unit that ran only in 2022 can therefore have a 2024 row and a 2024 peak. EIA plant 6019 is W. H. Zimmer in Ohio, a 1,425.6 MW coal plant retired in May 2022 ([Wikidata](https://www.wikidata.org/wiki/Q8010688), citing EIA-860M; [Wikipedia](https://en.wikipedia.org/wiki/William_H._Zimmer_Power_Station)). It is an absent gap unit in both 2023 and 2024, and its peak falls from 1,427 MW (window 2021 to 2023) to 1,313 MW (window 2022 to 2024), as it would if only its last months were left in the window. EIA plant 55243 is Astoria Gas Turbines in Queens, New York ([GridInfo](https://www.gridinfo.com/plant/astoria-gas-turbines/55243)): its 24 units are absent gap units in 2024 and were not unmatched in 2023. We have not checked when each of the 16 absent plants stopped running. If retirement explains most of them, the rising yearly count (24 in 2018, 75 in 2024) says more about which units the yearly table keeps than about the crosswalk.
- **EPA-only plant ids.** Plants 880079 and 880102 are absent in every report year from 2018 to 2024. Codes beginning with 88 are ones EPA's Clean Air Markets Division assigns when EIA has none ([Envirofacts definition](https://enviro.epa.gov/enviro/EF_METADATA_HTML.ef_metadata_page?p_column_name=PLANT_CODE_INDICATOR&p_table_name=V_GHG_EMITTER_FACILITIES&p_topic=IGMS); EPA's [crosswalk README](https://github.com/USEPA/camd-eia-crosswalk) says many units that do not send power to the grid have such ids). These 4 units may have no EIA generator to match at all.
- **Open Grid Emissions already covers the linking cases.** All 10 all_linked units of 2024 have rows in OGE's hand-made table, and none of the 65 others do. So the part of the gap a person could fix by adding a crosswalk row is already handled downstream, and the rest has nothing in EIA-860 to point to.
- **The all_linked units are long-standing.** Every one of the 10 was also unmatched in 2023. Plants 315, 335, 7063, 55641 and 55699 have gap units in every year from 2020 (7063 and 55699 from 2018).

## What happens next

- [xwstale-1](xwstale-plan.md) (pre-registered the same day, before its data is read) looks up when the generators of every absent and not_operating plant were last listed in EIA-860 and when they retired.
- This result and the list below go to PUDL as a comment on our open issue [pudl#5752](https://github.com/catalyst-cooperative/pudl/issues/5752) once xwstale-1 is scored, saying plainly that no person has checked them.

## Limits

- A reason is a description, not a diagnosis. "Absent" means no generator row for that EIA plant id in PUDL's 2024 `core_eia860__scd_generators`; it does not say why.
- An all_linked unit with a fit may share a generator with another unit (common in combined cycles and shared stacks), or may be a different unit altogether.
- "Unmatched in 2023" is false both for units linked in 2023 and for units not in 2023's CEMS table; this check does not tell them apart.
- PUDL's tables change nightly; this run read the builds named above. Nothing from PUDL or Open Grid Emissions is stored here except the derived list below.
- No person has checked the code or the results by hand.

## Files

- [`data/xwgap-units-2018-2024.csv`](../data/xwgap-units-2018-2024.csv) (317 rows): every gap unit of every report year with its reason and leads, as job xwgap-v1 wrote it, CC BY 4.0, derived from PUDL (CC BY 4.0, Catalyst Cooperative) and Open Grid Emissions' manual crosswalk (MIT). It is meant as a regression list to re-run on each new PUDL build.
- [`tools/xwgap/xwgap.py`](../tools/xwgap/xwgap.py) 0.1.0, its tests and the plan-gated fetch; the plan: [xwgap-plan.md](xwgap-plan.md).
