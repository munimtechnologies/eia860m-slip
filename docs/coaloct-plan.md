# Coal in EIA's October 2026 workbook: pre-registration

Status: pre-registered, not yet scored. Written on 28-29 October 2026, before EIA has published its October 2026 EIA-860M workbook (EIA's page gives the next release as 24 November 2026). MV2 of Munim, Inc.; this plan and its test were made with AI agents working in my name.

## Why

[`coalsep.md`](coalsep.md) found no coal generator on the Retired sheet of EIA's September 2026 workbook with retirement year 2026, so EIA-860M records no U.S. coal retirement from January to September 2026. This plan fixes, before the October file exists, what would count as the first 2026 coal retirement in it, and what else we expect it to show.

October is a weak month for this test, and we say so now. No coal unit was dated 2026-10 in September's workbook, and the first order expiry among the coal plants DOE holds open is Campbell's, on 14 November 2026. November's workbook (due in late December) is the stronger test; it will get its own plan.

## What was already known before this plan

From job coalsep-v1 ([`coalsep-2026-09.md`](coalsep-2026-09.md), [`../data/coalsep_2026-09.json`](../data/coalsep_2026-09.json)), the September 2026 workbook:
- has 0 coal rows on its Retired sheet with retirement year 2026;
- dates 9 operating coal units in six plants to retire in 2026, 3,584.5 MW in all: Campbell 1-3 (1,330.5 MW) to 2026-11, and Schahfer 17-18 (722.0 MW), Sherburne County 1 (680.0 MW), Craig 1 (427.0 MW), Comanche 2 (335.0 MW) and Culley 2 (90.0 MW) to 2026-12;
- has no operating coal unit dated before 2026-10, and none dated 2026-10.

Campbell, Schahfer, Craig and Culley are held open by DOE 202(c) orders that expire on 14 November (Campbell) and 18 to 25 December 2026. As of 28 October 2026 DOE's page of 2026 orders lists no order newer than 202-26-50 (12 October). Xcel has asked the Colorado PUC (proceeding 26A-0235E, filed 15 June 2026) to move Comanche 2's retirement to 31 March 2028; we found no decision. We found no report of a deferral or an order for Sherburne County 1, and no report of any U.S. coal unit retiring in October 2026.

## Rules

The same as [`coalsep-plan.md`](coalsep-plan.md): a row is coal when its energy source code is BIT, SUB, LIG, ANT, RC, WC or SGC, or, with no code, its technology names coal; capacity is net summer, nameplate where summer is blank or zero; only the Operating and Retired sheets are read; on the Operating sheet the month is the planned retirement month, on the Retired sheet the retirement month. The plan generators are the 16 coal generators (6,354.4 MW) that EIA's December 2025 inventory dated to retire in 2026 ([`../data/coal_plan_2026_followup.csv`](../data/coal_plan_2026_followup.csv)).

## Gate G2 (reproduction)

EIA's September 2026 workbook, downloaded again from EIA's current or archive address, must give what coalsep-v1 recorded: (a) no coal row on its Retired sheet with retirement year 2026, and (b) the same 9 operating coal units dated 2026-10 to 2026-12, with the same months, 3,584.5 MW in all. The job also reports whether the file still has 14,013,970 bytes and md5 4c741eb77a5ccad5aca32ffe43f398af; a changed file that passes (a) and (b) still passes the gate, and we will say it changed. If G2 fails, O1 to O3 are not scored and the cause is reported.

## Predictions on the October 2026 workbook

| # | prediction | our chance |
|---|---|---|
| O1 | No coal row on the Retired sheet has retirement year 2026. | about 85% |
| O2 | No coal unit on the Operating sheet is dated before 2026-11. | about 85% |
| O3 | None of the 16 plan generators is on the Retired sheet, and Sherburne County 1 (6090/1) and Comanche 2 (470/2) are both still dated 2026-12. | about 75% |

The three chances add up to 2.45 predictions expected to hold. They are not independent: a coal retirement reported for October would most likely break O1 and O3 together.

If O1 holds, January to October 2026 has no coal retirement in EIA-860M. If it fails, the rows are named. Late reports can still add rows later (Schiller's 2025 retirement appeared four months after it happened), so O1 says nothing about later workbooks. O2 fails if a unit is left dated to a month already past at the end of October, or newly dated to one.

## Described, not scored

- The planned month of Campbell 1-3 in the October workbook, beside forecast R3 in [`renew-plan.md`](renew-plan.md) (that DOE renews Campbell's order by 14 November 2026). The October file reports the state at the end of October, before that expiry, so it is not a test of R3.
- Every operating coal plant dated to retire from 2026-11 to 2027-12, with its units, MW, months and whether it is under a DOE order.
- Every coal unit whose sheet or month changed from the September to the October workbook (the comparison coalsep makes; it does not compare capacity).
- Coal on the October Retired sheet with retirement year 2025 or later, against the eight 2025 rows in September's.

## Job

`coaloct-v1` will run `coaloct.py`, the code of `coalsep.py` 0.1.0 with the workbook names, the gate and these bars changed, with its unit tests on hand-built sheets. The code will be published before the October workbook is read. The job is filed once EIA posts `october_generator2026.xlsx`; it records that file's size and md5 when it downloads it. The scored result will say plainly which bars held and which failed. Forecast F1 in [`coalsep-plan.md`](coalsep-plan.md) (a DOE order covering Sherburne County 1 by 31 December 2026) is unchanged and is scored on 1 January 2027.

Text: CC BY 4.0. [`test_coaloct_plan_doc.py`](../test_coaloct_plan_doc.py) (Apache-2.0) checks the numbers on this page against job coalsep-v1's output.
