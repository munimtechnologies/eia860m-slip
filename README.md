# eia860m-slip

Do U.S. generators listed as planned in EIA-860M come online when planned? Do planned retirements happen when planned? And how reliable are the monthly EIA-860M files, and the open changelog most people read them through?

`eia860m-slip` scores the planned operating and retirement months in the monthly Form EIA-860M as forecasts against what later reports show happened. It also checks the data itself, month by month, against EIA's own workbooks. Plain Python, standard tests, public data. Most later results are pre-registered: the predictions and code are published before the job that scores them runs. Most notes are also checked number by number against the job's raw output by a doc test in this repository.

Made by MV2 of Munim, Inc. with AI agents working in his name. Code: Apache-2.0. Results and data files in `docs/` and `data/`: CC BY 4.0.

This README was shortened on 22 October 2026. The full earlier README (results 1 to 23 in detail, every run command and output file, the version history and the full prior-art notes, as of 20 October 2026) is unchanged in [`README-full-2026-10-20.md`](README-full-2026-10-20.md).

## Start here: the latest findings (October 2026)

**PUDL's EIA-860M changelog keeps stale values.** Catalyst Cooperative's PUDL table `core_eia860m__changelog_generators` drops a generator's monthly record when it equals an earlier record of that generator. So a value that changes and later comes back (A, B, A) is lost and B stays in force.

- [`docs/changelog-revert.md`](docs/changelog-revert.md) (twenty-eighth result, scored; 4 of 4 predictions held) shows the rule and reproduces PUDL's value with it.
- [`docs/history-revert.md`](docs/history-revert.md) (twenty-ninth result, scored; 4 of 5 held) replays all 134 monthly workbooks from July 2015 to August 2026. PUDL's changelog has kept stale values in every year since 2016. EIA's workbook and PUDL's record in force disagree on status, planned month or MW in 17,193 of 4,080,451 generator-months, and a simulation of the rule gives PUDL's value in 15,901 of them.
- [`docs/heldtrace.md`](docs/heldtrace.md) (descriptive) traces the rest. Every stale value is a value EIA once published. The remaining misses come from the same rule applied to all of PUDL's columns. Its dated updates count which columns let a returning value back in.

**EIA's own November 2024 file leaves out 279 generators that the files before and after it list.** The October, November and December 2024 workbooks in PUDL's archive are byte-identical to EIA's own files. 277 of the 279 are on the Retired sheet (retired 2002 to 2014) and 2 move from planned to operating. Together they are 5,543.6 MW of nameplate capacity in December's rows. See the dated update in [`docs/heldtrace.md`](docs/heldtrace.md) and the raw output in [`docs/retiredgap-v1-output.md`](docs/retiredgap-v1-output.md).

**EIA's annual and monthly retired lists differ by plant, not by generator.** EIA-860M's August 2026 Retired sheet lists 2,703 generators retired in 2002 to 2025 (87,678.1 MW) that the annual EIA-860 2025 file lists on no sheet, and every one of them is at a plant the annual file lists on no sheet. EIA documents that rule; [`docs/annualids.md`](docs/annualids.md) (thirtieth result, scored; 2 of 2 held) measures how much it leaves out.

**An open month-to-month changelog rebuilt from EIA's own workbooks.** [`data/eia860m_changelog_from_workbooks.csv.gz`](data/eia860m_changelog_from_workbooks.csv.gz) has 117,110 rows from July 2015 to August 2026. It records a row when a generator is first listed, changes status, planned month, MW or sheet, leaves the workbook, or comes back, and it keeps values that come back. It is preliminary: read the known limits in [`docs/eia860m-changelog-from-workbooks.md`](docs/eia860m-changelog-from-workbooks.md) before using it.

**Each new month, scored on release.** [`docs/sep2026-plan.md`](docs/sep2026-plan.md) set four bars for EIA's September 2026 workbook before EIA published it: the file reads cleanly and lists within 3% as many generators as August's, at most 50 generators leave, fewer than 10 of them leave from the Retired sheet, and the share of generators planned for September that September lists as operating lies between the second lowest and the second highest of the 24 months before. The scored result will be a new note, and the changelog will grow by a month if the first bar holds. Not yet scored.

## All results

Scored results were checked against predictions fixed before the job ran. Descriptive ones tested nothing in advance.

| # | question | note |
|---|---|---|
| 1 | EIA's start-of-year "developers plan N GW" against EIA's own actuals, 2020-2026 | [`headline-plans.md`](docs/headline-plans.md) |
| 2 | Planned retirements against what retired, 2020-2026 | [`headline-retirements.md`](docs/headline-retirements.md) |
| 3 | The earlier years, 2016-2019 | [`headline-2016-2019.md`](docs/headline-2016-2019.md) |
| 4 | Why coal misses its plan, and 2026 stated in advance | [`coal-plan-misses.md`](docs/coal-plan-misses.md) |
| 5 | 2025 scored early on Form EIA-860 | [`eia860-2025-scored.md`](docs/eia860-2025-scored.md) |
| 6 | Coal, row by row; no coal retired in January-August 2026 | [`coal-rows.md`](docs/coal-rows.md) |
| 7 | The January STEO's same-year solar and wind figures were the developers' plan, 2020-2024 | [`steo-vs-plan.md`](docs/steo-vs-plan.md) |
| 8 | Planned retirement dates of plants DOE holds open follow the 202(c) order calendar | [`order-dates.md`](docs/order-dates.md) |
| 9 | 2026 solar month by month: the plan and the STEO still 10 GW apart | [`plan-path.md`](docs/plan-path.md) |
| 10 | Under the steady 2026 solar total, a quarter of the plan was replaced | [`plan-flows.md`](docs/plan-flows.md) |
| 11 | The 2026 battery plan, and batteries beside solar | [`storage-flows.md`](docs/storage-flows.md) |
| 12 | The 2026 natural gas plan, and all four technologies side by side | [`gas-flows.md`](docs/gas-flows.md) |
| 13 | Every DOE 202(c) emergency order of 2025-2026, as one table | [`doe-202c-orders.md`](docs/doe-202c-orders.md) |
| 14 | The plants under order generated a third of their usual output | [`gen-202c.md`](docs/gen-202c.md) |
| 15 | DOE's answers to rehearing requests all came after the orders expired | [`doe-202c-rehearing.md`](docs/doe-202c-rehearing.md) |
| 16 | In court: one order decided and 21 petitions in abeyance | [`doe-202c-court.md`](docs/doe-202c-court.md) |
| 17 | What January's plan delivered, 2017-2025 | [`annual-flows.md`](docs/annual-flows.md) |
| 18 | The annual EIA-860 dates January's plan the same way EIA-860M does | [`annual-flows-eia860.md`](docs/annual-flows-eia860.md) |
| 19 | The 2017 gap is in the baseline; the two surveys' plans hold different projects | [`annual-flows-eia860-baseline.md`](docs/annual-flows-eia860-baseline.md) |
| 20 | What only the annual EIA-860 planned for a year was mostly first listed in EIA-860M during that year | [`annual-flows-eia860-entry.md`](docs/annual-flows-eia860-entry.md) |
| 21 | Planned generators rarely move back a stage, and those that do rarely come online within a year | [`stage-moves.md`](docs/stage-moves.md) |
| 22 | Inside a stage, how far away the planned month is matters little until it is more than a year out | [`stage-leadtime.md`](docs/stage-leadtime.md) |
| 23 | Backward stage moves bunch in the December-March reports; forward moves do not | [`report-months.md`](docs/report-months.md) |
| 24-27 | What became of planned capacity scored "not online", and is any of it a stale key beside a built replacement? (5 of 5 predictions held) | [`stale-keys.md`](docs/stale-keys.md) |
| | Were plans that "never came online" re-filed at the same plant under new generator ids? (4 of 5 held) | [`split-rekey.md`](docs/split-rekey.md) |
| | In which month do the annual EIA-860's plan-only projects enter EIA-860M? (5 of 5 held) | [`entry-timing.md`](docs/entry-timing.md) |
| | Were the annual EIA-860's plan-only generators already in its early release? (0 of 3 held) | [`er-plan.md`](docs/er-plan.md) |
| 28 | PUDL's EIA-860M changelog drops a value that comes back (4 of 4 held) | [`changelog-revert.md`](docs/changelog-revert.md) |
| 29 | How far back PUDL's EIA-860M changelog keeps stale values (4 of 5 held) | [`history-revert.md`](docs/history-revert.md) |
| 30 | Retired generators only the monthly file lists are at plants the annual file no longer lists (2 of 2 held) | [`annualids.md`](docs/annualids.md) |

Pre-registered, not yet scored: [`sep2026-plan.md`](docs/sep2026-plan.md) (EIA's September 2026 workbook against four bars, scored by `tools/annual-flows-candidate/monthcheck.py`).

Descriptive follow-ups: [`stage-leadtime-cells.md`](docs/stage-leadtime-cells.md) (which plants fill the stage-by-lead cells), [`workbook-route.md`](docs/workbook-route.md) (building the watchlist from EIA's own workbook on release day), [`watchlist.md`](docs/watchlist.md) (how to read the EIA-860M watchlist tool's editions), and [`heldtrace.md`](docs/heldtrace.md) (where the twenty-ninth result's misses come from, and the November 2024 gap; its later dated updates follow every generator that left the monthly workbook from July 2015 to August 2026, the scope of its Retired sheet, and EIA's annual EIA-860 files).

Every note says what failed as plainly as what held. Corrections are made openly, in dated sections; old claims are not rewritten silently.

## Data

- Catalyst Cooperative's PUDL table `core_eia860m__changelog_generators` (CC BY 4.0): https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/core_eia860m__changelog_generators.parquet
- EIA's monthly EIA-860M workbooks (public domain): https://www.eia.gov/electricity/data/eia860m/. The data checks also read the copies in PUDL's raw archive (Zenodo record 22995197), each md5-checked.
- The annual Form EIA-860, EIA's Short-Term Energy Outlook archives, DOE's 202(c) order pages and CourtListener's RECAP archive, as each note says.

## Run

```
pip install pandas pyarrow openpyxl
python -m unittest -v
python eia860m_slip.py --data-dir data --out-dir out
```

The root tests include the doc tests (`test_*_doc.py`). Each one checks the numbers in its note against the job's raw output in `docs/` and `data/`. The code for each check is in `tools/` (most of it in `tools/annual-flows-candidate/`), run from its own folder, with its tests. Every command and output file up to the twenty-third result is listed in [`README-full-2026-10-20.md`](README-full-2026-10-20.md#run). Later notes name their code, job and raw output at the top.

## Prior art

EIA's Today in Energy has compared planned and actual additions and retirements for single years. Others have studied delayed coal retirements, DOE's 202(c) orders and the stages of planned generators in one region. We found no multi-year, all-technology scoring of EIA-860M planned months as forecasts. We also found no published month-by-month check of PUDL's EIA-860M changelog against EIA's workbooks, and no open changelog rebuilt from those workbooks that keeps values that come back. The full notes, result by result, are in [`README-full-2026-10-20.md`](README-full-2026-10-20.md#prior-art). If you know of earlier work, please tell us.

## History

The version history up to 20 October 2026 is in [`README-full-2026-10-20.md`](README-full-2026-10-20.md#status). Every later change is described in its commit message.

## Licence

Code: Apache License 2.0 (see LICENSE). Result tables and data files under `docs/` and `data/`: CC BY 4.0. PUDL data is CC BY 4.0 (Catalyst Cooperative); EIA data is public domain.
