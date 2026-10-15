# How much of EIA's start-of-year planned retirement capacity actually retires? 2020-2026, from EIA's own numbers

MV2 of Munim, Inc., 15 October 2026. Made with AI agents. Text and table: CC BY 4.0. Code (`headline.py`): Apache-2.0.

Each January or February, EIA's *Today in Energy* also says how many gigawatts of generating capacity operators plan to retire that year, from the same Preliminary Monthly Electric Generator Inventory (EIA-860M) that gives the planned additions. This note puts seven years of those retirement headlines next to what EIA later reported as retired. It is the companion to [`headline-plans.md`](headline-plans.md), which does the same for additions. Every number is in [`data/eia_headline_retirements.csv`](../data/eia_headline_retirements.csv), with the EIA page it comes from and the words it rests on. `python headline.py --retirements` rebuilds the tables below.

## Table

The actual is the most final figure EIA has stated: the Electric Power Annual (Form EIA-860) where it exists, else a later article, else the first article after the year. "~" marks a derived value.

| year | technology | planned GW | actual GW | actual from | actual / plan |
|---|---|---|---|---|---|
| 2020 | total | 11 |  |  |  |
| 2020 | gas | 3.7 |  |  |  |
| 2020 | coal | 5.8 |  |  |  |
| 2020 | nuclear | 1.6 |  |  |  |
| 2021 | total | 9.1 |  |  |  |
| 2021 | gas | 0.253 |  |  |  |
| 2021 | coal | 2.7 | 5.6 | actual_later | 207% |
| 2021 | nuclear | 5.1 | 0.965 | actual_later | 19% |
| 2022 | total | 14.9 |  |  |  |
| 2022 | gas | 1.2 |  |  |  |
| 2022 | coal | 12.6 | 13.7 | actual_later | 109% |
| 2022 | nuclear | 0.8 |  |  |  |
| 2023 | total | 15.6 | 13.5 | actual_first | 87% |
| 2023 | gas | 6.2 |  |  |  |
| 2023 | coal | 8.9 | 10.8 | actual_first | ~121% |
| 2024 | total | 5.2 | 9.0274 | actual_final | 174% |
| 2024 | gas | 2.4 | 4.2692 | actual_final | 178% |
| 2024 | coal | 2.3 | 3.9586 | actual_final | 172% |
| 2025 | total | 12.3 | 4.6 | actual_first | 37% |
| 2025 | gas | 2.6 |  |  |  |
| 2025 | coal | 8.1 | 2.6 | actual_first | 32% |
| 2026 | total | 11 |  |  |  |
| 2026 | gas | 4.6 |  |  |  |
| 2026 | coal | 6.4 |  |  |  |

Blank cells are years where we found no EIA figure for what retired. The generator-level run of `eia860m_slip.py` (still queued) will fill them from EIA-860M itself.

## What it shows

1. **Retirement plans miss in both directions; addition plans miss in one.** Planned additions came in under plan in every year EIA gives both numbers (74-84% of the total since 2023). Planned retirements came in at 87% of plan in 2023, 174% in 2024 (EIA-860 final; 144% on the first reported 7.5 GW) and 37% in 2025.
2. **Until 2024, more coal retired than was planned at the start of each year. In 2025, a third did.** Coal came in at 207% of plan in 2021, 109% in 2022 (91% on the first reported 11.5 GW), about 121% in 2023 and 172% in 2024. In 2025 it fell to 32%: 2.6 GW retired against 8.1 GW planned. EIA attributes the 2025 shortfall to Department of Energy emergency orders that kept plants open, along with retirements that operators delayed or cancelled. The April 2026 article counts 4.8 GW delayed and 1.1 GW cancelled ([67427](https://www.eia.gov/todayinenergy/detail.php?id=67427)).
3. **The smallest plans were overshot the most.** The two smallest coal plans (2.7 GW in 2021 and 2.3 GW in 2024) were followed by about twice as much retiring. One reading is that some retirements are decided and carried out within the year, after January's inventory is taken. We have not tested this at the generator level yet.
4. **The same plants can be planned twice.** The 2020 article's gas retirements include 2.2 GW at Alamitos, Huntington Beach and Redondo Beach in California. The 2023 article lists the same three plants, "with a combined 2.2 GW of capacity", as scheduled to retire that year. In nuclear, 4.1 GW of the 5.1 GW planned for 2021 (Byron and Dresden) reversed course after Illinois passed a support law ([50136](https://www.eia.gov/todayinenergy/detail.php?id=50136)), leaving Indian Point 3 (965 MW): 19% of plan.
5. **First reports of what retired were revised upward.** 2024 went from 7.5 GW (February 2025 article) to 9.03 GW net summer in the Electric Power Annual. 2021 coal went from 4.6 to 5.6 GW, and 2022 coal from 11.5 to 13.7 GW (the April 2026 article does not say which capacity measure it uses). The planned additions were also revised upward after first report.
6. **For 2025 coal, EIA's forecast missed by more than the plan.** The January 2025 Short-Term Energy Outlook expected 11 GW of coal retirements in 2025, against 8.1 GW planned and 2.6 GW retired. For 2025 solar additions it was the other way round ([`headline-plans.md`](headline-plans.md)). Two cases do not make a track record.

## A range for 2026, stated before the result

Same rule as for additions: the 2026 plan times the lowest and highest actual / plan of 2023-2025, values only.

| technology | planned GW | low GW | high GW | years used |
|---|---|---|---|---|
| total | 11 | 4.1 | 19.1 | 3 |
| gas | 4.6 | 8.2 | 8.2 | 1 |
| coal | 6.4 | 2.1 | 11.0 | 3 |

The total range runs from 4.1 to 19.1 GW against about 11 GW planned. That width is the result: in recent years, the start-of-year retirement figure has said little about how much would retire. Both the coal range (2.1 to 11.0 GW) and the gas figure (from 2024 alone) are as weak. It will be scored against EIA's 2026 figure, expected around February 2027.

## Limits

- **Capacity basis.** The articles do not say whether their figures are net summer or nameplate. The EIA-860 values used for 2024 are net summer. On nameplate, 2024 retirements were 10.68 GW in total (205% of plan), 4.46 GW of coal and 5.25 GW of gas.
- **Inventory month.** Plans for 2021 and 2022 come from the October inventory and those for 2023-2026 from December. The 2020 article does not name its month. The first-reported 2021 coal figure (4.6 GW) was written from an October inventory, so part of it may have been scheduled rather than retired.
- **Derived and mixed sources.** 2023 coal (10.8 GW) is EIA's "22.3 GW ... over the past two years" minus the 11.5 GW it first gave for 2022. If the later 13.7 GW is used for 2022 instead, 2023 drops to 8.6 GW (97% of plan). 2021 nuclear comes from EIA's reactor shutdown list, not an article. EIA's own figure for the 2025 coal plan is 8.1 GW in the February 2025 article, 8.0 GW in February 2026 and 8.5 GW in April 2026. We use the start-of-year 8.1 GW.
- **Missing actuals.** We found no EIA statement of total retirements for 2020, 2021 or 2022, or of gas retirements outside 2024.
- **Scope.** These are headline numbers. Which units slipped, by how long and why is what the generator-level scoring in `eia860m_slip.py` measures.

## Prior art

EIA compares one year's planned and actual retirements in its articles (for 2025: 12.3 GW planned, 4.6 GW retired). SynMax argued in 2025 that EIA's 2025 coal retirement figures looked overstated. In early 2025, OnLocation counted 22 coal units whose retirements had recently been delayed. Environment America Research & Policy Center (2026) tracked EIA's monthly surveys from January 2023 to December 2025 and found that about a third of the coal capacity expected to retire by the end of 2025 was still online. We found no year-by-year table, across 2020-2026 and across fuels, of EIA's start-of-year retirement figures against EIA's own later actuals, with a citation for each number. If you know of one, please open an issue.

## Sources

Every row of the CSV links its page: Today in Energy articles 42495 (14 Jan 2020), 46436 (12 Jan 2021), 50838 (11 Jan 2022), 55439 (7 Feb 2023), 61425 (20 Feb 2024), 64364 (24 Jan 2025), 64604 (25 Feb 2025), 67206 (23 Feb 2026) and 67427 (13 Apr 2026), all at `https://www.eia.gov/todayinenergy/detail.php?id=<id>`; article 50136 on the Illinois reversals; the Electric Power Annual 2024 Table 4.6 at https://www.eia.gov/electricity/annual/html/epa_04_06.html; and the nuclear reactor shutdown list at https://www.eia.gov/nuclear/reactors/shutdown/. All pages were read on 15 October 2026. EIA data is public domain.
