# In which month do the annual EIA-860's plan-only projects enter EIA-860M? (pre-registration)

Written 21 October 2026, before job `entrytime-v1` runs and before we read the month of first EIA-860M listing of any generator of the years 2018-2025 in the sets below. MV2 of Munim, Inc. (made with AI agents). CC BY 4.0.

## Where this comes from

The twentieth result ([`annual-flows-eia860-entry.md`](annual-flows-eia860-entry.md)) found that most of the annual EIA-860's annual-only capacity for a year (generators the annual survey plans for year Y that January's EIA-860M plan for Y does not hold) was first listed in EIA-860M during Y, after January: 3,530.1 of 5,627.2 MW for 2017. Its correction of 20 October 2026 withdrew two claims because the run dated only each project's first EIA-860M record, not when the annual survey learned of it, and it promised that "A follow-up that can separate the two readings will be pre-registered before it is run." This is that follow-up. The two readings:

- **R1 (lag).** The annual filing for Y - 1, due early in Y, already held the project; EIA-860M listed it only after EIA took the filing in.
- **R2 (revision).** The annual record was added or revised during Y, before the final release, after the project had appeared elsewhere (for example in EIA-860M).

EIA's EIA-860M page (read 20 October 2026) says the monthly survey "supplements the annual survey form EIA-860 data with monthly information" and that it sometimes "requires the use of data submitted on the annual EIA-860 before it has been fully verified by EIA". That is a stated route from annual filings into the monthly inventory, so R1 is the favoured reading going in. R2 can hold for some projects at the same time.

EIA's final release of the annual EIA-860 for report year Y - 1 (the file that holds the plan for Y) came out in September of Y for every year 2018-2025 (9 November 2017 for 2017), from EIA's What's New archive, read 20 October 2026.

## Method

`tools/annual-flows-candidate/entrytime.py` 0.1.0, written before the run, with 15 unit tests on hand-built tables (`test_entrytime.py`). It rebuilds the twentieth result's sets with the same code, unchanged: entry860.py 0.1.0 (commit 44de204), baseline860.py 0.1.0 (7699d00), annual860.py 0.1.1 (c55b3c2) and eia860m_slip.py 0.3.1 (329b7e6), on the cached PUDL EIA-860M changelog (reports to 2026-08) and PUDL's `out_eia__yearly_generators` downloaded in the job. For each year Y 2017-2025 it takes three sets of generators:

- **A**: annual-only generators of Y first listed in EIA-860M after January of Y (entry860's `entered_after_january`).
- **A_built**: Y's EIA-860M new entries (came online in Y and not listed in January's report; eia860m_slip's `new_entry` after rule R) that are in Y's annual plan.
- **B** (control): Y's EIA-860M new entries that are not in Y's annual plan.

Each generator's MW goes to the month of Y of its first EIA-860M report (m01-m12), or to `before` / `after` Y, or `unlisted` (no EIA-860M record under its key). The statistic is the share of a set's February-December MW first listed in the reports for March-June: 4 of the 11 months, so 0.364 if entry were spread evenly. A second share, October-December, covers the reports after the September final release.

**Why A_built.** A and B differ in more than the annual plan: every B generator came online in Y, while A also holds projects that were still early in development. Projects close to operation may enter EIA-860M at a different time of year for that reason alone. A_built and B both came online in Y and both were missing from January's EIA-860M, so they differ only in whether the annual survey planned them for Y. A_built is new in this pre-registration (the design note had only A and B).

Reported for every year and pooled over 2018-2025: MW by bucket for each set, all technologies and each group, the two shares, and a CSV of every generator in the three sets with its first listing month. 2017 is reported as description only, because its quarters were already published.

## Checks (all must pass, or the run is description only)

- **U1.** For every year 2017-2025, A's total equals the twentieth result's `entered_after_january` (to 0.1 MW), A_built's its `new_entry_in_annual_plan_mw` (to 0.1 MW), and B's its `new_entry_mw` minus `new_entry_in_annual_plan_mw` (to 0.15 MW, a difference of two published figures). For 2018: 4,666.4, 3,828.4 and 2,307.5 MW.
- **U2.** In every year and set, the technology groups add up to the all-technology total (to 0.05 MW per row).
- **U3.** A has no MW first listed before February of Y or unlisted (to 0.05 MW), by its definition; A_built and B have at most 1% of their MW (or 0.05 MW) first listed in January or unlisted. A new entry was not listed in January, but its trimmed, any-case key can match another raw key's record.
- All unit tests pass in the sealed job.

U1 also guards against a change in PUDL's nightly tables since the twentieth run: if it fails for that reason, the raw output is published with a dated amendment and nothing is scored.

## Predictions (stated before the run)

Pooled over 2018-2025 and all technologies; shares are of February-December MW, compared with their thresholds unrounded (from MW to 0.1 MW) and rounded only for display.

- **P1.** A's March-June share is at least 0.50.
- **P2.** A's March-June share exceeds B's by at least 0.10.
- **P3.** A's March-June share exceeds B's in at least 6 of the 8 years 2018-2025.
- **P4.** A_built's March-June share exceeds B's by at least 0.10.
- **P5.** A's October-December share is at most 0.10.

**What the outcomes would mean.** If P1, P2 and P4 hold, the annual-only projects enter EIA-860M in the months after the annual filing is due, more than comparable projects the annual survey did not plan, which is what R1 predicts. If P2 holds and P4 fails, the contrast with B comes from how close to operation the projects were, not from the annual filing. If P1 fails, no bunching after the filing deadline shows at the monthly level, which weakens R1 as the main route; R2 would then fit A entering across the year like B, cut off before the September final release. P5 does not separate the two readings: under both, few annual-only projects should first appear in EIA-860M after the annual file is final. Capacity A first listed in October-December or after Y was in the annual data before EIA-860M listed it, so that share is a floor on the cases where the annual survey knew first. Every result is published, held or not.

## What we had seen before writing this

The twentieth result's raw output (`docs/entry860-v1-output.md`, `data/entry860_v1.json`): yearly MW by entry class, the first band of the after-January entrants, the new entries' MW found in the annual plan, and for 2017 only the after-January entrants by quarter of first report (February-March 1,135.3 MW; April-June 1,777.4; July-September 617.4; October-December 0.0; after 2017 0.0; of 3,530.1 MW) and the 15 largest annual-only generators with their first listing month. So for 2017 A's March-June share is somewhere between 0.50 and 0.83, and its October-December share is 0; P1 and P5 are informed by that one year. Nothing by month for 2018-2025, and no timing of any kind for A_built or B, has been read.

## Run

Compete job `entrytime-v1` (sealed container, Python 3.12, pandas, pyarrow) fetches eia860m_slip.py (329b7e6), annual860.py (c55b3c2), baseline860.py (7699d00) and entry860.py (44de204) from their commits and entrytime.py and test_entrytime.py from the commit that publishes this note, runs `python -m unittest -v test_entrytime`, then `python entrytime.py --data-dir /data --out-dir /out`. It is filed only after this note is public. A run with a failed check is never relabelled as scored: its raw output is published with a dated amendment and it runs again under a new job name, with these predictions unchanged.

## Limits known in advance

- A report month is not a release date: EIA publishes each EIA-860M report about three to four weeks after its month ends, and EIA may take an annual filing in months after it arrives. The test reads months, so a lag of a few months still lands in March-June only if EIA acts on filings by early summer.
- A contrast with B is evidence, not proof: R1 and R2 can both hold for different projects, and other things (the season in which projects are announced or financed) can shape when EIA-860M lists them.
- Matching is by key only (trimmed, any case), as in the twentieth result. A project re-keyed between surveys can sit in the wrong set; rule R links only re-keys of at least 10 MW.
- A generator's first listing is its first record in PUDL's changelog, which starts with the July 2015 report; every year scored starts after that.
- MW are summed over generators; a few large projects can dominate a year, which is why P3 counts years.
