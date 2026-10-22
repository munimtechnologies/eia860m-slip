# EIA-860M generator changelog rebuilt from EIA's own workbooks, 2015-07 to 2026-08 (preliminary, 0.1.0)

File: [`../data/eia860m_changelog_from_workbooks.csv.gz`](../data/eia860m_changelog_from_workbooks.csv.gz). MV2 of Munim, Inc. (made with AI agents working in his name). Compilation CC BY 4.0; the underlying EIA-860M data are published by the U.S. Energy Information Administration.

## What it is

A consecutive changelog of every generator in EIA's monthly EIA-860M workbooks. A row is written when a generator is first listed, when it changes, when it leaves the workbook, and when it comes back. Each month is compared only with the month before. Unlike PUDL's `core_eia860m__changelog_generators`, a value that changes and later comes back (A, B, A) is kept. The twenty-ninth result ([`history-revert.md`](history-revert.md)) shows why that matters.

It was written by `tools/annual-flows-candidate/history.py` 0.1.0 in compete job `history-v1` (22 October 2026), from all 134 monthly workbooks in PUDL's raw archive (Zenodo record 22995197, `eia860m-2015.zip` to `eia860m-2026.zip`, each md5-checked). The file is the job's output, unchanged.

## Columns

| column | meaning |
|---|---|
| report_month | the workbook month, YYYY-MM |
| key | plant_id_eia/generator_id, keyed as PUDL keys them (no leading zeros) |
| plant_id_eia, generator_id | the two parts of the key |
| event | first, changed, left or back |
| sheet | the workbook sheet the row is on (blank for left) |
| status | EIA's status code; rows on the Retired sheet read RE (blank for left) |
| planned_month | planned operating month, YYYY-MM, for planned statuses only |
| nameplate_mw | nameplate capacity in MW; blank where the sheet has no Nameplate Capacity column or the cell is empty |

## How rows are made

- Sheets read: every sheet except Canceled or Postponed and the Puerto Rico sheets (`*_PR`). A key on more than one row keeps its first row (each month has one such duplicate key; see [`layouts-v1-output.md`](layouts-v1-output.md)).
- **changed** means the sheet, status, planned month or nameplate MW (rounded to 0.001 MW) differs from the generator's row in the month before.
- **left** means the generator was in the month before and is not in this month. **back** means it was listed in an earlier month, was not in the month before, and is listed again.

## Rows by year and event (the job's own count; 117,110 rows in all)

| year | first | changed | left | back |
|---|---|---|---|---|
| 2015 | 24193 | 1472 | 43 | 1 |
| 2016 | 1174 | 27603 | 178 | 10 |
| 2017 | 2008 | 4200 | 372 | 24 |
| 2018 | 1067 | 3241 | 169 | 25 |
| 2019 | 1373 | 3776 | 160 | 29 |
| 2020 | 1265 | 4401 | 192 | 40 |
| 2021 | 1440 | 4852 | 155 | 40 |
| 2022 | 1232 | 4543 | 194 | 30 |
| 2023 | 1356 | 5139 | 152 | 27 |
| 2024 | 1884 | 5440 | 471 | 313 |
| 2025 | 1472 | 5329 | 219 | 36 |
| 2026 | 1455 | 4061 | 216 | 38 |

The month-by-month count is in [`heldtrace-v2-output.md`](heldtrace-v2-output.md) ("Rebuilt changelog rows by month"; job `heldtrace-v2`, 22 October 2026).

## Known limits (read before use)

- **July 2015 to March 2016 have no nameplate MW.** Those sheets have only Net Summer Capacity, so `nameplate_mw` is blank there. This is expected to account for most of the 27,603 "changed" rows of 2016: in April 2016, MW goes from blank to a value for nearly every generator. A month-by-month count is queued (job `heldtrace-v1`).
  - Update, 22 October 2026: confirmed by job `heldtrace-v2`. 24,427 of the 27,603 are in April 2016 ([`heldtrace.md`](heldtrace.md)).
- **2024 has 313 "back" rows**, against 1 to 40 in every other year. Not yet explained; the same job counts the rows month by month.
  - Update, 22 October 2026: 283 of the 313 are in December 2024, after 282 generators left the November 2024 workbook (job `heldtrace-v2`). Why they were missing from that workbook as read is still not known; it has not been checked against EIA's own site. Treat November 2024 as a month in which about 280 generators may be missing.
- Only status, planned month, MW and sheet are tracked. Changes in other columns (technology, retirement dates and so on) give no row.
- Workbook values are as EIA published them in each month's file. A later EIA revision of a month is not reflected.
- Ends at the August 2026 workbook. EIA's September 2026 file is due on 23 October 2026; an update will follow once its archive copy can be checked.
- Preliminary: these rows have not yet been checked against EIA's files by any test beyond the job's own readers and checks.
