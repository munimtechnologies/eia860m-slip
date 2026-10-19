# Every DOE 202(c) emergency order of 2025-2026, as one table

Status: description (the counts below are not predictions); three predictions about the renewals due from 14 November 2026 are stated in advance at the end. Table as of 18 October 2026 (DOE's 2026 list re-checked on 19 October: no new orders). MV2 of Munim, Inc.; the table, code and this note were made with AI agents working in my name.

## What this is

Under section 202(c) of the Federal Power Act, the U.S. Department of Energy can order a utility or grid operator to run generation it would otherwise not run. DOE lists its orders on two web pages, [2025](https://www.energy.gov/ceser/2025-doe-202c-orders) and [2026](https://www.energy.gov/ceser/2026-doe-202c-orders), as text. [`data/doe_202c_orders.csv`](../data/doe_202c_orders.csv) puts every order, extension and amendment on those pages in one row each (85 rows): number, kind, area, recipient, plant, dates issued, in force and expiring, the expiry time where given, the source page and a note. [`orders_202c.py`](../orders_202c.py) (standard library only) checks the table and prints the counts below; [`test_orders_202c.py`](../test_orders_202c.py) checks the code on a hand-built table and checks these counts against the CSV.

Three kinds:

- **plant** (34 rows): orders that name a plant's units, keep them available, run about 90 days and are renewed. Eight plants: J.H. Campbell (MI), Eddystone 3-4 (PA), H.A. Wagner (MD), Centralia 2 (WA), R.M. Schahfer 17-18 and F.B. Culley 2 (IN), Craig 1 (CO) and Stanton 1 (FL). These are the 34 orders in [`data/doe_202c_unit_orders.csv`](../data/doe_202c_unit_orders.csv), which the eighth result ([`docs/order-dates.md`](order-dates.md)) compared with EIA-860M; the plant rows here match them.
- **event** (38 rows): short orders to a grid operator or utility, in force for 2 to 16 calendar days, letting it run units past permit limits or call on backup generation during an emergency.
- **island** (13 rows): the 90-day system orders for Puerto Rico (PREPA, two orders renewed together) and one for Guam.

Days are calendar dates, with the start and end dates both counted; the times of day are kept in the table but not used. Where DOE's page gives no start date, the issue date is used (noted in the row).

## What the table shows

- **2026 so far: 66 orders, extensions and amendments** (22 plant, 37 event, 7 island), against 19 in all of 2025 (12 plant, 1 event, 6 island).
- **Event orders come in episodes.** The 37 event orders of 2026 fall into nine runs of overlapping or back-to-back days in force. The first, 24 January to 14 February, holds 21 of them across six areas (ERCOT, PJM, ISO-NE, NYISO, Duke and five Florida utilities). The others: 18-20 May (PJM), 11-12 June (Duke), 30 June-7 July (PJM and Duke, 5 orders), 14-21 July (PJM, SPP), 26 July-10 August (SPP), 1-8 September (PJM, Duke), 17-21 September (PJM, Duke) and 13-16 October (PJM).
- **On 76 of the 291 days of 2026 up to 18 October, at least one event order was in force somewhere.**
- **PJM received the most event orders in 2026: 13** (66 order-days), then Duke 8, Florida utilities 7, ERCOT 3, SPP 3, ISO-NE 2, NYISO 1.
- **Plant orders are renewed back to back.** Of 26 renewals, 25 started the day the previous order expired or the day after. The one gap is Wagner: its order ran out on 31 December 2025 and the next began on 22 May 2026, leaving 1 January to 21 May (141 days) uncovered. Campbell has been under order continuously since 23 May 2025 (541 days to its current expiry); Eddystone since 30 May 2025.
- **33 of the 34 plant orders expire 89 or 90 days after they start**: every one up to 202-26-16 (February 2026) ran 90 days, and all 21 since then 89. Section 202(c)(4) of the Act limits orders that may conflict with environmental law to 90-day periods, renewable. The exception is Wagner's 2025 extension (66 days, to 31 December 2025).
- **DOE's own 2026 list leaves out one order.** ERCOT's page lists an amended order, 202-26-01A (customer-owned backup generation, 25 to 27 January 2026), that DOE's list does not; it is in the table with that note.

Current plant orders expire: Campbell 14 November, Wagner 17 November, Eddystone 20 November, Stanton 30 November, Centralia 11 December, Schahfer and Culley 18 December, Craig 25 December 2026.

## The court ruling on the first Campbell order (added 19 October 2026)

On 11 September 2026 the U.S. Court of Appeals for the D.C. Circuit vacated DOE's first Campbell order, 202-25-3 of 23 May 2025, in *People of the State of Michigan v. U.S. Department of Energy* (No. 25-1159). The court held that the long-term resource adequacy risks DOE cited were not an emergency under section 202(c), which it read as a limited backstop ([Utility Dive, 11 September 2026](https://www.utilitydive.com/news/appeals-court-vacates-doe-emergency-order-michigan-power-plant/830189/); [ArentFox Schiff, 16 September 2026](https://www.afslaw.com/perspectives/energy-cleantech-counsel/dc-circuit-decision-emphasizes-limits-does-emergency-grid)). Only that first order was before the court; challenges to the later Campbell orders were held in abeyance. DOE's 2026 list still shows the newest Campbell order, 202-26-39, in force to 14 November 2026; the press we read does not say whether DOE will seek further review.

The 18 October version of this note did not mention the ruling. It changes no row or count in the table: the CSV lists orders as DOE issued them, and a vacated order stays in it. It does bear on R1 below, since Campbell's renewal is due on 14 November. R1 stays as written and will be scored by its letter.

## Megawatts under plant orders, day by day (added in 0.2.15)

[`data/doe_202c_plant_mw.csv`](../data/doe_202c_plant_mw.csv) gives each plant's covered units their summer capacity and primary fuel as EIA-860M listed them in the last monthly report before the plant's first order (the same generators and figures as the order-dates check, [`docs/order-dates-output-v2.md`](order-dates-output-v2.md)). `orders_202c.py` 0.2.0 counts, for each calendar day, the summer MW of plants with a plant order in force. Up to 18 October 2026:

| from | plants under order | MW | of which coal |
|---|---|---|---|
| 2025-05-23 | 1 (Campbell) | 1,330.5 | 1,330.5 |
| 2025-05-30 | 2 (+ Eddystone 3-4) | 2,090.5 | 1,330.5 |
| 2025-07-28 | 3 (+ Wagner 4) | 2,487.5 | 1,330.5 |
| 2025-12-16 | 4 (+ Centralia 2) | 3,157.5 | 2,000.5 |
| 2025-12-23 | 6 (+ Schahfer 17-18, Culley 2) | 3,969.5 | 2,812.5 |
| 2025-12-30 | 7 (+ Craig 1) | 4,396.5 | 3,239.5 |
| 2026-01-01 | 6 (Wagner's gap) | 3,999.5 | 3,239.5 |
| 2026-05-22 | 7 (Wagner again) | 4,396.5 | 3,239.5 |
| 2026-06-04 | 8 (+ Stanton 1) | 4,849.9 | 3,692.9 |

- **Since 4 June 2026 all eight plants have been under order at once: 4,849.9 MW of summer capacity**, 3,692.9 MW of it coal (Campbell, Centralia, Schahfer, Culley, Craig, Stanton); the rest is Eddystone 3-4 (760 MW, gas and oil) and Wagner 4 (397 MW, oil).
- **2,665 plant-days and 1,827,592.8 MW-days of capacity held under order** from 23 May 2025 to 18 October 2026, about 5.01 GW-years; 1,320,393.8 MW-days of it coal. Campbell alone is 514 days and 37% of the MW-days.
- This is capacity ordered to stay available, not energy produced. Utility Dive ([23 June 2026](https://www.utilitydive.com/news/doe-202c-power-plants-centralia-campbell-schahfer/822062/)) reported from EIA data that Campbell had run at a 46% capacity factor since 1 June, against a nearly 66% average for the same periods of the four years before, and quoted TransAlta (29 April) that Centralia "hasn't produced electricity since the DOE ordered it to be available starting Jan. 1." How much the covered units generated month by month is the subject of a separate check, pre-registered before it runs: [`docs/gen-202c-preregistration.md`](gen-202c-preregistration.md).

Other trackers give different totals because they count different things: POWER's log gave "at least 4.4 GW" of coal retirements stalled as of April 2026 (before Stanton's order), and other lists use nameplate or owner figures (Campbell 1,420 or 1,560 MW against EIA's 1,330.5 MW summer). The tests check the table, the plant-days and MW-days and the per-plant day counts in this section against the CSVs.

## Stated in advance (18 October 2026), scored on 1 January 2027

- **R1.** At least seven of the eight plants receive a new order that starts no later than the day after the current one expires.
- **R2.** Every new plant order that starts between 19 October and 31 December 2026 expires 89 or 90 days after it starts.
- **R3.** At least one plant not yet under a 202(c) order receives its first plant order between 19 October and 31 December 2026. (Four plants got their first orders in December 2025, as their retirement dates came up.)

## Prior art and limits

DOE publishes the orders as web text. POWER magazine kept a log of orders and extensions with capacity and fuel (43 entries as of 2 April 2026); the State Impact Center tracks state attorneys general's actions on the orders; ERCOT, PJM and others post their own orders. On 19 October 2026 we found no machine-readable table of every 2025-2026 order with its dates, no count of how many days event orders were in force or of gaps between plant renewals, and no day-by-day series of the EIA-listed capacity under plant orders. If you know of one, open an issue.

Limits: the table was transcribed from DOE's list pages, not from each order's PDF, so the start dates of six 2025 orders (202-25-1 to 202-25-6) and the expiries of the first two PREPA orders are missing from the pages and marked in the notes (the expiries of the first Campbell and Eddystone orders come from the earlier unit-order table). Kinds and areas are our labels. Days in force count whole calendar days, so an order that starts at 11:59 PM counts that day. The causes of event orders (cold, heat, maintenance outages) are not on the list pages and are not in the table. The MW figures are one EIA-860M snapshot per plant (summer capacity, or nameplate where summer is blank); they do not follow later re-ratings, and they cover only the units the order-dates check matched to each order. Court rulings are noted in the text, not in the table.

Run: `python -m unittest -v test_orders_202c && python orders_202c.py --out-dir out --as-of 2026-10-18`. Data: CC BY 4.0. Code: Apache-2.0.
