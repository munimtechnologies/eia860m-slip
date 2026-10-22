# How far back PUDL's EIA-860M changelog keeps stale values (twenty-ninth result)

Status: scored against its pre-registration ([`history-revert-preregistration.md`](history-revert-preregistration.md), id history-revert-29); all checks passed and 4 of 5 predictions held. Scored 22 October 2026. MV2 of Munim, Inc. (made with AI agents working in his name). CC BY 4.0.

## In short

The twenty-eighth result ([`changelog-revert.md`](changelog-revert.md)) found that PUDL's EIA-860M changelog (`core_eia860m__changelog_generators`, built by `pudl.helpers.make_changelog`) drops a generator's monthly record when it equals any earlier record of that generator. So a value that changes and comes back (A, B, A) is lost, and B stays in force. That test covered 2026 only. This one replayed all 134 monthly EIA-860M workbooks in PUDL's own raw archive, July 2015 to August 2026, against PUDL's changelog, with a simulation of the rule fed only EIA's workbooks.

- EIA's workbook and PUDL's record in force disagree on status, planned month or MW in 17,193 of 4,080,451 generator-months. The workbook-fed simulation gives PUDL's value in 15,901 of them (coverage 0.9249).
- The stale values are there in every year from 2016 (at least 56 a year), and they pile up: 9.42 a month in 2017, 283.33 a month in 2025.
- In August 2026, 289 generators carry such a value. In 247 of them EIA's workbook says operating (OP) and PUDL says out of service (OA or OS), on standby (SB) or retired (RE). For 75 the PUDL record in force was reported before 2020, and 23 have disagreed with the workbook in every month since a month before 2020.
- The prediction that failed: coverage of at least 0.80 in every year. It was 0.5160 in 2017, 0.4954 in 2018 and 0.7660 in 2019. In those three years, 459 of the 503 disagreements the simulation misses are of one kind: the workbook's value equals an earlier PUDL record of the same generator, but the simulation does not arrive at PUDL's value. Why is not yet known. A descriptive trace is queued.

## Run

Compete job `history-v1` (sealed container, Python 3.12, 22 October 2026) ran history.py 0.1.0, which passed 13 of 13 unit tests ([`history-v1-unittests.txt`](history-v1-unittests.txt)). Its gate saw the pre-registration live on GitHub at its first check (04:13:10 UTC, commit 889040e) before reading any data. Its last step confirmed that the copies of history.py and test_history.py it ran are byte for byte the published ones (last line of the raw output). Raw output, unchanged: [`history-v1-output.md`](history-v1-output.md), [`../data/history_v1.json`](../data/history_v1.json), by year [`../data/history_v1_years.csv`](../data/history_v1_years.csv), by month [`../data/history_v1_months.csv`](../data/history_v1_months.csv), and every hit generator-month [`../data/history_v1_hits.csv`](../data/history_v1_hits.csv).

Data: PUDL's nightly `core_eia860m__changelog_generators.parquet` (2,631,992 bytes, 224,408 rows, file time 18 October 2026, latest report 2026-08), and EIA's 134 monthly workbooks in 12 yearly zips from PUDL's archive (Zenodo record 22995197), each zip matching the md5 on the record page and in its datapackage.json. The twenty-eighth result read a copy with file time 15 October 2026 and the same size and row count; whether the two copies are byte-identical was not checked.

## Checks

| check | result |
|---|---|
| C1 all 12 zips match a listed md5, every year 2015 to 2026 read, every month readable | passed (12 of 12 zips, 134 months, none unreadable) |
| C2 PUDL's latest report 2026-08 or later | passed (2026-08) |
| C3 each year, at least 0.95 of workbook generator-months have a PUDL record in force | passed (lowest 0.9999) |
| C4 disagreeing and simulated stale generator-months, each at least 100 | passed (17,193 and 28,297) |
| unit tests in the sealed job | passed (13 of 13) |

## Predictions

| prediction | bar | value | held |
|---|---|---|---|
| P1 hits in each year 2016-2025 | at least 50 | lowest 56 (2016) | yes |
| P2 coverage, all months | at least 0.90 | 0.9249 (15,901 of 17,193) | yes |
| P3 precision, all months | at least 0.50 | 0.5619 (15,901 of 28,297) | yes |
| P4 hits per month, 2025 above 2017 | greater | 283.33 against 9.42 | yes |
| P5 coverage in each year 2016-2025 | at least 0.80 | 0.5160 (2017), 0.4954 (2018), 0.7660 (2019); every other year at least 0.9032 | no |

## By year

"PUDL later": a later PUDL record has the workbook's value. "PUDL held before": an earlier PUDL record has it. "Other": neither.

| year | months | generator-months in both | disagree | hits | coverage | PUDL later | PUDL held before | other | hits per month |
|---|---|---|---|---|---|---|---|---|---|
| 2015 | 6 | 144,185 | 5 | 5 | 1.0000 | 0 | 0 | 0 | 0.83 |
| 2016 | 12 | 294,742 | 62 | 56 | 0.9032 | 6 | 0 | 0 | 4.67 |
| 2017 | 12 | 315,212 | 219 | 113 | 0.5160 | 16 | 90 | 0 | 9.42 |
| 2018 | 12 | 327,072 | 438 | 217 | 0.4954 | 16 | 205 | 0 | 18.08 |
| 2019 | 12 | 341,338 | 752 | 576 | 0.7660 | 12 | 164 | 0 | 48.00 |
| 2020 | 12 | 355,183 | 1,295 | 1,184 | 0.9143 | 12 | 99 | 0 | 98.67 |
| 2021 | 12 | 369,193 | 1,507 | 1,411 | 0.9363 | 12 | 84 | 0 | 117.58 |
| 2022 | 12 | 385,223 | 1,810 | 1,739 | 0.9608 | 3 | 68 | 0 | 144.92 |
| 2023 | 12 | 399,449 | 2,333 | 2,253 | 0.9657 | 5 | 75 | 0 | 187.75 |
| 2024 | 12 | 414,833 | 2,774 | 2,667 | 0.9614 | 12 | 95 | 0 | 222.25 |
| 2025 | 12 | 434,022 | 3,611 | 3,400 | 0.9416 | 35 | 176 | 0 | 283.33 |
| 2026 | 8 | 299,999 | 2,387 | 2,280 | 0.9552 | 12 | 95 | 0 | 285.00 |
| all | 134 | 4,080,451 | 17,193 | 15,901 | 0.9249 | 141 | 1,151 | 0 | 118.66 |

## What the outcome means

The predictions note set out in advance how each prediction could fail: if the rule mattered only recently, P1, P4 and P5 fail; if older disagreements have another cause, P2 and P5 fail; if stale values were corrected quickly, P4 fails.

- **P1 and P4 held**, so the rule's stale values reach back to 2016 and build up instead of being corrected quickly. The direct evidence of persistence is in the August 2026 list: 23 generators have disagreed with the workbook in every month since before 2020. P4 alone would not show it, because returns may also simply have become more common.
- **P2 held overall, but it cannot rule out a cause limited to a few older years.** 15,717 of the 17,193 disagreeing generator-months fall in 2020 to 2026. P5 tests exactly that, and it failed in 2017, 2018 and 2019. On the terms fixed in advance, those three years have a source of disagreement besides the rule as the simulation reproduces it.
- **P3 held**, but it measures how far the three-field simulation runs ahead of PUDL's all-column comparison, not the rule itself. The simulation marks 12,396 more stale generator-months than it hits (28,297 less 15,901).

What is known about that other source in 2017 to 2019:

- In no year is any disagreement of the "other" kind. Each disagreement the simulation misses has the workbook's value in a later PUDL record (141 generator-months, all years) or in an earlier one (1,151).
- In 2017 to 2019 the "held before" kind is 459 of the 503 misses. The output lists the first ten per year in month and key order, which is not a random draw ([`history-v1-output.md`](history-v1-output.md)). In those lists the same few plants recur, and units of one plant often appear with their statuses swapped. For example, in August 2017 the workbook has 3075/11 operating (OP) and 3075/12 out of service (OA), while PUDL's records in force, both reported in April 2017, have the reverse.
- A workbook value that equals an earlier PUDL record fits the same drop rule acting on a history where PUDL and the workbook-fed simulation had already parted, for example over a column the simulation does not compare or a different reading of an older layout. It fits other causes too: OP is a value nearly every generator has held at some point. This run does not tell these apart.

## Examples (all in [`../data/history_v1_hits.csv`](../data/history_v1_hits.csv))

- 3084/13, 3895/3, 3921/3, 6174/1 and 6174/2 (285.2 MW together) are operating in EIA's August 2026 workbook. Each has disagreed with PUDL in every month since March 2018. PUDL's record in force, reported in March 2017, shows them out of service (OA).
- 1134/5 (2.8 MW) is on standby (SB) in EIA's August 2026 workbook and has disagreed with PUDL in every month since December 2017. PUDL's record in force, reported in January 2017, shows it operating (OP).

## What it does not show

- The simulation compares three fields, and PUDL compares every column (see P3).
- In 2015-07 to 2016-03 the sheets have no Nameplate Capacity column, so only status and planned month are compared there.
- P2 is strongest where the returning value is unusual. For status the returning value is usually OP, so a different cause of a missed return to OP would also count as a hit.
- The copy of PUDL read is the nightly build with file time 18 October 2026. A later fix in PUDL would not change this result for that copy.
- In 2026, 16 workbook generator-months have no PUDL record in force. They are not units (C3).

## Also written by the job

The job also wrote a consecutive changelog of every generator, built only from EIA's workbooks (2015 to 2026): a row when a generator is first listed, changes on status, planned month, MW or sheet, leaves the workbook, or comes back. It is published separately, with its own notes. Two things in it are not yet explained. One is that 2016 has 27,603 "changed" rows; most are expected to come from April 2016, when the sheets first have a Nameplate Capacity column and MW goes from missing to a value. The other is that 2024 has 313 "back" rows, against 1 to 40 in every other year.

## What it means for this repository

Every earlier eia860m-slip result reads PUDL's changelog, so some of their generator-months carry stale values like these. The per-result count is still to come, from [`../data/history_v1_hits.csv`](../data/history_v1_hits.csv), followed by a dated note on each affected result. This document does not change any earlier result or bar.

The fix suggested in the twenty-eighth result is unchanged: compare each record with the previous record of the same generator, instead of dropping duplicates across the generator's whole history. A short issue for the PUDL maintainers has been drafted and is being held until a person checks and files it.
