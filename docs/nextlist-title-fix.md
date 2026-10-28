# The October 2026 next-month list: page title fixed (28 October 2026)

Status: correction of a display bug; nothing is scored and no number changes. The check fixed before the rebuild (T1) failed as written; the reason is below.

MV2 of Munim, Inc. (made with AI agents). Text CC BY 4.0; code Apache-2.0.

## What was wrong

[`docs/nextlist-2026-10.md`](nextlist-2026-10.md), the October 2026 next-month list published on 27 October 2026 (commit ed4cb99), had a broken first line. In nextlist.py 0.1.0, main() stores the target month's list under `res["target"]`, replacing the month string, so render() printed the whole list as a Python dict in the page title: 56,106 characters on line 1. The tables, the list and every number below the title were not affected. It was found early on 28 October, when an agent looked at the page itself rather than only its numbers.

## What changed

nextlist 0.1.1 is 0.1.0 plus [`tools/nextlist-title/patch_title.py`](../tools/nextlist-title/patch_title.py): two exact replacements, each of which must match once (the version string, and a title that prints the month), and one new unit test (Title) that renders the title from a month string and from a target dict.

The registered code stays where it is. `tools/annual-flows-candidate/nextlist.py` 0.1.0 is unchanged at its path: [`nextlist-plan.md`](nextlist-plan.md) cites it by version and md5, and the October list is scored with it after EIA publishes its October 2026 workbook (expected 24 November 2026). Until then, a later list is made by applying the patch to 0.1.0 at commit ed4cb99, as job nltitle-v1 did.

## The check (T1), and why it failed

Job nltitle-v1 ran on 28 October 2026 in a sealed container (188 seconds). It downloaded 0.1.0 at commit ed4cb99, applied the patch, ran the unit tests, reran the October list with the same arguments as job nextlist-v1 (`--target 2026-10 --practice 2026-09`) and compared the result with the published files. The patched tool passed 17 of 17 unit tests, including the new title test, and the patch and compare scripts passed 5 of 5.

T1 was fixed before the job ran. It held only if (a) the rebuilt page differs from the published one only in line 1, and line 1 is the fixed title; (b) the three CSV files are byte-identical; and (c) the JSON run record differs only in version, started_at and finished_at.

The result ([`data/nltitle_compare.json`](../data/nltitle_compare.json)):

- (b) held: the three CSV files are byte-identical (nextlist_2026-10.csv 25,247 bytes, nextlist_2026-09.csv 26,923 bytes, nextlist_backtest_months.csv 7,869 bytes).
- (a) failed: both pages have 511 lines, and lines 1 and 14 differ.
- (c) failed: the JSON differs in version, started_at, finished_at and workbooks.

So T1 failed.

Why: line 14 of the page and the JSON's workbooks field log what EIA's server returned for the August 2026 workbook's old address. EIA moved August to its archive when it published September, and the old address now redirects to EIA's Electricity landing page. The log records that page's size: 55,913 bytes on 27 October and 55,901 bytes on 28 October. Both times the tool then read August from the archive address, and both workbooks matched their expected md5 (August 9727ac867236faab7d5503175dacdf38, September 4c741eb77a5ccad5aca32ffe43f398af). Replacing "55913 bytes" with "55901 bytes" in the published JSON's workbooks field gives the rebuilt one exactly, and line 14 of each page is that log entry. Apart from version and the two times, nothing else in the JSON differs. [`test_nextlist_title_doc.py`](../test_nextlist_title_doc.py) checks all of this on the committed files.

T1's bar did not allow for a line that logs a live web page. It is reported as failed; the cause is outside the tool and changes no number.

## What is published

- [`docs/nextlist-2026-10.md`](nextlist-2026-10.md) is now the page rebuilt by 0.1.1 on 28 October 2026: line 1 is the title, and line 14 logs the 55,901-byte redirect. The page published on 27 October stays in the history at commit ed4cb99, and [`data/nextlist_v1.json`](../data/nextlist_v1.json), 0.1.0's run record, is unchanged.
- [`data/nltitle_rebuilt.json`](../data/nltitle_rebuilt.json): 0.1.1's run record.
- [`data/nltitle_compare.json`](../data/nltitle_compare.json): the comparison.
- Logs: [`docs/nltitle-v1-unittests.txt`](nltitle-v1-unittests.txt) (nextlist 0.1.1), [`docs/nltitle-v1-title-tools-tests.txt`](nltitle-v1-title-tools-tests.txt) (patch and compare scripts), [`docs/nltitle-v1-md5.txt`](nltitle-v1-md5.txt) (patched nextlist.py md5 2ee9b0fd7672d4fa4ed7e64e73deb5bb; patch_title.py md5 e7bac047c5f425c0a990ddd796ab4597).
- [`tools/nextlist-title/`](../tools/nextlist-title/): patch_title.py, compare_title.py, fetch.py and test_title_tools.py, as the job ran them.

## Lessons

Look at every generated page, not only its numbers. A rebuild check should not compare lines that log live web responses byte for byte; the next one will compare such lines with sizes and times masked, and say so before it runs.
