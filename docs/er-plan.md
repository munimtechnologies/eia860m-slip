# Were the annual EIA-860's plan-only generators already in its early release?

Status: scored against its pre-registration ([`er-plan-preregistration.md`](er-plan-preregistration.md)). All checks passed; 0 of 3 predictions held. On the terms fixed in advance that means R2 (revision) for most: none of the capacity EIA-860M first listed in its July and August reports was in the annual file's early release, yet the final release planned all of it for the year. A route the pre-registration did not consider, an annual filing that reached EIA after the early release was compiled, gives the same result, so this settles that the annual file gained this capacity during the year, not which form brought it in (see below). MV2 of Munim, Inc. (made with AI agents). CC BY 4.0.

## What this is

The twenty-sixth result ([`entry-timing.md`](entry-timing.md)) followed the annual EIA-860's plan-only generators for a year Y (set A: generators the annual file for report year Y - 1 plans for Y, missing from January's EIA-860M, first listed in EIA-860M after January). They enter EIA-860M about evenly from the February to the August report and then stop, at about the time of the annual file's final release in September of Y. That result could not separate R1 (lag: the annual filing for Y - 1 already held the project, and EIA-860M listed it only after EIA took the filing in) from R2 (revision: the annual record was added or revised during Y, after the project had appeared elsewhere). This note scores the follow-up pre-registered to separate them. For plan years 2022-2025 it reads two dated copies of each annual file from Catalyst Cooperative's raw EIA-860 archive on Zenodo: the early release, archived by PUDL in June to August of Y, before EIA-860M's July report came out, and the final release. It asks how much of A's capacity first listed in the July or August report (A late) was already in the early release's plan for Y. A's capacity first listed in the February or March report (A early) is the comparison.

Data: job `erplan-v1` (sealed container, 2 CPUs, 6 GB, 21 October 2026) fetched erplan.py 0.1.0 and test_erplan.py from commit b73dc6a, the commit that published the pre-registration, ran the unit tests, then the tool. It read the twenty-sixth result's sets unchanged from `data/entrytime_sets.csv` at commit c7eca74 and the eight Zenodo copies listed in the pre-registration, each checked against Zenodo's size and MD5 checksum. The headers-only structure report ([`erplan-structure-v1-output.md`](erplan-structure-v1-output.md), commit 3abc8fd) was public before this run started. Raw output: [`erplan-v1-output.md`](erplan-v1-output.md), [`../data/erplan_v1.json`](../data/erplan_v1.json); every generator of the three sets for 2022-2025 with its class in both copies (3,120 rows, one per generator, year and set): [`../data/erplan_rows.csv`](../data/erplan_rows.csv); unit tests: [`erplan-v1-unittests.txt`](erplan-v1-unittests.txt). Shares are MW shares, shown to four decimals as the job wrote them.

## What we found

**No prediction held.** Pooled over 2022-2025, A late holds 9,721.8 MW. Its share in the early release's plan for Y is 0.0000, against P1's floor of 0.70, and none of it is in the early release on any sheet. That is so in every year: all 4 years have at least 100 MW of A late, and 0 of 4 reach 0.70 (P2). A early, 10,955.0 MW, is 0.9753 in the early release's plan for Y and 0.9997 in the early release on some sheet, so A early's share minus A late's is 0.9753, against P3's ceiling of 0.20. The final release plans 0.9999 of A's MW for Y (check F2), and all of A late.

**What the pre-registration said this would mean.** In its words: "A late's share at most 0.30: most of it was not in the annual data's plan for Y until after EIA-860M listed it. R2 for most of it." A late is not on the early release's Proposed sheet under another year either (0.0 MW), so on those terms it is R2 in the sense of a record added, not a planned year revised.

**The later the first listing, the less the early release held (description only).** These readings were made after the run and change no verdict. The early release's plan share falls with the span of first EIA-860M listing: 0.9753 for the February-March reports, 0.4946 for April-June (13,713.5 MW), 0.0000 for July-August, and 0.0068 for September-December or after Y (643.5 MW). A_built, the part of A that came online in Y, follows the same order: 0.9996, 0.5523 and 0.0000 for the first three spans. The April-June share differs a lot between years, from 0.1766 in 2022 to 0.8716 in 2025. In 2023, 262.5 MW of A early was on the early release's Proposed sheet with another planned year.

**What that means for R1 and R2, and what it does not settle.** The pre-registration asked whether each prediction could hold under the rival reading. It did not ask whether P1 could fail under R1, and it can. The early release holds what EIA had of the annual filings when the release was compiled; its sheets say "The data has not been fully edited". If a respondent's annual filing for Y - 1 reached EIA, or was entered, after that, the project is missing from the early release and present in the final release, and EIA-860M can list it once the filing is in. That is R1's route with a late filing, and these data cannot tell it from R2, where the project reached EIA first through EIA-860M or another form and the annual record followed. What the data do settle is narrower. The capacity at issue was not in the annual data by the early release. The final release added it, in the same stretch of the year in which EIA-860M first listed it. So the annual file's plan for Y as finally published in September is not a plan fixed before Y: for set A it holds 17,171.8 MW (of 35,033.8 MW, 2022-2025) that the early release of the same file did not hold on any sheet. We claim no more than that.

**For anyone using the annual EIA-860's planned generators:** the final release's Proposed sheet for the current year includes capacity added during that year. For a plan known earlier in the year, read the early release, which comes out in early summer; neither copy is a plan fixed before the year began. This is an association in two dated copies of one survey and the monthly survey's records, not a cause.

**A check value to explain.** Check F3, the share of the final release's Operable generators found in the early release, came out 0.9977 in all four years. Four equal values to four decimals is unusual, and we have not yet found why. F3 passed whatever the reason, and a second control in the same run argues against keys that fail to match: A early, matched with the same keys against the same early-release copies, was found in them at 0.9997. A descriptive follow-up job reports the counts behind F3 in each year (see Next).

## Checks (all passed)

| check | result |
|---|---|
| D1, D2, E1 | all 8 copies passed; plan years 2022-2025 scored |
| C1 | A 55,263.5, A_built 36,998.4, B 32,937.3 MW; A July-August 13,082.3 MW |
| F1 | 0.9999 (floor 0.95) |
| F2 | 0.9999 (floor 0.90) |
| F3 | 2022 0.9977, 2023 0.9977, 2024 0.9977, 2025 0.9977 (floor 0.95) |
| unit tests | 22 of 22 passed |

C1's totals are pooled over 2018-2025, as in the twenty-sixth result; everything else is pooled over 2022-2025.

## Predictions (0 of 3 held)

| prediction | stated before the run | result | verdict |
|---|---|---|---|
| P1 | A late's share in the early release's plan for Y is at least 0.70 | 0.0000 | failed |
| P2 | A late's share is at least 0.70 in at least 3 of the plan years with at least 100 MW of A late | 0 of 4 years | failed |
| P3 | A early's share minus A late's share is at most 0.20 | 0.9753 - 0.0000 = 0.9753 | failed |

Shares are of MW, pooled over 2022-2025, all technologies.

## Set A by span of first EIA-860M listing, pooled 2022-2025

| span | reports | MW | in the early release's plan for Y | in the early release at all | absent from the early release (MW) | in the final release's plan for Y |
|---|---|---|---|---|---|---|
| early | February-March | 10,955.0 | 0.9753 | 0.9997 | 3.0 | 0.9997 |
| mid | April-June | 13,713.5 | 0.4946 | 0.5036 | 6,807.9 | 1.0000 |
| late | July-August | 9,721.8 | 0.0000 | 0.0000 | 9,721.8 | 1.0000 |
| edge | September-December or after Y | 643.5 | 0.0068 | 0.0068 | 639.1 | 1.0000 |
| all | February-December or after Y | 35,033.8 | 0.4987 | 0.5099 | 17,171.8 | 0.9999 |

No generator of A is on the early release's Operable or Retired and Canceled sheet. A month is the month of the EIA-860M report, not of its release.

## Share in the early release's plan for Y, set A, by year

| year | early | mid | late | late MW | all |
|---|---|---|---|---|---|
| 2022 | 1.0000 | 0.1766 | 0.0000 | 2,001.5 | 0.3587 |
| 2023 | 0.9230 | 0.3908 | 0.0000 | 2,272.3 | 0.4868 |
| 2024 | 0.9983 | 0.5326 | 0.0000 | 3,542.6 | 0.4743 |
| 2025 | 0.9987 | 0.8716 | 0.0000 | 1,905.4 | 0.6883 |

Every group by technology, A_built and B are in the raw output, with the 15 largest late generators of A not in the early release's plan.

## Limits

As in the pre-registration: a Zenodo date is when PUDL archived a copy, not when EIA released it; only four plan years have an early-release copy; matching is by plant id and generator id only (trimmed, any case), so a project re-keyed between the two copies counts as absent from the early release; MW come from PUDL's tables, summed over generators, so a few large projects can dominate a year. The test separates the annual data holding a project before EIA-860M listed it from the reverse only if the early release holds every annual filing EIA had received. Found after the run: a filing that reached EIA after the early release was compiled would also be absent from it, so P1 can fail under R1, and this result does not tell such a late filing from R2. F3's four equal values are not yet explained. The readings by span beyond A early and A late, by year, for A_built and of A early's 2023 capacity under another year were all made from the raw output after the run.

## Prior art

Searched 21 October 2026. PUDL's documentation describes EIA's two rounds of annual EIA-860 data, an early release in the summer and a final release in the fall, and PUDL's notes on taking in a final release mention generator records that changed from the early release. We found no public measurement of how much of the annual file's planned capacity for the current year the final release adds over the early release, or of how that depends on when EIA-860M first lists a generator. This note gives both for 2022-2025, with the checks and predictions fixed in advance.

## Next

- A descriptive follow-up job (`erdetail-v1`, not pre-registered) reports the counts behind F3 in each year, the early release's plan share by single report month from February to August, and, for A's generators missing from the early release, the MW whose plant has another generator in the early release (a new unit at a known plant, not a new plant).
- Our earlier notes that read PUDL's final annual tables as the annual plan for a year include this in-year capacity. Each will get a dated pointer to this result.
- Telling a late annual filing from R2 would need the date each filing reached EIA, which EIA does not publish as far as we know. This line of tests stops here unless such a source turns up.
