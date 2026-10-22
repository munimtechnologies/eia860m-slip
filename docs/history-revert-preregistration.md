# How far back does PUDL's EIA-860M changelog keep stale values? (pre-registration)

Pre-registration id: history-revert-29 (22 October 2026). Written before job `history-v1` compares any workbook with PUDL; the job waits until this file is public on GitHub before it reads any data. The predictions and their bars were fixed earlier, in [`history-revert-predictions.md`](history-revert-predictions.md) (commit 04fb92c), and are not changed here. MV2 of Munim, Inc. (made with AI agents working in his name). CC BY 4.0.

## Where this comes from

The twenty-eighth result ([`changelog-revert.md`](changelog-revert.md), 4 of 4 predictions held) found that PUDL's EIA-860M changelog (`core_eia860m__changelog_generators`, built by `pudl.helpers.make_changelog`) drops a generator's monthly record when it equals any earlier record of that generator. A value that changes and comes back (A, B, A) is lost, and B stays in force. That test covered January to August 2026 only, and it started its simulation from PUDL's own records before 2026. This test asks the same question for every month PUDL archives, July 2015 to August 2026, with a simulation fed only EIA's workbooks.

## Data

- PUDL's `core_eia860m__changelog_generators.parquet` (nightly build): the copy kept in the job runner's data volume, which jobs `revert-v1` and `layouts-v1` used. The job records its size, file time and latest report.
- EIA's monthly EIA-860M workbooks from PUDL's own raw archive: Zenodo record 22995197 (version 50.0.0), `eia860m-2015.zip` to `eia860m-2026.zip`. Each zip is used only when its md5 matches the record page (the values in `layouts.py`'s `ZIP_MD5`) or the record's `datapackage.json`.

## Method

`tools/annual-flows-candidate/history.py` 0.1.0 (written before the run), with 13 unit tests on hand-built rows and sheets (`test_history.py`). It reuses `layouts.py` 0.1.0 (zips, md5 checks and the sheet reader with its readability rules) and `revert.py` 0.1.0 (the three-field projection, `match`, `classify`, `is_hit`).

- **Sheets read:** every sheet except Canceled or Postponed and the Puerto Rico sheets (`*_PR`), as in the twenty-eighth test. Retired-sheet rows read RE. A key on more than one row keeps its first row.
- **Units:** generator-months in which the generator is in the month's workbook and PUDL has a record in force for that month (`eia860m_slip.snapshot`, the reading every earlier result used).
- **Fields compared:** status code, planned operating month (planned statuses only) and nameplate MW (to 0.05 MW). A field missing on either side is not compared.
- **Disagreeing:** the workbook and PUDL's record in force differ on a compared field.
- **Simulation:** for each generator, make_changelog's rule on the three fields from the first workbook month that lists it, fed only the workbooks. A workbook value is taken in only if no earlier value matches it. No PUDL record is used.
- **Simulation stale:** the simulated value differs from the workbook.
- **Hit:** simulation stale, PUDL's record in force equals the simulated value, and PUDL differs from the workbook (`revert.is_hit`).
- **Scoring:** the shares in P2, P3 and P5 and the comparison in P4 use unrounded counts. P2 and P3 count every month read, July 2015 to August 2026. P1, P4 and P5 use calendar years.

**Two readings differ from `revert.py`.** Both were set from the structure check and PUDL's column map, before any comparison:

1. **MW comes only from a Nameplate Capacity column.** In the 9 months 2015-07 to 2016-03, the sheets have no such column; the reader's fallback picks Net Summer Capacity (MW). PUDL's EIA-860M column map (`src/pudl/package_data/eia860m/column_maps/generator_existing.csv`) leaves `capacity_mw` blank for those months and maps net summer capacity to `summer_capacity_mw`. So in those months MW is missing on both sides and is not compared. Without this, every generator-month of those months would disagree on MW (net summer against nothing), for a reason that has nothing to do with the rule.
2. **PUDL's missing capacity is missing,** not 0 MW (`eia860m_slip.prepare` fills it with 0). In the simulation, a field missing on one side equals only a field missing on the other, because `drop_duplicates` treats NaN as equal to NaN and to nothing else. A record without capacity therefore never removes a later record that has one.

## Checks (all must pass, or the run is description only)

These are the checks fixed in the predictions note, made exact:

- **C1 workbooks.** All 12 zips match a listed md5. Every year 2015 to 2026 has workbooks. Every month found is readable by `layouts.py`'s rules (the rules set before its first run).
- **C2 PUDL.** PUDL's latest report is 2026-08 or later.
- **C3 keys.** In each calendar year read (2015 to 2026), at least 0.95 of the workbook's generator-months have a PUDL record in force.
- **C4 links.** Overall, at least 100 disagreeing generator-months and at least 100 simulated stale generator-months.
- All unit tests pass in the sealed job.

## Predictions (fixed on 22 October 2026, unchanged)

- **P1 reach.** At least 50 hit generator-months in each calendar year 2016 to 2025.
- **P2 coverage.** Over all months, at least 0.90 of disagreeing generator-months are hits.
- **P3 precision.** Over all months, at least 0.50 of simulated stale generator-months are hits.
- **P4 accumulation.** The mean number of hits per month in 2025 is greater than in 2017.
- **P5 every year.** Coverage is at least 0.80 in each calendar year 2016 to 2025.

**Could each prediction fail under the favoured reading, or hold under a rival?** The rivals are: (a) the rule matters only lately (for example, older months rebuilt differently); (b) older disagreements have other causes (reader differences on old layouts, revised workbooks, PUDL fixes for given years); (c) stale values are corrected quickly. P1 and P5 can fail under the favoured reading in a year with few returning values, or where other causes are common. P2 can fail under the favoured reading if reader differences remain in old layouts. P3 can fail under the favoured reading because PUDL compares every column: a value that returns with another column changed is kept by PUDL but counted as stale by the simulation. P4 can fail under the favoured reading if returns were as common in 2017 as in 2025 and a stale value is soon replaced by a value the generator never held before. P2 cannot hold under (b) or (c), because a late or differently read value gives no hit. P1 cannot hold under (a). The full output is published, held or not.

**Outputs besides the verdict:**

- `eia860m_changelog_from_workbooks.csv.gz`: a consecutive changelog built from EIA's own workbooks. It has a row when a generator is first listed, changes on a compared field or its sheet, leaves the workbook, or comes back.
- `history_hits.csv`: every hit generator-month, with the workbook's value, PUDL's stale value, the month PUDL's record was reported and the month the disagreement started.

## What we had seen before writing this

- **Job `layouts-v1`'s full output** (published with this note: [`layouts-v1-output.md`](layouts-v1-output.md)). All 134 monthly workbooks, 2015-07 to 2026-08, are readable by the rules above. The capacity column is Net Summer Capacity in the 9 months 2015-07 to 2016-03. From 2020-11 the header row index moves from 1 to 2. The Puerto Rico sheets start in 2018-03. Every month has one duplicate key. It compared nothing with PUDL.
- **PUDL's column map** for capacity, as above.
- **The twenty-eighth result for 2026.**

No workbook before 2026 has been compared with PUDL, and the simulation has not been run on any data before 2026.

## Run

Compete job `history-v1` (sealed container, Python 3.12) works in this order:

1. It downloads eia860m_slip.py, stagemoves.py, watchlist.py, zenodoprobe.py, xlsxprobe.py, workbook.py and rawcheck.py from the commits earlier jobs used, plus revert.py and keyhist.py from commit f64de4c and layouts.py from commit 04fb92c.
2. It takes history.py and test_history.py from its folder (the files this note publishes).
3. It runs `python -m unittest -v test_history`.
4. It runs `python history.py` with a gate. The gate polls this file on GitHub's main branch until it contains the pre-registration id above, for at most 100 minutes, and records the commit it saw before reading any data. If the gate times out, nothing is scored, and the job runs again under a new name with these predictions unchanged.
5. At the end, it checks that the published history.py and test_history.py equal the run copies.

A run with a failed check is never relabelled as scored.

## Limits known in advance

- The simulation compares three fields; PUDL compares every column. P3 measures that gap and is not a test of the rule itself.
- In 2015-07 to 2016-03, only status and planned month are compared.
- PUDL's nightly build can change. The copy read is recorded, and a later fix in PUDL would not change this result for that copy.
- A generator that leaves the workbook and comes back unchanged has no PUDL record in force (the returning record is dropped). Such generator-months are not units. They are counted separately ("workbook only, of which held before") and lower C3's share.
