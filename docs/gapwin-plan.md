# Pre-registration: in 2020-2021, is a one-month slip a good sign within solar and batteries, and a bad one within gas and wind?

Status: pre-registered, not yet scored.

Fixed in October 2026, before job gapwin-v1 counts any 2020-2021 row by first listing or months since the last listing. The job's first step polls this file's address on GitHub and computes nothing until it is served, so the commit time of this file is the record of when the bars below were fixed. They will not be moved after the job runs.

Made by MV2 of Munim, Inc. with AI agents working in his name. Text: CC BY 4.0. Code: [`tools/annual-flows-candidate/gapwin.py`](../tools/annual-flows-candidate/gapwin.py) 0.1.0 (Apache-2.0), with its tests. It uses the cells of [`gaptech.py`](../tools/annual-flows-candidate/gaptech.py) 0.1.0 and the counting rules of [`nextcount.py`](../tools/annual-flows-candidate/nextcount.py) 0.1.0 unchanged, and only Python's standard library.

## Why

The thirty-eighth result ([`docs/nextgaptech.md`](nextgaptech.md)) scored four bars, and all held: in 2022-2025 and in January to August 2026, a solar or battery generator planned for the next month again right after a one-month slip was on time more often than a new listing, and a solar one more often than one back after a slip of 2-3 months. Its tables, reported but not scored, also showed gas and wind going the other way in both 2016-2019 and 2022-2025. A pattern found in data needs a test on data it was not found in. The next-month groups of January 2020 to December 2021 (2,826 generator-months) lie between the periods that every earlier result compared, and none of those results split them by first listing, earlier listings or months since the last listing. This plan does.

## The rule

The job reads [`data/nexttech_cohort.csv`](../data/nexttech_cohort.csv) at commit ea63c15 and annotates every row as `nextcount.py` does, with each generator's history counted from August 2015. Each row goes in one cell: a first listing (no earlier next-month listing since August 2015) or a repeat listing by the months since the generator's last one (1, 2-3, 4-12, more than 12). A row is on time if that month's workbook lists the generator as operating. Shares are in generator-months. The period is January 2020 to December 2021. Technology groups are the cohort file's `group` column (solar, batteries, gas, wind, other).

## What was known when this plan was fixed

- For 2020-2021, only whole groups by technology and year, from the thirty-fourth result's table by year ([`docs/nexttech.md`](nexttech.md) for solar, batteries and gas; its raw output [`docs/nexttech-v1-output.md`](nexttech-v1-output.md) for wind), and the monthly share of all technologies together ([`docs/nextmonth-share.md`](nextmonth-share.md)):
  - Solar: 0.473 (366 of 774) in 2020, 0.387 (320 of 826) in 2021.
  - Batteries: 0.348 (31 of 89) in 2020, 0.282 (72 of 255) in 2021.
  - Gas: 0.426 (46 of 108) in 2020, 0.390 (104 of 267) in 2021.
  - Wind: 0.354 (81 of 229) in 2020, 0.431 (62 of 144) in 2021.
- The cells by technology and months since the last listing for 2016-2019, 2022-2025 and January to August 2026 ([`docs/nextgaptech.md`](nextgaptech.md)). There, a gas generator right after a one-month slip was on time less often than a new gas listing by 0.092 (2016-2019) and 0.190 (2022-2025), and a wind one by 0.014 and 0.071; solar's one-month cell was above its 2-3 month cell by 0.030 in 2016-2019 and 0.131 in 2022-2025.
- Nothing else about 2020-2021 was counted for this plan.

## Check (not a prediction)

- **C0.** The file has 14,807 rows, and its 2020-2021 generator-months reproduce solar 686 of 1,600, batteries 103 of 344, gas 150 of 375 and wind 143 of 373 (the 2020 and 2021 counts above, added). If C0 fails, W1 to W5 are reported as not scored.

## Predictions

- **W1.** 2020-2021, solar: repeat listings 1 month after the last one are on time more often than first listings.
- **W2.** 2020-2021, solar: repeat listings 1 month after the last one are on time more often than those 2-3 months after.
- **W3.** 2020-2021, batteries: repeat listings 1 month after the last one are on time more often than first listings.
- **W4.** 2020-2021, gas: repeat listings 1 month after the last one are on time less often than first listings.
- **W5.** 2020-2021, wind: repeat listings 1 month after the last one are on time less often than first listings.

Every cell a prediction compares needs at least 30 rows; a prediction with a smaller cell is reported as not scored. Results are reported as "N of the scored predictions held".

## How each could fail

W4 and W5 are the riskiest: the gas and wind pattern was found in tables reported, not scored, at few plants, and wind's margin in 2016-2019 was only 0.014. W2 could fail because in 2016-2019 a 2-3 month slip cost solar little (0.030), and 2020-2021 may look more like 2016-2019 than 2022-2025. W3 could be not scored if batteries' one-month cell has fewer than 30 rows: batteries had only 344 generator-months in the two years. If W1 to W3 hold and W4 or W5 fails, the solar and battery pattern carries over but the gas and wind reversal does not.

## Also reported, not scored

Every cell for each technology group and for all technologies together, with generator-months, on-time rows, distinct generators and distinct plants.

## Limits

- Generators at one plant are not independent, so no significance test is made. This is an association, not a cause.
- Generator-months, not generators. "On time" is the next workbook's status: one listed as operating a month late is not on time, and one that leaves the file is not on time.
- 2020-2021 includes the first months of the COVID-19 pandemic, which may have delayed projects in ways later years do not share.
- The cohort file was made by this repository's own code; C0 is a reproducibility check, not an independent one.
