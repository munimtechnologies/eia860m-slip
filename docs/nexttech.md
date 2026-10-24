# Most of the fall in EIA-860M's next-month share is inside technologies: solar and batteries fell, gas did not

Status: scored against its pre-registration ([`docs/nexttech-plan.md`](nexttech-plan.md), commit 7d2780e, fixed before job nexttech-v1 read the technology of any generator): 3 of 4 predictions held, and the reproduction check T0 held. T2 failed: natural gas's share rose. Every number below is checked against the job's raw output by the doc test [`test_nexttech_doc.py`](../test_nexttech_doc.py).

Made by MV2 of Munim, Inc. with AI agents working in his name. Text and data: CC BY 4.0. Job nexttech-v1 (23 October 2026) ran [`tools/annual-flows-candidate/nexttech.py`](../tools/annual-flows-candidate/nexttech.py) 0.1.0 (Apache-2.0) unchanged, after its 11 unit tests passed ([`nexttech-v1-unittests.txt`](nexttech-v1-unittests.txt)). Raw output: [`docs/nexttech-v1-output.md`](nexttech-v1-output.md) and the job's log [`docs/nexttech-v1-stdout.txt`](nexttech-v1-stdout.txt). Data: [`data/nexttech_cohort.csv`](../data/nexttech_cohort.csv) (one row per generator and cohort month, 14,807 rows) and [`data/nexttech_years.csv`](../data/nexttech_years.csv).

## What was measured

Each month's next-month cohort is the set of generators that the month before listed on the Planned sheet with this month as their planned operating month. The share is the part of the cohort that this month's workbook lists as operating. [`docs/nextmonth-share.md`](nextmonth-share.md) found that share fell from 0.469 in 2016-2019 to 0.349 in 2022-2025, by count, and could not say why. This note splits it by the technology each generator had in the month before. A generator that is planned for the next month again and again is counted once in each of those months, so the counts are generator-months, as in `nextmonth-share.md`.

## Order of events

The plan was committed at 21:57:45 UTC on 23 October 2026 (commit 7d2780e). The job started at 22:27:37 UTC, was served the plan on its first poll at 22:29:24 UTC, and only then downloaded the changelog and read any workbook. It read the rebuilt changelog at commit a3ce085 (1,054,060 bytes, 117,756 rows, the expected file) and 134 workbooks from PUDL's raw archive, July 2015 to August 2026, with no read errors.

## The check and the bars

| bar | outcome | value |
|---|---|---|
| T0 (check). All technologies reproduce 1,980 of 4,223 and 2,110 of 6,047, at most 1% without a technology | held | 1,980 of 4,223 and 2,110 of 6,047; 32 and 25 without a technology |
| T1. Solar's share is lower in 2022-2025 than in 2016-2019 | held | 0.506 (1,243 of 2,457) to 0.354 (1,292 of 3,654) |
| T2. Gas's share is lower in 2022-2025 than in 2016-2019 | failed | 0.401 (298 of 743) to 0.455 (191 of 420) |
| T3. Batteries' share is lower in 2022-2025 than in 2016-2019 | held | 0.442 (61 of 138) to 0.299 (453 of 1,515) |
| T4. The within-technology fall is at least half the total fall | held | 0.094 of 0.120 |

The 32 and 25 generators without a technology are 0.76% and 0.41% of their periods' cohorts. They are counted in "other", as the plan said.

## T4: about four-fifths of the fall is inside technologies

The cohort's mix moved a long way. Batteries were 3.3% of the 2016-2019 cohort and 25.1% of the 2022-2025 cohort. Gas went from 17.6% to 6.9%, wind from 10.9% to 4.4%, other technologies from 10.0% to 3.1%, and solar from 58.2% to 60.4%.

Weighting each technology's 2022-2025 share by its part of the 2016-2019 cohort gives 0.374. So with the old mix, the share would have fallen from 0.469 to 0.374: a within-technology fall of 0.094, against a total fall of 0.120. That is 79% of the fall. The other 21% is the change of mix: toward batteries, whose share was low, and away from gas, wind and other technologies.

| technology | 2016-2019 | 2022-2025 |
|---|---|---|
| solar | 0.506 (1,243 of 2,457) | 0.354 (1,292 of 3,654) |
| batteries | 0.442 (61 of 138) | 0.299 (453 of 1,515) |
| gas | 0.401 (298 of 743) | 0.455 (191 of 420) |
| wind | 0.471 (217 of 461) | 0.403 (108 of 268) |
| other | 0.380 (161 of 424) | 0.347 (66 of 190) |
| all | 0.469 (1,980 of 4,223) | 0.349 (2,110 of 6,047) |

By nameplate MW (reported, not scored), solar went from 0.541 to 0.377, batteries from 0.453 to 0.349, gas from 0.450 to 0.562, and all technologies from 0.503 to 0.401. The data file gives 0.0 MW for all 259 cohort generators of January to April 2016 (and for every one of 2015), so the 2016-2019 MW shares leave them out.

## T2: gas rose, and one plant accounts for the rise

Inside gas, combustion turbines moved most:

| gas technology | 2016-2019 | 2022-2025 |
|---|---|---|
| Natural Gas Internal Combustion Engine | 0.504 (115 of 228) | 0.460 (86 of 187) |
| Natural Gas Fired Combustion Turbine | 0.249 (66 of 265) | 0.460 (58 of 126) |
| Natural Gas Fired Combined Cycle | 0.472 (108 of 229) | 0.596 (34 of 57) |
| other gas technologies | 0.429 (9 of 21) | 0.260 (13 of 50) |

The low 2016-2019 combustion-turbine share owes much to one plant. Plant 60264 has 102 of the 265 combustion-turbine generator-months of 2016-2019, from 12 generators that were planned for the next month again and again from June 2016 to July 2018. Only 6 of the 102 were listed as operating in the planned month: generators BCGT1 to BCGT6, in July 2018. Without plant 60264, gas's share is 0.456 (292 of 641) in 2016-2019 and 0.455 (191 of 420) in 2022-2025: flat. Plant 60264 has no cohort row in 2022-2025.

So T2's failure is real as scored, but it rests on one plant's repeated slips, not on a broad change in gas. That is a weakness of counting generator-months, which the plan did not foresee. A check that counts each generator once per period is pre-registered in [`docs/nexttechonce-plan.md`](nexttechonce-plan.md).

## By year

The share by year of the cohort month (2015 is August to December; 2026 is January to September):

| year | solar | batteries | gas |
|---|---|---|---|
| 2015 | 0.520 (118 of 227) | 0.333 (4 of 12) | 0.515 (17 of 33) |
| 2016 | 0.558 (256 of 459) | 0.429 (6 of 14) | 0.361 (74 of 205) |
| 2017 | 0.492 (367 of 746) | 0.455 (15 of 33) | 0.390 (76 of 195) |
| 2018 | 0.549 (335 of 610) | 0.500 (15 of 30) | 0.470 (103 of 219) |
| 2019 | 0.444 (285 of 642) | 0.410 (25 of 61) | 0.363 (45 of 124) |
| 2020 | 0.473 (366 of 774) | 0.348 (31 of 89) | 0.426 (46 of 108) |
| 2021 | 0.387 (320 of 826) | 0.282 (72 of 255) | 0.390 (104 of 267) |
| 2022 | 0.331 (241 of 729) | 0.241 (76 of 316) | 0.374 (58 of 155) |
| 2023 | 0.342 (303 of 886) | 0.247 (96 of 389) | 0.440 (37 of 84) |
| 2024 | 0.365 (382 of 1,047) | 0.339 (143 of 422) | 0.459 (34 of 74) |
| 2025 | 0.369 (366 of 992) | 0.356 (138 of 388) | 0.579 (62 of 107) |
| 2026 | 0.290 (237 of 818) | 0.300 (114 of 380) | 0.557 (44 of 79) |

Solar's share in every year from 2021 to 2026 is below its share in every year from 2015 to 2020. January to September 2026 is solar's lowest year in the series. Batteries were lowest in 2022 and 2023. Gas's two highest years are 2025 and 2026, on small cohorts.

## What was already known, and what is new

The plan cited EIA's Today in Energy of 8 May 2024, which reported delays for planned solar capacity rising through 2021 and 2022. After the job ran we found a later EIA article that the plan did not cite: on 10 November 2025 EIA wrote that "solar projects representing about 20% of planned capacity reported a delay" in the third quarter of 2025, "a decrease from 25% in the same period in 2024", and that "These delays are typically only for a month or two." That measures something else: capacity whose reported online date moved later, not generators listed as operating in their planned month. A delay of a month counts as a miss here, so short delays weigh heavily in this measure. Our January-September 2026 solar share is the lowest of the series while EIA reports fewer solar delays in late 2025; this note does not resolve the difference, and the two measures need not move together.

We found no published next-month share for EIA-860M split by technology, and no split of its fall into mix and within-technology parts (searches of EIA's Today in Energy and the web, 24 October 2026). What is new here is that split: about 79% of the fall is inside technologies, solar and batteries each fell, and gas did not.

## Limits

- Counts are generator-months. A generator planned for the next month in many months counts in each; plant 60264 shows how much one plant can move a group. Counts also weigh a 1 MW generator like a 1,000 MW one.
- Technology is taken from the month before. A technology edited later is not followed.
- Generators at one plant are not independent, so no significance test is given. The split is an association, not a cause.
- Five groups are coarse: a shift inside a group (for example from combined cycle to engines inside gas) counts as "within".
- The changelog is rebuilt by this repository's own code from the same archive; T0 is a reproducibility check, not an independent one.
- No person has checked these counts by hand against the workbooks.

## Sources

- EIA, Today in Energy, 8 May 2024, "U.S. electric power sector reported fewer delays for new solar capacity projects in 2023": https://www.eia.gov/todayinenergy/detail.php?id=62003
- EIA, Today in Energy, 10 November 2025, "Fewer U.S. solar projects are reporting delays in their expected online date": https://www.eia.gov/todayinenergy/detail.php?id=66604
- EIA, Preliminary Monthly Electric Generator Inventory (EIA-860M): https://www.eia.gov/electricity/data/eia860m/

## Update, 24 October 2026: counting each generator once

The once-per-generator check pre-registered above is scored in [`docs/nexttechonce.md`](nexttechonce.md) (thirty-fifth result): 3 of 4 predictions held. Counting each generator once per period, solar and batteries still fall, and a little under 70% of the fall is inside technologies, against 79% in generator-months above. Gas still rises, by 0.057 against a band of 0.05; without plant 60264 the rise is 0.040. Repeat listings grew from 1.94 to 2.39 per generator, which is part of why the generator-month fall above is larger. Nothing above this section was changed.
