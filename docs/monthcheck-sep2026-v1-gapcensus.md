# gapcensus 0.1.0: generators that leave EIA's monthly EIA-860M workbook

Descriptive follow-up to docs/heldtrace.md; no prediction is tested. MV2 of Munim, Inc. (made with AI agents).

Workbook months read: 135 (2015-07 to 2026-09); not readable: none.

## Rebuilt changelog against the published copy

Published: https://raw.githubusercontent.com/munimtechnologies/eia860m-slip/e4ecb0d748bf7dc4738c27811e5fc07775eb72a3/data/eia860m_changelog_from_workbooks.csv.gz (1047087 bytes, md5 2c272b809794440ffcfc7b478c91b136).

Same text through 2026-08: True. Lines: published 117111, rebuilt 117111. First difference: none.

Rebuilt rows: 117756 (eia860m_changelog_from_workbooks.csv.gz).

## EIA's own file for 2026-09

Plan: append. URL: https://www.eia.gov/electricity/data/eia860m/xls/september_generator2026.xlsx. Bytes: 14013970. md5: 4c741eb77a5ccad5aca32ffe43f398af. Errors: https://www.eia.gov/electricity/data/eia860m/archive/xls/september_generator2026.xlsx: not an xlsx file (first bytes b'<!doctype html>\r').

Readable: True; problems: none. Keys: 38162. Rows appended: 646 (back 1, changed 455, first 170, left 20).

## Left events by sheet the month before, and what happened (all years)

Last month read: 2026-09. back_1: listed again the next month; back_2_12 and back_13_plus: after that many months; not_back: not listed again by the last month.

| sheet | left | back_1 | back_2_12 | back_13_plus | not_back |
|---|---|---|---|---|---|
| Operating | 442 | 42 | 20 | 1 | 379 |
| Planned | 1520 | 117 | 81 | 69 | 1253 |
| Retired | 579 | 281 | 3 | 0 | 295 |

## By year left

| year | sheet | left | back_1 | back_2_12 | back_13_plus | not_back |
|---|---|---|---|---|---|---|
| 2015 | Operating | 2 | 0 | 0 | 0 | 2 |
| 2015 | Planned | 40 | 2 | 3 | 0 | 35 |
| 2015 | Retired | 1 | 0 | 1 | 0 | 0 |
| 2016 | Operating | 30 | 1 | 1 | 0 | 28 |
| 2016 | Planned | 148 | 2 | 4 | 21 | 121 |
| 2017 | Operating | 28 | 4 | 0 | 0 | 24 |
| 2017 | Planned | 103 | 3 | 5 | 12 | 83 |
| 2017 | Retired | 241 | 1 | 2 | 0 | 238 |
| 2018 | Operating | 37 | 4 | 1 | 0 | 32 |
| 2018 | Planned | 132 | 5 | 1 | 3 | 123 |
| 2019 | Operating | 44 | 2 | 4 | 0 | 38 |
| 2019 | Planned | 115 | 18 | 5 | 9 | 83 |
| 2019 | Retired | 1 | 1 | 0 | 0 | 0 |
| 2020 | Operating | 60 | 6 | 1 | 0 | 53 |
| 2020 | Planned | 128 | 14 | 3 | 6 | 105 |
| 2020 | Retired | 4 | 2 | 0 | 0 | 2 |
| 2021 | Operating | 40 | 9 | 0 | 1 | 30 |
| 2021 | Planned | 109 | 24 | 3 | 7 | 75 |
| 2021 | Retired | 6 | 0 | 0 | 0 | 6 |
| 2022 | Operating | 57 | 7 | 3 | 0 | 47 |
| 2022 | Planned | 137 | 9 | 6 | 2 | 120 |
| 2023 | Operating | 20 | 1 | 0 | 0 | 19 |
| 2023 | Planned | 129 | 14 | 1 | 8 | 106 |
| 2023 | Retired | 3 | 0 | 0 | 0 | 3 |
| 2024 | Operating | 27 | 1 | 3 | 0 | 23 |
| 2024 | Planned | 144 | 8 | 29 | 1 | 106 |
| 2024 | Retired | 300 | 277 | 0 | 0 | 23 |
| 2025 | Operating | 41 | 2 | 1 | 0 | 38 |
| 2025 | Planned | 172 | 10 | 9 | 0 | 153 |
| 2025 | Retired | 6 | 0 | 0 | 0 | 6 |
| 2026 | Operating | 56 | 5 | 6 | 0 | 45 |
| 2026 | Planned | 163 | 8 | 12 | 0 | 143 |
| 2026 | Retired | 17 | 0 | 0 | 0 | 17 |

## Months in which generators were missing for exactly one month

pudl_in_force: PUDL's changelog has a record in force for the generator in that month (its latest record reported by then has no valid_until_date or a later one). PUDL: core_eia860m__changelog_generators.parquet, latest report 2026-08-01.

| missing month | generators | Operating | Planned | Retired | other | pudl_in_force |
|---|---|---|---|---|---|---|
| 2015-09 | 1 | 0 | 1 | 0 | 0 | 1 |
| 2015-12 | 1 | 0 | 1 | 0 | 0 | 1 |
| 2016-03 | 1 | 1 | 0 | 0 | 0 | 1 |
| 2016-04 | 1 | 0 | 1 | 0 | 0 | 1 |
| 2016-08 | 1 | 0 | 1 | 0 | 0 | 1 |
| 2017-03 | 1 | 0 | 1 | 0 | 0 | 1 |
| 2017-04 | 1 | 1 | 0 | 0 | 0 | 1 |
| 2017-05 | 4 | 3 | 0 | 1 | 0 | 4 |
| 2017-06 | 2 | 0 | 2 | 0 | 0 | 2 |
| 2018-01 | 1 | 0 | 1 | 0 | 0 | 1 |
| 2018-03 | 3 | 3 | 0 | 0 | 0 | 3 |
| 2018-05 | 1 | 1 | 0 | 0 | 0 | 1 |
| 2018-11 | 3 | 0 | 3 | 0 | 0 | 3 |
| 2018-12 | 1 | 0 | 1 | 0 | 0 | 1 |
| 2019-01 | 3 | 0 | 3 | 0 | 0 | 3 |
| 2019-02 | 1 | 1 | 0 | 0 | 0 | 1 |
| 2019-03 | 1 | 1 | 0 | 0 | 0 | 1 |
| 2019-04 | 1 | 0 | 1 | 0 | 0 | 1 |
| 2019-06 | 1 | 0 | 1 | 0 | 0 | 1 |
| 2019-10 | 2 | 0 | 2 | 0 | 0 | 2 |
| 2019-11 | 10 | 0 | 10 | 0 | 0 | 10 |
| 2019-12 | 2 | 0 | 1 | 1 | 0 | 2 |
| 2020-01 | 8 | 6 | 2 | 0 | 0 | 8 |
| 2020-02 | 3 | 0 | 3 | 0 | 0 | 3 |
| 2020-06 | 2 | 0 | 0 | 2 | 0 | 2 |
| 2020-07 | 1 | 0 | 1 | 0 | 0 | 1 |
| 2020-08 | 2 | 0 | 2 | 0 | 0 | 2 |
| 2020-09 | 1 | 0 | 1 | 0 | 0 | 1 |
| 2020-10 | 3 | 0 | 3 | 0 | 0 | 3 |
| 2020-11 | 2 | 0 | 2 | 0 | 0 | 2 |
| 2021-02 | 4 | 3 | 1 | 0 | 0 | 4 |
| 2021-03 | 3 | 1 | 2 | 0 | 0 | 3 |
| 2021-04 | 4 | 3 | 1 | 0 | 0 | 4 |
| 2021-05 | 2 | 0 | 2 | 0 | 0 | 2 |
| 2021-06 | 3 | 1 | 2 | 0 | 0 | 3 |
| 2021-07 | 13 | 1 | 12 | 0 | 0 | 13 |
| 2021-10 | 2 | 0 | 2 | 0 | 0 | 2 |
| 2021-11 | 1 | 0 | 1 | 0 | 0 | 1 |
| 2021-12 | 1 | 0 | 1 | 0 | 0 | 1 |
| 2022-01 | 2 | 2 | 0 | 0 | 0 | 2 |
| 2022-02 | 2 | 2 | 0 | 0 | 0 | 2 |
| 2022-03 | 1 | 0 | 1 | 0 | 0 | 1 |
| 2022-05 | 6 | 0 | 6 | 0 | 0 | 6 |
| 2022-06 | 4 | 3 | 1 | 0 | 0 | 4 |
| 2022-11 | 1 | 0 | 1 | 0 | 0 | 1 |
| 2023-01 | 3 | 0 | 3 | 0 | 0 | 3 |
| 2023-02 | 2 | 1 | 1 | 0 | 0 | 2 |
| 2023-03 | 1 | 0 | 1 | 0 | 0 | 1 |
| 2023-04 | 2 | 0 | 2 | 0 | 0 | 2 |
| 2023-06 | 5 | 0 | 5 | 0 | 0 | 5 |
| 2023-08 | 2 | 0 | 2 | 0 | 0 | 2 |
| 2024-01 | 1 | 0 | 1 | 0 | 0 | 1 |
| 2024-02 | 1 | 1 | 0 | 0 | 0 | 1 |
| 2024-03 | 1 | 0 | 1 | 0 | 0 | 1 |
| 2024-05 | 1 | 0 | 1 | 0 | 0 | 1 |
| 2024-06 | 1 | 0 | 1 | 0 | 0 | 1 |
| 2024-08 | 1 | 0 | 1 | 0 | 0 | 1 |
| 2024-11 | 279 | 0 | 2 | 277 | 0 | 279 |
| 2024-12 | 1 | 0 | 1 | 0 | 0 | 1 |
| 2025-01 | 1 | 0 | 1 | 0 | 0 | 1 |
| 2025-02 | 1 | 1 | 0 | 0 | 0 | 1 |
| 2025-05 | 1 | 0 | 1 | 0 | 0 | 1 |
| 2025-06 | 1 | 0 | 1 | 0 | 0 | 1 |
| 2025-07 | 1 | 1 | 0 | 0 | 0 | 1 |
| 2025-08 | 1 | 0 | 1 | 0 | 0 | 1 |
| 2025-09 | 1 | 0 | 1 | 0 | 0 | 1 |
| 2025-10 | 1 | 0 | 1 | 0 | 0 | 1 |
| 2025-11 | 4 | 0 | 4 | 0 | 0 | 4 |
| 2026-03 | 3 | 1 | 2 | 0 | 0 | 3 |
| 2026-04 | 4 | 2 | 2 | 0 | 0 | 4 |
| 2026-05 | 1 | 1 | 0 | 0 | 0 | 1 |
| 2026-06 | 3 | 0 | 3 | 0 | 0 | 3 |
| 2026-07 | 1 | 1 | 0 | 0 | 0 | 1 |
| 2026-08 | 1 | 0 | 1 | 0 | 0 | 0 |

PUDL status of all one-month gaps: closed 1, in force 439.

## November 2024

Generators that left in 2024-11: 282. Where the 2024-11 workbook lists them (every sheet, the left-out ones included):

| sheets | generators |
|---|---|
| not listed | 280 |
| Canceled or Postponed | 2 |

Outcomes of the 2024-11 left events: back_1 279, back_2_12 1, back_13_plus 0, not_back 2.

### Changelog rows of those not back in 2024-12 or not on the Retired sheet before leaving

| report_month | key | event | sheet | status | planned_month | nameplate_mw |
|---|---|---|---|---|---|---|
| 2015-07 | 59806/SOLAR | first | Planned | U | 2016-12 |  |
| 2015-12 | 59806/SOLAR | changed | Planned | L | 2018-12 |  |
| 2016-04 | 59806/SOLAR | changed | Planned | L | 2018-12 | 140.0 |
| 2017-12 | 59806/SOLAR | changed | Planned | L | 2019-12 | 140.0 |
| 2018-12 | 59806/SOLAR | left |  |  |  |  |
| 2020-02 | 59806/SOLAR | back | Planned | L | 2022-02 | 101.0 |
| 2021-03 | 59806/SOLAR | changed | Planned | L | 2023-03 | 101.0 |
| 2021-07 | 64844/TRB | first | Planned | U | 2022-06 | 1.4 |
| 2021-07 | 64844/TRS | first | Planned | U | 2022-06 | 4.0 |
| 2021-10 | 64844/TRB | changed | Planned | U | 2022-12 | 1.4 |
| 2021-10 | 64844/TRS | changed | Planned | U | 2022-12 | 4.0 |
| 2022-01 | 64844/TRB | changed | Planned | U | 2023-04 | 1.4 |
| 2022-01 | 64844/TRS | changed | Planned | U | 2023-04 | 4.0 |
| 2022-10 | 59806/SOLAR | changed | Planned | L | 2023-12 | 101.0 |
| 2022-11 | 64844/TRB | changed | Planned | U | 2023-05 | 1.4 |
| 2022-11 | 64844/TRS | changed | Planned | U | 2023-05 | 4.0 |
| 2022-12 | 64844/TRB | changed | Planned | U | 2023-06 | 1.4 |
| 2022-12 | 64844/TRS | changed | Planned | U | 2023-06 | 4.0 |
| 2023-01 | 59806/SOLAR | changed | Planned | L | 2025-11 | 101.0 |
| 2023-01 | 64844/TRB | changed | Planned | U | 2023-09 | 1.4 |
| 2023-01 | 64844/TRS | changed | Planned | U | 2023-09 | 4.0 |
| 2023-04 | 64844/TRB | changed | Planned | U | 2023-12 | 1.4 |
| 2023-04 | 64844/TRS | changed | Planned | U | 2023-12 | 4.0 |
| 2023-05 | 64844/TRB | changed | Planned | U | 2024-01 | 1.4 |
| 2023-05 | 64844/TRS | changed | Planned | U | 2024-01 | 4.0 |
| 2023-10 | 64844/TRB | changed | Planned | U | 2024-04 | 1.4 |
| 2023-10 | 64844/TRS | changed | Planned | U | 2024-04 | 4.0 |
| 2023-11 | 64844/TRB | changed | Planned | U | 2024-06 | 1.4 |
| 2023-11 | 64844/TRS | changed | Planned | U | 2024-06 | 4.0 |
| 2024-01 | 67190/FBESS | first | Planned | U | 2024-06 | 100.0 |
| 2024-03 | 67190/FBESS | changed | Planned | V | 2024-06 | 100.0 |
| 2024-04 | 64844/TRB | changed | Planned | U | 2024-07 | 1.4 |
| 2024-04 | 64844/TRS | changed | Planned | U | 2024-07 | 4.0 |
| 2024-05 | 67190/FBESS | left |  |  |  |  |
| 2024-06 | 67190/FBESS | back | Planned | V | 2024-09 | 100.0 |
| 2024-06 | 67691/731 | first | Planned | V | 2025-11 | 18.9 |
| 2024-07 | 64844/TRB | changed | Planned | U | 2024-08 | 1.4 |
| 2024-07 | 64844/TRS | changed | Planned | U | 2024-08 | 4.0 |
| 2024-08 | 64844/TRB | changed | Planned | U | 2024-10 | 1.4 |
| 2024-08 | 64844/TRS | changed | Planned | U | 2024-10 | 4.0 |
| 2024-09 | 67190/FBESS | changed | Planned | V | 2024-10 | 100.0 |
| 2024-10 | 67190/FBESS | changed | Operating | OP |  | 100.0 |
| 2024-11 | 59806/SOLAR | left |  |  |  |  |
| 2024-11 | 64844/TRB | left |  |  |  |  |
| 2024-11 | 64844/TRS | left |  |  |  |  |
| 2024-11 | 67190/FBESS | left |  |  |  |  |
| 2024-11 | 67691/731 | left |  |  |  |  |
| 2024-12 | 64844/TRB | back | Operating | OP |  | 1.4 |
| 2024-12 | 64844/TRS | back | Operating | OP |  | 4.0 |
| 2025-07 | 67691/731 | back | Planned | U | 2025-11 | 18.9 |
| 2025-08 | 67691/731 | left |  |  |  |  |
