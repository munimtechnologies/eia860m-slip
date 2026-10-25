# Pre-registration: does the one-month-slip pattern by technology hold when each plant is weighted once?

Status: pre-registered, not yet scored.

Fixed in October 2026, before job plantw-v1 computes any share with each plant weighted once. The job's first step polls this file's address on GitHub and computes nothing until it is served, so the commit time of this file is the record of when the bars below were fixed. They will not be moved after the job runs.

Made by MV2 of Munim, Inc. with AI agents working in his name. Text: CC BY 4.0. Code: [`tools/annual-flows-candidate/plantw.py`](../tools/annual-flows-candidate/plantw.py) 0.1.0 (Apache-2.0), with its tests. It uses only Python's standard library and the cells of [`gaptech.py`](../tools/annual-flows-candidate/gaptech.py) 0.1.0, written out again so that the job needs no other file.

## Why

Every note in this series counts generator-months and says the same limit: generators at one plant are not independent. A plant with many generators, or one generator planned for the next month again and again, weighs more than a plant with one. The thirty-eighth and thirty-ninth results ([`docs/nextgaptech.md`](nextgaptech.md), [`docs/gapwin.md`](gapwin.md)) found that, in generator-months, a generator planned for the next month again right after a one-month slip was on time more often than a new listing in solar and batteries in every period since 2016, and less often in wind. Gas went the same way as wind in the periods where that was found, and by only 0.005 in the held-out one. This plan asks whether the pattern holds when each plant counts once.

## The rule

The job reads [`data/nexttech_cohort.csv`](../data/nexttech_cohort.csv) at commit ea63c15 and puts every row in a cell as `gaptech.py` does: a first listing (no earlier next-month listing of that generator since August 2015) or a repeat listing by the months since the generator's last one (1, 2-3, 4-12, more than 12). A row is on time if that month's workbook lists the generator as operating. A plant is the part of the generator key before the slash (EIA's plant ID). For each cell, each plant's share of on-time rows among its rows in that cell is computed, and the cell's plant-weighted share is the mean of those shares over the plants with rows in it. The pooled period is January 2016 to December 2025; P5 uses January 2022 to August 2026. Technology groups are the cohort file's `group` column.

## What was known when this plan was fixed

- The generator-month cells of each period and their counts of distinct generators and plants ([`docs/nextgaptech-v2-output.md`](nextgaptech-v2-output.md), [`docs/gapwin-v1-output.md`](gapwin-v1-output.md)). Added over 2016-2019, 2020-2021 and 2022-2025, the compared cells in generator-months are:
  - solar: first listings 0.413 (1,474 of 3,568), 1 month after the last listing 0.463 (1,230 of 2,657);
  - batteries: first listings 0.282 (205 of 728), 1 month after the last listing 0.364 (297 of 816);
  - wind: first listings 0.477 (237 of 497), 1 month after the last listing 0.411 (191 of 465);
  - gas: first listings 0.454 (312 of 687), 1 month after the last listing 0.358 (206 of 576);
  - and for P5, solar from January 2022 to August 2026: 1 month after the last listing 0.391 (639 of 1,636), 2-3 months after 0.266 (171 of 644).
- In 2020-2021, gas's one-month cell had 71 generators at 28 plants and its first listings 168 at 62.
- No share with each plant weighted once was computed for any cell, and the number of distinct plants in the pooled cells was not counted.

## Check (not a prediction)

- **C0.** The file has 14,807 rows and md5 1681df9fdee9878ca2c359d1239c6467, and its pooled 2016-2025 solar cells reproduce, in generator-months, first listings 1,474 of 3,568 and 1 month after the last listing 1,230 of 2,657. If C0 fails, P1 to P5 are reported as not scored.

## Predictions

Each plant weighted once:

- **P1.** 2016-2025, solar: repeat listings 1 month after the last one are on time more often than first listings.
- **P2.** 2016-2025, batteries: repeat listings 1 month after the last one are on time more often than first listings.
- **P3.** 2016-2025, wind: repeat listings 1 month after the last one are on time less often than first listings.
- **P4.** 2016-2025, gas: repeat listings 1 month after the last one are on time less often than first listings.
- **P5.** January 2022 to August 2026, solar: repeat listings 1 month after the last one are on time more often than those 2-3 months after.

Every cell a prediction compares needs at least 30 plants; a prediction with fewer is reported as not scored. A tie counts as failed. Results are reported as "N of the scored predictions held".

## How each could fail

P4 is the riskiest: gas's one-month cell sits at few plants, so a handful of plants whose generators slip again and again may carry the generator-month gap, and in 2020-2021 that gap was only 0.005. P1 could fail if solar's one-month advantage (0.050 in generator-months) comes from large plants with many generators that slip together; in plant terms such a plant counts once. P3 could fail for the same reason in wind, whose farms often list many turbines or phases as separate generators. P2 and P5 have the widest generator-month margins (0.082 and 0.125). If P1, P2 and P5 hold and P3 or P4 fails, the solar and battery pattern does not depend on how plants are weighted, but the wind or gas reversal does.

## Also reported, not scored

Every cell for each technology group and for all technologies together, in each of 2016-2019, 2020-2021, 2022-2025 and January to August 2026, and pooled, with generator-months, on-time rows, generator-month share, plants and plant-weighted share.

## Limits

- Weighting each plant once removes one kind of dependence, not all: plants of one developer, region or year are not independent either. No significance test is made. This is an association, not a cause.
- A plant with one row in a cell has a share of 0 or 1, so the plant-weighted share of a small cell moves in large steps.
- "On time" is the next workbook's status: one listed as operating a month late is not on time, and one that leaves the file is not on time.
- The cohort file was made by this repository's own code; C0 is a reproducibility check, not an independent one.
