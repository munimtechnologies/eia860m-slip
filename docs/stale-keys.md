# What became of planned EIA-860M capacity scored "not online", and is any of it a stale key beside a built replacement?

Status: scored against its pre-registration ([`stale-keys-preregistration.md`](stale-keys-preregistration.md)). All checks passed; rule T linked no groups, so there were no links to read by hand; 5 of 5 predictions held, but only T1 tests something not already known (see below). MV2 of Munim, Inc. (made with AI agents). CC BY 4.0.

## What this is

Every eia860m-slip delivery rate follows a planned generator by its key, plant id plus generator id. A row is "not online" when its generator had not come online within 12 months of the planned month in that row. This note splits the not-online capacity by what became of each key by the last report, and tests rule T, fixed in the pre-registration before any data was read. Rule T looks for planned keys still listed as planned beside generators of the same plant and fuel family that were planned, first listed later and came online with about the same capacity (within 20%). Data: PUDL's EIA-860M changelog, reports to 2026-08. The rows are the same 0-12-month cohort rows as the first full run (78,646 rows, 4,550,498.4 MW summed over rows) and the same 0-24-month stage-by-lead rows as [`stage-leadtime.md`](stage-leadtime.md) (87,351 rows). Job `staykey-v1` (4 GB) fetched eia860m_slip.py (commit 329b7e6), leadtime.py (commit 9ee085b), splitkey.py (commit 7bd3f30), and staykey.py and test_staykey.py (commit eef7d45, the commit that published the pre-registration). It ran the unit tests, then the tool, on 21 October 2026. Raw output: [`staykey-v1-output.md`](staykey-v1-output.md), [`../data/staykey_v1.json`](../data/staykey_v1.json); unit tests: [`staykey-v1-unittests.txt`](staykey-v1-unittests.txt); the records file for the hand-reading, which has a header and no rows: [`../data/staykey_v1_handread.csv`](../data/staykey_v1_handread.csv). Shares are MW shares, with MW summed over rows as in every eia860m-slip note, shown to four decimals as the job wrote them.

## What we found

**Of the capacity scored "not online", more came online late than was dropped, and a quarter is still waiting.** The 0-12-month rows hold 871,839.9 MW of not-online rows. Of it, 0.4354 (379,559.0 MW) belongs to generators that came online more than 12 months after the row's planned month; 0.2615 (227,965.7 MW) to generators still listed as planned in the 2026-08 report; 0.3032 (264,315.2 MW) to generators that left EIA-860M without operating; and none to anything else. T1 put the still-listed share between 0.10 and 0.40; it held. So a planned generator that misses its month by more than a year is more often late than dropped, and for a quarter of that capacity the answer is not in yet.

**The split differs by technology and stage.** These comparisons were made after the run and are description only. Gas combined cycle's not-online MW is mostly plans that left the list (0.7750), and so is gas combustion turbines' (0.5706), while solar's is mostly delayed or still waiting (online later 0.4371, still listed 0.3892, left 0.1737). By stage at the report, the not-online MW of generators listed as testing (construction complete, not yet in commercial operation) is mostly still listed (0.6190), and that of generators under construction mostly came online later (0.5732), while about half of the planning-stage not-online MW left the list (0.5020). In the stage-by-lead cells, the share that left the list rises with lead time in the early, U and V cells (early 0.3175 to 0.5164, U 0.1331 to 0.4727, V 0.2346 to 0.6367, from 0-3 to 13-24 months), so the further ahead a plan was when it missed, the more often the miss was a dropped plan rather than a delay. The approved cells do not follow that pattern.

**Rule T found no stale keys.** The 2,307 stayers (287,881.0 MW in their last records) form 1,767 groups by plant and fuel family. None has a twin: at no group's plant did a generator of the same family that was planned and first listed after the group's first listing come online. Bound B, which drops the planned and capacity conditions, covers 1 stayer (1.0 MW in its last record; 55.6 MW of not-online rows, less than 0.001 of the not-online MW). So rule T replaces nothing at any tolerance from 0.05 to 0.30, and T2 and T3 held trivially: rule T's replaced share is zero, and the on-time share stays 0.3247.

**T4 and T5 rest on rule S alone and add nothing new.** With rule T crediting nothing, rules S and T together are rule S, and the shares are the twenty-fourth result's ([`split-rekey.md`](split-rekey.md)): on time 0.3249, not online 0.1884 (T4 held), and all six stage-by-lead verdicts unchanged (T5 held). The pre-registration said T5 was partly informed by that result; with no links, T4 was fixed by it as well. Of the five predictions, only T1 tested something not already known.

**The hand-reading had nothing to read.** The pre-registered gate (at least 7 of the 10 largest links read as one project) guards against over-linking. With no links rule T cannot over-link, and the records file is empty. We do not count this as a passed hand-reading.

**The published delivery rates stand.** Through the two kinds of re-keying tested so far (a plan that left and came back under new ids at the same plant, and a stale planned key kept beside a later-listed built generator), neither key rule moves the overall on-time share by more than 0.0002. Not tested: a stale key listed in the same month as its replacement (rule T and bound B both need the replacement to be first listed later, so a combined-cycle total-unit key listed beside its turbines in the same report would be missed), a replacement under a new plant id, and one in another fuel family.

**For anyone reading EIA-860M's lists of planned generators:** missing a planned month by more than a year is not the same as being cancelled. In these rows, more of that capacity came online late than left the list. For gas plants it mostly did mean the plan was dropped. This is an association in one survey's records, not a cause.

## Checks (all passed)

| check | result |
|---|---|
| K1 | cohort 78,646 rows, 4,550,498.4 MW, on time 0.3247, not online 0.1916; cells U 00-03, U 13-24, V 00-03, V 13-24 match |
| K2 | 0 violations of the 7 conditions |
| K3 | rule T: cohort 78,646 rows, 0 changed, 0 stray; lead-time rows 87,351, 0 changed, 0 stray; rules S and T: cohort 78,646 rows, 82 changed, 0 stray |
| unit tests | 9 of 9 passed |

## Predictions (5 of 5 held)

| prediction | stated before the run | result | verdict |
|---|---|---|---|
| T1 | stayers hold at least 0.10 and at most 0.40 of the not-online MW in the 0-12-month rows | 0.2615 | held |
| T2 | rule T's replaced share is below rule S's published 0.0235 | 0.0000 | held |
| T3 | rule T raises the overall 0-12-month on-time share by less than 0.01 | 0.3247 to 0.3247 (rise 0.0000) | held |
| T4 | after rules S and T together, the not-online share is at least 0.17 | 0.1916 to 0.1884 | held |
| T5 | each of L1-L6 keeps its verdict after rules S and T together | 6 of 6 unchanged | held |

## What became of the not-online capacity, 0-12-month rows (MW)

| part | rows | not online MW | online later | still listed | left the list | other | not online before | not online, rules S and T |
|---|---|---|---|---|---|---|---|---|
| all | 78,646 | 871,839.9 | 0.4354 | 0.2615 | 0.3032 | 0.0000 | 0.1916 | 0.1884 |
| solar | 45,802 | 366,047.2 | 0.4371 | 0.3892 | 0.1737 | 0.0000 | 0.2082 | 0.2073 |
| wind_onshore | 7,104 | 177,849.8 | 0.4806 | 0.2240 | 0.2953 | 0.0000 | 0.1715 | 0.1684 |
| gas_cc | 3,090 | 80,690.0 | 0.1862 | 0.0388 | 0.7750 | 0.0000 | 0.0991 | 0.0869 |
| battery | 10,382 | 122,916.7 | 0.4616 | 0.2903 | 0.2481 | 0.0000 | 0.2330 | 0.2330 |
| gas_ct | 3,126 | 67,953.2 | 0.4133 | 0.0161 | 0.5706 | 0.0000 | 0.2629 | 0.2629 |
| approved | 8,691 | 110,033.3 | 0.4127 | 0.3463 | 0.2410 | 0.0000 | 0.3729 | 0.3687 |
| construction | 47,440 | 380,219.9 | 0.5732 | 0.1759 | 0.2510 | 0.0000 | 0.1168 | 0.1127 |
| other | 204 | 5,942.7 | 0.0129 | 0.7249 | 0.2622 | 0.0000 | 0.5630 | 0.5630 |
| permitting | 7,467 | 132,288.9 | 0.3891 | 0.2499 | 0.3611 | 0.0000 | 0.5298 | 0.5298 |
| planning | 5,939 | 181,809.4 | 0.2366 | 0.2614 | 0.5020 | 0.0000 | 0.5766 | 0.5765 |
| testing | 8,905 | 61,545.7 | 0.3519 | 0.6190 | 0.0291 | 0.0000 | 0.1447 | 0.1447 |

"Online later": the key came online more than 12 months after the row's planned month. "Still listed": a stayer (planned, never operating, listed as planned in the 2026-08 report). "Left the list": a leaver as in [`split-rekey.md`](split-rekey.md). The last column is after rules S and T together, which here is rule S alone.

## What became of the not-online capacity, stage-by-lead cells, 0-24-month rows (MW)

| part | rows | not online MW | online later | still listed | left the list | other | not online before | not online, rules S and T |
|---|---|---|---|---|---|---|---|---|
| early 00-03 | 875 | 10,459.3 | 0.5133 | 0.1692 | 0.3175 | 0.0000 | 0.5654 | 0.5654 |
| early 04-06 | 2,728 | 35,069.7 | 0.4155 | 0.1441 | 0.4404 | 0.0000 | 0.5452 | 0.5452 |
| early 07-12 | 7,593 | 187,690.0 | 0.3584 | 0.1890 | 0.4526 | 0.0000 | 0.5243 | 0.5242 |
| early 13-24 | 17,387 | 1,311,151.7 | 0.2137 | 0.2699 | 0.5164 | 0.0000 | 0.6992 | 0.6989 |
| approved 00-03 | 791 | 5,023.7 | 0.2884 | 0.0073 | 0.7043 | 0.0000 | 0.4809 | 0.4809 |
| approved 04-06 | 1,999 | 12,801.5 | 0.5650 | 0.0914 | 0.3436 | 0.0000 | 0.3541 | 0.3541 |
| approved 07-12 | 4,272 | 61,369.0 | 0.4926 | 0.2495 | 0.2580 | 0.0000 | 0.3568 | 0.3496 |
| approved 13-24 | 6,665 | 340,002.5 | 0.2156 | 0.1883 | 0.5961 | 0.0000 | 0.5391 | 0.5327 |
| U 00-03 | 5,131 | 22,232.8 | 0.7938 | 0.0731 | 0.1331 | 0.0000 | 0.1165 | 0.1165 |
| U 04-06 | 5,316 | 44,900.9 | 0.7078 | 0.0672 | 0.2249 | 0.0000 | 0.1441 | 0.1408 |
| U 07-12 | 6,247 | 119,775.1 | 0.6105 | 0.0758 | 0.3137 | 0.0000 | 0.1844 | 0.1731 |
| U 13-24 | 4,138 | 294,236.1 | 0.3771 | 0.1501 | 0.4727 | 0.0000 | 0.4621 | 0.4381 |
| V 00-03 | 11,795 | 36,237.6 | 0.7072 | 0.0582 | 0.2346 | 0.0000 | 0.0578 | 0.0568 |
| V 04-06 | 3,599 | 26,518.6 | 0.4593 | 0.0840 | 0.4566 | 0.0000 | 0.0743 | 0.0650 |
| V 07-12 | 1,901 | 43,201.3 | 0.4573 | 0.0435 | 0.4992 | 0.0000 | 0.1336 | 0.1302 |
| V 13-24 | 315 | 16,824.7 | 0.3077 | 0.0556 | 0.6367 | 0.0000 | 0.2948 | 0.2948 |

## Capacity tolerance (reported, never used to choose the rule)

| tolerance | linked groups | replaced stayers | replaced share | on time after | not online after |
|---|---|---|---|---|---|
| 0.05 | 0 | 0 | 0.0000 | 0.3247 | 0.1916 |
| 0.10 | 0 | 0 | 0.0000 | 0.3247 | 0.1916 |
| 0.20 | 0 | 0 | 0.0000 | 0.3247 | 0.1916 |
| 0.30 | 0 | 0 | 0.0000 | 0.3247 | 0.1916 |

## Limits

As in the pre-registration: rule T is a heuristic; a stale key at another plant id or in another fuel family is not caught; a replacement month would score whether the plant came, not whether the key's plan was right. Rule T and bound B need a replacement to be first listed after the stayers' first listing, so a stale key listed in the same report as the generators that built it is not caught; this was stated in the rule, and its size is not known. "Still listed" is a snapshot of the 2026-08 report: a stayer may yet come online or leave, and rows planned close to the end of the data have had the least time to resolve, so the still-listed share is partly a measure of how recent the plans are. MW is summed over rows, so a generator counts once for every monthly report in which it was 0-12 (or 0-24) months from its planned month. Rows are not independent, and a few large plants can dominate a share. Not pre-registered: the comparisons by technology and stage, and the lead-time pattern in the share that left the list, were read from the raw output after the run.

## Prior art

As in the pre-registration (searched 21 October 2026). EIA's review of 2017 additions splits one year's planned capacity into came online, delayed and cancelled, for that year only. We found no public split of the EIA-860M capacity that missed its planned month by what became of each key over the whole changelog, by technology, stage and lead time, and no test for planned keys kept beside the generators that built them. This note gives both, with the rule and the checks fixed in advance.
