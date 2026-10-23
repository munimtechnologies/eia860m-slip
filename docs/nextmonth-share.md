# Generators planned for next month: how many are operating in it? A monthly series, August 2015 to August 2026

Status: descriptive. Nothing here was predicted in advance. Every number below is recomputed from the job's raw output by the doc test [`test_nextmonth_share_doc.py`](../test_nextmonth_share_doc.py).

Made by MV2 of Munim, Inc. with AI agents working in his name. Text: CC BY 4.0. Data: [`data/monthcheck_months_2026-08.csv`](../data/monthcheck_months_2026-08.csv) (CC BY 4.0), written on 23 October 2026 by job monthcheck-dry-v1, the practice run of [`tools/annual-flows-candidate/monthcheck.py`](../tools/annual-flows-candidate/monthcheck.py) 0.1.0 (Apache-2.0, commit e027d6b) on EIA's August 2026 workbook. The job's own report is [`docs/monthcheck-dry-v1-output.md`](monthcheck-dry-v1-output.md). As practice it scored the four bars of [`docs/sep2026-plan.md`](sep2026-plan.md) on August 2026, a month already published: 4 of 4 held. That checks the code; it is not a test of anything.

## The measure

The **next-month cohort** of month M is every generator that EIA's EIA-860M workbook for the month before M listed on its Planned sheet with planned operating month M. The **share to Operating** is the fraction of that cohort, by count, that the workbook for M lists on its Operating sheet. These are the definitions in [`docs/sep2026-plan.md`](sep2026-plan.md). The job replays EIA's 134 monthly workbooks from July 2015 to August 2026 (the copies in PUDL's raw archive, Zenodo record 22995197, md5-checked; the August 2026 copy is byte-identical to EIA's own file), so the series has 133 months, August 2015 to August 2026.

## By year

Each year pools its months: the cohorts are summed, and so are the generators listed as Operating in their planned month.

| year | months | cohort | to Operating | share |
|---|---|---|---|---|
| 2015 | 5 | 347 | 187 | 0.539 |
| 2016 | 12 | 951 | 457 | 0.481 |
| 2017 | 12 | 1171 | 557 | 0.476 |
| 2018 | 12 | 1066 | 527 | 0.494 |
| 2019 | 12 | 1035 | 439 | 0.424 |
| 2020 | 12 | 1260 | 540 | 0.429 |
| 2021 | 12 | 1566 | 586 | 0.374 |
| 2022 | 12 | 1326 | 428 | 0.323 |
| 2023 | 12 | 1510 | 490 | 0.325 |
| 2024 | 12 | 1625 | 592 | 0.364 |
| 2025 | 12 | 1586 | 600 | 0.378 |
| 2026 | 8 | 1194 | 366 | 0.307 |

2015 covers August to December and 2026 January to August. Over all 133 months: 5,769 of 14,637 (0.394).

## What the series shows

- **The share fell.** In 2016-2019, 1,980 of 4,223 (0.469) generators planned for the next month were listed as operating in it. In 2022-2025 it was 2,110 of 6,047 (0.349). Every year from 2021 to 2026 (2026 to August) is below every year from 2016 to 2020: the lowest of 2016-2020 was 0.424 (2019) and the highest of 2021-2026 was 0.378 (2025). Over the same years the yearly cohort grew from 951 in 2016 to 1,586 in 2025.
- **December stands out.** In each of the ten years 2016 to 2025, December's cohort was the largest of its year, and December's share was above its year's pooled share. The 11 Decembers from 2015 to 2025 together: 1,238 of 2,211 (0.560). The other 122 months: 4,531 of 12,426 (0.365).
- **The fall is not a December effect.** Leaving out December, 2016-2019 gives 1,508 of 3,495 (0.431) and 2022-2025 gives 1,694 of 5,172 (0.328).

Whether December keeps its pattern in 2026 is pre-registered in [`docs/dec2026-plan.md`](dec2026-plan.md), before EIA publishes any month after August 2026.

## The September 2026 band

Applied to the 24 months September 2024 to August 2026, the P4 rule of [`docs/sep2026-plan.md`](sep2026-plan.md) (second lowest to second highest share, both ends included) gives the band 0.2195 to 0.4740. Those are October 2024 and December 2025. This note was written before EIA published its September 2026 workbook, and it changes nothing in that plan; the band is the plan's own rule applied to months already published.

## Prior art

- EIA's Today in Energy has reported, for utility-scale solar only and by capacity, the share of planned capacity whose developers reported a delay: 19% on average in 2023 against 23% in 2022 (https://www.eia.gov/todayinenergy/detail.php?id=62003), and about 20% in the third quarter of 2025 against 25% a year earlier (https://www.eia.gov/todayinenergy/detail.php?id=66604, 10 November 2025). That measure differs from this one (a reported delay among all planned solar capacity, against operating in the planned month for the next month's cohort of every technology), so the two series cannot be compared number for number.
- EIA's Today in Energy of 21 June 2018 (https://www.eia.gov/todayinenergy/detail.php?id=36513) found that 78% of the capacity planned for 2017 in the annual EIA-860 came online that year: a whole-year measure, for one year.
- In this repository, [`docs/stage-leadtime.md`](stage-leadtime.md) pooled report months January 2016 to June 2023 by construction stage and lead time, with no breakdown by year or calendar month, and [`docs/annual-flows.md`](annual-flows.md) scored January's plan for the whole year.
- A web search on 23 October 2026 found no published monthly series, for all technologies, of how many generators planned for the next month are listed as operating in it.

## Limits

- **Count, not capacity.** The data file also has MW columns (filled from May 2016); they are not analysed here.
- **Generators are not independent.** One plant can have many generators that move together, so one large project can swing a month. No significance test is offered.
- **The mix changed.** Far more solar and battery generators are planned now than in 2016. This note does not split the series by technology, so it cannot say whether projects now slip more often or whether different kinds of projects are being planned. Association, not cause.
- **Listed, not dated.** A generator that starts in its planned month but is first listed as operating a month later counts as not operating. One that starts early is already on the Operating sheet the month before and is not in the cohort at all. Generators that move to the Canceled or Postponed sheet count as not operating.
- **December.** Year-end deadlines in contracts and tax rules are a common explanation for year-end start-ups; nothing here tests it.
- The series is rebuilt from EIA's workbooks by this repository's own code; that is a reproducibility check, not an independent one. The months around EIA's November 2024 gap (see [`docs/heldtrace.md`](heldtrace.md)) are kept as they are.
