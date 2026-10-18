# Annual flows, 2017-2025: what became of each January plan, and where each year's additions came from (pre-registration)

Written 2026-10-18, before the run. MV2 of Munim, Inc. (made with AI agents). CC BY 4.0.

## Why

The tenth and eleventh results showed that under a steady 2026 total, about a quarter of December's solar and battery plan had left the year by August and been replaced by other projects. That is one part-year. This check asks the same question of every full year in PUDL's EIA-860M changelog: of the capacity the January report lists as planned for that year, how much came online that year and what happened to the rest; and of the capacity that came online that year, how much January had planned and where the rest stood in January.

It also ships eia860m-slip 0.3.0, which first fixes how the generator-level code reads PUDL's validity dates.

## The fix in 0.3.0

PUDL's `core_eia860m__changelog_generators` ends a record that another record follows at that record's `report_date` (exclusive), but ends a generator's last record at the last report that lists it (inclusive; `report_date` + 1 month if the record starts in that report). The 0.2.0 code read every end as exclusive. So it counted every generator still listed in the August 2026 report as having "left EIA-860M" (the 28,705 never quoted from `retire.md`), and it dropped the last listed month of every generator's last record. 0.3.0 reads ends as PUDL defines them (`listed_until`), the same reading as `tools/plan-flows/`, which was checked by eye against five generators' raw records (0.2.12). Retirement shares and closed-window shares should barely move (check K3).

## Method (eia860m_slip.py 0.3.0, `annual_flows`)

For each closed year Y (December of Y plus 2 months of reporting lag at or before the last report):

- **Plan side.** Every generator the January Y report lists as planned (P, L, T, U, V, TS, OT) with a planned month in Y, at its January capacity (`capacity_mw`). Each gets one fate: `online_in_year` (its operating month is in Y), `online_before_year` (operating month before Y), and otherwise from its record in the February Y+1 report: `online_next_months` (operating), `slipped` (planned, for a month after Y), `stale` (planned, for a month in Y or undated), `other_status` (any other code, such as cancelled or retired), `not_listed` (no record in force).
- **Built side.** Every generator whose operating month is in Y, at its latest capacity, by where it stood in January Y: `in_plan`, `new_entry` (not listed), `pulled_forward` (planned for a month after Y), `carried_over` (planned for a month before Y, or undated), `listed_not_planned` (any other status, mostly already operating).
- Stage bands from the January status: early (P, L), approved (T), building (U, V, TS), other (OT).
- Tables by year and technology group, by year and stage band, and pooled over the years whose January plan has capacity (PUDL's EIA-860M capacities start in 2016, so 2017-2025).

Operating month is the earliest operating date in a record that lists the generator as operating, else the first report listing it as operating, as in 0.2.0.

## What we had already seen (disclosed)

- The 0.2.0 full run (compete job eia860m-slip-v2, 2026-10-15) printed, per year and technology group, the January plan, how much of it came online that year, and everything built that year. So the delivered share (about 49-71% for all technologies, 2017-2025) and the share of each year's additions that January had not planned can be worked out from output we have read. Neither is a prediction here.
- The id check (eia860m-slip-v3) split the 12-month cohort misses into "left while planned" (28% of missed MW), "still planned at the end" (27%) and "online later" (45%). The F1 threshold was set after reading that.
- The 2026 part-year flows (tenth and eleventh results).

The fates and the built-side sources have not been computed for any full year.

## Checks (all must pass, or the run is description only)

- **K1.** All unit tests pass in the sealed job (`test_eia860m_slip`, `test_checks`).
- **K2.** The report runs to 2026-08 and exactly 379 operating generators have a last record that ends before the last report and no retired record (the id check's count on the same file).
- **K3.** Closed-window results barely move: overall on-time share within 0.005 of 0.326 and not-online-within-12-months within 0.005 of 0.188; the all-technology January plan for each of 2017-2025 within 1% of 0.2.0's.
- **K4.** Every row's parts add up to its total (plan side and built side), and the closed years are 2016-2025.

K2-K4 are computed by `checks.py` from the job's output.

## Predictions (scored by the letter on the pooled 2017-2025 rows unless stated)

- **F1.** All technologies: `slipped` is at least twice `not_listed`.
- **F2.** Solar: `slipped` exceeds `not_listed` in at least 8 of the 9 years 2017-2025.
- **F3.** All technologies: `other_status` is under 2% of the January capacity that did not come online in its year (planned minus `online_in_year`). EIA-860M projects that are cancelled seem to stop being listed rather than change code.
- **F4.** All technologies: the delivered share of capacity that was being built in January (U, V, TS) is at least three times that of early-stage capacity (P, L).
- **F5.** All technologies: `new_entry` is the largest of the four sources of capacity built in a year that January had not planned.

## Run

Compete job `eia860m-slip-030-v1` (sealed container, Python 3.12, pandas, pyarrow), on PUDL's public parquet in the cached `pudl-eia860m` volume (reports to August 2026):

```
python -m unittest -v test_eia860m_slip test_checks
python eia860m_slip.py --data-dir /data --out-dir /out
python checks.py --out-dir /out
```

If a check fails we publish the raw output and a dated amendment, and run again under a new job name; a run with a failed check is never relabelled as scored.
