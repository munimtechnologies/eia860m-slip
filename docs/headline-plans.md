# How much of EIA's start-of-year planned capacity gets built? 2020-2026, from EIA's own numbers

MV2 of Munim, Inc., 15 October 2026. Made with AI agents. Text and table: CC BY 4.0. Code (`headline.py`): Apache-2.0.

Every January or February, EIA's *Today in Energy* says how many gigawatts of new utility-scale capacity developers plan to bring online that year. The figures come from EIA's Preliminary Monthly Electric Generator Inventory (EIA-860M) and are reported widely as "a record N GW this year". This note puts seven years of those headline plans next to what EIA itself later reported as added, technology by technology. Every number is in [`data/eia_headline_plans.csv`](../data/eia_headline_plans.csv), along with the EIA page it comes from and the words it rests on. `python headline.py` rebuilds the table below from that file.

This is the headline-level companion to the generator-level study in this repo (`eia860m_slip.py`), which scores every planned month in EIA-860M. That run is still waiting for compute. When it lands, its annual table gives a third, independent "actual" for each row here.

## Table

The actual is the most final figure EIA has stated: the Electric Power Annual (Form EIA-860) where it exists, else a later article, else the first article after the year. "~" marks a value derived from the article (for example, a stated percentage change) or one that EIA built partly from scheduled additions. "<" marks a bound.

| year | technology | planned GW | actual GW | actual from | actual / plan |
|---|---|---|---|---|---|
| 2020 | total | 42 |  |  |  |
| 2020 | solar | 13.5 | 11.7 | actual_first | ~87% |
| 2020 | wind | 18.5 | 20.9 | actual_first | ~113% |
| 2020 | gas | 9.3 |  |  |  |
| 2021 | total | 39.7 |  |  |  |
| 2021 | solar | 15.4 | 13.4 | actual_later | 87% |
| 2021 | battery | 4.3 |  |  |  |
| 2021 | wind | 12.2 | 17.1 | actual_first | ~140% |
| 2021 | gas | 6.6 |  |  |  |
| 2022 | total | 46.1 |  |  |  |
| 2022 | solar | 21.5 | 10.3 | actual_later | ~48% |
| 2022 | battery | 5.1 |  |  |  |
| 2022 | wind | 7.6 |  |  |  |
| 2022 | gas | 9.6 |  |  |  |
| 2023 | total | 54.5 | 40.4 | actual_first | 74% |
| 2023 | solar | 29.1 | 19 | actual_later | 65% |
| 2023 | battery | 9.4 | 6.4 | actual_first | 68% |
| 2023 | wind | 6 |  |  |  |
| 2023 | gas | 7.5 |  |  |  |
| 2023 | nuclear | 2.2 |  |  |  |
| 2024 | total | 62.8 | 50.454 | actual_final | 80% |
| 2024 | solar | 36.4 | 30.916 | actual_final | 85% |
| 2024 | battery | 14.3 | 10.3 | actual_first | 72% |
| 2024 | wind | 8.2 | 5.154 | actual_final | 63% |
| 2024 | gas | 2.5 | 2.113 | actual_final | 85% |
| 2024 | nuclear | 1.1 | 1.114 | actual_final | 101% |
| 2025 | total | 63 | 53 | actual_first | 84% |
| 2025 | solar | 32.5 | 27.2 | actual_first | 84% |
| 2025 | battery | 18.2 | 15 | actual_first | 82% |
| 2025 | wind | 7.7 | < 5.9 | actual_first | < 77% |
| 2025 | gas | 4.4 |  |  |  |
| 2026 | total | 86 |  |  |  |
| 2026 | solar | 43.4 |  |  |  |
| 2026 | battery | 24 |  |  |  |
| 2026 | wind | 11.8 |  |  |  |
| 2026 | gas | 6.3 |  |  |  |

Blank cells are years where EIA's articles give no actual figure for that technology. The EIA-860M run will fill them.

## What it shows

1. **Total and solar came in under the plan every year EIA gives both figures.** Total: 74% of plan in 2023, 80% in 2024 (EIA-860 final) and 84% in 2025. Solar: 87% in 2021, about 48% in 2022 (EIA blamed "supply chain disruptions and other pandemic-related challenges"), 65% in 2023, 85% in 2024 and 84% in 2025.
2. **Wind went the other way in 2020-2021, then fell short.** 2020 came in at about 113% of plan and 2021 at about 140% (17.1 GW first reported, against 12.2 GW planned). EIA's 2020 article tied that year's rush to the production tax credit's scheduled expiry. Both figures are first reports that include scheduled November-December additions, and EIA later said only "more than 14 GW" for each year. In 2024 it was 63%, and in 2025 it was below 77% (EIA says the 11.8 GW planned for 2026 is "more than double" what was added in 2025).
3. **Batteries are getting closer to plan:** 68%, 72% and 82% in 2023, 2024 and 2025.
4. **First-reported actuals were partly forecasts until 2022.** The articles for 2020-2022 came out in January and were built on the October inventory, so "last year's additions" included what was scheduled for November and December: 14.9 GW of 2020's "21 GW" of wind, and 6.9 GW of 2021's 15.5 GW of solar. EIA later gave 2021 solar as 13.4 GW, 2.1 GW (14%) less. Since 2023 the articles have come out in February on the December inventory. Revisions since then have been small and upward: 2023 solar went from 18.4 to 19 GW, 2024 solar from 30 to 30.8 GW (30.9 GW in EIA-860), and the 2024 total from 48.6 to 50.5 GW.
5. **For 2025 solar, EIA's own forecast beat the developers' plan.** The Short-Term Energy Outlook (24 January 2025) expected 26 GW. That was 1.2 GW under the 27.2 GW added, while the developer-reported plan of 32.5 GW was 5.3 GW over. For wind, both overshot: the STEO had about 8 GW, the plan 7.7 GW, and less than 5.9 GW was added. This is one year, not a track record.
6. **EIA products disagree about the same year.** The same January 2025 STEO article said 7 GW of wind and 1 GW of natural gas were added in 2024. The Electric Power Annual (Form EIA-860) has 5.15 GW of wind and 2.11 GW of gas (net summer, gross additions). We have not found the reason. The STEO covers the electric power sector and is preliminary, but that alone does not obviously explain a 2 GW wind gap. It is flagged here, not resolved.

## A range for 2026, stated before the result

Rule: take the 2026 plan and multiply it by the lowest and the highest actual / plan of 2023-2025, using values only, not bounds. This is a rule of thumb, not a model. It is written down now so it can be scored against EIA's 2026 figure, expected around February 2027.

| technology | planned GW | low GW | high GW | years used |
|---|---|---|---|---|
| total | 86 | 63.8 | 72.3 | 3 |
| solar | 43.4 | 28.3 | 36.9 | 3 |
| battery | 24 | 16.3 | 19.8 | 3 |
| wind | 11.8 | 7.4 | 7.4 | 1 |
| gas | 6.3 | 5.3 | 5.3 | 1 |

If 2026 lands inside these ranges, the start-of-year headline overstates the year by roughly 14 to 22 GW. If it lands above them, the gap between plan and build is closing faster than 2023-2025 suggest.

## Limits

- **Capacity basis.** The 2021 article says its figures are net summer capacity. The others do not say. The EIA-860 values used here are net summer. On nameplate, the 2024 total would be 81% of plan instead of 80%, and gas would be 101% instead of 85%. For gas, the gap between nameplate and summer ratings is large enough to matter.
- **Different inventory months.** Plans for 2020-2022 come from the October inventory and those for 2023-2026 from December, so the early plans were made two months further out.
- **Rounding.** Article figures are rounded to 0.1 GW or to whole GW. Rows marked "~" are derived (for example, 2022 solar = 13.4 GW × (1 − 23%)) or include scheduled additions.
- **Batteries in EIA-860.** The Electric Power Annual's Table 4.6 puts batteries in "Other Energy Sources" (11.06 GW net summer added in 2024), so the battery actual for 2024 here is the article's 10.3 GW.
- **Scope.** These are EIA's headline numbers only. The project-level picture (which projects slip, by how much, and at what stage) is what `eia860m_slip.py` measures.

## Prior art

EIA's articles compare single years and single technologies, and trade press repeats each year's plan. We found no compiled, cited, multi-year table of EIA's headline plans against EIA's own later actuals by technology, and no note of how the first-reported actuals were revised. If you know of one, please open an issue.

## Sources

Every row of the CSV links its page: Today in Energy articles 42495 (14 Jan 2020), 46416 (11 Jan 2021), 50818 (10 Jan 2022), 55419 (6 Feb 2023), 61424 (15 Feb 2024), 62003 (8 May 2024), 64364 (24 Jan 2025), 64586 (24 Feb 2025) and 67205 (20 Feb 2026), all at `https://www.eia.gov/todayinenergy/detail.php?id=<id>`, and Electric Power Annual 2024 Table 4.6 at https://www.eia.gov/electricity/annual/html/epa_04_06.html. All pages were read on 15 October 2026. EIA data is public domain.
