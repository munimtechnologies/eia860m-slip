# eia860m-slip

Do U.S. generators listed as planned in EIA-860M come online when planned? Do planned retirements happen when planned?

`eia860m-slip` scores every planned operating month and every planned retirement month in the monthly Form EIA-860M as a forecast, against what later reports show happened. Plain Python, standard tests, public data.

Made by MV2 of Munim, Inc. with AI agents. Code: Apache-2.0. Results and data files in `docs/` and `data/`: CC BY 4.0.

## First result: EIA's headline plans against EIA's own actuals, 2020-2026 (0.2.3)

[`docs/headline-plans.md`](docs/headline-plans.md) puts seven years of EIA's start-of-year "developers plan N GW" figures next to what EIA later reported as added, by technology. Every number is in [`data/eia_headline_plans.csv`](data/eia_headline_plans.csv) with its EIA page. `python headline.py` (standard library only) rebuilds the table.

- Over 2020-2024, 79% of the capacity planned at the start of each year was added that year (194 of 245 GW, EIA-860 final figures): 77%, 97%, 67%, 78% and 80%. 2025's first count is 84%; the final 2025 EIA-860 file gives 90% (56.6 of 63 GW).
- Solar fell short every year (51% in 2022 to 87% in 2021) and makes up most of the gap. Wind came to 96% of plan over 2020-2024 and beat it in 2021-2023. Batteries rose from 68% to 82% over 2023-2025 on first counts (90% for 2025 on the final file).
- Until 2022, the "last year" figures in EIA's January articles included additions still scheduled for November and December. 2021 solar went from 15.5 GW at first report to 13.4 GW later. Those early first counts were later revised down by 11-30%; since 2023 first counts have been revised up by 1-9%.
- For 2025 solar, EIA's Short-Term Energy Outlook (26 GW) came closer than the developers' plan (32.5 GW) to EIA's first count (27.2 GW), but not to the final EIA-860 figure (29.5 GW): 3.5 GW under against 3.0 GW over (corrected in 0.2.6). The seventh result shows that in 2020-2024 the STEO's same-year solar figure was the developers' plan itself, so 2025 is the first year the two can be compared at all.
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

## Seventh result: the January STEO's same-year solar and wind figures were the developers' plan, 2020-2024 (0.2.7)

[`docs/steo-vs-plan.md`](docs/steo-vs-plan.md) puts the Short-Term Energy Outlook's January figure for that year's solar and wind additions beside the developers' plan and the EIA-860 final, 2020-2025, from the archived STEO PDFs (sentences pulled by [`tools/steo-text/`](tools/steo-text/), every figure read twice). Four predictions written before the 2020-2022 editions were read ([`docs/steo-vs-plan-preregistration.md`](docs/steo-vs-plan-preregistration.md)) all held. Data: [`data/steo_vs_plan.csv`](data/steo_vs_plan.csv).

- In January 2020, 2021, 2022 and 2024 the STEO's capacity table implies same-year solar additions of 13.5, 15.4, 21.4 and 36.4 GW; the developers' plans were 13.5, 15.4, 21.5 and 36.4 GW. Wind agreed within 0.3 GW in 2020-2023. The STEO carried the EIA-860M schedule; it was not a second forecast.
- Only three cases depart from the schedule: 2024 wind (STEO 7.0 against 8.2 GW planned; 5.2 added, so the discount helped), 2025 solar (25.7 against 32.5; 29.5 added, so it over-corrected and 2025 is the only year the STEO was under the final) and 2023 solar, where the STEO was above the plan (31.7 against 29.1; 18.9 added).
- Scored against EIA-860 finals over 12 cases: STEO closer in 5, plan in 6, one tie. Mean error for solar 6.0 GW (STEO) against 5.7 GW (plan); for wind 2.3 against 2.2. The plan overshot solar in all six years, the STEO in five.
- The prediction for 2026 missed (scored 18 October 2026). We said the January 2026 STEO's 2026 solar figure would be within 2 GW of the 43.4 GW plan. Its capacity table implies 32.1 GW, 26% below the plan, a deeper discount than 2025's; wind is 9.7 against 11.8 GW. The remaining prediction, that the 2026 final comes in below both, is scored when EIA publishes (late 2027). The ninth result follows both 2026 numbers month by month.

## Eighth result: planned retirement dates for the plants DOE holds open are the order calendar (0.2.9, scored)

[`docs/order-dates.md`](docs/order-dates.md) compares, month by month from May 2025 to August 2026, the planned retirement month EIA-860M gives each generator covered by a DOE 202(c) order with the expiry of the order in force (34 orders, eight plants; [`data/doe_202c_unit_orders.csv`](data/doe_202c_unit_orders.csv)). Code in [`tools/order-dates/`](tools/order-dates/); every generator-month in [`data/order_dates_v2.csv`](data/order_dates_v2.csv). The checks and predictions were published first ([`docs/order-dates-preregistration.md`](docs/order-dates-preregistration.md)). The first run (0.2.8) failed one check because Centralia's generator was listed under a boiler ID; the second run, with only that ID corrected ([`docs/order-dates-amendment.md`](docs/order-dates-amendment.md)), passed all three checks, so the result is scored: three of the four scorable predictions held, one missed, and the fifth waits for the September 2026 report.

- 101 of 126 unit-months (80%) were dated to the exact month the current order expires; 107 (85%) to that month or the next. At Campbell, Eddystone, Craig 1 and Culley 2 it was 95 of 98, and each renewal moved the date three months, to the new expiry.
- No covered generator at any of the eight plants was reported retired while under an order. Schahfer ran ahead of its orders; Wagner 4 (whose orders lift a run-hour limit, not a retirement) is dated 2029.
- Centralia 2 and Stanton 1 carry no planned retirement month at all while under orders, in every report since each plant's first order. Centralia 2 is the unit Washington law required to stop burning coal by the end of 2025.
- The prediction that at least six of the eight plants would change date twice or more missed (four did). The September report (P5: three of the four coal plants dated to the order in force on 30 September) is scored next.
- So 2,570 MW of the 2026 coal plan in EIA-860M (Campbell, Schahfer, Craig 1, Culley 2) is dated by the order calendar, not by an owner's plan, and 1,123 MW more (Centralia 2, Stanton 1) is in no year's plan.

## Ninth result: 2026 solar, month by month, the plan and the STEO still 10 GW apart (0.2.10, scored)

[`docs/plan-path.md`](docs/plan-path.md) follows both of EIA's 2026 solar numbers through the year: the developers' implied 2026 total in every EIA-860M report from November 2025 to August 2026 (added so far plus still planned), and the 2026 figure in every STEO edition from January to October 2026, each edition paired with the report two months earlier. Code in [`tools/plan-path/`](tools/plan-path/); one row per report in [`data/plan_path.csv`](data/plan_path.csv). The checks and predictions were published first ([`docs/plan-path-preregistration.md`](docs/plan-path-preregistration.md)); all three checks passed and 2 of the 5 predictions held.

- **Neither number moved much.** The developers' implied 2026 total stayed between 41.0 and 43.7 GW in all ten reports (41.1 GW in August, 94% of December's). The STEO stayed between 29.1 and 32.0 GW (30.7 GW in October). The gap was 9.3-12.8 GW in every pair; it is 10.4 GW now. We predicted the plan would shrink toward the STEO (P1, P3); it did not.
- **The year is back-loaded.** By August 14.7 GW (36%) was online and 26.5 GW was still scheduled for September-December. The October STEO implies about 16 GW in those months, about 60% of what is scheduled.
- **Missed months are re-dated, not dropped from the year.** In no report was more than 0.21 GW of 2026 solar still planned for a month already past.
- **Wind tracks the plan.** The STEO's 2026 wind figure stayed within 1.2 GW of the developers' implied total in all ten pairs, as in the seventh result.
- The May 2026 STEO raised its whole 2025 solar history by about 9-10 GW without changing its 2026 increment; no reason is given in the table notes.
- Stated in advance: the September report's implied total within 1.5 GW of 41.13 GW and at least 16.0 GW added; EIA's first count of 2026 solar (December report) below 35.9 GW, closer to the STEO than to the plan, and at least 28.0 GW.
- The tenth result splits the steady net total into the projects that left the year and those that joined it.

## Tenth result: under the steady 2026 solar total, a quarter of the plan was replaced (0.2.11, scored)

[`docs/plan-flows.md`](docs/plan-flows.md) follows every solar generator in the December 2025 2026 book (online in 2026 or planned for a 2026 month; 43.65 GW, 537 generators) to the August 2026 report, and splits each month's change into entries, exits and resizes. Code in [`tools/plan-flows/`](tools/plan-flows/); the monthly split in [`data/plan_flows.csv`](data/plan_flows.csv); every generator in [`data/plan_flows_generators.csv`](data/plan_flows_generators.csv). The checks and predictions were published first ([`docs/plan-flows-preregistration.md`](docs/plan-flows-preregistration.md)); all three checks passed and 3 of the 5 predictions held.

- **The steady total is not the same projects.** By August, 10.4 GW (24%) of the December book had left 2026 and 7.9 GW had joined (19% of the August book). The net change, -2.5 GW, is a quarter of the outflow.
- **Leaving mostly means slipping.** 7.6 GW moved to 2027 or later and 2.3 GW dropped out of the inventory; none moved to a cancelled or postponed status code. 0.45 GW left by being reported as already online before 2026.
- **Stage in December predicts the outcome.** Of capacity under construction or complete in December, 3.6% slipped to 2027+ and 1.3% dropped out; of capacity at the earliest stages (planned, approvals pending), 55.5% slipped and 19.2% dropped out. Early-stage projects were 20% of the December book but 64% of what slipped.
- **What remains is mostly being built.** 86% of the December book still planned for 2026 in August was already under construction or complete in December. Under construction is not the same as online by August, though: only 38.5% of it was, so the prediction that 60% would be missed.
- The largest 2026 solar project EIA named in February, Tehuacana Creek 1 (837 MW, Texas), is one of the slips: it is now more than half built but planned for May 2027, at 644.8 MW. Its raw records confirm the name (0.2.12: the five largest movers were checked by eye against PUDL's raw records, and all five match).
- Wind, same reading: 53.5% of the December wind book is online, 20% slipped to 2027+, none dropped out.
- Stated in advance for the September report: at least 0.5 GW of solar leaves for 2027 or later, and the book shrinks.

## Eleventh result: the 2026 battery plan, and batteries beside solar (0.2.12, scored)

[`docs/storage-flows.md`](docs/storage-flows.md) reads EIA-860M's batteries exactly as the tenth result reads solar, following every battery in the December 2025 2026 book (24.28 GW, 263 generators, 1.2% from EIA's 24 GW) to the August 2026 report, and asks whether a battery at a plant with 2026 solar shares that solar's fate. Code in [`tools/plan-flows/`](tools/plan-flows/) (`storage_flows.py`, which reuses `plan_flows.py` unchanged); the monthly split in [`data/storage_flows.csv`](data/storage_flows.csv); every battery in [`data/storage_flows_generators.csv`](data/storage_flows_generators.csv). The checks and predictions were published first ([`docs/storage-flows-preregistration.md`](docs/storage-flows-preregistration.md)); all four checks passed and 4 of the 6 predictions held.

- **The same quarter left the year.** By August 6.0 GW (24.8%) of the December battery book had left 2026 (solar: 24%) and 4.5 GW had joined. 3.65 GW slipped to 2027 or later and 1.88 GW is no longer listed.
- **Batteries are further along than solar.** 39.4% of the December book is online by August (solar: 28.8%), and only 15.0% slipped to 2027+ (solar: 17.5%). We predicted batteries would do worse than solar on both counts; both predictions missed.
- **Stage predicts the outcome again.** Of early-stage capacity (P, L) 40.6% slipped and 23.2% dropped out; of capacity being built, 3.7% slipped.
- **Batteries at solar plants waited for their solar.** 78.6% of battery capacity at a plant with 2026 solar is in the same state as that solar in August (72% without the large both-still-planned group). Not pre-registered: all 19 such batteries that slipped to 2027+ did so with their solar, each to the same month; none slipped alone.
- **EIA's four largest named 2026 batteries** (2,139 MW): none online by August. Lunis Creek (621 MW) left the inventory after the April report; Clear Fork Creek (600 MW) moved to March 2027 with its solar; Bellefield 2 (500 MW) and Tehuacana Creek 1 (418 MW) are planned for December 2026, the latter while its solar has moved to May 2027.
- Stated in advance for the September report: the battery book shrinks, and at least 0.5 GW of batteries comes online.

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

The tool downloads it if `--data-dir` holds no parquet file. `eia860_final.py` reads EIA's annual Form EIA-860 zips (https://www.eia.gov/electricity/data/eia860/) and downloads them if `--data-dir` does not hold them. `tools/steo-text/steo_text.py` downloads archived Short-Term Energy Outlook PDFs from https://www.eia.gov/outlooks/steo/archives/.

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
cd tools/steo-text && python -m unittest -v test_steo_text && pip install pypdf && python steo_text.py --data-dir ../../data --out-dir ../../out jan20 feb20 jan21 feb21 jan22 feb22 jan23 feb23 jan24 jan25 jan26 feb26
cd tools/order-dates && python -m unittest -v test_order_dates && python order_dates.py --data-dir ../../data --out-dir ../../out
cd tools/plan-path && python -m unittest -v test_plan_path && python steo_text.py --data-dir=../../data/steo --out-dir=../../out jan26 feb26 mar26 apr26 may26 jun26 jul26 aug26 sep26 oct26 && python plan_path.py --data-dir ../../data --steo-dir ../../out --out-dir ../../out
cd tools/plan-flows && python -m unittest -v test_plan_flows && python plan_flows.py --data-dir ../../data --out-dir ../../out
cd tools/plan-flows && python -m unittest -v test_storage_flows test_spot && python storage_flows.py --data-dir ../../data --out-dir ../../out && python spot.py --data-dir ../../data --out-dir ../../out
```

Outputs: `profile.json` (what the data looks like), `slip.json` and `slip.md` (planned operating months), `retire.json` and `retire.md` (planned retirement months), and the per-row cohort tables as gzipped CSV. `eia860_final.py` writes `eia860_final.json` and `eia860_final.md`; the first run's output is in [`docs/eia860-final-output.md`](docs/eia860-final-output.md) and [`data/eia860_final_2025.json`](data/eia860_final_2025.json). `coal25.py` writes `coal25.md` and `coal25.json`, and `coal_rows.py` writes `coal_rows.md` and `coal_rows.json` plus two CSVs. The first runs are in [`docs/coal25-output.md`](docs/coal25-output.md), [`docs/coal-rows-output.md`](docs/coal-rows-output.md), [`data/coal_retired_generators.csv`](data/coal_retired_generators.csv) and [`data/coal_plan_2026_followup.csv`](data/coal_plan_2026_followup.csv). `steo_text.py` writes `<edition>.txt` (page text) and `<edition>-capacity.md` (matched sentences); the sentence files from the first two runs are in [`tools/steo-text/output/`](tools/steo-text/output/). `order_dates.py` writes `order_dates.md`, `order_dates.json` and `order_dates.csv`; the two runs are in [`docs/order-dates-output.md`](docs/order-dates-output.md) and [`docs/order-dates-output-v2.md`](docs/order-dates-output-v2.md), [`data/order_dates_v1.csv`](data/order_dates_v1.csv) and [`data/order_dates_v2.csv`](data/order_dates_v2.csv). `plan_path.py` writes `plan_path.md`, `plan_path.json` and `plan_path.csv`; the first run is in [`docs/plan-path-output.md`](docs/plan-path-output.md) and [`data/plan_path.csv`](data/plan_path.csv). `plan_flows.py` writes `plan_flows.md`, `plan_flows.json`, `plan_flows.csv` and `plan_flows_generators.csv`; the first run is in [`docs/plan-flows-output.md`](docs/plan-flows-output.md), [`data/plan_flows.csv`](data/plan_flows.csv) and [`data/plan_flows_generators.csv`](data/plan_flows_generators.csv). `storage_flows.py` writes `storage_flows.md`, `storage_flows.json`, `storage_flows.csv` and `storage_flows_generators.csv`; the first run is in [`docs/storage-flows-output.md`](docs/storage-flows-output.md), [`data/storage_flows.csv`](data/storage_flows.csv) and [`data/storage_flows_generators.csv`](data/storage_flows_generators.csv). `spot.py` prints the raw records of named generators to `spot.md`, `spot.csv` and `spot_named.csv`; the run used here is in [`data/plan_flows_spot.md`](data/plan_flows_spot.md).

The tests for `eia860m_slip.py` run on hand-built changelogs with known outcomes and need pandas; the tests for `eia860_final.py` and `coal25.py` build a small workbook and need pandas and openpyxl. Without them those tests are skipped. `test_headline` and `test_steo_text` need only the standard library (`steo_text.py` itself needs pypdf to run). `tools/coal-rows/`, `tools/order-dates/`, `tools/plan-path/` and `tools/plan-flows/` need pandas; the `tools/` folders are run from their own folder.

## Status

0.2.12 (2026-10-18): the storage-flows check (docs/storage-flows.md), scored: all four pre-registered checks passed; B3, B4, B5 and B6 held, B1 and B2 missed. Adds docs/storage-flows-output.md, data/storage_flows.csv, data/storage_flows_generators.csv and tools/plan-flows/storage_flows.py 0.1.0 (8 unit tests passed in the sealed job storage-flows-v2), two predictions for the September 2026 report stated before it is released, and the plan-flows spot check: tools/plan-flows/spot.py 0.2.0 (6 unit tests passed in the sealed job plan-flows-spot-v2) and its output, data/plan_flows_spot.md; docs/plan-flows.md now gives the result (all five generators match) and confirms Tehuacana Creek 1 by its raw record. 0.2.11 (2026-10-18): the plan-flows check (docs/plan-flows.md), scored: all three pre-registered checks passed; F2, F3 and F4 held, F1 and F5 missed. Adds docs/plan-flows-output.md, data/plan_flows.csv, data/plan_flows_generators.csv and tools/plan-flows/ (plan_flows.py 0.1.0; 10 unit tests passed in the sealed job plan-flows-v1), and two predictions for the September 2026 report stated before it is released. 0.2.10 (2026-10-18): the plan-path check (docs/plan-path.md), scored: all three pre-registered checks passed; P2 and P4 held, P1, P3 and P5 missed. Adds docs/plan-path-output.md, data/plan_path.csv and tools/plan-path/ (plan_path.py 0.1.0 and its own copy of steo_text.py; 11 unit tests passed in the sealed job plan-path-v1), and four predictions for the rest of 2026 stated before the September 2026 EIA-860M is released; also the pre-registration of the plan-flows check (docs/plan-flows-preregistration.md). 0.2.9 (2026-10-18): second run of the order-dates check (docs/order-dates.md) with Centralia's generator ID corrected and nothing else changed; all three pre-registered checks passed, so the result is scored: P1, P2 and P3 held, P4 missed, P5 waits for the September 2026 report. Adds docs/order-dates-output-v2.md, data/order_dates_v2.csv and tools/order-dates/ 0.1.1 (which also lists every generator at each matched plant); its 10 unit tests passed in the sealed job. 2026-10-18 (docs only, no release): the 2026 STEO prediction (P5 in docs/steo-vs-plan.md) is scored and missed; 2026 rows added to data/steo_vs_plan.csv; the January and February 2026 sentence files added to tools/steo-text/output/; corrects the 0.2.7 description of *Today in Energy* 67005's "almost 70 GW" (it is the STEO's own two-year figure, not the developers' schedule). 0.2.8 (2026-10-18): docs/order-dates.md, docs/order-dates-output.md, docs/order-dates-amendment.md, data/order_dates_v1.csv and tools/order-dates/ (EIA-860M planned retirement months against DOE 202(c) order expiries, first run; one pre-registered check failed, so the result was description until the second run). 0.2.7 (2026-10-18): docs/steo-vs-plan.md, data/steo_vs_plan.csv and tools/steo-text/ (the January STEO's same-year solar and wind figures against the developers' plan and the EIA-860 final, 2020-2025; four pre-registered predictions, all held; the pre-registration is published with the result). 0.2.6 (2026-10-17, docs only): corrects the 2025 solar STEO comparison in docs/headline-plans.md (point 7), docs/headline-retirements.md (point 7) and this README. It held against EIA's first count but not against the final EIA-860 figure that the same point already gave; no number changed. 2026-10-16 (docs and tools, no release): docs/coal-rows.md, the row-level coal check with `tools/coal-rows/` and `coal25.py`; docs/coal-plan-misses.md gains a 2021 section and a 2026 update (the stated 2026 range is unchanged). 0.2.5 (2026-10-16): `eia860_final.py` and the early scoring of the 2025 ranges (docs/eia860-2025-scored.md); both headline docs note the result. 2026-10-16 (docs only, no release): docs/coal-plan-misses.md, with a 2026 coal retirement range stated in advance. 0.2.4: plans and EIA-860 finals for 2016, 2018 and 2019 (docs/headline-2016-2019.md). 0.2.3: EIA-860 final additions and retirements for 2020-2023 from the archived Electric Power Annual editions, correcting three additions claims and two retirement figures (see the Corrections sections of both docs). 0.2.3 and 0.2.4 were released together. 0.2.2: the retirement headline comparison. 0.2.1: the additions headline comparison. 0.2.0: generator-level code and tests.

The generator-level code has had its first full run on the live PUDL table (report months to August 2026). Its results are not published yet, for two reasons found in that run. First, PUDL gives a generator that is still listed a last `valid_until_date` equal to the last report month, not a blank, so this version counts every still-listed operating generator as having "left EIA-860M". This does not change the retirement shares of closed years, but the count of generators that left is wrong in this version and should not be quoted; the fix is in a later release. Second, some planned generators may change ids between reports, which would make a project look late when it was renamed; a check found that linking renamed units changes the on-time share by less than 0.001 (15 of 1,249 exits link). Generator-level tables will be added under `docs/` once the first fix ships.

## Prior art

EIA's Today in Energy has compared planned and actual additions and retirements for single years, and broke 2025's coal shortfall down by cause; EIA has also reported the share of planned solar capacity reporting a delay (about 20% in Q3 2025). SynMax, OnLocation and Environment America have looked at delayed coal retirements. EIA's STEO accuracy evaluations cover prices, consumption and production, not capacity additions. Trackers of DOE's 202(c) orders exist (DOE, POWER, State Power Project). Third-party sites label EIA-860M batteries as standalone or solar-paired. We found no multi-year, all-technology, lead-time-resolved scoring of EIA-860M planned months as forecasts, no scoring of planned retirement months, no compiled multi-year table of EIA's headline plans (additions or retirements) against its own later actuals, no row-level split of coal retirements by what EIA's start-of-year inventory said about them, no year-by-year comparison of the STEO's same-year capacity additions with the EIA-860M plan and the EIA-860 final, no month-by-month comparison of EIA-860M planned retirement dates with 202(c) order expiries, no month-by-month record of the year's implied solar total in EIA-860M beside each STEO edition's figure, no generator-level split of that total into projects that slipped, dropped out or joined during the year, and no generator-level tracing of a year's battery plan or test of whether co-located batteries share their solar's schedule. If you know of one, open an issue.

## Licence

Code: Apache License 2.0 (see LICENSE). Result tables and data files under `docs/` and `data/`: CC BY 4.0. PUDL data is CC BY 4.0 (Catalyst Cooperative); EIA data is public domain.
