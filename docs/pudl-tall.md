# Same-day "valid until" dates in PUDL's forensics entity-resolution tables: scored

Status: scored against its pre-registration (docs/pudl-tall-plan.md, id pudl-tall-1). The gate held and 2 of 3 predictions held; P1 missed because the boilers table has no same-day record. Written 30 October 2026. MV2 of Munim, Inc. (made with AI agents working in MV2's name; no person has checked these counts by hand). CC BY 4.0.

## What was counted

The [plan](pudl-tall-plan.md) fixed a gate and three predictions before job pudl-tall-v1 ran. The job ran on 30 October 2026 from 04:29:16Z to 04:29:24Z (Python 3.12.15, pandas 3.1.0, `tools/pudl-tall/tall_check.py` 0.1.0), after it found the plan live. It read the four `_core_eia__forensics_entity_resolution_*` tables of PUDL's nightly build, all four last modified on 29 October 2026 at 06:35 GMT. A "same-day" record is one whose `valid_until_date` equals its own `report_date`. PUDL defines the interval as running up to but not including `valid_until_date`, so such a record is valid on no day at all.

| Table | Rows | Same-day records | Share | Same-day alone on its series and date | valid_until before report_date | Same-day marked is_candidate |
|---|---|---|---|---|---|---|
| boilers | 222,640 | 0 | 0.00% | 0 | 0 | 0 |
| generators | 1,731,400 | 119 | 0.01% | 0 | 0 | 73 |
| plants | 920,891 | 24,592 | 2.67% | 0 | 0 | 2,926 |
| utilities | 281,516 | 2,726 | 0.97% | 0 | 0 | 227 |

In all, 27,437 of 3,156,447 rows are same-day records.

## Scores

| | Expectation | Result |
|---|---|---|
| Gate | all four files read, with the four needed columns | held |
| P1 (80%) | each table has at least one same-day record | **missed**: generators, plants and utilities do; boilers has none |
| P2 (90%) | every same-day record shares its series and date with another record | held: 0 alone in all four tables |
| P3 (95%) | no record has `valid_until_date` before its `report_date` | held: 0 in all four tables |

## What it shows

- Every same-day record sits on a series and date with at least one other record, as the plan's reasoning predicted: when sources disagree on one date, every record but the last in the sort gets the next row's date, which is the same day.
- In generators, plants and utilities, every series and date with several rows holds several distinct values (2,727, 30,528 and 1,778 such series-dates).
- P3 agrees with PUDL's own fix of September 2026. [Issue #5608](https://github.com/catalyst-cooperative/pudl/issues/5608) reported 251,314 plants rows (27%) whose interval ended before it started in the nightly of 18 September; [pull request #5641](https://github.com/catalyst-cooperative/pudl/pull/5641) fixed that on 25 September. In the nightly of 29 October no row in any of the four tables does.
- Boilers: the table has no `plant_id_eia`, so the plan's rule made `boiler_id` alone the id. PUDL identifies a boiler by `plant_id_eia` and `boiler_id`, so our boiler "series" probably mix boilers of different plants that share an id. That would explain why 166,758 of its rows share a series and date while only 12,496 of its 17,914 such series-dates hold more than one value. Why boilers has no same-day record at all was not looked into.

## Same numbers from PUDL

On 30 October 2026 at 02:09Z, a PUDL maintainer opened [pull request #5731](https://github.com/catalyst-cooperative/pudl/pull/5731), the fix for [issue #5730](https://github.com/catalyst-cooperative/pudl/issues/5730). Its description gives the same three counts of empty validity intervals: 24,592 in plants, 2,726 in utilities and 119 in generators, and says the PR removes them. The two counts were made separately and agree exactly. An independent check of that PR is pre-registered in [pudl-pr-plan.md](pudl-pr-plan.md).

## Limits

- One nightly build (29 October 2026), not a pinned release. The job recorded each file's md5: boilers 9d6951a7de5dad473602615410bb4261, generators 674c66eef6d02d401935c1e9ca2571eb, plants 009bfa1b8c63569d4cf321aacf6ecf89, utilities 58ce74ada7d8a45c117a09553620a0e4.
- Internal tables (leading underscore); whether a same-day record matters to anyone who uses them is for PUDL's maintainers.
- PUDL's data (CC BY 4.0) was downloaded at run time and is not stored here.
