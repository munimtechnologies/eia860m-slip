# The 2017 gap is in the baseline: a fifth of each survey's plan is projects the other does not hold, and those parts fared oppositely

Status: scored against its pre-registration. All checks passed; all five predictions held. MV2 of Munim, Inc., 19 October 2026. Made with AI agents working in his name. CC BY 4.0.

## The question

[`annual-flows.md`](annual-flows.md) found that 63.8% of the January 2017 EIA-860M plan came online in 2017, and 62.5% of its onshore wind; EIA's own count ([Today in Energy, 21 June 2018](https://www.eia.gov/todayinenergy/detail.php?id=36513)) says 78%, and 86% for onshore wind. [`annual-flows-eia860.md`](annual-flows-eia860.md) ruled out the outcome definition. This run tests the other named explanation, the baseline: EIA's plan is the annual EIA-860 at the end of 2016, which may hold different projects than January's EIA-860M ([pre-registration](annual-flows-eia860-baseline-preregistration.md); [amendment 1](annual-flows-eia860-baseline-amendment-1.md), committed at 17:59 UTC: the first job never started, so the test ran as `baseline860-v2` with 3 GB and the same code, starting at 18:34 UTC).

- Code: `tools/annual-flows-candidate/baseline860.py` 0.1.0 (commit 7699d00), with annual860.py 0.1.1 (c55b3c2) and eia860m_slip.py 0.3.1 (329b7e6), all published before the run; the job downloaded each from its commit.
- Data: PUDL's `core_eia860m__changelog_generators` (reports to 2026-08, the same cached file as `annual-flows.md`) and `out_eia__yearly_generators`, the nightly build downloaded in the job (10,643,130 bytes, report years 2001-2026). The 35,635 `monthly_update` and 2,608 `incremental_ytd` rows that PUDL takes from EIA-860M were left out; 628,545 rows were kept.
- Raw output, unchanged: [`baseline860-v2-output.md`](baseline860-v2-output.md), [`baseline860-v2-unittests.txt`](baseline860-v2-unittests.txt) and `data/baseline860_v2.json`. `test_baseline860_doc.py` checks every number in this note against them.

## Checks (all passed)

| check | rule | result |
|---|---|---|
| D1 | the nine columns used, and report years 2016-2024 | none missing; report years 2001-2026 |
| D2 | January's 2017 EIA-860M plan equals `annual-flows.md` to 0.1 MW | 26,268.8 MW; onshore wind 6,858.3 MW |
| D3 | in every row the annual classes add up to the annual plan, to 0.05 MW | 101 rows, 0 not adding up |
| D4 | the 2017 annual plan is between 10,000 and 50,000 MW | 26,808.6 MW |
| unit tests | all pass in the sealed job | 7 of 7 passed |

## Predictions (all five held)

| prediction | stated in advance | result | verdict |
|---|---|---|---|
| B1 | 2017 annual plan, all technologies, within 10% of EIA's 25.1 GW | 26,808.6 MW, 6.8% from 25,100 MW | held |
| B2 | 2017 annual plan, all technologies: share in year at least 0.75 | 0.8002 (21,451.1 of 26,808.6 MW) | held |
| B3 | 2017 annual plan, onshore wind: share in year at least 0.80 | 0.9495 (6,578.2 of 6,928.1 MW) | held |
| B4 | at most 0.80 of the 2017 annual plan's onshore wind is also in January's EIA-860M plan | 0.6847 (4,743.9 of 6,928.1 MW) | held |
| B5 | in at least 6 of 8 years 2017-2024, the annual plan's share in year is above EIA-860M's delivered share | 8 of 8 years | held |

Shares were compared with their thresholds unrounded, as the pre-registration says, and are rounded here for display.

## Every year, all technologies (MW)

| year | annual plan | in year | share_in_year | both | annual only | January EIA-860M plan | delivered | share_860m | EIA-860M only |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2017 | 26,808.6 | 21,451.1 | 0.800 | 21,181.4 | 5,627.2 | 26,268.8 | 16,750.8 | 0.638 | 5,420.2 |
| 2018 | 37,113.4 | 32,022.3 | 0.863 | 30,333.9 | 6,779.5 | 35,982.4 | 27,710.2 | 0.770 | 5,565.3 |
| 2019 | 27,422.9 | 20,166.6 | 0.735 | 22,193.7 | 5,229.2 | 24,826.1 | 17,688.6 | 0.713 | 2,552.6 |
| 2020 | 45,840.9 | 29,835.7 | 0.651 | 35,511.2 | 10,329.7 | 42,753.9 | 24,328.7 | 0.569 | 6,843.6 |
| 2021 | 45,495.2 | 34,559.4 | 0.760 | 37,299.8 | 8,195.4 | 43,181.4 | 29,982.7 | 0.694 | 5,560.8 |
| 2022 | 44,620.7 | 26,801.0 | 0.601 | 34,863.6 | 9,757.1 | 46,461.4 | 22,608.7 | 0.487 | 11,620.3 |
| 2023 | 52,775.4 | 38,472.9 | 0.729 | 40,861.8 | 11,913.6 | 52,145.7 | 31,386.7 | 0.602 | 10,796.3 |
| 2024 | 64,633.7 | 46,366.6 | 0.717 | 48,188.8 | 16,444.9 | 59,102.8 | 35,178.6 | 0.595 | 10,844.9 |
| 2025 | 65,101.5 | 48,527.9 | 0.745 | 52,598.3 | 12,503.2 | 60,890.9 | 38,154.5 | 0.627 | 8,616.4 |

"Annual plan": generators the annual EIA-860 for the year before lists as planned with a current planned operating month in the year. "In year": its annual operating month is in the year. "Both": also in January's EIA-860M plan for the year (same plant and generator id; re-keyed plants under either key). "Annual only": the rest of the annual plan. "January EIA-860M plan", "delivered" and share_860m as in `annual-flows.md`; "EIA-860M only": the part of January's plan not in the annual plan. Every technology group and every annual class is in the raw output.

## 2017 by technology (MW)

| group | annual plan | share_in_year | both | both: share in year | annual only | annual only: share in year | January EIA-860M plan | share_860m | EIA-860M only | EIA-860M only: delivered share |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 26,808.6 | 0.800 | 21,181.4 | 0.787 | 5,627.2 | 0.851 | 26,268.8 | 0.638 | 5,420.2 | 0.038 |
| wind_onshore | 6,928.1 | 0.950 | 4,743.9 | 0.932 | 2,184.2 | 0.987 | 6,858.3 | 0.625 | 2,252.4 | 0.000 |
| solar | 5,309.0 | 0.747 | 3,435.5 | 0.804 | 1,873.5 | 0.641 | 4,430.2 | 0.629 | 1,192.0 | 0.013 |
| gas_cc | 11,407.2 | 0.747 | 11,407.2 | 0.747 | 0.0 | n/a | 13,030.6 | 0.661 | 1,654.2 | 0.073 |
| battery | 164.9 | 0.699 | 105.6 | 0.812 | 59.3 | 0.497 | 128.6 | 0.744 | 23.0 | 0.000 |
| gas_ct | 1,709.0 | 0.620 | 911.7 | 0.398 | 797.3 | 0.875 | 1,001.7 | 0.362 | 90.0 | 0.000 |

"Both: share in year" and "annual only: share in year" are by the annual operating date; "EIA-860M only: delivered share" is EIA-860M's own delivered share of that part. Gas combined cycle is the one group shown whose annual plan is wholly inside January's; the 1,654.2 MW only EIA-860M lists is mostly York Energy Center and Eagle Valley, both of which slipped (the all-technologies lists in the raw output name them).

## 2017 onshore wind in the annual plan only (largest 5)

| plant | key | MW | fate |
|---|---|---:|---|
| Red Dirt Wind Project | 61270/RDDRT | 299.3 | in_year |
| Thunder Ranch Wind Project | 61269/WT1 | 297.8 | in_year |
| Bethel Wind Farm LLC | 60414/GEN1 | 276.0 | in_year |
| Red Pine Wind Project | 61357/RP1 | 200.0 | in_year |
| Beaver Creek Wind | 61079/1 | 170.0 | in_year |

## 2017 onshore wind in January's EIA-860M plan only (largest 5)

| plant | key | MW | fate |
|---|---|---:|---|
| Goodnight | 59246/GOOD1 | 500.0 | slipped (later) |
| Mariah East | 59006/MARN | 230.4 | slipped (never) |
| Mariah South | 59007/MAR S | 230.4 | slipped (never) |
| Grady Wind Energy Center, LLC | 60317/1 | 200.8 | slipped (later) |
| Bright Stalk Wind Farm II | 57622/GEN1 | 200.0 | slipped (never) |

"Fate" on the annual side is the annual class; on the EIA-860M side it is the EIA-860M state in the February 2018 report and, in brackets, the annual class of the same generator. The 15 largest on each side, all technologies and onshore wind, are in the raw output.

## What it shows

- **The rebuilt annual plan reproduces EIA's measure.** The annual EIA-860 for 2016 lists 26,808.6 MW as planned for 2017, 6.8% above EIA's 25.1 GW, and 21,451.1 MW of it (80.0%) came online in 2017 by the annual operating date, against EIA's 78%. For onshore wind it lists 6,928.1 MW, of which 6,578.2 MW (94.9%) came online in 2017, against EIA's 86% of 6.9 GW.
- **A fifth of each plan is projects the other does not hold, and those parts fared oppositely.** 21,181.4 MW of the annual plan is also in January's EIA-860M plan; 5,627.2 MW (21.0%) is not, and 85.1% of that came online in 2017. The other way round, 5,420.2 MW of January's 26,268.8 MW plan (20.6%) is not in the annual plan, and 3.8% of that was delivered in 2017. The two surveys agree about the projects they share: 78.7% of the overlap came online in 2017 by the annual date.
- **For onshore wind the split is the whole gap.** 4,743.9 MW (68.5%) of the annual plan's onshore wind is in January's plan too; the 2,184.2 MW that is not came online in 2017 at 98.7%, led by Red Dirt Wind Project, Thunder Ranch Wind Project and Bethel Wind Farm LLC. January's plan holds 2,252.4 MW of onshore wind that the annual plan does not, and 0.0% of it was delivered in 2017: Goodnight (500.0 MW), Mariah East (230.4 MW) and Mariah South (230.4 MW) and the rest all slipped past the year or left the listings.
- **The pattern holds in every year.** In all 8 years 2017-2024 the annual plan's share in year is above January's EIA-860M delivered share, smallest in 2019 (0.735 against 0.713) and largest in 2017 (0.800 against 0.638); 2025, outside B5, is 0.745 against 0.627.

## What this means

By the pre-registration's own wording: B1-B3 held, so the rebuilt annual plan reproduces EIA's measure and the 2017 gap lies in which projects the two plans hold; B4 held, so for onshore wind the two plans differ in composition, and the lists above name the projects; B5 held, so the difference is not peculiar to 2017. EIA's 78% and the 63.8% in `annual-flows.md` are both right, about different lists.

Why the lists differ is not tested here. The two surveys describe the same moment, the start of 2017, but January's EIA-860M reports the inventory as of the end of January 2017, while the annual EIA-860 for 2016 is collected and published during 2017. The projects only the annual survey lists for 2017 came online in 2017 at a rate above any January plan's in 2017-2025 (85.1% all technologies, 98.7% for onshore wind, against at most 0.770 for a January plan in `annual-flows.md`), and the projects only January's EIA-860M lists mostly slipped. That is what one would expect if the annual list for a year is, in part, compiled with knowledge of how the year went. `annual-flows.md` counts 4,626.7 MW of 2017 additions that were not listed in EIA-860M at all in January; whether the annual-only projects are those generators, entering EIA-860M during 2017, is the next test, and it is pre-registered before any record is read.

For anyone quoting either survey's "planned capacity" figure: the two agree on the total but not on the projects, and the one-off EIA comparison for 2017 should not be read as the delivery rate of a January EIA-860M plan.

## Limits

- The planned month is the one the annual report gave at the end of the year before, as PUDL's current nightly build holds it; EIA's article may have used an earlier release of the same survey.
- The annual operating date is PUDL's harvested value (one per generator, as later revised), as in `annual-flows-eia860.md`, with the same limit that it can come from the latest EIA-860M filing.
- Matching is by key only; a generator renumbered between the two surveys is `annual only` on one side and `EIA-860M only` on the other. The 15 largest on each side for 2017 are named in the raw output; no plant name appears in both of the onshore-wind lists, but the rest was not checked.
- For 2024 and 2025, generators that came online after the last annual report year read `never`, not `later`; that changes how the part not in year splits, not `share_in_year`.
- EIA's figures (25.1 GW, 78%, 6.9 GW, 86%) are quoted from EIA's article and are not checked here.

## Reproduce

```
cd tools/annual-flows-candidate
python -m unittest -v test_baseline860
python baseline860.py --data-dir <folder with the PUDL EIA-860M parquet> --out-dir out
```

`baseline860.py` uses `eia860m_slip.py` and `annual860.py` from the same folder and downloads the annual table if `--annual` does not point to it.
