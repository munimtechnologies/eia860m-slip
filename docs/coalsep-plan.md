# Coal in EIA's September 2026 workbook: pre-registration

Status: pre-registered, not yet scored. Written on 28 October 2026, before any of our code read the coal rows of EIA's September 2026 EIA-860M workbook outside the eight plants under DOE orders. MV2 of Munim, Inc.; this plan and the code were made with AI agents working in my name.

## Why

[`coal-rows.md`](coal-rows.md) found, on PUDL's EIA-860M changelog (reports to August 2026), that no coal generator retired from January to August 2026, the first such year in the record, which starts in 2016. It also followed the 16 generators (6,354.4 MW) that EIA's December 2025 inventory dated to retire in 2026 ([`data/coal_plan_2026_followup.csv`](../data/coal_plan_2026_followup.csv)). EIA published its September 2026 workbook on 23 October 2026. PUDL's nightly changelog still ends with August, so this check reads EIA's own workbooks, as [`p5score-2026-09.md`](p5score-2026-09.md) did.

## What was already known before this plan

- The September workbook's rows for the eight plants under DOE 202(c) orders were already read by job p5score-v1: Campbell is dated 2026-11, and Schahfer, Culley and Craig 2026-12 ([`p5score-2026-09.md`](p5score-2026-09.md)). So most of the MW in S3 below is already known. S3 is a check that nothing large was added or removed, not a test of the order plants.
- The August record (PUDL): Sherburne County 1 (680.0 MW) and Comanche 2 (335.0 MW) dated 2026-12. Xcel has asked the Colorado PUC to let Comanche 2 run to March 2028; we found no decision.
- No earlier output of ours lists the September workbook's Retired-sheet coal rows, the dates of the other coal units, or the August-to-September changes.

## Rules

- A row is coal when its energy source code is BIT, SUB, LIG, ANT, RC, WC or SGC, or, with no code, its technology names coal. Capacity is net summer, nameplate where summer is blank or zero.
- Only the Operating and Retired sheets are read. On the Operating sheet the month is the planned retirement month; on the Retired sheet it is the retirement month.
- Plants under DOE orders are the eight plants with plant orders in [`data/doe_202c_orders.csv`](../data/doe_202c_orders.csv), matched by EIA plant ID: Campbell 1710, Eddystone 3161, Wagner 1554, Centralia 3845, Schahfer 6085, Culley 1012, Craig 6021 and Stanton 564.

## Gate G1 (reproduction)

EIA's August 2026 workbook must reproduce what coal-rows took from PUDL: (a) no coal row on its Retired sheet with retirement year 2026, and (b) at least 15 of the 16 plan generators on its Operating sheet with the planned month PUDL gave (no date where PUDL had none). If G1 fails, S1 to S3 are not scored and the cause is reported.

## Predictions on the September 2026 workbook

| # | prediction | our chance |
|---|---|---|
| S1 | No coal row on the Retired sheet has retirement year 2026. | about 85% |
| S2 | None of the 16 plan generators is on the Retired sheet, and Sherburne County 1 (6090/1) and Comanche 2 (470/2) are both still dated 2026-12. | about 75% |
| S3 | Operating coal dated 2026-10 to 2026-12 totals 3,000 to 4,500 MW, and at least 60% of it is at plants under DOE orders. | about 85% |

If S1 holds, January to September 2026 has no coal retirement in EIA-860M. If it fails, the rows are named. Late reports can still add rows later (Schiller's 2025 retirement appeared four months after it happened), so S1 says nothing about later workbooks.

## Forecast F1 (not part of the job; scored on 1 January 2027)

F1: DOE issues a 202(c) order that covers Sherburne County 1 (Xcel Energy, Minnesota, in MISO), dated on or before 31 December 2026. Our probability: 60%. It is scored against DOE's page of 2026 orders (energy.gov/ceser/2026-doe-202c-orders) as read on or after 1 January 2027.

Why 60%, from what was on record on 28 October 2026:
- For it: since May 2025 DOE has issued orders to six coal plants at or near their planned retirement (Campbell, Centralia, Schahfer, Culley, Craig and Stanton), three of them in MISO, and each order at these six plants has been followed by a new one issued no later than the day it expired. Sherburne County 1 is the only unit of the December 2025 plan with no deferral or order on record.
- Against it: the two Intermountain coal units in Utah (1,640 MW nameplate) stopped in October and November 2025 with no 202(c) order in our orders table; Utah law keeps them operable. DOE has issued no first order to a new plant since Stanton on 4 June 2026. The D.C. Circuit vacated Campbell's first order on 11 September 2026, and DOE's rehearing petition is pending (as reported; see [`doe-202c-court.md`](doe-202c-court.md)).
- We found no report, as of 28 October 2026, that DOE, MISO or Xcel has proposed an order for the unit.

## Described, not scored

- Every operating coal plant dated to retire from 2026-10 to 2027-12, with its units, MW, months and whether it is under a DOE order.
- Operating coal units dated before 2026-10, that is past their planned month.
- Every coal unit whose record changed from the August to the September workbook.
- Coal on the September Retired sheet with retirement year 2025 or later.

## Job

`coalsep-v1` runs `coalsep.py` 0.1.0 with its unit tests on hand-built sheets. It downloads EIA's September 2026 workbook (recorded earlier: 14,013,970 bytes, md5 4c741eb77a5ccad5aca32ffe43f398af) and its August 2026 workbook from EIA's archive (13,955,142 bytes, md5 9727ac867236faab7d5503175dacdf38), and reports whether each file still matches. The code and the result will be published together, and the scored result will say plainly which bars held and which failed.

Code: Apache-2.0. Text: CC BY 4.0. [`test_coalsep_plan_doc.py`](../test_coalsep_plan_doc.py) checks this page against the two CSVs it names.
