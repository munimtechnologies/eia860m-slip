# revert 0.1.0: does PUDL's EIA-860M changelog drop a value that comes back?

Twenty-eighth test, pre-registered in docs/changelog-revert-preregistration.md. MV2 of Munim, Inc. (made with AI agents).

Pre-registration live: True (checks 1, at 2026-10-21T21:35:21Z; commit f64de4c06f191c57b34b5cf775ed1d8f4838eadb).

## Checks

| check | ok | detail |
|---|---|---|
| C1 workbooks | True | zip md5 380a9824a20be96d182fea793c299e91; months read 8 of 8 |
| C2 PUDL through August | True | latest report 2026-08 |
| C3 links | True | disagree 2395, simulation stale 2893 (each at least 100) |

## Predictions

Scored: 4 of 4 predictions held.

| prediction | bar | value | held |
|---|---|---|---|
| P1 repeats in the changelog | 0 | 0 | True |
| P2 coverage | 0.90 | 1.0 (2395 of 2395) | True |
| P3 precision | 0.50 | 0.8279 (2395 of 2893) | True |
| P4 named generators | both | 69338/LEAKY True, 69372/KNOXS True | True |

Generator-months in both sources: 299999.

## Disagreements by month

| month | in both | predicted | PUDL takes it later | PUDL held it before | other |
|---|---|---|---|---|---|
| 2026-01 | 36865 | 273 | 0 | 0 | 0 |
| 2026-02 | 36890 | 290 | 0 | 0 | 0 |
| 2026-03 | 37404 | 296 | 0 | 0 | 0 |
| 2026-04 | 37480 | 301 | 0 | 0 | 0 |
| 2026-05 | 37629 | 316 | 0 | 0 | 0 |
| 2026-06 | 37779 | 314 | 0 | 0 | 0 |
| 2026-07 | 37957 | 304 | 0 | 0 | 0 |
| 2026-08 | 37995 | 301 | 0 | 0 | 0 |

## Predicted disagreements by first differing field and value

| field | workbook | PUDL | generator-months |
|---|---|---|---|
| status | OP | OA | 1489 |
| status | OP | OS | 278 |
| status | OP | RE | 136 |
| MW | OP | OP | 84 |
| status | OP | SB | 83 |
| status | OA | OP | 78 |
| status | OA | OS | 60 |
| status | SB | OP | 46 |
| status | OS | OP | 39 |
| planned month | V | V | 25 |
| planned month | T | T | 16 |
| status | OS | OA | 12 |
| planned month | L | L | 9 |
| planned month | U | U | 9 |
| status | RE | OP | 8 |
| status | U | T | 7 |
| planned month | P | P | 4 |
| status | RE | OS | 3 |
| planned month | TS | TS | 3 |
| status | OA | SB | 2 |
| status | U | V | 2 |
| status | L | U | 1 |
| status | TS | V | 1 |

## P4

| generator | month | workbook | PUDL records before 2026 | matching |
|---|---|---|---|---|
| 69338/LEAKY | 2026-08 | TS, 2026-12, 9.9 MW | 2 | 2025-10 |
| 69372/KNOXS | 2026-07 | V, 2026-11, 5.0 MW | 2 | 2025-12 |

## P1

224408 rows, 32 columns hashed (all but report_date, valid_until_date, report_date_max); 0 repeats at 0 generators.

## August 2026: generators the simulation predicts PUDL shows a stale value for

301 generators, 16574.2 MW by the workbook.

| generator | fields | workbook | PUDL | PUDL reported | differs since |
|---|---|---|---|---|---|
| 6481/1 | status | RE, -, 820.0 MW | OS, -, 820.0 MW | 2026-03 | 2026-07 |
| 6481/2 | status | RE, -, 820.0 MW | OS, -, 820.0 MW | 2026-03 | 2026-07 |
| 2828/3 | status | OP, -, 650.0 MW | OS, -, 650.0 MW | 2024-02 | 2026-01 |
| 2828/1 | status | OP, -, 615.2 MW | OS, -, 615.2 MW | 2024-02 | 2026-01 |
| 2828/2 | status | OP, -, 615.2 MW | OS, -, 615.2 MW | 2024-02 | 2026-01 |
| 6100/1 | status | OP, -, 351.0 MW | OA, -, 351.0 MW | 2025-02 | 2026-02 |
| 6100/2 | status | OP, -, 351.0 MW | OA, -, 351.0 MW | 2025-02 | 2026-02 |
| 6100/3 | status | OP, -, 351.0 MW | OA, -, 351.0 MW | 2025-02 | 2026-02 |
| 66545/MMTHS | planned month | V, 2026-10, 300.0 MW | V, 2026-09, 300.0 MW | 2026-07 | 2026-08 |
| 68514/MC201 | planned month | U, 2026-10, 300.0 MW | U, 2026-09, 300.0 MW | 2026-04 | 2026-07 |
| 55129/STG | status | OP, -, 272.1 MW | OA, -, 272.1 MW | 2023-04 | 2026-01 |
| 392/1 | status | OP, -, 271.0 MW | OA, -, 271.0 MW | 2023-03 | 2026-01 |
| 392/5 | status | OP, -, 271.0 MW | OA, -, 271.0 MW | 2023-03 | 2026-01 |
| 67909/SHS01 | MW | OP, -, 222.9 MW | OP, -, 264.6 MW | 2025-04 | 2026-01 |
| 66893/TXJS2 | status | U, 2027-03, 200.0 MW | V, 2027-03, 200.0 MW | 2026-05 | 2026-07 |
| 104/1 | status | OP, -, 199.8 MW | OS, -, 199.8 MW | 2023-01 | 2026-01 |
| 2693/2 | status | OP, -, 193.5 MW | OA, -, 193.5 MW | 2025-03 | 2026-05 |
| 2693/6 | status | OP, -, 193.5 MW | OA, -, 193.5 MW | 2024-07 | 2026-05 |
| 55098/GEN3 | status | OP, -, 185.0 MW | RE, -, 185.0 MW | 2022-04 | 2026-01 |
| 55098/GEN1 | status | OP, -, 172.0 MW | RE, -, 172.0 MW | 2022-04 | 2026-01 |
| 55098/GEN2 | status | OP, -, 172.0 MW | RE, -, 172.0 MW | 2022-04 | 2026-01 |
| 56252/CWF | MW | OP, -, 150.0 MW | OP, -, 201.2 MW | 2020-03 | 2026-01 |
| 3082/11 | status | OP, -, 135.0 MW | OA, -, 135.0 MW | 2019-12 | 2026-01 |
| 3082/12 | status | OP, -, 135.0 MW | OA, -, 135.0 MW | 2019-12 | 2026-01 |
| 3082/13 | status | OP, -, 135.0 MW | OA, -, 135.0 MW | 2022-07 | 2026-01 |
| 3082/2 | status | OP, -, 135.0 MW | OA, -, 135.0 MW | 2017-04 | 2026-01 |
| 3082/3 | status | OA, -, 135.0 MW | OP, -, 135.0 MW | 2023-01 | 2026-02 |
| 3082/4 | status | OP, -, 135.0 MW | OA, -, 135.0 MW | 2019-02 | 2026-01 |
| 3082/5 | status | OP, -, 135.0 MW | OA, -, 135.0 MW | 2023-01 | 2026-01 |
| 3082/6 | status | OP, -, 135.0 MW | OS, -, 135.0 MW | 2020-06 | 2026-01 |
| 3082/7 | status | OP, -, 135.0 MW | OS, -, 135.0 MW | 2019-02 | 2026-02 |
| 3082/9 | status | OP, -, 135.0 MW | OA, -, 135.0 MW | 2021-01 | 2026-01 |
| 3926/1 | status | OP, -, 135.0 MW | OA, -, 135.0 MW | 2019-02 | 2026-01 |
| 3926/2 | status | OP, -, 135.0 MW | OA, -, 135.0 MW | 2019-02 | 2026-01 |
| 3926/3 | status | OA, -, 135.0 MW | OP, -, 135.0 MW | 2017-03 | 2026-01 |
| 3926/5 | status | OA, -, 135.0 MW | OS, -, 135.0 MW | 2019-02 | 2026-01 |
| 3926/6 | status | OP, -, 135.0 MW | OA, -, 135.0 MW | 2023-01 | 2026-01 |
| 3927/2 | status | OA, -, 135.0 MW | OP, -, 135.0 MW | 2019-02 | 2026-02 |
| 3927/4 | status | OP, -, 135.0 MW | OA, -, 135.0 MW | 2018-03 | 2026-01 |
| 6175/1 | status | OA, -, 135.0 MW | OP, -, 135.0 MW | 2017-04 | 2026-02 |
| 6175/2 | status | OP, -, 135.0 MW | OA, -, 135.0 MW | 2019-12 | 2026-01 |
| 6175/3 | status | OP, -, 135.0 MW | OA, -, 135.0 MW | 2023-12 | 2026-01 |
| 6175/4 | status | OP, -, 135.0 MW | OA, -, 135.0 MW | 2023-01 | 2026-01 |
| 6175/6 | status | OP, -, 135.0 MW | OA, -, 135.0 MW | 2019-12 | 2026-01 |
| 219/1 | status | OP, -, 117.9 MW | OA, -, 117.9 MW | 2024-02 | 2026-02 |
| 3925/5 | status | OP, -, 111.0 MW | OA, -, 111.0 MW | 2019-12 | 2026-01 |
| 840/1 | status | OP, -, 103.0 MW | OA, -, 103.0 MW | 2021-01 | 2026-01 |
| 344/1 | status | OP, -, 95.0 MW | OA, -, 95.0 MW | 2021-04 | 2026-01 |
| 344/2 | status | OP, -, 95.0 MW | OA, -, 95.0 MW | 2021-04 | 2026-01 |
| 3921/19 | status | OA, -, 95.0 MW | OP, -, 95.0 MW | 2017-03 | 2026-02 |
| 3921/20 | status | OP, -, 95.0 MW | OA, -, 95.0 MW | 2022-07 | 2026-01 |
| 3921/22 | status | OP, -, 95.0 MW | OA, -, 95.0 MW | 2021-01 | 2026-01 |
| 3921/23 | status | OP, -, 95.0 MW | OA, -, 95.0 MW | 2021-01 | 2026-01 |
| 3921/24 | status | OP, -, 95.0 MW | OA, -, 95.0 MW | 2021-01 | 2026-02 |
| 3921/25 | status | OP, -, 95.0 MW | OA, -, 95.0 MW | 2021-01 | 2026-01 |
| 3921/26 | status | OP, -, 95.0 MW | OA, -, 95.0 MW | 2021-01 | 2026-01 |
| 3921/27 | status | OP, -, 95.0 MW | OA, -, 95.0 MW | 2019-02 | 2026-01 |
| 3925/1 | status | OA, -, 90.0 MW | OS, -, 90.0 MW | 2023-12 | 2026-02 |
| 3921/11 | status | OA, -, 88.2 MW | OP, -, 88.2 MW | 2019-02 | 2026-02 |
| 3921/14 | status | OP, -, 88.2 MW | OA, -, 88.2 MW | 2019-02 | 2026-01 |

## August 2026 workbook generators with no PUDL record in force (descriptive)

16 generators; first 16 traced (last six PUDL records each).

| generator | workbook August | 2026 workbooks listing it | last PUDL records |
|---|---|---|---|
| 1517/1 | RE, -, 920.0 MW | 2026-08 |  |
| 1645/1 | RE, -, 185.0 MW | 2026-08 |  |
| 1697/1 | RE, -, 75.0 MW | 2026-08 |  |
| 1729/1 | RE, -, 65.0 MW | 2026-08 |  |
| 246/3 | RE, -, 65.0 MW | 2026-08 |  |
| 3166/1 | RE, -, 42.0 MW | 2026-08 |  |
| 360/1 | RE, -, 456.0 MW | 2026-08 |  |
| 4143/5 | RE, -, 50.3 MW | 2026-08 |  |
| 558/1 | RE, -, 600.3 MW | 2026-08 |  |
| 566/1 | RE, -, 661.5 MW | 2026-08 |  |
| 6107/1 | RE, -, 1216.0 MW | 2026-08 |  |
| 6176/1 | RE, -, 963.0 MW | 2026-08 |  |
| 8011/2 | RE, -, 961.0 MW | 2026-08 |  |
| 869/1 | RE, -, 207.0 MW | 2026-08 |  |
| 885/1 | RE, -, 1098.0 MW | 2026-08 |  |
| 885/2 | RE, -, 1098.0 MW | 2026-08 |  |
