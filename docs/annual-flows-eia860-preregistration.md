# Why does EIA-860M deliver less of the 2017 plan than EIA's own count? (pre-registration)

Written 19 October 2026, before the job runs and before we read any annual EIA-860 record for it. MV2 of Munim, Inc. (made with AI agents). CC BY 4.0.

## The gap

[`annual-flows.md`](annual-flows.md) follows each January EIA-860M plan to what became of it. For 2017 it finds that 16,750.8 of 26,268.8 MW came online in the year (63.8%), and 4,283.6 of 6,858.3 MW of onshore wind (62.5%). EIA's own count for 2017 ([Today in Energy, 21 June 2018](https://www.eia.gov/todayinenergy/detail.php?id=36513)) says 19.7 of 25.1 GW (78%), and 86% of 6.9 GW of onshore wind. The planned totals are close, so the difference is mostly in what counts as having come online.

There are two candidate explanations:

- **Outcome.** EIA's count uses the annual EIA-860, whose operating dates may be earlier than the operating months EIA-860M shows. A wind farm the annual survey dates to December 2017 could still be "planned for 2018" in EIA-860M's February 2018 report.
- **Baseline.** EIA's baseline is the annual EIA-860 at the end of 2016, so it may hold different projects than the January 2017 EIA-860M, even with a similar total.

This run tests the first one. It keeps the January 2017 EIA-860M plan fixed and changes only the outcome: each generator's operating date as the annual EIA-860 gives it.

## Method

`tools/annual-flows-candidate/annual860.py` 0.1.0, written and unit-tested before the run:

1. The plan side of the annual flows comes from eia860m_slip 0.3.1 (commit 329b7e6, unchanged), the same run as `annual-flows.md`, on the same cached PUDL file (`core_eia860m__changelog_generators`, reports to 2026-08).
2. Each plan generator is looked up in PUDL's `core_eia860__scd_generators` (the annual EIA-860, nightly build of 2026-10-18) by plant id and generator id. The generator id is trimmed and compared in any case. A generator that rule R re-keyed is looked up under its new key.
3. Its **annual operating month** is the earliest `generator_operating_date` in an annual record that lists it as operating (OP, SB, OS, OA).
4. Each plan generator of year Y gets one class: `before`, `in_year`, `next_year` or `later` (annual operating month before Y, in Y, in Y+1, or later); `undated` (listed as operating, never with a date); `never` (in the annual data, never operating); or `not_in_860` (no annual record under its key).
5. `share_860` = MW in `in_year` / planned MW. It is set against `share_860m` = (online in year + rekeyed online) / planned, the delivered share of `annual-flows.md`. Both are reported for every year 2017-2025, by technology group and by EIA-860M fate.

## Checks (all must pass, or the run is description only)

- **C1.** The 2017 plan equals `annual-flows.md` to 0.1 MW: all technologies 26,268.8 MW planned and 16,750.8 MW online in year; onshore wind 6,858.3 MW planned, 4,283.6 MW online in year and 2,236.3 MW slipped.
- **C2.** The annual file has all six columns used (plant id, generator id, report date, status, operating date, capacity) and report years 2017 and 2018.
- **C3.** In every row, the classes add up to the planned MW, to 0.05 MW.
- All unit tests pass in the sealed job.

How many plan generators the annual data matches is reported (`not_in_860`), not gated.

## Predictions (2017; stated before the run)

- **W1.** For the January 2017 onshore-wind plan, `share_860` is at least 0.75.
- **W2.** Of the 2,236.3 MW of 2017 onshore wind that EIA-860M shows as slipped, at least half (by MW) is `in_year` in the annual data.
- **W3.** For all technologies in 2017, `share_860` is at least 0.70.
- **W4.** In at least 7 of the 8 years 2017-2024, all-technology MW `in_year` in the annual data exceeds the MW delivered in EIA-860M.

If W1-W3 hold, the outcome definition explains most of the 2017 gap: EIA-860M's operating months lag the annual survey's. If they fail, the gap is mostly in the baseline, and `annual-flows.md`'s delivered shares stand as a measure of the monthly survey's own plan. Either way the result is published.

## Run

Compete job `annual860-v1` (sealed container, Python 3.12, pandas, pyarrow) fetches eia860m_slip.py from commit 329b7e6, runs `python -m unittest -v test_annual860`, then `python annual860.py --data-dir /data --out-dir /out`. The annual parquet is downloaded inside the job from PUDL's public bucket. If the job reads an EIA-860M file with reports past 2026-08, C1 can fail by its own wording. A run with a failed check is never relabelled as scored: we publish its raw output with a dated amendment and run again under a new job name.

## Limits known in advance

- The annual operating date is what the annual survey reports, possibly revised in later years. The earliest operating record is used, so a later revision to an earlier date counts.
- Matching is by key only. A generator renumbered between the two surveys is `not_in_860`.
- W1-W3 test the outcome side only. The baseline explanation is not tested here.
