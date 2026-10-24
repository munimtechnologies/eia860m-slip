# Pre-registration: in October to December 2026, months EIA has not yet published, is a generator planned for the next month right after a one-month slip on time more often than a new listing and than one back after a longer slip?

Status: pre-registered, not yet scored.

Fixed in October 2026, before EIA publishes its October 2026 EIA-860M workbook (EIA's page says "Next Release Date: November 24, 2026"), so none of the data this plan scores existed when it was fixed. The commit time of this file is the record of when the bars below were fixed. They will not be moved.

Made by MV2 of Munim, Inc. with AI agents working in his name. Text: CC BY 4.0. Code: [`tools/annual-flows-candidate/q4held.py`](../tools/annual-flows-candidate/q4held.py) 0.1.0 (Apache-2.0), with its tests. It uses the counting rules of [`nextcount.py`](../tools/annual-flows-candidate/nextcount.py) 0.1.0 unchanged and only Python's standard library.

## Why this one is different

The thirty-sixth and thirty-seventh results ([`docs/nextcount.md`](nextcount.md), [`docs/nextheld.md`](nextheld.md)) counted months whose workbooks were already published when their plans were fixed. The thirty-seventh was a held-out test, but its data existed. This plan scores the next-month groups of October, November and December 2026, whose workbooks do not exist yet. It is the series' first prospective test of the pattern.

## The rule

- Base: [`data/nexttech_cohort.csv`](../data/nexttech_cohort.csv) at commit ea63c15 (950,816 bytes, md5 1681df9fdee9878ca2c359d1239c6467, 14,807 rows; next-month groups from August 2015 to September 2026).
- Each scored month's group is the `monthrun_cohort.csv` that [`monthrun.py`](../tools/annual-flows-candidate/monthrun.py) 0.1.0 writes when run with `--target` for that month (the job that scores [`docs/oct2026-plan.md`](oct2026-plan.md) writes October's). The scored months are appended in month order after the cohort's rows up to September 2026.
- `q4held.py` counts each row's earlier next-month listings and the months since the last one (`nextcount.annotate`) and scores the bars below. A row is on time if that month's workbook lists the generator as operating. Shares are in generator-months.
- Scored period: October, November and December 2026 pooled. December's status comes from EIA's December 2026 workbook, expected in late January 2027. Tables for October and November alone are reported as they arrive, not scored.

## What was known when this plan was fixed

- 2022-2025: first listings 0.362 (866 of 2,393), repeat listings 1 month after the last one 0.390 (878 of 2,254), 2-3 months after 0.260 (231 of 890).
- January to August 2026 (thirty-seventh result): 0.304 (144 of 473), 0.347 (166 of 479) and 0.249 (43 of 173); 5 or more earlier listings 0.163 (15 of 92).
- September 2026, from the practice job q4held-practice-v1 (24 October 2026), which replayed September with monthrun.py's own output; its 170 appended rows equal the cohort's September rows ([`docs/q4held-practice-v1-output.md`](q4held-practice-v1-output.md)): first listings 0.426 (26 of 61), 1 month after the last listing 0.365 (19 of 52), 2-3 months after 0.214 (9 of 42), 4-12 months after 0.154 (2 of 13), 5 or more earlier listings 0.182 (4 of 22); repeat listings together 0.284 (31 of 109). On September alone Q1 would have held, Q2 failed, and Q3 not been scored (22 rows).
- By technology in September 2026 (first listings, 1 month after, 2-3 months after): solar 0.390 (16 of 41), 0.400 (14 of 35), 0.208 (5 of 24); batteries 0.375 (6 of 16), 0.455 (5 of 11), 0.300 (3 of 10).
- A split by technology and months since the last listing for 2016-2026 is pre-registered separately (the thirty-eighth result's plan) and had not been scored when this plan was fixed.

## Checks (not predictions)

- **C1.** Each scored month's group size and on-time count equal monthrun.py's own numbers for that month (`cohort` and `cohort_operating` in its `monthrun_months.csv`).
- **C2.** For every scored row, monthrun.py's `listing` column says "first" exactly when the row has no earlier listing in the cohort and the months appended before it. These are two separate counts of the same thing: monthrun's replay of the workbooks and the cohort file.

If C1 or C2 fails, no prediction is scored.

## Predictions (October to December 2026 pooled)

- **Q1.** Repeat listings 1 month after the last one are on time more often than those 2-3 months after.
- **Q2.** Repeat listings 1 month after the last one are on time more often than first listings.
- **Q3.** Rows with 5 or more earlier listings are on time less often than first listings.

Every cell a prediction compares needs at least 30 rows; a prediction with a smaller cell is reported as not scored. Results are reported as "N of the scored predictions held".

## How each could fail

Q2 is the riskiest: its margin was 0.028 in 2022-2025 and 0.042 in January to August 2026, and in September 2026 first listings (0.426) beat repeat listings 1 month after the last one (0.365). Q3's cell may have fewer than 30 rows: it had 92 in eight months of 2026 and 22 in September. Q1 held in every period counted so far, so a failure there would be the clearest sign that the pattern has changed.

## Also reported, not scored

Each month's cells and the pooled cells, including 4-12 and more than 12 months since the last listing, and the first, 1-month and 2-3-month cells for solar, batteries, gas, wind and other technologies.

## Limits

- Three months. Generators at one plant are not independent, so no significance test is made. This is an association, not a cause.
- Generator-months, not generators. "On time" is the next workbook's status: one listed as operating a month late is not on time, and one that leaves the file is not on time.
- Each month is counted from its workbook as first published, by this repository's own code; C1 and C2 are reproducibility checks, not independent ones.
