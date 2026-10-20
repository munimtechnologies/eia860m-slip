# EIA-860M watchlist: how to read it

MV2 of Munim, Inc. (made with AI agents working in his name). Code Apache-2.0; tables CC BY 4.0.

`tools/annual-flows-candidate/watchlist.py` (0.1.0) reads PUDL's EIA-860M changelog
(`core_eia860m__changelog_generators`, CC BY 4.0) and, for one monthly report, lists every planned
U.S. generator whose stage, status code or planned operating month changed since the report before.
It is built on this repo's pre-registered `stagemoves.py` and `eia860m_slip.py` code.

    python watchlist.py --data-dir DATA --out-dir OUT [--report YYYY-MM]

Without `--report` it reads the latest report in the file. Outputs: `watchlist_<YYYY-MM>.csv` (one
row per changed generator), `.json` (everything) and `.md` (the tables).

First run: job `watchlist-v2` on 20 October 2026, on PUDL's nightly changelog with reports to 2026-08 (it fetched `eia860m_slip.py` at commit 329b7e6 and `stagemoves.py` at commit a059121), for reports 2026-08 and 2026-07. Checks C1 to C4 passed for both reports; 10 of 10 unit tests passed ([`watchlist-v2-unittests.txt`](watchlist-v2-unittests.txt)). Editions: [`watchlist-2026-08.md`](watchlist-2026-08.md) with [`../data/watchlist_2026-08.csv`](../data/watchlist_2026-08.csv), and [`watchlist-2026-07.md`](watchlist-2026-07.md) with [`../data/watchlist_2026-07.csv`](../data/watchlist_2026-07.csv). [`../test_watchlist_doc.py`](../test_watchlist_doc.py) checks every number in this note against them.

## What each change means

Stages are grouped into bands, as in the twenty-first result: early (P, L), approved (T), building
(U, V, TS).

| change | in the report before | in this report |
|---|---|---|
| forward | early, approved or building | a later band |
| backward | early, approved or building | an earlier band |
| to_operating | early, approved or building | operating (OP, SB, OS, OA) |
| exit_other | early, approved or building | any other status (OT, IP, CN, RE, ...) |
| left | early, approved or building | no record in force |
| within_band | early, approved or building | the same band, another status (U -> TS, ...) |
| delayed | early, approved or building | the same status, a later planned month |
| advanced | early, approved or building | the same status, an earlier planned month |
| new | no record in force | early, approved or building |
| into_planned | another status | early, approved or building |

A band move counts before a status change, and a status change before a change of planned month,
so each generator appears once. `shift_months` is filled whenever both planned months are known.
MW is the capacity in the report before, except for new and into_planned rows.

## What it adds to a plain diff

A month-over-month diff of two EIA-860M workbooks already exists (see "Prior art" below). The
watchlist adds three things:

1. **History beside each count.** For every kind of change except delayed and advanced, this
   report's count and MW sit beside the median and the largest of the previous 36 report pairs.
   That shows whether a month is unusual or ordinary.
2. **Repeat movers.** Each row carries `backward_before`: how many times the same generator moved
   back a band in those 36 pairs.
3. **A recent base rate.** For earlier moves whose next 12 reports are all in the file, the share
   of MW listed as operating within 12 reports, by starting band and move (the same measure as the
   twenty-first result, docs/stage-moves.md). It describes what happened to earlier moves of that
   kind; it is not a forecast for any one generator.

It also flags **possible re-keys**: a `left` row of at least 10 MW and a `new` row in the same
report with the same technology group and generator id, capacities within 0.05 MW. Both rows name
each other in `possible_rekey`. These are the terms of rule R (docs/annual-flows-rekey.md), which
linked exactly the 11 hand-read re-keys in the earlier results. A flag is a lead to check, not a
finding.

## What the first two editions show

**Report 2026-08: 418 changed generators: 238 delayed (17,371.6 MW), 63 within a band, 50 to operating (3,084.1 MW), 28 new (1,509.4 MW; the median of the 36 earlier pairs is 83), 22 forward, 9 left, 8 advanced and 0 backward (median 1).** The largest generator delayed is Singing Grass Wind (CO, onshore wind, 603.0 MW, under construction), moved 13 months, from 2026-08 to 2027-09. Most of the other large delays are one to three months for plants under construction or testing.

**Report 2026-07: 537 changed generators, 264 of them delayed (27,075.9 MW) and 103 new (8,140.2 MW).** It holds one backward move: Madena 4 (CA, battery, 5.0 MW) from U to L. The largest generator delayed is Chokecherry and Sierra Madre Wind (WY, 1,303.2 MW, under construction), moved 24 months, from 2030-12 to 2032-12. The largest exit is Atlas (AZ, battery, 300.0 MW, more than half built, planned for 2026-07), which has no record in force in the 2026-07 report and no matching new row; a `left` row like this is a lead to check (a plant can come online or be re-filed in ways rule R does not catch), not a cancellation.

**Neither edition has a possible re-key pair**, so the re-key flag has not yet fired on live data.

**The recent base rates point the same way as the twenty-first result** (0.053 against 0.528 over all reports since 2016, in docs/stage-moves.md). In the 2026-08 edition, of the MW that stepped back from building in reports 2023-07 to 2025-08, 0.032 was listed as operating within 12 reports (18 steps), against 0.565 for building MW that held its band.

## Checks run on every report

- C1: one row per generator, every change of a known kind.
- C2: the MW of every planned generator in the report before equals the sum of its moves.
- C3: the counts by move equal `stagemoves.steps` for the same report pair.
- C4: the rows' band moves and `left` equal those counts, and the within-band, delayed and
  advanced rows are no more than the generators that held their band.

A report whose checks fail is not published.

## Limits

- EIA-860M statuses and planned months are reported by plant owners. A change can be a correction
  of an earlier report rather than an event at the plant.
- PUDL's report month is the month the data describes, not the month EIA released it.
- Rule R re-keys are not merged here (the history and base rates read raw keys), so a plant that
  was re-filed under a new plant id shows as one `left` row and one `new` row. stagemoves merges
  the 11 rule R links, so the base rates here can differ slightly from docs/stage-moves.md.
- delayed and advanced are not set beside the history pairs, because stagemoves' timeline keeps
  no planned month.
- The base rates are associations in earlier reports, not causes and not forecasts.

## Prior art (checked 20 October 2026)

- The Apify actor "EIA Power Project Change & Lead Scraper" (scrapesignal_labs/eia-power-project-
  change-feed) compares the two newest EIA-860M workbooks generator by generator, with nine change
  types and a score, paid per change. Its page describes no historical baseline, base rates or
  re-key handling.
- Grid Status publishes EIA's "Canceled or Postponed" sheet as a dataset; it does not track moves
  between stages.
- So a month-over-month diff is not new. What is new here is the diff set beside its own history
  and earlier outcomes, with checks against pre-registered code, from open code and open data.
