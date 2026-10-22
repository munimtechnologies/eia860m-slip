# keptreturn 0.1.0: which columns let a returning value back into PUDL's changelog

Descriptive census for docs/heldtrace.md; no prediction is tested. MV2 of Munim, Inc. (made with AI agents).

PUDL file: core_eia860m__changelog_generators.parquet (2631992 bytes, file time 2026-10-15T16:11:49Z, latest report 2026-08).

Records: 224408. Generators: 39903. Kept returns: 442 (no differing column: 0; the generator's last record: 196).

## Columns that differ (a return can count under several)

| column | kept returns |
|---|---|
| winter_capacity_mw | 137 |
| utility_name_eia | 117 |
| summer_capacity_mw | 115 |
| longitude | 63 |
| utility_id_eia | 48 |
| balancing_authority_code_eia | 42 |
| generator_operating_date | 32 |
| planned_generator_retirement_date | 28 |
| plant_name_eia | 28 |
| technology_description | 28 |
| energy_source_code_1 | 27 |
| fuel_type_code_pudl | 27 |
| sector_id_eia | 26 |
| latitude | 21 |
| net_capacity_mwdc | 17 |
| generator_retirement_date | 16 |
| planned_net_summer_capacity_uprate_mw | 13 |
| planned_uprate_date | 13 |
| county | 9 |
| planned_net_summer_capacity_derate_mw | 2 |
| planned_repower_date | 2 |
| energy_storage_capacity_mwh | 1 |
| planned_derate_date | 1 |
| prime_mover_code | 1 |

## Column sets (top 20)

| columns | kept returns |
|---|---|
| summer_capacity_mw+winter_capacity_mw | 86 |
| utility_name_eia | 55 |
| longitude | 34 |
| utility_id_eia+utility_name_eia | 32 |
| generator_operating_date | 24 |
| balancing_authority_code_eia+winter_capacity_mw | 16 |
| energy_source_code_1+fuel_type_code_pudl+technology_description | 16 |
| planned_generator_retirement_date | 16 |
| net_capacity_mwdc | 15 |
| balancing_authority_code_eia | 13 |
| generator_retirement_date | 11 |
| plant_name_eia | 10 |
| planned_net_summer_capacity_uprate_mw+planned_uprate_date+summer_capacity_mw+winter_capacity_mw | 7 |
| summer_capacity_mw | 7 |
| winter_capacity_mw | 7 |
| county+latitude+longitude | 6 |
| latitude+longitude | 6 |
| plant_name_eia+sector_id_eia | 6 |
| sector_id_eia | 6 |
| balancing_authority_code_eia+energy_source_code_1+fuel_type_code_pudl+latitude+longitude+technology_description+winter_capacity_mw | 5 |

## Report months (top 20)

| month | kept returns |
|---|---|
| 2026-01 | 37 |
| 2026-02 | 19 |
| 2017-04 | 16 |
| 2025-02 | 16 |
| 2022-04 | 13 |
| 2022-07 | 11 |
| 2025-03 | 11 |
| 2025-05 | 11 |
| 2023-02 | 10 |
| 2026-03 | 10 |
| 2017-07 | 9 |
| 2019-12 | 9 |
| 2021-01 | 9 |
| 2024-01 | 9 |
| 2016-07 | 8 |
| 2023-01 | 8 |
| 2025-06 | 8 |
| 2026-08 | 8 |
| 2020-01 | 7 |
| 2016-02 | 6 |

## Report years

| year | kept returns |
|---|---|
| 2015 | 1 |
| 2016 | 30 |
| 2017 | 44 |
| 2018 | 19 |
| 2019 | 32 |
| 2020 | 28 |
| 2021 | 27 |
| 2022 | 40 |
| 2023 | 33 |
| 2024 | 36 |
| 2025 | 71 |
| 2026 | 81 |

### 3075/11

| month | status | earlier record | columns that differ |
|---|---|---|---|
| 2017-04 | OA | 2016-07 | longitude |

### 6175/2

| month | status | earlier record | columns that differ |
|---|---|---|---|
| 2019-12 | OA | 2017-03 | summer_capacity_mw, winter_capacity_mw |

### 3082/2

| month | status | earlier record | columns that differ |
|---|---|---|---|
| 2017-04 | OA | 2016-07 | longitude |

### 3925/1

| month | status | earlier record | columns that differ |
|---|---|---|---|
| 2017-04 | OA | 2016-07 | longitude |

### 3655/1

| month | status | earlier record | columns that differ |
|---|---|---|---|
| 2017-07 | OP | 2016-07 | longitude |
