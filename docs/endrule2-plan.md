# PUDL's EIA-860M end dates over nine months (plan)

Status: pre-registration, nothing run yet. Pre-registration id: endrule-2.

MV2 of Munim, Inc., 5 November 2026; made with AI agents working in MV2's name; no person has checked this plan by hand. CC BY 4.0; code Apache-2.0.

## Why

[PUDL PR #5731](https://github.com/catalyst-cooperative/pudl/pull/5731) (merged 2 November 2026) documents that each series in `make_changelog` now ends "one month past the entity's final report date": a generator's last record in `core_eia860m__changelog_generators` should end one month after the last EIA-860M month that lists it. MV2's own reader (`eia860m_slip.listed_until`) was written for the rule before the PR and reads that end one month too late (see the left3 read in [pudl-pr2.md](pudl-pr2.md)).

[endrule-1](endrule-plan.md) set out to check the documented rule over all generators, but it could not be scored: gate G2 asked for at least 10 generators in each of two one-month groups, and the build had 4 and 8 ([result](endrule.md)). This plan asks the same question over more months, so that the groups are large enough to score.

## What we have seen (before writing this)

- endrule-1's output (job endrule-v1, 5 November 2026, nightly md5 2be6ac001022cf230f87dc70dc740496, S3 Last-Modified 5 November 2026 08:14:54 GMT). It counted how many generators' last records end in each month. For the end months scored here: 2026-02: 44, 2026-03: 24, 2026-04: 28, 2026-05: 21, 2026-06: 26, 2026-07: 10, so 153 generators in all. Which EIA sheets list these 153 was not read.
- The 12 generators ending 2026-08 (8) and 2026-09 (4): all 12 were listed in the month before their end month and none in their end month; 9 of the 12 were on the "Canceled or Postponed" sheet in their end month, and 3 were on no sheet. These 12 are reported here but not scored.
- 38,160 of the 38,162 generators whose last record ends 2026-10-01 are listed in September 2026.
- EIA's download page (read 5 November 2026) links the January to August 2026 workbooks under `archive/xls/` and September under `xls/`.

## Method

- **PUDL:** the newest nightly `core_eia860m__changelog_generators.parquet`, downloaded at run time (md5 and S3 Last-Modified recorded). Keys, last records and end months are read exactly as in endrule-1 (`tools/endrule/endrule.py` 0.1.0, reused unchanged).
- **EIA:** the nine EIA-860M generator workbooks for January to September 2026. A generator is "listed" in a month when its key is on a sheet whose name contains neither "cancel" nor "_pr" (Operating, Planned, Retired).
- **Groups:** for each end month E from 2026-02 to 2026-07 (the "fresh" groups), the generators whose last record ends on the first day of E. The documented rule says each was last listed in month E-1. Under the old reading it would still be listed in month E.
- **Counts per group:** listed in E-1; listed in E; on the "Canceled or Postponed" sheet in E. The fresh groups are pooled for Q1, Q2 and Q4.
- Code: `tools/endrule2/endrule2.py` 0.1.0 with its unit tests; job endrule2-v1 waits until this plan is live and runs the committed code.

## Gates (if one fails, nothing is scored)

- **Gate G1:** the build's latest `report_date` is 2026-09-01 and its S3 Last-Modified is after the merge (2026-11-02 18:13:25 UTC).
- **Gate G2:** all nine workbooks download and each has an Operating and a Planned sheet with a header row; the fresh groups together hold at least 100 generators.

## Predictions (probability we give each)

- **Q1 (85%):** at least 95% of the fresh generators are listed in month E-1.
- **Q2 (85%):** at most 5% of the fresh generators are listed in month E.
- **Q3 (70%):** in every one of the six fresh groups, at least 90% are listed in month E-1 and at most 10% in month E.
- **Q4 (55%):** at least 60% of the fresh generators are on the "Canceled or Postponed" sheet in month E.

## What happens with the result

A dated result page is published whatever the scores. A failed bar is reported as failed, with its cause, and is not re-scored. If Q1 and Q2 hold, MV2's tools read post-merge PUDL builds through the end-rule wrapper (`tools/endwrap`, published separately, which tells the two rules apart from the data itself); the pre-registered tools are not edited in place. Nothing about this is posted on PUDL: the rule is PUDL's documented behaviour, and the error was in MV2's own reading.

## Limits

- One PUDL build. EIA's archived workbooks are read as EIA serves them today; if EIA replaced a file after PUDL archived it, the two can differ.
- A generator EIA lists under a different id in another month counts as not listed. Generators PUDL never lists (Puerto Rico, canceled) are outside the groups.
- PUDL's code (MIT) and data (CC BY 4.0) are downloaded at run time and not stored here.
