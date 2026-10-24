# Pre-registration: within solar and within batteries, is a generator planned for the next month right after a one-month slip on time more often?

Status: pre-registered, not yet scored.

Fixed in October 2026, before job gaptech-v2 counts any row by technology and months since the last listing. The job's first step polls this file's address on GitHub and computes nothing until it is served, so the commit time of this file is the record of when the bars below were fixed. They will not be moved after the job runs.

Made by MV2 of Munim, Inc. with AI agents working in his name. Text: CC BY 4.0. Code: [`tools/annual-flows-candidate/gaptech.py`](../tools/annual-flows-candidate/gaptech.py) 0.1.0 (Apache-2.0), with its tests. It uses the counting rules of [`nextcount.py`](../tools/annual-flows-candidate/nextcount.py) 0.1.0 unchanged and only Python's standard library.

## Why

EIA's Today in Energy of November 2025 ("Fewer U.S. solar projects are reporting delays in their expected online date") says solar delays are usually short, a month or two, and that much of the delayed capacity is at projects in late construction or testing. If so, a solar generator planned for the next month again right after a one-month slip should be close to done. The thirty-sixth and thirty-seventh results ([`docs/nextcount.md`](nextcount.md), [`docs/nextheld.md`](nextheld.md)) found that pattern for all technologies together, but did not split the months since the last listing by technology, so they do not test EIA's statement about solar. Solar is the largest group, and batteries went the other way from the rest in both results. This plan splits the same cells by technology.

## The rule

The job reads [`data/nexttech_cohort.csv`](../data/nexttech_cohort.csv) at commit ea63c15 and annotates every row as `nextcount.py` does. Each row goes in one cell: a first listing (no earlier next-month listing since August 2015) or a repeat listing by the months since the generator's last one (1, 2-3, 4-12, more than 12). A row is on time if that month's workbook lists the generator as operating. Shares are in generator-months. Periods: 2016-2019, 2022-2025 and January to August 2026. Technology groups are the cohort file's `group` column (solar, batteries, gas, wind, other).

## What was known when this plan was fixed

- All technologies together, 2022-2025: first listings 0.362 (866 of 2,393), repeat listings 1 month after the last one 0.390 (878 of 2,254), 2-3 months after 0.260 (231 of 890). January to August 2026: 0.304 (144 of 473), 0.347 (166 of 479) and 0.249 (43 of 173).
- By technology, only by the number of earlier listings (none, one, two, 3 or more). Solar, 2022-2025: 0.361 (536 of 1,483), 0.363 (312 of 860), 0.348 (179 of 514), 0.332 (265 of 797). Batteries, 2022-2025: 0.278 (143 of 514), 0.306 (107 of 350), 0.316 (74 of 234), 0.309 (129 of 417). Solar, January to August 2026: 0.290 (82 of 283), 0.277 (48 of 173), 0.317 (33 of 104), 0.248 (37 of 149).
- A row with one earlier listing can be any number of months after it, so these tables hint at the cells below but do not give them. Before this plan was fixed, the only count by technology and months since the last listing was of September 2026, a month no bar uses (practice job q4held-practice-v1, 24 October 2026): solar first listings 0.390 (16 of 41), 1 month after the last listing 0.400 (14 of 35), 2-3 months after 0.208 (5 of 24); batteries 0.375 (6 of 16), 0.455 (5 of 11) and 0.300 (3 of 10).

## Check (not a prediction)

- **C0.** The file has 14,807 rows; its generator-months reproduce 1,980 of 4,223 (2016-2019), 2,110 of 6,047 (2022-2025) and 366 of 1,194 (January to August 2026); and the first listings of 2022-2025 reproduce 536 of 1,483 for solar and 143 of 514 for batteries. If C0 fails, G1 to G4 are reported as not scored.

## Predictions

- **G1.** 2022-2025, solar: repeat listings 1 month after the last one are on time more often than first listings.
- **G2.** 2022-2025, solar: repeat listings 1 month after the last one are on time more often than those 2-3 months after.
- **G3.** January to August 2026, solar: repeat listings 1 month after the last one are on time more often than those 2-3 months after.
- **G4.** 2022-2025, batteries: repeat listings 1 month after the last one are on time more often than first listings.

Every cell a prediction compares needs at least 30 rows; a prediction with a smaller cell is reported as not scored. Results are reported as "N of the scored predictions held".

## How each could fail

G1 is the riskiest: in 2022-2025, solar with one earlier listing was on time 0.363 against 0.361 with none, so a solar generator right after a one-month slip may be no more likely to start than a new listing. If G1 fails while G2 holds, a short solar slip is not a good sign, only a better one than a long slip. G3 could fail because 2026 solar with one earlier listing was below solar with none (0.277 against 0.290), and its 2-3 month cell will be small. G4 could fail if batteries' higher share with earlier listings comes from longer slips rather than one-month ones.

## Also reported, not scored

Every cell for every period and technology group, and for all technologies together, with generator-months, on-time rows, distinct generators and distinct plants.

## Limits

- Generators at one plant are not independent, so no significance test is made. This is an association, not a cause.
- Generator-months, not generators. "On time" is the next workbook's status: one listed as operating a month late is not on time, and one that leaves the file is not on time.
- EIA's article speaks of capacity and of delays reported by developers; this counts generator-months and next-month listings. A failed bar would not show the article wrong, only that its reading does not carry over to this measure.
- The cohort file was made by this repository's own code; C0 is a reproducibility check, not an independent one.
