# Coal in EIA's September 2026 EIA-860M workbook (coalsep 0.1.0)

- September 2026: https://www.eia.gov/electricity/data/eia860m/xls/september_generator2026.xlsx, 14,013,970 bytes, md5 4c741eb77a5ccad5aca32ffe43f398af (same as recorded earlier: True)
- August 2026: https://www.eia.gov/electricity/data/eia860m/archive/xls/august_generator2026.xlsx, 13,955,142 bytes, md5 9727ac867236faab7d5503175dacdf38 (same as recorded earlier: True)

Coal rows read: August 1,356, September 1,356.

## Gate G1: the August workbook reproduces coal-rows (PUDL, to August 2026)

- Coal rows on August's Retired sheet with retirement year 2026: 0
- Plan generators whose August planned month equals PUDL's: 16 of 16 (needs 15)
- G1: **held**

| key | PUDL (to Aug 2026) | August workbook | match |
|---|---|---|---|
| 1012/2 | 2026-09 | 2026-09 | yes |
| 165/2 | no date | no date | yes |
| 1710/1 | 2026-11 | 2026-11 | yes |
| 1710/2 | 2026-11 | 2026-11 | yes |
| 1710/3 | 2026-11 | 2026-11 | yes |
| 3399/2 | 2034-12 | 2034-12 | yes |
| 3407/7 | 2034-12 | 2034-12 | yes |
| 3407/8 | 2034-12 | 2034-12 | yes |
| 3407/9 | 2034-12 | 2034-12 | yes |
| 4041/7 | 2027-12 | 2027-12 | yes |
| 4041/8 | 2027-12 | 2027-12 | yes |
| 470/2 | 2026-12 | 2026-12 | yes |
| 6021/1 | 2026-09 | 2026-09 | yes |
| 6085/17 | 2026-10 | 2026-10 | yes |
| 6085/18 | 2026-10 | 2026-10 | yes |
| 6090/1 | 2026-12 | 2026-12 | yes |

## Predictions (docs/coalsep-plan.md), September 2026 workbook

| # | prediction | result | verdict |
|---|---|---|---|
| S1 | no coal row on the Retired sheet with retirement year 2026 | 0 rows | held |
| S2 | none of the 16 plan generators retired; Sherburne County 1 and Comanche 2 still dated 2026-12 | retired: none; 6090/1: 2026-12; 470/2: 2026-12 | held |
| S3 | operating coal dated 2026-10 to 2026-12 is 3,000-4,500 MW, at least 60% of it at plants under DOE orders | 3,584.5 MW in 9 units; 2,569.5 MW under orders (share 0.7168) | held |

## Described, not scored

### Operating coal dated to retire 2026-10 to 2027-12, by plant (September 2026 workbook)

| plant | state | plant ID | units | MW | months | DOE 202(c) order |
|---|---|---|---|---|---|---|
| J H Campbell | MI | 1710 | 1, 2, 3 | 1,330.5 | 2026-11 | yes |
| R M Schahfer | IN | 6085 | 17, 18 | 722.0 | 2026-12 | yes |
| Sherburne County | MN | 6090 | 1 | 680.0 | 2026-12 | no |
| Craig (CO) | CO | 6021 | 1 | 427.0 | 2026-12 | yes |
| Comanche (CO) | CO | 470 | 2 | 335.0 | 2026-12 | no |
| F B Culley | IN | 1012 | 2 | 90.0 | 2026-12 | yes |
| Baldwin Energy Complex | IL | 889 | 1, 2 | 1,157.0 | 2027-12 | no |
| Kincaid Generation LLC | IL | 876 | 1, 2 | 1,112.0 | 2027-12 | no |
| Victor J Daniel Jr | MS | 6073 | 1, 2 | 1,004.0 | 2027-12 | no |
| Kingston | TN | 3407 | 1, 2, 3, 4, 5, 6 | 703.0 | 2027-12 | no |
| South Oak Creek | WI | 4041 | 7, 8 | 616.0 | 2027-12 | no |
| Newton | IL | 6017 | 1 | 595.0 | 2027-12 | no |
| Springerville | AZ | 8223 | 1 | 381.0 | 2027-12 | no |
| Hayden | CO | 525 | 2 | 262.0 | 2027-12 | no |
| Dave Johnston | WY | 4158 | 3 | 220.0 | 2027-12 | no |
| Merrimack | NH | 2364 | 1 | 108.0 | 2027-12 | no |

16 plants, 9,742.5 MW; 2,569.5 MW at plants under DOE orders.

### Operating coal dated before 2026-10 (past its planned month), September 2026 workbook

| key | plant | state | planned | MW |
|---|---|---|---|---|
| none | | | | |

### Coal units whose record changed from August to September 2026

| key | plant | state | MW | August | September |
|---|---|---|---|---|---|
| 1012/2 | F B Culley | IN | 90.0 | operating 2026-09 | operating 2026-12 |
| 6021/1 | Craig (CO) | CO | 427.0 | operating 2026-09 | operating 2026-12 |
| 6085/17 | R M Schahfer | IN | 361.0 | operating 2026-10 | operating 2026-12 |
| 6085/18 | R M Schahfer | IN | 361.0 | operating 2026-10 | operating 2026-12 |

### Coal on the September Retired sheet with retirement year 2025 or later

| key | plant | state | retired | MW |
|---|---|---|---|---|
| 594/4 | Indian River Generating Station | DE | 2025-02 | 410.0 |
| 113/1 | Cholla | AZ | 2025-03 | 112.0 |
| 113/3 | Cholla | AZ | 2025-03 | 271.0 |
| 2367/4 | Schiller | NH | 2025-10 | 47.5 |
| 2367/6 | Schiller | NH | 2025-10 | 47.9 |
| 6481/1 | Intermountain Power Project | UT | 2025-10 | 900.0 |
| 6481/2 | Intermountain Power Project | UT | 2025-11 | 900.0 |
| 1073/1 | Prairie Creek | IA | 2025-12 | 14.6 |

### Sheets read

- september / Canceled or Postponed: not read
- september / Operating: header row 2, 28,486 rows, 446 coal; columns missing: none
- september / Operating_PR: header row 2, 230 rows, 2 coal; columns missing: none
- september / Planned: not read
- september / Planned_PR: not read
- september / Retired: header row 2, 7,323 rows, 908 coal; columns missing: status
- september / Retired_PR: header row 2, 12 rows, 0 coal; columns missing: status
- august / Canceled or Postponed: not read
- august / Operating: header row 2, 28,379 rows, 446 coal; columns missing: none
- august / Operating_PR: header row 2, 230 rows, 2 coal; columns missing: none
- august / Planned: not read
- august / Planned_PR: not read
- august / Retired: header row 2, 7,338 rows, 908 coal; columns missing: status
- august / Retired_PR: header row 2, 12 rows, 0 coal; columns missing: status
