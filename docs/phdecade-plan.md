# Does only the current install decade change from one PHMSA report year to the next? (plan)

Status: pre-registration, nothing run yet. Pre-registration id: phdecade-1.

MV2 of Munim, Inc., 11 November 2026 (UTC); made with AI agents working in MV2's name; no person has checked this plan by hand. Text CC BY 4.0; code Apache-2.0.

## Why

PHMSA's annual gas distribution report (Part B, Section 4) gives each operator's miles of main and number of services in operation at year end, split by the decade the pipe was installed. PUDL publishes this as `core_phmsagas__yearly_distribution_by_install_decade`. [pudl#5505](https://github.com/catalyst-cooperative/pudl/issues/5505) proposes a new table of yearly pipeline installations, built by comparing each operator's report with the one from the year before. The issue states the assumption and asks for it to be checked: "We expect that only the install_decade contained within the data (`2020s`) should be changing year to year, but we should verify this before dropping the data."

If older buckets also change from year to year (pipe retired or replaced, records corrected, mileage moved out of `unknown_decade`), then the change in the current bucket is new pipe less any of it removed, and the change in the total mixes new pipe with retirements. This check measures how often and by how much the older buckets move, before anyone builds on the assumption.

## What we have seen (before writing this)

- The text of pudl#5505 (opened 19 August 2026, labels `analysis`, `needs_gfi_treatment` and `phmsa`, no assignee, one comment by its author, no linked pull request). It proposes columns install_year, operator_id_phmsa, commodity, operating_state, mains_miles and services, and starting with 2015 data because commodity breakdowns do not exist before 2015.
- PUDL's `main` branch: the resource metadata in `src/pudl/metadata/resources/phmsagas.py` (8 fields: report_id, report_date, operator_id_phmsa, commodity, operating_state, install_decade, mains_miles, services; primary key report_id, report_date, operator_id_phmsa, commodity, install_decade). Its description says PHMSA reported that some operators entered negative values "to reconcile totals across Parts B1 and B4", and that those were replaced with zero.
- The asset `core_phmsagas__yearly_distribution_by_install_decade` in `src/pudl/transform/phmsagas.py`: commodity labels mapped and missing commodity set to "all", negatives in the decade rows clipped to 0, a sum check of the decades against `total_decades` (at most 43 mains and 162 services mismatches allowed), and the `total_decades` rows dropped. `INSTALL_DECADE_PHMSAGAS` in `src/pudl/metadata/patterns.py` matches a four-digit decade ending in "s", unknown_decade, pre_1940 or total_decades.
- Merged pull requests #5443 (the table) and #5548 (adds 2025 PHMSA data). A PUDL pull request search for `install_decade` shows only those two.
- The S3 listing of the nightly folder: `core_phmsagas__yearly_distribution_by_install_decade.parquet` is 1,034,817 bytes, last modified 2026-11-10T08:52:18Z.
- Not seen: any row of the table, its row count, which years it covers, or any operator's numbers.

## Data

- PUDL's nightly `core_phmsagas__yearly_distribution_by_install_decade` (`https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/core_phmsagas__yearly_distribution_by_install_decade.parquet`, CC BY 4.0, Catalyst Cooperative), all rows and all eight columns. The md5 and Last-Modified are recorded. Values are PHMSA's, as operators reported them, with PUDL's clipping of negatives.

## Method

`tools/phdecade/phdecade.py` 0.1.0 (standard library, plus polars to read the parquet file; its unit tests run first).

1. **Window:** report years 2015 to 2025.
2. **Key:** operator_id_phmsa, commodity and operating_state (the issue's columns without report_id). A key-year with more than one report_id is left out, and counted.
3. **Pairs:** a key with exactly one report in year t and exactly one in year t+1, for t = 2015 to 2024 (ten year pairs).
4. **Current decade** of a pair: the decade of year t+1 (2010s for t+1 up to 2019, 2020s from 2020). Every other bucket, including pre_1940 and unknown_decade, is an **old bucket**. A bucket missing in one of the two years counts as 0 there.
5. A bucket's mains **changed** if the two years differ by more than 0.001 miles (PUDL's own mains tolerance in its sum check); its services changed if they differ at all. A **material** mains change is more than 1 mile and more than 1% of the year-t value.
6. A pair has an **old mains change** if at least one old bucket's mains changed, and an **old services change** likewise.

**Gate G1:** the file downloads and has the eight columns.
**Gate G2:** at least 2,000 pairs, and at least 100 pairs in at least 8 of the 10 year pairs.

## Gate (if it fails, nothing is scored)

If G1 or G2 fails, no prediction is scored, and the result page says which gate failed and why.

## Predictions (probability we give each)

- **P1 (75%):** at least 40% of pairs have an old mains change.
- **P2 (85%):** the pairs with an old mains change hold at least 80% of all the pairs' year-t mains miles (large systems change most).
- **P3 (75%):** summed over all pairs, the old buckets lose mains miles (net change below -0.001 miles). If no old bucket changes at all, there is nothing to test, and P3 counts as failed.
- **P4 (75%):** summed over all pairs, the absolute changes in old buckets are at least 25% of the absolute changes in the current bucket. If the current bucket never changes, P4 counts as failed.
- **P5 (70%):** in at least 8 of the 10 year pairs, the four oldest buckets (pre_1940, 1940s, 1950s and 1960s) together lose mains miles (net change below -0.001 miles, summed over that year pair's pairs).
- **P6 (65%):** at least 40% of pairs have an old services change.

Reported, not scored:

- Pairs by year pair; key-years left out because they have more than one report; pairs where nothing changed; pairs with a material old change; pairs whose current bucket went down.
- For each old bucket: pairs, pairs with miles, pairs changed (mains, services), net and gross mains change, net services change. The net change of the current bucket next to the net change of the total, which are the two ways of differencing that #5505 could use.
- **Files:** every (year pair, bucket) with its counts and sums; every pair with its totals, current-bucket change and old-bucket changes; and the 300 largest old-bucket mains changes with operator id, commodity, state, bucket and both years' values.

## What happens with the result

A result page `docs/phdecade.md` in this repository, with every number checked by a test against the job's output, whatever it shows. MV2 will then post the counts once on pudl#5505, after the result page is live and on a UTC day with no other post from him in the PUDL repository, whether the assumption holds or not. He will not open a pull request or claim the issue unless a maintainer asks (MV2 has one PUDL community task open, on pudl#5154). A failed bar is reported as failed, with its cause, and is not re-scored.

## Limits

- This measures PUDL's published table, not PHMSA's raw files. A change between two years can be a real retirement, a correction, a transfer of pipe between operators or a typing error; the table cannot tell these apart, so this counts changes and does not explain them.
- Keys are matched by operator id, commodity and state text. An operator that changes its id or its state list, or splits a report, drops out of the pairs; a merger shows as a jump in one key.
- PUDL clips negative decade values to 0, so a bucket an operator reported as negative shows as 0 here.
- PUDL's nightly table changes from night to night; the md5 and Last-Modified are recorded.
- The probabilities are our own before-the-fact guesses.

The job (`phdecade-v1`, 1 CPU, 1 GB) waits until this plan is live on the main branch, then downloads `tools/phdecade/` from it and runs it, within a 240-minute limit (most of it the wait).
