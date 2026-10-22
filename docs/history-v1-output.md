# history 0.1.0: how far back does PUDL's EIA-860M changelog keep stale values?

Twenty-ninth test. Predictions fixed in docs/history-revert-predictions.md, method pre-registered in docs/history-revert-preregistration.md. MV2 of Munim, Inc. (made with AI agents).

Pre-registration live: True (checks 1, at 2026-10-22T04:13:10Z; commit 889040e02da91aa8411ffb74b776e35925f09bb5).

## Checks

| check | ok | detail |
|---|---|---|
| C1 workbooks | True | zips with a listed md5 12 of 12; years read 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026; months read 134; not readable: none |
| C2 PUDL through 2026-08 | True | latest report 2026-08 |
| C3 keys | True | years below 0.95: none; lowest share 0.9999 |
| C4 links | True | disagree 17193, simulation stale 28297 (each at least 100) |

## Predictions

Scored: 4 of 5 predictions held.

| prediction | bar | value | held |
|---|---|---|---|
| P1 hits in each year 2016-2025 | at least 50 | lowest 56 (2016) | True |
| P2 coverage, all months | 0.90 | 0.9249 (15901 of 17193) | True |
| P3 precision, all months | 0.50 | 0.5619 (15901 of 28297) | True |
| P4 hits per month, 2025 above 2017 | greater | 283.33 against 9.42 | True |
| P5 coverage in each year 2016-2025 | 0.80 | lowest 0.4954 (2018) | False |

## By year

| year | months | workbook generator-months | with a PUDL record | share | in both | disagree | hits | simulation stale | coverage | precision | hits per month | PUDL later | PUDL held before | other | workbook only | of which held before |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2015 | 6 | 144185 | 144185 | 1.0000 | 144185 | 5 | 5 | 6 | 1.0000 | 0.8333 | 0.83 | 0 | 0 | 0 | 0 | 0 |
| 2016 | 12 | 294742 | 294742 | 1.0000 | 294742 | 62 | 56 | 159 | 0.9032 | 0.3522 | 4.67 | 6 | 0 | 0 | 0 | 0 |
| 2017 | 12 | 315212 | 315212 | 1.0000 | 315212 | 219 | 113 | 366 | 0.5160 | 0.3087 | 9.42 | 16 | 90 | 0 | 0 | 0 |
| 2018 | 12 | 327072 | 327072 | 1.0000 | 327072 | 438 | 217 | 591 | 0.4954 | 0.3672 | 18.08 | 16 | 205 | 0 | 0 | 0 |
| 2019 | 12 | 341338 | 341338 | 1.0000 | 341338 | 752 | 576 | 1173 | 0.7660 | 0.4910 | 48.0 | 12 | 164 | 0 | 0 | 0 |
| 2020 | 12 | 355183 | 355183 | 1.0000 | 355183 | 1295 | 1184 | 2050 | 0.9143 | 0.5776 | 98.67 | 12 | 99 | 0 | 0 | 0 |
| 2021 | 12 | 369193 | 369193 | 1.0000 | 369193 | 1507 | 1411 | 2515 | 0.9363 | 0.5610 | 117.58 | 12 | 84 | 0 | 0 | 0 |
| 2022 | 12 | 385223 | 385223 | 1.0000 | 385223 | 1810 | 1739 | 3096 | 0.9608 | 0.5617 | 144.92 | 3 | 68 | 0 | 0 | 0 |
| 2023 | 12 | 399449 | 399449 | 1.0000 | 399449 | 2333 | 2253 | 3883 | 0.9657 | 0.5802 | 187.75 | 5 | 75 | 0 | 0 | 0 |
| 2024 | 12 | 414833 | 414833 | 1.0000 | 414833 | 2774 | 2667 | 4607 | 0.9614 | 0.5789 | 222.25 | 12 | 95 | 0 | 0 | 0 |
| 2025 | 12 | 434022 | 434022 | 1.0000 | 434022 | 3611 | 3400 | 5610 | 0.9416 | 0.6061 | 283.33 | 35 | 176 | 0 | 0 | 0 |
| 2026 | 8 | 300015 | 299999 | 0.9999 | 299999 | 2387 | 2280 | 4241 | 0.9552 | 0.5376 | 285.0 | 12 | 95 | 0 | 16 | 0 |
| all | 134 | 4080467 | 4080451 | 1.0000 | 4080451 | 17193 | 15901 | 28297 | 0.9249 | 0.5619 | 118.66 | 141 | 1151 | 0 | 16 | 0 |

## Changelog rebuilt from the workbooks: rows by year and event

| year | first | changed | left | back |
|---|---|---|---|---|
| 2015 | 24193 | 1472 | 43 | 1 |
| 2016 | 1174 | 27603 | 178 | 10 |
| 2017 | 2008 | 4200 | 372 | 24 |
| 2018 | 1067 | 3241 | 169 | 25 |
| 2019 | 1373 | 3776 | 160 | 29 |
| 2020 | 1265 | 4401 | 192 | 40 |
| 2021 | 1440 | 4852 | 155 | 40 |
| 2022 | 1232 | 4543 | 194 | 30 |
| 2023 | 1356 | 5139 | 152 | 27 |
| 2024 | 1884 | 5440 | 471 | 313 |
| 2025 | 1472 | 5329 | 219 | 36 |
| 2026 | 1455 | 4061 | 216 | 38 |

## Disagreements by kind, first differing field and status (top 40)

| kind | field | workbook | PUDL | generator-months |
|---|---|---|---|---|
| predicted | status | OP | OA | 10800 |
| predicted | status | OP | OS | 1132 |
| predicted | status | OP | SB | 614 |
| predicted | status | OP | RE | 589 |
| predicted | status | OA | OS | 440 |
| held_before | status | OP | OA | 424 |
| predicted | MW | OP | OP | 403 |
| predicted | status | OA | OP | 402 |
| predicted | status | SB | OP | 298 |
| held_before | status | OS | OP | 247 |
| held_before | MW | OP | OP | 218 |
| held_before | status | OA | OP | 210 |
| predicted | status | OS | OA | 158 |
| predicted | planned month | U | U | 142 |
| predicted | planned month | V | V | 136 |
| predicted | status | OS | OP | 99 |
| predicted | status | OA | SB | 97 |
| predicted | planned month | P | P | 95 |
| pudl_later | MW | OP | OP | 79 |
| predicted | status | RE | OP | 77 |
| predicted | planned month | T | T | 69 |
| predicted | planned month | L | L | 56 |
| pudl_later | status | OP | SB | 42 |
| predicted | status | L | P | 34 |
| predicted | status | V | U | 27 |
| predicted | status | U | L | 25 |
| held_before | status | OP | SB | 24 |
| predicted | status | SB | OA | 22 |
| predicted | status | P | L | 17 |
| predicted | status | U | V | 16 |
| predicted | status | U | T | 14 |
| predicted | planned month | TS | TS | 14 |
| predicted | status | OS | RE | 12 |
| held_before | planned month | U | U | 12 |
| predicted | status | OA | RE | 12 |
| pudl_later | status | OP | OA | 8 |
| predicted | status | T | U | 8 |
| predicted | status | T | L | 8 |
| predicted | status | T | P | 8 |
| predicted | status | L | T | 8 |

## Disagreements the rule does not predict (first 10 per year and kind, in month and key order; not a random draw)

- 2016 pudl_later: 2016-03 10382/GEN1 workbook OP, -, - MW, PUDL OA, -, - MW (from 2016-02); 2016-03 10789/GEN3 workbook OS, -, - MW, PUDL OP, -, - MW (from 2016-02); 2016-03 3319/1 workbook RE, -, - MW, PUDL OP, -, - MW (from 2016-02); 2016-03 3319/2 workbook RE, -, - MW, PUDL OP, -, - MW (from 2016-02); 2016-03 56352/1 workbook P, 2020-05, - MW, PUDL P, 2019-05, - MW (from 2016-02); 2016-03 56352/2 workbook P, 2023-05, - MW, PUDL P, 2021-05, - MW (from 2016-02)
- 2017 held_before: 2017-08 3075/11 workbook OP, -, 66.5 MW, PUDL OA, -, 66.5 MW (from 2017-04); 2017-08 3075/12 workbook OA, -, 66.5 MW, PUDL OP, -, 66.5 MW (from 2017-04); 2017-08 3075/7 workbook OA, -, 62.1 MW, PUDL OP, -, 62.1 MW (from 2017-04); 2017-08 3075/8 workbook OA, -, 62.1 MW, PUDL OP, -, 62.1 MW (from 2017-04); 2017-08 3082/2 workbook OP, -, 135.0 MW, PUDL OA, -, 135.0 MW (from 2017-04); 2017-08 3082/4 workbook OP, -, 135.0 MW, PUDL OA, -, 135.0 MW (from 2017-04); 2017-08 3082/6 workbook OA, -, 135.0 MW, PUDL OP, -, 135.0 MW (from 2017-04); 2017-08 3925/1 workbook OP, -, 90.0 MW, PUDL OA, -, 90.0 MW (from 2017-04); 2017-08 3925/2 workbook OA, -, 90.0 MW, PUDL OP, -, 90.0 MW (from 2017-04); 2017-08 6175/1 workbook OA, -, 135.0 MW, PUDL OP, -, 135.0 MW (from 2017-04)
- 2017 pudl_later: 2017-07 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04); 2017-08 3925/3 workbook OP, -, 90.0 MW, PUDL OA, -, 90.0 MW (from 2017-04); 2017-08 3925/5 workbook OA, -, 111.0 MW, PUDL OP, -, 111.0 MW (from 2017-04); 2017-08 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04); 2017-09 3925/3 workbook OP, -, 90.0 MW, PUDL OA, -, 90.0 MW (from 2017-04); 2017-09 3925/5 workbook OA, -, 111.0 MW, PUDL OP, -, 111.0 MW (from 2017-04); 2017-09 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04); 2017-10 3925/3 workbook OP, -, 90.0 MW, PUDL OA, -, 90.0 MW (from 2017-04); 2017-10 3925/5 workbook OA, -, 111.0 MW, PUDL OP, -, 111.0 MW (from 2017-04); 2017-10 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04)
- 2018 held_before: 2018-01 3075/11 workbook OP, -, 66.5 MW, PUDL OA, -, 66.5 MW (from 2017-04); 2018-01 3075/12 workbook OA, -, 66.5 MW, PUDL OP, -, 66.5 MW (from 2017-04); 2018-01 3075/7 workbook OA, -, 62.1 MW, PUDL OP, -, 62.1 MW (from 2017-04); 2018-01 3075/8 workbook OA, -, 62.1 MW, PUDL OP, -, 62.1 MW (from 2017-04); 2018-01 3082/2 workbook OP, -, 135.0 MW, PUDL OA, -, 135.0 MW (from 2017-04); 2018-01 3082/4 workbook OP, -, 135.0 MW, PUDL OA, -, 135.0 MW (from 2017-04); 2018-01 3082/6 workbook OA, -, 135.0 MW, PUDL OP, -, 135.0 MW (from 2017-04); 2018-01 3655/1 workbook OS, -, 2.4 MW, PUDL OP, -, 2.4 MW (from 2017-07); 2018-01 3655/2 workbook OS, -, 2.4 MW, PUDL OP, -, 2.4 MW (from 2017-07); 2018-01 3655/4 workbook OS, -, 5.5 MW, PUDL OP, -, 5.5 MW (from 2017-07)
- 2018 pudl_later: 2018-01 3925/3 workbook OP, -, 90.0 MW, PUDL OA, -, 90.0 MW (from 2017-04); 2018-01 3925/5 workbook OA, -, 111.0 MW, PUDL OP, -, 111.0 MW (from 2017-04); 2018-01 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04); 2018-02 3925/3 workbook OP, -, 90.0 MW, PUDL OA, -, 90.0 MW (from 2017-04); 2018-02 3925/5 workbook OA, -, 111.0 MW, PUDL OP, -, 111.0 MW (from 2017-04); 2018-02 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04); 2018-03 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04); 2018-04 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04); 2018-05 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04); 2018-06 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04)
- 2019 held_before: 2019-01 3075/11 workbook OP, -, 66.5 MW, PUDL OA, -, 66.5 MW (from 2017-04); 2019-01 3082/2 workbook OP, -, 135.0 MW, PUDL OA, -, 135.0 MW (from 2017-04); 2019-01 3082/4 workbook OP, -, 135.0 MW, PUDL OA, -, 135.0 MW (from 2017-04); 2019-01 3082/6 workbook OA, -, 135.0 MW, PUDL OP, -, 135.0 MW (from 2017-04); 2019-01 3655/1 workbook OS, -, 2.4 MW, PUDL OP, -, 2.4 MW (from 2017-07); 2019-01 3655/2 workbook OS, -, 2.4 MW, PUDL OP, -, 2.4 MW (from 2017-07); 2019-01 3655/4 workbook OS, -, 5.5 MW, PUDL OP, -, 5.5 MW (from 2017-07); 2019-01 3925/1 workbook OP, -, 90.0 MW, PUDL OA, -, 90.0 MW (from 2017-04); 2019-01 3925/2 workbook OA, -, 90.0 MW, PUDL OP, -, 90.0 MW (from 2017-04); 2019-01 56666/1 workbook OP, -, 94.0 MW, PUDL OP, -, 97.8 MW (from 2017-07)
- 2019 pudl_later: 2019-01 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04); 2019-02 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04); 2019-03 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04); 2019-04 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04); 2019-05 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04); 2019-06 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04); 2019-07 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04); 2019-08 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04); 2019-09 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04); 2019-10 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04)
- 2020 held_before: 2020-01 3075/11 workbook OP, -, 66.5 MW, PUDL OA, -, 66.5 MW (from 2017-04); 2020-01 3082/2 workbook OP, -, 135.0 MW, PUDL OA, -, 135.0 MW (from 2017-04); 2020-01 3082/4 workbook OP, -, 135.0 MW, PUDL OA, -, 135.0 MW (from 2019-02); 2020-01 3082/6 workbook OA, -, 135.0 MW, PUDL OP, -, 135.0 MW (from 2017-04); 2020-01 3655/1 workbook OS, -, 2.4 MW, PUDL OP, -, 2.4 MW (from 2017-07); 2020-01 3655/2 workbook OS, -, 2.4 MW, PUDL OP, -, 2.4 MW (from 2017-07); 2020-01 3655/4 workbook OS, -, 5.5 MW, PUDL OP, -, 5.5 MW (from 2017-07); 2020-01 3925/1 workbook OP, -, 90.0 MW, PUDL OA, -, 90.0 MW (from 2017-04); 2020-01 56841/2 workbook OP, -, 39.0 MW, PUDL OP, -, 40.7 MW (from 2017-07); 2020-01 57299/1 workbook OP, -, 111.0 MW, PUDL OP, -, 115.8 MW (from 2017-07)
- 2020 pudl_later: 2020-01 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04); 2020-02 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04); 2020-03 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04); 2020-04 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04); 2020-05 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04); 2020-06 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04); 2020-07 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04); 2020-08 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04); 2020-09 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04); 2020-10 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04)
- 2021 held_before: 2021-01 3075/11 workbook OP, -, 66.5 MW, PUDL OA, -, 66.5 MW (from 2017-04); 2021-01 3082/2 workbook OP, -, 135.0 MW, PUDL OA, -, 135.0 MW (from 2017-04); 2021-01 3082/4 workbook OP, -, 135.0 MW, PUDL OA, -, 135.0 MW (from 2019-02); 2021-01 3925/1 workbook OP, -, 90.0 MW, PUDL OA, -, 90.0 MW (from 2017-04); 2021-01 57299/1 workbook OP, -, 111.0 MW, PUDL OP, -, 115.8 MW (from 2017-07); 2021-01 57949/2 workbook OS, -, 1.0 MW, PUDL OP, -, 1.0 MW (from 2017-04); 2021-01 6175/2 workbook OP, -, 135.0 MW, PUDL OA, -, 135.0 MW (from 2019-12); 2021-02 3075/11 workbook OP, -, 66.5 MW, PUDL OA, -, 66.5 MW (from 2017-04); 2021-02 3082/2 workbook OP, -, 135.0 MW, PUDL OA, -, 135.0 MW (from 2017-04); 2021-02 3082/4 workbook OP, -, 135.0 MW, PUDL OA, -, 135.0 MW (from 2019-02)
- 2021 pudl_later: 2021-01 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04); 2021-02 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04); 2021-03 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04); 2021-04 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04); 2021-05 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04); 2021-06 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04); 2021-07 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04); 2021-08 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04); 2021-09 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04); 2021-10 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04)
- 2022 held_before: 2022-01 3075/11 workbook OP, -, 66.5 MW, PUDL OA, -, 66.5 MW (from 2017-04); 2022-01 3082/2 workbook OP, -, 135.0 MW, PUDL OA, -, 135.0 MW (from 2017-04); 2022-01 3082/4 workbook OP, -, 135.0 MW, PUDL OA, -, 135.0 MW (from 2019-02); 2022-01 3925/1 workbook OP, -, 90.0 MW, PUDL OA, -, 90.0 MW (from 2017-04); 2022-01 57299/1 workbook OP, -, 111.0 MW, PUDL OP, -, 115.8 MW (from 2017-07); 2022-01 57949/2 workbook OS, -, 1.0 MW, PUDL OP, -, 1.0 MW (from 2017-04); 2022-01 6175/2 workbook OP, -, 135.0 MW, PUDL OA, -, 135.0 MW (from 2019-12); 2022-02 3075/11 workbook OP, -, 66.5 MW, PUDL OA, -, 66.5 MW (from 2017-04); 2022-02 3082/2 workbook OP, -, 135.0 MW, PUDL OA, -, 135.0 MW (from 2017-04); 2022-02 3082/4 workbook OP, -, 135.0 MW, PUDL OA, -, 135.0 MW (from 2019-02)
- 2022 pudl_later: 2022-01 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04); 2022-02 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04); 2022-03 59485/PV2 workbook OP, -, 2.2 MW, PUDL OP, -, 1.2 MW (from 2017-04)
- 2023 held_before: 2023-01 3082/2 workbook OP, -, 135.0 MW, PUDL OA, -, 135.0 MW (from 2017-04); 2023-01 3082/4 workbook OP, -, 135.0 MW, PUDL OA, -, 135.0 MW (from 2019-02); 2023-01 3925/1 workbook OP, -, 90.0 MW, PUDL OA, -, 90.0 MW (from 2022-07); 2023-01 57949/2 workbook OS, -, 1.0 MW, PUDL OP, -, 1.0 MW (from 2017-04); 2023-01 6175/2 workbook OP, -, 135.0 MW, PUDL OA, -, 135.0 MW (from 2019-12); 2023-02 3082/2 workbook OP, -, 135.0 MW, PUDL OA, -, 135.0 MW (from 2017-04); 2023-02 3082/4 workbook OP, -, 135.0 MW, PUDL OA, -, 135.0 MW (from 2019-02); 2023-02 3925/1 workbook OP, -, 90.0 MW, PUDL OA, -, 90.0 MW (from 2022-07); 2023-02 57949/2 workbook OS, -, 1.0 MW, PUDL OP, -, 1.0 MW (from 2017-04); 2023-02 6175/2 workbook OP, -, 135.0 MW, PUDL OA, -, 135.0 MW (from 2019-12)
- 2023 pudl_later: 2023-08 57868/UNIT3 workbook OP, -, 0.3 MW, PUDL OP, -, 0.7 MW (from 2023-05); 2023-09 57868/UNIT3 workbook OP, -, 0.3 MW, PUDL OP, -, 0.7 MW (from 2023-05); 2023-10 57868/UNIT3 workbook OP, -, 0.3 MW, PUDL OP, -, 0.7 MW (from 2023-05); 2023-11 57868/UNIT3 workbook OP, -, 0.3 MW, PUDL OP, -, 0.7 MW (from 2023-05); 2023-12 57868/UNIT3 workbook OP, -, 0.3 MW, PUDL OP, -, 0.7 MW (from 2023-05)
- 2024 held_before: 2024-01 3075/11 workbook OP, -, 66.5 MW, PUDL OA, -, 66.5 MW (from 2017-04); 2024-01 3082/2 workbook OP, -, 135.0 MW, PUDL OA, -, 135.0 MW (from 2017-04); 2024-01 3925/3 workbook OP, -, 90.0 MW, PUDL OA, -, 90.0 MW (from 2021-01); 2024-01 54965/ACTG workbook OS, -, 2.0 MW, PUDL OP, -, 2.0 MW (from 2020-01); 2024-01 57868/UNIT1 workbook OP, -, 0.5 MW, PUDL OP, -, 1.3 MW (from 2023-05); 2024-01 57949/2 workbook OS, -, 1.0 MW, PUDL OP, -, 1.0 MW (from 2017-04); 2024-01 6175/1 workbook OA, -, 135.0 MW, PUDL OP, -, 135.0 MW (from 2017-04); 2024-02 10700/TG6 workbook OS, -, 16.0 MW, PUDL OP, -, 16.0 MW (from 2022-04); 2024-02 3075/11 workbook OP, -, 66.5 MW, PUDL OA, -, 66.5 MW (from 2017-04); 2024-02 3082/2 workbook OP, -, 135.0 MW, PUDL OA, -, 135.0 MW (from 2017-04)
- 2024 pudl_later: 2024-01 57868/UNIT3 workbook OP, -, 0.3 MW, PUDL OP, -, 0.7 MW (from 2023-05); 2024-02 57868/UNIT3 workbook OP, -, 0.3 MW, PUDL OP, -, 0.7 MW (from 2023-05); 2024-03 57868/UNIT3 workbook OP, -, 0.3 MW, PUDL OP, -, 0.7 MW (from 2023-05); 2024-04 57868/UNIT3 workbook OP, -, 0.3 MW, PUDL OP, -, 0.7 MW (from 2023-05); 2024-05 57868/UNIT3 workbook OP, -, 0.3 MW, PUDL OP, -, 0.7 MW (from 2023-05); 2024-06 57868/UNIT3 workbook OP, -, 0.3 MW, PUDL OP, -, 0.7 MW (from 2023-05); 2024-07 57868/UNIT3 workbook OP, -, 0.3 MW, PUDL OP, -, 0.7 MW (from 2023-05); 2024-08 57868/UNIT3 workbook OP, -, 0.3 MW, PUDL OP, -, 0.7 MW (from 2023-05); 2024-09 57868/UNIT3 workbook OP, -, 0.3 MW, PUDL OP, -, 0.7 MW (from 2023-05); 2024-10 57868/UNIT3 workbook OP, -, 0.3 MW, PUDL OP, -, 0.7 MW (from 2023-05)
- 2025 held_before: 2025-01 10700/TG6 workbook OS, -, 16.0 MW, PUDL OP, -, 16.0 MW (from 2022-04); 2025-01 3075/11 workbook OP, -, 66.5 MW, PUDL OA, -, 66.5 MW (from 2017-04); 2025-01 3082/2 workbook OP, -, 135.0 MW, PUDL OA, -, 135.0 MW (from 2017-04); 2025-01 3925/3 workbook OP, -, 90.0 MW, PUDL OA, -, 90.0 MW (from 2021-01); 2025-01 54965/ACTG workbook OA, -, 2.0 MW, PUDL OP, -, 2.0 MW (from 2020-01); 2025-01 57868/UNIT1 workbook OP, -, 0.5 MW, PUDL OP, -, 1.3 MW (from 2023-05); 2025-01 57949/2 workbook OS, -, 1.0 MW, PUDL OP, -, 1.0 MW (from 2017-04); 2025-01 6175/1 workbook OA, -, 135.0 MW, PUDL OP, -, 135.0 MW (from 2017-04); 2025-02 10700/TG6 workbook OS, -, 16.0 MW, PUDL OP, -, 16.0 MW (from 2022-04); 2025-02 3075/11 workbook OP, -, 66.5 MW, PUDL OA, -, 66.5 MW (from 2017-04)
- 2025 pudl_later: 2025-01 57868/UNIT3 workbook OP, -, 0.3 MW, PUDL OP, -, 0.7 MW (from 2023-05); 2025-02 57868/UNIT3 workbook OP, -, 0.3 MW, PUDL OP, -, 0.7 MW (from 2023-05); 2025-03 57868/UNIT3 workbook OP, -, 0.3 MW, PUDL OP, -, 0.7 MW (from 2023-05); 2025-04 57868/UNIT3 workbook OP, -, 0.3 MW, PUDL OP, -, 0.7 MW (from 2023-05); 2025-05 57868/UNIT3 workbook OP, -, 0.3 MW, PUDL OP, -, 0.7 MW (from 2023-05); 2025-08 54477/GEN1 workbook OP, -, 1.1 MW, PUDL SB, -, 1.1 MW (from 2025-06); 2025-08 54477/GEN2 workbook OP, -, 1.1 MW, PUDL SB, -, 1.1 MW (from 2025-06); 2025-08 54477/GEN3 workbook OP, -, 1.1 MW, PUDL SB, -, 1.1 MW (from 2025-06); 2025-08 54477/GEN4 workbook OP, -, 1.1 MW, PUDL SB, -, 1.1 MW (from 2025-06); 2025-08 54477/GEN5 workbook OP, -, 1.1 MW, PUDL SB, -, 1.1 MW (from 2025-06)
- 2026 held_before: 2026-01 10700/TG6 workbook OS, -, 16.0 MW, PUDL OP, -, 16.0 MW (from 2022-04); 2026-01 3075/11 workbook OP, -, 66.5 MW, PUDL OA, -, 66.5 MW (from 2017-04); 2026-01 3075/7 workbook OA, -, 62.1 MW, PUDL OP, -, 62.1 MW (from 2017-04); 2026-01 3075/8 workbook OA, -, 62.1 MW, PUDL OP, -, 62.1 MW (from 2017-04); 2026-01 3082/2 workbook OP, -, 135.0 MW, PUDL OA, -, 135.0 MW (from 2017-04); 2026-01 3082/4 workbook OP, -, 135.0 MW, PUDL OA, -, 135.0 MW (from 2019-02); 2026-01 3925/3 workbook OP, -, 90.0 MW, PUDL OA, -, 90.0 MW (from 2021-01); 2026-01 54477/GEN7 workbook OA, -, 1.1 MW, PUDL SB, -, 1.1 MW (from 2025-06); 2026-01 54965/ACTG workbook OA, -, 2.0 MW, PUDL OP, -, 2.0 MW (from 2020-01); 2026-01 57868/UNIT1 workbook OP, -, 0.5 MW, PUDL OP, -, 1.3 MW (from 2023-05)
- 2026 pudl_later: 2026-01 54477/GEN1 workbook OP, -, 1.1 MW, PUDL SB, -, 1.1 MW (from 2025-06); 2026-01 54477/GEN2 workbook OP, -, 1.1 MW, PUDL SB, -, 1.1 MW (from 2025-06); 2026-01 54477/GEN3 workbook OP, -, 1.1 MW, PUDL SB, -, 1.1 MW (from 2025-06); 2026-01 54477/GEN4 workbook OP, -, 1.1 MW, PUDL SB, -, 1.1 MW (from 2025-06); 2026-01 54477/GEN5 workbook OP, -, 1.1 MW, PUDL SB, -, 1.1 MW (from 2025-06); 2026-01 54477/GEN6 workbook OP, -, 1.1 MW, PUDL SB, -, 1.1 MW (from 2025-06); 2026-02 54477/GEN1 workbook OP, -, 1.1 MW, PUDL SB, -, 1.1 MW (from 2025-06); 2026-02 54477/GEN2 workbook OP, -, 1.1 MW, PUDL SB, -, 1.1 MW (from 2025-06); 2026-02 54477/GEN3 workbook OP, -, 1.1 MW, PUDL SB, -, 1.1 MW (from 2025-06); 2026-02 54477/GEN4 workbook OP, -, 1.1 MW, PUDL SB, -, 1.1 MW (from 2025-06)

## By month

| month | in both | disagree | hits |
|---|---|---|---|
| 2015-07 | 23988 | 0 | 0 |
| 2015-08 | 23986 | 0 | 0 |
| 2015-09 | 23982 | 2 | 2 |
| 2015-10 | 23974 | 0 | 0 |
| 2015-11 | 24104 | 3 | 3 |
| 2015-12 | 24151 | 0 | 0 |
| 2016-01 | 24174 | 0 | 0 |
| 2016-02 | 24333 | 14 | 14 |
| 2016-03 | 24439 | 31 | 25 |
| 2016-04 | 24503 | 0 | 0 |
| 2016-05 | 24532 | 0 | 0 |
| 2016-06 | 24568 | 5 | 5 |
| 2016-07 | 24592 | 0 | 0 |
| 2016-08 | 24620 | 0 | 0 |
| 2016-09 | 24612 | 1 | 1 |
| 2016-10 | 24612 | 5 | 5 |
| 2016-11 | 24600 | 5 | 5 |
| 2016-12 | 25157 | 1 | 1 |
| 2017-01 | 25155 | 0 | 0 |
| 2017-02 | 25317 | 2 | 2 |
| 2017-03 | 26092 | 1 | 1 |
| 2017-04 | 26234 | 21 | 21 |
| 2017-05 | 26239 | 24 | 24 |
| 2017-06 | 26340 | 23 | 23 |
| 2017-07 | 26441 | 28 | 27 |
| 2017-08 | 26530 | 22 | 9 |
| 2017-09 | 26645 | 24 | 1 |
| 2017-10 | 26675 | 24 | 1 |
| 2017-11 | 26727 | 25 | 2 |
| 2017-12 | 26817 | 25 | 2 |
| 2018-01 | 26884 | 35 | 12 |
| 2018-02 | 26965 | 36 | 14 |
| 2018-03 | 27026 | 41 | 24 |
| 2018-04 | 27071 | 38 | 18 |
| 2018-05 | 27135 | 40 | 20 |
| 2018-06 | 27185 | 36 | 19 |
| 2018-07 | 27238 | 35 | 18 |
| 2018-08 | 27329 | 34 | 17 |
| 2018-09 | 27438 | 35 | 18 |
| 2018-10 | 27463 | 35 | 18 |
| 2018-11 | 27598 | 34 | 17 |
| 2018-12 | 27740 | 39 | 22 |
| 2019-01 | 27916 | 53 | 36 |
| 2019-02 | 28006 | 61 | 46 |
| 2019-03 | 28079 | 59 | 44 |
| 2019-04 | 28174 | 62 | 47 |
| 2019-05 | 28293 | 62 | 47 |
| 2019-06 | 28409 | 61 | 46 |
| 2019-07 | 28443 | 61 | 46 |
| 2019-08 | 28595 | 61 | 46 |
| 2019-09 | 28721 | 61 | 47 |
| 2019-10 | 28796 | 62 | 48 |
| 2019-11 | 28924 | 65 | 51 |
| 2019-12 | 28982 | 84 | 72 |
| 2020-01 | 29107 | 122 | 110 |
| 2020-02 | 29229 | 114 | 102 |
| 2020-03 | 29314 | 108 | 96 |
| 2020-04 | 29402 | 119 | 107 |
| 2020-05 | 29485 | 135 | 125 |
| 2020-06 | 29569 | 99 | 91 |
| 2020-07 | 29627 | 103 | 95 |
| 2020-08 | 29708 | 101 | 93 |
| 2020-09 | 29790 | 100 | 92 |
| 2020-10 | 29879 | 98 | 91 |
| 2020-11 | 29978 | 99 | 92 |
| 2020-12 | 30095 | 97 | 90 |
| 2021-01 | 30201 | 112 | 104 |
| 2021-02 | 30310 | 112 | 104 |
| 2021-03 | 30394 | 130 | 122 |
| 2021-04 | 30482 | 132 | 124 |
| 2021-05 | 30541 | 129 | 121 |
| 2021-06 | 30658 | 127 | 119 |
| 2021-07 | 30737 | 126 | 118 |
| 2021-08 | 30775 | 128 | 120 |
| 2021-09 | 31146 | 127 | 119 |
| 2021-10 | 31216 | 125 | 117 |
| 2021-11 | 31313 | 129 | 121 |
| 2021-12 | 31420 | 130 | 122 |
| 2022-01 | 31558 | 148 | 140 |
| 2022-02 | 31623 | 150 | 142 |
| 2022-03 | 31940 | 156 | 149 |
| 2022-04 | 32019 | 147 | 141 |
| 2022-05 | 32050 | 152 | 146 |
| 2022-06 | 32057 | 149 | 143 |
| 2022-07 | 32125 | 153 | 148 |
| 2022-08 | 32297 | 159 | 154 |
| 2022-09 | 32277 | 150 | 145 |
| 2022-10 | 32371 | 150 | 145 |
| 2022-11 | 32418 | 146 | 141 |
| 2022-12 | 32488 | 150 | 145 |
| 2023-01 | 32618 | 158 | 153 |
| 2023-02 | 32739 | 176 | 171 |
| 2023-03 | 32950 | 189 | 183 |
| 2023-04 | 33187 | 209 | 203 |
| 2023-05 | 33217 | 205 | 199 |
| 2023-06 | 33300 | 216 | 210 |
| 2023-07 | 33421 | 200 | 194 |
| 2023-08 | 33529 | 197 | 189 |
| 2023-09 | 33551 | 193 | 185 |
| 2023-10 | 33582 | 192 | 184 |
| 2023-11 | 33636 | 194 | 186 |
| 2023-12 | 33719 | 204 | 196 |
| 2024-01 | 33791 | 209 | 201 |
| 2024-02 | 33953 | 221 | 212 |
| 2024-03 | 34138 | 223 | 214 |
| 2024-04 | 34319 | 224 | 215 |
| 2024-05 | 34443 | 234 | 225 |
| 2024-06 | 34511 | 241 | 232 |
| 2024-07 | 34649 | 241 | 232 |
| 2024-08 | 34741 | 235 | 226 |
| 2024-09 | 34825 | 236 | 227 |
| 2024-10 | 35035 | 236 | 227 |
| 2024-11 | 34983 | 238 | 229 |
| 2024-12 | 35445 | 236 | 227 |
| 2025-01 | 35599 | 250 | 241 |
| 2025-02 | 35727 | 260 | 251 |
| 2025-03 | 35906 | 312 | 297 |
| 2025-04 | 36000 | 310 | 295 |
| 2025-05 | 36064 | 295 | 278 |
| 2025-06 | 36138 | 318 | 302 |
| 2025-07 | 36187 | 310 | 293 |
| 2025-08 | 36227 | 313 | 290 |
| 2025-09 | 36338 | 313 | 290 |
| 2025-10 | 36514 | 314 | 291 |
| 2025-11 | 36588 | 313 | 290 |
| 2025-12 | 36734 | 303 | 282 |
| 2026-01 | 36865 | 272 | 251 |
| 2026-02 | 36890 | 289 | 269 |
| 2026-03 | 37404 | 295 | 284 |
| 2026-04 | 37480 | 300 | 289 |
| 2026-05 | 37629 | 315 | 304 |
| 2026-06 | 37779 | 313 | 302 |
| 2026-07 | 37957 | 303 | 292 |
| 2026-08 | 37995 | 300 | 289 |

Months whose sheets have no Nameplate Capacity column (MW not compared): 2015-07, 2015-08, 2015-09, 2015-10, 2015-11, 2015-12, 2016-01, 2016-02, 2016-03.

Published copies same as run copies: True (history.py True 8cd5ccfe9d3027510eb5dce4b5d4f710, test_history.py True 4009416d4407def1e51b578b6d0cb464).
