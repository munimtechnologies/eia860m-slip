# Does lead time matter less for a generator that is already being built? Stage by lead time in EIA-860M

Status: scored against its pre-registration ([`stage-leadtime-preregistration.md`](stage-leadtime-preregistration.md)). All checks passed; 4 of 6 predictions held. MV2 of Munim, Inc. (made with AI agents). CC BY 4.0.

## What this is

The first full run of eia860m_slip ([`annual-flows-run1-slip.md`](annual-flows-run1-slip.md)) gave the share of planned capacity online by its planned month by development stage and, separately, by months ahead. This note crosses the two. A row is a generator listed as planned (P, L, T, U, V, TS, OT) in an EIA-860M report with a planned operating month 0-24 months ahead, scored once its outcome window has closed: on time (online by the planned month), late (online 1-12 months after it) or not online (not within 12 months of it). Shares are of MW. Stages: early = P (planned, approvals not started) and L (approvals pending); approved = T (approvals received, not under construction); U (under construction, half or less complete); V (under construction, more than half complete); TS (construction complete, not yet operating); OT (other). Data: PUDL's EIA-860M changelog, reports to 2026-08, report months 2016-01 to 2023-06 so that every lead band covers the same months: 87,351 rows, 6,483 generators, 6,582,226.3 MW summed over rows. Job `leadtime-v1` (2 GB) fetched eia860m_slip.py (commit 329b7e6) and leadtime.py and test_leadtime.py (commit 9ee085b, the commit that published the pre-registration), ran the unit tests, then the tool, on 20 October 2026. Raw output: [`leadtime-v1-output.md`](leadtime-v1-output.md), [`../data/leadtime_v1.json`](../data/leadtime_v1.json); unit tests: [`leadtime-v1-unittests.txt`](leadtime-v1-unittests.txt). Shares are shown to three decimals from the job's four-decimal values.

## What we found

**Pooled over all stages, the on-time share falls steadily with lead time; inside most stages it does not.** Over all rows, the on-time share is 0.391 at 0-3 months, 0.331 at 4-6, 0.280 at 7-12 and 0.159 at 13-24 (computed from the cells table below; not pre-registered). Of the four stages the predictions are about, only approved (T) falls band by band (0.255, 0.225, 0.210, 0.176). Early-stage plans (P, L) sit between 0.125 and 0.158 at every lead. For plants under construction the share hardly moves within a year of the planned month and drops beyond it: U is 0.302, 0.285 and 0.322 at 0-3, 4-6 and 7-12 months, then 0.246 at 13-24; V is 0.409, 0.425 and 0.368, then 0.139. So L1, that for U and for V the share would never rise from one band to the next, failed for both. Much of the pooled gradient is a change of mix: at 0-3 months 0.969 of the MW is under construction or testing (U, V, TS), at 13-24 months 0.217.

**Beyond a year, what grows is not lateness but not coming online at all.** The share not online within 12 months of the planned month is 0.117 at 0-3 months and 0.462 at 13-24 for U, and 0.058 and 0.295 for V.

**Even a plant more than half built and due within three months was late more often than on time.** V at 0-3 months: 0.409 on time, 0.533 late, 0.058 not online (11,795 rows of 3,421 generators). L3 put the on-time share at 0.45 or more; it failed. Of that MW, 0.942 came online by 12 months after the planned month: the month is optimistic, the plant is real.

**For early-stage plans the clock says almost nothing, and the stage says more than the clock.** From 0-3 to 13-24 months the early on-time share falls by 0.0068, against 0.2699 for V (L2 held). An early plan 13-24 months out was on time for 0.125 of its MW (L4 held, ceiling 0.20), and 0.699 of it was not online within 12 months of its planned month (L6 held, floor 0.50). V at 7-12 months was on time for 0.368 of its MW, against 0.132 for early plans due within 3 months (L5 held). Every U cell (lowest 0.246) is above every early cell (highest 0.158), and every V cell up to 12 months (lowest 0.368) is above every approved cell (highest 0.255).

**Counting generators instead of MW changes little.** In all 16 prediction cells the count-based on-time share is within 0.09 of the MW share (largest gap V at 4-6 months: 0.338 by count, 0.425 by MW); in 14 of the 16 it is lower, so in most cells the larger generators were on time more often than the smaller ones. The cell behind L1's failure for V at 13-24 months is the thinnest: 79 generators, 315 rows.

**By technology** the grids carry no generator counts and were not checked for thin cells, so read them with care. The largest departure from the all-generators grid is gas combined cycle, early stage, 4-6 months (1.000 against 0.140); a share of exactly 1.000 or 0.000, as in several gas cells, means every MW in the cell had the same outcome. Battery plans at the early stages were on time for at most 0.072 of their MW in every band.

For anyone reading EIA-860M's planned months: within a year of the planned month, the status code carries most of the information and the distance little; a planned month more than a year out is a weak forecast at every stage, and for a plan not yet approved, so is any planned month. These are associations in the survey's own records, not causes.

## Checks (all passed)

| check | result |
|---|---|
| C1 | 2017-01 66,278.6 MW, 833 rows; 2019-01 56,235.6 MW, 792 rows; 2021-01 80,740.6 MW, 1,061 rows |
| C2 | 16 cells, fewest generators 79 |
| C3 | 24 cells, 87,351 rows, 0 not adding up |
| C4 | 0 duplicates, 0 rows outside 2016-01 to 2023-06 |
| unit tests | 10 of 10 passed |

## Predictions (4 of 6 held)

| prediction | stated before the run | result | verdict |
|---|---|---|---|
| L1 | for U and for V, the on-time share is non-increasing from 0-3 to 13-24 months (ties allowed) | U 0.3017, 0.2848, 0.3220, 0.2457; V 0.4088, 0.4253, 0.3683, 0.1389 | failed |
| L2 | the fall in on-time share from 0-3 to 13-24 months is larger for V than for early (P, L) | fall V 0.2699, early 0.0068 | held |
| L3 | V due within 3 months: on time for at least 0.45 of MW | 0.4088 | failed |
| L4 | early 13-24 months out: on time for at most 0.20 of MW | 0.1247 | held |
| L5 | V at 7-12 months beats early at 0-3 months | V 07-12 0.3683, early 00-03 0.1316 | held |
| L6 | early 13-24 months out: at least 0.50 of MW not online within 12 months of the planned month | 0.6992 | held |

The pre-registration said that if L1 and L2 held, lead time would be informative mainly for plants already under construction. L2 held and L1 did not: inside U and V lead time is informative only beyond 12 months, and early-stage plans are flat at every lead.

## On-time share by stage and lead band, all generators (MW)

| stage | 00-03 | 04-06 | 07-12 | 13-24 |
|---|---|---|---|---|
| early | 0.132 | 0.140 | 0.158 | 0.125 |
| approved | 0.255 | 0.225 | 0.210 | 0.176 |
| U | 0.302 | 0.285 | 0.322 | 0.246 |
| V | 0.409 | 0.425 | 0.368 | 0.139 |

## On-time share by stage and lead band, by technology (MW)

| group | stage | 00-03 | 04-06 | 07-12 | 13-24 |
|---|---|---|---|---|---|
| solar | early | 0.136 | 0.112 | 0.138 | 0.091 |
| solar | approved | 0.326 | 0.182 | 0.189 | 0.143 |
| solar | U | 0.264 | 0.267 | 0.299 | 0.236 |
| solar | V | 0.427 | 0.432 | 0.257 | 0.211 |
| battery | early | 0.068 | 0.064 | 0.072 | 0.051 |
| battery | approved | 0.360 | 0.102 | 0.077 | 0.163 |
| battery | U | 0.148 | 0.141 | 0.191 | 0.180 |
| battery | V | 0.250 | 0.215 | 0.331 | 0.337 |
| wind_onshore | early | 0.103 | 0.286 | 0.262 | 0.156 |
| wind_onshore | approved | 0.590 | 0.459 | 0.338 | 0.276 |
| wind_onshore | U | 0.343 | 0.341 | 0.387 | 0.122 |
| wind_onshore | V | 0.466 | 0.482 | 0.497 | 0.747 |
| gas_cc | early | 0.727 | 1.000 | 0.033 | 0.247 |
| gas_cc | approved | 0.000 | 0.000 | 0.000 | 0.217 |
| gas_cc | U | 0.399 | 0.318 | 0.331 | 0.365 |
| gas_cc | V | 0.398 | 0.446 | 0.455 | 0.198 |
| gas_ct | early | 0.002 | 0.059 | 0.097 | 0.092 |
| gas_ct | approved | 1.000 | 0.000 | 0.016 | 0.028 |
| gas_ct | U | 0.112 | 0.136 | 0.232 | 0.046 |
| gas_ct | V | 0.309 | 0.360 | 0.395 | 0.141 |

## Every cell

| stage | band | rows | generators | MW | on time | late | not online | on time (count) |
|---|---|---|---|---|---|---|---|---|
| early | 00-03 | 875 | 448 | 18,497.4 | 0.132 | 0.303 | 0.565 | 0.210 |
| early | 04-06 | 2,728 | 963 | 64,322.4 | 0.140 | 0.315 | 0.545 | 0.115 |
| early | 07-12 | 7,593 | 1,416 | 357,996.4 | 0.158 | 0.318 | 0.524 | 0.113 |
| early | 13-24 | 17,387 | 1,527 | 1,875,236.4 | 0.125 | 0.176 | 0.699 | 0.094 |
| approved | 00-03 | 791 | 477 | 10,447.0 | 0.255 | 0.265 | 0.481 | 0.197 |
| approved | 04-06 | 1,999 | 831 | 36,149.3 | 0.225 | 0.420 | 0.354 | 0.156 |
| approved | 07-12 | 4,272 | 1,042 | 171,988.0 | 0.210 | 0.433 | 0.357 | 0.158 |
| approved | 13-24 | 6,665 | 589 | 630,726.9 | 0.176 | 0.285 | 0.539 | 0.117 |
| U | 00-03 | 5,131 | 1,774 | 190,762.7 | 0.302 | 0.582 | 0.117 | 0.236 |
| U | 04-06 | 5,316 | 2,130 | 311,576.7 | 0.285 | 0.571 | 0.144 | 0.245 |
| U | 07-12 | 6,247 | 1,552 | 649,498.4 | 0.322 | 0.494 | 0.184 | 0.283 |
| U | 13-24 | 4,138 | 506 | 636,740.1 | 0.246 | 0.292 | 0.462 | 0.194 |
| V | 00-03 | 11,795 | 3,421 | 627,147.3 | 0.409 | 0.533 | 0.058 | 0.366 |
| V | 04-06 | 3,599 | 1,470 | 356,847.4 | 0.425 | 0.500 | 0.074 | 0.338 |
| V | 07-12 | 1,901 | 548 | 323,299.3 | 0.368 | 0.498 | 0.134 | 0.300 |
| V | 13-24 | 315 | 79 | 57,078.8 | 0.139 | 0.566 | 0.295 | 0.206 |
| TS | 00-03 | 5,480 | 1,745 | 234,061.2 | 0.444 | 0.484 | 0.071 | 0.444 |
| TS | 04-06 | 711 | 291 | 17,581.9 | 0.133 | 0.679 | 0.188 | 0.340 |
| TS | 07-12 | 117 | 33 | 786.4 | 0.168 | 0.305 | 0.527 | 0.470 |
| TS | 13-24 | 30 | 4 | 96.7 | 0.736 | 0.000 | 0.264 | 0.967 |
| OT | 00-03 | 69 | 20 | 4,573.0 | 0.207 | 0.133 | 0.659 | 0.159 |
| OT | 04-06 | 43 | 18 | 1,767.6 | 0.424 | 0.336 | 0.240 | 0.093 |
| OT | 07-12 | 81 | 19 | 3,338.8 | 0.449 | 0.064 | 0.487 | 0.074 |
| OT | 13-24 | 68 | 9 | 1,706.2 | 0.146 | 0.000 | 0.854 | 0.015 |

## Limits

As in the pre-registration: the planned month is the respondent's current plan, so a plan pushed back month after month produces many short-lead rows, each scored on its own (the count-based share and the generator counts show how much of a cell is repeated rows); the stage is what the respondent reports; rows are not independent; report months after 2023-06 are not read (a follow-up can read leads of 0-12 months to a later month and compare); OT's meaning changed over time and TS and OT are outside the predictions; re-keyed plants are not linked and read as not online under the old key. Not pre-registered: the pooled shares by band and the mix shares in the first finding are computed from the cells table's four-decimal shares, and which generators make up the U and V cells at 13-24 months has not been read; the per-row output (not in the repository; `leadtime.py` rebuilds it) holds that.

## Prior art

As in the pre-registration (searched 20 October 2026). EIA publishes the status codes and no delivery rate by stage or lead time; LBNL's "Queued Up" reports completion by interconnection-queue stage, an earlier pipeline. Mounts and Cross, "Canceled: A New Reliability Incentive for Energy-Only Electricity Markets" (arXiv:2406.15687, 2024), pool the six pre-operation statuses of 2,249 ERCOT generators as one "applicant pool" and do not analyse planned dates. Ullrich and Fleten, "Sequential Investment Under Uncertainty" (AEA 2026 annual meeting, session "Infrastructure, Environment, and Market Response"), model transitions between four pooled stages ("Planning, Construction, Indefinitely Postponed, and Canceled") for generators in PJM from the annual EIA-860. Neither scores planned months as forecasts, splits U from V, or resolves lead time. This note does all three, nationally and for all technologies.

## Correction and follow-up, 20 October 2026

Added after scoring; the text above is left as it was scored. **Correction:** the sentence "The cell behind L1's failure for V at 13-24 months is the thinnest: 79 generators, 315 rows." is wrong in one part. The cell is the thinnest, but it is not behind L1's failure for V: V's share rises from 0-3 to 4-6 months (0.4088 to 0.4253), and the 13-24 cell is V's lowest, which is consistent with L1. L1's verdict (failed) is unchanged. **Follow-up:** which generators make up the U and V cells at 13-24 months has now been read, in [`stage-leadtime-cells.md`](stage-leadtime-cells.md) (job `cellmakeup-v1`, a description, not a scored check). V at 13-24 months is mostly a few large projects: Vogtle alone holds 0.312 of its MW. L2's verdict does not rest on Vogtle.
