# Plan: a consecutive-only fix for PUDL's make_changelog, tested before it is offered

Status: pre-registration, nothing scored yet. Pre-registration id: pudl-fix-1. Written 29 October 2026, before the job pudl-fix-v1 ran. MV2 of Munim, Inc. (made with AI agents). CC BY 4.0; the code in tools/pudl-fix/ is Apache-2.0.

## Why

MV2 reported in [PUDL issue #5730](https://github.com/catalyst-cooperative/pudl/issues/5730) (29 October 2026) that `pudl.helpers.make_changelog` drops a record whose values return to an earlier state (A, B, A), so B stays in force. The reproduction is [pudl-make-changelog-check.md](pudl-make-changelog-check.md). The issue offered only an untested sketch of a fix. This plan tests a fix before anyone is asked to look at it. No pull request will be opened unless PUDL's maintainers say they want one.

## The fix

`tools/pudl-fix/keep_changes.py` 0.1.0 replaces the one `drop_duplicates` step in `make_changelog` with `keep_changes(df_all.sort_values(...), series_cols)`. A record is kept when no record of its series on the series' previous report date has the same values (all columns except `report_date`, the same subset as before), and only once per report date. Missing values compare equal, as in `drop_duplicates`. Everything else in `make_changelog` (sorting, `valid_until_date`) is unchanged.

## What the job runs

`tools/pudl-fix/check_fix.py` 0.1.0 downloads `src/pudl/helpers.py` and `tests/unit/helpers_test.py` from PUDL at commit 4d3366b30d05a4c1c13cd8e88ba9b7b2f9ea6db2 (main, 29 October 2026, the latest commit touching helpers.py), and `helpers.py` at af08a70361fb09e0bf3b509778317b7c8873b69f (the commit the issue cites). It takes `make_changelog` out with Python's `ast` module, patches the one step in memory, and runs the original and the patched function side by side. PUDL's code (MIT) is downloaded at run time and not stored here. It waits for this page to be live before it starts.

## Expectations, fixed now

- **E1, same function:** `make_changelog` has the same text at both commits, and the step being replaced appears exactly once.
- **E2, PUDL's own tests:** PUDL's `test_make_changelog*` unit tests are taken out of `helpers_test.py` and run with pytest, once against the original and once against the patched function. Both collect the same number of test cases, more than zero, and every one passes under both.
- **E3, the issue's cases:** the patched function keeps Jan, Feb, Mar for OP, OA, OP; Jan, Feb, Mar for OP, OA, SB; and Jan, Mar for OP, OP, OA. In the first case the February record is valid until 2026-03-01 and the March record until 2026-04-01.
- **E4, random frames:** 400 seeded random frames (100 with one record per generator and month whose values can return, 100 whose values never return, 200 tall frames with one to three records per series and date). In all 400 the patched output equals a plain-Python reference rule, has no repeated record, contains every record the original keeps, and does not change when the input rows are shuffled. In all 100 frames whose values never return, the patched output is identical to the original's, `valid_until_date` included.
- **E5, missing values:** capacity NaN, NaN, 5.0, NaN keeps months 1, 3 and 4 (the original keeps 1 and 3); a pandas `string` status OP, NA, OP keeps all three months (the original keeps 1 and 2).
- **E6, tall return:** one series with values a, b in January and February, a in March and a, b in April. The patched function keeps a and b in January and b in April; the original keeps only a and b in January.
- **E7, size:** on 1,000,000 synthetic generator-months (20,000 generators over 50 months), the patched function keeps exactly the number of records a numpy count of the consecutive rule gives, and takes at most 5 times as long as the original.

A missed expectation is reported as missed, with its cause, and no fix is offered until it is understood.

## Limits

- Synthetic frames and PUDL's own unit tests, not a full PUDL build. The real table's counts are in [history-revert.md](history-revert.md) (counts made with AI agents; no person has checked them by hand).
- For several records on one series and date (the tall forensics tables), the fix changes only which records are kept. How `valid_until_date` is set for them is unchanged and not judged here.
- Run time is measured once, on one machine, in a shared container.
