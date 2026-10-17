# eia860m-slip

Do U.S. generators listed as planned in EIA-860M come online when planned? Do planned retirements happen when planned?

`eia860m-slip` scores every planned operating month and every planned retirement month in the monthly Form EIA-860M as a forecast, against what later reports show happened. Plain Python, standard tests, public data.

Made by MV2 of Munim, Inc. with AI agents. Code: Apache-2.0. Results and data files in `docs/` and `data/`: CC BY 4.0.

## First result: EIA's headline plans against EIA's own actuals, 2020-2026 (0.2.3)

[`docs/headline-plans.md`](docs/headline-plans.md) puts seven years of EIA's start-of-year "developers plan N GW" figures next to what EIA later reported as added, by technology. Every number is in [`data/eia_headline_plans.csv`](data/eia_headline_plans.csv) with its EIA page. `python headline.py` (standard library only) rebuilds the table.

- Over 2020-2024, 79% of the capacity planned at the start of each year was added that year (194 of 245 GW, EIA-860 final figures): 77%, 97%, 67%, 78% and 80%. 2025's first count is 84%; the final 2025 EIA-860 file gives 90% (56.6 of 63 GW).
- Solar fell short every year (51% in 2022 to 87% in 2021) and makes up most of the gap. Wind came to 96% of plan over 2020-2024 and beat it in 2021-2023. Batteries rose from 68% to 82% over 2023-2025 on first counts (90% for 2025 on the final file).
- Until 2022, the "last year" figures in EIA's January articles included additions still scheduled for November and December. 2021 solar went from 15.5 GW at first report to 13.4 GW later. Those early first counts were later revised down by 11-30%; since 2023 first counts have been revised up by 1-9%.
- For 2025 solar, EIA's Short-Term Energy Outlook (26 GW) came closer than the developers' plan (32.5 GW) to EIA's first count (27.2 GW), but not to the final EIA-860 figure (29.5 GW): 3.5 GW under against 3.0 GW over (corrected in 0.2.6).
- Stated in advance: 66.8-72.3 GW added in 2026 against 86 GW planned (63.8-72.3 in 0.2.1, before the 2023 correction), scored when EIA publishes. The 2025 range (55.0-55.5 GW) missed: see the fifth result.

## Second result: planned retirements, 2020-2026 (0.2.3)

[`docs/headline-retirements.md`](docs/headline-retirements.md) does the same for EIA's start-of-year "operators plan to retire N GW" figures, from [`data/eia_headline_retirements.csv`](data/eia_headline_retirements.csv). `python headline.py --retirements` rebuilds it.

- Until 2025, start-of-year retirement plans understated what retired. On EIA's final (EIA-860) figures, 2020-2024 retirements came to 121% of plan in total (98-174% each year). In 2025 only 42% retired (5.1 of 12.3 GW on the final EIA-860 file; 37% on the first count). Additions came in under plan every year.
- Coal retired at or above plan every year from 2020 to 2024: 180%, 206%, 109%, 104% and 172%. In 2025 it was 33% (2.69 of 8.1 GW). EIA attributes the shortfall to emergency orders and delayed or cancelled retirements.
- EIA's first count of what retired was revised up by 11-21% in five of seven comparable cases (2024 coal: -1%; 2025 coal: +3%).
- The same 2.2 GW of California gas plants appear in both the 2020 and the 2023 retirement plans. In 2021, 4.1 GW of the 5.1 GW of planned nuclear retirements reversed course.
- EIA's January 2025 forecast of 11 GW of coal retirements in 2025 was further off than the 8.1 GW plan.
- Stated in advance: the 2026 range from the same rule is 4.1-19.1 GW against about 11 GW planned. The start-of-year retirement figure says little about the year. The 2025 range (5.2-5.5 GW) missed narrowly: see the fifth result.

## Third result: the earlier years, 2016-2019 (0.2.4)

[`docs/headline-2016-2019.md`](docs/headline-2016-2019.md) extends both records back to 2016 (no usable 2017 plan was found), again against EIA-860 final figures. Both CSVs now cover 2016-2026 (no 2017).

- In 2016, 2018 and 2019 the headline additions plans were close: 82.7 GW built against 81.7 GW planned (101%), against 79% in 2020-2024. The shortfall since 2020 is new. Solar beat its small plans in 2018 and 2019 and fell short of its larger plans in every year after.
- Coal retirements met or beat the January plan in every year from 2018 to 2024 (139% pooled; 2019 alone was 287%, 12.9 GW against 4.5 GW). 2025 is the first shortfall in this record.
- The 2016 and 2018 plans were published in March and May, after part of the year was known, so they had a head start; the clean January 2019 plan alone is still 98%.

## Fourth result: why coal misses its plan, and 2026 stated in advance (2026-10-16)

[`docs/coal-plan-misses.md`](docs/coal-plan-misses.md) traces the coal gaps to named decisions, from public documents.

- Overshoot years came from closures decided during the year. In 2019 about 80% of the ~8 GW excess traces to five such decisions (Bruce Mansfield, Gorgas, Hammond, Vistra's Illinois plants). In 2024 about 71% of the excess was one plant, Rush Island. In 2021 most of the excess was retirements already dated to later years and brought forward (Schahfer, G.G. Allen, Gallagher, River Rouge).
- In 2025 every decision made during the year was a deferral: DOE emergency orders (3.2 GW) and voluntary delays (2.2 GW). By EIA's own accounting, no retirement was added during the year.
- In 2026, 4.4 GW (69%) of the 6.4 GW coal plan has already been deferred by name: DOE orders for Campbell, Schahfer, Craig 1 and Culley 2; TVA's Cumberland 2; South Oak Creek 7-8.
- Stated in advance: EIA's first count of 2026 coal retirements will be 0.3-2.5 GW (central 1.3 GW), below 2025's 2.6 GW.

## Fifth result: 2025 scored early on Form EIA-860 (0.2.5)

[`docs/eia860-2025-scored.md`](docs/eia860-2025-scored.md) scores the three 2025 ranges stated in the first two results against the final 2025 Form EIA-860, before the Electric Power Annual 2025 appears. `eia860_final.py` sums the EIA-860 generator file and must first reproduce Table 4.6 for 2023 and 2024; it did, to the printed 0.1 MW in all 16 rows checked.

- All three ranges missed: 2025 additions were 56.6 GW (range 55.0-55.5), solar 29.5 GW (27.9-28.0), retirements 5.11 GW (5.2-5.5). The first count of additions was revised up 6.8%, more than in 2023 or 2024; retirements +11%, less. Two years of revisions were too thin a base. The ranges were written before we read the file, but after EIA had released it.
- 2025 additions were 90% of the January plan, the best year since 2021. Retirements were 42% and coal 33%, still the lowest in the record.
- Stated now: Table 4.6 of the Electric Power Annual 2025 will print 56,609.0 MW of additions, 5,114.4 MW of retirements and 2,688.4 MW of coal retirements (net summer), each within 0.1%. The coal figure counts Prairie Creek 1's blank summer rating as zero. If EIA counts its 14.6 MW nameplate instead, the coal figure misses (see [`docs/coal-rows.md`](docs/coal-rows.md)).

## Sixth result: coal, row by row, and no coal retired in January-August 2026 (2026-10-16)

[`docs/coal-rows.md`](docs/coal-rows.md) checks the fourth result against EIA-860M's own rows (code in [`tools/coal-rows/`](tools/coal-rows/), six predictions written before the run: five held, one missed).

- The row-level plans match EIA's start-of-year coal figures within 13% in all six years tested (2021-2026). Row-level retirements match Table 4.6 within 7% in 6 of 7 years (2018-2024; 2021 is 12% high).
- **As of the August 2026 report, no U.S. coal generator has retired in 2026.** Every year from 2016 to 2025 had coal retirements in January-August. The smallest was 2025, with 793 MW. EIA's Electric Power Monthly Table 6.4 (data for July 2026) lists no coal unit either.
- Of the 6,354 MW in the 2026 coal plan, 44% has been moved out of the year or left undated, and 40% is held open by DOE emergency orders. Only Sherburne County 1 (680 MW) is still dated 2026 with no deferral on record.
- In 2025 only 26% of the December plan's MW retired on time. In every earlier year, 2016-2024, it was 72% or more.
- The eight 2025 coal retirements on the final Form EIA-860 are named. Summer capacity exceeds nameplate (2,688 vs 2,626 MW) because Intermountain 1-2 are rated 900 MW summer against 820 MW nameplate.

## What it does

Every month, EIA-860M lists each planned generator of 1 MW or more with its development stage and its current planned operating month. Operating generators carry a planned retirement month where one has been reported.

For each monthly report, each generator listed as planned with a planned month 0 to 12 months ahead becomes one cohort row. Its outcome is read from later reports:

| outcome | meaning |
|---|---|
| `on_time` | online by the planned month (operating date, or first report that lists it as operating) |
| `late_1_3`, `late_4_6`, `late_7_12` | online 1-3, 4-6 or 7-12 months after the planned month |
| `not_online_12` | not online within 12 months of the planned month |

Shares are capacity-weighted (MW). A planned month is only scored once its outcome window has closed (planned month + 12 months + 2 months of reporting lag at or before the last report in the data). Results are broken down by technology group, development stage at the report, months of lead time (0-2, 3-5, 6-8, 9-12), report year, and group by stage and by year.

Planned retirement months are scored the same way (since 0.2.0): each operating generator with a planned retirement month 0 to 12 months ahead, against the month it retired. A retirement is read from the retirement date in a record that lists the generator as retired, else the first report that lists it as retired, else, for a generator that left EIA-860M while still listed as operating, its last listed month (the count of each kind is reported so a reader can judge that rule).

Two annual tables compare, per calendar year and technology group, the capacity that January's report planned for that year with what came online (or retired) during the year.

## Data

Catalyst Cooperative's PUDL table `core_eia860m__changelog_generators`, one record per change with `report_date` and `valid_until_date`:

https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/core_eia860m__changelog_generators.parquet

The tool downloads it if `--data-dir` holds no parquet file. `eia860_final.py` reads EIA's annual Form EIA-860 zips (https://www.eia.gov/electricity/data/eia860/) and downloads them if `--data-dir` does not hold them.

## Run

```
pip install pandas pyarrow openpyxl
python -m unittest -v test_eia860m_slip test_headline test_eia860_final test_coal25
python eia860m_slip.py --data-dir data --out-dir out
python headline.py
python headline.py --retirements
python eia860_final.py --data-dir data --out-dir out
python coal25.py --data-dir data --out-dir out
cd tools/coal-rows && python -m unittest -v test_coal_rows && python coal_rows.py --data-dir ../../data --out-dir ../../out
```

Outputs: `profile.json` (what the data looks like), `slip.json` and `slip.md` (planned operating months), `retire.json` and `retire.md` (planned retirement months), and the per-row cohort tables as gzipped CSV. `eia860_final.py` writes `eia860_final.json` and `eia860_final.md`; the first run's output is in [`docs/eia860-final-output.md`](docs/eia860-final-output.md) and [`data/eia860_final_2025.json`](data/eia860_final_2025.json). `coal25.py` writes `coal25.md` and `coal25.json`, and `coal_rows.py` writes `coal_rows.md` and `coal_rows.json` plus two CSVs. The first runs are in [`docs/coal25-output.md`](docs/coal25-output.md), [`docs/coal-rows-output.md`](docs/coal-rows-output.md), [`data/coal_retired_generators.csv`](data/coal_retired_generators.csv) and [`data/coal_plan_2026_followup.csv`](data/coal_plan_2026_followup.csv).

The tests for `eia860m_slip.py` run on hand-built changelogs with known outcomes and need pandas; the tests for `eia860_final.py` and `coal25.py` build a small workbook and need pandas and openpyxl. Without them those tests are skipped. `test_headline` needs only the standard library. `tools/coal-rows/` needs pandas and is run from its own folder.

## Status

0.2.6 (2026-10-17, docs only): corrects the 2025 solar STEO comparison in docs/headline-plans.md (point 7), docs/headline-retirements.md (point 7) and this README. It held against EIA's first count but not against the final EIA-860 figure that the same point already gave; no number changed. 2026-10-16 (docs and tools, no release): docs/coal-rows.md, the row-level coal check with `tools/coal-rows/` and `coal25.py`; docs/coal-plan-misses.md gains a 2021 section and a 2026 update (the stated 2026 range is unchanged). 0.2.5 (2026-10-16): `eia860_final.py` and the early scoring of the 2025 ranges (docs/eia860-2025-scored.md); both headline docs note the result. 2026-10-16 (docs only, no release): docs/coal-plan-misses.md, with a 2026 coal retirement range stated in advance. 0.2.4: plans and EIA-860 finals for 2016, 2018 and 2019 (docs/headline-2016-2019.md). 0.2.3: EIA-860 final additions and retirements for 2020-2023 from the archived Electric Power Annual editions, correcting three additions claims and two retirement figures (see the Corrections sections of both docs). 0.2.3 and 0.2.4 were released together. 0.2.2: the retirement headline comparison. 0.2.1: the additions headline comparison. 0.2.0: generator-level code and tests.

The generator-level code has had its first full run on the live PUDL table (report months to August 2026). Its results are not published yet, for two reasons found in that run. First, PUDL gives a generator that is still listed a last `valid_until_date` equal to the last report month, not a blank, so this version counts every still-listed operating generator as having "left EIA-860M". This does not change the retirement shares of closed years, but the count of generators that left is wrong in this version and should not be quoted; the fix is in a later release. Second, some planned generators may change ids between reports, which would make a project look late when it was renamed; a check found that linking renamed units changes the on-time share by less than 0.001 (15 of 1,249 exits link). Generator-level tables will be added under `docs/` once the first fix ships.

## Prior art

EIA's Today in Energy has compared planned and actual additions and retirements for single years, and broke 2025's coal shortfall down by cause. SynMax, OnLocation and Environment America have looked at delayed coal retirements. We found no multi-year, all-technology, lead-time-resolved scoring of EIA-860M planned months as forecasts, no scoring of planned retirement months, no compiled multi-year table of EIA's headline plans (additions or retirements) against its own later actuals, and no row-level split of coal retirements by what EIA's start-of-year inventory said about them. If you know of one, open an issue.

## Licence

Code: Apache License 2.0 (see LICENSE). Result tables and data files under `docs/` and `data/`: CC BY 4.0. PUDL data is CC BY 4.0 (Catalyst Cooperative); EIA data is public domain.
