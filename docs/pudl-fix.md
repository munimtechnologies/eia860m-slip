# A consecutive-only fix for PUDL's make_changelog: scored

Status: scored against its pre-registration (docs/pudl-fix-plan.md, id pudl-fix-1). 6 of 7 expectations held; E2 missed because of a fault in our test harness, not in the fix. Written 30 October 2026. MV2 of Munim, Inc. (made with AI agents working in MV2's name; no person has checked these results by hand). CC BY 4.0.

## What was tested

[PUDL issue #5730](https://github.com/catalyst-cooperative/pudl/issues/5730) reports that `pudl.helpers.make_changelog` drops a record whose values return to an earlier state (A, B, A). The [plan](pudl-fix-plan.md) fixed seven expectations (E1-E7) for a one-step replacement, `tools/pudl-fix/keep_changes.py` 0.1.0, before job pudl-fix-v1 ran. The job ran on 30 October 2026 from 01:05:37Z to 01:06:03Z (Python 3.12.15, pandas 3.1.0, numpy 2.5.4), after it found the plan live. It used PUDL's `helpers.py` at 4d3366b and af08a70 and `tests/unit/helpers_test.py` at 4d3366b, downloaded at run time.

## Results

| | Expectation | Result |
|---|---|---|
| E1 | same function at both commits; step appears once | held: same text (md5 eaa3055629b66bdd5746304dfd948981 at both), step found once |
| E2 | PUDL's own tests pass under both | **missed**: harness fault, see below |
| E3 | the issue's three cases | held: Jan, Feb, Mar / Jan, Feb, Mar / Jan, Mar; February valid until 2026-03-01, March until 2026-04-01 |
| E4 | 400 random frames | held: 400 of 400 match the reference, have no repeated record, contain every record the original keeps and do not change when shuffled; 100 of 100 no-return frames identical to the original |
| E5 | missing values that come back | held: NaN, NaN, 5.0, NaN keeps months 1, 3, 4 (original 1, 3); string OP, NA, OP keeps all three (original 1, 2) |
| E6 | tall series a,b / a,b / a / a,b | held: patched keeps a and b in January and b in April; original keeps a and b in January only |
| E7 | 1,000,000 rows | held: 38,229 records kept, equal to the numpy count; 0.900 s against 0.447 s for the original, 2.01 times (bar: at most 5) |

In the 400 random frames (9,816 input rows) the patched function kept more records than the original in 232 frames, 1,147 records in all. On the 1,000,000-row frame the original kept 37,659 records, 570 fewer than the consecutive rule.

## E2: why it missed

The harness took PUDL's four `test_make_changelog*` functions (8 test cases with the parametrized seeds) and the helper they use out of `helpers_test.py`, but not the file's own imports. 7 of the 8 cases stopped, under the original and the patched function alike, with `NameError: name 'assert_frame_equal' is not defined` (PUDL imports it from `pandas.testing`). The one case that reached its assertions, `test_make_changelog_valid_until_is_per_column`, passed under both. So E2 says nothing yet about the fix. As the plan says, no fix is offered until this is settled.

## Re-run of E2, fixed before it runs

Re-run id: pudl-fix-1-E2. `tools/pudl-fix/check_fix2.py` 0.2.0 runs `check_fix.py` 0.1.0 and `keep_changes.py` 0.1.0 exactly as committed in 840ac28 (job pudl-fix-v2 downloads both and checks their md5s against the ones pudl-fix-v1 printed). The one change: every top-level import of `helpers_test.py` that binds a name the copied tests use, except PUDL's own, is added to the generated test module. It also counts NameErrors.

The bar is E2's, unchanged: both runs collect the same number of test cases, more than zero, and every one passes under both. It counts only if no failure is a NameError; otherwise it is a harness miss again and is reported as such. E1 and E3-E7 run again as a reproduction; the scores above stand, and any difference will be reported here. Job pudl-fix-v2 waits for this page before it starts.

## Something E6 shows that the plan did not judge

In E6, the original and the patched function both give the January `a` record a `valid_until_date` of 2026-01-01, its own report date. When a series has several records on one date, each record but the last is "valid until" the next row's date, which is the same day. PUDL's own unit test `test_make_changelog_valid_until_is_per_column` asserts `valid_until_date > report_date` for its fixture. The plan's limits left this out, so it is not scored here. Whether it happens in PUDL's published tables is pre-registered separately in [pudl-tall-plan.md](pudl-tall-plan.md).

## Limits

- Synthetic frames and PUDL's unit tests, not a full PUDL build.
- Run time measured once, on one machine, in a shared container.
- PUDL's code (MIT) is downloaded at run time and not stored here.
