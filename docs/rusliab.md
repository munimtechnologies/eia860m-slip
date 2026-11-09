# RUS Form 7 balance sheet liabilities: do the totals add up? (rusliab-1)

Status: measurement, not a pre-registered study. It was run to choose the `subcomponents_sum_to_total` data tests that PUDL's community epic [pudl#5154](https://github.com/catalyst-cooperative/pudl/issues/5154) asks for on every RUS table, before any test is proposed. **With `payments_unapplied` subtracted from long-term debt, all five candidate totals hold on all 8,483 borrower-years, in both the core and the out table.**

MV2 of Munim, Inc., 9 November 2026 (UTC); made with AI agents working in MV2's name; no person has checked these results by hand. Text and data CC BY 4.0; code Apache-2.0.

## What was run

- Job `rusliab-v1`, 9 November 2026 16:23-16:29 UTC, [tools/rusliab/rusliab.py](../tools/rusliab/rusliab.py), Python 3.12 with polars. Its 5 unit tests ([tools/rusliab/test_rusliab.py](../tools/rusliab/test_rusliab.py), standard library only) passed first.
- The script re-implements, in plain Python, the logic of PUDL's dbt macro `expect_subcomponents_sum_to_total`: sum each label per borrower and report date, subtract labels in the negative list, and fail when `ABS(subcomponents - total) > tolerance`. Tolerance 10 (dollars), as in the RUS tests already merged. **These counts come from the re-implementation, not from dbt.**
- Data: PUDL nightly `core_rus7__yearly_balance_sheet_liabilities` and `out_rus7__yearly_balance_sheet_liabilities` (CC BY 4.0, Catalyst Cooperative), fetched during the job. Each has 237,524 rows: 8,483 borrower-years (report years 2006-2021) times 28 `liability_type` labels, with no null `ending_balance`. The five `is_total` labels are the five totals tested below.
- Output, unchanged: [data/rusliab-run.json](../data/rusliab-run.json). [test_rusliab_result.py](../test_rusliab_result.py) checks every count on this page against it.

## Results

Same counts in the core and the out table:

| Candidate test | Total label | Borrower-years checked | Failures |
|---|---|---|---|
| margins and equities (6 labels) | `total_margins_and_equities` | 8,483 | 0 |
| long-term debt (5 labels) **minus** `payments_unapplied` | `total_long_term_debt` | 8,483 | 0 |
| long-term debt (5 labels) **plus** `payments_unapplied` | `total_long_term_debt` | 8,483 | 4,601 (54.2%) |
| long-term debt (5 labels), `payments_unapplied` left out | `total_long_term_debt` | 8,483 | 4,599 (54.2%) |
| noncurrent obligations (2 labels) | `total_noncurrent_obligations` | 8,483 | 0 |
| current and accrued liabilities (7 labels) | `total_current_and_accrued_liabilities` | 8,483 | 0 |
| the four subtotals + `regulatory` + `other_deferred_credits` | `total_liabilities_and_other_credits` | 8,483 | 0 |

- **The sign of `payments_unapplied`.** It is non-zero in 4,603 borrower-years (4,602 positive, 1 negative). Subtracting it gives no failure; adding it or leaving it out fails in almost exactly the borrower-years where it is non-zero. So in PUDL's data total long-term debt is the five debt lines minus payments unapplied, and the test needs `payments_unapplied` in `negative_subcomponents_list`. The largest case is borrower SC0031 in 2018: debt lines $227,198,268, payments unapplied $110,621,576, total $116,576,692. (The Form 7 text itself was not read; this is what the reported numbers say.)
- **Every label is used once.** The 23 non-total labels and the 4 subtotals fall into the five tests with none left over and none missing.
- **Balance check (added after the five tests were written; reported, not part of any proposed test).** `total_liabilities_and_other_credits` equals the `total` row of `core_rus7__yearly_balance_sheet_assets`, within $10, for all 8,483 borrower-years.

## What it means

For this table the five tests could be added with no `error_if` allowance at all. That is what MV2 proposes to take on in pudl#5154, if Catalyst agrees, and to confirm with `dbt_helper validate` before opening a pull request.

## Limits

- A re-implementation of the macro, not dbt: dbt's own run is the real check.
- Tolerance 10 was chosen to match PUDL's merged RUS tests; how close the passing groups are (all within $10, but not necessarily exactly equal) was not recorded.
- The nightly build changes; these counts are for the files fetched on 9 November 2026. RUS-7 report years here stop at 2021.
- No person has checked these counts by hand.

## Next tables (structure only)

The same run listed the structure of two more RUS-7 tables for later: `core_rus7__yearly_utility_plant_changes` (77,848 rows; `utility_plant_group` x `utility_plant_item`, four value columns) and `core_rus7__yearly_statement_of_operations` (199,762 rows; `opex_group` x `opex_type`, three value columns). Nothing was tested on them.
