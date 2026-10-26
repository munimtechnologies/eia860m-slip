# The next-month series in one place: results 34 to 41, every bar, and what still stands

Status: descriptive summary; it tests nothing new. Every bar and outcome below is copied from the scored notes, and the doc test [`test_nextmonth_series_doc.py`](../test_nextmonth_series_doc.py) checks each row against its note and each note's count of held predictions against its status line.

Made by MV2 of Munim, Inc. with AI agents working in his name. Text: CC BY 4.0. Written on 25 October 2026, after the forty-first result.

## The question

Of the generators that a monthly EIA-860M workbook lists as planned to come online the next month, how many does the next workbook list as operating? That share was 0.469 (1,980 of 4,223) in 2016-2019 and 0.349 (2,110 of 6,047) in 2022-2025, counted in generator-months ([`docs/nexttech.md`](nexttech.md)). Results 34 to 41 asked why it fell, and whether a generator's earlier listings say anything about whether it will be on time. Each was pre-registered: its bars were committed before the job that scored them counted anything.

"On time" means the next workbook lists the generator as operating. A "first listing" is a generator's first month planned for the next month since August 2015; "1 month after the last listing" is a generator planned for the next month again right after a one-month slip.

## The eight results

| # | note | predictions held | failed |
|---|---|---|---|
| 34 | [`nexttech.md`](nexttech.md) | 3 of 4 | T2 |
| 35 | [`nexttechonce.md`](nexttechonce.md) | 3 of 4 | O3 |
| 36 | [`nextcount.md`](nextcount.md) | 2 of 3 | K2 |
| 37 | [`nextheld.md`](nextheld.md) | 3 of 3 | none |
| 38 | [`nextgaptech.md`](nextgaptech.md) | 4 of 4 | none |
| 39 | [`gapwin.md`](gapwin.md) | 4 of 5 | W2 |
| 40 | [`plantw.md`](plantw.md) | 3 of 5 | P3, P4 |
| 41 | [`clusterboot.md`](clusterboot.md) | 5 of 5 | none |

In all, 27 of 33 predictions held, and all 8 reproduction checks held.

## Every bar

Copied from each note's table of bars, with the result's number in front. The last column is each note's own.

| # | bar | outcome | numbers |
|---|---|---|---|
| 34 | T0 (check). All technologies reproduce 1,980 of 4,223 and 2,110 of 6,047, at most 1% without a technology | held | 1,980 of 4,223 and 2,110 of 6,047; 32 and 25 without a technology |
| 34 | T1. Solar's share is lower in 2022-2025 than in 2016-2019 | held | 0.506 (1,243 of 2,457) to 0.354 (1,292 of 3,654) |
| 34 | T2. Gas's share is lower in 2022-2025 than in 2016-2019 | failed | 0.401 (298 of 743) to 0.455 (191 of 420) |
| 34 | T3. Batteries' share is lower in 2022-2025 than in 2016-2019 | held | 0.442 (61 of 138) to 0.299 (453 of 1,515) |
| 34 | T4. The within-technology fall is at least half the total fall | held | 0.094 of 0.120 |
| 35 | C0 (check). 14,807 rows that reproduce 1,980 of 4,223 and 2,110 of 6,047 generator-months | held | 14,807 rows; 1,980 of 4,223 and 2,110 of 6,047 |
| 35 | O1. Solar's share, each generator once, is lower in 2022-2025 | held | 0.476 (642 of 1,348) to 0.360 (557 of 1,549) |
| 35 | O2. Batteries' share, each generator once, is lower in 2022-2025 | held | 0.362 (25 of 69) to 0.282 (154 of 547) |
| 35 | O3. Gas's share, each generator once, moves by less than 0.05 | failed | 0.443 (144 of 325) to 0.500 (110 of 220) |
| 35 | O4. The all-technology share falls, and at least half the fall is inside technologies | held | 0.070 of 0.100 |
| 36 | C0 (check). 14,807 rows that reproduce 1,980 of 4,223 and 2,110 of 6,047 generator-months | held | 14,807 rows; 1,980 of 4,223 and 2,110 of 6,047 |
| 36 | K1. In 2022-2025, the share with no earlier listing is above the share with 3 or more | held | 0.362 (866 of 2,393) against 0.306 (428 of 1,398) |
| 36 | K2. In 2022-2025, the share does not rise from 0 to 1 to 2 to 3 or more earlier listings | failed | 0.362, 0.365, 0.357, 0.306 |
| 36 | K3. The K1 gap is smaller in 2016-2019 than in 2022-2025 | held | 0.010 against 0.056 |
| 37 | C1 (check). Each month's rows and on-time rows as in `data/monthcheck_months_2026-09.csv` | held | 366 of 1,194 in 8 months, each month equal |
| 37 | H1. The share with 3 or more earlier listings is below the share with none | held | 0.270 (66 of 244) against 0.304 (144 of 473) |
| 37 | H2. Repeat listings 1 month after the last one are on time more often than those 2-3 months after | held | 0.347 (166 of 479) against 0.249 (43 of 173) |
| 37 | H3. Repeat listings 1 month after the last one are on time more often than first listings | held | 0.347 (166 of 479) against 0.304 (144 of 473) |
| 38 | C0 (check). The file's rows, the three periods' generator-months and the 2022-2025 first listings of solar and batteries as already published | held | 14,807 rows; 1,980 of 4,223, 2,110 of 6,047 and 366 of 1,194; solar 536 of 1,483, batteries 143 of 514 |
| 38 | G1. 2022-2025, solar: 1 month after the last listing above first listings | held | 0.404 (547 of 1,354) against 0.361 (536 of 1,483) |
| 38 | G2. 2022-2025, solar: 1 month after the last listing above 2-3 months after | held | 0.404 (547 of 1,354) against 0.273 (147 of 539) |
| 38 | G3. January to August 2026, solar: 1 month after the last listing above 2-3 months after | held | 0.326 (92 of 282) against 0.229 (24 of 105) |
| 38 | G4. 2022-2025, batteries: 1 month after the last listing above first listings | held | 0.349 (220 of 630) against 0.278 (143 of 514) |
| 39 | C0 (check). The file's rows and the 2020-2021 generator-months of the four technologies, as already published | held | 14,807 rows; 2020-2021: solar 686 of 1,600, batteries 103 of 344, gas 150 of 375, wind 143 of 373 |
| 39 | W1. Solar: 1 month after the last listing above first listings | held | 0.447 (240 of 537) against 0.414 (326 of 787) |
| 39 | W2. Solar: 1 month after the last listing above 2-3 months after | failed | 0.447 (240 of 537) against 0.451 (96 of 213) |
| 39 | W3. Batteries: 1 month after the last listing above first listings | held | 0.352 (45 of 128) against 0.252 (37 of 147) |
| 39 | W4. Gas: 1 month after the last listing below first listings | held | 0.400 (56 of 140) against 0.405 (68 of 168) |
| 39 | W5. Wind: 1 month after the last listing below first listings | held | 0.350 (64 of 183) against 0.462 (66 of 143) |
| 40 | C0 (check). The file's rows and md5 and the pooled 2016-2025 solar cells in generator-months, as already published | held | 14,807 rows, md5 1681df9fdee9878ca2c359d1239c6467; solar first listings 1,474 of 3,568, 1 month after the last listing 1,230 of 2,657 |
| 40 | P1. Solar, 2016-2025: 1 month after the last listing above first listings | held | 0.624 over 1,381 plants against 0.417 over 3,316 plants |
| 40 | P2. Batteries, 2016-2025: 1 month after the last listing above first listings | held | 0.519 over 371 plants against 0.279 over 680 plants |
| 40 | P3. Wind, 2016-2025: 1 month after the last listing below first listings | failed | 0.665 over 198 plants against 0.495 over 460 plants |
| 40 | P4. Gas, 2016-2025: 1 month after the last listing below first listings | failed | 0.586 over 108 plants against 0.425 over 246 plants |
| 40 | P5. Solar, January 2022 to August 2026: 1 month after the last listing above 2-3 months after | held | 0.545 over 791 plants against 0.323 over 443 plants |
| 41 | C0 (check). The file's rows and md5 and the ten generator-month cells already published | held | 14,807 rows, md5 1681df9fdee9878ca2c359d1239c6467; 10 of 10 cells reproduced |
| 41 | B1. Solar, 2016-2025: 1 month after the last listing minus first listings; the interval is above 0 | held | +0.0498 (+0.0200 to +0.0795); 1 month after the last listing 1,230 of 2,657 at 1,381 plants; first listings 1,474 of 3,568 at 3,316 plants |
| 41 | B2. Batteries, 2016-2025: 1 month after the last listing minus first listings; the interval is above 0 | held | +0.0824 (+0.0275 to +0.1405); 1 month after the last listing 297 of 816 at 371 plants; first listings 205 of 728 at 680 plants |
| 41 | B3. Wind, 2016-2025: first listings minus 1 month after the last listing; the interval includes 0 | held | +0.0661 (-0.0340 to +0.1530); first listings 237 of 497 at 460 plants; 1 month after the last listing 191 of 465 at 198 plants |
| 41 | B4. Gas, 2016-2025: first listings minus 1 month after the last listing; the interval includes 0 | held | +0.0965 (-0.0545 to +0.2165); first listings 312 of 687 at 246 plants; 1 month after the last listing 206 of 576 at 108 plants |
| 41 | B5. Solar, January 2022 to August 2026: 1 month after the last listing minus 2-3 months after; the interval is above 0 | held | +0.1251 (+0.0798 to +0.1686); 1 month after the last listing 639 of 1,636 at 791 plants; 2-3 months after 171 of 644 at 443 plants |

## What still stands

- **The fall is mostly inside technologies.** With the 2016-2019 mix of technologies, the share would have fallen from 0.469 to 0.374: "That is 79% of the fall." Counted with each generator once, "a little under 70%" is inside technologies. Solar and batteries fell; gas did not (T2 and O3 failed, and one gas plant with 12 turbines listed again and again in 2016-2018 drives the early gas share). These two results were not retested with whole plants resampled.
- **For solar and batteries, a one-month slip has been a mildly good sign.** Pooled over 2016-2025, a generator planned for the next month again right after a one-month slip was on time more often than a first listing, by +0.0498 (+0.0200 to +0.0795) in solar and +0.0824 (+0.0275 to +0.1405) in batteries, with 95% intervals from resampling whole plants (B1, B2). It held in generator-months in 2022-2025 (G1, G4) and in the held-out 2020-2021 (W1, W3).
- **For solar since 2022, a slip of 2-3 months has been a bad sign.** One month after the last listing against 2-3 months after, January 2022 to August 2026: +0.1251 (+0.0798 to +0.1686) (B5). In 2020-2021 it did not show (W2 failed, 0.447 against 0.451).

## What does not stand, or was never shown

- **Wind and gas reversals: not shown.** In generator-months a one-month slip pointed the other way for wind and gas (W4, W5 held), but W4 held by 0.005, one generator-month, and with whole plants resampled both pooled intervals include 0 (B3, B4), as does wind's in 2020-2021: "wind's is +0.1118 (-0.0530 to +0.2323)".
- **All technologies together, a one-month slip is not shown to be a good sign.** The thirty-seventh result's 2026 comparison (H3, 0.347 against 0.304) is +0.0421 (-0.0335 to +0.1201) with whole plants resampled, and the pooled interval includes 0 in every period. H1 and H2 were not retested.
- **The number of earlier listings matters less than how long ago the last one was.** In 2022-2025 the share fell with 3 or more earlier listings (K1), but not step by step (K2 failed). In 2026 the H1 gap comes from 5 or more earlier listings, 0.163 (15 of 92), and weighting each technology by its part of those rows leaves "the gap only 0.009".
- **Weighting each plant once is not a fair test here.** It lifts the one-month cell by 0.155 to 0.254 in every technology and first listings by at most 0.029, because a plant collects more rows in a repeat cell by missing more months (fortieth result). P3 and P4 failed for that reason, not because of the plants.

## Still open

Three plans fixed before their data exist are not yet scored: [`q4held-plan.md`](q4held-plan.md) (October to December 2026 pooled, the series' first prospective test; December's workbook is expected in late January 2027), [`dec2026-plan.md`](dec2026-plan.md) and [`oct2026-plan.md`](oct2026-plan.md) (EIA's October 2026 workbook, due 24 November 2026).

## Limits

- Generator-months from one cohort file made by this repository's own code. "On time" is the next workbook's status: one listed as operating a month late is not on time, and one that leaves the file is not on time.
- Plant resampling (forty-first result) handles dependence within a plant, not between plants of one developer, region or year. Results 34 to 40 have no intervals.
- Eight results on overlapping data, each chosen after reading the one before. Results 37, 39 and 41 tested patterns on periods or methods they were not found with; the rest are within the data that suggested them.
- These are associations, not causes.
