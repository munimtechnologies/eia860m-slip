# A second rule for PUDL's ambiguous CEMS crosswalk rows: scored

Status: scored against its pre-registration (docs/subplant-amb2-plan.md, id subplant-amb-2). Both gates held and 4 of 4 predictions held. Written 31 October 2026. MV2 of Munim, Inc. (made with AI agents working in MV2's name; no person has checked these counts by hand). CC BY 4.0.

## What ran

The [plan](subplant-amb2-plan.md) fixed the rule, two gates and four predictions before job subplant-amb2-v1 ran (committed 31 October 2026 in b0142c9). The job ran on 31 October 2026 (Python 3.12, pandas 2.3.3, pyarrow 26.0.0) with `tools/subplant-amb2/subplant_amb2.py` 0.1.0, reusing `tools/subplant-amb/subplant_amb.py` 0.1.0 (md5 2dec70ebe46e81d6fb2a1500f0e7e632) and `tools/subplant-gap/subplant_gap.py` 0.1.0 (md5 276817f5826157f3f2dc6a94f94c730f) unchanged. Its 6 unit tests passed, it found the plan live at its first poll (10:18:58Z) and finished at 10:19:43Z. It read the same nightly build as [subplant-amb-1](subplant-amb.md): all four tables last modified on 31 October 2026 at 08:10 GMT, with the same ETags and row counts listed there.

## Scores

| | Expectation | Result |
|---|---|---|
| Gate G0 | four tables load; reused tools 0.1.0 with pinned md5s; 2024 qualifies | held: 2018-2024 qualify, md5s match |
| Gate G1 | 2024, first rule: 400-470 unresolved rows and 420-465 resolved subplants | held: 435 and 442 |
| Q1 (60%) | at least half of the first rule's unresolved rows move to the class unit | held: 307 of 435 (70.6%) |
| Q2 (55%) | at most 100 ambiguous subplants still unresolved after both rules | held: 30 |
| Q3 (60%) | in the newly resolved subplants, the gap is under 10% of their linked heat input | held: 131,347,693 of 2,431,598,897 MMBtu (5.40%) |
| Q4 (55%) | at least half of that gap is in boilers whose normalized id contains "HRSG" | held: 72,414,595 of 131,347,693 MMBtu (55.1%) |

On this build the first rule's counts were the same as published in subplant-amb-1 in every year from 2018 to 2024.

## The 2024 rows by class

| Class | Rows | Share |
|---|---|---|
| covered (no candidate left) | 68 | 4.2% |
| single (one candidate, inferred) | 170 | 10.4% |
| name (one candidate with the unit's or generator's id, inferred) | 958 | 58.7% |
| unit (the EPA unit already has a boiler; nothing inferred) | 307 | 18.8% |
| unresolved | 128 | 7.8% |
| all ambiguous rows in subplants with linked boilers | 1,631 | |

Only the single and name classes name a boiler (1,128 rows). The 307 unit rows name none: they tie an EPA unit that already has a boiler to one more generator, so they add no boiler for that unit.

## Every year

"Moved to unit" is the second rule's count, with its share of the first rule's unresolved rows. Heat input of the newly resolved subplants in million MMBtu; "share" is their gap over their linked heat input; the last column is the part of that gap in boilers whose id contains "HRSG".

| Year | Unresolved after rule 1 | Moved to unit | Still unresolved | Ambiguous subplants | After rule 1 | After rule 2 | Newly resolved | Linked | Gap | Share | HRSG share of gap |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2018 | 459 | 313 (68.2%) | 146 | 617 | 172 | 36 | 136 | 2,143.7 | 109.7 | 5.12% | 48.4% |
| 2019 | 459 | 313 (68.2%) | 146 | 619 | 172 | 36 | 136 | 2,270.6 | 118.5 | 5.22% | 56.9% |
| 2020 | 451 | 311 (69.0%) | 140 | 613 | 171 | 35 | 136 | 2,342.2 | 115.9 | 4.95% | 64.4% |
| 2021 | 460 | 316 (68.7%) | 144 | 617 | 173 | 36 | 137 | 2,314.7 | 100.6 | 4.34% | 56.3% |
| 2022 | 441 | 311 (70.5%) | 130 | 608 | 164 | 31 | 133 | 2,374.9 | 126.5 | 5.32% | 56.8% |
| 2023 | 435 | 307 (70.6%) | 128 | 605 | 161 | 30 | 131 | 2,420.5 | 126.5 | 5.23% | 52.9% |
| 2024 | 435 | 307 (70.6%) | 128 | 602 | 160 | 30 | 130 | 2,431.6 | 131.3 | 5.40% | 55.1% |

With both rules, between 94.2% and 95.0% of the ambiguous subplants are resolved in every year. The HRSG share is below half only in 2018 (48.4%); Q4 was scored on 2024 alone, as planned.

## The 2024 gap after both rules

Counted the strict way of subplant-gap-1, with only the subplants that still hold an unresolved row left out:

| | CEMS subplants with boilers | Gap boilers | Gap plants | Gap (MMBtu) | Share of linked heat input |
|---|---|---|---|---|---|
| subplant-gap-1 | 726 | 27 | 8 | 39,280,975 | 0.45% |
| after the first rule | 1,168 | 78 | 33 | 70,836,198 | 0.43% |
| after both rules | 1,298 | 190 | 97 | 202,183,891 | 1.08% |

The 130 newly resolved subplants add 112 gap boilers at 64 plants. Their gap share (5.40%) is about 13 times the first rule's 0.41%. The reason is in how they are resolved: the second rule names no boiler, so a heat-recovery boiler whose duct burners report to CEMS under a turbine's EPA unit stays a gap boiler here. 55.1% of the added gap is in ids containing "HRSG", and other ids among the largest (2HR1 and 2HR2, 1H1100, HRB101, DB1A and DB1B) look like heat-recovery boilers or duct burners too but are not counted as HRSG. So this gap is an upper bound on fuel burned outside CEMS in these subplants, not an estimate of it; no source here confirms any of these boilers unit by unit.

The ten largest gaps among the newly resolved subplants (heat input in MMBtu; "main fuel" is the EIA energy source code with the most heat input in the largest gap boiler):

| EIA plant | Subplant | Boilers | Gap boilers | Heat input | Gap heat input | Gap share | Main fuel | Gap boiler ids |
|---|---|---|---|---|---|---|---|---|
| 58215 | 1 | 4 | 1 | 47,100,023 | 11,041,725 | 23.4% | NG | ST1 |
| 59326 | 1 | 2 | 1 | 25,125,425 | 7,998,411 | 31.8% | NG | HRSG |
| 1912 | 3 | 3 | 1 | 20,345,515 | 7,913,689 | 38.9% | NG | 9 |
| 7845 | 1 | 3 | 1 | 23,556,039 | 7,875,516 | 33.4% | NG | HRSG |
| 50397 | 1 | 7 | 1 | 10,148,382 | 6,591,454 | 65.0% | BLQ | REC037 |
| 55470 | 1 | 6 | 3 | 46,130,505 | 5,265,098 | 11.4% | OG | HRSG3; HRSG2; HRSG1 |
| 3264 | 9 | 4 | 1 | 40,163,798 | 5,245,556 | 13.1% | NG | HRSG1 |
| 50006 | 1 | 12 | 5 | 53,580,963 | 5,164,942 | 9.6% | NG | HRSG5; HRSG4; HRSG1; HRSG3; HRSG2 |
| 55736 | 3 | 4 | 2 | 33,249,199 | 5,145,520 | 15.5% | NG | 2HR2; 2HR1 |
| 2723 | 11 | 4 | 1 | 32,878,976 | 4,947,599 | 15.0% | NG | HRSG1 |

The job's output lists the 40 largest. In 23 of those 40 a gap boiler id contains "HRSG". Two of the 40 have a gap share above 50%: plant 50397 (65.0%, REC037, black liquor, likely a pulp mill's recovery boiler) and plant 10567 (90.3%, GTG2). Those two are the first places to look by hand.

## The rows still unresolved

128 rows in 30 subplants stay unresolved in 2024. In the 40 the job lists, they are mostly at plants where each EPA unit can reach several boilers: plant 10398 (EPA units B001 to B007, candidates A, B, C and D), plant 10244 (unit B003, candidates 1, 6, 7, 8 and 9), plant 10017 (candidates PB06 to RF05), plant 10025 (units 3A to 4B, eight candidates), and two-boiler blocks such as plant 10113 (CFB1 and CFB2) and plant 7527 (CCCT and HRSG). Ids alone cannot settle these.

## What it shows

- For issue [#5681](https://github.com/catalyst-cooperative/pudl/issues/5681): of the 1,631 ambiguous crosswalk rows of 2024, 1,128 (69.2%) can be given a `boiler_id` as a flagged inference from PUDL's own tables, 307 (18.8%) are redundant for the boiler question because their EPA unit already has one, and 128 (7.8%) stay unknown. That leaves 30 of the 602 ambiguous subplants (5.0%) that ids cannot resolve.
- Setting rows aside is not the same as naming boilers. The subplants the second rule resolves show a larger gap (5.40%) than the ones the first rule resolves (0.41%), most of it in heat-recovery boilers, so their gap should not be read as unmonitored fuel without checking each block's duct burners.
- Whether PUDL wants inferred ids, and how to mark rows that add no boiler, is a choice for its maintainers.

## Limits

- The second rule is an assumption about rows that add no boiler, not EPA's or EIA's own statement. Both rules use ids only; no capacities, dates or stack data were read.
- Q4 counts only ids with "HRSG"; heat-recovery boilers named otherwise are left out of that share.
- Heat input from generators without boilers is outside this count. No CO2 is estimated.
- One nightly build (31 October 2026), not a pinned release; plant names were not looked up here.
- PUDL's data (CC BY 4.0) was downloaded at run time and is not stored here.
