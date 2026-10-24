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

**An open month-to-month changelog rebuilt from EIA's own workbooks.** [`data/eia860m_changelog_from_workbooks.csv.gz`](data/eia860m_changelog_from_workbooks.csv.gz) has 117,756 rows from July 2015 to September 2026 (version 0.1.1; version 0.1.0 ended at August 2026). It records a row when a generator is first listed, changes status, planned month, MW or sheet, leaves the workbook, or comes back, and it keeps values that come back. It is preliminary: read the known limits in [`docs/eia860m-changelog-from-workbooks.md`](docs/eia860m-changelog-from-workbooks.md) before using it.

**Each new month, scored on release: September 2026, 3 of 4 held.** [`docs/sep2026-plan.md`](docs/sep2026-plan.md) set four bars for EIA's September 2026 workbook before EIA published it. [`docs/sep2026.md`](docs/sep2026.md) (thirty-first result, scored; 3 of 4 held) scores them: the file read cleanly and listed 0.40% more generators than August's, 20 generators left (at most 50 allowed), and 57 of the 170 generators planned for September were listed as operating in it (0.3353, inside the band fixed in advance). P3 failed: 16 generators left the Retired sheet, at 15 plants, against a bar of fewer than 10; since April 2017 only November 2024 and January 2024 had more.

**The 16 that left are nuclear units retired before 2002.** [`docs/sepretired.md`](docs/sepretired.md) (thirty-second result, scored against [`docs/sepretired-plan.md`](docs/sepretired-plan.md); 1 of 2 held so far, one bar waits for October) finds that all 16 are nuclear units that August 2026's sheet lists as retired between 1972 and 1998, 8,663.1 MW in all, from Maine Yankee to Zion. EIA's page gives the sheet's scope as generators retired since 2002. September's sheet lists none retired before 2002, so the removal brought the sheet back inside that scope; it is not a loss of generators retired since 2002. When these 16 came onto the sheet was pre-registered in [`docs/retiredentry-plan.md`](docs/retiredentry-plan.md) and is scored in the thirty-third result.

**August 2026 added 28 reactors retired before 2002, and September removed them all.** [`docs/retiredentry.md`](docs/retiredentry.md) (thirty-third result, scored; 3 of 4 held) finds that none of the 16 was in any workbook before August 2026, and that August's Retired sheet has 28 nuclear rows retired from 1963 to 1998 (10,446.1 MW), 12 of them with no plant ID, against 16 predicted. September's workbook has none of the 28. Catalyst Cooperative had already documented the August addition (EIA's nuclear shutdown list, as EIA confirmed to PUDL); the full count and the September removal are what this note adds.

**Fewer generators planned for next month are operating in it than ten years ago.** Of the generators EIA-860M listed as planned for the next month, the share listed as operating in that month was 0.469 in 2016-2019 and 0.349 in 2022-2025, by count, and every year from 2021 to 2026 is below every year from 2016 to 2020. In each year from 2016 to 2025, December had the largest such group and a share above its year's. [`docs/nextmonth-share.md`](docs/nextmonth-share.md) (descriptive; it tested nothing in advance) gives the monthly series from August 2015 to August 2026 and its limits: it does not split by technology, so it cannot say why. Whether December keeps its pattern in 2026 is pre-registered in [`docs/dec2026-plan.md`](docs/dec2026-plan.md).

**Most of that fall is inside technologies.** [`docs/nexttech.md`](docs/nexttech.md) (thirty-fourth result, scored against [`docs/nexttech-plan.md`](docs/nexttech-plan.md); 3 of 4 held) splits the share by technology. Solar fell from 0.506 to 0.354 and batteries from 0.442 to 0.299. With the 2016-2019 mix of technologies the share would still have fallen from 0.469 to 0.374, so about 79% of the fall is inside technologies and 21% is the change of mix. T2 failed: gas rose from 0.401 to 0.455, but one plant whose 12 turbines were planned for the next month again and again in 2016-2018 accounts for that, and without it gas is flat. Whether the split holds when each generator counts once is pre-registered in [`docs/nexttechonce-plan.md`](docs/nexttechonce-plan.md).

**Counting each generator once, the split holds, and repeat listings grew.** [`docs/nexttechonce.md`](docs/nexttechonce.md) (thirty-fifth result, scored against [`docs/nexttechonce-plan.md`](docs/nexttechonce-plan.md); 3 of 4 held) keeps only each generator's first planned month in each period. Solar fell from 0.476 to 0.360 and batteries from 0.362 to 0.282, and a little under 70% of the fall is inside technologies. O3 failed: gas rose by 0.057, against a band of 0.05; without the same plant the rise is 0.040. In 2022-2025 a generator was named as planned for the next month in 2.39 monthly reports on average, against 1.94 in 2016-2019, which is part of why the share counted in generator-months fell further. *Corrected on 24 October 2026: the larger number of repeat listings explains under 2% of the generator-month fall (0.002 of 0.120). What made that fall steeper is that repeat listings were on time much less often than before (0.477 to 0.340, against 0.462 to 0.361 for first listings); see the dated update at the end of the note.* Whether a generator's chance of being on time falls with each earlier listing is pre-registered in [`docs/nextcount-plan.md`](docs/nextcount-plan.md).

**After three or more misses, a generator planned for the next month is on time less often.** [`docs/nextcount.md`](docs/nextcount.md) (thirty-sixth result, scored against [`docs/nextcount-plan.md`](docs/nextcount-plan.md); 2 of 3 held) counts, for each next-month listing, the generator's earlier next-month listings since August 2015. In 2022-2025 the share was 0.362 with none, 0.365 with one, 0.357 with two and 0.306 with three or more; the gap between none and three or more was 0.010 in 2016-2019, against 0.056 in 2022-2025, and the gas plant that skews 2016-2019 does not cause that. K2 failed: the share rises by 0.003 from none to one. Generators planned for the next month again right after a one-month slip were on time 0.390 in 2022-2025; those back after a slip of 2-3 months, 0.260, against 0.492 in 2016-2019. Most of the 2022-2025 gap is in gas and wind, at few plants; for solar it is small, and batteries go the other way. These splits were reported, not scored. Whether the pattern holds in the next-month groups of January to August 2026 was pre-registered in [`docs/nextheld-plan.md`](docs/nextheld-plan.md) and is scored in the thirty-seventh result.

**In 2026, the months since the last listing matter most.** [`docs/nextheld.md`](docs/nextheld.md) (thirty-seventh result, scored against [`docs/nextheld-plan.md`](docs/nextheld-plan.md); 3 of 3 held) tests the thirty-sixth result's pattern on the next-month groups of January to August 2026, which that result did not count. Generators planned for the next month again right after a one-month slip were on time 0.347, first listings 0.304, and those back after a slip of 2-3 months 0.249. Generators with 3 or more earlier listings were on time 0.270, but that gap comes from 5 or more earlier listings (0.163) and shrinks to 0.009 when each technology is weighted by its part of those rows; batteries go the other way again. Repeat listings as a whole were on time about as often as first listings (0.308 against 0.304). In 2026 the share depended more on how long ago a generator was last planned for the next month than on how many times it had been. Whether a one-month slip is a good sign within solar and within batteries is pre-registered in [`docs/nextgaptech-plan.md`](docs/nextgaptech-plan.md).

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
| 31 | EIA's September 2026 workbook, scored on release against four bars fixed before it was published (3 of 4 held) | [`sep2026.md`](docs/sep2026.md) |
| 32 | The 16 generators that left the Retired sheet in September 2026 are nuclear units retired before 2002 (1 of 2 held; one bar waits for October 2026) | [`sepretired.md`](docs/sepretired.md) |
| 33 | August 2026 added 28 nuclear reactors retired before 2002 to the Retired sheet for one month (3 of 4 held) | [`retiredentry.md`](docs/retiredentry.md) |
| 34 | Most of the fall in the next-month share is inside technologies: solar and batteries fell, gas did not (3 of 4 held) | [`nexttech.md`](docs/nexttech.md) |
| 35 | Counting each generator once, solar and batteries still fall and most of the fall is inside technologies; gas rises (3 of 4 held) | [`nexttechonce.md`](docs/nexttechonce.md) |
| 36 | After three or more earlier misses, a generator planned for the next month is on time less often, and that gap is new since 2016-2019 (2 of 3 held) | [`nextcount.md`](docs/nextcount.md) |
| 37 | In January to August 2026, generators planned for the next month right after a one-month slip were on time more often than new listings, and those back after a longer slip less often (3 of 3 held) | [`nextheld.md`](docs/nextheld.md) |

Pre-registered, not yet scored: [`dec2026-plan.md`](docs/dec2026-plan.md) (whether December 2026 has the largest next-month group of 2026 and a share above the year's, two bars) and [`oct2026-plan.md`](docs/oct2026-plan.md) (EIA's October 2026 workbook, due 24 November 2026, scored on release against five bars: the four of September and one on nuclear rows retired before 2002). Bar S3 of [`sepretired-plan.md`](docs/sepretired-plan.md) (whether any of the 16 generators that left the Retired sheet in September 2026 is listed again in October 2026) is scored with EIA's October 2026 workbook. Also [`nextgaptech-plan.md`](docs/nextgaptech-plan.md) (whether a one-month slip is a good sign within solar and within batteries, four bars).

The code that will score October 2026, [`tools/annual-flows-candidate/monthrun.py`](tools/annual-flows-candidate/monthrun.py) 0.1.0 (with `wait_eia.py`, which waits for EIA's file), was practised on September 2026 before October's release: it rebuilt the changelog from the archive through July 2026 plus EIA's own August and September files, matched the published changelog's text line for line, and reproduced all ten published September numbers it checks ([`docs/monthrun-practice-v1-output.md`](docs/monthrun-practice-v1-output.md)). EIA's own August 2026 file has the same md5 as the copy in PUDL's archive. This is a check of the code, not a result.

Descriptive follow-ups: [`nextmonth-share.md`](docs/nextmonth-share.md) (the monthly share of generators planned for the next month that are listed as operating in it, August 2015 to August 2026, from the practice run of `monthcheck.py`; its raw report is [`monthcheck-dry-v1-output.md`](docs/monthcheck-dry-v1-output.md) and its data [`data/monthcheck_months_2026-08.csv`](data/monthcheck_months_2026-08.csv); the series to September 2026 is in [`data/monthcheck_months_2026-09.csv`](data/monthcheck_months_2026-09.csv)), [`stage-leadtime-cells.md`](docs/stage-leadtime-cells.md) (which plants fill the stage-by-lead cells), [`workbook-route.md`](docs/workbook-route.md) (building the watchlist from EIA's own workbook on release day), [`watchlist.md`](docs/watchlist.md) (how to read the EIA-860M watchlist tool's editions), and [`heldtrace.md`](docs/heldtrace.md) (where the twenty-ninth result's misses come from, and the November 2024 gap; its later dated updates follow every generator that left the monthly workbook from July 2015 to August 2026, the scope of its Retired sheet, and EIA's annual EIA-860 files).

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
