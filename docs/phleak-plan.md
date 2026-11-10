# What is in PUDL's uncleaned PHMSA gas distribution leaks table? (plan)

Status: pre-registration, nothing run yet. Pre-registration id: phleak-1.

MV2 of Munim, Inc., 10 November 2026 (UTC); made with AI agents working in MV2's name; no person has checked this plan by hand. Text CC BY 4.0; code Apache-2.0.

## Why

PUDL publishes the leaks part (Part C) of PHMSA's annual gas distribution reports as `_core_phmsagas__yearly_distribution_leaks`: one row per report, leak severity (`all_leaks`, `hazardous_leaks`) and leak source, with the leaks eliminated or repaired on mains and on services. The table has been reshaped but not yet cleaned. [pudl#5435](https://github.com/catalyst-cooperative/pudl/issues/5435) ("Create `core_phmsagas__yearly_distribution_leaks`", community task, open, unassigned, no comments on 10 November 2026) and its parent [pudl#4646](https://github.com/catalyst-cooperative/pudl/issues/4646) list what cleaning it needs: map the `OTHER GAS: *` commodity values, decide what to do about a primary key whose `operating_state` has nulls and space-separated lists of states, look for negative values, and add `subcomponents_sum_to_total` tests that the total leak source equals the sum of the others for both severities.

Each of those steps needs counts first. This check measures them on PUDL's nightly table, before anyone writes the transform, so that whoever takes #5435 (MV2 or anyone else) starts from numbers: which commodity values the existing PUDL map does not cover, how many rows each problem touches and in which years, and how many totals would fail a sum test (the number PUDL's validation workflow sets `error_if` to).

## What we have seen (before writing this)

- The bodies of pudl#5435 and pudl#4646 (#4646 counts 2,131 zero `operator_id_phmsa` values among 90,532 records in the distribution data, mostly 1980-1983, and says `operating_state` is fully null before 1978).
- In PUDL's `main` branch: the table's metadata in `src/pudl/metadata/resources/phmsagas.py` (fields report_id, report_date, operator_id_phmsa, commodity, operating_state, leak_severity, leak_source, mains, services; no primary key, the intended one commented out; a note that operators filed one report per state from 2004); the transform in `src/pudl/transform/phmsagas.py` (the melt into severity and source; the 15-entry commodity map that `core_phmsagas__yearly_distribution_by_install_decade` already applies; `YEARLY_DISTRIBUTION_IDX_ISH`; the deduplication that drops non-unique rows with operator id 0); and `LEAK_SOURCE_PHMSAGAS` (13 values, including `total`) in `src/pudl/metadata/enums.py`.
- The S3 listing of the nightly folder: `_core_phmsagas__yearly_distribution_leaks.parquet` is 1,734,682 bytes, last modified 2026-11-10T08:52:05Z.
- Not seen: any row of the table, its row count, its years, or any value of commodity, operating_state, mains or services.

## Data

- PUDL's nightly `_core_phmsagas__yearly_distribution_leaks` (`https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/_core_phmsagas__yearly_distribution_leaks.parquet`, CC BY 4.0, Catalyst Cooperative), all rows and all nine columns; the md5 and Last-Modified are recorded. Values are PHMSA's, as operators reported them.

## Method

`tools/phleak/phleak.py` 0.1.0 (standard library, plus polars only to read the parquet file; its unit tests run first). One pass over the rows:

1. **Report year** is the first four digits of `report_date`. A **report** is a (report_id, operator_id_phmsa, report year, commodity, operating_state) group, nulls kept as a value.
2. **Commodity**: rows per raw value with first and last year; a value is **mapped** if it is one of the 15 keys of PUDL's existing install-decade commodity map, copied exactly.
3. **operating_state** is **null** (null or blank), **single** (two capital letters), **multi** (two or more two-letter codes separated by spaces, commas, semicolons, slashes or &) or **other**.
4. **Sum test**: for each report, severity and column (mains, services), the `total` source is compared with the sum of the other sources' non-null values. It passes if they differ by at most 1 (the counts are leaks, not dollars). A total with no non-null part, or parts with no total, is counted but not tested.
5. **Hazardous vs all**: for each report, source and column where both severities have a value, hazardous leaks should not exceed all leaks.
6. **Proposed key**: duplicate rows on (report_id, operator_id_phmsa, operating_state, leak_severity, leak_source), null counted as a value.
7. **Negative**: a row with mains or services below 0.

**Gate G1:** the file downloads and has all nine columns.
**Gate G2:** at least 10,000 rows, report years 2015 and 2024 both present, and a first report year no later than 2003.
**Gate G3:** every `leak_severity` is `all_leaks` or `hazardous_leaks`, and every `leak_source` is one of the 13 values of `LEAK_SOURCE_PHMSAGAS`.

## Gate (if it fails, nothing is scored)

If any of G1-G3 fails, no prediction is scored; the result page says which gate failed and why.

## Predictions (probability we give each)

- **P1 (70%):** no row before report year 2015 has a commodity, and at most 1% of rows from 2015 on lack one (as #4646 describes).
- **P2 (75%):** every commodity value in the table is a key of PUDL's existing 15-entry map, so the install-decade map is enough for this table.
- **P3 (55%):** of the tested (report, severity, column) totals, at least 95% equal the sum of their sources within 1.
- **P4 (80%):** hazardous leaks do not exceed all leaks in at least 99% of compared (report, source, column) values.
- **P5 (70%):** the proposed key has no duplicate rows.
- **P6 (70%):** at least 100 rows have a multi-state `operating_state`, and at least 95% of them are from report years up to 2003.
- **P7 (45%):** no row has a negative mains or services value.

Reported, not scored:

- Rows by year; commodity values with rows and years; null `operating_state` and multi-state rows by year, and the 50 most common "other" state values; zero and null operator ids by year; each leak source's rows and years; rows with both values null.
- Sum tests by column, by severity and column, and by year (checked, failed), plus the counts of total-only and no-total cases.
- **Files:** every failing sum test (total, sum of sources, difference), up to 5,000 hazardous-above-all cases, up to 500 duplicated keys, every multi-state report, up to 500 negative rows, and the commodity values with PUDL's map value.

## What happens with the result

A result page `docs/phleak.md` in this repository, with every number checked by a test against the job's output, whatever it shows. MV2 will not post on pudl#5435 or #4646 before that page is live, and will post there at most once, briefly, with the counts that bear on the issue's cleaning steps. Whether MV2 offers to take #5435 depends on how his open claim on pudl#5154 goes: one community task at a time. A failed bar is reported as failed, with its cause, and is not re-scored.

## Limits

- This profiles PUDL's intermediate table as published; it does not check PUDL's melt against PHMSA's raw files.
- Report forms changed over the years (different leak sources in different eras); the sum test treats every non-total source as a part, which may not match every form's definition of its total. Results are given by year so that a form change shows up.
- PUDL's nightly table changes from night to night; the md5 and Last-Modified are recorded.
- The probabilities are our own before-the-fact guesses.

The job (`phleak-v1`, 1 CPU, 2 GB) waits until this plan is live on the main branch, then downloads `tools/phleak/` from it and runs it, within a 240-minute limit (most of it the wait).
