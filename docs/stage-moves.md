# How planned generators move between stages from one EIA-860M report to the next

Status: scored against its pre-registration ([`stage-moves-preregistration.md`](stage-moves-preregistration.md), including its two dated amendments and the prior-art addition of 20 October 2026). All checks passed; all four predictions held. MV2 of Munim, Inc. (made with AI agents). CC BY 4.0.

## What this is

EIA-860M gives each planned generator a status code every month. The earlier results read a generator's stage at one report; this one reads how the stage moves from each report to the next, reports 2016-01 to 2026-08 (179,141 steps over 10,474 generators). A step is a generator planned in report m as early (P, L), approved (T) or building (U, V, TS) that is still listed in report m + 1. Job `stagemoves-v2` (2 GB; the pre-registered `stagemoves-v1` asked for 3 GB and never started, Amendment 2) ran the pinned code on 20 October 2026. Raw output: [`stagemoves-v2-output.md`](stagemoves-v2-output.md), [`../data/stagemoves_v2.json`](../data/stagemoves_v2.json); unit tests: [`stagemoves-v2-unittests.txt`](stagemoves-v2-unittests.txt).

The status codes, as EIA defines them: P, planned, regulatory approvals not initiated; L, regulatory approvals pending, not under construction; T, regulatory approvals received, not under construction; U, under construction, 50% complete or less; V, under construction, more than 50% complete; TS, construction complete, not yet in commercial operation.

## What we found

**Backward moves are rare (M1 held).** Of the 5,952,841.7 MW of building steps with m in 2016-2025, 7,620.0 MW (0.0013) moved to an earlier band in the next report: 4,748.0 MW to early and 2,872.0 MW to approved. From approved, 8,366.2 of 2,288,249.9 MW (0.0037) moved back to early. In no year from 2016 to 2026 (steps from January to July for 2026) did more than 0.0032 of building MW move backward (2018), or more than 0.0072 of approved MW (2020).

**Almost all of it is solar and onshore wind.** They make up 7,143.2 of the 7,620.0 MW that moved back from building in 2016-2025 (solar 4,408.3 MW, onshore wind 2,734.9 MW); gas combined cycle moved back 35.0 of 1,303,711.1 MW. The ten largest backward steps from building (table below) are all solar or onshore wind projects of 200 MW or more; five went back to P and five to T. None of the 8 whose 12-report window has closed was listed as operating within it. Cradle Solar (225.0 MW) moved back from building in 2023-01 and again in 2024-06.

**A backward move is bad news (M3 held).** Of building steps with a closed window, 0.528 of the MW held in building was listed as operating within 12 reports, against 0.053 after a backward move (369.0 of 6,965.2 MW): a gap of 0.475, against the 0.20 predicted. Not pre-registered, the same split shows earlier in the pipeline: 0.375 of the MW that moved forward out of early was operating within 12 reports, against 0.020 of the MW that stayed early; from approved, 0.460 after a forward move against 0.045 held. Within each band, the generators whose stage changed fared very differently from those whose stage held. These are associations in the record, not causes: a forward move from early is by definition a step closer to operation, and a backward move is the respondent's own report of a setback.

**About a third flicker back (M2 held).** Of the 102 generators whose first backward move from building can be followed for six reports, 38 (0.3725) were listed as building or operating again within those six reports; the other 64 were not.

**Most capacity skips the approved code (M4 held).** Of the 1,823 generators first listed at an early stage after January 2016 that later reached building, 395 (26,372.4 of 151,028.8 MW, 0.1746 of the MW) were listed as approved (T) in some report in between. In the steps of 2016-2025, 129,933.1 MW moved straight from early to building and 40,260.4 MW from early to approved. So for most of this capacity the monthly record has no approved stage: either it lasted less than a month or the respondent did not report it. This run cannot tell which, but a reading of EIA-860M's codes as a pipeline that every project passes through stage by stage does not fit the record.

## Checks (all passed)

| check | result |
|---|---|
| S1 | 2017-01 109,382.3 MW, 1,024 steps; 2020-01 111,807.9 MW, 1,273 steps; 2024-01 160,368.0 MW, 1,537 steps |
| S2 | 33 rows, 0 not adding up |
| S3 | 11 links |
| S4 | 0 duplicates, 0 missing months |
| unit tests | 13 of 13 passed |

## Predictions (4 of 4 held)

| prediction | stated before the run | result | verdict |
|---|---|---|---|
| M1 | building steps that move backward < 0.02 of MW, 2016-2025 | 0.0013 (7,620.0 of 5,952,841.7 MW) | held |
| M2 | at least 0.25 of generators back in building or operating within 6 reports of a first backward move from building | 0.3725 (38 of 102 generators) | held |
| M3 | online within 12 reports: held minus backward, building steps, at least 0.20 | gap 0.4750 (held 0.5280, backward 0.0530) | held |
| M4 | less than 0.50 of early-to-building MW listed as approved in between | 0.1746 (26,372.4 of 151,028.8 MW) | held |

## Pooled 2016-2025: the band in the next report (MW)

| from | steps | step MW | early | approved | building | operating | other | left |
|---|---|---|---|---|---|---|---|---|
| early | 68,958 | 8,374,086.2 | 8,201,333.3 | 40,260.4 | 129,933.1 | 1,555.8 | 1,003.6 | 66,712.2 |
| approved | 24,379 | 2,288,249.9 | 8,366.2 | 2,168,647.9 | 109,381.3 | 1,599.5 | 255.0 | 16,309.4 |
| building | 70,416 | 5,952,841.7 | 4,748.0 | 2,872.0 | 5,608,238.5 | 336,192.8 | 790.4 | 16,280.8 |

Step MW is the sum of the five columns from early to other; left (no record in force in the next report) is not a step and is not in step MW.

## Every year: steps from building (MW)

| year | steps | step MW | forward | held | backward | to_operating | exit_other | left | backward share |
|---|---|---|---|---|---|---|---|---|---|
| 2016 | 5,519 | 390,119.6 | 0.0 | 370,239.5 | 135.3 | 19,744.8 | 0.0 | 1,748.6 | 0.000 |
| 2017 | 5,478 | 510,381.2 | 0.0 | 488,341.1 | 113.6 | 21,926.5 | 0.0 | 1,005.9 | 0.000 |
| 2018 | 4,740 | 454,881.9 | 0.0 | 419,940.7 | 1,443.7 | 33,281.4 | 216.1 | 5,693.9 | 0.003 |
| 2019 | 5,050 | 401,652.5 | 0.0 | 377,449.4 | 844.4 | 23,246.5 | 112.2 | 1,150.2 | 0.002 |
| 2020 | 6,649 | 554,817.7 | 0.0 | 522,316.6 | 585.0 | 31,753.0 | 163.1 | 2,179.7 | 0.001 |
| 2021 | 7,305 | 637,756.7 | 0.0 | 601,261.1 | 479.2 | 35,962.4 | 54.0 | 491.0 | 0.001 |
| 2022 | 7,685 | 634,066.0 | 0.0 | 604,877.9 | 846.1 | 28,342.0 | 0.0 | 1,096.5 | 0.001 |
| 2023 | 8,779 | 709,468.4 | 0.0 | 668,407.7 | 296.6 | 40,759.1 | 5.0 | 62.2 | 0.000 |
| 2024 | 9,549 | 736,591.9 | 0.0 | 685,216.6 | 2,037.9 | 49,337.4 | 0.0 | 1,239.1 | 0.003 |
| 2025 | 9,662 | 923,105.8 | 0.0 | 870,187.9 | 838.2 | 51,839.7 | 240.0 | 1,613.7 | 0.001 |
| 2026 | 6,549 | 654,916.0 | 0.0 | 623,039.4 | 991.8 | 30,884.8 | 0.0 | 1,254.8 | 0.002 |

## Every year: steps from approved (MW)

| year | steps | step MW | forward | held | backward | to_operating | exit_other | left | backward share |
|---|---|---|---|---|---|---|---|---|---|
| 2016 | 1,910 | 138,051.7 | 3,895.9 | 134,003.8 | 147.0 | 5.0 | 0.0 | 250.8 | 0.001 |
| 2017 | 2,259 | 206,151.7 | 8,270.5 | 197,203.7 | 635.5 | 42.0 | 0.0 | 701.3 | 0.003 |
| 2018 | 1,849 | 202,432.7 | 10,849.3 | 190,037.7 | 1,313.0 | 227.7 | 5.0 | 1,766.9 | 0.006 |
| 2019 | 2,899 | 216,144.3 | 10,858.0 | 204,954.1 | 41.5 | 40.7 | 250.0 | 840.1 | 0.000 |
| 2020 | 2,811 | 223,406.6 | 12,958.9 | 208,705.9 | 1,597.5 | 144.3 | 0.0 | 2,545.5 | 0.007 |
| 2021 | 2,811 | 208,585.2 | 11,193.2 | 196,999.7 | 156.3 | 236.0 | 0.0 | 1,172.9 | 0.001 |
| 2022 | 2,468 | 221,799.7 | 8,637.8 | 212,070.6 | 1,063.2 | 28.1 | 0.0 | 3,801.5 | 0.005 |
| 2023 | 2,098 | 254,910.7 | 14,509.6 | 238,755.8 | 1,363.8 | 281.5 | 0.0 | 1,918.1 | 0.005 |
| 2024 | 2,358 | 305,095.6 | 7,855.4 | 295,054.6 | 1,597.0 | 588.6 | 0.0 | 981.7 | 0.005 |
| 2025 | 2,916 | 311,671.7 | 20,352.7 | 290,862.0 | 451.4 | 5.6 | 0.0 | 2,330.6 | 0.001 |
| 2026 | 1,697 | 186,820.9 | 9,099.3 | 176,514.2 | 1,200.9 | 6.5 | 0.0 | 420.0 | 0.006 |

The steps from early are in the raw output; nothing can move backward from early.

## Pooled 2016-2025: backward share by technology

| group | building steps MW | backward MW | building share | approved steps MW | approved backward MW | approved share |
|---|---|---|---|---|---|---|
| all | 5,952,841.7 | 7,620.0 | 0.001 | 2,288,249.9 | 8,366.2 | 0.004 |
| solar | 1,953,731.2 | 4,408.3 | 0.002 | 801,748.9 | 2,826.7 | 0.004 |
| wind_onshore | 1,325,912.1 | 2,734.9 | 0.002 | 296,685.3 | 941.7 | 0.003 |
| battery | 648,615.9 | 303.3 | 0.001 | 146,688.0 | 658.0 | 0.004 |
| gas_cc | 1,303,711.1 | 35.0 | 0.000 | 755,054.8 | 1,841.5 | 0.002 |
| gas_ct | 297,896.8 | 100.0 | 0.000 | 119,506.9 | 1,317.8 | 0.011 |

## Listed as operating within 12 reports (closed windows, MW)

| from | move | steps | scored MW | online MW | share |
|---|---|---|---|---|---|
| early | forward | 2,040 | 161,121.5 | 60,439.3 | 0.375 |
| early | held | 63,117 | 7,582,451.4 | 150,932.5 | 0.020 |
| early | to_operating | 81 | 1,445.8 | 1,445.8 | 1.000 |
| early | exit_other | 21 | 1,003.6 | 97.3 | 0.097 |
| approved | forward | 1,718 | 104,786.8 | 48,228.2 | 0.460 |
| approved | held | 21,589 | 2,084,202.9 | 94,810.0 | 0.045 |
| approved | backward | 96 | 8,366.2 | 155.4 | 0.019 |
| approved | to_operating | 73 | 1,599.5 | 1,599.5 | 1.000 |
| approved | exit_other | 2 | 255.0 | 0.0 | 0.000 |
| building | held | 61,233 | 5,300,216.6 | 2,798,352.9 | 0.528 |
| building | backward | 96 | 6,965.2 | 369.0 | 0.053 |
| building | to_operating | 5,844 | 312,851.9 | 312,851.9 | 1.000 |
| building | exit_other | 17 | 790.4 | 352.3 | 0.446 |

A window is closed when report m + 12 is at or before the last report (2026-08). Rows with no steps (backward from early, forward from building) are left out.

## Largest backward steps from building

| plant | key | group | MW | moved in | from | to | operating within 12 |
|---|---|---|---|---|---|---|---|
| Obsidian Solar Center | 63488/OBSLR | solar | 400.0 | 2021-01 | U | P | no |
| Alle-Catt Wind Energy LLC | 62954/GEN1 | wind_onshore | 340.0 | 2024-12 | U | T | no |
| Easter | 59971/ESTR1 | wind_onshore | 300.0 | 2019-01 | U | P | no |
| Stagecoach LRE | 68079/STAS1 | solar | 300.0 | 2024-12 | U | T | no |
| Changing Winds | 59243/CHAN1 | wind_onshore | 288.0 | 2018-02 | U | P | no |
| Cradle Solar | 65822/CRAS0 | solar | 225.0 | 2023-01 | U | T | no |
| Cradle Solar | 65822/CRAS0 | solar | 225.0 | 2024-06 | U | T | no |
| ATLAS Solar X, LLC | 69198/ATL10 | solar | 225.0 | 2025-10 | V | P | not yet known |
| Minco Wind V, LLC | 61837/MV | wind_onshore | 220.0 | 2018-11 | V | P | no |
| Beekman Solar | 69589/BEEK1 | solar | 206.8 | 2026-02 | U | T | not yet known |

The ten largest of all years 2016-2026; the raw output lists fifteen. Plant names are as EIA-860M gives them; we have not checked these projects against other sources.

## Limits

As in the pre-registration: the stage is what the respondent reports; a report not updated reads as held; codes outside the ordered bands count as exit_other; renumbered generators without a rule R link read as left; steps are not independent (return and path counts are per generator). From the run: 2026 holds only the steps from January to July 2026, and the outcome and return windows of the latest moves are not yet closed. The shares by year and group are descriptions, not tests: no prediction was made about them.

## Prior art

As in the pre-registration (searched 20 October 2026): no published table of month-to-month EIA-860M status transitions, backward moves or their outcomes. The closest work we found later the same day, before the job ran, is two papers. Mounts and Cross, "Canceled: A New Reliability Incentive for Energy-Only Electricity Markets" (arXiv:2406.15687, 2024), uses EIA-860M from July 2015 to December 2022 for 2,249 ERCOT generators and counts the six pre-operation statuses together as one "applicant pool". It says the authors "cannot confidently determine when a unit enters or exits any of the six applicant pool stages that precede operation", so it tracks the pool's size, entry and exit, not moves between stages. For natural gas generators in Texas it reports that "only 2% of the megawatts from these generators appear in the first applicant pool phase", a related observation that the first stage is often skipped (compare M4, which covers the whole country and asks about the approved stage). Ullrich and Fleten, "Sequential Investment Under Uncertainty" (AEA 2026 annual meeting, session "Infrastructure, Environment, and Market Response"), model transitions between four pooled stages ("Planning, Construction, Indefinitely Postponed, and Canceled") for generators in PJM from the annual EIA-860, and find that "longer time in Planning reduces the probability of Construction and increases the probability of Cancellation"; they do not read monthly reports, backward moves or what follows a move. This note reads each generator's stage in every report and counts the moves between them, nationally, 2016 to 2026.
