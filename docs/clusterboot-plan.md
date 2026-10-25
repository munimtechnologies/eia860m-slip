# Pre-registration: do the one-month-slip gaps survive when whole plants are resampled?

Status: pre-registered, not yet scored.

Fixed in October 2026, before job clusterboot-v1 resamples any plant. The job's first step polls this file's address on GitHub and computes nothing until it is served, so the commit time of this file is the record of when the bars below were fixed. They will not be moved after the job runs.

Made by MV2 of Munim, Inc. with AI agents working in his name. Text: CC BY 4.0. Code: [`tools/annual-flows-candidate/clusterboot.py`](../tools/annual-flows-candidate/clusterboot.py) 0.1.0 (Apache-2.0), with its tests. It uses only Python's standard library and the cells of [`gaptech.py`](../tools/annual-flows-candidate/gaptech.py) 0.1.0 and [`plantw.py`](../tools/annual-flows-candidate/plantw.py) 0.1.0, written out again so that the job needs no other file.

## Why

Every note in this series counts generator-months and says that generators at one plant are not independent, so no significance test was made. The fortieth result ([`docs/plantw.md`](plantw.md)) tried weighting each plant once and found that this weighting lifts every repeat-listing cell, because a plant collects more rows in such a cell by missing more months; it changed the question instead of answering it. This plan keeps the share of generator-months on time and treats each plant as a cluster: it resamples whole plants, with all their rows in both compared cells, and asks whether each gap stays on the same side of zero.

## The rule

The job reads [`data/nexttech_cohort.csv`](../data/nexttech_cohort.csv) at commit ea63c15 and puts every row in a cell as `gaptech.py` does: a first listing (no earlier next-month listing of that generator since August 2015) or a repeat listing by the months since the generator's last one (1, 2-3, 4-12, more than 12). A row is on time if that month's workbook lists the generator as operating. A plant is the part of the generator key before the slash (EIA's plant ID). Technology groups are the cohort file's `group` column.

For each bar it takes the plants with rows in either compared cell and the difference of the two cells' shares (on-time generator-months over generator-months) in the bar's direction. It then draws 2,000 resamples, each the same number of those plants drawn with replacement (Python's `random.Random(20261025).choices`, plants in sorted order, a new generator with the same seed for each bar), recomputes the difference from all rows of the drawn plants (a plant drawn twice counts twice), and sorts the 2,000 differences. The 95% interval runs from the 51st to the 1,950th of them. The pooled period is January 2016 to December 2025; B5 uses January 2022 to August 2026.

## What was known when this plan was fixed

- The generator-month cells and the plants in each, from [`docs/plantw-v1-output.md`](plantw-v1-output.md), pooled over 2016-2025:
  - solar: 1 month after the last listing 0.463 (1,230 of 2,657) at 1,381 plants, first listings 0.413 (1,474 of 3,568) at 3,316 plants; 1 month minus first +0.050
  - batteries: 1 month after the last listing 0.364 (297 of 816) at 371 plants, first listings 0.282 (205 of 728) at 680 plants; 1 month minus first +0.082
  - wind: 1 month after the last listing 0.411 (191 of 465) at 198 plants, first listings 0.477 (237 of 497) at 460 plants; 1 month minus first -0.066
  - gas: 1 month after the last listing 0.358 (206 of 576) at 108 plants, first listings 0.454 (312 of 687) at 246 plants; 1 month minus first -0.097
  - and for B5, solar from January 2022 to August 2026: 1 month after the last listing 0.391 (639 of 1,636) at 791 plants, 2-3 months after 0.266 (171 of 644) at 443 plants; 1 month minus 2-3 months +0.125
- The plant-weighted shares of the fortieth result, which this plan does not use.
- No interval from resampling plants, and no other measure of how much the differences move between plants, was computed for any cell.

## Check (not a prediction)

- **C0.** The file has 14,807 rows and md5 1681df9fdee9878ca2c359d1239c6467, and its ten generator-month cells listed above reproduce exactly. If C0 fails, B1 to B5 are reported as not scored.

## Predictions

With the 95% interval from resampling whole plants:

- **B1.** 2016-2025, solar: 1 month after the last listing minus first listings. The interval is above 0.
- **B2.** 2016-2025, batteries: 1 month after the last listing minus first listings. The interval is above 0.
- **B3.** 2016-2025, wind: first listings minus 1 month after the last listing. The interval includes 0.
- **B4.** 2016-2025, gas: first listings minus 1 month after the last listing. The interval includes 0.
- **B5.** January 2022 to August 2026, solar: 1 month after the last listing minus 2-3 months after. The interval is above 0.

"Above 0" means the interval's lower end is above 0; "includes 0" means its lower end is 0 or below and its upper end 0 or above. Every compared cell needs at least 30 plants; a prediction with fewer is reported as not scored. Results are reported as "N of the scored predictions held".

## Why these bars, and how each could fail

Before writing this plan we made only a rough guess, from the counts above, of how wide the intervals would be: a binomial spread, widened for plants with several rows in a cell. By that guess the solar, battery and recent solar gaps (B1, B2, B5) are several times their spread, and the wind and gas gaps (B3, B4) about one and a half to two times theirs, at fewer plants with more rows each (gas: 576 generator-months at 108 plants). So we expect the solar and battery patterns to survive clustering and the wind and gas reversals not to. B3 and B4 are near calls by that guess and either could fail: if B3 fails, wind's reversal is wider than plant-to-plant noise, which would back the thirty-ninth result's held-out wind test. B2 could fail if a few battery plants carry the gap.

## Also reported, not scored

The same difference and interval, with the plants in each cell, for those five comparisons and for all technologies together (1 month after the last listing minus first listings), in each of 2016-2019, 2020-2021, 2022-2025 and January to August 2026, pooled 2016-2025, and January 2022 to August 2026.

## Limits

- Resampling plants handles dependence between rows of one plant, not between plants of one developer, region or year.
- A percentile interval from 2,000 resamples; its ends move a little with the seed. A bar decided near the edge of its interval will be reported as such.
- Generator-months. "On time" is the next workbook's status: one listed as operating a month late is not on time, and one that leaves the file is not on time.
- The cohort file was made by this repository's own code; C0 is a reproducibility check, not an independent one.
- This is an association, not a cause.
