# rusdbt 0.1.0: check proposed RUS Form 7 liabilities totals with PUDL's own dbt project

Licence: Apache-2.0. Made with AI agents working in the name of MV2 of Munim, Inc.
(mv2@munimtech.com); no person has checked this code or its results by hand.

## Why

Catalyst Cooperative's PUDL issue
[#5760](https://github.com/catalyst-cooperative/pudl/issues/5760) asks for
`subcomponents_sum_to_total` data tests on `core_rus7__yearly_balance_sheet_liabilities`
and `out_rus7__yearly_balance_sheet_liabilities`, validated with dbt, and for the number
of failing records whenever a test fails. MV2's earlier tool
[`tools/rusliab`](../rusliab/) measured the five proposed tests with a plain-Python copy
of the macro (0 failures for all five, on both tables, on the 9 November 2026 nightly).
That copy might differ from the real macro. This tool runs the real one.

## What it does

1. Downloads three tables from PUDL's nightly parquet outputs: both liabilities tables and
   `core_rus7__yearly_balance_sheet_assets`.
2. Shallow-clones only the `dbt/` folder of `catalyst-cooperative/pudl` main and records
   the commit.
3. Adds the five proposed tests ([tests-block.yml](tests-block.yml), the exact text a pull
   request would add) to both liabilities `schema.yml` files. It also adds one **negative
   control** to the core table only: total long-term debt with `payments_unapplied`
   *added* instead of subtracted, which should fail.
4. Runs `dbt test` (dbt-duckdb, a throwaway local profile) for the
   `subcomponents_sum_to_total` tests of the two liabilities tables and of the assets table.
   The assets tests already exist on main (PR #5729), so they serve as a **positive control**
   for the setup.
5. Reads dbt's `run_results.json` and `manifest.json` and scores the predictions below.

It only measures. Nothing is sent to PUDL.

## Pre-registered predictions (written 2026-11-11, before any dbt run)

- **P1.** All five proposed tests on `core_rus7__yearly_balance_sheet_liabilities` pass in
  dbt (status `pass`, 0 failures).
- **P2.** All five proposed tests on `out_rus7__yearly_balance_sheet_liabilities` pass in dbt.
- **P3.** The negative control fails, with between 4,555 and 4,647 failing borrower-years
  (rusliab counted 4,601 on the 9 November nightly; the band is 1% either way for data drift).
- **P4.** Every existing `subcomponents_sum_to_total` test on
  `core_rus7__yearly_balance_sheet_assets` passes.

**Nothing-to-test rule.** If dbt reports `error` for any test in a prediction's group, or a
group has the wrong number of tests, that prediction is scored "not tested", not held or failed.
P1 and P2 count as confirmed by dbt only if P3 and P4 also held (the setup can both pass and fail
a test). If P1 or P2 fails, the number of failing records per test is reported and, as #5760 asks,
an `error_if` threshold is proposed instead of a fix.

## Run

```
pip install "dbt-core>=1.10" "dbt-duckdb>=1.9.4"
python -m unittest -v test_rusdbt
python rusdbt.py --data-dir <folder for parquet> --out-dir <output folder>
```

Outputs: `rusdbt.json` (PUDL commit, dbt version, every test's status and failure count,
verdicts), `run_results.json`, `dbt_test_stdout.txt`.

PUDL is MIT-licensed (Catalyst Cooperative); this tool only reads it.
