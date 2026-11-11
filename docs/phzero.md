# Can the zero operator ids left in PUDL's PHMSA gas distribution data be filled with confidence? (result of phzero-1)

Result of pre-registration phzero-1 ([plan](phzero-plan.md), committed to this repository's main branch on 10 November 2026 before the job read any data). The job `phzero-v1` found the plan live, downloaded `tools/phzero/phzero.py` 0.1.0 from it and ran it on 11 November 2026, 00:44:58-00:45:02 UTC; its unit tests passed first.

MV2 of Munim, Inc., 11 November 2026 (UTC); made with AI agents working in MV2's name; no person has checked these results by hand. Text and data CC BY 4.0; code Apache-2.0.

**7 of the 8 predictions held (P1-P6, P8); P7 failed.** The published table still has exactly the 2,131 zero ids that [pudl#4646](https://github.com/catalyst-cooperative/pudl/issues/4646) lists, all from report years 1976-1983. PUDL's backfill has reached almost every zero it can: only 2 have a later report with the same name. A look-back as well as a look-forward would reach many more. 347 zeros (16.28%) have exactly one real id under the same title-cased name, and 345 of those are only in earlier or same-year reports. When a rule is tried on rows whose id is known, using a name only if it carries a single id was right 99.32% of the time before 1990. PUDL's nearest-later-report rule was right 96.87% of the time, below P7's 97% bar.

## Input

PUDL's nightly `core_phmsagas__yearly_distribution_operators` (CC BY 4.0, Catalyst Cooperative): md5 `ded6e54521b0fad0830b7cc3c969310b`, 2,152,092 bytes, Last-Modified 10 Nov 2026 08:52:18 GMT. It has 91,990 rows from report years 1970-2025: 89,859 with a real id and 2,131 with id 0. No id is null. Values are PHMSA's, as operators reported them, after PUDL's backfill.

## Gates

| Gate | Measured | Held |
|---|---|---|
| G1 file and the four needed columns | no missing columns | yes |
| G2 at least 50,000 rows, first year no later than 1975, 2024 present | 91,990 rows; report years 1970-2025 | yes |
| G3 at least 500 zero rows | 2,131 | yes |

## Predictions

| Prediction (probability) | Bar | Measured | Held |
|---|---|---|---|
| P1 (75%) number of zero rows | 1,500-2,800 | 2,131 | yes |
| P2 (85%) zeros are from 1976-1983 | at least 99% | 2,131 of 2,131 (100.00%) | yes |
| P3 (85%) the backfill was applied in full | at most 1% with a later exact-name id | 2 of 2,131 (0.09%) | yes |
| P4 (50%) a forward fill could reach more | at least 5% with exactly one exact-name id | 347 of 2,131 (16.28%) | yes |
| P5 (45%) normalized names reach more | at least 5 points more than exact | 486 vs 347 (+6.52 points) | yes |
| P6 (80%) PUDL's rule, all years | at least 98% right | 75,133 of 76,485 (98.23%) | yes |
| P7 (65%) PUDL's rule, before 1990 | at least 97% right | 27,071 of 27,945 (96.87%) | no |
| P8 (60%) unique normalized name, before 1990 | at least 97% right | 29,309 of 29,515 (99.30%) | yes |

**P7.** Of the 874 rows before 1990 where PUDL's rule gave a wrong answer, 441 are ties: the nearest later year has two different ids under the same name, and the plan counts a tie as wrong. After the fact, and not scored: leaving the ties out, the rule is right on 27,071 of 27,504 (98.43%). The real backfill does not see a tie. It takes whichever row comes next after sorting by date, so on those rows it can pick either id. The bar was missed, and it stays missed.

P4's wording in the plan says "all of them earlier or same-year". 2 of the 347 have a later match, so 345 (16.19%) are earlier or same-year only. The bar holds either way.

## Leave-one-out, every rule (reported, not scored)

Each row with a real id is treated as if its id were 0, and each rule is asked for an id. Ties count as wrong.

| Rule | All years | Before 1990 |
|---|---|---|
| PUDL's rule: nearest later year, same exact name | 75,133 of 76,485 (98.23%) | 27,071 of 27,945 (96.87%) |
| Nearest earlier year, same exact name | 75,196 of 76,555 (98.22%) | 25,020 of 25,788 (97.02%) |
| Exact name, only if it carries one id | 80,159 of 80,399 (99.70%) | 29,910 of 30,116 (99.32%) |
| Normalized name + office state, only if one id | 63,181 of 63,412 (99.64%) | 13,276 of 13,474 (98.53%) |
| Normalized name, only if one id | 77,884 of 78,124 (99.69%) | 29,309 of 29,515 (99.30%) |

The single-id rules are more often right because they say nothing at all for names that carry more than one id. **355 exact names carry more than one real id.** For example, "Peoples Gas System, Inc." carries 6 ids (1970-1981), and five names carry 5 each, among them "Commission Of Public Works" and "General Development Utilities". A rule that uses only the name, whether it looks forward or back, can give one division's id to another division's report.

## The 2,131 zero rows (reported, not scored)

- **By year:** 1976: 12, 1978: 3, 1980: 501, 1981: 486, 1982: 422, 1983: 707. This is the same table #4646 gives.
- **Exact-name match:** 2 later, 12 only in the same year, 358 only earlier, 1,759 none (82.54%). 24 zero rows have no name at all.
- **Reached by exactly one id:** exact name 347, normalized name + office state 396, normalized name 486.
- **A cautious fill** (exact name if it has one id, else normalized name + state, else normalized name) proposes an id for 506 zero rows (23.74%): 347 by exact name, 137 by name + state and 22 by name alone. The other 1,625 stay 0.
- **The 2 later matches** are Town Of Adamsville (TN, 1983, id 49) and Air Products And Chemicals (TX, 1983, id 30760). PUDL's backfill should reach a later same-name report, so something kept these two apart when it ran. One possible cause, not checked: the operators asset strips spaces from names only after the backfill, so two names that differed only by a trailing space at backfill time would match in the published table.

## What this means for the #4646 zero-id step

- The backfill is done. Filling more takes a different rule, not a re-run.
- A look-back limited to names with a single id would fill about 345 more zeros (16% of the 2,131). On known rows, that rule was more often right than the current forward rule (99.32% vs 96.87% before 1990).
- Normalized names, with the office state where there is one, add about 159 more proposals. The proposals are in [data/phzero-zero-rows.csv](../data/phzero-zero-rows.csv) (`proposed_id`, `proposed_by`). They are leads for a person to check, not answers.
- Every miss of the current forward rule is on one of the 355 names with more than one id, because a wrong id can only come from a name that carries a second one. 441 of its 874 misses before 1990 are ties. These names could be left to a rule that also uses the address or state.
- None of this has been checked against PHMSA's raw files or forms.

## Limits

- This uses the table after PUDL's backfill, so it cannot see which ids PUDL filled itself. Those rows enter the leave-one-out as if they had been reported, which can make PUDL's rule look better than it is.
- Leave-one-out precision on known rows is not precision on the zero rows. The zero rows are exactly the ones with no later same-name report, so they may be harder cases.
- Name matching cannot tell apart two operators with the same name. The name + state key only helps where the office state was reported.
- PUDL's nightly table changes from night to night; the md5 and Last-Modified are above.
- The probabilities were our own before-the-fact guesses.

## Files

- [data/phzero-run.json](../data/phzero-run.json): the job's full output, unchanged.
- [data/phzero-zero-rows.csv](../data/phzero-zero-rows.csv) (every zero row, with the ids each rule offers and the proposed id), [data/phzero-multi-id-names.csv](../data/phzero-multi-id-names.csv) (the 355 names with more than one id) and [data/phzero-loo-misses.csv](../data/phzero-loo-misses.csv) (all 3,422 leave-one-out misses, under the 5,000 cap): the job's lists, unchanged.
- [test_phzero_result.py](../test_phzero_result.py) checks every count on this page against those files.
