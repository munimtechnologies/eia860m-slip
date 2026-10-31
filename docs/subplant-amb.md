# Naming the boiler behind PUDL's ambiguous CEMS crosswalk rows: scored

Status: scored against its pre-registration (docs/subplant-amb-plan.md, id subplant-amb-1). Both gates held and 3 of 4 predictions held; P2 missed. Written 31 October 2026. MV2 of Munim, Inc. (made with AI agents working in MV2's name; no person has checked these counts by hand). CC BY 4.0.

## What ran

The [plan](subplant-amb-plan.md) fixed the rule, two gates and four predictions before job subplant-amb-v1 ran (committed 31 October 2026 in 2eb405c). The job ran on 31 October 2026 (Python 3.12, pandas 2.3.3, pyarrow 26.0.0) with `tools/subplant-amb/subplant_amb.py` 0.1.0 (md5 2dec70ebe46e81d6fb2a1500f0e7e632) and `tools/subplant-gap/subplant_gap.py` 0.1.0 (md5 276817f5826157f3f2dc6a94f94c730f, as pinned). Its 6 unit tests passed, it found the plan live at its first poll (08:48:14Z) and finished at 08:48:43Z. It read a newer nightly build than subplant-gap-1 did, with all four tables last modified on 31 October 2026 at 08:10 GMT:

| Table | Rows | ETag |
|---|---|---|
| core_epa__assn_eia_epacamd | 44,833 | 420d50a7e4d066d29eee909eab73d932 |
| core_epa__assn_eia_epacamd_subplant_ids | 45,386 | ede6b149a95624546b9d83d28e3fb175 |
| core_eia860__assn_boiler_generator | 177,670 | 51f538af79158528909c30d4a732c74f |
| core_eia923__monthly_boiler_fuel | 1,898,779 | bbe16105da4ecb5b283f4a13227e0225 |

On this build subplant-gap-1's own counts came out the same as [published](subplant-gap.md) in every year from 2018 to 2024 (for 2024: 602 ambiguous subplants, 726 strict CEMS subplants with boilers, 27 gap boilers at 8 plants, 39,280,975 MMBtu).

## Scores

| | Expectation | Result |
|---|---|---|
| Gate G0 | four tables load; reused tool 0.1.0; 2024 qualifies | held: 2018-2024 qualify, md5 matches |
| Gate G1 | 2024: 580-625 ambiguous subplants and 6-10 strict gap plants | held: 602 and 8 |
| P1 (60%) | at least half of the 2024 ambiguous subplants are resolved | held: 442 of 602 (73.4%) |
| P2 (65%) | at least 60% of the 2024 ambiguous rows belong to a generator with no linked boiler of its own | **missed**: 35 of 1,631 (2.1%) |
| P3 (55%) | in the resolved subplants, the revised gap is under 1% of their linked boilers' heat input | held: 31,555,223 of 7,646,909,177 MMBtu (0.41%) |
| P4 (50%) | the name rule resolves at least 100 ambiguous rows in 2024 | held: 958 rows |

**P2.** The plan took its turbine pattern from a 2018 note that combined-cycle turbine generators were missing from EIA's boiler-generator associations. In the 2024 associations that PUDL serves, 1,596 of the 1,631 ambiguous rows (97.9%) have a generator with boilers of its own; at plant 3, for example, generator A1CT is linked to a boiler also called A1CT. What the ambiguous rows lack is the boiler id in the crosswalk row, not a boiler association. The prediction rested on an outdated source and is scored as missed.

## The 2024 rows by class

| Class | Rows | Share |
|---|---|---|
| covered (no candidate left) | 68 | 4.2% |
| single (one candidate, inferred) | 170 | 10.4% |
| name (one candidate with the unit's or generator's id, inferred) | 958 | 58.7% |
| unresolved | 435 | 26.7% |
| all ambiguous rows in subplants with linked boilers | 1,631 | |

Another 2,272 ambiguous rows sit in subplants with no linked boiler and are left out, as in subplant-gap-1.

## Every year

Gap and linked heat input in million MMBtu. "Before" is subplant-gap-1's strict count on this build; "after" adds the resolved subplants with their inferred boilers counted as matched. "Share" is the gap after over the linked heat input after.

| Year | Ambiguous rows | Covered | Single | Name | Unresolved | Ambiguous subplants | Resolved | Gap plants before | Gap plants after | Gap before | Gap after | Linked after | Share |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2018 | 1,661 | 67 | 179 | 956 | 459 | 617 | 445 | 11 | 33 | 47.4 | 74.8 | 19,843.6 | 0.38% |
| 2019 | 1,669 | 67 | 176 | 967 | 459 | 619 | 447 | 11 | 35 | 44.4 | 64.8 | 18,451.3 | 0.35% |
| 2020 | 1,648 | 67 | 169 | 961 | 451 | 613 | 442 | 11 | 36 | 40.6 | 65.0 | 16,569.9 | 0.39% |
| 2021 | 1,667 | 70 | 174 | 963 | 460 | 617 | 444 | 8 | 30 | 38.3 | 55.3 | 17,518.2 | 0.32% |
| 2022 | 1,645 | 68 | 171 | 965 | 441 | 608 | 444 | 8 | 33 | 37.6 | 63.1 | 17,471.5 | 0.36% |
| 2023 | 1,636 | 68 | 170 | 963 | 435 | 605 | 444 | 9 | 31 | 38.4 | 68.1 | 16,380.5 | 0.42% |
| 2024 | 1,631 | 68 | 170 | 958 | 435 | 602 | 442 | 8 | 33 | 39.3 | 70.8 | 16,375.5 | 0.43% |

The rule resolves between 72.0% and 73.4% of the ambiguous subplants in every year.

## The 2024 gap subplants added by the rule

These are the resolved subplants that still have a gap boiler once the inferred boilers count as matched. Heat input in MMBtu; "main fuel" is the EIA energy source code with the most heat input in the subplant's largest gap boiler. The 9 strict gap subplants of subplant-gap-1 are unchanged and not repeated here.

| EIA plant | Subplant | Boilers | Gap boilers | Heat input | Gap heat input | Gap share | Main fuel | Gap boiler ids |
|---|---|---|---|---|---|---|---|---|
| 55259 | 1 | 4 | 2 | 26,491,699 | 5,394,553 | 20.4% | NG | 1100; 2100 |
| 60589 | 1 | 4 | 2 | 49,687,564 | 3,859,926 | 7.8% | NG | HRSG1B; HRSG1A |
| 628 | 4 | 4 | 1 | 41,689,288 | 2,176,118 | 5.2% | NG | CC2BA |
| 55518 | 1 | 6 | 3 | 33,496,671 | 2,039,136 | 6.1% | NG | 3; 1; 2 |
| 628 | 2 | 4 | 1 | 41,719,449 | 2,009,884 | 4.8% | NG | CC1BA |
| 55089 | 1 | 6 | 3 | 37,574,961 | 1,998,845 | 5.3% | OG | 20F101; 20F301; 20F201 |
| 2406 | 4 | 4 | 2 | 19,532,180 | 1,871,501 | 9.6% | NG | 22; 21 |
| 8031 | 1 | 4 | 2 | 18,544,933 | 1,664,154 | 9.0% | NG | 1; 2 |
| 1403 | 5 | 4 | 2 | 26,050,562 | 1,270,194 | 4.9% | NG | 6AHRSG; 6BHRSG |
| 56349 | 2 | 4 | 2 | 13,245,693 | 1,191,695 | 9.0% | NG | HRSG4; HRSG3 |
| 55933 | 1 | 4 | 2 | 8,425,894 | 1,145,120 | 13.6% | NG | 4H0401; 3H0301 |
| 54537 | 1 | 4 | 2 | 14,227,549 | 1,078,620 | 7.6% | NG | HRSGB; HRSGA |
| 55418 | 1 | 4 | 2 | 15,100,856 | 856,046 | 5.7% | NG | 1H1100; 1H2100 |
| 2070 | 1 | 3 | 1 | 7,135,468 | 788,500 | 11.1% | NG | HRSG1 |
| 56349 | 1 | 4 | 2 | 12,838,119 | 765,571 | 6.0% | NG | HRSG1; HRSG2 |
| 1391 | 1 | 6 | 1 | 14,309,843 | 612,185 | 4.3% | OG | 9 |
| 2070 | 2 | 3 | 1 | 6,365,955 | 573,465 | 9.0% | NG | HRSG2 |
| 7242 | 2 | 10 | 1 | 42,549,130 | 519,742 | 1.2% | NG | 2A |
| 2406 | 2 | 4 | 2 | 15,737,755 | 515,017 | 3.3% | NG | 12; 11 |
| 55137 | 1 | 6 | 3 | 35,917,611 | 354,466 | 1.0% | NG | 201; 101; 301 |
| 55271 | 1 | 6 | 2 | 12,892,190 | 336,668 | 2.6% | NG | HRSG2; HRSG1 |
| 55270 | 1 | 14 | 1 | 17,102,928 | 234,196 | 1.4% | NG | HRSG7 |
| 55177 | 1 | 4 | 2 | 21,680,256 | 90,034 | 0.4% | NG | HRSG B; HRSG A |
| 56350 | 2 | 4 | 2 | 10,927,328 | 77,873 | 0.7% | NG | HRSG4; HRSG3 |
| 56046 | 1 | 2 | 1 | 11,718,875 | 60,920 | 0.5% | NG | HRSG2 |
| 56350 | 1 | 4 | 2 | 9,229,391 | 58,459 | 0.6% | NG | HRSG2; HRSG1 |
| 7784 | 1 | 2 | 1 | 128,192 | 10,537 | 8.2% | NG | HRSG |
| 7546 | 1 | 2 | 1 | 105,610 | 1,090 | 1.0% | NG | HRSG1 |
| 7238 | 3 | 2 | 1 | 10,832,542 | 402 | 0.0% | NG | MS3B |
| 55406 | 1 | 5 | 1 | 11,813,783 | 303 | 0.0% | NG | AUX |

These 30 subplants at 25 plants hold the 51 gap boilers and 31,555,223 MMBtu that the rule adds. By the boilers' own main fuel that is natural gas 29.5 and other gas 2.0 million MMBtu. None of the 30 has a gap share above 50%; the largest is 20.4%. In 14 of them a gap boiler id contains "HRSG", the heat-recovery boiler of a combined-cycle block, whose duct burners may report to CEMS under a turbine's EPA unit; no source here confirms that unit by unit.

## The unresolved rows

435 rows in 160 subplants stay unresolved in 2024. The job's output lists 40 of them (the first 40 in its row order). A common shape among them: a generator whose id suggests a combined-cycle block's steam turbine (ST1 at plant 260, MV3C and MV4C at plant 358, 3ST at plant 609, 5ST at plants 617 and 619) is tied to each turbine's EPA unit, and its candidates are all the block's turbine and heat-recovery boilers, so no single boiler can be picked. At plants 260 and 358 (8 of the 40 rows) the same EPA unit also has a row for its own turbine generator that the name rule resolved, so those rows add no boiler the unit lacks. A second rule that sets such rows aside could resolve more subplants; it was not tested here and would need its own pre-registration.

## What it shows

- A short fixed rule names one boiler for 1,128 of the 1,631 ambiguous rows of 2024 (69.2%; single 170, name 958) and resolves 442 of the 602 ambiguous subplants, at a similar share in every year from 2018 to 2024.
- Once their boilers are named, the resolved subplants look covered by CEMS: their gap is 0.41% of their linked heat input in 2024. The strict count grows from 726 to 1,168 subplants and from 8 to 33 gap plants, but its gap share stays under half a percent (0.45% before, 0.43% after).
- With the ambiguous subplants counted in, subplant-gap-1 found an apparent gap of 9,536.5 million MMBtu. Once the rule names their boilers, the 442 resolved subplants keep a gap of only 31.6 million MMBtu, so for them the apparent gap was mostly missing boiler ids rather than fuel outside CEMS (their part of the 9,536.5 million was not counted here).
- For issue [#5681](https://github.com/catalyst-cooperative/pudl/issues/5681): a `boiler_id` column in `core_epa__assn_eia_epacamd_subplant_ids` could be filled for most ambiguous rows from PUDL's own tables, as a flagged inference, with about a quarter of rows left blank. Whether PUDL wants inferred ids is a choice for its maintainers.

## Limits

- An inferred boiler is a candidate for PUDL to check, not EPA's or EIA's own link. The name rule uses ids only; no capacities, dates or stack data were read.
- P2 rested on a 2018 description of EIA's associations that no longer fits PUDL's 2024 table; the miss says nothing about the rule itself.
- Heat input from generators without boilers is outside this count. No CO2 is estimated.
- One nightly build (31 October 2026), not a pinned release; plant names were not looked up here.
- PUDL's data (CC BY 4.0) was downloaded at run time and is not stored here.
