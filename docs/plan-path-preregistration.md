# Pre-registration: the 2026 solar figure, month by month, in EIA-860M and in the STEO

MV2 of Munim, Inc., 18 October 2026. Made with AI agents. CC BY 4.0. Written and published before the job (`plan-path-v1`) runs; code in `tools/plan-path/` (Apache-2.0) once the job has run its tests.

## Why

[`steo-vs-plan.md`](steo-vs-plan.md) found that the January Short-Term Energy Outlook (STEO) carried the developers' same-year solar plan until 2024, then discounted it: by 21% for 2025 and, for 2026, by 26% (32.1 GW against a 43.4 GW plan; prediction P5 there missed). The 2026 final (EIA-860) will not be out until late 2027. But both numbers are restated every month: EIA-860M's inventory (what came online so far plus what is still planned for the year) and each new STEO edition. This check follows both through 2026, to see whether the plan moves toward the STEO, the STEO toward the plan, or neither.

## What has been seen before this was written

- The January and February 2026 STEO capacity tables: 32.1 and 31.5 GW of 2026 solar (electric power sector), 9.7 and 11.7 GW of wind.
- EIA's 2026 plan figures from *Today in Energy* 67205 (December 2025 inventory): 43.4 GW solar, 11.8 GW wind.
- Not seen: any 2026 STEO edition after February; any month-by-month 2026 solar or wind total computed from EIA-860M (earlier eia860m-slip work on 2026 used coal rows only).

## Method (`plan_path.py` 0.1.0)

- **Plan side.** For each monthly EIA-860M report from November 2025 to the latest in PUDL's changelog (August 2026 at the time of writing), each generator's record as of that report. *Added* = solar photovoltaic generators listed as operating whose operating month is in 2026 and no later than the report month (if the operating date is blank, the first report listing it as operating). *Planned* = generators in a planned status (P, L, T, U, V, TS, OT) with a planned operating month in 2026, including months already past. *Implied 2026 total* = added + planned. Wind = onshore + offshore wind turbines, the same way. Computed on both nameplate and net summer capacity (summer falls back to nameplate when blank or zero).
- **STEO side.** Editions jan26 to oct26 from `eia.gov/outlooks/steo/archives/`. In each edition's page text, the first page holding a "Solar photovoltaic ....." row of 15 numbers (12 quarters, three year-end columns); the 2026 figure is the end-2026 column minus the end-2025 column. Wind is the first 15-number "Wind ....." row on that page (the electric power sector block). Every figure is re-read by hand in the page text.
- **Pairing.** Edition of month X is paired with the EIA-860M report for month X-2 (the latest inventory published before the edition was finished: the January edition, finished 8 January, with the November report).

## Checks (if one fails, the numbers are published as description and the check is fixed and re-run as -v2)

- **C1.** The December 2025 report's planned-for-2026 solar is within 5% of 43.4 GW on nameplate or on summer capacity. The measure that is closer is used for everything below.
- **C2.** At least 8 of the 10 editions give a solar row whose end-2025 value is between 130 and 150 GW, and the January 2026 edition reproduces 139.2 and 171.3 GW (solar) and 160.4 and 170.1 GW (wind), as read by hand.
- **C3.** Added-in-2026 never falls by more than 0.5 GW from one report to the next.

## Predictions (scored on the C1 measure)

- **P1.** The implied 2026 solar total falls by at least 4 GW from the December 2025 report to the latest report.
- **P2.** In every pair, the implied 2026 solar total is above the STEO's 2026 figure.
- **P3.** The gap (implied minus STEO) in the latest pair is less than half the gap in the February 2026 pair.
- **P4.** The latest edition's 2026 solar figure is within 4 GW of the January edition's 32.1 GW.
- **P5.** Solar added in 2026 by the latest report is at least 40% of that report's implied 2026 total.

What these say together: we expect the developers' 2026 plan to shrink toward the STEO as the year goes on (P1, P3) without crossing it (P2), the STEO to hold its figure (P4), and most 2026 solar to still be ahead at the end of August (P5 is about how back-loaded the year is, not about who is right).

## Limits stated in advance

- EIA-860M covers all utility-scale generators; the STEO row is the electric power sector only. The difference is well under 1 GW a year for solar.
- An implied total is not a forecast: it counts every 2026 plan at face value. Neither side is "right" until the 2026 EIA-860 final.
- PUDL's changelog is a reconstruction of the monthly files; generators that change ids between reports can be counted twice or dropped (earlier eia860m-slip work found this changes shares by under 0.001).
- If an edition is not in EIA's archive (October 2026 may not be), it is reported as missing and C2 counts it as a failure to parse.
