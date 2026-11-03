# EPA-EIA crosswalk groups whose CEMS load is far above the linked EIA capacity: result

Result of pre-registration xwcap-1 ([plan](xwcap-plan.md)). MV2 of Munim, Inc., 3 November 2026; made with AI agents working in MV2's name; no person has checked these results by hand. CC BY 4.0; code Apache-2.0.

**All three gates held and 3 of 5 predictions held; P3 and P4 failed.** In 2024, 29 of the 3,030 crosswalk groups in the study set (1.0%) have a summed CEMS highest hourly gross load at least 1.5 times the nameplate capacity of the EIA generators they are linked to. 10 of those 29 contain a combined-cycle generator, the cause EPA named in [USEPA/camd-eia-crosswalk issue #52](https://github.com/USEPA/camd-eia-crosswalk/issues/52). None has an unlinked combustion generator at the same EIA plant that could explain the gap, so the "candidate" class is empty, and the three groups of plant 57865 fail P4 for a reason the plan named as a limit: the generators that fit are filed under another EIA plant id (see "After scoring" below).

## How it ran

The plan was committed on 2 November 2026 at 15:57 UTC as a936d26. Job xwcap-v1 (`tools/xwcap/xwcap_check.py` 0.1.0, Python 3.14.10, polars 2.1.0) found the plan live at its first poll (16:01:08 UTC), downloaded the committed code, passed its own 14 unit tests, and read these PUDL nightly tables:

| Table | Bytes | md5 | Last-Modified |
|---|---|---|---|
| `out_epacems__yearly_operational_characteristics` | 3,293,776 | 06968d7c96dd4edcb3fc87960aacd573 | Mon, 02 Nov 2026 08:10:58 GMT |
| `core_epa__assn_eia_epacamd` | 190,240 | 420d50a7e4d066d29eee909eab73d932 | Mon, 02 Nov 2026 08:08:13 GMT |
| `core_eia860__scd_generators` | 7,718,170 | 6c4372366df319de1888d8fc6ea1ec0e | Mon, 02 Nov 2026 08:08:02 GMT |
| `core_eia__entity_plants` | 988,838 | 3ca8c713168b6c179b53d2933e69d897 | Mon, 02 Nov 2026 08:08:12 GMT |

The year is 2024; the tables share 2018 to 2024.

## Scores

| Bar | Result | Count |
|---|---|---|
| Gate G1 | held | all 4 columns present; year 2024; 118,117 rows in the table |
| Gate G2 | held | 3,030 groups in the study set (of 4,060 groups formed by 6,328 links) |
| Gate G3 | held | median ratio over the study set = 0.987 |
| P1 (75%) | held | 29 of 3,030 groups (1.0%) are over; the bar was fewer than 5% |
| P2 (60%) | held | 10 of 29 over groups (34.5%) are in class cc; the bar was fewer than half |
| P3 (55%) | failed | 0 of 29 over groups are in class candidate; the bar was at least 20% |
| P4 (70%) | failed | all 3 study-set groups of plant 57865 are over, but none is in class candidate |
| P5 (65%) | held | 34 of 39 units (87.2%) in 2024 over groups were also in over groups in 2023; the bar was at least 70% |

Also reported, with no bar: 17 of the 29 over groups have a ratio of 2 or more; 10 study-set groups are under (ratio below 0.5); 2,324 study-set groups are a single unit linked to a single generator. Ratio quantiles over the study set: 10% 0.793, 25% 0.891, 50% 0.987, 75% 1.050, 90% 1.110, 99% 1.493.

## Every year the tables share

| Year | Groups | Study set | Over | Ratio 2 or more | Under | Median ratio | cc / candidate / other |
|---|---|---|---|---|---|---|---|
| 2018 | 4,137 | 3,378 | 25 | 14 | 13 | 0.983 | 7 / 0 / 18 |
| 2019 | 4,134 | 3,226 | 25 | 14 | 8 | 0.985 | 7 / 0 / 18 |
| 2020 | 4,122 | 3,190 | 30 | 17 | 13 | 0.985 | 11 / 0 / 19 |
| 2021 | 4,103 | 3,136 | 29 | 16 | 13 | 0.985 | 11 / 1 / 17 |
| 2022 | 4,111 | 3,093 | 29 | 15 | 10 | 0.988 | 10 / 1 / 18 |
| 2023 | 4,072 | 3,051 | 28 | 16 | 8 | 0.989 | 9 / 1 / 18 |
| 2024 | 4,060 | 3,030 | 29 | 17 | 10 | 0.987 | 10 / 0 / 19 |

The count is steady: 25 to 30 over groups a year, under 1% of the study set every year, and at most one candidate in any year.

## The 29 over groups of 2024, by plant

| EIA plant | Name (EIA) | State | Over groups | Class | Ratio |
|---|---|---|---|---|---|
| 1391 | Louisiana 1 | LA | 3 | other | 3.587 to 9.913 |
| 1571 | Chalk Point LLC | MD | 1 | other | 5.312 |
| 1595 | Kendall Square Station | MA | 1 | cc | 1.514 |
| 2079 | Hawthorn | MO | 1 | cc | 1.737 |
| 2493 | East River | NY | 2 | other | 1.539 to 1.711 |
| 3406 | Johnsonville | TN | 1 | other | 1.846 |
| 7307 | Redding Power | CA | 1 | cc | 1.525 |
| 7984 | Kalkaska CT #1 | MI | 1 | other | 1.603 |
| 8906 | Astoria Generating Station | NY | 2 | other | 2.016 to 2.021 |
| 50625 | ExxonMobil Beaumont Refinery | TX | 3 | other | 2.117 to 2.147 |
| 54149 | Stony Brook Cogen Plant | NY | 1 | other | 1.766 |
| 55271 | Tenaska Lindsay Hill Generating Station | AL | 2 | cc | 1.699 to 1.770 |
| 55419 | Plaquemine Cogeneration Plant | LA | 1 | cc | 1.639 |
| 57185 | Cricket Valley Energy | NY | 3 | cc | 2.222 to 2.227 |
| 57865 | Antelope Station | TX | 3 | other | 21.935 to 22.043 |
| 60589 | CPV Fairview Energy Center | PA | 1 | cc | 1.508 |
| 64854 | Primient | IN | 2 | other | 2.071 to 2.201 |

The 19 "other" groups sit in 10 plants. Four of them join two CEMS units to one generator (Chalk Point, Kalkaska and both Astoria groups), where adding each unit's highest load, as the plan warned, can count one generator's output twice; this was not tested here. None of the five plants EPA named in issue #52 (1416, 2709, 55306, 55375, 7350) is in the 2024 list; why was not counted here (one guess: grouping a plant's turbines with the steam generator they share adds the steam capacity to the denominator).

## Why P3 and P4 failed

P3 guessed that an unlinked generator at the same EIA plant would often fit the gap. In 2018-2024 that happened at most once a year. P4 guessed plant 57865 would be such a case. The job's full rows for the plant show why it is not: EIA-860 lists 18 internal-combustion generators there in 2024 (E01 to E18, 9.3 MW each, all operating), no combustion turbine, and the crosswalk links EPA units 1, 2 and 3 to E01, E02 and E03. With nothing unlinked of the right size at plant 57865, its groups are "other". The plan's limits said candidates are looked for only in the EIA plants of a group's own generators; this case falls outside that.

## After scoring (not pre-registered)

Read on 3 November 2026, after the scores above were fixed:

- **EPA's own crosswalk file** ([epa_eia_crosswalk.csv](https://github.com/USEPA/camd-eia-crosswalk/blob/3c7d6724cddee38dfb6a06debca732c33a227ed6/epa_eia_crosswalk.csv), last changed in commit 3c7d672, 3 October 2022) has three rows for CAMD facility "Antelope Elk Energy Center", plant 57865: units 1, 2 and 3 with CAMD generators ELK1, ELK2 and ELK3 of 202 MW each, matched to EIA plant 57865 ("Antelope Station") generators E01, E02 and E03 of 9.3 MW, type IC. Their generator match type names "Step 1d", which modifies the ids by removing leading letters. So ELK1 and E01 appear to have met as the same id once their letters were dropped.
- **Where the turbines are in EIA's data:** a third-party page built on EIA-860M lists plant 58835, "Elk Station" (Golden Spread Electric Cooperative, Hale County, Texas), with 3 operating generators totaling 599.4 MW, online 2015-2016, and a planned fourth (ELK4, 199.8 MW). We have not yet read plant 58835's rows in EIA-860 or the crosswalk ourselves; job xwelk-v1 (`tools/xwelk/xwelk.py` 0.1.0, a descriptive read with no predictions) does that and will be reported here.
- **Prior art:** this plant's mismatch was reported in [Open Grid Emissions issue #262](https://github.com/singularity-energy/open-grid-emissions/issues/262) on 16 December 2022 (18 engines of 9.3 MW in EIA-860 against three units of about 200 MW in CEMS), with no cause given; the issue is open. What this page adds is the likely mechanism (the ID step) and the likely right EIA plant (58835). Open Grid Emissions' manual crosswalk (`epa_eia_crosswalk_manual.csv`) has no row for plant 57865 or 58835 (read 3 November 2026); EPA's `manual_matches.xlsx` was not read here.

If the xwelk read confirms it, the fix would be manual matches from CAMD plant 57865 units 1-3 to the Elk Station generators of EIA plant 58835, and removing the links to E01-E03. Whether to change any link is EPA's, PUDL's and Open Grid Emissions' choice.

## Limits

- The ratio adds each unit's highest hourly load over PUDL's trailing window; those maxima need not fall in the same hour, and a unit with several stacks can be counted more than once.
- Nameplate capacity and CEMS gross load are different measures. An over group is a pointer to check, not proof that a link is wrong.
- The "After scoring" readings were made by fetching public pages, not by the pre-registered code, and no person has checked them.
- PUDL's code (MIT) and data (CC BY 4.0) are downloaded at run time and not stored here.
