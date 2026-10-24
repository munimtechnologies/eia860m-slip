# Pre-registration: after a generator has missed its next-month date several times, how often does it make the next one?

Status: pre-registered, not yet scored.

Fixed on 24 October 2026, before job nextcount-v1 counts any earlier listing. The job's first step polls this file's address on GitHub and computes nothing until it is served, so the commit time of this file is the record of when the bars below were fixed. They will not be moved after the job runs.

Made by MV2 of Munim, Inc. with AI agents working in his name. Text: CC BY 4.0. Code: [`tools/annual-flows-candidate/nextcount.py`](../tools/annual-flows-candidate/nextcount.py) 0.1.0 (Apache-2.0), with its tests. It uses only Python's standard library.

## Why

Each month EIA-860M lists generators whose developers plan to start them the next month. Of those, the share that the next month's workbook lists as operating fell from 0.469 in 2016-2019 to 0.349 in 2022-2025 ([`docs/nextmonth-share.md`](nextmonth-share.md)). Many generators are in that next-month group more than once: they were planned for next month, did not start, and were planned for a later next month again. EIA's Today in Energy of November 2025 ("Fewer U.S. solar projects are reporting delays in their expected online date") says solar delays are usually short, a month or two, and that much of the delayed capacity is at projects in late construction or testing. That suggests a generator that just missed is close to done. The other reading is that a generator that keeps missing has a problem that does not go away.

So: for a generator in the next-month group, does the chance that it is operating that month depend on how many times it was in the group before? Anyone who reads the monthly file for what comes online next month (grid operators, analysts, trackers) can use the answer to weight a listing that has already missed.

## The rule

The job reads [`data/nexttech_cohort.csv`](../data/nexttech_cohort.csv) at commit ea63c15, the cohort file of job nexttech-v1 (14,807 rows, one per generator and cohort month, August 2015 to September 2026). For each row it counts the generator's earlier cohort months in the file (from August 2015): its earlier next-month listings. Bins: 0, 1, 2, and 3 or more. A row is on time if that month's workbook lists the generator as operating. The share of a bin is its on-time rows over its rows, in generator-months, in each period (2016-2019 and 2022-2025, by cohort month, as before). Generators listed before August 2015 have their earlier listings missed; that touches the 2016-2019 bins most and the 2022-2025 bins hardly at all.

## What was known when this plan was fixed

- The dated update of 24 October 2026 in [`docs/nexttechonce.md`](nexttechonce.md) splits each period into a generator's first listing in that period and later ones. In 2016-2019 first listings were on time 0.462 (1,006 of 2,179) and later ones 0.477 (974 of 2,044); in 2022-2025, 0.361 (915 of 2,532) and 0.340 (1,195 of 3,515). Those splits start counting at each period's start, not at August 2015, and do not separate 1, 2 or 3 or more earlier listings.
- The practice run of the October 2026 scoring job ([`docs/monthrun-practice-v1-output.md`](monthrun-practice-v1-output.md)) split September 2026's group of 170 the same way from July 2015: 26 of 61 first listings were on time (0.4262) and 31 of 109 repeat listings (0.2844). One month, not a period.
- [`docs/nexttech.md`](nexttech.md): one gas plant (60264) has 102 gas generator-months of 2016-2019, its 12 turbines planned for the next month again and again, mostly not on time. They will sit mainly in 2016-2019's bin of 3 or more.
- EIA's November 2025 article above. No count by number of earlier listings has been computed for either period.

## Check (not a prediction)

- **C0.** The file has 14,807 rows, and its generator-month counts reproduce `docs/nexttech.md`: 1,980 of 4,223 in 2016-2019 and 2,110 of 6,047 in 2022-2025. If C0 fails, K1 to K3 are reported as not scored.

## Predictions

- **K1.** In 2022-2025, the share of rows with no earlier listing is higher than the share of rows with 3 or more.
- **K2.** In 2022-2025, the share does not rise from one bin to the next: 0 at least 1, 1 at least 2, 2 at least 3 or more.
- **K3.** The gap K1 measures (share with no earlier listing minus share with 3 or more) is smaller in 2016-2019 than in 2022-2025.

Every bin a prediction compares needs at least 30 rows; a prediction with a smaller bin is reported as not scored. Results are reported as "N of the scored predictions held".

## How each could fail

K1 fails if, in 2022-2025, generators that have already missed three or more times are on time at least as often as new listings: EIA's "short delays near the finish" reading would then win. K2 fails if any later bin has a higher share than the one before it, for example if a generator that missed once is more often on time than a new listing. K3 fails if the gap was at least as wide ten years ago, so that the rise of repeat listings is not a new pattern (plant 60264 could cause that by itself).

## Also reported, not scored

Finer bins (0, 1, 2, 3, 4, 5-9, 10 or more); repeat rows by months since the generator's last listing (1, 2-3, 4-12, more than 12); the bins without plant 60264; the bins by technology group. Each with generator-months, on-time rows, distinct generators and distinct plants.

## Limits

- Generator-months, not generators: a generator listed ten times is in ten rows, one per bin it passes through. Generators at one plant are not independent (no significance test). This is an association and not a cause.
- "On time" is the next workbook's status. A generator listed as operating a month late is not on time here, and a generator that leaves the file is not on time.
- Earlier listings before August 2015 are not seen (above).
- The cohort file was made by this repository's own code; C0 is a reproducibility check, not an independent one.
