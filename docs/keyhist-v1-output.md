# keyhist 0.1.0: EIA-860M's 2026 workbooks against PUDL's changelog

Descriptive probe, no prediction tested. MV2 of Munim, Inc. (made with AI agents).

PUDL file: core_eia860m__changelog_generators.parquet, latest report 2026-08. Workbooks from Zenodo record 22995197, eia860m-2026.zip (md5 380a9824a20be96d182fea793c299e91; downloaded).

## Each month: workbook against PUDL's records in force

| month | workbook keys | PUDL keys | both | workbook only | PUDL only | status agree | planned month agree | capacity agree |
|---|---|---|---|---|---|---|---|---|
| 2026-01 | 36865 | 36879 | 36865 | 0 | 14 | 29481 of 29739 | 1965 of 1972 | 36858 of 36865 |
| 2026-02 | 36890 | 36907 | 36890 | 0 | 17 | 29385 of 29661 | 1940 of 1946 | 36883 of 36890 |
| 2026-03 | 37404 | 37420 | 37404 | 0 | 16 | 29877 of 30153 | 2307 of 2317 | 37395 of 37404 |
| 2026-04 | 37480 | 37498 | 37480 | 0 | 18 | 29942 of 30226 | 2247 of 2256 | 37473 of 37480 |
| 2026-05 | 37629 | 37651 | 37629 | 0 | 22 | 30071 of 30356 | 2301 of 2311 | 37609 of 37629 |
| 2026-06 | 37779 | 37794 | 37779 | 0 | 15 | 30206 of 30491 | 2286 of 2295 | 37760 of 37779 |
| 2026-07 | 37957 | 37962 | 37957 | 0 | 5 | 30372 of 30658 | 2333 of 2341 | 37949 of 37957 |
| 2026-08 | 38011 | 37996 | 37995 | 16 | 1 | 30403 of 30687 | 2304 of 2311 | 37988 of 37995 |

## Given generators, month by month

| key | first month that differs | months that differ |
|---|---|---|
| 61912/MHSOL | 2026-07 | 2 of 8 |
| 65710/PTNM | 2026-07 | 2 of 8 |
| 66545/MMTHS | 2026-08 | 1 of 8 |
| 66546/MMTHC | 2026-07 | 1 of 8 |
| 66893/TXJS2 | 2026-07 | 2 of 8 |
| 67223/SUNYF | 2026-07 | 1 of 8 |
| 67836/GSP1 | 2026-03 | 6 of 8 |
| 67836/GSP2 | 2026-03 | 6 of 8 |
| 68334/EVCRK | 2026-08 | 1 of 8 |
| 68514/MC201 | 2026-07 | 2 of 8 |
| 69338/LEAKY | 2026-08 | 1 of 8 |
| 69372/KNOXS | 2026-07 | 2 of 8 |
| 69579/HMWT | 2026-04 | 4 of 8 |
| 69589/BEEK1 | 2026-03 | 5 of 8 |
| 69825/MADCR | 2026-06 | 3 of 8 |
| 70257/H2SLR | 2026-07 | 1 of 8 |

### 61912/MHSOL

| month | workbook (sheet: status, planned, MW) | PUDL in force | same | PUDL equals the workbook of |
|---|---|---|---|---|
| 2026-01 | Planned: L, 2026-12, 14.0 MW | L, 2026-12, 14.0 MW (from 2025-09) | True |  |
| 2026-02 | Planned: T, 2026-12, 14.0 MW | T, 2026-12, 14.0 MW (from 2026-02) | True |  |
| 2026-03 | Planned: T, 2026-12, 14.0 MW | T, 2026-12, 14.0 MW (from 2026-02) | True |  |
| 2026-04 | Planned: T, 2026-12, 14.0 MW | T, 2026-12, 14.0 MW (from 2026-02) | True |  |
| 2026-05 | Planned: U, 2027-01, 14.0 MW | U, 2027-01, 14.0 MW (from 2026-05) | True |  |
| 2026-06 | Planned: T, 2027-01, 14.0 MW | T, 2027-01, 14.0 MW (from 2026-06) | True |  |
| 2026-07 | Planned: U, 2027-01, 14.0 MW | T, 2027-01, 14.0 MW (from 2026-06) | False | 2026-06 |
| 2026-08 | Planned: U, 2027-01, 14.0 MW | T, 2027-01, 14.0 MW (from 2026-06) | False | 2026-06 |

### 65710/PTNM

| month | workbook (sheet: status, planned, MW) | PUDL in force | same | PUDL equals the workbook of |
|---|---|---|---|---|
| 2026-01 | Planned: L, 2027-09, 4.0 MW | L, 2027-09, 4.0 MW (from 2025-12) | True |  |
| 2026-02 | Planned: L, 2027-03, 4.0 MW | L, 2027-03, 4.0 MW (from 2026-02) | True |  |
| 2026-03 | Planned: L, 2026-11, 4.0 MW | L, 2026-11, 4.0 MW (from 2026-03) | True |  |
| 2026-04 | Planned: L, 2026-11, 4.0 MW | L, 2026-11, 4.0 MW (from 2026-03) | True |  |
| 2026-05 | Planned: L, 2027-01, 4.0 MW | L, 2027-01, 4.0 MW (from 2026-05) | True |  |
| 2026-06 | Planned: L, 2027-01, 4.0 MW | L, 2027-01, 4.0 MW (from 2026-05) | True |  |
| 2026-07 | Planned: L, 2027-03, 4.0 MW | L, 2027-01, 4.0 MW (from 2026-05) | False | 2026-05, 2026-06 |
| 2026-08 | Planned: L, 2027-03, 4.0 MW | L, 2027-01, 4.0 MW (from 2026-05) | False | 2026-05, 2026-06 |

### 66545/MMTHS

| month | workbook (sheet: status, planned, MW) | PUDL in force | same | PUDL equals the workbook of |
|---|---|---|---|---|
| 2026-01 | Planned: V, 2026-10, 300.0 MW | V, 2026-10, 300.0 MW (from 2025-12) | True |  |
| 2026-02 | Planned: V, 2026-10, 300.0 MW | V, 2026-10, 300.0 MW (from 2025-12) | True |  |
| 2026-03 | Planned: V, 2026-08, 300.0 MW | V, 2026-08, 300.0 MW (from 2026-03) | True |  |
| 2026-04 | Planned: V, 2026-08, 300.0 MW | V, 2026-08, 300.0 MW (from 2026-03) | True |  |
| 2026-05 | Planned: V, 2026-08, 300.0 MW | V, 2026-08, 300.0 MW (from 2026-03) | True |  |
| 2026-06 | Planned: V, 2026-08, 300.0 MW | V, 2026-08, 300.0 MW (from 2026-03) | True |  |
| 2026-07 | Planned: V, 2026-09, 300.0 MW | V, 2026-09, 300.0 MW (from 2026-07) | True |  |
| 2026-08 | Planned: V, 2026-10, 300.0 MW | V, 2026-09, 300.0 MW (from 2026-07) | False | 2026-07 |

### 66546/MMTHC

| month | workbook (sheet: status, planned, MW) | PUDL in force | same | PUDL equals the workbook of |
|---|---|---|---|---|
| 2026-01 | Planned: U, 2026-10, 300.0 MW | U, 2026-10, 300.0 MW (from 2025-12) | True |  |
| 2026-02 | Planned: U, 2026-10, 300.0 MW | U, 2026-10, 300.0 MW (from 2025-12) | True |  |
| 2026-03 | Planned: U, 2026-09, 300.0 MW | U, 2026-09, 300.0 MW (from 2026-03) | True |  |
| 2026-04 | Planned: U, 2026-09, 300.0 MW | U, 2026-09, 300.0 MW (from 2026-03) | True |  |
| 2026-05 | Planned: U, 2026-08, 300.0 MW | U, 2026-08, 300.0 MW (from 2026-05) | True |  |
| 2026-06 | Planned: U, 2026-08, 300.0 MW | U, 2026-08, 300.0 MW (from 2026-05) | True |  |
| 2026-07 | Planned: U, 2026-10, 300.0 MW | U, 2026-08, 300.0 MW (from 2026-05) | False | 2026-05, 2026-06 |
| 2026-08 | Planned: U, 2026-11, 300.0 MW | U, 2026-11, 300.0 MW (from 2026-08) | True |  |

### 66893/TXJS2

| month | workbook (sheet: status, planned, MW) | PUDL in force | same | PUDL equals the workbook of |
|---|---|---|---|---|
| 2026-01 | Planned: U, 2027-03, 200.0 MW | U, 2027-03, 200.0 MW (from 2025-06) | True |  |
| 2026-02 | Planned: U, 2027-03, 200.0 MW | U, 2027-03, 200.0 MW (from 2025-06) | True |  |
| 2026-03 | Planned: U, 2027-03, 200.0 MW | U, 2027-03, 200.0 MW (from 2025-06) | True |  |
| 2026-04 | Planned: U, 2027-03, 200.0 MW | U, 2027-03, 200.0 MW (from 2025-06) | True |  |
| 2026-05 | Planned: V, 2027-03, 200.0 MW | V, 2027-03, 200.0 MW (from 2026-05) | True |  |
| 2026-06 | Planned: V, 2027-03, 200.0 MW | V, 2027-03, 200.0 MW (from 2026-05) | True |  |
| 2026-07 | Planned: U, 2027-03, 200.0 MW | V, 2027-03, 200.0 MW (from 2026-05) | False | 2026-05, 2026-06 |
| 2026-08 | Planned: U, 2027-03, 200.0 MW | V, 2027-03, 200.0 MW (from 2026-05) | False | 2026-05, 2026-06 |

### 67223/SUNYF

| month | workbook (sheet: status, planned, MW) | PUDL in force | same | PUDL equals the workbook of |
|---|---|---|---|---|
| 2026-01 | Planned: P, 2026-12, 20.0 MW | P, 2026-12, 20.0 MW (from 2025-09) | True |  |
| 2026-02 | Planned: P, 2026-12, 20.0 MW | P, 2026-12, 20.0 MW (from 2025-09) | True |  |
| 2026-03 | Planned: P, 2026-12, 20.0 MW | P, 2026-12, 20.0 MW (from 2025-09) | True |  |
| 2026-04 | Planned: P, 2026-12, 20.0 MW | P, 2026-12, 20.0 MW (from 2025-09) | True |  |
| 2026-05 | Planned: P, 2026-12, 20.0 MW | P, 2026-12, 20.0 MW (from 2025-09) | True |  |
| 2026-06 | Planned: P, 2027-01, 20.0 MW | P, 2027-01, 20.0 MW (from 2026-06) | True |  |
| 2026-07 | Canceled or Postponed: , None, 20.0 MW | P, 2027-01, 20.0 MW (from 2026-06) | False | 2026-06 |
| 2026-08 | Canceled or Postponed: , None, 20.0 MW |  | True |  |

### 67836/GSP1

| month | workbook (sheet: status, planned, MW) | PUDL in force | same | PUDL equals the workbook of |
|---|---|---|---|---|
| 2026-01 | Planned: T, 2027-12, 13.0 MW | T, 2027-12, 13.0 MW (from 2024-09) | True |  |
| 2026-02 | Planned: T, 2026-12, 13.0 MW | T, 2026-12, 13.0 MW (from 2026-02) | True |  |
| 2026-03 | Planned: T, 2027-12, 13.0 MW | T, 2026-12, 13.0 MW (from 2026-02) | False | 2026-02 |
| 2026-04 | Planned: T, 2027-12, 13.0 MW | T, 2026-12, 13.0 MW (from 2026-02) | False | 2026-02 |
| 2026-05 | Planned: T, 2027-12, 13.0 MW | T, 2026-12, 13.0 MW (from 2026-02) | False | 2026-02 |
| 2026-06 | Planned: T, 2027-12, 13.0 MW | T, 2026-12, 13.0 MW (from 2026-02) | False | 2026-02 |
| 2026-07 | Planned: T, 2027-12, 13.0 MW | T, 2026-12, 13.0 MW (from 2026-02) | False | 2026-02 |
| 2026-08 | Planned: T, 2027-12, 13.0 MW | T, 2026-12, 13.0 MW (from 2026-02) | False | 2026-02 |

### 67836/GSP2

| month | workbook (sheet: status, planned, MW) | PUDL in force | same | PUDL equals the workbook of |
|---|---|---|---|---|
| 2026-01 | Planned: T, 2027-12, 13.0 MW | T, 2027-12, 13.0 MW (from 2024-09) | True |  |
| 2026-02 | Planned: T, 2026-12, 13.0 MW | T, 2026-12, 13.0 MW (from 2026-02) | True |  |
| 2026-03 | Planned: T, 2027-12, 13.0 MW | T, 2026-12, 13.0 MW (from 2026-02) | False | 2026-02 |
| 2026-04 | Planned: T, 2027-12, 13.0 MW | T, 2026-12, 13.0 MW (from 2026-02) | False | 2026-02 |
| 2026-05 | Planned: T, 2027-12, 13.0 MW | T, 2026-12, 13.0 MW (from 2026-02) | False | 2026-02 |
| 2026-06 | Planned: T, 2027-12, 13.0 MW | T, 2026-12, 13.0 MW (from 2026-02) | False | 2026-02 |
| 2026-07 | Planned: T, 2027-12, 13.0 MW | T, 2026-12, 13.0 MW (from 2026-02) | False | 2026-02 |
| 2026-08 | Planned: T, 2027-12, 13.0 MW | T, 2026-12, 13.0 MW (from 2026-02) | False | 2026-02 |

### 68334/EVCRK

| month | workbook (sheet: status, planned, MW) | PUDL in force | same | PUDL equals the workbook of |
|---|---|---|---|---|
| 2026-01 | Planned: U, 2026-06, 103.0 MW | U, 2026-06, 103.0 MW (from 2024-11) | True |  |
| 2026-02 | Planned: U, 2026-06, 103.0 MW | U, 2026-06, 103.0 MW (from 2024-11) | True |  |
| 2026-03 | Planned: U, 2026-06, 103.0 MW | U, 2026-06, 103.0 MW (from 2024-11) | True |  |
| 2026-04 | Planned: U, 2026-06, 103.0 MW | U, 2026-06, 103.0 MW (from 2024-11) | True |  |
| 2026-05 | Planned: U, 2026-06, 103.0 MW | U, 2026-06, 103.0 MW (from 2024-11) | True |  |
| 2026-06 | Planned: U, 2026-06, 103.0 MW | U, 2026-06, 103.0 MW (from 2024-11) | True |  |
| 2026-07 | Planned: U, 2026-07, 103.0 MW | U, 2026-07, 103.0 MW (from 2026-07) | True |  |
| 2026-08 |  | U, 2026-07, 103.0 MW (from 2026-07) | False | 2026-07 |

### 68514/MC201

| month | workbook (sheet: status, planned, MW) | PUDL in force | same | PUDL equals the workbook of |
|---|---|---|---|---|
| 2026-01 | Planned: U, 2026-10, 300.0 MW | U, 2026-10, 300.0 MW (from 2025-12) | True |  |
| 2026-02 | Planned: U, 2026-10, 300.0 MW | U, 2026-10, 300.0 MW (from 2025-12) | True |  |
| 2026-03 | Planned: U, 2026-10, 300.0 MW | U, 2026-10, 300.0 MW (from 2025-12) | True |  |
| 2026-04 | Planned: U, 2026-09, 300.0 MW | U, 2026-09, 300.0 MW (from 2026-04) | True |  |
| 2026-05 | Planned: U, 2026-09, 300.0 MW | U, 2026-09, 300.0 MW (from 2026-04) | True |  |
| 2026-06 | Planned: U, 2026-09, 300.0 MW | U, 2026-09, 300.0 MW (from 2026-04) | True |  |
| 2026-07 | Planned: U, 2026-10, 300.0 MW | U, 2026-09, 300.0 MW (from 2026-04) | False | 2026-04, 2026-05, 2026-06 |
| 2026-08 | Planned: U, 2026-10, 300.0 MW | U, 2026-09, 300.0 MW (from 2026-04) | False | 2026-04, 2026-05, 2026-06 |

### 69338/LEAKY

| month | workbook (sheet: status, planned, MW) | PUDL in force | same | PUDL equals the workbook of |
|---|---|---|---|---|
| 2026-01 | Planned: V, 2026-12, 9.9 MW | V, 2026-12, 9.9 MW (from 2025-12) | True |  |
| 2026-02 | Planned: V, 2026-12, 9.9 MW | V, 2026-12, 9.9 MW (from 2025-12) | True |  |
| 2026-03 | Planned: V, 2026-12, 9.9 MW | V, 2026-12, 9.9 MW (from 2025-12) | True |  |
| 2026-04 | Planned: V, 2026-12, 9.9 MW | V, 2026-12, 9.9 MW (from 2025-12) | True |  |
| 2026-05 | Planned: V, 2026-12, 9.9 MW | V, 2026-12, 9.9 MW (from 2025-12) | True |  |
| 2026-06 | Planned: V, 2026-12, 9.9 MW | V, 2026-12, 9.9 MW (from 2025-12) | True |  |
| 2026-07 | Planned: V, 2026-12, 9.9 MW | V, 2026-12, 9.9 MW (from 2025-12) | True |  |
| 2026-08 | Planned: TS, 2026-12, 9.9 MW | V, 2026-12, 9.9 MW (from 2025-12) | False | 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07 |

### 69372/KNOXS

| month | workbook (sheet: status, planned, MW) | PUDL in force | same | PUDL equals the workbook of |
|---|---|---|---|---|
| 2026-01 | Planned: V, 2026-08, 5.0 MW | V, 2026-08, 5.0 MW (from 2026-01) | True |  |
| 2026-02 | Planned: V, 2026-08, 5.0 MW | V, 2026-08, 5.0 MW (from 2026-01) | True |  |
| 2026-03 | Planned: V, 2026-08, 5.0 MW | V, 2026-08, 5.0 MW (from 2026-01) | True |  |
| 2026-04 | Planned: V, 2026-08, 5.0 MW | V, 2026-08, 5.0 MW (from 2026-01) | True |  |
| 2026-05 | Planned: V, 2026-08, 5.0 MW | V, 2026-08, 5.0 MW (from 2026-01) | True |  |
| 2026-06 | Planned: V, 2026-10, 5.0 MW | V, 2026-10, 5.0 MW (from 2026-06) | True |  |
| 2026-07 | Planned: V, 2026-11, 5.0 MW | V, 2026-10, 5.0 MW (from 2026-06) | False | 2026-06 |
| 2026-08 | Planned: V, 2026-11, 5.0 MW | V, 2026-10, 5.0 MW (from 2026-06) | False | 2026-06 |

### 69579/HMWT

| month | workbook (sheet: status, planned, MW) | PUDL in force | same | PUDL equals the workbook of |
|---|---|---|---|---|
| 2026-01 | Planned: V, 2026-12, 180.5 MW | V, 2026-12, 180.5 MW (from 2026-01) | True |  |
| 2026-02 | Planned: V, 2026-12, 180.5 MW | V, 2026-12, 180.5 MW (from 2026-01) | True |  |
| 2026-03 | Planned: V, 2026-07, 180.5 MW | V, 2026-07, 180.5 MW (from 2026-03) | True |  |
| 2026-04 | Planned: V, 2026-12, 180.5 MW | V, 2026-07, 180.5 MW (from 2026-03) | False | 2026-03 |
| 2026-05 | Planned: V, 2026-12, 180.5 MW | V, 2026-07, 180.5 MW (from 2026-03) | False | 2026-03 |
| 2026-06 | Planned: V, 2026-12, 180.5 MW | V, 2026-07, 180.5 MW (from 2026-03) | False | 2026-03 |
| 2026-07 | Planned: V, 2026-12, 180.5 MW | V, 2026-07, 180.5 MW (from 2026-03) | False | 2026-03 |
| 2026-08 | Planned: TS, 2026-12, 180.5 MW | TS, 2026-12, 180.5 MW (from 2026-08) | True |  |

### 69589/BEEK1

| month | workbook (sheet: status, planned, MW) | PUDL in force | same | PUDL equals the workbook of |
|---|---|---|---|---|
| 2026-01 | Planned: U, 2027-02, 206.8 MW | U, 2027-02, 206.8 MW (from 2026-01) | True |  |
| 2026-02 | Planned: T, 2027-02, 206.8 MW | T, 2027-02, 206.8 MW (from 2026-02) | True |  |
| 2026-03 | Planned: U, 2027-02, 206.8 MW | T, 2027-02, 206.8 MW (from 2026-02) | False | 2026-02 |
| 2026-04 | Planned: U, 2027-02, 206.8 MW | T, 2027-02, 206.8 MW (from 2026-02) | False | 2026-02 |
| 2026-05 | Planned: U, 2027-02, 206.8 MW | T, 2027-02, 206.8 MW (from 2026-02) | False | 2026-02 |
| 2026-06 | Planned: U, 2027-02, 206.8 MW | T, 2027-02, 206.8 MW (from 2026-02) | False | 2026-02 |
| 2026-07 | Planned: U, 2027-02, 206.8 MW | T, 2027-02, 206.8 MW (from 2026-02) | False | 2026-02 |
| 2026-08 | Planned: V, 2027-02, 206.8 MW | V, 2027-02, 206.8 MW (from 2026-08) | True |  |

### 69825/MADCR

| month | workbook (sheet: status, planned, MW) | PUDL in force | same | PUDL equals the workbook of |
|---|---|---|---|---|
| 2026-01 |  |  | True |  |
| 2026-02 |  |  | True |  |
| 2026-03 | Planned: T, 2027-04, 5.0 MW | T, 2027-04, 5.0 MW (from 2026-03) | True |  |
| 2026-04 | Planned: T, 2027-04, 5.0 MW | T, 2027-04, 5.0 MW (from 2026-03) | True |  |
| 2026-05 | Planned: T, 2027-03, 5.0 MW | T, 2027-03, 5.0 MW (from 2026-05) | True |  |
| 2026-06 | Planned: T, 2027-04, 5.0 MW | T, 2027-03, 5.0 MW (from 2026-05) | False | 2026-05 |
| 2026-07 | Planned: T, 2027-04, 5.0 MW | T, 2027-03, 5.0 MW (from 2026-05) | False | 2026-05 |
| 2026-08 | Planned: T, 2027-04, 5.0 MW | T, 2027-03, 5.0 MW (from 2026-05) | False | 2026-05 |

### 70257/H2SLR

| month | workbook (sheet: status, planned, MW) | PUDL in force | same | PUDL equals the workbook of |
|---|---|---|---|---|
| 2026-01 |  |  | True |  |
| 2026-02 |  |  | True |  |
| 2026-03 |  |  | True |  |
| 2026-04 |  |  | True |  |
| 2026-05 |  |  | True |  |
| 2026-06 | Planned: L, 2028-03, 250.0 MW | L, 2028-03, 250.0 MW (from 2026-06) | True |  |
| 2026-07 |  | L, 2028-03, 250.0 MW (from 2026-06) | False | 2026-06 |
| 2026-08 |  |  | True |  |
