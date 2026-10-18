# Where the 2026 battery plan went: a quarter left the year, and batteries at solar plants waited for their solar

MV2 of Munim, Inc., 18 October 2026. Made with AI agents working in his name. Text and data CC BY 4.0; code in [`tools/plan-flows/`](../tools/plan-flows/) Apache-2.0.

**Status: scored.** The checks and predictions were published before the job ran ([`storage-flows-preregistration.md`](storage-flows-preregistration.md), with a dated note that `storage-flows-v1` never ran and the same code was re-filed as `storage-flows-v2` for an operational reason). Job `storage-flows-v2` ran in a sealed container on 2026-10-18 (19:42-19:45Z); its 8 unit tests passed first. All four checks passed. **4 of the 6 predictions held.** Raw output: [`storage-flows-output.md`](storage-flows-output.md); month by month: [`../data/storage_flows.csv`](../data/storage_flows.csv); one row per generator: [`../data/storage_flows_generators.csv`](../data/storage_flows_generators.csv).

## Question

[`plan-flows.md`](plan-flows.md) followed every solar generator in EIA-860M's December 2025 2026 book to the August 2026 report. EIA's *Today in Energy* of 20 February 2026 (article 67205) said developers planned to add 24 GW of utility-scale battery storage in 2026. Two questions:

1. Does the battery book behave like the solar book: how much of it is online, still planned, slipped or gone by August?
2. Many 2026 batteries share a plant with 2026 solar. Does a battery share the fate of the solar beside it?

## Method (as pre-registered)

- PUDL's EIA-860M changelog, technology `Batteries`, net summer capacity, read with `plan_flows.py` 0.1.0's own functions, unchanged. `storage_flows.py` 0.1.0 adds batteries to its technology list and the pairing below.
- **Base:** December 2025 report. **Latest:** August 2026 report. The 2026 book is every battery online in 2026 by that month or planned for a 2026 month.
- **Paired:** the battery's plant also has a solar generator in the December 2025 solar book; it is compared with the plant's largest such solar generator (the lead) in four groups: online in 2026, still planned for 2026, planned for 2027 or later, other. **Alone:** every other battery in the December book.
- **Stage:** building = U, V, TS in December; early = P, L in December. T (approved, not started) is in neither.

## Results

### The December 2025 battery book in August 2026

| state in August 2026 | GW (December capacity) | share | generators |
|---|---:|---:|---:|
| online in 2026 | 9.57 | 39.4% | 107 |
| still planned for 2026 | 8.69 | 35.8% | 90 |
| planned for 2027 or later | 3.65 | 15.0% | 43 |
| operating, online date outside 2026 | 0.50 | 2.1% | 2 |
| no longer listed | 1.88 | 7.7% | 21 |
| another status (cancelled, postponed...) | 0.00 | 0.0% | 0 |
| **December book** | **24.28** | | **263** |

Joined the book since December: **4.51 GW in 75 generators** (3.71 GW not listed in December, 0.70 GW then planned for 2027 or later, 0.10 GW then undated or dated before 2026); 1.20 GW of it is already online. Generators in both books changed size by +0.00 GW. So 9.57 + 8.69 + 4.51 = 22.77 GW, the August book.

- **The same share left the year as for solar.** 6.02 GW (24.8%) of December's battery book had left 2026 by August (solar: 24%) and 4.51 GW joined; the net change is -1.51 GW. The December book is 24.28 GW, 1.2% from EIA's 24 GW.
- **Batteries are further along than solar.** 39.4% of the December book is online against solar's 28.8%. Of the 17.72 GW under construction or complete in December, 54.0% is online, 36.7% still planned for 2026, 3.7% slipped to 2027+ and 2.8% dropped out (solar: 38.5% online, 3.6% slipped).
- **Leaving is more often dropping out than for solar.** 1.88 GW of the 6.02 GW that left (31%) is no longer listed, against 22% for solar. No battery moved to a cancelled or postponed status code.
- **Stage predicts the outcome again.** Of the 5.93 GW at the earliest stages (P, L), none is online, 36.2% is still planned for 2026, 40.6% slipped to 2027+ and 23.2% dropped out. Early-stage capacity was 24% of the December book but 66% of what slipped and 73% of what dropped out.

| status in December | GW | online | still 2026 | 2027+ | online outside 2026 | not listed |
|---|---:|---:|---:|---:|---:|---:|
| U, V, TS (building or complete) | 17.72 | 9.57 | 6.50 | 0.65 | 0.50 | 0.50 |
| T (approved, not started) | 0.63 | 0.00 | 0.04 | 0.59 | 0.00 | 0.00 |
| P, L (planned, approvals pending) | 5.93 | 0.00 | 2.15 | 2.41 | 0.00 | 1.38 |

- **Month by month** (January to August reports): the book fell in five of eight reports and ranged from 22.04 to 24.13 GW. The March report added 2.24 GW of newly listed batteries, the largest single entry.

### Batteries beside 2026 solar

6.89 GW (76 generators) of the December battery book sat at a plant with 2026 solar; 17.39 GW (187) did not.

| battery in August \ lead solar in August | online 2026 | still 2026 | 2027+ | other |
|---|---:|---:|---:|---:|
| online in 2026 | 1.63 | 0.35 | 0.04 | 0.05 |
| still planned for 2026 | 0.24 | 1.66 | 0.42 | 0.00 |
| planned for 2027 or later | 0.00 | 0.00 | 2.00 | 0.00 |
| other | 0.08 | 0.30 | 0.00 | 0.13 |

Alone, in August: 7.50 GW online, 6.37 GW still planned for 2026, 1.65 GW 2027+, 1.87 GW other.

- **78.6% of paired battery capacity is in the same group as its solar** (B6 held). Without the cell where both are simply still planned for 2026, agreement is 71.7% (3.75 of 5.23 GW), under the 75% bar; the pre-registration counted that cell, and said in advance that it would, so B6 is scored held by its letter.

## Other things seen (not pre-registered)

- **No paired battery slipped without its solar.** All 19 paired batteries that moved to 2027 or later (2.00 GW) did so with their plant's lead solar generator, and in every one of the 19 the two are now planned for the same month (checked by hand against [`../data/plan_flows_generators.csv`](../data/plan_flows_generators.csv)). The other way round is not true: 0.46 GW of batteries stayed in 2026 or came online while their solar slipped. The largest is Tehuacana Creek 1's 418 MW battery (below).
- **Paired batteries slipped three times as often as standalone ones, mostly because they were earlier.** 29.0% of paired capacity slipped to 2027+, against 9.5% of the rest. But 45% of paired capacity was at the earliest stages in December, against 16% of the rest. Within the early stages, the same share left the year either way (64% paired, 64% alone): paired batteries left by slipping (60% slipped, 4% dropped out), standalone ones by dropping out of the inventory (20% slipped, 44% dropped out). The standalone drop-outs are four generators (1.22 of 1.25 GW), so this is a pattern in a handful of large projects, not across many. One of the four is Lunis Creek's battery, whose solar generator had already left the inventory after the September 2025 report; by the pairing rule it counts as alone.
- **EIA's four largest named 2026 batteries, by raw record.** EIA's article 67205 named the year's four largest battery projects (2,139 MW together). In the August 2026 report none is online. The raw PUDL records of all four, and of their solar generators, are printed in [`../data/plan_flows_spot.md`](../data/plan_flows_spot.md) (job `plan-flows-spot-v2`):
  - **Lunis Creek** (plant 65852, generator LUNBS, 621 MW, Texas): planned for October 2026 at stage L, last listed in the April 2026 report, absent from May to August. Its 617 MW solar generator was last listed in September 2025.
  - **Clear Fork Creek Solar and BESS** (65842, CFCBS, 600 MW, Texas): moved from December 2026 to March 2027 in the February 2026 report, together with its 600 MW solar generator; both under construction since the April 2026 report.
  - **Bellefield 2 Solar & Energy Storage Farm** (64209, 26SBB, 500 MW, California): planned for September 2026 at stage P in December; more than half built since May; planned for December 2026 in August, as is its solar.
  - **Tehuacana Creek 1 Solar and BESS** (65855, TE1BS, 418 MW, Texas): stage L until the July 2026 report, then V (more than half built), planned for December 2026 throughout. Its 836.8 MW solar generator moved to May 2027 at 644.8 MW in the same July report (see [`plan-flows.md`](plan-flows.md)).

## Checks (all passed)

| check | rule | result |
|---|---|---|
| K1 | change = entries - exits + resize for every pair of battery reports, within 0.001 GW | 9 pairs, largest residual 0.000 GW |
| K2 | the December battery book's August states add up to the December book, within 0.01 GW | 24.2827 = 24.2827 |
| K3 | the solar reading is unchanged from plan-flows-v1, each figure within 0.01 GW | largest difference 0.0037 GW |
| K4 | the December battery book within 15% of EIA's 24 GW | 24.28 GW, +1.2% |

The technology census printed `Batteries` (9,555 records) as the battery category. The other matches are pumped hydro (1,089), compressed air (30), solar thermal (176) and `Other Energy Storage` (9 records), which this check does not read.

## Predictions (4 of 6 held)

| | prediction | result | |
|---|---|---|---|
| B1 | at least 17.5% of the December book planned for 2027 or later | 15.0% (3.65 GW) | **missed** |
| B2 | less than 35% of the December book online in 2026 by August | 39.4% | **missed** |
| B3 | less no longer listed or in another status than slipped to 2027+ | 1.88 against 3.65 GW | **held** |
| B4 | early (P, L) at least 40% slipped to 2027+; building (U, V, TS) at most 10% | 40.6%; 3.7% | **held** |
| B5 | joined since December at least 15% of the August book | 19.8% (4.51 of 22.77 GW) | **held** |
| B6 | at least 75% of paired capacity in the same group as its lead solar | 78.6% | **held** |

We expected batteries to slip at least as much as solar and to lag it in delivery. They did the opposite: they slipped less (15.0% against 17.5%) and were further along (39.4% online against 28.8%), so B1 and B2 missed. B3 also holds if the 0.50 GW listed as online outside 2026 is counted with the drop-outs (2.38 against 3.65 GW). B4 held narrowly on its early-stage part (40.6% against a 40% bar).

## Stated in advance for the September 2026 report

Written 2026-10-18, before the September 2026 EIA-860M is released. Scored with `storage_flows.py` 0.1.0 unchanged (its monthly split covers every report in the data).

- **BS1.** The September battery book is smaller than August's. Basis: it fell in five of the eight reports from January to August.
- **BS2.** At least 0.5 GW of batteries comes online in the September report. Basis: 0.55-2.69 GW in every report from January to August.

## Limits

- A state is what the inventory says, not what happened on site. "Not listed" is not confirmed cancellation; EIA-860M's separate list of cancelled and postponed projects was not read.
- Pairing is by EIA plant id and by the December solar book. A battery next to a solar farm under another plant id, or whose solar left the inventory before December (Lunis Creek), counts as alone.
- The paired-against-alone comparisons and the same-month observation were found after the run and are description, not tests. They rest on 19 slipped paired generators and, for the drop-outs, on four large ones.
- EIA's 24 GW is nameplate; this is net summer capacity.
- The plant names above come from the raw records' `plant_name_eia` and match EIA's article in name, county and size.

## Files

- [`storage-flows-preregistration.md`](storage-flows-preregistration.md): checks and predictions, published before the run.
- [`storage-flows-output.md`](storage-flows-output.md): the job's raw output.
- [`../data/storage_flows.csv`](../data/storage_flows.csv): the monthly split for batteries, one row per report pair.
- [`../data/storage_flows_generators.csv`](../data/storage_flows_generators.csv): every battery in the December or August book, with its state in both.
- [`../data/plan_flows_spot.md`](../data/plan_flows_spot.md): raw PUDL records of the named generators.
- [`../tools/plan-flows/`](../tools/plan-flows/): `storage_flows.py` 0.1.0 and its tests, beside `plan_flows.py` 0.1.0 and `spot.py` 0.2.0.

```
cd tools/plan-flows
pip install pandas pyarrow
python -m unittest -v test_storage_flows
python storage_flows.py --data-dir DATA --out-dir out
```

`DATA` holds PUDL's `core_eia860m__changelog_generators.parquet`.
