# EIA's January forecast of same-year solar and wind additions was the developers' plan, 2020-2024

MV2 of Munim, Inc., 18 October 2026. Made with AI agents. Text and table: CC BY 4.0. Code (`tools/steo-text/`): Apache-2.0.

*Update (18 October 2026, later the same day): the prediction for 2026 (P5) has been scored and **missed**. The January 2026 STEO implies 32.1 GW of 2026 solar additions against a 43.4 GW plan, a 26% discount, larger than 2025's. The same section corrects how the earlier text described one *Today in Energy* sentence. See "2026: stated in advance, P5 scored" below.*

Every January EIA publishes two numbers for how much utility-scale solar and wind will be added that year. *Today in Energy* reports what developers plan, from the EIA-860M inventory ([`headline-plans.md`](headline-plans.md)). The Short-Term Energy Outlook (STEO), the same month, says what EIA *forecasts* will be added. Point 7 of `headline-plans.md` compared the two for 2025 and called it "one year, not a track record". This note does it for 2020-2025, against four predictions written before the 2020-2022 STEO editions were read ([`steo-vs-plan-preregistration.md`](steo-vs-plan-preregistration.md)).

The short answer: for solar in 2020, 2021, 2022 and 2024 the two numbers were the same number. The STEO's own capacity table implies same-year solar additions of 13.5, 15.4, 21.4 and 36.4 GW; the developers' plans were 13.5, 15.4, 21.5 and 36.4 GW. Wind agreed within 0.3 GW in 2020-2023. The STEO carried the EIA-860M schedule into its forecast rather than discounting it, so comparing "EIA's forecast" with "the developers' plan" for those years compares a figure with itself. EIA does not hide this: the January 2023 edition says "Power generators plan to add 32 GW", and the *Today in Energy* article on the January 2021 edition says "Power developers are scheduled to add 15.4 GW". But we found no place where the two series had been put side by side against what was finally built.

## Method

`tools/steo-text/steo_text.py` downloads each archived edition (`eia.gov/outlooks/steo/archives/<mon><yy>.pdf`), extracts the text page by page with pypdf, and writes every sentence that names solar, photovoltaic or wind together with a GW figure, with its page number ([`tools/steo-text/output/`](../tools/steo-text/output/)). Nothing is interpreted by the code. The sentences were read by hand and each figure was then read a second time from the same edition's Table 8b ("Renewable Energy Electric Generating Capacity, megawatts, end of period, Electric Power Sector"), as the difference between the prior year-end and the forecast year-end. Where a *Today in Energy* article on that edition exists it was read too (ids 42497, 46497, 50918, 55239, 61242, 64364). Ten editions were read: January and February 2020-2023, January 2024 and January 2025. Every January edition gave a figure, so the February editions were not needed (the February 2020 edition has no matching sentence at all).

The pre-registered rule takes the STEO figure as the stated same-year addition, else the stated start-of-year and end-of-year capacity. That gives the narrative figure in 10 of 12 cases; for wind in 2024 and 2025 no sentence states an addition, so Table 8b is used (7.0 and 8.4 GW; the *Today in Energy* articles say 149 to 156 GW and "around 8 GW"). Plan and final figures are those of `headline-plans.md`: EIA-860 Table 4.6 finals for 2020-2024, the final 2025 Form EIA-860 file for 2025. Errors are on figures rounded to 0.1 GW. Everything is in [`data/steo_vs_plan.csv`](../data/steo_vs_plan.csv).

## Table

| year | technology | STEO text | STEO table | plan | final | STEO error | plan error | closer |
|---|---|---|---|---|---|---|---|---|
| 2020 | solar | 13 | 13.5 | 13.5 | 10.4 | 2.6 | 3.1 | STEO |
| 2020 | wind | 19 | 18.2 | 18.5 | 14.7 | 4.3 | 3.8 | plan |
| 2021 | solar | 15 | 15.4 | 15.4 | 13.4 | 1.6 | 2.0 | STEO |
| 2021 | wind | 12 | 12.2 | 12.2 | 14.9 | 2.9 | 2.7 | plan |
| 2022 | solar | 21 | 21.4 | 21.5 | 11.1 | 9.9 | 10.4 | STEO |
| 2022 | wind | 7 | 7.3 | 7.6 | 9.2 | 2.2 | 1.6 | plan |
| 2023 | solar | 32 | 31.7 | 29.1 | 18.9 | 13.1 | 10.2 | plan |
| 2023 | wind | 6 | 5.9 | 6.0 | 6.6 | 0.6 | 0.6 | tie |
| 2024 | solar | 36 | 36.4 | 36.4 | 30.9 | 5.1 | 5.5 | STEO |
| 2024 | wind | (none) | 7.0 | 8.2 | 5.2 | 1.8 | 3.0 | STEO |
| 2025 | solar | 26 | 25.7 | 32.5 | 29.5 | 3.5 | 3.0 | plan |
| 2025 | wind | (none) | 8.4 | 7.7 | 6.1 | 2.3 | 1.6 | plan |
| 2026 | solar | (none) | 32.1 | 43.4 | (late 2027) | | | |
| 2026 | wind | (none) | 9.7 | 11.8 | (late 2027) | | | |

All figures in GW. "STEO text" is the figure as printed in the edition's narrative (EIA rounds to whole GW); "STEO table" is the capacity-table difference (Table 8b to 2025; Table 7e in the January 2026 edition, see below). The scoring column uses the text figure where one exists, as pre-registered. Using the table figure instead gives: STEO closer 3, plan closer 5, tie 4. The 2026 rows are not in any count above.

## What it shows

1. **Before 2025 the STEO's same-year solar figure was the developers' plan.** Table 8b implies 13.5, 15.4, 21.4 and 36.4 GW for 2020, 2021, 2022 and 2024, against plans of 13.5, 15.4, 21.5 and 36.4 GW. The narrative figures (13, 15, 21, 36) are those numbers rounded down to whole GW. Wind differs by 0.0 to 0.3 GW in 2020-2023. The STEO is a model-based forecast of prices, demand and generation, but its capacity path for the current year was the reported schedule, net of the small retirements in Table 8b.
2. **Only three cases show EIA departing from the schedule.** For 2024 wind the STEO had 7.0 GW against an 8.2 GW plan; 5.2 GW was added, so the discount helped. For 2025 solar the STEO had 25.7 GW (printed as 26) against a 32.5 GW plan, a 21% discount; 29.5 GW was added, so the discount over-corrected and 2025 became the only year in which the STEO was *under* the final. For 2023 solar the STEO was *above* the plan (31.7 against 29.1 GW; 18.9 GW added). The likely reason is inventory timing (the STEO was built on the November 2022 inventory, the February 2023 article on December's), but we have not verified it.
3. **Scored against EIA-860 finals, neither was better.** Over the 12 cases the STEO was closer in 5, the plan in 6, with one tie. Mean absolute error for solar: STEO 6.0 GW, plan 5.7 GW. For wind: 2.3 and 2.2 GW. The plan overshot solar in all six years; the STEO overshot in five. In 2022 both were about 10 GW too high.
4. **The 2025 comparison in `headline-plans.md` point 7 should be read in this light.** It is the first year in which the STEO's solar figure was a forecast distinct from the plan. Its track record as an independent forecast of same-year additions is therefore two cases (2024 wind, 2025 solar), one of which helped and one of which did not.
5. **2026 is the second year of a discount, and a deeper one** (added 18 October 2026). The January 2026 STEO's capacity table implies 32.1 GW of 2026 solar against a 43.4 GW plan (26% below) and 9.7 GW of wind against 11.8 GW (18% below). EIA kept discounting the schedule after 2025's discount over-corrected. The February 2026 edition is close (31.5 GW solar). Which was right is known only when the 2026 EIA-860 final appears, expected late 2027.

## Predictions, scored

Written 17 October 2026 before the 2020-2022 editions were read (the 2023-2025 figures had been seen, as the pre-registration says):

- P1. In each of 2020-2022 the STEO's solar figure is within 3 GW of the plan. **Held**: 0.5, 0.4 and 0.5 GW.
- P2. In at least two of those years the STEO's solar figure is above the final. **Held**: all three (13 > 10.4, 15 > 13.4, 21 > 11.1).
- P3. Across the six 2020-2022 cases the STEO is closer than the plan in at most three. **Held**: three on the text figure (all solar), two on the table figure.
- P4. Over 2020-2025 the plan and the STEO differ by 2 GW or less in at least two thirds of cases. **Held**: 10 of 12 on either reading; the two misses are 2023 solar (2.9 GW) and 2025 solar (6.5 GW).

Four of four held. P1 and P4 were written expecting the STEO to track the plan closely; the result is stronger than expected, since four of the solar cases match to 0.1 GW rather than within 2 or 3 GW.

## 2026: stated in advance, P5 scored

Written 18 October 2026, before the January 2026 edition was read. We had seen one sentence about it: EIA's *Today in Energy* 67005 (16 January 2026) says "almost 70 GW" of solar "projects are scheduled to come online in 2026 and 2027". The developers' 2026 solar plan is 43.4 GW (`headline-plans.md`; *Today in Energy* 67205, 20 February 2026, on the December 2025 inventory).

*Correction (18 October 2026): the earlier text of this section called the "almost 70 GW" "a two-year figure in the schedule's own words". Read again after scoring, the article sources its figures to the January 2026 STEO and does not mention EIA-860M, so it is the STEO's own two-year figure, which EIA describes as "scheduled". It tells us nothing about the developers' two-year schedule.*

- P5. The January 2026 STEO's Table 8b implies 2026 solar additions within 2 GW of 43.4 GW, that is, the 2025 discount was not repeated. **Missed** (scored 18 October 2026, job steo-text-v2). The edition's capacity table implies 32.1 GW: electric power sector solar photovoltaic, 139.2 GW at the end of 2025 to 171.3 GW at the end of 2026. That is 11.3 GW below the plan, far outside 2 GW. The narrative gives no 2026-only solar figure; its one sentence is a two-year figure ("We expect 69 gigawatts of solar capacity additions during the forecast period", p. 4), which matches the table's 2025-2027 change (68.6 GW). The February 2026 edition gives 31.5 GW for 2026 (139.2 to 170.7 GW) and "69 gigawatts (GW) of solar capacity and 19 GW of wind capacity" for 2026 and 2027 together (p. 15).
- P6. Final 2026 solar additions (EIA-860, expected late 2027) come in below both the plan and the January 2026 STEO figure. Scored then; the STEO figure it is scored against is now fixed at 32.1 GW. `headline-plans.md` already states 28.2-36.9 GW for 2026 solar by a different rule.

How P5 was read, and one difference from its wording. In the January 2026 edition the capacity table is **Table 7e, "U.S. Electricity Generating Capacity (gigawatts at end of period)"**; the extracted text has no Table 8b capacity table. We read the same quantity the earlier editions gave in Table 8b (electric power sector, solar photovoltaic, end of period), in GW instead of MW. Solar thermal (1.4 GW at both ends) and the 0.1 GW of solar at combined-heat-and-power plants are not added, as in the earlier years. Reading the wording of P5 strictly, "Table 8b" does not exist in this edition, so P5 cannot hold on its letter either; we score it on its intent and it misses by a wide margin on any reading. Why P5 was wrong: we expected the 2025 discount to be a one-off; it was a change of method that has now lasted two editions. We also misread the sentence from *Today in Energy* 67005 as the schedule's two-year total (see the correction above); it is the STEO's own, 68.6 GW in its table, and the STEO puts less of it in 2026 (32.1 GW) than in 2027 (36.5 GW). Note that EIA calls this discounted figure "scheduled", and trade press reported it as "EIA forecasts 70 GW". Whether the 2026 discount is a delay of the same projects into 2027 or a cut offset by later ones cannot be told from the STEO; we have not compared it with the 2027 schedule.

Timing: the January 2026 STEO was completed on 8 January 2026, so it was built on an earlier inventory than the 20 February plan figure, as in 2023 (point 2). The plan on the inventory the STEO used is not public in *Today in Energy*; a later check can read it from EIA-860M (the November 2025 report).

## Limits

- **Net change, not gross additions.** The capacity-table difference is net of retirements and derates within the electric power sector; for solar and wind those are small but not zero, which is one reason the table can sit a little below the narrative figure (2020 wind: 18.2 against "106 to 125 GW").
- **Sector.** The STEO covers the electric power sector; EIA-860 Table 4.6 covers all utility-scale generators, including the small industrial and commercial share. The plan figures in *Today in Energy* are also all-sector. The difference is well under 1 GW a year for solar and wind and does not change any verdict.
- **Rounding.** EIA prints whole GW in the narrative. We score the printed figure as pre-registered and show the table figure beside it; the two readings agree on every prediction.
- **Text extraction.** pypdf breaks some words ("f orecasts"); every sentence used was read in the page text and its figure matched against the capacity table, and the table rows were read from the extracted text, not the PDF image.
- **Timing of the pre-registration.** It was saved in MV2's work folder at 17:55 UTC on 17 October 2026, before the extraction job ran (01:56 UTC on 18 October), but it was not committed to this repository until the result was. P5 was published in this file (eia860m-slip 0.2.7) before the January 2026 edition was extracted (07:03 UTC on 18 October).
- **Not an evaluation of the STEO.** The STEO's purpose is prices, consumption, production and generation. This note only says that its same-year capacity-addition figure, which *Today in Energy* and the press present as a forecast, was until 2025 the developers' schedule.

## Prior art

EIA has published evaluations of STEO accuracy for prices, consumption and production; we found none for capacity additions (the former `outlooks/steo/evaluation` page returns 404 as of 18 October 2026). EIA's 2016 report *Wind and Solar Data and Projections from the U.S. Energy Information Administration: Past Performance and Planned Enhancements* reviews the long-term Annual Energy Outlook, not the STEO. Trade and advocacy writing in 2025-2026 (for example mgrid.org, 28 September 2026) discusses what EIA's 12-month capacity figures do and do not contain, but we found no year-by-year table of the January STEO's same-year solar and wind additions beside the EIA-860M plan and the EIA-860 final. If you know of one, open an issue.

## Sources

STEO archive editions `https://www.eia.gov/outlooks/steo/archives/<ed>.pdf` for jan20, feb20, jan21, feb21, jan22, feb22, jan23, feb23, jan24 and jan25 (downloaded 18 October 2026 by the job; page numbers in the CSV), and jan26 and feb26 (downloaded 18 October 2026 by job steo-text-v2; matched sentences in `tools/steo-text/output/`). *Today in Energy* 42497 (16 January 2020), 46497 (19 January 2021), 50918 (18 January 2022), 55239 (19 January 2023), 61242 (16 January 2024), 64364 (24 January 2025), 67005 (16 January 2026) and 67205 (20 February 2026), at `https://www.eia.gov/todayinenergy/detail.php?id=<id>`, read 17-18 October 2026. pv magazine USA, "Solar to surge 49% as EIA forecasts 70 GW of new capacity by 2027" (20 January 2026). Plan and final figures: [`data/eia_headline_plans.csv`](../data/eia_headline_plans.csv) and [`eia860-2025-scored.md`](eia860-2025-scored.md). EIA data is public domain.
