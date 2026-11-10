# Can the zero operator ids left in PUDL's PHMSA gas distribution data be filled with confidence? (plan)

Status: pre-registration, nothing run yet. Pre-registration id: phzero-1.

MV2 of Munim, Inc., 10 November 2026 (UTC); made with AI agents working in MV2's name; no person has checked this plan by hand. Text CC BY 4.0; code Apache-2.0.

## Why

PHMSA's annual gas distribution reports use an operator id of 0 where the id is missing, mostly in the early 1980s. PUDL fills some of them: `backfill_zero_operator_id_phmsa` in `src/pudl/transform/phmsagas.py` sorts the reports by `report_date`, title-cases `operator_name_phmsa`, turns the zeros into nulls, and fills each one with `groupby("operator_name_phmsa")[...].bfill()`, that is, only from a **later** report with exactly the same title-cased name; whatever is left goes back to 0. Its docstring says the aim is to replace all of the zeros confidently, and that for now only exact name matches are used. [pudl#4646](https://github.com/catalyst-cooperative/pudl/issues/4646) (open, unassigned, no comments on 10 November 2026) lists "Fill in/clean up `operator_id_phmsa` = 0" as one of the steps before the `_core_phmsagas__yearly_distribution_*` tables can become `core`, with 2,131 zeros left out of 90,532 records.

Two simple ways to fill more are visible in the code itself: look back as well as forward (an exact-name match that is only **earlier** is never used by a backfill), and match names after removing punctuation and words like "Inc" or "Company". This check measures how many of the remaining zeros each would reach, and, on the rows whose id is known, how often each rule (and PUDL's own forward rule) gives the right id when the id is hidden. That tells whoever does the #4646 step whether a wider fill is safe before it is written.

## What we have seen (before writing this)

- The body of pudl#4646, including its table of the remaining zeros by year: 1976: 12, 1978: 3, 1980: 501, 1981: 486, 1982: 422, 1983: 707 (these sum to 2,131), and its two sub-issues (#5266, closed; #5435, open).
- In PUDL's `main` branch: `backfill_zero_operator_id_phmsa` (bfill only, no ffill; ascending `report_date`; title-cased names; leftovers set back to 0) and the call order in `_core_phmsagas__yearly_distribution` (nulls set to 0, then the backfill, then `_dedupe_year_distribution_idx`, which drops non-unique rows whose id is 0); the metadata of `core_phmsagas__yearly_distribution_operators` in `src/pudl/metadata/resources/phmsagas.py` (15 fields including report_id, report_date, operator_id_phmsa, operator_name_phmsa and office_state; primary key report_id, report_date, operator_id_phmsa).
- A search of PUDL's issues and pull requests for `operator_id_phmsa` (7 results: #5505, #4646, #5435, #5443, #5266, #4005, #3929); none other than #4646 is about the zero ids.
- The S3 listing of the nightly folder: `core_phmsagas__yearly_distribution_operators.parquet` is 2,152,092 bytes, last modified 2026-11-10T08:52:18Z.
- Not seen: any row of the table, its row count or years, any operator name, or how many zeros it holds today.

## Data

- PUDL's nightly `core_phmsagas__yearly_distribution_operators` (`https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/core_phmsagas__yearly_distribution_operators.parquet`, CC BY 4.0, Catalyst Cooperative): report_id, report_date, operator_id_phmsa, operator_name_phmsa and office_state, all rows; the md5 and Last-Modified are recorded. Values are PHMSA's, as operators reported them, after PUDL's backfill.

## Method

`tools/phzero/phzero.py` 0.1.0 (standard library, plus polars only to read the parquet file; its unit tests run first).

1. **Report year** is the first four digits of `report_date`. An id is **zero** if it is 0, **null** if it is missing; both count as a zero below. Every other id is **real**.
2. Three name keys: **exact** is the name title-cased with Python's `str.title` and nothing else (PUDL's key); **norm** is the name lower-cased, `&` read as "and", every run of other non-letters and non-digits made one space, and the words inc, incorporated, co, company, corp, corporation, llc, ltd, lp, the and of dropped; **norm_state** is norm plus `office_state` (trimmed, upper-cased; only when both exist).
3. **Zero rows**: for each zero row, the real ids that rows with the same key carry (any year). An exact match is **later** if one such row has a later report year, else **same_year**, else **earlier**. A rule **reaches** a row if it offers exactly one id.
4. **Leave-one-out**: for each row with a real id, pretend it is 0. **PUDL's rule** gives the id(s) on the nearest later report year with the same exact name (two different ids in that year is a tie and counts as wrong); the **earlier** rule does the same looking back; each **unique** rule gives the other rows' ids for its key and is used only when there is exactly one. Precision = right / given. **Early** means report years before 1990.

**Gate G1:** the file downloads and has report_id, report_date, operator_id_phmsa and operator_name_phmsa.
**Gate G2:** at least 50,000 rows, a first report year no later than 1975, and report year 2024 present.
**Gate G3:** at least 500 zero rows.

## Gate (if it fails, nothing is scored)

If any of G1-G3 fails, no prediction is scored; the result page says which gate failed and why (a G3 failure would mean the zeros have already been filled).

## Predictions (probability we give each)

- **P1 (75%):** the table has between 1,500 and 2,800 zero rows.
- **P2 (85%):** at least 99% of the zero rows are from report years 1976 to 1983, as #4646's table shows.
- **P3 (85%):** at most 1% of the zero rows have an exact-name match with a later real id (PUDL's backfill has been applied in full to the published table).
- **P4 (50%):** at least 5% of the zero rows have an exact-name match with exactly one real id (all of them earlier or same-year, so a backfill cannot reach them and a forward fill could).
- **P5 (45%):** the normalized name gives exactly one real id to at least 5 percentage points more of the zero rows than the exact name does.
- **P6 (80%):** PUDL's rule gives the right id for at least 98% of the rows with a real id where it gives one (leave-one-out, all years).
- **P7 (65%):** the same, at least 97%, on report years before 1990.
- **P8 (60%):** the unique normalized-name rule gives the right id for at least 97% of the rows before 1990 where it gives one.

Reported, not scored:

- Rows by year; zero and null rows by year; zero rows by exact-match timing (later, same_year, earlier, none); how many zero rows each rule reaches; the id a cautious fill would propose (exact, else norm_state, else norm, each only when unique) and how many each step gives.
- Leave-one-out counts (given, right, ties) for every rule, all years and before 1990; the number of exact names carried with more than one real id.
- **Files:** every zero row with the ids each rule offers and the proposed id; every exact name with more than one real id; up to 5,000 leave-one-out misses.

## What happens with the result

A result page `docs/phzero.md` in this repository, with every number checked by a test against the job's output, whatever it shows. MV2 will not post on pudl#4646 before that page is live, will post there at most once, briefly, with the counts that bear on the zero-id step, and will not open a pull request for it unless a maintainer asks for one (MV2 has one PUDL community task open, on pudl#5154). A failed bar is reported as failed, with its cause, and is not re-scored.

## Limits

- This uses PUDL's published table, after the backfill, so it cannot see which real ids PUDL itself filled; those rows enter the leave-one-out as if they were reported, which can make PUDL's rule look better than it is.
- Leave-one-out precision on rows with a real id is not the same as precision on the zero rows: the zero rows are exactly the ones with no later same-name report, so they may be harder cases. The proposed ids are leads for a person to check, not answers.
- Name matching cannot tell apart two operators with the same name; the norm_state key only helps where the office state was reported.
- PUDL's nightly table changes from night to night; the md5 and Last-Modified are recorded.
- The probabilities are our own before-the-fact guesses.

The job (`phzero-v1`, 1 CPU, 1 GB) waits until this plan is live on the main branch, then downloads `tools/phzero/` from it and runs it, within a 240-minute limit (most of it the wait).
