# DOE's answers to rehearing requests on its 202(c) plant orders have all come after the orders expired

Status: description (the counts below are not predictions); four predictions are stated in advance at the end. Table as of 19 October 2026. MV2 of Munim, Inc.; the table, code and this note were made with AI agents working in my name.

## What this is

A party that wants a court to review a DOE order under section 202(c) of the Federal Power Act must first ask DOE for rehearing, within 30 days after the order is issued (section 313(a)). If DOE does not act within 30 days, the request may be deemed denied. Each plant order has its own page on energy.gov, which lists the requests and DOE's replies: a "Notice of Denial of Rehearing by Operation of Law and Providing for Further Consideration" (numbered with an A), and sometimes, later, an "Order Addressing Arguments Raised on Rehearing" (B; C at Centralia, whose B is an amended order).

[`data/doe_202c_rehearing.csv`](../data/doe_202c_rehearing.csv) records for each of the 34 plant orders in [`data/doe_202c_orders.csv`](../data/doe_202c_orders.csv) the date of the first request, who asked, the date and number of the notice, and the date and number of the order on rehearing, with the page each came from. [`rehearing_202c.py`](../rehearing_202c.py) (standard library only) joins it to the orders table, checks it and prints the counts below. [`test_rehearing_202c.py`](../test_rehearing_202c.py) checks the code on hand-built tables and checks every count here against the CSVs.

## What DOE's pages show

- **25 of the 33 plant orders whose 30-day window has closed drew at least one request for rehearing.** These are every order at Campbell (6) and Eddystone (6), the first three at Centralia, Schahfer, Culley and Craig, and Stanton's first. None of Wagner's four orders drew a request. PJM applied for those, Talen did not oppose them, and they lift a run-hour limit instead of holding off a retirement. Four orders from September have no request listed yet: Stanton 202-26-42, Centralia 202-26-44, and Schahfer and Culley 202-26-46 and 202-26-47 (see H4). Craig's 202-26-49 window runs to 25 October.
- **The requests came 19 to 30 days after the order (median 28).** They came from:
  - six state attorneys general (MI, MN, IL, WI, WA, CO);
  - public interest organizations at every challenged plant;
  - consumer advocates at Eddystone;
  - the Organization of MISO States and the Illinois Commerce Commission;
  - at Craig, the plant's own co-owners, Tri-State and Platte River Power Authority, on all three orders.
- **DOE answered 24 of the 25 with a notice that rehearing was denied by operation of law.** The notices came 31 to 46 days after the first request (median 34), and every one was issued before the order expired. The 25th, Eddystone's 202-26-40 (request filed 17 September), has no notice listed yet.
- **Only 10 of the 25 challenged orders have an order addressing the arguments, and all 10 came after the order they address had expired**: 18 to 135 days after (median 86). None came while the challenged order was in force. Another 13 challenged orders have expired with no such order. Two are still in force: Campbell 202-26-39 to 14 November and Eddystone 202-26-40 to 20 November.
- The latest two orders on rehearing, 202-26-19B and 202-26-20B (Schahfer and Culley, 16 October 2026), address orders that expired on 21 June, 117 days earlier.

| order addressed | plant | expired | order on rehearing | dated | days after expiry |
|---|---|---|---|---|---|
| 202-25-3 | J.H. Campbell | 2025-08-21 | (no number on the page) | 2025-09-08 | 18 |
| 202-25-7 | J.H. Campbell | 2025-11-19 | 202-25-7B | 2026-01-21 | 63 |
| 202-25-4 | Eddystone | 2025-08-28 | 202-25-4B | 2026-01-10 | 135 |
| 202-25-8 | Eddystone | 2025-11-26 | 202-25-8B | 2026-03-05 | 99 |
| 202-25-11 | Centralia | 2026-03-16 | 202-25-11C | 2026-06-10 | 86 |
| 202-25-12 | R.M. Schahfer | 2026-03-23 | 202-25-12B | 2026-06-01 | 70 |
| 202-25-13 | F.B. Culley | 2026-03-23 | 202-25-13B | 2026-06-01 | 70 |
| 202-25-14 | Craig | 2026-03-30 | 202-25-14B | 2026-06-24 | 86 |
| 202-26-19 | R.M. Schahfer | 2026-06-21 | 202-26-19B | 2026-10-16 | 117 |
| 202-26-20 | F.B. Culley | 2026-06-21 | 202-26-20B | 2026-10-16 | 117 |

Each plant order runs 89 or 90 days. On DOE's own pages, its reasoned answer to a rehearing request has never come while the order it answers was in force. The D.C. Circuit's decision of 11 September 2026 on the first Campbell order (202-25-3; *Michigan v. DOE*, No. 25-1159) vacated that order 386 days after it expired, and Campbell had been under five later orders in the meantime. The legal consequences are for the courts and the parties; this note only counts dates.

Still open: DOE's time to ask the full D.C. Circuit to rehear *Michigan v. DOE* runs to 26 October 2026 (Federal Rule of Appellate Procedure 40 allows 45 days when a federal agency is a party). On 19 October we found no report of a filing.

## Stated in advance (19 October 2026)

- **H1.** Neither Campbell's 202-26-39 nor Eddystone's 202-26-40 receives an order addressing rehearing dated on or before its expiry (14 and 20 November 2026). Scored from DOE's pages on 1 December 2026.
- **H2.** DOE's page for 202-26-40 lists a notice of denial by operation of law dated no later than 2 November 2026. That is 46 days after the request, the longest wait so far. Scored from the page on 10 November 2026.
- **H3.** Every order addressing rehearing that DOE dates between 20 October and 31 December 2026 addresses an order that had already expired on that date. Scored on 1 January 2027; not scorable if there is none.
- **H4.** By 30 November 2026, DOE's pages list at least one request for rehearing for at least two of the four September orders that have none now (202-26-42, 202-26-44, 202-26-46, 202-26-47). If H4 misses, either the challengers stopped asking DOE after the D.C. Circuit's ruling or DOE stopped posting the requests. We will say which, if the record lets us tell.

## Prior art and limits

The State Impact Center's tracker of state attorneys general's actions on these orders was archived on 31 August 2026. It has no download, and it lists only filings by attorneys general, so it shows no request for orders that only public interest organizations challenged (Eddystone's from 202-25-10 on, and Stanton's). The State Power Project's page describes the challenges in prose, with filings up to May 2026. POWER magazine's log covers the orders themselves, to April 2026. DOE's pages each cover one order. On 19 October 2026 we found no table that joins every plant order to its rehearing record, and no count of when DOE's orders on rehearing come relative to the expiry of the order they address. Lawyers in these cases know their own dockets; what this adds is the count across all eight plants from DOE's own pages. If you know of an earlier one, open an issue.

Cross-check: the State Impact Center's tracker gives the number and issue date of 24 plant orders (Campbell and Eddystone 1-6; Centralia, Schahfer, Culley and Craig 1-3). All 24 match [`data/doe_202c_orders.csv`](../data/doe_202c_orders.csv).

Limits:
- **Source.** The table was transcribed from each page's list of documents, not from the PDFs. Dates are the ones the pages give.
- **Coverage.** A filing DOE did not post is not in the table, and pages can be updated late, so requests against the September orders may still appear.
- **Fields.** Only the first request's date is kept. The requesters column lists everyone who asked, in short labels: PIOs (public interest organizations), JCA (Joint Consumer Advocates), OMS (Organization of MISO States), ICC (Illinois Commerce Commission). Court petitions and FERC cost-recovery dockets are not in the table.
- **Page quirks.** The CSV's notes record where a page shows no number for the notice or the order on rehearing, or where a filing's file name cites a different order.

Run: `python -m unittest -v test_rehearing_202c && python rehearing_202c.py --out-dir out --as-of 2026-10-19`. Data: CC BY 4.0. Code: Apache-2.0.
