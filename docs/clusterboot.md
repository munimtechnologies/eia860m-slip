# Resampling whole plants: the solar and battery gaps hold, the wind and gas reversals do not stand out from plant-to-plant noise

Status: scored against its pre-registration ([`docs/clusterboot-plan.md`](clusterboot-plan.md), commit 9d72b7d, fixed before job clusterboot-v1 resampled any plant): 5 of 5 predictions held, and the reproduction check C0 held. Every count and point difference below is recomputed from the cohort file by the doc test [`test_clusterboot_doc.py`](../test_clusterboot_doc.py), which also redraws the 2,000 resamples of each of the five bars with the same seed and checks the job's raw output against them.

Made by MV2 of Munim, Inc. with AI agents working in his name. Text: CC BY 4.0. Job clusterboot-v1 (25 October 2026) ran [`tools/annual-flows-candidate/clusterboot.py`](../tools/annual-flows-candidate/clusterboot.py) 0.1.0 (Apache-2.0) unchanged, after its 12 unit tests passed ([`clusterboot-v1-unittests.txt`](clusterboot-v1-unittests.txt)). Raw output: [`docs/clusterboot-v1-output.md`](clusterboot-v1-output.md) and the job's log [`docs/clusterboot-v1-stdout.txt`](clusterboot-v1-stdout.txt).

## What was tested

Every note in this series counts generator-months, and generators at one plant are not independent, so none of them made a significance test. The fortieth result ([`docs/plantw.md`](plantw.md)) tried weighting each plant once and found that this weighting lifts every repeat-listing cell by construction. This test keeps the share of generator-months on time and treats each plant as a cluster. For each bar it takes the plants with rows in either compared cell, draws 2,000 resamples of them with replacement (seed 20261025), recomputes the difference of the two cells' shares from all rows of the drawn plants, and reads the 95% interval from the 51st to the 1,950th sorted difference. Five bars were fixed in advance: four on 2016-2025 pooled and one on January 2022 to August 2026.

"On time" means that month's workbook lists the generator as operating. A plant is EIA's plant ID.

## Order of events

The plan was committed at 07:02:13 UTC on 25 October 2026 (commit 9d72b7d). The job's first poll of the plan's address, at 07:27:41 UTC, was served the plan. Only then did it download the cohort file [`data/nexttech_cohort.csv`](../data/nexttech_cohort.csv) at commit ea63c15 (950,816 bytes, md5 1681df9fdee9878ca2c359d1239c6467, 14,807 rows) and resample anything.

## The check and the bars

| bar | outcome | difference, 95% interval with whole plants resampled, and the two cells |
|---|---|---|
| C0 (check). The file's rows and md5 and the ten generator-month cells already published | held | 14,807 rows, md5 1681df9fdee9878ca2c359d1239c6467; 10 of 10 cells reproduced |
| B1. Solar, 2016-2025: 1 month after the last listing minus first listings; the interval is above 0 | held | +0.0498 (+0.0200 to +0.0795); 1 month after the last listing 1,230 of 2,657 at 1,381 plants; first listings 1,474 of 3,568 at 3,316 plants |
| B2. Batteries, 2016-2025: 1 month after the last listing minus first listings; the interval is above 0 | held | +0.0824 (+0.0275 to +0.1405); 1 month after the last listing 297 of 816 at 371 plants; first listings 205 of 728 at 680 plants |
| B3. Wind, 2016-2025: first listings minus 1 month after the last listing; the interval includes 0 | held | +0.0661 (-0.0340 to +0.1530); first listings 237 of 497 at 460 plants; 1 month after the last listing 191 of 465 at 198 plants |
| B4. Gas, 2016-2025: first listings minus 1 month after the last listing; the interval includes 0 | held | +0.0965 (-0.0545 to +0.2165); first listings 312 of 687 at 246 plants; 1 month after the last listing 206 of 576 at 108 plants |
| B5. Solar, January 2022 to August 2026: 1 month after the last listing minus 2-3 months after; the interval is above 0 | held | +0.1251 (+0.0798 to +0.1686); 1 month after the last listing 639 of 1,636 at 791 plants; 2-3 months after 171 of 644 at 443 plants |

Every compared cell has at least 30 plants, so all five were scored. No bar was decided near the edge of its interval: the end closest to 0 is B1's lower end (+0.0200), and of the two bars expected to include 0, B3's lower end (-0.0340).

## Every period (reported, not scored)

The job also reported the same differences in each of 2016-2019, 2020-2021, 2022-2025 and January to August 2026. Read with care: these are 24 intervals that were not fixed as bars, and at 95% some will exclude 0 by chance.

- **Solar, 1 month after minus first listings:** the interval is above 0 in 2016-2019 and 2022-2025 (narrowly: +0.0048 to +0.0795) and includes 0 in 2020-2021 and January to August 2026.
- **Batteries, the same:** above 0 in 2022-2025 and January to August 2026, and includes 0 in 2016-2019 and 2020-2021, when the one-month cell had 33 and 64 plants.
- **Wind and gas, first listings minus 1 month after:** the interval includes 0 in every period. In 2020-2021, the held-out period of the thirty-ninth result, wind's is +0.1118 (-0.0530 to +0.2323).
- **Solar, 1 month after minus 2-3 months after:** above 0 only in 2022-2025 (+0.0797 to +0.1783) among the four periods; in January to August 2026 its lower end is -0.0034.
- **All technologies together, 1 month after minus first listings:** the interval includes 0 in every period, pooled 2016-2025 (+0.0239, -0.0045 to +0.0517) and January 2022 to August 2026.

## What this changes in the series

- The solar and battery reading stands, now with plant-clustered intervals: pooled over 2016-2025, a generator planned for the next month again right after a one-month slip was on time about 0.05 more often than a first listing in solar and about 0.08 more often in batteries, and resampling whole plants keeps both gaps above 0.
- The cost of a 2-3 month slip for solar since 2022 stands too (B5), and the periods agree with the thirty-ninth result that it shows only from 2022 on.
- The wind and gas reversals are not shown. Their generator-month gaps point the same way as before, but they are within what plant-to-plant variation gives, pooled and in every period. That includes the thirty-ninth result's held-out wind bar (W5 held in generator-months, 0.350 against 0.462): its generator-month numbers stand, but "a bad sign for wind" should be read as not shown.
- For all technologies together, the one-month advantage over first listings is within plant noise in every period. The thirty-seventh result's 2026 comparison (0.347 against 0.304) is +0.0421 (-0.0335 to +0.1201) here. Its other bars are not retested here.

## What a reader of the monthly file can take from it

For a planned solar or battery generator in EIA-860M, being planned for the next month again right after a one-month slip has been a mildly good sign compared with a first listing, and that holds when the rows of each plant are kept together. For a solar generator back after a slip of 2-3 months it has been a bad sign since 2022. For wind and gas, this file does not show which way a one-month slip points.

## Limits

- Resampling plants handles dependence between rows of one plant, not between plants of one developer, region or year.
- A percentile interval from 2,000 resamples; its ends move a little with the seed.
- Only C0 and the five bars were fixed in advance. The period intervals were reported, not scored, and the reading of them above was written after the job ran.
- Generator-months. "On time" is the next workbook's status: one listed as operating a month late is not on time, and one that leaves the file is not on time.
- The cohort file was made by this repository's own code; C0 is a reproducibility check, not an independent one.
- This is an association, not a cause.

## Prior art

Resampling whole clusters (the cluster bootstrap) is a standard method. We found no EIA-860M analysis that puts plant-clustered intervals on how often generators planned for the next month are listed as operating in it. If you know of earlier work, please tell us.
