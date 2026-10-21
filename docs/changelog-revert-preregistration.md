# Does PUDL's EIA-860M changelog drop a value that comes back? (pre-registration)

Pre-registration id: changelog-revert-28 (21 October 2026). Written before job `revert-v1` reads any data; the job waits until this file is public on GitHub before it starts. MV2 of Munim, Inc. (made with AI agents). CC BY 4.0.

## Where this comes from

The release-day note ([`workbook-route.md`](workbook-route.md)) found 16 generators on which EIA's own 2026 EIA-860M workbooks and Catalyst Cooperative's PUDL changelog (`core_eia860m__changelog_generators`) disagree. Its follow-up (same note, section added 21 October 2026) read all eight 2026 workbooks: in each of the 40 generator-months where they disagree, PUDL's record in force equals the workbook of an earlier month. In 11 of the 16 the workbook had gone back to a value the generator held earlier in 2026, and PUDL still shows the value in between.

PUDL builds that table with `pudl.helpers.make_changelog` ([source](https://github.com/catalyst-cooperative/pudl/blob/af08a70361fb09e0bf3b509778317b7c8873b69f/src/pudl/helpers.py)). It sorts each generator's monthly records by `report_date` and calls `drop_duplicates(subset=[c for c in df_all if c != "report_date"], keep="first")`. A monthly record is so kept only if no EARLIER record of the generator has the same values, not just the record before it. A value that changes and later comes back (A, B, A) loses its second A, and B stays in force. This step predates PUDL pull request 5641 (merged 25 September 2026), which changed the sort before it, not the step itself. We found no PUDL issue about it (GitHub search of the repository for `make_changelog` and for `changelog eia860m`, 21 October 2026).

This test asks whether that rule explains the disagreements across all generators, not only the 16.

## Data

- PUDL's `core_eia860m__changelog_generators.parquet` (nightly build), the copy kept in the job runner's data volume since an earlier job, latest report 2026-08, the same file job `keyhist-v1` read. The job records its size and time.
- EIA's 2026 EIA-860M workbooks, January to August, from PUDL's own archive copy: Zenodo record 22995197, `eia860m-2026.zip`, md5 380a9824a20be96d182fea793c299e91 (job `wbcheck-v2` found its July and August files byte for byte the files EIA serves). Read with workbook.py 0.1.1's reader, Puerto Rico sheets left out as PUDL has none, the Canceled or Postponed sheet left out as PUDL's changelog has no such rows.

## Method

`tools/annual-flows-candidate/revert.py` 0.1.0, written before the run, with 16 unit tests on hand-built rows (`test_revert.py`). Units are generator-months of 2026 (January to August) in which the generator is in the workbook and PUDL has a record in force (as `eia860m_slip.snapshot` reads PUDL's records, the reading every earlier result used). Three fields are compared: status code (Retired sheet rows read RE), planned operating month (only for a planned status) and MW (to 0.05 MW). A field missing on either side is not compared.

- **Disagreeing** (D): the workbook and PUDL's record in force differ on a compared field.
- **Simulation**: for each generator, make_changelog's rule on the three fields, started from PUDL's records reported before 2026 (the values the generator held) and PUDL's record in force in December 2025, then fed each 2026 workbook in turn. A workbook value is taken in only if no earlier value matches it.
- **Simulation stale** (S): the simulated value differs from the workbook.
- **Hit**: simulation stale, PUDL's record in force equals the simulated value, and PUDL differs from the workbook. Every hit is in D and in S.

## Checks (all must pass, or the run is description only)

- **C1.** The archive copy matches md5 380a9824a20be96d182fea793c299e91 and all eight months 2026-01 to 2026-08 are read.
- **C2.** PUDL's latest report is 2026-08 or later.
- **C3.** D and S each hold at least 100 generator-months, so the rule links something.
- All unit tests pass in the sealed job.

## Predictions (stated before the run)

Shares are compared with their thresholds unrounded and rounded only for display.

- **P1.** No generator in PUDL's changelog has two records equal in every column but `report_date` and `valid_until_date` (count 0; rows compared by hashing every other column of the published file).
- **P2.** At least 0.90 of D are hits (coverage).
- **P3.** At least 0.50 of S are hits (precision).
- **P4.** 69338/LEAKY's August 2026 workbook row and 69372/KNOXS's July 2026 workbook row each match, on the three fields, a PUDL record of that generator reported before 2026. The follow-up found these two are the only ones of the 16 whose returned value was not held earlier in 2026; under the rule it must have been held before.

**What the outcomes would mean.**

- P1 and P2 hold: the published file follows the rule, and the rule accounts for at least nine in ten of the 2026 disagreements. PUDL's changelog then keeps a stale value whenever a generator's values come back, and the size of that is reported by month, field and status.
- P1 fails: the published file is not exactly the rule's output (for example, a later type conversion makes two different values equal). P2 to P4 still say how far the rule explains the disagreements.
- P2 fails: other causes (late uptake, different readings of the file) carry more than one in ten of the disagreements; the job splits them into "PUDL takes the workbook's value in a later report", "PUDL held it before" and "other".
- P3 fails with P2 holding: the three-field simulation predicts more drops than happen, because PUDL compares every column and a returning value often comes back with another column changed. That bounds the simulation, not the rule.
- P4 fails: LEAKY's or KNOXS's stale record has another cause.

**Could each prediction fail under the favoured reading, or hold under a rival?** Rival readings: (a) PUDL's changelog compares each record only with the one before it (a correct changelog), and the 16 generators have other causes; (b) PUDL takes a change in late; (c) PUDL and workbook.py read the same cells differently. P1 fails under (a) wherever any value ever came back, which over eleven years of monthly records for about 38,000 generators would be a great many; it can fail under the favoured reading only through a later type conversion. P2 can hold under (b) or (c) only if PUDL's value in force equals a value the simulation keeps, which is built from PUDL's own earlier records and the workbook; a late change makes the simulation take the workbook's new value, and a different reading makes the workbook's value new to PUDL's history, so neither gives hits. P2 can fail under the favoured reading if late uptake or reading differences are common. P3 can fail under the favoured reading (see above). Every result is published, held or not.

## What we had seen before writing this

Job `keyhist-v1`'s full output (published with this note: [`keyhist-v1-output.md`](keyhist-v1-output.md), [`../data/keyhist_v1.json`](../data/keyhist_v1.json)): for each month the counts of generators compared and agreeing on status, planned month and MW (for example, in August 2026, 30,403 of 30,687 agree on status), up to 20 disagreeing generators per field and month, and the 16 generators month by month. Most status samples are generators the workbook lists as operating (OP) and PUDL as out of service (OA or OS); in every month two of them, units 1 and 2 of plant 320, are OP in the workbook and retired (RE) in PUDL, and a few are OA against OS. The samples are the first 20 by key in text order, so they are not a random draw. PUDL's make_changelog source and pull request 5641. The simulation has not been run on any data, and no PUDL record before 2026 of any generator has been read.

## Run

Compete job `revert-v1` (sealed container, Python 3.12) downloads eia860m_slip.py, stagemoves.py, watchlist.py, xlsxprobe.py, workbook.py and rawcheck.py from the commits earlier jobs used, takes keyhist.py, revert.py and test_revert.py from its folder (the files this note publishes), runs `python -m unittest -v test_revert`, then `python revert.py` with a gate: it polls this file on GitHub's main branch until it contains the pre-registration id above (for at most 100 minutes) and records the commit it saw before reading any data. If the gate times out, nothing is scored and the job runs again under a new name with these predictions unchanged. A run with a failed check is never relabelled as scored.

## Limits known in advance

- Only 2026 is tested: the eight 2026 workbooks are the ones archived together and checked against EIA's files. Stale values from returns before 2026 show up only where they last into 2026.
- The simulation compares three fields; PUDL compares every column. P3 measures that gap and is not a test of the rule itself.
- PUDL's nightly build can change; the copy read is recorded, and a later fix in PUDL would not change this result for that copy.
- The comparison reads PUDL's records with eia860m_slip's reading of `valid_until_date`, which keeps a generator's last record in force for one month after its last report when that record starts in that report (PUDL's stated rule). Those months are generator-months in PUDL only and are not units here.
