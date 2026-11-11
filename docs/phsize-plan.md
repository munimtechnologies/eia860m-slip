# Are the services sizes in PUDL's PHMSA gas distribution material-and-size table labelled as reported? (plan)

Status: pre-registration, nothing run yet. Pre-registration id: phsize-1.

MV2 of Munim, Inc., 11 November 2026 (UTC); made with AI agents working in MV2's name; no person has checked this plan by hand. Text CC BY 4.0; code Apache-2.0.

## Why

PHMSA's annual gas distribution report counts miles of main and numbers of services by material and by size. PUDL melts these wide columns into `_core_phmsagas__yearly_distribution_by_material_and_size`, one of the uncleaned tables that [pudl#4646](https://github.com/catalyst-cooperative/pudl/issues/4646) plans to clean and validate. Reading the code suggests that some services sizes get the wrong label:

- The services columns are picked with the filter `^services_(<materials>)_(.*)$`, so any suffix is accepted.
- `main_size` is then taken from each column name by `str.extract` with the alternation of `MAIN_PIPE_SIZES_PHMSAGAS`. That is the list of **mains** sizes, and the pattern has no anchors, so the leftmost match wins.
- The services columns in PUDL's column map end in `over_6_in` and `over_8_in` as well as sizes the mains list has. The mains list has neither of those two. Reading the code, a services count for "over 6 in" would get a null `main_size`, and one for "over 8 in" would be labelled `8_in`, where `8_in` is a mains size for exactly 8 inches. The column `services_other_alt` (a by-material count, not a size) also passes the filter and would get a null size.

This is a reading of the code only. Whether the published table holds such rows, how many there are and how much they weigh is what this check measures, before anyone reports it.

## What we have seen (before writing this)

- In PUDL's `main` branch, `src/pudl/transform/phmsagas.py`: the `MELT_PATTERNS` entry for the table (mains `^main_(<materials>)_(<main sizes>)_miles$`, services `^services_(<materials>)_(.*)$`); the category patterns passed to `_melt_merge_main_services` (`main_size` from `MAIN_PIPE_SIZES_PHMSAGAS`, `material` from `MATERIAL_TYPES_PHMSAGAS`, each one unanchored capture group); `_assign_cols_from_patterns` (`df[col_name] = df[pattern_col].str.extract(pattern)`); `_melt_col_pattern`; and the later steps of the asset (the `other` material detail merge, and services text that is not a number moved into `main_other_material_detail`).
- In `src/pudl/metadata/enums.py`: `MAIN_PIPE_SIZES_PHMSAGAS` (0.5_in_or_less, 0.5_to_1_in, 1_in_or_less, 1_to_2_in, 2_in_or_less, 2_to_4_in, 4_to_6_in, 4_to_8_in, 8_in, 8_to_12_in, 10_in, 12_in, over_12_in, total, unknown) and `MATERIAL_TYPES_PHMSAGAS`.
- The header row of `src/pudl/package_data/phmsagas/column_maps/yearly_distribution.csv`. Its services size columns end in unknown, 0.5_in_or_less, 0.5_to_1_in, 1_in_or_less, 1_to_2_in, 2_to_4_in, 4_to_6_in, 4_to_8_in, over_6_in, over_8_in or total. `over_6_in` appears for steel, copper, cast_iron, plastic, other and all_materials. `over_8_in` appears for twelve materials, seven of which (cast_or_wrought_iron, pvc, pe, abs, other_plastic, other_alt, reconditioned_cast_iron) have no 8-inch mains column. Which years carry each column was not read.
- PUDL issue and pull request searches for `main_size`, `by_material_and_size` and `over_8_in`: 0 results each.
- The S3 listing of the nightly folder: `_core_phmsagas__yearly_distribution_by_material_and_size.parquet` is 6,532,003 bytes, last modified 2026-11-10T08:52:05Z.
- Not seen: any row of the table, its row count or years, or whether any services row has a null or `8_in` size.

## Data

- PUDL's nightly `_core_phmsagas__yearly_distribution_by_material_and_size` (`https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/_core_phmsagas__yearly_distribution_by_material_and_size.parquet`, CC BY 4.0, Catalyst Cooperative): report_date, report_id, operator_id_phmsa, material, main_size, mains_miles and services, all rows. The md5 and Last-Modified are recorded. Values are PHMSA's, as operators reported them.

## Method

`tools/phsize/phsize.py` 0.1.0 (standard library, plus polars to read and group the parquet file; its unit tests run first).

1. **Groups:** one per report year, material and `main_size` (null kept as its own value), with the number of rows, of rows with a mains value, of rows with a services value, of rows with both, and the sums of each. NaN counts as missing.
2. A **services row** is a row with a services value (0 counts as a value). A **null-size services row** has a services value and a null `main_size`. An **8_in no-mains row** has a services value, `main_size` `8_in` and one of the seven materials with no 8-inch mains column.
3. **Base** for the shares: the sum of services over every row whose `main_size` is not `total` (null included).

**Gate G1:** the file downloads and has the seven columns above.
**Gate G2:** at least 100,000 rows and at least 1,000 services rows.

## Gate (if it fails, nothing is scored)

If G1 or G2 fails, no prediction is scored, and the result page says which gate failed and why.

## Predictions (probability we give each)

- **P1 (80%):** at least 100 services rows have a null `main_size`.
- **P2 (85%):** at least 99% of the null-size services rows are for steel, copper, cast_iron, plastic, other, all_materials, other_alt or other_material (the materials whose columns the code would leave without a size: the six `over_6_in` materials, `services_other_alt`, and any numeric text in `services_other_material_detail`). If there are no null-size services rows, there is nothing to test, and P2 counts as failed.
- **P3 (70%):** at least 100 services rows are 8_in no-mains rows (labelled `8_in` for a material that has no 8-inch size on the form, so they can only come from `over_8_in`).
- **P4 (85%):** no services row has a size the services columns cannot produce: only 0.5_in_or_less, 0.5_to_1_in, 1_in_or_less, 1_to_2_in, 2_to_4_in, 4_to_6_in, 4_to_8_in, 8_in, total, unknown or null.
- **P5 (65%):** the null-size and 8_in no-mains services together sum to less than 1% of the base.

Reported, not scored:

- Rows, years, services rows and mains rows; services rows and mains rows by size; null-size services rows by material (rows, first and last year, sum) and by year; `8_in` services rows by material, with the rows where an 8-inch mains value and an over-8-inch services count share one row; the number of distinct reports with each kind of flagged row.
- **Files:** every group (year, material, size) with its counts and sums, and up to 3,000 flagged rows (null-size and 8_in no-mains services rows) with report id, year, operator id, material, size, mains and services.

## What happens with the result

A result page `docs/phsize.md` in this repository, with every number checked by a test against the job's output, whatever it shows. If the table does hold mislabelled services sizes (P1 or P3 holds), MV2 will report them to PUDL at most once, on a UTC day with no other post from him there, with the counts and the code lines, after the result page is live. He will not open a pull request unless a maintainer asks for one (MV2 has one PUDL community task open, on pudl#5154). If neither holds, the page says so and nothing is posted beyond it. A failed bar is reported as failed, with its cause, and is not re-scored.

## Limits

- This checks PUDL's published intermediate table, not PHMSA's raw files, and it cannot see which raw column a row came from. Labels are inferred from the code and the column map.
- A size of `8_in` on a steel, ductile_iron, copper, other or all_materials services row (the five materials with both an `over_8_in` services column and an 8-inch mains column) cannot be told apart from a true 8-inch count here, so only the seven materials with no 8-inch mains column are counted for P3.
- Counts include reported zeros, which carry no services but still carry a wrong label.
- PUDL's nightly table changes from night to night; the md5 and Last-Modified are recorded.
- The probabilities are our own before-the-fact guesses.

The job (`phsize-v1`, 1 CPU, 2 GB) waits until this plan is live on the main branch, then downloads `tools/phsize/` from it and runs it, within a 240-minute limit (most of it the wait).
