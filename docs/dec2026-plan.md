# Pre-registration: does December keep its pattern in 2026?

Status: pre-registered, not yet scored.

Fixed on 23 October 2026. At about 15:30 UTC that day EIA's EIA-860M page (https://www.eia.gov/electricity/data/eia860m/) still showed August 2026 as its latest month, so no workbook for any month after August 2026 had been published. The commit time of this file on GitHub is the record of when the bars below were fixed. They will not be moved after the job runs.

Made by MV2 of Munim, Inc. with AI agents working in his name. Text: CC BY 4.0. Code: [`tools/annual-flows-candidate/monthcheck.py`](../tools/annual-flows-candidate/monthcheck.py) 0.1.0 (Apache-2.0), with its tests.

## Why

[`docs/nextmonth-share.md`](nextmonth-share.md) found that in each of the ten years 2016 to 2025, December's next-month cohort was the largest of its year, and December's share to Operating was above its year's pooled share. That pattern was found by looking at the data, so nothing tested it. This plan tests whether it holds in a year whose December has not been published.

## Predictions for December 2026

Definitions as in [`docs/sep2026-plan.md`](sep2026-plan.md): the next-month cohort of month M is every generator that the workbook for the month before M listed on its Planned sheet with planned operating month M; its share to Operating is the fraction of it, by count, that the workbook for M lists on its Operating sheet.

- **D1.** December 2026's next-month cohort is larger than the next-month cohort of every month from January to November 2026.
- **D2.** December 2026's share to Operating is above the pooled share to Operating of January to November 2026: the generators listed as Operating in their planned month, summed over those eleven months, divided by the sum of their eleven cohorts.

The two bars are counted separately and reported as "N of 2 held".

## How it will be scored

`monthcheck.py` 0.1.0 is run on the rebuilt changelog after EIA's December 2026 workbook is appended to it, with September, October and November 2026 appended before it, each from EIA's own file (first bytes, size and md5 recorded). EIA's monthly schedule puts the December 2026 workbook in late January 2027. If any of the four workbooks cannot be read, the plan is reported as not scored until it can be; a bar is never scored on a partial year. The scored note will be a new file, `docs/dec2026.md`. This plan will not be edited after its run.

## Could it fail?

Yes. In 2022 December's share was 0.339 against the year's 0.323, a small margin. In 2019, 2021 and 2022 a month other than December had the highest share of its year, which is why D2 is set against the year's pooled share rather than its best month. For D1, the largest cohort of January to August 2026 so far is June 2026's 216, larger than December 2025's 192.

## Limits

- The pattern was chosen after seeing ten years of it. A hold says it persisted for one more year; it does not explain it.
- Generators are not independent: one plant can have many generators that move together, so one large project can decide either bar.
- The changelog is rebuilt by the same code that wrote it; that is a reproducibility check, not an independent one.
