# Plan: the plants of the 41, late monthly retirements and monthly-only retired generators (annualids)

Status: pre-registered on 22 October 2026, before compete job `annualids-v1` ran. Not yet scored.

MV2 of Munim, Inc. (made with AI agents working in his name). Code: Apache-2.0. Text and data: CC BY 4.0.

## Why

Job `annual860-v1` (see the late-night update of 22 October 2026 in [`heldtrace.md`](heldtrace.md)) compared EIA's annual EIA-860 files for 2020 to 2025 with EIA-860M. It left three things open: which generator IDs the annual files give at the plants of the 41 generators that left the monthly Retired sheet, which years the 168 annual-retired generators that EIA-860M's December 2025 file still listed as operating retired in, and where the 2,703 generators on the August 2026 monthly Retired sheet (retired 2002 to 2025) that the annual 2025 file does not list come from.

EIA's EIA-860 page says the annual Retired and Canceled tab "only includes those retired generators which were reported in the most current data cycle". One reading of that: a plant that no longer reports drops out of later annual files with its retired units.

## What runs

`tools/annual-flows-candidate/annualids.py` 0.1.0 with `annual860.py` 0.1.0's reader. It reads the annual files for 2016 to 2025 (2016 to 2019 are new; 2020 to 2025 are the files annual860-v1 kept) and the EIA-860M workbooks for the month before each focus plant's generators left (plants 1439, 55526, 1571, 1572, 955 and 7922), December 2025 and August 2026, from the same archive (Zenodo record 22995197).

## Predictions

Each is scored by its bar and nothing else. Neither bar will be moved.

- **P1.** Of the generators on the August 2026 monthly Retired sheet, retired 2002 to 2025, that the annual 2025 file lists on no sheet, more than half are at plants the annual 2025 file lists on no sheet. This is what that reading of EIA's note predicts. It fails if half or fewer are, which would mean most monthly-only retirements are at plants that still report.
- **P2.** Of the generators the annual 2025 file lists as retired (status RE, retired 2002 to 2025) that the December 2025 monthly file lists on its Operating sheet, more than half retired in 2025 by the annual file. This is what a monthly file that reports recent retirements late predicts. It fails if half or fewer did, which would mean the annual file recorded mostly older retirements that the monthly file had not.

## Descriptive, no prediction

- For each of the 41 and each annual file from 2016 to 2025, where the file lists it.
- Every row the annual files and the monthly workbooks give at the six focus plants, so the A and B units at plant 1439 and 55526/GEN5 can be compared with the IDs the annual files use.
- For the generators in P1: retirement years, MW and technologies, split by whether the plant is listed, and the last earlier annual file (2016 to 2024) that lists each one.

## Limits set down now

Generator IDs are compared as text after the same normalisation as annual860 (plant IDs without leading zeros). A generator reported under a new ID counts as not listed. The annual files before 2016 are not read.
