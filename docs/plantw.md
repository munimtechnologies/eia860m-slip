# Weighting each plant once lifts every repeat-listing cell, so it cannot settle the wind and gas reversals

Status: scored against its pre-registration ([`docs/plantw-plan.md`](plantw-plan.md), commit c3520c3, fixed before job plantw-v1 computed any share with each plant weighted once): 3 of 5 predictions held, and the reproduction check C0 held. P3 and P4 failed. Every number below is recomputed from the cohort file by the doc test [`test_plantw_doc.py`](../test_plantw_doc.py), which also checks the job's raw output against it.

Made by MV2 of Munim, Inc. with AI agents working in his name. Text: CC BY 4.0. Job plantw-v1 (25 October 2026) ran [`tools/annual-flows-candidate/plantw.py`](../tools/annual-flows-candidate/plantw.py) 0.1.0 (Apache-2.0) unchanged, after its 11 unit tests passed ([`plantw-v1-unittests.txt`](plantw-v1-unittests.txt)). Raw output: [`docs/plantw-v1-output.md`](plantw-v1-output.md) and the job's log [`docs/plantw-v1-stdout.txt`](plantw-v1-stdout.txt).

## What was tested

Every note in this series counts generator-months and says the same limit: generators at one plant are not independent. The thirty-eighth and thirty-ninth results ([`docs/nextgaptech.md`](nextgaptech.md), [`docs/gapwin.md`](gapwin.md)) found, in generator-months, that a generator planned for the next month again right after a one-month slip was on time more often than a new listing in solar and batteries, and less often in wind. The plan asked whether that holds when each plant counts once: within a cell, each plant's share of on-time rows is computed first, and the cell's share is the mean over its plants. Five bars were fixed in advance, four on 2016-2025 pooled and one on January 2022 to August 2026.

"On time" means that month's workbook lists the generator as operating.

## Order of events

The plan was committed at 03:35:47 UTC on 25 October 2026 (commit c3520c3). The job's first poll of the plan's address, at 05:22:50 UTC, was served the plan. Only then did it download the cohort file [`data/nexttech_cohort.csv`](../data/nexttech_cohort.csv) at commit ea63c15 (950,816 bytes, md5 1681df9fdee9878ca2c359d1239c6467, 14,807 rows) and compute anything.

## The check and the bars

| bar | outcome | value (each plant weighted once) |
|---|---|---|
| C0 (check). The file's rows and md5 and the pooled 2016-2025 solar cells in generator-months, as already published | held | 14,807 rows, md5 1681df9fdee9878ca2c359d1239c6467; solar first listings 1,474 of 3,568, 1 month after the last listing 1,230 of 2,657 |
| P1. Solar, 2016-2025: 1 month after the last listing above first listings | held | 0.624 over 1,381 plants against 0.417 over 3,316 plants |
| P2. Batteries, 2016-2025: 1 month after the last listing above first listings | held | 0.519 over 371 plants against 0.279 over 680 plants |
| P3. Wind, 2016-2025: 1 month after the last listing below first listings | failed | 0.665 over 198 plants against 0.495 over 460 plants |
| P4. Gas, 2016-2025: 1 month after the last listing below first listings | failed | 0.586 over 108 plants against 0.425 over 246 plants |
| P5. Solar, January 2022 to August 2026: 1 month after the last listing above 2-3 months after | held | 0.545 over 791 plants against 0.323 over 443 plants |

Every compared cell has at least 30 plants, so all five were scored. Read alone, P3 and P4 would say that the wind and gas reversals come from a few plants. The next section shows why that reading is not safe.

## Why weighting each plant once lifts the repeat cells (found after scoring)

Pooled over 2016-2025, the share of the same cells counted both ways:

| technology | first listings, generator-months | first listings, each plant once | 1 month after, generator-months | 1 month after, each plant once |
|---|---|---|---|---|
| solar | 0.413 | 0.417 | 0.463 | 0.624 |
| batteries | 0.282 | 0.279 | 0.364 | 0.519 |
| gas | 0.454 | 0.425 | 0.358 | 0.586 |
| wind | 0.477 | 0.495 | 0.411 | 0.665 |
| all technologies | 0.404 | 0.411 | 0.428 | 0.610 |

Weighting each plant once moves first listings by at most 0.029 in any of the four technologies, and lifts the one-month cell by 0.155 to 0.254 in every one of them. For all technologies together the one-month cell is lifted more than first listings in each of 2016-2019, 2020-2021, 2022-2025 and January to August 2026.

This follows from how the cells are built, and we did not see it when we wrote the plan. A row is in the one-month cell only if the same generator was planned for the month before too, and so had not come online then. A plant collects more rows in that cell by missing more months, so the more rows a plant has there, the lower its share tends to be. Counting generator-months weighs each plant by its rows; weighting each plant once gives a plant with one on-time row the same weight as a plant whose generators missed month after month, and the mean of the plants' shares then sits above the share of all rows. A first listing is a generator's first next-month listing, so in that cell a plant's rows are just its generators, and the two ways of counting stay close.

So the plant-weighted share answers a different question from the one the series asks (how often is a listing on time), and it favours every repeat cell by construction. P1, P2 and P5 holding says little for that reason, and P3 and P4 failing does not show that the wind and gas reversals come from a few plants. The plan's sentence on how the bars could fail ("If P1, P2 and P5 hold and P3 or P4 fails, ... the wind or gas reversal does" depend on how plants are weighted) is true as written, but most of that dependence is the weighting's own lift.

The test the series still needs keeps the share per listing and treats each plant as a cluster: resample whole plants, with all their rows, and see whether each gap stays on the same side of zero. That is the next pre-registered test, [`docs/clusterboot-plan.md`](clusterboot-plan.md).

## What a reader of the monthly file can take from it

Nothing changes in the generator-month results of the thirty-eighth and thirty-ninth notes: they stand as they were, with the same limit. For anyone who analyses EIA-860M's repeat listings, this note is a warning: averaging over plants gives a plant that slips once and then comes online the same weight as one that slips for a year, and that alone lifts every repeat-listing share.

## Limits

- The explanation above follows from how the cells are defined; this note does not measure how much of each lift it accounts for.
- Only C0 and the five bars were fixed in advance. The table of both ways of counting, the lift by period and the explanation were found after scoring.
- No significance test is made. This is an association, not a cause.
- "On time" is the next workbook's status: one listed as operating a month late is not on time, and one that leaves the file is not on time.
- The cohort file was made by this repository's own code; C0 is a reproducibility check, not an independent one.

## Prior art

Whether to average within clusters first or pool all rows is a standard choice in statistics, and the two answer different questions when cluster size depends on the outcome. We found no EIA-860M analysis that weights next-month listings by plant, or that points out this effect for repeat listings. If you know of earlier work, please tell us.
