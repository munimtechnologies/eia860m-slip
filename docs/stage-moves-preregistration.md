# How do planned generators move between stages from one EIA-860M report to the next? (pre-registration)

Written 20 October 2026, before job `stagemoves-v1` is filed and before any month-to-month stage transition in EIA-860M has been computed or read. MV2 of Munim, Inc. (made with AI agents). CC BY 4.0.

## Where this comes from

The earlier results read a generator's stage at one report: stage in December predicts how much of the 2026 solar, battery and gas books slipped ([`plan-flows.md`](plan-flows.md), [`storage-flows.md`](storage-flows.md), [`gas-flows.md`](gas-flows.md)), and stage in January separates what each year's plan delivered ([`annual-flows.md`](annual-flows.md)); the twentieth result ([`annual-flows-eia860-entry.md`](annual-flows-eia860-entry.md)) reads the stage of a generator's first EIA-860M record. None of them looks at how the stage moves from one monthly report to the next. Two questions:

1. **Backward moves.** How often, and with how much capacity, does a planned generator move to an earlier stage between consecutive reports (being built -> approved or earlier, approved -> earlier)?
2. **What follows.** Does a generator that moved back from being built come online within a year as often as one that stayed being built in the same months? Does it return to being built soon after (a status that flickers)?

## Method

`tools/annual-flows-candidate/stagemoves.py` 0.1.0, written before the run, with 13 unit tests on a hand-built changelog (`test_stagemoves.py`):

1. **Data.** PUDL's `core_eia860m__changelog_generators`, the same cached file as the seventeenth to twentieth results (reports to 2026-08), read with eia860m_slip.py 0.3.1 (commit 329b7e6) unchanged. Re-keyed plants are one generator: the job first runs eia860m_slip's annual flows, and each rule R entry key is renamed to its plan key.
2. **Bands**, as in `entry860.py`: early (P, L), approved (T), building (U, V, TS), operating (OP, SB, OS, OA), other (OT and every other code). Order: early < approved < building.
3. **Step.** For each report month m from January 2016 (PUDL's EIA-860M capacities start in 2016) to the month before the last report: every generator whose record in force in m has an early, approved or building band, and that has a record in force in m + 1. Its move: `forward` (later planned band), `held` (same band), `backward` (earlier planned band), `to_operating`, or `exit_other` (any other status). A generator with no record in force in m + 1 is not a step; it is counted as `left`. MW is the capacity in report m. Records in force are read with eia860m_slip's `snapshot`.
4. **Outcome.** A step is scored for whether its generator is listed as operating in any report m + 1 to m + 12, and only when m + 12 is at or before the last report.
5. **Return.** For each generator's first backward step from building at m with six reports after the move (m + 7 at or before the last report): is it listed as building or operating in any report m + 2 to m + 7?
6. **Path.** For generators first in force after January 2016 whose first band is early and that later reach building: is the generator listed as approved in any report before its first building report? MW is the capacity at that first building report.
7. Reported: steps by year (2016 to 2026) and starting band, MW by move and left; the 2016-2025 matrix of starting band against the band in m + 1; backward shares by technology group; outcome shares by starting band and move; the 15 largest backward steps from building with plant, group, month and status codes; the return and path counts.

## Checks (all must pass, or the run is description only)

- **S1.** For January 2017, January 2020 and January 2024, the steps' MW and count equal an independent reading: generators with an ordered band in `snapshot` at m on the whole re-keyed changelog that are also in `snapshot` at m + 1 (MW to 0.1, count exact).
- **S2.** In every year and starting band, forward + held + backward + to_operating + exit_other equal all steps, in MW (to 0.05) and in count.
- **S3.** Rule R links exactly 11 re-keys, as in [`annual-flows-rekey.md`](annual-flows-rekey.md).
- **S4.** The month-by-month table has one row per generator and month, and every report month from January 2016 to the last report has rows.
- All unit tests pass in the sealed job.

## Predictions (stated before the run)

Shares are compared with their thresholds unrounded and rounded only for display. Capacity-weighted unless said otherwise.

- **M1.** Backward steps are rare: less than 0.02 of the MW of building steps with m in 2016-2025 (all technologies) moves backward.
- **M2.** Backward moves from building are often a flicker: at least 0.25 of the generators (count) whose first backward step from building can be followed for six reports are listed as building or operating again within those six reports.
- **M3.** A backward move is bad news: among building steps with a closed window, the share listed as operating within 12 reports is at least 0.20 lower after a backward step than after a held step.
- **M4.** Approved is often skipped: less than 0.50 of the MW of generators that go from a first early band to building is listed as approved in any report in between.

If M1 holds, backward moves are a small part of the monthly record; M3 says whether they still carry information about the outcome, and M2 whether many are reversed within half a year. M4 says whether the approved code is a stage most projects are reported in, which matters for any reading of EIA-860M's stages as an ordered pipeline. Every result is published, held or not.

## What we had seen before writing this

Each generator's stage at one report, in the published results above. No month-to-month transition of any generator's status has been computed, tabulated or read for this question; the twentieth result's raw output gives only the first-record band of the annual-only generators.

## Run

Compete job `stagemoves-v1` (sealed container, Python 3.12, pandas, pyarrow) fetches eia860m_slip.py (329b7e6) and stagemoves.py with its tests from the commit that publishes this note, runs `python -m unittest -v test_stagemoves`, then `python stagemoves.py --data-dir /data --out-dir /out`. It is filed after this commit. A run with a failed check is never relabelled as scored: its raw output is published with a dated amendment and it runs again under a new job name, with these predictions unchanged.

## Prior art

A web search (20 October 2026) found no EIA, LBNL or academic table of month-to-month EIA-860M status-code transitions, backward moves or their outcomes. EIA's EIA-860M instructions define the codes and ask for a reason when a status changes, but EIA publishes no transition statistics; PUDL publishes the changelog, not transitions. LBNL's "Queued Up" covers interconnection queues, an earlier and different pipeline.

## Limits known in advance

- The stage is what the respondent reports, not what happened on site, and a report that was not updated reads as a held step.
- Some codes changed use over time; every code outside the ordered bands counts as `exit_other`, so a change in their use moves MW between `exit_other` and `left`, not into backward moves.
- A generator renumbered without a rule R link (under 10 MW, or more than three months between keys) reads as `left` under its old key and as a new generator under its new one.
- Steps are not independent: one generator held in building for a year is twelve steps. The return and path counts are per generator.
