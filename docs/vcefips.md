# vcefips: two place_name tests on PUDL's VCE RARE table that can never fail

Pre-registered on 2026-11-12, before any data was read. Licence: Apache-2.0 (code), CC BY 4.0 (text).
Made with AI agents working in the name of MV2 of Munim, Inc. (mv2@munimtech.com); no person has
checked this analysis or its results by hand.

Code: [tools/vcefips/vcefips.py](../tools/vcefips/vcefips.py) (unit tests: `test_vcefips.py`).

## What the tests say

PUDL's `out_vcerare__hourly_available_capacity_factor` (hourly solar and wind capacity factors
for every US county, from Vibrant Clean Energy's RARE data) has two `dbt_expectations` tests on
`place_name`. The source is
`dbt/schema_inputs/pudl/vcerare/out_vcerare__hourly_available_capacity_factor/schema.human.yml`,
and `docs/dev/data_validation_reference.rst` copies the same YAML as its worked example
(PUDL main, 2026-11-12):

```yaml
- dbt_expectations.expect_column_values_to_not_be_in_set:
    arguments:
      value_set: [bedford_city, clifton_forge_city, lake_hurron, lake_st_clair]
- dbt_expectations.expect_column_values_to_be_in_set:
    arguments:
      value_set: [oglala lakota]
      row_condition: county_id_fips = '46012'
```

## Desk proof (no data needed)

**1. The Oglala Lakota test filters on a county that does not exist.** In 2015, Shannon County,
South Dakota became Oglala Lakota County and got the new FIPS code 46102. PUDL issue #3914 asked why
it was missing from maps. PR #4319 (merged 2025-06-12) fixed this by taking place names from the
latest Census PEP vintage, and its description lists "Add a dbt test to ensure this county in
particular is renamed as expected". The
documentation lines that PR removed say "The VCE data includes the new FIPS code (46102) but the
old name". The test it added filters on `'46012'`, with the middle digits swapped. The Census
Bureau's 2020 South Dakota county list
([st46_sd_cou2020.txt](https://www2.census.gov/geo/docs/reference/codes2020/cou/st46_sd_cou2020.txt))
goes from 011 (Brookings) to 013 (Brown) and has no 012; Oglala Lakota is 102. A `row_condition`
that selects no rows leaves nothing to check, so the test passes whatever the county is called. If
the rename broke, it would not notice.

**2. The not-in-set test lists underscore spellings that can no longer occur.** Since #4319,
`_standardize_census_names` in `src/pudl/transform/vcerare.py` replaces every `_` in the name with a
space (`names_df["area_name"].str.replace("_", " ")`), and the result becomes `place_name`. The list
was written in May 2025 (PR #4198, migrating an asset check), when names still had underscores. In
that form no value can match, so the test cannot fail:

- if dropping the two Virginia independent cities broke (`_drop_city_cols`), the rows would show up
  as `bedford city` and `clifton forge city`, which the test does not catch;
- if the Lake Huron spelling fix broke (`_spot_fix_great_lakes_*`), the rows would show up as
  `lake hurron`, which the test does not catch either.

There is a further wrinkle: `lake_st_clair` was forbidden because #4029 (Feb 2025) renamed it to
`lake_saint_clair`. #4319 then went back to `lake_st_clair_michigan` on purpose, so `lake st clair`
is now an expected place name. Switching the list to spaces as it stands would make the test fail
on correct data, so that entry should be dropped, not converted.

dbt does apply these arguments: PUDL sets `require_generic_test_arguments_property: true`, and
dbt-core's `extract_test_args` merges `arguments` into the test kwargs.

## Proposed fix

```yaml
- dbt_expectations.expect_column_values_to_not_be_in_set:
    arguments:
      value_set: [bedford city, clifton forge city, lake hurron]
- dbt_expectations.expect_column_values_to_be_in_set:
    arguments:
      value_set: [oglala lakota]
      row_condition: county_id_fips = '46102'
```

The same change is needed in the generated `schema.yml` and in the docs example.

## Pre-registered predictions

The job reads only `county_id_fips` and `place_name` from PUDL's nightly
`out_vcerare__hourly_available_capacity_factor.parquet` (3.96 GB, S3 LastModified
2026-11-11 06:36 UTC at registration). It counts rows per (county_id_fips, place_name) and
re-implements both tests in Python.

- **V1.** No rows have `county_id_fips = '46012'`, so the test as written selects nothing.
- **V2.** Rows with `county_id_fips = '46102'` exist, and all of them have `place_name = 'oglala lakota'`.
  The corrected test passes on today's data.
- **V3.** No `place_name` contains `_`, so the not-in-set test as written returns 0 rows.
- **V4.** `lake st clair` (with NULL `county_id_fips`) and `lake huron` are present. `lake hurron`,
  `bedford city` and `clifton forge city` are absent. The corrected not-in-set test passes.
- **Control C1.** The in-set test at `'46102'` with a wrong expected name (`shannon`) fails on every
  46102 row, so the scoring code does detect failures. **C1b**: the same wrong name at `'46012'`
  still returns 0 rows.
- **Control C2.** The not-in-set test with all four values in space form returns more than 0 rows
  (`lake st clair`).

If C1 or C2 does not hold, the results are not used. Exploratory, no prediction: row and FIPS
counts, NULL-FIPS place names, rows still under the old Shannon code 46113, and FIPS codes with
more than one name.

## Results

Pending: job `vcefips-v1` is queued.
