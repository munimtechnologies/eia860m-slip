# Where did the projects only the annual EIA-860 plans stand in EIA-860M? (pre-registration)

Written 19 October 2026, before job `entry860-v1` runs and before we read any EIA-860M record of a generator in the annual plan only. MV2 of Munim, Inc. (made with AI agents). CC BY 4.0.

## Where this comes from

[`annual-flows-eia860-baseline.md`](annual-flows-eia860-baseline.md) rebuilt the annual EIA-860's own plan for each year (generators the annual report for Y - 1 lists as planned for a month in Y) and compared it with January's EIA-860M plan for the same year. About a fifth of each plan is projects the other does not hold. For 2017, 5,627.2 MW of the 26,808.6 MW annual plan is not in January's EIA-860M plan (`annual_only`), and 85.1% of it came online in 2017, against 63.8% for January's EIA-860M plan as a whole. [`annual-flows.md`](annual-flows.md) separately counts 4,626.7 MW of 2017 additions that EIA-860M did not list at all in January 2017.

The open question that note names: are the annual-only projects the generators that entered EIA-860M during the year? The annual EIA-860 for a year is filed and published during the following year, while January's EIA-860M is the inventory at the start of that year. If the annual-only part is mostly projects that only reached EIA-860M after January, the annual survey's planned list for a year partly records what was already being built, and any planned-against-built comparison that starts from it measures something different from a January forecast.

## Method

`tools/annual-flows-candidate/entry860.py` 0.1.0, written before the run, with 10 unit tests on hand-built tables (`test_entry860.py`):

1. **The annual plan and its annual-only part** are rebuilt with baseline860.py 0.1.0 (commit 7699d00) unchanged, on annual860.py 0.1.1 (c55b3c2) and eia860m_slip.py 0.3.1 (329b7e6), with the same cached PUDL EIA-860M file (`core_eia860m__changelog_generators`, reports to 2026-08) and PUDL's `out_eia__yearly_generators` downloaded in the job.
2. **Entry class.** Each annual-only generator of year Y (key: plant id and generator id, trimmed, any case) gets exactly one class from the EIA-860M changelog:
   - `in_january_not_planned`: a record is in force in January's report of Y with a status that is not planned;
   - `in_january_other_month`: in force in January, planned, for a month outside Y or undated;
   - `in_january_planned_in_year`: in force in January, planned for a month in Y (expected to be none, since those generators are January's plan; check E3);
   - `entered_after_january`: first listed in a report after January of Y;
   - `listed_before_not_in_january`: first listed before January of Y, with no record in force in January;
   - `never_in_860m`: never listed.
3. **First band.** The status in the generator's first EIA-860M record: `operating` (OP, SB, OS, OA), `building` (U, V, TS), `approved` (T), `early` (P, L) or `other`.
4. **New entries.** The year's EIA-860M additions not listed in January (eia860m_slip's `new_entry` after rule R, as in `annual-flows.md`) are looked up by the same key in the year's annual plan (any group).
5. Reported for every year 2017-2025 and technology group: MW by entry class, the share that entered after January (`after_share`), MW of those entrants by first band, the share of them that came online in the year by the annual date, and the new entries' MW found in the annual plan. For 2017: the after-January entrants' MW by quarter of first report, and the 15 largest annual-only generators and the 15 largest new entries not in the annual plan, all technologies and onshore wind.

## Checks (all must pass, or the run is description only)

- **E1.** Every column the annual plan needs is in the annual file, and the annual plan and annual-only MW (all technologies) equal the nineteenth result's table to 0.1 MW in every year 2017-2025 (2017: 26,808.6 and 5,627.2 MW).
- **E2.** In every row, the entry classes add up to the annual-only MW, to 0.05 MW.
- **E3.** `in_january_planned_in_year` is at most 0.05 MW in every year 2017-2025 (all technologies).
- **E4.** The 2017 new entries total 4,626.7 MW (to 0.1 MW), as in `annual-flows.md`.
- All unit tests pass in the sealed job.

E1 also guards against a change in PUDL's nightly annual table since the nineteenth run: if it fails for that reason, the raw output is published with a dated amendment and nothing is scored.

## Predictions (stated before the run)

Shares are compared with their thresholds unrounded (from MW to 0.1 MW) and rounded only for display.

- **A1.** At least 0.60 of the 2017 annual-only MW (all technologies) is `entered_after_january`.
- **A2.** Of the 2017 annual-only MW that entered after January, at least 0.80 has a first EIA-860M record that is `operating` or `building`.
- **A3.** In at least 6 of the 8 years 2017-2024, `after_share` (all technologies) is at least 0.50.
- **A4.** At least 0.50 of the 2017 new entries' MW (4,626.7 MW) is in the 2017 annual plan.

If A1 and A3 hold, the annual-only part of the annual plan is mostly projects EIA-860M first listed during the year, and A2 says whether they arrived already built or being built. If A1 fails, the annual-only part was mostly known to EIA-860M in January under another status or month, and the class table says which. A4 asks the question from the other side: whether the projects EIA-860M learns of during a year are, for the most part, in the annual survey's plan for that year. Every result is published, held or not.

## What we had seen before writing this

The nineteenth result's raw output (`docs/baseline860-v2-output.md`): yearly totals, and for 2017 the 15 largest annual-only and EIA-860M-only generators by name, key, MW and annual class. `annual-flows.md` and its raw output: yearly new-entry totals by group. No EIA-860M record of any annual-only generator has been read, and no list of 2017 new entries by generator.

## Run

Compete job `entry860-v1` (sealed container, Python 3.12, pandas, pyarrow) fetches eia860m_slip.py (329b7e6), annual860.py (c55b3c2) and baseline860.py (7699d00) from their commits, runs `python -m unittest -v test_entry860`, then `python entry860.py --data-dir /data --out-dir /out`. A run with a failed check is never relabelled as scored: its raw output is published with a dated amendment and it runs again under a new job name, with these predictions unchanged.

## Limits known in advance

- A generator's first EIA-860M listing is its first record in PUDL's changelog, which starts with the July 2015 report (as in `annual-flows.md`'s raw output), so a generator first listed then may have been listed earlier; for every year scored that start is before January.
- Matching is by key only, as in the nineteenth result. A generator renumbered between the surveys reads `never_in_860m` here even if EIA-860M lists it under another key; the named lists let a reader check the largest ones.
- An entrant's first band is from its first record, which can lag the true status by the time EIA-860M takes to add a project.
- Why the annual survey's list includes these projects (when respondents file, how EIA compiles the planned list) is not tested; this run only says where the projects stood in EIA-860M.
