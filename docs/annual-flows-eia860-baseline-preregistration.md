# Is the 2017 gap in the baseline? The annual EIA-860's own plan against January's EIA-860M plan (pre-registration)

Written 19 October 2026, before job `baseline860-v1` runs and before we read any planned-generator record of the annual EIA-860. MV2 of Munim, Inc. (made with AI agents). CC BY 4.0.

## Where this comes from

[`annual-flows.md`](annual-flows.md) finds that 63.8% of the January 2017 EIA-860M plan came online in 2017 (onshore wind 62.5%). EIA's own count for 2017 ([Today in Energy, 21 June 2018](https://www.eia.gov/todayinenergy/detail.php?id=36513)) says 19.7 of 25.1 GW (78%) and 86% of 6.9 GW of onshore wind. The first pre-registered follow-up ([`annual-flows-eia860.md`](annual-flows-eia860.md)) kept the January plan fixed and dated each generator by the annual EIA-860 instead. That changed almost nothing (63.7%; wind 62.5%), so the outcome definition does not explain the gap. EIA's article also gives the December 2017 EIA-860M as the source of its charts, and its plan as what developers reported on the annual EIA-860.

That leaves the other explanation named in the first pre-registration: **the baseline**. EIA's plan is the annual EIA-860 at the end of 2016, which may hold different projects than the January 2017 EIA-860M, even though the two totals are close (25.1 GW against 26,268.8 MW; 6.9 GW of wind against 6,858.3 MW).

## Method

`tools/annual-flows-candidate/baseline860.py` 0.1.0, written before the run, with 7 unit tests on hand-built tables (`test_baseline860.py`):

1. **January's EIA-860M plan** is unchanged: eia860m_slip 0.3.1 (commit 329b7e6) on the same cached PUDL file (`core_eia860m__changelog_generators`, reports to 2026-08), with rule R, through annual860.py 0.1.1 (commit c55b3c2).
2. **The annual plan for year Y** is every generator that PUDL's `out_eia__yearly_generators` (nightly build current when the job runs) lists in report year Y - 1 with an EIA-860M planned status code (P, L, T, U, V, TS, OT) and a `current_planned_generator_operating_date` in Y. Rows PUDL took from EIA-860M (`data_maturity` `incremental_ytd` or `monthly_update`) are left out, as in annual860 0.1.1. Capacity is that record's `capacity_mw`; technology group as in eia860m_slip.
3. **Outcome**: each annual-plan generator gets annual860's annual class (its earliest operating date in an annual record that lists it as operating): `before`, `in_year`, `next_year`, `later`, `undated` or `never`. `share_in_year` = MW `in_year` / annual-plan MW.
4. **Overlap**: an annual-plan generator is `both` if January's EIA-860M plan for Y has the same key (plant id and generator id, trimmed, any case; a generator re-keyed by rule R counts under either key), else `annual_only`. A January plan generator not in the annual plan is `m_only`.
5. Reported for every year 2017-2025 and technology group: both plans' MW, overlap MW, `share_in_year` for the annual plan and for each overlap part, and EIA-860M's delivered share (`share_860m`, as in `annual-flows.md`). For 2017, the 15 largest generators on each side of the difference, all technologies and onshore wind, are listed by name.

## Checks (all must pass, or the run is description only)

- **D1.** The annual file has all nine columns used (plant id, generator id, report date, status, operating date, capacity, current planned operating date, technology, plant name) and report years 2016-2024.
- **D2.** January's 2017 EIA-860M plan equals `annual-flows.md` to 0.1 MW: 26,268.8 MW, of which onshore wind 6,858.3 MW.
- **D3.** In every row, the annual classes add up to the annual-plan MW, to 0.05 MW.
- **D4.** The 2017 annual plan is between 10,000 and 50,000 MW (a check that the right status and date columns were read, as annual860-v1's missing column showed is needed; it is not set from EIA's figure).
- All unit tests pass in the sealed job.

## Predictions (stated before the run)

Shares are compared with their thresholds unrounded (from MW to 0.1 MW) and rounded only for display.

- **B1.** The 2017 annual plan, all technologies, is within 10% of EIA's 25.1 GW (22,590 to 27,610 MW).
- **B2.** Of the 2017 annual plan, all technologies, at least 0.75 by MW is `in_year`.
- **B3.** Of the 2017 annual plan, onshore wind, at least 0.80 by MW is `in_year`.
- **B4.** At most 0.80 of the 2017 annual plan's onshore-wind MW is also in January's 2017 EIA-860M plan (`both`).
- **B5.** In at least 6 of the 8 years 2017-2024, the annual plan's `share_in_year` (all technologies) is above January's EIA-860M delivered share.

If B1-B3 hold, the rebuilt annual plan reproduces EIA's measure, and the 2017 gap lies in which projects the two plans hold; B4 then says whether they differ in composition for wind, and the named lists show which projects. If B1 fails, our rebuild is not EIA's baseline and B2-B3 say nothing about EIA's figure. B5 asks whether the pattern holds beyond 2017. Every result is published, held or not.

## What we had seen before writing this

annual860-v2's output (the January EIA-860M plan generators with their annual operating dates, every year 2017-2025) and EIA's 2017 article. No planned-generator record of the annual EIA-860 has been read: the earlier jobs looked up only the January EIA-860M plan's own generators, and only for their operating dates.

## Run

Compete job `baseline860-v1` (sealed container, Python 3.12, pandas, pyarrow) fetches eia860m_slip.py from commit 329b7e6 and annual860.py from commit c55b3c2, runs `python -m unittest -v test_baseline860`, then `python baseline860.py --data-dir /data --out-dir /out`. The annual parquet is downloaded inside the job from PUDL's public bucket. A run with a failed check is never relabelled as scored: its raw output is published with a dated amendment and it runs again under a new job name, with these predictions unchanged.

## Limits known in advance

- `current_planned_generator_operating_date` is the planned month the annual report gave at the end of Y - 1. EIA's article may have used an earlier release of the same survey.
- The annual operating date is PUDL's harvested value, the same one used in `annual-flows-eia860.md`, with the same limit: one value per generator, mostly from the annual survey, as later revised.
- Matching is by key only. A generator renumbered between the two surveys counts as `annual_only` on one side and `m_only` on the other.
- For 2024 and 2025, generators that came online after the last annual report year in the data have only EIA-860M records after it, which are left out, so they read `never` rather than `later`. That changes how the part that did not come online in the year splits, not `share_in_year`. B5 uses 2017-2024, as W4 did.
