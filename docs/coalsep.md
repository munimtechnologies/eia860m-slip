# Coal in EIA's September 2026 workbook: no coal retirement from January to September 2026

Status: scored against its pre-registration. The gate held and 3 of 3 predictions held. The plan, [`coalsep-plan.md`](coalsep-plan.md), was committed on 28 October 2026 at 12:17 UTC; job coalsep-v1 ran from 19:24 to 19:27 UTC the same day. Nothing in the plan was changed after the output was read. MV2 of Munim, Inc.; this page and the code were made with AI agents working in my name.

## Result

**No coal generator is on the Retired sheet of EIA's September 2026 EIA-860M workbook with retirement year 2026.** So EIA-860M, as of its September 2026 report (published 23 October 2026), records no U.S. coal retirement from January to September 2026. [`coal-rows.md`](coal-rows.md) found the same for January to August on PUDL's changelog, the first such year in a record that starts in 2016.

| # | what was fixed in advance | our chance | result | verdict |
|---|---|---|---|---|
| G1 | gate: EIA's August 2026 workbook reproduces coal-rows (no 2026 coal retirement; at least 15 of the 16 plan generators with PUDL's month) | gate | 0 coal rows retired in 2026; 16 of 16 plan generators match | held |
| S1 | no coal row on the September Retired sheet has retirement year 2026 | about 85% | 0 rows | held |
| S2 | none of the 16 plan generators retired; Sherburne County 1 and Comanche 2 still dated 2026-12 | about 75% | none retired; 6090/1 and 470/2 both 2026-12 | held |
| S3 | operating coal dated 2026-10 to 2026-12 totals 3,000 to 4,500 MW, at least 60% at plants under DOE orders | about 85% | 3,584.5 MW in 9 units; 2,569.5 MW under orders (share 0.7168) | held |

The three chances add up to 2.45 predictions expected to hold; 3 held. Brier scores: 0.0225 (S1), 0.0625 (S2) and 0.0225 (S3), mean 0.0358. The three are not independent (a 2026 coal retirement would most likely have broken S1 and S2 together), and, as the plan said in advance, most of the MW in S3 was already known from job p5score-v1.

## What moved from August to September

Four coal units changed their status or month, and no other did (the job compares sheet and month for every coal unit in either workbook, apart from retirements dated before 2026; it does not compare capacity): Culley 2 (90.0 MW) and Craig 1 (427.0 MW) moved from 2026-09 to 2026-12, and Schahfer 17 and 18 (361.0 MW each) moved from 2026-10 to 2026-12. All four are at plants under DOE 202(c) orders, and each new month is the month the order now in force expires ([`p5score-2026-09.md`](p5score-2026-09.md)).

No operating coal unit is dated before 2026-10, so none is past its planned month, and none is dated 2026-10 at all: the earliest is Campbell 1-3 (1,330.5 MW), dated 2026-11, the month its order 202-26-39 expires.

## Coal dated to retire from 2026-10 to 2027-12

From the job output ([`coalsep-2026-09.md`](coalsep-2026-09.md)): 16 plants, 9,742.5 MW, of which 2,569.5 MW is at plants under DOE orders.

- **Dated 2026:** 3,584.5 MW in six plants. Four are under DOE orders (Campbell, Schahfer, Craig, Culley). The other two are Sherburne County 1 (680.0 MW, Minnesota) and Comanche 2 (335.0 MW, Colorado), whose owner has asked to run it to March 2028.
- **Dated 2027-12:** 6,158.0 MW in ten plants, none under a DOE order, led by Baldwin (1,157.0 MW) and Kincaid (1,112.0 MW) in Illinois and Victor J Daniel (1,004.0 MW) in Mississippi.

The eight coal generators on the September Retired sheet with retirement year 2025 are the same eight that the final 2025 EIA-860 lists in [`coal-rows.md`](coal-rows.md), with the same months.

## What this does and does not say

- It extends "no coal retirement in 2026" by one month, on EIA's own workbook. It says nothing about later workbooks: EIA-860M rows can appear months late (Schiller's 2025 retirement appeared four months after it happened).
- The source changed from PUDL's changelog (which still ends with August) to EIA's workbooks. The plan said so before the job ran, and gate G1 checked that EIA's August workbook gives the same rows PUDL did.
- The range stated in advance in [`coal-plan-misses.md`](coal-plan-misses.md) for EIA's first count of 2026 coal retirements (0.3-2.5 GW) is not re-scored here. Forecast F1 in the plan (a DOE order covering Sherburne County 1 by 31 December 2026, 60%) stays open and is scored on 1 January 2027.
- Prior art: a tutorial at spatialworkflow.io, updated 15 October 2026, found no coal among the 2026 retirements in EIA-860M for August 2026, as coal-rows did on 16 October. We found no other published reading of the September workbook's coal rows as of 28 October 2026.

## Files

- [`coalsep-2026-09.md`](coalsep-2026-09.md) and [`../data/coalsep_2026-09.json`](../data/coalsep_2026-09.json): the job output, unchanged.
- [`../tools/coal-rows/coalsep.py`](../tools/coal-rows/coalsep.py) 0.1.0 and its 25 unit tests, which passed in the sealed job on 2026-10-28 ([`coalsep-v1-unittests.txt`](coalsep-v1-unittests.txt); md5s in [`coalsep-v1-md5.txt`](coalsep-v1-md5.txt)).
- Workbooks read: September 2026 (14,013,970 bytes, md5 4c741eb77a5ccad5aca32ffe43f398af) and August 2026 from EIA's archive (13,955,142 bytes, md5 9727ac867236faab7d5503175dacdf38), both the same as recorded in the plan.

Reproduce:

```
pip install openpyxl
cd tools/coal-rows && python -m unittest -v test_coalsep
python coalsep.py --out-dir out --work-dir .
```

Code: Apache-2.0. Text and data: CC BY 4.0. [`test_coalsep_doc.py`](../test_coalsep_doc.py) checks this page against the job's output.
