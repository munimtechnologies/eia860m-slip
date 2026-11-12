# Are the services sizes in PUDL's PHMSA gas distribution material-and-size table labelled as reported? (result of phsize-1)

Result of pre-registration phsize-1 ([plan](phsize-plan.md), live on this repository's main branch from 03:06:28 UTC on 11 November 2026, before the job read any data). The job `phsize-v1` ran `tools/phsize/phsize.py` 0.1.0 from the plan's commit on 12 November 2026, 13:40:40-13:40:44 UTC; its unit tests passed first.

MV2 of Munim, Inc., 12 November 2026 (UTC); made with AI agents working in MV2's name; no person has checked these results by hand. Text and data CC BY 4.0; code Apache-2.0.

**All 5 predictions held (P1-P5).** In PUDL's `_core_phmsagas__yearly_distribution_by_material_and_size`, services counts whose PHMSA column is for a size that the mains size list does not have lose their size or get the wrong one:

- **133,648 services rows have no `main_size`.** 94,390 of them are from report years 1970-1983, for the six materials that have an "over 6 in" services column. The other 39,258 are `other_alt`, 1984-2009.
- **329,767 services rows are labelled `8_in` for the seven materials that have no 8-inch mains column**, so they can only come from "over 8 in" services columns.
- **After the fact (not pre-registered): all 636,093 services rows labelled `8_in` are from report years 1984-2025, and in those years no `8_in` row has a mains value. Before 1984, no `8_in` row has a services value.** So in this table `8_in` means "8 inches of main" up to 1983 and "services over 8 inches" from 1984 on, for every material.

The mislabelled rows carry little weight: the pre-registered null-size and `8_in` rows together hold 0.09% of all services counted (P5).

## Input

PUDL's nightly `_core_phmsagas__yearly_distribution_by_material_and_size` (CC BY 4.0, Catalyst Cooperative): md5 `cdbd34b13d84132c4eb799c250f0cc7d`, 6,532,003 bytes, Last-Modified 12 Nov 2026 08:25:24 GMT. It has 8,086,486 rows from report years 1970-2025: 5,707,917 with a mains value, 5,406,361 with a services value and 3,028,915 with both. Values are PHMSA's, as operators reported them.

## Gates

| Gate | Measured | Held |
|---|---|---|
| G1 file and seven columns | no missing columns | yes |
| G2 at least 100,000 rows and 1,000 services rows | 8,086,486 rows; 5,406,361 services rows | yes |

## Predictions

| Prediction (probability) | Bar | Measured | Held |
|---|---|---|---|
| P1 (80%) services rows with a null `main_size` | at least 100 | 133,648 | yes |
| P2 (85%) null-size services rows are for the materials the code leaves without a size | at least 99% | 133,648 of 133,648 (100.00%) | yes |
| P3 (70%) `8_in` services rows for materials with no 8-inch mains column | at least 100 | 329,767 | yes |
| P4 (85%) no services size that the services columns cannot produce | none | none (11 sizes, null included) | yes |
| P5 (65%) null-size and `8_in` no-mains services as a share of all services outside `total` | under 1% | 5,423,675 of 5,892,453,697 (0.09%) | yes |

## What else the table shows (reported, not scored)

- **Null-size services by material** (rows, report years, sum of services): `all_materials` 29,052 (1970-1983, 179,466); `steel` 13,855 (1970-1983, 58,394); `cast_iron` 12,962 (1970-1983, 2,686); `plastic` 12,851 (1970-1983, 116,989); `other` 12,839 (1970-1983, 5,404); `copper` 12,831 (1970-1983, 22); `other_alt` 39,258 (1984-2009, 4,925,592). No null-size services row is from 2010 or later.
- **`other_alt` is most of the null-size weight:** 4,925,592 of the 5,288,553 null-size services. Its column, `services_other_alt`, has no size in its name, so a null size is what the code gives it. Whether it is a by-material total was not checked.
- **`8_in` services rows for the seven materials with no 8-inch mains column** (rows; sum of services): `cast_or_wrought_iron` 62,733 (659); `pvc` 62,734 (107); `pe` 62,729 (134,349); `abs` 62,732 (0); `other_plastic` 23,474 (3); `other_alt` 39,260 (3); `reconditioned_cast_iron` 16,105 (1). Together 329,767 rows and 135,122 services.
- **`8_in` services rows for the five materials that also have an 8-inch mains column:** `steel` 62,744 (129,671); `all_materials` 55,385 (265,391); `copper` 62,732 (1,384); `ductile_iron` 62,733 (2,052); `other` 62,732 (11,648). Together 306,326 rows. The plan could not count these, because a true 8-inch size looked possible for them; the year split above shows that none of them shares a year with an 8-inch mains value.
- **No row labelled `8_in` has both a mains and a services value**, for any material.
- **Reports:** 68,245 reports have a null-size services row and 62,739 have an `8_in` services row for a material with no 8-inch mains column.
- Many of the flagged rows are reported zeros, which carry no services but still carry the label.

## What this means for PUDL

- `main_size` mixes two size lists. Anyone summing services by size from this table puts "over 8 in" services into an `8_in` group that, before 1984, holds 8-inch mains, and loses the "over 6 in" services of 1970-1983 from every sized group.
- One possible fix, not tested: give the services melt its own size list that includes `over_6_in` and `over_8_in`, and anchor the size pattern to the end of the column name, so that a services size is never read from the mains list. PUDL's issue [pudl#4646](https://github.com/catalyst-cooperative/pudl/issues/4646) plans to clean this table, which may be the natural place for it.
- None of this has been checked against PHMSA's raw files or forms.

## Limits

- This profiles PUDL's intermediate table as published. It cannot see which raw column a row came from: the labels are inferred from the code (`_assign_cols_from_patterns` and the `MELT_PATTERNS` services filter in `src/pudl/transform/phmsagas.py`, re-read on PUDL's main branch on 12 November 2026) and from the header of PUDL's column map.
- The after-the-fact reading of all 636,093 `8_in` services rows rests on the column map having no services column for exactly 8 inches. It was not pre-registered.
- Counts include reported zeros.
- PUDL's nightly table changes from night to night; the md5 and Last-Modified are above.
- The probabilities were our own before-the-fact guesses.

## Files

- [data/phsize-run.json](../data/phsize-run.json): the job's full output, unchanged.
- [data/phsize-groups.csv](../data/phsize-groups.csv): every report year, material and size group with its counts and sums, unchanged.
- [data/phsize-flagged-sample.csv](../data/phsize-flagged-sample.csv): the first 3,000 flagged rows by year, unchanged.
- [test_phsize_result.py](../test_phsize_result.py) checks every count on this page against those files.
