# Pre-registration: is the fall in EIA-860M's next-month share inside technologies, or a change of mix?

Status: pre-registered, not yet scored.

Fixed on 23 October 2026, before job nexttech-v1 reads the technology of any generator in a next-month cohort. The job's first step polls this file's address on GitHub and computes nothing until it is served, so the commit time of this file is the record of when the bars below were fixed. They will not be moved after the job runs.

Made by MV2 of Munim, Inc. with AI agents working in his name. Text: CC BY 4.0. Code: [`tools/annual-flows-candidate/nexttech.py`](../tools/annual-flows-candidate/nexttech.py) 0.1.0 (Apache-2.0), with its tests. It reuses `monthcheck.py` 0.1.0 (its `replay`, unchanged), `retiredentry.py` 0.1.0 (its workbook reader) and `retiredgap.py` 0.1.0 (its sheet reader).

## Why

[`docs/nextmonth-share.md`](nextmonth-share.md) found that of the generators EIA-860M listed as planned for the next month, the share listed as operating in that month was 0.469 (1,980 of 4,223) in 2016-2019 and 0.349 (2,110 of 6,047) in 2022-2025, by count. Its limits said it does not split by technology, so it cannot say why. Two readings fit that result. Either each technology's generators came online on time less often, or the cohort moved toward technologies that always did so less often (for example more solar and batteries). This plan asks which, with a split fixed in advance.

## What was known when this plan was fixed

- The pooled shares above and the yearly series in `nextmonth-share.md`, and the September 2026 cohort (57 of 170) in [`docs/sep2026.md`](sep2026.md). None of them is split by technology.
- EIA's Today in Energy (8 May 2024, "U.S. electric power sector reported fewer delays for new solar capacity projects in 2023", https://www.eia.gov/todayinenergy/detail.php?id=62003) reports, by capacity, that the share of planned solar capacity whose online date developers pushed back rose through 2021 and 2022, peaking at 33% in December 2022, and averaged 19% in 2023 against 23% in 2022, still above the 2018-2021 average. So T1 below leans on a direction EIA has already reported for solar by another measure. That is a different measure (capacity, delays reported in a month) from this one (count, listed as operating in the planned month).
- Earlier results in this repository score whole years and capacity by technology (for example [`docs/headline-plans.md`](headline-plans.md)). None of them gives the next-month share by technology or by period.
- Nothing about the technology mix of the next-month cohorts in any period.

## What the job does

`nexttech.py` 0.1.0 downloads the rebuilt changelog [`../data/eia860m_changelog_from_workbooks.csv.gz`](../data/eia860m_changelog_from_workbooks.csv.gz) at commit a3ce085 (version 0.1.1, 117,756 rows) and replays it once with `monthcheck.replay`, keeping every month's next-month cohort: the generators that the month before listed on the Planned sheet with that month as their planned operating month, and where this month lists them. For each cohort month it reads the workbook of the month before from PUDL's raw archive (md5-checked as before) and takes each cohort generator's technology from it. Technologies are grouped as:

- **solar:** "Solar Photovoltaic";
- **batteries:** "Batteries";
- **gas:** every technology whose name starts with "Natural Gas", and "Other Natural Gas";
- **wind:** every technology whose name contains "wind";
- **other:** everything else, including a generator whose technology is missing.

Periods are by the cohort's month: 2016-2019 is January 2016 to December 2019, and 2022-2025 is January 2022 to December 2025, as in `nextmonth-share.md`. Counts are generators; MW is reported but not scored.

## Check (not a prediction)

- **T0.** The all-technology counts reproduce `nextmonth-share.md` exactly: 1,980 of 4,223 in 2016-2019 and 2,110 of 6,047 in 2022-2025, and at most 1% of each period's cohort has no technology in the workbook of the month before. If T0 fails, T1 to T4 are reported as not scored and the job is fixed and run again under a new version.

## Predictions

- **T1.** Solar: the share listed as operating in the planned month is lower in 2022-2025 than in 2016-2019.
- **T2.** Gas: the same, lower in 2022-2025 than in 2016-2019.
- **T3.** Batteries: the same, lower in 2022-2025 than in 2016-2019.
- **T4.** Most of the fall is inside technologies. Weight the 2022-2025 share of each technology group by that group's share of the 2016-2019 cohort (direct standardization over the five groups). The within-technology fall, the 2016-2019 share minus that standardized share, is at least half the total fall (the 2016-2019 share minus the 2022-2025 share).

T1 to T3 each need at least 30 generators in each period; a technology with fewer is reported as not scored. T4 is not scored if a group that has a 2016-2019 cohort has no 2022-2025 cohort. Results are reported as "N of the scored predictions held".

## How each could fail

T1 to T3 fail if a technology's share held steady or rose, which would put the fall in the mix or in the other technologies. T4 fails if the standardized share is closer to the 2022-2025 share than to the 2016-2019 share, which would mean the move toward technologies that were always less often on time explains most of the fall. Both outcomes are reported the same way.

## Limits

- Technology is taken from the month before, when the generator was listed as planned. A technology edited later is not followed.
- Counts weigh a 1 MW generator like a 1,000 MW one. MW shares are reported for each period and group but are not scored.
- Generators at one plant are not independent, so no significance test is given. The split is an association, not a cause.
- The changelog is rebuilt by this repository's own code from the same archive. T0 checks that the replay gives the published numbers; it is a reproducibility check, not an independent one.
- Direct standardization with five groups is coarse: a mix shift inside a group (for example from combined-cycle to small engines inside gas) counts as "within".
