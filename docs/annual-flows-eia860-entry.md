# The projects only the annual EIA-860 plans for a year mostly entered EIA-860M during that year, and not only as projects already being built

Status: scored against its pre-registration. All checks passed; 3 of 4 predictions held. MV2 of Munim, Inc., 20 October 2026. Made with AI agents working in his name. CC BY 4.0.

## The question

[`annual-flows-eia860-baseline.md`](annual-flows-eia860-baseline.md) found that a fifth of the annual EIA-860's plan for each year is projects January's EIA-860M plan does not hold (5,627.2 MW of the 26,808.6 MW plan for 2017), and that this part came online in the year far more often than any January plan (85.1% for 2017). This run asks where those projects stood in EIA-860M: known in January under another status or month, first listed during the year, or never listed ([pre-registration](annual-flows-eia860-entry-preregistration.md), committed at 20:53 UTC on 19 October 2026 as 44de204; job `entry860-v1` was queued at 20:50 UTC, before the commit, and started at 04:49 UTC on 20 October from compete.log, after it).

- Code: `tools/annual-flows-candidate/entry860.py` 0.1.0 (commit 44de204), with baseline860.py 0.1.0 (7699d00), annual860.py 0.1.1 (c55b3c2) and eia860m_slip.py 0.3.1 (329b7e6), all published before the run; the job downloaded each from its commit.
- Data: PUDL's `core_eia860m__changelog_generators` (reports to 2026-08, the same cached file as `annual-flows.md`) and `out_eia__yearly_generators`, the nightly build downloaded in the job (10,643,130 bytes, report years 2001-2026). The 35,635 `monthly_update` and 2,608 `incremental_ytd` rows that PUDL takes from EIA-860M were left out; 628,545 rows were kept.
- Raw output, unchanged: [`entry860-v1-output.md`](entry860-v1-output.md), [`entry860-v1-unittests.txt`](entry860-v1-unittests.txt) and `data/entry860_v1.json`. `test_entry860_doc.py` checks every number in this note against them.

## Checks (all passed)

| check | rule | result |
|---|---|---|
| E1 | the annual columns are present, and the annual plan and annual-only MW equal the nineteenth result in every year 2017-2025 to 0.1 MW | none missing; 2017 annual plan 26,808.6 MW, annual only 5,627.2 MW; every year to 0.1 MW |
| E2 | in every row the entry classes add up to the annual-only MW, to 0.05 MW | 100 rows, 0 not adding up |
| E3 | `in_january_planned_in_year` at most 0.05 MW in every year | largest 0.0 MW |
| E4 | the 2017 new entries equal `annual-flows.md`'s 4,626.7 MW to 0.1 MW | 4,626.7 MW |
| unit tests | all pass in the sealed job | 10 of 10 passed |

## Predictions (3 of four held)

| prediction | stated in advance | result | verdict |
|---|---|---|---|
| A1 | at least 0.60 of the 2017 annual-only MW entered EIA-860M after January | 0.6273 (3,530.1 of 5,627.2 MW) | held |
| A2 | of that, at least 0.80 was operating or building in its first EIA-860M record | 0.6088 (2,149.1 of 3,530.1 MW) | failed |
| A3 | after_share at least 0.50 in at least 6 of the 8 years 2017-2024 | 8 of 8 years | held |
| A4 | at least 0.50 of the 2017 new entries' MW is in the 2017 annual plan | 0.6207 (2,871.8 of 4,626.7 MW) | held |

Shares were compared with their thresholds unrounded, as the pre-registration says, and are rounded here for display.

## Every year, all technologies (MW)

| year | annual plan | annual only | in January, not planned | in January, other month | entered after January | listed before, not in January | never in EIA-860M | after_share |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2017 | 26,808.6 | 5,627.2 | 1,436.3 | 652.0 | 3,530.1 | 0.0 | 8.8 | 0.627 |
| 2018 | 37,113.4 | 6,779.5 | 1,618.9 | 482.2 | 4,666.4 | 12.0 | 0.0 | 0.688 |
| 2019 | 27,422.9 | 5,229.2 | 1,670.6 | 461.4 | 3,067.2 | 30.0 | 0.0 | 0.587 |
| 2020 | 45,840.9 | 10,329.7 | 2,084.3 | 621.7 | 7,158.8 | 464.9 | 0.0 | 0.693 |
| 2021 | 45,495.2 | 8,195.4 | 2,599.6 | 252.0 | 5,337.3 | 6.5 | 0.0 | 0.651 |
| 2022 | 44,620.7 | 9,757.1 | 2,129.9 | 435.3 | 7,141.9 | 10.0 | 40.0 | 0.732 |
| 2023 | 52,775.4 | 11,913.6 | 2,139.6 | 184.0 | 9,565.0 | 25.0 | 0.0 | 0.803 |
| 2024 | 64,633.7 | 16,444.9 | 3,783.1 | 1,629.8 | 11,032.0 | 0.0 | 0.0 | 0.671 |
| 2025 | 65,101.5 | 12,503.2 | 4,296.5 | 911.8 | 7,294.9 | 0.0 | 0.0 | 0.583 |

"Annual plan" and "annual only" as in `annual-flows-eia860-baseline.md`. The entry classes are read from PUDL's EIA-860M changelog: "in January" means a record in force in the report for January of the year; "entered after January" means the generator's first EIA-860M record is in a later report; "listed before, not in January" means it was listed earlier but had no record in force in January; "never in EIA-860M" means no record under that plant and generator id. `in_january_planned_in_year` is at most 0.05 MW in every year (E3) and is left out. after_share: entered after January / annual only.

## Every year: what entered after January, by its first EIA-860M band (MW)

| year | entered after January | operating | building | approved | early | other | operating or building share | in-year share |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2017 | 3,530.1 | 336.6 | 1,812.5 | 179.7 | 1,200.4 | 0.9 | 0.609 | 0.812 |
| 2018 | 4,666.4 | 107.9 | 1,259.1 | 2,495.7 | 803.7 | 0.0 | 0.293 | 0.821 |
| 2019 | 3,067.2 | 111.1 | 318.2 | 1,800.6 | 837.3 | 0.0 | 0.140 | 0.494 |
| 2020 | 7,158.8 | 568.0 | 4,079.6 | 979.0 | 1,532.2 | 0.0 | 0.649 | 0.594 |
| 2021 | 5,337.3 | 199.1 | 3,235.2 | 1,274.9 | 628.1 | 0.0 | 0.643 | 0.524 |
| 2022 | 7,141.9 | 547.3 | 3,658.9 | 894.7 | 2,041.0 | 0.0 | 0.589 | 0.513 |
| 2023 | 9,565.0 | 549.2 | 5,623.9 | 2,686.8 | 705.1 | 0.0 | 0.645 | 0.682 |
| 2024 | 11,032.0 | 761.9 | 9,528.0 | 390.3 | 351.8 | 0.0 | 0.933 | 0.696 |
| 2025 | 7,294.9 | 289.1 | 5,821.5 | 506.3 | 678.0 | 0.0 | 0.838 | 0.795 |

Band of the generator's first EIA-860M record: operating (OP, SB, OS, OA), building (U, V, TS), approved (T), early (P, L). "In-year share": the part of the after-January MW whose annual operating month is in the year.

## Every year: EIA-860M new entries found in the annual plan (MW)

| year | new entries | in the annual plan | share |
|---|---:|---:|---:|
| 2017 | 4,626.7 | 2,871.8 | 0.621 |
| 2018 | 6,135.9 | 3,828.4 | 0.624 |
| 2019 | 4,017.4 | 1,873.7 | 0.466 |
| 2020 | 8,355.6 | 4,266.4 | 0.511 |
| 2021 | 6,384.5 | 2,815.2 | 0.441 |
| 2022 | 8,390.6 | 3,815.9 | 0.455 |
| 2023 | 12,233.5 | 6,765.5 | 0.553 |
| 2024 | 11,118.1 | 7,662.0 | 0.689 |
| 2025 | 13,300.1 | 5,971.3 | 0.449 |

"New entries": the year's EIA-860M additions that were not listed in January (eia860m_slip 0.3.1, rule R applied, as in `annual-flows.md`), looked up by plant and generator id in the year's annual plan, any technology group.

## 2017 by technology (MW)

| group | annual only | entered after January | after_share | operating or building share | in-year share | new entries | in the annual plan | share |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 5,627.2 | 3,530.1 | 0.627 | 0.609 | 0.812 | 4,626.7 | 2,871.8 | 0.621 |
| wind_onshore | 2,184.2 | 1,808.9 | 0.828 | 0.725 | 0.985 | 2,137.8 | 1,781.3 | 0.833 |
| solar | 1,873.5 | 1,462.4 | 0.781 | 0.419 | 0.584 | 2,017.7 | 848.2 | 0.420 |
| gas_cc | 0.0 | 0.0 | n/a | n/a | n/a | 0.0 | 0.0 | n/a |
| battery | 59.3 | 49.3 | 0.831 | 0.598 | 0.598 | 61.0 | 39.4 | 0.646 |
| gas_ct | 797.3 | 127.3 | 0.160 | 1.000 | 1.000 | 176.5 | 127.3 | 0.721 |

## 2017: entered after January, by quarter of first report (MW)

| first report | all | onshore wind |
|---|---:|---:|
| 2017-Q1 | 1,135.3 | 411.8 |
| 2017-Q2 | 1,777.4 | 1,107.4 |
| 2017-Q3 | 617.4 | 289.7 |
| 2017-Q4 | 0.0 | 0.0 |
| after 2017 | 0.0 | 0.0 |

Q1 is February and March (the January report is the baseline).

## 2017 onshore wind in the annual plan only (largest 5)

| plant | key | MW | entry | first listed | first band | annual fate |
|---|---|---:|---|---|---|---|
| Red Dirt Wind Project | 61270/RDDRT | 299.3 | entered_after_january | 2017-05 | building | in_year |
| Thunder Ranch Wind Project | 61269/WT1 | 297.8 | entered_after_january | 2017-05 | building | in_year |
| Bethel Wind Farm LLC | 60414/GEN1 | 276.0 | in_january_not_planned | 2016-05 | approved | in_year |
| Red Pine Wind Project | 61357/RP1 | 200.0 | entered_after_january | 2017-07 | building | in_year |
| Beaver Creek Wind | 61079/1 | 170.0 | entered_after_january | 2017-02 | early | in_year |

## 2017 onshore wind new entries not in the annual plan (largest 5)

| key | MW |
|---|---:|
| 60987/GEN1 | 300.0 |
| 2240/CTNWD | 40.9 |
| 61668/CR2-1 | 2.3 |
| 61668/CR2-2 | 2.3 |
| 61668/CR2-3 | 2.3 |

The 15 largest on each side, all technologies and onshore wind, are in the raw output.

## What it shows

- **Most of the annual-only part entered EIA-860M during the year (A1 held).** Of the 5,627.2 MW of the 2017 annual plan that January's EIA-860M plan did not hold, 3,530.1 MW (0.627) was first listed in an EIA-860M report after January 2017: 1,135.3 MW in February-March, 1,777.4 MW in April-June and 617.4 MW in July-September, and none from October on. Of the rest, 1,436.3 MW was in January's report with a status that was not planned, 652.0 MW was planned there for a month outside 2017, and 8.8 MW was never listed. Four of the five largest onshore wind projects only the annual survey planned (Red Dirt, Thunder Ranch, Red Pine, Beaver Creek) are entrants after January; Bethel (276.0 MW) was in January's report with a status that was not planned.
- **They were not mostly built or being built when first listed (A2 failed).** Of the 3,530.1 MW that entered after January, 2,149.1 MW (0.609) was operating or under construction in its first EIA-860M record, below the 0.80 we predicted; 1,200.4 MW was first listed at the earliest stages (P, L) and 179.7 MW as approved but not yet being built. Even so, 0.812 of it came online in 2017 by the annual operating date. Beaver Creek Wind (170.0 MW) was first listed in the 2017-02 report at an early stage and came online in 2017.
- **The pattern holds every year (A3 held), but the first band does not.** after_share was at least 0.50 in all 8 years 2017-2024; over 2017-2025 it ranges from 0.583 (2025) to 0.803 (2023). The share of the after-January entrants first listed as operating or building ranges from 0.140 (2019) to 0.933 (2024): in 2018, 2,495.7 of the 4,666.4 MW was first listed as approved, and in 2019, 1,800.6 of the 3,067.2 MW.
- **From the other side (A4 held).** Of the 4,626.7 MW that EIA-860M added to its 2017 list after January, 2,871.8 MW (0.621) is in the 2017 annual plan; onshore wind 1,781.3 of 2,137.8 MW (0.833). Over 2017-2025 the share ranges from 0.441 (2021) to 0.689 (2024). The largest 2017 onshore wind entrant not in the annual plan is 60987/GEN1 (300.0 MW); the next is 40.9 MW.

## What this means

A1 and A3 held, so, in the pre-registration's own words, the annual-only part of the annual plan is mostly projects EIA-860M first listed during the year. The annual EIA-860's planned list for 2017 holds projects that EIA-860M first listed as late as July-September 2017, which a list made at the start of the year could not hold. A2 failed: the projects did not arrive mostly already built or being built. In 2017, 1,200.4 MW of them was first listed at an early stage and 179.7 MW as approved, and 0.812 of all the after-January MW still came online in 2017. From the other side, 0.621 of what EIA-860M added to its 2017 list after January is in the annual plan for 2017 (A4).

For anyone starting a planned-against-built comparison from the annual survey's planned list: that list is partly a record of projects that became known during the planned year, not a forecast made in January. This fits the nineteenth result, where a share measured from it (EIA's 78% for 2017) is higher than one measured from January's EIA-860M plan (our 63.8%). We do not test why the annual list includes these projects (when respondents file, how EIA compiles the planned list).

## Limits

- A generator's first EIA-860M listing is its first record in PUDL's changelog, which starts with the July 2015 report, so a generator first listed then may have been listed earlier; for every year scored that start is before January.
- Matching is by key only. A generator renumbered between the surveys reads "never in EIA-860M" here even if EIA-860M lists it under another key; the named lists let a reader check the largest ones. None of the five named onshore wind annual-only generators reads "never in EIA-860M"; in 2017 only 8.8 MW does, all of it solar.
- An entrant's first band is from its first record, which can lag the true status by the time EIA-860M takes to add a project.
- Why the annual survey's list includes these projects (when respondents file, how EIA compiles the planned list) is not tested; this run only says where the projects stood in EIA-860M. That no 2017 entrant was first listed from October on is consistent with the annual file being compiled during the year, but it is not a test of it.
- The planned month and the operating date are PUDL's harvested values from the current nightly build, as in the nineteenth result.

## Reproduce

```
cd tools/annual-flows-candidate
python -m unittest -v test_entry860
python entry860.py --data-dir <folder with the PUDL EIA-860M parquet> --out-dir out
```

`entry860.py` uses `eia860m_slip.py`, `annual860.py` and `baseline860.py` from the same folder and downloads the annual table if `--annual` does not point to it.
