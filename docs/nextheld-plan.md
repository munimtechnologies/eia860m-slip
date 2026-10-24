# Pre-registration: does the thirty-sixth result's pattern hold in the next-month groups of January to August 2026?

Status: pre-registered, not yet scored.

Fixed on 24 October 2026, before job nextheld-v1 counts any 2026 row by earlier listings. The job's first step polls this file's address on GitHub and computes nothing until it is served, so the commit time of this file is the record of when the bars below were fixed. They will not be moved after the job runs.

Made by MV2 of Munim, Inc. with AI agents working in his name. Text: CC BY 4.0. Code: [`tools/annual-flows-candidate/nextheld.py`](../tools/annual-flows-candidate/nextheld.py) 0.1.0 (Apache-2.0), with its tests. It uses the counting rules of [`nextcount.py`](../tools/annual-flows-candidate/nextcount.py) 0.1.0 unchanged and only Python's standard library.

## Why

[`docs/nextcount.md`](nextcount.md) (thirty-sixth result) counted, for each generator in a month's next-month group, how many times it was in such a group before, and scored three bars on 2016-2019 and 2022-2025. Its clearest patterns came from tables that were reported, not scored: a generator planned for the next month again right after a one-month slip was on time more often than a first listing, and one that came back after a slip of 2-3 months much less often. A pattern found in the data that suggested it needs a test on data it was not found in. The next-month groups of January to August 2026 are in the same cohort file and were not counted by earlier listings in that note.

## The rule

The job reads [`data/nexttech_cohort.csv`](../data/nexttech_cohort.csv) at commit ea63c15, the same file, and annotates every row as `nextcount.py` does: its earlier next-month listings from August 2015 (bins 0, 1, 2, 3 or more) and, for a repeat listing, the months since the generator's last one (1, 2-3, 4-12, more than 12). It then keeps the cohort months January to August 2026. A row is on time if that month's workbook lists the generator as operating. Shares are in generator-months.

September 2026 is left out: the practice run of the October scoring job already published its split into first and repeat listings ([`docs/monthrun-practice-v1-output.md`](monthrun-practice-v1-output.md): 26 of 61 first listings on time, 0.4262, and 31 of 109 repeat listings, 0.2844).

## What was known when this plan was fixed

- The thirty-sixth result. In 2022-2025: no earlier listing 0.362 (866 of 2,393), 3 or more 0.306 (428 of 1,398); repeat listings 1 month after the last one 0.390 (878 of 2,254), 2-3 months after 0.260 (231 of 890). In 2016-2019 the same comparisons were 0.459 against 0.449, and 0.499 against 0.492.
- The month totals in [`data/monthcheck_months_2026-09.csv`](../data/monthcheck_months_2026-09.csv): January to August 2026 have 1,194 generator-months in their next-month groups, 366 of them on time (0.307), month by month as in the check C1 below.
- The rows for 2026 are in [`data/nextcount_rows.csv`](../data/nextcount_rows.csv), published with this plan in the same commit. No count of the 2026 rows by earlier listings or by months since the last one was made before this plan was fixed.

## Check (not a prediction)

- **C1.** For each month from January to August 2026, the cohort file's rows and on-time rows equal that month's `cohort` and `cohort_operating` in `data/monthcheck_months_2026-09.csv` (366 of 1,194 in all). If C1 fails, H1 to H3 are reported as not scored.

## Predictions (January to August 2026)

- **H1.** The share of rows with 3 or more earlier listings is below the share of rows with none.
- **H2.** Repeat listings 1 month after the generator's last listing are on time more often than repeat listings 2-3 months after it.
- **H3.** Repeat listings 1 month after the last listing are on time more often than rows with no earlier listing.

Every cell a prediction compares needs at least 30 rows; a prediction with a smaller cell is reported as not scored. Results are reported as "N of the scored predictions held".

## How each could fail

H1 fails if, in 2026, generators that have already missed three or more times are on time at least as often as new listings. In 2022-2025 the gap was 0.056 and came mostly from gas and wind at a few plants, so a few plants could turn it. H2 fails if a longer slip is no worse a sign than a one-month slip, as in 2016-2019, when the two were 0.007 apart. H3 is the riskiest: in 2022-2025 one-month slips led first listings by only 0.028.

## Also reported, not scored

Each month's rows and on-time rows; the finer bins (0, 1, 2, 3, 4, 5-9, 10 or more); all four bins of months since the last listing; the bins by technology group. Each with generator-months, on-time rows, distinct generators and distinct plants.

## Limits

- Eight months, not four years: cells will be small, and generators at one plant are not independent (no significance test).
- Generator-months, not generators. "On time" is the next workbook's status. This is an association, not a cause.
- The cohort file was made by this repository's own code; C1 is a reproducibility check, not an independent one.
