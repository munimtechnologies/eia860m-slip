# How much did the plants under DOE 202(c) orders generate? Checks and predictions, stated before the run

Status: pre-registration, published 19 October 2026 before the job `gen-202c-v1` runs. Nothing below has been scored. MV2 of Munim, Inc.; the code and this note were made with AI agents working in my name.

## Question

DOE's plant orders under section 202(c) of the Federal Power Act keep eight plants' units available to run (the thirteenth result, [`docs/doe-202c-orders.md`](doe-202c-orders.md): 4,849.9 MW of summer capacity since 4 June 2026). The orders do not say how much the units must run. How much electricity did the covered units actually generate in the months they were under order, against the same months before any order?

## Data and code

- **Generation:** EIA-923 monthly net generation by generator, from Catalyst Cooperative's PUDL nightly table `core_eia923__monthly_generation` (https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/core_eia923__monthly_generation.parquet). 2026 months are EIA's monthly year-to-date figures; the run reports the last month with data and, where the table carries it, each month's data maturity.
- **Units:** the generators in [`data/doe_202c_plant_mw.csv`](../data/doe_202c_plant_mw.csv) (Campbell 1710/1-3, Centralia 3845/2, Craig 6021/1, Culley 1012/2, Eddystone 3161/3-4, Schahfer 6085/17-18, Stanton 564/1, Wagner 1554/4), with their summer MW.
- **Days under order:** [`data/doe_202c_orders.csv`](../data/doe_202c_orders.csv), through `orders_202c.plant_dates` (start and expiry both counted).
- **Code:** [`gen_202c.py`](../gen_202c.py) 0.1.0 and [`test_gen_202c.py`](../test_gen_202c.py) (standard-library tests on hand-built tables and on the two real CSVs; reading the parquet needs pandas and pyarrow). The job runs the tests, then `python gen_202c.py --data-dir /data --out-dir /out`.

## Definitions (fixed now)

- **Plant-month:** the sum of the covered generators' net generation (MWh) in a calendar month. It is *missing* if any covered generator has no value that month; a missing month is never read as zero.
- **Full order month:** every day of the month has an order for the plant in force.
- **Baseline:** for each plant-month, the mean of the same calendar month over 2021, 2022, 2023 and 2024 (years with the plant-month reported; at least two needed).
- **Included month:** a full order month, reported, with a baseline.
- **Ratio:** a plant's net generation over the sum of its baselines, both over its included months. **CF:** net generation over summer MW x hours of the included months.
- **2026 window:** included months from January 2026 to the last month with data. **All window:** included months from the plant's first order on (only Campbell, Eddystone and Wagner have 2025 months).
- **Combined 2026 ratio:** all plants' included 2026 months pooled.

## Checks (both must pass for the result to be scored)

- **C1.** The data reach at least March 2026, and every covered generator has at least one value in 2021-2024 (so the units matched the table).
- **C2.** At least six of the eight plants have at least one included 2026 month.

If a check fails, the raw output is published with a dated amendment, the cause is diagnosed, and any changed check is pre-registered again before a re-run. A failed run is never relabelled as scored.

## Predictions (scored by their letter on the first run that passes C1 and C2)

- **G1.** The combined 2026 ratio is below 0.50: the eight plants together generated less than half of what the same units did in the same months of 2021-2024.
- **G2.** Centralia 2 has net generation of zero or less in every reported 2026 month, with at least three months reported.
- **G3.** Campbell's ratio over the all window (every full order month since June 2025) is between 0.55 and 0.85.
- **G4.** At least five plants have a 2026 ratio below 0.75.
- **G5.** Stanton 1's 2026 ratio (full order months from July 2026) is below 0.50. Not scorable if no Stanton month is included.

**Compared, not scored (X1):** Utility Dive reported on 23 June 2026, from EIA data, that five of the plants (by elimination Campbell, Centralia, Craig, Culley and Schahfer) produced 1.5 million MWh in the first quarter of 2026, against 4.3 million MWh in the first quarter of 2025. The run prints the same five plants' first-quarter totals from the covered units. Utility Dive's exact definition (whole plant or covered units) is not stated, so the comparison is reported, not scored.

## What we knew before writing this

We have not read any EIA-923 2026 values for these units. We had read the press: Utility Dive ([23 June 2026](https://www.utilitydive.com/news/doe-202c-power-plants-centralia-campbell-schahfer/822062/)) gave Campbell a 46% capacity factor from June 2025 to March 2026 against nearly 66% in the same periods of the four prior years, quoted TransAlta that Centralia had produced no electricity since 1 January, reported that Craig 1 ran only from 10 to 25 April, put Culley 2 at 14% (prior four years nearly 22%) and Schahfer 17-18 at 17% (24%) in the first quarter, and said Schahfer's units were offline for repairs expected to end in the third quarter. G2, G3 and G4 lean on those figures; G1 and G5 extend them to months and plants the article did not cover.

## Prior art

Utility Dive's article covers the first quarter of 2026 (and Campbell from June 2025 to March 2026) in prose. Synapse and the Sierra Club have estimated the orders' costs; CMS Energy reports Campbell's net cost. On 19 October 2026 we found no open, month-by-month table of the covered units' net generation under order against a fixed pre-order baseline, for all eight plants and through the latest EIA-923 month. If you know of one, open an issue.

## Limits

EIA-923 2026 values are year-to-date figures that EIA revises. Generator-level net generation is reported only by plants in EIA's monthly sample; a plant outside it will show as missing, not zero. Net generation can be negative when a unit is idle and draws station power. The 2021-2024 baseline is the units' pre-order output, not what they would have done in 2026 without an order (a plant near retirement may have run less anyway), so a ratio below one does not by itself show that the order changed anything. The orders require availability, not output.

Data: CC BY 4.0. Code: Apache-2.0.
