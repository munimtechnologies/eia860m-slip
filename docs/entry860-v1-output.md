# Where the annual EIA-860's plan-only projects stood in EIA-860M

entry860 0.1.0 on baseline860 0.1.0, annual860 0.1.1 and eia860m-slip 0.3.1; annual data out_eia__yearly_generators.parquet (report years 2001-2026). MV2 of Munim, Inc. (made with AI agents).

annual_only: generators in the annual EIA-860's plan for Y (report year Y - 1, planned for a month in Y) that January's EIA-860M plan for Y does not hold, as in docs/annual-flows-eia860-baseline.md. Entry classes are read from the EIA-860M changelog (January = the report for January of Y). after_share: entered_after_january / annual_only. Bands are of the first EIA-860M record (building = U, V, TS). new_entry: the year's EIA-860M additions not listed in January (eia860m_slip 0.3.1, rule R applied); in_annual_plan: in the year's annual plan, any group.

Annual records by data_maturity before EIA-860M rows were left out: {"final": 628543, "incremental_ytd": 2608, "monthly_update": 35635}; kept 628545.

## Every year: the annual-only part by entry class (MW)

| year | group | baseline_mw | annual_only_mw | in_january_not_planned | in_january_other_month | in_january_planned_in_year | entered_after_january | listed_before_not_in_january | never_in_860m | after_share |
|---|---|---|---|---|---|---|---|---|---|---|
| 2017 | all | 26808.6 | 5627.2 | 1436.3 | 652.0 | 0.000 | 3530.1 | 0.000 | 8.800 | 0.627 |
| 2017 | battery | 164.9 | 59.3 | 10.0 | 0.000 | 0.000 | 49.3 | 0.000 | 0.000 | 0.831 |
| 2017 | gas_cc | 11407.2 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |  |
| 2017 | gas_ct | 1709.0 | 797.3 | 108.0 | 562.0 | 0.000 | 127.3 | 0.000 | 0.000 | 0.160 |
| 2017 | solar | 5309.0 | 1873.5 | 312.3 | 90.0 | 0.000 | 1462.4 | 0.000 | 8.800 | 0.781 |
| 2017 | wind_onshore | 6928.1 | 2184.2 | 375.3 | 0.000 | 0.000 | 1808.9 | 0.000 | 0.000 | 0.828 |
| 2018 | all | 37113.4 | 6779.5 | 1618.9 | 482.2 | 0.000 | 4666.4 | 12.0 | 0.000 | 0.688 |
| 2018 | battery | 211.4 | 127.3 | 19.8 | 0.000 | 0.000 | 97.5 | 10.0 | 0.000 | 0.766 |
| 2018 | gas_cc | 19846.7 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |  |
| 2018 | gas_ct | 2337.8 | 147.0 | 7.800 | 0.000 | 0.000 | 139.2 | 0.000 | 0.000 | 0.947 |
| 2018 | solar | 5787.6 | 1975.9 | 741.3 | 482.2 | 0.000 | 750.4 | 2.000 | 0.000 | 0.380 |
| 2018 | wind_onshore | 7956.7 | 4388.5 | 810.6 | 0.000 | 0.000 | 3577.9 | 0.000 | 0.000 | 0.815 |
| 2019 | all | 27422.9 | 5229.2 | 1670.6 | 461.4 | 0.000 | 3067.2 | 30.0 | 0.000 | 0.587 |
| 2019 | battery | 203.6 | 73.7 | 14.1 | 0.000 | 0.000 | 59.6 | 0.000 | 0.000 | 0.809 |
| 2019 | gas_cc | 6515.1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |  |
| 2019 | gas_ct | 1834.5 | 46.5 | 0.000 | 0.000 | 0.000 | 16.5 | 30.0 | 0.000 | 0.355 |
| 2019 | solar | 5806.4 | 1864.1 | 650.0 | 155.0 | 0.000 | 1059.1 | 0.000 | 0.000 | 0.568 |
| 2019 | wind_onshore | 12323.0 | 3143.0 | 922.8 | 303.4 | 0.000 | 1916.8 | 0.000 | 0.000 | 0.610 |
| 2020 | all | 45840.9 | 10329.7 | 2084.3 | 621.7 | 0.000 | 7158.8 | 464.9 | 0.000 | 0.693 |
| 2020 | battery | 1057.8 | 961.3 | 9.900 | 300.0 | 0.000 | 647.4 | 4.000 | 0.000 | 0.673 |
| 2020 | gas_cc | 6019.8 | 191.2 | 191.2 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 2020 | gas_ct | 1135.0 | 99.1 | 99.1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 2020 | solar | 13544.3 | 3589.3 | 1047.7 | 302.9 | 0.000 | 2238.7 | 0.000 | 0.000 | 0.624 |
| 2020 | wind_onshore | 23641.2 | 5443.5 | 726.4 | 0.000 | 0.000 | 4261.2 | 455.9 | 0.000 | 0.783 |
| 2021 | all | 45495.2 | 8195.4 | 2599.6 | 252.0 | 0.000 | 5337.3 | 6.500 | 0.000 | 0.651 |
| 2021 | battery | 4391.9 | 999.9 | 137.5 | 0.000 | 0.000 | 855.9 | 6.500 | 0.000 | 0.856 |
| 2021 | gas_cc | 4175.1 | 1000.0 | 1000.0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 2021 | gas_ct | 2576.6 | 122.3 | 0.000 | 0.000 | 0.000 | 122.3 | 0.000 | 0.000 | 1.000 |
| 2021 | solar | 16345.0 | 2459.6 | 351.0 | 252.0 | 0.000 | 1856.6 | 0.000 | 0.000 | 0.755 |
| 2021 | wind_onshore | 17639.2 | 3511.0 | 1094.1 | 0.000 | 0.000 | 2416.9 | 0.000 | 0.000 | 0.688 |
| 2022 | all | 44620.7 | 9757.1 | 2129.9 | 435.3 | 0.000 | 7141.9 | 10.0 | 40.0 | 0.732 |
| 2022 | battery | 6029.2 | 1445.7 | 80.3 | 12.0 | 0.000 | 1313.4 | 0.000 | 40.0 | 0.908 |
| 2022 | gas_cc | 8596.3 | 15.5 | 0.000 | 0.000 | 0.000 | 15.5 | 0.000 | 0.000 | 1.000 |
| 2022 | gas_ct | 1482.0 | 388.8 | 69.8 | 0.000 | 0.000 | 319.0 | 0.000 | 0.000 | 0.821 |
| 2022 | solar | 16345.5 | 3579.0 | 878.3 | 278.3 | 0.000 | 2412.4 | 10.0 | 0.000 | 0.674 |
| 2022 | wind_onshore | 11811.6 | 4217.2 | 1101.5 | 145.0 | 0.000 | 2970.7 | 0.000 | 0.000 | 0.704 |
| 2023 | all | 52775.4 | 11913.6 | 2139.6 | 184.0 | 0.000 | 9565.0 | 25.0 | 0.000 | 0.803 |
| 2023 | battery | 9644.3 | 2900.1 | 65.3 | 0.000 | 0.000 | 2809.8 | 25.0 | 0.000 | 0.969 |
| 2023 | gas_cc | 6847.5 | 646.0 | 244.0 | 0.000 | 0.000 | 402.0 | 0.000 | 0.000 | 0.622 |
| 2023 | gas_ct | 1493.0 | 1.600 | 0.000 | 0.000 | 0.000 | 1.600 | 0.000 | 0.000 | 1.000 |
| 2023 | solar | 24835.3 | 6616.3 | 1161.3 | 182.0 | 0.000 | 5273.0 | 0.000 | 0.000 | 0.797 |
| 2023 | wind_onshore | 8255.3 | 1587.2 | 651.0 | 0.000 | 0.000 | 936.2 | 0.000 | 0.000 | 0.590 |
| 2024 | all | 64633.7 | 16444.9 | 3783.1 | 1629.8 | 0.000 | 11032.0 | 0.000 | 0.000 | 0.671 |
| 2024 | battery | 15349.8 | 3922.3 | 9.900 | 100.0 | 0.000 | 3812.4 | 0.000 | 0.000 | 0.972 |
| 2024 | gas_cc | 97.8 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |  |
| 2024 | gas_ct | 2336.8 | 187.8 | 0.000 | 88.0 | 0.000 | 99.8 | 0.000 | 0.000 | 0.531 |
| 2024 | solar | 38496.4 | 9759.4 | 2952.8 | 1441.8 | 0.000 | 5364.8 | 0.000 | 0.000 | 0.550 |
| 2024 | wind_onshore | 6324.3 | 2275.8 | 801.2 | 0.000 | 0.000 | 1474.6 | 0.000 | 0.000 | 0.648 |
| 2025 | all | 65101.5 | 12503.2 | 4296.5 | 911.8 | 0.000 | 7294.9 | 0.000 | 0.000 | 0.583 |
| 2025 | battery | 19395.9 | 3033.0 | 216.2 | 95.4 | 0.000 | 2721.4 | 0.000 | 0.000 | 0.897 |
| 2025 | gas_cc | 1595.7 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |  |
| 2025 | gas_ct | 3007.5 | 389.6 | 0.000 | 0.000 | 0.000 | 389.6 | 0.000 | 0.000 | 1.000 |
| 2025 | solar | 32705.7 | 6780.0 | 2823.3 | 690.4 | 0.000 | 3266.3 | 0.000 | 0.000 | 0.482 |
| 2025 | wind_onshore | 6834.9 | 2152.3 | 1193.9 | 126.0 | 0.000 | 832.4 | 0.000 | 0.000 | 0.387 |

## Every year: what entered after January, by its first band (MW)

| year | group | entered_after_january | after_operating | after_building | after_approved | after_early | after_other | after_op_or_building_share | after_in_year_share |
|---|---|---|---|---|---|---|---|---|---|
| 2017 | all | 3530.1 | 336.6 | 1812.5 | 179.7 | 1200.4 | 0.900 | 0.609 | 0.812 |
| 2017 | battery | 49.3 | 13.0 | 16.5 | 19.8 | 0.000 | 0.000 | 0.598 | 0.598 |
| 2017 | gas_cc | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |  |  |
| 2017 | gas_ct | 127.3 | 0.000 | 127.3 | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 |
| 2017 | solar | 1462.4 | 266.8 | 345.9 | 158.5 | 691.2 | 0.000 | 0.419 | 0.584 |
| 2017 | wind_onshore | 1808.9 | 0.000 | 1311.7 | 0.000 | 497.2 | 0.000 | 0.725 | 0.985 |
| 2018 | all | 4666.4 | 107.9 | 1259.1 | 2495.7 | 803.7 | 0.000 | 0.293 | 0.821 |
| 2018 | battery | 97.5 | 20.3 | 11.5 | 15.0 | 50.7 | 0.000 | 0.326 | 0.684 |
| 2018 | gas_cc | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |  |  |
| 2018 | gas_ct | 139.2 | 7.200 | 0.000 | 132.0 | 0.000 | 0.000 | 0.052 | 1.000 |
| 2018 | solar | 750.4 | 78.9 | 120.5 | 198.9 | 352.1 | 0.000 | 0.266 | 0.924 |
| 2018 | wind_onshore | 3577.9 | 1.500 | 1049.9 | 2136.1 | 390.4 | 0.000 | 0.294 | 0.797 |
| 2019 | all | 3067.2 | 111.1 | 318.2 | 1800.6 | 837.3 | 0.000 | 0.140 | 0.494 |
| 2019 | battery | 59.6 | 8.000 | 3.500 | 19.3 | 28.8 | 0.000 | 0.193 | 0.716 |
| 2019 | gas_cc | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |  |  |
| 2019 | gas_ct | 16.5 | 0.000 | 16.5 | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 |
| 2019 | solar | 1059.1 | 103.1 | 74.4 | 487.4 | 394.2 | 0.000 | 0.168 | 0.689 |
| 2019 | wind_onshore | 1916.8 | 0.000 | 213.3 | 1292.2 | 411.3 | 0.000 | 0.111 | 0.372 |
| 2020 | all | 7158.8 | 568.0 | 4079.6 | 979.0 | 1532.2 | 0.000 | 0.649 | 0.594 |
| 2020 | battery | 647.4 | 257.3 | 52.1 | 0.000 | 338.0 | 0.000 | 0.478 | 0.448 |
| 2020 | gas_cc | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |  |  |
| 2020 | gas_ct | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |  |  |
| 2020 | solar | 2238.7 | 304.6 | 825.6 | 522.5 | 586.0 | 0.000 | 0.505 | 0.707 |
| 2020 | wind_onshore | 4261.2 | 0.000 | 3198.1 | 456.5 | 606.6 | 0.000 | 0.750 | 0.557 |
| 2021 | all | 5337.3 | 199.1 | 3235.2 | 1274.9 | 628.1 | 0.000 | 0.643 | 0.524 |
| 2021 | battery | 855.9 | 33.4 | 479.3 | 271.2 | 72.0 | 0.000 | 0.599 | 0.658 |
| 2021 | gas_cc | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |  |  |
| 2021 | gas_ct | 122.3 | 61.8 | 60.5 | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 |
| 2021 | solar | 1856.6 | 72.0 | 861.1 | 373.8 | 549.7 | 0.000 | 0.503 | 0.514 |
| 2021 | wind_onshore | 2416.9 | 0.000 | 1811.8 | 605.1 | 0.000 | 0.000 | 0.750 | 0.445 |
| 2022 | all | 7141.9 | 547.3 | 3658.9 | 894.7 | 2041.0 | 0.000 | 0.589 | 0.513 |
| 2022 | battery | 1313.4 | 301.3 | 463.5 | 548.6 | 0.000 | 0.000 | 0.582 | 0.438 |
| 2022 | gas_cc | 15.5 | 15.5 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 |
| 2022 | gas_ct | 319.0 | 99.0 | 220.0 | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 |
| 2022 | solar | 2412.4 | 89.0 | 1602.3 | 322.4 | 398.7 | 0.000 | 0.701 | 0.578 |
| 2022 | wind_onshore | 2970.7 | 0.000 | 1333.9 | 0.000 | 1636.8 | 0.000 | 0.449 | 0.421 |
| 2023 | all | 9565.0 | 549.2 | 5623.9 | 2686.8 | 705.1 | 0.000 | 0.645 | 0.682 |
| 2023 | battery | 2809.8 | 10.0 | 1787.5 | 622.0 | 390.3 | 0.000 | 0.640 | 0.609 |
| 2023 | gas_cc | 402.0 | 402.0 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 |
| 2023 | gas_ct | 1.600 | 0.000 | 0.000 | 0.000 | 1.600 | 0.000 | 0.000 | 0.000 |
| 2023 | solar | 5273.0 | 134.2 | 3057.4 | 1770.0 | 311.4 | 0.000 | 0.605 | 0.690 |
| 2023 | wind_onshore | 936.2 | 0.000 | 736.2 | 200.0 | 0.000 | 0.000 | 0.786 | 0.785 |
| 2024 | all | 11032.0 | 761.9 | 9528.0 | 390.3 | 351.8 | 0.000 | 0.933 | 0.696 |
| 2024 | battery | 3812.4 | 125.0 | 3652.4 | 14.3 | 20.7 | 0.000 | 0.991 | 0.636 |
| 2024 | gas_cc | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |  |  |
| 2024 | gas_ct | 99.8 | 99.8 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 |
| 2024 | solar | 5364.8 | 327.9 | 4725.0 | 182.8 | 129.1 | 0.000 | 0.942 | 0.745 |
| 2024 | wind_onshore | 1474.6 | 0.000 | 1085.8 | 190.0 | 198.8 | 0.000 | 0.736 | 0.606 |
| 2025 | all | 7294.9 | 289.1 | 5821.5 | 506.3 | 678.0 | 0.000 | 0.838 | 0.795 |
| 2025 | battery | 2721.4 | 0.000 | 2521.4 | 200.0 | 0.000 | 0.000 | 0.926 | 0.809 |
| 2025 | gas_cc | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |  |  |
| 2025 | gas_ct | 389.6 | 0.000 | 389.6 | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 |
| 2025 | solar | 3266.3 | 289.1 | 2208.2 | 92.0 | 677.0 | 0.000 | 0.765 | 0.901 |
| 2025 | wind_onshore | 832.4 | 0.000 | 618.1 | 214.3 | 0.000 | 0.000 | 0.743 | 0.682 |

## Every year: EIA-860M new entries found in the annual plan (MW)

| year | group | new_entry_mw | new_entry_in_annual_plan_mw | new_entry_in_annual_plan_share |
|---|---|---|---|---|
| 2017 | all | 4626.7 | 2871.8 | 0.621 |
| 2017 | battery | 61.0 | 39.4 | 0.646 |
| 2017 | gas_cc | 0.000 | 0.000 |  |
| 2017 | gas_ct | 176.5 | 127.3 | 0.721 |
| 2017 | solar | 2017.7 | 848.2 | 0.420 |
| 2017 | wind_onshore | 2137.8 | 1781.3 | 0.833 |
| 2018 | all | 6135.9 | 3828.4 | 0.624 |
| 2018 | battery | 122.6 | 66.7 | 0.544 |
| 2018 | gas_cc | 0.000 | 0.000 |  |
| 2018 | gas_ct | 185.9 | 139.2 | 0.749 |
| 2018 | solar | 1586.3 | 696.9 | 0.439 |
| 2018 | wind_onshore | 3871.7 | 2834.9 | 0.732 |
| 2019 | all | 4017.4 | 1873.7 | 0.466 |
| 2019 | battery | 137.3 | 42.7 | 0.311 |
| 2019 | gas_cc | 73.4 | 0.000 | 0.000 |
| 2019 | gas_ct | 117.2 | 17.4 | 0.148 |
| 2019 | solar | 2157.4 | 949.6 | 0.440 |
| 2019 | wind_onshore | 1280.7 | 852.2 | 0.665 |
| 2020 | all | 8355.6 | 4266.4 | 0.511 |
| 2020 | battery | 513.6 | 290.0 | 0.565 |
| 2020 | gas_cc | 775.1 | 0.000 | 0.000 |
| 2020 | gas_ct | 417.4 | 0.000 | 0.000 |
| 2020 | solar | 2736.7 | 1528.0 | 0.558 |
| 2020 | wind_onshore | 3487.4 | 2441.1 | 0.700 |
| 2021 | all | 6384.5 | 2815.2 | 0.441 |
| 2021 | battery | 1066.8 | 572.8 | 0.537 |
| 2021 | gas_cc | 0.000 | 0.000 |  |
| 2021 | gas_ct | 1164.5 | 122.3 | 0.105 |
| 2021 | solar | 2274.1 | 965.6 | 0.425 |
| 2021 | wind_onshore | 1638.5 | 1075.8 | 0.657 |
| 2022 | all | 8390.6 | 3815.9 | 0.455 |
| 2022 | battery | 1348.1 | 575.1 | 0.427 |
| 2022 | gas_cc | 1463.2 | 15.5 | 0.011 |
| 2022 | gas_ct | 510.7 | 319.0 | 0.625 |
| 2022 | solar | 2634.3 | 1386.8 | 0.526 |
| 2022 | wind_onshore | 2133.0 | 1410.4 | 0.661 |
| 2023 | all | 12233.5 | 6765.5 | 0.553 |
| 2023 | battery | 2573.0 | 1710.6 | 0.665 |
| 2023 | gas_cc | 402.0 | 402.0 | 1.000 |
| 2023 | gas_ct | 1513.2 | 0.000 | 0.000 |
| 2023 | solar | 6417.5 | 3882.5 | 0.605 |
| 2023 | wind_onshore | 1128.3 | 734.6 | 0.651 |
| 2024 | all | 11118.1 | 7662.0 | 0.689 |
| 2024 | battery | 3008.3 | 2421.0 | 0.805 |
| 2024 | gas_cc | 0.000 | 0.000 |  |
| 2024 | gas_ct | 224.1 | 99.0 | 0.442 |
| 2024 | solar | 6423.3 | 3982.7 | 0.620 |
| 2024 | wind_onshore | 1082.5 | 894.2 | 0.826 |
| 2025 | all | 13300.1 | 5971.3 | 0.449 |
| 2025 | battery | 3871.9 | 2202.9 | 0.569 |
| 2025 | gas_cc | 0.000 | 0.000 |  |
| 2025 | gas_ct | 93.6 | 0.000 | 0.000 |
| 2025 | solar | 7535.0 | 3118.8 | 0.414 |
| 2025 | wind_onshore | 1539.2 | 567.4 | 0.369 |

## 2017: entered after January, by quarter of first report (MW)

```
{
 "all": {
  "2017-Q1": 1135.3,
  "2017-Q2": 1777.4,
  "2017-Q3": 617.4,
  "2017-Q4": 0.0,
  "after_2017": 0.0
 },
 "wind_onshore": {
  "2017-Q1": 411.8,
  "2017-Q2": 1107.4,
  "2017-Q3": 289.7,
  "2017-Q4": 0.0,
  "after_2017": 0.0
 }
}
```

## 2017, wind_onshore: largest annual-only generators

| key | plant | group | mw | entry | first_listed | first_band | cls | online_860 |
|---|---|---|---|---|---|---|---|---|
| 61270/RDDRT | Red Dirt Wind Project | wind_onshore | 299.3 | entered_after_january | 2017-05 | building | in_year | 2017-12 |
| 61269/WT1 | Thunder Ranch Wind Project | wind_onshore | 297.8 | entered_after_january | 2017-05 | building | in_year | 2017-12 |
| 60414/GEN1 | Bethel Wind Farm LLC | wind_onshore | 276.0 | in_january_not_planned | 2016-05 | approved | in_year | 2017-01 |
| 61357/RP1 | Red Pine Wind Project | wind_onshore | 200.0 | entered_after_january | 2017-07 | building | in_year | 2017-12 |
| 61079/1 | Beaver Creek Wind | wind_onshore | 170.0 | entered_after_january | 2017-02 | early | in_year | 2017-12 |
| 61261/RF1 | Rock Falls Wind Farm LLC | wind_onshore | 154.5 | entered_after_january | 2017-04 | early | in_year | 2017-12 |
| 61303/BLUFF | Bluff Point Wind Facility | wind_onshore | 119.7 | entered_after_january | 2017-06 | building | in_year | 2017-12 |
| 60983/BWIND | Buckthorn Wind | wind_onshore | 100.5 | entered_after_january | 2017-02 | building | in_year | 2017-12 |
| 60905/WT1 | Oliver Wind III, LLC | wind_onshore | 99.3 | in_january_not_planned | 2016-12 | building | in_year | 2017-01 |
| 61221/WT1 | Redbed Plains Wind Farm | wind_onshore | 99.1 | entered_after_january | 2017-04 | early | in_year | 2017-07 |
| 61407/CTNWD | Cottonwood Wind Energy Center | wind_onshore | 89.7 | entered_after_january | 2017-08 | building | in_year | 2017-11 |
| 61040/WT1 | Twin Buttes II Wind | wind_onshore | 75.0 | entered_after_january | 2017-02 | building | in_year | 2017-12 |
| 61330/WT1 | Hog Creek Wind Project | wind_onshore | 66.0 | entered_after_january | 2017-06 | building | in_year | 2017-12 |
| 61222/1 | Golden Hills North Wind Energy Center | wind_onshore | 46.0 | entered_after_january | 2017-04 | early | in_year | 2017-11 |
| 61039/WT1 | Deerfield Wind LLC | wind_onshore | 30.0 | entered_after_january | 2017-02 | building | in_year | 2017-12 |

## 2017, wind_onshore: largest new entries not in the annual plan

| key | group | mw |
|---|---|---|
| 60987/GEN1 | wind_onshore | 300.0 |
| 2240/CTNWD | wind_onshore | 40.9 |
| 61668/CR2-1 | wind_onshore | 2.300 |
| 61668/CR2-2 | wind_onshore | 2.300 |
| 61668/CR2-3 | wind_onshore | 2.300 |
| 61644/AUG | wind_onshore | 1.800 |
| 62130/ROS | wind_onshore | 1.800 |
| 62172/BIR | wind_onshore | 1.800 |
| 61056/T1 | wind_onshore | 1.700 |
| 61734/1 | wind_onshore | 1.500 |
| 61990/WIND | wind_onshore | 0.100 |

## 2017, all: largest annual-only generators

| key | plant | group | mw | entry | first_listed | first_band | cls | online_860 |
|---|---|---|---|---|---|---|---|---|
| 7242/2CC | Polk | gas_other | 463.0 | in_january_not_planned | 2015-07 | building | in_year | 2017-01 |
| 61270/RDDRT | Red Dirt Wind Project | wind_onshore | 299.3 | entered_after_january | 2017-05 | building | in_year | 2017-12 |
| 61269/WT1 | Thunder Ranch Wind Project | wind_onshore | 297.8 | entered_after_january | 2017-05 | building | in_year | 2017-12 |
| 60414/GEN1 | Bethel Wind Farm LLC | wind_onshore | 276.0 | in_january_not_planned | 2016-05 | approved | in_year | 2017-01 |
| 61357/RP1 | Red Pine Wind Project | wind_onshore | 200.0 | entered_after_january | 2017-07 | building | in_year | 2017-12 |
| 61079/1 | Beaver Creek Wind | wind_onshore | 170.0 | entered_after_january | 2017-02 | early | in_year | 2017-12 |
| 61261/RF1 | Rock Falls Wind Farm LLC | wind_onshore | 154.5 | entered_after_january | 2017-04 | early | in_year | 2017-12 |
| 61303/BLUFF | Bluff Point Wind Facility | wind_onshore | 119.7 | entered_after_january | 2017-06 | building | in_year | 2017-12 |
| 58063/COGN1 | SABIC Innovative Plastics Mt. Vernon | gas_ct | 108.0 | in_january_not_planned | 2016-12 | building | in_year | 2017-01 |
| 60983/BWIND | Buckthorn Wind | wind_onshore | 100.5 | entered_after_january | 2017-02 | building | in_year | 2017-12 |
| 61422/PV1 | Southampton Solar, LLC | solar | 100.0 | entered_after_january | 2017-08 | early | in_year | 2017-12 |
| 60905/WT1 | Oliver Wind III, LLC | wind_onshore | 99.3 | in_january_not_planned | 2016-12 | building | in_year | 2017-01 |
| 61221/WT1 | Redbed Plains Wind Farm | wind_onshore | 99.1 | entered_after_january | 2017-04 | early | in_year | 2017-07 |
| 61407/CTNWD | Cottonwood Wind Energy Center | wind_onshore | 89.7 | entered_after_january | 2017-08 | building | in_year | 2017-11 |
| 61262/STGRT | Stuttgart Solar | solar | 81.0 | entered_after_january | 2017-04 | building | next_year | 2018-01 |

## 2017, all: largest new entries not in the annual plan

| key | group | mw |
|---|---|---|
| 60987/GEN1 | wind_onshore | 300.0 |
| 59940/GVS2 | solar | 60.0 |
| 61813/RCHLD | solar | 60.0 |
| 61048/PV1 | solar | 56.3 |
| 60989/PV1 | solar | 50.0 |
| 61512/GEN1 | solar | 50.0 |
| 61561/GEN1 | solar | 50.0 |
| 2240/CTNWD | wind_onshore | 40.9 |
| 63285/79G1 | gas_ct | 33.5 |
| 61463/VBERG | solar | 25.3 |
| 59940/GVS3 | solar | 20.0 |
| 59940/GVS4 | solar | 20.0 |
| 61489/CAM | solar | 20.0 |
| 61490/EST1 | solar | 20.0 |
| 61498/HAM2 | solar | 20.0 |

## Checks

```
{
 "E1": {
  "missing_columns": [],
  "got": {
   "2017": [
    26808.6,
    5627.2
   ],
   "2018": [
    37113.4,
    6779.5
   ],
   "2019": [
    27422.9,
    5229.2
   ],
   "2020": [
    45840.9,
    10329.7
   ],
   "2021": [
    45495.2,
    8195.4
   ],
   "2022": [
    44620.7,
    9757.1
   ],
   "2023": [
    52775.4,
    11913.6
   ],
   "2024": [
    64633.7,
    16444.9
   ],
   "2025": [
    65101.5,
    12503.2
   ]
  },
  "expected": {
   "2017": [
    26808.6,
    5627.2
   ],
   "2018": [
    37113.4,
    6779.5
   ],
   "2019": [
    27422.9,
    5229.2
   ],
   "2020": [
    45840.9,
    10329.7
   ],
   "2021": [
    45495.2,
    8195.4
   ],
   "2022": [
    44620.7,
    9757.1
   ],
   "2023": [
    52775.4,
    11913.6
   ],
   "2024": [
    64633.7,
    16444.9
   ],
   "2025": [
    65101.5,
    12503.2
   ]
  },
  "pass": true
 },
 "E2": {
  "rows": 100,
  "not_adding_up": 0,
  "pass": true
 },
 "E3": {
  "in_january_planned_in_year_mw": {
   "2017": 0.0,
   "2018": 0.0,
   "2019": 0.0,
   "2020": 0.0,
   "2021": 0.0,
   "2022": 0.0,
   "2023": 0.0,
   "2024": 0.0,
   "2025": 0.0
  },
  "pass": true
 },
 "E4": {
  "new_entry_2017_mw": 4626.7,
  "expected": 4626.7,
  "pass": true
 },
 "all_pass": true
}
```

## Predictions

```
{
 "A1": {
  "after_share": 0.6273,
  "floor": 0.6,
  "held": true
 },
 "A2": {
  "op_or_building_share": 0.6088,
  "floor": 0.8,
  "held": false
 },
 "A3": {
  "years": [
   2017,
   2018,
   2019,
   2020,
   2021,
   2022,
   2023,
   2024
  ],
  "years_after_share_at_least_half": [
   2017,
   2018,
   2019,
   2020,
   2021,
   2022,
   2023,
   2024
  ],
  "min": 6,
  "held": true
 },
 "A4": {
  "new_entry_in_annual_plan_share": 0.6207,
  "floor": 0.5,
  "held": true
 }
}
```
