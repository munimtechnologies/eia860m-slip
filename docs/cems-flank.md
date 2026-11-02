# What sits on each side of the short down runs behind PUDL's minimum down times: result

Status: result of pre-registration cems-flank-1 ([plan](cems-flank-plan.md), committed 1 November 2026 at 13:34 UTC as 6561eff, before the job read any data). All four gates held and 7 of 8 predictions held; U1 failed. MV2 of Munim, Inc., 2 November 2026 (made with AI agents working in MV2's name; no person has checked these results by hand). CC BY 4.0; code Apache-2.0.

**The short version: this result cuts against MV2's own fill patch for PUDL issue #5514.** The single blank hours the patch fills sit between two partly-operating hours just as often as stops of 10 hours or more do. On this measure they look like real short stops, not missing reports.

## What ran

Job cems-flank-v1 ran on 1 November 2026 from 16:36 to 16:46 UTC. It found the plan live at its first poll (16:38:43 UTC), downloaded the committed `tools/cems-flank` files, checked that all 6 pinned files (`tools/cems-mindown` and `blank_check.py` from 583c49c) had the md5s cems-blank-v1 ran, and passed its own 22 unit tests. It then repeated cems-blank-1's pipeline unchanged by importing `blank_check.py`: PUDL's `operational_characteristics.py` at 4d3366b on the nightly `core_epacems__hourly_emissions` rows for Colorado, Indiana and Wisconsin (2023-2025, report year 2025), once with no patch and once with the fill patch. The nightly hourly file it read had Last-Modified Sun, 01 Nov 2026 08:02:15 GMT. Tool: `flank_check.py` 0.1.0, Python 3.14.10, polars 2.1.0. Peak memory was 1.75 GB.

## Scores

| Bar | Result | Counts |
|---|---|---|
| Gate K1 | held | in both runs the flank table lists the same down runs as `blank_check.py` (46,952 with no patch, 46,142 with the fill patch), with 0 mismatched full flanks |
| Gate K2 | held | 748 two-hour runs at 178 units at exactly 2 hours, the same counts as cems-blank-1 |
| Gate K3 | held | 0 null-load hours with heat input above 0 belong to a unit with `load_factor_nunique` above 1 |
| Gate U0 | held | 249 of the 259 units with a minimum down time (96.1%) get a prime-mover class |
| F1 (70%) | held | 1,468 of 1,492 flanking hours of the 2-hour runs at units at exactly 2 hours (98.4%) are partial |
| F2 (60%) | held | with no patch, 1,575 of 1,620 flanking hours of the 810 one-hour sandwiched runs (97.2%) are partial, 1.2 points from F1's share |
| F3 (65%) | held | with the fill patch, 64,424 of 65,405 flanking hours of the 32,851 down runs of 10 hours or more (98.5%) are partial |
| D1 (60%) | held | 384,478 hours in the binning frame have null `gross_load_mw` and heat input above 0 |
| D2 (75%) | held | 43 units have `load_factor_nunique` of 1 or less and heat input above 0 |
| U1 (50%) | failed | CT-based share: 132 of 172 matched units at exactly 2 hours (76.7%) against 54 of 77 at 3 hours or more (70.1%), 6.6 points apart; the bar was 10 |
| U2 (60%) | held | 40 of 63 ST units (63.5%) sit at exactly 2 hours |
| U3 (55%) | held | 81 of 112 slow-start units (72.3%) have a minimum down time of 2 hours or less |

A flanking hour is partial when its `operating_time_hours` is above 0 and below 0.999. No flanking hour in any group was null or 0.

## What the counts show

- **Every kind of down run starts and ends in a partly-operating hour.** The partial share is 97.2% for the one-hour sandwiched runs (no patch), 98.4% for the 2-hour runs at units at 2 hours, 98.8% for runs of 3 to 9 hours (24,773 of 25,073 flanking hours, 12,543 runs) and 98.5% for runs of 10 hours or more. Full operating hours on a side are rare in every group: 45 of 1,620 (2.8%) for the one-hour runs, 24 of 1,492 (1.6%) for the 2-hour runs and 981 of 65,405 (1.5%) for the long runs. That is the shape of a unit that stops partway through one clock hour and restarts partway through a later one. A unit that kept running while one hour's report went missing would more likely show full hours on both sides.
- **So the flanking hours separate nothing.** cems-blank-1 asked whether a flanking hour was full and found almost none were; this count shows why: the hours next to long stops are not full either. Its full-hour rule was the wrong test, as the plan said it would be if F1 and F3 held.
- **By prime mover, the 2-hour runs look the same:** partial shares of 97.9% (758 of 774 flanking hours) for GT units, 99.0% (481 of 486) for combined-cycle units and 98.6% (211 of 214) for ST units.
- **Short minimum down times are not mainly a combustion-turbine thing.** With the fill patch, 89 of 135 GT units, 43 of 51 combined-cycle units and 40 of 63 ST units sit at exactly 2 hours (median 2 hours in every class); 10 units are unmatched. By EIA-860 cold-start code, 91 of 137 fast-start units and 81 of 112 slow-start units sit at 2 hours. In EIA-860's 2024 generator rows (all U.S. generators) the cold-start codes are 10M 9,041, 1H 6,643, 12H 3,947, OVER 1,646 and none 13,637.
- **The null-load hours with heat input belong to units the calculation drops.** All 384,478 such hours in the binning frame belong to units with at most one distinct load factor (46 of 305 units; 43 of them with heat input). Those units' whole heat input, 118.1 million MMBtu (2.5% of the frame's 4,651.9 million), falls in null-load hours: they report fuel use but no gross load in 2023-2025. PUDL drops them before the down-time step, so they do not bias `min_down_time_hours`; the table simply has no value for them. This answers the cause cems-blank-1 named but did not count.

## Why U1 failed

U1 expected the units at exactly 2 hours to be more often combustion-turbine based than the units at 3 hours or more. They are, but only by 6.6 points (76.7% against 70.1%), short of the 10-point bar. Combustion-turbine units dominate both groups because they make up most of the units with a minimum down time (186 of 249 matched). Relative to their number, ST units sit at 2 hours about as often (40 of 63) as simple-cycle GT units (89 of 135).

## What this means for issue #5514

The plan said, before the data was read: if F2 holds, the single blank hours the fill patch removes are mostly bracketed by partial hours too, which is what a real stop of one to three hours looks like, so it would be evidence against treating them as blank reports, and MV2 will say so plainly on issue #5514 because it cuts against his own patch. F2 held (97.2%, against 98.5% for stops of 10 hours or more). That is the pre-registered reading.

Together with cems-blank-1 (every one of these hours reports zero operating time and no heat input), CEMS describes these hours as a unit that was off: it stopped during the hour before and restarted during the hour after. PUDL's `min_down_time_hours` counts only whole null-load hours, so a value of 1 hour stands for an observed stop of somewhere between 1 and 3 clock hours.

U2 and U3 held as well. Under the plan's reading, PUDL's minimum down time (the shortest stop seen in 12 quarters) behaves like a hot-restart or trip-and-return time on steam and slow-start units, not a cold-start or commitment minimum, and the table's description could say so. The issue's concern that a 1-hour minimum down time is implausible for a steam coal unit as a commitment parameter still stands; this check suggests the cause is what the column measures, not missing reports. Options the issue lists, such as a percentile of down-run lengths instead of the minimum, are untouched by this check. The choice of fix is PUDL's.

## Limits

- Three states and one report year, the same as cems-blank-1; not a full PUDL build.
- A run's shape is read from CEMS alone. A partial flanking hour fits a real stop but does not prove one, and nothing here was checked against an outside source.
- The prime-mover class uses the 2024 crosswalk for all of 2023-2025; repowered units can be misclassed. EIA-860's cold-start code is self-reported and is used only to sort units.
- The newest polars and pandas below 3, not PUDL's locked environment; Gate K2 shows the run repeats cems-blank-1.
- PUDL's code (MIT) and data (CC BY 4.0) are downloaded at run time and not stored here. The job's per-run and per-unit CSVs are not committed.
- Made with AI agents working in MV2's name; no person has checked these results by hand.
