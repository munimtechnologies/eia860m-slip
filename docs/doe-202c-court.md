# Court petitions against DOE's 202(c) plant orders: one order decided, 21 petitions in abeyance

Status: description (the counts below are not predictions). Table as of 19 October 2026. MV2 of Munim, Inc.; the table, code and this note were made with AI agents working in my name.

## What this is

After DOE denies rehearing of a 202(c) order (or the request is deemed denied), a party has 60 days to petition a court of appeals for review (Federal Power Act section 313(b)). The fifteenth result ([`docs/doe-202c-rehearing.md`](doe-202c-rehearing.md)) counted the rehearing record on DOE's own pages. This note follows the challenges into court.

[`data/doe_202c_petitions.csv`](../data/doe_202c_petitions.csv) has one row for each petition for review of a 202(c) plant order that we found in CourtListener's RECAP archive of the D.C. Circuit and Ninth Circuit dockets. Each row gives the docket, filing date, petitioners, the DOE order the record names, how that order is known, the lead docket of its consolidated group, and the latest status the archive shows, with a link. [`court_202c.py`](../court_202c.py) (standard library only) joins it to [`data/doe_202c_orders.csv`](../data/doe_202c_orders.csv), checks it and prints the counts below. [`test_court_202c.py`](../test_court_202c.py) checks the code on hand-built tables and checks every count here against the CSVs.

## What the dockets show

- **35 petitions for review: 32 in the D.C. Circuit and 3 in the Ninth Circuit** (Centralia, Washington). They touch all seven plants whose orders drew rehearing requests (Stanton only by inference from its petitioners). None touches Wagner, whose orders drew no request.
- **One order has been decided.** The D.C. Circuit decided the three petitions against Campbell's first order (202-25-3; *Michigan v. DOE*, No. 25-1159, with 25-1160 and 25-1162) on 11 September 2026. That was 414 days after the first petition and 386 days after the order had expired.
- **21 petitions are held in abeyance**, in five groups:

| abeyance order | petitions | orders challenged |
|---|---|---|
| 2026-02-18 | 3 | Campbell's second order, 202-25-7, held until 25-1159 is resolved (the petitioners asked; DOE opposed and asked to consolidate instead, which was denied) |
| 2026-03-13 | 1 | 26-1026 (NRDC), held until 30 days after the decision in the Eddystone cases 25-1193 et al. |
| 2026-06-08 | 3 | Craig's first order, 202-25-14 (Colorado, the environmental groups, and the co-owners Tri-State and Platte River), on DOE's unopposed motion; motions to govern due within 60 days of the decision in 25-1159 |
| 2026-07-28 | 10 | Schahfer's and Culley's first orders (202-25-12, 202-25-13) and five more Indiana petitions whose order we did not see, consolidated under 26-1056 |
| 2026-08-26 | 4 | Eddystone's first two orders, 202-25-4 and 202-25-8. Briefing had been set on 7 April 2026 and was suspended on 11 June; DOE moved for abeyance on 21 May. Motions to govern are due 14 days after the mandate in 25-1159. |

- **The three Ninth Circuit petitions on Centralia have briefing schedules.** These are 26-1252 and 26-1261 (consolidated; opening briefs due 22 July, answering brief 21 August 2026) and 26-3781 (opening brief 31 August, answering brief 29 September 2026). No argument date appears.
- **8 petitions show no abeyance or briefing order in the archive.** Two are on Campbell's third order (202-25-9). The others are the latest Campbell petition (26-1233, on 202-26-22, 10 September 2026), Eddystone (26-1167), Stanton (26-1224), and three on Craig (26-1255, 26-1256, 26-1273, with first entries in September-October 2026).
- **The oldest open petition is 25-1193**, from the Illinois Attorney General and the Maryland and New Jersey consumer advocates, against Eddystone's first order. It was filed 25 September 2025, 389 days ago, and is now in abeyance.
- **22 petitions name their order in the record.** These are 10 plant orders: 202-25-3, -4, -7, -8, -9, -11, -12, -13, -14 and 202-26-22. 14 of the 22 were filed while the order was still in force, and 8 after it had expired. Measured from the order's expiry, they were filed between 41 days before it and 29 days after it (median 12 days before).

So DOE renews each plant order every 90 days, and the court record is one decided order and a queue. The decided order is Campbell's first, after 414 days. The queue is 21 petitions at Campbell, Eddystone, Craig, Schahfer and Culley, and at least 10 of them are waiting, by the orders' own words, on that decision or its mandate. Only Centralia's challenges, in the Ninth Circuit, are being briefed. DOE's time to ask the full D.C. Circuit to rehear *Michigan v. DOE* runs to 26 October 2026. On 19 October we found no report of a filing. The legal consequences are for the courts and the parties; this note only counts dockets and dates.

## How each order is known

The `order_evidence` column says where the order number comes from:
- **`petition`** (14 rows): the petition's own text, as indexed by CourtListener.
- **`filing`** (7): another filing in the case, such as DOE's certified index or a caption.
- **`secondary`** (1): the State Power Project's page, for 26-1060, which was consolidated with Colorado's 26-1059 the next day.
- **blank** (13): we did not see the order number. For these rows the plant is inferred, and the note says how. Petitioners' names give some of them, such as Florida Rising for Stanton and Citizens for Pennsylvania's Future for Eddystone. Consolidation gives the rest. Five Indiana rows are marked `schahfer-culley` because the record we saw does not say which plant.

## Prior art and limits

- **State Power Project.** Its litigation page lists seven docket numbers in prose, with filings to May 2026, and no abeyance status.
- **Jones Day.** Its Climate Report of 22 June 2026 says all the petitions are held in abeyance pending *Michigan v. DOE*. It gives one docket number and no table. Its claim does not fit the Ninth Circuit's Centralia cases, which have briefing schedules.
- **Others.** The State Impact Center's tracker (archived 31 August 2026) lists attorneys general's actions only. Law-firm notes and the Yale Journal on Regulation discuss the decision.

On 19 October 2026 we found no open, docket-level table of the petitions against these orders with their consolidation and abeyance status. If you know of one, open an issue.

Limits:
- **Coverage.** The table holds what CourtListener's RECAP archive held on 19 October 2026, found by searching case names and docket numbers. RECAP holds what PACER users have uploaded, so a petition nobody uploaded is missing.
- **Dates.** Seven dockets have no filing date in the archive and are left blank: 26-1101, 26-1158, 26-1159, 26-1186, 26-1187, 26-1255 and 26-1256.
- **Status.** Status is the latest order whose text we saw. A later order with no text in the archive, such as the clerk's orders of 24 September and 5 October 2026 in the Craig dockets, may have changed it. "No later order seen" means only that.
- **Out of scope.** This is not legal analysis. The FERC cost-recovery dockets are not in the table.

Run: `python -m unittest -v test_court_202c && python court_202c.py --out-dir out --as-of 2026-10-19`. Data: CC BY 4.0. Code: Apache-2.0.

## Update of 28 October 2026: DOE asked for rehearing on the last day

Status: dated update; description only, nothing is scored. Everything above is unchanged from 19 October 2026, and so is the table: `data/doe_202c_petitions.csv` is still as of 19 October.

- **What was reported.** Two reports dated 27 October 2026 say DOE filed a petition for rehearing in *Michigan v. DOE* (No. 25-1159) on Monday, 26 October 2026: Bloomberg Law ("Energy Department Asks Full Court to Rehear Michigan Coal Case") and The Baseload, the newsletter of America's Power. Bloomberg Law says the petition asks for rehearing by the panel or by the full court, and that DOE argues the panel was wrong to read the Federal Power Act as making its emergency authority a last resort.
- **It came on the last day.** The decision was entered on 11 September 2026. When a federal agency is a party, a petition for rehearing is due 45 days after judgment, and 11 September plus 45 days is 26 October.
- **What we did not see.** We have not read the petition or the docket entry itself. On 28 October we could not read CourtListener from our tools, so this update rests on the two reports. If the docket shows a different date or form, this section will be corrected in a later dated section.
- **The mandate waits.** Under Federal Rule of Appellate Procedure 41(b), the mandate issues 7 days after the time to petition for rehearing expires, or 7 days after an order denying a timely petition, whichever is later. Without a petition it would have issued on 2 November 2026 (26 October plus 7 days). With a timely petition pending, it issues only after the court rules on it.
- **What the abeyance groups wait on, as the table above records their orders.** Eddystone's first two orders (abeyance of 26 August, 4 petitions) have motions to govern due 14 days after the mandate, so they now also wait on the rehearing petition. Campbell's second order (18 February, 3 petitions) is held until 25-1159 is resolved. Craig's first order (8 June, 3 petitions) has motions to govern due within 60 days of the decision, which counted from 11 September is 10 November 2026; the archive does not yet show whether anyone treats that date as moved. The Schahfer and Culley group (28 July) and NRDC's 26-1026 (13 March) are as described above.
- **No new plant order since our orders table.** DOE's page of 2026 orders, read on 28 October 2026, lists nothing after 202-26-50 (PJM, 12 October 2026, in force 13 to 16 October), which names no plant.
- **Next expiries, from [`data/doe_202c_orders.csv`](../data/doe_202c_orders.csv).** Campbell's sixth order, 202-26-39, expires 14 November 2026; Wagner's 202-26-25A on 17 November; Eddystone's 202-26-40 on 20 November; Stanton's 202-26-42 on 30 November. The orders table holds six Campbell orders, each of the last five issued no later than the day the one before it expired, so whether DOE issues a seventh while its own rehearing petition is pending is the next public event to watch.

The legal consequences are for the courts and the parties; this section only records dates and filings. [`test_doe_202c_court_update.py`](../test_doe_202c_court_update.py) checks the dates above by arithmetic and the expiries against the orders table.
