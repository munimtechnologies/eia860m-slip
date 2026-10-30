# Plan: an independent check of PUDL pull request #5731, and of the last record's end date

Status: pre-registration, nothing run yet. Pre-registration id: pudl-pr-1. Written 30 October 2026, before job pudl-pr-v1 ran. MV2 of Munim, Inc. (made with AI agents working in MV2's name). CC BY 4.0; the code in tools/pudl-pr/ is Apache-2.0.

## Why

On 30 October 2026 a PUDL maintainer opened [pull request #5731](https://github.com/catalyst-cooperative/pudl/pull/5731), "Keep reverted values in make_changelog", which closes [issue #5730](https://github.com/catalyst-cooperative/pudl/issues/5730). It keeps a report date when the series' snapshot (its set of distinct records on that date) differs from the snapshot on the previous date, and moves the end-date rule into a new helper, `_valid_until`. The PR's own checklist leaves the full ETL, pudl-diff and pytest-ci for later. This plan runs our own checks from [pudl-fix.md](pudl-fix.md) against the PR's code at its head commit, as a second, independent look before it merges. The PR reports the same three counts of empty validity intervals that our job pudl-tall-v1 found ([pudl-tall.md](pudl-tall.md)).

It also tests one rule that neither #5730 nor the PR changes. PUDL defines `valid_until_date` as the end of an interval that does not include it: "The record is valid from the report_date up until but not including the valid_until_date." In [issue #3614](https://github.com/catalyst-cooperative/pudl/issues/3614) (2024) PUDL gave records reported on an entity's last report date a `valid_until_date` one month later for that reason. A series' last record that started earlier and has not changed since is instead valid until the entity's last report date (`report_date_max`), as the PR's `_valid_until` docstring says. Under PUDL's own definition, that record is then not valid on the last date, although the same value was reported then. Searching PUDL's issues for `report_date_max` and for changelog `valid_until` found only #3614, which does not discuss this case.

## What the job runs

`tools/pudl-pr/pr_check.py` 0.1.0 downloads PUDL's `src/pudl/helpers.py` and `tests/unit/helpers_test.py` at the PR head c98ea31c5d7401ca21d47028d6cfda1a8322b856 and at main 4d3366b30d05a4c1c13cd8e88ba9b7b2f9ea6db2. It takes out `_valid_until` and `make_changelog` (PR) and `make_changelog` (main) with ast. It reuses `check_fix.py` 0.1.0 (840ac28) for the random frames, the reference rule and the 1,000,000-row frame, and `check_fix2.py` 0.2.0 (a8926e1) for carrying over the test file's imports; `get_pinned2.py` downloads both and checks their md5s. Then it downloads PUDL's nightly `core_eia860m__changelog_generators` and records its size, md5 and Last-Modified date. It waits for this page to be live before it starts. PUDL's code (MIT) and data (CC BY 4.0) are downloaded at run time and not stored here.

## Expectations, fixed now

- **Gate:** both commits' files download, the functions load, and each of the three PUDL test runs below collects at least one test case with no NameError. If the gate fails, Q1-Q7 and S1 are not scored.
- **Q1 (95%):** every `test_make_changelog*` case at the PR head passes against the PR's function.
- **Q2 (95%):** every `test_make_changelog*` case at main (the 8 that job pudl-fix-v2 ran) passes against the PR's function.
- **Q3 (90%):** at least one `test_make_changelog*` case at the PR head fails against main's function (the PR says its reversion tests fail on main).
- **Q4 (85%):** in all 200 random frames with one record per series and date (100 with values that return, 100 without), the PR keeps exactly the records of check_fix.py's consecutive reference rule, keeps no record twice, and gives the same output when the input rows are shuffled; in all 100 frames without returning values it gives the same rows as main.
- **Q5 (80%):** in all 200 random tall frames (one to three records per series and date), the PR keeps exactly the snapshot reference (a date is kept, with all its distinct records, when its set of records differs from the previous date's set), keeps no record twice, and gives the same output when the input rows are shuffled.
- **Q6 (90%):** no record the PR keeps in those tall frames has a `valid_until_date` on or before its own `report_date`.
- **Q7 (95%):** on the 1,000,000-row frame the PR keeps 38,229 records, the numpy count of consecutive changes. Run times of the PR and of main are reported with no bar.
- **S1 (90%):** under both functions, a series reported OP, OP, OP in January to March 2026 gives one record, "2026-01-01 OP until 2026-03-01"; OP, OA, OA gives "2026-02-01 OA until 2026-03-01" as its last record; and under the PR, OP, OA, OP gives "2026-03-01 OP until 2026-04-01" as its last record.
- **Nightly gate:** the nightly file downloads and has `plant_id_eia`, `generator_id`, `report_date` and `valid_until_date`. If it fails, L1 and L2 are not scored.
- **L1 (85%):** let D be the table's last `report_date`. Among generators reported on D, at least 80% have a last record that started before D (so it is valid until D, not past it). If the table has `report_date_max`, "reported on D" uses it. If not, the count uses only last records that started before the month before D and end on D, against those that start on D; last records that started in the month before D and end on D are reported separately, because without `report_date_max` they can't be told apart from a generator last reported that month.
- **L2 (90%):** the number of generators with a record valid on D (`report_date` <= D < `valid_until_date`) equals the number whose last record starts on D.

Also reported, with no bar: each test run's case names and failures, the rows the PR keeps in the tall frames against the per-value rule of `keep_changes.py`, and three example generators for L1.

## Limits

- The PR head of 30 October 2026; the PR may change before it merges. The nightly build of the day the job runs.
- Synthetic frames and PUDL's unit tests, not a full PUDL build.
- Whether the last-record rule is intended is for PUDL's maintainers; this plan only counts what it does under PUDL's written definition.
- Run time measured once, on one machine, in a shared container.
- Made with AI agents; no person has checked these checks by hand.
