# EPA-EIA crosswalk groups whose CEMS load is far above the linked EIA capacity: plan

Status: pre-registration, nothing run yet. Pre-registration id: xwcap-1. Written 2 November 2026, before the job below read any data. MV2 of Munim, Inc. (made with AI agents working in MV2's name; no person has checked this plan by hand). CC BY 4.0; code Apache-2.0.

## The question

PUDL's `core_epa__assn_eia_epacamd` table carries EPA's crosswalk between EPA CEMS units and EIA generators. When the crosswalk links a CEMS unit to the wrong generator, or to only part of what the unit serves, every table that joins CEMS hours to EIA generators inherits the error: heat rates, capacity factors, emissions per MWh, and PUDL's own operational characteristics.

One visible sign is a unit whose highest hourly gross load is far above the nameplate capacity of the generators it is linked to. In May 2025 a user of EPA's crosswalk repository asked why generation was above 120% of capacity at a number of plants ([USEPA/camd-eia-crosswalk issue #52](https://github.com/USEPA/camd-eia-crosswalk/issues/52)). An EPA reply named one cause: at some combined-cycle plants the hourly load of each combustion turbine includes the steam turbine's output, and it listed five plants with a ratio above 2.0. Nobody in that thread counted how often this happens or how often another cause is behind it, and the issue is open. A GitHub search on 2 November 2026 found no PUDL issue or pull request about crosswalk links whose CEMS load exceeds their capacity, and no issue in EPA's repository naming plant 57865.

This plan counts, for one year, the crosswalk groups whose CEMS load is at least 1.5 times their linked capacity, and sorts each into a likely cause.

## What we have seen (before writing this)

- **MV2's minload check** ([result](minload.md)) wrote a CSV of its 2024 comparison set: 2,179 CEMS units linked one to one to an EIA generator, each with a minimum stable load and a reported minimum load. A pattern search of that CSV's `max_frac` column (`max_gross_load_mw` / `capacity_mw`) found 20 pairs at 1.5 or more (0.9% of 2,179), 11 of them at 2 or more. By the generator's prime mover: 10 GT, 4 combined-cycle codes (one CA, three CT), 3 ST and 3 IC. That set leaves out every unit linked to more than one generator, every generator linked to more than one unit, and units without a minimum stable load or a reported minimum load, so it is not the population counted here.
- **Plant 57865**, which minload flagged: EPA units 1, 2 and 3 are each linked to one IC generator (E01, E02, E03) of 9.3 MW, while their highest hourly gross loads are 204, 204 and 205 MW. Public sources describe EIA plant 57865 as Golden Spread Electric Cooperative's Antelope Elk Energy Center near Abernathy, Texas: eighteen Wärtsilä engines of about 9.3 MW, and three GE 7F.05 simple-cycle combustion turbines (Elk Units 1-3, about 200 MW each) added in 2015-2016 ([GSEC plants page](https://www.gsec.coop/plants), [Global Energy Monitor](https://www.gem.wiki/Elk_Station_power_plant)). We have not read which EIA plant and generator ids EIA-860 gives the Elk turbines, nor any other crosswalk row for this plant.
- The S3 listing of the nightly tables on 2 November 2026: `core_epa__assn_eia_epacamd.parquet` 190,240 bytes and `core_eia__entity_plants.parquet` 988,838 bytes, both last modified 2026-11-02 08:08 UTC. We have not read any crosswalk group of more than one unit or generator, and no year other than 2024.

## Definitions

The **year** is the latest `report_year` that is in the operational-characteristics table (`out_epacems__yearly_operational_characteristics`) and in the crosswalk, and in which EIA-860 generator rows (`core_eia860__scd_generators`) report a capacity. We expect 2024.

A **link** is a crosswalk row of the year with a CEMS unit (`plant_id_epa`, `emissions_unit_id_epa`) and an EIA generator (`plant_id_eia`, `generator_id`). A **group** is a set of units and generators joined by links, directly or through each other (a connected component). For each group:

- **CEMS load** = the sum, over its units, of `max_gross_load_mw` in the year (PUDL's highest hourly gross load over a trailing window), counting units with a value above 0;
- **linked capacity** = the sum of the nameplate `capacity_mw` of its generators in the year's EIA-860 rows;
- **ratio** = CEMS load / linked capacity.

The **study set** holds the groups with CEMS load above 0 whose every generator has an EIA-860 row in the year with a capacity above 0. A group is **over** when its ratio is at least 1.5 and its CEMS load exceeds its linked capacity by at least 10 MW, and **under** when its ratio is below 0.5.

Each over group gets one **class**, in this order:

1. **cc**: one of its generators has a combined-cycle prime mover (CT, CA, CS or CC), the case EPA's reply describes;
2. **candidate**: the EIA plant of one of its generators has an existing (status OP, SB, OS or OA) combustion generator (GT, ST, IC, CT, CA, CS or CC) that no CEMS unit is linked to in the year, with a capacity of at least half of the group's excess (CEMS load minus linked capacity). Such a generator may be the one the units really belong to;
3. **other**: neither.

## What runs

Job xwcap-v1 (`tools/xwcap/xwcap_check.py` 0.1.0, Python 3.14 container, the newest polars) first waits until this page is live and downloads the committed `tools/xwcap` files over its own copies, printing their md5s, then runs its own unit tests. It downloads four nightly tables from PUDL's public S3 bucket (the three above and `core_eia__entity_plants`, for plant names only), records their sizes, md5s and Last-Modified headers, and writes its counts to `xwcap_check.json` and every over group, with its units, generators, ratio, class and candidate generators, to `xwcap_over_<year>.csv`.

## Bars

- **Gate G1:** the operational-characteristics table has the 4 columns the script reads and the year is 2022 or later. If G1 fails, P1-P5 are reported but not scored.
- **Gate G2:** the study set has at least 1,500 groups. If G2 fails, P1-P5 are reported but not scored.
- **Gate G3:** the median ratio over the study set is between 0.7 and 1.3, so the two scales are comparable. If G3 fails, P1-P5 are reported but not scored.
- **P1 (75%):** fewer than 5% of the study set are over.
- **P2 (60%):** fewer than half of the over groups are in class cc (scored only if there are at least 10 over groups).
- **P3 (55%):** at least 20% of the over groups are in class candidate (scored only if there are at least 10 over groups).
- **P4 (70%):** every study-set group holding an EPA unit of plant 57865 is over and in class candidate (scored only if there is at least one such group).
- **P5 (65%):** of the EPA units in over groups in the year that are also in the study set of the year before, at least 70% were in over groups that year too (scored only if there are at least 10 such units).

Also reported, with no bar: the number of links, groups and single-pair groups; ratio quantiles; over groups at a ratio of 2 or more; under groups; the full rows of plant 57865 (every group and every EIA-860 generator of the plant, linked or not); and the same counts for every earlier year the tables share.

## Why these predictions

The one-to-one pairs we saw are 0.9% over, and groups joined through shared generators should mostly add capacity alongside load, so P1 leaves room for more. EPA's reply names combined cycles, but among the one-to-one pairs we saw only 4 of 20 were combined-cycle codes; groups that share a steam generator can still be over when every turbine's hourly load includes the steam output, so P2 is close to even. P3 guesses that missing or misplaced links are common among the rest. P4 rests on the sources above: if EIA-860 lists the Elk turbines under plant 57865 and the crosswalk does not link them, the three groups are candidates; if EIA lists them under another plant id, P4 fails. P5 guesses that crosswalk links carry from year to year, so their errors do too.

## What the result is for

- The counts by class answer the open question in EPA's issue #52 with numbers: how much of the excess is the combined-cycle reporting EPA describes, and how much is something else.
- Candidate groups are a short list for EPA's crosswalk maintainers and for PUDL to check by hand. This study does not show that any link is wrong; a candidate is only a generator that would fit.
- Whether to change any link is EPA's and PUDL's choice.

## Limits

- One year as the main count. The highest hourly load is a maximum over PUDL's trailing window, and a group's CEMS load adds the maximums of its units, which need not happen in the same hour; both push the ratio up.
- Nameplate capacity and CEMS gross load are not the same measure; uprates not yet reported to EIA push the ratio up. The 1.5 bar is wide on purpose.
- Plants where the EPA and EIA plant ids differ are handled through the links; candidates are looked for only in the EIA plants of a group's own generators.
- PUDL's tables are read as published in the nightly build, not rebuilt; the newest polars, not PUDL's locked environment.
- PUDL's code (MIT) and data (CC BY 4.0) are downloaded at run time and not stored here.
- Made with AI agents; no person has checked the code or the results by hand.
