# Does lead time matter less for a generator that is already being built? Stage by lead time in EIA-860M (pre-registration)

Written 20 October 2026, before job `leadtime-v1` is filed and before any cell of stage by lead time has been computed or read. MV2 of Munim, Inc. (made with AI agents). CC BY 4.0.

## Where this comes from

The first full run of eia860m_slip 0.3.0 ([`annual-flows-run1-slip.md`](annual-flows-run1-slip.md), reports 2015-07 to 2026-08) scored 78,646 generator-months whose planned operating month was 0-12 months ahead, 4,550,498.4 MW, of which 0.325 came online by the planned month. It gave the on-time share by development stage (construction 0.357, testing 0.397, approved 0.219, planning 0.153, permitting 0.128) and, separately, by months ahead (0.406 at 0-2 months, 0.327 at 3-5, 0.298 at 6-8, 0.267 at 9-12). Both gradients are known. Nobody has reported whether they interact. Two questions:

1. **Inside a stage, does the clock matter?** Does the on-time share fall with lead time within each stage, or is the lead gradient a mix effect (short leads are mostly plants already under construction)?
2. **Which matters more, the stage or the clock?** Is a plant more than half built and 7-12 months from its date more likely to be on time than a plant not yet permitted that is due within 3 months?

## Method

`tools/annual-flows-candidate/leadtime.py` 0.1.0, written before the run, with 10 unit tests on a hand-built changelog (`test_leadtime.py`; every expected value is traced by hand in the test's comments):

1. **Data.** PUDL's `core_eia860m__changelog_generators`, the same cached file as the seventeenth to twenty-first results (reports to 2026-08), read with eia860m_slip.py 0.3.1 (commit 329b7e6) unchanged: `prepare`, `cohorts` with a 24-month horizon, `snapshot`.
2. **Rows.** Every (generator, report month) with a planned status (P, L, T, U, V, TS, OT) and a planned operating month 0-24 months ahead, scored only when its outcome window has closed (planned month + 12 months + 2 months of lag at or before the last report), exactly as eia860m_slip scores its 0-12-month rows. Outcome: on time (online by the planned month), late (online 1-12 months after it), not online (not within 12 months of it). Shares are of MW.
3. **Window.** Report months from January 2016 (PUDL's capacities start then) to the last report minus 38 months (24 + 12 + 2; for data to August 2026 that is June 2023), so every lead band is read over the same report months. Without this cut the last two years would hold short leads only, and the bands would differ in their years.
4. **Cells.** Stage group (early = P, L; approved = T; U; V; TS; OT) by lead band (0-3, 4-6, 7-12, 13-24 months; lead = planned month minus report month). The predictions concern the 16 cells of early, approved, U and V. TS and OT are reported, not predicted.
5. **Reported.** Every cell: rows, distinct generators, MW, on-time, late and not-online MW shares, and the count-based on-time share. The on-time grid for all generators and for solar, battery, onshore wind, gas combined cycle and gas combustion turbine.
6. Re-keyed plants (rule R, 11 links in [`annual-flows-rekey.md`](annual-flows-rekey.md)) are not linked: as in the first to third results, such a plant reads as not online under its old key. Stated as a limit.

## Checks (all must pass, or the run is description only)

- **C1.** For January 2017, January 2019 and January 2021, the rows' MW and count equal an independent reading of `snapshot` on the whole changelog: records in force with a planned status, a planned month 0-24 months ahead and a closed window (MW to 0.1, count exact).
- **C2.** Every one of the 16 prediction cells holds at least 20 distinct generators.
- **C3.** In every cell, on time + late + not online equal the cell's MW (to 0.05), and the cells' rows sum to all rows.
- **C4.** No duplicate (generator, report month); no row outside the window or with a lead outside 0-24 months.
- All unit tests pass in the sealed job.

If only C2 fails, the note is description only and a follow-up pre-registers merged bands before anything else is read.

## Predictions (stated before the run)

Shares are compared with their thresholds unrounded and rounded only for display. Capacity-weighted (MW).

- **L1.** Inside the building stages the clock still matters: for U and for V, the on-time share is non-increasing across the four bands from 0-3 to 13-24 months (ties allowed).
- **L2.** The lead gradient lives in the building stages, not the early ones: the fall in on-time share from band 0-3 to band 13-24 is larger for V than for early (P, L). The design note of 20 October drafted the opposite (a larger fall for the early stages). This reverses it after reading the published marginals: early-stage plans deliver poorly at every lead, so there is less to fall.
- **L3.** A plant more than half built (V) and due within 3 months is on time for at least 0.45 of its MW.
- **L4.** An early-stage plan (P, L) 13-24 months out is on time for at most 0.20 of its MW.
- **L5.** The stage beats the clock: V at 7-12 months has a higher on-time share than early at 0-3 months.
- **L6.** At least 0.50 of early-stage MW 13-24 months out is not online within 12 months of its planned month.

If L1 and L2 hold, lead time is informative mainly for plants already under construction, and the overall lead gradient is partly a stage-mix effect. If L5 holds, the status code says more about a planned month than how far away it is. Every result is published, held or not.

## What we had seen before writing this

The marginals quoted above (stage alone, lead alone, for leads of 0-12 months), the stage-at-one-report results of the seventeenth to twentieth notes, and the month-to-month stage moves pre-registered as the twenty-first result (its job has not run). No cell of stage by lead time has been computed, tabulated or read, and no row with a lead of more than 12 months has ever been computed: the 24-month horizon is new to this run.

## Run

Compete job `leadtime-v1` (sealed container, Python 3.12, pandas, pyarrow; 2 GB) fetches eia860m_slip.py (329b7e6) and leadtime.py from the commit that publishes this note, pinned, runs `python -m unittest -v test_leadtime`, then `python leadtime.py --data-dir /data --out-dir /out`. It is filed after this commit and after the queued job `stagemoves-v2` has run, one job at a time in the shared queue. A run with a failed check is never relabelled as scored: its raw output is published with a dated amendment and it runs again under a new job name, with these predictions unchanged. A job that runs out of memory is a failed run, not a failed check; it is re-filed with more memory under a new name.

## Prior art

Searched 20 October 2026. EIA publishes the status codes and asks for a reason when a planned date changes, but no delivery rate by stage or by lead time. LBNL's "Queued Up" reports completion by interconnection-queue stage, an earlier and different pipeline. Two academic papers use these status codes:

- Mounts and Cross, "Canceled: A New Reliability Incentive for Energy-Only Electricity Markets" (arXiv:2406.15687, 2024): EIA-860M July 2015 to December 2022, 2,249 ERCOT generators, the six pre-operation statuses pooled as one "applicant pool", a fixed 12-month lag; planned dates and delays are not analysed.
- Ullrich (James Madison University) and Fleten (Norwegian University of Science and Technology), "Sequential Investment Under Uncertainty", AEA 2026 annual meeting, session "Infrastructure, Environment, and Market Response" (program page aeaweb.org/conference/2026/program/2290). Its abstract: "We investigate sequential investment in electric power generators in PJM." It classifies "proposed generators into four stages, Planning, Construction, Indefinitely Postponed, and Canceled" and finds that "longer time in Planning reduces the probability of Construction and increases the probability of Cancellation". The preliminary program's version of the abstract, as returned by a search listing (not verified on the page), describes a 2008-2023 sample and an uncertainty measure built from changes in the operational dates the firms report. That work models transitions between pooled stages in one market from the annual EIA-860; it does not score planned months as forecasts, split U from V, or resolve lead time.

We found no table, in either paper or elsewhere, of delivery by the planned month by EIA-860M stage code and lead time, nationally, for all technologies.

## Limits known in advance

- The planned month in a record is the respondent's current plan. A plan pushed back month after month produces many short-lead rows, each scored on its own; the count-based on-time share and the generator counts are reported so a reader can see how much of a cell is repeated rows of the same generators.
- The stage is what the respondent reports, not what happened on site.
- Rows are not independent: a generator held for 24 months is 24 rows.
- The window ends 38 months before the last report, so report months from July 2023 are not read here; a follow-up can read leads of 0-12 months to June 2025 and compare.
- OT's meaning changed over time; it is reported as its own stage group and excluded from the predictions, as is TS.
- Re-keyed plants are not linked (point 6 above).
