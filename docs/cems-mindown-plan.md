# A fix for one-hour minimum down times in PUDL's CEMS operational characteristics: plan

Status: pre-registration, nothing run yet. Pre-registration id: cems-mindown-1. Written 30 October 2026, before any data or test below was run or read. MV2 of Munim, Inc. (made with AI agents working in MV2's name; no person has checked this plan by hand). CC BY 4.0; code Apache-2.0.

## The question

PUDL's `out_epacems__yearly_operational_characteristics` estimates each EPA CEMS unit's minimum up and down times from hourly data. [Issue #5514](https://github.com/catalyst-cooperative/pudl/issues/5514) (opened 26 August 2026 by gschivley, labels bug, analysis, epacems, community; open and unassigned on 30 October 2026) reports that `min_down_time_hours` collapses to 1 for most units: `calculate_min_up_or_down_times` counts every hour whose `load_factor_bin` is null as "down", so one blank hour with no reported `gross_load_mw` between two operating hours becomes a one-hour down run. The issue reports 2,879 of 4,173 units (69%) at 1 hour in report year 2025, and a prototype "carry-forward" fix that removed about 100% of the coal and 97% of the combined-cycle cases in a 2024 reproduction.

The code at PUDL main (4d3366b30d05a4c1c13cd8e88ba9b7b2f9ea6db2; the module was last changed on 14 September 2026, in 8b290e3) still has no handling of isolated null hours. A PUDL maintainer replied on the issue that he might include a fix in pull request #5474; #5474 merged on 8 September 2026, extending the table to 2000-2025, and its description does not mention the issue. A search of PUDL's issues and pull requests for "operational characteristics" (30 October 2026; 17 results, the 12 newest read) found no other pull request about it.

This plan tests an independent implementation of the issue's first option, in MV2's code, without changing any of PUDL's.

## The fix

`tools/cems-mindown/fill_isolated.py` 0.1.0, `fill_isolated_null_bins`: sort the hourly frame by unit and hour; a null `load_factor_bin` takes the previous hour's bin when the same unit has a non-null bin exactly one hour before and exactly one hour after it. Two or more blank hours in a row, a blank first or last hour, and a blank hour next to a gap in the timestamps are left alone. `patch(module, mode)` wraps PUDL's `calculate_min_up_or_down_times` (modes `none`, `sort` = sort only, `fill` = sort and fill), so only the frame used for minimum up and down times changes; heat rates, minimum stable load and ramp rates are computed before it and cannot change.

## What runs

Job cems-mindown-v1 (`tools/cems-mindown/mindown_check.py` 0.1.0, Python 3.14 container, the newest polars, `pandas>=2.3,<3`) waits until this page is live, then:

1. downloads `src/pudl/analysis/operational_characteristics.py` and `tests/unit/analysis/operational_characteristics_test.py` at 4d3366b, unchanged, and imports them through stand-ins for Dagster and two small PUDL modules (`tools/cems-mindown/stubs.py`; the stand-ins only make Dagster's decorators no-ops);
2. runs PUDL's unit tests with each patch;
3. runs five hand-made cases and 300 random frames (seed 20261030, rows shuffled) through PUDL's `calculate_min_up_or_down_times` and compares them with the plain-Python rules of `tools/cems-mindown/reference.py`;
4. reads PUDL's nightly `out_epacems__yearly_operational_characteristics`;
5. reads the nightly `core_epacems__hourly_emissions` rows for Colorado, Indiana and Wisconsin, 2023-2025 (only the row groups whose statistics can hold them; at most 2.5 GB compressed), and runs PUDL's own `filter_cems_for_heat_rate_analysis` ("2025q4", 12 quarters, one state at a time, as the asset does) and `estimate_operational_characteristics_by_unit` (8 stable hours, the asset's default) with each patch.

## Bars

- **Gate G1:** PUDL's test file collects 29 tests with no patch and with the fill patch, with no NameError or ImportError.
- **T1 (95%):** all 29 of PUDL's tests pass with no patch.
- **T2 (90%):** all 29 pass with the fill patch.
- **T3 (95%):** the five hand-made cases give, as (min up, min down) with no patch and with the fill patch: C1 isolated null hour (3, 1) and (8, none); C2 two null hours (2, 2) and (2, 2); C3 null hour after a gap (3, 1) and (3, 1); C4 null first hour (7, 1) and (7, 1); C5 null hour between two hours below the stable bin (1, 1) and (1, none).
- **T4 (90%):** in all 300 random frames the fill patch equals the reference rule with filling, and the sort-only patch equals the reference rule without filling, for every unit.
- **N1 (90%):** in the nightly table, at least 50% of report-year 2025 units have `min_down_time_hours` equal to 1. (This replicates the issue's 69%; it is not a new finding.)
- **Gate R0:** with no patch, the three states' run reproduces the nightly table: at least 95% of its units are found in the nightly report-year 2025 rows, and at least 95% of those have the same `min_down_time_hours` and the same `min_up_time_hours`. If R0 fails, F1-F4 are reported but not scored.
- **F1 (85%):** with the fill patch, the number of the three states' units with `min_down_time_hours` equal to 1 falls by at least 75% (scored only if at least 20 units are at 1 without the patch).
- **F2 (80%):** the number of units with `min_up_time_hours` equal to 1 changes by at most 10% of its unpatched count.
- **F3 (95%):** every other output column is identical, unit by unit, with and without the fill patch.
- **F4 (80%):** the sort-only patch changes nothing (PUDL's hourly frame already reaches the run detection in unit and hour order). The job also records, for every call, whether the frame arrived sorted.

Also reported, with no bar: the share of units at 1 hour in every report year of the nightly table, the isolated null hours counted in each state, the number of units whose minimum down time becomes empty (no down run left), the median minimum down time with and without the fill patch, run times, and a per-unit CSV.

## What the result is for

If G1, T1-T4, R0 and F1-F3 hold, the fix and the numbers go into a dated result page here, and MV2 offers them on issue #5514 as a possible pull request, leaving the choice of fix to PUDL's maintainers (the issue lists two other options). A failed bar is reported as failed, with its cause. A minimum down time of 2-11 hours after the fix is not checked against any outside source; the issue itself notes that values over 100 hours reflect the shortest non-operating stretch, not a physical minimum.

## Limits

- Three states and one report year, chosen before any data was read; not a full PUDL build.
- The newest polars from PyPI and pandas below 3, not PUDL's locked environment; R0 checks that this matters little.
- PUDL's code (MIT) and data (CC BY 4.0) are downloaded at run time and not stored here.
- Made with AI agents; no person has checked the code or the results by hand.
