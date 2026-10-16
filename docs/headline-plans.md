# How much of EIA's start-of-year planned capacity gets built? 2020-2026, from EIA's own numbers

MV2 of Munim, Inc., 15 October 2026; corrected in 0.2.3 (see Corrections); 2025 predictions scored in 0.2.5. Made with AI agents. Text and table: CC BY 4.0. Code (`headline.py`): Apache-2.0.

Every January or February, EIA's *Today in Energy* says how many gigawatts of new utility-scale capacity developers plan to bring online that year. The figures come from EIA's Preliminary Monthly Electric Generator Inventory (EIA-860M) and are reported widely as "a record N GW this year". This note puts seven years of those headline plans next to what EIA itself later reported as added, technology by technology. Every number is in [`data/eia_headline_plans.csv`](../data/eia_headline_plans.csv), along with the EIA page it comes from and the words it rests on. `python headline.py` rebuilds the table below from that file (since 0.2.4 it also prints 2016, 2018 and 2019, which are covered in [`headline-2016-2019.md`](headline-2016-2019.md)).

This is the headline-level companion to the generator-level study in this repo (`eia860m_slip.py`), which scores every planned month in EIA-860M. Its generator-level results are not published yet (see the README's Status section).

## Table

The actual is the most final figure EIA has stated: the Electric Power Annual (Form EIA-860, Table 4.6) where it exists, else a later article, else the first article after the year. For 2020-2024 every row except batteries now uses the Electric Power Annual. "~" marks a value derived from an article or one that EIA built partly from scheduled additions. "<" marks an upper bound.

| year | technology | planned GW | actual GW | actual from | actual / plan |
|---|---|---|---|---|---|
| 2020 | total | 42 | 32.2382 | actual_final | 77% |
| 2020 | solar | 13.5 | 10.4106 | actual_final | 77% |
| 2020 | wind | 18.5 | 14.6649 | actual_final | 79% |
| 2020 | gas | 9.3 | 6.3682 | actual_final | 68% |
| 2021 | total | 39.7 | 38.3537 | actual_final | 97% |
| 2021 | solar | 15.4 | 13.4183 | actual_final | 87% |
| 2021 | battery | 4.3 | < 3.2531 | actual_final | < 76% |
| 2021 | wind | 12.2 | 14.9314 | actual_final | 122% |
| 2021 | gas | 6.6 | 6.6131 | actual_final | 100% |
| 2022 | total | 46.1 | 30.7795 | actual_final | 67% |
| 2022 | solar | 21.5 | 11.0532 | actual_final | 51% |
| 2022 | battery | 5.1 | < 4.1096 | actual_final | < 81% |
| 2022 | wind | 7.6 | 9.1545 | actual_final | 120% |
| 2022 | gas | 9.6 | 6.2101 | actual_final | 65% |
| 2023 | total | 54.5 | 42.318 | actual_final | 78% |
| 2023 | solar | 29.1 | 18.8876 | actual_final | 65% |
| 2023 | battery | 9.4 | 6.4 | actual_first | 68% |
| 2023 | wind | 6 | 6.5864 | actual_final | 110% |
| 2023 | gas | 7.5 | 8.7013 | actual_final | 116% |
| 2023 | nuclear | 2.2 | 1.114 | actual_final | 51% |
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

Blank cells are years where EIA has published no actual figure for that technology yet. The 2025 rows still show EIA's first article. The final 2025 Form EIA-860 gives higher figures (total 56.6 GW, 90% of plan; solar 29.5 GW, 91%; battery 16.3 GW, 90%; wind 6.1 GW, 79%; gas 4.6 GW, 104%), computed in [`eia860-2025-scored.md`](eia860-2025-scored.md). They will replace the first counts in the table once the Electric Power Annual 2025 prints them.

## What it shows

1. **Over 2020-2024, 79% of the planned capacity was added in the planned year.** On EIA-860 final figures, 194.1 GW was added against 245.1 GW planned at the start of each year. Year by year: 77%, 97%, 67%, 78% and 80%. 2025's first count is 84%, and the final EIA-860 file gives 90% (`eia860-2025-scored.md`). In 2016, 2018 and 2019 the plans were close (101% pooled); see [`headline-2016-2019.md`](headline-2016-2019.md).
2. **Solar accounts for most of the gap.** It fell short every year: 77% (2020), 87% (2021), 51% (2022, when EIA blamed "supply chain disruptions and other pandemic-related challenges"), 65% (2023), 85% (2024) and 84% (2025, first count; 91% on the final EIA-860 file). Over 2020-2024 it came to 73% of plan (84.7 of 115.9 GW). That is 31.2 GW of the 51.0 GW total shortfall.
3. **Wind came close to its plan overall and beat it in three years.** Over 2020-2024 wind came to 96% of plan (50.5 of 52.5 GW): 79% in 2020, then 122%, 120% and 110% in 2021-2023, then 63% in 2024. In 2025 it was below 77% on the first count (EIA says the 11.8 GW planned for 2026 is "more than double" what was added in 2025) and 79% on the final EIA-860 file.
4. **Natural gas was mixed:** 68%, 100%, 65%, 116% and 85% over 2020-2024 (85% in total). Gas is the one technology where nameplate and net summer ratings differ a lot (see Limits).
5. **Batteries are getting closer to plan:** 68%, 72% and 82% in 2023, 2024 and 2025 (first counts; 2025 is 90% on the final EIA-860 file). For 2021 and 2022 only an upper bound exists (at most 76% and 81%), because EIA-860's table puts batteries in "Other Energy Sources".
6. **How far to trust EIA's first count of additions depends on the inventory month.** Until 2022, the January articles were built on the October inventory, so "last year's additions" included what was still scheduled for November and December. Those first counts were too high: 2020 wind 20.9 GW against 14.66 GW final (-30%), 2020 solar 11.7 against 10.41 (-11%), 2021 wind 17.1 against 14.93 (-13%), 2021 solar 15.5 against 13.42 (-13%). Since 2023 the articles use the December inventory, and the first counts have been low: 2023 total 40.4 against 42.3 GW final (+4.7%), 2023 solar +2.7%, 2024 total +3.8%, 2024 solar +3.1%, 2024 wind +1.1%, and on the final 2025 EIA-860 file 2025 total +6.8%, solar +8.3%, battery +8.7%. EIA's first count of *retirements* has usually been revised up more (by 11-21% in five of seven cases; see `headline-retirements.md`).
7. **For 2025 solar, EIA's own forecast beat the developers' plan.** The Short-Term Energy Outlook (24 January 2025) expected 26 GW. That was 1.2 GW under the 27.2 GW first count (3.5 GW under the 29.5 GW in the final EIA-860 file), while the developer-reported plan of 32.5 GW was 5.3 GW over (3.0 GW over the final). For wind, both overshot: the STEO had about 8 GW, the plan 7.7 GW, and 6.1 GW was added. This is one year, not a track record.
8. **EIA products disagree about the same year.** The same January 2025 STEO article said 7 GW of wind and 1 GW of natural gas were added in 2024. The Electric Power Annual (Form EIA-860) has 5.15 GW of wind and 2.11 GW of gas (net summer, gross additions). We have not found the reason. The STEO covers the electric power sector and is preliminary, but that alone does not obviously explain a 2 GW wind gap. It is flagged here, not resolved.

## Predictions, stated before the result

**Final 2025 additions.** If the December-inventory revisions of 2023 and 2024 repeat, the Electric Power Annual 2025 (Table 4.6, expected late 2026) will show about 55.0-55.5 GW added in 2025 (87-88% of plan) and 27.9-28.0 GW of solar (86%). This rests on two years of revisions, so a result a little outside it would not be surprising; a result below 53 GW would mean the pattern broke.

**Scored early (0.2.5, 16 October 2026): both missed.** The final 2025 Form EIA-860, read with a method that reproduces Table 4.6 for 2023 and 2024 to the decimal, gives 56.6 GW added (1.1 GW above the range) and 29.5 GW of solar (1.5 GW above). The first count was revised up by 6.8% (solar 8.3%), more than in either year the range was built on. The ranges were written before we read the file but after EIA had released it. Details, and the exact figures we now expect Table 4.6 to print, are in [`eia860-2025-scored.md`](eia860-2025-scored.md).

**2026 additions.** Rule: take the 2026 plan and multiply it by the lowest and the highest actual / plan of 2023-2025, using values only, not bounds. This is a rule of thumb, not a model.

| technology | planned GW | low GW | high GW | years used |
|---|---|---|---|---|
| total | 86 | 66.8 | 72.3 | 3 |
| solar | 43.4 | 28.2 | 36.9 | 3 |
| battery | 24 | 16.3 | 19.8 | 3 |
| wind | 11.8 | 7.4 | 13.0 | 2 |
| gas | 6.3 | 5.3 | 7.3 | 2 |

The first version of this note (0.2.1, 15 October 2026) gave 63.8-72.3 GW for the total, using EIA's first count for 2023. Both ranges were written down before any 2026 figure existed. Both will be scored against EIA's 2026 figure, expected around February 2027. The change comes only from replacing the 2023 first count with EIA's final one, not from any 2026 information. Over the longer 2020-2024 record the yearly ratio ran from 67% to 97%, so a 2026 total anywhere between about 57 and 83 GW would not be out of line with history. With 2025's final EIA-860 values the same rule gives 66.8-77.3 GW; that is recorded in `eia860-2025-scored.md` but is not a new scored range.

## Limits

- **Capacity basis.** The 2021 article says its figures are net summer capacity. The others do not say. The EIA-860 values used here are net summer. On nameplate, the 2024 total would be 81% of plan instead of 80%, and gas would be 101% instead of 85%. For gas, the gap between nameplate and summer ratings is large enough to matter: 2020 gas is 68% on net summer and 77% on nameplate.
- **Different inventory months.** Plans for 2021-2022 come from the October inventory (2020's article does not name the month) and those for 2023-2026 from December, so the early plans were made two months further out.
- **Rounding.** Article figures are rounded to 0.1 GW or to whole GW. Rows marked "~" are derived or include scheduled additions. They stay in the CSV for the record but are outranked by the EIA-860 rows.
- **Batteries in EIA-860.** The Electric Power Annual's Table 4.6 puts batteries in "Other Energy Sources" with hydrogen, purchased steam and other sources. For 2021 and 2022 that row is an upper bound on batteries. For 2023-2025 the article figures are used.
- **Gross additions.** Table 4.6 counts new generators. Uprates and derates of existing ones are in a separate block of the same table and are not used here.
- **Edition dates.** The CSV dates each Electric Power Annual row by the edition's release date on EIA's archive pages: 2020 edition 29 October 2021 (re-released 10 March 2022; we read the archived copy), 2021 edition 7 November 2022, 2022 edition 19 October 2023, 2023 edition 17 October 2024, 2024 edition October 2025.
- **Scope.** These are EIA's headline numbers only. The project-level picture (which projects slip, by how much, and at what stage) is what `eia860m_slip.py` measures.

## Corrections

- **0.2.3 (16 October 2026, released together with 0.2.4):** 2020-2023 now use EIA-860 final figures from the archived Electric Power Annual editions. Each table was read twice, and its rows sum to its printed total. Three claims in 0.2.1/0.2.2 were wrong:
  - "Wind beat its plan in 2020-2021 and has fallen short since." In fact 2020 was 79% (the 113% came from a first count that was mostly still scheduled), and wind beat its plan in 2021, 2022 and 2023.
  - 2023 total additions were 78% of plan, not 74% (first count 40.4 GW, final 42.3 GW).
  - 2022 solar was 51%, not about 48% (the derived 10.3 GW against 11.05 GW final).
  The 2026 total range moves from 63.8-72.3 to 66.8-72.3 GW for the same reason. Both are kept for scoring.

## Prior art

EIA's articles compare single years and single technologies, and trade press repeats each year's plan. We found no compiled, cited, multi-year table of EIA's headline plans against EIA's own final counts by technology, and no note of how the first-reported actuals were revised. If you know of one, please open an issue.

## Sources

Every row of the CSV links its page: Today in Energy articles 42495 (14 Jan 2020), 46416 (11 Jan 2021), 46976 (3 Mar 2021), 50818 (10 Jan 2022), 51518 (7 Mar 2022), 55419 (6 Feb 2023), 61424 (15 Feb 2024), 62003 (8 May 2024), 64364 (24 Jan 2025), 64586 (24 Feb 2025) and 67205 (20 Feb 2026), all at `https://www.eia.gov/todayinenergy/detail.php?id=<id>`; the Electric Power Annual 2024 Table 4.6 at https://www.eia.gov/electricity/annual/html/epa_04_06.html; and the 2020-2023 editions at `https://www.eia.gov/electricity/annual/archive/<year>/html/epa_04_06.html`. The articles were read on 15 October 2026, and the archived tables and edition release dates on 16 October 2026. The final 2025 Form EIA-860 (https://www.eia.gov/electricity/data/eia860/xls/eia8602025.zip) was read on 16 October 2026. EIA data is public domain.
