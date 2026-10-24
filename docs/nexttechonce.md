# Counting each generator once, solar and batteries still fall, gas rises, and the share inside technologies is a little under 70%

Status: scored against its pre-registration ([`docs/nexttechonce-plan.md`](nexttechonce-plan.md), commit 470e60f, fixed before job nexttechonce-v1 counted any generator once): 3 of 4 predictions held, and the reproduction check C0 held. O3 failed: gas's share rose by 0.057, just outside the band of 0.05. Every number below is checked against the job's raw output by the doc test [`test_nexttechonce_doc.py`](../test_nexttechonce_doc.py).

Made by MV2 of Munim, Inc. with AI agents working in his name. Text and data: CC BY 4.0. Job nexttechonce-v1 (24 October 2026) ran [`tools/annual-flows-candidate/nexttechonce.py`](../tools/annual-flows-candidate/nexttechonce.py) 0.1.0 (Apache-2.0) unchanged, after its 10 unit tests passed ([`nexttechonce-v1-unittests.txt`](nexttechonce-v1-unittests.txt)). Raw output: [`docs/nexttechonce-v1-output.md`](nexttechonce-v1-output.md) and the job's log [`docs/nexttechonce-v1-stdout.txt`](nexttechonce-v1-stdout.txt). Data: [`data/nexttechonce_first.csv`](../data/nexttechonce_first.csv) (each generator's first next-month cohort month in each period, 4,711 rows).

## What was measured

[`docs/nexttech.md`](nexttech.md) split EIA-860M's next-month share by technology and counted generator-months, so a generator planned for the next month again and again counted once in each of those months. This note keeps only each generator's first cohort month in each period (2016-2019 and 2022-2025) and asks whether it was listed as operating in that month. The cohort file is the one `docs/nexttech.md` published, [`data/nexttech_cohort.csv`](../data/nexttech_cohort.csv).

## Order of events

The plan was committed at 00:22:03 UTC on 24 October 2026 (commit 470e60f). The job's first poll, at 00:19:12 UTC, found no plan (404). Its next poll, at 00:29:12 UTC, was served the plan, and only then did it download the cohort file (950,816 bytes, md5 1681df9fdee9878ca2c359d1239c6467, 14,807 rows) and count anything.

## The check and the bars

| bar | outcome | value |
|---|---|---|
| C0 (check). 14,807 rows that reproduce 1,980 of 4,223 and 2,110 of 6,047 generator-months | held | 14,807 rows; 1,980 of 4,223 and 2,110 of 6,047 |
| O1. Solar's share, each generator once, is lower in 2022-2025 | held | 0.476 (642 of 1,348) to 0.360 (557 of 1,549) |
| O2. Batteries' share, each generator once, is lower in 2022-2025 | held | 0.362 (25 of 69) to 0.282 (154 of 547) |
| O3. Gas's share, each generator once, moves by less than 0.05 | failed | 0.443 (144 of 325) to 0.500 (110 of 220) |
| O4. The all-technology share falls, and at least half the fall is inside technologies | held | 0.070 of 0.100 |

## The shares, each generator once

| technology | 2016-2019 | 2022-2025 | listings per generator, 2016-2019 | listings per generator, 2022-2025 |
|---|---|---|---|---|
| solar | 0.476 (642 of 1,348) | 0.360 (557 of 1,549) | 1.82 | 2.36 |
| batteries | 0.362 (25 of 69) | 0.282 (154 of 547) | 2.00 | 2.77 |
| gas | 0.443 (144 of 325) | 0.500 (110 of 220) | 2.29 | 1.91 |
| wind | 0.477 (116 of 243) | 0.496 (64 of 129) | 1.90 | 2.08 |
| other | 0.407 (79 of 194) | 0.345 (30 of 87) | 2.19 | 2.18 |
| all | 0.462 (1,006 of 2,179) | 0.361 (915 of 2,532) | 1.94 | 2.39 |

"Listings per generator" is a group's generator-months in the period divided by its generators: how many monthly reports, on average, named a generator as planned for the next month.

## O4: a little under 70% of the fall is inside technologies

Counting each generator once, the all-technology share fell from 0.462 to 0.361, by 0.100. Weighting each technology's 2022-2025 share by its part of the 2016-2019 generators gives 0.392, so with the old mix the share would have fallen by 0.070. That is a little under 70% of the fall; counted in generator-months, `docs/nexttech.md` found 79%. The mix moved the same way as before: batteries were 3.2% of the 2016-2019 generators and 21.6% of the 2022-2025 ones, gas went from 14.9% to 8.7%, wind from 11.2% to 5.1%, other technologies from 8.9% to 3.4%, and solar from 61.9% to 61.2%.

## Repeat listings grew, and they made the generator-month fall look larger

Counted in generator-months the share fell by 0.120; counted once per generator it fell by 0.100. The difference comes from repeat listings: in 2022-2025 a generator was named as planned for the next month in 2.39 monthly reports on average, against 1.94 in 2016-2019. Batteries went from 2.00 to 2.77 and solar from 1.82 to 2.36. A generator that misses its month and is planned for the next month again counts as a miss in each month under the old count, so more repeat listings pull the generator-month share down further. Even so, solar's and batteries' first planned months were met less often in 2022-2025 than in 2016-2019.

Repeat listings also changed in how often they were met. Within each period, the listings after a generator's first one in that period were on time 0.477 (974 of 2,044) in 2016-2019 and 0.340 (1,195 of 3,515) in 2022-2025, against 0.462 and 0.361 for first listings. So in 2016-2019 a generator planned for the next month again was a little more likely to make it than one planned for the first time, and in 2022-2025 a little less likely. Both gaps are small and were not tested in advance.

*Corrected on 24 October 2026: the rise in the number of repeat listings explains almost none of the gap between the two falls; their steeper fall does. See the update at the end of this note.*

## O3: gas rose, and plant 60264 still decides the verdict

Counting each generator once, gas's share rose from 0.443 to 0.500, by 0.057. Plant 60264's 12 combustion turbines are now 12 of the 325 gas generators of 2016-2019, and none was listed as operating in its first planned month (June 2016 for CLGT1 to CLGT6, January 2017 for BCGT1 to BCGT6). Without the plant, gas's 2016-2019 share is 0.460 (144 of 313), and the rise is 0.040, inside the band. The plan did not exclude any plant, so O3 failed as scored. What it shows is that the gas rise is small and rests on one plant, not that gas got much more punctual; gas's two highest years by generator-month are 2025 and 2026, on small cohorts (`docs/nexttech.md`).

## What was already known, and what is new

`docs/nexttech.md` and its plan list what was known: EIA's Today in Energy of 8 May 2024 and of 10 November 2025, which measure capacity whose reported online date moved later, not generators listed as operating in their planned month. We found no published count of how often EIA-860M names the same generator as planned for the next month, and no next-month share counted once per generator (web search, 24 October 2026). What is new here: the technology split survives counting each generator once (solar and batteries fall, most of the fall is inside technologies), and repeat listings rose from 1.94 to 2.39 per generator, which is part of why the generator-month series fell as far as it did.

## Limits

- The first cohort month in a period is a choice. A generator first planned for the next month before 2022 and again in 2022-2025 counts in 2022-2025 with its first month there, which may itself be a repeat; the 2022-2025 share is not a share of brand-new plans.
- Counts weigh a 1 MW generator like a 1,000 MW one. Technology is taken from the month before.
- Generators at one plant are not independent, so no significance test is given. The split is an association, not a cause.
- The cohort file was made by this repository's own code; C0 is a reproducibility check, not an independent one.
- No person has checked these counts by hand against the workbooks.

## Sources

- EIA, Preliminary Monthly Electric Generator Inventory (EIA-860M): https://www.eia.gov/electricity/data/eia860m/
- EIA, Today in Energy, 10 November 2025, "Fewer U.S. solar projects are reporting delays in their expected online date": https://www.eia.gov/todayinenergy/detail.php?id=66604

## Update, 24 October 2026: more repeat listings explain almost none of the extra fall

Two sentences above give the wrong cause. The section on repeat listings says "more repeat listings pull the generator-month share down further", and the section on what is new says the rise in repeat listings "is part of why the generator-month series fell as far as it did". Splitting each period's generator-months into first listings and repeat listings, with the counts above, shows that the rise in how many listings were repeats did almost none of it. What made the generator-month fall larger is that repeat listings were met much less often than before. Every count and share above is unchanged; the doc test [`test_nexttechonce_update_doc.py`](../test_nexttechonce_update_doc.py) recomputes the numbers below from [`data/nexttech_cohort.csv`](../data/nexttech_cohort.csv).

- Repeat listings were 48.4% of the generator-months of 2016-2019 (2,044 of 4,223) and 58.1% of those of 2022-2025 (3,515 of 6,047).
- With 2016-2019's mix of first and repeat listings, 2022-2025's generator-month share would be 0.351 instead of 0.349. The change in mix accounts for 0.002 of the 0.120 fall, under 2%; about 98% is the fall inside each kind of listing.
- Weighted the other way, with 2022-2025's mix, 2016-2019's share would have been 0.470 instead of 0.469: slightly higher, because in 2016-2019 repeat listings were met slightly more often than first ones.
- The share of repeat listings met fell by 0.137 (0.477 to 0.340), against 0.100 for first listings (0.462 to 0.361). That steeper fall is what makes the generator-month fall larger than the fall counted once per generator.

More listings per generator pull the generator-month share down only when repeat listings are met less often than first ones. That was true in 2022-2025 but not in 2016-2019, so the growth in repeat listings matters little for the change between the two periods. This is arithmetic on the published counts, not a pre-registered test, and the limits above apply to it.
