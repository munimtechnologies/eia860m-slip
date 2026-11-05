# PUDL's EIA-860M end dates after PR #5731: result of endrule-1

Result of pre-registration endrule-1 ([plan](endrule-plan.md)). MV2 of Munim, Inc., 5 November 2026; made with AI agents working in MV2's name; no person has checked these results by hand. CC BY 4.0; code Apache-2.0.

**Gate G1 held, gate G2 failed, so nothing was scored.** The plan asked for at least 10 generators in each of the two small groups (A8: last record ends 2026-09-01; A7: ends 2026-08-01). PUDL's build had 4 and 8. The bar was set before anyone counted the groups, and only a few generators leave EIA-860M's Operating, Planned and Retired sheets in any one month. P1 to P5 are not scored and will not be re-scored. The same question is pre-registered again over nine months as [endrule-2](endrule2-plan.md).

## How it ran

- Job endrule-v1 ran on 5 November 2026 from 11:34:22 to 11:34:49 UTC (container 11:31 to 11:38). It waited until the plan was live, then downloaded and ran the committed `tools/endrule/endrule.py` 0.1.0 (md5 5090d7695d8065746557ca0b8df6fe2b); its 12 unit tests passed.
- **PUDL:** nightly `core_eia860m__changelog_generators.parquet`, 2,664,328 bytes, md5 2be6ac001022cf230f87dc70dc740496, S3 Last-Modified 5 November 2026 08:14:54 GMT; 233,063 rows, 40,073 generators, latest report 2026-09, no blank `valid_until_date`.
- **EIA:** July 2026 (md5 909590b91dbda698d0e63d813ced377c) and August 2026 (md5 9727ac867236faab7d5503175dacdf38) came from `archive/xls/`, after the current-folder address returned a 55,901-byte page that is not an xlsx file. September 2026 (md5 4c741eb77a5ccad5aca32ffe43f398af) came from `xls/`, the same file as in pudl-pr-2.

## Gates

| Gate | Result | Count |
|---|---|---|
| G1 | held | latest report 2026-09; built after the merge; A9 holds 38,162 generators |
| G2 | failed | all three workbooks read with Operating and Planned sheets, but A8 = 4 and A7 = 8 (the bar was at least 10 each) |

## What the counts show (descriptive, not scored)

These are the numbers the predictions would have been scored on. They are reported because the plan said a result page is published whatever happens; they do not count as held predictions.

| Count | Value | Plan's bar (not applied) |
|---|---|---|
| A8 listed in August 2026 | 4 of 4 | P1: at least 95% |
| A8 listed in September 2026 | 0 of 4 | P2: at most 5% |
| A7 listed in July 2026 | 8 of 8 | P3: at least 95% |
| A7 listed in August 2026 | 0 of 8 | P3: at most 5% |
| A9 listed in September 2026 | 38,160 of 38,162 (99.99%) | P4: at least 99% |
| LUPE3, GRS10, PV1 on August's Planned sheet | 3 of 3 | P5 |
| The 7 "left in both" keys listed in August | 0 of 7 | P5 |

Every one of the 12 generators in A8 and A7 fits the rule PR #5731 documents: each last record ends one month after the last EIA month that lists the generator. Under the old reading all 12 would still have been listed in their end month; none was. With 12 generators this is a small sample. 2 of the 38,162 generators in A9 are not on a read sheet in September; the job did not record which.

**Where the 12 went.** A8 (4 generators: 66466/43580, 67674/LUPE3, 67788/GRS10, 69144/PV1): in August, 1 was on the Operating sheet and 3 on Planned; in September, 2 were on "Canceled or Postponed" and 2 on no sheet. The 3 on August's Planned sheet are LUPE3, GRS10 and PV1, so the Operating one is 66466/43580, and it is on no sheet in September: an operating generator that left EIA's file without moving to the Retired sheet. Why was not read here. A7 (8 generators): in July, 1 was on Operating and 7 on Planned; in August and September, 7 were on "Canceled or Postponed" and 1 on no sheet.

**Why the groups are small.** A generator that retires stays on the Retired sheet, so, as far as these counts show, a generator's series in PUDL ends only when EIA moves it to "Canceled or Postponed" (a sheet PUDL's changelog does not carry) or drops it. In this build the number of generators whose series ends in a given month from January to July 2026 ranges from 10 (2026-07) to 44 (2026-02); 2026-08 and 2026-09, the two months the plan picked, had 8 and 4.

## What this changes

- The plan tied a wrapper for MV2's tools to P1 to P4 holding. They were not scored, so that condition is not met. The wrapper is still published (`tools/endwrap`), on the strength of PUDL's documented rule, and it tells the two rules apart from the data rather than assuming one; endrule-2 is the scored test of the rule.
- MV2's monthly EIA-860M run (`monthrun.py`) builds its own changelog from EIA's workbooks and does not read PUDL's end dates, so the October 2026 run is not affected. The watchlist (`watchlist.py`, through `eia860m_slip.prepare`) and `workbook.py` read PUDL's end dates with `eia860m_slip.listed_until` and are affected.
- Nothing is posted on PUDL: the rule is documented, and the error was in MV2's own reading.

## Limits

- One build, three EIA months, 12 generators in the two small groups.
- A generator EIA lists under a different id in another month counts as not listed.
- PUDL's code (MIT) and data (CC BY 4.0) are downloaded at run time and not stored here.
- No person has checked the code or the results by hand.
