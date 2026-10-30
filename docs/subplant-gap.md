# EIA boilers left out of PUDL's CEMS subplants: scored

Status: scored against its pre-registration (docs/subplant-gap-plan.md, id subplant-gap-1). Both gates held and 2 of 4 predictions held; P1 and P3 missed. Written 30 October 2026. MV2 of Munim, Inc. (made with AI agents working in MV2's name; no person has checked these counts by hand). CC BY 4.0.

## What was counted

The [plan](subplant-gap-plan.md) fixed the rule, two gates and four predictions before job subplant-gap-v1 ran. The job ran on 30 October 2026 (Python 3.12, pandas 2.3.3, pyarrow 26.0.0, `tools/subplant-gap/subplant_gap.py` 0.1.0, md5 276817f5826157f3f2dc6a94f94c730f). Its 8 unit tests passed, it found the plan live at 21:02:42Z and finished at 21:03:05Z. It read four tables of PUDL's nightly build, all last modified on 29 October 2026 at 06:35-06:36 GMT:

| Table | Rows | ETag |
|---|---|---|
| core_epa__assn_eia_epacamd | 44,833 | 420d50a7e4d066d29eee909eab73d932 |
| core_epa__assn_eia_epacamd_subplant_ids | 45,220 | 0d16dcd3eaa253b36574ef29b754b7f5 |
| core_eia860__assn_boiler_generator | 177,670 | 51f538af79158528909c30d4a732c74f |
| core_eia923__monthly_boiler_fuel | 1,897,951 | c8e8b84bd8a1942eb4ec2ecd9150ff01 |

Seven years qualified (2018 to 2024), so the main year is 2024 as planned. A **gap boiler** burned fuel in the year, is tied through EIA-860's boiler-generator associations to a generator of a subplant that holds a matched EPA unit, and has no crosswalk row with an EPA unit at its plant and boiler. "Strict" leaves out **ambiguous** subplants, where the crosswalk ties a generator to an EPA unit without naming a boiler.

## Scores

| | Expectation | Result |
|---|---|---|
| Gate G0 | four tables load with the planned columns; 2023 and the main year qualify | held: 2018-2024 qualify |
| Gate G1 | 2023, plant 50472: BLR3 and BLR4 gap boilers, BLR1 and BLR2 matched, gap 7.0-9.5 million MMBtu | held: 8,179,711 MMBtu |
| P1 (75%) | at least 20 plants have a gap boiler in 2024 | **missed**: 8 plants |
| P2 (70%) | gap boilers burn at least 25 million MMBtu in 2024 | held: 39,280,975 MMBtu |
| P3 (60%) | at least 10 strict CEMS subplants have a gap share above 50% | **missed**: 5 subplants |
| P4 (70%) | at least 3 of P3's subplants have a largest gap boiler not burning mainly MSW | held: 4 of the 5 |

G1 reproduces issue #5681's case at Covanta Niagara: in 2023 BLR3 burned 4,058,644 MMBtu and BLR4 4,121,067 MMBtu with no crosswalk row, while BLR1 (201,090 MMBtu) and BLR2 (0) are matched. P4 held on a smaller pool than the plan expected, since P3 found 5 subplants, not 10.

## Every year (strict)

Gap and linked heat input in million MMBtu; "share" is gap heat input over the heat input of all boilers linked to strict CEMS subplants.

| Year | Strict CEMS subplants with boilers | Ambiguous subplants | Gap boilers | Gap plants | Gap | Linked | Share | Gap share > 50% | Of those, not MSW |
|---|---|---|---|---|---|---|---|---|---|
| 2018 | 1,017 | 617 | 32 | 11 | 47.4 | 13,232.3 | 0.36% | 6 | 5 |
| 2019 | 960 | 619 | 31 | 11 | 44.4 | 11,365.5 | 0.39% | 6 | 5 |
| 2020 | 896 | 613 | 31 | 11 | 40.6 | 9,451.4 | 0.43% | 6 | 5 |
| 2021 | 845 | 617 | 28 | 8 | 38.3 | 10,664.4 | 0.36% | 5 | 4 |
| 2022 | 803 | 608 | 27 | 8 | 37.6 | 10,274.3 | 0.37% | 4 | 3 |
| 2023 | 786 | 605 | 28 | 9 | 38.4 | 8,819.7 | 0.44% | 4 | 3 |
| 2024 | 726 | 602 | 27 | 8 | 39.3 | 8,728.5 | 0.45% | 5 | 4 |

In every year, none of the strict gap boilers is matched to an EPA unit in any other year of the crosswalk.

## The 2024 gap subplants (strict)

Heat input in MMBtu. "Main fuel" is the EIA energy source code with the most heat input in the subplant's largest gap boiler.

| EIA plant | Subplant | Boilers | Gap boilers | Heat input | Gap heat input | Gap share | Main fuel | Gap boiler ids |
|---|---|---|---|---|---|---|---|---|
| 992 | 1 | 8 | 2 | 2,798,369 | 214,611 | 7.7% | NG | 18; 17 |
| 2098 | 1 | 7 | 5 | 3,814,082 | 3,281,523 | 86.0% | NG | 5; 8; 4; 2; 1 |
| 10252 | 1 | 2 | 1 | 4,610,764 | 1,962,943 | 42.6% | WDS | THB |
| 10328 | 1 | 5 | 1 | 4,299,994 | 47,316 | 1.1% | NG | BLR6 |
| 50472 | 1 | 4 | 2 | 8,278,042 | 8,125,257 | 98.2% | MSN | BLR4; BLR3 |
| 50481 | 1 | 10 | 8 | 9,755,949 | 4,962,356 | 50.9% | BIT | 83-22; 83-21; 83-20; 423-C; 423-A; 83-18; 423-B; 83-19 |
| 50481 | 2 | 5 | 1 | 21,103,186 | 4,537,193 | 21.5% | NG | 253-28 |
| 52193 | 4 | 6 | 4 | 9,034,669 | 6,408,953 | 70.9% | OG | BLR2; BLR3; HRSG 1; HRSG 2 |
| 54216 | 5 | 7 | 3 | 9,740,823 | 9,740,823 | 100.0% | BLQ | REC3; PB1; PB2 |

These 9 subplants at 8 plants hold all 27 strict gap boilers of 2024. By main fuel the gap heat input is natural gas (NG) 12.9, municipal solid waste (MSN) 8.1, black liquor (BLQ) 7.2, other gas (OG) 5.6, bituminous coal (BIT) 3.4 and wood (WDS) 2.0 million MMBtu. Four of the 8 plants also have an EPA unit with no EIA generator in the subplant table, so some of their gap boilers may report to CEMS under a unit the crosswalk did not match.

## What it shows

- The pattern of issue #5681 is real but narrow in the strict count: 8 to 11 plants a year from 2018 to 2024, 37.6 to 47.4 million MMBtu, under half a percent of the heat input of boilers linked to strict CEMS subplants. Our predictions of at least 20 plants and 10 badly affected subplants were too high.
- Where it happens it can be large: in 5 subplants in 2024 CEMS sees less than half of the boiler fuel, and 4 of them burn mainly gas, black liquor or coal, not waste. So it is not only a waste-plant pattern.
- The bigger limit is the ambiguous subplants: 602 of the 1,328 CEMS subplants with linked boilers in 2024 (45%) have a generator tied to an EPA unit with no boiler named. For those the rule cannot tell which boiler CEMS covers. Counted with them, 460 plants and 9,536.5 million MMBtu look like gaps, 9,179.2 million of it natural gas, and most of the 40 largest such subplants carry turbine or heat-recovery boiler ids such as CT01, CTG1 and HRSG1. That is mostly a measure of boiler ids missing from the crosswalk, not of fuel outside CEMS, and it is not a gap estimate.
- These counts size the problem; they do not choose a fix for PUDL.

## Limits

- A gap boiler is not proof of missing emissions: some boilers are outside CEMS by law, and some may report under an EPA unit the crosswalk did not match (see the four plants above).
- Heat input from generators without boilers is outside this count. No CO2 is estimated.
- One nightly build (29 October 2026), not a pinned release; plant names were not looked up here.
- PUDL's data (CC BY 4.0) was downloaded at run time and is not stored here.
