# heldtrace 0.1.0: where the twenty-ninth test's misses come from

Descriptive follow-up to docs/history-revert.md; no prediction is tested. MV2 of Munim, Inc. (made with AI agents).

PUDL file: 2631992 bytes, file time 2026-10-15T16:11:49Z, latest report 2026-08. Workbook months read: 134.

## Disagreements by kind (should equal history-v1's counts)

| year | predicted | pudl_later | held_before | other |
|---|---|---|---|---|
| 2015 | 5 | 0 | 0 | 0 |
| 2016 | 56 | 6 | 0 | 0 |
| 2017 | 113 | 16 | 90 | 0 |
| 2018 | 217 | 16 | 205 | 0 |
| 2019 | 576 | 12 | 164 | 0 |
| 2020 | 1184 | 12 | 99 | 0 |
| 2021 | 1411 | 12 | 84 | 0 |
| 2022 | 1739 | 3 | 68 | 0 |
| 2023 | 2253 | 5 | 75 | 0 |
| 2024 | 2667 | 12 | 95 | 0 |
| 2025 | 3400 | 35 | 176 | 0 |
| 2026 | 2280 | 12 | 95 | 0 |

## What the workbook showed in the month PUDL's record in force was reported

| year | kind | workbook then | generator-months |
|---|---|---|---|
| 2015 | predicted | same | 5 |
| 2016 | predicted | same | 56 |
| 2016 | pudl_later | same | 6 |
| 2017 | predicted | same | 113 |
| 2017 | pudl_later | same | 16 |
| 2017 | held_before | same | 90 |
| 2018 | predicted | same | 217 |
| 2018 | pudl_later | same | 16 |
| 2018 | held_before | same | 205 |
| 2019 | predicted | same | 576 |
| 2019 | pudl_later | same | 12 |
| 2019 | held_before | same | 164 |
| 2020 | predicted | same | 1184 |
| 2020 | pudl_later | same | 12 |
| 2020 | held_before | same | 99 |
| 2021 | predicted | same | 1411 |
| 2021 | pudl_later | same | 12 |
| 2021 | held_before | same | 84 |
| 2022 | predicted | same | 1739 |
| 2022 | pudl_later | same | 3 |
| 2022 | held_before | same | 68 |
| 2023 | predicted | same | 2253 |
| 2023 | pudl_later | same | 5 |
| 2023 | held_before | same | 75 |
| 2024 | predicted | same | 2667 |
| 2024 | pudl_later | same | 12 |
| 2024 | held_before | same | 95 |
| 2025 | predicted | same | 3400 |
| 2025 | pudl_later | same | 35 |
| 2025 | held_before | same | 176 |
| 2026 | predicted | same | 2280 |
| 2026 | pudl_later | same | 12 |
| 2026 | held_before | same | 95 |

## "Held before": the simulation's value and the earlier PUDL record

strict: an earlier PUDL record equals the workbook's value also when a missing field equals only a missing field.

| year | simulation | strict | workbook then | generator-months |
|---|---|---|---|---|
| 2017 | equals workbook | True | same | 90 |
| 2018 | equals workbook | True | same | 205 |
| 2019 | equals workbook | True | same | 164 |
| 2020 | equals workbook | True | same | 99 |
| 2021 | equals workbook | True | same | 84 |
| 2022 | equals workbook | True | same | 68 |
| 2023 | equals workbook | True | same | 74 |
| 2023 | stale elsewhere | True | same | 1 |
| 2024 | equals workbook | True | same | 74 |
| 2024 | stale elsewhere | True | same | 21 |
| 2025 | equals workbook | True | same | 152 |
| 2025 | stale elsewhere | True | same | 24 |
| 2026 | equals workbook | True | same | 93 |
| 2026 | stale elsewhere | True | same | 2 |

## Plants with most "held before" generator-months (top 25)

| plant | generator-months |
|---|---|
| 3082 | 217 |
| 3075 | 135 |
| 3925 | 124 |
| 6175 | 109 |
| 57949 | 108 |
| 3655 | 96 |
| 56841 | 57 |
| 57299 | 54 |
| 57868 | 37 |
| 54965 | 35 |
| 10700 | 31 |
| 56666 | 27 |
| 57040 | 27 |
| 673 | 24 |
| 67909 | 16 |
| 3921 | 14 |
| 64253 | 8 |
| 54477 | 7 |
| 67347 | 7 |
| 1634 | 6 |
| 58175 | 5 |
| 58377 | 5 |
| 319 | 1 |
| 55129 | 1 |

## Rebuilt changelog rows by month

| month | first | changed | left | back |
|---|---|---|---|---|
| 2015-07 | 23988 | 0 | 0 | 0 |
| 2015-08 | 2 | 285 | 4 | 0 |
| 2015-09 | 0 | 219 | 4 | 0 |
| 2015-10 | 0 | 224 | 9 | 1 |
| 2015-11 | 135 | 322 | 5 | 0 |
| 2015-12 | 68 | 422 | 21 | 0 |
| 2016-01 | 73 | 396 | 51 | 1 |
| 2016-02 | 183 | 390 | 25 | 1 |
| 2016-03 | 114 | 283 | 9 | 1 |
| 2016-04 | 74 | 24427 | 12 | 2 |
| 2016-05 | 46 | 333 | 18 | 1 |
| 2016-06 | 45 | 309 | 11 | 2 |
| 2016-07 | 37 | 303 | 13 | 0 |
| 2016-08 | 30 | 290 | 3 | 1 |
| 2016-09 | 0 | 200 | 9 | 1 |
| 2016-10 | 0 | 209 | 0 | 0 |
| 2016-11 | 0 | 151 | 12 | 0 |
| 2016-12 | 572 | 312 | 15 | 0 |
| 2017-01 | 18 | 288 | 21 | 1 |
| 2017-02 | 165 | 262 | 3 | 0 |
| 2017-03 | 1027 | 446 | 253 | 1 |
| 2017-04 | 150 | 396 | 9 | 1 |
| 2017-05 | 34 | 360 | 34 | 5 |
| 2017-06 | 104 | 352 | 8 | 5 |
| 2017-07 | 112 | 281 | 13 | 2 |
| 2017-08 | 88 | 330 | 3 | 4 |
| 2017-09 | 118 | 359 | 4 | 1 |
| 2017-10 | 32 | 272 | 2 | 0 |
| 2017-11 | 54 | 342 | 2 | 0 |
| 2017-12 | 106 | 512 | 20 | 4 |
| 2018-01 | 85 | 386 | 18 | 0 |
| 2018-02 | 104 | 301 | 24 | 1 |
| 2018-03 | 69 | 346 | 8 | 0 |
| 2018-04 | 48 | 250 | 6 | 3 |
| 2018-05 | 72 | 241 | 8 | 0 |
| 2018-06 | 69 | 310 | 26 | 7 |
| 2018-07 | 63 | 193 | 11 | 1 |
| 2018-08 | 91 | 147 | 0 | 0 |
| 2018-09 | 118 | 188 | 9 | 0 |
| 2018-10 | 28 | 218 | 3 | 0 |
| 2018-11 | 163 | 226 | 28 | 0 |
| 2018-12 | 157 | 435 | 28 | 13 |
| 2019-01 | 213 | 472 | 38 | 1 |
| 2019-02 | 106 | 249 | 19 | 3 |
| 2019-03 | 82 | 296 | 13 | 4 |
| 2019-04 | 102 | 295 | 8 | 1 |
| 2019-05 | 124 | 239 | 8 | 3 |
| 2019-06 | 120 | 320 | 5 | 1 |
| 2019-07 | 34 | 224 | 1 | 1 |
| 2019-08 | 151 | 301 | 1 | 2 |
| 2019-09 | 134 | 301 | 8 | 0 |
| 2019-10 | 80 | 263 | 5 | 0 |
| 2019-11 | 146 | 278 | 21 | 3 |
| 2019-12 | 81 | 538 | 33 | 10 |
| 2020-01 | 148 | 591 | 30 | 7 |
| 2020-02 | 163 | 308 | 52 | 11 |
| 2020-03 | 91 | 416 | 9 | 3 |
| 2020-04 | 94 | 368 | 9 | 3 |
| 2020-05 | 87 | 318 | 4 | 0 |
| 2020-06 | 109 | 387 | 29 | 4 |
| 2020-07 | 58 | 258 | 3 | 3 |
| 2020-08 | 83 | 266 | 3 | 1 |
| 2020-09 | 86 | 244 | 6 | 2 |
| 2020-10 | 93 | 329 | 5 | 1 |
| 2020-11 | 114 | 344 | 18 | 3 |
| 2020-12 | 139 | 572 | 24 | 2 |
| 2021-01 | 142 | 555 | 37 | 1 |
| 2021-02 | 134 | 383 | 26 | 1 |
| 2021-03 | 86 | 365 | 6 | 4 |
| 2021-04 | 93 | 348 | 12 | 7 |
| 2021-05 | 59 | 342 | 4 | 4 |
| 2021-06 | 122 | 469 | 7 | 2 |
| 2021-07 | 94 | 307 | 19 | 4 |
| 2021-08 | 27 | 299 | 3 | 14 |
| 2021-09 | 374 | 345 | 3 | 0 |
| 2021-10 | 78 | 387 | 8 | 0 |
| 2021-11 | 104 | 511 | 9 | 2 |
| 2021-12 | 127 | 541 | 21 | 1 |
| 2022-01 | 164 | 612 | 28 | 2 |
| 2022-02 | 92 | 325 | 31 | 4 |
| 2022-03 | 335 | 347 | 21 | 3 |
| 2022-04 | 87 | 383 | 9 | 1 |
| 2022-05 | 48 | 340 | 17 | 0 |
| 2022-06 | 7 | 359 | 10 | 10 |
| 2022-07 | 76 | 436 | 13 | 5 |
| 2022-08 | 184 | 381 | 12 | 0 |
| 2022-09 | 0 | 328 | 20 | 0 |
| 2022-10 | 99 | 281 | 5 | 0 |
| 2022-11 | 61 | 316 | 16 | 2 |
| 2022-12 | 79 | 435 | 12 | 3 |
| 2023-01 | 147 | 607 | 21 | 4 |
| 2023-02 | 141 | 637 | 25 | 5 |
| 2023-03 | 218 | 415 | 11 | 4 |
| 2023-04 | 243 | 419 | 8 | 2 |
| 2023-05 | 51 | 434 | 23 | 2 |
| 2023-06 | 99 | 386 | 16 | 0 |
| 2023-07 | 119 | 375 | 3 | 5 |
| 2023-08 | 117 | 367 | 12 | 3 |
| 2023-09 | 21 | 341 | 1 | 2 |
| 2023-10 | 37 | 258 | 6 | 0 |
| 2023-11 | 63 | 390 | 9 | 0 |
| 2023-12 | 100 | 510 | 17 | 0 |
| 2024-01 | 122 | 390 | 50 | 0 |
| 2024-02 | 181 | 611 | 20 | 1 |
| 2024-03 | 193 | 413 | 12 | 4 |
| 2024-04 | 188 | 387 | 9 | 2 |
| 2024-05 | 137 | 478 | 18 | 5 |
| 2024-06 | 89 | 491 | 23 | 2 |
| 2024-07 | 133 | 567 | 8 | 13 |
| 2024-08 | 102 | 400 | 11 | 1 |
| 2024-09 | 92 | 339 | 9 | 1 |
| 2024-10 | 211 | 394 | 2 | 1 |
| 2024-11 | 230 | 379 | 282 | 0 |
| 2024-12 | 206 | 591 | 27 | 283 |
| 2025-01 | 168 | 636 | 20 | 6 |
| 2025-02 | 181 | 699 | 55 | 2 |
| 2025-03 | 212 | 617 | 36 | 3 |
| 2025-04 | 106 | 360 | 17 | 5 |
| 2025-05 | 65 | 415 | 4 | 3 |
| 2025-06 | 79 | 433 | 7 | 2 |
| 2025-07 | 70 | 356 | 27 | 6 |
| 2025-08 | 47 | 367 | 9 | 2 |
| 2025-09 | 119 | 326 | 9 | 1 |
| 2025-10 | 180 | 321 | 5 | 1 |
| 2025-11 | 80 | 301 | 7 | 1 |
| 2025-12 | 165 | 498 | 23 | 4 |
| 2026-01 | 157 | 467 | 26 | 0 |
| 2026-02 | 70 | 809 | 50 | 5 |
| 2026-03 | 543 | 482 | 30 | 1 |
| 2026-04 | 104 | 436 | 34 | 6 |
| 2026-05 | 168 | 420 | 25 | 6 |
| 2026-06 | 176 | 543 | 31 | 5 |
| 2026-07 | 177 | 502 | 11 | 12 |
| 2026-08 | 60 | 402 | 9 | 3 |

### 3075/11

seen before: the workbook's value equals a value the simulation took in earlier (the value in force included).

| month | sheet | workbook | simulation | seen before | PUDL in force | reported | result |
|---|---|---|---|---|---|---|---|
| 2015-07 | Operating | OA, -, - MW | OA, -, - MW | False | OA, -, - MW | 2015-07 | agree |
| 2015-08 | Operating | OA, -, - MW | OA, -, - MW | True | OA, -, - MW | 2015-07 | agree |
| 2015-09 | Operating | OA, -, - MW | OA, -, - MW | True | OA, -, - MW | 2015-07 | agree |
| 2015-10 | Operating | OA, -, - MW | OA, -, - MW | True | OA, -, - MW | 2015-07 | agree |
| 2015-11 | Operating | OA, -, - MW | OA, -, - MW | True | OA, -, - MW | 2015-07 | agree |
| 2015-12 | Operating | OA, -, - MW | OA, -, - MW | True | OA, -, - MW | 2015-12 | agree |
| 2016-01 | Operating | OA, -, - MW | OA, -, - MW | True | OA, -, - MW | 2015-12 | agree |
| 2016-02 | Operating | OA, -, - MW | OA, -, - MW | True | OA, -, - MW | 2015-12 | agree |
| 2016-03 | Operating | OA, -, - MW | OA, -, - MW | True | OA, -, - MW | 2015-12 | agree |
| 2016-04 | Operating | OA, -, 66.5 MW | OA, -, 66.5 MW | False | OA, -, 66.5 MW | 2016-04 | agree |
| 2016-05 | Operating | OA, -, 66.5 MW | OA, -, 66.5 MW | True | OA, -, 66.5 MW | 2016-04 | agree |
| 2016-06 | Operating | OA, -, 66.5 MW | OA, -, 66.5 MW | True | OA, -, 66.5 MW | 2016-04 | agree |
| 2016-07 | Operating | OA, -, 66.5 MW | OA, -, 66.5 MW | True | OA, -, 66.5 MW | 2016-07 | agree |
| 2016-08 | Operating | OA, -, 66.5 MW | OA, -, 66.5 MW | True | OA, -, 66.5 MW | 2016-07 | agree |
| 2016-09 | Operating | OA, -, 66.5 MW | OA, -, 66.5 MW | True | OA, -, 66.5 MW | 2016-07 | agree |
| 2016-10 | Operating | OA, -, 66.5 MW | OA, -, 66.5 MW | True | OA, -, 66.5 MW | 2016-07 | agree |
| 2016-11 | Operating | OA, -, 66.5 MW | OA, -, 66.5 MW | True | OA, -, 66.5 MW | 2016-07 | agree |
| 2016-12 | Operating | OA, -, 66.5 MW | OA, -, 66.5 MW | True | OA, -, 66.5 MW | 2016-07 | agree |
| 2017-01 | Operating | OA, -, 66.5 MW | OA, -, 66.5 MW | True | OA, -, 66.5 MW | 2016-07 | agree |
| 2017-02 | Operating | OA, -, 66.5 MW | OA, -, 66.5 MW | True | OA, -, 66.5 MW | 2016-07 | agree |
| 2017-03 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | False | OP, -, 66.5 MW | 2017-03 | agree |
| 2017-04 | Operating | OA, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | agree |
| 2017-05 | Operating | OA, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | agree |
| 2017-06 | Operating | OA, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | agree |
| 2017-07 | Operating | OA, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | agree |
| 2017-08 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2017-09 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2017-10 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2017-11 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2017-12 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2018-01 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2018-02 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2018-03 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2018-04 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2018-05 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2018-06 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2018-07 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2018-08 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2018-09 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2018-10 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2018-11 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2018-12 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2019-01 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2019-02 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2019-03 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2019-04 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2019-05 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2019-06 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2019-07 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2019-08 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2019-09 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2019-10 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2019-11 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2019-12 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2020-01 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2020-02 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2020-03 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2020-04 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2020-05 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2020-06 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2020-07 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2020-08 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2020-09 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2020-10 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2020-11 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2020-12 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2021-01 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2021-02 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2021-03 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2021-04 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2021-05 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2021-06 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2021-07 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2021-08 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2021-09 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2021-10 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2021-11 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2021-12 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2022-01 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2022-02 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2022-03 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2022-04 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2022-05 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2022-06 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2022-07 | Operating | OA, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | agree |
| 2022-08 | Operating | OA, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | agree |
| 2022-09 | Operating | OA, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | agree |
| 2022-10 | Operating | OA, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | agree |
| 2022-11 | Operating | OA, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | agree |
| 2022-12 | Operating | OA, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | agree |
| 2023-01 | Operating | OA, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | agree |
| 2023-02 | Operating | OA, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | agree |
| 2023-03 | Operating | OA, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | agree |
| 2023-04 | Operating | OA, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | agree |
| 2023-05 | Operating | OA, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | agree |
| 2023-06 | Operating | OA, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | agree |
| 2023-07 | Operating | OA, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | agree |
| 2023-08 | Operating | OA, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | agree |
| 2023-09 | Operating | OA, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | agree |
| 2023-10 | Operating | OA, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | agree |
| 2023-11 | Operating | OA, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | agree |
| 2023-12 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2024-01 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2024-02 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2024-03 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2024-04 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2024-05 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2024-06 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2024-07 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2024-08 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2024-09 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2024-10 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2024-11 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2024-12 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2025-01 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2025-02 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2025-03 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2025-04 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2025-05 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2025-06 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2025-07 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2025-08 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2025-09 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2025-10 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2025-11 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2025-12 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2026-01 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2026-02 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2026-03 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2026-04 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2026-05 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2026-06 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2026-07 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |
| 2026-08 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OA, -, 66.5 MW | 2017-04 | held_before |

### 3075/12

seen before: the workbook's value equals a value the simulation took in earlier (the value in force included).

| month | sheet | workbook | simulation | seen before | PUDL in force | reported | result |
|---|---|---|---|---|---|---|---|
| 2015-07 | Operating | OP, -, - MW | OP, -, - MW | False | OP, -, - MW | 2015-07 | agree |
| 2015-08 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-07 | agree |
| 2015-09 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-07 | agree |
| 2015-10 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-07 | agree |
| 2015-11 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-07 | agree |
| 2015-12 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-12 | agree |
| 2016-01 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-12 | agree |
| 2016-02 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-12 | agree |
| 2016-03 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-12 | agree |
| 2016-04 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | False | OP, -, 66.5 MW | 2016-04 | agree |
| 2016-05 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OP, -, 66.5 MW | 2016-04 | agree |
| 2016-06 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OP, -, 66.5 MW | 2016-04 | agree |
| 2016-07 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OP, -, 66.5 MW | 2016-07 | agree |
| 2016-08 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OP, -, 66.5 MW | 2016-07 | agree |
| 2016-09 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OP, -, 66.5 MW | 2016-07 | agree |
| 2016-10 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OP, -, 66.5 MW | 2016-07 | agree |
| 2016-11 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OP, -, 66.5 MW | 2016-07 | agree |
| 2016-12 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OP, -, 66.5 MW | 2016-07 | agree |
| 2017-01 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OP, -, 66.5 MW | 2016-07 | agree |
| 2017-02 | Operating | OP, -, 66.5 MW | OP, -, 66.5 MW | True | OP, -, 66.5 MW | 2016-07 | agree |
| 2017-03 | Operating | OA, -, 66.5 MW | OA, -, 66.5 MW | False | OA, -, 66.5 MW | 2017-03 | agree |
| 2017-04 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2017-05 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2017-06 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2017-07 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2017-08 | Operating | OA, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | held_before |
| 2017-09 | Operating | OA, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | held_before |
| 2017-10 | Operating | OA, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | held_before |
| 2017-11 | Operating | OA, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | held_before |
| 2017-12 | Operating | OA, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | held_before |
| 2018-01 | Operating | OA, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | held_before |
| 2018-02 | Operating | OA, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | held_before |
| 2018-03 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2018-04 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2018-05 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2018-06 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2018-07 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2018-08 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2018-09 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2018-10 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2018-11 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2018-12 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2019-01 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2019-02 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2019-03 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2019-04 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2019-05 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2019-06 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2019-07 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2019-08 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2019-09 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2019-10 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2019-11 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2019-12 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2020-01 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2020-02 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2020-03 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2020-04 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2020-05 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2020-06 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2020-07 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2020-08 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2020-09 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2020-10 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2020-11 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2020-12 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2021-01 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2021-02 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2021-03 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2021-04 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2021-05 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2021-06 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2021-07 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2021-08 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2021-09 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2021-10 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2021-11 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2021-12 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2022-01 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2022-02 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2022-03 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2022-04 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2022-05 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2022-06 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2022-07 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2022-08 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2022-09 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2022-10 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2022-11 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2022-12 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2023-01 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2023-02 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2023-03 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2023-04 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2023-05 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2023-06 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2023-07 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2023-08 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2023-09 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2023-10 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2023-11 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2023-12 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2024-01 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2024-02 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2024-03 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2024-04 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2024-05 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2024-06 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2024-07 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2024-08 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2024-09 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2024-10 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2024-11 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2024-12 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2025-01 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2025-02 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2025-03 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2025-04 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2025-05 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2025-06 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2025-07 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2025-08 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2025-09 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2025-10 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2025-11 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2025-12 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2026-01 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2026-02 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2026-03 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2026-04 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2026-05 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2026-06 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2026-07 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |
| 2026-08 | Operating | OP, -, 66.5 MW | OA, -, 66.5 MW | True | OP, -, 66.5 MW | 2017-04 | agree |

### 3075/7

seen before: the workbook's value equals a value the simulation took in earlier (the value in force included).

| month | sheet | workbook | simulation | seen before | PUDL in force | reported | result |
|---|---|---|---|---|---|---|---|
| 2015-07 | Operating | OP, -, - MW | OP, -, - MW | False | OP, -, - MW | 2015-07 | agree |
| 2015-08 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-07 | agree |
| 2015-09 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-07 | agree |
| 2015-10 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-07 | agree |
| 2015-11 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-07 | agree |
| 2015-12 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-12 | agree |
| 2016-01 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-12 | agree |
| 2016-02 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-12 | agree |
| 2016-03 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-12 | agree |
| 2016-04 | Operating | OP, -, 62.1 MW | OP, -, 62.1 MW | False | OP, -, 62.1 MW | 2016-04 | agree |
| 2016-05 | Operating | OP, -, 62.1 MW | OP, -, 62.1 MW | True | OP, -, 62.1 MW | 2016-04 | agree |
| 2016-06 | Operating | OP, -, 62.1 MW | OP, -, 62.1 MW | True | OP, -, 62.1 MW | 2016-04 | agree |
| 2016-07 | Operating | OP, -, 62.1 MW | OP, -, 62.1 MW | True | OP, -, 62.1 MW | 2016-07 | agree |
| 2016-08 | Operating | OP, -, 62.1 MW | OP, -, 62.1 MW | True | OP, -, 62.1 MW | 2016-07 | agree |
| 2016-09 | Operating | OP, -, 62.1 MW | OP, -, 62.1 MW | True | OP, -, 62.1 MW | 2016-07 | agree |
| 2016-10 | Operating | OP, -, 62.1 MW | OP, -, 62.1 MW | True | OP, -, 62.1 MW | 2016-07 | agree |
| 2016-11 | Operating | OP, -, 62.1 MW | OP, -, 62.1 MW | True | OP, -, 62.1 MW | 2016-07 | agree |
| 2016-12 | Operating | OP, -, 62.1 MW | OP, -, 62.1 MW | True | OP, -, 62.1 MW | 2016-07 | agree |
| 2017-01 | Operating | OP, -, 62.1 MW | OP, -, 62.1 MW | True | OP, -, 62.1 MW | 2016-07 | agree |
| 2017-02 | Operating | OP, -, 62.1 MW | OP, -, 62.1 MW | True | OP, -, 62.1 MW | 2016-07 | agree |
| 2017-03 | Operating | OA, -, 62.1 MW | OA, -, 62.1 MW | False | OA, -, 62.1 MW | 2017-03 | agree |
| 2017-04 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2017-05 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2017-06 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2017-07 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2017-08 | Operating | OA, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | held_before |
| 2017-09 | Operating | OA, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | held_before |
| 2017-10 | Operating | OA, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | held_before |
| 2017-11 | Operating | OA, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | held_before |
| 2017-12 | Operating | OA, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | held_before |
| 2018-01 | Operating | OA, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | held_before |
| 2018-02 | Operating | OA, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | held_before |
| 2018-03 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2018-04 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2018-05 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2018-06 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2018-07 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2018-08 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2018-09 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2018-10 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2018-11 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2018-12 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2019-01 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2019-02 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2019-03 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2019-04 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2019-05 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2019-06 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2019-07 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2019-08 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2019-09 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2019-10 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2019-11 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2019-12 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2020-01 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2020-02 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2020-03 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2020-04 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2020-05 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2020-06 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2020-07 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2020-08 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2020-09 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2020-10 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2020-11 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2020-12 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2021-01 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2021-02 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2021-03 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2021-04 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2021-05 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2021-06 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2021-07 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2021-08 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2021-09 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2021-10 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2021-11 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2021-12 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2022-01 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2022-02 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2022-03 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2022-04 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2022-05 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2022-06 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2022-07 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2022-08 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2022-09 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2022-10 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2022-11 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2022-12 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2023-01 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2023-02 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2023-03 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2023-04 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2023-05 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2023-06 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2023-07 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2023-08 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2023-09 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2023-10 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2023-11 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2023-12 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2024-01 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2024-02 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2024-03 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2024-04 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2024-05 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2024-06 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2024-07 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2024-08 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2024-09 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2024-10 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2024-11 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2024-12 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2025-01 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2025-02 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2025-03 | Operating | OA, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | held_before |
| 2025-04 | Operating | OA, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | held_before |
| 2025-05 | Operating | OA, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | held_before |
| 2025-06 | Operating | OA, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | held_before |
| 2025-07 | Operating | OA, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | held_before |
| 2025-08 | Operating | OA, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | held_before |
| 2025-09 | Operating | OA, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | held_before |
| 2025-10 | Operating | OA, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | held_before |
| 2025-11 | Operating | OA, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | held_before |
| 2025-12 | Operating | OA, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | held_before |
| 2026-01 | Operating | OA, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | held_before |
| 2026-02 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2026-03 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2026-04 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2026-05 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2026-06 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2026-07 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |
| 2026-08 | Operating | OP, -, 62.1 MW | OA, -, 62.1 MW | True | OP, -, 62.1 MW | 2017-04 | agree |

### 3082/2

seen before: the workbook's value equals a value the simulation took in earlier (the value in force included).

| month | sheet | workbook | simulation | seen before | PUDL in force | reported | result |
|---|---|---|---|---|---|---|---|
| 2015-07 | Operating | OA, -, - MW | OA, -, - MW | False | OA, -, - MW | 2015-07 | agree |
| 2015-08 | Operating | OA, -, - MW | OA, -, - MW | True | OA, -, - MW | 2015-07 | agree |
| 2015-09 | Operating | OA, -, - MW | OA, -, - MW | True | OA, -, - MW | 2015-07 | agree |
| 2015-10 | Operating | OA, -, - MW | OA, -, - MW | True | OA, -, - MW | 2015-07 | agree |
| 2015-11 | Operating | OA, -, - MW | OA, -, - MW | True | OA, -, - MW | 2015-07 | agree |
| 2015-12 | Operating | OA, -, - MW | OA, -, - MW | True | OA, -, - MW | 2015-12 | agree |
| 2016-01 | Operating | OA, -, - MW | OA, -, - MW | True | OA, -, - MW | 2015-12 | agree |
| 2016-02 | Operating | OA, -, - MW | OA, -, - MW | True | OA, -, - MW | 2015-12 | agree |
| 2016-03 | Operating | OA, -, - MW | OA, -, - MW | True | OA, -, - MW | 2015-12 | agree |
| 2016-04 | Operating | OA, -, 135.0 MW | OA, -, 135.0 MW | False | OA, -, 135.0 MW | 2016-04 | agree |
| 2016-05 | Operating | OA, -, 135.0 MW | OA, -, 135.0 MW | True | OA, -, 135.0 MW | 2016-04 | agree |
| 2016-06 | Operating | OA, -, 135.0 MW | OA, -, 135.0 MW | True | OA, -, 135.0 MW | 2016-04 | agree |
| 2016-07 | Operating | OA, -, 135.0 MW | OA, -, 135.0 MW | True | OA, -, 135.0 MW | 2016-07 | agree |
| 2016-08 | Operating | OA, -, 135.0 MW | OA, -, 135.0 MW | True | OA, -, 135.0 MW | 2016-07 | agree |
| 2016-09 | Operating | OA, -, 135.0 MW | OA, -, 135.0 MW | True | OA, -, 135.0 MW | 2016-07 | agree |
| 2016-10 | Operating | OA, -, 135.0 MW | OA, -, 135.0 MW | True | OA, -, 135.0 MW | 2016-07 | agree |
| 2016-11 | Operating | OA, -, 135.0 MW | OA, -, 135.0 MW | True | OA, -, 135.0 MW | 2016-07 | agree |
| 2016-12 | Operating | OA, -, 135.0 MW | OA, -, 135.0 MW | True | OA, -, 135.0 MW | 2016-07 | agree |
| 2017-01 | Operating | OA, -, 135.0 MW | OA, -, 135.0 MW | True | OA, -, 135.0 MW | 2016-07 | agree |
| 2017-02 | Operating | OA, -, 135.0 MW | OA, -, 135.0 MW | True | OA, -, 135.0 MW | 2016-07 | agree |
| 2017-03 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | False | OP, -, 135.0 MW | 2017-03 | agree |
| 2017-04 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | agree |
| 2017-05 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | agree |
| 2017-06 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | agree |
| 2017-07 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | agree |
| 2017-08 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2017-09 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2017-10 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2017-11 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2017-12 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2018-01 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2018-02 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2018-03 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2018-04 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2018-05 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2018-06 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2018-07 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2018-08 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2018-09 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2018-10 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2018-11 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2018-12 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2019-01 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2019-02 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | agree |
| 2019-03 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | agree |
| 2019-04 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | agree |
| 2019-05 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | agree |
| 2019-06 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | agree |
| 2019-07 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | agree |
| 2019-08 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | agree |
| 2019-09 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | agree |
| 2019-10 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | agree |
| 2019-11 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | agree |
| 2019-12 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2020-01 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2020-02 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2020-03 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2020-04 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2020-05 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2020-06 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2020-07 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2020-08 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2020-09 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2020-10 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2020-11 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2020-12 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2021-01 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2021-02 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2021-03 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2021-04 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2021-05 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2021-06 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2021-07 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2021-08 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2021-09 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2021-10 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2021-11 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2021-12 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2022-01 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2022-02 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2022-03 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2022-04 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2022-05 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2022-06 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2022-07 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2022-08 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2022-09 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2022-10 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2022-11 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2022-12 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2023-01 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2023-02 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2023-03 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2023-04 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2023-05 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2023-06 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2023-07 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2023-08 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2023-09 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2023-10 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2023-11 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2023-12 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2024-01 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2024-02 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2024-03 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2024-04 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2024-05 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2024-06 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2024-07 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2024-08 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2024-09 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2024-10 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2024-11 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2024-12 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2025-01 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2025-02 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2025-03 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2025-04 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2025-05 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2025-06 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2025-07 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2025-08 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2025-09 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2025-10 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2025-11 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2025-12 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2026-01 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2026-02 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2026-03 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2026-04 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2026-05 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2026-06 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2026-07 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |
| 2026-08 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-04 | held_before |

### 3925/1

seen before: the workbook's value equals a value the simulation took in earlier (the value in force included).

| month | sheet | workbook | simulation | seen before | PUDL in force | reported | result |
|---|---|---|---|---|---|---|---|
| 2015-07 | Operating | OA, -, - MW | OA, -, - MW | False | OA, -, - MW | 2015-07 | agree |
| 2015-08 | Operating | OA, -, - MW | OA, -, - MW | True | OA, -, - MW | 2015-07 | agree |
| 2015-09 | Operating | OA, -, - MW | OA, -, - MW | True | OA, -, - MW | 2015-07 | agree |
| 2015-10 | Operating | OA, -, - MW | OA, -, - MW | True | OA, -, - MW | 2015-07 | agree |
| 2015-11 | Operating | OA, -, - MW | OA, -, - MW | True | OA, -, - MW | 2015-07 | agree |
| 2015-12 | Operating | OA, -, - MW | OA, -, - MW | True | OA, -, - MW | 2015-12 | agree |
| 2016-01 | Operating | OA, -, - MW | OA, -, - MW | True | OA, -, - MW | 2015-12 | agree |
| 2016-02 | Operating | OA, -, - MW | OA, -, - MW | True | OA, -, - MW | 2015-12 | agree |
| 2016-03 | Operating | OA, -, - MW | OA, -, - MW | True | OA, -, - MW | 2015-12 | agree |
| 2016-04 | Operating | OA, -, 90.0 MW | OA, -, 90.0 MW | False | OA, -, 90.0 MW | 2016-04 | agree |
| 2016-05 | Operating | OA, -, 90.0 MW | OA, -, 90.0 MW | True | OA, -, 90.0 MW | 2016-04 | agree |
| 2016-06 | Operating | OA, -, 90.0 MW | OA, -, 90.0 MW | True | OA, -, 90.0 MW | 2016-04 | agree |
| 2016-07 | Operating | OA, -, 90.0 MW | OA, -, 90.0 MW | True | OA, -, 90.0 MW | 2016-07 | agree |
| 2016-08 | Operating | OA, -, 90.0 MW | OA, -, 90.0 MW | True | OA, -, 90.0 MW | 2016-07 | agree |
| 2016-09 | Operating | OA, -, 90.0 MW | OA, -, 90.0 MW | True | OA, -, 90.0 MW | 2016-07 | agree |
| 2016-10 | Operating | OA, -, 90.0 MW | OA, -, 90.0 MW | True | OA, -, 90.0 MW | 2016-07 | agree |
| 2016-11 | Operating | OA, -, 90.0 MW | OA, -, 90.0 MW | True | OA, -, 90.0 MW | 2016-07 | agree |
| 2016-12 | Operating | OA, -, 90.0 MW | OA, -, 90.0 MW | True | OA, -, 90.0 MW | 2016-07 | agree |
| 2017-01 | Operating | OA, -, 90.0 MW | OA, -, 90.0 MW | True | OA, -, 90.0 MW | 2016-07 | agree |
| 2017-02 | Operating | OA, -, 90.0 MW | OA, -, 90.0 MW | True | OA, -, 90.0 MW | 2016-07 | agree |
| 2017-03 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | False | OP, -, 90.0 MW | 2017-03 | agree |
| 2017-04 | Operating | OA, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | agree |
| 2017-05 | Operating | OA, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | agree |
| 2017-06 | Operating | OA, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | agree |
| 2017-07 | Operating | OA, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | agree |
| 2017-08 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2017-09 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2017-10 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2017-11 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2017-12 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2018-01 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2018-02 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2018-03 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2018-04 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2018-05 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2018-06 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2018-07 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2018-08 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2018-09 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2018-10 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2018-11 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2018-12 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2019-01 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2019-02 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2019-03 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2019-04 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2019-05 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2019-06 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2019-07 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2019-08 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2019-09 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2019-10 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2019-11 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2019-12 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2020-01 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2020-02 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2020-03 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2020-04 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2020-05 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2020-06 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2020-07 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2020-08 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2020-09 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2020-10 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2020-11 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2020-12 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2021-01 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2021-02 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2021-03 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2021-04 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2021-05 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2021-06 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2021-07 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2021-08 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2021-09 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2021-10 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2021-11 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2021-12 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2022-01 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2022-02 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2022-03 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2022-04 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2022-05 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2022-06 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2017-04 | held_before |
| 2022-07 | Operating | OA, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2022-07 | agree |
| 2022-08 | Operating | OA, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2022-07 | agree |
| 2022-09 | Operating | OA, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2022-07 | agree |
| 2022-10 | Operating | OA, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2022-07 | agree |
| 2022-11 | Operating | OA, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2022-07 | agree |
| 2022-12 | Operating | OA, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2022-07 | agree |
| 2023-01 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2022-07 | held_before |
| 2023-02 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2022-07 | held_before |
| 2023-03 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2022-07 | held_before |
| 2023-04 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2022-07 | held_before |
| 2023-05 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2022-07 | held_before |
| 2023-06 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2022-07 | held_before |
| 2023-07 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2022-07 | held_before |
| 2023-08 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2022-07 | held_before |
| 2023-09 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2022-07 | held_before |
| 2023-10 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2022-07 | held_before |
| 2023-11 | Operating | OP, -, 90.0 MW | OP, -, 90.0 MW | True | OA, -, 90.0 MW | 2022-07 | held_before |
| 2023-12 | Operating | OS, -, 90.0 MW | OS, -, 90.0 MW | False | OS, -, 90.0 MW | 2023-12 | agree |
| 2024-01 | Operating | OS, -, 90.0 MW | OS, -, 90.0 MW | True | OS, -, 90.0 MW | 2023-12 | agree |
| 2024-02 | Operating | OS, -, 90.0 MW | OS, -, 90.0 MW | True | OS, -, 90.0 MW | 2023-12 | agree |
| 2024-03 | Operating | OS, -, 90.0 MW | OS, -, 90.0 MW | True | OS, -, 90.0 MW | 2023-12 | agree |
| 2024-04 | Operating | OS, -, 90.0 MW | OS, -, 90.0 MW | True | OS, -, 90.0 MW | 2023-12 | agree |
| 2024-05 | Operating | OS, -, 90.0 MW | OS, -, 90.0 MW | True | OS, -, 90.0 MW | 2023-12 | agree |
| 2024-06 | Operating | OS, -, 90.0 MW | OS, -, 90.0 MW | True | OS, -, 90.0 MW | 2023-12 | agree |
| 2024-07 | Operating | OS, -, 90.0 MW | OS, -, 90.0 MW | True | OS, -, 90.0 MW | 2023-12 | agree |
| 2024-08 | Operating | OS, -, 90.0 MW | OS, -, 90.0 MW | True | OS, -, 90.0 MW | 2023-12 | agree |
| 2024-09 | Operating | OS, -, 90.0 MW | OS, -, 90.0 MW | True | OS, -, 90.0 MW | 2023-12 | agree |
| 2024-10 | Operating | OS, -, 90.0 MW | OS, -, 90.0 MW | True | OS, -, 90.0 MW | 2023-12 | agree |
| 2024-11 | Operating | OS, -, 90.0 MW | OS, -, 90.0 MW | True | OS, -, 90.0 MW | 2023-12 | agree |
| 2024-12 | Operating | OS, -, 90.0 MW | OS, -, 90.0 MW | True | OS, -, 90.0 MW | 2023-12 | agree |
| 2025-01 | Operating | OS, -, 90.0 MW | OS, -, 90.0 MW | True | OS, -, 90.0 MW | 2023-12 | agree |
| 2025-02 | Operating | OS, -, 90.0 MW | OS, -, 90.0 MW | True | OS, -, 90.0 MW | 2023-12 | agree |
| 2025-03 | Operating | OS, -, 90.0 MW | OS, -, 90.0 MW | True | OS, -, 90.0 MW | 2023-12 | agree |
| 2025-04 | Operating | OS, -, 90.0 MW | OS, -, 90.0 MW | True | OS, -, 90.0 MW | 2023-12 | agree |
| 2025-05 | Operating | OS, -, 90.0 MW | OS, -, 90.0 MW | True | OS, -, 90.0 MW | 2023-12 | agree |
| 2025-06 | Operating | OS, -, 90.0 MW | OS, -, 90.0 MW | True | OS, -, 90.0 MW | 2023-12 | agree |
| 2025-07 | Operating | OS, -, 90.0 MW | OS, -, 90.0 MW | True | OS, -, 90.0 MW | 2023-12 | agree |
| 2025-08 | Operating | OS, -, 90.0 MW | OS, -, 90.0 MW | True | OS, -, 90.0 MW | 2023-12 | agree |
| 2025-09 | Operating | OS, -, 90.0 MW | OS, -, 90.0 MW | True | OS, -, 90.0 MW | 2023-12 | agree |
| 2025-10 | Operating | OS, -, 90.0 MW | OS, -, 90.0 MW | True | OS, -, 90.0 MW | 2023-12 | agree |
| 2025-11 | Operating | OS, -, 90.0 MW | OS, -, 90.0 MW | True | OS, -, 90.0 MW | 2023-12 | agree |
| 2025-12 | Operating | OS, -, 90.0 MW | OS, -, 90.0 MW | True | OS, -, 90.0 MW | 2023-12 | agree |
| 2026-01 | Operating | OS, -, 90.0 MW | OS, -, 90.0 MW | True | OS, -, 90.0 MW | 2023-12 | agree |
| 2026-02 | Operating | OA, -, 90.0 MW | OS, -, 90.0 MW | True | OS, -, 90.0 MW | 2023-12 | predicted |
| 2026-03 | Operating | OA, -, 90.0 MW | OS, -, 90.0 MW | True | OS, -, 90.0 MW | 2023-12 | predicted |
| 2026-04 | Operating | OA, -, 90.0 MW | OS, -, 90.0 MW | True | OS, -, 90.0 MW | 2023-12 | predicted |
| 2026-05 | Operating | OA, -, 90.0 MW | OS, -, 90.0 MW | True | OS, -, 90.0 MW | 2023-12 | predicted |
| 2026-06 | Operating | OA, -, 90.0 MW | OS, -, 90.0 MW | True | OS, -, 90.0 MW | 2023-12 | predicted |
| 2026-07 | Operating | OA, -, 90.0 MW | OS, -, 90.0 MW | True | OS, -, 90.0 MW | 2023-12 | predicted |
| 2026-08 | Operating | OA, -, 90.0 MW | OS, -, 90.0 MW | True | OS, -, 90.0 MW | 2023-12 | predicted |

### 3655/1

seen before: the workbook's value equals a value the simulation took in earlier (the value in force included).

| month | sheet | workbook | simulation | seen before | PUDL in force | reported | result |
|---|---|---|---|---|---|---|---|
| 2015-07 | Operating | OP, -, - MW | OP, -, - MW | False | OP, -, - MW | 2015-07 | agree |
| 2015-08 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-07 | agree |
| 2015-09 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-07 | agree |
| 2015-10 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-07 | agree |
| 2015-11 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-07 | agree |
| 2015-12 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-12 | agree |
| 2016-01 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-12 | agree |
| 2016-02 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-12 | agree |
| 2016-03 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-12 | agree |
| 2016-04 | Operating | OP, -, 2.4 MW | OP, -, 2.4 MW | False | OP, -, 2.4 MW | 2016-04 | agree |
| 2016-05 | Operating | OP, -, 2.4 MW | OP, -, 2.4 MW | True | OP, -, 2.4 MW | 2016-04 | agree |
| 2016-06 | Operating | OP, -, 2.4 MW | OP, -, 2.4 MW | True | OP, -, 2.4 MW | 2016-04 | agree |
| 2016-07 | Operating | OP, -, 2.4 MW | OP, -, 2.4 MW | True | OP, -, 2.4 MW | 2016-07 | agree |
| 2016-08 | Operating | OP, -, 2.4 MW | OP, -, 2.4 MW | True | OP, -, 2.4 MW | 2016-07 | agree |
| 2016-09 | Operating | OP, -, 2.4 MW | OP, -, 2.4 MW | True | OP, -, 2.4 MW | 2016-07 | agree |
| 2016-10 | Operating | OP, -, 2.4 MW | OP, -, 2.4 MW | True | OP, -, 2.4 MW | 2016-07 | agree |
| 2016-11 | Operating | OP, -, 2.4 MW | OP, -, 2.4 MW | True | OP, -, 2.4 MW | 2016-07 | agree |
| 2016-12 | Operating | OP, -, 2.4 MW | OP, -, 2.4 MW | True | OP, -, 2.4 MW | 2016-07 | agree |
| 2017-01 | Operating | OP, -, 2.4 MW | OP, -, 2.4 MW | True | OP, -, 2.4 MW | 2016-07 | agree |
| 2017-02 | Operating | OP, -, 2.4 MW | OP, -, 2.4 MW | True | OP, -, 2.4 MW | 2016-07 | agree |
| 2017-03 | Operating | OS, -, 2.4 MW | OS, -, 2.4 MW | False | OS, -, 2.4 MW | 2017-03 | agree |
| 2017-04 | Operating | OS, -, 2.4 MW | OS, -, 2.4 MW | True | OS, -, 2.4 MW | 2017-03 | agree |
| 2017-05 | Operating | OS, -, 2.4 MW | OS, -, 2.4 MW | True | OS, -, 2.4 MW | 2017-03 | agree |
| 2017-06 | Operating | OS, -, 2.4 MW | OS, -, 2.4 MW | True | OS, -, 2.4 MW | 2017-03 | agree |
| 2017-07 | Operating | OP, -, 2.4 MW | OS, -, 2.4 MW | True | OP, -, 2.4 MW | 2017-07 | agree |
| 2017-08 | Operating | OP, -, 2.4 MW | OS, -, 2.4 MW | True | OP, -, 2.4 MW | 2017-07 | agree |
| 2017-09 | Operating | OS, -, 2.4 MW | OS, -, 2.4 MW | True | OP, -, 2.4 MW | 2017-07 | held_before |
| 2017-10 | Operating | OS, -, 2.4 MW | OS, -, 2.4 MW | True | OP, -, 2.4 MW | 2017-07 | held_before |
| 2017-11 | Operating | OS, -, 2.4 MW | OS, -, 2.4 MW | True | OP, -, 2.4 MW | 2017-07 | held_before |
| 2017-12 | Operating | OS, -, 2.4 MW | OS, -, 2.4 MW | True | OP, -, 2.4 MW | 2017-07 | held_before |
| 2018-01 | Operating | OS, -, 2.4 MW | OS, -, 2.4 MW | True | OP, -, 2.4 MW | 2017-07 | held_before |
| 2018-02 | Operating | OS, -, 2.4 MW | OS, -, 2.4 MW | True | OP, -, 2.4 MW | 2017-07 | held_before |
| 2018-03 | Operating | OS, -, 2.4 MW | OS, -, 2.4 MW | True | OP, -, 2.4 MW | 2017-07 | held_before |
| 2018-04 | Operating | OS, -, 2.4 MW | OS, -, 2.4 MW | True | OP, -, 2.4 MW | 2017-07 | held_before |
| 2018-05 | Operating | OS, -, 2.4 MW | OS, -, 2.4 MW | True | OP, -, 2.4 MW | 2017-07 | held_before |
| 2018-06 | Operating | OS, -, 2.4 MW | OS, -, 2.4 MW | True | OP, -, 2.4 MW | 2017-07 | held_before |
| 2018-07 | Operating | OS, -, 2.4 MW | OS, -, 2.4 MW | True | OP, -, 2.4 MW | 2017-07 | held_before |
| 2018-08 | Operating | OS, -, 2.4 MW | OS, -, 2.4 MW | True | OP, -, 2.4 MW | 2017-07 | held_before |
| 2018-09 | Operating | OS, -, 2.4 MW | OS, -, 2.4 MW | True | OP, -, 2.4 MW | 2017-07 | held_before |
| 2018-10 | Operating | OS, -, 2.4 MW | OS, -, 2.4 MW | True | OP, -, 2.4 MW | 2017-07 | held_before |
| 2018-11 | Operating | OS, -, 2.4 MW | OS, -, 2.4 MW | True | OP, -, 2.4 MW | 2017-07 | held_before |
| 2018-12 | Operating | OS, -, 2.4 MW | OS, -, 2.4 MW | True | OP, -, 2.4 MW | 2017-07 | held_before |
| 2019-01 | Operating | OS, -, 2.4 MW | OS, -, 2.4 MW | True | OP, -, 2.4 MW | 2017-07 | held_before |
| 2019-02 | Operating | OS, -, 2.4 MW | OS, -, 2.4 MW | True | OP, -, 2.4 MW | 2017-07 | held_before |
| 2019-03 | Operating | OS, -, 2.4 MW | OS, -, 2.4 MW | True | OP, -, 2.4 MW | 2017-07 | held_before |
| 2019-04 | Operating | OS, -, 2.4 MW | OS, -, 2.4 MW | True | OP, -, 2.4 MW | 2017-07 | held_before |
| 2019-05 | Operating | OS, -, 2.4 MW | OS, -, 2.4 MW | True | OP, -, 2.4 MW | 2017-07 | held_before |
| 2019-06 | Operating | OS, -, 2.4 MW | OS, -, 2.4 MW | True | OP, -, 2.4 MW | 2017-07 | held_before |
| 2019-07 | Operating | OS, -, 2.4 MW | OS, -, 2.4 MW | True | OP, -, 2.4 MW | 2017-07 | held_before |
| 2019-08 | Operating | OS, -, 2.4 MW | OS, -, 2.4 MW | True | OP, -, 2.4 MW | 2017-07 | held_before |
| 2019-09 | Operating | OS, -, 2.4 MW | OS, -, 2.4 MW | True | OP, -, 2.4 MW | 2017-07 | held_before |
| 2019-10 | Operating | OS, -, 2.4 MW | OS, -, 2.4 MW | True | OP, -, 2.4 MW | 2017-07 | held_before |
| 2019-11 | Operating | OS, -, 2.4 MW | OS, -, 2.4 MW | True | OP, -, 2.4 MW | 2017-07 | held_before |
| 2019-12 | Operating | OS, -, 2.4 MW | OS, -, 2.4 MW | True | OP, -, 2.4 MW | 2017-07 | held_before |
| 2020-01 | Operating | OS, -, 2.4 MW | OS, -, 2.4 MW | True | OP, -, 2.4 MW | 2017-07 | held_before |
| 2020-02 | Operating | OS, -, 2.4 MW | OS, -, 2.4 MW | True | OP, -, 2.4 MW | 2017-07 | held_before |
| 2020-03 | Operating | OS, -, 2.4 MW | OS, -, 2.4 MW | True | OP, -, 2.4 MW | 2017-07 | held_before |
| 2020-04 | Operating | OS, -, 2.4 MW | OS, -, 2.4 MW | True | OP, -, 2.4 MW | 2017-07 | held_before |
| 2020-05 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | False | RE, -, 2.4 MW | 2020-05 | agree |
| 2020-06 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2020-07 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2020-08 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2020-09 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2020-10 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2020-11 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2020-12 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2021-01 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2021-02 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2021-03 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2021-04 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2021-05 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2021-06 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2021-07 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2021-08 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2021-09 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2021-10 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2021-11 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2021-12 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2022-01 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2022-02 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2022-03 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2022-04 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2022-05 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2022-06 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2022-07 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2022-08 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2022-09 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2022-10 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2022-11 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2022-12 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2023-01 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2023-02 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2023-03 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2023-04 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2023-05 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2023-06 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2023-07 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2023-08 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2023-09 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2023-10 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2023-11 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2023-12 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2024-01 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2024-02 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2024-03 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2024-04 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2024-05 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2024-06 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2024-07 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2024-08 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2024-09 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2024-10 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2024-11 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2024-12 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2025-01 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2025-02 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2025-03 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2025-04 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2025-05 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2025-06 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2025-07 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2025-08 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2025-09 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2025-10 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2025-11 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2025-12 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2026-01 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2026-02 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2026-03 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2026-04 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2026-05 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2026-06 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2026-07 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |
| 2026-08 | Retired | RE, -, 2.4 MW | RE, -, 2.4 MW | True | RE, -, 2.4 MW | 2020-05 | agree |

### 57299/1

seen before: the workbook's value equals a value the simulation took in earlier (the value in force included).

| month | sheet | workbook | simulation | seen before | PUDL in force | reported | result |
|---|---|---|---|---|---|---|---|
| 2015-07 | Operating | OP, -, - MW | OP, -, - MW | False | OP, -, - MW | 2015-07 | agree |
| 2015-08 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-07 | agree |
| 2015-09 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-07 | agree |
| 2015-10 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-07 | agree |
| 2015-11 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-07 | agree |
| 2015-12 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-12 | agree |
| 2016-01 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-12 | agree |
| 2016-02 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-12 | agree |
| 2016-03 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-12 | agree |
| 2016-04 | Operating | OP, -, 115.8 MW | OP, -, 115.8 MW | False | OP, -, 115.8 MW | 2016-04 | agree |
| 2016-05 | Operating | OP, -, 115.8 MW | OP, -, 115.8 MW | True | OP, -, 115.8 MW | 2016-04 | agree |
| 2016-06 | Operating | OP, -, 115.8 MW | OP, -, 115.8 MW | True | OP, -, 115.8 MW | 2016-04 | agree |
| 2016-07 | Operating | OP, -, 115.8 MW | OP, -, 115.8 MW | True | OP, -, 115.8 MW | 2016-07 | agree |
| 2016-08 | Operating | OP, -, 115.8 MW | OP, -, 115.8 MW | True | OP, -, 115.8 MW | 2016-07 | agree |
| 2016-09 | Operating | OP, -, 115.8 MW | OP, -, 115.8 MW | True | OP, -, 115.8 MW | 2016-07 | agree |
| 2016-10 | Operating | OP, -, 115.8 MW | OP, -, 115.8 MW | True | OP, -, 115.8 MW | 2016-07 | agree |
| 2016-11 | Operating | OP, -, 115.8 MW | OP, -, 115.8 MW | True | OP, -, 115.8 MW | 2016-07 | agree |
| 2016-12 | Operating | OP, -, 115.8 MW | OP, -, 115.8 MW | True | OP, -, 115.8 MW | 2016-07 | agree |
| 2017-01 | Operating | OP, -, 115.8 MW | OP, -, 115.8 MW | True | OP, -, 115.8 MW | 2016-07 | agree |
| 2017-02 | Operating | OP, -, 115.8 MW | OP, -, 115.8 MW | True | OP, -, 115.8 MW | 2016-07 | agree |
| 2017-03 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | False | OP, -, 111.0 MW | 2017-03 | agree |
| 2017-04 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 111.0 MW | 2017-03 | agree |
| 2017-05 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 111.0 MW | 2017-03 | agree |
| 2017-06 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 111.0 MW | 2017-03 | agree |
| 2017-07 | Operating | OP, -, 115.8 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | agree |
| 2017-08 | Operating | OP, -, 115.8 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | agree |
| 2017-09 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2017-10 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2017-11 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2017-12 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2018-01 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2018-02 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2018-03 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2018-04 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2018-05 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2018-06 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2018-07 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2018-08 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2018-09 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2018-10 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2018-11 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2018-12 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2019-01 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2019-02 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2019-03 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2019-04 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2019-05 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2019-06 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2019-07 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2019-08 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2019-09 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2019-10 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2019-11 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2019-12 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2020-01 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2020-02 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2020-03 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2020-04 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2020-05 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2020-06 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2020-07 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2020-08 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2020-09 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2020-10 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2020-11 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2020-12 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2021-01 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2021-02 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2021-03 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2021-04 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2021-05 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2021-06 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2021-07 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2021-08 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2021-09 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2021-10 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2021-11 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2021-12 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2022-01 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2022-02 | Operating | OP, -, 111.0 MW | OP, -, 111.0 MW | True | OP, -, 115.8 MW | 2017-07 | held_before |
| 2022-03 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | False | OP, -, 129.5 MW | 2022-03 | agree |
| 2022-04 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2022-05 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2022-06 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2022-07 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2022-08 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2022-09 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2022-10 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2022-11 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2022-12 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2023-01 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2023-02 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2023-03 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2023-04 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2023-05 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2023-06 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2023-07 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2023-08 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2023-09 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2023-10 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2023-11 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2023-12 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2024-01 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2024-02 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2024-03 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2024-04 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2024-05 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2024-06 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2024-07 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2024-08 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2024-09 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2024-10 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2024-11 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2024-12 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2025-01 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2025-02 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2025-03 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2025-04 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2025-05 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2025-06 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2025-07 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2025-08 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2025-09 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2025-10 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2025-11 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2025-12 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2026-01 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2026-02 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2026-03 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2026-04 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2026-05 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2026-06 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2026-07 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |
| 2026-08 | Operating | OP, -, 129.5 MW | OP, -, 129.5 MW | True | OP, -, 129.5 MW | 2022-03 | agree |

### 6175/2

seen before: the workbook's value equals a value the simulation took in earlier (the value in force included).

| month | sheet | workbook | simulation | seen before | PUDL in force | reported | result |
|---|---|---|---|---|---|---|---|
| 2015-07 | Operating | OA, -, - MW | OA, -, - MW | False | OA, -, - MW | 2015-07 | agree |
| 2015-08 | Operating | OA, -, - MW | OA, -, - MW | True | OA, -, - MW | 2015-07 | agree |
| 2015-09 | Operating | OA, -, - MW | OA, -, - MW | True | OA, -, - MW | 2015-07 | agree |
| 2015-10 | Operating | OA, -, - MW | OA, -, - MW | True | OA, -, - MW | 2015-07 | agree |
| 2015-11 | Operating | OA, -, - MW | OA, -, - MW | True | OA, -, - MW | 2015-07 | agree |
| 2015-12 | Operating | OA, -, - MW | OA, -, - MW | True | OA, -, - MW | 2015-12 | agree |
| 2016-01 | Operating | OA, -, - MW | OA, -, - MW | True | OA, -, - MW | 2015-12 | agree |
| 2016-02 | Operating | OA, -, - MW | OA, -, - MW | True | OA, -, - MW | 2015-12 | agree |
| 2016-03 | Operating | OA, -, - MW | OA, -, - MW | True | OA, -, - MW | 2015-12 | agree |
| 2016-04 | Operating | OA, -, 135.0 MW | OA, -, 135.0 MW | False | OA, -, 135.0 MW | 2016-04 | agree |
| 2016-05 | Operating | OA, -, 135.0 MW | OA, -, 135.0 MW | True | OA, -, 135.0 MW | 2016-04 | agree |
| 2016-06 | Operating | OA, -, 135.0 MW | OA, -, 135.0 MW | True | OA, -, 135.0 MW | 2016-04 | agree |
| 2016-07 | Operating | OA, -, 135.0 MW | OA, -, 135.0 MW | True | OA, -, 135.0 MW | 2016-07 | agree |
| 2016-08 | Operating | OA, -, 135.0 MW | OA, -, 135.0 MW | True | OA, -, 135.0 MW | 2016-07 | agree |
| 2016-09 | Operating | OA, -, 135.0 MW | OA, -, 135.0 MW | True | OA, -, 135.0 MW | 2016-07 | agree |
| 2016-10 | Operating | OA, -, 135.0 MW | OA, -, 135.0 MW | True | OA, -, 135.0 MW | 2016-07 | agree |
| 2016-11 | Operating | OA, -, 135.0 MW | OA, -, 135.0 MW | True | OA, -, 135.0 MW | 2016-07 | agree |
| 2016-12 | Operating | OA, -, 135.0 MW | OA, -, 135.0 MW | True | OA, -, 135.0 MW | 2016-07 | agree |
| 2017-01 | Operating | OA, -, 135.0 MW | OA, -, 135.0 MW | True | OA, -, 135.0 MW | 2016-07 | agree |
| 2017-02 | Operating | OA, -, 135.0 MW | OA, -, 135.0 MW | True | OA, -, 135.0 MW | 2016-07 | agree |
| 2017-03 | Operating | OA, -, 135.0 MW | OA, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-03 | agree |
| 2017-04 | Operating | OA, -, 135.0 MW | OA, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-03 | agree |
| 2017-05 | Operating | OA, -, 135.0 MW | OA, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-03 | agree |
| 2017-06 | Operating | OA, -, 135.0 MW | OA, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-03 | agree |
| 2017-07 | Operating | OA, -, 135.0 MW | OA, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-03 | agree |
| 2017-08 | Operating | OA, -, 135.0 MW | OA, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-03 | agree |
| 2017-09 | Operating | OA, -, 135.0 MW | OA, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-03 | agree |
| 2017-10 | Operating | OA, -, 135.0 MW | OA, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-03 | agree |
| 2017-11 | Operating | OA, -, 135.0 MW | OA, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-03 | agree |
| 2017-12 | Operating | OA, -, 135.0 MW | OA, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-03 | agree |
| 2018-01 | Operating | OA, -, 135.0 MW | OA, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-03 | agree |
| 2018-02 | Operating | OA, -, 135.0 MW | OA, -, 135.0 MW | True | OA, -, 135.0 MW | 2017-03 | agree |
| 2018-03 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | False | OP, -, 135.0 MW | 2018-03 | agree |
| 2018-04 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OP, -, 135.0 MW | 2018-03 | agree |
| 2018-05 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OP, -, 135.0 MW | 2018-03 | agree |
| 2018-06 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OP, -, 135.0 MW | 2018-03 | agree |
| 2018-07 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OP, -, 135.0 MW | 2018-03 | agree |
| 2018-08 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OP, -, 135.0 MW | 2018-03 | agree |
| 2018-09 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OP, -, 135.0 MW | 2018-03 | agree |
| 2018-10 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OP, -, 135.0 MW | 2018-03 | agree |
| 2018-11 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OP, -, 135.0 MW | 2018-03 | agree |
| 2018-12 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OP, -, 135.0 MW | 2018-03 | agree |
| 2019-01 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OP, -, 135.0 MW | 2018-03 | agree |
| 2019-02 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OP, -, 135.0 MW | 2018-03 | agree |
| 2019-03 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OP, -, 135.0 MW | 2018-03 | agree |
| 2019-04 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OP, -, 135.0 MW | 2018-03 | agree |
| 2019-05 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OP, -, 135.0 MW | 2018-03 | agree |
| 2019-06 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OP, -, 135.0 MW | 2018-03 | agree |
| 2019-07 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OP, -, 135.0 MW | 2018-03 | agree |
| 2019-08 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OP, -, 135.0 MW | 2018-03 | agree |
| 2019-09 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OP, -, 135.0 MW | 2018-03 | agree |
| 2019-10 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OP, -, 135.0 MW | 2018-03 | agree |
| 2019-11 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OP, -, 135.0 MW | 2018-03 | agree |
| 2019-12 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | agree |
| 2020-01 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | agree |
| 2020-02 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | agree |
| 2020-03 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | agree |
| 2020-04 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | agree |
| 2020-05 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | agree |
| 2020-06 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | agree |
| 2020-07 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | agree |
| 2020-08 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | agree |
| 2020-09 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | agree |
| 2020-10 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | agree |
| 2020-11 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | agree |
| 2020-12 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | agree |
| 2021-01 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2021-02 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2021-03 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2021-04 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2021-05 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2021-06 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2021-07 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2021-08 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2021-09 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2021-10 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2021-11 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2021-12 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2022-01 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2022-02 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2022-03 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2022-04 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2022-05 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2022-06 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2022-07 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2022-08 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2022-09 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2022-10 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2022-11 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2022-12 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2023-01 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2023-02 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2023-03 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2023-04 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2023-05 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2023-06 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2023-07 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2023-08 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2023-09 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2023-10 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2023-11 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2023-12 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | agree |
| 2024-01 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | agree |
| 2024-02 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | agree |
| 2024-03 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | agree |
| 2024-04 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | agree |
| 2024-05 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | agree |
| 2024-06 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | agree |
| 2024-07 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | agree |
| 2024-08 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | agree |
| 2024-09 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | agree |
| 2024-10 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | agree |
| 2024-11 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | agree |
| 2024-12 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | agree |
| 2025-01 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | agree |
| 2025-02 | Operating | OA, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | agree |
| 2025-03 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2025-04 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2025-05 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2025-06 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2025-07 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2025-08 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2025-09 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2025-10 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2025-11 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2025-12 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2026-01 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2026-02 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2026-03 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2026-04 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2026-05 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2026-06 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2026-07 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |
| 2026-08 | Operating | OP, -, 135.0 MW | OP, -, 135.0 MW | True | OA, -, 135.0 MW | 2019-12 | held_before |

### 3921/3

seen before: the workbook's value equals a value the simulation took in earlier (the value in force included).

| month | sheet | workbook | simulation | seen before | PUDL in force | reported | result |
|---|---|---|---|---|---|---|---|
| 2015-07 | Operating | OP, -, - MW | OP, -, - MW | False | OP, -, - MW | 2015-07 | agree |
| 2015-08 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-07 | agree |
| 2015-09 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-07 | agree |
| 2015-10 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-07 | agree |
| 2015-11 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-07 | agree |
| 2015-12 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-12 | agree |
| 2016-01 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-12 | agree |
| 2016-02 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-12 | agree |
| 2016-03 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-12 | agree |
| 2016-04 | Operating | OP, -, 88.2 MW | OP, -, 88.2 MW | False | OP, -, 88.2 MW | 2016-04 | agree |
| 2016-05 | Operating | OP, -, 88.2 MW | OP, -, 88.2 MW | True | OP, -, 88.2 MW | 2016-04 | agree |
| 2016-06 | Operating | OP, -, 88.2 MW | OP, -, 88.2 MW | True | OP, -, 88.2 MW | 2016-04 | agree |
| 2016-07 | Operating | OP, -, 88.2 MW | OP, -, 88.2 MW | True | OP, -, 88.2 MW | 2016-07 | agree |
| 2016-08 | Operating | OP, -, 88.2 MW | OP, -, 88.2 MW | True | OP, -, 88.2 MW | 2016-07 | agree |
| 2016-09 | Operating | OP, -, 88.2 MW | OP, -, 88.2 MW | True | OP, -, 88.2 MW | 2016-07 | agree |
| 2016-10 | Operating | OP, -, 88.2 MW | OP, -, 88.2 MW | True | OP, -, 88.2 MW | 2016-07 | agree |
| 2016-11 | Operating | OP, -, 88.2 MW | OP, -, 88.2 MW | True | OP, -, 88.2 MW | 2016-07 | agree |
| 2016-12 | Operating | OP, -, 88.2 MW | OP, -, 88.2 MW | True | OP, -, 88.2 MW | 2016-07 | agree |
| 2017-01 | Operating | OP, -, 88.2 MW | OP, -, 88.2 MW | True | OP, -, 88.2 MW | 2016-07 | agree |
| 2017-02 | Operating | OP, -, 88.2 MW | OP, -, 88.2 MW | True | OP, -, 88.2 MW | 2016-07 | agree |
| 2017-03 | Operating | OA, -, 88.2 MW | OA, -, 88.2 MW | False | OA, -, 88.2 MW | 2017-03 | agree |
| 2017-04 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2017-05 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2017-06 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2017-07 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2017-08 | Operating | OA, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | agree |
| 2017-09 | Operating | OA, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | agree |
| 2017-10 | Operating | OA, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | agree |
| 2017-11 | Operating | OA, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | agree |
| 2017-12 | Operating | OA, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | agree |
| 2018-01 | Operating | OA, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | agree |
| 2018-02 | Operating | OA, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | agree |
| 2018-03 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2018-04 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2018-05 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2018-06 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2018-07 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2018-08 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2018-09 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2018-10 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2018-11 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2018-12 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2019-01 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2019-02 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2019-03 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2019-04 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2019-05 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2019-06 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2019-07 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2019-08 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2019-09 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2019-10 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2019-11 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2019-12 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2020-01 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2020-02 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2020-03 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2020-04 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2020-05 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2020-06 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2020-07 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2020-08 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2020-09 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2020-10 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2020-11 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2020-12 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2021-01 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2021-02 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2021-03 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2021-04 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2021-05 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2021-06 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2021-07 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2021-08 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2021-09 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2021-10 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2021-11 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2021-12 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2022-01 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2022-02 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2022-03 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2022-04 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2022-05 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2022-06 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2022-07 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2022-08 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2022-09 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2022-10 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2022-11 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2022-12 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2023-01 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2023-02 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2023-03 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2023-04 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2023-05 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2023-06 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2023-07 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2023-08 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2023-09 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2023-10 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2023-11 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2023-12 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2024-01 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2024-02 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2024-03 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2024-04 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2024-05 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2024-06 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2024-07 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2024-08 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2024-09 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2024-10 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2024-11 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2024-12 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2025-01 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2025-02 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2025-03 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2025-04 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2025-05 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2025-06 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2025-07 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2025-08 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2025-09 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2025-10 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2025-11 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2025-12 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2026-01 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2026-02 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2026-03 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2026-04 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2026-05 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2026-06 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2026-07 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |
| 2026-08 | Operating | OP, -, 88.2 MW | OA, -, 88.2 MW | True | OA, -, 88.2 MW | 2017-03 | predicted |

### 1134/5

seen before: the workbook's value equals a value the simulation took in earlier (the value in force included).

| month | sheet | workbook | simulation | seen before | PUDL in force | reported | result |
|---|---|---|---|---|---|---|---|
| 2015-07 | Operating | SB, -, - MW | SB, -, - MW | False | SB, -, - MW | 2015-07 | agree |
| 2015-08 | Operating | SB, -, - MW | SB, -, - MW | True | SB, -, - MW | 2015-07 | agree |
| 2015-09 | Operating | SB, -, - MW | SB, -, - MW | True | SB, -, - MW | 2015-07 | agree |
| 2015-10 | Operating | SB, -, - MW | SB, -, - MW | True | SB, -, - MW | 2015-07 | agree |
| 2015-11 | Operating | SB, -, - MW | SB, -, - MW | True | SB, -, - MW | 2015-07 | agree |
| 2015-12 | Operating | SB, -, - MW | SB, -, - MW | True | SB, -, - MW | 2015-12 | agree |
| 2016-01 | Operating | SB, -, - MW | SB, -, - MW | True | SB, -, - MW | 2015-12 | agree |
| 2016-02 | Operating | SB, -, - MW | SB, -, - MW | True | SB, -, - MW | 2015-12 | agree |
| 2016-03 | Operating | SB, -, - MW | SB, -, - MW | True | SB, -, - MW | 2016-03 | agree |
| 2016-04 | Operating | SB, -, 2.8 MW | SB, -, 2.8 MW | False | SB, -, 2.8 MW | 2016-04 | agree |
| 2016-05 | Operating | SB, -, 2.8 MW | SB, -, 2.8 MW | True | SB, -, 2.8 MW | 2016-04 | agree |
| 2016-06 | Operating | SB, -, 2.8 MW | SB, -, 2.8 MW | True | SB, -, 2.8 MW | 2016-04 | agree |
| 2016-07 | Operating | SB, -, 2.8 MW | SB, -, 2.8 MW | True | SB, -, 2.8 MW | 2016-07 | agree |
| 2016-08 | Operating | SB, -, 2.8 MW | SB, -, 2.8 MW | True | SB, -, 2.8 MW | 2016-07 | agree |
| 2016-09 | Operating | SB, -, 2.8 MW | SB, -, 2.8 MW | True | SB, -, 2.8 MW | 2016-07 | agree |
| 2016-10 | Operating | SB, -, 2.8 MW | SB, -, 2.8 MW | True | SB, -, 2.8 MW | 2016-07 | agree |
| 2016-11 | Operating | SB, -, 2.8 MW | SB, -, 2.8 MW | True | SB, -, 2.8 MW | 2016-07 | agree |
| 2016-12 | Operating | SB, -, 2.8 MW | SB, -, 2.8 MW | True | SB, -, 2.8 MW | 2016-07 | agree |
| 2017-01 | Operating | OP, -, 2.8 MW | OP, -, 2.8 MW | False | OP, -, 2.8 MW | 2017-01 | agree |
| 2017-02 | Operating | OP, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | agree |
| 2017-03 | Operating | OP, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | agree |
| 2017-04 | Operating | OP, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | agree |
| 2017-05 | Operating | OP, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | agree |
| 2017-06 | Operating | OP, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | agree |
| 2017-07 | Operating | OP, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | agree |
| 2017-08 | Operating | OP, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | agree |
| 2017-09 | Operating | OP, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | agree |
| 2017-10 | Operating | OP, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | agree |
| 2017-11 | Operating | OP, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | agree |
| 2017-12 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2018-01 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2018-02 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2018-03 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2018-04 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2018-05 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2018-06 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2018-07 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2018-08 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2018-09 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2018-10 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2018-11 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2018-12 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2019-01 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2019-02 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2019-03 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2019-04 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2019-05 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2019-06 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2019-07 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2019-08 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2019-09 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2019-10 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2019-11 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2019-12 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2020-01 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2020-02 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2020-03 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2020-04 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2020-05 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2020-06 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2020-07 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2020-08 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2020-09 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2020-10 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2020-11 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2020-12 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2021-01 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2021-02 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2021-03 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2021-04 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2021-05 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2021-06 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2021-07 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2021-08 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2021-09 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2021-10 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2021-11 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2021-12 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2022-01 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2022-02 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2022-03 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2022-04 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2022-05 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2022-06 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2022-07 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2022-08 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2022-09 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2022-10 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2022-11 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2022-12 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2023-01 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2023-02 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2023-03 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2023-04 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2023-05 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2023-06 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2023-07 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2023-08 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2023-09 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2023-10 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2023-11 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2023-12 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2024-01 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2024-02 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2024-03 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2024-04 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2024-05 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2024-06 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2024-07 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2024-08 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2024-09 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2024-10 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2024-11 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2024-12 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2025-01 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2025-02 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2025-03 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2025-04 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2025-05 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2025-06 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2025-07 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2025-08 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2025-09 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2025-10 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2025-11 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2025-12 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2026-01 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2026-02 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2026-03 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2026-04 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2026-05 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2026-06 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2026-07 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |
| 2026-08 | Operating | SB, -, 2.8 MW | OP, -, 2.8 MW | True | OP, -, 2.8 MW | 2017-01 | predicted |

### 59485/PV2

seen before: the workbook's value equals a value the simulation took in earlier (the value in force included).

| month | sheet | workbook | simulation | seen before | PUDL in force | reported | result |
|---|---|---|---|---|---|---|---|
| 2015-07 | Operating | OP, -, - MW | OP, -, - MW | False | OP, -, - MW | 2015-07 | agree |
| 2015-08 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-07 | agree |
| 2015-09 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-07 | agree |
| 2015-10 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-07 | agree |
| 2015-11 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-07 | agree |
| 2015-12 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-12 | agree |
| 2016-01 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-12 | agree |
| 2016-02 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-12 | agree |
| 2016-03 | Operating | OP, -, - MW | OP, -, - MW | True | OP, -, - MW | 2015-12 | agree |
| 2016-04 | Operating | OP, -, 1.2 MW | OP, -, 1.2 MW | False | OP, -, 1.2 MW | 2016-04 | agree |
| 2016-05 | Operating | OP, -, 1.2 MW | OP, -, 1.2 MW | True | OP, -, 1.2 MW | 2016-04 | agree |
| 2016-06 | Operating | OP, -, 1.2 MW | OP, -, 1.2 MW | True | OP, -, 1.2 MW | 2016-04 | agree |
| 2016-07 | Operating | OP, -, 1.2 MW | OP, -, 1.2 MW | True | OP, -, 1.2 MW | 2016-07 | agree |
| 2016-08 | Operating | OP, -, 1.2 MW | OP, -, 1.2 MW | True | OP, -, 1.2 MW | 2016-07 | agree |
| 2016-09 | Operating | OP, -, 1.2 MW | OP, -, 1.2 MW | True | OP, -, 1.2 MW | 2016-07 | agree |
| 2016-10 | Operating | OP, -, 1.2 MW | OP, -, 1.2 MW | True | OP, -, 1.2 MW | 2016-07 | agree |
| 2016-11 | Operating | OP, -, 1.2 MW | OP, -, 1.2 MW | True | OP, -, 1.2 MW | 2016-07 | agree |
| 2016-12 | Operating | OP, -, 1.2 MW | OP, -, 1.2 MW | True | OP, -, 1.2 MW | 2016-07 | agree |
| 2017-01 | Operating | OP, -, 1.2 MW | OP, -, 1.2 MW | True | OP, -, 1.2 MW | 2016-07 | agree |
| 2017-02 | Operating | OP, -, 1.2 MW | OP, -, 1.2 MW | True | OP, -, 1.2 MW | 2016-07 | agree |
| 2017-03 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | False | OP, -, 2.2 MW | 2017-03 | agree |
| 2017-04 | Operating | OP, -, 1.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | agree |
| 2017-05 | Operating | OP, -, 1.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | agree |
| 2017-06 | Operating | OP, -, 1.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | agree |
| 2017-07 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2017-08 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2017-09 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2017-10 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2017-11 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2017-12 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2018-01 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2018-02 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2018-03 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2018-04 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2018-05 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2018-06 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2018-07 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2018-08 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2018-09 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2018-10 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2018-11 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2018-12 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2019-01 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2019-02 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2019-03 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2019-04 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2019-05 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2019-06 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2019-07 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2019-08 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2019-09 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2019-10 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2019-11 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2019-12 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2020-01 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2020-02 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2020-03 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2020-04 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2020-05 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2020-06 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2020-07 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2020-08 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2020-09 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2020-10 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2020-11 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2020-12 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2021-01 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2021-02 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2021-03 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2021-04 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2021-05 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2021-06 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2021-07 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2021-08 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2021-09 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2021-10 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2021-11 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2021-12 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2022-01 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2022-02 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2022-03 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 1.2 MW | 2017-04 | pudl_later |
| 2022-04 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 2.2 MW | 2022-04 | agree |
| 2022-05 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 2.2 MW | 2022-04 | agree |
| 2022-06 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 2.2 MW | 2022-04 | agree |
| 2022-07 | Operating | OP, -, 2.2 MW | OP, -, 2.2 MW | True | OP, -, 2.2 MW | 2022-04 | agree |
| 2022-08 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | False | OP, -, 1.0 MW | 2022-08 | agree |
| 2022-09 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2022-08 | agree |
| 2022-10 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2022-08 | agree |
| 2022-11 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2022-08 | agree |
| 2022-12 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2022-08 | agree |
| 2023-01 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2022-08 | agree |
| 2023-02 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2023-03 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2023-04 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2023-05 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2023-06 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2023-07 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2023-08 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2023-09 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2023-10 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2023-11 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2023-12 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2024-01 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2024-02 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2024-03 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2024-04 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2024-05 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2024-06 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2024-07 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2024-08 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2024-09 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2024-10 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2024-11 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2024-12 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2025-01 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2025-02 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2025-03 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2025-04 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2025-05 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2025-06 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2025-07 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2025-08 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2025-09 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2025-10 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2025-11 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2025-12 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2026-01 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2026-02 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2026-03 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2026-04 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2026-05 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2026-06 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2026-07 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |
| 2026-08 | Operating | OP, -, 1.0 MW | OP, -, 1.0 MW | True | OP, -, 1.0 MW | 2023-02 | agree |

PUDL's full rows for these generators: heldtrace_pudl_rows.csv.
