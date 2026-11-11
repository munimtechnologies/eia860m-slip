# Do PHMSA Part B2/B3 (material and size) totals agree with Parts B1 and B4 in PUDL, and is the 2017+ `pvc` label right? (plan)

Status: pre-registration, nothing run yet. Pre-registration id: phb23-1.

MV2 of Munim, Inc., 11 November 2026 (UTC); made with AI agents working in MV2's name; no person has checked this plan by hand. Text CC BY 4.0; code Apache-2.0.

## Why

PHMSA's annual gas distribution report (Form PHMSA F 7100.1-1) gives each operator's miles of main and number of services several times over: by material (Part B, Section 1), by material and size (Section 2 for mains, Section 3 for services) and by the decade the pipe was installed (Section 4). PUDL publishes Sections 2 and 3 together as `_core_phmsagas__yearly_distribution_by_material_and_size`, one of the tables that [pudl#4646](https://github.com/catalyst-cooperative/pudl/issues/4646) plans to clean and validate ("spend time validating the numeric data" is one of its open tasks).

Our earlier plan [phrecon-1](phrecon-plan.md) compares Section 1 with Section 4. This one adds the third view. It asks whether the material-and-size table's grand totals agree with the other two parts by PHMSA's own consistency rule, and whether its cells add up to its own totals. Where Section 4 disagrees with Sections 1 and 2 at once, that points at Section 4 (where PUDL sets negative decade values to zero). Where only Section 2 disagrees, that points at Section 2.

It also tests one line of PUDL's column map. For the 2017 form, `src/pudl/package_data/phmsagas/column_maps/yearly_distribution.csv` files PHMSA's raw `mmiles_plastic_unk`, `mmiles_plastic_lt2in` and `mmiles_plastic_total` fields under PUDL's `main_pvc_*` columns, next to separate raw PE, ABS and other-plastic fields. If those raw fields really are PVC only, Section 1's plastic miles should equal PVC + PE + ABS + other plastic. If they are all plastics, Section 1's plastic miles should equal the `pvc` total alone. The data can tell the two apart.

## What we have seen (before writing this)

- PUDL's `main` branch, `src/pudl/transform/phmsagas.py`. The material-and-size asset melts columns matching `^main_(<materials>)_(<main sizes>)_miles$` and `^services_(<materials>)_(.*)$` and takes `material` and `main_size` from each column name with unanchored `str.extract`. It clips nothing and drops no total rows. The material asset melts `^main_(<materials>)_miles$` and `^services_(<materials>)$`. Only the install-decade asset clips negatives to zero and drops `total_decades` rows.
- `src/pudl/metadata/enums.py`: `MATERIAL_TYPES_PHMSAGAS` lists `other_plastic` before `plastic`, `other_alt` and `other_material` before `other`, and the four steel kinds before `steel`. So the leftmost-alternative rule gives the longer names, and we found no material mislabelling from the alternation order. `MAIN_PIPE_SIZES_PHMSAGAS` ends with `total` and `unknown`.
- The column map's header and its 2004 and 2017 rows, read through a fetch tool that aligns cells by position. No person has checked this alignment. Part B1 columns include `main_unprotected_steel_bare_miles` (2017 raw `mmiles_steel_unp_bare`), `main_plastic_miles` (`mmiles_plastic`) and `main_total_miles` (`mmiles_total`). The grand total `main_all_materials_total_miles` maps to raw `mmiles_part_b2_total` in 2017 and is blank in 2010. `services_all_materials_total` maps to `num_srvs_part_b3_total` in 2017. `main_pvc_total_miles` maps to `mmiles_plastic_total` in 2017 and `pvcmt` in 2004. `main_pe_total_miles` maps to `mmiles_pe_total`, `main_abs_total_miles` to `mmiles_abs_total` and `main_other_plastic_total_miles` to `mmiles_oth_plstc_total`. `main_plastic_total_miles` is blank in both years. `services_steel_over_8_in` maps to `num_srvs_steel_gt8in`.
- We could not read PHMSA's field descriptions. The Data Fields PDF linked from PUDL's PHMSA page came back as compressed PDF streams our tools cannot read. So whether `mmiles_plastic_*` means PVC or all plastics is not known to us before the data.
- PHMSA's consistency rule, as quoted in [phrecon-1](phrecon-plan.md) from search-engine excerpts of its instructions (CY 2017 and later): Part B4 is the baseline; over 60 within 0.5%; under 60 within 0.3 miles for mains and exactly for services. The example there names Parts B1 and B2. No person has checked these quotes against the PDFs.
- A PUDL issue search for "phmsagas size" (11 November 2026) found 4 items (#2848, #4005, #3770, #3670), none about Section 2/3 totals or the PVC label. An earlier search for `main_size`, `by_material_and_size` and `over_8_in` found none ([phsize-1](phsize-plan.md)).
- The S3 listing of the nightly folder on 11 November 2026: `_core_phmsagas__yearly_distribution_by_material_and_size.parquet` is 6,532,003 bytes, `_core_phmsagas__yearly_distribution_by_material.parquet` 2,250,542 bytes (both last modified 2026-11-11 06:33:16 UTC), and `core_phmsagas__yearly_distribution_by_install_decade.parquet` 1,034,817 bytes.
- Not seen: any row of any of the three tables, their row counts or years, or any operator's numbers. Neither phrecon-1 nor phsize-1 has run yet.

## Data

PUDL's nightly `_core_phmsagas__yearly_distribution_by_material_and_size`, `_core_phmsagas__yearly_distribution_by_material` and `core_phmsagas__yearly_distribution_by_install_decade` (`https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/<table>.parquet`, CC BY 4.0, Catalyst Cooperative). The md5 and Last-Modified of each are recorded. Values are PHMSA's as operators reported them, with PUDL's clipping of negative decade values.

## Method

`tools/phb23/phb23.py` 0.1.0 (standard library, plus polars to read the parquet files in slices of 1,000,000 rows; its unit tests run first).

1. **Report:** report year, report_id and operator_id_phmsa. A blank value is left out, not read as 0; a sum with no non-blank value is blank.
2. **Section 2/3 grand total:** the rows with material `all_materials` and size `total`. **Cell sum:** every row whose material is not `all_materials` or `total` and whose size is not `total` or blank. Rows with a blank size are counted but left out, since phsize-1 expects some services sizes to lose their label, and the material table's own by-material services count can fall into this table with no size. **Material totals:** each material's size-`total` row.
3. **Section 1:** the `total` material row, and each material's value; `all_materials` rows are left out (counted).
4. **Section 4:** the sum of the decade rows after PUDL's clipping, as in phrecon-1.
5. **Material groups** to line the sections up: steel = the four steel kinds and `steel`; plastic = `pvc`, `pe`, `abs`, `other_plastic` and `plastic`; other = `other`, `other_alt` and `other_material`; every other material is its own group.
6. **PHMSA's rule** (the second value is the baseline): if the baseline is over 60, a value passes when it is within 0.5% of it; if it is 60 or less, within 0.3 miles (mains) or exactly equal (services). Floating-point slack of 0.000001 is allowed. Comparisons: grand total against the Section 4 sum (baseline Section 4); grand total against the Section 1 total (baseline Section 1); cell sum against the grand total (baseline the grand total); each Section 2/3 group total against the Section 1 group (baseline Section 1).
7. **Plastic test:** a report is **comparable** when it has a Section 1 plastic value, a `pvc` total and a plastic-group total. It is **discriminating** when the plastic-group total and the `pvc` total alone do not both pass against Section 1's plastic value. Only discriminating reports are scored.
8. **Window:** report years 2017 to 2025 are scored; every year is reported.

**Gate G1:** all three files download and have the needed columns.
**Gate G2:** at least 5,000 reports in 2017 to 2025 with both a mains grand total and a Section 4 mains sum, and at least 300 in each of at least 7 of those 9 years.

## Gate (if it fails, nothing is scored)

If G1 or G2 fails, no prediction is scored, and the result page says which gate failed and why. The counts by year are still published.

## Predictions (probability we give each)

All shares are of comparable 2017 to 2025 reports.

- **P1 (65%):** at least 97% pass PHMSA's rule for mains, grand total against the Section 4 sum.
- **P2 (75%):** at least 97% pass for mains, grand total against the Section 1 total.
- **P3 (80%):** at least 97% pass for mains, cell sum against the grand total.
- **P4 (60%):** at least 95% pass for services, grand total against the Section 4 sum.
- **P5 (65%):** in at least 90% of discriminating reports for mains, the plastic-group total passes against Section 1's plastic value (PUDL's `pvc` label fits). If fewer than 100 reports are discriminating, there is nothing to test, and P5 counts as failed.
- **P6 (65%):** in at most 10% of discriminating reports for mains, the `pvc` total alone passes against Section 1's plastic value. If fewer than 100 reports are discriminating, there is nothing to test, and P6 counts as failed.
- **P7 (70%):** at least 95% pass for mains, the Section 2 steel total against the sum of Section 1's steel kinds.
- **P8 (55%):** of the reports that fail for mains (grand total against the Section 4 sum) and have a Section 1 total, at least 60% pass grand total against the Section 1 total (Sections 1 and 2 agree; Section 4 is the odd one out). If fewer than 10 such reports fail, there is nothing to test, and P8 counts as failed.

Reported, not scored:

- By report year: reports in each table; for mains and services, each comparison's comparable and passing counts, the cell sum against the Section 4 sum, and the plastic test's comparable, discriminating, plastic-group passing and `pvc`-alone passing counts.
- By era, group and kind: comparable and passing counts of Section 2/3 group totals against Section 1.
- Rows with a blank size that carry a value, and `plastic` size-total rows, by era.
- **Files:** counts by year; group counts; every report and kind that fails a grand-total or cell-sum comparison (up to 3,000 rows), with both totals, the cell sum and the Section 4 sum; and every discriminating report of the plastic test (up to 3,000 rows).

## What happens with the result

A result page `docs/phb23.md` in this repository, with every number checked by a test against the job's output, whatever it shows. MV2 will then post the counts once in the PUDL repository, after the result page is live and on a UTC day with no other post from him there: on pudl#4646 together with phrecon-1's counts if both are ready, or on its own otherwise. If the `pvc` total alone matches Section 1's plastic in most discriminating reports (so P5 and P6 both fail that way), the post will point to the column map lines as a possible mislabel, with the counts. He will not open a pull request unless a maintainer asks (MV2 has one PUDL community task open, on pudl#5154). A failed bar is reported as failed, with its cause, and is not re-scored.

## Limits

- This measures PUDL's published tables, not PHMSA's raw files, and cannot see which raw column a row came from. The column map was read through a fetch tool, not by a person.
- A report missing from one table counts as one-sided, not as a failure. Reports are matched on report_id and operator id within a year.
- PHMSA's rule names Section 4 as the baseline. The Section 1 baseline for Section 2/3 comparisons, and the grand total as baseline for the cell sum, are our choice. Near 60 the choice of baseline can move a borderline report.
- The plastic test only says which of two sums fits Section 1. It cannot rule out a third explanation, such as an operator entering only PVC in Section 1.
- PUDL's nightly tables change from night to night; the md5 and Last-Modified are recorded.
- The probabilities are our own before-the-fact guesses.

The job (`phb23-v1`, 1 CPU, 2 GB) waits until this plan is live on the main branch, then downloads `tools/phb23/` from it and runs it, within a 240-minute limit. It will be filed once one of MV2's three PHMSA jobs already in the queue (phsize-1, phdecade-1, phrecon-1) has finished, so this plan is public before any of these data are read.
