# Why checks K2 and K3 failed in eia860m-slip 0.3.0's first annual-flows run

diag 0.1.2 on eia860m_slip 0.3.0; PUDL EIA-860M changelog to 2026-08. MV2 of Munim, Inc. (made with AI agents). Diagnosis only: nothing here is scored.

## 1. January plans under 0.3.0's and 0.2.0's reading of validity dates

| year | planned_030 | planned_020_rule | ref_020 | only_030_mw | only_030_n | only_020_mw | only_020_n |
|---|---|---|---|---|---|---|---|
| 2017 | 26268.8 | 26236.8 | 26236.8 | 32.0 | 4 | 0.000 | 0 |
| 2018 | 35982.4 | 34723.5 | 34723.5 | 1258.9 | 14 | 0.000 | 0 |
| 2019 | 24826.1 | 24812.1 | 24812.1 | 14.0 | 3 | 0.000 | 0 |
| 2020 | 42753.9 | 42505.9 | 42505.9 | 248.0 | 8 | 0.000 | 0 |
| 2021 | 43181.4 | 42861.4 | 42861.4 | 320.0 | 4 | 0.000 | 0 |
| 2022 | 46461.4 | 46062.1 | 46062.1 | 399.3 | 6 | 0.000 | 0 |
| 2023 | 52145.7 | 52142.9 | 52142.9 | 2.800 | 1 | 0.000 | 0 |
| 2024 | 59102.8 | 59099.8 | 59099.8 | 3.000 | 1 | 0.000 | 0 |
| 2025 | 60890.9 | 60887.1 | 60887.1 | 3.800 | 3 | 0.000 | 0 |

Generators in only one reading (largest first, up to 60):

| year | kind | key | plant | group | status | planned | mw | record_from | valid_until | last_record | one_month |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2017 | only_030 | 60964/PV1 | AEPS1 Solar | solar | T | 2017-08 | 17.0 | 2016-12 | 2017-01 | True | True |
| 2017 | only_030 | 60292/PV1 | Whiteville Solar 2 | solar | P | 2017-06 | 5.000 | 2016-08 | 2017-01 | True | False |
| 2017 | only_030 | 60295/PV1 | Crimson Solar | solar | P | 2017-06 | 5.000 | 2016-08 | 2017-01 | True | False |
| 2017 | only_030 | 60557/PV1 | Peanut Solar | solar | L | 2017-12 | 5.000 | 2016-12 | 2017-01 | True | True |
| 2018 | only_030 | 60671/STG1 | Allen Combined Cycle Plant | gas_cc | U | 2018-06 | 476.9 | 2017-03 | 2018-01 | True | False |
| 2018 | only_030 | 60671/CTG1 | Allen Combined Cycle Plant | gas_cc | U | 2018-06 | 347.0 | 2017-03 | 2018-01 | True | False |
| 2018 | only_030 | 60671/CTG2 | Allen Combined Cycle Plant | gas_cc | U | 2018-06 | 347.0 | 2017-03 | 2018-01 | True | False |
| 2018 | only_030 | 59252/PV1 | Aragonne Solar LLC | solar | L | 2018-12 | 40.0 | 2017-03 | 2018-01 | True | False |
| 2018 | only_030 | 60163/PV1 | Hawk Solar | solar | T | 2018-04 | 5.000 | 2017-04 | 2018-01 | True | False |
| 2018 | only_030 | 60155/PV1 | Signature Solar | solar | T | 2018-04 | 5.000 | 2017-04 | 2018-01 | True | False |
| 2018 | only_030 | 60168/PV1 | Sadie Solar | solar | T | 2018-04 | 5.000 | 2017-04 | 2018-01 | True | False |
| 2018 | only_030 | 60167/PV1 | Carter Solar | solar | T | 2018-04 | 5.000 | 2017-04 | 2018-01 | True | False |
| 2018 | only_030 | 60164/PV1 | Jordan Solar | solar | L | 2018-04 | 5.000 | 2017-04 | 2018-01 | True | False |
| 2018 | only_030 | 60171/PV1 | Clayton Solar | solar | L | 2018-04 | 5.000 | 2017-04 | 2018-01 | True | False |
| 2018 | only_030 | 60174/PV1 | Cardinal Solar | solar | L | 2018-04 | 5.000 | 2017-04 | 2018-01 | True | False |
| 2018 | only_030 | 60175/PV1 | Bonnie Solar | solar | L | 2018-04 | 5.000 | 2017-04 | 2018-01 | True | False |
| 2018 | only_030 | 60176/PV1 | Anna Solar | solar | L | 2018-04 | 5.000 | 2017-04 | 2018-01 | True | False |
| 2018 | only_030 | 60172/PV1 | Christina Solar | solar | L | 2018-04 | 3.000 | 2017-04 | 2018-01 | True | False |
| 2019 | only_030 | 60139/PV1 | Alexis Solar | solar | L | 2019-06 | 5.000 | 2018-10 | 2019-01 | True | False |
| 2019 | only_030 | 60162/PV1 | Wilfork Solar | solar | L | 2019-06 | 5.000 | 2018-10 | 2019-01 | True | False |
| 2019 | only_030 | 60158/PV1 | June Solar | solar | L | 2019-06 | 4.000 | 2018-10 | 2019-01 | True | False |
| 2020 | only_030 | 62796/1 | Arbor Hill II | wind_onshore | V | 2020-02 | 60.0 | 2019-12 | 2020-01 | True | True |
| 2020 | only_030 | 60094/BLCK1 | Blythe Solar III, LLC | solar | U | 2020-06 | 31.2 | 2019-08 | 2020-01 | True | False |
| 2020 | only_030 | 60094/BLCK3 | Blythe Solar III, LLC | solar | U | 2020-10 | 31.2 | 2019-10 | 2020-01 | True | False |
| 2020 | only_030 | 60094/BLCK2 | Blythe Solar III, LLC | solar | U | 2020-08 | 31.2 | 2019-10 | 2020-01 | True | False |
| 2020 | only_030 | 60095/BLCK2 | Blythe Solar IV, LLC | solar | U | 2020-08 | 31.2 | 2019-12 | 2020-01 | True | True |
| 2020 | only_030 | 60095/BLCK1 | Blythe Solar IV, LLC | solar | U | 2020-06 | 31.2 | 2019-12 | 2020-01 | True | True |
| 2020 | only_030 | 60095/BLCK3 | Blythe Solar IV, LLC | solar | U | 2020-10 | 31.2 | 2019-12 | 2020-01 | True | True |
| 2020 | only_030 | 56278/4 | Green Valley LFGTE | other | P | 2020-10 | 0.800 | 2017-03 | 2020-01 | True | False |
| 2021 | only_030 | 62955/GEN2 | Badger Hollow Solar Farm LLC | solar | U | 2021-12 | 150.0 | 2020-12 | 2021-01 | True | True |
| 2021 | only_030 | 62802/GW | Grizzly Wind LLC | wind_onshore | P | 2021-12 | 80.0 | 2019-06 | 2021-01 | True | False |
| 2021 | only_030 | 62808/BBW | Black Bear Wind (MT) | wind_onshore | P | 2021-12 | 80.0 | 2019-06 | 2021-01 | True | False |
| 2021 | only_030 | 60630/PV1 | Howardtown Farm | solar | L | 2021-05 | 10.0 | 2020-03 | 2021-01 | True | False |
| 2022 | only_030 | 63890/ERWE | Edmondson Ranch Wind, LLC | wind_onshore | L | 2022-12 | 293.3 | 2020-11 | 2022-01 | True | False |
| 2022 | only_030 | 64507/OEALD | OETN1 | solar | T | 2022-12 | 100.0 | 2021-02 | 2022-01 | True | False |
| 2022 | only_030 | 64703/GOR1 | Gorham ME 1 | solar | T | 2022-12 | 4.800 | 2021-10 | 2022-01 | True | False |
| 2022 | only_030 | 64941/GEN1 | WAL4279 | gas_ice | V | 2022-03 | 0.400 | 2021-12 | 2022-01 | True | True |
| 2022 | only_030 | 64941/GEN2 | WAL4279 | gas_ice | V | 2022-03 | 0.400 | 2021-12 | 2022-01 | True | True |
| 2022 | only_030 | 64941/GEN3 | WAL4279 | gas_ice | V | 2022-03 | 0.400 | 2021-12 | 2022-01 | True | True |
| 2023 | only_030 | 65356/KLEES | Klees Mill CSG | solar | L | 2023-10 | 2.800 | 2022-11 | 2023-01 | True | False |
| 2024 | only_030 | 1272/10 | Colby City of | oil | TS | 2024-03 | 3.000 | 2023-12 | 2024-01 | True | True |
| 2025 | only_030 | 65148/VCP13 | Dollar Tree Solar One | solar | P | 2025-12 | 2.000 | 2024-12 | 2025-01 | True | True |
| 2025 | only_030 | 67970/MNC14 | Caron Gardens LLC | solar | L | 2025-12 | 0.900 | 2024-12 | 2025-01 | True | True |
| 2025 | only_030 | 67971/MNC15 | Wells Garden | solar | L | 2025-12 | 0.900 | 2024-12 | 2025-01 | True | True |

## 2. Dropped from the plan, new in the year, at the same plants

| year | not_listed_mw | not_listed_at_shared_plant_mw | new_entry_mw | new_entry_at_shared_plant_mw | shared_plants |
|---|---|---|---|---|---|
| 2017 | 425.3 | 34.0 | 4626.7 | 20.0 | 1 |
| 2018 | 3500.3 | 0.000 | 9277.4 | 0.000 | 0 |
| 2019 | 799.0 | 0.500 | 4027.4 | 0.500 | 1 |
| 2020 | 1325.4 | 249.6 | 8355.6 | 274.2 | 2 |
| 2021 | 763.3 | 0.000 | 6384.5 | 0.000 | 0 |
| 2022 | 1104.8 | 0.000 | 8535.6 | 0.000 | 0 |
| 2023 | 302.7 | 0.000 | 12233.5 | 0.000 | 0 |
| 2024 | 1451.1 | 0.000 | 11118.1 | 0.000 | 0 |
| 2025 | 1482.6 | 0.000 | 13300.1 | 0.000 | 0 |

2018 generators at shared plants:

| year | kind | key | group | mw |
|---|---|---|---|---|

## 3. Operating exits

id check rule: 379; 0.3.0 exits: 379; 0.3.0 exits without any retired record (the count K2 compared): 377.

In the id check's count only: 55199/GT8, 55199/GT9
In 0.3.0's count only: 
id check exits with a retired record: 55199/GT8, 55199/GT9

## Records: exits that differ

| report_date | valid_until_date | plant_id_eia | generator_id | capacity_mw | current_planned_generator_operating_date | generator_operating_date | operational_status_code | technology_description | plant_name_eia |
|---|---|---|---|---|---|---|---|---|---|
| 2015-07-01 | 2015-12-01 | 55199 | GT8 | 0.0 |  | 2001-08-01 | OP | Natural Gas Fired Combustion Turbine | Elwood Energy LLC |
| 2015-12-01 | 2016-04-01 | 55199 | GT8 | 0.0 |  | 2001-08-01 | OP | Natural Gas Fired Combustion Turbine | Elwood Energy LLC |
| 2016-04-01 | 2016-07-01 | 55199 | GT8 | 192.0 |  | 2001-08-01 | OP | Natural Gas Fired Combustion Turbine | Elwood Energy LLC |
| 2016-07-01 | 2025-02-01 | 55199 | GT8 | 192.0 |  | 2001-08-01 | OP | Natural Gas Fired Combustion Turbine | Elwood Energy LLC |
| 2025-02-01 | 2025-06-01 | 55199 | GT8 | 192.0 |  | 2001-08-01 | OP | Natural Gas Fired Combustion Turbine | Elwood Energy LLC |
| 2025-06-01 | 2026-01-01 | 55199 | GT8 | 192.0 |  | 2001-08-01 | RE | Natural Gas Fired Combustion Turbine | Elwood Energy LLC |
| 2026-01-01 | 2026-03-01 | 55199 | GT8 | 192.0 |  | 2001-08-01 | RE | Natural Gas Fired Combustion Turbine | Elwood Energy LLC |
| 2026-03-01 | 2026-04-01 | 55199 | GT8 | 192.0 |  | 2001-08-01 | OS | Natural Gas Fired Combustion Turbine | Elwood Energy LLC |
| 2026-04-01 | 2026-05-01 | 55199 | GT8 | 192.0 |  | 2001-08-01 | OS | Natural Gas Fired Combustion Turbine | Elwood Energy LLC |
| 2015-07-01 | 2015-12-01 | 55199 | GT9 | 0.0 |  | 2001-07-01 | OP | Natural Gas Fired Combustion Turbine | Elwood Energy LLC |
| 2015-12-01 | 2016-04-01 | 55199 | GT9 | 0.0 |  | 2001-07-01 | OP | Natural Gas Fired Combustion Turbine | Elwood Energy LLC |
| 2016-04-01 | 2016-07-01 | 55199 | GT9 | 192.0 |  | 2001-07-01 | OP | Natural Gas Fired Combustion Turbine | Elwood Energy LLC |
| 2016-07-01 | 2025-02-01 | 55199 | GT9 | 192.0 |  | 2001-07-01 | OP | Natural Gas Fired Combustion Turbine | Elwood Energy LLC |
| 2025-02-01 | 2025-06-01 | 55199 | GT9 | 192.0 |  | 2001-07-01 | OP | Natural Gas Fired Combustion Turbine | Elwood Energy LLC |
| 2025-06-01 | 2026-01-01 | 55199 | GT9 | 192.0 |  | 2001-07-01 | RE | Natural Gas Fired Combustion Turbine | Elwood Energy LLC |
| 2026-01-01 | 2026-03-01 | 55199 | GT9 | 192.0 |  | 2001-07-01 | RE | Natural Gas Fired Combustion Turbine | Elwood Energy LLC |
| 2026-03-01 | 2026-04-01 | 55199 | GT9 | 192.0 |  | 2001-07-01 | OS | Natural Gas Fired Combustion Turbine | Elwood Energy LLC |
| 2026-04-01 | 2026-05-01 | 55199 | GT9 | 192.0 |  | 2001-07-01 | OS | Natural Gas Fired Combustion Turbine | Elwood Energy LLC |

## Records: largest 2018 generators only 0.3.0 has

| report_date | valid_until_date | plant_id_eia | generator_id | capacity_mw | current_planned_generator_operating_date | generator_operating_date | operational_status_code | technology_description | plant_name_eia |
|---|---|---|---|---|---|---|---|---|---|
| 2015-07-01 | 2015-11-01 | 59252 | PV1 | 0.0 | 2016-12-01 |  | L | Solar Photovoltaic | Aragonne Solar LLC |
| 2015-11-01 | 2015-12-01 | 59252 | PV1 | 0.0 | 2016-12-01 |  | L | Solar Photovoltaic | Aragonne Solar LLC |
| 2015-12-01 | 2016-04-01 | 59252 | PV1 | 0.0 | 2016-12-01 |  | L | Solar Photovoltaic | Aragonne Solar LLC |
| 2016-04-01 | 2016-07-01 | 59252 | PV1 | 40.0 | 2016-12-01 |  | L | Solar Photovoltaic | Aragonne Solar LLC |
| 2016-07-01 | 2017-03-01 | 59252 | PV1 | 40.0 | 2018-12-01 |  | L | Solar Photovoltaic | Aragonne Solar LLC |
| 2017-03-01 | 2018-01-01 | 59252 | PV1 | 40.0 | 2018-12-01 |  | L | Solar Photovoltaic | Aragonne Solar LLC |
| 2016-02-01 | 2016-04-01 | 60155 | PV1 | 0.0 | 2016-11-01 |  | T | Solar Photovoltaic | Signature Solar |
| 2016-04-01 | 2016-07-01 | 60155 | PV1 | 5.0 | 2016-11-01 |  | T | Solar Photovoltaic | Signature Solar |
| 2016-07-01 | 2016-08-01 | 60155 | PV1 | 5.0 | 2017-03-01 |  | T | Solar Photovoltaic | Signature Solar |
| 2016-08-01 | 2016-12-01 | 60155 | PV1 | 5.0 | 2017-04-01 |  | T | Solar Photovoltaic | Signature Solar |
| 2016-12-01 | 2017-03-01 | 60155 | PV1 | 5.0 | 2017-08-01 |  | T | Solar Photovoltaic | Signature Solar |
| 2017-03-01 | 2017-04-01 | 60155 | PV1 | 5.0 | 2017-08-01 |  | T | Solar Photovoltaic | Signature Solar |
| 2017-04-01 | 2018-01-01 | 60155 | PV1 | 5.0 | 2018-04-01 |  | T | Solar Photovoltaic | Signature Solar |
| 2016-02-01 | 2016-04-01 | 60163 | PV1 | 0.0 | 2016-11-01 |  | T | Solar Photovoltaic | Hawk Solar |
| 2016-04-01 | 2016-07-01 | 60163 | PV1 | 5.0 | 2016-11-01 |  | T | Solar Photovoltaic | Hawk Solar |
| 2016-07-01 | 2016-08-01 | 60163 | PV1 | 5.0 | 2017-03-01 |  | T | Solar Photovoltaic | Hawk Solar |
| 2016-08-01 | 2016-12-01 | 60163 | PV1 | 5.0 | 2017-04-01 |  | T | Solar Photovoltaic | Hawk Solar |
| 2016-12-01 | 2017-03-01 | 60163 | PV1 | 5.0 | 2017-08-01 |  | T | Solar Photovoltaic | Hawk Solar |
| 2017-03-01 | 2017-04-01 | 60163 | PV1 | 5.0 | 2017-08-01 |  | T | Solar Photovoltaic | Hawk Solar |
| 2017-04-01 | 2018-01-01 | 60163 | PV1 | 5.0 | 2018-04-01 |  | T | Solar Photovoltaic | Hawk Solar |
| 2016-02-01 | 2016-04-01 | 60164 | PV1 | 0.0 | 2016-12-01 |  | L | Solar Photovoltaic | Jordan Solar |
| 2016-04-01 | 2016-07-01 | 60164 | PV1 | 5.0 | 2016-12-01 |  | L | Solar Photovoltaic | Jordan Solar |
| 2016-07-01 | 2016-08-01 | 60164 | PV1 | 5.0 | 2017-03-01 |  | L | Solar Photovoltaic | Jordan Solar |
| 2016-08-01 | 2016-12-01 | 60164 | PV1 | 5.0 | 2017-04-01 |  | L | Solar Photovoltaic | Jordan Solar |
| 2016-12-01 | 2017-03-01 | 60164 | PV1 | 5.0 | 2017-08-01 |  | L | Solar Photovoltaic | Jordan Solar |
| 2017-03-01 | 2017-04-01 | 60164 | PV1 | 5.0 | 2017-08-01 |  | L | Solar Photovoltaic | Jordan Solar |
| 2017-04-01 | 2018-01-01 | 60164 | PV1 | 5.0 | 2018-04-01 |  | L | Solar Photovoltaic | Jordan Solar |
| 2016-02-01 | 2016-04-01 | 60167 | PV1 | 0.0 | 2016-11-01 |  | T | Solar Photovoltaic | Carter Solar |
| 2016-04-01 | 2016-07-01 | 60167 | PV1 | 5.0 | 2016-11-01 |  | T | Solar Photovoltaic | Carter Solar |
| 2016-07-01 | 2016-08-01 | 60167 | PV1 | 5.0 | 2017-03-01 |  | T | Solar Photovoltaic | Carter Solar |
| 2016-08-01 | 2016-12-01 | 60167 | PV1 | 5.0 | 2017-04-01 |  | T | Solar Photovoltaic | Carter Solar |
| 2016-12-01 | 2017-03-01 | 60167 | PV1 | 5.0 | 2017-08-01 |  | T | Solar Photovoltaic | Carter Solar |
| 2017-03-01 | 2017-04-01 | 60167 | PV1 | 5.0 | 2017-08-01 |  | T | Solar Photovoltaic | Carter Solar |
| 2017-04-01 | 2018-01-01 | 60167 | PV1 | 5.0 | 2018-04-01 |  | T | Solar Photovoltaic | Carter Solar |
| 2016-02-01 | 2016-04-01 | 60168 | PV1 | 0.0 | 2016-11-01 |  | T | Solar Photovoltaic | Sadie Solar |
| 2016-04-01 | 2016-07-01 | 60168 | PV1 | 5.0 | 2016-11-01 |  | T | Solar Photovoltaic | Sadie Solar |
| 2016-07-01 | 2016-08-01 | 60168 | PV1 | 5.0 | 2017-03-01 |  | T | Solar Photovoltaic | Sadie Solar |
| 2016-08-01 | 2016-12-01 | 60168 | PV1 | 5.0 | 2017-04-01 |  | T | Solar Photovoltaic | Sadie Solar |
| 2016-12-01 | 2017-03-01 | 60168 | PV1 | 5.0 | 2017-08-01 |  | T | Solar Photovoltaic | Sadie Solar |
| 2017-03-01 | 2017-04-01 | 60168 | PV1 | 5.0 | 2017-08-01 |  | T | Solar Photovoltaic | Sadie Solar |
| 2017-04-01 | 2018-01-01 | 60168 | PV1 | 5.0 | 2018-04-01 |  | T | Solar Photovoltaic | Sadie Solar |
| 2016-02-01 | 2016-04-01 | 60171 | PV1 | 0.0 | 2016-12-01 |  | L | Solar Photovoltaic | Clayton Solar |
| 2016-04-01 | 2016-07-01 | 60171 | PV1 | 5.0 | 2016-12-01 |  | L | Solar Photovoltaic | Clayton Solar |
| 2016-07-01 | 2016-08-01 | 60171 | PV1 | 5.0 | 2017-03-01 |  | L | Solar Photovoltaic | Clayton Solar |
| 2016-08-01 | 2016-12-01 | 60171 | PV1 | 5.0 | 2017-04-01 |  | L | Solar Photovoltaic | Clayton Solar |
| 2016-12-01 | 2017-03-01 | 60171 | PV1 | 5.0 | 2017-08-01 |  | L | Solar Photovoltaic | Clayton Solar |
| 2017-03-01 | 2017-04-01 | 60171 | PV1 | 5.0 | 2017-08-01 |  | L | Solar Photovoltaic | Clayton Solar |
| 2017-04-01 | 2018-01-01 | 60171 | PV1 | 5.0 | 2018-04-01 |  | L | Solar Photovoltaic | Clayton Solar |
| 2016-02-01 | 2016-04-01 | 60172 | PV1 | 0.0 | 2016-11-01 |  | L | Solar Photovoltaic | Christina Solar |
| 2016-04-01 | 2016-07-01 | 60172 | PV1 | 3.0 | 2016-11-01 |  | L | Solar Photovoltaic | Christina Solar |
| 2016-07-01 | 2016-08-01 | 60172 | PV1 | 3.0 | 2017-03-01 |  | L | Solar Photovoltaic | Christina Solar |
| 2016-08-01 | 2016-12-01 | 60172 | PV1 | 3.0 | 2017-04-01 |  | L | Solar Photovoltaic | Christina Solar |
| 2016-12-01 | 2017-03-01 | 60172 | PV1 | 3.0 | 2017-08-01 |  | L | Solar Photovoltaic | Christina Solar |
| 2017-03-01 | 2017-04-01 | 60172 | PV1 | 3.0 | 2017-08-01 |  | L | Solar Photovoltaic | Christina Solar |
| 2017-04-01 | 2018-01-01 | 60172 | PV1 | 3.0 | 2018-04-01 |  | L | Solar Photovoltaic | Christina Solar |
| 2016-02-01 | 2016-04-01 | 60174 | PV1 | 0.0 | 2016-12-01 |  | L | Solar Photovoltaic | Cardinal Solar |
| 2016-04-01 | 2016-07-01 | 60174 | PV1 | 5.0 | 2016-12-01 |  | L | Solar Photovoltaic | Cardinal Solar |
| 2016-07-01 | 2016-08-01 | 60174 | PV1 | 5.0 | 2017-03-01 |  | L | Solar Photovoltaic | Cardinal Solar |
| 2016-08-01 | 2016-12-01 | 60174 | PV1 | 5.0 | 2017-04-01 |  | L | Solar Photovoltaic | Cardinal Solar |
| 2016-12-01 | 2017-03-01 | 60174 | PV1 | 5.0 | 2017-08-01 |  | L | Solar Photovoltaic | Cardinal Solar |
| 2017-03-01 | 2017-04-01 | 60174 | PV1 | 5.0 | 2017-08-01 |  | L | Solar Photovoltaic | Cardinal Solar |
| 2017-04-01 | 2018-01-01 | 60174 | PV1 | 5.0 | 2018-04-01 |  | L | Solar Photovoltaic | Cardinal Solar |
| 2016-02-01 | 2016-04-01 | 60175 | PV1 | 0.0 | 2016-11-01 |  | L | Solar Photovoltaic | Bonnie Solar |
| 2016-04-01 | 2016-07-01 | 60175 | PV1 | 5.0 | 2016-11-01 |  | L | Solar Photovoltaic | Bonnie Solar |
| 2016-07-01 | 2016-08-01 | 60175 | PV1 | 5.0 | 2017-03-01 |  | L | Solar Photovoltaic | Bonnie Solar |
| 2016-08-01 | 2016-12-01 | 60175 | PV1 | 5.0 | 2017-04-01 |  | L | Solar Photovoltaic | Bonnie Solar |
| 2016-12-01 | 2017-03-01 | 60175 | PV1 | 5.0 | 2017-08-01 |  | L | Solar Photovoltaic | Bonnie Solar |
| 2017-03-01 | 2017-04-01 | 60175 | PV1 | 5.0 | 2017-08-01 |  | L | Solar Photovoltaic | Bonnie Solar |
| 2017-04-01 | 2018-01-01 | 60175 | PV1 | 5.0 | 2018-04-01 |  | L | Solar Photovoltaic | Bonnie Solar |
| 2016-02-01 | 2016-04-01 | 60176 | PV1 | 0.0 | 2016-11-01 |  | L | Solar Photovoltaic | Anna Solar |
| 2016-04-01 | 2016-07-01 | 60176 | PV1 | 5.0 | 2016-11-01 |  | L | Solar Photovoltaic | Anna Solar |
| 2016-07-01 | 2016-08-01 | 60176 | PV1 | 5.0 | 2017-03-01 |  | L | Solar Photovoltaic | Anna Solar |
| 2016-08-01 | 2016-12-01 | 60176 | PV1 | 5.0 | 2017-04-01 |  | L | Solar Photovoltaic | Anna Solar |
| 2016-12-01 | 2017-03-01 | 60176 | PV1 | 5.0 | 2017-08-01 |  | L | Solar Photovoltaic | Anna Solar |
| 2017-03-01 | 2017-04-01 | 60176 | PV1 | 5.0 | 2017-08-01 |  | L | Solar Photovoltaic | Anna Solar |
| 2017-04-01 | 2018-01-01 | 60176 | PV1 | 5.0 | 2018-04-01 |  | L | Solar Photovoltaic | Anna Solar |
| 2016-12-01 | 2017-03-01 | 60671 | CTG1 | 347.0 | 2018-06-01 |  | U | Natural Gas Fired Combined Cycle | Allen Combined Cycle Plant |
| 2017-03-01 | 2018-01-01 | 60671 | CTG1 | 347.0 | 2018-06-01 |  | U | Natural Gas Fired Combined Cycle | Allen Combined Cycle Plant |
| 2016-12-01 | 2017-03-01 | 60671 | CTG2 | 347.0 | 2018-06-01 |  | U | Natural Gas Fired Combined Cycle | Allen Combined Cycle Plant |
| 2017-03-01 | 2018-01-01 | 60671 | CTG2 | 347.0 | 2018-06-01 |  | U | Natural Gas Fired Combined Cycle | Allen Combined Cycle Plant |
| 2016-12-01 | 2017-03-01 | 60671 | STG1 | 476.9 | 2018-06-01 |  | U | Natural Gas Fired Combined Cycle | Allen Combined Cycle Plant |
| 2017-03-01 | 2018-01-01 | 60671 | STG1 | 476.9 | 2018-06-01 |  | U | Natural Gas Fired Combined Cycle | Allen Combined Cycle Plant |

## Records: 2018 gas_cc generators at shared plants

| report_date | valid_until_date | plant_id_eia | generator_id | capacity_mw | current_planned_generator_operating_date | generator_operating_date | operational_status_code | technology_description | plant_name_eia |
|---|---|---|---|---|---|---|---|---|---|

## Records since 2025-11: gas plants 728, 3399, 67262, 160

| report_date | valid_until_date | plant_id_eia | generator_id | capacity_mw | current_planned_generator_operating_date | generator_operating_date | operational_status_code | technology_description | plant_name_eia |
|---|---|---|---|---|---|---|---|---|---|
| 2016-07-01 | 2026-08-01 | 160 | GT1 | 11.5 |  | 1963-02-01 | SB | Natural Gas Fired Combustion Turbine | Apache Station |
| 2016-07-01 | 2026-08-01 | 160 | GT2 | 20.4 |  | 1972-06-01 | SB | Natural Gas Fired Combustion Turbine | Apache Station |
| 2016-07-01 | 2026-08-01 | 160 | GT3 | 78.7 |  | 1975-06-01 | SB | Natural Gas Fired Combustion Turbine | Apache Station |
| 2016-07-01 | 2026-08-01 | 160 | GT4 | 60.5 |  | 2002-10-01 | SB | Natural Gas Fired Combustion Turbine | Apache Station |
| 2025-06-01 | 2026-03-01 | 160 | GT5 | 41.4 |  | 2025-06-01 | OP | Natural Gas Fired Combustion Turbine | Apache Station |
| 2026-03-01 | 2026-08-01 | 160 | GT5 | 60.5 |  | 2025-06-01 | OP | Natural Gas Fired Combustion Turbine | Apache Station |
| 2025-06-01 | 2026-03-01 | 160 | GT6 | 41.4 |  | 2025-06-01 | OP | Natural Gas Fired Combustion Turbine | Apache Station |
| 2026-03-01 | 2026-08-01 | 160 | GT6 | 60.5 |  | 2025-06-01 | OP | Natural Gas Fired Combustion Turbine | Apache Station |
| 2025-08-01 | 2026-01-01 | 160 | GT7 | 41.4 | 2026-12-01 |  | L | Natural Gas Fired Combustion Turbine | Apache Station |
| 2026-01-01 | 2026-05-01 | 160 | GT7 | 51.1 | 2027-06-01 |  | L | Natural Gas Fired Combustion Turbine | Apache Station |
| 2025-08-01 | 2026-01-01 | 160 | GT8 | 41.4 | 2026-12-01 |  | L | Natural Gas Fired Combustion Turbine | Apache Station |
| 2026-01-01 | 2026-05-01 | 160 | GT8 | 51.1 | 2027-06-01 |  | L | Natural Gas Fired Combustion Turbine | Apache Station |
| 2016-07-01 | 2026-08-01 | 160 | ST1 | 81.6 |  | 1964-11-01 | SB | Natural Gas Steam Turbine | Apache Station |
| 2018-12-01 | 2026-08-01 | 160 | ST2 | 204.0 |  | 1979-01-01 | OP | Natural Gas Steam Turbine | Apache Station |
| 2016-07-01 | 2026-08-01 | 160 | ST3 | 204.0 |  | 1979-09-01 | OP | Conventional Steam Coal | Apache Station |
| 2021-07-01 | 2026-08-01 | 3399 | 1 | 1300.0 |  | 1973-03-01 | OP | Conventional Steam Coal | Cumberland (TN) |
| 2021-07-01 | 2026-07-01 | 3399 | 2 | 1300.0 |  | 1973-11-01 | OP | Conventional Steam Coal | Cumberland (TN) |
| 2026-07-01 | 2026-08-01 | 3399 | 2 | 1300.0 |  | 1973-11-01 | OP | Conventional Steam Coal | Cumberland (TN) |
| 2025-03-01 | 2026-07-01 | 3399 | CTG1 | 454.8 | 2026-12-01 |  | U | Natural Gas Fired Combined Cycle | Cumberland (TN) |
| 2026-07-01 | 2026-08-01 | 3399 | CTG1 | 454.8 | 2034-12-01 |  | U | Natural Gas Fired Combined Cycle | Cumberland (TN) |
| 2025-03-01 | 2026-08-01 | 3399 | CTG2 | 454.8 | 2029-01-01 |  | P | Natural Gas Fired Combined Cycle | Cumberland (TN) |
| 2025-03-01 | 2026-07-01 | 3399 | STG1 | 323.0 | 2026-12-01 |  | U | Natural Gas Fired Combined Cycle | Cumberland (TN) |
| 2026-07-01 | 2026-08-01 | 3399 | STG1 | 323.0 | 2034-12-01 |  | U | Natural Gas Fired Combined Cycle | Cumberland (TN) |
| 2025-03-01 | 2026-08-01 | 3399 | STG2 | 323.0 | 2029-01-01 |  | P | Natural Gas Fired Combined Cycle | Cumberland (TN) |
| 2025-11-01 | 2026-01-01 | 67262 | RP1 | 419.0 | 2026-10-01 |  | U | Natural Gas Fired Combustion Turbine | Ripley Energy Center |
| 2026-01-01 | 2026-06-01 | 67262 | RP1 | 419.0 | 2026-10-01 |  | V | Natural Gas Fired Combustion Turbine | Ripley Energy Center |
| 2026-06-01 | 2026-08-01 | 67262 | RP1 | 419.0 | 2026-12-01 |  | V | Natural Gas Fired Combustion Turbine | Ripley Energy Center |
| 2026-08-01 | 2026-09-01 | 67262 | RP1 | 419.0 | 2027-03-01 |  | V | Natural Gas Fired Combustion Turbine | Ripley Energy Center |
| 2016-07-01 | 2026-08-01 | 728 | 1 | 122.5 |  | 1950-09-01 | RE | Conventional Steam Coal | Yates |
| 2024-08-01 | 2026-08-01 | 728 | 10 | 482.8 | 2027-12-01 |  | P | Natural Gas Fired Combustion Turbine | Yates |
| 2016-07-01 | 2026-08-01 | 728 | 2 | 122.5 |  | 1950-11-01 | RE | Conventional Steam Coal | Yates |
| 2016-07-01 | 2026-08-01 | 728 | 3 | 122.5 |  | 1952-08-01 | RE | Conventional Steam Coal | Yates |
| 2016-07-01 | 2026-08-01 | 728 | 4 | 156.2 |  | 1957-06-01 | RE | Conventional Steam Coal | Yates |
| 2016-07-01 | 2026-08-01 | 728 | 5 | 156.2 |  | 1958-05-01 | RE | Conventional Steam Coal | Yates |
| 2017-05-01 | 2026-08-01 | 728 | 6 | 403.7 |  | 1974-07-01 | OP | Natural Gas Steam Turbine | Yates |
| 2017-05-01 | 2026-08-01 | 728 | 7 | 403.7 |  | 1974-04-01 | OP | Natural Gas Steam Turbine | Yates |
| 2024-08-01 | 2026-02-01 | 728 | 8 | 482.8 | 2026-12-01 |  | P | Natural Gas Fired Combustion Turbine | Yates |
| 2026-02-01 | 2026-08-01 | 728 | 8 | 482.8 | 2026-12-01 |  | V | Natural Gas Fired Combustion Turbine | Yates |
| 2026-08-01 | 2026-09-01 | 728 | 8 | 482.8 | 2027-02-01 |  | V | Natural Gas Fired Combustion Turbine | Yates |
| 2024-08-01 | 2026-08-01 | 728 | 9 | 482.8 | 2027-12-01 |  | P | Natural Gas Fired Combustion Turbine | Yates |

