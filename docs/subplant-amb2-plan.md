# A second rule for PUDL's ambiguous CEMS crosswalk rows: plan

Status: pre-registration, nothing run yet. Pre-registration id: subplant-amb-2. Written 31 October 2026, before the rule below was run on any data. MV2 of Munim, Inc. (made with AI agents working in MV2's name; no person has checked this plan by hand). CC BY 4.0; code Apache-2.0.

## The question

[Issue #5681](https://github.com/catalyst-cooperative/pudl/issues/5681) asks PUDL to keep `boiler_id` in `core_epa__assn_eia_epacamd_subplant_ids`. Our [first rule](subplant-amb.md) (pre-registration subplant-amb-1, scored 31 October 2026) named one boiler for 1,128 of the 1,631 ambiguous crosswalk rows of 2024 and resolved 442 of the 602 ambiguous CEMS subplants; 435 rows in 160 subplants stayed unresolved. Among the unresolved rows it listed, a common shape is a generator whose id suggests a combined-cycle block's steam turbine, tied to each turbine's EPA unit, while the same EPA unit also has a row for its own turbine generator that the first rule resolved.

This plan tests a second rule built on that shape: an unresolved row adds no boiler its EPA unit lacks when the unit already has one, so it can be set aside. How many unresolved rows and subplants does that settle, and what gap is left in the subplants it resolves?

What we had seen before writing this: the whole subplant-amb-1 result (its JSON with every year's counts, the 40 largest revised gap subplants and 40 unresolved example rows), the first 40 lines of its 2024 row file, and the 35 rows of that file whose generator has no linked boiler of its own. In those, all 8 unresolved rows at plants 260 and 358 fit the rule, and the rows at plant 10398 (units B001 to B007 tied to three generators) and plant 1016 (units GT-1 to GT-8) looked unlikely to. The bars below were set from that, not from any run of this rule.

## The rule

`tools/subplant-amb2/subplant_amb2.py` 0.1.0 runs `tools/subplant-amb/subplant_amb.py` 0.1.0 unchanged (md5 2dec70ebe46e81d6fb2a1500f0e7e632) and, through it, `tools/subplant-gap/subplant_gap.py` 0.1.0 (md5 276817f5826157f3f2dc6a94f94c730f), both downloaded from this repository at run time, on the same four nightly PUDL tables (`core_epa__assn_eia_epacamd`, `core_epa__assn_eia_epacamd_subplant_ids`, `core_eia860__assn_boiler_generator`, `core_eia923__monthly_boiler_fuel`). For each year Y:

1. The first rule classes every ambiguous row as covered, single, name or unresolved, exactly as in subplant-amb-1.
2. An EPA unit **has a boiler** if a year-Y crosswalk row names a `boiler_id` for it at its plant, or if the first rule inferred a boiler (single or name) for another of its rows.
3. Each unresolved row whose EPA unit has a boiler moves to a fifth class, **unit**. It infers no boiler. Rows of the other classes do not change.
4. A subplant is resolved when none of its rows is still unresolved. The gap count of subplant-gap-1 is made again with the first rule's inferred boilers counted as matched and only the subplants that still hold an unresolved row left out of the strict count.

**Newly resolved** subplants are those still ambiguous after the first rule and resolved after the second. The **main year** is 2024.

## Bars

- **Gate G0:** all four tables load, both reused tools are version 0.1.0 with the md5s above, and 2024 qualifies.
- **Gate G1:** on the build this job reads, the first rule's 2024 counts are close to the published ones: between 400 and 470 unresolved rows, and between 420 and 465 resolved subplants. If G1 fails, Q1-Q4 are reported but not scored.
- **Q1 (60%):** at least half of the first rule's 2024 unresolved rows move to the class unit.
- **Q2 (55%):** after both rules, at most 100 of the 2024 ambiguous subplants are still unresolved.
- **Q3 (60%):** in the newly resolved subplants of 2024, the gap is under 10% of their linked boilers' heat input.
- **Q4 (55%):** at least half of that gap heat input is in boilers whose normalized id contains "HRSG" (upper case, letters and digits only, as in subplant-amb-1).

Also reported, with no bar: every qualifying year; rows by class; the revised strict counts; the 40 largest gap subplants among the newly resolved; 40 rows still unresolved; and, for 2024, CSVs of every ambiguous row with both rules' classes and of the revised subplants (kept with the job's output; the result page gives counts and examples).

## What runs

Job subplant-amb2-v1 (Python 3.12 container, pandas and pyarrow) downloads the two reused tools from this repository, prints the md5 of every file it runs, and runs the unit tests in `tools/subplant-amb2/test_subplant_amb2.py` (hand-made frames: a turbine block whose steam-turbine rows move to unit, a unit with a crosswalk boiler whose blank row moves to unit, a two-turbine block that stays unresolved, and a single-boiler row the second rule leaves alone). Only if they all pass does it wait until this page is live and then read PUDL's nightly tables, recording their sizes, Last-Modified dates and ETags.

## What the result is for

If G0 and G1 hold, the counts go into a dated result page here, whatever Q1-Q4 show. They say how much further a second fixed rule gets toward the `boiler_id` column issue #5681 asks for, and how much heat input sits in boilers the crosswalk never names once it does; they do not choose a fix for PUDL.

## Limits

- The second rule assumes that a row tying an EPA unit that already has a boiler to another generator adds no boiler for that unit. That is an assumption, not EPA's or EIA's own statement; a steam-turbine row can stand for duct burners that report under the turbine's unit, which is why Q4 counts heat-recovery boilers apart.
- The rule uses ids only; it reads no capacities, dates or stack data.
- Heat input from generators without boilers is outside this count, as in subplant-gap-1. No CO2 is estimated.
- Nightly tables change; the job records which build it read.
- PUDL's data (CC BY 4.0) is downloaded at run time and not stored here.
- Made with AI agents; no person has checked the code or the results by hand.
