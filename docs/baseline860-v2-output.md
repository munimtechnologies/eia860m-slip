# The annual EIA-860's own plan against January's EIA-860M plan

baseline860 0.1.0 on eia860m-slip 0.3.1 annual flows and annual860 0.1.1; annual data out_eia__yearly_generators.parquet (report years 2001-2026). MV2 of Munim, Inc. (made with AI agents).

Annual plan for year Y: generators the annual EIA-860 for Y - 1 lists as planned (P, L, T, U, V, TS, OT) with a current planned operating month in Y. share_in_year: MW whose annual operating month is in Y / annual plan. both: also in January's EIA-860M plan for Y (same key). share_860m: (online_in_year + rekeyed_online) / January's EIA-860M plan, as in docs/annual-flows.md.

Annual records by data_maturity before EIA-860M rows were left out: {"final": 628543, "incremental_ytd": 2608, "monthly_update": 35635}; kept 628545.

## Every year: the two plans and their overlap (MW)

| year | group | baseline_mw | share_in_year | both_mw | both_share_in_year | annual_only_mw | annual_only_share_in_year | plan_860m_mw | share_860m | m_only_mw | m_only_share_860m |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2017 | all | 26808.6 | 0.800 | 21181.4 | 0.787 | 5627.2 | 0.851 | 26268.8 | 0.638 | 5420.2 | 0.038 |
| 2017 | battery | 164.9 | 0.699 | 105.6 | 0.812 | 59.3 | 0.497 | 128.6 | 0.744 | 23.0 | 0.000 |
| 2017 | gas_cc | 11407.2 | 0.747 | 11407.2 | 0.747 | 0.000 |  | 13030.6 | 0.661 | 1654.2 | 0.073 |
| 2017 | gas_ct | 1709.0 | 0.620 | 911.7 | 0.398 | 797.3 | 0.875 | 1001.7 | 0.362 | 90.0 | 0.000 |
| 2017 | solar | 5309.0 | 0.747 | 3435.5 | 0.804 | 1873.5 | 0.641 | 4430.2 | 0.629 | 1192.0 | 0.013 |
| 2017 | wind_onshore | 6928.1 | 0.950 | 4743.9 | 0.932 | 2184.2 | 0.987 | 6858.3 | 0.625 | 2252.4 | 0.000 |
| 2018 | all | 37113.4 | 0.863 | 30333.9 | 0.885 | 6779.5 | 0.765 | 35982.4 | 0.770 | 5565.3 | 0.136 |
| 2018 | battery | 211.4 | 0.788 | 84.1 | 0.951 | 127.3 | 0.679 | 84.1 | 0.988 | 0.000 |  |
| 2018 | gas_cc | 19846.7 | 0.955 | 19846.7 | 0.955 | 0.000 |  | 20332.7 | 0.956 | 555.0 | 1.000 |
| 2018 | gas_ct | 2337.8 | 0.828 | 2190.8 | 0.816 | 147.0 | 1.000 | 4478.7 | 0.399 | 2288.9 | 0.000 |
| 2018 | solar | 5787.6 | 0.749 | 3811.7 | 0.675 | 1975.9 | 0.893 | 4305.5 | 0.632 | 482.8 | 0.000 |
| 2018 | wind_onshore | 7956.7 | 0.733 | 3568.2 | 0.776 | 4388.5 | 0.699 | 6046.3 | 0.518 | 2205.9 | 0.091 |
| 2019 | all | 27422.9 | 0.735 | 22193.7 | 0.792 | 5229.2 | 0.494 | 24826.1 | 0.713 | 2552.6 | 0.001 |
| 2019 | battery | 203.6 | 0.575 | 129.9 | 0.463 | 73.7 | 0.771 | 137.4 | 0.641 | 7.800 | 0.179 |
| 2019 | gas_cc | 6515.1 | 0.806 | 6515.1 | 0.806 | 0.000 |  | 6564.2 | 0.805 | 17.3 | 0.000 |
| 2019 | gas_ct | 1834.5 | 0.834 | 1788.0 | 0.846 | 46.5 | 0.355 | 1955.5 | 0.822 | 100.0 | 0.000 |
| 2019 | solar | 5806.4 | 0.764 | 3942.3 | 0.774 | 1864.1 | 0.741 | 4991.2 | 0.612 | 1047.9 | 0.000 |
| 2019 | wind_onshore | 12323.0 | 0.665 | 9180.0 | 0.780 | 3143.0 | 0.329 | 10460.1 | 0.679 | 1333.1 | 0.000 |
| 2020 | all | 45840.9 | 0.651 | 35511.2 | 0.657 | 10329.7 | 0.630 | 42753.9 | 0.569 | 6843.6 | 0.039 |
| 2020 | battery | 1057.8 | 0.343 | 96.5 | 0.650 | 961.3 | 0.312 | 392.9 | 0.159 | 296.7 | 0.000 |
| 2020 | gas_cc | 6019.8 | 0.838 | 5828.6 | 0.833 | 191.2 | 1.000 | 6145.0 | 0.914 | 274.5 | 0.000 |
| 2020 | gas_ct | 1135.0 | 0.665 | 1035.9 | 0.633 | 99.1 | 1.000 | 1079.3 | 0.608 | 43.4 | 0.000 |
| 2020 | solar | 13544.3 | 0.712 | 9955.0 | 0.688 | 3589.3 | 0.777 | 12964.9 | 0.516 | 3011.3 | 0.013 |
| 2020 | wind_onshore | 23641.2 | 0.579 | 18197.7 | 0.582 | 5443.5 | 0.570 | 21584.9 | 0.507 | 3051.2 | 0.075 |
| 2021 | all | 45495.2 | 0.760 | 37299.8 | 0.783 | 8195.4 | 0.655 | 43181.4 | 0.694 | 5560.8 | 0.001 |
| 2021 | battery | 4391.9 | 0.690 | 3392.0 | 0.686 | 999.9 | 0.701 | 4066.5 | 0.572 | 675.0 | 0.000 |
| 2021 | gas_cc | 4175.1 | 0.892 | 3175.1 | 0.859 | 1000.0 | 1.000 | 3940.0 | 0.690 | 771.0 | 0.000 |
| 2021 | gas_ct | 2576.6 | 0.929 | 2454.3 | 0.925 | 122.3 | 1.000 | 2560.4 | 0.889 | 100.0 | 0.000 |
| 2021 | solar | 16345.0 | 0.763 | 13885.4 | 0.792 | 2459.6 | 0.601 | 15937.0 | 0.708 | 1762.7 | 0.002 |
| 2021 | wind_onshore | 17639.2 | 0.721 | 14128.2 | 0.761 | 3511.0 | 0.561 | 15238.2 | 0.738 | 1077.6 | 0.000 |
| 2022 | all | 44620.7 | 0.601 | 34863.6 | 0.596 | 9757.1 | 0.616 | 46461.4 | 0.487 | 11620.3 | 0.001 |
| 2022 | battery | 6029.2 | 0.579 | 4583.5 | 0.616 | 1445.7 | 0.460 | 5852.4 | 0.494 | 1201.2 | 0.000 |
| 2022 | gas_cc | 8596.3 | 0.460 | 8580.8 | 0.459 | 15.5 | 1.000 | 8580.8 | 0.594 | 0.000 |  |
| 2022 | gas_ct | 1482.0 | 0.732 | 1093.2 | 0.636 | 388.8 | 1.000 | 1790.4 | 0.388 | 715.0 | 0.000 |
| 2022 | solar | 16345.5 | 0.618 | 12766.5 | 0.608 | 3579.0 | 0.653 | 19742.9 | 0.398 | 7029.4 | 0.001 |
| 2022 | wind_onshore | 11811.6 | 0.666 | 7594.4 | 0.708 | 4217.2 | 0.592 | 9053.5 | 0.650 | 1459.1 | 0.000 |
| 2023 | all | 52775.4 | 0.729 | 40861.8 | 0.727 | 11913.6 | 0.736 | 52145.7 | 0.602 | 10796.3 | 0.011 |
| 2023 | battery | 9644.3 | 0.658 | 6744.2 | 0.677 | 2900.1 | 0.612 | 8665.1 | 0.560 | 1851.4 | 0.000 |
| 2023 | gas_cc | 6847.5 | 1.000 | 6201.5 | 1.000 | 646.0 | 1.000 | 6594.9 | 1.000 | 0.000 |  |
| 2023 | gas_ct | 1493.0 | 0.863 | 1491.4 | 0.864 | 1.600 | 0.000 | 1491.4 | 0.864 | 0.000 |  |
| 2023 | solar | 24835.3 | 0.678 | 18219.0 | 0.655 | 6616.3 | 0.741 | 25616.0 | 0.491 | 7389.0 | 0.017 |
| 2023 | wind_onshore | 8255.3 | 0.695 | 6668.1 | 0.653 | 1587.2 | 0.873 | 7074.0 | 0.667 | 389.2 | 0.000 |
| 2024 | all | 64633.7 | 0.717 | 48188.8 | 0.717 | 16444.9 | 0.719 | 59102.8 | 0.595 | 10844.9 | 0.013 |
| 2024 | battery | 15349.8 | 0.663 | 11427.5 | 0.674 | 3922.3 | 0.633 | 14620.9 | 0.511 | 3601.1 | 0.004 |
| 2024 | gas_cc | 97.8 | 1.000 | 97.8 | 1.000 | 0.000 |  | 97.8 | 1.000 | 0.000 |  |
| 2024 | gas_ct | 2336.8 | 0.774 | 2149.0 | 0.754 | 187.8 | 1.000 | 2150.6 | 0.754 | 1.600 | 0.000 |
| 2024 | solar | 38496.4 | 0.718 | 28737.0 | 0.712 | 9759.4 | 0.735 | 34325.0 | 0.621 | 5110.6 | 0.025 |
| 2024 | wind_onshore | 6324.3 | 0.773 | 4048.5 | 0.789 | 2275.8 | 0.745 | 5309.7 | 0.601 | 1262.2 | 0.000 |
| 2025 | all | 65101.5 | 0.745 | 52598.3 | 0.719 | 12503.2 | 0.857 | 60890.9 | 0.627 | 8616.4 | 0.031 |
| 2025 | battery | 19395.9 | 0.743 | 16362.9 | 0.727 | 3033.0 | 0.829 | 19580.0 | 0.610 | 3437.0 | 0.044 |
| 2025 | gas_cc | 1595.7 | 1.000 | 1595.7 | 1.000 | 0.000 |  | 1612.0 | 0.990 | 16.3 | 0.000 |
| 2025 | gas_ct | 3007.5 | 0.863 | 2617.9 | 0.991 | 389.6 | 0.000 | 2617.5 | 0.991 | 0.000 |  |
| 2025 | solar | 32705.7 | 0.737 | 25925.7 | 0.692 | 6780.0 | 0.910 | 29296.8 | 0.610 | 3472.2 | 0.034 |
| 2025 | wind_onshore | 6834.9 | 0.749 | 4682.6 | 0.691 | 2152.3 | 0.877 | 5575.2 | 0.647 | 895.0 | 0.000 |

## Every year: the annual plan by annual class (MW)

| year | group | baseline_mw | before | in_year | next_year | later | undated | never | not_in_860 |
|---|---|---|---|---|---|---|---|---|---|
| 2017 | all | 26808.6 | 0.000 | 21451.1 | 4978.6 | 38.8 | 0.000 | 340.1 | 0.000 |
| 2017 | battery | 164.9 | 0.000 | 115.2 | 19.8 | 9.900 | 0.000 | 20.0 | 0.000 |
| 2017 | gas_cc | 11407.2 | 0.000 | 8517.4 | 2889.8 | 0.000 | 0.000 | 0.000 | 0.000 |
| 2017 | gas_ct | 1709.0 | 0.000 | 1060.3 | 648.7 | 0.000 | 0.000 | 0.000 | 0.000 |
| 2017 | solar | 5309.0 | 0.000 | 3964.0 | 1158.7 | 21.6 | 0.000 | 164.7 | 0.000 |
| 2017 | wind_onshore | 6928.1 | 0.000 | 6578.2 | 194.5 | 0.000 | 0.000 | 155.4 | 0.000 |
| 2018 | all | 37113.4 | 597.1 | 32022.3 | 2887.7 | 368.6 | 0.000 | 1237.7 | 0.000 |
| 2018 | battery | 211.4 | 0.000 | 166.5 | 33.9 | 1.000 | 0.000 | 10.0 | 0.000 |
| 2018 | gas_cc | 19846.7 | 0.000 | 18957.3 | 889.4 | 0.000 | 0.000 | 0.000 | 0.000 |
| 2018 | gas_ct | 2337.8 | 0.000 | 1935.2 | 302.6 | 100.0 | 0.000 | 0.000 | 0.000 |
| 2018 | solar | 5787.6 | 0.000 | 4336.2 | 848.3 | 239.4 | 0.000 | 363.7 | 0.000 |
| 2018 | wind_onshore | 7956.7 | 597.1 | 5833.3 | 733.2 | 2.000 | 0.000 | 791.1 | 0.000 |
| 2019 | all | 27422.9 | 804.7 | 20166.6 | 3735.9 | 1037.2 | 0.000 | 1678.5 | 0.000 |
| 2019 | battery | 203.6 | 0.000 | 117.0 | 26.8 | 33.0 | 0.000 | 26.8 | 0.000 |
| 2019 | gas_cc | 6515.1 | 0.000 | 5252.0 | 293.2 | 244.0 | 0.000 | 725.9 | 0.000 |
| 2019 | gas_ct | 1834.5 | 0.000 | 1529.9 | 249.1 | 0.000 | 0.000 | 55.5 | 0.000 |
| 2019 | solar | 5806.4 | 2.300 | 4434.3 | 1034.2 | 200.2 | 0.000 | 135.4 | 0.000 |
| 2019 | wind_onshore | 12323.0 | 802.4 | 8191.8 | 2092.4 | 547.5 | 0.000 | 688.9 | 0.000 |
| 2020 | all | 45840.9 | 0.000 | 29835.7 | 10684.2 | 2921.8 | 0.000 | 2399.2 | 0.000 |
| 2020 | battery | 1057.8 | 0.000 | 362.4 | 373.9 | 316.0 | 0.000 | 5.500 | 0.000 |
| 2020 | gas_cc | 6019.8 | 0.000 | 5045.7 | 0.000 | 240.4 | 0.000 | 733.7 | 0.000 |
| 2020 | gas_ct | 1135.0 | 0.000 | 755.1 | 354.4 | 0.000 | 0.000 | 25.5 | 0.000 |
| 2020 | solar | 13544.3 | 0.000 | 9636.2 | 3175.6 | 260.8 | 0.000 | 471.7 | 0.000 |
| 2020 | wind_onshore | 23641.2 | 0.000 | 13684.1 | 6762.4 | 2091.3 | 0.000 | 1103.4 | 0.000 |
| 2021 | all | 45495.2 | 280.2 | 34559.4 | 7524.3 | 1980.2 | 0.000 | 1151.1 | 0.000 |
| 2021 | battery | 4391.9 | 1.400 | 3028.4 | 1193.2 | 56.8 | 0.000 | 112.1 | 0.000 |
| 2021 | gas_cc | 4175.1 | 0.000 | 3725.9 | 205.2 | 244.0 | 0.000 | 0.000 | 0.000 |
| 2021 | gas_ct | 2576.6 | 0.000 | 2393.1 | 158.0 | 0.000 | 0.000 | 25.5 | 0.000 |
| 2021 | solar | 16345.0 | 80.0 | 12472.7 | 2406.9 | 962.2 | 0.000 | 423.2 | 0.000 |
| 2021 | wind_onshore | 17639.2 | 198.8 | 12719.3 | 3460.8 | 713.2 | 0.000 | 547.1 | 0.000 |
| 2022 | all | 44620.7 | 1.400 | 26801.0 | 11803.1 | 2380.5 | 0.000 | 3634.7 | 0.000 |
| 2022 | battery | 6029.2 | 1.400 | 3487.7 | 1528.4 | 496.5 | 0.000 | 515.2 | 0.000 |
| 2022 | gas_cc | 8596.3 | 0.000 | 3951.1 | 3482.2 | 0.000 | 0.000 | 1163.0 | 0.000 |
| 2022 | gas_ct | 1482.0 | 0.000 | 1084.2 | 397.8 | 0.000 | 0.000 | 0.000 | 0.000 |
| 2022 | solar | 16345.5 | 0.000 | 10099.4 | 4241.4 | 964.4 | 0.000 | 1040.3 | 0.000 |
| 2022 | wind_onshore | 11811.6 | 0.000 | 7871.7 | 2114.8 | 914.1 | 0.000 | 911.0 | 0.000 |
| 2023 | all | 52775.4 | 3.000 | 38472.9 | 9950.5 | 2141.5 | 0.000 | 2207.5 | 0.000 |
| 2023 | battery | 9644.3 | 0.000 | 6344.6 | 2372.7 | 396.0 | 0.000 | 531.0 | 0.000 |
| 2023 | gas_cc | 6847.5 | 0.000 | 6847.5 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 2023 | gas_ct | 1493.0 | 0.000 | 1288.4 | 203.0 | 1.600 | 0.000 | 0.000 | 0.000 |
| 2023 | solar | 24835.3 | 3.000 | 16838.5 | 5223.1 | 1277.2 | 0.000 | 1493.5 | 0.000 |
| 2023 | wind_onshore | 8255.3 | 0.000 | 5737.6 | 1891.4 | 464.2 | 0.000 | 162.1 | 0.000 |
| 2024 | all | 64633.7 | 10.0 | 46366.6 | 11627.7 | 0.000 | 0.000 | 6629.4 | 0.000 |
| 2024 | battery | 15349.8 | 0.000 | 10185.0 | 3521.5 | 0.000 | 0.000 | 1643.3 | 0.000 |
| 2024 | gas_cc | 97.8 | 0.000 | 97.8 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 2024 | gas_ct | 2336.8 | 0.000 | 1808.8 | 528.0 | 0.000 | 0.000 | 0.000 | 0.000 |
| 2024 | solar | 38496.4 | 10.0 | 27625.6 | 6068.4 | 0.000 | 0.000 | 4792.4 | 0.000 |
| 2024 | wind_onshore | 6324.3 | 0.000 | 4888.1 | 1274.1 | 0.000 | 0.000 | 162.1 | 0.000 |
| 2025 | all | 65101.5 | 60.0 | 48527.9 | 6.900 | 0.000 | 0.000 | 16506.7 | 0.000 |
| 2025 | battery | 19395.9 | 0.000 | 14401.4 | 0.000 | 0.000 | 0.000 | 4994.5 | 0.000 |
| 2025 | gas_cc | 1595.7 | 0.000 | 1595.7 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 2025 | gas_ct | 3007.5 | 0.000 | 2594.2 | 0.000 | 0.000 | 0.000 | 413.3 | 0.000 |
| 2025 | solar | 32705.7 | 60.0 | 24118.2 | 4.900 | 0.000 | 0.000 | 8522.6 | 0.000 |
| 2025 | wind_onshore | 6834.9 | 0.000 | 5121.1 | 0.000 | 0.000 | 0.000 | 1713.8 | 0.000 |

## 2017, wind_onshore: largest in the annual plan only

| key | plant | group | mw | cls |
|---|---|---|---|---|
| 61270/RDDRT | Red Dirt Wind Project | wind_onshore | 299.3 | in_year |
| 61269/WT1 | Thunder Ranch Wind Project | wind_onshore | 297.8 | in_year |
| 60414/GEN1 | Bethel Wind Farm LLC | wind_onshore | 276.0 | in_year |
| 61357/RP1 | Red Pine Wind Project | wind_onshore | 200.0 | in_year |
| 61079/1 | Beaver Creek Wind | wind_onshore | 170.0 | in_year |
| 61261/RF1 | Rock Falls Wind Farm LLC | wind_onshore | 154.5 | in_year |
| 61303/BLUFF | Bluff Point Wind Facility | wind_onshore | 119.7 | in_year |
| 60983/BWIND | Buckthorn Wind | wind_onshore | 100.5 | in_year |
| 60905/WT1 | Oliver Wind III, LLC | wind_onshore | 99.3 | in_year |
| 61221/WT1 | Redbed Plains Wind Farm | wind_onshore | 99.1 | in_year |
| 61407/CTNWD | Cottonwood Wind Energy Center | wind_onshore | 89.7 | in_year |
| 61040/WT1 | Twin Buttes II Wind | wind_onshore | 75.0 | in_year |
| 61330/WT1 | Hog Creek Wind Project | wind_onshore | 66.0 | in_year |
| 61222/1 | Golden Hills North Wind Energy Center | wind_onshore | 46.0 | in_year |
| 61039/WT1 | Deerfield Wind LLC | wind_onshore | 30.0 | in_year |

## 2017, wind_onshore: largest in January's EIA-860M plan only

| key | plant | group | mw | state | cls |
|---|---|---|---|---|---|
| 59246/GOOD1 | Goodnight | wind_onshore | 500.0 | slipped | later |
| 59006/MARN | Mariah East | wind_onshore | 230.4 | slipped | never |
| 59007/MAR S | Mariah South | wind_onshore | 230.4 | slipped | never |
| 60317/1 | Grady Wind Energy Center, LLC | wind_onshore | 200.8 | slipped | later |
| 57622/GEN1 | Bright Stalk Wind Farm II | wind_onshore | 200.0 | slipped | never |
| 57623/GEN1 | Bright Stalk Wind Farm I | wind_onshore | 200.0 | slipped | later |
| 58780/1 | Scioto Ridge Wind Farm | wind_onshore | 189.2 | slipped | later |
| 60743/WT1 | Rattlesnake Power, LLC | wind_onshore | 160.0 | slipped | next_year |
| 59296/NWOH2 | Northwest Ohio Wind | wind_onshore | 150.0 | slipped | never |
| 59296/NWOH1 | Northwest Ohio Wind | wind_onshore | 100.0 | slipped | next_year |
| 55352/GEN1 | Alta Mesa Project Phase IV | wind_onshore | 40.0 | slipped | never |
| 58837/WT1 | Na Pua Makani Wind Project | wind_onshore | 25.0 | slipped | later |
| 59813/nan | Black Oak Wind Farm | wind_onshore | 16.1 | not_listed | not_in_860 |
| 57283/WTG2 | Flat Water Wind Farm LLC | wind_onshore | 10.5 | slipped | never |

## 2017, all: largest in the annual plan only

| key | plant | group | mw | cls |
|---|---|---|---|---|
| 7242/2CC | Polk | gas_other | 463.0 | in_year |
| 61270/RDDRT | Red Dirt Wind Project | wind_onshore | 299.3 | in_year |
| 61269/WT1 | Thunder Ranch Wind Project | wind_onshore | 297.8 | in_year |
| 60414/GEN1 | Bethel Wind Farm LLC | wind_onshore | 276.0 | in_year |
| 61357/RP1 | Red Pine Wind Project | wind_onshore | 200.0 | in_year |
| 61079/1 | Beaver Creek Wind | wind_onshore | 170.0 | in_year |
| 61261/RF1 | Rock Falls Wind Farm LLC | wind_onshore | 154.5 | in_year |
| 61303/BLUFF | Bluff Point Wind Facility | wind_onshore | 119.7 | in_year |
| 58063/COGN1 | SABIC Innovative Plastics Mt. Vernon | gas_ct | 108.0 | in_year |
| 60983/BWIND | Buckthorn Wind | wind_onshore | 100.5 | in_year |
| 61422/PV1 | Southampton Solar, LLC | solar | 100.0 | in_year |
| 60905/WT1 | Oliver Wind III, LLC | wind_onshore | 99.3 | in_year |
| 61221/WT1 | Redbed Plains Wind Farm | wind_onshore | 99.1 | in_year |
| 61407/CTNWD | Cottonwood Wind Energy Center | wind_onshore | 89.7 | in_year |
| 61262/STGRT | Stuttgart Solar | solar | 81.0 | next_year |

## 2017, all: largest in January's EIA-860M plan only

| key | plant | group | mw | state | cls |
|---|---|---|---|---|---|
| 59246/GOOD1 | Goodnight | wind_onshore | 500.0 | slipped | later |
| 55524/STG2 | York Energy Center | gas_cc | 419.6 | slipped | later |
| 55524/CTG5 | York Energy Center | gas_cc | 234.9 | slipped | later |
| 55524/CTG6 | York Energy Center | gas_cc | 234.9 | slipped | later |
| 59006/MARN | Mariah East | wind_onshore | 230.4 | slipped | never |
| 59007/MAR S | Mariah South | wind_onshore | 230.4 | slipped | never |
| 991/STG1 | Eagle Valley (IN) | gas_cc | 230.0 | slipped | next_year |
| 991/GT1 | Eagle Valley (IN) | gas_cc | 207.0 | slipped | next_year |
| 991/GT2 | Eagle Valley (IN) | gas_cc | 207.0 | slipped | next_year |
| 60317/1 | Grady Wind Energy Center, LLC | wind_onshore | 200.8 | slipped | later |
| 57622/GEN1 | Bright Stalk Wind Farm II | wind_onshore | 200.0 | slipped | never |
| 57623/GEN1 | Bright Stalk Wind Farm I | wind_onshore | 200.0 | slipped | later |
| 58780/1 | Scioto Ridge Wind Farm | wind_onshore | 189.2 | slipped | later |
| 60743/WT1 | Rattlesnake Power, LLC | wind_onshore | 160.0 | slipped | next_year |
| 59296/NWOH2 | Northwest Ohio Wind | wind_onshore | 150.0 | slipped | never |

## Checks

```
{
 "D1": {
  "missing_columns": [],
  "missing_report_years": [],
  "pass": true
 },
 "D2": {
  "got": {
   "all": 26268.8,
   "wind_onshore": 6858.3
  },
  "pass": true
 },
 "D3": {
  "rows": 101,
  "not_adding_up": 0,
  "pass": true
 },
 "D4": {
  "baseline_2017_mw": 26808.6,
  "range": [
   10000.0,
   50000.0
  ],
  "pass": true
 },
 "all_pass": true
}
```

## Predictions

```
{
 "B1": {
  "baseline_mw": 26808.6,
  "eia_mw": 25100.0,
  "off": 0.0681,
  "max": 0.1,
  "held": true
 },
 "B2": {
  "share_in_year": 0.8002,
  "floor": 0.75,
  "held": true
 },
 "B3": {
  "share_in_year": 0.9495,
  "floor": 0.8,
  "held": true
 },
 "B4": {
  "both_share": 0.6847,
  "max": 0.8,
  "held": true
 },
 "B5": {
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
  "years_annual_above_860m": [
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
 }
}
```
