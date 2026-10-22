# retiredgap 0.1.0: generators missing from November 2024's EIA-860M workbook

Descriptive check for docs/heldtrace.md; no prediction is tested. MV2 of Munim, Inc. (made with AI agents).

PUDL archive: zenodo-22995197-eia860m-2024.zip (127335369 bytes, md5 55592d39081c290b755b36f78e123be2).

## Files

| month | archive member | archive bytes | archive md5 | EIA URL | EIA bytes | EIA md5 | same file |
|---|---|---|---|---|---|---|---|
| 2024-10 | eia860m-2024-10.xlsx | 12360107 | 9defe23e9607dd944f6bbdb9ac495e9e | https://www.eia.gov/electricity/data/eia860m/archive/xls/october_generator2024.xlsx | 12360107 | 9defe23e9607dd944f6bbdb9ac495e9e | True |
| 2024-11 | eia860m-2024-11.xlsx | 12251506 | fc902dbcf91640cb465edbda03a9ed7d | https://www.eia.gov/electricity/data/eia860m/archive/xls/november_generator2024.xlsx | 12251506 | fc902dbcf91640cb465edbda03a9ed7d | True |
| 2024-12 | eia860m-2024-12.xlsx | 12520937 | e98fcfc7ef27811b19c7bf3eefa844a4 | https://www.eia.gov/electricity/data/eia860m/archive/xls/december_generator2024.xlsx | 12520937 | e98fcfc7ef27811b19c7bf3eefa844a4 | True |

Errors: none.

## Sheets (rows with a plant id; - not read by the route)

| month | source | sheets |
|---|---|---|
| 2024-10 | archive | Operating 26455; Planned 1866; Retired 6715; Canceled or Postponed 1481 -; Operating_PR 208 -; Planned_PR 7 -; Retired_PR 6 - |
| 2024-10 | eia | Operating 26455; Planned 1866; Retired 6715; Canceled or Postponed 1481 -; Operating_PR 208 -; Planned_PR 7 -; Retired_PR 6 - |
| 2024-11 | archive | Operating 26554; Planned 1985; Retired 6445; Canceled or Postponed 1397 -; Operating_PR 208 -; Planned_PR 7 -; Retired_PR 6 - |
| 2024-11 | eia | Operating 26554; Planned 1985; Retired 6445; Canceled or Postponed 1397 -; Operating_PR 208 -; Planned_PR 7 -; Retired_PR 6 - |
| 2024-12 | archive | Operating 26795; Planned 1905; Retired 6746; Canceled or Postponed 1495 -; Operating_PR 208 -; Planned_PR 7 -; Retired_PR 6 - |
| 2024-12 | eia | Operating 26795; Planned 1905; Retired 6746; Canceled or Postponed 1495 -; Operating_PR 208 -; Planned_PR 7 -; Retired_PR 6 - |

## Listed in 2024-10 and 2024-12 but not in 2024-11

| source | keys 2024-10 | keys 2024-11 | keys 2024-12 | left in 2024-11 | back in 2024-12 | nameplate MW of those back |
|---|---|---|---|---|---|---|
| archive | 35036 | 34984 | 35446 | 282 | 279 | 5543.6 |
| eia | 35036 | 34984 | 35446 | 282 | 279 | 5543.6 |

Of the archive's 279, listed in EIA's own 2024-11 file: 0.

### archive: sheet in 2024-10

| value | generators |
|---|---|
| Retired | 277 |
| Planned | 2 |

### archive: sheet in 2024-12

| value | generators |
|---|---|
| Retired | 277 |
| Operating | 2 |

### archive: retirement year

| value | generators |
|---|---|
| 2013 | 120 |
| 2014 | 75 |
| 2012 | 26 |
| 2011 | 20 |
| 2004 | 8 |
| 2010 | 7 |
| 2002 | 6 |
| 2006 | 6 |
| 2008 | 4 |
| - | 2 |
| 2009 | 2 |
| 2003 | 1 |
| 2005 | 1 |
| 2007 | 1 |

### archive: state (top 15)

| value | generators |
|---|---|
| ME | 30 |
| CA | 25 |
| TX | 24 |
| IL | 22 |
| CO | 18 |
| NY | 16 |
| CT | 14 |
| IA | 13 |
| MI | 13 |
| MO | 13 |
| PA | 11 |
| WI | 11 |
| NJ | 9 |
| AZ | 7 |
| NC | 7 |

### archive: technology (top 15)

| value | generators |
|---|---|
| Petroleum Liquids | 71 |
| Conventional Hydroelectric | 36 |
| Landfill Gas | 36 |
| Conventional Steam Coal | 34 |
| Natural Gas Internal Combustion Engine | 31 |
| Natural Gas Steam Turbine | 13 |
| Natural Gas Fired Combined Cycle | 12 |
| Wood/Wood Waste Biomass | 10 |
| Natural Gas Fired Combustion Turbine | 9 |
| Municipal Solid Waste | 5 |
| Other Gases | 5 |
| Onshore Wind Turbine | 4 |
| Other Natural Gas | 4 |
| Batteries | 3 |
| Nuclear | 2 |

First 20 of archive's: 10002/GEN1, 10045/0011, 10045/0012, 10045/0013, 10045/0014, 10111/GEN1, 10157/ENG1, 10157/ENG2, 10159/GEN1, 10165/GEN1, 10165/GEN2, 10171/GEN1, 10171/GEN2, 10171/GEN3, 10232/TB-1, 10232/TB-2, 10390/1, 10390/2, 10390/3, 10390/4

### eia: sheet in 2024-10

| value | generators |
|---|---|
| Retired | 277 |
| Planned | 2 |

### eia: sheet in 2024-12

| value | generators |
|---|---|
| Retired | 277 |
| Operating | 2 |

### eia: retirement year

| value | generators |
|---|---|
| 2013 | 120 |
| 2014 | 75 |
| 2012 | 26 |
| 2011 | 20 |
| 2004 | 8 |
| 2010 | 7 |
| 2002 | 6 |
| 2006 | 6 |
| 2008 | 4 |
| - | 2 |
| 2009 | 2 |
| 2003 | 1 |
| 2005 | 1 |
| 2007 | 1 |

### eia: state (top 15)

| value | generators |
|---|---|
| ME | 30 |
| CA | 25 |
| TX | 24 |
| IL | 22 |
| CO | 18 |
| NY | 16 |
| CT | 14 |
| IA | 13 |
| MI | 13 |
| MO | 13 |
| PA | 11 |
| WI | 11 |
| NJ | 9 |
| AZ | 7 |
| NC | 7 |

### eia: technology (top 15)

| value | generators |
|---|---|
| Petroleum Liquids | 71 |
| Conventional Hydroelectric | 36 |
| Landfill Gas | 36 |
| Conventional Steam Coal | 34 |
| Natural Gas Internal Combustion Engine | 31 |
| Natural Gas Steam Turbine | 13 |
| Natural Gas Fired Combined Cycle | 12 |
| Wood/Wood Waste Biomass | 10 |
| Natural Gas Fired Combustion Turbine | 9 |
| Municipal Solid Waste | 5 |
| Other Gases | 5 |
| Onshore Wind Turbine | 4 |
| Other Natural Gas | 4 |
| Batteries | 3 |
| Nuclear | 2 |

First 20 of eia's: 10002/GEN1, 10045/0011, 10045/0012, 10045/0013, 10045/0014, 10111/GEN1, 10157/ENG1, 10157/ENG2, 10159/GEN1, 10165/GEN1, 10165/GEN2, 10171/GEN1, 10171/GEN2, 10171/GEN3, 10232/TB-1, 10232/TB-2, 10390/1, 10390/2, 10390/3, 10390/4
