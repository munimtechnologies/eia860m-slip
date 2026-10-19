# The annual EIA-860 does not date January's plan earlier than EIA-860M does

Status: scored against its pre-registration. All checks passed; all four predictions failed. MV2 of Munim, Inc., 19 October 2026. Made with AI agents working in his name. CC BY 4.0.

## The question

[`annual-flows.md`](annual-flows.md) found that 63.8% of the January 2017 EIA-860M plan came online in 2017, and 62.5% of its onshore wind. EIA's own count for 2017 ([Today in Energy, 21 June 2018](https://www.eia.gov/todayinenergy/detail.php?id=36513)) says 78%, and 86% for onshore wind. The [pre-registration](annual-flows-eia860-preregistration.md) named two possible explanations and tested one, the outcome: it kept the January 2017 plan fixed and dated each of its generators by the annual EIA-860 instead of EIA-860M.

- Code: `tools/annual-flows-candidate/annual860.py` 0.1.1, committed before the run (commit c55b3c2) with [amendment 1](annual-flows-eia860-amendment-1.md), written after the first run read a PUDL table with no operating date.
- Data: PUDL's `core_eia860m__changelog_generators` (reports to 2026-08), the same cached file as `annual-flows.md`, and PUDL's `out_eia__yearly_generators`, the nightly build downloaded in the job (10,643,130 bytes, report years 2001-2026). The 35,635 `monthly_update` and 2,608 `incremental_ytd` rows that PUDL takes from EIA-860M were left out; 628,545 rows were kept, 628,543 marked `final` and 2 with no `data_maturity` value.
- Job: `annual860-v2`, sealed container, 19 October 2026.
- Raw output, unchanged: [`annual860-v2-output.md`](annual860-v2-output.md), [`annual860-v2-unittests.txt`](annual860-v2-unittests.txt) and `data/annual860_v2.json`. `test_annual860_doc.py` checks every number in this note against them.

## Checks (all passed)

| check | rule | result |
|---|---|---|
| C1 | the January 2017 plan equals `annual-flows.md` to 0.1 MW | 26,268.8 MW planned, 16,750.8 MW online in year; onshore wind 6,858.3 MW, 4,283.6 MW, 2,236.3 MW slipped |
| C2 | the six columns used, and report years 2017 and 2018 | none missing; report years 2001-2026 |
| C3 | in every row the classes add up to the planned MW, to 0.05 MW | 493 rows, 0 not adding up |
| C4 | under 10% of the 2017 plan undated (amendment 1) | 0.0% undated |
| unit tests | all pass in the sealed job | 8 of 8 passed |

## Predictions (all four failed)

| prediction | stated in advance | result | verdict |
|---|---|---|---|
| W1 | 2017 onshore wind: share in year by the annual date at least 0.75 | 0.6246 (4,283.6 of 6,858.3 MW) | failed |
| W2 | at least half of the 2017 onshore wind that EIA-860M shows as slipped is in year by the annual date | 0.0000 (0.0 of 2,236.3 MW) | failed |
| W3 | 2017, all technologies: share in year by the annual date at least 0.70 | 0.6370 (16,733.3 of 26,268.8 MW) | failed |
| W4 | in at least 7 of the 8 years 2017-2024, more MW in year by the annual date than delivered in EIA-860M | 0 of 8 years | failed |

## Every year, all technologies (MW)

| year | planned | delivered in EIA-860M | in year by annual date | difference | share_860m | share_860 |
|---|---:|---:|---:|---:|---:|---:|
| 2017 | 26,268.8 | 16,750.8 | 16,733.3 | 17.5 | 0.638 | 0.637 |
| 2018 | 35,982.4 | 27,710.2 | 27,566.5 | 143.7 | 0.770 | 0.766 |
| 2019 | 24,826.1 | 17,688.6 | 17,663.0 | 25.6 | 0.713 | 0.711 |
| 2020 | 42,753.9 | 24,328.7 | 23,798.1 | 530.6 | 0.569 | 0.557 |
| 2021 | 43,181.4 | 29,982.7 | 29,483.2 | 499.5 | 0.694 | 0.683 |
| 2022 | 46,461.4 | 22,608.7 | 20,782.5 | 1,826.2 | 0.487 | 0.447 |
| 2023 | 52,145.7 | 31,386.7 | 30,248.5 | 1,138.2 | 0.602 | 0.580 |
| 2024 | 59,102.8 | 35,178.6 | 34,815.8 | 362.8 | 0.595 | 0.589 |
| 2025 | 60,890.9 | 38,154.5 | 37,676.9 | 477.6 | 0.627 | 0.619 |

"Delivered in EIA-860M" is online in year plus re-keyed online, as in `annual-flows.md`; share_860m is that over planned. "In year by annual date" is the MW whose annual operating month is in the year; share_860 is that over planned. Difference is the first minus the second. Every technology group and every EIA-860M fate is in the raw output.

## What it shows

- **The annual record dates the January 2017 plan to the same years EIA-860M does.** 16,733.3 MW came online in 2017 by the annual operating date, against 16,750.8 MW by EIA-860M. For onshore wind the two are identical: 4,283.6 MW.
- **None of the 2017 wind that EIA-860M shows as slipped came online in 2017 in the annual record.** Of the 2,236.3 MW, the annual record dates 260.0 MW to 2018 and 1,115.0 MW to later years, and lists 861.3 MW that never operated.
- **In no year does the annual record give more.** In every year 2017-2025 the MW in year by the annual date is at or below EIA-860M's delivered MW, by 17.5 MW (2017) to 1,826.2 MW (2022), under 4% of the year's planned MW in every year. In 2022 the gas combined-cycle share is 0.594 in EIA-860M, 0.459 by the annual date.

## What this means

By the pre-registration's own wording, the outcome definition does not explain the 2017 gap, and the delivered shares in `annual-flows.md` stand as a measure of the monthly survey's own January plan. EIA's article points the same way: it names the December 2017 EIA-860M as the source of its charts, so its outcomes are monthly-survey outcomes too, while its plan is what developers reported on the annual EIA-860.

That leaves the other explanation the pre-registration named, the baseline: the annual EIA-860's plan for 2017 may hold different projects than January's EIA-860M, with a similar total. This run does not test it. The next run does, pre-registered in [`annual-flows-eia860-baseline-preregistration.md`](annual-flows-eia860-baseline-preregistration.md).

## Limits

- **The two dates are not fully independent.** PUDL keeps one operating date per generator, harvested from all its EIA-860 and EIA-923 records: the value they agree on, else the most recently reported one, which can come from the latest EIA-860M filing ([PUDL's field description](https://docs.catalyst.coop/pudl/en/nightly/data_dictionaries/pudl_db.html); [PR #3419](https://github.com/catalyst-cooperative/pudl/pull/3419)). It is also the date as later revised, not as first reported. So part of the agreement is built in, and this run cannot say whether EIA's first annual release, which its June 2018 article could have used, dated these generators differently. What it shows is that EIA's annual record as it stands now does not.
- "Never" means never listed as operating in an annual record. It includes generators still planned and, for 2024 and 2025, generators that came online after the last annual report year, whose later records are EIA-860M rows and were left out (13,158.7 MW in 2024, 22,954.2 MW in 2025). It is not cancellation.
- Matching is by plant id and generator id only: 140.1 MW of the 2017 plan has no annual record under its key.
- Only the outcome side is tested here. The baseline is not.

## Reproduce

```
cd tools/annual-flows-candidate
python -m unittest -v test_annual860
python annual860.py --data-dir <folder with the PUDL EIA-860M parquet> --out-dir out
```

`annual860.py` uses `eia860m_slip.py` from the same folder and downloads the annual table if `--annual` does not point to it.
