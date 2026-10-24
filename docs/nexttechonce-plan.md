# Pre-registration: does the technology split of EIA-860M's next-month share hold when each generator counts once?

Status: pre-registered, not yet scored.

Fixed on 24 October 2026, before job nexttechonce-v1 counts any generator once. The job's first step polls this file's address on GitHub and computes nothing until it is served, so the commit time of this file is the record of when the bars below were fixed. They will not be moved after the job runs.

Made by MV2 of Munim, Inc. with AI agents working in his name. Text: CC BY 4.0. Code: [`tools/annual-flows-candidate/nexttechonce.py`](../tools/annual-flows-candidate/nexttechonce.py) 0.1.0 (Apache-2.0), with its tests. It uses only Python's standard library.

## Why

[`docs/nexttech.md`](nexttech.md) split the next-month share by technology and counted generator-months: a generator planned for the next month in many months counted once in each. It found that one gas plant (60264) has 102 of the 743 gas generator-months of 2016-2019, and that without it gas's share is flat. Any group can be moved the same way by a few generators that slip month after month. This plan asks whether that note's answers hold when each generator counts once in each period.

## The rule

The job reads [`data/nexttech_cohort.csv`](../data/nexttech_cohort.csv), the cohort file of job nexttech-v1 (14,807 rows, one per generator and cohort month), from this repository. For each period (2016-2019 and 2022-2025, by cohort month, as before) it keeps each generator's first cohort month in that period, with the technology group and the listing of that month. A generator counts as on time if that month's workbook lists it as operating. The share of a group is its on-time generators over its generators. So a generator that is planned for the next month six times and comes online the seventh counts once, as late.

## What was known when this plan was fixed

- Everything in `docs/nexttech.md`: the generator-month shares by period, technology and year, the gas split by technology, plant 60264's 102 generator-months and gas's share without it (0.456, then 0.455).
- That once-per-generator shares will be higher than generator-month shares wherever generators slip repeatedly, since each late generator then counts once instead of many times. Which period has more repeated slips is not known.
- No once-per-generator count of any group or period has been computed.

## Check (not a prediction)

- **C0.** The file has 14,807 rows, and its generator-month counts reproduce `docs/nexttech.md`: 1,980 of 4,223 in 2016-2019 and 2,110 of 6,047 in 2022-2025. If C0 fails, O1 to O4 are reported as not scored.

## Predictions

- **O1.** Solar: counting each generator once, the share is lower in 2022-2025 than in 2016-2019.
- **O2.** Batteries: the same.
- **O3.** Gas: counting each generator once, the 2022-2025 share is within 0.05 of the 2016-2019 share (no clear change either way).
- **O4.** Counting each generator once, the all-technology share falls from 2016-2019 to 2022-2025, and the within-technology fall (the 2016-2019 share minus the 2022-2025 shares weighted by the 2016-2019 mix of the five groups) is at least half of that fall.

O1 to O3 each need at least 30 generators in each period; a group with fewer is reported as not scored. O4 is not scored if a group with 2016-2019 generators has none in 2022-2025. Results are reported as "N of the scored predictions held".

## How each could fail

O1 or O2 fail if, once repeated slips are counted once, solar's or batteries' share held steady or rose: the fall in `docs/nexttech.md` would then come from generators that slip again and again. O3 fails if gas moves by 0.05 or more either way. O4 fails if there is no fall, or if the change of mix explains more of it than the change inside technologies.

## Also reported, not scored

For each period and group: the plant with the most generator-months, how many it has, and the group's generator-month share without it.

## Limits

- The first cohort month in a period is a choice; another rule (for example, on time in any of its cohort months) could give other shares. A generator with cohort months in both periods counts once in each.
- Technology and outcome come from the cohort file, so its limits carry over: technology from the month before, counts not MW, generators at one plant not independent (no significance test), an association and not a cause.
- The cohort file was made by this repository's own code; C0 is a reproducibility check, not an independent one.
