# EIA boilers left out of PUDL's CEMS subplants: plan

Status: pre-registration, nothing run yet. Pre-registration id: subplant-gap-1. Written 30 October 2026, before any of the data below was downloaded or read. MV2 of Munim, Inc. (made with AI agents working in MV2's name; no person has checked this plan by hand). CC BY 4.0; code Apache-2.0.

## The question

PUDL's `core_epa__assn_eia_epacamd_subplant_ids` groups EPA CAMD emissions units and EIA generators into subplants. Open Grid Emissions (OGE) uses it to decide, subplant by subplant, whether EPA CEMS data covers the whole subplant (then CEMS is used) or only part of it (then EIA-923 is used). The table has no `boiler_id`. [Issue #5681](https://github.com/catalyst-cooperative/pudl/issues/5681) (opened 30 September 2026 by grgmiller; labels glue, eia923, community, epacamd_eia; open, unassigned and with no comments on 30 October 2026) shows what that costs at one plant: at Covanta Niagara (plant 50472) only the gas boilers BLR1 and BLR2 report to CEMS, while the waste boilers BLR3 and BLR4, which feed the same generators and burn about 8.2 million MMBtu, are in no crosswalk row. The subplant looks fully covered by CEMS, and OGE's 2023 result was about 205 thousand MMBtu and 12 kt CO2 instead of about 8.38 million MMBtu and 819 kt CO2 in EIA-923.

The issue gives one plant. As far as we could find on 30 October 2026, nobody has counted how many plants and how much fuel share this pattern: not issue #5681, the older [#2710](https://github.com/catalyst-cooperative/pudl/issues/2710) (2023, no description), the OGE harmonization epic [#5439](https://github.com/catalyst-cooperative/pudl/issues/5439), or pull request [#5543](https://github.com/catalyst-cooperative/pudl/pull/5543) (merged 1 October 2026, which overhauled subplant ids and does not mention `boiler_id`). This plan counts it across every year PUDL's nightly tables allow.

## The rule

`tools/subplant-gap/subplant_gap.py` 0.1.0 reads four nightly PUDL tables: `core_epa__assn_eia_epacamd` (the EPA-EIA crosswalk, by `report_year`), `core_epa__assn_eia_epacamd_subplant_ids`, `core_eia860__assn_boiler_generator` and `core_eia923__monthly_boiler_fuel`. For each year Y:

1. A **CEMS subplant** is a subplant holding at least one EPA unit that has a crosswalk row in year Y.
2. Its **linked boilers** are the EIA boilers that the year-Y boiler-generator associations tie to any generator of that subplant.
3. A boiler's **heat input** is the sum over year Y of `fuel_consumed_units` times `fuel_mmbtu_per_unit` in EIA-923 boiler fuel (a blank counts as 0). Its **main fuel** is the `energy_source_code` with the most heat input.
4. A **gap boiler** is a linked boiler with heat input above 0 that has no year-Y crosswalk row with an EPA unit at the same plant and boiler.
5. A subplant is **ambiguous** when a year-Y crosswalk row ties one of its generators to an EPA unit with a blank `boiler_id`: there the crosswalk does not say which boiler the EPA unit is. The scored counts leave ambiguous subplants out ("strict"); the same counts with them are reported with no bar.
6. A subplant's **gap share** is its gap boilers' heat input divided by the heat input of all its linked boilers.

The **main year** is 2024. If the crosswalk, the associations or 12 months of boiler fuel are missing for 2024, the main year is the latest year that has all three, and the result page says so.

## Bars

- **Gate G0:** all four tables load with the columns named above, and 2023 and the main year both qualify.
- **Gate G1:** the rule finds issue #5681's case: in 2023, at plant 50472, BLR3 and BLR4 are gap boilers, BLR1 and BLR2 are matched, and the plant's gap heat input is between 7.0 and 9.5 million MMBtu. If G1 fails, P1-P4 are reported but not scored.
- **P1 (75%):** in the main year, at least 20 plants have a gap boiler (strict).
- **P2 (70%):** in the main year, gap boilers burn at least 25 million MMBtu in total (strict; each boiler counted once).
- **P3 (60%):** in the main year, at least 10 strict CEMS subplants have a gap share above 50%: CEMS sees less than half of their boiler fuel, and the subplant table cannot show it.
- **P4 (70%):** among P3's subplants, at least 3 have a largest gap boiler whose main fuel is not municipal solid waste (MSW, MSB or MSN): the pattern is not only a waste-plant one.

Also reported, with no bar: every qualifying year; the counts with ambiguous subplants included; the number of ambiguous subplants; gap heat input by main fuel; how many gap boilers are matched to an EPA unit in another year of the crosswalk (a match that comes and goes, not a boiler that never reports to CEMS); how many gap plants also have an EPA unit with no EIA generator in the subplant table (perhaps an unmatched CEMS unit rather than a boiler outside CEMS); and a per-boiler and per-subplant CSV for the main year.

## What runs

Job subplant-gap-v1 (Python 3.12 container, pandas and pyarrow) first runs the unit tests in `tools/subplant-gap/test_subplant_gap.py` (hand-made frames, including issue #5681's pattern, an ambiguous subplant, a boiler that burned nothing and a match from another year), then waits until this page is live, then downloads the four nightly tables (about 7 MB in all) and records their sizes, Last-Modified dates and ETags.

## What the result is for

If G0 and G1 hold, the counts go into a dated result page here, whatever P1-P4 show. They size the problem issue #5681 describes from one plant; they do not choose a fix. MV2 would offer them on issue #5681 only after his open offer on issue #5514 is settled, one outside contribution at a time.

## Limits

- A gap boiler is not proof of missing emissions: some boilers are outside CEMS by law (size, fuel, program), and the question is only whether the subplant table can show that CEMS covers part of a subplant. Some gap boilers may report to CEMS under a unit the crosswalk failed to match; the unmatched-unit count above hints at how many.
- EIA-923 boiler fuel covers the boilers EIA asks about; heat input from generators without boilers (for example most combustion turbines) is outside this count. No CO2 is estimated.
- Nightly tables change; the job records which build it read.
- PUDL's data (CC BY 4.0) is downloaded at run time and not stored here.
- Made with AI agents; no person has checked the code or the results by hand.
