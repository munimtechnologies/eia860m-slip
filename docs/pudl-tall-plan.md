# Plan: same-day "valid until" dates in PUDL's forensics entity-resolution tables

Status: pre-registration, nothing counted yet. Pre-registration id: pudl-tall-1. Written 30 October 2026, before job pudl-tall-v1 ran. MV2 of Munim, Inc. (made with AI agents working in MV2's name). CC BY 4.0; the code in tools/pudl-tall/ is Apache-2.0.

## Why

PUDL's `make_changelog` (src/pudl/helpers.py) sets each record's `valid_until_date` to the `report_date` of the next row in its series (the entity's id columns plus `column_name`). The harvesting step that builds PUDL's four `_core_eia__forensics_entity_resolution_*` tables passes it one row per source record, so a series can hold several rows on one report date when EIA's forms disagree. Every such row that survives the de-duplication step, except the last, should then be "valid until" its own report date (rows on the entity's last report date are instead given one more month). Our synthetic check E6 showed exactly this ([pudl-fix.md](pudl-fix.md)). PUDL's own unit test `test_make_changelog_valid_until_is_per_column` asserts `valid_until_date > report_date`, but its fixture has one row per series and date. This plan counts how often it happens in the tables PUDL publishes. It is separate from [issue #5730](https://github.com/catalyst-cooperative/pudl/issues/5730), which is about dropped records.

## What the job runs

`tools/pudl-tall/tall_check.py` 0.1.0 downloads the four tables (boilers, generators, plants, utilities) from PUDL's nightly build at https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/ and records each file's size, md5 and Last-Modified date. The id columns are every column except `report_date`, `valid_until_date`, `column_name`, `record_value`, `entity_occurrences`, `record_occurrences`, `consistent_rate` and `is_candidate`. It waits for this page to be live before it starts. PUDL's data is downloaded at run time and not stored here.

## Expectations, fixed now

- **Gate:** all four files download and read, and each has `report_date`, `valid_until_date`, `column_name` and `record_value`. If the gate fails, nothing below is scored.
- **P1 (80%):** in each of the four tables at least one record has `valid_until_date` equal to its own `report_date`.
- **P2 (90%):** in each table, every record whose `valid_until_date` equals its `report_date` shares its series and report date with at least one other record.
- **P3 (95%):** no record in any table has `valid_until_date` before its `report_date`.

Also reported, with no bar: each table's row count, the share of same-day records, how many series-dates hold more than one row and more than one distinct value, how many same-day records are marked `is_candidate`, and three examples per table.

## Limits

- The nightly build of the day the job runs, not a pinned release; the md5s and dates identify it.
- These are internal tables (the leading underscore), built to explain entity resolution; whether a same-day `valid_until_date` matters to anyone who uses them is a question for PUDL's maintainers, not something this count settles.
- Counts made with AI agents; no person has checked them by hand.
