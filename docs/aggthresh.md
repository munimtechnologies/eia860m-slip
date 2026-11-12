# aggthresh: PUDL aggregate tests whose `error_if` can never be reached

Pre-registered on 2026-11-12, before any data or test file was read by code. Licence: Apache-2.0 (code),
CC BY 4.0 (text). Made with AI agents working in the name of MV2 of Munim, Inc. (mv2@munimtech.com);
no person has checked this analysis or its results by hand.

Code: [`tools/aggthresh/aggthresh.py`](../tools/aggthresh/aggthresh.py) (unit tests in `test_aggthresh.py`).
PUDL is by Catalyst Cooperative (MIT); dbt-expectations (metaplane/dbt-expectations) is Apache-2.0.

## The mechanism (desk proof)

1. dbt counts a test's failures as the number of rows its query returns. `error_if` compares that
   count with a threshold (default `!=0`). If `error_if` is not met, dbt checks `warn_if` (default
   `!=0`) and reports **warn**.
2. dbt-expectations' aggregate tests (`expect_column_min_to_be_between`, `..._max_...`,
   `..._sum_...` and others) call `expression_between` -> `expression_is_true`
   (`macros/schema_tests/_generalized/expression_is_true.sql`). Without `group_by` that query is
   `select min(col) >= 0 as expression from model where <row_condition>`, filtered to rows where the
   expression is not true. It returns **0 or 1 rows**.
3. So with `error_if: ">13"` a failing min test returns 1 row, `1 > 13` is false, and dbt reports
   warn. PUDL's runner (`src/pudl/validate/dbt.py`) calls `dbt build` with only `--target`,
   `--select` and `--exclude`, takes `success` from dbt, and gathers context only for `fail`
   results, so a warn never fails validation. **Such a test cannot fail, however bad the data.**
4. Examples on PUDL `main` (2026-11-12): `core_rus7__yearly_statement_of_operations` (and `out_`)
   has three `expect_column_min_to_be_between` tests with `error_if` `">6750"`, `">1600"`, `">810"`;
   `core_epamats__hourly_emissions.heat_content_mmbtu` has one with `error_if: ">13"` and the
   description "Fail if many more negative values appear"; `core_rus12__yearly_plant_costs` has
   three with comments `# 0.4% of the data` and `# 0.7% of the data`. These thresholds look sized
   as row counts, which only a row-level test (for example
   `dbt_expectations.expect_column_values_to_be_between`) produces.

A search of PUDL issues and PRs (GitHub, 2026-11-12) found no report of this.

## A second slip in the same table (RUS-7 statement of operations)

`src/pudl/package_data/rus7/column_maps/statement_of_operations.csv` maps the raw field
`othercapitalcreditsthismonth` to `patronage_capital_or_margins_other_capital_credits_ytd_opex_report_month`
(every year 2006-2021), while its siblings are `..._other_capital_credits_opex_ytd` and
`..._opex_ytd_budget`. The transform's regex `^(group)_(.+)_(opex_ytd|opex_ytd_budget|opex_report_month)$`
therefore files the this-month value under opex_type `other_capital_credits_ytd`, and
`src/pudl/metadata/fields.py` lists `other_capital_credits_ytd` as a valid opex_type, so no
constraint catches it. The header came in with PR #4974 (2026-02-05), whose old header used
`other_capital_credits_ytd`, `..._ytd_budget`, `..._ytd_report_month`. No PUDL issue mentions it.

## Pre-registered predictions

Part 1, static scan of `dbt/schema_inputs/**.yml` at PUDL commit
`551954e7af0e3bb7c7c314ac0ee1734a0efbedaa` (read from the GitHub source tarball):

- **A1**: at least 40 aggregate dbt-expectations tests have no `group_by`, are not `severity: warn`,
  and have an `error_if` that 1 failing row cannot reach. (Desk estimate from a code search: about
  80, counting core and out tables.)
- **A2**: at least 3 of them size the threshold in rows, records, cases, values or percent of the
  data in a comment or description.
- **S1** (consistency): an independent line scanner flags exactly as many tests as the YAML parse.
- Controls: **K1** the RUS-7 SOO `opex_ytd` min test is flagged; **K2** the EPA MATS
  `operating_time_hours` `expect_column_values_to_be_between` test (row level, `error_if: ">0"`) is
  not flagged; **K3** the EPA MATS `heat_content_mmbtu` min test is flagged.

Part 2, PUDL nightly `core_rus7__yearly_statement_of_operations.parquet`, with each test's own
`row_condition`:

- **A3a/b/c**: for `opex_report_month`, `opex_ytd` and `opex_ytd_budget`, the exact query shape
  dbt-expectations compiles for the min test returns 1 row (the test currently warns and cannot
  fail), while more than 1 row is below 0.
- **O1**: rows with opex_type `other_capital_credits_ytd` exist, all in group
  `patronage_capital_or_margins`, and none has an `opex_ytd` or `opex_ytd_budget` value.
- **O2**: no row with opex_type `other_capital_credits` has an `opex_report_month` value.
- **O3**: at least one borrower-year has a this-month other-capital-credits value above 10 USD in
  absolute value.
- **O4**: a patronage-capital totals check (Form 7 Part A line 28 = line 20 + lines 21-27, per
  borrower-year, tolerance 10, NULL parts as 0) on `opex_report_month` fails on more borrower-years
  as labelled than when `other_capital_credits_ytd` is counted as `other_capital_credits`.
- **O5**: the same check on `opex_ytd` fails on at most 5% of borrower-years.
- **OC** (control): leaving line 20 (`total_minus`) out of the check makes at least 50% of
  borrower-years fail on `opex_ytd`.

Not predicted, reported: counts by category, which custom PUDL tests carry `error_if`, the
generated `dbt/models` count, how many rows are below 0 against each RUS-7 threshold and which
opex types they come from, and the budget-column version of the totals check.

## Suggested fixes (for PUDL to judge)

- Where a threshold is meant as a row count, use the row-level test
  (`dbt_expectations.expect_column_values_to_be_between` with the same `min_value`/`row_condition`),
  so `error_if` counts rows; or keep the aggregate test and drop `error_if`.
- Map `othercapitalcreditsthismonth` to `patronage_capital_or_margins_other_capital_credits_opex_report_month`
  and remove `other_capital_credits_ytd` from the opex_type enum.

## Results

Pending: job `aggthresh-v1`. Results will be added here with the counts as measured, whether each
prediction held or not.
