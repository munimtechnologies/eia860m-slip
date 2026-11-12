# totcov 0.1.0: can each of PUDL's "sum to total" data tests ever fail?

Licence: Apache-2.0. Made with AI agents working in the name of MV2 of Munim, Inc.
(mv2@munimtech.com); no person has checked this code or its results by hand.
PUDL itself is MIT (code) and CC BY 4.0 (data); nothing from it is copied here
except table, column and label names.

Pre-registered on 2026-11-12, before any data is read. The predictions below are
fixed in this commit; the result follows in a later commit, whatever it shows.

## Why

[PUDL](https://github.com/catalyst-cooperative/pudl) checks many of its tables with a
dbt test, `subcomponents_sum_to_total` (macro `dbt/macros/expect_subcomponents_sum_to_total.sql`).
For each group it sums the subcomponent rows and compares the sum with the row that
carries `total_label`. The grand total is
`MAX(CASE WHEN <total label condition> THEN total END)`, and a group fails when
`ABS(subcomponents_sum - grand_total) > tolerance`. If no row in a group carries the
total label, the grand total is NULL, the comparison is NULL, and the group passes
silently. The macro's own comment says this, and offers an optional
`minimum_total_coverage` argument (off by default) to catch it.

So a test whose `total_label` never occurs in its `categorical_column` checks nothing.
A desk check (2026-11-12) found one such test on PUDL `main`:

- `core_rus7__yearly_utility_plant_changes` (RUS Form 7 Part E) has
  `categorical_column: utility_plant_group`, `total_label: total`,
  `row_condition: utility_plant_group='utility_plant_in_service'`. But
  `utility_plant_group` only takes the values `utility_plant_in_service` and
  `total_utility_plant` (`UTILITY_PLANT_GROUP_RUS7` in `pudl/metadata/enums.py`);
  `total` is a value of `utility_plant_item`. Every group's grand total is NULL.

The same desk check found two label problems in `core_rus7__yearly_statement_of_operations`
(Part A):

- The column map `rus7/column_maps/statement_of_operations.csv` names one column
  `patronage_capital_or_margins_other_capital_credits_ytd_opex_report_month` (an extra
  `_ytd`). The transform splits column names with
  `^(group)_(.+)_(opex_ytd|opex_ytd_budget|opex_report_month)$`, so that line's
  report-month value should land under its own `opex_type`, `other_capital_credits_ytd`,
  instead of `other_capital_credits`.
- Three `expect_column_min_to_be_between` tests exclude
  `opex_type != 'interest_charged_to_construction_credit'`, but the column map names that
  line `interest_charged_to_construction`, so the exclusion matches nothing.

totcov measures all of this on the nightly data, and, as a by-product, the coverage of
every other `subcomponents_sum_to_total` test in PUDL's dbt project.

## Method

1. Sparse-clone `dbt/` of catalyst-cooperative/pudl `main`; record the commit.
2. Read every `subcomponents_sum_to_total` test in `dbt/models/**/schema.yml`
   (arguments, plus `row_condition` and `config` written beside `arguments`).
3. Download the nightly parquet of each table used (S3, `pudl.catalyst.coop/nightly/`;
   tables over 600 MB are skipped and listed).
4. Re-implement the macro in DuckDB, branch for branch (negative subcomponents first,
   then the listed subcomponents or, with no list, every label except the total; no
   ELSE), and count per test: groups, groups with a non-NULL grand total (coverage),
   failing groups, and the rows matching each label. A label with zero rows is listed.
5. Measure six proposed replacement tests for Part E on the core and out tables:
   items of plant in service (distribution, general, headquarters, intangibles,
   transmission, regional transmission and market operation, all other) sum to its
   `total`, for `ending_balance`, `additions`, `retirements`, `adjustments_and_transfers`
   (`categorical_column: utility_plant_item`, row condition on the group); and total
   utility plant = plant in service total + construction work in progress, for
   `ending_balance` and `additions` (two categorical columns, pairs of labels), all
   with `tolerance: 10` as in pudl#5154's other RUS tests. Plus a negative control:
   the first test for `ending_balance` with `distribution` left out.
6. Count the statement-of-operations labels above.
7. Exploratory, no prediction: compare Part E ending balances with the balance sheet
   (Part C, `core_rus7__yearly_balance_sheet_assets`) for plant in service, CWIP and
   total utility plant, per borrower-year, tolerance 10.

## Predictions (fixed before any data is read)

- **P1** Every existing `subcomponents_sum_to_total` test on
  `core_rus7__yearly_utility_plant_changes` (and on its `out_` table, if it has one) has
  groups but zero groups with a total: it cannot fail.
- **P2** Each of the six proposed Part E tests on the core table has a non-NULL total in
  at least 90% of its borrower-year groups. (No prediction on how many fail; the counts
  are what a PR's `error_if` would be based on.)
- **P3** The negative control finds a mismatch in at least 90% of the groups that have
  a total, so a pass of the proposed tests means something.
- **P4** The core statement-of-operations table has at least one row with
  `opex_type = 'other_capital_credits_ytd'`; in all such rows `opex_ytd` and
  `opex_ytd_budget` are NULL; and `opex_report_month` is NULL in every row with
  `opex_type = 'other_capital_credits'`.
- **P5** At least one `other_capital_credits_ytd` row has a non-NULL `opex_report_month`
  (a real value is filed under the wrong label, not just an empty one).
- **P6** No row has `opex_type = 'interest_charged_to_construction_credit'`, and at
  least one has `opex_type = 'interest_charged_to_construction'`.
- **P7** (harness check) Of the existing tests that have a finite failure allowance
  (default `error_if: !=0`, or `error_if: ">N"`; tests with `severity: warn` excluded),
  at least 95% have no more failing groups in this re-implementation than they allow.
  PUDL's nightly build runs these tests, so a lower share means the re-implementation
  is wrong, and every count above is suspect. Needs at least 10 such tests.

Scoring rules: a prediction whose inputs errored or were not downloaded is "not tested".
P1 is scored on whichever of the two tables has the test, but needs the core table.
Ties count as held (">= 90%", ">= 95%"). Nothing else is predicted; every other test's
coverage is reported as found.

## Limits

- This is a re-implementation of the macro, not dbt itself (P7 checks it against the
  nightly build's own test results only indirectly). A follow-up PR would run
  `dbt_helper validate`.
- dbt's handling of `row_condition` written beside `arguments` (rather than inside it)
  was not checked; totcov applies it either way. For the Part E test this does not
  matter: without the row condition the total label still never matches.
- Nightly data changes daily; the commit and download notes are in `totcov.json`.

## Run

    pip install duckdb pyyaml
    python -m unittest -v test_totcov
    python totcov.py --data-dir /tmp/totcov-data --out-dir out

Outputs: `out/totcov.json` (everything) and `out/totcov.csv` (one row per test).
