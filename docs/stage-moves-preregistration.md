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

## Amendment, 20 October 2026 (before the job ran; no EIA-860M data read)

The unit tests had not yet been run anywhere. Re-counting the hand-built changelog by hand before filing the job showed that three tests expected one building step too few for two of the test generators. 2/B is building from June 2016 to May 2017 (12 steps, 7 of them in 2016), and 3/C from May 2016 to May 2017 (13 steps, 8 in 2016). The tests had counted 11 and 12 (6 and 7 in 2016). This commit corrects only those expected values in `test_stagemoves.py`:

- `test_matrix`, building in 2016: 24 steps, 1,110 MW, 900 MW held, backward share 0.0901 (was 22, 1,040, 830 and 0.0962).
- `test_pooled_and_groups`, building: 1,460 MW of steps, 1,250 MW still building (was 1,390 and 1,180); battery building steps 260 MW (was 240).
- `test_predictions`, M1 on the test data: 0.0685 (was 0.0719).

`stagemoves.py` is unchanged (still commit a059121, 0.1.0), and so are the checks, the predictions and their thresholds. Job `stagemoves-v1` fetches eia860m_slip.py (329b7e6) and stagemoves.py (a059121) pinned. It runs the corrected `test_stagemoves.py` from its own working folder, which is the same file as the one in this commit. That file is supplied with the job because the job can start before this commit lands. If the corrected tests still fail in the job, the run counts as a failed check under the rule above.

## Amendment 2, 20 October 2026 (job never started; no EIA-860M data read)

Job `stagemoves-v1` asked for 3 GB of memory. It was queued at 06:28 UTC and had still not started at about 09:10 UTC, because the shared compute hosts start a job only when its memory plus a 2 GB reserve is free, and no host had 5 GB free. Earlier jobs on the same cached changelog ran in 1 to 2 GB (`plan-flows-v1` in 1 GB; `storage-flows-v2`, `rekey-v1` and `flows-diag-v3` in 2 GB). So the run is re-filed as job `stagemoves-v2` with 2 GB, which replaces `stagemoves-v1` in the queue. Nothing else changes: the same pinned eia860m_slip.py (329b7e6) and stagemoves.py (a059121), the same `test_stagemoves.py` (an identical copy, supplied in the job's working folder), the same data file and data key, and the same checks, predictions and thresholds. If the job runs out of memory, that is a failed run, not a failed check. It is re-filed with more memory under a new name, with the predictions unchanged. The scored result will name the job that actually produced it.

## Prior art

A web search (20 October 2026) found no EIA, LBNL or academic table of month-to-month EIA-860M status-code transitions, backward moves or their outcomes. EIA's EIA-860M instructions define the codes and ask for a reason when a status changes, but EIA publishes no transition statistics; PUDL publishes the changelog, not transitions. LBNL's "Queued Up" covers interconnection queues, an earlier and different pipeline.

## Prior art, added 20 October 2026 (job still queued; no EIA-860M data read)

Two papers found later the same day, before the job ran, come closer than anything above; neither changes the method, checks or predictions:

- Mounts and Cross, "Canceled: A New Reliability Incentive for Energy-Only Electricity Markets" (arXiv:2406.15687, 2024): EIA-860M July 2015 to December 2022, 2,249 ERCOT generators. It pools the six pre-operation statuses as one "applicant pool" and says the authors "cannot confidently determine when a unit enters or exits any of the six applicant pool stages that precede operation", so it tracks the pool's size, entry and exit, not moves between stages.
- Ullrich (James Madison University) and Fleten (Norwegian University of Science and Technology), "Sequential Investment Under Uncertainty", AEA 2026 annual meeting, session "Infrastructure, Environment, and Market Response" (aeaweb.org/conference/2026/program/2290). From its abstract: "We investigate sequential investment in electric power generators in PJM"; it classifies "proposed generators into four stages, Planning, Construction, Indefinitely Postponed, and Canceled" and finds that "longer time in Planning reduces the probability of Construction and increases the probability of Cancellation". That is a model of transitions between pooled stages (Planning = P, L, T; Construction = U, V, TS) in one market from the annual EIA-860, with no backward moves, no month-to-month resolution and no outcome after a move.

This note reads each generator's stage in every monthly report and counts the moves between three ordered bands, nationally, 2016 to 2026, including the moves backward and what follows them.

## Limits known in advance

- The stage is what the respondent reports, not what happened on site, and a report that was not updated reads as a held step.
- Some codes changed use over time; every code outside the ordered bands counts as `exit_other`, so a change in their use moves MW between `exit_other` and `left`, not into backward moves.
- A generator renumbered without a rule R link (under 10 MW, or more than three months between keys) reads as `left` under its old key and as a new generator under its new one.
- Steps are not independent: one generator held in building for a year is twelve steps. The return and path counts are per generator.
