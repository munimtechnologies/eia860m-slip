# The 16 generators that left EIA-860M's Retired sheet in September 2026 are nuclear units retired before 2002

Status: scored against its pre-registration ([`docs/sepretired-plan.md`](sepretired-plan.md), commit a3ce085, fixed before job sepretired-v1 read anything about these generators): 1 of 2 scored predictions held. S2 failed. S3 is scored on EIA's October 2026 workbook, which EIA's page says is due on 24 November 2026. Every number below is checked against the job's raw output by the doc test [`test_sepretired_doc.py`](../test_sepretired_doc.py).

Made by MV2 of Munim, Inc. with AI agents working in his name. Text and data: CC BY 4.0. Job sepretired-v1 (23 October 2026) ran [`tools/annual-flows-candidate/sepretired.py`](../tools/annual-flows-candidate/sepretired.py) 0.1.0 (Apache-2.0) unchanged, after its 10 unit tests passed ([`sepretired-v1-unittests.txt`](sepretired-v1-unittests.txt)). Raw output: [`docs/sepretired-v1-output.md`](sepretired-v1-output.md) and the job's log [`docs/sepretired-v1-stdout.txt`](sepretired-v1-stdout.txt). Data: [`data/sepretired_rows.csv`](../data/sepretired_rows.csv).

## Order of events

The plan was committed at 19:07:11 UTC on 23 October 2026. The job polled the plan's address from 19:07:11 UTC, got a 404, and was first served the plan at 19:17:11 UTC. Only then did it read any workbook. It read EIA-860M August 2026 from PUDL's raw archive, EIA's own September 2026 file (14,013,970 bytes, md5 4c741eb77a5ccad5aca32ffe43f398af, the same file monthcheck-sep2026-v1 read) and the annual EIA-860 2025 generator workbook.

## The bars

| bar | outcome | value |
|---|---|---|
| S1. All 16 are on no sheet of the September 2026 workbook, Canceled or Postponed and `*_PR` included | held | 16 of 16 |
| S2. At least 12 of the 16 are listed as retired (RE, 2002 to 2025) by the annual EIA-860 2025 file | failed | 0 of 16 |
| S3. At most 3 of the 16 are listed again in October 2026 | not scored yet | |

S2 failed in the direction the plan named as the other possibility. All 16 are among the 56 generators on August's Retired sheet whose retirement year is not in 2002 to 2025: each is retired before 2002 by August's own sheet. None of them is on any sheet of the annual 2025 file.

## The 16

All 16 are nuclear. August 2026's Retired sheet lists them as retired between 1972 and 1998. Together they are 8,663.1 MW of nameplate capacity, at 15 plants in 9 states. Plant names, months and years are as the workbook gives them.

| key | plant | state | retired (month/year) | MW |
|---|---|---|---|---|
| 1517/1 | Maine Yankee | ME | 8/1997 | 920 |
| 1645/1 | Yankee Rowe | MA | 2/1992 | 185 |
| 1697/1 | Big Rock Point | MI | 8/1997 | 75 |
| 1729/1 | Fermi | MI | 11/1972 | 65 |
| 246/3 | Humboldt Bay | CA | 12/1985 | 65 |
| 3166/1 | Peach Bottom | PA | 3/1975 | 42 |
| 360/1 | San Onofre Nuclear Generating Station | CA | 11/1992 | 456 |
| 4143/5 | Genoa | WI | 4/1987 | 50.3 |
| 558/1 | Haddam Neck | CT | 12/1996 | 600.3 |
| 566/1 | Millstone | CT | 7/1998 | 661.5 |
| 6107/1 | Trojan | OR | 1/1993 | 1216 |
| 6176/1 | Rancho Seco | CA | 9/1990 | 963 |
| 8011/2 | Crane Clean Energy Center | PA | 7/1979 | 961 |
| 869/1 | Dresden Generating Station | IL | 10/1985 | 207 |
| 885/1 | Zion | IL | 1/1998 | 1098 |
| 885/2 | Zion | IL | 1/1998 | 1098 |

At 7 of the 15 plants, the September workbook lists no generator at all. The other 8 still have generators listed in September: on the Operating sheet at 6 of them (for example 5 at Fermi and 10 at Humboldt Bay), and only on the Retired sheet at San Onofre (2) and Genoa (1). September's Retired sheet lists no generator retired before 2002, so those 3 are later retirements.

## The Retired sheet as a whole

- **August 2026:** 7,324 generators: 7,268 retired in 2002 to 2025, 40 after 2025 and 16 before 2002 (the 16 above). None has a missing year.
- **September 2026:** 7,321 generators: 7,270 retired in 2002 to 2025 and 51 after 2025. None is retired before 2002 and none has a missing year.
- **Moves between the two months:** 16 left (8,663.1 MW), all before 2002. 13 entered (20.5 MW), all from the Operating sheet: 11 retired after 2025 and 2 in 2002 to 2025.

So September's Retired sheet holds only generators retired since 2002, which is the scope EIA's page gives for it ("a comprehensive list of generators which retired since 2002", from March 2017 data). In August it did not. The September file removed exactly the rows outside that scope and nothing inside it.

The comparison with the annual EIA-860 2025 file is unchanged by September. All 4,565 generators the annual file lists as retired in 2002 to 2025 are on September's Retired sheet, as they were on August's. The monthly sheet lists 2,705 more retired in those years, against 2,703 in August.

## What it means

The 16 generators that failed bar P3 of [`docs/sep2026.md`](sep2026.md) are not losses of generators retired since 2002. They are nuclear units retired between 1972 and 1998, outside the Retired sheet's documented scope, and September's file brought the sheet back inside it. For a user, then: a count of generators retired since 2002 taken from September 2026's sheet loses nothing against August's, but a count of all retired capacity taken from August 2026's sheet includes 8,663.1 MW that is outside the sheet's documented scope.

What the files do not say is when or why these 16 came onto the sheet. March 2017's Retired sheet listed no generator retired before 2002 (job retiredscope-v1, [`docs/heldtrace.md`](heldtrace.md)), so they came on at some later month. [`docs/retiredentry-plan.md`](retiredentry-plan.md) sets four predictions about that before job retiredentry-v1 reads their history. One of them tests a third-party website's statement that August 2026's inventory lists 21 historically retired reactors.

## Limits

- One month's removal. S3, scored on the October 2026 workbook, will say whether any of the 16 comes back.
- The scope check uses the retirement year each sheet gives. A retirement year that EIA edits would move a generator between groups without any other change.
- Nothing here says why EIA added or removed these rows. EIA's page says estimates "will be corrected without specific acknowledgment or explanation in subsequent month's inventory", and it has no note on this change.
- The 16 are not independent: one edit at EIA can add or remove many rows at once.
- No person has opened the workbooks by hand to confirm these rows.
