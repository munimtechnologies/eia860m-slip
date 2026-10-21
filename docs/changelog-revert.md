# PUDL's EIA-860M changelog drops a value that comes back (twenty-eighth result)

Status: scored against its pre-registration ([`changelog-revert-preregistration.md`](changelog-revert-preregistration.md), id changelog-revert-28); all checks passed and 4 of 4 predictions held. Scored 21 October 2026. MV2 of Munim, Inc. (made with AI agents). CC BY 4.0.

## In short

Catalyst Cooperative's PUDL publishes a monthly changelog of EIA-860M generator records (`core_eia860m__changelog_generators`). It is built by `pudl.helpers.make_changelog`, which keeps a monthly record only if no earlier record of the same generator has the same values. So when a generator's values change and later come back (A, B, A), the second A is dropped and B stays in force. The pre-registered test found this in the published file and in every month of 2026:

- The published changelog has no two records of a generator that are equal in every column but the dates (0 of 224,408 rows). A changelog that compared each record only with the one before it would have such pairs wherever a value came back.
- In 2,395 of 299,999 generator-months (January to August 2026) EIA's own workbook and PUDL's record in force disagree on status, planned month or MW. A simulation of make_changelog's rule on those three fields, started from PUDL's own records before 2026 and fed EIA's 2026 workbooks, gives PUDL's value in all 2,395.
- In August 2026 that is 301 generators, 16,574.2 MW by the workbook. 251 of them are operating in EIA's workbook and out of service, on standby or retired in PUDL (17 retired). For 82 the PUDL record in force was reported before 2020, the earliest in 2017.

The rule is still on PUDL's main branch (read 21 October 2026). A one-line change fixes it: compare each record with the previous record of the same generator (for example keep a row where any column differs from the row before it within the generator), instead of dropping duplicates across the generator's whole history.

## Run

Compete job `revert-v1` (sealed container, Python 3.12, 21 October 2026) ran revert.py 0.1.0, which passed 16 of 16 unit tests ([`revert-v1-unittests.txt`](revert-v1-unittests.txt)). Its gate saw the pre-registration live on GitHub at its first check (21:35:21 UTC, commit f64de4c) before reading any data. Its last step confirmed that the copies of revert.py, test_revert.py and keyhist.py it ran are byte for byte the published ones ([`revert-v1-md5.txt`](revert-v1-md5.txt)). Raw output, unchanged: [`revert-v1-output.md`](revert-v1-output.md), [`../data/revert_v1.json`](../data/revert_v1.json), and the August list as [`../data/revert_v1_august.csv`](../data/revert_v1_august.csv).

Data: PUDL's nightly `core_eia860m__changelog_generators.parquet` (2,631,992 bytes, file time 15 October 2026, latest report 2026-08), and EIA's eight 2026 EIA-860M workbooks from PUDL's archive copy (Zenodo record 22995197, md5 380a9824a20be96d182fea793c299e91).

## Checks

| check | result |
|---|---|
| C1 archive md5 and all eight months read | passed |
| C2 PUDL's latest report 2026-08 or later | passed (2026-08) |
| C3 D and S each at least 100 generator-months | passed (D 2,395, S 2,893) |
| unit tests in the sealed job | passed (16 of 16) |

## Predictions

| prediction | bar | value | held |
|---|---|---|---|
| P1 records repeated in the changelog | 0 | 0 of 224,408 rows (32 columns compared) | yes |
| P2 coverage (hits / D) | at least 0.90 | 1.0 (2,395 of 2,395) | yes |
| P3 precision (hits / S) | at least 0.50 | 0.8279 (2,395 of 2,893) | yes |
| P4 LEAKY and KNOXS held their value before 2026 | both | 69338/LEAKY matches its 2025-10 record, 69372/KNOXS its 2025-12 record | yes |

By the outcome map set before the run: P1 and P2 hold, so the published file follows the rule and the rule accounts for every 2026 disagreement found. P3 holding means the three-field simulation over-predicts by 498 generator-months (2,893 less 2,395). The pre-registered reading of that gap is that a returning value often comes back with some other column changed, so PUDL keeps it; the job did not check which columns.

## How big

Every month of 2026 has between 273 and 316 such generator-months, out of 36,865 to 37,995 generators in both sources. None of the disagreements fell in the other classes the job counted (PUDL takes the workbook's value in a later report, PUDL held it before, or other).

By the first field that differs: status in 2,245 generator-months, MW in 84 and planned month in 66. In 1,986 of them EIA's workbook says operating (OP) and PUDL says out of service (OA or OS), on standby (SB) or retired (RE).

Examples from the August list (all in [`../data/revert_v1_august.csv`](../data/revert_v1_august.csv)):

- 55098/GEN1, GEN2 and GEN3 (529 MW together) are operating in EIA's August 2026 workbook and have disagreed with PUDL in every month since January 2026; PUDL's record in force, which shows them retired, was reported in April 2022.
- 2828/1, 2828/2 and 2828/3 (1,880.4 MW together) are operating in EIA's August 2026 workbook and have disagreed with PUDL since January 2026; PUDL's record in force, which shows them out of service (OS), was reported in February 2024.
- 6481/1 and 6481/2 (820 MW each) are on the Retired sheet of EIA's August 2026 workbook and have disagreed with PUDL since July 2026; PUDL's record in force, from March 2026, shows them out of service (OS).

## What it does not show

- It tests 2026 only. Stale values from returns before 2026 are counted only where they last into 2026; how far back the effect goes in PUDL's history is not measured here.
- P2 is strongest where the returning value is unusual. For status, the returning value is usually OP, which almost every generator held at some point, so a different cause of a missed return to OP would also count as a hit. P1 is the direct test of the rule; P2 measures how much of the gap the rule can account for.
- The simulation compares three fields; PUDL compares every column. P3 measures that gap.
- 16 generators on the August 2026 workbook's Retired sheet (8,663.1 MW) have no PUDL record at all and are in no earlier 2026 workbook. That is a separate matter, not explained by this rule (descriptive only).
- The copy of PUDL read is the nightly build of 15 October 2026. A later fix in PUDL would not change this result for that copy.

## What it means for this repository

Every earlier eia860m-slip result reads PUDL's changelog, so some of their generator-months carry stale values like these. How many is not yet counted. The next step is a descriptive job that counts them, followed by a dated note. No earlier result is changed by this document. It also explains the release-day route's shortfall ([`workbook-route.md`](workbook-route.md)): the 0.98 bar compared a workbook edition with PUDL, and the gap was PUDL's stale values, not the workbook route. The bar is not changed.

We found no PUDL issue about this (GitHub search of the repository, 21 October 2026). A short issue with a minimal A, B, A example and the one-line fix has been drafted for the PUDL maintainers.
