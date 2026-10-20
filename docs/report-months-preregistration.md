# Pre-registration: are stage moves in EIA-860M bunched in the reports around the annual survey?

Status: pre-registered 20 October 2026, before any job has run tools/annual-flows-candidate/monthsteps.py
on data. Twenty-third result of eia860m-slip. Job name when filed: monthsteps-v1 (a unit-test-only job,
monthsteps-unittests-v1, reads no data). MV2 of Munim, Inc. (made with AI agents). CC BY 4.0.

## Question

The twenty-first result (docs/stage-moves.md) followed each planned generator from one EIA-860M report to
the next and counted moves between stage bands: early (P, L), approved (T) and building (U, V, TS). It did
not ask in which month of the year the moves show up. If a large part of the moves shows up in the
reports around the annual survey, the month of a status change is partly a paperwork calendar, and an
analyst who sees a project step back in a January report should read it differently from one in July.

## Why December to March

- PUDL's EIA-860 page (docs.catalyst.coop/pudl/en/latest/data_sources/eia860.html, read 20 October 2026):
  "Annual responses are due between the beginning of January and the end of February."
- EIA's EIA-860M page (eia.gov/electricity/data/eia860m/, read 20 October 2026; fragments only):
  EIA-860M "supplements the annual survey form EIA-860 data with monthly information", and building the
  monthly figures sometimes "requires the use of data submitted on the annual EIA-860 before it has been
  fully verified by EIA".
- The window is the reports for December, January, February and March (4 of 12 calendar months): the
  last report of the year the annual form describes, and the reports for the months in which it is filed
  and taken in. The month of a step is the calendar month of report m + 1, the report in which the move
  first shows (PUDL's report_date: the month the data describes, not the month EIA publishes it, which is
  about four weeks later).

Two readings could bunch moves around the turn of the year, and this design cannot fully separate them:
(a) the filing calendar: annual responses and EIA's follow-up correct stale monthly statuses, so moves of
every direction bunch; (b) the project calendar: projects aiming to be in service by the end of the year
that miss it are re-planned in December or January, so mainly backward moves bunch. W2 (forward moves) is
the partial test between them. Either way the result is an association, not a cause.

## What was already seen (disclosed before the run)

- The twenty-first result's table of the 15 largest backward steps from building (docs/stage-moves.md)
  shows each move's report month. 14 of the 15 are inside this pool (Beekman Solar, 2026-02, is not); 7 of
  those 14 are in December-March reports (Obsidian 2021-01, Alle-Catt 2024-12, Easter 2019-01, Stagecoach
  2024-12, Changing Winds 2018-02, Cradle 2023-01, Crowned Ridge II 2019-12). Under no bunching, about 4.7
  of 14 would be. That table is why this question was asked, and W1's floor was set after seeing it: read
  W1 as partly informed.
- Nothing else by month has been read: not the full list of backward steps (the file backward_steps.csv
  from job stagemoves-v2, which was never tallied by month and is not published), and no forward,
  exit_other or to_operating move by month. W2 and W4 are on moves no one has looked at by month.

## Data and method

- Data: PUDL's nightly core_eia860m__changelog_generators.parquet, the cached copy under data_key
  pudl-eia860m that job stagemoves-v2 read (reports 2016-01 to 2026-08).
- Code: monthsteps.py 0.1.0 (this commit) on stagemoves.py 0.1.0 (pinned a059121) and eia860m_slip.py
  0.3.1 (pinned 329b7e6). The steps are exactly stagemoves' steps (rule R re-keys merged), pooled for m in
  2016-2025, so report m + 1 runs from 2016-02 to 2026-01 and each calendar month is ten reports.
- Kinds (moves counted / eligible steps):

| kind | starting bands | moves counted |
|---|---|---|
| backward | approved, building | backward |
| backward_building | building | backward |
| forward | early, approved | forward |
| exit_other | early, approved, building | exit_other (any status that is neither planned nor operating) |
| to_operating | early, approved, building | to_operating |

- Rates are generator counts (one per step): moves / eligible steps, inside the window and outside it.
  The ratio is the inside rate over the outside rate; no bunching gives about 1. Counts are primary so
  that a few large projects (the ones already seen) weigh no more than small ones; the same rates in MW
  are reported as description.

## Checks (all must pass before the predictions are scored)

- C1: the twelve months add up to stagemoves' pooled table for the same steps: steps exactly; step MW and
  backward-from-building MW to within 1.0 MW (each month's MW is rounded to 0.1).
- C2: every calendar month has exactly ten reports.
- C3: stagemoves' own checks S1-S4 pass on this run.
- C4 (read from the output by hand): C1's pooled backward-from-building MW equals the twenty-first
  result's 7,620.0 MW. If it does not, the cached data file changed; say so and score anyway.
- C5: all 7 unit tests in test_monthsteps.py pass, each expectation traced by hand before any run.

## Predictions (pooled 2016-2025, generator counts)

- W1: backward moves (from approved or building): the inside rate is at least 1.5 times the outside rate.
- W2: forward moves (from early or approved): the inside rate is at least 1.25 times the outside rate.
- W3: backward moves: the inside rate is higher than the outside rate in at least 7 of the 10 years of m,
  2016-2025. (A year of m, Y, covers reports 2-12 of Y and report 1 of Y + 1, so its window months are
  February, March and December of Y and January of Y + 1.)
- W4: exit_other moves (from any planned band): the inside rate is at least 1.5 times the outside rate.

Ratios are compared with their floors unrounded. A prediction with no rate (no eligible steps) is not
scored and is reported as such.

How the result will be read: W1 and W2 both held points to the filing calendar; W1 held and W2 not is
what year-end re-planning alone would give, without ruling out the filing calendar; W1 not held means the
top-table pattern is a property of a few large projects, not of backward moves in general. Description,
not predicted: the to_operating rate by month (many plants are reported as entering service in December).

## Prior art

Searched 20 October 2026 (web search for EIA-860M status changes by month of year, seasonality and the
annual survey). No study or EIA note found that counts EIA-860M status changes by calendar month. The
closest work on these status codes, Mounts and Cross (2024, arXiv:2406.15687) and Ullrich and Fleten
(2026), read stages at a point in time or pool them, as noted in docs/stage-moves.md and
docs/stage-leadtime-preregistration.md.

## Known limits

- Steps of the same generator are not independent, and ten reports per month means one unusual year can
  move a month's rate.
- Statuses are self-reported; a move's report month is when it was reported, not when it happened.
- The window is fixed in advance; no other window will be scored as a prediction.
