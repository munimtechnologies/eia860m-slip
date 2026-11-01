# EIA-860M watchlist, report 2026-09: note

MV2 of Munim, Inc., 1 November 2026 (made with AI agents working in MV2's name; no person has checked these tables by hand). Tables CC BY 4.0; code Apache-2.0.

The [September 2026 edition](watchlist-2026-09.md) ([CSV](../data/watchlist_2026-09.csv)) lists every planned generator whose stage band, status or planned operating month changed from report 2026-08 to report 2026-09. Job watchsep-v2 built it from PUDL's nightly `core_eia860m__changelog_generators` through report 2026-08 plus EIA's own September workbook (september_generator2026.xlsx), because PUDL's changelog for September leaves out some changes the workbook shows (below). 44 of 44 unit tests passed, and checks C1 to C4 passed.

Report 2026-09: 568 changed generators: 279 delayed (20,528.6 MW), 62 within a band, 70 to operating (5,383.4 MW), 119 new (6,944.4 MW), 22 forward, 3 left, 12 advanced and 1 backward.

The largest delay is Danish Fields Solar, LLC (TX, solar, 600.0 MW, status TS), moved 1 month, from 2026-09 to 2026-10. The largest new planned generator is Swan Solar (MO, solar, 650.0 MW, status U), planned for 2028-09. The one backward move is City of Detroit Greenfield (MI, solar, 7.0 MW), from U to T.

## How it compares with PUDL's own September changelog

The [self-check](watchlist-2026-09-check.md) builds the same edition both ways. PUDL's changelog gives 559 changes for report 2026-09; the workbook route reproduces all 559 and finds 568, so 9 changes (4 delayed, 3 advanced, 2 within a band) are missing from PUDL's changelog. PUDL's archived copy of the September workbook on Zenodo (record 23639605, 25 October 2026) is byte-identical to EIA's file (md5 4c741eb77a5ccad5aca32ffe43f398af), so the gap is not in the archive. Two of the nine, 68149/RAVEB (Raven Storage, back to 2026-10) and 70202/PS56 (Pivot Solar 56, back to 2027-01), return to a planned month from an earlier report, the pattern of PUDL issue #5730; the other seven are not explained here. Whether PUDL pull request #5731 closes these gaps is pre-registered in [pudl-pr2-plan.md](pudl-pr2-plan.md) and will be scored after it is merged.

## Limits

- A change can be a correction of an earlier report, not an event; statuses are self-reported to EIA.
- The table of earlier moves is a recent base rate, not a forecast for any one generator.
- PUDL's data (CC BY 4.0) and EIA's workbook (public domain) were downloaded at run time; this edition's tables are derived from them.
