# In 2020-2021 too, a one-month slip was a good sign for solar and batteries and a bad one for wind

Status: scored against its pre-registration ([`docs/gapwin-plan.md`](gapwin-plan.md), commit 67c562b, fixed before job gapwin-v1 counted any 2020-2021 row by first listing or months since the last listing): 4 of 5 predictions held, and the reproduction check C0 held. W2 failed. Every number below is recomputed from the cohort file by the doc test [`test_gapwin_doc.py`](../test_gapwin_doc.py), which also checks the job's raw output against it.

Made by MV2 of Munim, Inc. with AI agents working in his name. Text: CC BY 4.0. Job gapwin-v1 (25 October 2026) ran [`tools/annual-flows-candidate/gapwin.py`](../tools/annual-flows-candidate/gapwin.py) 0.1.0 (Apache-2.0) unchanged, with [`gaptech.py`](../tools/annual-flows-candidate/gaptech.py) 0.1.0 fetched at commit 85fd467 and [`nextcount.py`](../tools/annual-flows-candidate/nextcount.py) 0.1.0 at commit bdd4b8b, after its 11 unit tests passed ([`gapwin-v1-unittests.txt`](gapwin-v1-unittests.txt)). Raw output: [`docs/gapwin-v1-output.md`](gapwin-v1-output.md) and the job's log [`docs/gapwin-v1-stdout.txt`](gapwin-v1-stdout.txt).

## What was tested

The thirty-eighth result ([`docs/nextgaptech.md`](nextgaptech.md)) found that, in 2022-2025 and in January to August 2026, a solar or battery generator planned for the next month again right after a one-month slip was on time more often than a new listing. Its tables, reported but not scored, showed gas and wind going the other way in 2016-2019 and 2022-2025. A pattern found in data needs a test on data it was not found in. This note scores five bars, fixed in advance, on the next-month groups of January 2020 to December 2021 (2,826 generator-months), which no earlier result split by first listing or months since the last listing.

"On time" means that month's workbook lists the generator as operating. Shares are in generator-months.

## Order of events

The plan was committed at 00:07:44 UTC on 25 October 2026 (commit 67c562b). The job started 16 minutes later, and its first poll of the plan's address, at 00:23:25 UTC, was served the plan. Only then did it download the cohort file [`data/nexttech_cohort.csv`](../data/nexttech_cohort.csv) at commit ea63c15 (950,816 bytes, md5 1681df9fdee9878ca2c359d1239c6467, 14,807 rows) and count anything.

## The check and the bars

| bar | outcome | value |
|---|---|---|
| C0 (check). The file's rows and the 2020-2021 generator-months of the four technologies, as already published | held | 14,807 rows; 2020-2021: solar 686 of 1,600, batteries 103 of 344, gas 150 of 375, wind 143 of 373 |
| W1. Solar: 1 month after the last listing above first listings | held | 0.447 (240 of 537) against 0.414 (326 of 787) |
| W2. Solar: 1 month after the last listing above 2-3 months after | failed | 0.447 (240 of 537) against 0.451 (96 of 213) |
| W3. Batteries: 1 month after the last listing above first listings | held | 0.352 (45 of 128) against 0.252 (37 of 147) |
| W4. Gas: 1 month after the last listing below first listings | held | 0.400 (56 of 140) against 0.405 (68 of 168) |
| W5. Wind: 1 month after the last listing below first listings | held | 0.350 (64 of 183) against 0.462 (66 of 143) |

Every compared cell has at least 30 rows, so all five were scored. The margins, in each bar's direction, were 0.033 (W1), 0.100 (W3), 0.005 (W4) and 0.112 (W5); W2 went the wrong way by 0.004. W4 held only on paper: one more on-time generator-month in gas's one-month cell (57 of 140, 0.407) would have made it fail. The plan named W2's way of failing in advance: in 2016-2019 a 2-3 month slip cost solar little, and 2020-2021 looks like 2016-2019 here.

The compared cells: solar's one-month cell has 311 generators at 299 plants and its 2-3 month cell 162 at 156; batteries' one-month cell has 67 at 64; wind's one-month cell 76 at 67 and its first listings 143 at 138. Gas is concentrated: its one-month cell has 71 generators at 28 plants, its first listings 168 at 62.

## 2020-2021 by technology (W1 to W5 compare five pairs of these cells)

| technology | first listing | 1 month after the last listing | 2-3 months after |
|---|---|---|---|
| all technologies | 0.394 (505 of 1,283) | 0.411 (429 of 1,045) | 0.400 (152 of 380) |
| solar | 0.414 (326 of 787) | 0.447 (240 of 537) | 0.451 (96 of 213) |
| batteries | 0.252 (37 of 147) | 0.352 (45 of 128) | 0.269 (14 of 52) |
| gas | 0.405 (68 of 168) | 0.400 (56 of 140) | 0.396 (21 of 53) |
| wind | 0.462 (66 of 143) | 0.350 (64 of 183) | 0.297 (11 of 37) |

The full table, with the 4-12 and more-than-12-month cells, "other" technologies, distinct generators and plants, is in the raw output.

## All four periods side by side (reported, not scored)

With 2020-2021 counted, the same cells now exist for four periods. The 2016-2019, 2022-2025 and 2026 values are the thirty-eighth result's, recomputed here from the same file.

The one-month cell minus first listings:

| technology | 2016-2019 | 2020-2021 | 2022-2025 | January-August 2026 |
|---|---|---|---|---|
| all technologies | +0.040 | +0.017 | +0.028 | +0.042 |
| solar | +0.107 | +0.033 | +0.043 | +0.036 |
| batteries | +0.179 | +0.100 | +0.071 | +0.122 |
| gas | -0.092 | -0.005 | -0.190 | +0.067 (under 30 rows) |
| wind | -0.014 | -0.112 | -0.071 | +0.178 (under 30 rows) |

The one-month cell minus the 2-3 month cell:

| technology | 2016-2019 | 2020-2021 | 2022-2025 | January-August 2026 |
|---|---|---|---|---|
| all technologies | +0.007 | +0.011 | +0.130 | +0.098 |
| solar | +0.030 | -0.004 | +0.131 | +0.098 |

Three things in these tables were not bars:

- **Solar and batteries point the same way in every period.** Their one-month cell is above their first listings in all four periods.
- **Wind's reversal has now held on data it was not found in; gas's has not, in any useful sense.** Wind's one-month cell is below its first listings in each of the three periods with enough rows; 2020-2021, the held-out period, has the largest gap. Gas's gap was 0.092 and 0.190 in the periods it was found in, and 0.005 in the held-out one.
- **The cost of a 2-3 month slip is new since 2022.** For all technologies together and for solar, a generator back after a slip of 2-3 months was on time about as often as one right after a one-month slip in 2016-2019 and 2020-2021, and much less often in 2022-2025 and 2026.

## What a reader of the monthly file can take from it

In each of the four periods since 2016, a solar or battery generator that EIA-860M lists as planned for the next month right after a one-month slip was listed as operating in that month more often than a new listing of the same technology. For wind it was less often in every period with enough rows. A slip of 2-3 months became a bad sign only from 2022 on. These are rates for groups, not forecasts for any one generator.

## Limits

- Generators at one plant are not independent, so no significance test is made. This is an association, not a cause.
- Generator-months, not generators. "On time" is the next workbook's status: one listed as operating a month late is not on time, and one that leaves the file is not on time.
- 2020-2021 includes the first months of the COVID-19 pandemic, which may have delayed projects in ways later years do not share.
- The cohort file was made by this repository's own code; C0 is a reproducibility check, not an independent one.
- Only C0 and the five bars were fixed in advance. The tables of all four periods and the three points under them were reported, not scored.

## Prior art

We found no published count of EIA-860M's next-month share by technology and the months since a generator's last next-month listing, for 2020-2021 or any other period. EIA's November 2025 Today in Energy article ("Fewer U.S. solar projects are reporting delays in their expected online date") describes how long solar delays are, not how often a delayed generator then starts in its next planned month. If you know of earlier work, please tell us.
