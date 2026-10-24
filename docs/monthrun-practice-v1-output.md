# monthrun 0.1.0: EIA-860M 2026-09

Pre-registration: docs/oct2026-plan.md. Mode: practice (the month is in the published changelog). MV2 of Munim, Inc. (made with AI agents).

## Files

Archive replayed through 2026-07 (133 months; not readable: none).

| month | url | bytes | md5 | archive md5 | same as archive | readable | keys | rows appended | events | errors and problems |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-08 | https://www.eia.gov/electricity/data/eia860m/archive/xls/august_generator2026.xlsx | 13955142 | 9727ac867236faab7d5503175dacdf38 | 9727ac867236faab7d5503175dacdf38 | True | True | 38011 | 474 | back 3, changed 402, first 60, left 9 | none |
| 2026-09 | https://www.eia.gov/electricity/data/eia860m/xls/september_generator2026.xlsx | 14013970 | 4c741eb77a5ccad5aca32ffe43f398af | - | - | True | 38162 | 646 | back 1, changed 455, first 170, left 20 | https://www.eia.gov/electricity/data/eia860m/archive/xls/september_generator2026.xlsx: not an xlsx file (first bytes b'<!doctype html>\r') |

## C0: rebuilt changelog against the published copy

Published: https://raw.githubusercontent.com/munimtechnologies/eia860m-slip/a3ce0851c47d820ba5f8a0556358b4abef960909/data/eia860m_changelog_from_workbooks.csv.gz (1054060 bytes, md5 4fb178fbed7052b9e6618b481cab94f8). Same text through 2026-09: True. Lines: published 117757, rebuilt 117757. First difference: none.

Rebuilt rows, all months: 117756 (eia860m_changelog_from_workbooks.csv.gz).

## Predictions

| id | outcome | value | bar |
|---|---|---|---|
| P1 | held | listed 38162 vs 38011 in 2026-08 (+0.40%); readable True | readable; listed within 3% of the month before |
| P2 | held | 20 left | at most 50 |
| P3 | failed | 16 left from Retired | fewer than 10 |
| P4 | held | 0.3353 (57 of 170) | 0.2195 to 0.4740 (2024-09 to 2026-08) |
| P5 | held | 0 rows | no row on any sheet, plant id or not, nuclear and retired before 2002 |

Held: 4 of 5 scored.

## S3 (docs/sepretired-plan.md)

Of the 16 generators that left the Retired sheet in September 2026, listed in 2026-09: 0 (none). Bar: at most 3. held.

## Nuclear rows retired before 2002, every sheet, plant id or not

| month | source | nuclear rows | retired before 2002 | also on a Retired sheet with no year |
|---|---|---|---|---|
| 2026-08 | EIA's site | 156 | 28 | 0 |
| 2026-09 | EIA's site | 128 | 0 | 0 |

## The 2026-09 next-month cohort

Generators that the month before listed on the Planned sheet with planned operating month 2026-09: 170 (13854.0 MW); listed as operating in 2026-09: 57. Still planned for a later month: 106.

| where now | generators | MW |
|---|---|---|
| Operating | 57 | 4403.3 |
| Planned | 112 | 9420.7 |
| Retired | 0 | 0.0 |
| other | 0 | 0.0 |
| absent | 1 | 30.0 |

### By technology group and listing (reported, not scored)

Technology from 2026-08's file (EIA's site); cohort generators it does not list: 0. first: in a next-month cohort for the first time since July 2015; repeat: in an earlier month's cohort too.

| technology | listing | cohort | operating | share |
|---|---|---|---|---|
| solar | first | 41 | 16 | 0.3902 |
| solar | repeat | 68 | 21 | 0.3088 |
| solar | all | 109 | 37 | 0.3394 |
| batteries | first | 16 | 6 | 0.3750 |
| batteries | repeat | 27 | 9 | 0.3333 |
| batteries | all | 43 | 15 | 0.3488 |
| gas | repeat | 7 | 1 | 0.1429 |
| gas | all | 7 | 1 | 0.1429 |
| wind | first | 4 | 4 | 1.0000 |
| wind | repeat | 1 | 0 | 0.0000 |
| wind | all | 5 | 4 | 0.8000 |
| other | repeat | 6 | 0 | 0.0000 |
| other | all | 6 | 0 | 0.0000 |
| all | first | 61 | 26 | 0.4262 |
| all | repeat | 109 | 31 | 0.2844 |
| all | all | 170 | 57 | 0.3353 |

## Practice check against the published numbers

| item | expected | got | same |
|---|---|---|---|
| listed | 38162 | 38162 | True |
| listed_before | 38011 | 38011 | True |
| left | 20 | 20 | True |
| left_retired | 16 | 16 | True |
| cohort | 170 | 170 | True |
| operating | 57 | 57 | True |
| held | [True, True, False, True] | [True, True, False, True] | True |
| p5 | 0 | 0 | True |
| p5_before | 28 | 28 | True |
| s3 | 0 | 0 | True |

All the same: True.
