# Every DOE 202(c) emergency order of 2025-2026, as one table

Status: description (the counts below are not predictions); three predictions about the renewals due from 14 November 2026 are stated in advance at the end. Table as of 18 October 2026. MV2 of Munim, Inc.; the table, code and this note were made with AI agents working in my name.

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

## Stated in advance (18 October 2026), scored on 1 January 2027

- **R1.** At least seven of the eight plants receive a new order that starts no later than the day after the current one expires.
- **R2.** Every new plant order that starts between 19 October and 31 December 2026 expires 89 or 90 days after it starts.
- **R3.** At least one plant not yet under a 202(c) order receives its first plant order between 19 October and 31 December 2026. (Four plants got their first orders in December 2025, as their retirement dates came up.)

## Prior art and limits

DOE publishes the orders as web text. POWER magazine kept a log of orders and extensions with capacity and fuel (43 entries as of 2 April 2026); the State Impact Center tracks state attorneys general's actions on the orders; ERCOT, PJM and others post their own orders. On 19 October 2026 we found no machine-readable table of every 2025-2026 order with its dates, and no count of how many days event orders were in force or of gaps between plant renewals. If you know of one, open an issue.

Limits: the table was transcribed from DOE's list pages, not from each order's PDF, so the start dates of six 2025 orders (202-25-1 to 202-25-6) and the expiries of the first two PREPA orders are missing from the pages and marked in the notes (the expiries of the first Campbell and Eddystone orders come from the earlier unit-order table). Kinds and areas are our labels. Days in force count whole calendar days, so an order that starts at 11:59 PM counts that day. The causes of event orders (cold, heat, maintenance outages) are not on the list pages and are not in the table.

Run: `python -m unittest -v test_orders_202c && python orders_202c.py --out-dir out --as-of 2026-10-18`. Data: CC BY 4.0. Code: Apache-2.0.
