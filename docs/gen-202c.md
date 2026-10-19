# How much did the plants under DOE 202(c) orders generate? A third of their usual output

MV2 of Munim, Inc., 19 October 2026. Made with AI agents working in his name. Text and data CC BY 4.0; code ([`../gen_202c.py`](../gen_202c.py) 0.1.0) Apache-2.0.

**Status: scored.** The checks and predictions were published before the job ran ([`gen-202c-preregistration.md`](gen-202c-preregistration.md), committed in 0.2.16 on 19 October 2026). Job `gen-202c-v1` ran in a sealed container on 2026-10-19 (07:38-07:41Z); its 12 unit tests passed first. **Both checks passed. All four scorable predictions held; the fifth cannot be scored yet.** Raw output: [`gen-202c-output.md`](gen-202c-output.md); every plant-month: [`../data/gen_202c_months.csv`](../data/gen_202c_months.csv).

## Question

DOE's orders under section 202(c) of the Federal Power Act require eight plants' units to stay available ([`doe-202c-orders.md`](doe-202c-orders.md): 4,849.9 MW of summer capacity since 4 June 2026). They do not say how much the units must run. How much did the covered units generate in the months they were under order, against the same calendar months of 2021-2024?

## Method (as pre-registered)

- EIA-923 monthly net generation by generator, from PUDL's `core_eia923__monthly_generation` (809,021 records; last month with data **June 2026**; the 2026 months carry EIA's `incremental_ytd` maturity, the 2025 months `final`).
- Covered units and summer MW from [`../data/doe_202c_plant_mw.csv`](../data/doe_202c_plant_mw.csv); days under order from [`../data/doe_202c_orders.csv`](../data/doe_202c_orders.csv).
- A plant-month is the sum of the covered units; it is missing if any unit has no value. An included month is a full order month with a 2021-2024 same-month baseline. A plant's ratio is its net generation over its baseline, summed over included months; CF is net generation over summer MW times the hours.

## Results

| plant | summer MW | window | months | net MWh | baseline MWh | ratio | CF | CF baseline | idle months |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| J.H. Campbell 1-3 | 1,330.5 | Jan-Jun 2026 | 6 | 1,766,053 | 3,370,852 | 0.524 | 30.6% | 58.3% | 0 |
| J.H. Campbell 1-3 | 1,330.5 | Jun 2025-Jun 2026 | 13 | 5,410,749 | 8,465,147 | 0.639 | 42.9% | 67.1% | 0 |
| Centralia 2 | 670.0 | Jan-Jun 2026 | 6 | 0 | 1,280,930 | 0.000 | 0.0% | 44.0% | 6 |
| Craig 1 | 427.0 | Jan-Jun 2026 | 6 | 56,782 | 1,076,411 | 0.053 | 3.1% | 58.0% | 5 |
| F.B. Culley 2 | 90.0 | Jan-Jun 2026 | 6 | 48,923 | 93,946 | 0.521 | 12.5% | 24.0% | 1 |
| Eddystone 3-4 | 760.0 | Jun-Dec 2025 | 7 | 18,651 | 26,575 | 0.702 | 0.5% | 0.7% | 5 |
| R.M. Schahfer 17-18 | 722.0 | Jan-Jun 2026 | 6 | 303,344 | 853,259 | 0.355 | 9.7% | 27.2% | 4 |
| Stanton 1 | 453.4 | none yet | 0 | | | | | | |
| H.A. Wagner 4 | 397.0 | Jun 2026 | 1 | 8,233 | 281 | 29.299 | 2.9% | 0.1% | 0 |

An idle month is an included month with net generation of zero or less. Eddystone has no 2026 values in the table (its two units' last value is December 2025); Stanton's first order began on 4 June 2026, so June is not a full order month and July is beyond the data.

**Combined, January-June 2026: 31 plant-months at six plants, 2,183,335 MWh against a baseline of 6,675,679 MWh, a ratio of 0.327.** The units under order generated about a third of what the same units generated in the same months of 2021-2024; the gap is about 4.5 million MWh over six months.

- **Centralia 2 (670 MW) generated nothing in any month of 2026.** Its baseline for the same six months is 1.28 million MWh. It ran in December 2025 (84,115 MWh, 16 days under order).
- **Craig 1 (427 MW) ran in one month.** 56,782 MWh in April 2026 (the press had reported a 10-25 April run) and zero in the other five; its baseline is 150,000-220,000 MWh a month.
- **Schahfer 17-18 (722 MW) ran above baseline in January and February, then drew power for four months.** 168,359 and 147,610 MWh against baselines of 159,670 and 132,395, then -4,792, -3,385, -2,550 and -1,898 MWh in March-June: idle units taking station power, which fits the reported repairs.
- **Campbell (1,330 MW) ran at half its usual rate in 2026** (ratio 0.524; CF 30.6% against 58.3%), falling from 586,859 MWh in January to 62,940 in April before 334,717 in June. Over every full order month since June 2025 the ratio is 0.639 (CF 42.9% against 67.1%; Utility Dive had reported 46% against about 66% for June 2025-March 2026).
- **Culley 2 (90 MW) ran at half its usual rate** (ratio 0.521) and drew power in June.
- **Eddystone 3-4 (760 MW) generated 18,651 MWh in June-July 2025 and nothing from August to December 2025**, against a baseline of 26,575 MWh for those seven months (CF 0.5% against 0.7%): units that barely ran before the orders and barely ran under them.
- **Wagner 4 (397 MW) is a different case.** Its orders lift a run-hour limit rather than hold off a retirement, and its baseline is near zero (281 MWh for June), so its ratio (29.3) means little. Not pre-registered: in January-May 2026, when no order was in force, it generated 80,277 MWh against 6,738 MWh in the same months of 2021-2024, and 88,510 MWh over January-June against 7,019 MWh.
- **Stanton 1 (453 MW), not included:** in June 2026 (27 of 30 days under order) it generated 171,122 MWh against a baseline of 143,565, so the pre-registered G5 (below 0.50 from July) may well miss when July-September data arrive.

## Checks (both passed)

| check | rule | result |
|---|---|---|
| C1 | data reach at least March 2026; every covered generator has a 2021-2024 value | data to June 2026; no generator without a baseline |
| C2 | at least six of the eight plants have an included 2026 month | six: Campbell, Centralia, Craig, Culley, Schahfer, Wagner |

## Predictions (4 of 4 scorable held; G5 waits)

| | prediction | result | |
|---|---|---|---|
| G1 | combined 2026 ratio below 0.50 | 0.327 | **held** |
| G2 | Centralia 2 at zero or less in every reported 2026 month, at least three months | 0 in all six months | **held** |
| G3 | Campbell's ratio over every full order month since June 2025 between 0.55 and 0.85 | 0.639 | **held** |
| G4 | at least five plants with a 2026 ratio below 0.75 | five: Campbell 0.524, Centralia 0.000, Craig 0.053, Culley 0.521, Schahfer 0.355 (Wagner 29.3) | **held** |
| G5 | Stanton 1's ratio over its full 2026 order months below 0.50 | no full order month in the data yet | not scorable |

**X1, compared and not scored:** the five plants Utility Dive reported on (Campbell, Centralia, Craig, Culley, Schahfer) generated 1,470,565 MWh in the first quarter of 2026 from their covered units, against 4,483,857 MWh in the first quarter of 2025. Utility Dive gave 1.5 million and 4.3 million MWh. The 2026 figure matches; the 2025 figure is 4% higher here, which could be a whole-plant against covered-unit difference or a revision.

## Stated in advance for the next data

Written 2026-10-19, before PUDL carries any EIA-923 month after June 2026. Scored with `gen_202c.py` 0.1.0 unchanged, as job `gen-202c-v2` or later, once the table reaches September 2026.

- **GN1.** Centralia 2's net generation is zero or less in every month from July to September 2026. Basis: six months of zero so far.
- **GN2.** The combined 2026 ratio over all included months through September 2026 stays below 0.50. Basis: 0.327 through June, and the summer months of 2021-2024 are the baseline's largest.
- G5 is scored as written.

## Limits

- The 2026 values are EIA's monthly year-to-date figures (`incremental_ytd`), which EIA revises; the 2025 values are final.
- The baseline is what the same units did in 2021-2024, not what they would have done in 2026 without an order. A unit heading for retirement might have run little anyway; a ratio below one does not by itself show that the order changed its output. The orders require availability, not generation.
- Eddystone's units have no 2026 values in the table; a missing month is never read as zero.
- Summer MW comes from EIA-860M via the order-dates run; capacity factors use it.
- Wagner's baseline is close to zero, so its ratio is not meaningful; its MWh are reported as they are.

## Files

- [`gen-202c-preregistration.md`](gen-202c-preregistration.md): checks and predictions, published before the run.
- [`gen-202c-output.md`](gen-202c-output.md): the job's raw output, with the month-by-month table, the checks as the code printed them and the diagnostics (data maturity by month, the months each covered generator has).
- [`../data/gen_202c_months.csv`](../data/gen_202c_months.csv): one row per plant-month from the first order on: days under order, whether the month is full, net MWh, baseline MWh, number of baseline years, the same month of 2025, and whether the month is included.
- [`../gen_202c.py`](../gen_202c.py) 0.1.0 and [`../test_gen_202c.py`](../test_gen_202c.py).

```
pip install pandas pyarrow
python -m unittest -v test_gen_202c
python gen_202c.py --data-dir DATA --out-dir out
```

`DATA` holds PUDL's `core_eia923__monthly_generation.parquet`.
