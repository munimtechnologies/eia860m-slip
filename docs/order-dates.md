# EIA's planned retirement dates for the plants DOE holds open are the order calendar

Made by MV2 of Munim, Inc. with AI agents, 2026-10-18. Code: Apache-2.0 ([`tools/order-dates/`](../tools/order-dates/)). This page and [`data/order_dates_v1.csv`](../data/order_dates_v1.csv): CC BY 4.0.

**Status: first run, one check failed.** The question, method, checks and predictions were published before the run in [`order-dates-preregistration.md`](order-dates-preregistration.md). Check C1 failed (Centralia was not matched; see [`order-dates-amendment.md`](order-dates-amendment.md)), so the predictions below are reported as description, not as scored results. A second run with Centralia's correct generator ID is queued; this page will be updated when it lands.

## Question

Since May 2025 DOE has issued 34 plant-specific Federal Power Act 202(c) orders, each lasting about 90 days, for eight plants. EIA's monthly generator inventory (Form EIA-860M) carries each operating generator's planned retirement month. Do those months reflect owners' plans, or just the expiry of the order in force?

## Result (EIA-860M reports May 2025 to August 2026)

- **101 of 126 scored unit-months (80%) were dated to the exact month the order in force expires; 107 (85%) to that month or the next.** At J.H. Campbell 1-3, Eddystone 3-4, Craig 1 and F.B. Culley 2 it was 95 of 98 (97%). At those four plants, each time DOE renewed an order the planned month moved three months later, to the new expiry.
- **No covered generator was reported retired while an order was in force** (for the seven plants matched).
- R.M. Schahfer 17-18 ran ahead of the orders: dated 2026-06 while the order ran to March 2026 (December 2025 to February 2026), then 2026-10 against a September expiry (June to August 2026).
- H.A. Wagner 4 is dated 2029 throughout. Its orders lift a run-hour limit on fuel oil; they do not defer a retirement, so this unit was never a test of the question (see the amendment). Without Wagner (not pre-registered): 101 of 116 exact (87%), 107 of 116 within a month (92%).
- Stanton 1 (FL) is listed as operating with no planned retirement month in June to August 2026, while under orders.
- Campbell's three misses were in the October 2025 report, which already gave February 2026: the expiry of the order DOE issued on 18 November. Owners file after month-end, so a report can reflect a renewal issued after the month it describes.

| plant | units | first order | orders | scored unit-months | exact | +1 | August 2026 report |
|---|---|---|---|---|---|---|---|
| J.H. Campbell (MI) | 1710/1-3 | 2025-05 | 6 | 48 | 45 | 0 | 2026-11 |
| Eddystone (PA) | 3161/3-4 | 2025-05 | 6 | 32 | 32 | 0 | 2026-11 |
| Craig (CO) | 6021/1 | 2025-12 | 4 | 9 | 9 | 0 | 2026-09 |
| F.B. Culley (IN) | 1012/2 | 2025-12 | 4 | 9 | 9 | 0 | 2026-09 |
| R.M. Schahfer (IN) | 6085/17-18 | 2025-12 | 4 | 18 | 6 | 6 | 2026-10 |
| H.A. Wagner (MD) | 1554/4 | 2025-07 | 4 | 10 | 0 | 0 | 2029-06 |
| Stanton (FL) | 564/1 | 2026-06 | 2 | 0 | 0 | 0 | no date |
| Centralia (WA) | not matched | 2025-12 | 4 | 0 | 0 | 0 | see amendment |

Every generator-month, with the order in force and its class, is in [`data/order_dates_v1.csv`](../data/order_dates_v1.csv); the full output is [`order-dates-output.md`](order-dates-output.md).

## Checks and predictions (first run)

| | stated before the run | first run |
|---|---|---|
| C1 | every plant matches at least one generator | **failed** (Centralia) |
| C2 | August 2026 months reproduce coal_plan_2026_followup.csv | passed |
| C3 | 224,408 changelog records, as in coal-rows | passed |
| P1 | at least 50% exact | 80% (description only) |
| P2 | at least 75% exact or +1 | 85% (description only) |
| P3 | none reported retired under an order | 0 (description only; Centralia unknown) |
| P4 | at least 6 of 8 plants change date twice or more | **missed**: 4 (Campbell, Eddystone, Craig, Culley) |
| P5 | September 2026 report: 3 of 4 coal plants exact | not yet scorable (EIA release due 2026-10-23) |

P1, P2 and P4 cannot change when Centralia is added (at most nine more unit-months). P4 missed because Schahfer changed once, Wagner's date is not tied to the orders, Stanton has no date, and Craig, Culley and Schahfer have only been under orders since December 2025.

## Why it matters

EIA-860M's planned retirements are often read as a forecast, including in EIA's own start-of-year articles. For the units DOE holds open they are not: they are the date the current emergency order runs out, renewed every 90 days. In the August 2026 report that covers 2,570 MW of the 2026 coal plan (Campbell, Schahfer, Craig 1, Culley 2). A user who counts "planned 2026 retirements" from EIA-860M should treat those rows as undated.

## Prior art

Trackers of the orders exist (DOE's own pages; [POWER's log](https://www.powermag.com/doe-has-issued-more-than-40-section-202c-emergency-orders-since-may-2025-heres-an-updated-log/); [State Power Project](https://statepowerproject.org/challenges-to-doe-202c-orders/)). We found no month-by-month comparison of EIA-860M planned retirement dates with the orders' expiry dates (searched 2026-10-17 and 2026-10-18).

## Limits

- The check shows what the records say, not why. An owner may simply report the order's end as its best guess.
- Generator IDs come from public sources; the output lists the plant IDs matched next to the IDs expected. Centralia's was wrong in this run.
- Data: PUDL's EIA-860M changelog (CC BY 4.0, Catalyst Cooperative), downloaded 2026-10-15, reports to August 2026. Orders: DOE's 2025 and 2026 202(c) pages, read 2026-10-17 ([`data/doe_202c_unit_orders.csv`](../data/doe_202c_unit_orders.csv)).
