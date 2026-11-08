# Gap units at plants missing from EIA-860: retired before the report year? (plan)

Status: pre-registration, nothing run yet. Pre-registration id: xwstale-1.

MV2 of Munim, Inc., 8 November 2026; made with AI agents working in MV2's name; no person has checked this plan by hand. CC BY 4.0; code Apache-2.0.

## Why

[xwgap.md](xwgap.md) (pre-registration xwgap-1) sorted the CEMS units that have a peak load, no row in PUDL's EPA-EIA crosswalk (`core_epa__assn_eia_epacamd`) and no unlinked operating combustion generator at their EIA plant. In report year 2024 there are 75. 62 of them are at EIA plants with no generator row at all in PUDL's EIA-860 table that year ("absent"), and 3 more are at a plant with no operating combustion generator ("not_operating"). PUDL's yearly CEMS table (`out_epacems__yearly_operational_characteristics`) gives each report year a three-year trailing window, so a unit at a plant that closed in 2022 or 2023 can still have a 2024 row. If that explains most of the 65, the yearly count of unexplained gaps is mostly retired units, not missing links, and the units that remain are the ones a person should look at.

This check asks, for every absent and not_operating gap unit of every report year: when was its EIA plant last listed in EIA-860, up to that year, and had all of the plant's combustion generators in that listing retired before the year began?

**Prior art.** PUDL's [methodology page](https://docs.catalyst.coop/pudl/en/nightly/methodology/operational_characteristics.html) describes the trailing window but says nothing about units retired inside it. EPA's tracker asks to "Perform manual matches on all remaining unmatched plants and units, including retired units" ([camd-eia-crosswalk#44](https://github.com/USEPA/camd-eia-crosswalk/issues/44)). A search of PUDL's issues for "trailing window retired" and "operational characteristics retired" on 8 November 2026 found no count of retired units in the yearly table.

## What we have seen (before writing this)

- xwgap-1's result and its file `data/xwgap-units-2018-2024.csv`: each gap unit's reason and leads, but no EIA-860 listing year or retirement date for any plant. Absent and not_operating gap units by report year: 18 (2018), 27 (2019), 28 (2020), 28 (2021), 23 (2022), 39 (2023), 65 (2024).
- EIA plant 6019 is W. H. Zimmer, retired in May 2022 ([Wikidata](https://www.wikidata.org/wiki/Q8010688), citing EIA-860M). It is used below as a gate, not a prediction.
- EIA plant 55243 is Astoria Gas Turbines in Queens, New York ([GridInfo](https://www.gridinfo.com/plant/astoria-gas-turbines/55243)); we have not looked up when it retired.
- Frontera (EIA 55098), absent in 2018 to 2022, was operating and selling into Mexico in those years (see [xwpair.md](xwpair.md)), so it is not retired.
- Plants 880079 and 880102 carry EPA-assigned 88 codes and are absent in every year.

## Method

- **Data:** PUDL nightly `core_eia860__scd_generators` (CC BY 4.0), every report year, downloaded at run time from PUDL's public S3 bucket, with md5, byte count, row count and Last-Modified recorded; the population file `data/xwgap-units-2018-2024.csv` read from this repository's main branch, with its md5 recorded. Nothing from PUDL is stored here.
- **Population:** every row of the population file whose reason is absent or not_operating.
- **Definitions:** a combustion generator has prime mover CA, CS, CT, GT, IC or ST. The plant's last listing is the latest EIA-860 report year, up to and including the unit's report year, in which its EIA plant has any generator row. A generator's retirement date is `generator_retirement_date` on its row in that listing or, if that is empty, the latest one on any of its rows up to the report year. Later listings are recorded but not used.
- **Classes:** **never_listed** (no generator row in any year up to the report year); **retired_before** (the last listing has combustion generators and every one has a retirement date before 1 January of the report year); **retired_in_year** (every one has a date, the latest in the report year); **other** (a combustion generator with no date, one retiring after the report year, or no combustion generator; the cause is recorded). For retired_before units, the year of the latest retirement date is recorded.
- Report year 2024 is the one scored, plus P5 on 2019 to 2023. Every unit is written to `xwstale-units.csv` and published with the result.
- Code: `tools/xwstale/xwstale.py` 0.1.0 with its unit tests; job xwstale-v1 waits until this plan is live and runs the committed code.

## Gate (if it fails, nothing is scored)

- **Gate G1:** the EIA-860 table has every column used and report years 2018 to 2024.
- **Gate G2:** the population file has 317 rows, 65 of them absent or not_operating units of 2024.
- **Gate G3:** W. H. Zimmer's unit (EIA 6019, unit 1, 2024) is classed retired_before with its latest retirement in 2022. This is a known case and checks the method, so it is a gate.

## Predictions (probability we give each)

About report year 2024 unless said otherwise; N = 65.

- **P1 (60%):** at least 60% of the 65 units are retired_before.
- **P2 (55%):** at least 90% of the retired_before units had their latest retirement in 2022 or 2023, inside the trailing window. Fails if there are none.
- **P3 (60%):** at most 10 of the 65 units are never_listed.
- **P4 (40%):** all 35 absent units at plants 563, 2866 and 55243 are retired_before, with their latest retirement in 2023.
- **P5 (40%):** in each report year from 2019 to 2023, at least half of that year's absent and not_operating gap units are retired_before.

## What happens with the result

A dated result page is published whatever the scores, with every unit's class. A failed bar is reported as failed, with its cause, and is not re-scored. The result says which 2024 gap units are not explained by retirement; those, with the xwgap-1 list, are offered to PUDL as one comment on our open issue [pudl#5752](https://github.com/catalyst-cooperative/pudl/issues/5752), saying that no person has checked them. Whether retired units belong in the yearly table, or in a match-rate count, is PUDL's decision.

## Limits

- A retirement date in EIA-860 is what the plant reported, not proof the unit stopped burning fuel; CEMS hours inside the window are not checked here.
- A plant can change its EIA plant id; a unit at a renumbered plant would look never_listed or retired here.
- The population is xwgap-1's list from PUDL's 8 November 2026 build; PUDL's tables change nightly, and the run records which EIA-860 build it read.
