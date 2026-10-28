# Coal retirements against EIA's plan, row by row (2016-2026)

Made by MV2 of Munim, Inc. with AI agents, 2026-10-16. Code: Apache-2.0 ([`tools/coal-rows/`](../tools/coal-rows/)). This page and the CSVs in `data/`: CC BY 4.0. Source: PUDL's EIA-860M changelog (`core_eia860m__changelog_generators.parquet`, PUDL nightly, downloaded 2026-10-15; EIA reports 2015-07 to 2026-08; CC BY 4.0, Catalyst Cooperative).

[`coal-plan-misses.md`](coal-plan-misses.md) explained coal's plan misses from EIA articles and news, and listed one limit: plan membership was inferred, not read from EIA-860M rows. This page reads the rows. For each year Y, the **plan** is every operating coal generator whose planned retirement date falls in Y in EIA's October or December inventory of Y-1. Each coal generator that retired in Y is then put in one of these classes by what that inventory said about it: planned for Y, planned for a later year, planned for an earlier year, no date on file, not operating, or not listed. Capacity is net summer (nameplate where summer is blank).

Six predictions were written down before the job ran ([scored below](#predictions-scored)). Five held and one missed.

## Summary

- **The rows reproduce EIA.** The row-level plan is within 13% of EIA's start-of-year coal figure in all six years tested (2021-2026). Row-level retired MW is within 7% of the final Table 4.6 count in 6 of 7 years (2018-2024). 2021 is 12% high.
- **2026, January to August: no coal generator retired.** This is the first such year in the record. Every year from 2016 to 2025 had coal retirements in those months (the smallest was 2025: 793 MW). EIA's Electric Power Monthly Table 6.4 (data for July 2026, released 2026-09-24) independently lists no coal unit among its 35 retirements of 2026.
- **84% of the 2026 plan has been moved out of the year or is held open by DOE.** Of the 16 generators (6,354 MW) dated to retire in 2026 in the December 2025 inventory, none has retired. 2,291 MW is now dated 2027 or 2034, 479 MW has no date, and 2,570 MW is still dated 2026 but held open by DOE emergency orders. Comanche 2 (335 MW) is still dated 2026, but its owner has asked to run it to March 2028. That leaves Sherburne County 1 (680 MW, Minnesota) as the only unit in the plan with no deferral on record.
- **2021 (206% of plan) explained.** Most of the extra came from retirements that already had a date on file and were brought forward: R.M. Schahfer, G.G. Allen, R. Gallagher and River Rouge. This differs from 2019, where 8.8 GW of the 9.4 GW unplanned retirement had no date on file at all in the December 2018 inventory.

## Plan and outcome by year

GW net summer. "inv" is the inventory month. The class columns split the retired MW by what that inventory said.

| year | inv | EIA plan | plan (rows) | plan retired in year | retired (rows) | EIA final | planned same year | planned later | planned earlier | no date | not operating | not listed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2016 | 2015-12 |  | 5.33 | 4.76 | 7.91 |  | 4.76 | 0.25 | 0.00 | 2.90 | 0.00 | 0.00 |
| 2017 | 2016-12 |  | 4.89 | 4.56 | 6.31 |  | 4.56 | 0.04 | 0.00 | 1.70 | 0.00 | 0.00 |
| 2018 | 2017-12 | 13.0 | 11.90 | 10.27 | 13.30 | 13.30 | 10.27 | 0.00 | 0.00 | 3.03 | 0.00 | 0.00 |
| 2019 | 2018-12 | 4.5 | 3.99 | 3.61 | 12.98 | 12.90 | 3.61 | 0.57 | 0.00 | 8.80 | 0.00 | 0.00 |
| 2020 | 2019-12 | 5.8 | 6.10 | 6.04 | 11.18 | 10.46 | 6.04 | 0.58 | 0.00 | 4.03 | 0.00 | 0.52 |
| 2021 | 2020-12 | 2.7 | 3.03 | 2.82 | 6.24 | 5.56 | 2.70 | 1.87 | 0.00 | 1.00 | 0.00 | 0.67 |
| 2022 | 2021-12 | 12.6 | 12.87 | 10.04 | 13.68 | 13.68 | 10.01 | 0.40 | 0.00 | 3.27 | 0.00 | 0.00 |
| 2023 | 2022-12 | 8.9 | 9.00 | 6.49 | 8.60 | 9.22 | 6.49 | 0.84 | 0.00 | 1.27 | 0.00 | 0.00 |
| 2024 | 2023-12 | 2.3 | 2.60 | 1.92 | 3.96 | 3.96 | 1.92 | 1.18 | 0.38 | 0.48 | 0.00 | 0.00 |
| 2025 | 2024-12 | 8.1 | 8.45 | 2.21 | 2.69 | 2.6 (first) | 2.21 | 0.00 | 0.00 | 0.21 | 0.27 | 0.00 |
| 2026 (to Aug) | 2025-12 | 6.4 | 6.35 | 0.00 | 0.00 |  | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |

The October inventories, the per-plant tables of unplanned retirements and the diagnostics are in [`coal-rows-output.md`](coal-rows-output.md). Every retired coal generator, with its class in both inventories, is in [`data/coal_retired_generators.csv`](../data/coal_retired_generators.csv).

Two things stand out. First, in the years the plan was met (2018, 2022, 2023), 72-86% of the plan's MW retired on time, and retirements with no date on file made up most of the gap. Second, in 2025 only 26% of the December plan's MW retired. That is the lowest rate in the record by far; the next lowest is 72%.

## 2026 so far: the December 2025 plan, unit by unit

As of the August 2026 EIA-860M report (data in [`data/coal_plan_2026_followup.csv`](../data/coal_plan_2026_followup.csv)), with the reason for each change:

| Unit | MW | Dated (Dec 2025) | Dated now | Why | Source |
|---|---|---|---|---|---|
| J.H. Campbell 1-3, MI | 1,330.5 | 2026-02 | 2026-11 | DOE 202(c) orders, renewed every 90 days | [DOE](https://www.energy.gov/ceser/2026-doe-202c-orders) |
| Cumberland 2, TN | 1,231.0 | 2026-12 | 2034-12 | TVA board postponed (2026-02-11) | [TVA](https://www.tva.com/energy/our-power-system/coal/cumberland-fossil-plant) |
| R.M. Schahfer 17-18, IN | 722.0 | 2026-06 | 2026-10 | DOE 202(c) order | DOE |
| Sherburne County 1, MN | 680.0 | 2026-12 | 2026-12 | none found; Xcel's 2025-12-30 Sherco plan: "operation of Unit 1 until the end of 2026" | [Xcel Sherco annual plan](https://mn.gov/deed/assets/etac-2026-02-10-agenda-5b-sherco-annual-plan_tcm1045-721697.pdf) |
| South Oak Creek 7-8, WI | 616.0 | 2026-12 | 2027-12 | We Energies deferred (April 2026) | [RTO Insider](https://www.rtoinsider.com/129786-we-energies-defers-oak-creek-coal-units-retirement-through-2027/) |
| Grand River Energy Center 2, OK | 478.9 | 2026-06 | no date | GRDA reversed its plan to decommission; DOE is funding $28.5M of upgrades | [Oklahoma Watch, 2026-06-11](https://oklahomawatch.org/2026/06/11/with-assist-from-trump-administration-grda-sticks-with-coal-power/), [KTUL, 2026-07-30](https://ktul.com/news/local/federal-grant-keeps-grda-coal-unit-online-07-30-2026) |
| Kingston 7-9, TN | 444.0 | 2026-12 | 2034-12 | re-dated by TVA in EIA-860M (reason not checked) | EIA-860M |
| Craig 1, CO | 427.0 | 2026-03 | 2026-09 | DOE 202(c) order | DOE |
| Comanche 2, CO | 335.0 | 2026-12 | 2026-12 | Xcel applied 2026-06-15 to extend to 2028-03-31 (Colorado PUC Proceeding 26A-0235E); no decision found | [CPR News, 2026-06-17](https://www.cpr.org/2026/06/17/xcel-aging-coal-plant/) |
| F.B. Culley 2, IN | 90.0 | 2026-03 | 2026-09 | DOE 202(c) order | DOE |

- **Moved out of 2026 or undated:** 2,770 MW (44%).
- **Still dated 2026 but under DOE orders:** 2,570 MW (40%).
- **Still dated 2026, deferral requested:** 335 MW (5%).
- **Still dated 2026, no deferral on record:** 680 MW (11%), Sherburne County 1 alone.
- **EIA's own planned-retirement table** (Electric Power Monthly Table 6.6, data for July 2026) shows the same six units still dated 2026: Campbell 1-3, Culley 2, Craig 1, Schahfer 17-18, Sherburne County 1 and Comanche 2.
- **Unnamed units resolved.** The plan's units that EIA's February article did not name (1,603 MW) are GREC 2, Kingston 7-9 and Sherburne County 1. [`coal-plan-misses.md`](coal-plan-misses.md) left them open.

The range stated in advance in [`coal-plan-misses.md`](coal-plan-misses.md) is unchanged: EIA's first count of 2026 coal retirements will be **0.3-2.5 GW (central 1.3)**. Nothing here re-scores it. These facts point to the lower half of that range: Sherburne County 1 alone is 0.68 GW, and so far no coal retirement outside the plan has been reported. The way the range fails is unchanged too: if DOE's orders lapse, Campbell (1.33 GW) alone could retire before year end.

## 2025 coal retirements on the final Form EIA-860

The final 2025 EIA-860 (generator file, retired sheet) lists 8 coal generators retired in 2025. Their nameplate total is 2,626.0 MW and their net summer total 2,688.4 MW:

| Plant | State | Gen | Nameplate MW | Summer MW | Retired |
|---|---|---|---:|---:|---|
| Indian River | DE | 4 | 445.5 | 410 | 2025-02 |
| Cholla | AZ | 1 | 113.6 | 112 | 2025-03 |
| Cholla | AZ | 3 | 312.3 | 271 | 2025-03 |
| Schiller | NH | 4 | 50 | 47.5 | 2025-10 |
| Schiller | NH | 6 | 50 | 47.9 | 2025-10 |
| Intermountain Power Project | UT | 1 | 820 | 900 | 2025-10 |
| Intermountain Power Project | UT | 2 | 820 | 900 | 2025-11 |
| Prairie Creek | IA | 1 | 14.6 | (blank) | 2025-12 |

- **Why summer exceeds nameplate.** The two Intermountain units are rated 900 MW summer against 820 MW nameplate (+160 MW together). This is not unusual: 36-40 operable coal rows a year carry summer above nameplate (2023: +847 MW, 2024: +894 MW, 2025: +772 MW). Prairie Creek 1 has no summer rating and adds nothing to the summer total.
- **Schiller 4 and 6 are not in EIA's April 2026 article.** That article listed four plants (2,608 MW). Schiller's retirement first appeared in EIA-860M in February 2026, four months after it happened. EIA's April article came later still. We have not found why it was left out.
- **A risk to our stated Table 4.6 coal figure.** The 2,688.4 MW stated in [`eia860-2025-scored.md`](eia860-2025-scored.md) counts a blank summer rating as zero. That is the same rule `eia860_final.py` used to reproduce Table 4.6 exactly for 2023 and 2024. If EIA instead counts Prairie Creek at its 14.6 MW nameplate, Table 4.6 would print 2,703.0, and the stated figure would miss its 0.1% band.

Source: `coal25.py` in this repo, run on EIA's 3_1_Generator_Y2025 file, plus the job output.

## Predictions scored

These were written before the job ran, and nothing was changed after the output was read.

| # | Prediction | Result | Score |
|---|---|---|---|
| 1 | The row-level plan is within ±15% of EIA's figure in at least 5 of 6 years (2021-2026) | 6 of 6 (−8.5%, +12.9%, +1.1%, +13.0%, +4.3%, −0.7%) | hit |
| 2 | Retired rows are within ±10% of Table 4.6 final in at least 6 of 7 years (2018-2024) | 6 of 7; 2021 is +12.2% | hit |
| 3 | 2021, October 2020 inventory: unplanned MW dated to another year > no date + not listed | 2.19 > 1.91 GW (53% vs 47%) | hit, narrowly |
| 4 | MW first recorded for the year during the year is ≥30% of retired MW in 2019, 2020, 2021 and 2024, and ≤15% in 2025 | 67%, 41%, 57%, 42%; **2025: 18%** | **miss** |
| 5 | Plan delivery is 0.25-0.40 in 2025 and ≥0.60 in 2021-2024 | 0.26; 0.93, 0.78, 0.72, 0.74 | hit |
| 6 | 2026: ≤1.5 GW of the plan retired; ≥4 of EIA's 7 named units in the row plan | 0 GW; 7 of 7 | hit |

**About the miss (4).** In 2025 the measure counts Cholla 1 and 3 (383 MW): EIA-860M first dated them to 2025 in February 2025, a month before they closed. It also counts Schiller (95 MW), which was first recorded after the fact. Cholla's 2025 closure, however, was settled years earlier. APS committed in 2014 to stop burning coal at Units 1 and 3 by the mid-2020s, the rules set April 2025, and APS repeated the 2025 date in its January 2020 clean-energy plan ([RMI, 2020-01-25](https://rmi.org/aps-and-the-momentum-of-100-percent-clean-energy/); [Pinnacle West 10-K for 2025](https://www.sec.gov/Archives/edgar/data/764622/000076462226000011/pnw-20251231.htm)). Even so, the December 2024 inventory carried no 2025 date for either unit. So the measure records when EIA's inventory carried the date, not when the decision was made. coal-plan-misses.md's wording ("decided during the year") should be read with that in mind.

## Limits

- **Late reports.** EIA-860M retirements can appear months late (Schiller: four months). "No coal retired January-August 2026" holds as of the August 2026 report and EPM data for July 2026. Later reports could add rows.
- **2021 is 12% high against the final count.** The 0.68 GW excess is close to Chalk Point 1-2 (670 MW, retired June 2021). Neither 2020 inventory lists those units as operating coal. We have not checked how the final EIA-860 classes them.
- **Inventory dates are not decision dates** (see the miss above).
- **The record starts in 2015-07**, so "first year with no January-August coal retirement" covers 2016-2026 only.
- Plant reasons in the 2026 table come from news and utility pages, cited per row. No court or commission filings were read.

## Reproduce

```
pip install pandas pyarrow
curl -O https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/core_eia860m__changelog_generators.parquet
cd tools/coal-rows && python -m unittest -v test_coal_rows
python coal_rows.py --data-dir <folder with the parquet> --out-dir out
```

PUDL's nightly file changes over time. The numbers here come from the copy downloaded on 2026-10-15.

## Update, 2026-10-28: September 2026, still no coal retirement

EIA's September 2026 EIA-860M workbook (published 23 October 2026) has no coal generator on its Retired sheet with retirement year 2026, so EIA-860M now records **no coal retirement from January to September 2026**. PUDL's changelog had not yet taken in September, so this was read from EIA's own workbooks under a plan fixed in advance, with a gate: EIA's August 2026 workbook had to reproduce this page's August rows, and it did (16 of 16 plan generators with the same month, and no 2026 coal retirement). The gate and all three predictions held; details in [`coalsep.md`](coalsep.md).

In the September workbook, none of the 16 plan generators has retired. Culley 2 and Craig 1 moved from 2026-09 to 2026-12, and Schahfer 17-18 from 2026-10 to 2026-12, the months their DOE orders now expire. Sherburne County 1 and Comanche 2 are still dated 2026-12. Everything above this section is unchanged and still describes the August 2026 report.
