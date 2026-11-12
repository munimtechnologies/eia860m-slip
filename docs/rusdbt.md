# Do the proposed RUS Form 7 liabilities totals tests pass in PUDL's own dbt project? (result of rusdbt-1)

Result of the pre-registered check in [tools/rusdbt](../tools/rusdbt/README.md) (the
predictions there went live at 23:24:46 UTC on 11 November 2026, commit `6d5d7cc`, before any
dbt run). Job `rusdbt-v1` ran `rusdbt 0.1.0` on 12 November 2026 (dbt test at 14:35 UTC), after
its 14 unit tests passed.

Made with AI agents working in MV2's name (MV2 of Munim, Inc., mv2@munimtech.com); no person
has checked these results by hand. Text and data CC BY 4.0; code Apache-2.0. PUDL is
MIT-licensed (Catalyst Cooperative); this check only reads it.

## Why

Catalyst Cooperative's PUDL issue
[#5760](https://github.com/catalyst-cooperative/pudl/issues/5760) asks for
`subcomponents_sum_to_total` data tests on `core_rus7__yearly_balance_sheet_liabilities` and
`out_rus7__yearly_balance_sheet_liabilities`. MV2 proposed five tests per table
([tests-block.yml](../tools/rusdbt/tests-block.yml)). This check runs them with PUDL's real dbt
macro instead of a re-implementation.

## Setup

- PUDL `dbt/` folder at commit `060c1875c47d557420cd63e55ca07dce2bc80838` (main on
  12 November 2026), dbt-core 1.12.7 with dbt-duckdb 1.11.1, a throwaway local profile.
- Data: PUDL's nightly parquet outputs as downloaded during the run:
  `core_rus7__yearly_balance_sheet_liabilities` (1,025,519 bytes),
  `out_rus7__yearly_balance_sheet_liabilities` (1,115,797 bytes) and
  `core_rus7__yearly_balance_sheet_assets` (1,064,867 bytes).
- 16 data tests ran: the 5 proposed tests on each liabilities table, 1 negative control on the
  core table (total long-term debt with `payments_unapplied` **added** instead of subtracted),
  and the 5 tests already on main for the assets table (positive control, from PR #5729).

## Results

**All 4 predictions held (P1-P4).** dbt summary: `PASS=15 WARN=0 ERROR=1 SKIP=0`; the one
error is the negative control, as planned.

| Prediction | Bar | Measured | Held |
|---|---|---|---|
| P1 five proposed tests on the core table | all pass, 0 failures | 5 of 5 pass | yes |
| P2 five proposed tests on the out table | all pass, 0 failures | 5 of 5 pass | yes |
| P3 negative control fails | 4,555-4,647 failing borrower-years | 4,601 | yes |
| P4 existing assets tests pass | all pass | 5 of 5 pass | yes |

Per test (both liabilities tables gave the same result):

| Total | Core | Out |
|---|---|---|
| `total_margins_and_equities` | pass, 0 | pass, 0 |
| `total_long_term_debt` (minus `payments_unapplied`) | pass, 0 | pass, 0 |
| `total_noncurrent_obligations` | pass, 0 | pass, 0 |
| `total_current_and_accrued_liabilities` | pass, 0 | pass, 0 |
| `total_liabilities_and_other_credits` | pass, 0 | pass, 0 |

The negative control failed for exactly 4,601 borrower-years, the same count that MV2's earlier
plain-Python check (`tools/rusliab`) found on the 9 November nightly. So the setup can both pass
and fail a test, and the reported long-term debt totals match only when unapplied payments are
subtracted.

## Limits

- One nightly build. Every test uses `tolerance: 10`, as the assets tests on main do.
- `dbt_helper` was not run; the tests were added to each `schema.yml` by script, mirroring the
  `schema.human.yml` text. A pull request would edit both files the same way, as #5729 did.
- The sign of `payments_unapplied` is inferred from the data, not checked against the RUS Form 7
  instructions.

## Files

- [data/rusdbt-run.json](../data/rusdbt-run.json): the job's `rusdbt.json`, unchanged (PUDL
  commit, dbt version, every test's status and failure count, verdicts).
- [data/rusdbt-dbt-stdout.txt](../data/rusdbt-dbt-stdout.txt): dbt's own output, unchanged.
- [test_rusdbt_result.py](../test_rusdbt_result.py) checks every number on this page against
  those files.
