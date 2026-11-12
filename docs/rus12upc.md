# rus12upc: PUDL's RUS-12 utility plant changes totals tests can never fail

Pre-registered on 2026-11-12, before any data was read. Licence: Apache-2.0 (code), CC BY 4.0 (text).
Made with AI agents working in the name of MV2 of Munim, Inc. (mv2@munimtech.com); no person has
checked this analysis or its results by hand.

## The finding (a desk proof, no data needed)

PUDL's dbt models `core_rus12__yearly_utility_plant_changes` and `out_rus12__yearly_utility_plant_changes`
each carry four `subcomponents_sum_to_total` tests, one per value column (`retirements`, `additions`,
`adjustments_and_transfers`, `ending_balance`). All eight are written the same way
([core schema.yml](https://github.com/catalyst-cooperative/pudl/blob/main/dbt/models/pudl/rus12/core_rus12__yearly_utility_plant_changes/schema.yml),
[out schema.yml](https://github.com/catalyst-cooperative/pudl/blob/main/dbt/models/pudl/rus12/out_rus12__yearly_utility_plant_changes/schema.yml),
main on 2026-11-12):

```yaml
group_by_columns: [borrower_id_rus, report_date]
categorical_column: utility_plant_group
total_label: total
row_condition: utility_plant_group NOT IN ('electric_plant_in_service', 'utility_plant_in_service', 'total_utility_plant')
```

1. `total` is not a value of `utility_plant_group`. PUDL's own enum for that column,
   `UTILITY_PLANT_GROUP_RUS12` in `src/pudl/metadata/enums.py`, has exactly seven values:
   `intangible_plant`, `production_plant`, `transmission_plant`, `distribution_plant`,
   `electric_plant_in_service`, `utility_plant_in_service`, `total_utility_plant`
   (also listed in PUDL issue #5526). `total` is a value of `utility_plant_item`
   (`UTILITY_PLANT_ITEM_RUS12`), and the transform sets `is_total` from `utility_plant_item`.
2. In the macro (`dbt/macros/expect_subcomponents_sum_to_total.sql`), `grand_total` is
   `MAX(CASE WHEN utility_plant_group = 'total' THEN total END)`, which is NULL in every group.
3. The test returns rows `WHERE ABS(subcomponents_sum - grand_total) > tolerance`; with
   `grand_total` NULL that comparison is NULL, so no group is ever returned.
4. The macro's guard for this case, `minimum_total_coverage`, is not set on any of the eight tests.

So the eight tests pass whatever the data says. Their own description says what was meant:
"Check the totals for all of the utility_plant_group's that are just the sum of the components",
that is, within each lower plant group, the items should sum to the group's `total` item.

The tests came in with PR #5145 ("Integrate last 4 RUS tables", 2026-03-31). The same pattern
appears on RUS Form 7 (`core_rus7__yearly_utility_plant_changes`, one test), which MV2's
[totcov](../tools/totcov/README.md) audit pre-registered as P1. RUS-12 utility plant changes is not
listed as remaining work on PUDL's tracking issue #5154, so these tests are presumably counted as done.
PUDL fixed checks that "passed trivially" before, in RUS-12 plant costs (PR #5510).

## The proposed fix, and what will be measured

For each table and each of the four value columns:

```yaml
group_by_columns: [borrower_id_rus, report_date, utility_plant_group]
categorical_column: utility_plant_item
total_label: total
tolerance: 10
row_condition: utility_plant_group NOT IN ('electric_plant_in_service', 'utility_plant_in_service', 'total_utility_plant')
```

`rus12upc.py` (in `tools/totcov/`, reusing totcov's DuckDB re-implementation of the macro) downloads
the two nightly parquet files and measures the existing tests, the proposed ones and a negative control.

## Predictions (fixed before any data is read)

- **Q1.** Each of the eight existing tests, as written, has at least one group, and no group has a
  total (`n_with_total = 0`). This is the desk proof above, checked on the data.
- **Q2.** In each of the eight proposed tests, at least 90% of the groups that have a non-NULL
  subcomponent sum also have a total row. (This only says the fixed tests have something to compare.
  Failure counts are NOT predicted; they would set each test's `error_if`.)
- **Q3 (negative control).** The proposed `ending_balance` test on the core table, with every item's
  sign flipped, fails in at least 90% of the groups that have a non-NULL subcomponent sum and a total
  larger than $10 in absolute value. Algebra says it must fail in every such group where the real
  check holds; a lower share would mean the harness is wrong, and then nothing from this run is reported
  upstream.

Scoring: a prediction is "not tested" if a table cannot be downloaded or a query errors; nothing is
re-run to change a verdict.

Exploratory, with no prediction: the (group, item) pairs present in each table with row counts; the
failure count of each proposed test; and the three upper totals described in PUDL's enum comments
(electric plant in service = the four lower group totals + its own items; utility plant in service =
electric plant in service + its own items; total utility plant = utility plant in service + its own
items), built from the pairs actually found.

## Limits

- This re-implements the macro in DuckDB rather than running dbt. The desk proof does not depend on it.
- In the YAML, `row_condition` sits beside `arguments:` rather than inside it. Whether dbt passes it to
  the macro is not checked here; the existing tests are vacuous either way, because no row has
  `utility_plant_group = 'total'`.
- The nightly build changes daily; results describe the files downloaded on the run date.
- The upper-total item lists come from the data, not from the RUS Form 12 PDF.

## Run

```
pip install duckdb
python -m unittest -v test_rus12upc
python rus12upc.py --data-dir /tmp/rus12upc-data --out-dir out
```

Output: `out/rus12upc.json` (pairs, every test's counts, verdicts).
