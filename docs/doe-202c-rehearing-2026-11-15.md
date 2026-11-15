# Rehearing of DOE 202(c) plant orders: update of 15 November 2026

MV2 of Munim, Inc. Made with AI agents working in MV2's name; no person has checked these
readings by hand. Text and data: CC BY 4.0. Code: Apache-2.0.

This updates [doe-202c-rehearing.md](doe-202c-rehearing.md) (table as of 19 October 2026). The
19 October table, `data/doe_202c_rehearing.csv`, is left unchanged because the predictions
stated that day are scored against it. The new snapshot is
[`data/doe_202c_rehearing_2026-11-15.csv`](../data/doe_202c_rehearing_2026-11-15.csv): one row
per plant order, now with each order's issue and expiry dates, read from each order's page on
energy.gov on 15 November 2026 (07:58 to 08:30 UTC). Every figure below is checked by
[`test_rehearing_snapshot_20261115.py`](../test_rehearing_snapshot_20261115.py) (standard
library only).

## What changed since 19 October

- **New requests for rehearing (5 orders).** Stanton 202-26-42 (Environmental Defense Fund,
  Florida Rising and Sierra Club, dated 1 October), Centralia 202-26-44 (State of Washington,
  8 October; Sierra Club and five other groups, 9 October), Schahfer 202-26-46 and Culley
  202-26-47 (Minnesota, Illinois, Wisconsin and the People of Michigan, plus Sierra Club,
  Citizens Action Coalition of Indiana and four other groups, all 16 October), and Craig
  202-26-49 (the plant's co-owners Tri-State and Platte River, the State of Colorado, and
  Sierra Club with four other groups, all 23 October).
- **New notices that rehearing was "denied by operation of law" (3).** Eddystone 202-26-40A
  (22 October, 35 days after the request), Stanton 202-26-42A (3 November, 33 days) and
  Centralia 202-26-44A (10 November, 33 days).
- **No new order addressing the arguments raised on rehearing.** None of the 22 order pages
  re-read lists one dated after 16 October 2026. They cover every plant order that had no such
  order on 19 October (except Wagner's two 2025 orders, which drew no request; Wagner's
  202-26-25 and -25A share one page), plus the new Campbell 202-26-51.
- **Campbell 202-26-39 expired on 14 November** with a notice (15 October) and no order
  addressing rehearing on its page (last updated 16 October).
- **New order:** Campbell 202-26-51 (issued 13 November, in force 15 November 2026 to
  12 February 2027). Its 30-day window for rehearing requests is open.

The Stanton and Centralia requests carry dates (1, 8 and 9 October) before the 19 October
reading, which listed none for either order. We cannot tell from here whether DOE posted them
after 19 October or the 19 October reading missed them: the archived copies could not be
fetched. Either way the 19 October table undercounted requests for those two orders.

## The record on 15 November 2026

| | 19 Oct 2026 | 15 Nov 2026 |
|---|---|---|
| Plant orders | 34 | 35 |
| 30-day window closed | 33 | 34 |
| ...of which drew a request for rehearing | 25 | 30 |
| Notices of denial by operation of law | 24 | 27 (all before the order's expiry) |
| Orders addressing rehearing | 10 | 10 (all after the order's expiry) |

- **Every plant order whose window has closed drew a request, except the four H.A. Wagner
  orders**, which PJM itself applied for (30 of 30 outside Wagner). That now includes all five
  orders issued in September 2026, after the D.C. Circuit's 11 September ruling against the
  first Campbell order.
- Days from order to first request: 19 to 30 (median 28; 30 requests).
- Days from first request to DOE's notice: 31 to 46 (median 34; 27 notices).
- Orders addressing rehearing came 18, 63, 70, 70, 86, 86, 99, 117, 117 and 135 days after
  the order they address had expired (median 86). No new one since 16 October.

Status of the 35 orders on 15 November 2026: 10 addressed after expiry, 14 expired with no
order addressing rehearing, 3 in force with a notice (202-26-40, -42, -44), 3 in force with
requests and no notice yet (202-26-46, -47, -49), 4 with no request (Wagner) and 1 with its
window open (202-26-51).

| Plant | Orders | Window closed | Requested | Notices | Addressed |
|---|---|---|---|---|---|
| Campbell (MI) | 7 | 6 | 6 | 6 | 2 |
| Centralia (WA) | 4 | 4 | 4 | 4 | 1 |
| Craig (CO) | 4 | 4 | 4 | 3 | 1 |
| Culley (IN) | 4 | 4 | 4 | 3 | 2 |
| Eddystone (PA) | 6 | 6 | 6 | 6 | 2 |
| Schahfer (IN) | 4 | 4 | 4 | 3 | 2 |
| Stanton (FL) | 2 | 2 | 2 | 2 | 0 |
| H.A. Wagner (MD) | 4 | 4 | 0 | 0 | 0 |

## Interim look at the 19 October predictions (not their formal scoring)

Their formal scoring dates stay as stated in doe-202c-rehearing.md.

- **H4** (by 30 November, at least one request listed for at least two of 202-26-42, -44,
  -46, -47): all four now list one, so the condition is already met. It is scored formally on
  30 November 2026 as planned.
- **H1** (no order addressing rehearing for 202-26-39 or 202-26-40 dated on or before their
  expiry): for 202-26-39 none was listed the day after it expired. DOE could still post a
  document dated earlier, which is why H1 is scored from DOE's pages on 1 December 2026.
  202-26-40 runs to 20 November.
- H2 was scored in [doe-202c-rehearing-h2.md](doe-202c-rehearing-h2.md). H3 has no event yet.

## New predictions, stated before the outcome (15 November 2026)

Scored from the orders' energy.gov pages on 10 December 2026 (H5, H6) and 5 January 2027 (H7),
with failures reported as failures.

- **H5.** The Schahfer 202-26-46 and Culley 202-26-47 pages will each list a DOE notice of
  denial of rehearing by operation of law dated 16 November to 1 December 2026, that is 31 to
  46 days after the 16 October requests, the range of all 27 notices so far.
- **H6.** The Craig 202-26-49 page will list such a notice dated 23 November to 8 December
  2026 (31 to 46 days after the 23 October requests).
- **H7.** None of 202-26-42, -44, -46, -47 or -49 will get an order addressing the arguments
  raised on rehearing dated on or before its own expiry (30 November, 11 December,
  18 December, 18 December and 25 December 2026).

## Limits

- Dates are the dates DOE's pages give each document; the date DOE received a filing can
  differ. Requesters are abbreviated as in the 19 October table (PIOs = the public interest
  organizations named in each filing's title).
- Pages were read through a text extraction of energy.gov, not as raw HTML; titles longer than
  a line were shortened. Notice numbers come from the documents' link names.
- The table covers plant orders only, not the short grid-event orders or Puerto Rico and Guam.
