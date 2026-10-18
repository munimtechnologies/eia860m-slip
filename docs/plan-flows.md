# Where the 2026 solar plan went: a steady total over a quarter of the plan replaced

MV2 of Munim, Inc., 18 October 2026. Made with AI agents working in his name. Text and data CC BY 4.0; code in [`tools/plan-flows/`](../tools/plan-flows/) Apache-2.0.

**Status: scored.** The checks and predictions were published before the job ran ([`plan-flows-preregistration.md`](plan-flows-preregistration.md), released in 0.2.10). Job `plan-flows-v1` ran in a sealed container on 2026-10-18 (14:08-14:15Z); its 10 unit tests passed first. All three checks passed. **3 of the 5 predictions held.** Raw output: [`plan-flows-output.md`](plan-flows-output.md); month by month: [`../data/plan_flows.csv`](../data/plan_flows.csv); one row per generator: [`../data/plan_flows_generators.csv`](../data/plan_flows_generators.csv).

## Question

[`plan-path.md`](plan-path.md) found that EIA-860M's implied 2026 solar total (online in 2026 plus still planned for a 2026 month) stayed between 41.0 and 43.7 GW from December 2025 to August 2026. A net total that barely moves can still hide large flows. Did the same projects hold the year, or did some leave and others take their place?

## Method (as pre-registered)

- Same data and the same reading of each report as `plan_path.py` 0.1.0 (PUDL's EIA-860M changelog, net summer capacity). The **2026 book** of a report is every solar generator online in 2026 by that month or planned for a 2026 month.
- Each listed generator is in one state: online_2026, planned_2026 (together the book), planned_later (2027 or later), planned_other (blank or pre-2026 month), online_other (operating, online outside 2026), other_status (cancelled, postponed and so on) or not_listed.
- **Monthly split:** entries, exits and resize between consecutive reports, adding up to the change exactly. **The December book:** every generator in the December 2025 book, at its December capacity, by its state in the August 2026 report, plus what joined since.

## Results

### The December 2025 book in August 2026

| state in August 2026 | GW (December capacity) | share | generators |
|---|---:|---:|---:|
| online in 2026 | 12.58 | 28.8% | 178 |
| still planned for 2026 | 20.71 | 47.4% | 228 |
| planned for 2027 or later | 7.63 | 17.5% | 99 |
| operating, online date outside 2026 | 0.45 | 1.0% | 4 |
| no longer listed | 2.29 | 5.2% | 28 |
| another status (cancelled, postponed...) | 0.00 | 0.0% | 0 |
| **December book** | **43.65** | | **537** |

Joined the book since December: **7.94 GW in 266 generators** (6.30 GW not listed in December, 1.37 GW then planned for 2027 or later, 0.27 GW then listed as operating outside 2026); 2.08 GW of it is already online. Generators in both books shrank by 0.11 GW. So 12.58 + 20.71 - 0.11 + 7.94 = 41.12 GW, the August book's 41.13 GW to rounding.

- **The steady total is not the same projects.** 10.37 GW (24%) of December's 2026 book had left the year by August and 7.94 GW joined it; 19% of the August book was not in December's. The net change, -2.52 GW, is a quarter of the gross outflow.
- **Leaving mostly means slipping.** 7.63 GW moved to 2027 or later, 2.29 GW dropped out of the inventory. No generator in the book moved to a cancelled or postponed status code: in PUDL's changelog, projects that leave are simply no longer listed. 0.45 GW (4 generators) left by being reported as already online before 2026; one 331.6 MW unit (plant 67123, MISII), planned for March 2026 in December, is now listed as operating since December 2025. That is an early arrival, not a loss.
- **Stage in December predicts the outcome.** Of the 32.09 GW under construction or complete in December (U, V, TS), 38.5% is online and 55.4% still planned for 2026; only 3.6% slipped to 2027+ and 1.3% dropped out. Of the 8.85 GW at the earliest stages (P planned, L awaiting approvals), 2.0% is online, 55.5% slipped to 2027+ and 19.2% dropped out. Early-stage capacity was 20% of the December book but 64% of what slipped and 74% of what dropped out.

| status in December | GW | online | still 2026 | 2027+ | online outside 2026 | not listed |
|---|---:|---:|---:|---:|---:|---:|
| U, V, TS (building or complete) | 32.09 | 12.37 | 17.79 | 1.17 | 0.34 | 0.41 |
| T (approved, not started) | 2.61 | 0.04 | 0.96 | 1.44 | 0.00 | 0.17 |
| P, L (planned, approvals pending) | 8.85 | 0.18 | 1.95 | 4.91 | 0.11 | 1.70 |
| OT (other) | 0.10 | 0.00 | 0.00 | 0.10 | 0.00 | 0.00 |

- **What is left of December's plan is mostly under construction.** Of the 20.71 GW of the December book still planned for 2026 in August, 17.79 GW (86%) was already U, V or TS in December.
- **Month by month** (January to August reports): 11.13 GW left the book (8.42 GW to 2027 or later, 2.27 GW no longer listed, 0.45 GW online outside 2026) and 8.71 GW entered (6.91 GW newly listed, 1.52 GW pulled forward from 2027 or later, 0.27 GW from online outside 2026). These monthly sums count a generator each time it moves, so they exceed the December-to-August figures. The December report itself took in 3.20 GW that had been planned for 2025 or undated. The August report moved least: 0.21 GW in, 0.08 GW out.
- **Wind, same reading:** of the 12.12 GW December wind book, 6.48 GW (53.5%) is online, 2.85 GW still planned for 2026, 2.39 GW (20%) planned for 2027 or later, 0.40 GW online outside 2026, none dropped out; 1.03 GW joined. Wind slipped a similar share but is much further along.

## Other things seen (not pre-registered)

- **The largest 2026 solar project EIA named has slipped to 2027 in EIA's own inventory.** EIA's *Today in Energy* of 20 February 2026 (article 67205) called Tehuacana Creek 1 Solar and BESS, 837 MW in Texas, "the largest solar photovoltaic project expected to come online in 2026". The generator that matches it in the December report, plant 65855 generator TE1PV (836.8 MW, stage L, planned October 2026), is in the August report at stage V (more than half built) but planned for May 2027, at 644.8 MW. The match rests on size and generator id; the plant name is being confirmed from the raw record (see Limits).
- **Prior art agrees on direction.** pv magazine USA (18 November 2025), reporting EIA's inventory figures, gave about 20% of planned solar capacity reporting a schedule delay in Q3 2025, and under 1% of planned solar capacity typically cancelled in a month. This result adds what EIA's delay share does not give: how much of one year's book left the year, where it went, and what replaced it.

## Checks (all passed)

| check | rule | result |
|---|---|---|
| C1 | change = entries - exits + resize in every pair, within 0.001 GW | 9 pairs, largest residual 0.000 GW |
| C2 | the book matches plan_path 0.1.0's implied total in all ten reports, within 0.01 GW | 10 of 10; largest difference 0.0037 GW |
| C3 | the December book's August states add up to 43.65 GW, within 0.01 GW | 43.6537 = 43.6537 |

## Predictions (3 of 5 held)

| | prediction | result | |
|---|---|---|---|
| F1 | at least 8.0 GW of the December book planned for 2027 or later | 7.63 GW | **missed** |
| F2 | at least 5.0 GW of the August book not in the December book | 7.94 GW | **held** |
| F3 | less than 30% of the December book online in 2026 by August | 28.8% | **held** |
| F4 | less cancelled, other status or not listed than slipped to 2027+ | 2.29 against 7.63 GW | **held** |
| F5 | building (U, V, TS) at least 60% online by August; early (P, L) at most 20% | 38.5%; 2.0% | **missed** (first part) |

We expected gross churn of 5-10 GW each way hidden under the steady total, mostly slips rather than drops, and stage to predict delivery. The churn and the direction held (F2, F4; F1 missed by 0.37 GW). Stage does separate the outcomes sharply, but F5 was written as a delivery-by-August bar and the year is back-loaded ([`plan-path.md`](plan-path.md), P5): most building capacity is still scheduled for September-December, not slipped. F5 is scored as missed by its letter.

## Stated in advance for the September 2026 report

Written 2026-10-18, before the September 2026 EIA-860M is released. Scored with `plan_flows.py` 0.1.0 unchanged (its monthly split covers every report in the data).

- **S1.** In the September report at least 0.5 GW of solar leaves the 2026 book for 2027 or later. Basis: 0.53-2.23 GW in every report from January to July; August's 0.07 GW looks like a pause, not a trend. September is the last report before Q4 in which a late-2026 project can still reschedule early.
- **S2.** The September book is smaller than August's (exits plus resize exceed entries). Basis: it fell in 6 of the 9 reports so far.

## Limits

- PUDL's changelog is a reconstruction of the monthly files. A generator that changes its id shows up as one exit (not listed) and one entry (not listed); earlier work here found renames are rare (15 of 1,249 exits), but some of the 6.30 GW newly listed and the 2.29 GW no longer listed could be the same projects under new ids.
- A state is what the inventory says, not what happened on site. "Not listed" is not confirmed cancellation; EIA-860M's separate list of cancelled and postponed projects was not read.
- Planned months can move within 2026 without any flow (plan-path's "re-dated, not dropped").
- The per-generator rows were read from the job's own output. The raw PUDL records of five of the largest movers (TE1PV, DAWN1, INMA1, SDTWO, MISII) are being printed by a separate job (`plan-flows-spot-v1`) for a check by eye; this document will note its result.

## Files

- [`plan-flows-preregistration.md`](plan-flows-preregistration.md): checks and predictions, published before the run.
- [`plan-flows-output.md`](plan-flows-output.md): the job's raw output.
- [`../data/plan_flows.csv`](../data/plan_flows.csv): the monthly split, one row per report pair.
- [`../data/plan_flows_generators.csv`](../data/plan_flows_generators.csv): every generator in the December or August book, with its state in both.
- [`../tools/plan-flows/`](../tools/plan-flows/): `plan_flows.py` 0.1.0 and its tests.

```
cd tools/plan-flows
python -m unittest -v test_plan_flows
pip install pandas pyarrow
python plan_flows.py --data-dir DATA --out-dir out
```

`DATA` holds PUDL's `core_eia860m__changelog_generators.parquet`.
