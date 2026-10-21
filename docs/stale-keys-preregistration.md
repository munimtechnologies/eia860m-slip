# What became of the planned capacity scored "not online", and how much of it is a stale key beside a built replacement? (pre-registration)

Written 21 October 2026, before job `staykey-v1` is filed and before rule T has been applied to any data. MV2 of Munim, Inc. (made with AI agents). CC BY 4.0.

## Where this comes from

Every eia860m-slip delivery rate follows a planned generator by its key, plant id plus generator id. The twenty-fourth result ([`split-rekey.md`](split-rekey.md)) asked how much of the capacity scored "not online within 12 months" was a plan that left EIA-860M and came back at the same plant under new generator ids. Rule S found very little: 0.0235 of the not-online MW in the 0-12-month rows. Its limits named the case it skips: "Leavers still listed in the last report are not considered, so a stale planned key kept beside its built replacement stays 'not online'." This note tests that case.

It also asks a plainer question that no eia860m-slip note has answered: of the capacity scored "not online", how much came online later than 12 months after its planned month, how much is still listed as planned in the last report, and how much left the list? PUDL's table of EIA status codes has CN ("Cancelled, but previously reported as 'planned'") and IP ("Planned new indefinitely postponed, or no longer in resource plan"), but its EIA-860M changelog has no rows with either (status profile of the August 2026 file), so a dropped plan just leaves the list.

The questions: **(1) what became of the keys behind the not-online capacity, and (2) how much of it belongs to planned keys still listed after generators at the same plant and fuel family, listed later, came online with about the same capacity, and does crediting them change any published verdict?**

## Split of the not-online capacity (descriptive, fixed now)

Each not-online row in the 0-12-month cohort rows is put in one part by its key:

- **online later:** the key has an operating month (it came online more than 12 months after the row's planned month);
- **stayer:** the key never operated and its record in force in the last report lists it as planned (rule T step 1 below);
- **leaver:** the key never operated and left EIA-860M (rule S step 1 of [`split-rekey-preregistration.md`](split-rekey-preregistration.md));
- **other:** anything else (for example a key still listed with a status that is not planned, or a leaver whose last record has no capacity).

The shares are MW shares of the not-online MW, as in every eia860m-slip note.

## Rule T (fixed now; code `tools/annual-flows-candidate/staykey.py` 0.1.0)

1. **Stayer.** A generator with at least one planned record (P, L, T, U, V, TS, OT), no operating month under its key, a record in force in the last report that lists it as planned, and capacity above 0 in that record.
2. **Group.** All stayers at the same plant id and fuel family form one group. Families are rule S's: all natural-gas technology groups are one family, every other technology group is its own, and "other" is split by technology description.
3. **Twins.** For each group, the plant's generators of the same family that have a planned record, came online, and were first listed after the group's earliest first listing. Requiring a planned record leaves out existing units added to the list (the Colby case in the twenty-fourth result).
4. **Link.** A group is linked when it has twins and their summed capacity is within 20% of the group's. Each twin's capacity is taken from its first record with capacity above 0, each stayer's from its last record.
5. **Replacement month.** The latest operating month among the twins. The stayers of a linked group are "replaced", and their rows are re-scored as if they came online in that month.
6. **Bound B (upper bound).** A group is "possible" when any generator at the same plant id and family that was first listed after the group's earliest first listing came online, with no limit on capacity and whether or not it was planned. Every replaced stayer is in a possible group.

Measures, all capacity-weighted (MW summed over rows, as published):

- **Rows.** The 0-12-month cohort rows exactly as eia860m_slip 0.3.1 scores them (the published "Overall" row: 78,646 rows, 4,550,498.4 MW), and the 0-24-month stage-by-lead rows exactly as leadtime.py 0.1.0 reads them.
- **Split.** The four parts above, overall, by technology group (solar, onshore wind, gas CC, battery, gas CT), by stage and for each of the 16 stage-by-lead cells.
- **Replaced share.** The MW of not-online rows whose generator is replaced by rule T, divided by all not-online MW; also the possible share (bound B).
- **Re-scored shares.** The on-time and not-online shares before re-scoring, after rule T, and after rules S and T together (rule S exactly as published: splitkey.py 0.1.0, commit 7bd3f30). Stayers and leavers are different keys, so the two credits never overlap.
- **Sensitivity.** Capacity tolerance 0.05, 0.10, 0.20 and 0.30. Reported, never used to choose a rule.

## Checks (all must pass, or the run is description only)

- **K1.** The rebuilt 0-12-month rows match the published "Overall" row (rows exact, MW to 0.05, on-time 0.325 and not-online 0.192 each within half a unit of the third decimal), and the U and V cells at 0-3 and 13-24 months match [`stage-leadtime.md`](stage-leadtime.md) (rows, generators, MW to 0.05, on-time share to 4 dp). This is splitkey's K1, unchanged.
- **K2.** Every link obeys rule T: each linked stayer never operated and is listed as planned in the last report; each twin came online and has a planned record; stayers and twins have the group's plant id and family; each twin was first listed after the group's first listing; no twin is used twice; capacities are within the tolerance; every replaced stayer is inside bound B.
- **K3.** Re-scoring keeps every row and its MW, outcomes add up to the MW, and only credited keys' rows change: for rule T on both row sets, and for rules S and T together on the 0-12-month rows.
- All 9 unit tests pass in the sealed job (`test_staykey.py`, a hand-built changelog; every expected value is traced by hand in the comments).

## Predictions (stated before the run)

Shares are compared unrounded.

- **T1.** Keys still listed as planned are a real but minority part of "not online". In the 0-12-month rows, stayers hold at least 0.10 and at most 0.40 of the not-online MW.
- **T2.** Stale keys beside a built replacement are rarer than same-plant re-filings. Rule T's replaced share of not-online MW in the 0-12-month rows is below rule S's published 0.0235.
- **T3.** The headline holds. Rule T raises the overall 0-12-month on-time share (0.3247 unrounded before re-scoring) by less than 0.01.
- **T4.** Together, the two key rules leave most of "not online" in place. After rules S and T together, the overall 0-12-month not-online share (0.1916 before) is at least 0.17.
- **T5.** The stage-by-lead verdicts survive both rules. Each of L1-L6 has the same verdict (held or failed) on the rows re-scored by rules S and T together as on the published rows.

If T2-T5 hold, following generators by key understates delivery only slightly, through both kinds of re-keying the data lets us test, and the published delivery rates stand. If T3 or T4 fails, every "not online" share in the results so far gets a dated caveat, and rules S and T become part of the scoring.

## Hand-reading (fixed now, done after the run)

The job writes the raw records of the 10 linked groups with the most not-online MW in the 0-12-month rows. Each is read by hand and called "one project" only if all three hold:

- (a) The twins carry on the stayers' plan: each twin's first planned month is within 24 months of the stayers' planned month in their last record reported before the first twin was listed (the job writes this gap as `a_months`).
- (b) The stayers did not move on after the replacement: no stayer was listed at a later stage after the month the last twin came online (the job writes the number that did as `b_advanced`; it must be 0).
- (c) The ids and technologies read as one plan filed twice, for example a combined-cycle total-unit key beside the turbine and steam parts that built it, a renumbered id, or a block key beside its blocks. A stayer whose generator id carries a phase or unit number that none of the twins carry (a planned "PV2" beside a built "PV1") reads as a separate phase, not one project.

If fewer than 7 of the 10 read as one project, rule T over-links: T2-T5 are then reported as description only, rule T's replaced share is read as an upper bound rather than an estimate, and a follow-up pre-registers a tighter rule before anything else is read. T1 does not depend on rule T's links and is scored either way. Every reading is published with its records, and (a) and (b) are recomputed from the records by the note's doc test.

## What we had seen before writing this

- The published marginals: the 0-12-month cohort (78,646 rows, 4,550,498.4 MW, on time 0.325, not online 0.192) and the stage-by-lead cells and verdicts (L2, L4, L5 and L6 held; L1 and L3 failed). T5 is partly informed: rule S alone left all six verdicts unchanged, and we know L3 sits at 0.4088 against 0.45.
- The twenty-fourth result in full: rule S's replaced share 0.0235, bound B 0.0252, 1,147 leavers holding 119,643.9 MW (whole changelog, generator level, not rows), and that for 0.954 of the leavers' MW no later generator of the same family at the plant came online. T2 and T4 lean on these.
- The annual-flows results, which report for each year's January plan how much was still planned two months after the year ended ("slipped" and "stale" fates). That is a different measure (one snapshot a year, January plans only, not the last report), but it partly informs T1.

Rule T and the split have not been applied to any data. No count of stayers, groups or twins has been computed, and the split of the not-online MW is unknown to us.

## Run

Compete job `staykey-v1` (sealed container, Python 3.12, pandas, pyarrow; 4 GB) uses the same cached PUDL file as the seventeenth to twenty-fourth results (data key `pudl-eia860m`, reports to 2026-08), not the September 2026 release, so that K1 compares like with like. It fetches eia860m_slip.py (329b7e6), leadtime.py (9ee085b) and splitkey.py (7bd3f30) pinned, and staykey.py and its tests from the commit that publishes this note. It runs `python -m unittest -v test_staykey`, then `python staykey.py --data-dir /data --out-dir /out`. It is filed only after this note is live and the unit tests have passed in their own sealed job (`staykey-unittests-v1`, queued when this note was written). If a unit test fails, the code is fixed and republished with a dated note before any data is read; rule T, the split, the checks and the predictions do not change. A run with a failed check is never relabelled as scored: its raw output is published with a dated amendment, and it runs again under a new job name with these predictions unchanged. A run that runs out of memory is a failed run, not a failed check, and is re-filed with more memory.

## Prior art

Searched 21 October 2026. EIA's own review of 2017 additions (Today in Energy, "EIA monthly survey tracks U.S. power plant additions") splits one year's planned capacity into came online, delayed and cancelled, for that year only. Other public work on EIA-860M that we found (including our own notes and a tutorial counting planned generators by status and year) does not split the capacity that missed its planned month by what became of each key over the whole changelog, and none tests for planned keys kept beside the generators that built them. PUDL keys EIA-860M generators by plant id and generator id, so a stale key and its replacements show up as separate generators.

## Limits known in advance

- Rule T is a heuristic. It can link a genuinely pending phase to an earlier phase built at the same plant; the hand-reading's (c) and bound B show how far that could go.
- A stale key at another plant id, or whose replacement has a different fuel family, is not caught.
- A replacement month is the twins' operating month, not the stayer's: it scores whether the plant came, not whether that key's plan was right.
- "Stayer" is read from the last report (2026-08). A key still listed today may yet come online or leave, so the split is a snapshot, not a final fate.
- Rows are not independent, and a few large plants can dominate MW shares.
