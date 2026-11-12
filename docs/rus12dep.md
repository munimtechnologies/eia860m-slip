# rus12dep: PUDL's RUS-12 depreciation changes totals tests can never fail

Pre-registered on 2026-11-12, before any data was read. Licence: Apache-2.0 (code), CC BY 4.0 (text).
Made with AI agents working in the name of MV2 of Munim, Inc. (mv2@munimtech.com); no person has
checked this analysis or its results by hand.

Companion to [rus12upc.md](rus12upc.md), which found the same flaw in the RUS-12 utility plant
changes tests. Code: [tools/totcov/rus12dep.py](../tools/totcov/rus12dep.py), reusing
[totcov.py](../tools/totcov/totcov.py)'s re-implementation of PUDL's dbt macro.

## The desk proof

PUDL ([catalyst-cooperative/pudl](https://github.com/catalyst-cooperative/pudl), main on
2026-11-12) has four `subcomponents_sum_to_total` tests on each of
`core_rus12__yearly_depreciation_changes` and `out_rus12__yearly_depreciation_changes`
(`dbt/models/pudl/rus12/<table>/schema.yml`), one per value column (`accruals`,
`retirements_less_net_salvage`, `adjustments_and_transfers`, `ending_balance`):

```yaml
group_by_columns: [borrower_id_rus, report_date]
categorical_column: depreciation_and_amortization_group
total_label: total_depreciation
# beside `arguments`:
row_condition: depreciation_and_amortization_group='electric_plant_in_service'
```

1. `depreciation_and_amortization_group` is constrained in `src/pudl/metadata/fields.py` to
   `DEPRECIATION_CHANGES_GROUP_RUS12`, which in `src/pudl/metadata/enums.py` has two values:
   `electric_plant_in_service` and `provision_for_depreciation_and_amortization`.
2. The transform (`_core_rus12__yearly_depreciation_changes` in `src/pudl/transform/rus12.py`)
   builds the column from a regex whose group alternatives are exactly those two names.
   `total_depreciation` is one of `DEPRECIATION_CHANGES_ITEMS_RUS12`, the item enum.
3. In the macro (`dbt/macros/expect_subcomponents_sum_to_total.sql`), `grand_total` is
   `MAX(CASE WHEN depreciation_and_amortization_group = 'total_depreciation' THEN total END)`,
   which is NULL in every group. `ABS(subcomponents_sum - grand_total) > tolerance` is then
   NULL, never true, so no group is returned. `minimum_total_coverage`, the macro's guard for
   exactly this case, is not set.
4. The `row_condition` makes it doubly sure: if it is applied, only
   `electric_plant_in_service` rows remain, so no row can carry any other group label.
   If it is not applied, point 1 still holds.

So the eight tests pass whatever the data says. Their shared description ("Check the totals
for all of the depreciation_and_amortization_group's that are just the sum of the
components") is the same sentence as on the RUS-12 utility plant changes tests, which have
the same flaw. `core_rus12__yearly_depreciation_changes` is not on the open RUS totals
checklist, [pudl#5154](https://github.com/catalyst-cooperative/pudl/issues/5154), so it is
presumably counted as done. A GitHub search on 2026-11-12 found no issue or pull request
about these tests; the only issue mentioning `total_depreciation` is the enum-reconciliation
issue [#5530](https://github.com/catalyst-cooperative/pudl/issues/5530).

## Proposed fix (what the row condition and description point to)

Within electric plant in service, the depreciation items should sum to `total_depreciation`:

```yaml
group_by_columns: [borrower_id_rus, report_date]
categorical_column: depreciation_and_amortization_item
total_label: total_depreciation
row_condition: depreciation_and_amortization_group='electric_plant_in_service'
subcomponents_list: [depreciation_steam_production_plant, depreciation_nuclear_production_plant,
  depreciation_hydraulic_production_plant, depreciation_other_production_plant,
  depreciation_transmission_plant, depreciation_distribution_plant, depreciation_general_plant,
  retirement_work_in_progress]
tolerance: 10
minimum_total_coverage: 0.9   # suggested, so a future label change cannot empty it again
```

Whether `retirement_work_in_progress` belongs in the total depends on the form; the data
check measures both versions (exploratory, below) rather than guessing.

## Pre-registered predictions

Scored by `evaluate()` in `rus12dep.py` on PUDL's nightly parquet
(`s3://pudl.catalyst.coop/nightly/<table>.parquet`, both tables). "Not tested" if a table
cannot be read or a measurement errors.

- **D1 (the existing tests are vacuous on real data).** For all 16 measurements (8 tests, each
  with and without its row condition), there is at least one group and no group has a
  `total_depreciation` row in `depreciation_and_amortization_group`.
- **D2 (the fix has something to check).** For each of the 8 proposed tests (2 tables x 4 value
  columns), at least 90% of the groups that have depreciation items also have a
  `total_depreciation` row.
- **D3 (negative control).** The proposed `ending_balance` test on the core table with every
  item's sign flipped must fail on at least 90% of groups whose `total_depreciation` is larger
  than $10 in absolute value. If the real check holds in a group (|S - T| <= 10) and |T| > 10,
  then |-S - T| >= 2|T| - |S - T| > 10, so a control that fails less often than this would
  mean the harness is not comparing what it claims to.

Exploratory, no prediction: failure counts of the proposed tests (these would set an
`error_if` in a PR); the same tests without `retirement_work_in_progress`; the
(group, item) pairs present; and the provision group's `total` built from its own items,
with and without the electric plant `total_depreciation`.

## Limits

- This re-implements the macro in DuckDB; it does not run PUDL's dbt project. A PR would be
  checked with `dbt_helper validate` first.
- The proposed item list comes from the enum, not from the RUS Form 12 instructions; the
  measured failure counts, not this document, should decide what goes in a PR.

## Results

Pending: job `rus12dep-v1` is queued.
