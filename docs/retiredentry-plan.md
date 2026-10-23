# Pre-registration: when did the 16 pre-2002 nuclear generators reach EIA-860M's Retired sheet?

Status: pre-registered, not yet scored.

Fixed on 23 October 2026, before job retiredentry-v1 reads the changelog rows of these 16 generators or any workbook other than August and September 2026. The job's first step polls this file's address on GitHub and computes nothing until it is served, so the commit time of this file is the record of when the bars below were fixed. They will not be moved after the job runs.

Made by MV2 of Munim, Inc. with AI agents working in his name. Text: CC BY 4.0. Code: [`tools/annual-flows-candidate/retiredentry.py`](../tools/annual-flows-candidate/retiredentry.py) 0.1.0 (Apache-2.0), with its tests. It reuses the sheet readers of `retiredgap.py` 0.1.0 and `retiredscope.py` 0.1.0 unchanged.

## Why

[`docs/sepretired.md`](sepretired.md) found that the 16 generators that left the Retired sheet of EIA's September 2026 EIA-860M workbook are all nuclear units that August 2026's sheet lists as retired between 1972 and 1998, and that September's Retired sheet lists no generator retired before 2002. EIA's page says that from March 2017 data the Retired tab "includes a comprehensive list of generators which retired since 2002", and job retiredscope-v1 found that March 2017's sheet listed no generator retired before 2002 ([`docs/heldtrace.md`](heldtrace.md)). So at some month between April 2017 and August 2026 these 16 came onto a sheet whose documented scope leaves them out. This plan asks when, and how.

## What was known when this plan was fixed

- The 16 keys and the retirement year August 2026's Retired sheet gives each (job sepretired-v1, [`../data/sepretired_rows.csv`](../data/sepretired_rows.csv)).
- None of them is among the 238 generators that left the Retired sheet in March 2017 (all 238 were on no sheet the changelog reads through August 2026), and none is among the 41 that left it later and were not listed again (job gapcensus-v1).
- A third-party website that lists U.S. nuclear plants (usnuclearpowerplants.com, read on 23 October 2026) says that EIA-860M's August 2026 inventory "for the first time lists 21 historically retired reactors, among them Shippingport, Vallecitos, Saxton and Piqua". None of those four plants is among the 16. No EIA source we found says this, and EIA's EIA-860M page carries no note about it. The site is not affiliated with EIA, and how it counted is not stated.
- Nothing else about the 16: not their changelog rows, the month they reached the Retired sheet, or any workbook before August 2026.

## What the job does

`retiredentry.py` 0.1.0 downloads the rebuilt changelog [`../data/eia860m_changelog_from_workbooks.csv.gz`](../data/eia860m_changelog_from_workbooks.csv.gz) at commit a3ce085 (version 0.1.1, 117,756 rows) and takes every row of the 16. For each it finds the first month it is on the Retired sheet, what the row before says (first listed, back after a gap, or moved from another sheet), and any later row up to August 2026 that is not a change on the Retired sheet. It counts, month by month from July 2015 to September 2026, how many of the 16 are on the Retired sheet. It then reads, from PUDL's raw archive (Zenodo record 22995197, md5-checked as before), the workbook of each arrival month and of the month before, plus July and August 2026, and EIA's own September 2026 file (size and md5 compared with the file monthcheck-sep2026-v1 read). For each arrival month it reports each generator's retirement year, technology and MW, and how many generators the Retired sheet lists by retirement year. In July, August and September 2026 and every month it reads, it lists every row on every sheet (Canceled or Postponed and `*_PR` included) whose technology names nuclear, whether or not the row has a plant ID, and every row whose plant name contains Shippingport, Vallecitos, Saxton or Piqua.

## Predictions

- **R1.** All 16 first reach the Retired sheet in one and the same workbook month. Two or more arrival months fail this bar.
- **R2.** In the workbook of the month each of them first reaches the Retired sheet, its retirement year is the one August 2026's sheet gives it (so each came on with a retirement year before 2002, rather than with a later year that was edited afterwards). One of the 16 with another year, or none, fails this bar.
- **R3.** From its arrival month to August 2026, each of the 16 is on the Retired sheet every month by the changelog: no row of it in that span is a "left", a "back" or a move to another sheet (a change of MW on the Retired sheet is allowed). One such row for one of them fails this bar.
- **R4.** Counting every row on every sheet of the August 2026 workbook whose technology names nuclear and whose retirement year is before 2002, plus nuclear rows on a Retired sheet with no retirement year, gives exactly 16. More (for example the 21 the website above states) or fewer fails this bar.

Each bar is counted separately and reported as "N of 4 held". A bar the job cannot score (a file not served or not readable) is reported as not scored, and the job is run again under a new version.

## Limits

- The changelog is rebuilt by this repository's own code from the same archive; a month read again here by the same reader is a reproducibility check, not an independent one.
- The changelog tracks only sheet, status, planned month and MW, so a retirement year edited while a generator stays on the Retired sheet gives no row. R2 checks the arrival month only.
- The 16 are not independent: one edit at EIA can add or remove many rows at once.
- R4 looks for "nuclear" in the technology column. A reactor listed under another technology name would be missed.
- The site quoted above may have counted differently (for example reactors rather than generators, or sources other than this workbook). A result against R4 says what the workbook lists, not why the site's count differs.
