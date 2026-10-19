# Where the 2026 natural gas plan went: a quarter left the year, as for solar, wind and batteries

MV2 of Munim, Inc., 18 October 2026. Made with AI agents working in his name. Text and data CC BY 4.0; code in [`tools/plan-flows/`](../tools/plan-flows/) Apache-2.0.

**Status: scored.** The checks and predictions were published before the job ran ([`gas-flows-preregistration.md`](gas-flows-preregistration.md), committed 2026-10-18 22:51Z). Job `gas-flows-v1` ran in a sealed container on 2026-10-18 (23:15-23:18Z); its 10 unit tests passed first. All four checks passed. **3 of the 6 predictions held.** Raw output: [`gas-flows-output.md`](gas-flows-output.md); month by month: [`../data/gas_flows.csv`](../data/gas_flows.csv); one row per generator: [`../data/gas_flows_generators.csv`](../data/gas_flows_generators.csv).

## Question

EIA's *Today in Energy* of 20 February 2026 (article 67205) said developers planned to add 6.3 GW of natural gas-fired capacity in 2026 (3.3 GW combined cycle, 2.8 GW combustion turbine) and named the two largest plants, Orange County Advanced Power Station (Texas, 1,158 MW) and Trumbull Energy Center (Ohio, 900 MW). [`plan-flows.md`](plan-flows.md) and [`storage-flows.md`](storage-flows.md) followed the December 2025 solar and battery books to the August 2026 report. Three questions:

1. Does the gas book, a few large plants, behave like the solar and battery books?
2. Combined cycle against combustion turbine: which is further along?
3. Do the EIA-860M records of the two named plants match what has been reported about them?

## Method (as pre-registered)

- PUDL's EIA-860M changelog, net summer capacity, read with `plan_flows.py` 0.1.0's own functions, unchanged. `gas_flows.py` 0.1.0 adds five technologies: natural gas combined cycle, combustion turbine, internal combustion engine, steam turbine and other natural gas. The census printed six names containing "natural gas"; the sixth, `Natural Gas with Compressed Air Storage` (30 records), is storage and is not read, as stated in advance.
- **Base:** December 2025 report. **Latest:** August 2026 report. The 2026 book is every gas generator online in 2026 by that month or planned for a 2026 month.
- **Prime mover** by each generator's latest technology: cc (combined cycle), ct (combustion turbine), other (engines, steam, other).
- **Stage:** building = U, V, TS in December; early = P, L in December. T (approved, not started) is in neither.

## Results

### Four technologies, one reading

| technology | December book (GW) | online 2026 | still 2026 | 2027+ | not listed | online outside 2026 | left the year | joined since | August book |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| solar | 43.65 | 12.58 | 20.71 | 7.63 | 2.29 | 0.45 | 23.7% | 7.94 | 41.13 |
| wind | 12.12 | 6.48 | 2.85 | 2.39 | 0.00 | 0.40 | 23.0% | 1.03 | 10.39 |
| batteries | 24.28 | 9.57 | 8.69 | 3.65 | 1.88 | 0.50 | 24.8% | 4.51 | 22.77 |
| **gas** | **6.26** | **2.30** | **2.36** | **1.53** | **0.08** | **0.00** | **25.6%** | **1.11** | **5.77** |

The four December books add up to 86.32 GW (EIA: 86 GW). Check K3 confirms that the solar, wind and battery rows reproduce the published results to within 0.004 GW.

- **Every technology lost about a quarter of its 2026 plan by August: 23.0% to 25.6%.** Solar is thousands of small projects, gas a few dozen large ones, wind and batteries sit between, and the share that left the year is the same within three points. (Not pre-registered: we predicted each part of the gas outcome, not this comparison.)
- **How they left differs.** Gas and wind left mostly by slipping to 2027 or later (95% and 86% of what left; the rest of wind's is listed as online outside 2026). Solar and batteries also lost capacity that dropped out of the inventory (2.29 and 1.88 GW).

### The December 2025 gas book in August 2026

| state in August 2026 | GW (December capacity) | share | generators |
|---|---:|---:|---:|
| online in 2026 | 2.30 | 36.7% | 43 |
| still planned for 2026 | 2.36 | 37.7% | 29 |
| planned for 2027 or later | 1.53 | 24.4% | 8 |
| no longer listed | 0.08 | 1.2% | 2 |
| another status, or online outside 2026 | 0.00 | 0.0% | 0 |
| **December book** | **6.26** | | **82** |

Joined the book since December: 1.11 GW in 28 generators (0.66 GW not listed in December, 0.45 GW then planned for 2027 or later); 0.62 GW of it is already online. Resize of generators in both books: -0.01 GW. The December book is 6.26 GW, 0.6% from EIA's 6.3 GW.

- **Gas slipped more than solar or batteries.** 24.4% of the December gas book is now planned for 2027 or later (solar 17.5%, batteries 15.0%, wind 19.7%). But almost nothing dropped out: 0.08 GW, two 38 MW turbines.
- **Three projects are almost all of the slip.** Of the 1.53 GW that moved to 2027 or later, 1.50 GW is three projects (EIA plant ids): plant 3399, a two-generator combined cycle (669.5 MW) under construction, now planned for December 2034; plant 67262, a 411.4 MW combustion turbine under construction, now planned for March 2027; and plant 728, a 418.4 MW combustion turbine at the planning stage, now February 2027. The plants are named here only by id until their raw records are read (a follow-up job prints them).
- **Month by month** the book rose from 6.26 GW in December to 7.58 GW in March (1.65 GW joined, including 0.45 GW pulled forward from 2027), then fell to 5.77 GW by August as 0.42, 0.67 and 0.83 GW moved to 2027 or later in the April, July and August reports.

### Combined cycle against combustion turbine

| group | December book (GW) | generators | online 2026 | still 2026 | 2027+ | not listed | joined since | August book |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| combined cycle | 3.28 | 11 | 0.90 (27.4%) | 1.70 | 0.69 | 0.00 | 0.00 | 2.60 |
| combustion turbine | 2.79 | 30 | 1.35 (48.4%) | 0.53 | 0.83 | 0.08 | 0.87 | 2.74 |
| engines, steam, other | 0.19 | 41 | 0.05 | 0.14 | 0.01 | 0.00 | 0.24 | 0.43 |

- **Combustion turbines are further along by August**: 48.4% online against 27.4% for combined cycle. That is mostly timing. The combined-cycle online figure, 0.90 GW, is the size of Trumbull's three generators (900.4 MW), and Orange County's 1.16 GW, more than a third of the combined-cycle book, was still testing in August. Counting it, as its owner's 14 October announcement would, combined cycle would be 62.7% online.
- **Combustion turbines kept joining**: 0.87 GW of turbines not in December's 2026 book had joined it by August, none of it combined cycle.

### Stage in December

| stage in December | GW | online | still 2026 | 2027+ | not listed |
|---|---:|---:|---:|---:|---:|
| building (U, V, TS) | 5.58 | 41.2% | 39.4% | 19.4% | 0.0% |
| early (P, L) | 0.53 | 0.0% | 5.7% | 79.9% | 14.4% |

T (approved, not started): 0.16 GW, 0.13 still planned for 2026, 0.02 later.

- **Early-stage gas almost all left** (94.3%), as for solar and batteries.
- **Unlike solar and batteries, building-stage gas slipped too**: 19.4% of it, all from two projects (plants 3399 and 67262, 1.08 GW, both under construction in December). For solar and batteries under 4% of building-stage capacity slipped.

### The two plants EIA named, by raw record

| plant | generators | summer MW | December 2025 | August 2026 |
|---|---|---:|---|---|
| Trumbull Energy Center (66918) | GT11, GT12, STG | 900.4 | V (more than half built), planned January 2026 | operating, operating month April 2026 |
| Orange County Advanced Power Station (66621) | 1A, 1B, 1C | 1,158.2 | V, planned June 2026 | TS (testing), planned September 2026 |

Both match EIA's article in name and size (900 and 1,158 MW). Every raw record is printed in [`gas-flows-output.md`](gas-flows-output.md). Trumbull's planned month moved from January to April 2026 in the January 2026 report, and the April report lists it as operating from April. The local press we read before the run had said Trumbull entered commercial operation in January 2026; EIA-860M says April. We have not resolved the difference. Orange County moved from June to July, August and then September 2026, and has been testing since the July report; its owner announced it in service on 14 October 2026, after the August report.

## Checks (all passed)

| check | rule | result |
|---|---|---|
| K1 | change = entries - exits + resize for every pair of gas reports, within 0.001 GW | 9 pairs, largest residual 0.000 GW |
| K2 | the December gas book's August states add up to the December book, within 0.01 GW | 6.2635 = 6.2635 |
| K3 | the solar, wind and battery readings reproduce the published figures, each within 0.01 GW | largest difference 0.0037 GW |
| K4 | the December gas book within 20% of EIA's 6.3 GW | 6.264 GW, -0.6% |

## Predictions (3 of 6 held)

| | prediction | result | |
|---|---|---|---|
| G1 | at least 30% of the December gas book online in 2026 by August | 36.7% (2.30 GW) | **held** |
| G2 | at most 17.5% planned for 2027 or later | 24.4% (1.53 GW) | **missed** |
| G3 | less than 5.2% no longer listed or in another status | 1.2% (0.08 GW) | **held** |
| G4 | combined-cycle share online at least the combustion-turbine share | 27.4% against 48.4% | **missed** |
| G5 | early (P, L) at least 40% to 2027+ or gone; building (U, V, TS) at most 10% to 2027+ | 94.3%; 19.4% | **missed** (first part held) |
| G6 | every Trumbull generator operating with a 2026 month; every Orange County generator still planned for 2026, not operating | Trumbull: 3 of 3 operating, April 2026; Orange County: 3 of 3 planned September 2026 (testing) | **held** |

We expected the 2026 gas plants, ordered before the turbine shortage, to slip less than solar. They slipped more, though the slip is three projects, two of them already under construction, so G2 and the building part of G5 missed. G4 missed for the reason the pre-registration gave against it: Orange County came online after the August report. G6 held by its letter; the operating month EIA-860M gives Trumbull (April) is later than the January we had read.

## Stated in advance for the September 2026 report

Written 2026-10-18, before the September 2026 EIA-860M is released (due 23 October). Scored with `gas_flows.py` 0.1.0 unchanged.

- **GS1.** None of Orange County Advanced Power Station's three generators is listed as operating in the September report. Basis: its owner announced it in service on 14 October, after September.
- **GS2.** The September gas book is at most 5.77 GW (August's). Basis: it fell in the July and August reports, and 2.36 GW of the December book is still planned for the last four months of the year.

## Limits

- A state is what the inventory says, not what happened on site. "Not listed" is not confirmed cancellation; EIA-860M's separate list of cancelled and postponed projects was not read.
- The gas book is 82 generators, and three projects make up almost all of the slip. Its shares can swing on one plant.
- The four-technology comparison and the observations on what joined the book were made after the run and are description, not tests.
- EIA's 6.3 GW is nameplate; this is net summer capacity.
- Plants 3399, 67262 and 728 are named only by EIA plant id here; names will be added from their raw records.

## Files

- [`gas-flows-preregistration.md`](gas-flows-preregistration.md): checks and predictions, published before the run.
- [`gas-flows-output.md`](gas-flows-output.md): the job's raw output, with the named plants' raw records.
- [`../data/gas_flows.csv`](../data/gas_flows.csv): the monthly split for gas, one row per report pair.
- [`../data/gas_flows_generators.csv`](../data/gas_flows_generators.csv): every gas generator in the December or August book, with its state in both.
- [`../tools/plan-flows/`](../tools/plan-flows/): `gas_flows.py` 0.1.0 and its tests, beside `plan_flows.py` 0.1.0.

```
cd tools/plan-flows
pip install pandas pyarrow
python -m unittest -v test_gas_flows
python gas_flows.py --data-dir DATA --out-dir out
```

`DATA` holds PUDL's `core_eia860m__changelog_generators.parquet`.
