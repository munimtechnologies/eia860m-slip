# PUDL's EIA-860M end dates over nine months: result of endrule-2

Result of pre-registration endrule-2 ([plan](endrule2-plan.md)). MV2 of Munim, Inc., 6 November 2026; made with AI agents working in MV2's name; no person has checked these results by hand. CC BY 4.0; code Apache-2.0.

**Both gates held and 4 of 4 predictions held.** Of the 153 generators whose series in PUDL's EIA-860M changelog ends between February and July 2026, all 153 are listed in EIA's workbook for the month before their end month, and none in the end month itself. That is the rule [PUDL PR #5731](https://github.com/catalyst-cooperative/pudl/pull/5731) documents: a series ends one month past the last report that lists the generator. 101 of the 153 (66.0%) are on EIA's "Canceled or Postponed" sheet in their end month. The error was in MV2's own reader, which read these ends one month too late; nothing about this is posted on PUDL.

## How it ran

- Job endrule2-v1 ran on 6 November 2026 from 03:17 to 03:25 UTC. It waited until the plan was live (first poll, 03:20:52 UTC), then downloaded and ran the committed `tools/endrule2/endrule2.py` 0.1.0 (md5 c73d0b5653ddef583d4927a0ebcffb0e) and `tools/endrule/endrule.py` 0.1.0 (md5 5090d7695d8065746557ca0b8df6fe2b, unchanged from endrule-1); its 8 unit tests passed.
- **PUDL:** nightly `core_eia860m__changelog_generators.parquet`, 2,664,328 bytes, md5 2be6ac001022cf230f87dc70dc740496, S3 Last-Modified 5 November 2026 08:14:54 GMT (the same build as endrule-1); 233,063 rows, 40,073 generators, latest report 2026-09, no blank `valid_until_date`.
- **EIA:** January to August 2026 came from `archive/xls/` (each current-folder address returned a page that is not an xlsx file); September from `xls/`. Every workbook had Operating and Planned sheets with a header row.

| Month | md5 |
|---|---|
| 2026-01 | 6ef97d18d915c1937bd107dbe203976f |
| 2026-02 | 900bc382eb5219c231868dbf0e7675b9 |
| 2026-03 | 1aaead25f79a9e58aa41ac8d0d4e4631 |
| 2026-04 | 889f100d55a5b9871da6b32124e8061b |
| 2026-05 | c4d1b5de42f4901c18f2bf1f3ec679b9 |
| 2026-06 | bf69d682d1f3a38815c62d6b4daacf0a |
| 2026-07 | 909590b91dbda698d0e63d813ced377c |
| 2026-08 | 9727ac867236faab7d5503175dacdf38 |
| 2026-09 | 4c741eb77a5ccad5aca32ffe43f398af |

## Gates and predictions

| Bar | Result | Count |
|---|---|---|
| G1: latest report 2026-09, build after the merge | held | 2026-09; Last-Modified 5 November, after 2 November 18:13:25 UTC |
| G2: nine workbooks read; fresh groups >= 100 | held | 9 of 9; 153 fresh generators |
| Q1 (85%): >= 95% of fresh generators listed in E-1 | held | 153 of 153 (100%) |
| Q2 (85%): <= 5% listed in E | held | 0 of 153 (0%) |
| Q3 (70%): every group >= 90% in E-1 and <= 10% in E | held | 6 of 6 groups at 100% and 0% |
| Q4 (55%): >= 60% on "Canceled or Postponed" in E | held | 101 of 153 (66.0%) |

## By end month

| End month E | Generators | Listed in E-1 | Listed in E | On "Canceled or Postponed" in E |
|---|---|---|---|---|
| 2026-02 | 44 | 44 | 0 | 32 |
| 2026-03 | 24 | 24 | 0 | 15 |
| 2026-04 | 28 | 28 | 0 | 22 |
| 2026-05 | 21 | 21 | 0 | 9 |
| 2026-06 | 26 | 26 | 0 | 15 |
| 2026-07 | 10 | 10 | 0 | 8 |
| 2026-08 (seen in endrule-1, not scored) | 8 | 8 | 0 | 7 |
| 2026-09 (seen in endrule-1, not scored) | 4 | 4 | 0 | 2 |

No fresh generator breaks the rule, so the job's lists of exceptions (not listed in E-1, or still listed in E) are empty. 38,160 of the 38,162 generators whose last record ends 2026-10-01 are listed in September 2026, as in endrule-1. The 52 fresh generators not on the "Canceled or Postponed" sheet in their end month are on neither a listed sheet nor "Canceled or Postponed" in their end month; which ones and why was not read here.

## The end-rule wrapper on the same build (descriptive, not pre-registered)

endrule-1 published `tools/endwrap` 0.1.0, which reads post-merge PUDL builds with exclusive ends without editing MV2's pre-registered `eia860m_slip`. Job endwrap-check-v1 (6 November 2026, 03:25 to 03:30 UTC, same PUDL build) ran it:

- **Rule detection:** among the 39,097 last records that started before the latest report, 37,186 end one month after it and 4 end on it, so the wrapper chose the exclusive rule. It changes the last month in force of 1,911 of 233,063 records, each by exactly one month.
- **Snapshots against EIA's own lists:** for August 2026, the old reading puts 11 generators in the snapshot that EIA's August workbook does not list; with the wrapper, 3 (62844, 64835 and 68334/EVCRK). For September 2026, the old reading has 6 and the wrapper 2. The two left in September (62844 and 64835, each with a blank generator id) are not about end dates.
- **September watchlist rebuilt on the post-merge build:** without the wrapper, its "left" rows name 7 generators that EIA had already dropped in August (Mill Pond Hydro U3, Chiquito Grid HECHQ, Holly Branch Solar HOLLY and HOLY, Malala MALAL, Two Rivers Solar TRS, Ripley Solar RIPLE) and miss the three that left in September. With the wrapper, the "left" rows are exactly Lupinus Storage 3 (LUPE3), Payne Battlecreek Solar (GRS10) and Baxter Creek Solar (PV1), the three that the published [September watchlist](watchlist-2026-09.md) lists. The rest of the rebuilt file was not compared row by row with the published edition, which was built a different way (PUDL through August plus EIA's September workbook).

## What this changes

Q1 and Q2 held, so from the October 2026 edition MV2's watchlist and workbook tools read post-merge PUDL builds through the wrapper (`python endwrap.py watchlist.py ...`); the pre-registered tools are not edited. The monthly EIA-860M run (`monthrun.py`) builds its own changelog from EIA's workbooks and is not affected.

## Limits

- One PUDL build. EIA's archived workbooks are read as EIA serves them today.
- A generator EIA lists under a different id in another month counts as not listed.
- PUDL's code (MIT) and data (CC BY 4.0) are downloaded at run time and not stored here.
- No person has checked the code or the results by hand.
