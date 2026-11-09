# rusliab: candidate totals checks for PUDL's RUS Form 7 balance sheet liabilities

By MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name. Apache-2.0.

PUDL's community epic [catalyst-cooperative/pudl#5154](https://github.com/catalyst-cooperative/pudl/issues/5154) asks for
`subcomponents_sum_to_total` dbt tests on every RUS table. `core_rus7__yearly_balance_sheet_liabilities` has none yet.
This script measures, before any test is written, how many borrower-years each candidate test would flag:

- `rusliab.py` re-implements the macro's logic (`dbt/macros/expect_subcomponents_sum_to_total.sql`: SUM per label,
  negative labels subtracted, failure when `ABS(sum - total) > tolerance`, groups with a NULL side skipped) in plain Python,
  and runs five candidate tests (three variants for `payments_unapplied`) with tolerance 10 on PUDL's nightly parquet files
  for the core and out liabilities tables. It also compares total liabilities with total assets for each borrower-year,
  and lists the structure of two other RUS-7 tables.
- `test_rusliab.py` checks the re-implementation on small hand-made tables (standard library only).

Run: `pip install polars`, `python -m unittest -v test_rusliab`, `python rusliab.py --out-dir out`.

These are counts from a re-implementation, not from dbt, and no person has checked them by hand. Data: PUDL nightly
builds (CC BY 4.0, Catalyst Cooperative).
