# Does PUDL split RUS Form 7 "other capital credits" across two labels? (plan)

Status: pre-registration, nothing run yet.
Pre-registration id: rusops-1.

Made with AI agents working in MV2's name (MV2, Munim, Inc., mv2@munimtech.com). Code
Apache-2.0, text CC BY 4.0. PUDL is MIT-licensed and its data CC BY 4.0; this check only reads it.
PUDL's data (CC BY 4.0) is downloaded at run time and not stored here.

## Why

PUDL builds `core_rus7__yearly_statement_of_operations` (RUS Form 7, Part A) by matching every
column name in `src/pudl/package_data/rus7/column_maps/statement_of_operations.csv` against
`^(<group>)_(.+)_(opex_ytd|opex_ytd_budget|opex_report_month)$` in `src/pudl/transform/rus7.py`.
The middle part becomes `opex_type`, and every item should have three columns, one per period.

Reading the column map on main (2026-11-14), one name is spelled differently from the other two
for its item:

- `patronage_capital_or_margins_other_capital_credits_opex_ytd`
- `patronage_capital_or_margins_other_capital_credits_opex_ytd_budget`
- `patronage_capital_or_margins_other_capital_credits_ytd_opex_report_month`

So the year-to-date and budget values of Form 7 line 27 ("Other Capital Credits and Patronage
Dividends") should land under `opex_type` `other_capital_credits`, and the monthly value under a
second label, `other_capital_credits_ytd`. `opex_type` has no enum constraint, so nothing stops
this. A structure-only profile of the nightly table from an earlier MV2 job (rusliab-v1, 2026-11-09)
did list both labels among the 28 `opex_type` values; it did not look at their values. A search
of PUDL's issues for "other_capital_credits" (2026-11-14) found nothing.

That reading was made through a text-summarising fetch, not byte for byte, so this check re-reads
the column map exactly and measures what the split does in the data.

## Data

- The column map at the commit `main` points to when the job runs (recorded), from
  raw.githubusercontent.com.
- PUDL nightly tables from `https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/`:
  `core_rus7__yearly_statement_of_operations` and `out_rus7__yearly_statement_of_operations`
  (Last-Modified and ETag recorded).

## Method (`tools/rusops/rusops.py` 0.1.0)

1. Apply PUDL's regex to every column name and list each item that does not have all three
   periods ("orphans"), and every name ending `_ytd_opex_report_month`.
2. For `other_capital_credits` and `other_capital_credits_ytd` in each table: rows,
   borrower-years, and per value column the non-null count and the count with an absolute value
   above $10.
3. A Form 7 line-29 check per borrower-year (`borrower_id_rus`, `report_date`), with the same
   semantics as PUDL's `subcomponents_sum_to_total` macro and a $10 tolerance: `total` in
   `patronage_capital_or_margins` against `total_minus` in `patronage_and_operating_margins`
   (line 21) plus `non_operating_margins_interest`, `construction_funds_allowance`,
   `equity_investment_losses`, `non_operating_margins_other`,
   `generation_and_transmission_capital`, `other_capital_credits` and `extraordinary_items`
   (lines 22-28). Run twice for each value column: **as labelled** (those eight items) and
   **merged** (also counting `other_capital_credits_ytd`).

## Gate and predictions

- **Gate G1:** the column map is read at a recorded commit, and both nightly tables download and
  each has exactly the four `opex_group` values `cost_of_electric_service`, `opex`,
  `patronage_and_operating_margins` and `patronage_capital_or_margins`. If G1 fails, nothing below
  is reported as measured.
- **P1 (90%):** in the core table, `other_capital_credits_ytd` has at least one row, its
  `opex_ytd` and `opex_ytd_budget` are null in every row, and `opex_report_month` of
  `other_capital_credits` is null in every row.
- **P2 (90%):** the same holds in the out table.
- **P3 (60%):** core rows of `other_capital_credits_ytd` with an absolute `opex_report_month` above
  $10 number at least 1% of the table's borrower-years.
- **P4 (65%):** for `opex_report_month`, the line-29 check fails for strictly more borrower-years
  as labelled than merged.
- **P5 (55%):** for `opex_ytd`, the merged line-29 check fails for fewer than 5% of the
  borrower-years it checks.

## Outputs

`rusops.json`: the column-map orphans, both profiles, failures by year, and both line-29 checks
for all three value columns with their largest failures.

## Limits

The line-29 item list is taken from the printed Form 7 and PUDL's labels; signs (for example
whether `equity_investment_losses` is stored as income or loss) are not adjusted, so P5 measures
whether a test is usable as is, not whether the reported totals are right. Lines 20 and 21 are
not checked here. Nightly tables change between runs. No person has checked these results by hand.
