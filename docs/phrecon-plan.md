# Do PHMSA Part B1 (material) and Part B4 (install decade) totals agree in PUDL? (plan)

Status: pre-registration, nothing run yet. Pre-registration id: phrecon-1.

MV2 of Munim, Inc., 11 November 2026 (UTC); made with AI agents working in MV2's name; no person has checked this plan by hand. Text CC BY 4.0; code Apache-2.0.

## Why

PHMSA's annual gas distribution report (Form PHMSA F 7100.1-1) gives each operator's miles of main and number of services twice: by material (Part B, Section 1) and by the decade the pipe was installed (Part B, Section 4). PUDL publishes the first as `_core_phmsagas__yearly_distribution_by_material` (not yet cleaned) and the second as `core_phmsagas__yearly_distribution_by_install_decade`. PUDL's description of the decade table says PHMSA told Catalyst that some operators entered negative values "to reconcile totals across Parts B1 and B4", and PUDL replaces those negatives with zero.

Nobody has published how often the two parts actually agree in the data. [pudl#4646](https://github.com/catalyst-cooperative/pudl/issues/4646), the open issue for cleaning and validating the PHMSA distribution tables, lists "spend time validating the numeric data" as a task still to scope, probably as dbt tests. A B1-against-B4 check is one such test. This study measures it with PHMSA's own consistency rule, before anyone writes the test, and shows how much PUDL's zero-clipping moves the decade totals away from the material totals.

## What we have seen (before writing this)

- PUDL's `main` branch: `src/pudl/metadata/resources/phmsagas.py` (the decade table's description quoted above; `_core_phmsagas__yearly_distribution_by_material` is an underscore table with its primary key commented out) and `src/pudl/transform/phmsagas.py` (the decade asset clips negative decade values to 0, checks the decades against `total_decades` and drops the `total_decades` rows; the material asset clips nothing). `MATERIAL_TYPES_PHMSAGAS` in `src/pudl/metadata/enums.py` includes `all_materials` and `total`.
- PHMSA's consistency rule, as given in its instructions for Form PHMSA F 7100.1-1 (CY 2017 and later versions, including rev 6-2023): "Part B4, decade of installation, will serve as the baseline for main miles and service counts", and "Main miles and service counts over 60 must be within 0.5% of the baseline and values under 60 must be within 0.3 miles for main and service counts must match exactly", with an example that 60 miles in Part B4 allows Parts B1 and B2 to be within 0.3 miles. We saw this wording only in search-engine excerpts of PHMSA's instruction PDFs: phmsa.dot.gov and regulations.gov refused our fetcher (HTTP 403) and our tools could not read the PDF text, so no person has checked these quotes against the PDFs.
- Searches of PUDL's issues ("phmsa material", "phmsagas" in titles) and pull requests ("install_decade": only #5443 and #5548): none is about comparing Part B1 with Part B4.
- The S3 listing of the nightly folder on 11 November 2026: `_core_phmsagas__yearly_distribution_by_material.parquet` is 2,250,542 bytes and `core_phmsagas__yearly_distribution_by_install_decade.parquet` is 1,034,817 bytes, both last modified 2026-11-11 06:33 UTC.
- Not seen: any row of either table, their row counts, which years have a `total` material row, or any operator's numbers.

## Data

- PUDL's nightly `_core_phmsagas__yearly_distribution_by_material` and `core_phmsagas__yearly_distribution_by_install_decade` (`https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/<table>.parquet`, CC BY 4.0, Catalyst Cooperative). The md5 and Last-Modified of each are recorded. Values are PHMSA's as operators reported them, with PUDL's clipping of negative decade values.

## Method

`tools/phrecon/phrecon.py` 0.1.0 (standard library, plus polars to read the parquet files; its unit tests run first).

1. **Report:** report year, report_id and operator_id_phmsa. Duplicate rows for a report and material are summed and counted.
2. **B1 total:** the report's `total` material row. **B1 material sum:** the sum of its other material rows, leaving out `all_materials` (counted). A blank value is left out, not read as 0; a report whose `total` value is blank has no B1 total.
3. **B4 sum:** the sum of the report's decade rows (every decade, `pre_1940` and `unknown_decade` included), after PUDL's clipping. A report with no non-blank decade value has no B4 sum.
4. **PHMSA's rule, with B4 as the baseline** (our reading of the wording above): if the B4 sum is over 60, the B1 total passes when it is within 0.5% of the B4 sum; if the B4 sum is 60 or less, it passes when it is within 0.3 miles (mains) or exactly equal (services). Floating-point slack of 0.000001 is allowed.
5. **Exact:** mains within 0.001 miles (PUDL's own mains tolerance), services equal.
6. A report is **comparable** for mains (or services) when it has both a B1 total and a B4 sum for it. A failing report is **B4 higher** or **B4 lower**.
7. **Windows:** report years 2017 to 2025 (the scored years); report years 2009 and earlier (before PHMSA's 2010 form); 2010 to 2016 is reported, not scored.

**Gate G1:** both files download and have the needed columns.
**Gate G2:** at least 5,000 comparable reports for mains in 2017 to 2025, and at least 300 in each of those 9 years.

## Gate (if it fails, nothing is scored)

If G1 or G2 fails, no prediction is scored, and the result page says which gate failed and why. The counts by year are still published.

## Predictions (probability we give each)

- **P1 (70%):** at least 97% of comparable 2017 to 2025 reports pass PHMSA's rule for mains.
- **P2 (55%):** at least 90% of comparable 2017 to 2025 reports match exactly for mains.
- **P3 (60%):** of the 2017 to 2025 reports that fail PHMSA's rule for mains, at least 60% are B4 higher (what zero-clipping of negative decade values would cause). If fewer than 10 fail, there is nothing to test, and P3 counts as failed.
- **P4 (65%):** at least 95% of comparable 2017 to 2025 reports pass PHMSA's rule for services.
- **P5 (55%):** the share of comparable reports passing for mains is at least 10 percentage points higher in 2017 to 2025 than in report years 2009 and earlier. If fewer than 1,000 reports from 2009 and earlier are comparable, there is nothing to test, and P5 counts as failed.
- **P6 (50%):** `_core_phmsagas__yearly_distribution_by_material` has at least one negative `mains_miles` or `services` value in a non-total material row (any year).
- **P7 (75%):** inside Part B1, the material sum passes PHMSA's rule for mains against B1's own total (the total as baseline) in at least 97% of comparable 2017 to 2025 reports.

Reported, not scored:

- By report year: reports in both tables, in B1 only, in B4 only; comparable, passing, exact, B4 higher and B4 lower, for mains and services; reports with no B1 total or no B4 sum; the B1 material sum against the B4 sum; material labels by era; negative values in either table.
- **Files:** counts by year; every report that fails PHMSA's rule for mains or services (up to 3,000 rows) with operator id, commodity, state, both totals, the B1 material sum and the difference; and every negative non-total value in the material table (up to 2,000 rows).

## What happens with the result

A result page `docs/phrecon.md` in this repository, with every number checked by a test against the job's output, whatever it shows. MV2 will then post the counts once on pudl#4646, as a candidate check for its numeric-validation task, after the result page is live and on a UTC day with no other post from him in the PUDL repository, whether the parts agree or not. He will not open a pull request unless a maintainer asks (MV2 has one PUDL community task open, on pudl#5154). A failed bar is reported as failed, with its cause, and is not re-scored.

## Limits

- This measures PUDL's published tables, not PHMSA's raw files. The decade table has PUDL's zero-clipping and no `total_decades` rows, so a report that matched before clipping can fail here; that is part of what is measured, but this cannot show the original negative values.
- PHMSA's portal check is described in its instructions; we do not know from which year the portal enforced it, or whether supplemental reports were held to it.
- The rule's wording ("over 60" and "under 60") leaves exactly 60 open; we treat 60 as small, following PHMSA's own example.
- Reports are matched by report_id and operator id within a year; a report missing from one table counts as one-sided, not as a failure.
- PUDL's nightly tables change from night to night; the md5 and Last-Modified are recorded.
- The probabilities are our own before-the-fact guesses.

The job (`phrecon-v1`, 1 CPU, 2 GB) waits until this plan is live on the main branch, then downloads `tools/phrecon/` from it and runs it, within a 240-minute limit (most of it the wait).
