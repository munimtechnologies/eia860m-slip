# After three or more misses, a generator planned for the next month is on time less often, and that gap is new

Status: scored against its pre-registration ([`docs/nextcount-plan.md`](nextcount-plan.md), commit bdd4b8b, fixed before job nextcount-v1 counted any earlier listing): 2 of 3 predictions held, and the reproduction check C0 held. K2 failed: in 2022-2025 the share rises by 0.003 from no earlier listing to one. Every number below is recomputed from the cohort file by the doc test [`test_nextcount_doc.py`](../test_nextcount_doc.py), which also checks the job's rows and raw output against it.

Made by MV2 of Munim, Inc. with AI agents working in his name. Text and data: CC BY 4.0. Job nextcount-v1 (24 October 2026) ran [`tools/annual-flows-candidate/nextcount.py`](../tools/annual-flows-candidate/nextcount.py) 0.1.0 (Apache-2.0) unchanged, after its 13 unit tests passed ([`nextcount-v1-unittests.txt`](nextcount-v1-unittests.txt)). Raw output: [`docs/nextcount-v1-output.md`](nextcount-v1-output.md) and the job's log [`docs/nextcount-v1-stdout.txt`](nextcount-v1-stdout.txt). Data: [`data/nextcount_rows.csv`](../data/nextcount_rows.csv) (one row per generator and cohort month, 14,807 rows, with its number of earlier next-month listings and the months since the last one).

## What was measured

Each month EIA-860M lists generators whose developers plan to start them the next month: that month's next-month group, or cohort. A generator that is not operating by then can be planned for a later next month again, so it can be in many cohorts. For every row of the cohort file [`data/nexttech_cohort.csv`](../data/nexttech_cohort.csv) (August 2015 to September 2026), the job counted the generator's earlier cohort months in the file, from August 2015, and asked whether the next workbook lists it as operating ("on time"). Shares are on-time rows over rows, in generator-months, for the cohort months of 2016-2019 and 2022-2025.

## Order of events

The plan was committed at 07:20:25 UTC on 24 October 2026 (commit bdd4b8b). The job started at 07:28:18 UTC; its first poll, at 07:28:19 UTC, was served the plan, and only then did it download the cohort file (950,816 bytes, md5 1681df9fdee9878ca2c359d1239c6467, 14,807 rows, no repeated generator and month) and count anything.

## The check and the bars

| bar | outcome | value |
|---|---|---|
| C0 (check). 14,807 rows that reproduce 1,980 of 4,223 and 2,110 of 6,047 generator-months | held | 14,807 rows; 1,980 of 4,223 and 2,110 of 6,047 |
| K1. In 2022-2025, the share with no earlier listing is above the share with 3 or more | held | 0.362 (866 of 2,393) against 0.306 (428 of 1,398) |
| K2. In 2022-2025, the share does not rise from 0 to 1 to 2 to 3 or more earlier listings | failed | 0.362, 0.365, 0.357, 0.306 |
| K3. The K1 gap is smaller in 2016-2019 than in 2022-2025 | held | 0.010 against 0.056 |

## The shares by earlier next-month listings

| earlier listings | 2016-2019 | 2022-2025 |
|---|---|---|
| 0 | 0.459 (969 of 2,110) | 0.362 (866 of 2,393) |
| 1 | 0.489 (532 of 1,087) | 0.365 (515 of 1,412) |
| 2 | 0.484 (253 of 523) | 0.357 (301 of 844) |
| 3+ | 0.449 (226 of 503) | 0.306 (428 of 1,398) |

Finer (reported, not scored):

| earlier listings | 2016-2019 | 2022-2025 |
|---|---|---|
| 3 | 0.511 (134 of 262) | 0.348 (173 of 497) |
| 4 | 0.480 (49 of 102) | 0.307 (94 of 306) |
| 5-9 | 0.327 (36 of 110) | 0.301 (154 of 511) |
| 10+ | 0.241 (7 of 29) | 0.083 (7 of 84) |

The 10+ rows are few generators: 7 generators at 2 plants in 2016-2019 and 20 generators at 15 plants in 2022-2025.

## K2 failed narrowly: flat for 0 to 2 earlier listings, lower from 3

K2 said the share would not rise from one bin to the next in 2022-2025. It rose once, from 0.362 with no earlier listing to 0.365 with one, by 0.003; from 1 to 2 and from 2 to 3 or more it fell. So the failure is a flat start, not a reversal: in 2022-2025 a generator that had been planned for the next month once or twice before was on time about as often as a new listing, and the share is lower only from 3 earlier listings on (0.348 with 3, about 0.30 with 4 to 9). In 2016-2019 the share was flat or higher up to 4 earlier listings and lower only from 5.

## K3: the gap is new, and plant 60264 does not make it

With no earlier listing against 3 or more, the gap was 0.010 in 2016-2019 and 0.056 in 2022-2025. The plan named one gas plant (60264, 12 turbines) that sits in 2016-2019's bin of 3 or more and could close that period's gap on its own. It works the other way: its 66 generator-months there were on time 6 times. Without the plant, 2016-2019's share with 3 or more earlier listings is 0.503 (220 of 437), above 0.462 (969 of 2,098) with none. The plant has no rows in 2022-2025. Ten years ago, earlier misses did not lower a generator's next-month share; in 2022-2025 three or more did.

## Repeat listings by months since the last one (reported, not scored)

| months since the last listing | 2016-2019 | 2022-2025 |
|---|---|---|
| first listing (no earlier one) | 0.459 (969 of 2,110) | 0.362 (866 of 2,393) |
| 1 month | 0.499 (746 of 1,494) | 0.390 (878 of 2,254) |
| 2-3 months | 0.492 (225 of 457) | 0.260 (231 of 890) |
| 4-12 months | 0.248 (38 of 153) | 0.270 (123 of 455) |
| more than 12 months | 0.222 (2 of 9) | 0.218 (12 of 55) |

EIA's Today in Energy of November 2025 ("Fewer U.S. solar projects are reporting delays in their expected online date") says solar delays are usually short, a month or two, and that much of the delayed capacity is at projects in late construction or testing. That reading suggests a generator that has just missed is close to done. It fits the generators planned for the next month again right after a one-month slip: in 2022-2025 they were on time more often than first listings (0.390 against 0.362). It does not fit those that come back to the next-month group after a gap of 2-3 months: 0.260. Ten years ago those were on time about as often as one-month slips (0.492 against 0.499).

Between the two periods the share fell by 0.097 for first listings, by 0.110 for one-month slips and by 0.233 for slips of 2-3 months, and repeat listings after a gap of 2 months or more grew from 29.3% to 38.3% of all repeat listings. This split was reported, not scored, and it is not split by technology, so it does not test EIA's statement about solar.

## By technology: in 2022-2025 the gap is mostly gas and wind (reported, not scored)

| technology | 0 earlier listings | 3 or more | generators (plants) with 3 or more |
|---|---|---|---|
| solar | 0.361 (536 of 1,483) | 0.332 (265 of 797) | 311 (297) |
| batteries | 0.278 (143 of 514) | 0.309 (129 of 417) | 157 (145) |
| gas | 0.510 (101 of 198) | 0.185 (17 of 92) | 26 (16) |
| wind | 0.500 (59 of 118) | 0.190 (12 of 63) | 18 (16) |
| other | 0.338 (27 of 80) | 0.172 (5 of 29) | 9 (7) |

The gap is not a change of mix. Weighting each technology's share with 3 or more earlier listings by its part of the rows with none gives 0.303, so with the same mix the gap is 0.059, a little more than the 0.056 measured; with the mix of the rows with 3 or more, the share with none would be 0.352 and the gap 0.046. Of the 0.059, gas and wind give 0.042, solar 0.018 and other technologies 0.006, and batteries take away 0.007: a battery planned for the next month three or more times before was on time more often than a new one. Gas and wind are 13.2% of the rows with no earlier listing, and their rows with 3 or more come from 26 gas generators at 16 plants and 18 wind generators at 16 plants, so a few plants weigh heavily. For solar, the largest group, the gap is small.

## What a reader of the monthly file can take from it

In 2022-2025, a generator planned for the next month for the first time, or again right after a one-month slip, was listed as operating in that month 36% to 39% of the time. One planned for the next month three or more times before was listed 31% of the time, and one back after a slip of 2-3 months 26% of the time. These are rates for groups, not forecasts for any one generator.

## Limits

- Generator-months, not generators: a generator listed ten times is in ten rows. Generators at one plant are not independent, so no significance test is made. This is an association, not a cause.
- "On time" is the next workbook's status. A generator listed as operating a month late is not on time here, and one that leaves the file is not on time.
- Earlier listings before August 2015 are not seen, so some 2016-2019 rows sit in a lower bin than they would with a longer history.
- The cohort file was made by this repository's own code; C0 is a reproducibility check, not an independent one.
- Only the three bars were fixed in advance. The finer bins, the months-since table and the technology split were listed in the plan as reported, not scored, and the weighting above was done after the job ran.

## Next

Whether this pattern holds in the next-month groups of January to August 2026, which this note does not count, is pre-registered in [`docs/nextheld-plan.md`](nextheld-plan.md) (three bars), before any 2026 row is counted by earlier listings.

## Prior art

We found no published count of EIA-860M's next-month share by the number of times a generator was planned for the next month before, or by the months since its last such listing. EIA's article above describes solar delays in general. The closest published studies we know of (Mounts and Cross, 2024, on ERCOT; Ullrich and Fleten, 2026, on PJM; see [`README-full-2026-10-20.md`](../README-full-2026-10-20.md#prior-art)) look at one region each. If you know of earlier work, please tell us.
