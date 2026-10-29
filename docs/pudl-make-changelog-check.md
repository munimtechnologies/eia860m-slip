# PUDL's own make_changelog drops a value that comes back

Status: reproduction, no prediction tested. Run 29 October 2026 (job pudl-changelog-v1). MV2 of Munim, Inc. (made with AI agents). CC BY 4.0; the code in tools/pudl-check/ is Apache-2.0.

Earlier results here ([changelog-revert.md](changelog-revert.md), [history-revert.md](history-revert.md)) traced stale values in PUDL's `core_eia860m__changelog_generators` to one step in `pudl.helpers.make_changelog`: a `drop_duplicates` over every column except `report_date`, which compares a record with every earlier record of the same generator, not only with the one before it. Those results simulated that step. This check runs PUDL's own function instead.

## What was run

- `tools/pudl-check/check_changelog.py` 0.1.0 downloaded `src/pudl/helpers.py` from PUDL at commit af08a70361fb09e0bf3b509778317b7c8873b69f (main, 19 October 2026; still the latest commit touching that file on 29 October 2026). The file had 126,001 bytes and md5 2810fbaba0ea8e87ec560342b3f69f79.
- It took the `make_changelog` function out of that file with Python's `ast` module and ran it unchanged, with only pandas imported. PUDL itself was not installed, and PUDL's code (MIT) is not stored in this repository.
- Each case is one generator over January, February and March 2026, with idx `["plant_id_eia", "generator_id", "report_date"]` and one value column, `operational_status_code`.
- Container python:3.12 (Python 3.12.15, pandas 3.1.0), 29 October 2026 16:19 to 16:22 UTC. The 7 unit tests of the tool passed first. The job's md5 log: check_changelog.py 968c1975331aa73b6f803834e483b4a6, test_check_changelog.py 2de4ccc7c646aeb6827f745136d72e3c.

## Result

| statuses in (Jan, Feb, Mar) | months kept | a consecutive-only rule keeps |
|---|---|---|
| OP, OA, OP | Jan, Feb | Jan, Feb, Mar |
| OP, OA, SB | Jan, Feb, Mar | Jan, Feb, Mar |
| OP, OP, OA | Jan, Mar | Jan, Mar |

When the status comes back to OP in March, PUDL's function drops the March record. Its output ends with the February record (OA), valid until 2026-03-01, and no record covers March. When the value moves on to a new status (SB), or simply repeats, the function keeps what a rule comparing each record only with the one before it keeps.

## Limits

- Three hand-made frames, not PUDL's data. How often this happens in the real table is in [history-revert.md](history-revert.md); those counts were made with AI agents and no person has checked them by hand.
- Only the narrow form of the function was tested: one value column, one record per generator per month. The tall forensics tables, where many records share an entity and a report date, were not tested.
- The function ran outside a PUDL install, under pandas 3.1.0. A full PUDL environment could pin a different pandas, but the step in question is plain `sort_values` and `drop_duplicates`.
