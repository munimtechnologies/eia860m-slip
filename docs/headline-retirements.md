# How much of EIA's start-of-year planned retirement capacity actually retires? 2020-2026, from EIA's own numbers

MV2 of Munim, Inc., 15 October 2026 (revised in 0.2.3: final EIA-860 figures for 2020-2023). Made with AI agents. Text and table: CC BY 4.0. Code (`headline.py`): Apache-2.0.

Each January or February, EIA's *Today in Energy* also says how many gigawatts of generating capacity operators plan to retire that year, from the same Preliminary Monthly Electric Generator Inventory (EIA-860M) that gives the planned additions. This note puts seven years of those retirement headlines next to what EIA later reported as retired. It is the companion to [`headline-plans.md`](headline-plans.md), which does the same for additions. Every number is in [`data/eia_headline_retirements.csv`](../data/eia_headline_retirements.csv), with the EIA page it comes from and the words it rests on. `python headline.py --retirements` rebuilds the tables below (since 0.2.4 it also prints 2018 and 2019, which are covered in [`headline-2016-2019.md`](headline-2016-2019.md)).

## Table

The actual is the most final figure EIA has stated: the Electric Power Annual (Form EIA-860, net summer capacity) where it exists, else a later article, else the first article after the year. "~" marks a derived value. Since 0.2.3, every year from 2020 to 2024 uses the Electric Power Annual.

| year | technology | planned GW | actual GW | actual from | actual / plan |
|---|---|---|---|---|---|
| 2020 | total | 11 | 16.3795 | actual_final | 149% |
| 2020 | gas | 3.7 | 2.6509 | actual_final | 72% |
| 2020 | coal | 5.8 | 10.4567 | actual_final | 180% |
| 2020 | nuclear | 1.6 | 1.6129 | actual_final | 101% |
| 2021 | total | 9.1 | 9.0349 | actual_final | 99% |
| 2021 | gas | 0.253 | 0.9338 | actual_final | 369% |
| 2021 | coal | 2.7 | 5.5618 | actual_final | 206% |
| 2021 | nuclear | 5.1 | 1.0394 | actual_final | 20% |
| 2022 | total | 14.9 | 17.9391 | actual_final | 120% |
| 2022 | gas | 1.2 | 2.3505 | actual_final | 196% |
| 2022 | coal | 12.6 | 13.6798 | actual_final | 109% |
| 2022 | nuclear | 0.8 | 0.7685 | actual_final | 96% |
| 2023 | total | 15.6 | 15.2379 | actual_final | 98% |
| 2023 | gas | 6.2 | 5.128 | actual_final | 83% |
| 2023 | coal | 8.9 | 9.2249 | actual_final | 104% |
| 2024 | total | 5.2 | 9.0274 | actual_final | 174% |
| 2024 | gas | 2.4 | 4.2692 | actual_final | 178% |
| 2024 | coal | 2.3 | 3.9586 | actual_final | 172% |
| 2025 | total | 12.3 | 4.6 | actual_first | 37% |
| 2025 | gas | 2.6 |  |  |  |
| 2025 | coal | 8.1 | 2.6 | actual_first | 32% |
| 2026 | total | 11 |  |  |  |
| 2026 | gas | 4.6 |  |  |  |
| 2026 | coal | 6.4 |  |  |  |

The 2025 gas cell is blank because we found no EIA figure for it yet. EIA released the final 2025 EIA-860 on 10 September 2026; we have not read it yet, so 2025 still uses EIA's first article.

## What it shows

1. **Until 2025, start-of-year retirement plans understated what retired.** On EIA's final figures, total retirements from 2020 to 2024 came to 67.6 GW against 55.8 GW planned (121%). No year fell below 98% of plan: 149%, 99%, 120%, 98% and 174%. Planned *additions* do the opposite: they came in under plan every year from 2020 to 2025, at 67-97% (`headline-plans.md`). 2025 broke the pattern: 4.6 GW retired against 12.3 GW planned (37%, first count).
2. **Coal retired at or above plan every year from 2020 to 2024, and then fell to a third in 2025.** 180% in 2020, 206% in 2021, 109% in 2022, 104% in 2023 and 172% in 2024: 42.9 GW retired against 32.3 GW planned (133%). In 2025, 2.6 GW retired against 8.1 GW planned (32%). EIA attributes the 2025 shortfall to Department of Energy emergency orders that kept plants open, along with retirements that operators delayed or cancelled. The April 2026 article counts 4.8 GW delayed and 1.1 GW cancelled ([67427](https://www.eia.gov/todayinenergy/detail.php?id=67427)). Going back further, coal retirements met or beat the January plan in every year from 2018 to 2024 (139% pooled; 2019 alone was 287%), so 2025 is the first shortfall in this record, which starts in 2018 ([`headline-2016-2019.md`](headline-2016-2019.md)).
3. **The smallest coal plans were overshot the most.** The three smallest coal plans (2.3, 2.7 and 5.8 GW) were followed by 172-206% of plan. The three largest (8.1, 8.9 and 12.6 GW) were followed by 32-109%. In gigawatts, coal retirements ranged from 4.0 to 13.7 GW a year in 2020-2024 whatever the plan said. One reading is that some retirements are decided and carried out within the year, after January's inventory is taken. Six years is a small sample, and we have not tested this at the generator level yet.
4. **The same plants can be planned twice, and nuclear plans can reverse.** The 2020 article's gas retirements include 2.2 GW at Alamitos, Huntington Beach and Redondo Beach in California. The 2023 article lists the same three plants, "with a combined 2.2 GW of capacity", as scheduled to retire that year. In nuclear, 4.1 GW of the 5.1 GW planned for 2021 (Byron and Dresden) reversed course after Illinois passed a support law ([50136](https://www.eia.gov/todayinenergy/detail.php?id=50136)), leaving Indian Point 3 (1,039 MW net summer in EIA-860; 965 MW on EIA's reactor shutdown list): 20% of plan. The two nuclear plans that went ahead (2020 and 2022) came in at 101% and 96%.
5. **EIA's first count of what retired has usually been too low.** Every first count we can compare with the final EIA-860 figure, and how it was revised:

   | year | technology | first count GW (article) | final GW (EIA-860) | revision |
   |---|---|---|---|---|
   | 2021 | coal | 4.6 (50838, October inventory) | 5.56 | +21% |
   | 2022 | coal | 11.5 (55439) | 13.68 | +19% |
   | 2023 | total | 13.5 (61425, December inventory) | 15.24 | +13% |
   | 2024 | total | 7.5 (64604, December inventory) | 9.03 | +20% |
   | 2024 | coal | 4.0 (64604) | 3.96 | -1% |

   Four of five went up by 13-21%. For 2023 and 2024 the first count was already built on the December inventory, so this is not the "scheduled months" problem that inflated the first-reported 2020 additions (see `headline-plans.md`). It runs the other way. One plausible cause, untested: EIA-860M adds a generator to its frame ahead of a *planned* retirement, so unplanned retirements may be reported late. For additions, revisions since 2023 have been small and upward (1-5%; the totals rose 4.7% for 2023 and 3.8% for 2024); for 2020-2021, when first counts included scheduled November-December additions, they were downward (11-30%).
6. **What this implies for 2025, stated before reading the final file.** If 2025's first count (4.6 GW) is revised like 2023 and 2024 (+13% to +20%), the final figure would be about 5.2-5.5 GW: 42-45% of plan. That would still be by far the lowest year in the table. We will check this against the final 2025 EIA-860 (released 10 September 2026, not yet read).
7. **For 2025 coal, EIA's forecast missed by more than the plan.** The January 2025 Short-Term Energy Outlook expected 11 GW of coal retirements in 2025, against 8.1 GW planned and 2.6 GW retired. For 2025 solar additions it was the other way round ([`headline-plans.md`](headline-plans.md)). Two cases do not make a track record.

## A range for 2026, stated before the result

Same rule as for additions: the 2026 plan times the lowest and highest actual / plan of 2023-2025, values only.

| technology | planned GW | low GW | high GW | years used |
|---|---|---|---|---|
| total | 11 | 4.1 | 19.1 | 3 |
| gas | 4.6 | 3.8 | 8.2 | 2 |
| coal | 6.4 | 2.1 | 11.0 | 3 |

The total range runs from 4.1 to 19.1 GW against about 11 GW planned. That width is the result: in recent years, the start-of-year retirement figure has said little about how much would retire. The low end rests on 2025's first count; if that is revised upward (point 6), the low end rises to about 4.6-5.0 GW. The range will be scored against EIA's 2026 figure, expected around February 2027. The 0.2.3 revision changed only the gas range (from 8.2-8.2 GW on one year to 3.8-8.2 GW on two). The total and coal ranges are unchanged.

## Limits

- **Capacity basis.** The Electric Power Annual figures are net summer capacity, by each generator's primary energy source. The articles do not say which measure they use, but the April 2026 article's 13.7 GW for 2022 coal matches the Electric Power Annual's 13,679.8 MW net summer. On nameplate, total retirements are 9-18% higher (2024: 10.68 GW in total, 205% of plan).
- **Plan vs final are not the same measure.** The plans are EIA-860M figures as reported in January or February; the finals are EIA-860. Some of the gap between them is reporting, not behaviour.
- **Inventory month.** Plans for 2021 and 2022 come from the October inventory and those for 2023-2026 from December. The 2020 article does not name its month.
- **Edition dates.** The CSV dates each Electric Power Annual row by the edition's release date on EIA's archive pages: 2020 edition 29 October 2021 (re-released 10 March 2022; we read the archived copy), 2021 edition 7 November 2022, 2022 edition 19 October 2023, 2023 edition 17 October 2024, 2024 edition October 2025.
- **Replaced figures.** Up to 0.2.2, 2023 coal was derived ("22.3 GW over the past two years" minus 11.5 GW for 2022) as 10.8 GW (~121%). The final figure is 9.22 GW (104%). The two-year total was close (22.90 GW final), but the split was not, because the 2022 first count was 2.2 GW low. The 2023 total moved from 87% (first count) to 98%.
- **Missing actuals.** None for 2025 gas. 2025 total and coal are first counts.
- **Scope.** These are headline numbers. Which units slipped, by how long and why is what the generator-level scoring in `eia860m_slip.py` measures.

## Corrections

0.2.3 (16 October 2026, released together with 0.2.4): 2020-2023 now use the Electric Power Annual's final figures. 0.2.2 said 2023 total retirements were 87% of plan and 2023 coal about 121%; on EIA-860 they were 98% and 104%. 0.2.2's point 5 also said "the planned additions were also revised upward after first report". That was wrong in two ways: it is the reported *actual* additions that were revised, and for 2020-2021 they were revised downward.

## Prior art

EIA compares one year's planned and actual retirements in its articles (for 2025: 12.3 GW planned, 4.6 GW retired). SynMax argued in 2025 that EIA's 2025 coal retirement figures looked overstated. In early 2025, OnLocation counted 22 coal units whose retirements had recently been delayed. Environment America Research & Policy Center (2026) tracked EIA's monthly surveys from January 2023 to December 2025 and found that about a third of the coal capacity expected to retire by the end of 2025 was still online. EIA says EIA-860M figures are preliminary and are corrected without notice in later months. We found no year-by-year table, across 2020-2026 and across fuels, of EIA's start-of-year retirement figures against EIA's own final figures, and no measurement of how much EIA's first-reported retirements are revised. If you know of one, please open an issue.

## Sources

Every row of the CSV links its page: Today in Energy articles 42495 (14 Jan 2020), 46436 (12 Jan 2021), 50838 (11 Jan 2022), 55439 (7 Feb 2023), 61425 (20 Feb 2024), 64364 (24 Jan 2025), 64604 (25 Feb 2025), 67206 (23 Feb 2026) and 67427 (13 Apr 2026), all at `https://www.eia.gov/todayinenergy/detail.php?id=<id>`; article 50136 on the Illinois reversals; Electric Power Annual Table 4.6 for 2024 at https://www.eia.gov/electricity/annual/html/epa_04_06.html and for 2020-2023 at `https://www.eia.gov/electricity/annual/archive/<year>/html/epa_04_06.html`; and the nuclear reactor shutdown list at https://www.eia.gov/nuclear/reactors/shutdown/. The articles and tables were read on 15 October 2026 and the edition release dates on 16 October 2026. EIA data is public domain.
