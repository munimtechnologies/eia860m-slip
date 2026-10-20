# Are stage moves in EIA-860M bunched in the reports around the annual survey?

Status: scored against its pre-registration ([`report-months-preregistration.md`](report-months-preregistration.md)). All checks passed; 3 of 4 predictions held. MV2 of Munim, Inc. (made with AI agents). CC BY 4.0.

## What this is

The twenty-first result ([`stage-moves.md`](stage-moves.md)) followed each planned generator from one EIA-860M report to the next and counted moves between stage bands: early (P, L), approved (T) and building (U, V, TS). This note asks in which calendar month the moves show up. The window is the reports for December, January, February and March: the last report of the year the annual EIA-860 describes, and the reports for the months in which annual responses are due (January and February) and taken in. A step from report m to report m + 1 is placed in the calendar month of report m + 1. Data: PUDL's EIA-860M changelog, reports 2016-01 to 2026-08, the same cached file as the twenty-first result; steps with m in 2016-2025, so every calendar month holds ten reports: 163,753 steps in all. Rates count generators (one per step): moves over eligible steps. Job `monthsteps-v1` (2 GB) fetched eia860m_slip.py (commit 329b7e6), stagemoves.py (commit a059121) and monthsteps.py and test_monthsteps.py (commit bd6c4bf, the commit that published the pre-registration), ran the unit tests, then the tool, on 20 October 2026. Raw output: [`monthsteps-v1-output.md`](monthsteps-v1-output.md), [`../data/monthsteps_v1.json`](../data/monthsteps_v1.json); unit tests: [`monthsteps-v1-unittests.txt`](monthsteps-v1-unittests.txt).

## What we found

**Backward moves bunch in the December-March reports; forward moves do not.** Pooled over 2016-2025, 97 of 31,347 steps from approved or building inside the window moved back a stage (0.0031), against 100 of 63,448 outside it (0.0016): a ratio of 1.9633, so W1 (at least 1.5) held. Its floor was set after seeing the twenty-first result's table of the largest backward moves, so read W1 as partly informed. From building alone the ratio is 2.6117 (57 against 44 moves). Forward moves out of the early and approved stages were slightly rarer inside the window: 0.0390 against 0.0428, a ratio of 0.9111, so W2 (at least 1.25) failed.

**It is not one year.** The backward rate inside the window is higher in 7 of the 10 years (W3 held). The exceptions are 2016, 2021 and 2025, and in 2020 the two rates are close (0.0029 against 0.0025).

**Within the window, January and December carry most of it.** January holds 36 of the 197 backward moves and 20 of the 101 from building; December 27 and 18. The backward rate is highest in January (0.0046) and lowest in August and September (0.0011).

**Moves to another status (neither planned nor operating) bunch too, but there are few of them**: 20 inside the window and 20 outside, on about twice as many steps outside, a ratio of 2.0299 (W4 held), on 40 moves in ten years.

**Not predicted: December is when plants enter service.** The December report lists 1,303 steps to operating, a rate of 0.0917, against 0.0245 to 0.0393 in every other month; 77,118.2 MW, against at most 31,471.3 MW in any other month.

How to read it, as stated before the run: W1 held and W2 did not, which is what year-end re-planning alone would give. Projects that aimed at an in-service date by the end of the year and missed it show up as stepping back around the turn of the year, while forward progress is not batched. This does not rule out the filing calendar, and the December peak in plants entering service fits the same year-end deadline. By MW the backward ratio is larger still (3.1583), so by capacity the bunching is stronger. These are associations in the survey's own records, not causes. For anyone reading EIA-860M month by month: a step back reported in December or January is about twice as common as in the rest of the year, and the twenty-first result shows that a step back from building is followed by coming online within a year far less often than staying put, whenever it is reported.

## Checks (all passed)

| check | result |
|---|---|
| C1 | 163,753 steps; 16,615,177.8 MW; backward from building 7,620.0 MW; all equal to stagemoves' pooled table |
| C2 | 12 months, each with 10 reports |
| C3 | stagemoves' checks S1-S4 pass |
| C4 | backward from building 7,620.0 MW, as in the twenty-first result |
| C5 | 7 of 7 unit tests passed |

## Predictions (3 of 4 held)

| prediction | stated before the run | result | verdict |
|---|---|---|---|
| W1 | backward moves (from approved or building): inside rate at least 1.5 times the outside rate | 1.9633 | held |
| W2 | forward moves (from early or approved): inside rate at least 1.25 times the outside rate | 0.9111 | failed |
| W3 | backward moves: inside rate higher than outside in at least 7 of the 10 years | 7 of 10 | held |
| W4 | moves to another status (from any planned band): inside rate at least 1.5 times the outside rate | 2.0299 | held |

## Inside and outside the window, pooled 2016-2025

Rates are moves over eligible steps (generator counts); the ratio is the inside rate over the outside rate, compared unrounded. MW ratio: the same with MW, description only.

| kind | inside moves | inside steps | inside rate | outside moves | outside steps | outside rate | ratio | MW ratio |
|---|---|---|---|---|---|---|---|---|
| backward | 97 | 31,347 | 0.0031 | 100 | 63,448 | 0.0016 | 1.9633 | 3.1583 |
| backward_building | 57 | 23,347 | 0.0024 | 44 | 47,069 | 0.0009 | 2.6117 | 3.7391 |
| forward | 1,198 | 30,699 | 0.0390 | 2,683 | 62,638 | 0.0428 | 0.9111 | 1.3988 |
| exit_other | 20 | 54,046 | 0.0004 | 20 | 109,707 | 0.0002 | 2.0299 | 2.9405 |
| to_operating | 2,651 | 54,046 | 0.0491 | 3,645 | 109,707 | 0.0332 | 1.4763 | 1.5111 |

## By calendar month of report m + 1

| month | window | steps | backward | backward rate | backward from building | forward rate | exit_other | to operating | to operating rate |
|---|---|---|---|---|---|---|---|---|---|
| 1 | yes | 13,696 | 36 | 0.0046 | 20 | 0.0453 | 6 | 510 | 0.0372 |
| 2 | yes | 12,842 | 15 | 0.0020 | 9 | 0.0338 | 2 | 315 | 0.0245 |
| 3 | yes | 13,302 | 19 | 0.0025 | 10 | 0.0323 | 8 | 523 | 0.0393 |
| 4 | no | 13,373 | 10 | 0.0013 | 2 | 0.0404 | 6 | 458 | 0.0342 |
| 5 | no | 13,523 | 13 | 0.0017 | 9 | 0.0457 | 1 | 418 | 0.0309 |
| 6 | no | 13,525 | 16 | 0.0020 | 6 | 0.0460 | 3 | 504 | 0.0373 |
| 7 | no | 13,559 | 10 | 0.0013 | 9 | 0.0464 | 4 | 474 | 0.0350 |
| 8 | no | 13,626 | 9 | 0.0011 | 3 | 0.0488 | 1 | 402 | 0.0295 |
| 9 | no | 13,830 | 9 | 0.0011 | 1 | 0.0416 | 2 | 407 | 0.0294 |
| 10 | no | 14,094 | 14 | 0.0017 | 6 | 0.0389 | 2 | 468 | 0.0332 |
| 11 | no | 14,177 | 19 | 0.0023 | 8 | 0.0346 | 1 | 514 | 0.0363 |
| 12 | yes | 14,206 | 27 | 0.0032 | 18 | 0.0442 | 4 | 1,303 | 0.0917 |

## Backward rate inside and outside the window, by year of m (W3)

A year of m, Y, covers reports 2-12 of Y and report 1 of Y + 1.

| year | inside rate | outside rate | higher |
|---|---|---|---|
| 2016 | 0.0004 | 0.0016 | no |
| 2017 | 0.0041 | 0.0011 | yes |
| 2018 | 0.0068 | 0.0014 | yes |
| 2019 | 0.0048 | 0.0021 | yes |
| 2020 | 0.0029 | 0.0025 | yes |
| 2021 | 0.0015 | 0.0023 | no |
| 2022 | 0.0047 | 0.0012 | yes |
| 2023 | 0.0020 | 0.0012 | yes |
| 2024 | 0.0043 | 0.0011 | yes |
| 2025 | 0.0007 | 0.0013 | no |

## Limits

As in the pre-registration: steps of the same generator are not independent, and with ten reports per month one unusual year can move a month's rate; statuses are self-reported, and a move's report month is when it was reported, not when it happened; the window was fixed in advance and no other window is scored. W1's floor was set after seeing part of the data (disclosed in the pre-registration). W4 rests on 40 moves. The design cannot fully separate the filing calendar from year-end re-planning; W2 is only a partial test between them. Rates are shown to four decimals as the job wrote them.

## Prior art

As in the pre-registration (searched 20 October 2026): no study or EIA note found that counts EIA-860M status changes by calendar month. Mounts and Cross (2024, arXiv:2406.15687) and Ullrich and Fleten (2026) read stages at a point in time or pool them.
