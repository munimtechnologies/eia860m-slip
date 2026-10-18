# Pre-registration: where the 2026 solar plan went, December 2025 to August 2026

MV2 of Munim, Inc., 18 October 2026. Made with AI agents working in his name. CC BY 4.0. Written and published before the job (`plan-flows-v1`) runs; code in `tools/plan-flows/` (Apache-2.0) once the job has run its tests.

## Why

[`plan-path.md`](plan-path.md) found that EIA-860M's implied 2026 solar total (online in 2026 plus still planned for a 2026 month) stayed between 41.0 and 43.7 GW from December 2025 to August 2026, while the number of solar generators planned for 2026 fell from 537 to 388. A net total that barely moves can still hide large flows: projects slipping into 2027, cancelled or dropped, and others joining the year. This check splits the net change into those flows and follows every generator in the December 2025 book to the August 2026 report.

## What has been seen before this was written

- plan_path 0.1.0's net totals per report (data/plan_path.csv): implied 2026 solar, added, planned, overdue and the count of planned generators.
- Not seen: any generator-level flow, any count of generators or capacity moving into or out of the 2026 book, any status breakdown of the December book.

## Method (`plan_flows.py` 0.1.0)

- Same data and the same reading of each report as plan_path 0.1.0 (PUDL's EIA-860M changelog; each generator's latest record by the report month, if still valid; net summer capacity, nameplate where summer is blank or zero).
- Each solar generator listed in a report is in one state: **online_2026** (operating, online in 2026 by the report month) or **planned_2026** (planned status, planned for a 2026 month): together the 2026 book; **planned_later** (planned for 2027 or later); **planned_other** (planned, with a blank or pre-2026 month); **online_other** (operating, online outside 2026); **other_status** (any other status code: cancelled, postponed, retired and so on); **not_listed** (no valid record).
- **Monthly split.** For each pair of consecutive reports: entries (in the book now, not before; at their new capacity, by their earlier state), exits (in the book before, not now; at their old capacity, by their new state) and resize (capacity change of generators in both books). Change = entries - exits + resize.
- **The December book.** Every generator in the December 2025 book, at its December capacity, by its state in the August 2026 report; plus the generators in the August book that were not in December's, at their August capacity, by their December state. If the PUDL file has reports after August, the monthly split includes them but the December-book figures still use August.
- Status codes for the breakdown by December status: under construction or complete = U, V, TS; early = P, L.

## Checks (if one fails, the numbers are published as description and the check is fixed and re-run as -v2)

- **C1.** In every pair of reports, change = entries - exits + resize to within 0.001 GW.
- **C2.** The 2026 book in every report from November 2025 to August 2026 matches plan_path 0.1.0's implied total (data/plan_path.csv, summer) to within 0.01 GW.
- **C3.** The December book's states in August add up to the December book (43.65 GW) to within 0.01 GW.

## Predictions (on the December book in the August report unless stated)

- **F1.** At least 8.0 GW of the December book is planned for 2027 or later.
- **F2.** At least 5.0 GW of the August book was not in the December book.
- **F3.** Less than 30% of the December book's capacity is online in 2026 by August (some of the 14.7 GW added came from outside the December book, such as projects that had been scheduled for 2025).
- **F4.** Less of the December book is cancelled, under another status or no longer listed than is planned for 2027 or later: slips outweigh drops.
- **F5.** Of December-book capacity that was under construction or complete (U, V, TS) in December, at least 60% is online in 2026 by August; of capacity at the early stages (P, L), at most 20%.

What these say together: we expect the steady net total to hide gross churn of 5-10 GW each way (F1, F2), mostly slips rather than cancellations (F4), and stage in December to predict delivery (F5).

## Limits stated in advance

- PUDL's changelog is a reconstruction of the monthly files. A generator that changes its id between reports shows up as one exit (not listed) and one entry (not listed); earlier eia860m-slip work found such renames are rare (15 of 1,249 exits) but this check does not link them.
- A generator's state is what the inventory says, not what happened on site.
- Planned months can move within 2026 without any flow; that is plan-path's "re-dated, not dropped" finding and is not counted here.
