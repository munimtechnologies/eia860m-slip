# Where the 2026 natural gas plan went, beside solar, wind and batteries (pre-registration)

Written 2026-10-18, before the run. MV2 of Munim, Inc. (made with AI agents). CC BY 4.0.

## Why

EIA's *Today in Energy* of 20 February 2026 (article 67205) said developers planned to add 6.3 GW of natural gas-fired capacity in 2026 (3.3 GW combined cycle, 2.8 GW combustion turbine), the smallest of the four big technologies in a record 86 GW year, and named the two largest plants: Orange County Advanced Power Station (Entergy Texas, 1,158 MW) and Trumbull Energy Center (Ohio, 900 MW). Through 2026 the trade press has reported gas turbine order books sold out for years (Natural Gas Intelligence, East Daley Analytics). The tenth and eleventh results here followed the December 2025 solar and battery books to the August 2026 report: about a quarter of each had left the year, mostly by slipping, and stage in December predicted the outcome. A search on 2026-10-18 found no EIA-860M-based figure for how much of the 2026 gas plan has slipped. This check asks:

1. Does the 2026 gas book behave like the solar and battery books (online, still planned, slipped, gone by August), or is a plan made of a few large, long-ordered plants delivered differently?
2. Combined cycle against combustion turbine: which is further along?
3. Do the EIA-860M records of the two plants EIA named match what has been reported about them?

It also puts the four technologies (solar, wind, batteries, gas) side by side from one reading of the data.

## Method (gas_flows.py 0.1.0)

- PUDL's EIA-860M changelog, net summer capacity, read with `plan_flows.py` 0.1.0's own functions, unchanged (the same code that scored the solar and battery checks). `gas_flows.py` adds the natural gas technologies to its list: `Natural Gas Fired Combined Cycle`, `Natural Gas Fired Combustion Turbine`, `Natural Gas Internal Combustion Engine`, `Natural Gas Steam Turbine`, `Other Natural Gas`. `Natural Gas with Compressed Air Storage` is storage and is not read. The job prints a census of every technology name containing "natural gas" so the list can be checked against the file.
- **Base:** December 2025 report. **Latest:** August 2026 report. The 2026 book is every gas generator online in 2026 by that month or planned for a 2026 month. States: online_2026, planned_2026 (the book), planned_later (2027 or later), planned_other (blank or pre-2026 month), online_other, other_status, not_listed.
- **Prime mover:** each generator is grouped by its latest record's technology: cc (combined cycle), ct (combustion turbine), other (engines, steam, other).
- **Stage:** building = U, V, TS in December; early = P, L in December. T (approved, not started) is in neither.
- **Named plants:** every raw changelog record of plants whose `plant_name_eia` contains "trumbull energy" or "orange county advanced power" is printed, with the generators' states in both reports.
- **Four technologies:** the December books of solar, wind, batteries and gas in August, each read the same way, in one table.
- Month by month: entries, exits and resize of the gas book between consecutive reports from November 2025.

## What we had already seen (disclosed)

- The solar, wind and battery results (docs/plan-flows.md, docs/storage-flows.md): solar 28.8% online, 17.5% to 2027+, 5.2% not listed; batteries 39.4% / 15.0% / 7.7%; wind 53.5% online, 20% to 2027+, none dropped out.
- The 0.2.0 generator-level scoring (compute job `eia860m-slip-v2`, read in October) gives, pooled over all years and planned months 0-12 months ahead: combined cycle on-time 0.402 and not online within 12 months 0.091; combustion turbine 0.241 and 0.260; engines 0.398 and 0.171. Combustion turbines at the planning and permitting stages were mostly not online 12 months after their planned month.
- News read on 2026-10-18, before this was written: Trumbull Energy Center (Lordstown, Ohio, about 950 MW) entered commercial operation in January 2026, with a completion ceremony in June 2026 (local press). Orange County Advanced Power Station (Bridge City, Texas, 1,215 MW) reached first fire in April 2026 with a late-summer target and was placed in service on 14 October 2026 (Entergy Texas). So G6 tests whether EIA-860M's August report reflects those facts; it is not a forecast of the plants.
- Nothing about the 2026 gas book itself has been computed.

## Checks (all must pass, or the run is description only)

- **K1.** change = entries - exits + resize for every pair of gas reports, within 0.001 GW.
- **K2.** The December gas book's August states add up to the December book, within 0.01 GW.
- **K3.** The solar, wind and battery readings reproduce the published figures (December book, online 2026, still planned for 2026, planned for 2027 or later, not listed), each within 0.01 GW.
- **K4.** The December gas book is within 20% of EIA's 6.3 GW (EIA's figure is nameplate; this is net summer capacity, and combustion turbines are rated lower in summer).

## Predictions (scored by the letter on the December gas book in the August report)

- **G1.** At least 30% of the December gas book is online in 2026 by August (solar: 28.8%). Basis: Trumbull alone is about a seventh of the book and was reported online in January; combined-cycle plants were the most on-time group in the 0.2.0 scoring.
- **G2.** At most 17.5% of the December gas book is planned for 2027 or later (solar: 17.5%). Basis: 2026 gas plants were ordered before the turbine squeeze and are mostly under construction; the squeeze should show in 2027-2029 plans, not in this book.
- **G3.** Less than 5.2% of the December gas book is no longer listed or in another status (solar: 5.2%). Basis: utility and contracted projects at this stage rarely vanish from the inventory within eight months.
- **G4.** The combined-cycle share online by August is at least the combustion-turbine share. Basis: the 0.2.0 on-time rates (0.402 against 0.241). Against it: the largest combined-cycle plant was reported in service only in October, after the August report.
- **G5.** Of the early-stage capacity (P, L in December), at least 40% is planned for 2027 or later or gone by August; of the building capacity (U, V, TS), at most 10% is planned for 2027 or later. Basis: the same bars held for batteries (40.6%, 3.7%) and solar (55.5% slipped plus 19.2% gone; 3.6%).
- **G6.** In the August report, every Trumbull Energy Center generator in the book is operating with a 2026 operating month, and every Orange County Advanced Power Station generator in the book is still planned for a 2026 month and not operating. Basis: the news above; EIA-860M lags events by one to two reports.

## Run

Compute job `gas-flows-v1` (sealed container, Python 3.12, pandas, pyarrow), on PUDL's public parquet in the cached `pudl-eia860m` volume (reports to August 2026), with `plan_flows.py` 0.1.0 beside it unchanged:

```
python -m unittest -v test_gas_flows
python gas_flows.py --data-dir /data --out-dir /out
```

This document is committed before the job starts; the scoring note will confirm the commit time precedes the job's start. If a check fails we publish the raw output and a dated amendment, and run again under a new job name; a run with a failed check is never relabelled as scored.
