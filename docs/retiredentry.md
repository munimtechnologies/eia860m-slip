# EIA-860M's August 2026 Retired sheet added 28 nuclear reactors retired from 1963 to 1998, and September's removed all of them

Status: scored against its pre-registration ([`docs/retiredentry-plan.md`](retiredentry-plan.md), commit d5e9181, fixed before job retiredentry-v1 read the history of these generators): 3 of 4 predictions held. R4 failed: August 2026's workbook has 28 such rows, not 16. Every number below is checked against the job's raw output by the doc test [`test_retiredentry_doc.py`](../test_retiredentry_doc.py).

Made by MV2 of Munim, Inc. with AI agents working in his name. Text and data: CC BY 4.0. Job retiredentry-v1 (23 October 2026) ran [`tools/annual-flows-candidate/retiredentry.py`](../tools/annual-flows-candidate/retiredentry.py) 0.1.0 (Apache-2.0) unchanged, after its 11 unit tests passed ([`retiredentry-v1-unittests.txt`](retiredentry-v1-unittests.txt)). Raw output: [`docs/retiredentry-v1-output.md`](retiredentry-v1-output.md) and the job's log [`docs/retiredentry-v1-stdout.txt`](retiredentry-v1-stdout.txt). Data: [`data/retiredentry_keys.csv`](../data/retiredentry_keys.csv), [`data/retiredentry_log_rows.csv`](../data/retiredentry_log_rows.csv) and [`data/retiredentry_nuclear.csv`](../data/retiredentry_nuclear.csv).

## Order of events

The plan was committed at 20:37:10 UTC on 23 October 2026. The job started at 21:03:51 UTC, was served the plan on its first poll at 21:05:41 UTC, and only then downloaded the changelog and read any workbook. It read the rebuilt changelog at commit a3ce085 (1,054,060 bytes, 117,756 rows, the expected file), EIA-860M July and August 2026 from PUDL's raw archive, and EIA's own September 2026 file (14,013,970 bytes, md5 4c741eb77a5ccad5aca32ffe43f398af, the same file monthcheck-sep2026-v1 read).

## The bars

| bar | outcome | value |
|---|---|---|
| R1. All 16 first reach the Retired sheet in one and the same workbook month | held | 16 of 16, all in August 2026 |
| R2. Each has, in that month, the retirement year August 2026 gives it | held | 16 of 16 |
| R3. Each stays on the Retired sheet every month from arrival to August 2026 | held | 16 of 16 |
| R4. Exactly 16 nuclear rows retired before 2002 on all sheets of the August 2026 workbook | failed | 28 |

R1 to R3 held in the simplest way. By the changelog, none of the 16 was listed in any workbook from July 2015 to July 2026 on any sheet the changelog reads. Each first appears in August 2026, on the Retired sheet, with the retirement year and MW it had there, and leaves in September 2026. Each has exactly two changelog rows: "first" in August 2026 and "left" in September 2026. So R3 had only one month to test and says little.

## R4: 28 rows, not 16

August 2026's workbook has 28 rows whose technology is nuclear and whose retirement year is before 2002, all on the Retired sheet. 16 are the generators above, with plant IDs. The other 12 have no plant ID, so the sheet reader behind the changelog, which needs a plant ID and a generator ID, never saw them. Together the 28 are 10,446.1 MW of nameplate capacity as the sheet gives it: 8,663.1 MW with plant IDs and 1,783.0 MW without. Their retirement years run from 1963 to 1998.

The 12 rows without a plant ID, as August's sheet gives them (generator 1 in every case):

| plant | retirement year | MW |
|---|---|---|
| Bonus | 1968 | 18 |
| CVTR | 1967 | 19 |
| Elk River | 1968 | 24 |
| Fort St. Vrain | 1989 | 342 |
| Hallam | 1964 | 84 |
| Indian Point 1 | 1974 | 277 |
| Pathfinder | 1967 | 63 |
| Piqua | 1966 | 12 |
| Saxton | 1972 | 3 |
| Shippingport | 1982 | 68 |
| Shoreham | 1989 | 849 |
| Vallecitos Nuclear Center | 1963 | 24 |

The 16 with plant IDs are listed in [`docs/sepretired.md`](sepretired.md). Three of their plant names on August's Retired rows differ from the names that note's table gives: Three Mile Island (plant 8011, given there as Crane Clean Energy Center), Dresden (869, Dresden Generating Station) and Genoa (Lacrosse) (4143, Genoa). The plant IDs and every other number are the same.

## Month by month

| month | nuclear rows on the Retired sheet | of them retired before 2002 | generators on the Retired sheet (with plant IDs) |
|---|---|---|---|
| July 2026 | 11 | 0 | 7,299, all retired 2002 or later |
| August 2026 | 39 | 28 | 7,324: 7,308 retired 2002 or later and 16 before 2002 |
| September 2026 | 11 | 0 | 7,321, all retired 2002 or later |

The 11 nuclear rows of July and September are the same reactors in both months, all retired from 2013 to 2021 (from San Onofre 2 and 3 to Indian Point 3). August's sheet has those 11 and the 28. September's has the 11 and none of the 28: no nuclear row retired before 2002 is on any sheet of it, with or without a plant ID.

## What was already known, and what is new

After the job ran we found that Catalyst Cooperative had already documented the August addition, and we missed that when we wrote the plan. The plan said "No EIA source we found says this". We had not searched PUDL's documentation and issue tracker. PUDL's EIA-860 data source page (release 2026.10.0, section "Notable Irregularities") says that "In August 2026, the EIA confirmed through email communication that they added data from their nuclear shutdown list to the retired generators tab of the EIA-860M data release", and that "Some of these reactors did not contain plant or utility IDs". PUDL's issue #5677 (opened 28 September 2026, closed 2 October 2026) says these records "are not found in prior months of the spreadsheet", speaks of "a few dozen records" with no entity or plant ID, and records that PUDL drops them as out of scope. So the reason for the August addition (EIA's nuclear shutdown list) and the fact that the rows were new are Catalyst Cooperative's findings, not ours. R1 confirms the second for the 16 rows that have plant IDs.

What we did not find stated anywhere on 23 October 2026, in EIA's EIA-860M page, PUDL's pages or a web search:

- **The exact count.** 28 nuclear rows retired before 2002 (16 with plant IDs, 12 without), 10,446.1 MW. A third-party website says August's file "for the first time lists 21 historically retired reactors"; the workbook has 28 such rows. We do not know how the site counted.
- **The removal.** EIA's September 2026 workbook, published 23 October 2026, has none of the 28. Its Retired sheet is back to generators retired since 2002, the scope EIA's page gives for it, and its nuclear rows are the same 11 as July's. EIA's page carries no note about the addition or the removal.

For a user, then: a count of retired capacity taken from August 2026's file alone includes 10,446.1 MW of reactors retired before 2002 that the files before and after it leave out. A tool that follows the files month to month sees 16 generators (or 28 rows) appear and leave within one month. That is how this repository first saw them: as a failed bar (P3 of [`docs/sep2026.md`](sep2026.md)).

## Limits

- The scan counts rows whose technology column says nuclear. A reactor listed under another technology name would be missed, and so would any other row without a plant ID. PUDL's issue speaks of "a few dozen" records with no entity or plant ID; we did not read utility IDs, so we cannot say how its count relates to ours.
- Two of the three months are from PUDL's archive (md5-checked) and one from EIA's own site. A month read again by the same reader is a reproducibility check, not an independent one.
- Nothing here says why EIA removed the rows in September. EIA's page says estimates "will be corrected without specific acknowledgment or explanation in subsequent month's inventory".
- Whether any of the 16 come back is bar S3 of [`docs/sepretired-plan.md`](sepretired-plan.md), scored on EIA's October 2026 workbook (EIA's page gives 24 November 2026 as the next release).
- No person has opened the workbooks by hand to confirm these rows.

## Sources

- PUDL, EIA Form 860 data source page, "Notable Irregularities": https://docs.catalyst.coop/pudl/en/stable/data_sources/eia860.html
- PUDL issue #5677, "Integrate August 2026 860M data": https://github.com/catalyst-cooperative/pudl/issues/5677
- EIA, Preliminary Monthly Electric Generator Inventory (EIA-860M): https://www.eia.gov/electricity/data/eia860m/
