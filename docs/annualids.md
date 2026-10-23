# Scored: the plants of the 41, late monthly retirements and monthly-only retired generators (annualids)

Status: scored against its pre-registration ([`annualids-plan.md`](annualids-plan.md), set down on 22 October 2026 before job `annualids-v1` ran). 2 of 2 predictions held.

MV2 of Munim, Inc. (made with AI agents working in his name). Code: Apache-2.0. Text and data: CC BY 4.0.

## In short

- **EIA's annual and monthly retired lists differ by plant, not by generator.** EIA-860M's August 2026 Retired sheet lists 2,703 generators retired in 2002 to 2025 that the annual EIA-860 2025 file lists on no sheet (87,678.1 MW). Every one of the 2,703 is at a plant that the annual 2025 file lists on no sheet. None is at a plant the annual file still lists. Job `annual860-v1` had already found the other direction: all 4,565 generators the annual 2025 file lists as retired in 2002 to 2025 are on the monthly Retired sheet with the same retirement year. So a retirement history built from the annual 2025 file alone leaves out the generators of plants that have retired entirely, among them 287 conventional steam coal generators.
- **This is what EIA documents; the size of it is what is new here.** EIA's EIA-860 page (read 23 October 2026) says the annual Retired and Canceled tab holds canceled generators and "retired generators at existing plants", that it "only includes those retired generators which were reported in the most current data cycle", and that it "is not a comprehensive list". It points to EIA-860M's Retired tab for a comprehensive list of generators retired since 2002. EIA's March 2018 *Guide to EIA Electric Power Data* is quoted elsewhere as saying that a respondent whose last operating unit retires no longer files the annual form; this run did not open that PDF. So P1's result is the documented rule at work. This run measures how much it leaves out of the 2025 file (2,703 generators, 87,678.1 MW) and finds no exception to it.
- **Most late monthly retirements are recent.** Of the 168 generators the annual 2025 file lists as retired that EIA-860M's December 2025 file still listed on its Operating sheet, 92 retired in 2025 by the annual file and 45 in 2024. The other 31 retired from 2006 to 2023 by the annual file. By August 2026 the monthly file lists all 168 on its Retired sheet.

## Scores

Each prediction is scored by its pre-set bar and nothing else.

| | bar | result | |
|---|---|---|---|
| P1 | more than half of the 2,703 at plants the annual 2025 file lists on no sheet | 2,703 of 2,703 | held |
| P2 | more than half of the 168 retired in 2025 by the annual file | 92 of 168 | held |

P1 could have failed: it would have if most monthly-only retirements were at plants that still report. It held with no exception. P2 held narrowly: half of 168 is 84, and 92 retired in 2025.

## What ran

`tools/annual-flows-candidate/annualids.py` 0.1.0 (6 of 6 unit tests passed first) with `annual860.py` 0.1.0's reader, on 23 October 2026 (UTC). It read the 3_1_Generator workbook (sheets Operable, Proposed and Retired and Canceled) of EIA's annual EIA-860 files for 2016 to 2025 from eia.gov; for the 9 years before 2025 EIA's current-data path returned a web page, so they came from its archive path. It read the EIA-860M workbooks for 2020-01, 2021-11, 2022-12, 2023-12, 2025-02, 2025-12 and 2026-08 from PUDL's archive (Zenodo record 22995197), each zip's md5 matching the record page. Sizes and md5s of every file are in the raw output, [`annualids-v1-output.md`](annualids-v1-output.md); every row is in `data/annualids_v1.json` and the four `data/annualids_*.csv` files.

## P1: the 2,703 monthly-only retired generators

- Retirement years run from 2002 to 2024 (none in 2025); the most are 2015 (177) and 2013 (171).
- 1,308 of them are on no annual file from 2016 to 2024. The other 1,395 were last listed on an annual Retired and Canceled sheet as retired (RE); the last year that lists them is 2020 for the most (274).
- Technologies: Petroleum Liquids 630, Landfill Gas 323, Natural Gas Internal Combustion Engine 292, Natural Gas Fired Combustion Turbine 289, Conventional Steam Coal 287.

Limits: "a plant the annual file lists" means a plant with at least one row on one of the three sheets of the 3_1_Generator workbook; the annual plant workbook (2___Plant) was not read. The run describes EIA's two files; the reason given above is EIA's own, not something this run tested. The rule does not run the other way: at plants still listed, the annual files have also dropped retired generators (the 41 below; plants 955 and 1572), and the monthly file dropped those too.

## P2: the 168 late monthly retirements

- 2,412.5 MW in all. By the annual file: 92 retired in 2025, 45 in 2024, 31 from 2006 to 2023.
- Status on the December 2025 Operating sheet: OP 93, SB 37, OS 31, OA 7. That sheet gives no planned retirement year for 165 of them, 2030 for 2 and 2027 for 1.
- Technologies: Petroleum Liquids 51, Landfill Gas 23, Onshore Wind Turbine 19.
- One example: 10764/GEN1 (Wood/Wood Waste Biomass, 13.8 MW) is retired in 2015 by the annual 2025 file and on the December 2025 Operating sheet as OS (out of service).

## The 41 and their plants in the annual files from 2016 (descriptive, no prediction)

`annual860-v1` read the annual files from 2020; this run adds 2016 to 2019 and every row at six focus plants.

- **Plant 1439 (23 of the 41).** No annual file from 2016 to 2025 lists any of the 23 IDs with an A or B suffix. Every one of those files lists the same 10 generators at the plant: 3 on the Operable sheet (1439/14, 1439/15 and 1439/16; 12.6, 25.5 and 40.8 MW) and 7 retired in 2010 (1439/6 to 1439/12). EIA-860M's December 2023 file lists those 10 and the 23, all 23 retired in 2023 with no nameplate MW; its December 2025 file lists only the 10. Because that monthly file lists the 23 next to the 10, the 23 are not the annual files' 10 under other IDs; no annual file read here lists them at all.
- **55526/GEN5.** On the Operable sheet of the 2016 and 2017 files and retired in 2018 by the 2018 file; on no sheet from 2019, while the plant's other 5 generators stay on the Retired and Canceled sheet through 2025.
- **57693/ALSTO and 57692/ALSTO.** 57693/ALSTO is on the Operable sheet of the 2016 and 2017 files, retired in 2018 by the 2018 and 2019 files, and on no sheet from 2020. 57692/ALSTO is on no annual file from 2016 to 2025.
- **7922/6.** On the Operable sheet of the 2016 and 2017 files, then retired in 2011 by the 2018 to 2021 files. From 2022 the plant's only listed generator is 7922/7 (Operable, 2.3 MW), which the December 2025 and August 2026 monthly files also list as operating.
- **1571/ST1 and 1571/ST2** (364 MW each) are on the Operable sheet of every file from 2016 to 2020, then on no sheet. **1572/2, 1572/3 and 1572/ST1** (196 MW each) are on the Operable sheet from 2016 to 2019, retired in 2020 by the 2020 file, then on no sheet.
- **423/3A.** On the Operable sheet from 2016 to 2023, retired in 2018 by the 2024 file, on no sheet in 2025.

Two other things at the focus plants, outside the 41:

- **Plant 955.** 7 generators (955/16, 955/17, 955/GT1 and 955/HC1 to 955/HC4; 23 MW) are on the Operable sheet of every annual file from 2016 to 2023 and on no sheet of the 2024 and 2025 files. EIA-860M's February 2025 file lists them on its Operating sheet; its December 2025 and August 2026 files list them on no sheet. Neither product lists them as retired. Whether they were moved to another plant ID was not checked.
- **Plant 1571.** 1571/SGT1 (94 MW) is on the Operable sheet of the 2016 file only. 1571/GT1 (16 MW) is on the Operable sheet from 2016 to 2020, on no sheet in 2021 and 2022, and back from 2023.

## What this changes

Nothing earlier is withdrawn. With `retiredscope-v1` and `annual860-v1` it completes the picture of EIA's retired lists: for 2002 to 2025 the monthly Retired sheet is the more complete of the two, by August 2026 it gives every annual-retired generator the annual file's retirement year, and both products drop some retired generators, so neither is a complete history. MV2's rebuilt EIA-860M changelog ([`eia860m-changelog-from-workbooks.md`](eia860m-changelog-from-workbooks.md)) keeps generators after EIA drops them.

Not checked here: the annual files before 2016, the 2___Plant workbook, and whether a dropped generator reappears under another plant or generator ID.
