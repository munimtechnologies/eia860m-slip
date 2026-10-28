# nextlist 0.1.1: EIA-860M generators planned for 2026-10, with the on-time share of earlier ones like them

MV2 of Munim, Inc. (made with AI agents). Code Apache-2.0; tables CC BY 4.0. p describes what happened to earlier generators in the same technology group and listing cell; it is not a forecast made with knowledge of any plant.

Cohort file: https://raw.githubusercontent.com/munimtechnologies/eia860m-slip/ea63c150a8ed41cc1fcad901ccab51686c924d46/data/nexttech_cohort.csv (950816 bytes, md5 1681df9fdee9878ca2c359d1239c6467; 14807 rows; expected md5 1681df9fdee9878ca2c359d1239c6467: True).

## Workbooks

| month | url | bytes | md5 | as expected |
|---|---|---|---|---|
| 2026-08 | https://www.eia.gov/electricity/data/eia860m/archive/xls/august_generator2026.xlsx | 13955142 | 9727ac867236faab7d5503175dacdf38 | True |
| 2026-09 | https://www.eia.gov/electricity/data/eia860m/xls/september_generator2026.xlsx | 14013970 | 4c741eb77a5ccad5aca32ffe43f398af | True |

- 2026-08: https://www.eia.gov/electricity/data/eia860m/xls/august_generator2026.xlsx: not an xlsx file: status 200, final URL https://www.eia.gov/electricity/, Content-Type text/html; charset=UTF-8, Content-Encoding None, 55901 bytes, starts b'<!doctype html>\r\n<html>\r\n<head>\r\n\t<title>Electricity - U.S. Energy Information Administration (EIA)</title>\r\n\t<meta property="og:title" content="Electricity - U'

## Checks

- C1 (practice 2026-09): held. List 170 rows, cohort file 170; only in the list none; only in the cohort file none; technology group differs for 0.
- C2 (practice 2026-09): the practice list's Brier scores equal the backtest's for that month: held ([0.2147253162, 0.2229562762, 0.2255703716] against [0.2147253162, 0.2229562762, 0.2255703716]).

## Backtest, 2020-01 to 2026-09 (each month from the 48 months before it only)

10237 generator-months at 3531 plants; on time 3659, expected by p 3941.2.

| forecast | Brier score | minus r0 (95% interval, plants resampled) | minus r1 |
|---|---|---|---|
| p (group and cell) | 0.2295 | -0.0016 (-0.0034 to +0.0003) | -0.0004 (-0.0019 to +0.0010) |
| r0 (all rows) | 0.2311 | | |
| r1 (group) | 0.2300 | | |

Months where p's Brier score is below r0's: 43 of 81; below r1's: 47 of 81. 2000 resamples, seed 20261026.

### Calibration, pooled

| p from | p to | generator-months | mean p | on-time share |
|---|---|---|---|---|
| 0.0 | 0.2 | 137 | 0.1871 | 0.3723 |
| 0.2 | 0.3 | 1667 | 0.2536 | 0.2543 |
| 0.3 | 0.4 | 3879 | 0.3590 | 0.3511 |
| 0.4 | 0.5 | 3726 | 0.4443 | 0.3929 |
| 0.5 | 0.6 | 810 | 0.5357 | 0.4407 |
| 0.6 | 1.0 | 18 | 0.6189 | 0.0556 |

### By month

| month | rows | on time | expected | Brier p | Brier r0 | Brier r1 |
|---|---|---|---|---|---|---|
| 2020-01 | 90 | 44 | 43.2 | 0.2445 | 0.2503 | 0.2473 |
| 2020-02 | 72 | 29 | 34.4 | 0.2469 | 0.2449 | 0.2361 |
| 2020-03 | 97 | 40 | 45.2 | 0.2522 | 0.2457 | 0.2426 |
| 2020-04 | 85 | 30 | 39.0 | 0.2477 | 0.2420 | 0.2409 |
| 2020-05 | 71 | 34 | 32.5 | 0.2634 | 0.2497 | 0.2543 |
| 2020-06 | 82 | 34 | 39.3 | 0.2375 | 0.2452 | 0.2410 |
| 2020-07 | 80 | 29 | 37.2 | 0.2577 | 0.2419 | 0.2463 |
| 2020-08 | 71 | 25 | 33.6 | 0.2479 | 0.2403 | 0.2434 |
| 2020-09 | 100 | 21 | 46.8 | 0.2314 | 0.2290 | 0.2274 |
| 2020-10 | 128 | 49 | 60.0 | 0.2391 | 0.2417 | 0.2470 |
| 2020-11 | 115 | 35 | 52.7 | 0.2382 | 0.2350 | 0.2324 |
| 2020-12 | 269 | 170 | 125.8 | 0.2563 | 0.2637 | 0.2586 |
| 2021-01 | 105 | 37 | 49.1 | 0.2507 | 0.2388 | 0.2431 |
| 2021-02 | 98 | 20 | 43.1 | 0.2232 | 0.2241 | 0.2187 |
| 2021-03 | 128 | 44 | 55.9 | 0.2319 | 0.2364 | 0.2330 |
| 2021-04 | 144 | 43 | 63.0 | 0.2308 | 0.2305 | 0.2363 |
| 2021-05 | 120 | 33 | 52.3 | 0.2330 | 0.2263 | 0.2247 |
| 2021-06 | 156 | 53 | 66.0 | 0.2341 | 0.2337 | 0.2324 |
| 2021-07 | 116 | 41 | 50.4 | 0.2421 | 0.2348 | 0.2379 |
| 2021-08 | 99 | 38 | 42.7 | 0.2346 | 0.2388 | 0.2244 |
| 2021-09 | 113 | 46 | 46.8 | 0.2607 | 0.2420 | 0.2406 |
| 2021-10 | 145 | 77 | 58.0 | 0.2847 | 0.2589 | 0.2763 |
| 2021-11 | 153 | 58 | 64.0 | 0.2361 | 0.2385 | 0.2390 |
| 2021-12 | 189 | 96 | 82.2 | 0.2486 | 0.2559 | 0.2472 |
| 2022-01 | 84 | 27 | 35.9 | 0.2269 | 0.2288 | 0.2300 |
| 2022-02 | 93 | 26 | 39.2 | 0.2193 | 0.2222 | 0.2240 |
| 2022-03 | 129 | 52 | 54.7 | 0.2421 | 0.2409 | 0.2456 |
| 2022-04 | 86 | 23 | 36.4 | 0.2215 | 0.2192 | 0.2307 |
| 2022-05 | 112 | 31 | 47.0 | 0.2117 | 0.2196 | 0.2176 |
| 2022-06 | 145 | 50 | 55.7 | 0.2134 | 0.2304 | 0.2198 |
| 2022-07 | 105 | 37 | 40.9 | 0.2369 | 0.2316 | 0.2262 |
| 2022-08 | 115 | 35 | 44.9 | 0.2308 | 0.2221 | 0.2224 |
| 2022-09 | 101 | 26 | 38.3 | 0.2009 | 0.2126 | 0.1986 |
| 2022-10 | 92 | 32 | 36.5 | 0.2453 | 0.2295 | 0.2382 |
| 2022-11 | 87 | 29 | 34.4 | 0.2174 | 0.2262 | 0.2272 |
| 2022-12 | 177 | 60 | 67.6 | 0.2075 | 0.2272 | 0.2156 |
| 2023-01 | 118 | 38 | 44.3 | 0.2124 | 0.2222 | 0.2133 |
| 2023-02 | 106 | 29 | 37.9 | 0.2029 | 0.2100 | 0.2013 |
| 2023-03 | 129 | 34 | 45.6 | 0.1855 | 0.2074 | 0.1964 |
| 2023-04 | 129 | 38 | 47.0 | 0.2042 | 0.2145 | 0.2044 |
| 2023-05 | 118 | 24 | 43.4 | 0.1841 | 0.1914 | 0.1817 |
| 2023-06 | 118 | 33 | 42.3 | 0.2128 | 0.2100 | 0.2149 |
| 2023-07 | 127 | 52 | 45.3 | 0.2444 | 0.2436 | 0.2537 |
| 2023-08 | 118 | 34 | 42.2 | 0.2041 | 0.2114 | 0.2118 |
| 2023-09 | 113 | 36 | 42.0 | 0.2112 | 0.2194 | 0.2149 |
| 2023-10 | 97 | 24 | 35.0 | 0.1985 | 0.1998 | 0.2004 |
| 2023-11 | 126 | 43 | 46.0 | 0.2214 | 0.2253 | 0.2265 |
| 2023-12 | 211 | 105 | 74.2 | 0.2650 | 0.2685 | 0.2720 |
| 2024-01 | 95 | 32 | 33.8 | 0.2151 | 0.2240 | 0.2154 |
| 2024-02 | 79 | 28 | 27.8 | 0.2195 | 0.2288 | 0.2208 |
| 2024-03 | 130 | 59 | 43.2 | 0.2699 | 0.2571 | 0.2676 |
| 2024-04 | 118 | 24 | 43.6 | 0.1993 | 0.1863 | 0.1846 |
| 2024-05 | 124 | 46 | 42.3 | 0.2352 | 0.2336 | 0.2398 |
| 2024-06 | 141 | 41 | 47.5 | 0.2019 | 0.2103 | 0.2038 |
| 2024-07 | 132 | 37 | 45.2 | 0.2078 | 0.2069 | 0.2011 |
| 2024-08 | 118 | 32 | 40.7 | 0.2069 | 0.2040 | 0.2048 |
| 2024-09 | 119 | 42 | 40.5 | 0.2292 | 0.2284 | 0.2349 |
| 2024-10 | 123 | 27 | 42.6 | 0.1982 | 0.1888 | 0.1950 |
| 2024-11 | 151 | 64 | 54.4 | 0.2445 | 0.2499 | 0.2497 |
| 2024-12 | 295 | 160 | 98.8 | 0.2870 | 0.2849 | 0.2873 |
| 2025-01 | 140 | 52 | 50.6 | 0.2323 | 0.2340 | 0.2280 |
| 2025-02 | 83 | 27 | 29.9 | 0.2172 | 0.2200 | 0.2200 |
| 2025-03 | 127 | 44 | 42.5 | 0.2266 | 0.2264 | 0.2331 |
| 2025-04 | 112 | 48 | 38.8 | 0.2372 | 0.2510 | 0.2465 |
| 2025-05 | 133 | 51 | 45.3 | 0.2349 | 0.2373 | 0.2377 |
| 2025-06 | 138 | 50 | 49.5 | 0.2315 | 0.2311 | 0.2322 |
| 2025-07 | 166 | 52 | 57.3 | 0.2204 | 0.2169 | 0.2236 |
| 2025-08 | 136 | 58 | 51.6 | 0.2390 | 0.2497 | 0.2421 |
| 2025-09 | 121 | 27 | 43.0 | 0.1977 | 0.1909 | 0.1957 |
| 2025-10 | 138 | 58 | 54.0 | 0.2501 | 0.2483 | 0.2516 |
| 2025-11 | 100 | 42 | 34.9 | 0.2574 | 0.2486 | 0.2425 |
| 2025-12 | 192 | 91 | 69.5 | 0.2515 | 0.2647 | 0.2592 |
| 2026-01 | 136 | 46 | 49.9 | 0.2146 | 0.2239 | 0.2182 |
| 2026-02 | 114 | 20 | 38.6 | 0.1793 | 0.1748 | 0.1729 |
| 2026-03 | 156 | 38 | 54.2 | 0.1905 | 0.1949 | 0.1944 |
| 2026-04 | 168 | 71 | 58.9 | 0.2473 | 0.2503 | 0.2493 |
| 2026-05 | 140 | 35 | 47.0 | 0.1848 | 0.1968 | 0.1914 |
| 2026-06 | 216 | 70 | 73.8 | 0.2096 | 0.2195 | 0.2195 |
| 2026-07 | 140 | 47 | 50.7 | 0.2323 | 0.2231 | 0.2219 |
| 2026-08 | 124 | 39 | 45.8 | 0.2134 | 0.2165 | 0.2044 |
| 2026-09 | 170 | 57 | 55.4 | 0.2147 | 0.2230 | 0.2256 |

## Practice list: 2026-09 (from EIA's 2026-08 workbook)

170 generators at 146 plants, 13854.0 MW. Expected on time by p: 55.4 generators, 4799.5 MW.

| group | cell | generators | MW | p | p from | rows behind p |
|---|---|---|---|---|---|---|
| batteries | first | 16 | 1171.7 | 0.2810 | group and cell | 573 |
| batteries | 1 month | 11 | 623.0 | 0.3504 | group and cell | 682 |
| batteries | 2-3 months | 10 | 955.6 | 0.2059 | group and cell | 238 |
| batteries | 4-12 months | 6 | 631.0 | 0.3431 | group and cell | 137 |
| gas | 1 month | 6 | 1335.6 | 0.4713 | group and cell | 87 |
| gas | 2-3 months | 1 | 594.0 | 0.5741 | group and cell | 54 |
| other | 2-3 months | 6 | 2.8 | 0.1471 | group and cell | 34 |
| solar | first | 41 | 2346.2 | 0.3598 | group and cell | 1584 |
| solar | 1 month | 35 | 3120.2 | 0.3876 | group and cell | 1473 |
| solar | 2-3 months | 24 | 2120.8 | 0.2724 | group and cell | 558 |
| solar | 4-12 months | 7 | 467.5 | 0.1929 | group and cell | 254 |
| solar | more than 12 months | 2 | 9.8 | 0.1818 | group and cell | 33 |
| wind | first | 4 | 210.8 | 0.4865 | group and cell | 111 |
| wind | 2-3 months | 1 | 265.0 | 0.1579 | group and cell | 38 |

Scored: 170 rows (0 without an outcome); on time 57 against 55.4 expected; MW on time 4403.3 against 4799.5 expected. Brier p 0.2147, r0 0.2230, r1 0.2256; p minus r0 -0.0214 to +0.0047; p minus r1 -0.0209 to -0.0012.

| key | plant | state | technology | MW | status | cell | p |
|---|---|---|---|---|---|---|---|
| 165/4 | GREC | OK | Natural Gas Fired Combustion Turbine | 594.0 | TS | 2-3 months | 0.5741 |
| 68197/ROCKY | Rocky Forge Wind | VA | Onshore Wind Turbine | 78.0 | V | first | 0.4865 |
| 68981/GRWF3 | Gonzaga Ridge Wind Farm | CA | Onshore Wind Turbine | 57.9 | V | first | 0.4865 |
| 68981/GRWF1 | Gonzaga Ridge Wind Farm | CA | Onshore Wind Turbine | 40.3 | V | first | 0.4865 |
| 68981/GRWF2 | Gonzaga Ridge Wind Farm | CA | Onshore Wind Turbine | 34.6 | V | first | 0.4865 |
| 66621/1A | Orange County Advanced Power Station | TX | Natural Gas Fired Combined Cycle | 453.0 | TS | 1 month | 0.4713 |
| 66621/1B | Orange County Advanced Power Station | TX | Natural Gas Fired Combined Cycle | 453.0 | TS | 1 month | 0.4713 |
| 66621/1C | Orange County Advanced Power Station | TX | Natural Gas Fired Combined Cycle | 400.0 | TS | 1 month | 0.4713 |
| 1239/13 | Riverton | KS | Natural Gas Fired Combustion Turbine | 13.5 | TS | 1 month | 0.4713 |
| 1239/14 | Riverton | KS | Natural Gas Fired Combustion Turbine | 13.5 | TS | 1 month | 0.4713 |
| 54808/GR1 | New York University Central Plant | NY | Natural Gas Internal Combustion Engine | 2.6 | V | 1 month | 0.4713 |
| 66914/DAN | Danish Fields Solar, LLC | TX | Solar Photovoltaic | 600.0 | TS | 1 month | 0.3876 |
| 66912/HS1 | Hill Solar 1 | TX | Solar Photovoltaic | 405.0 | TS | 1 month | 0.3876 |
| 66915/CTW | Cottonwood Bayou Solar | TX | Solar Photovoltaic | 350.0 | TS | 1 month | 0.3876 |
| 68847/PV1 | 1000 Mile Solar | TX | Solar Photovoltaic | 300.0 | TS | 1 month | 0.3876 |
| 68592/OERHA | Rockhound A | TX | Solar Photovoltaic | 245.0 | TS | 1 month | 0.3876 |
| 66390/GDYPV | MRG Goody Solar Project Hybrid | TX | Solar Photovoltaic | 170.8 | V | 1 month | 0.3876 |
| 68410/BRAZ | Brazoria Solar I | TX | Solar Photovoltaic | 125.0 | TS | 1 month | 0.3876 |
| 68410/BRAZ2 | Brazoria Solar I | TX | Solar Photovoltaic | 125.0 | TS | 1 month | 0.3876 |
| 68155/RIOLA | Rio Lago Solar | TX | Solar Photovoltaic | 123.0 | TS | 1 month | 0.3876 |
| 68851/HSPV1 | Hermes Solar PV | TX | Solar Photovoltaic | 100.4 | V | 1 month | 0.3876 |
| 69238/ATL6 | ATLAS Solar VI, LLC | AZ | Solar Photovoltaic | 100.0 | V | 1 month | 0.3876 |
| 69197/HALIF | Halifax County Solar | NC | Solar Photovoltaic | 80.0 | U | 1 month | 0.3876 |
| 64346/9999 | Highland Solar South | FL | Solar Photovoltaic | 74.9 | V | 1 month | 0.3876 |
| 68052/PV1 | Bailey Mill Solar | FL | Solar Photovoltaic | 74.9 | V | 1 month | 0.3876 |
| 68074/CERUL | Cerulean Solar | VA | Solar Photovoltaic | 62.0 | V | 1 month | 0.3876 |
| 68593/OERHC | Rockhound C | TX | Solar Photovoltaic | 61.0 | TS | 1 month | 0.3876 |
| 68929/RUBY | Ruby Solar, LLC | IL | Solar Photovoltaic | 50.0 | V | 1 month | 0.3876 |
| 68594/OERHD | Rockhound D | TX | Solar Photovoltaic | 28.0 | TS | 1 month | 0.3876 |
| 68388/RT5SS | AES Rt 5 Solar CSG | NY | Solar Photovoltaic | 5.0 | V | 1 month | 0.3876 |
| 70242/215 | Riverhead - CVE | NY | Solar Photovoltaic | 4.9 | U | 1 month | 0.3876 |
| 68097/CHERR | SR Cherry Valley | AR | Solar Photovoltaic | 4.8 | TS | 1 month | 0.3876 |
| 70103/PS43 | Pivot Solar 43 LLC | CO | Solar Photovoltaic | 3.5 | V | 1 month | 0.3876 |
| 70185/PV1 | Copenhagen Ct | IL | Solar Photovoltaic | 3.5 | V | 1 month | 0.3876 |
| 68070/ALBER | Alberta Solar | VA | Solar Photovoltaic | 3.0 | U | 1 month | 0.3876 |
| 69220/11253 | West Genesee | NY | Solar Photovoltaic | 2.9 | V | 1 month | 0.3876 |
| 69592/PSKPV | NL NY- Pulaski | NY | Solar Photovoltaic | 2.5 | TS | 1 month | 0.3876 |
| 69052/MD11 | MDD109-NCBP BLDG 11-Manekin | MD | Solar Photovoltaic | 2.4 | V | 1 month | 0.3876 |
| 69053/IL60 | ILL060-Sangamon-Atchison | IL | Solar Photovoltaic | 2.0 | V | 1 month | 0.3876 |
| 70046/GNDHG | OER IL - Groundhog | IL | Solar Photovoltaic | 2.0 | TS | 1 month | 0.3876 |
| 70182/PV1 | Steger | IL | Solar Photovoltaic | 2.0 | V | 1 month | 0.3876 |
| 70393/S1 | Stephenson County IL S1 | IL | Solar Photovoltaic | 2.0 | V | 1 month | 0.3876 |
| 69791/NJUDC | BPL NJ - Union Distribution Center | NJ | Solar Photovoltaic | 1.5 | TS | 1 month | 0.3876 |
| 69064/NC12 | NCBP TWELVE, LLC | MD | Solar Photovoltaic | 1.2 | V | 1 month | 0.3876 |
| 68783/NY009 | NY CDG 009 | NY | Solar Photovoltaic | 1.0 | TS | 1 month | 0.3876 |
| 69616/USLYN | USS Lyndon Solar LLC | IL | Solar Photovoltaic | 1.0 | V | 1 month | 0.3876 |
| 69877/CHPV1 | Charger Solar | TX | Solar Photovoltaic | 394.4 | TS | first | 0.3598 |
| 68758/IPEA1 | Easley Solar | CA | Solar Photovoltaic | 290.0 | TS | first | 0.3598 |
| 66216/SOL | Yaupon Solar Project (Hybrid) | TX | Solar Photovoltaic | 200.0 | TS | first | 0.3598 |
| 69585/5568 | Kaufman Solar | TX | Solar Photovoltaic | 200.0 | TS | first | 0.3598 |
| 69755/5568 | King Mountain Solar | TX | Solar Photovoltaic | 175.0 | TS | first | 0.3598 |
| 69647/JCKSN | Jackson County Solar, LLC | MI | Solar Photovoltaic | 125.0 | TS | first | 0.3598 |
| 66778/HS1 | Hart Solar Project | MI | Solar Photovoltaic | 120.0 | U | first | 0.3598 |
| 64745/BHS02 | Black Hollow Sun | CO | Solar Photovoltaic | 107.0 | V | first | 0.3598 |
| 66678/IPAR1 | Aramis I Solar Project | CA | Solar Photovoltaic | 100.0 | U | first | 0.3598 |
| 69471/CLCSP | Cold Creek Solar Park | MI | Solar Photovoltaic | 100.0 | TS | first | 0.3598 |
| 65050/MRC1 | Mark Center Solar Project | OH | Solar Photovoltaic | 90.0 | U | first | 0.3598 |
| 70084/AC | Alligator Creek Solar | GA | Solar Photovoltaic | 80.0 | V | first | 0.3598 |
| 67666/SUNDN | Sundance (CO) | CO | Solar Photovoltaic | 74.9 | U | first | 0.3598 |
| 68000/BLUMN | Blue Moon | KY | Solar Photovoltaic | 70.0 | V | first | 0.3598 |
| 66313/MOCO | Moon Corner Solar | VA | Solar Photovoltaic | 60.0 | U | first | 0.3598 |
| 60434/PV1 | Baxter Creek Solar | NC | Solar Photovoltaic | 30.0 | V | first | 0.3598 |
| 69144/PV1 | Baxter Creek Solar | NC | Solar Photovoltaic | 30.0 | V | first | 0.3598 |
| 68240/SS3PV | Solar Star 3 | CA | Solar Photovoltaic | 24.0 | V | first | 0.3598 |
| 69516/HAMM | Hamms Landfill | NJ | Solar Photovoltaic | 6.0 | V | first | 0.3598 |
| 69105/SLO-2 | SLO-2 | NM | Solar Photovoltaic | 5.0 | V | first | 0.3598 |
| 69262/HILL1 | Hillsboro Solar Project | TX | Solar Photovoltaic | 5.0 | V | first | 0.3598 |
| 69262/HILL2 | Hillsboro Solar Project | TX | Solar Photovoltaic | 5.0 | V | first | 0.3598 |
| 69847/SPIL2 | Spillertown CSG 2 LLC | IL | Solar Photovoltaic | 5.0 | V | first | 0.3598 |
| 69852/MCCR1 | McCray Solar 1, LLC | IL | Solar Photovoltaic | 5.0 | U | first | 0.3598 |
| 70002/MACED | Macedon CSG LLC | NY | Solar Photovoltaic | 5.0 | U | first | 0.3598 |
| 70446/33699 | Dragon's Breath Solar LLC PV | IL | Solar Photovoltaic | 5.0 | U | first | 0.3598 |
| 70048/AIREX | City of Milwaukee- Airport Expansion | WI | Solar Photovoltaic | 4.6 | V | first | 0.3598 |
| 70201/PS50 | Pivot Solar 50 LLC | CO | Solar Photovoltaic | 4.0 | V | first | 0.3598 |
| 70181/CN001 | Prologis - SLCNJ001 - Community Solar | NJ | Solar Photovoltaic | 3.2 | TS | first | 0.3598 |
| 69842/CARN1 | Carneys Point Solar 1 LLC | NJ | Solar Photovoltaic | 3.0 | U | first | 0.3598 |
| 70447/45629 | Ember Sun LLC PV | IL | Solar Photovoltaic | 3.0 | U | first | 0.3598 |
| 69371/HALIF | Middle Road Solar Partners | PA | Solar Photovoltaic | 2.5 | V | first | 0.3598 |
| 70205/BURS2 | Bureau Solar 2 LLC | IL | Solar Photovoltaic | 2.5 | V | first | 0.3598 |
| 70206/PS57 | Pivot Solar 57 LLC | CO | Solar Photovoltaic | 2.0 | V | first | 0.3598 |
| 70448/22258 | Keithsburg North Solar LLC PV | IL | Solar Photovoltaic | 2.0 | U | first | 0.3598 |
| 69554/BELMO | BPL NJ - Belmont | NJ | Solar Photovoltaic | 1.8 | TS | first | 0.3598 |
| 70428/DRIVS | Bakersfield Driver | CA | Solar Photovoltaic | 1.7 | V | first | 0.3598 |
| 70445/PV1 | W 167th St | IL | Solar Photovoltaic | 1.5 | V | first | 0.3598 |
| 70368/R4220 | Ranch 4220 | CA | Solar Photovoltaic | 1.1 | V | first | 0.3598 |
| 65045/VCP14 | Emery Shute Solar One | ME | Solar Photovoltaic | 1.0 | V | first | 0.3598 |
| 69983/GRTKN | Novel Gertken Solar LLC | MN | Solar Photovoltaic | 1.0 | V | first | 0.3598 |
| 69255/VESP1 | Vertus Energy Storage Plant | TX | Batteries | 200.0 | U | 1 month | 0.3504 |
| 69290/DSBLM | Desert Bloom | AZ | Batteries | 150.0 | TS | 1 month | 0.3504 |
| 69423/BCNV2 | Bocanova Energy Storage II | TX | Batteries | 150.0 | V | 1 month | 0.3504 |
| 66390/GDYES | MRG Goody Solar Project Hybrid | TX | Batteries | 50.4 | V | 1 month | 0.3504 |
| 70232/EVERG | Evergreen Energy Center, LLC | VA | Batteries | 20.0 | V | 1 month | 0.3504 |
| 66785/ELVAK | Elevate Arthur Kill | NY | Batteries | 15.1 | TS | 1 month | 0.3504 |
| 69988/WBA2 | Warsaw 2 Energy Storage | NC | Batteries | 11.0 | V | 1 month | 0.3504 |
| 69457/MEBA1 | Mesquite Clean Energy Center (BESS) | TX | Batteries | 10.1 | TS | 1 month | 0.3504 |
| 69318/APPLE | Apple BESS | TX | Batteries | 9.9 | TS | 1 month | 0.3504 |
| 70242/216 | Riverhead - CVE | NY | Batteries | 4.0 | U | 1 month | 0.3504 |
| 69592/PSKBS | NL NY- Pulaski | NY | Batteries | 2.5 | TS | 1 month | 0.3504 |
| 69778/HK1ST | Hashknife Energy Center LLC | AZ | Batteries | 275.0 | V | 4-12 months | 0.3431 |
| 65880/ZEYA | Zeya | TX | Batteries | 250.0 | U | 4-12 months | 0.3431 |
| 68466/CFB3 | Centennial Flats | AZ | Batteries | 89.0 | U | 4-12 months | 0.3431 |
| 66410/596 | Grizzly Ridge Solar | TX | Batteries | 10.0 | TS | 4-12 months | 0.3431 |
| 66497/BHBA1 | Bensonhurst Energy Storage 1 LLC | NY | Batteries | 5.0 | U | 4-12 months | 0.3431 |
| 67283/6569B | Six Flags Magic Mountain | CA | Batteries | 2.0 | V | 4-12 months | 0.3431 |
| 69684/70125 | Maricopa Solar | AZ | Batteries | 550.0 | U | first | 0.2810 |
| 69424/FBS1 | Faraday Energy Storage | UT | Batteries | 150.0 | U | first | 0.2810 |
| 66678/IPARB | Aramis I Solar Project | CA | Batteries | 100.0 | U | first | 0.2810 |
| 708/5 | Hammond | GA | Batteries | 57.5 | V | first | 0.2810 |
| 68980/GRBF | Gonzaga Ridge Battery Facility | CA | Batteries | 51.8 | V | first | 0.2810 |
| 65043/DUST | Dulles Solar and Storage | VA | Batteries | 50.0 | V | first | 0.2810 |
| 67666/SUNBA | Sundance (CO) | CO | Batteries | 50.0 | U | first | 0.2810 |
| 69964/BALBE | Baldy Mesa Storage | CA | Batteries | 50.0 | V | first | 0.2810 |
| 69404/CRAGB | Craggy Energy Storage | NC | Batteries | 30.5 | V | first | 0.2810 |
| 67669/ABESS | Arlington Battery Energy Storage System | WA | Batteries | 25.0 | U | first | 0.2810 |
| 69444/ECB1 | Elm City BESS | NC | Batteries | 20.0 | V | first | 0.2810 |
| 69429/AVLB1 | Asheville BESS | NC | Batteries | 17.3 | U | first | 0.2810 |
| 65897/INPKY | Industrial Parkway Storage | CA | Batteries | 9.8 | TS | first | 0.2810 |
| 69551/90915 | Holyoke MA BESS 1 | MA | Batteries | 5.0 | U | first | 0.2810 |
| 69195/LONTB | Longtown Energy Storage | SC | Batteries | 4.5 | V | first | 0.2810 |
| 70428/DRIVB | Bakersfield Driver | CA | Batteries | 0.3 | V | first | 0.2810 |
| 65028/ROSES | Roseland Solar Project, LLC | TX | Solar Photovoltaic | 500.0 | TS | 2-3 months | 0.2724 |
| 68065/CHILS | Chillingham Solar | TX | Solar Photovoltaic | 350.0 | TS | 2-3 months | 0.2724 |
| 69150/SYPRT | Sypert Branch Solar | TX | Solar Photovoltaic | 293.9 | U | 2-3 months | 0.2724 |
| 67837/RAYRS | Ray Ranch Solar | TX | Solar Photovoltaic | 255.2 | TS | 2-3 months | 0.2724 |
| 69149/ANSN2 | Anson 2 Solar | TX | Solar Photovoltaic | 218.5 | V | 2-3 months | 0.2724 |
| 64672/BLUJS | Blue Jay Solar I, LLC | TX | Solar Photovoltaic | 210.0 | TS | 2-3 months | 0.2724 |
| 67552/ELMFL | Elm Flats Solar | TX | Solar Photovoltaic | 125.0 | U | 2-3 months | 0.2724 |
| 65043/DUSO | Dulles Solar and Storage | VA | Solar Photovoltaic | 100.0 | V | 2-3 months | 0.2724 |
| 66066/WAIPV | AES Waiawa Phase 2 Solar | HI | Solar Photovoltaic | 30.0 | V | 2-3 months | 0.2724 |
| 68392/IL2PV | IL2 - W109 | IL | Solar Photovoltaic | 4.9 | TS | 2-3 months | 0.2724 |
| 70010/167 | Pescara 1 | NY | Solar Photovoltaic | 4.9 | U | 2-3 months | 0.2724 |
| 70011/168 | Pescara 2 | NY | Solar Photovoltaic | 4.9 | U | 2-3 months | 0.2724 |
| 69896/7999G | 7999 Gateway Solar | CA | Solar Photovoltaic | 4.6 | U | 2-3 months | 0.2724 |
| 70051/GRISS | Kearsarge Grissom | NH | Solar Photovoltaic | 4.0 | TS | 2-3 months | 0.2724 |
| 66516/19500 | TX Dallas 7750 Dynasty Drive | TX | Solar Photovoltaic | 2.3 | TS | 2-3 months | 0.2724 |
| 68118/CH404 | Addison 11-SLCHI404 | IL | Solar Photovoltaic | 1.6 | TS | 2-3 months | 0.2724 |
| 68142/CH303 | Northlake 3-SLCHI303 | IL | Solar Photovoltaic | 1.6 | U | 2-3 months | 0.2724 |
| 70095/IN015 | Perris DC 5 - sline015 | CA | Solar Photovoltaic | 1.6 | TS | 2-3 months | 0.2724 |
| 69891/LA100 | Torrance Dis Ctr 2 - SLLAX100 | CA | Solar Photovoltaic | 1.4 | TS | 2-3 months | 0.2724 |
| 70099/IL007 | Pivot Energy IL 7 LLC | IL | Solar Photovoltaic | 1.4 | V | 2-3 months | 0.2724 |
| 68790/LA512 | Dominguez - SLLAX512 | CA | Solar Photovoltaic | 1.3 | TS | 2-3 months | 0.2724 |
| 68793/LA710 | Bandini - SLLAX710 | CA | Solar Photovoltaic | 1.3 | TS | 2-3 months | 0.2724 |
| 68789/LA104 | South Bay Dis Ctr 12 - SLLAX104 | CA | Solar Photovoltaic | 1.2 | U | 2-3 months | 0.2724 |
| 69790/EZMLC | Elizabeth Metropolitan Logistics Center | NJ | Solar Photovoltaic | 1.2 | TS | 2-3 months | 0.2724 |
| 65870/CASTR | Castor | TX | Batteries | 200.0 | U | 2-3 months | 0.2059 |
| 68581/MTB | Mendoza Trail BESS | TX | Batteries | 200.0 | TS | 2-3 months | 0.2059 |
| 68582/PPB | Pintail BESS | TX | Batteries | 200.0 | TS | 2-3 months | 0.2059 |
| 68866/SAN | Santa Teresa Solar | NM | Batteries | 150.0 | V | 2-3 months | 0.2059 |
| 64531/KOV4A | Noosa Energy Storage LLC | CA | Batteries | 99.0 | U | 2-3 months | 0.2059 |
| 67552/ELMBA | Elm Flats Solar | TX | Batteries | 50.0 | U | 2-3 months | 0.2059 |
| 66066/WAIBA | AES Waiawa Phase 2 Solar | HI | Batteries | 30.0 | V | 2-3 months | 0.2059 |
| 69806/GWBS1 | Gaskell West Storage 1, LLC | CA | Batteries | 21.6 | TS | 2-3 months | 0.2059 |
| 68018/MRCDB | Merced BESS | CA | Batteries | 3.0 | TS | 2-3 months | 0.2059 |
| 68518/MRC2B | Merced 2 BESS | CA | Batteries | 2.0 | TS | 2-3 months | 0.2059 |
| 69778/HK1SO | Hashknife Energy Center LLC | AZ | Solar Photovoltaic | 275.0 | V | 4-12 months | 0.1929 |
| 68466/CFPV3 | Centennial Flats | AZ | Solar Photovoltaic | 166.7 | U | 4-12 months | 0.1929 |
| 67283/6569 | Six Flags Magic Mountain | CA | Solar Photovoltaic | 10.0 | V | 4-12 months | 0.1929 |
| 69828/MEXIC | Mexico PV, LLC | NY | Solar Photovoltaic | 4.5 | V | 4-12 months | 0.1929 |
| 69293/WTS1 | Waterton Solar I | CO | Solar Photovoltaic | 4.0 | U | 4-12 months | 0.1929 |
| 69620/WTS2 | Waterton Solar II | CO | Solar Photovoltaic | 4.0 | U | 4-12 months | 0.1929 |
| 69854/GLWAY | TJA-NY-1806 Perth Rd Galway, LLC | NY | Solar Photovoltaic | 3.3 | TS | 4-12 months | 0.1929 |
| 68389/GLENG | AES Glengarry Farms Solar CSG | NY | Solar Photovoltaic | 5.0 | V | more than 12 months | 0.1818 |
| 67749/TWISS | Pistachio Road 1726-WD | CA | Solar Photovoltaic | 4.8 | V | more than 12 months | 0.1818 |
| 68873/BIGS | Big Sampson Wind | TX | Onshore Wind Turbine | 265.0 | TS | 2-3 months | 0.1579 |
| 62749/1 | Heidelberg Hydroelectric Project | KY | Conventional Hydroelectric | 0.6 | TS | 2-3 months | 0.1471 |
| 62749/2 | Heidelberg Hydroelectric Project | KY | Conventional Hydroelectric | 0.6 | TS | 2-3 months | 0.1471 |
| 62749/5 | Heidelberg Hydroelectric Project | KY | Conventional Hydroelectric | 0.6 | TS | 2-3 months | 0.1471 |
| 62749/6 | Heidelberg Hydroelectric Project | KY | Conventional Hydroelectric | 0.6 | TS | 2-3 months | 0.1471 |
| 62749/3 | Heidelberg Hydroelectric Project | KY | Conventional Hydroelectric | 0.2 | TS | 2-3 months | 0.1471 |
| 62749/4 | Heidelberg Hydroelectric Project | KY | Conventional Hydroelectric | 0.2 | TS | 2-3 months | 0.1471 |

## The list: 2026-10 (from EIA's 2026-09 workbook)

161 generators at 136 plants, 11460.2 MW. Expected on time by p: 56.8 generators, 4116.5 MW.

| group | cell | generators | MW | p | p from | rows behind p |
|---|---|---|---|---|---|---|
| batteries | first | 7 | 173.6 | 0.2864 | group and cell | 583 |
| batteries | 1 month | 13 | 423.9 | 0.3569 | group and cell | 678 |
| batteries | 2-3 months | 7 | 230.8 | 0.2101 | group and cell | 238 |
| batteries | 4-12 months | 4 | 361.4 | 0.3380 | group and cell | 142 |
| gas | first | 4 | 480.0 | 0.5025 | group and cell | 199 |
| gas | 1 month | 6 | 1335.6 | 0.4483 | group and cell | 87 |
| other | first | 4 | 8.0 | 0.2917 | group and cell | 72 |
| other | 1 month | 6 | 2.8 | 0.5690 | group and cell | 58 |
| other | more than 12 months | 1 | 4.3 | 0.3182 | group | 198 |
| solar | first | 37 | 2204.9 | 0.3602 | group and cell | 1613 |
| solar | 1 month | 45 | 3823.2 | 0.3884 | group and cell | 1488 |
| solar | 2-3 months | 17 | 1299.1 | 0.2684 | group and cell | 570 |
| solar | 4-12 months | 8 | 849.6 | 0.1850 | group and cell | 254 |
| wind | first | 1 | 80.0 | 0.5043 | group and cell | 115 |
| wind | 4-12 months | 1 | 183.0 | 0.4047 | group | 257 |

| key | plant | state | technology | MW | status | cell | p |
|---|---|---|---|---|---|---|---|
| 62749/1 | Heidelberg Hydroelectric Project | KY | Conventional Hydroelectric | 0.6 | TS | 1 month | 0.5690 |
| 62749/2 | Heidelberg Hydroelectric Project | KY | Conventional Hydroelectric | 0.6 | TS | 1 month | 0.5690 |
| 62749/5 | Heidelberg Hydroelectric Project | KY | Conventional Hydroelectric | 0.6 | TS | 1 month | 0.5690 |
| 62749/6 | Heidelberg Hydroelectric Project | KY | Conventional Hydroelectric | 0.6 | TS | 1 month | 0.5690 |
| 62749/3 | Heidelberg Hydroelectric Project | KY | Conventional Hydroelectric | 0.2 | TS | 1 month | 0.5690 |
| 62749/4 | Heidelberg Hydroelectric Project | KY | Conventional Hydroelectric | 0.2 | TS | 1 month | 0.5690 |
| 70235/68372 | Mulqueeney Wind Energy | CA | Onshore Wind Turbine | 80.0 | V | first | 0.5043 |
| 2951/11 | Horseshoe Lake | OK | Natural Gas Fired Combustion Turbine | 224.0 | TS | first | 0.5025 |
| 2951/12 | Horseshoe Lake | OK | Natural Gas Fired Combustion Turbine | 224.0 | TS | first | 0.5025 |
| 3338/3 | Aberdeen CT | SD | Natural Gas Fired Combustion Turbine | 16.0 | V | first | 0.5025 |
| 3338/4 | Aberdeen CT | SD | Natural Gas Fired Combustion Turbine | 16.0 | V | first | 0.5025 |
| 66621/1A | Orange County Advanced Power Station | TX | Natural Gas Fired Combined Cycle | 453.0 | TS | 1 month | 0.4483 |
| 66621/1B | Orange County Advanced Power Station | TX | Natural Gas Fired Combined Cycle | 453.0 | TS | 1 month | 0.4483 |
| 66621/1C | Orange County Advanced Power Station | TX | Natural Gas Fired Combined Cycle | 400.0 | TS | 1 month | 0.4483 |
| 1239/13 | Riverton | KS | Natural Gas Fired Combustion Turbine | 13.5 | TS | 1 month | 0.4483 |
| 1239/14 | Riverton | KS | Natural Gas Fired Combustion Turbine | 13.5 | TS | 1 month | 0.4483 |
| 54808/GR1 | New York University Central Plant | NY | Natural Gas Internal Combustion Engine | 2.6 | V | 1 month | 0.4483 |
| 68319/NIM | Nimbus Wind Farm | AR | Onshore Wind Turbine | 183.0 | TS | 4-12 months | 0.4047 |
| 66914/DAN | Danish Fields Solar, LLC | TX | Solar Photovoltaic | 600.0 | TS | 1 month | 0.3884 |
| 65028/ROSES | Roseland Solar Project, LLC | TX | Solar Photovoltaic | 500.0 | TS | 1 month | 0.3884 |
| 66912/HS1 | Hill Solar 1 | TX | Solar Photovoltaic | 405.0 | TS | 1 month | 0.3884 |
| 69877/CHPV1 | Charger Solar | TX | Solar Photovoltaic | 394.4 | TS | 1 month | 0.3884 |
| 66915/CTW | Cottonwood Bayou Solar | TX | Solar Photovoltaic | 350.0 | TS | 1 month | 0.3884 |
| 68758/IPEA1 | Easley Solar | CA | Solar Photovoltaic | 290.0 | TS | 1 month | 0.3884 |
| 64672/BLUJS | Blue Jay Solar I, LLC | TX | Solar Photovoltaic | 210.0 | TS | 1 month | 0.3884 |
| 66390/GDYPV | MRG Goody Solar Project Hybrid | TX | Solar Photovoltaic | 170.8 | V | 1 month | 0.3884 |
| 68410/BRAZ | Brazoria Solar I | TX | Solar Photovoltaic | 125.0 | TS | 1 month | 0.3884 |
| 68410/BRAZ2 | Brazoria Solar I | TX | Solar Photovoltaic | 125.0 | TS | 1 month | 0.3884 |
| 66778/HS1 | Hart Solar Project | MI | Solar Photovoltaic | 120.0 | U | 1 month | 0.3884 |
| 68851/HSPV1 | Hermes Solar PV | TX | Solar Photovoltaic | 100.4 | V | 1 month | 0.3884 |
| 69197/HALIF | Halifax County Solar | NC | Solar Photovoltaic | 80.0 | U | 1 month | 0.3884 |
| 67666/SUNDN | Sundance (CO) | CO | Solar Photovoltaic | 74.9 | U | 1 month | 0.3884 |
| 68000/BLUMN | Blue Moon | KY | Solar Photovoltaic | 70.0 | V | 1 month | 0.3884 |
| 68929/RUBY | Ruby Solar, LLC | IL | Solar Photovoltaic | 50.0 | V | 1 month | 0.3884 |
| 60434/PV1 | Baxter Creek Solar | NC | Solar Photovoltaic | 30.0 | V | 1 month | 0.3884 |
| 66066/WAIPV | AES Waiawa Phase 2 Solar | HI | Solar Photovoltaic | 30.0 | V | 1 month | 0.3884 |
| 68240/SS3PV | Solar Star 3 | CA | Solar Photovoltaic | 24.0 | V | 1 month | 0.3884 |
| 69516/HAMM | Hamms Landfill | NJ | Solar Photovoltaic | 6.0 | TS | 1 month | 0.3884 |
| 68392/IL2PV | IL2 - W109 | IL | Solar Photovoltaic | 4.9 | TS | 1 month | 0.3884 |
| 70010/167 | Pescara 1 | NY | Solar Photovoltaic | 4.9 | V | 1 month | 0.3884 |
| 70011/168 | Pescara 2 | NY | Solar Photovoltaic | 4.9 | V | 1 month | 0.3884 |
| 70242/215 | Riverhead - CVE | NY | Solar Photovoltaic | 4.9 | V | 1 month | 0.3884 |
| 67749/TWISS | Pistachio Road 1726-WD | CA | Solar Photovoltaic | 4.8 | V | 1 month | 0.3884 |
| 69828/MEXIC | Mexico PV, LLC | NY | Solar Photovoltaic | 4.5 | V | 1 month | 0.3884 |
| 70201/PS50 | Pivot Solar 50 LLC | CO | Solar Photovoltaic | 4.0 | V | 1 month | 0.3884 |
| 70103/PS43 | Pivot Solar 43 LLC | CO | Solar Photovoltaic | 3.5 | V | 1 month | 0.3884 |
| 68070/ALBER | Alberta Solar | VA | Solar Photovoltaic | 3.0 | U | 1 month | 0.3884 |
| 69220/11253 | West Genesee | NY | Solar Photovoltaic | 2.9 | V | 1 month | 0.3884 |
| 69371/HALIF | Middle Road Solar Partners | PA | Solar Photovoltaic | 2.5 | V | 1 month | 0.3884 |
| 69592/PSKPV | NL NY- Pulaski | NY | Solar Photovoltaic | 2.5 | TS | 1 month | 0.3884 |
| 70182/PV1 | Steger | IL | Solar Photovoltaic | 2.0 | V | 1 month | 0.3884 |
| 70206/PS57 | Pivot Solar 57 LLC | CO | Solar Photovoltaic | 2.0 | V | 1 month | 0.3884 |
| 70393/S1 | Stephenson County IL S1 | IL | Solar Photovoltaic | 2.0 | V | 1 month | 0.3884 |
| 70448/22258 | Keithsburg North Solar LLC PV | IL | Solar Photovoltaic | 2.0 | U | 1 month | 0.3884 |
| 69554/BELMO | BPL NJ - Belmont | NJ | Solar Photovoltaic | 1.8 | TS | 1 month | 0.3884 |
| 68118/CH404 | Addison 11-SLCHI404 | IL | Solar Photovoltaic | 1.6 | TS | 1 month | 0.3884 |
| 69791/NJUDC | BPL NJ - Union Distribution Center | NJ | Solar Photovoltaic | 1.5 | TS | 1 month | 0.3884 |
| 70445/PV1 | W 167th St | IL | Solar Photovoltaic | 1.5 | TS | 1 month | 0.3884 |
| 69891/LA100 | Torrance Dis Ctr 2 - SLLAX100 | CA | Solar Photovoltaic | 1.4 | TS | 1 month | 0.3884 |
| 70099/IL007 | Pivot Energy IL 7 LLC | IL | Solar Photovoltaic | 1.4 | V | 1 month | 0.3884 |
| 69790/EZMLC | Elizabeth Metropolitan Logistics Center | NJ | Solar Photovoltaic | 1.2 | TS | 1 month | 0.3884 |
| 68783/NY009 | NY CDG 009 | NY | Solar Photovoltaic | 1.0 | TS | 1 month | 0.3884 |
| 69616/USLYN | USS Lyndon Solar LLC | IL | Solar Photovoltaic | 1.0 | V | 1 month | 0.3884 |
| 69040/ARY1 | Arroyo Solar | CO | Solar Photovoltaic | 335.0 | U | first | 0.3602 |
| 66545/MMTHS | Mammoth South Solar Project | IN | Solar Photovoltaic | 300.0 | V | first | 0.3602 |
| 69055/ALTS4 | ATLAS SOLAR IV | AZ | Solar Photovoltaic | 300.0 | TS | first | 0.3602 |
| 69968/RUS | Rumble Solar | OK | Solar Photovoltaic | 250.0 | U | first | 0.3602 |
| 62892/SONRI | EDPR CA Solar Park VI LLC (CA) Hybrid | CA | Solar Photovoltaic | 201.0 | TS | first | 0.3602 |
| 70344/RSPV | Rush Springs Solar | OK | Solar Photovoltaic | 200.0 | V | first | 0.3602 |
| 69540/RCS01 | Rock Creek Solar | IA | Solar Photovoltaic | 150.0 | TS | first | 0.3602 |
| 69156/GEN01 | Duff Solar Park | IN | Solar Photovoltaic | 100.0 | TS | first | 0.3602 |
| 69629/BIGM1 | Big Muddy Solar | IL | Solar Photovoltaic | 95.0 | V | first | 0.3602 |
| 69956/S8 | Sanborn Hybrid 3 | CA | Solar Photovoltaic | 55.0 | V | first | 0.3602 |
| 68850/GRTSP | Gratiot Solar Park | MI | Solar Photovoltaic | 50.0 | TS | first | 0.3602 |
| 59969/GEN01 | Windhub Solar B, LLC | CA | Solar Photovoltaic | 26.4 | V | first | 0.3602 |
| 68241/SS4PV | Solar Star 4 | CA | Solar Photovoltaic | 24.0 | V | first | 0.3602 |
| 70495/WEL02 | Welcome Solar II | PA | Solar Photovoltaic | 21.0 | TS | first | 0.3602 |
| 70496/WEL03 | Welcome Solar III | PA | Solar Photovoltaic | 21.0 | TS | first | 0.3602 |
| 70305/23 | Tanglewood Solar, LLC | NC | Solar Photovoltaic | 8.4 | U | first | 0.3602 |
| 68975/17340 | Washington Street Solar 1 LLC | IL | Solar Photovoltaic | 5.0 | U | first | 0.3602 |
| 69931/BJORN | Bjorn | WI | Solar Photovoltaic | 5.0 | V | first | 0.3602 |
| 70176/KIESE | Kieser | IL | Solar Photovoltaic | 5.0 | V | first | 0.3602 |
| 70563/HIBIS | Hibiscus Solar, LLC | IL | Solar Photovoltaic | 5.0 | U | first | 0.3602 |
| 68230/DESAR | SR Des Arc | AR | Solar Photovoltaic | 4.8 | V | first | 0.3602 |
| 69932/CSTLO | Castle Rock Lake Solar | WI | Solar Photovoltaic | 4.5 | V | first | 0.3602 |
| 70488/BOBW | IL - Renewable Properties - Bobcat - Wes | IL | Solar Photovoltaic | 4.5 | V | first | 0.3602 |
| 68195/DEAVE | Delaware Ave Solar | DE | Solar Photovoltaic | 4.0 | V | first | 0.3602 |
| 70380/GEN4 | Kraemer Garden | MN | Solar Photovoltaic | 4.0 | U | first | 0.3602 |
| 69472/18198 | NYSolar06 | NY | Solar Photovoltaic | 3.5 | V | first | 0.3602 |
| 70339/IL55B | Pivot Energy IL 55 LLC | IL | Solar Photovoltaic | 3.1 | V | first | 0.3602 |
| 69937/MNDVI | Mondovi | WI | Solar Photovoltaic | 3.0 | V | first | 0.3602 |
| 70486/WHWIL | IL - Renewable Properties - Bobcat - Whi | IL | Solar Photovoltaic | 3.0 | V | first | 0.3602 |
| 70031/ZEBRA | Zebrawood Solar, LLC | IL | Solar Photovoltaic | 2.5 | U | first | 0.3602 |
| 69939/SPOON | Spooner | WI | Solar Photovoltaic | 2.3 | V | first | 0.3602 |
| 70370/R4701 | Ranch 4701 | CA | Solar Photovoltaic | 2.3 | V | first | 0.3602 |
| 69888/USFLE | USS Fletcher Solar | NM | Solar Photovoltaic | 1.7 | U | first | 0.3602 |
| 68120/CH513 | Bensenville 13-SLCHI513 | IL | Solar Photovoltaic | 1.4 | U | first | 0.3602 |
| 70456/PV1 | W Belmont Ave | IL | Solar Photovoltaic | 1.4 | V | first | 0.3602 |
| 70207/PS60 | Pivot Solar 60 LLC | CO | Solar Photovoltaic | 1.1 | V | first | 0.3602 |
| 69305/FITZH | Enterprise MN - Fitzthum | MN | Solar Photovoltaic | 1.0 | V | first | 0.3602 |
| 68866/SAN | Santa Teresa Solar | NM | Batteries | 150.0 | TS | 1 month | 0.3569 |
| 708/5 | Hammond | GA | Batteries | 57.5 | V | 1 month | 0.3569 |
| 66390/GDYES | MRG Goody Solar Project Hybrid | TX | Batteries | 50.4 | V | 1 month | 0.3569 |
| 67666/SUNBA | Sundance (CO) | CO | Batteries | 50.0 | U | 1 month | 0.3569 |
| 66066/WAIBA | AES Waiawa Phase 2 Solar | HI | Batteries | 30.0 | V | 1 month | 0.3569 |
| 67669/ABESS | Arlington Battery Energy Storage System | WA | Batteries | 25.0 | V | 1 month | 0.3569 |
| 70232/EVERG | Evergreen Energy Center, LLC | VA | Batteries | 20.0 | V | 1 month | 0.3569 |
| 66785/ELVAK | Elevate Arthur Kill | NY | Batteries | 15.1 | TS | 1 month | 0.3569 |
| 69318/APPLE | Apple BESS | TX | Batteries | 9.9 | TS | 1 month | 0.3569 |
| 69551/90915 | Holyoke MA BESS 1 | MA | Batteries | 5.0 | U | 1 month | 0.3569 |
| 69195/LONTB | Longtown Energy Storage | SC | Batteries | 4.5 | V | 1 month | 0.3569 |
| 70242/216 | Riverhead - CVE | NY | Batteries | 4.0 | V | 1 month | 0.3569 |
| 69592/PSKBS | NL NY- Pulaski | NY | Batteries | 2.5 | TS | 1 month | 0.3569 |
| 69681/DRAKE | Mallard Energy Storage | TX | Batteries | 250.0 | U | 4-12 months | 0.3380 |
| 68852/HSBE1 | Hermes Storage BESS | TX | Batteries | 100.4 | V | 4-12 months | 0.3380 |
| 69226/KNBA1 | Knapp BESS | TX | Batteries | 10.0 | V | 4-12 months | 0.3380 |
| 63506/BCRV3 | Solar Carver 3 Hybrid | MA | Batteries | 1.0 | V | 4-12 months | 0.3380 |
| 56615/G200 | Rancho Penasquitos | CA | Conventional Hydroelectric | 4.3 | U | more than 12 months | 0.3182 |
| 1291/17 | Iola | KS | Petroleum Liquids | 2.0 | U | first | 0.2917 |
| 1291/18 | Iola | KS | Petroleum Liquids | 2.0 | U | first | 0.2917 |
| 1291/19 | Iola | KS | Petroleum Liquids | 2.0 | U | first | 0.2917 |
| 1291/20 | Iola | KS | Petroleum Liquids | 2.0 | U | first | 0.2917 |
| 68149/RAVEB | Raven Storage | TX | Batteries | 100.0 | V | first | 0.2864 |
| 62892/SONR2 | EDPR CA Solar Park VI LLC (CA) Hybrid | CA | Batteries | 40.0 | TS | first | 0.2864 |
| 69552/90916 | Danville VA BESS 2 | VA | Batteries | 11.0 | U | first | 0.2864 |
| 69338/LEAKY | Regis Leakey | TX | Batteries | 9.9 | TS | first | 0.2864 |
| 70386/BESS1 | Chicopee BESS | MA | Batteries | 5.0 | U | first | 0.2864 |
| 70387/BESS1 | Framingham BESS | MA | Batteries | 5.0 | U | first | 0.2864 |
| 69196/NEBOB | Nebo Energy Storage | NC | Batteries | 2.7 | U | first | 0.2864 |
| 66871/SOLAR | GulfStar Power, LLC | TX | Solar Photovoltaic | 451.6 | TS | 2-3 months | 0.2684 |
| 68481/HS2 | Hill Solar II | TX | Solar Photovoltaic | 200.0 | TS | 2-3 months | 0.2684 |
| 66905/SOLAR | Ables Springs Solar & Storage | TX | Solar Photovoltaic | 151.0 | TS | 2-3 months | 0.2684 |
| 68968/ENX37 | Border Basin Solar | OH | Solar Photovoltaic | 120.0 | V | 2-3 months | 0.2684 |
| 65338/UNIS1 | Union Ridge Solar | OH | Solar Photovoltaic | 108.0 | TS | 2-3 months | 0.2684 |
| 68002/FOLEY | Foley Solar, LLC | AL | Solar Photovoltaic | 80.0 | TS | 2-3 months | 0.2684 |
| 67723/SOLAR | Kingstree West 115 | SC | Solar Photovoltaic | 74.9 | TS | 2-3 months | 0.2684 |
| 68938/OHJE1 | Juliet Energy Project, LLC | OH | Solar Photovoltaic | 50.0 | TS | 2-3 months | 0.2684 |
| 69628/GBPV1 | GBG SOLAR | TX | Solar Photovoltaic | 22.2 | TS | 2-3 months | 0.2684 |
| 69535/NS1 | Nutes Solar | NH | Solar Photovoltaic | 20.0 | U | 2-3 months | 0.2684 |
| 69844/HORSE | Horseshoe Solar Project, LLC | IL | Solar Photovoltaic | 5.0 | V | 2-3 months | 0.2684 |
| 68277/1 | Brookings Solar | SD | Solar Photovoltaic | 4.9 | TS | 2-3 months | 0.2684 |
| 70228/LOCKW | AC IL - Lockport West | IL | Solar Photovoltaic | 3.4 | TS | 2-3 months | 0.2684 |
| 70227/LOCKE | AC IL - Lockport East | IL | Solar Photovoltaic | 3.1 | TS | 2-3 months | 0.2684 |
| 63541/SCRV1 | Solar Carver 1 Hybrid | MA | Solar Photovoltaic | 2.0 | V | 2-3 months | 0.2684 |
| 68139/CH102 | McCook 2-SLCHI102 | IL | Solar Photovoltaic | 2.0 | TS | 2-3 months | 0.2684 |
| 69886/USSWA | USS Swank Solar | IL | Solar Photovoltaic | 1.0 | V | 2-3 months | 0.2684 |
| 68914/12343 | Padua 3 | TX | Batteries | 200.0 | TS | 2-3 months | 0.2101 |
| 70296/MTBAT | Milltown Onsite BESS | NJ | Batteries | 13.2 | V | 2-3 months | 0.2101 |
| 69593/1 | MCCo BESS Generating Facility | OH | Batteries | 3.9 | V | 2-3 months | 0.2101 |
| 69593/2 | MCCo BESS Generating Facility | OH | Batteries | 3.9 | V | 2-3 months | 0.2101 |
| 69593/3 | MCCo BESS Generating Facility | OH | Batteries | 3.9 | V | 2-3 months | 0.2101 |
| 69593/4 | MCCo BESS Generating Facility | OH | Batteries | 3.9 | V | 2-3 months | 0.2101 |
| 63541/BCRV1 | Solar Carver 1 Hybrid | MA | Batteries | 2.0 | V | 2-3 months | 0.2101 |
| 66168/GEN01 | Cattlemen Solar Park | TX | Solar Photovoltaic | 240.0 | TS | 4-12 months | 0.1850 |
| 66559/TXJC1 | Jones City 1 Solar | TX | Solar Photovoltaic | 215.0 | TS | 4-12 months | 0.1850 |
| 67976/GEN01 | Cattlemen Solar II | TX | Solar Photovoltaic | 200.0 | TS | 4-12 months | 0.1850 |
| 66893/TXJC2 | Jones City 2 Solar | TX | Solar Photovoltaic | 185.0 | TS | 4-12 months | 0.1850 |
| 63677/STURB | Sturbridge Road Solar | MA | Solar Photovoltaic | 5.0 | TS | 4-12 months | 0.1850 |
| 67857/MCDOW | McDowell Creek Solar LLC | NC | Solar Photovoltaic | 2.0 | V | 4-12 months | 0.1850 |
| 68130/CH211 | Des Plaines 11-SLCHI211 | IL | Solar Photovoltaic | 1.6 | TS | 4-12 months | 0.1850 |
| 63506/SCRV3 | Solar Carver 3 Hybrid | MA | Solar Photovoltaic | 1.0 | V | 4-12 months | 0.1850 |
