# Re-keyed generators: dropped from a January plan under one id, online under another

rekey 0.1.0 on eia860m_slip 0.3.0; PUDL EIA-860M changelog to 2026-08. MV2 of Munim, Inc. (made with AI agents). Diagnosis only: nothing here is scored.

Pass A: same technology group, capacity within 0.05 MW, first listed 0-3 months after the dropped generator's last listed month. Pass B: within 5%, 0-6 months, among what A left. MW are the dropped side unless named otherwise.

## 1. Per year

| year | not_listed_mw | not_listed_n | new_entry_mw | new_entry_n | strict_pairs | strict_mw | loose_pairs | loose_mw | loose_entry_mw | matched_share | cross_plant_pairs | same_name_pairs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2017 | 425.3 | 35 | 4626.7 | 614 | 15 | 58.5 | 5 | 172.7 | 174.4 | 0.544 | 20 | 0 |
| 2018 | 3500.3 | 36 | 9277.4 | 583 | 24 | 3201.9 | 9 | 248.4 | 237.6 | 0.986 | 33 | 0 |
| 2019 | 799.0 | 26 | 4027.4 | 573 | 15 | 61.0 | 4 | 209.0 | 210.1 | 0.338 | 18 | 1 |
| 2020 | 1325.4 | 29 | 8355.6 | 654 | 10 | 16.5 | 2 | 337.4 | 330.0 | 0.267 | 12 | 0 |
| 2021 | 763.3 | 21 | 6384.5 | 786 | 10 | 109.8 | 4 | 29.5 | 29.6 | 0.182 | 14 | 0 |
| 2022 | 1104.8 | 39 | 8535.6 | 448 | 10 | 165.8 | 12 | 155.4 | 153.6 | 0.291 | 22 | 0 |
| 2023 | 302.7 | 23 | 12233.5 | 539 | 7 | 112.0 | 6 | 129.2 | 131.0 | 0.797 | 13 | 0 |
| 2024 | 1451.1 | 24 | 11118.1 | 634 | 6 | 168.0 | 3 | 94.8 | 94.9 | 0.181 | 9 | 0 |
| 2025 | 1482.6 | 22 | 13300.1 | 509 | 7 | 405.5 | 4 | 353.1 | 353.0 | 0.512 | 11 | 0 |
| all | 11154.5 | 255 | 77858.9 | 5340 | 104 | 4299.0 | 49 | 1729.5 | 1714.2 | 0.540 | 152 | 1 |

## 2. Pairs, pass A (strict)

104 pairs.

| year | pass | dropped | dropped_plant | entry | entry_plant | group | dropped_mw | entry_mw | last_listed | first_listed | months_apart | same_plant | same_name |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2017 | A | 60175/PV1 | Bonnie Solar | 61681/10257 | Middle Daisy | solar | 5.000 | 5.000 | 2018-01 | 2018-02 | 1 | False | False |
| 2017 | A | 59895/5MWPV | Louisburg Solar | 61124/EMS1 | Elizabeth Mines Solar 1 | solar | 5.000 | 5.000 | 2017-03 | 2017-03 | 0 | False | False |
| 2017 | A | 60286/PV1 | Climax Solar | 61352/GEN1 | Bondi Solar | solar | 5.000 | 5.000 | 2017-07 | 2017-07 | 0 | False | False |
| 2017 | A | 59970/BLOOM | Bloomsbury Solar, LLC | 61527/GEN1 | Bakatsias Solar | solar | 5.000 | 5.000 | 2017-11 | 2017-11 | 0 | False | False |
| 2017 | A | 60292/PV1 | Whiteville Solar 2 | 59112/1 | West Siler | solar | 5.000 | 5.000 | 2017-01 | 2017-02 | 1 | False | False |
| 2017 | A | 60294/PV1 | Crawford Solar | 61403/1 | Deep Branch Farm | solar | 5.000 | 5.000 | 2017-07 | 2017-08 | 1 | False | False |
| 2017 | A | 60295/PV1 | Crimson Solar | 61008/BROOK | Brook Street Solar 1 CSG | solar | 5.000 | 5.000 | 2017-01 | 2017-02 | 1 | False | False |
| 2017 | A | 60828/PV1 | Osceola Solar, LLC | 61451/NORTH | Northfield Holdco CSG | solar | 5.000 | 5.000 | 2017-09 | 2017-09 | 0 | False | False |
| 2017 | A | 60557/PV1 | Peanut Solar | 61031/PV1 | Floyd Road Solar Farm | solar | 5.000 | 5.000 | 2017-01 | 2017-02 | 1 | False | False |
| 2017 | A | 60172/PV1 | Christina Solar | 61733/HWOOD | Haywood Solar | solar | 3.000 | 3.000 | 2018-01 | 2018-02 | 1 | False | False |
| 2017 | A | 57569/KS1-A | Kalaeloa Solar One | 61069/62381 | BWC Wading River One, Two, Three CSG | solar | 3.000 | 3.000 | 2017-02 | 2017-02 | 0 | False | False |
| 2017 | A | 59883/SOLAR | Thermo Solar PV-01 | 61459/PV1 | Georgia Power at Swainsboro | solar | 2.900 | 2.900 | 2017-09 | 2017-09 | 0 | False | False |
| 2017 | A | 60090/2MWPV | Wallace Solar 2 | 61637/PV1 | Denison Solar Array | solar | 1.900 | 1.900 | 2017-12 | 2018-01 | 1 | False | False |
| 2017 | A | 60950/PV1 | Mountain Lion Solar | 61728/10263 | Barrett Farm Solar - Phase I | solar | 1.700 | 1.700 | 2018-01 | 2018-02 | 1 | False | False |
| 2017 | A | 58256/4 | Los Alamos PV Site | 61298/2112 | Pleasantdale Road Community Solar | solar | 1.000 | 1.000 | 2017-05 | 2017-06 | 1 | False | False |
| 2018 | A | 60671/STG1 | Allen Combined Cycle Plant | 3393/STG1 | Allen | gas_cc | 476.9 | 476.9 | 2018-01 | 2018-02 | 1 | False | False |
| 2018 | A | 60138/CC2ST | Citrus County Combined Cycle Plant | 628/CC1ST | Crystal River | gas_cc | 364.7 | 364.7 | 2018-06 | 2018-07 | 1 | False | False |
| 2018 | A | 60138/CC1ST | Citrus County Combined Cycle Plant | 628/CC2ST | Crystal River | gas_cc | 364.7 | 364.7 | 2018-06 | 2018-07 | 1 | False | False |
| 2018 | A | 60671/CTG1 | Allen Combined Cycle Plant | 3393/CTG1 | Allen | gas_cc | 347.0 | 347.0 | 2018-01 | 2018-02 | 1 | False | False |
| 2018 | A | 60671/CTG2 | Allen Combined Cycle Plant | 3393/CTG2 | Allen | gas_cc | 347.0 | 347.0 | 2018-01 | 2018-02 | 1 | False | False |
| 2018 | A | 60138/2GTB | Citrus County Combined Cycle Plant | 628/1GTA | Crystal River | gas_cc | 310.3 | 310.3 | 2018-06 | 2018-07 | 1 | False | False |
| 2018 | A | 60138/1GTA | Citrus County Combined Cycle Plant | 628/1GTB | Crystal River | gas_cc | 310.3 | 310.3 | 2018-06 | 2018-07 | 1 | False | False |
| 2018 | A | 60138/1GTB | Citrus County Combined Cycle Plant | 628/2GTA | Crystal River | gas_cc | 310.3 | 310.3 | 2018-06 | 2018-07 | 1 | False | False |
| 2018 | A | 60138/2GTA | Citrus County Combined Cycle Plant | 628/2GTB | Crystal River | gas_cc | 310.3 | 310.3 | 2018-06 | 2018-07 | 1 | False | False |
| 2018 | A | 60139/PV1 | Alexis Solar | 62583/5823 | Tanglewood Circle Solar 1 LLC | solar | 5.000 | 5.000 | 2019-01 | 2019-03 | 2 | False | False |
| 2018 | A | 60175/PV1 | Bonnie Solar | 61690/FOREM | Foreman's Hill Community Solar | solar | 5.000 | 5.000 | 2018-01 | 2018-02 | 1 | False | False |
| 2018 | A | 60155/PV1 | Signature Solar | 61762/SHERB | Sherburne North Project CSG | solar | 5.000 | 5.000 | 2018-01 | 2018-03 | 2 | False | False |
| 2018 | A | 60162/PV1 | Wilfork Solar | 62692/PGR04 | Sandy Solar | solar | 5.000 | 5.000 | 2019-01 | 2019-04 | 3 | False | False |
| 2018 | A | 60164/PV1 | Jordan Solar | 61817/BIGLA | Big Lake Project CSG | solar | 5.000 | 5.000 | 2018-01 | 2018-04 | 3 | False | False |
| 2018 | A | 59998/RNDHL | Round Hill PV1 | 61978/GEN1 | Pinesage | solar | 5.000 | 5.000 | 2018-08 | 2018-08 | 0 | False | False |
| 2018 | A | 59216/PV1 | Rhubarb One | 61842/PV1 | Sun Farm VI, LLC | solar | 5.000 | 5.000 | 2018-04 | 2018-05 | 1 | False | False |
| 2018 | A | 61130/12344 | Bear Poplar Solar | 62098/TILLE | Tiller CSG | solar | 5.000 | 5.000 | 2018-08 | 2018-09 | 1 | False | False |
| 2018 | A | 61624/GEN1 | West Moore Solar | 62168/CHU01 | Church Road Solar LLC | solar | 5.000 | 5.000 | 2018-10 | 2018-11 | 1 | False | False |
| 2018 | A | 60158/PV1 | June Solar | 62557/MONTA | Kearsarge Montague | solar | 4.000 | 4.000 | 2019-01 | 2019-02 | 1 | False | False |
| 2018 | A | 60172/PV1 | Christina Solar | 61740/GR01 | Gratis Road Solar Facility | solar | 3.000 | 3.000 | 2018-01 | 2018-02 | 1 | False | False |
| 2018 | A | 61081/PV1 | Lancaster SCE ReMAT | 62056/LANC | Lancaster | solar | 3.000 | 3.000 | 2018-09 | 2018-09 | 0 | False | False |
| 2018 | A | 60780/PV1 | Rowan Solar NC LLC | 62303/MF01 | Mattas Farms | solar | 2.000 | 2.000 | 2018-12 | 2018-12 | 0 | False | False |
| 2018 | A | 61123/SKYR5 | SCWA R5 Pond Solar | 61719/LWCJ1 | CJ Solar I, LLC | solar | 2.000 | 2.000 | 2018-02 | 2018-02 | 0 | False | False |
| 2018 | A | 61317/MB-21 | Farmingdale Fuel Cell | 61786/MB-22 | Trinity College Fuel Cell | gas_other | 1.400 | 1.400 | 2018-03 | 2018-03 | 0 | False | False |
| 2019 | A | 57567/VISTA | Albuquerque Solar Energy Center | 62467/VISTA | Vista Solar Energy Center | solar | 10.0 | 10.0 | 2019-02 | 2019-02 | 0 | False | False |
| 2019 | A | 60139/PV1 | Alexis Solar | 62595/10424 | Wendell Solar Farm LLC | solar | 5.000 | 5.000 | 2019-01 | 2019-03 | 2 | False | False |
| 2019 | A | 60360/51116 | Pike Road Solar | 62596/11999 | Sabattus Solar LLC | solar | 5.000 | 5.000 | 2019-02 | 2019-03 | 1 | False | False |
| 2019 | A | 60162/PV1 | Wilfork Solar | 62600/COOKS | Cookstown | solar | 5.000 | 5.000 | 2019-01 | 2019-03 | 2 | False | False |
| 2019 | A | 60141/PV1 | Izia Solar | 62953/1080 | Griffin Solar | solar | 5.000 | 5.000 | 2019-08 | 2019-08 | 0 | False | False |
| 2019 | A | 60884/HALFX | Halifax Solar LLC | 62602/STARR | Starr | solar | 5.000 | 5.000 | 2019-03 | 2019-03 | 0 | False | False |
| 2019 | A | 60166/PV1 | Higgins Solar | 63000/WALDN | RT 52 Walden Solar 1, LLC Hybrid | solar | 5.000 | 5.000 | 2019-08 | 2019-08 | 0 | False | False |
| 2019 | A | 60170/PV1 | Iga Solar | 63012/SWANN | Ransomville Solar 1, LLC | solar | 5.000 | 5.000 | 2019-08 | 2019-08 | 0 | False | False |
| 2019 | A | 60140/PV1 | Brooke Solar | 62995/NMGR1 | Grants CDEC 2 | solar | 4.500 | 4.500 | 2019-08 | 2019-08 | 0 | False | False |
| 2019 | A | 60177/PV1 | Blue Bird Solar | 62998/ASHDO | 25 Ashdown Road Solar, LLC | solar | 4.000 | 4.000 | 2019-08 | 2019-08 | 0 | False | False |
| 2019 | A | 59991/LEB1 | Lebanon Solar 1 | 62720/5540 | Chester Woods Point Solar, LLC CSG | solar | 2.000 | 2.000 | 2019-04 | 2019-05 | 1 | False | False |
| 2019 | A | 59992/LEB2 | Lebanon Solar 2 | 62721/SS29 | Steel Sun 2: 2303-III-9 Hamburg Tpke | solar | 2.000 | 2.000 | 2019-04 | 2019-05 | 1 | False | False |
| 2019 | A | 60973/LKPR | Lake Perris Solar | 63276/X0133 | Mtn. Solar 1 | solar | 1.500 | 1.500 | 2019-11 | 2019-11 | 0 | False | False |
| 2019 | A | 60972/SJAC | San Jacinto Solar | 63277/X0133 | Mtn. Solar 2 | solar | 1.500 | 1.500 | 2019-11 | 2019-11 | 0 | False | False |
| 2019 | A | 57057/1A | Quinhagak | 57057/3A | Quinhagak | oil | 0.500 | 0.500 | 2019-04 | 2019-05 | 1 | True | True |
| 2020 | A | 63014/PGR12 | Shakespeare Solar | 63733/11631 | Eros Solar, LLC | solar | 5.000 | 5.000 | 2020-02 | 2020-04 | 2 | False | False |
| 2020 | A | 55641/PV1 | Riverside Energy Center | 64179/17000 | IA - City of Ames - Airport Road | solar | 2.000 | 2.000 | 2020-11 | 2020-11 | 0 | False | False |
| 2020 | A | 62230/44 | Indigo Solar | 63244/SYDN | Sydney Solar | solar | 2.000 | 2.000 | 2020-03 | 2020-03 | 0 | False | False |
| 2020 | A | 63190/GCHOC | Guittard Chocolates | 63681/13 | Oak Leaf Solar XXXIII LLC (Lantz) | solar | 1.500 | 1.500 | 2020-04 | 2020-04 | 0 | False | False |
| 2020 | A | 63006/HOLM | Novel Holmquist Solar CSG | 63689/RLFS | Red Lake Falls Community Hybrid | solar | 1.000 | 1.000 | 2020-04 | 2020-04 | 0 | False | False |
| 2020 | A | 63316/GLADI | Gladiolus Solar, LLC | 63532/52837 | Winona Community Solar One LLC | solar | 1.000 | 1.000 | 2020-02 | 2020-02 | 0 | False | False |
| 2020 | A | 63310/SNOWD | Snowdrop Solar, LLC | 63533/52830 | Goodhue Community Solar Two LLC | solar | 1.000 | 1.000 | 2020-02 | 2020-02 | 0 | False | False |
| 2020 | A | 63248/LOREN | Novel Loren Solar LLC CSG | 63741/USBCS | USS Bluff Country Solar CSG | solar | 1.000 | 1.000 | 2020-04 | 2020-04 | 0 | False | False |
| 2020 | A | 63217/ZNZBR | USS Zanzibar Solar LLC CSG | 63534/52827 | Houston/Winona Community Solar One LLC | solar | 1.000 | 1.000 | 2020-02 | 2020-02 | 0 | False | False |
| 2020 | A | 63188/ALTPL | Altman Plants | 63595/SC | Lowry CSG2, LLC | solar | 1.000 | 1.000 | 2020-02 | 2020-02 | 0 | False | False |
| 2021 | A | 62808/BBW | Black Bear Wind (MT) | 64662/SAC | Sac County Wind, LLC | wind_onshore | 80.0 | 80.0 | 2021-01 | 2021-04 | 3 | False | False |
| 2021 | A | 60628/BEAM4 | BRE NC Solar 4 | 65298/81724 | DOCCS Eastern | solar | 5.000 | 5.000 | 2021-12 | 2021-12 | 0 | False | False |
| 2021 | A | 62070/FUMAR | Fumaria Solar Project | 64677/RYLND | Ryland Road Solar | solar | 5.000 | 5.000 | 2021-05 | 2021-05 | 0 | False | False |
| 2021 | A | 62068/TYPHA | Typha Solar Project | 64678/WDH17 | Windsor Hwy 17 Solar | solar | 5.000 | 5.000 | 2021-05 | 2021-05 | 0 | False | False |
| 2021 | A | 60626/BEAM2 | BRE NC Solar 2 | 65299/81721 | DOCCS Wende | solar | 5.000 | 5.000 | 2021-12 | 2021-12 | 0 | False | False |
| 2021 | A | 63196/ACP2 | AC Power 2 | 64751/267 | Amazon PSP1 | solar | 3.800 | 3.800 | 2021-06 | 2021-06 | 0 | False | False |
| 2021 | A | 64206/2004 | Highway 9 Solar | 64868/KEEV | Keeversville Solar CSG | solar | 2.000 | 2.000 | 2021-09 | 2021-09 | 0 | False | False |
| 2021 | A | 61285/PV1 | Crazy Horse Solar Project | 65227/401 | Ameresco Danville Solar, LLC | solar | 2.000 | 2.000 | 2021-11 | 2021-12 | 1 | False | False |
| 2021 | A | 63619/USGPA | USS Grandpa Solar | 65152/CLINT | Clinton Solar | solar | 1.000 | 1.000 | 2021-10 | 2021-10 | 0 | False | False |
| 2021 | A | 64394/FLODQ | Flodquist Community Solar DE LLC | 64866/USSWC | USS Wildcat Solar LLC | solar | 1.000 | 1.000 | 2021-07 | 2021-07 | 0 | False | False |
| 2022 | A | 64845/AREXP | Aragonne Mesa Wind Project | 56336/AREXP | Aragonne Wind LLC | wind_onshore | 145.0 | 145.0 | 2022-02 | 2022-03 | 1 | False | False |
| 2022 | A | 64703/GOR1 | Gorham ME 1 | 65638/SRGN1 | SR Greenville I | solar | 4.800 | 4.800 | 2022-01 | 2022-04 | 3 | False | False |
| 2022 | A | 61038/WEY1 | Weybridge 1 Solar | 65946/SOLAR | Hecate Energy Upshur Rural LLC | solar | 3.000 | 3.000 | 2022-11 | 2022-12 | 1 | False | False |
| 2022 | A | 62182/24 | Battle Solar | 66223/11000 | Lockenhurst Pond Solar | solar | 2.000 | 2.000 | 2023-01 | 2023-01 | 0 | False | False |
| 2022 | A | 62345/89 | Wayfair Solar | 66232/10894 | Svenski Solar (Hybrid) | solar | 2.000 | 2.000 | 2023-01 | 2023-01 | 0 | False | False |
| 2022 | A | 64205/2003 | Fairview Solar | 65982/TCLP | KDC Solar TC Little Patuxent WWTP LLC | solar | 2.000 | 2.000 | 2022-10 | 2022-10 | 0 | False | False |
| 2022 | A | 62349/82 | Topaz Solar (SC) | 66246/LSBST | Lisbon Street Solar | solar | 2.000 | 2.000 | 2023-01 | 2023-01 | 0 | False | False |
| 2022 | A | 64156/2002 | Davis Road Solar | 65983/TCGH | KDC Solar TC George Howard LLC | solar | 2.000 | 2.000 | 2022-10 | 2022-10 | 0 | False | False |
| 2022 | A | 65356/KLEES | Klees Mill CSG | 66371/EDISN | Edison Farm | solar | 2.000 | 2.000 | 2023-01 | 2023-02 | 1 | False | False |
| 2022 | A | 65065/CGS | TC Solar RCE | 65795/VSPRC | VS RXI Wilmington, LLC | solar | 1.000 | 1.000 | 2022-12 | 2023-01 | 1 | False | False |
| 2023 | A | 63880/TX17 | TX17 Nickel Prairie Storage | 66636/BESS | McFarland A Solar and Storage | battery | 100.0 | 100.0 | 2023-05 | 2023-05 | 0 | False | False |
| 2023 | A | 65147/VCP01 | Deptford Solar One | 67121/BAYCS | Bay Avenue CDG | solar | 3.000 | 3.000 | 2023-11 | 2023-12 | 1 | False | False |
| 2023 | A | 62307/71 | Scarlet Solar | 66488/10958 | Davis Solar | solar | 2.000 | 2.000 | 2023-03 | 2023-03 | 0 | False | False |
| 2023 | A | 65108/VCP17 | Moodus Solar One | 66989/28472 | Hubble Solar, LLC | solar | 2.000 | 2.000 | 2023-10 | 2023-10 | 0 | False | False |
| 2023 | A | 65062/VCP09 | Middletown Solar One | 66985/722 | Georgetown (Polk Burnett) | solar | 2.000 | 2.000 | 2023-10 | 2023-11 | 1 | False | False |
| 2023 | A | 65150/VCP06 | Ellington Solar One | 67001/93311 | Sunny Cow Solar, LLC | solar | 2.000 | 2.000 | 2023-11 | 2023-11 | 0 | False | False |
| 2023 | A | 65017/MZPA | Mazeppa CSG | 66969/USJAY | USS Jayhawk Solar LLC (CSG) | solar | 1.000 | 1.000 | 2023-10 | 2023-10 | 0 | False | False |
| 2024 | A | 66704/11106 | Chiltepin Solar | 56224/SOL1 | TS Power Plant | solar | 100.0 | 100.0 | 2024-02 | 2024-04 | 2 | False | False |
| 2024 | A | 66641/BESS1 | Lake Mabel Energy Storage | 68611/IBSS | International Battery Substation (IBSS) | battery | 40.0 | 40.0 | 2024-11 | 2025-02 | 3 | False | False |
| 2024 | A | 64095/KSSOL | Kahana Solar, LLC | 68454/LEEDS | Walden Solar Maine V | solar | 20.0 | 20.0 | 2024-12 | 2024-12 | 0 | False | False |
| 2024 | A | 67128/SCOTV | SR Scottsville, LLC | 67408/PIKE | Pike Road Solar (NY) | solar | 3.000 | 3.000 | 2024-02 | 2024-03 | 1 | False | False |
| 2024 | A | 1272/10 | Colby City of | 1312/7 | Oberlin (KS) | oil | 3.000 | 3.000 | 2024-01 | 2024-04 | 3 | False | False |
| 2024 | A | 65148/VCP13 | Dollar Tree Solar One | 68701/NLR2 | NLRED 2MW | solar | 2.000 | 2.000 | 2025-01 | 2025-02 | 1 | False | False |
| 2025 | A | 66297/A7BS1 | Alamo 7 BESS 1 | 68842/CHILB | Chillingham Storage | battery | 150.0 | 150.0 | 2025-03 | 2025-04 | 1 | False | False |
| 2025 | A | 66298/A7BS2 | Alamo 7 BESS 2 | 68879/BCNV1 | Bocanova Energy Storage | battery | 150.0 | 150.0 | 2025-03 | 2025-04 | 1 | False | False |
| 2025 | A | 67651/BERK | Berkman Storage | 69023/KNBA1 | Knightdale Battery | battery | 100.0 | 100.0 | 2025-04 | 2025-07 | 3 | False | False |
| 2025 | A | 65148/VCP13 | Dollar Tree Solar One | 68857/HM701 | Richmond Solar | solar | 2.000 | 2.000 | 2025-01 | 2025-04 | 3 | False | False |
| 2025 | A | 68134/CH901 | Elwood 1-SLCHI901 | 69129/26046 | Dudley Landfill Solar LLC | solar | 1.300 | 1.300 | 2025-07 | 2025-09 | 2 | False | False |
| 2025 | A | 66510/19616 | CA Moss Landing 3040 Hilltop Rd | 69736/10635 | New Britain - 142 Deming Rd | solar | 1.200 | 1.200 | 2025-12 | 2026-03 | 3 | False | False |
| 2025 | A | 66510/B9616 | CA Moss Landing 3040 Hilltop Rd | 69568/DIVIB | NL MA - Division | battery | 1.000 | 1.000 | 2025-12 | 2026-01 | 1 | False | False |

## 3. Pairs, pass B (loose)

49 pairs.

| year | pass | dropped | dropped_plant | entry | entry_plant | group | dropped_mw | entry_mw | last_listed | first_listed | months_apart | same_plant | same_name |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2017 | B | 60246/1 | Michigan Wind 3 | 61261/RF1 | Rock Falls Wind Farm LLC | wind_onshore | 152.8 | 154.5 | 2017-02 | 2017-04 | 2 | False | False |
| 2017 | B | 60168/PV1 | Sadie Solar | 61833/PGRC9 | Freedom Solar | solar | 5.000 | 5.000 | 2018-01 | 2018-05 | 4 | False | False |
| 2017 | B | 60155/PV1 | Signature Solar | 61869/SHS3 | Scenic Hill Solar III | solar | 5.000 | 5.000 | 2018-01 | 2018-06 | 5 | False | False |
| 2017 | B | 60171/PV1 | Clayton Solar | 61731/PLAIN | Solten Plainville 6000, LLC | solar | 5.000 | 4.900 | 2018-01 | 2018-03 | 2 | False | False |
| 2017 | B | 60829/PV1 | Eastway Solar, LLC | 61457/PALM | Palmer Solar Center | solar | 4.900 | 5.000 | 2017-09 | 2017-09 | 0 | False | False |
| 2018 | B | 59007/MAR S | Mariah South | 62133/GT1 | North English | wind_onshore | 210.4 | 200.0 | 2018-09 | 2018-09 | 0 | False | False |
| 2018 | B | 60159/PV1 | Roman Solar | 62693/PGR03 | Chowan Jehu Solar | solar | 5.000 | 5.000 | 2018-12 | 2019-04 | 4 | False | False |
| 2018 | B | 60163/PV1 | Hawk Solar | 61870/MONTE | Montevideo Solar LLC, CSG | solar | 5.000 | 5.000 | 2018-01 | 2018-06 | 5 | False | False |
| 2018 | B | 60167/PV1 | Carter Solar | 61873/GEN1 | Yellow Jacket | solar | 5.000 | 5.000 | 2018-01 | 2018-06 | 5 | False | False |
| 2018 | B | 60168/PV1 | Sadie Solar | 61877/HAN01 | Hanover Solar, LLC | solar | 5.000 | 4.900 | 2018-01 | 2018-06 | 5 | False | False |
| 2018 | B | 60176/PV1 | Anna Solar | 61928/GEN1 | Saint Albans Solar | solar | 5.000 | 4.900 | 2018-01 | 2018-07 | 6 | False | False |
| 2018 | B | 60173/PV1 | Longleaf Solar | 62368/62591 | BWC Origination 18 | solar | 5.000 | 4.800 | 2018-12 | 2018-12 | 0 | False | False |
| 2018 | B | 59571/PV1 | Soy Solar | 61983/COTG | Cottage Grove Project CSG | solar | 5.000 | 4.900 | 2018-02 | 2018-08 | 6 | False | False |
| 2018 | B | 60169/PV1 | Icarus Solar | 62558/SKSC2 | Kearsarge SKSC2 LLC | solar | 3.000 | 3.100 | 2018-12 | 2019-02 | 2 | False | False |
| 2019 | B | 59907/GEN | Black Fork Wind Energy Project | 62795/1 | Ida Grove II | wind_onshore | 200.0 | 201.0 | 2019-05 | 2019-05 | 0 | False | False |
| 2019 | B | 60158/PV1 | June Solar | 62890/BOXBR | GSPP Boxborough Littleton (MA) | solar | 4.000 | 4.000 | 2019-01 | 2019-07 | 6 | False | False |
| 2019 | B | 61845/MM29 | Bolthouse Farms Fuel Cell | 63714/GEN05 | GEN005 Antibody Fuel Cell | gas_other | 2.500 | 2.500 | 2019-12 | 2020-04 | 4 | False | False |
| 2019 | B | 61845/MM28 | Bolthouse Farms Fuel Cell | 63638/CTC13 | Tracy 210 | gas_other | 2.500 | 2.600 | 2019-12 | 2020-03 | 3 | False | False |
| 2020 | B | 61044/WT1 | La Joya NM | 64309/SCWKS | Soldier Creek Wind | wind_onshore | 306.2 | 300.0 | 2020-10 | 2020-12 | 2 | False | False |
| 2020 | B | 60094/BLCK3 | Blythe Solar III, LLC | 63545/GEN1 | Chevron - Lost Hills Hybrid | solar | 31.2 | 30.0 | 2020-01 | 2020-02 | 1 | False | False |
| 2021 | B | 64098/4 | Tesla Reno GigaFactory | 65258/WKP01 | Wapakoneta-Pratt | solar | 13.4 | 13.5 | 2021-10 | 2021-11 | 1 | False | False |
| 2021 | B | 60630/PV1 | Howardtown Farm | 64830/OS | Brightwood Solar, LLC | solar | 10.0 | 10.0 | 2021-01 | 2021-07 | 6 | False | False |
| 2021 | B | 62605/MVESS | Martha's Vineyard Community Battery | 64763/RUM | Rumford ESS | battery | 4.900 | 4.900 | 2021-03 | 2021-07 | 4 | False | False |
| 2021 | B | 63197/ACP4 | Pettinos Solar | 65257/LMS01 | Lineage MS | solar | 1.200 | 1.200 | 2021-06 | 2021-12 | 6 | False | False |
| 2022 | B | 62548/SJ-3 | SJRR Power LLC | 55129/CTG4 | Desert Basin | gas_ct | 50.0 | 49.5 | 2022-04 | 2022-07 | 3 | False | False |
| 2022 | B | 62548/SJ-4 | SJRR Power LLC | 55129/CTG5 | Desert Basin | gas_ct | 50.0 | 49.5 | 2022-04 | 2022-07 | 3 | False | False |
| 2022 | B | 61841/SCITU | Scituate RI Solar, LLC | 65781/BSHP2 | Bishopville Solar II, LLC | solar | 10.0 | 10.0 | 2022-04 | 2022-08 | 4 | False | False |
| 2022 | B | 64320/SIER | Sierra | 65810/CDRVL | Cedarville (TX) | battery | 10.0 | 9.900 | 2022-09 | 2022-12 | 3 | False | False |
| 2022 | B | 63545/BESS1 | Chevron - Lost Hills Hybrid | 65809/CATER | Caterina | battery | 10.0 | 9.900 | 2022-08 | 2022-08 | 0 | False | False |
| 2022 | B | 63135/KING1 | King CSG | 65641/SRPAR | SR Paris | solar | 7.000 | 6.800 | 2022-03 | 2022-04 | 1 | False | False |
| 2022 | B | 62183/25 | Bell Solar | 66339/BRN01 | Brainerd Airport | solar | 6.100 | 5.800 | 2022-11 | 2023-02 | 3 | False | False |
| 2022 | B | 64098/RDP | Tesla Reno GigaFactory | 66201/NBBRM | Niagara Bottling - Bloomfield | solar | 2.800 | 2.800 | 2022-08 | 2023-01 | 5 | False | False |
| 2022 | B | 64098/REP | Tesla Reno GigaFactory | 66021/ASSA1 | DRPA Ashland Station Solar Project | solar | 2.800 | 2.700 | 2022-08 | 2022-10 | 2 | False | False |
| 2022 | B | 64098/RD | Tesla Reno GigaFactory | 66182/AMHPV | Town of Amherst Solar | solar | 2.400 | 2.500 | 2022-08 | 2023-01 | 5 | False | False |
| 2022 | B | 63226/2078 | Deiter-STEU | 66095/712 | Cortez Solar 1, LLC | solar | 2.200 | 2.200 | 2022-05 | 2022-11 | 6 | False | False |
| 2022 | B | 63876/MLCRK | Mule Creek State Prison | 65984/TCBP | KDC Solar TC Blandair Park LLC | solar | 2.100 | 2.000 | 2022-09 | 2022-11 | 2 | False | False |
| 2023 | B | 64537/KOV4A | Tyre Bridge Solar LLC | 67161/OAK | Oak Solar | solar | 118.0 | 120.0 | 2023-07 | 2024-01 | 6 | False | False |
| 2023 | B | 64811/UPT7 | Upton County BESS | 66807/CUYA1 | SEPV Cuyama Hybrid | battery | 3.100 | 3.000 | 2023-06 | 2023-07 | 1 | False | False |
| 2023 | B | 65064/VCP03 | Millstone Solar One | 67526/62293 | UADA | solar | 2.800 | 2.800 | 2023-11 | 2024-04 | 5 | False | False |
| 2023 | B | 65180/CHKWL | Chuckawalla State Prison | 66507/BR1A | Briscoe 1A | solar | 2.100 | 2.000 | 2023-04 | 2023-05 | 1 | False | False |
| 2023 | B | 65063/VCP10 | Middletown Solar Two | 66936/FLOYD | Bryan Floyd | solar | 1.900 | 1.900 | 2023-04 | 2023-08 | 4 | False | False |
| 2023 | B | 64181/18017 | IL - SMHEC - Moraine Valley | 66884/FSS1 | FreeState Stull Solar I | solar | 1.300 | 1.300 | 2023-02 | 2023-08 | 6 | False | False |
| 2024 | B | 63513/OEALC | AL Solar C LLC | 68774/FTCR | Fountain Creek Solar | solar | 80.0 | 80.0 | 2024-11 | 2025-03 | 4 | False | False |
| 2024 | B | 65488/CROKT | Crockett | 60964/TRIB1 | Apache Solar I | battery | 9.900 | 10.0 | 2024-11 | 2025-02 | 3 | False | False |
| 2024 | B | 67010/GEN1 | Dynamic - Wales Pond Road | 68401/OSWEG | TJA-NY-1454 CR 15 Oswegatchie, LLC | solar | 4.900 | 4.900 | 2024-08 | 2024-12 | 4 | False | False |
| 2025 | B | 66301/PGBS1 | Peregrine BESS 1 | 69298/ESR2 | PP Jaguar BESS LLC | battery | 150.0 | 150.0 | 2025-05 | 2025-10 | 5 | False | False |
| 2025 | B | 66294/A4BS1 | Alamo 4 BESS | 66540/SES | Shamrock Wind | battery | 100.0 | 100.0 | 2025-03 | 2025-09 | 6 | False | False |
| 2025 | B | 66296/A5BS2 | Alamo 5 BESS 2 | 69122/5937 | Jackson Fuller Energy Storage | battery | 100.0 | 100.0 | 2025-03 | 2025-09 | 6 | False | False |
| 2025 | B | 67961/17182 | Solar Powered AG, LLC | 68589/UTICA | Community Solar Utica 1, LLC | solar | 3.100 | 3.000 | 2025-02 | 2025-02 | 0 | False | False |

## 4. Raw records of the 2018 pairs

| report_date | valid_until_date | plant_id_eia | generator_id | capacity_mw | current_planned_generator_operating_date | generator_operating_date | operational_status_code | technology_description | plant_name_eia |
|---|---|---|---|---|---|---|---|---|---|
| 2018-02-01 | 2018-03-01 | 3393 | CTG1 | 347.0 | 2018-06-01 |  | U | Natural Gas Fired Combined Cycle | Allen Steam Plant |
| 2018-03-01 | 2018-04-01 | 3393 | CTG1 | 347.0 | 2018-06-01 |  | U | Natural Gas Fired Combined Cycle | Allen Combined Cycle |
| 2018-04-01 | 2018-07-01 | 3393 | CTG1 | 347.0 |  | 2018-04-01 | OP | Natural Gas Fired Combined Cycle | Allen Combined Cycle |
| 2018-07-01 | 2022-03-01 | 3393 | CTG1 | 347.0 |  | 2018-04-01 | OP | Natural Gas Fired Combined Cycle | Allen |
| 2022-03-01 | 2026-08-01 | 3393 | CTG1 | 347.0 |  | 2018-04-01 | OP | Natural Gas Fired Combined Cycle | Allen |
| 2018-02-01 | 2018-03-01 | 3393 | CTG2 | 347.0 | 2018-06-01 |  | U | Natural Gas Fired Combined Cycle | Allen Steam Plant |
| 2018-03-01 | 2018-04-01 | 3393 | CTG2 | 347.0 | 2018-06-01 |  | U | Natural Gas Fired Combined Cycle | Allen Combined Cycle |
| 2018-04-01 | 2018-07-01 | 3393 | CTG2 | 347.0 |  | 2018-04-01 | OP | Natural Gas Fired Combined Cycle | Allen Combined Cycle |
| 2018-07-01 | 2022-03-01 | 3393 | CTG2 | 347.0 |  | 2018-04-01 | OP | Natural Gas Fired Combined Cycle | Allen |
| 2022-03-01 | 2026-08-01 | 3393 | CTG2 | 347.0 |  | 2018-04-01 | OP | Natural Gas Fired Combined Cycle | Allen |
| 2018-02-01 | 2018-03-01 | 3393 | STG1 | 476.9 | 2018-06-01 |  | U | Natural Gas Fired Combined Cycle | Allen Steam Plant |
| 2018-03-01 | 2018-04-01 | 3393 | STG1 | 476.9 | 2018-06-01 |  | U | Natural Gas Fired Combined Cycle | Allen Combined Cycle |
| 2018-04-01 | 2018-07-01 | 3393 | STG1 | 476.9 |  | 2018-04-01 | OP | Natural Gas Fired Combined Cycle | Allen Combined Cycle |
| 2018-07-01 | 2022-03-01 | 3393 | STG1 | 476.9 |  | 2018-04-01 | OP | Natural Gas Fired Combined Cycle | Allen |
| 2022-03-01 | 2026-08-01 | 3393 | STG1 | 476.9 |  | 2018-04-01 | OP | Natural Gas Fired Combined Cycle | Allen |
| 2015-07-01 | 2015-10-01 | 59007 | MAR S | 0.0 | 2016-12-01 |  | U | Onshore Wind Turbine | Mariah Renewable Energy Center Phase 2 |
| 2015-10-01 | 2015-12-01 | 59007 | MAR S | 0.0 | 2016-12-01 |  | U | Onshore Wind Turbine | Mariah South |
| 2015-12-01 | 2016-02-01 | 59007 | MAR S | 0.0 | 2017-10-01 |  | U | Onshore Wind Turbine | Mariah South |
| 2016-02-01 | 2016-04-01 | 59007 | MAR S | 0.0 | 2017-10-01 |  | U | Onshore Wind Turbine | Mariah South |
| 2016-04-01 | 2016-07-01 | 59007 | MAR S | 230.4 | 2017-10-01 |  | U | Onshore Wind Turbine | Mariah South |
| 2016-07-01 | 2017-03-01 | 59007 | MAR S | 230.4 | 2017-10-01 |  | U | Onshore Wind Turbine | Mariah South |
| 2017-03-01 | 2017-08-01 | 59007 | MAR S | 230.4 | 2017-10-01 |  | U | Onshore Wind Turbine | Mariah South |
| 2017-08-01 | 2018-03-01 | 59007 | MAR S | 210.4 | 2018-10-01 |  | U | Onshore Wind Turbine | Mariah South |
| 2018-03-01 | 2018-09-01 | 59007 | MAR S | 210.4 | 2019-10-01 |  | U | Onshore Wind Turbine | Mariah South |
| 2017-11-01 | 2018-03-01 | 59216 | PV1 | 5.0 | 2018-07-01 |  | L | Solar Photovoltaic | Rhubarb One |
| 2018-03-01 | 2018-04-01 | 59216 | PV1 | 5.0 | 2019-03-01 |  | L | Solar Photovoltaic | Rhubarb One |
| 2015-07-01 | 2015-08-01 | 59571 | PV1 | 0.0 | 2015-12-01 |  | L | Solar Photovoltaic | Soy Solar |
| 2015-08-01 | 2015-12-01 | 59571 | PV1 | 0.0 | 2016-06-01 |  | L | Solar Photovoltaic | Soy Solar |
| 2015-12-01 | 2016-04-01 | 59571 | PV1 | 0.0 | 2016-12-01 |  | L | Solar Photovoltaic | Soy Solar |
| 2016-04-01 | 2016-07-01 | 59571 | PV1 | 5.0 | 2016-12-01 |  | L | Solar Photovoltaic | Soy Solar |
| 2016-07-01 | 2016-10-01 | 59571 | PV1 | 5.0 | 2017-03-01 |  | L | Solar Photovoltaic | Soy Solar |
| 2016-10-01 | 2017-03-01 | 59571 | PV1 | 5.0 | 2017-12-01 |  | L | Solar Photovoltaic | Soy Solar |
| 2017-03-01 | 2017-07-01 | 59571 | PV1 | 5.0 | 2017-12-01 |  | L | Solar Photovoltaic | Soy Solar |
| 2017-07-01 | 2018-02-01 | 59571 | PV1 | 5.0 | 2018-07-01 |  | L | Solar Photovoltaic | Soy Solar |
| 2015-07-01 | 2015-12-01 | 59998 | RNDHL | 0.0 | 2016-12-01 |  | P | Solar Photovoltaic | Round Hill PV1 |
| 2015-12-01 | 2016-04-01 | 59998 | RNDHL | 0.0 | 2016-12-01 |  | L | Solar Photovoltaic | Round Hill PV1 |
| 2016-04-01 | 2016-05-01 | 59998 | RNDHL | 5.0 | 2016-12-01 |  | L | Solar Photovoltaic | Round Hill PV1 |
| 2016-05-01 | 2016-07-01 | 59998 | RNDHL | 5.0 | 2017-12-01 |  | L | Solar Photovoltaic | Round Hill PV1 |
| 2016-07-01 | 2017-03-01 | 59998 | RNDHL | 5.0 | 2017-12-01 |  | L | Solar Photovoltaic | Round Hill PV1 |
| 2017-03-01 | 2017-09-01 | 59998 | RNDHL | 5.0 | 2018-06-01 |  | L | Solar Photovoltaic | Round Hill PV1 |
| 2017-09-01 | 2018-08-01 | 59998 | RNDHL | 5.0 | 2018-12-01 |  | L | Solar Photovoltaic | Round Hill PV1 |
| 2015-12-01 | 2016-04-01 | 60138 | 1GTA | 0.0 | 2018-05-01 |  | U | Natural Gas Fired Combined Cycle | Citrus County Combined Cycle Plant |
| 2016-04-01 | 2016-07-01 | 60138 | 1GTA | 310.3 | 2018-05-01 |  | U | Natural Gas Fired Combined Cycle | Citrus County Combined Cycle Plant |
| 2016-07-01 | 2017-03-01 | 60138 | 1GTA | 310.3 | 2018-05-01 |  | U | Natural Gas Fired Combined Cycle | Citrus County Combined Cycle Plant |
| 2017-03-01 | 2017-07-01 | 60138 | 1GTA | 310.3 | 2018-05-01 |  | U | Natural Gas Fired Combined Cycle | Citrus County Combined Cycle Plant |
| 2017-07-01 | 2018-01-01 | 60138 | 1GTA | 310.3 | 2018-05-01 |  | V | Natural Gas Fired Combined Cycle | Citrus County Combined Cycle Plant |
| 2018-01-01 | 2018-06-01 | 60138 | 1GTA | 310.3 | 2018-09-01 |  | V | Natural Gas Fired Combined Cycle | Citrus County Combined Cycle Plant |
| 2015-12-01 | 2016-04-01 | 60138 | 1GTB | 0.0 | 2018-05-01 |  | U | Natural Gas Fired Combined Cycle | Citrus County Combined Cycle Plant |
| 2016-04-01 | 2016-07-01 | 60138 | 1GTB | 310.3 | 2018-05-01 |  | U | Natural Gas Fired Combined Cycle | Citrus County Combined Cycle Plant |
| 2016-07-01 | 2017-03-01 | 60138 | 1GTB | 310.3 | 2018-05-01 |  | U | Natural Gas Fired Combined Cycle | Citrus County Combined Cycle Plant |
| 2017-03-01 | 2017-07-01 | 60138 | 1GTB | 310.3 | 2018-05-01 |  | U | Natural Gas Fired Combined Cycle | Citrus County Combined Cycle Plant |
| 2017-07-01 | 2018-01-01 | 60138 | 1GTB | 310.3 | 2018-05-01 |  | V | Natural Gas Fired Combined Cycle | Citrus County Combined Cycle Plant |
| 2018-01-01 | 2018-06-01 | 60138 | 1GTB | 310.3 | 2018-09-01 |  | V | Natural Gas Fired Combined Cycle | Citrus County Combined Cycle Plant |
| 2015-12-01 | 2016-04-01 | 60138 | 2GTA | 0.0 | 2018-10-01 |  | U | Natural Gas Fired Combined Cycle | Citrus County Combined Cycle Plant |
| 2016-04-01 | 2016-07-01 | 60138 | 2GTA | 310.3 | 2018-10-01 |  | U | Natural Gas Fired Combined Cycle | Citrus County Combined Cycle Plant |
| 2016-07-01 | 2017-03-01 | 60138 | 2GTA | 310.3 | 2018-10-01 |  | U | Natural Gas Fired Combined Cycle | Citrus County Combined Cycle Plant |
| 2017-03-01 | 2017-10-01 | 60138 | 2GTA | 310.3 | 2018-10-01 |  | U | Natural Gas Fired Combined Cycle | Citrus County Combined Cycle Plant |
| 2017-10-01 | 2018-01-01 | 60138 | 2GTA | 310.3 | 2018-11-01 |  | V | Natural Gas Fired Combined Cycle | Citrus County Combined Cycle Plant |
| 2018-01-01 | 2018-06-01 | 60138 | 2GTA | 310.3 | 2018-12-01 |  | V | Natural Gas Fired Combined Cycle | Citrus County Combined Cycle Plant |
| 2015-12-01 | 2016-04-01 | 60138 | 2GTB | 0.0 | 2018-10-01 |  | U | Natural Gas Fired Combined Cycle | Citrus County Combined Cycle Plant |
| 2016-04-01 | 2016-07-01 | 60138 | 2GTB | 310.3 | 2018-10-01 |  | U | Natural Gas Fired Combined Cycle | Citrus County Combined Cycle Plant |
| 2016-07-01 | 2017-03-01 | 60138 | 2GTB | 310.3 | 2018-10-01 |  | U | Natural Gas Fired Combined Cycle | Citrus County Combined Cycle Plant |
| 2017-03-01 | 2017-10-01 | 60138 | 2GTB | 310.3 | 2018-10-01 |  | U | Natural Gas Fired Combined Cycle | Citrus County Combined Cycle Plant |
| 2017-10-01 | 2018-01-01 | 60138 | 2GTB | 310.3 | 2018-11-01 |  | V | Natural Gas Fired Combined Cycle | Citrus County Combined Cycle Plant |
| 2018-01-01 | 2018-06-01 | 60138 | 2GTB | 310.3 | 2018-12-01 |  | V | Natural Gas Fired Combined Cycle | Citrus County Combined Cycle Plant |
| 2015-12-01 | 2016-04-01 | 60138 | CC1ST | 0.0 | 2018-05-01 |  | U | Natural Gas Fired Combined Cycle | Citrus County Combined Cycle Plant |
| 2016-04-01 | 2016-07-01 | 60138 | CC1ST | 364.7 | 2018-05-01 |  | U | Natural Gas Fired Combined Cycle | Citrus County Combined Cycle Plant |
| 2016-07-01 | 2017-03-01 | 60138 | CC1ST | 364.7 | 2018-05-01 |  | U | Natural Gas Fired Combined Cycle | Citrus County Combined Cycle Plant |
| 2017-03-01 | 2017-07-01 | 60138 | CC1ST | 364.7 | 2018-05-01 |  | U | Natural Gas Fired Combined Cycle | Citrus County Combined Cycle Plant |
| 2017-07-01 | 2018-01-01 | 60138 | CC1ST | 364.7 | 2018-05-01 |  | V | Natural Gas Fired Combined Cycle | Citrus County Combined Cycle Plant |
| 2018-01-01 | 2018-06-01 | 60138 | CC1ST | 364.7 | 2018-09-01 |  | V | Natural Gas Fired Combined Cycle | Citrus County Combined Cycle Plant |
| 2015-12-01 | 2016-04-01 | 60138 | CC2ST | 0.0 | 2018-10-01 |  | U | Natural Gas Fired Combined Cycle | Citrus County Combined Cycle Plant |
| 2016-04-01 | 2016-07-01 | 60138 | CC2ST | 364.7 | 2018-10-01 |  | U | Natural Gas Fired Combined Cycle | Citrus County Combined Cycle Plant |
| 2016-07-01 | 2017-03-01 | 60138 | CC2ST | 364.7 | 2018-10-01 |  | U | Natural Gas Fired Combined Cycle | Citrus County Combined Cycle Plant |
| 2017-03-01 | 2017-10-01 | 60138 | CC2ST | 364.7 | 2018-10-01 |  | U | Natural Gas Fired Combined Cycle | Citrus County Combined Cycle Plant |
| 2017-10-01 | 2018-01-01 | 60138 | CC2ST | 364.7 | 2018-11-01 |  | V | Natural Gas Fired Combined Cycle | Citrus County Combined Cycle Plant |
| 2018-01-01 | 2018-06-01 | 60138 | CC2ST | 364.7 | 2018-12-01 |  | V | Natural Gas Fired Combined Cycle | Citrus County Combined Cycle Plant |
| 2015-12-01 | 2016-04-01 | 60139 | PV1 | 0.0 | 2016-11-01 |  | L | Solar Photovoltaic | Alexis Solar |
| 2016-04-01 | 2016-07-01 | 60139 | PV1 | 5.0 | 2016-11-01 |  | L | Solar Photovoltaic | Alexis Solar |
| 2016-07-01 | 2016-08-01 | 60139 | PV1 | 5.0 | 2017-03-01 |  | L | Solar Photovoltaic | Alexis Solar |
| 2016-08-01 | 2016-12-01 | 60139 | PV1 | 5.0 | 2017-04-01 |  | L | Solar Photovoltaic | Alexis Solar |
| 2016-12-01 | 2017-03-01 | 60139 | PV1 | 5.0 | 2017-08-01 |  | L | Solar Photovoltaic | Alexis Solar |
| 2017-03-01 | 2017-04-01 | 60139 | PV1 | 5.0 | 2017-08-01 |  | L | Solar Photovoltaic | Alexis Solar |
| 2017-04-01 | 2018-02-01 | 60139 | PV1 | 5.0 | 2018-04-01 |  | L | Solar Photovoltaic | Alexis Solar |
| 2018-02-01 | 2018-10-01 | 60139 | PV1 | 5.0 | 2018-12-01 |  | L | Solar Photovoltaic | Alexis Solar |
| 2018-10-01 | 2019-01-01 | 60139 | PV1 | 5.0 | 2019-06-01 |  | L | Solar Photovoltaic | Alexis Solar |
| 2016-02-01 | 2016-04-01 | 60155 | PV1 | 0.0 | 2016-11-01 |  | T | Solar Photovoltaic | Signature Solar |
| 2016-04-01 | 2016-07-01 | 60155 | PV1 | 5.0 | 2016-11-01 |  | T | Solar Photovoltaic | Signature Solar |
| 2016-07-01 | 2016-08-01 | 60155 | PV1 | 5.0 | 2017-03-01 |  | T | Solar Photovoltaic | Signature Solar |
| 2016-08-01 | 2016-12-01 | 60155 | PV1 | 5.0 | 2017-04-01 |  | T | Solar Photovoltaic | Signature Solar |
| 2016-12-01 | 2017-03-01 | 60155 | PV1 | 5.0 | 2017-08-01 |  | T | Solar Photovoltaic | Signature Solar |
| 2017-03-01 | 2017-04-01 | 60155 | PV1 | 5.0 | 2017-08-01 |  | T | Solar Photovoltaic | Signature Solar |
| 2017-04-01 | 2018-01-01 | 60155 | PV1 | 5.0 | 2018-04-01 |  | T | Solar Photovoltaic | Signature Solar |
| 2016-02-01 | 2016-04-01 | 60158 | PV1 | 0.0 | 2016-11-01 |  | L | Solar Photovoltaic | June Solar |
| 2016-04-01 | 2016-07-01 | 60158 | PV1 | 2.0 | 2016-11-01 |  | L | Solar Photovoltaic | June Solar |
| 2016-07-01 | 2016-08-01 | 60158 | PV1 | 2.0 | 2017-03-01 |  | L | Solar Photovoltaic | June Solar |
| 2016-08-01 | 2016-12-01 | 60158 | PV1 | 2.0 | 2017-04-01 |  | L | Solar Photovoltaic | June Solar |
| 2016-12-01 | 2017-02-01 | 60158 | PV1 | 2.0 | 2017-08-01 |  | L | Solar Photovoltaic | June Solar |
| 2017-02-01 | 2017-03-01 | 60158 | PV1 | 4.0 | 2017-08-01 |  | L | Solar Photovoltaic | June Solar |
| 2017-03-01 | 2017-04-01 | 60158 | PV1 | 4.0 | 2017-08-01 |  | L | Solar Photovoltaic | June Solar |
| 2017-04-01 | 2018-02-01 | 60158 | PV1 | 4.0 | 2018-04-01 |  | L | Solar Photovoltaic | June Solar |
| 2018-02-01 | 2018-10-01 | 60158 | PV1 | 4.0 | 2018-12-01 |  | L | Solar Photovoltaic | June Solar |
| 2018-10-01 | 2019-01-01 | 60158 | PV1 | 4.0 | 2019-06-01 |  | L | Solar Photovoltaic | June Solar |
| 2016-02-01 | 2016-04-01 | 60159 | PV1 | 0.0 | 2016-11-01 |  | L | Solar Photovoltaic | Roman Solar |
| 2016-04-01 | 2016-07-01 | 60159 | PV1 | 5.0 | 2016-11-01 |  | L | Solar Photovoltaic | Roman Solar |
| 2016-07-01 | 2016-08-01 | 60159 | PV1 | 5.0 | 2017-03-01 |  | L | Solar Photovoltaic | Roman Solar |
| 2016-08-01 | 2016-12-01 | 60159 | PV1 | 5.0 | 2017-04-01 |  | L | Solar Photovoltaic | Roman Solar |
| 2016-12-01 | 2017-04-01 | 60159 | PV1 | 5.0 | 2017-08-01 |  | L | Solar Photovoltaic | Roman Solar |
| 2017-04-01 | 2018-02-01 | 60159 | PV1 | 5.0 | 2018-04-01 |  | L | Solar Photovoltaic | Roman Solar |
| 2018-02-01 | 2018-10-01 | 60159 | PV1 | 5.0 | 2018-12-01 |  | L | Solar Photovoltaic | Roman Solar |
| 2018-10-01 | 2018-12-01 | 60159 | PV1 | 5.0 | 2019-06-01 |  | L | Solar Photovoltaic | Roman Solar |
| 2016-02-01 | 2016-04-01 | 60162 | PV1 | 0.0 | 2016-12-01 |  | L | Solar Photovoltaic | Wilfork Solar |
| 2016-04-01 | 2016-07-01 | 60162 | PV1 | 5.0 | 2016-12-01 |  | L | Solar Photovoltaic | Wilfork Solar |
| 2016-07-01 | 2016-08-01 | 60162 | PV1 | 5.0 | 2017-03-01 |  | L | Solar Photovoltaic | Wilfork Solar |
| 2016-08-01 | 2016-12-01 | 60162 | PV1 | 5.0 | 2017-04-01 |  | L | Solar Photovoltaic | Wilfork Solar |
| 2016-12-01 | 2017-03-01 | 60162 | PV1 | 5.0 | 2017-08-01 |  | L | Solar Photovoltaic | Wilfork Solar |
| 2017-03-01 | 2017-04-01 | 60162 | PV1 | 5.0 | 2017-08-01 |  | L | Solar Photovoltaic | Wilfork Solar |
| 2017-04-01 | 2018-02-01 | 60162 | PV1 | 5.0 | 2018-04-01 |  | L | Solar Photovoltaic | Wilfork Solar |
| 2018-02-01 | 2018-10-01 | 60162 | PV1 | 5.0 | 2018-12-01 |  | L | Solar Photovoltaic | Wilfork Solar |
| 2018-10-01 | 2019-01-01 | 60162 | PV1 | 5.0 | 2019-06-01 |  | L | Solar Photovoltaic | Wilfork Solar |
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
| 2016-02-01 | 2016-04-01 | 60169 | PV1 | 0.0 | 2016-12-01 |  | L | Solar Photovoltaic | Icarus Solar |
| 2016-04-01 | 2016-07-01 | 60169 | PV1 | 3.0 | 2016-12-01 |  | L | Solar Photovoltaic | Icarus Solar |
| 2016-07-01 | 2016-08-01 | 60169 | PV1 | 3.0 | 2017-03-01 |  | L | Solar Photovoltaic | Icarus Solar |
| 2016-08-01 | 2016-12-01 | 60169 | PV1 | 3.0 | 2017-04-01 |  | L | Solar Photovoltaic | Icarus Solar |
| 2016-12-01 | 2017-03-01 | 60169 | PV1 | 3.0 | 2017-08-01 |  | L | Solar Photovoltaic | Icarus Solar |
| 2017-03-01 | 2017-04-01 | 60169 | PV1 | 3.0 | 2017-08-01 |  | L | Solar Photovoltaic | Icarus Solar |
| 2017-04-01 | 2018-02-01 | 60169 | PV1 | 3.0 | 2018-04-01 |  | L | Solar Photovoltaic | Icarus Solar |
| 2018-02-01 | 2018-10-01 | 60169 | PV1 | 3.0 | 2018-12-01 |  | L | Solar Photovoltaic | Icarus Solar |
| 2018-10-01 | 2018-12-01 | 60169 | PV1 | 3.0 | 2019-06-01 |  | L | Solar Photovoltaic | Icarus Solar |
| 2016-02-01 | 2016-04-01 | 60172 | PV1 | 0.0 | 2016-11-01 |  | L | Solar Photovoltaic | Christina Solar |
| 2016-04-01 | 2016-07-01 | 60172 | PV1 | 3.0 | 2016-11-01 |  | L | Solar Photovoltaic | Christina Solar |
| 2016-07-01 | 2016-08-01 | 60172 | PV1 | 3.0 | 2017-03-01 |  | L | Solar Photovoltaic | Christina Solar |
| 2016-08-01 | 2016-12-01 | 60172 | PV1 | 3.0 | 2017-04-01 |  | L | Solar Photovoltaic | Christina Solar |
| 2016-12-01 | 2017-03-01 | 60172 | PV1 | 3.0 | 2017-08-01 |  | L | Solar Photovoltaic | Christina Solar |
| 2017-03-01 | 2017-04-01 | 60172 | PV1 | 3.0 | 2017-08-01 |  | L | Solar Photovoltaic | Christina Solar |
| 2017-04-01 | 2018-01-01 | 60172 | PV1 | 3.0 | 2018-04-01 |  | L | Solar Photovoltaic | Christina Solar |
| 2016-02-01 | 2016-04-01 | 60173 | PV1 | 0.0 | 2016-12-01 |  | L | Solar Photovoltaic | Longleaf Solar |
| 2016-04-01 | 2016-07-01 | 60173 | PV1 | 5.0 | 2016-12-01 |  | L | Solar Photovoltaic | Longleaf Solar |
| 2016-07-01 | 2016-08-01 | 60173 | PV1 | 5.0 | 2017-03-01 |  | L | Solar Photovoltaic | Longleaf Solar |
| 2016-08-01 | 2016-12-01 | 60173 | PV1 | 5.0 | 2017-04-01 |  | L | Solar Photovoltaic | Longleaf Solar |
| 2016-12-01 | 2017-03-01 | 60173 | PV1 | 5.0 | 2017-08-01 |  | L | Solar Photovoltaic | Longleaf Solar |
| 2017-03-01 | 2017-04-01 | 60173 | PV1 | 5.0 | 2017-08-01 |  | L | Solar Photovoltaic | Longleaf Solar |
| 2017-04-01 | 2018-02-01 | 60173 | PV1 | 5.0 | 2018-04-01 |  | L | Solar Photovoltaic | Longleaf Solar |
| 2018-02-01 | 2018-10-01 | 60173 | PV1 | 5.0 | 2018-12-01 |  | L | Solar Photovoltaic | Longleaf Solar |
| 2018-10-01 | 2018-12-01 | 60173 | PV1 | 5.0 | 2019-06-01 |  | L | Solar Photovoltaic | Longleaf Solar |
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
| 2016-12-01 | 2017-01-01 | 60780 | PV1 | 2.0 | 2017-05-01 |  | T | Solar Photovoltaic | Rowan Solar NC LLC |
| 2017-01-01 | 2017-07-01 | 60780 | PV1 | 2.0 | 2017-12-01 |  | T | Solar Photovoltaic | Rowan Solar NC LLC |
| 2017-07-01 | 2018-10-01 | 60780 | PV1 | 2.0 | 2018-12-01 |  | T | Solar Photovoltaic | Rowan Solar NC LLC |
| 2018-10-01 | 2018-12-01 | 60780 | PV1 | 2.0 | 2019-12-01 |  | T | Solar Photovoltaic | Rowan Solar NC LLC |
| 2017-03-01 | 2017-04-01 | 61081 | PV1 | 3.0 | 2017-12-01 |  | P | Solar Photovoltaic | Lancaster SCE ReMAT |
| 2017-04-01 | 2017-05-01 | 61081 | PV1 | 3.0 | 2018-03-01 |  | P | Solar Photovoltaic | Lancaster SCE ReMAT |
| 2017-05-01 | 2017-06-01 | 61081 | PV1 | 3.0 | 2018-06-01 |  | P | Solar Photovoltaic | Lancaster SCE ReMAT |
| 2017-06-01 | 2018-04-01 | 61081 | PV1 | 3.0 | 2018-06-01 |  | P | Solar Photovoltaic | Lancaster SCE ReMAT |
| 2018-04-01 | 2018-06-01 | 61081 | PV1 | 3.0 | 2018-06-01 |  | OT | Solar Photovoltaic | Lancaster SCE ReMAT |
| 2018-06-01 | 2018-08-01 | 61081 | PV1 | 3.0 | 2018-08-01 |  | OT | Solar Photovoltaic | Lancaster SCE ReMAT |
| 2018-08-01 | 2018-09-01 | 61081 | PV1 | 3.0 | 2018-10-01 |  | OT | Solar Photovoltaic | Lancaster SCE ReMAT |
| 2017-03-01 | 2017-05-01 | 61123 | SKYR5 | 2.0 | 2017-09-01 |  | L | Solar Photovoltaic | SCWA R5 Pond Solar |
| 2017-05-01 | 2017-06-01 | 61123 | SKYR5 | 2.0 | 2017-11-01 |  | L | Solar Photovoltaic | SCWA R5 Pond Solar |
| 2017-06-01 | 2017-08-01 | 61123 | SKYR5 | 2.0 | 2017-11-01 |  | T | Solar Photovoltaic | SCWA R5 Pond Solar |
| 2017-08-01 | 2018-01-01 | 61123 | SKYR5 | 2.0 | 2018-06-01 |  | T | Solar Photovoltaic | SCWA R5 Pond Solar |
| 2018-01-01 | 2018-02-01 | 61123 | SKYR5 | 2.0 | 2018-10-01 |  | T | Solar Photovoltaic | SCWA R5 Pond Solar |
| 2017-03-01 | 2017-10-01 | 61130 | 12344 | 5.0 | 2017-12-01 |  | P | Solar Photovoltaic | Bear Poplar Solar |
| 2017-10-01 | 2018-01-01 | 61130 | 12344 | 5.0 | 2018-03-01 |  | L | Solar Photovoltaic | Bear Poplar Solar |
| 2018-01-01 | 2018-03-01 | 61130 | 12344 | 5.0 | 2018-09-01 |  | L | Solar Photovoltaic | Bear Poplar Solar |
| 2018-03-01 | 2018-07-01 | 61130 | 12344 | 5.0 | 2018-12-01 |  | L | Solar Photovoltaic | Bear Poplar Solar |
| 2018-07-01 | 2018-08-01 | 61130 | 12344 | 5.0 | 2019-03-01 |  | L | Solar Photovoltaic | Bear Poplar Solar |
| 2017-06-01 | 2017-09-01 | 61317 | MB-21 | 1.4 | 2018-02-01 |  | P | Other Natural Gas | Farmingdale Fuel Cell |
| 2017-09-01 | 2018-03-01 | 61317 | MB-21 | 1.4 | 2018-07-01 |  | P | Other Natural Gas | Farmingdale Fuel Cell |
| 2017-12-01 | 2018-02-01 | 61624 | GEN1 | 5.0 | 2018-08-01 |  | L | Solar Photovoltaic | West Moore Solar |
| 2018-02-01 | 2018-05-01 | 61624 | GEN1 | 5.0 | 2018-08-01 |  | U | Solar Photovoltaic | West Moore Solar |
| 2018-05-01 | 2018-10-01 | 61624 | GEN1 | 5.0 | 2019-05-01 |  | U | Solar Photovoltaic | West Moore Solar |
| 2018-02-01 | 2018-04-01 | 61690 | FOREM | 5.0 | 2018-05-01 |  | U | Solar Photovoltaic | Foreman's Hill Community Solar |
| 2018-04-01 | 2018-06-01 | 61690 | FOREM | 5.0 | 2018-06-01 |  | U | Solar Photovoltaic | Foreman's Hill Community Solar |
| 2018-06-01 | 2018-07-01 | 61690 | FOREM | 5.0 | 2018-07-01 |  | U | Solar Photovoltaic | Foreman's Hill Community Solar |
| 2018-07-01 | 2022-04-01 | 61690 | FOREM | 5.0 |  | 2018-07-01 | OP | Solar Photovoltaic | Foreman's Hill Community Solar |
| 2022-04-01 | 2026-08-01 | 61690 | FOREM | 5.0 |  | 2018-07-01 | OP | Solar Photovoltaic | Foreman's Hill Community Solar |
| 2018-02-01 | 2018-06-01 | 61719 | LWCJ1 | 2.0 | 2018-06-01 |  | TS | Solar Photovoltaic | CJ Solar I, LLC         |
| 2018-06-01 | 2018-08-01 | 61719 | LWCJ1 | 2.0 | 2018-08-01 |  | TS | Solar Photovoltaic | CJ Solar I, LLC         |
| 2018-08-01 | 2019-06-01 | 61719 | LWCJ1 | 2.0 |  | 2018-08-01 | OP | Solar Photovoltaic | CJ Solar I, LLC         |
| 2019-06-01 | 2022-04-01 | 61719 | LWCJ1 | 2.0 |  | 2018-08-01 | OP | Solar Photovoltaic | CJ Solar I, LLC |
| 2022-04-01 | 2026-08-01 | 61719 | LWCJ1 | 2.0 |  | 2018-08-01 | OP | Solar Photovoltaic | CJ Solar I, LLC |
| 2018-02-01 | 2022-04-01 | 61740 | GR01 | 3.0 |  | 2018-01-01 | OP | Solar Photovoltaic | Gratis Road Solar Facility |
| 2022-04-01 | 2026-08-01 | 61740 | GR01 | 3.0 |  | 2018-01-01 | OP | Solar Photovoltaic | Gratis Road Solar Facility |
| 2018-03-01 | 2018-05-01 | 61762 | SHERB | 5.0 | 2018-05-01 |  | T | Solar Photovoltaic | Sherburne North Project |
| 2018-05-01 | 2018-06-01 | 61762 | SHERB | 5.0 | 2018-06-01 |  | TS | Solar Photovoltaic | Sherburne North Project |
| 2018-06-01 | 2018-07-01 | 61762 | SHERB | 5.0 | 2018-07-01 |  | TS | Solar Photovoltaic | Sherburne North Project |
| 2018-07-01 | 2018-10-01 | 61762 | SHERB | 5.0 |  | 2018-07-01 | OP | Solar Photovoltaic | Sherburne North Project |
| 2018-10-01 | 2022-04-01 | 61762 | SHERB | 5.0 |  | 2018-07-01 | OP | Solar Photovoltaic | Sherburne North Project CSG |
| 2022-04-01 | 2025-10-01 | 61762 | SHERB | 5.0 |  | 2018-07-01 | OP | Solar Photovoltaic | Sherburne North Project CSG |
| 2025-10-01 | 2026-08-01 | 61762 | SHERB | 5.0 |  | 2018-07-01 | OP | Solar Photovoltaic | Sherburne North Project CSG |
| 2018-03-01 | 2018-05-01 | 61786 | MB-22 | 1.4 | 2018-06-01 |  | U | Other Natural Gas | Trinity College Fuel Cell |
| 2018-05-01 | 2018-06-01 | 61786 | MB-22 | 1.4 | 2018-06-01 |  | TS | Other Natural Gas | Trinity College Fuel Cell |
| 2018-06-01 | 2018-08-01 | 61786 | MB-22 | 1.4 | 2018-08-01 |  | TS | Other Natural Gas | Trinity College Fuel Cell |
| 2018-08-01 | 2019-03-01 | 61786 | MB-22 | 1.4 |  | 2018-08-01 | OP | Other Natural Gas | Trinity College Fuel Cell |
| 2019-03-01 | 2021-05-01 | 61786 | MB-22 | 1.4 |  | 2018-08-01 | OP | Other Natural Gas | Trinity College Fuel Cell |
| 2021-05-01 | 2025-11-01 | 61786 | MB-22 | 1.4 |  | 2018-08-01 | OP | Other Natural Gas | Trinity College Fuel Cell |
| 2025-11-01 | 2026-08-01 | 61786 | MB-22 | 1.4 |  | 2018-08-01 | OP | Other Natural Gas | Trinity College Fuel Cell |
| 2018-04-01 | 2018-06-01 | 61817 | BIGLA | 5.0 | 2018-06-01 |  | T | Solar Photovoltaic | Big Lake Project |
| 2018-06-01 | 2018-09-01 | 61817 | BIGLA | 5.0 |  | 2018-06-01 | OP | Solar Photovoltaic | Big Lake Project |
| 2018-09-01 | 2022-04-01 | 61817 | BIGLA | 5.0 |  | 2018-06-01 | OP | Solar Photovoltaic | Big Lake Project CSG |
| 2022-04-01 | 2025-10-01 | 61817 | BIGLA | 5.0 |  | 2018-06-01 | OP | Solar Photovoltaic | Big Lake Project CSG |
| 2025-10-01 | 2026-08-01 | 61817 | BIGLA | 5.0 |  | 2018-06-01 | OP | Solar Photovoltaic | Big Lake Project CSG |
| 2018-05-01 | 2018-06-01 | 61842 | PV1 | 5.0 | 2018-09-01 |  | P | Solar Photovoltaic | Sun Farm VI, LLC |
| 2018-06-01 | 2018-07-01 | 61842 | PV1 | 5.0 | 2018-09-01 |  | U | Solar Photovoltaic | Sun Farm VI, LLC |
| 2018-07-01 | 2018-09-01 | 61842 | PV1 | 5.0 | 2018-09-01 |  | V | Solar Photovoltaic | Sun Farm VI, LLC |
| 2018-09-01 | 2018-11-01 | 61842 | PV1 | 5.0 | 2018-11-01 |  | V | Solar Photovoltaic | Sun Farm VI, LLC |
| 2018-11-01 | 2019-02-01 | 61842 | PV1 | 5.0 |  | 2018-11-01 | OP | Solar Photovoltaic | Sun Farm VI, LLC |
| 2019-02-01 | 2022-04-01 | 61842 | PV1 | 5.0 |  | 2018-11-01 | OP | Solar Photovoltaic | Sun Farm VI, LLC |
| 2022-04-01 | 2026-08-01 | 61842 | PV1 | 5.0 |  | 2018-11-01 | OP | Solar Photovoltaic | Sun Farm VI, LLC |
| 2018-06-01 | 2018-07-01 | 61870 | MONTE | 5.0 | 2018-09-01 |  | T | Solar Photovoltaic | Montevideo Solar LLC |
| 2018-07-01 | 2018-08-01 | 61870 | MONTE | 5.0 | 2018-09-01 |  | V | Solar Photovoltaic | Montevideo Solar LLC |
| 2018-08-01 | 2018-10-01 | 61870 | MONTE | 5.0 | 2018-11-01 |  | V | Solar Photovoltaic | Montevideo Solar LLC |
| 2018-10-01 | 2018-11-01 | 61870 | MONTE | 5.0 | 2018-11-01 |  | V | Solar Photovoltaic | Montevideo Solar LLC, CSG |
| 2018-11-01 | 2018-12-01 | 61870 | MONTE | 5.0 | 2018-12-01 |  | V | Solar Photovoltaic | Montevideo Solar LLC, CSG |
| 2018-12-01 | 2019-04-01 | 61870 | MONTE | 5.0 |  | 2018-12-01 | OP | Solar Photovoltaic | Montevideo Solar LLC, CSG |
| 2019-04-01 | 2022-04-01 | 61870 | MONTE | 5.0 |  | 2019-01-01 | OP | Solar Photovoltaic | Montevideo Solar LLC, CSG |
| 2022-04-01 | 2026-08-01 | 61870 | MONTE | 5.0 |  | 2019-01-01 | OP | Solar Photovoltaic | Montevideo Solar LLC, CSG |
| 2018-06-01 | 2018-07-01 | 61873 | GEN1 | 5.0 | 2018-10-01 |  | L | Solar Photovoltaic | Yellow Jacket |
| 2018-07-01 | 2018-08-01 | 61873 | GEN1 | 5.0 | 2018-10-01 |  | U | Solar Photovoltaic | Yellow Jacket |
| 2018-08-01 | 2018-09-01 | 61873 | GEN1 | 5.0 | 2018-10-01 |  | V | Solar Photovoltaic | Yellow Jacket |
| 2018-09-01 | 2018-11-01 | 61873 | GEN1 | 5.0 | 2018-11-01 |  | V | Solar Photovoltaic | Yellow Jacket |
| 2018-11-01 | 2022-04-01 | 61873 | GEN1 | 5.0 |  | 2018-11-01 | OP | Solar Photovoltaic | Yellow Jacket |
| 2022-04-01 | 2026-08-01 | 61873 | GEN1 | 5.0 |  | 2018-11-01 | OP | Solar Photovoltaic | Yellow Jacket |
| 2018-06-01 | 2022-03-01 | 61877 | HAN01 | 4.9 |  | 2018-04-01 | OP | Solar Photovoltaic | Hanover Solar, LLC |
| 2022-03-01 | 2022-04-01 | 61877 | HAN01 | 4.9 |  | 2018-04-01 | OP | Solar Photovoltaic | Hanover Solar, LLC |
| 2022-04-01 | 2022-11-01 | 61877 | HAN01 | 4.9 |  | 2018-04-01 | OP | Solar Photovoltaic | Hanover Solar, LLC |
| 2022-11-01 | 2024-01-01 | 61877 | HAN01 | 4.9 |  | 2018-04-01 | OP | Solar Photovoltaic | Hanover Solar, LLC |
| 2024-01-01 | 2026-08-01 | 61877 | HAN01 | 4.9 |  | 2018-04-01 | OP | Solar Photovoltaic | Hanover Solar, LLC |
| 2018-07-01 | 2018-09-01 | 61928 | GEN1 | 4.9 | 2018-10-01 |  | P | Solar Photovoltaic | Saint Albans Solar |
| 2018-09-01 | 2018-10-01 | 61928 | GEN1 | 4.9 | 2018-10-01 |  | V | Solar Photovoltaic | Saint Albans Solar |
| 2018-10-01 | 2022-04-01 | 61928 | GEN1 | 4.9 |  | 2018-10-01 | OP | Solar Photovoltaic | Saint Albans Solar |
| 2022-04-01 | 2026-08-01 | 61928 | GEN1 | 4.9 |  | 2018-10-01 | OP | Solar Photovoltaic | Saint Albans Solar |
| 2018-08-01 | 2018-09-01 | 61978 | GEN1 | 5.0 | 2018-11-01 |  | T | Solar Photovoltaic | Pinesage |
| 2018-09-01 | 2018-11-01 | 61978 | GEN1 | 5.0 | 2018-11-01 |  | V | Solar Photovoltaic | Pinesage |
| 2018-11-01 | 2018-12-01 | 61978 | GEN1 | 5.0 | 2018-12-01 |  | V | Solar Photovoltaic | Pinesage |
| 2018-12-01 | 2022-04-01 | 61978 | GEN1 | 5.0 |  | 2018-12-01 | OP | Solar Photovoltaic | Pinesage |
| 2022-04-01 | 2026-08-01 | 61978 | GEN1 | 5.0 |  | 2018-12-01 | OP | Solar Photovoltaic | Pinesage |
| 2018-08-01 | 2018-09-01 | 61983 | COTG | 4.9 | 2018-10-01 |  | TS | Solar Photovoltaic | Cottage Grove Project |
| 2018-09-01 | 2018-10-01 | 61983 | COTG | 4.9 | 2018-10-01 |  | TS | Solar Photovoltaic | Cottage Grove Project CSG |
| 2018-10-01 | 2018-12-01 | 61983 | COTG | 4.9 |  | 2018-10-01 | OP | Solar Photovoltaic | Cottage Grove Project CSG |
| 2018-12-01 | 2022-04-01 | 61983 | COTG | 4.9 |  | 2018-10-01 | OP | Solar Photovoltaic | Cottage Grove Project CSG |
| 2022-04-01 | 2025-10-01 | 61983 | COTG | 4.9 |  | 2018-10-01 | OP | Solar Photovoltaic | Cottage Grove Project CSG |
| 2025-10-01 | 2026-08-01 | 61983 | COTG | 4.9 |  | 2018-10-01 | OP | Solar Photovoltaic | Cottage Grove Project CSG |
| 2018-09-01 | 2018-10-01 | 62056 | LANC | 3.0 | 2018-11-01 |  | U | Solar Photovoltaic | Lancaster |
| 2018-10-01 | 2018-11-01 | 62056 | LANC | 3.0 | 2018-11-01 |  | TS | Solar Photovoltaic | Lancaster |
| 2018-11-01 | 2018-12-01 | 62056 | LANC | 3.0 |  | 2018-11-01 | OP | Solar Photovoltaic | Lancaster |
| 2018-12-01 | 2019-06-01 | 62056 | LANC | 3.0 |  | 2018-11-01 | OP | Solar Photovoltaic | Lancaster |
| 2019-06-01 | 2022-04-01 | 62056 | LANC | 3.0 |  | 2018-11-01 | OP | Solar Photovoltaic | Lancaster |
| 2022-04-01 | 2023-01-01 | 62056 | LANC | 3.0 |  | 2018-11-01 | OP | Solar Photovoltaic | Lancaster |
| 2023-01-01 | 2023-05-01 | 62056 | LANC | 3.0 |  | 2018-11-01 | OP | Solar Photovoltaic | Lancaster |
| 2023-05-01 | 2026-08-01 | 62056 | LANC | 3.0 |  | 2018-11-01 | OP | Solar Photovoltaic | Lancaster |
| 2018-09-01 | 2018-11-01 | 62098 | TILLE | 5.0 | 2018-11-01 |  | TS | Solar Photovoltaic | Tiller CSG |
| 2018-11-01 | 2018-12-01 | 62098 | TILLE | 5.0 | 2018-12-01 |  | TS | Solar Photovoltaic | Tiller CSG |
| 2018-12-01 | 2022-04-01 | 62098 | TILLE | 5.0 |  | 2018-12-01 | OP | Solar Photovoltaic | Tiller CSG |
| 2022-04-01 | 2025-10-01 | 62098 | TILLE | 5.0 |  | 2018-12-01 | OP | Solar Photovoltaic | Tiller CSG |
| 2025-10-01 | 2026-08-01 | 62098 | TILLE | 5.0 |  | 2018-12-01 | OP | Solar Photovoltaic | Tiller CSG |
| 2018-09-01 | 2018-12-01 | 62133 | GT1 | 200.0 | 2018-12-01 |  | V | Onshore Wind Turbine | North English |
| 2018-12-01 | 2022-02-01 | 62133 | GT1 | 200.0 |  | 2018-12-01 | OP | Onshore Wind Turbine | North English |
| 2022-02-01 | 2026-08-01 | 62133 | GT1 | 200.0 |  | 2018-12-01 | OP | Onshore Wind Turbine | North English |
| 2018-11-01 | 2018-12-01 | 62168 | CHU01 | 5.0 |  | 2018-08-01 | OP | Solar Photovoltaic | Church Road Solar LLC |
| 2018-12-01 | 2019-05-01 | 62168 | CHU01 | 5.0 |  | 2018-08-01 | OP | Solar Photovoltaic | Church Road Solar LLC |
| 2019-05-01 | 2022-03-01 | 62168 | CHU01 | 5.0 |  | 2018-08-01 | OP | Solar Photovoltaic | Church Road Solar LLC |
| 2022-03-01 | 2022-04-01 | 62168 | CHU01 | 5.0 |  | 2018-08-01 | OP | Solar Photovoltaic | Church Road Solar LLC |
| 2022-04-01 | 2022-11-01 | 62168 | CHU01 | 5.0 |  | 2018-08-01 | OP | Solar Photovoltaic | Church Road Solar LLC |
| 2022-11-01 | 2024-01-01 | 62168 | CHU01 | 5.0 |  | 2018-08-01 | OP | Solar Photovoltaic | Church Road Solar LLC |
| 2024-01-01 | 2026-08-01 | 62168 | CHU01 | 5.0 |  | 2018-08-01 | OP | Solar Photovoltaic | Church Road Solar LLC |
| 2018-12-01 | 2019-05-01 | 62303 | MF01 | 2.0 |  | 2018-11-01 | OP | Solar Photovoltaic | Mattas Farms |
| 2019-05-01 | 2022-04-01 | 62303 | MF01 | 2.0 |  | 2018-11-01 | OP | Solar Photovoltaic | Mattas Farms |
| 2022-04-01 | 2026-08-01 | 62303 | MF01 | 2.0 |  | 2018-11-01 | OP | Solar Photovoltaic | Mattas Farms |
| 2018-12-01 | 2022-04-01 | 62368 | 62591 | 4.8 |  | 2018-12-01 | OP | Solar Photovoltaic | BWC Origination 18 |
| 2022-04-01 | 2026-08-01 | 62368 | 62591 | 4.8 |  | 2018-12-01 | OP | Solar Photovoltaic | BWC Origination 18 |
| 2019-02-01 | 2022-04-01 | 62557 | MONTA | 4.0 |  | 2018-06-01 | OP | Solar Photovoltaic | Kearsarge Montague |
| 2022-04-01 | 2026-08-01 | 62557 | MONTA | 4.0 |  | 2018-06-01 | OP | Solar Photovoltaic | Kearsarge Montague |
| 2019-02-01 | 2022-04-01 | 62558 | SKSC2 | 3.1 |  | 2018-10-01 | OP | Solar Photovoltaic | Kearsarge SKSC2 LLC |
| 2022-04-01 | 2026-08-01 | 62558 | SKSC2 | 3.1 |  | 2018-10-01 | OP | Solar Photovoltaic | Kearsarge SKSC2 LLC |
| 2019-03-01 | 2022-04-01 | 62583 | 5823 | 5.0 |  | 2018-11-01 | OP | Solar Photovoltaic | Tanglewood Circle Solar 1 LLC |
| 2022-04-01 | 2026-08-01 | 62583 | 5823 | 5.0 |  | 2018-11-01 | OP | Solar Photovoltaic | Tanglewood Circle Solar 1 LLC |
| 2019-04-01 | 2019-05-01 | 62692 | PGR04 | 5.0 |  | 2018-03-01 | OP | Solar Photovoltaic | Sandy Solar |
| 2019-05-01 | 2022-04-01 | 62692 | PGR04 | 5.0 |  | 2018-03-01 | OP | Solar Photovoltaic | Sandy Solar |
| 2022-04-01 | 2026-01-01 | 62692 | PGR04 | 5.0 |  | 2018-03-01 | OP | Solar Photovoltaic | Sandy Solar |
| 2026-01-01 | 2026-08-01 | 62692 | PGR04 | 5.0 |  | 2018-03-01 | OP | Solar Photovoltaic | Sandy Solar |
| 2019-04-01 | 2019-05-01 | 62693 | PGR03 | 5.0 |  | 2018-02-01 | OP | Solar Photovoltaic | Chowan Jehu Solar |
| 2019-05-01 | 2022-04-01 | 62693 | PGR03 | 5.0 |  | 2018-02-01 | OP | Solar Photovoltaic | Chowan Jehu Solar |
| 2022-04-01 | 2026-01-01 | 62693 | PGR03 | 5.0 |  | 2018-02-01 | OP | Solar Photovoltaic | Chowan Jehu Solar |
| 2026-01-01 | 2026-08-01 | 62693 | PGR03 | 5.0 |  | 2018-02-01 | OP | Solar Photovoltaic | Chowan Jehu Solar |
| 2018-07-01 | 2018-08-01 | 628 | 1GTA | 310.3 | 2018-09-01 |  | V | Natural Gas Fired Combined Cycle | Crystal River |
| 2018-08-01 | 2018-10-01 | 628 | 1GTA | 310.3 | 2018-10-01 |  | V | Natural Gas Fired Combined Cycle | Crystal River |
| 2018-10-01 | 2019-01-01 | 628 | 1GTA | 310.3 |  | 2018-10-01 | OP | Natural Gas Fired Combined Cycle | Crystal River |
| 2019-01-01 | 2020-03-01 | 628 | 1GTA | 310.3 |  | 2018-10-01 | OP | Natural Gas Fired Combined Cycle | Crystal River |
| 2020-03-01 | 2022-01-01 | 628 | 1GTA | 310.3 |  | 2018-10-01 | OP | Natural Gas Fired Combined Cycle | Crystal River |
| 2022-01-01 | 2026-08-01 | 628 | 1GTA | 310.3 |  | 2018-10-01 | OP | Natural Gas Fired Combined Cycle | Crystal River |
| 2018-07-01 | 2018-08-01 | 628 | 1GTB | 310.3 | 2018-09-01 |  | V | Natural Gas Fired Combined Cycle | Crystal River |
| 2018-08-01 | 2018-10-01 | 628 | 1GTB | 310.3 | 2018-10-01 |  | V | Natural Gas Fired Combined Cycle | Crystal River |
| 2018-10-01 | 2019-01-01 | 628 | 1GTB | 310.3 |  | 2018-10-01 | OP | Natural Gas Fired Combined Cycle | Crystal River |
| 2019-01-01 | 2020-03-01 | 628 | 1GTB | 310.3 |  | 2018-10-01 | OP | Natural Gas Fired Combined Cycle | Crystal River |
| 2020-03-01 | 2022-01-01 | 628 | 1GTB | 310.3 |  | 2018-10-01 | OP | Natural Gas Fired Combined Cycle | Crystal River |
| 2022-01-01 | 2026-08-01 | 628 | 1GTB | 310.3 |  | 2018-10-01 | OP | Natural Gas Fired Combined Cycle | Crystal River |
| 2018-07-01 | 2018-11-01 | 628 | 2GTA | 310.3 | 2018-12-01 |  | V | Natural Gas Fired Combined Cycle | Crystal River |
| 2018-11-01 | 2020-03-01 | 628 | 2GTA | 310.3 |  | 2018-11-01 | OP | Natural Gas Fired Combined Cycle | Crystal River |
| 2020-03-01 | 2022-01-01 | 628 | 2GTA | 310.3 |  | 2018-11-01 | OP | Natural Gas Fired Combined Cycle | Crystal River |
| 2022-01-01 | 2024-06-01 | 628 | 2GTA | 310.3 |  | 2018-11-01 | OP | Natural Gas Fired Combined Cycle | Crystal River |
| 2024-06-01 | 2026-08-01 | 628 | 2GTA | 310.3 |  | 2018-11-01 | OP | Natural Gas Fired Combined Cycle | Crystal River |
| 2018-07-01 | 2018-11-01 | 628 | 2GTB | 310.3 | 2018-12-01 |  | V | Natural Gas Fired Combined Cycle | Crystal River |
| 2018-11-01 | 2020-03-01 | 628 | 2GTB | 310.3 |  | 2018-11-01 | OP | Natural Gas Fired Combined Cycle | Crystal River |
| 2020-03-01 | 2022-01-01 | 628 | 2GTB | 310.3 |  | 2018-11-01 | OP | Natural Gas Fired Combined Cycle | Crystal River |
| 2022-01-01 | 2024-06-01 | 628 | 2GTB | 310.3 |  | 2018-11-01 | OP | Natural Gas Fired Combined Cycle | Crystal River |
| 2024-06-01 | 2026-08-01 | 628 | 2GTB | 310.3 |  | 2018-11-01 | OP | Natural Gas Fired Combined Cycle | Crystal River |
| 2018-07-01 | 2018-08-01 | 628 | CC1ST | 364.7 | 2018-09-01 |  | V | Natural Gas Fired Combined Cycle | Crystal River |
| 2018-08-01 | 2018-10-01 | 628 | CC1ST | 364.7 | 2018-10-01 |  | V | Natural Gas Fired Combined Cycle | Crystal River |
| 2018-10-01 | 2019-01-01 | 628 | CC1ST | 364.7 |  | 2018-10-01 | OP | Natural Gas Fired Combined Cycle | Crystal River |
| 2019-01-01 | 2020-03-01 | 628 | CC1ST | 364.7 |  | 2018-10-01 | OP | Natural Gas Fired Combined Cycle | Crystal River |
| 2020-03-01 | 2022-01-01 | 628 | CC1ST | 364.7 |  | 2018-10-01 | OP | Natural Gas Fired Combined Cycle | Crystal River |
| 2022-01-01 | 2026-08-01 | 628 | CC1ST | 364.7 |  | 2018-10-01 | OP | Natural Gas Fired Combined Cycle | Crystal River |
| 2018-07-01 | 2018-11-01 | 628 | CC2ST | 364.7 | 2018-12-01 |  | V | Natural Gas Fired Combined Cycle | Crystal River |
| 2018-11-01 | 2020-03-01 | 628 | CC2ST | 364.7 |  | 2018-11-01 | OP | Natural Gas Fired Combined Cycle | Crystal River |
| 2020-03-01 | 2022-01-01 | 628 | CC2ST | 364.7 |  | 2018-11-01 | OP | Natural Gas Fired Combined Cycle | Crystal River |
| 2022-01-01 | 2026-08-01 | 628 | CC2ST | 364.7 |  | 2018-11-01 | OP | Natural Gas Fired Combined Cycle | Crystal River |
