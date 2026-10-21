# Were the annual EIA-860's plan-only generators already in its early release? (pre-registration)

Written 21 October 2026, before job `erplan-v1` runs and before any generator row of an early-release copy of the annual EIA-860 has been read. MV2 of Munim, Inc. (made with AI agents). CC BY 4.0.

## Where this comes from

The twenty-sixth result ([`entry-timing.md`](entry-timing.md)) followed the annual EIA-860's plan-only generators for a year Y (set A: generators the annual file for report year Y - 1 plans for Y, missing from January's EIA-860M, first listed in EIA-860M after January). They enter EIA-860M about evenly from the February to the August report and then stop, at about the time of the annual file's final release in September of Y. Its five predictions held, but it said plainly that the result does not separate the two readings it was built to test:

- **R1 (lag).** The annual filing for Y - 1, due early in Y, already held the project; EIA-860M listed it only after EIA took the filing in.
- **R2 (revision).** The annual record was added or revised during Y, before the final release, after the project had appeared elsewhere (for example in EIA-860M).

Its Next section said that telling them apart needs a dated copy of the annual file from before its final release. Probe `zenodoprobe-v1` (21 October 2026, metadata only; raw output [`zenodoprobe-v1-output.md`](zenodoprobe-v1-output.md), tool `tools/annual-flows-candidate/zenodoprobe.py`, 10 of 10 unit tests passed) found such copies. Catalyst Cooperative's raw EIA-860 archive on Zenodo (PUDL, seed record 13682785) holds two different copies of `eia860-2021.zip` to `eia860-2025.zip`: one published in June to August of the following year and a changed one published from September on. The 2015-2020 files have one copy each. EIA's own early-release file names (`eia860YYYYER.zip`) answered with an HTML page, not a zip, so they are not used.

| plan year Y | file (report year Y - 1) | first copy (Zenodo record, date) | final copy (record, date) |
|---|---|---|---|
| 2022 | eia860-2021.zip | 6954131, 2022-08-02 | 7113854, 2022-09-26 |
| 2023 | eia860-2022.zip | 8164776, 2023-07-19 | 10067566, 2023-11-02 |
| 2024 | eia860-2023.zip | 11662381, 2024-06-15 | 13682785, 2024-09-24 |
| 2025 | eia860-2024.zip | 15629904, 2025-06-12 | 17091669, 2025-09-10 |

The final copy is the last change of each file, the one PUDL's tables are built from. Check E1 below tests that each first copy is EIA's early release. EIA publishes each EIA-860M report three to four weeks after its month ends, so the July report of Y comes out in late August at the earliest. Every first copy above was published by 2 August of Y, before the July report came out.

## The question

Of A's capacity first listed in EIA-860M in the July or August report of Y (A late), how much was already in the early release's plan for Y? Under R1 the annual filing held it, so most of it should be there. Under R2 it was added to the annual record after EIA-860M listed it, so it cannot be in a copy published before that listing came out. A's capacity first listed in the February or March report (A early) is the comparison: under R1 when EIA-860M listed a project should not change whether the early release holds it; under R2, projects listed before the early release can have been added to it, while late ones cannot.

## Method

`tools/annual-flows-candidate/erplan.py` 0.1.0, written before the run, with 22 unit tests on hand-built rows (`test_erplan.py`). It reads the twenty-sixth result's sets unchanged from `data/entrytime_sets.csv` at commit c7eca74 (one row per generator, year and set, with its MW and first EIA-860M listing month) and downloads the eight copies above from Zenodo, each checked against the size and MD5 checksum Zenodo lists. In each copy it reads the generator workbook (`3_1_Generator...xlsx`): the Operable, Proposed, and Retired and Canceled sheets, each found by name, with its header row found by its "Plant Code" and "Generator ID" columns. Each generator of plan year Y gets one class in each copy, by plant id and generator id (trimmed, any case, as in the earlier results):

- `plan_y`: on the Proposed sheet with a current planned operation year of Y (the copy's plan for Y)
- `proposed_other`: on the Proposed sheet with another year or none
- `operable`: on the Operable sheet and not on the Proposed sheet
- `retired`: only on the Retired and Canceled sheet
- `absent`: on none of them

Spans of first EIA-860M listing: early (February-March reports), mid (April-June), late (July-August), edge (September-December or after Y). The statistic is a MW share: the MW of a span's generators that are `plan_y` in the early release, over the span's MW. MW come from the sets file, not from the copies.

Reported for each plan year and pooled over the years scored: MW by class in both copies for A, A_built and B, every span, all technologies and each group; a CSV of every generator with both classes; and the 15 largest late A generators not in the early release's plan for Y.

## Checks (all must pass, or the run is description only)

- **D1.** Each of the eight copies downloads and matches Zenodo's size and MD5 checksum.
- **D2.** Each copy holds exactly one generator workbook, with an Operable and a Proposed sheet whose header rows name the plant code and generator id columns, and on the Proposed sheet a current-year column.
- **E1.** Each first copy calls itself an early release (in the workbook's file name or in the text above a sheet's header row), and no final copy does.

A plan year whose copies fail D1, D2 or E1 is dropped. With fewer than three of the four plan years left, the run is description only.

- **C1.** The sets file matches the twenty-sixth result: pooled 2018-2025, A 55,263.5 MW, A_built 36,998.4 MW, B 32,937.3 MW, and A's July-August MW 13,082.3 (8,253.0 + 4,829.3), each to 0.15 MW.
- **F1.** Pooled over the plan years scored, at least 0.95 of A's MW is found in the final copy at all. A was built from PUDL's tables of the final file, so this checks the reading and the key matching.
- **F2.** Likewise, at least 0.90 of A's MW is in the final copy's plan for Y. This checks the current-year column.
- **F3.** In every plan year scored, at least 0.95 of the final copy's Operable generators are found in the early release (any sheet). Existing generators should be in both copies. This guards against keys written differently in the two copies, which would make A look absent from the early release for the wrong reason.
- All unit tests pass in the sealed job.

## Predictions (stated before the run)

Pooled over the plan years scored, MW shares compared with their thresholds unrounded and rounded only for display.

- **P1.** A late's share in the early release's plan for Y is at least 0.70.
- **P2.** A late's share is at least 0.70 in at least 3 of the plan years with at least 100 MW of A late (no verdict if fewer than 3 years have that much).
- **P3.** A early's share minus A late's share is at most 0.20.

We do not favour either reading going in. EIA says the monthly survey sometimes "requires the use of data submitted on the annual EIA-860 before it has been fully verified by EIA", a stated route for R1, but the twenty-sixth result's edge fits R2 at least as well. The predictions are written in R1's direction because that is the stated route; the outcome map below fixes in advance what every result would mean.

**What the outcomes would mean.**

- A late's share at least 0.70 (P1) with P3 holding: most of the capacity EIA-860M first listed in July and August was in the annual data before EIA-860M listed it. R1 for most of it.
- A late's share at most 0.30: most of it was not in the annual data's plan for Y until after EIA-860M listed it. R2 for most of it.
- Between 0.30 and 0.70: both routes carry material capacity.
- P1 holds but P3 fails (A early above 0.90): R1 for most, with a smaller R2 part concentrated in the late entrants.
- A late mostly in the early release but on its Proposed sheet with another year (`proposed_other`, description only): the annual data knew the project but moved it to Y later, which is R2 in its "revised" sense.

**Could each prediction hold under the rival reading?** We ask this before the run, as the twenty-sixth result taught. P1 and P2 cannot hold under R2 as defined, because a late entrant cannot be in a copy published before its first EIA-860M listing came out if the annual record followed that listing. They can hold if the annual record was added before the early release from some source other than EIA-860M. That is still the annual data holding the project before EIA-860M, so this test separates "annual first" from "EIA-860M first". It cannot tell an original filing from a revision made before the early release. P3 alone does not discriminate: it holds under R2 too if the early entrants are also mostly missing from the early release, but then P1 fails. P1 and P3 together discriminate. Every result is published, held or not.

## What we had seen before writing this

The twenty-sixth result's published output: A's MW by month of first listing pooled over 2018-2025 (July 8,253.0 MW, August 4,829.3 MW), its March-June shares by year, and the first five rows of `data/entrytime_sets.csv` (all 2017). We have not aggregated A's July-August MW for 2022-2025 by year. From the Zenodo archive we have read only metadata: version dates, file names, sizes and checksums. No row of any copy of the annual file has been read. Before `erplan-v1` runs, job `erplan-structure-v1` reports only the structure of the eight workbooks: member file names, sheet names, header rows, column names and the text above the header rows. It analyses and writes out no data row. If that report shows that the parser needs changing (for example, a different name for the current-year column), the change is made before `erplan-v1` runs and listed in a dated amendment, with the checks and predictions unchanged.

## Run

Compete job `erplan-v1` (sealed container, Python 3.12, openpyxl) fetches erplan.py and test_erplan.py from the commit that publishes this note, or from the commit of a dated amendment, runs `python -m unittest -v test_erplan`, then `python erplan.py --data-dir /data --out-dir /out`. It is filed only after this note is public and the structure report has been read. A run with a failed check is never relabelled as scored: its raw output is published with a dated amendment, and it runs again under a new job name with these predictions unchanged.

## Limits known in advance

- A Zenodo publication date is when PUDL archived the copy, not when EIA released it. EIA's early release comes out earlier in the year, so the content can be older than the date shown, but not newer.
- Only four plan years (2022-2025) have an early-release copy; the earlier files were archived once, after their final release.
- The test separates the annual data holding a project before EIA-860M listed it from the reverse. It cannot tell an original filing from a revision made before the early release.
- Matching is by key only (trimmed, any case), as in the earlier results. A project re-keyed between the two copies counts as absent from the early release; F3 bounds how often keys differ for existing generators, not for planned ones.
- MW come from PUDL's tables (the sets file), summed over generators, so a few large projects can dominate a year. That is why P2 counts years.
