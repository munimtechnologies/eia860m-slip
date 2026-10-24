# In 2026, a generator planned for the next month right after a one-month slip was on time more often than a new one; one back after a longer slip, less often

Status: scored against its pre-registration ([`docs/nextheld-plan.md`](nextheld-plan.md), commit f72579e, fixed before job nextheld-v1 counted any 2026 row by earlier listings): 3 of 3 predictions held, and the reproduction check C1 held. Every number below is recomputed from the cohort file by the doc test [`test_nextheld_doc.py`](../test_nextheld_doc.py), which also checks the job's raw output against it.

Made by MV2 of Munim, Inc. with AI agents working in his name. Text: CC BY 4.0. Job nextheld-v1 (24 October 2026) ran [`tools/annual-flows-candidate/nextheld.py`](../tools/annual-flows-candidate/nextheld.py) 0.1.0 (Apache-2.0) unchanged, with [`nextcount.py`](../tools/annual-flows-candidate/nextcount.py) 0.1.0 fetched at commit bdd4b8b, after its 11 unit tests passed ([`nextheld-v1-unittests.txt`](nextheld-v1-unittests.txt)). Raw output: [`docs/nextheld-v1-output.md`](nextheld-v1-output.md) and the job's log [`docs/nextheld-v1-stdout.txt`](nextheld-v1-stdout.txt). Data: the 2026 rows of [`data/nextcount_rows.csv`](../data/nextcount_rows.csv).

## What was tested

The thirty-sixth result ([`docs/nextcount.md`](nextcount.md)) counted, for each generator in a month's next-month group of 2016-2019 and 2022-2025, how many times it had been planned for the next month before. Its clearest patterns were in tables reported, not scored: right after a one-month slip a generator was on time more often than a first listing, and after a slip of 2-3 months much less often. A pattern found in data needs a test on data it was not found in. This note scores three bars, fixed in advance, on the next-month groups of January to August 2026, which that note did not count. September 2026 was left out because its split into first and repeat listings was already published.

"On time" means that month's workbook lists the generator as operating. Shares are in generator-months.

## Order of events

The plan was committed at 08:58:33 UTC on 24 October 2026 (commit f72579e). The job's first poll, at 09:20:31 UTC, was served the plan, and only then did it download the cohort file [`data/nexttech_cohort.csv`](../data/nexttech_cohort.csv) at commit ea63c15 (950,816 bytes, md5 1681df9fdee9878ca2c359d1239c6467, 14,807 rows) and count anything.

## The check and the bars

| bar | outcome | value |
|---|---|---|
| C1 (check). Each month's rows and on-time rows as in `data/monthcheck_months_2026-09.csv` | held | 366 of 1,194 in 8 months, each month equal |
| H1. The share with 3 or more earlier listings is below the share with none | held | 0.270 (66 of 244) against 0.304 (144 of 473) |
| H2. Repeat listings 1 month after the last one are on time more often than those 2-3 months after | held | 0.347 (166 of 479) against 0.249 (43 of 173) |
| H3. Repeat listings 1 month after the last one are on time more often than first listings | held | 0.347 (166 of 479) against 0.304 (144 of 473) |

Every compared cell has at least 30 rows, so all three were scored.

| month | on time | generator-months |
|---|---|---|
| 2026-01 | 46 | 136 |
| 2026-02 | 20 | 114 |
| 2026-03 | 38 | 156 |
| 2026-04 | 71 | 168 |
| 2026-05 | 35 | 140 |
| 2026-06 | 70 | 216 |
| 2026-07 | 47 | 140 |
| 2026-08 | 39 | 124 |

## Beside the earlier periods

| | 2016-2019 | 2022-2025 | January-August 2026 |
|---|---|---|---|
| first listing (no earlier one) | 0.459 (969 of 2,110) | 0.362 (866 of 2,393) | 0.304 (144 of 473) |
| 1 month after the last listing | 0.499 (746 of 1,494) | 0.390 (878 of 2,254) | 0.347 (166 of 479) |
| 2-3 months after the last listing | 0.492 (225 of 457) | 0.260 (231 of 890) | 0.249 (43 of 173) |
| 3 or more earlier listings | 0.449 (226 of 503) | 0.306 (428 of 1,398) | 0.270 (66 of 244) |

All four shares are lower in 2026 than in 2022-2025, as is the share of the whole group (0.307, against 0.349). The orderings held. H2's margin was 0.098 in 2026, against 0.130 in 2022-2025 and 0.007 in 2016-2019. H3's margin was 0.042 in 2026, larger than the 0.028 of 2022-2025 that made it the riskiest bar. H1's margin was 0.034, against 0.056 in 2022-2025.

## The months since the last listing matter more than the number of listings

| months since the last listing | generator-months | on time | share |
|---|---|---|---|
| 1 month | 479 | 166 | 0.347 |
| 2-3 months | 173 | 43 | 0.249 |
| 4-12 months | 57 | 12 | 0.211 |
| more than 12 months | 12 | 1 | 0.083 |

Taken together, the 2026 repeat listings were on time about as often as first listings: 0.308 (222 of 721) against 0.304. What separates them is how recently the generator was last planned for the next month: the share falls with each longer gap (the last cell is only 12 rows).

By the number of earlier listings (reported, not scored):

| earlier listings | generator-months | on time | share | generators (plants) |
|---|---|---|---|---|
| 0 | 473 | 144 | 0.304 | 473 (388) |
| 1 | 299 | 94 | 0.314 | 299 (246) |
| 2 | 178 | 62 | 0.348 | 178 (151) |
| 3 | 93 | 32 | 0.344 | 93 (81) |
| 4 | 59 | 19 | 0.322 | 59 (54) |
| 5-9 | 65 | 12 | 0.185 | 41 (36) |
| 10+ | 27 | 3 | 0.111 | 9 (8) |

H1 held, but not the way the thirty-sixth result's 2022-2025 table suggested. In 2026 every bin from 1 to 4 earlier listings is at or above the share with none; generators with 3 or 4 were on time 0.336 (51 of 152). The H1 gap comes from 5 or more earlier listings: 0.163 (15 of 92). That is closer to 2016-2019, when the share was flat or higher up to 4 earlier listings and lower only from 5.

## H1 depends on the mix of technologies (reported, not scored)

| technology | 0 earlier listings | 3 or more |
|---|---|---|
| solar | 0.290 (82 of 283) | 0.248 (37 of 149) |
| batteries | 0.238 (29 of 122) | 0.300 (21 of 70) |
| gas | 0.600 (27 of 45) | 0.167 (1 of 6) |
| wind | 0.222 (2 of 9) | 0.091 (1 of 11) |
| other | 0.286 (4 of 14) | 0.750 (6 of 8) |

Weighting each technology's share with 3 or more earlier listings by its part of the rows with none gives 0.266, so with that mix the gap is 0.039. With the mix of the rows with 3 or more, the share with none would be 0.279 and the gap only 0.009. Of the 0.039, solar gives 0.025 and gas and wind 0.044, while batteries take away 0.016 and other technologies 0.014; the gas, wind and other cells with 3 or more have 6, 11 and 8 rows. Gas first listings (0.600, 27 of 45, at 13 plants) lift the share with none. So H1's direction holds either way, but its size is small and rests on few plants. Batteries go the other way again, as in 2022-2025 (0.278 with none against 0.309 with 3 or more): a battery planned for the next month three or more times before was on time more often than a new one. For solar, the largest group, the gap is 0.041.

The months-since bins were not split by technology, so this note cannot say whether H2 and H3 hold within solar, as EIA's November 2025 Today in Energy article on short solar delays would suggest.

## What a reader of the monthly file can take from it

In January to August 2026, a generator planned for the next month again right after a one-month slip was listed as operating in that month 35% of the time, and a first listing 30% of the time. One back after a slip of 2-3 months was listed 25% of the time, after 4-12 months 21%, and one planned for the next month five or more times before 16%. These are rates for groups, not forecasts for any one generator.

## Limits

- Eight months. Generators at one plant are not independent, so no significance test is made. This is an association, not a cause.
- Generator-months, not generators: a generator listed in several 2026 months is in several rows.
- "On time" is the next workbook's status. A generator listed as operating a month late is not on time here, and one that leaves the file is not on time.
- The cohort file was made by this repository's own code; C1 is a reproducibility check against another of its outputs, not an independent one.
- Only C1 and the three bars were fixed in advance. The finer bins, the months-since table beyond H2 and H3, and the technology table were listed in the plan as reported, not scored; the weighting above was done after the job ran.

## Prior art

We found no published count of EIA-860M's next-month share by the months since a generator's last next-month listing other than this repository's thirty-sixth result, which found the pattern this note tests. If you know of earlier work, please tell us.
