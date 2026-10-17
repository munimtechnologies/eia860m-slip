# Do EIA's planned retirement dates follow DOE's emergency orders? (pre-registration)

Made by MV2 of Munim, Inc. with AI agents, 2026-10-17. Written and published **before** the check has run. Code: Apache-2.0 (`order_dates.py` 0.1.0, to be added under `tools/order-dates/` with its results). This page and [`data/doe_202c_unit_orders.csv`](../data/doe_202c_unit_orders.csv): CC BY 4.0.

## Question

Since May 2025 the U.S. Department of Energy has used Federal Power Act section 202(c) to keep eight plants from retiring: J.H. Campbell 1-3 (MI), Eddystone 3-4 (PA), H.A. Wagner 4 (MD), Centralia 2 (WA), R.M. Schahfer 17-18 (IN), F.B. Culley 2 (IN), Craig 1 (CO) and Stanton 1 (FL). Each order lasts about 90 days and is renewed a few days before it expires. As of 2026-10-17, DOE's pages list 34 such plant orders (12 in 2025, 22 in 2026).

EIA's monthly generator inventory (Form EIA-860M) asks each owner for a planned retirement month. [`coal-rows.md`](coal-rows.md) found Campbell, Culley 2 and Craig 1 dated to the month their current order expires, both in the December 2025 inventory and in the August 2026 one. **Does that hold for every ordered unit in every month? If it does, the inventory's "planned retirements" for these units only reflect the order calendar, not owners' plans.** That matters to anyone who reads EIA-860M's planned retirements as a forecast, including EIA's own start-of-year articles: 2,570 MW of the 2026 coal plan is held open this way.

We found no earlier month-by-month comparison of EIA-860M planned retirement dates with 202(c) order expiries. Trackers of the orders exist (DOE's own pages; [POWER's log](https://www.powermag.com/doe-has-issued-more-than-40-section-202c-emergency-orders-since-may-2025-heres-an-updated-log/); [State Power Project](https://statepowerproject.org/challenges-to-doe-202c-orders/)), but none of them compares the orders with EIA's generator records.

## Data and method

- **Orders:** [`data/doe_202c_unit_orders.csv`](../data/doe_202c_unit_orders.csv), every plant-specific order on DOE's [2025](https://www.energy.gov/ceser/2025-doe-202c-orders) and [2026](https://www.energy.gov/ceser/2026-doe-202c-orders) pages, read on 2026-10-17. System-wide orders (heat, cold, data-centre backup, Puerto Rico, Guam) are left out. The first Campbell and Eddystone orders do not state an expiry on DOE's page; the CSV uses 21 and 28 August 2025, the expiries reported for them.
- **Generators:** PUDL's EIA-860M changelog, the same copy that [`coal-rows.md`](coal-rows.md) used (downloaded 2026-10-15, reports to August 2026).
- **Units:** matched by plant name, state and generator ID: Campbell 1, 2, 3; Schahfer 17, 18; Craig 1 or C1; Culley 2; Eddystone 3, 4; Centralia BW22 or 22; Wagner 4 or ST4; Stanton 1. For coal plants, only plant IDs with coal records are used. If no listed ID matches, the fallback is fixed in advance: the plant's generators that were operating with a planned retirement in 2025-2026 in the report before its first order.
- **Comparison:** for each unit and each monthly report from the month of the plant's first order on, the order in force is the latest-issued order for the plant whose issue date is on or before the report month's last day and whose expiry is on or after it. The unit's planned retirement month is then classed against that order's expiry month as exact, +1, -1, later or earlier. Records that are retired, not operating, undated, unlisted, or that fall in a month with no order in force (Wagner, January to April 2026) are counted but not scored.

## Checks (they must pass for the predictions to count)

- **C1:** every one of the 8 plants matches at least one generator.
- **C2:** the August 2026 planned months reproduce [`data/coal_plan_2026_followup.csv`](../data/coal_plan_2026_followup.csv): Campbell 2026-11, Schahfer 2026-10, Culley 2026-09, Craig 2026-09.
- **C3:** the changelog has 224,408 records after preparation, as in coal-rows. If not, the copy changed; we will say so and give both counts.

## Predictions

- **P1:** among scored unit-months, at least 50% are dated exactly to the expiry month.
- **P2:** at least 75% are exact or one month later.
- **P3:** no covered unit is reported retired in a month with an order in force.
- **P4:** at least 6 of the 8 plants have a unit whose planned month changes at least twice while under orders. In other words, the dates ratchet rather than sit still.
- **P5 (scored once the September 2026 report is in the data; EIA's release is due 2026-10-23):** at least 3 of these 4 plants are dated exactly to the expiry of the order in force on 30 September: Campbell 2026-11 (order 202-26-39), Schahfer 2026-12 (202-26-46), Culley 2026-12 (202-26-47) and Craig 2026-12 (202-26-49).

## What we already knew

These thresholds were set after seeing 8 plant-months in coal-rows: the December 2025 and August 2026 dates of the 4 coal plants in the 2026 plan. Campbell, Culley 2 and Craig 1 were exact both times. Schahfer was not: it was dated 2026-06 in December 2025 against an order expiring in March, and 2026-10 in August against one expiring in September. Every other unit-month, all four other plants, and every month before August 2026 had not been looked at.

## Context, not scored

On 2026-09-11 the D.C. Circuit vacated DOE's first Campbell order (202-25-3), holding that 202(c) does not let DOE override a state-approved retirement ([Michigan Attorney General](https://www.michigan.gov/ag/news/press-releases/2026/09/11/federal-appeals-court-vacates-first-doe-order-forcing-operation-of-jh-campbell-coal-plant); [Utility Dive](https://www.utilitydive.com/news/appeals-court-vacates-doe-emergency-order-michigan-power-plant/830189/)). The current Campbell order, 202-26-39, runs to 2026-11-14. Challenges to the Indiana, Pennsylvania, Washington and Colorado orders are pending. None of this changes the method above. It does make the next renewals less certain, so the September and October inventories are worth reading closely.

## Limits

- A unit dated to its order's expiry month may just be the owner's best guess. The check measures what the records show, not why.
- The order in force is judged on the last day of the report month. Owners file later, so a renewal issued after month-end but before filing could explain some +3 month gaps. The month-by-month output shows each case.
- Generator IDs come from public sources and are not confirmed. The output lists every plant ID matched next to the ID we expected.
