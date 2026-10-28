# Will DOE renew its eleven open 202(c) orders in time? Ten forecasts, stated in advance

Status: pre-registered, not yet scored. Written on 28 October 2026, when the newest order on DOE's page was 202-26-50 (12 October). MV2 of Munim, Inc.; this plan and its test were made with AI agents working in my name.

## What is forecast

On 28 October 2026, eleven DOE orders under section 202(c) of the Federal Power Act were still in force: eight plant orders and three island orders ([`data/doe_202c_orders.csv`](../data/doe_202c_orders.csv)). Each runs about 90 days. For each one we give our chance that DOE renews it in time: that DOE's orders pages list a new order or an extension for the same plant (for the islands, the same recipient) with an issue date on or before the day the current order expires. The two Puerto Rico orders count as one forecast, which holds only if both are renewed.

| # | order | plant or recipient | expires | our chance it is renewed in time |
|---|---|---|---|---|
| R1 | 202-26-38 | Guam Power Authority | 2026-11-04 | 60% |
| R2 | 202-25-1E and 202-25-2E | PREPA | 2026-11-07 | 90% |
| R3 | 202-26-39 | J.H. Campbell | 2026-11-14 | 85% |
| R4 | 202-26-25A | H.A. Wagner | 2026-11-17 | 65% |
| R5 | 202-26-40 | Eddystone | 2026-11-20 | 90% |
| R6 | 202-26-42 | Stanton Energy Center | 2026-11-30 | 85% |
| R7 | 202-26-44 | Centralia | 2026-12-11 | 90% |
| R8 | 202-26-46 | R.M. Schahfer | 2026-12-18 | 90% |
| R9 | 202-26-47 | F.B. Culley | 2026-12-18 | 90% |
| R10 | 202-26-49 | Craig | 2026-12-25 | 90% |

Our expected count is 8.35 renewals in time out of 10.

**T1 (timing).** Every renewal in time among R1 to R10 is dated 0 to 3 days before the expiry of the order it follows. Our chance: 75%.

## The record these numbers start from

- **Plant orders.** Following each plant's orders in issue-date order gives 26 cases where one order was followed by another. In 25 of 26 the next order was issued on or before the day the earlier one expired, 0 to 3 days before it (0 days: 9; 1 day: 9; 2 days: 4; 3 days: 3). The one exception is Wagner: 202-25-6A expired on 31 December 2025, and the next Wagner order, 202-26-25, was issued on 21 May 2026.
- **Puerto Rico.** Both PREPA series were extended four times each after their first dated expiry, every time 0 to 2 days before expiry (8 of 8).
- **Guam.** 202-26-38 is the first and only Guam order, issued on 5 August 2026 after the Guam Power Authority applied on 4 August (DOE's order page). There is no renewal on record to learn from.
- **After the court ruling.** The D.C. Circuit vacated Campbell's first order on 11 September 2026. Since that day DOE has issued 4 plant orders (Centralia on 11 September, Schahfer and Culley on 18 September, Craig on 25 September), each renewing an order that was about to expire. DOE has asked the full court to rehear the case (as reported by Bloomberg Law and The Baseload; we did not see the docket). See [`doe-202c-court.md`](doe-202c-court.md).

A forecaster who gave every case the plant base rate, 25 of 26 (96%), would have been right every time but once. Our numbers are lower than that where we see a reason:
- **R1, Guam, 60%:** a first order made on the utility's own application, with no renewal history; we found no report either way of a new application.
- **R3, Campbell, 85%:** the plant whose first order the court vacated. DOE kept renewing other plants' orders after the ruling and is fighting it, which is why this is still high.
- **R4, Wagner, 65%:** Wagner's orders lift a run-hour limit instead of holding off a retirement (see [`doe-202c-rehearing.md`](doe-202c-rehearing.md)), and Wagner's is the only plant line that has lapsed, over the last winter.
- **R6, Stanton, 85%:** only one renewal so far.

These ten forecasts are not independent. A ruling by the full court, a stay, or a change of policy at DOE would move all of them together, so ten outcomes are a weak test of our calibration. We say this now so the score is read that way.

## How it is scored

- R1 to R6 are scored on 1 December 2026, and R7 to R10 and T1 on 1 January 2027, from DOE's pages of 2026 orders (energy.gov/ceser/2026-doe-202c-orders) and, for Puerto Rico, the PREPA order page.
- A renewal issued after the expiry date counts as not in time, and is reported as late. An order that covers several plants counts for each plant it names.
- For each forecast we report the outcome (1 renewed in time, 0 not) and its Brier score, (chance - outcome) squared, then the mean over the ten. We report the same for the constant 96% forecast. If all ten renew, the constant forecast beats ours, and we will say so.
- These forecasts sit beside H1 to H4 in [`doe-202c-rehearing.md`](doe-202c-rehearing.md) (DOE's answers to rehearing requests) and F1 in [`coalsep-plan.md`](coalsep-plan.md) (a first order for Sherburne County 1); they do not replace them.

## Prior art

Trackers already log these orders: the State Power Project's page on the challenges, the State Impact Center's tracker (archived on 31 August 2026), POWER magazine's log, and the Capture Cascade timeline. On 28 October 2026 we found no published probability for each renewal, and no prediction market on them. Lawyers and the utilities know their own plants; what this adds is a dated, checkable forecast for every open order, scored in public.

Text: CC BY 4.0. [`test_renew_plan_doc.py`](../test_renew_plan_doc.py) (Apache-2.0) checks the table, the counts and the lead times on this page against [`data/doe_202c_orders.csv`](../data/doe_202c_orders.csv).
