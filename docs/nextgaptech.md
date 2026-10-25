# Within solar and within batteries, a generator planned for the next month right after a one-month slip is on time more often

Status: scored against its pre-registration ([`docs/nextgaptech-plan.md`](nextgaptech-plan.md), commit 85fd467, fixed before job gaptech-v2 counted any row by technology and months since the last listing): 4 of 4 predictions held, and the reproduction check C0 held. Every number below is recomputed from the cohort file by the doc test [`test_nextgaptech_doc.py`](../test_nextgaptech_doc.py), which also checks the job's raw output against it.

Made by MV2 of Munim, Inc. with AI agents working in his name. Text: CC BY 4.0. Job gaptech-v2 (24 October 2026) ran [`tools/annual-flows-candidate/gaptech.py`](../tools/annual-flows-candidate/gaptech.py) 0.1.0 (Apache-2.0) unchanged, with [`nextcount.py`](../tools/annual-flows-candidate/nextcount.py) 0.1.0 fetched at commit bdd4b8b, after its 11 unit tests passed ([`nextgaptech-v2-unittests.txt`](nextgaptech-v2-unittests.txt)). Raw output: [`docs/nextgaptech-v2-output.md`](nextgaptech-v2-output.md) and the job's log [`docs/nextgaptech-v2-stdout.txt`](nextgaptech-v2-stdout.txt).

## What was tested

EIA's Today in Energy of November 2025 ("Fewer U.S. solar projects are reporting delays in their expected online date") says solar delays are usually short, a month or two, and that much of the delayed capacity is at projects in late construction or testing. The thirty-sixth and thirty-seventh results ([`docs/nextcount.md`](nextcount.md), [`docs/nextheld.md`](nextheld.md)) found that, for all technologies together, a generator planned for the next month again right after a one-month slip was on time more often than a first listing, and one back after a slip of 2-3 months less often. They did not split those cells by technology. This note scores four bars, fixed in advance, inside solar and inside batteries.

"On time" means that month's workbook lists the generator as operating. Shares are in generator-months.

## Order of events

The plan was committed at 22:39:37 UTC on 24 October 2026 (commit 85fd467). The job began polling the plan's address at 18:07:29 UTC and was refused at each of its 28 polls up to 22:37:31 UTC. Its next poll, at 22:47:32 UTC, was served the plan, and only then did it download the cohort file [`data/nexttech_cohort.csv`](../data/nexttech_cohort.csv) at commit ea63c15 (950,816 bytes, md5 1681df9fdee9878ca2c359d1239c6467, 14,807 rows) and count anything.

## The check and the bars

| bar | outcome | value |
|---|---|---|
| C0 (check). The file's rows, the three periods' generator-months and the 2022-2025 first listings of solar and batteries as already published | held | 14,807 rows; 1,980 of 4,223, 2,110 of 6,047 and 366 of 1,194; solar 536 of 1,483, batteries 143 of 514 |
| G1. 2022-2025, solar: 1 month after the last listing above first listings | held | 0.404 (547 of 1,354) against 0.361 (536 of 1,483) |
| G2. 2022-2025, solar: 1 month after the last listing above 2-3 months after | held | 0.404 (547 of 1,354) against 0.273 (147 of 539) |
| G3. January to August 2026, solar: 1 month after the last listing above 2-3 months after | held | 0.326 (92 of 282) against 0.229 (24 of 105) |
| G4. 2022-2025, batteries: 1 month after the last listing above first listings | held | 0.349 (220 of 630) against 0.278 (143 of 514) |

Every compared cell has at least 30 rows, so all four were scored. The margins were 0.043 (G1), 0.131 (G2), 0.098 (G3) and 0.071 (G4). G1, the bar the plan called riskiest, held: in 2022-2025 a solar generator with one earlier listing of any age was on time about as often as a new one (0.363 against 0.361), but one listed again right after a one-month slip was not.

The compared cells are spread over many plants: solar's 2022-2025 one-month cell has 682 generators at 662 plants and its 2-3 month cell 386 at 370; in 2026 they have 156 at 145 and 81 at 77; batteries' 2022-2025 one-month cell has 303 at 287.

## By technology (G1 to G4 compare four pairs of these cells; the rest are reported, not scored)

| technology | period | first listing | 1 month after the last listing | 2-3 months after |
|---|---|---|---|---|
| solar | 2016-2019 | 0.471 (612 of 1,298) | 0.578 (443 of 766) | 0.548 (164 of 299) |
| solar | 2022-2025 | 0.361 (536 of 1,483) | 0.404 (547 of 1,354) | 0.273 (147 of 539) |
| solar | January-August 2026 | 0.290 (82 of 283) | 0.326 (92 of 282) | 0.229 (24 of 105) |
| batteries | 2016-2019 | 0.373 (25 of 67) | 0.552 (32 of 58) | 0.444 (4 of 9) |
| batteries | 2022-2025 | 0.278 (143 of 514) | 0.349 (220 of 630) | 0.216 (49 of 227) |
| batteries | January-August 2026 | 0.238 (29 of 122) | 0.360 (54 of 150) | 0.140 (6 of 43) |
| gas | 2016-2019 | 0.445 (143 of 321) | 0.354 (110 of 311) | 0.473 (35 of 74) |
| gas | 2022-2025 | 0.510 (101 of 198) | 0.320 (40 of 125) | 0.464 (26 of 56) |
| gas | January-August 2026 | 0.600 (27 of 45) | 0.667 (6 of 9) | 0.667 (10 of 15) |
| wind | 2016-2019 | 0.475 (112 of 236) | 0.461 (88 of 191) | 0.480 (12 of 25) |
| wind | 2022-2025 | 0.500 (59 of 118) | 0.429 (39 of 91) | 0.175 (7 of 40) |
| wind | January-August 2026 | 0.222 (2 of 9) | 0.400 (8 of 20) | 0.000 (0 of 4) |

Cells under 30 rows are shown but say little. The full table, with every cell, "other" technologies, distinct generators and plants, is in the raw output.

Three things in it were not bars:

- **The bars' pattern also shows in the 2026 cells no bar used.** In January to August 2026, solar's one-month cell was above its first listings by 0.036 and batteries' by 0.122, the same direction as G1 and G4.
- **For solar, the cost of a 2-3 month slip is new.** In 2016-2019, solar's one-month cell was above its 2-3 month cell by only 0.030, against 0.131 in 2022-2025. The same was true of all technologies together in the thirty-sixth result.
- **Gas and wind go the other way.** A gas generator listed again right after a one-month slip was on time less often than a new gas listing, by 0.092 in 2016-2019 and 0.190 in 2022-2025; wind, by 0.014 and 0.071. These cells are at few plants (gas's 2022-2025 one-month cell has 67 generators at 32 plants), and 2016-2019 gas includes the plant whose 12 turbines the thirty-fourth result found planned for the next month again and again. Because this was found in tables reported, not scored, it is not a finding until it is tested on data it was not found in.

## What a reader of the monthly file can take from it

In 2022-2025, a solar generator planned for the next month again right after a one-month slip was listed as operating in that month 40% of the time, a new solar listing 36% of the time, and one back after a slip of 2-3 months 27%. For batteries the three were 35%, 28% and 22%. So for the two technologies that make up most of these next-month groups (85% of the generator-months of 2022-2025), a one-month slip was a mildly good sign and a longer one a bad sign, as EIA's reading of short solar delays suggests. For gas and wind the tables point the other way. These are rates for groups, not forecasts for any one generator.

## Limits

- Generators at one plant are not independent, so no significance test is made. This is an association, not a cause.
- Generator-months, not generators. "On time" is the next workbook's status: one listed as operating a month late is not on time, and one that leaves the file is not on time.
- EIA's article speaks of capacity and of delays reported by developers; this counts generator-months and next-month listings. The bars held on this measure; that does not test the article's own numbers.
- The cohort file was made by this repository's own code; C0 is a reproducibility check, not an independent one.
- Only C0 and the four bars were fixed in advance. Everything else above was reported, not scored.

## Prior art

We found no published count of EIA-860M's next-month share by technology and the months since a generator's last next-month listing. EIA's November 2025 article describes how long solar delays are, not how often a delayed generator then starts in its next planned month. If you know of earlier work, please tell us.
