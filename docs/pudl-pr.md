# An independent check of PUDL pull request #5731, and of the last record's end date: scored

Status: scored against its pre-registration (docs/pudl-pr-plan.md, id pudl-pr-1). Both gates held and 10 of 10 predictions held. Written 30 October 2026. MV2 of Munim, Inc. (made with AI agents working in MV2's name; no person has checked these checks by hand). CC BY 4.0.

## What ran

The [plan](pudl-pr-plan.md) fixed two gates and ten predictions before job pudl-pr-v1 ran. The job found the plan live on its first poll and ran on 30 October 2026 from 08:26:38Z to 08:27:11Z (Python 3.12.15, pandas 3.1.0, numpy 2.5.4, `tools/pudl-pr/pr_check.py` 0.1.0, with `check_fix.py` 0.1.0 and `check_fix2.py` 0.2.0). It downloaded PUDL's `src/pudl/helpers.py` and `tests/unit/helpers_test.py` at the head of [pull request #5731](https://github.com/catalyst-cooperative/pudl/pull/5731) (c98ea31c5d7401ca21d47028d6cfda1a8322b856; helpers.py md5 e446e9d540f5edaf322763e6a3ea9c14) and at main (4d3366b30d05a4c1c13cd8e88ba9b7b2f9ea6db2; helpers.py md5 f6d8b469c4af94e76c32fb798e3de9c8), and PUDL's nightly `core_eia860m__changelog_generators` (md5 ee7132321f9a882956a515d1632e0b1e, last modified Thu, 29 Oct 2026 06:35:53 GMT).

## Scores

| | Expectation | Result |
|---|---|---|
| Gate | both commits load; each of the three PUDL test runs collects a case with no NameError | held: 17, 8 and 17 cases collected, 0 NameErrors |
| Q1 (95%) | every `test_make_changelog*` case at the PR head passes against the PR | held: 17 of 17 |
| Q2 (95%) | every `test_make_changelog*` case at main passes against the PR | held: 8 of 8 |
| Q3 (90%) | at least one case at the PR head fails against main | held: 6 of 17 fail |
| Q4 (85%) | 200 one-record-per-date frames: consecutive reference, no duplicate, shuffle gives the same output; 100 without returning values same as main | held: 200, 200, 200 of 200; 100 of 100 |
| Q5 (80%) | 200 tall frames: snapshot reference, no duplicate, shuffle gives the same output | held: 200, 200, 200 of 200 |
| Q6 (90%) | no kept record in the tall frames is valid until a date on or before its own report date | held: 0 such records |
| Q7 (95%) | on 1,000,000 rows the PR keeps 38,229 records | held: 38,229 |
| S1 (90%) | the three three-month series give the stated last records | held |
| Nightly gate | the nightly file downloads with the four needed columns | held: 224,408 rows, 39,903 generators |
| L1 (85%) | at least 80% of generators reported on the last date have a last record that started earlier | held: 98.45% (36,710 against 577) |
| L2 (90%) | generators with a record valid on the last date = generators whose last record starts on it | held: 577 = 577 |

## The pull request

- PUDL's own tests: the PR head's eight `test_make_changelog*` functions (17 cases) all pass against the PR, and main's eight cases all pass too. Against main's function, 6 of the PR's 17 cases fail: three of the `test_make_changelog_keeps_reverted_values` cases, `test_make_changelog_multiple_records_per_series_and_date`, `test_make_changelog_reverted_value_in_tall_table` and `test_make_changelog_reverted_value_validity_periods`. This matches the PR's statement that its reversion tests fail on main.
- Random frames: in all 200 one-record-per-date frames (3,723 rows) the PR keeps exactly the records of the consecutive reference rule, and in all 200 tall frames (5,699 rows) exactly the snapshot reference, with no record kept twice, the same output from shuffled input, and no empty or backwards interval. In the tall frames the PR kept 4,573 rows, where a per-value rule (`keep_changes.py`) would keep 3,186; that difference is the snapshot rule at work, and whether it is the right rule is the question the PR itself asks.
- 1,000,000 rows: the PR keeps 38,229 records, the numpy count of consecutive changes; main keeps 37,659, so 570 fewer. Run times (no bar, one run, one CPU in a shared container): main 0.297 s, the PR 9.391 s, 31.62 times main. The consecutive-only fix of [pudl-fix.md](pudl-fix.md) took 2.18 times main in job pudl-fix-v2. On PUDL's real tables this may not matter (the PR's own row counts come from a full run); it is reported because it was measured.
- Row count: the nightly table has 224,408 rows, the same "rows before" figure the PR gives for `core_eia860m__changelog_generators`.

## The last record's end date

PUDL defines the interval as running up to but not including `valid_until_date` ("The record is valid from the report_date up until but not including the valid_until_date", [issue #3614](https://github.com/catalyst-cooperative/pudl/issues/3614), 2024). The PR's `_valid_until` keeps the existing rule for a series' last record: it is "valid until the entity's last report date (``report_date_max``)", or one month past it if the record was itself reported on that date. S1 shows what this does, under main and under the PR alike:

- OP, OP, OP in January to March 2026 gives one record, "2026-01-01 OP until 2026-03-01". OP was reported in March, but under the definition the record is not valid in March.
- OP, OA, OA gives "2026-02-01 OA until 2026-03-01" as its last record, so again nothing is valid in March.
- OP, OA, OP gives "2026-03-01 OP until 2026-04-01" under the PR (main drops this record, the bug of issue #5730), so March is covered only because the value changed that month.

In the nightly table the last `report_date` is 2026-08-01. 36,710 generators have a last record that started before July 2026 and is valid until 2026-08-01; 577 have a last record that starts on 2026-08-01; 709 more have a last record that started in July and is valid until 2026-08-01 (these are counted apart, because without `report_date_max` they can't be told from a generator last reported in July). A point-in-time query for August 2026 (`report_date <= '2026-08-01' < valid_until_date`) returns 577 generators, 1.5% of the 37,287 that the two clear groups put on the August file. By the same rule (not counted here), a generator last reported before August is not covered in its own last reported month either, unless its last record started in that month.

Whether this is intended is for PUDL's maintainers. One reading consistent with #3614 would be to give every series' last record a `valid_until_date` one month after `report_date_max`, not only records reported on that date. Searching PUDL's issues and pull requests for `valid_until_date` found 7 results, and for `report_date_max` only #3614; none discusses this case.

## Limits

- The PR head of 30 October 2026 (c98ea31); the PR may change before it merges. The nightly build of 29 October 2026, built from main, not from the PR.
- Synthetic frames and PUDL's unit tests, not a full PUDL build. One timing run.
- The nightly table has no `report_date_max`, so "reported on the last date" is inferred from `valid_until_date`, as the plan fixed.
- PUDL's code (MIT) and data (CC BY 4.0) were downloaded at run time and are not stored here.
- Made with AI agents; no person has checked these checks by hand.
