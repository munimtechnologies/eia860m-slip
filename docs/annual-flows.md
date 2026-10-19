# What January's plan delivered, 2017-2025: EIA-860M annual flows with re-keyed plants linked

Status: description, checked in advance (no predictions are scored). MV2 of Munim, Inc., 19 October 2026. Made with AI agents working in his name. CC BY 4.0.

## What this is

Every January, EIA's monthly generator inventory (EIA-860M) lists the generators their owners plan to bring online that year. This note follows each January plan from 2017 to 2025 to what became of it, and traces every generator that actually came online in the year back to where it stood in January. It is the first run of these flows whose checks all passed.

- Code: `tools/annual-flows-candidate/eia860m_slip.py` 0.3.1 and `checks.py` 0.2.0, committed before the run (commit 329b7e6).
- Data: PUDL's `core_eia860m__changelog_generators` (reports 2015-07 to 2026-08), the same file as the first run.
- Job: `eia860m-slip-031-v1`, sealed container, 19 October 2026.
- Checks, fixed before any code was written: [`annual-flows-preregistration-v2.md`](annual-flows-preregistration-v2.md).
- Raw output, unchanged: [`annual-flows-run2-output.md`](annual-flows-run2-output.md), [`annual-flows-run2-checks.json`](annual-flows-run2-checks.json), [`annual-flows-run2-unittests.txt`](annual-flows-run2-unittests.txt) and `data/annual_flows_run2.json`. `test_annual_flows_doc.py` checks every number in this note against them.

## In short

- **The nine January plans held 391,613.4 MW. 243,789.5 MW (62.3%) came online in the planned year**, including 3,296.5 MW that came online under another plant id. Of the rest, 118,185.4 MW (30.2%) was still planned for a later month in the February report after the year ("slipped"), 15,720.0 MW (4.0%) was operating by that report, 7,858.0 MW (2.0%) was no longer listed, 3,623.3 MW (0.9%) was still planned for a past month or undated ("stale") and 2,437.2 MW (0.6%) had come online before the year. None had another status.
- **Stage in January separates plans more than technology does.** Plans already under construction or testing delivered 0.718 of their capacity in the year; approved but not started, 0.365; still in planning or permitting, 0.271. The five largest technology groups range from 0.557 (battery) to 0.823 (gas combined cycle).
- **A quarter to a third of each year's additions were not in January's plan** (joined share 0.235 to 0.334). 345,267.1 MW came online in 2017-2025. 240,492.3 MW (69.7%) was in that year's January plan and 104,774.8 MW (30.3%) was not: 74,562.4 MW was not listed at all in January, 19,344.0 MW was listed but not as planned, 6,399.0 MW was planned for a later year, 3,296.5 MW was re-keyed and 1,172.9 MW was planned for an earlier month.
- **Linking re-keyed plants removes a double count.** Rule R found exactly the 11 links the re-key search had read and no others. It cuts "not listed" over 2017-2025 from 11,154.5 MW to 7,858.0 MW and lifts 2018's delivered share to 0.770 (0.683 without the links).

## Checks (all passed)

| check | rule | result |
|---|---|---|
| K1 | all unit tests pass in the sealed job | 39 of 39 passed |
| K2 | report runs to 2026-08; 377 operating generators left without a retired record | report max 2026-08; 377 exits |
| K3 | each January plan 2017-2025 equals run 1 to 0.1 MW; on-time and not-online-in-12-months shares each within 0.0005 of run 1 | max plan difference 0.0 MW; on time 0.3247; not online 0.1916 |
| K4 | every row's parts add up to its total; closed years 2016-2025 | 179 rows, 0 not adding up; years 2016-2025 |
| L1 | 2018 has exactly 9 links and 3,141.5 MW, all Allen or Citrus County, same generator id | 9 links, 3,141.5 MW, 0 unexpected |
| L2 | links include 2019 VISTA and 2022 AREXP; any further link is listed and named | 11 links, 0 missing, 0 extra |
| L3 | plan and built totals unchanged each year; not listed + rekeyed online and new entry + rekeyed equal run 1 | 10 years, 0 off |

## The re-key rule

Some plants leave EIA-860M under one plant id and reappear under another while still being built. Two 2018 combined-cycle plants did this, TVA's Allen and Duke Energy Florida's Citrus County (see [`annual-flows-rekey.md`](annual-flows-rekey.md)). Counted naively, such a plant shows up twice: as a dropped plan and as an unplanned addition. Rule R links a planned generator that left the listings to a new entry of the same year when they share the technology group and the generator id, their capacities agree within 0.05 MW, the plan side is at least 10 MW, and the entry is first listed 0-3 months after the generator was last listed. A linked plan generator counts as delivered ("rekeyed online"), and its entry is marked "rekeyed".

## Links found

| year | old key | old plant | new key | new plant | technology | MW | last listed | first listed |
|---|---|---|---|---|---|---:|---|---|
| 2018 | 60671/STG1 | Allen Combined Cycle Plant | 3393/STG1 | Allen | gas_cc | 476.9 | 2018-01 | 2018-02 |
| 2018 | 60138/CC1ST | Citrus County Combined Cycle Plant | 628/CC1ST | Crystal River | gas_cc | 364.7 | 2018-06 | 2018-07 |
| 2018 | 60138/CC2ST | Citrus County Combined Cycle Plant | 628/CC2ST | Crystal River | gas_cc | 364.7 | 2018-06 | 2018-07 |
| 2018 | 60671/CTG1 | Allen Combined Cycle Plant | 3393/CTG1 | Allen | gas_cc | 347.0 | 2018-01 | 2018-02 |
| 2018 | 60671/CTG2 | Allen Combined Cycle Plant | 3393/CTG2 | Allen | gas_cc | 347.0 | 2018-01 | 2018-02 |
| 2018 | 60138/1GTA | Citrus County Combined Cycle Plant | 628/1GTA | Crystal River | gas_cc | 310.3 | 2018-06 | 2018-07 |
| 2018 | 60138/1GTB | Citrus County Combined Cycle Plant | 628/1GTB | Crystal River | gas_cc | 310.3 | 2018-06 | 2018-07 |
| 2018 | 60138/2GTA | Citrus County Combined Cycle Plant | 628/2GTA | Crystal River | gas_cc | 310.3 | 2018-06 | 2018-07 |
| 2018 | 60138/2GTB | Citrus County Combined Cycle Plant | 628/2GTB | Crystal River | gas_cc | 310.3 | 2018-06 | 2018-07 |
| 2019 | 57567/VISTA | Albuquerque Solar Energy Center | 62467/VISTA | Vista Solar Energy Center | solar | 10.0 | 2019-02 | 2019-02 |
| 2022 | 64845/AREXP | Aragonne Mesa Wind Project | 56336/AREXP | Aragonne Wind LLC | wind_onshore | 145.0 | 2022-02 | 2022-03 |

Both sides of every link have the same capacity. Unlike the re-key search, rule R gives each Citrus County unit its own generator id on the other side, so no pair is crosswise. The raw records of all 22 keys are in the output.

## January's plan by year (all technologies, MW)

| year | planned | online in year | rekeyed online | online before year | online next months | slipped | stale | not listed | delivered share |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2017 | 26,268.8 | 16,750.8 | 0.0 | 111.3 | 219.0 | 8,713.4 | 49.0 | 425.3 | 0.638 |
| 2018 | 35,982.4 | 24,568.7 | 3,141.5 | 11.7 | 393.1 | 6,823.2 | 685.4 | 358.8 | 0.770 |
| 2019 | 24,826.1 | 17,678.6 | 10.0 | 4.0 | 1,079.4 | 5,265.1 | 0.0 | 789.0 | 0.713 |
| 2020 | 42,753.9 | 24,328.7 | 0.0 | 361.0 | 2,019.1 | 14,319.7 | 400.0 | 1,325.4 | 0.569 |
| 2021 | 43,181.4 | 29,982.7 | 0.0 | 5.8 | 1,492.1 | 10,166.5 | 771.0 | 763.3 | 0.694 |
| 2022 | 46,461.4 | 22,463.7 | 145.0 | 4.8 | 2,634.0 | 19,774.2 | 479.9 | 959.8 | 0.487 |
| 2023 | 52,145.7 | 31,386.7 | 0.0 | 312.4 | 2,568.2 | 16,743.1 | 832.6 | 302.7 | 0.602 |
| 2024 | 59,102.8 | 35,178.6 | 0.0 | 714.2 | 2,997.6 | 18,355.9 | 405.4 | 1,451.1 | 0.595 |
| 2025 | 60,890.9 | 38,154.5 | 0.0 | 912.0 | 2,317.5 | 18,024.3 | 0.0 | 1,482.6 | 0.627 |
| 2017-2025 | 391,613.4 | 240,493.0 | 3,296.5 | 2,437.2 | 15,720.0 | 118,185.4 | 3,623.3 | 7,858.0 | 0.623 |

Fates are read from each generator's own operating month and from the February report after the year. "Online next months" means operating in that report. "Slipped" means still planned there for a month after the year. Delivered share is (online in year + rekeyed online) / planned. "Other status" is 0.0 MW in every year and is left out.

## The year's additions by where they stood in January (all technologies, MW)

| year | built | in plan | new entry | rekeyed | pulled forward | carried over | listed, not planned | joined share |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2017 | 23,644.6 | 17,050.2 | 4,626.7 | 0.0 | 502.0 | 5.4 | 1,460.3 | 0.279 |
| 2018 | 34,720.3 | 23,915.8 | 6,135.9 | 3,141.5 | 539.2 | 82.8 | 905.1 | 0.311 |
| 2019 | 23,896.4 | 17,475.2 | 4,017.4 | 10.0 | 1,654.2 | 14.5 | 725.1 | 0.269 |
| 2020 | 34,513.1 | 23,860.8 | 8,355.6 | 0.0 | 195.4 | 8.4 | 2,092.9 | 0.309 |
| 2021 | 39,193.5 | 29,985.4 | 6,384.5 | 0.0 | 157.5 | 342.0 | 2,324.1 | 0.235 |
| 2022 | 34,386.9 | 22,911.4 | 8,390.6 | 145.0 | 604.0 | 0.0 | 2,335.9 | 0.334 |
| 2023 | 45,512.8 | 30,757.9 | 12,233.5 | 0.0 | 284.0 | 102.0 | 2,135.4 | 0.324 |
| 2024 | 51,328.6 | 35,345.7 | 11,118.1 | 0.0 | 1,685.1 | 316.0 | 2,863.7 | 0.311 |
| 2025 | 58,070.9 | 39,189.9 | 13,300.1 | 0.0 | 777.6 | 301.8 | 4,501.5 | 0.325 |
| 2017-2025 | 345,267.1 | 240,492.3 | 74,562.4 | 3,296.5 | 6,399.0 | 1,172.9 | 19,344.0 | 0.303 |

"New entry": not listed in January. "Pulled forward": planned in January for a month after the year. "Carried over": planned in January for a month before the year, or undated. "Listed, not planned": listed in January with a status that is not planned (mostly operating). The built side uses each generator's latest capacity and the plan side its January capacity, so "in plan" and "online in year" differ slightly.

Joined share is computed as in run 1, (built - in plan) / built, so it still counts rekeyed entries as joined. Pre-registration v2 did not change its definition, so we kept the old one.

## Pooled 2017-2025, by technology (MW)

| group | planned | delivered share | slipped | not listed | rekeyed online | built | in plan | joined share |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 391,613.4 | 0.623 | 118,185.4 | 7,858.0 | 3,296.5 | 345,267.1 | 240,492.3 | 0.303 |
| solar | 151,609.5 | 0.568 | 52,205.0 | 2,830.4 | 10.0 | 133,759.8 | 85,440.9 | 0.361 |
| wind_onshore | 87,200.2 | 0.621 | 25,005.6 | 2,650.6 | 145.0 | 79,892.2 | 54,602.0 | 0.317 |
| gas_cc | 66,898.0 | 0.823 | 9,254.0 | 10.5 | 3,141.5 | 61,290.7 | 52,290.3 | 0.147 |
| battery | 53,527.9 | 0.557 | 19,444.8 | 1,964.0 | 0.0 | 43,818.0 | 30,204.2 | 0.311 |
| gas_ct | 19,125.5 | 0.674 | 5,254.7 | 260.0 | 0.0 | 17,189.4 | 11,839.5 | 0.311 |

Every technology group, every year and every stage band is in the output.

## Pooled 2017-2025, by stage in January (all technologies, MW)

| band | planned | online in year | rekeyed online | slipped | not listed | delivered share |
|---|---:|---:|---:|---:|---:|---:|
| building | 301,370.7 | 213,163.2 | 3,296.5 | 68,917.1 | 1,762.3 | 0.718 |
| approved | 30,805.5 | 11,242.1 | 0.0 | 14,618.2 | 1,044.9 | 0.365 |
| early | 58,383.2 | 15,834.9 | 0.0 | 34,410.3 | 4,569.4 | 0.271 |
| other | 1,054.0 | 252.8 | 0.0 | 239.8 | 481.4 | 0.240 |

Bands use EIA-860M status codes: building = under construction (U, V) or testing (TS); approved = regulatory approvals received, not under construction (T); early = planned (P) or in permitting (L); other = OT.

## A comparison with EIA's own count for 2017

EIA ran this kind of comparison once, for 2017 ([Today in Energy, 21 June 2018](https://www.eia.gov/todayinenergy/detail.php?id=36513)). Its baseline is the annual EIA-860 at the end of 2016, not the January EIA-860M, so the two are not the same measure. The figure is a comparison, not a check:

| | EIA (baseline: EIA-860, end of 2016) | this run (baseline: January 2017 EIA-860M) |
|---|---|---|
| planned for 2017 | 25.1 GW | 26,268.8 MW |
| came online in 2017 | 19.7 GW (78%) | 16,750.8 MW (63.8%) |
| delayed | 5.3 GW into 2018 or later | 8,713.4 MW slipped |
| gas combined cycle | 10.1 GW planned, 7.5 GW online | 13,030.6 MW planned, 8,607.4 MW online |
| onshore wind | 6.9 GW planned, 86% online | 6,858.3 MW planned, 4,283.6 MW online (62.5%) |
| solar PV | 3.9 GW on schedule, 1.2 GW delayed | 4,430.2 MW planned, 2,787.5 MW online, 1,363.3 MW slipped |

The planned totals are close but the share that came online is not. The gap is largest for onshore wind (86% against 62.5%), where the planned capacities nearly match. We have not traced the difference yet. Possible causes are the baseline (which projects each survey lists for 2017), how a project counts as online (its operating month in EIA-860M against EIA's final annual count), and capacity revisions. Until it is traced, read our delivered shares as an EIA-860M measure that may run below EIA's own.

## The five predictions of the first pre-registration, seen in run 1 (not scored)

F1-F5 were written before run 1, but run 1's output (and what this rule would do to it) was seen before this run, so they are reported here as **seen in run 1, not scored**:

- F1 (slipped at least twice not listed, pooled): this run 118,185.4 MW slipped against 7,858.0 MW not listed (15.0 times); in run 1, not listed was 11,154.5 MW.
- F2 (solar slipped more than not listed in at least 8 of 9 years): this run 9 of 9.
- F3 (other status under 2% of what did not come online): this run 0.0 MW.
- F4 (building delivered share at least three times early): this run 0.718 against 0.271 (2.65 times, below 3); run 1 had 0.707 against 0.271.
- F5 (new entry the largest unplanned source): this run 74,562.4 MW of 101,478.3 MW unplanned (73.5%), not counting re-keyed entries as unplanned; run 1 had 77,858.9 MW of new entry, re-keyed plants included.

## Limits

- Rule R only catches re-keys that keep the generator id and capacity. A plant that moved and was renumbered is still counted as dropped and new.
- "Not listed" is not "cancelled": a generator may leave EIA-860M for reasons the records do not show.
- Capacities are as reported (plan side in January, built side latest), so later uprates or corrections can move a generator between rows.
- 2026 is a part year and is not in these tables. Its flows may contain re-keys that this run did not look for.
- Fates and sources come from EIA-860M alone. Nothing here was checked against owners' filings except the two 2018 plants, and our 2017 delivered share is well below EIA's own figure (above).
- The generator-level output (`flows_generators.csv.gz`, `cohort_rows.csv.gz`) is not in the repository. The commands below rebuild it.

## Reproduce

```
cd tools/annual-flows-candidate
python -m unittest -v test_eia860m_slip test_checks
python eia860m_slip.py --data-dir <folder with the PUDL parquet> --out-dir out
python checks.py --out-dir out
```
