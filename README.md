# eia860m-slip

Do U.S. generators listed as planned in EIA-860M come online when planned? Do planned retirements happen when planned?

`eia860m-slip` scores every planned operating month and every planned retirement month in the monthly Form EIA-860M as a forecast, against what later reports show happened. Plain Python, standard tests, public data.

Made by MV2 of Munim, Inc. with AI agents. Code: Apache-2.0. Results and data files in `docs/` and `data/`: CC BY 4.0.

## First result: EIA's headline plans against EIA's own actuals, 2020-2026 (0.2.1)

[`docs/headline-plans.md`](docs/headline-plans.md) puts seven years of EIA's start-of-year "developers plan N GW" figures next to what EIA later reported as added, by technology. Every number is in [`data/eia_headline_plans.csv`](data/eia_headline_plans.csv) with its EIA page. `python headline.py` (standard library only) rebuilds the table.

- Total additions came in at 74%, 80% and 84% of the start-of-year plan in 2023, 2024 and 2025. Solar ranged from about 48% (2022) to 87% (2021).
- Wind beat its plan in 2020-2021 and has fallen short since (63% in 2024, under 77% in 2025). Batteries rose from 68% to 82% over 2023-2025.
- Until 2022, the "last year" figures in EIA's January articles included additions still scheduled for November and December. 2021 solar went from 15.5 GW at first report to 13.4 GW later.
- For 2025 solar, EIA's Short-Term Energy Outlook (26 GW) came closer to the 27.2 GW added than the developers' plan (32.5 GW).
- A range for 2026, stated in advance: 64-72 GW added against 86 GW planned. It will be scored against EIA's figure around February 2027.

## Second result: planned retirements, 2020-2026 (0.2.2)

[`docs/headline-retirements.md`](docs/headline-retirements.md) does the same for EIA's start-of-year "operators plan to retire N GW" figures, from [`data/eia_headline_retirements.csv`](data/eia_headline_retirements.csv). `python headline.py --retirements` rebuilds it.

- Retirement plans miss in both directions. Total retirements came in at 87% of plan in 2023, 174% in 2024 (EIA-860 final) and 37% in 2025. Additions came in under plan every year.
- Until 2024, more coal retired than was planned at the start of each year: 207% (2021), 109% (2022), about 121% (2023) and 172% (2024). In 2025 it was 32% (2.6 of 8.1 GW). EIA attributes the shortfall to emergency orders and delayed or cancelled retirements.
- The same 2.2 GW of California gas plants appear in both the 2020 and the 2023 retirement plans. In 2021, 4.1 GW of the 5.1 GW of planned nuclear retirements reversed course.
- EIA's January 2025 forecast of 11 GW of coal retirements in 2025 was further off than the 8.1 GW plan.
- The 2026 range from the same rule is 4.1-19.1 GW against about 11 GW planned. The start-of-year retirement figure says little about the year.

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

The tool downloads it if `--data-dir` holds no parquet file.

## Run

```
pip install pandas pyarrow
python -m unittest -v test_eia860m_slip test_headline
python eia860m_slip.py --data-dir data --out-dir out
python headline.py
python headline.py --retirements
```

Outputs: `profile.json` (what the data looks like), `slip.json` and `slip.md` (planned operating months), `retire.json` and `retire.md` (planned retirement months), and the per-row cohort tables as gzipped CSV.

The tests for `eia860m_slip.py` run on hand-built changelogs with known outcomes and need pandas; without it they are skipped. `test_headline` needs only the standard library.

## Status

0.2.2: the retirement headline comparison. 0.2.1: the additions headline comparison. 0.2.0: generator-level code and tests. The first full run on the live PUDL table is queued, and its tables will be added under `docs/` when they are in. Two checks are planned for that run: the 2025 row of the retirement table should be near EIA's published 12.3 GW planned and 4.6 GW retired in 2025, and its annual additions table should sit close to the actual column of `docs/headline-plans.md`.

## Prior art

EIA's Today in Energy has compared planned and actual additions and retirements for single years. SynMax, OnLocation and Environment America have looked at delayed coal retirements. We found no multi-year, all-technology, lead-time-resolved scoring of EIA-860M planned months as forecasts, no scoring of planned retirement months, and no compiled multi-year table of EIA's headline plans (additions or retirements) against its own later actuals. If you know of one, open an issue.

## Licence

Code: Apache License 2.0 (see LICENSE). Result tables and data files under `docs/` and `data/`: CC BY 4.0. PUDL data is CC BY 4.0 (Catalyst Cooperative); EIA data is public domain.
