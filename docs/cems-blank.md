# What is behind the 2-hour minimum down times left by the #5514 fill patch: result

Status: result of pre-registration cems-blank-1 ([plan](cems-blank-plan.md), committed 31 October 2026 at 17:25 UTC as 583c49c, before the job read any data). Both gates held and 3 of 6 predictions held; P1, P3 and P4 failed. MV2 of Munim, Inc., 1 November 2026 (made with AI agents working in MV2's name; no person has checked these results by hand). CC BY 4.0; code Apache-2.0.

## What ran

Job cems-blank-v1 ran on 1 November 2026 from 07:20 to 07:28 UTC. It found the plan live at its first poll (07:21:57 UTC), downloaded the committed `tools/cems-blank` files, checked that all 5 pinned `tools/cems-mindown` files had the md5s cems-mindown-v3 checked, and passed its own 14 unit tests. It then ran PUDL's `operational_characteristics.py` at 4d3366b on the nightly `core_epacems__hourly_emissions` rows for Colorado, Indiana and Wisconsin (2023-2025, report year 2025), once with no patch and once with the fill patch, and built the table of down runs from the hourly frame PUDL's down-time call receives. The nightly hourly file it read had Last-Modified Sat, 31 Oct 2026 08:10:56 GMT. Tool: `blank_check.py` 0.1.0, Python 3.14.10, polars 2.1.0. Peak memory was 1.88 GB.

## Scores

| Bar | Result | Counts |
|---|---|---|
| Gate B0 | held | shortest down run = PUDL's `min_down_time_hours` for 305 of 305 units in both runs; 810 one-hour sandwiched runs, and `fill_isolated.py` counts 810 isolated null hours |
| Gate B1 | held | 305 of 305 of cems-mindown-v3's units found with the same `min_down_time_hours`, with no patch and with the fill patch |
| P0 (85%) | held | 810 of 810 one-hour sandwiched runs report no operating time and no heat input (100%) |
| P1 (55%) | failed | 33 of the 178 units at exactly 2 hours (18.5%) have an up-flanked 2-hour down run; the bar was at least half |
| P2 (75%) | held | 1,496 of 1,496 hours in those units' 748 two-hour runs report no operating time (100%) |
| P3 (55%) | failed | units at 2 hours or less: 178, and still 178 after setting aside strictly flanked runs of 1 or 2 hours (no fall; the bar was a fall of at least 40%) |
| P4 (65%) | failed | 0 of 3,843,401 down-run hours report operating time above 0 (0%); the band was 1% to 10% |
| P5 (65%) | held | 0 of the 259 units with a minimum down time have an hour with operating time above 0 in a shortest down run |

The 810 isolated hours equal the plan's 404 in Colorado, 260 in Indiana and 146 in Wisconsin. With no patch there are 46,952 down runs covering 3,844,211 hours; with the fill patch, 46,142 runs covering 3,843,401 hours, exactly 810 fewer of each.

## What the counts show

- **Almost no 2-hour run sits between two full stable hours.** None of the 748 two-hour runs is strictly flanked. Only 71 of the 748 (9.5%) have an hour at or above the unit's minimum stable bin on both sides. Setting aside the up-flanked runs instead of the strictly flanked ones (the looser rule, reported with no bar) moves only 3 units: units at 2 hours or less go from 178 to 175 (a 1.7% fall).
- **The flanking hours are rarely full hours.** In the job's `two_hour_runs_fill.csv`, the hour before a 2-hour run reports a full operating hour (at least 0.999) in 9 of 748 runs and the hour after in 15 of 748 (counted from the CSV, which is not committed here). The plan's limit applies: an hour counts as full only at 0.999 or more, and a null `operating_time_hours` counts as not full; how many flanking hours are partial rather than null is not counted here.
- **The single blank hours the fill patch fills look much the same.** With no patch, 105 of the 810 one-hour sandwiched runs (13.0%) are up-flanked and 5 (0.6%) are strictly flanked. So by this CEMS-only shape test, the 1-hour runs and the 2-hour runs are alike: mostly bracketed by hours below the minimum stable bin that are not full operating hours.
- **No down-run hour reports operating time or heat input.** In both runs, 0 down-run hours have `operating_time_hours` above 0 and 0 have `heat_content_mmbtu` above 0. The issue's ~1.07 million null-load rows a year with positive heat input or NOx (2024, all states) do not show up in the frame this calculation receives for these three states.
- Distribution of minimum down times, fill patch: 178 at 2 hours, 38 at 3, 36 at 4-9, 7 at 10 or more (259 units; median 2). After setting aside up-flanked short runs: 175, 40, 37 and 7. With no patch: 199 at 1 hour, 25 at 2, 11 at 3, 18 at 4-9, 6 at 10 or more (median 1).
- 744 of the 748 two-hour runs are sandwiched; the other 4 touch the edge of a unit's hours (for example, a run in the last two hours of 2025).

## Why the failed bars failed

- **P1 and P3:** the 2-hour pile is not the shape the plan described for a blank report (stable load on both sides with full operating hours). Very few flanking hours are full operating hours, so the strict rule sets almost nothing aside; the looser up-flank rule sets aside 3 units. The plan said ahead of time that units reporting operating time in coarser steps might never count as strictly flanked; the up-flank count shows this is not the whole cause.
- **P4:** the band was set from the issue's national figure, which counts null-load rows with positive heat input *or NOx* across all units. In this frame no null-load hour has operating time or heat input above 0. A likely cause, not counted here: PUDL keeps only units with more than one distinct load factor before the down-time call, so units that report fuel use with no gross load at all never reach it. The tool also did not look at NOx.

## What this means for issue #5514

The plan said: if P1 and P3 both fail, the 2-hour values mostly look like real short stops, which is evidence for the one-hour fill as it stands rather than a fill of two hours. Both failed, so that is the pre-registered reading. One caveat the plan did not foresee: by the same test, the single blank hours that the one-hour fill removes look much like the 2-hour runs (13.0% up-flanked against 9.5%; strict flanks 0.6% against 0%). So the CEMS shape does not single out the 1-hour runs as blank reports either. The case for filling them rests on the issue's own argument (it calls a 1-hour minimum down time physically implausible for its steam coal example, and reports that every sandwiched blank hour in 2024 has zero operating time and null emissions), not on this test. Every down-run hour here reports no operating time, which fits a unit that was off; nothing here shows whether it really was. MV2 will share these counts on issue #5514 together with the fill result. The choice of fix is PUDL's.

## Limits

- Three states and one report year; not a full PUDL build.
- A run's shape is read from CEMS alone. Nothing here was checked against an outside source, and no unit is said to have been really on or off.
- Fuel type and prime mover were not counted; combustion turbines can stop and restart within two hours.
- The newest polars and pandas below 3, not PUDL's locked environment; Gate B1 shows the run repeats cems-mindown-v3 exactly.
- PUDL's code (MIT) and data (CC BY 4.0) are downloaded at run time and not stored here. The job's per-unit and per-run CSVs are not committed.
- Made with AI agents working in MV2's name; no person has checked these results by hand.
