# Were EIA-860M plans that "never came online" re-filed at the same plant under new generator ids?

Status: scored against its pre-registration ([`split-rekey-preregistration.md`](split-rekey-preregistration.md)). All checks passed; 10 of 10 links read as one project; 4 of 5 predictions held. MV2 of Munim, Inc. (made with AI agents). CC BY 4.0.

## What this is

Every eia860m-slip delivery rate follows a planned generator by its key, plant id plus generator id, so a plan that is re-filed under a new key reads as never online. Rule S was fixed in the pre-registration before any data was read. It finds plans that left EIA-860M without operating and came back at the same plant and fuel family under new generator ids. It links them when the capacities agree within 20%, and re-scores the old key's rows with the month the last new generator came online. Data: PUDL's EIA-860M changelog, reports to 2026-08. The rows are the same 0-12-month cohort rows as the first full run (78,646 rows, 4,550,498.4 MW summed over rows) and the same 0-24-month stage-by-lead rows as [`stage-leadtime.md`](stage-leadtime.md) (87,351 rows). Job `splitkey-v1` (4 GB) fetched eia860m_slip.py (commit 329b7e6), leadtime.py (commit 9ee085b), and splitkey.py and test_splitkey.py (commit 7bd3f30, the commit that published the pre-registration). It ran the unit tests, then the tool, on 20 October 2026. Raw output: [`splitkey-v1-output.md`](splitkey-v1-output.md), [`../data/splitkey_v1.json`](../data/splitkey_v1.json); unit tests: [`splitkey-v1-unittests.txt`](splitkey-v1-unittests.txt); records of the ten links read by hand: [`../data/splitkey_v1_handread.csv`](../data/splitkey_v1_handread.csv); the readings: [`../data/splitkey_v1_readings.csv`](../data/splitkey_v1_readings.csv). Shares are shown to four decimals, as the job wrote them, because most changes are in the third or fourth decimal.

## What we found

**Very little of the capacity scored "not online" was re-filed at the same plant under new ids.** The 0-12-month rows hold 871,839.9 MW of not-online rows. Rule S replaces 20,507.0 MW of it, a share of 0.0235. S1 put the share between 0.03 and 0.20; it failed, low. The failure does not hang on the rule's settings: bound B, which counts any later generator of the same family at the plant that came online, reaches 0.0252, and a capacity tolerance of 0.30 instead of 0.20 gives 0.0235. Over the whole changelog, rule S found 1,147 leavers (planned generators that left EIA-860M with no operating month under their key; 119,643.9 MW) in 873 clusters. Of these, 23 clusters link, holding 47 leavers, and 25 leavers (2,655.4 MW) have a replacement month. Bound B covers 45 leavers (5,496.1 MW): for 0.954 of the leavers' MW, no generator of the same fuel family first listed later at the same plant id had come online by the 2026-08 report.

**The published delivery rates stand.** Re-scoring moves the overall on-time share from 0.3247 to 0.3249 (S2 held) and the not-online share from 0.1916 to 0.1884, so most of the moved MW became late, not on time. No on-time share in the breakdowns below rises by more than 0.003 (the largest rise: approved, 13-24 months, 0.1762 to 0.1791), and all six stage-by-lead verdicts are unchanged (S5 held). The largest falls in a not-online share are U at 13-24 months (0.4621 to 0.4381), gas combined cycle (0.0991 to 0.0869) and U at 7-12 months (0.1844 to 0.1731). The pre-registration asked for dated caveats on earlier results only if S1 failed high. It failed low, so none are needed, and rule S stays a check rather than part of the scoring.

**Where it matters, it is a few large plants.** Three links carry 0.924 of the replaced MW. At South Field Energy (Ohio, plant 60356), one 1,105.0 MW combined-cycle key was re-filed as four generators, by their ids two combustion turbines (SFCT1, SFCT2) and two steam turbines (SFST1, SFST2), which came online in 2021-08 and 2021-10. At La Joya (New Mexico, plant 61044), one 306.2 MW wind key was re-filed as two phase keys. At Bacliff (Texas, plant 60264), six 71.2 MW combustion turbines were renumbered when the plant's name changed from Cielo Lindo. Gas combined cycle's whole replaced MW (9,945.0) is South Field's, and onshore wind's (5,590.0) is La Joya's. So S4 (gas CC's replaced share, 0.1232, above solar's, wind's and battery's) held on the strength of one plant. The U cell at 13-24 months has a replaced share of 0.0654, against 0.0235 overall (S3 held). Bacliff's turbines came online in 2018-07, 20 months after the old keys' last planned month, so their rows stay "not online" after re-scoring (gas CT's not-online share is 0.2629 before and after): a replacement is not an on-time delivery.

**The hand-reading passed: all ten largest links read as one project.** Each of the ten meets (a), (b) and (c) of the pre-registration (table below). A new key's first planned month is at most 13 months from the old keys' last planned month; old and new keys were listed side by side for at most 2 report months; and each change is a split, merge or renumbering of one plan. The least clear-cut is (c) at Hop Bottom and Bayles (Pennsylvania), where five 4.4 MW gas engines were re-filed as three 7.0 MW gas engines with the same technology description; we read that as one project changing its engines. Four of the ten (Tesla Reno GigaFactory, Holley Road Solar, Hop Bottom and Bayles) never came fully online under the new keys either. They are linked but have no replacement month, and their rows do not change.

**One link outside the ten does not read as a re-filing.** At Colby (Kansas, plant 1272), the 3.0 MW new key 3A was first listed in 2024-02 with an operating month of 2019-08, 55 months before the old key's last planned month (2024-03). It reads as an existing unit added to the list, not a re-filed plan, and would fail (a); rule S still credits the old key's rows as on time. They hold 42.0 MW of the 0-12-month not-online MW (less than 0.0001 of it) and 57.0 MW of the stage-by-lead rows. This reading is outside the pre-registered ten and is description only. For the other twelve links outside the ten, the link table shows the new keys' planned month within 3 months of the old keys' (their records were not read).

**For anyone reading EIA-860M's lists of planned generators:** the survey has no cancelled status, so a dropped plan just leaves the list. At the same plant id, leaving the list without operating almost never meant that the plan came back under new generator ids. A re-filing under a new plant id and new generator ids at once is not tested here.

## Checks (all passed)

| check | result |
|---|---|
| K1 | cohort 78,646 rows, 4,550,498.4 MW, on time 0.3247, not online 0.1916; cells U 00-03, U 13-24, V 00-03, V 13-24 match |
| K2 | 0 violations of the 6 conditions |
| K3 | cohort 78,646 rows, 82 changed, 0 stray; lead-time rows 87,351, 225 changed, 0 stray |
| unit tests | 12 of 12 passed |

## Hand-reading of the ten largest links (10 of 10 one project)

| rank | plant | name | (a) months | (b) months | change | one project | replacement month |
|---|---|---|---|---|---|---|---|
| 1 | 60356 | South Field Energy | 0 | 0 | one combined-cycle total unit re-filed as four generators (by their ids two combustion turbines and two steam turbines) | yes | 2021-10 |
| 2 | 61044 | La Joya NM | 0 | 2 | one wind key split into two phase keys | yes | 2021-06 |
| 3 | 60264 | Bacliff | 2 | 0 | six combustion turbines renumbered (CLGT to BCGT) after the plant name changed from Cielo Lindo to Bacliff | yes | 2018-07 |
| 4 | 60094 | Blythe Solar III, LLC | 7 | 1 | four solar block keys merged into one key | yes | 2020-05 |
| 5 | 60095 | Blythe Solar IV, LLC | 7 | 1 | four solar block keys re-filed as two phase keys | yes | 2020-11 |
| 6 | 64507 | OETN1 | 0 | 0 | one solar key renumbered to the plant's name | yes | 2023-03 |
| 7 | 64098 | Tesla Reno GigaFactory | 13 | 0 | one solar key split into seven section keys | yes | none |
| 8 | 64240 | Holley Road Solar | 0 | 0 | one solar key renumbered (#0879 to 879) | yes | none |
| 9 | 58800 | Hop Bottom | 3 | 2 | five gas engines re-filed as three larger gas engines of the same technology | yes | none |
| 10 | 58816 | Bayles | 6 | 2 | five gas engines re-filed as three larger gas engines of the same technology | yes | none |

The ten are the linked clusters with the most not-online MW in the 0-12-month rows, in that order. (a): the largest gap, in months, between a new key's first planned month and the old keys' last planned month (limit 24). (b): report months in which an old and a new key were both listed, counting each key from its first report to its last record's valid-until month (limit 6). (c) is the reading in the change column. Both counts are recomputed from the records file by `test_split_rekey_doc.py`; each reading's notes are in the readings file.

## Predictions (4 of 5 held)

| prediction | stated before the run | result | verdict |
|---|---|---|---|
| S1 | replaced share of not-online MW in the 0-12-month rows at least 0.03 and at most 0.20 | 0.0235 | failed |
| S2 | the overall 0-12-month on-time share rises by less than 0.02 | 0.3247 to 0.3249 (rise 0.0002) | held |
| S3 | the replaced share in U at 13-24 months is above the 0-12-month share | U 13-24 0.0654, cohort 0.0235 | held |
| S4 | gas CC's replaced share is above solar's, onshore wind's and battery's | gas_cc 0.1232; solar 0.0041; wind 0.0314; battery 0.0000 | held |
| S5 | each of L1-L6 keeps its verdict after re-scoring | 6 of 6 unchanged | held |

## Re-scored shares, 0-12-month rows (MW)

| part | rows | not online MW | replaced MW | replaced share | on time before | on time after | not online before | not online after |
|---|---|---|---|---|---|---|---|---|
| all | 78,646 | 871,839.9 | 20,507.0 | 0.0235 | 0.3247 | 0.3249 | 0.1916 | 0.1884 |
| solar | 45,802 | 366,047.2 | 1,510.4 | 0.0041 | 0.3088 | 0.3093 | 0.2082 | 0.2073 |
| wind_onshore | 7,104 | 177,849.8 | 5,590.0 | 0.0314 | 0.3893 | 0.3893 | 0.1715 | 0.1684 |
| gas_cc | 3,090 | 80,690.0 | 9,945.0 | 0.1232 | 0.3985 | 0.3985 | 0.0991 | 0.0869 |
| battery | 10,382 | 122,916.7 | 0.0 | 0.0000 | 0.2299 | 0.2299 | 0.2330 | 0.2330 |
| gas_ct | 3,126 | 67,953.2 | 3,417.6 | 0.0503 | 0.2401 | 0.2401 | 0.2629 | 0.2629 |
| approved | 8,691 | 110,033.3 | 1,233.8 | 0.0112 | 0.2186 | 0.2193 | 0.3729 | 0.3687 |
| construction | 47,440 | 380,219.9 | 19,246.2 | 0.0506 | 0.3566 | 0.3568 | 0.1168 | 0.1127 |
| other | 204 | 5,942.7 | 0.0 | 0.0000 | 0.3030 | 0.3030 | 0.5630 | 0.5630 |
| permitting | 7,467 | 132,288.9 | 0.0 | 0.0000 | 0.1279 | 0.1279 | 0.5298 | 0.5298 |
| planning | 5,939 | 181,809.4 | 21.0 | 0.0001 | 0.1532 | 0.1533 | 0.5766 | 0.5765 |
| testing | 8,905 | 61,545.7 | 6.0 | 0.0001 | 0.3974 | 0.3974 | 0.1447 | 0.1447 |

## Re-scored stage-by-lead cells, 0-24-month rows (MW)

| part | rows | not online MW | replaced MW | replaced share | on time before | on time after | not online before | not online after |
|---|---|---|---|---|---|---|---|---|
| early 00-03 | 875 | 10,459.3 | 0.0 | 0.0000 | 0.1316 | 0.1316 | 0.5654 | 0.5654 |
| early 04-06 | 2,728 | 35,069.7 | 3.0 | 0.0001 | 0.1395 | 0.1396 | 0.5452 | 0.5452 |
| early 07-12 | 7,593 | 187,690.0 | 18.0 | 0.0001 | 0.1577 | 0.1577 | 0.5243 | 0.5242 |
| early 13-24 | 17,387 | 1,311,151.7 | 1,073.4 | 0.0008 | 0.1247 | 0.1250 | 0.6992 | 0.6989 |
| approved 00-03 | 791 | 5,023.7 | 0.0 | 0.0000 | 0.2545 | 0.2545 | 0.4809 | 0.4809 |
| approved 04-06 | 1,999 | 12,801.5 | 0.0 | 0.0000 | 0.2254 | 0.2254 | 0.3541 | 0.3541 |
| approved 07-12 | 4,272 | 61,369.0 | 1,233.8 | 0.0201 | 0.2101 | 0.2112 | 0.3568 | 0.3496 |
| approved 13-24 | 6,665 | 340,002.5 | 3,995.2 | 0.0118 | 0.1762 | 0.1791 | 0.5391 | 0.5327 |
| U 00-03 | 5,131 | 22,232.8 | 166.0 | 0.0075 | 0.3017 | 0.3017 | 0.1165 | 0.1165 |
| U 04-06 | 5,316 | 44,900.9 | 1,542.9 | 0.0344 | 0.2848 | 0.2850 | 0.1441 | 0.1408 |
| U 07-12 | 6,247 | 119,775.1 | 9,072.3 | 0.0757 | 0.3220 | 0.3227 | 0.1844 | 0.1731 |
| U 13-24 | 4,138 | 294,236.1 | 19,254.0 | 0.0654 | 0.2457 | 0.2457 | 0.4621 | 0.4381 |
| V 00-03 | 11,795 | 36,237.6 | 4,030.0 | 0.1112 | 0.4088 | 0.4088 | 0.0578 | 0.0568 |
| V 04-06 | 3,599 | 26,518.6 | 3,315.0 | 0.1250 | 0.4253 | 0.4253 | 0.0743 | 0.0650 |
| V 07-12 | 1,901 | 43,201.3 | 1,105.0 | 0.0256 | 0.3683 | 0.3683 | 0.1336 | 0.1302 |
| V 13-24 | 315 | 16,824.7 | 0.0 | 0.0000 | 0.1389 | 0.1389 | 0.2948 | 0.2948 |

## Capacity tolerance (reported, never used to choose the rule)

| tolerance | linked clusters | replaced leavers | replaced share | on time after | not online after |
|---|---|---|---|---|---|
| 0.05 | 18 | 16 | 0.0106 | 0.3247 | 0.1908 |
| 0.10 | 21 | 21 | 0.0228 | 0.3248 | 0.1885 |
| 0.20 | 23 | 25 | 0.0235 | 0.3249 | 0.1884 |
| 0.30 | 25 | 28 | 0.0235 | 0.3249 | 0.1884 |

With a tolerance of 0.05 the share falls to 0.0106, mostly because South Field's new generators total 9.5% more than the old key (1,210.4 against 1,105.0 MW). Crediting the first new key's operating month instead of the last: on time 0.3249, not online 0.1883.

## Limits

As in the pre-registration: rule S is a heuristic. It can link a cancelled phase to a different phase built at the same plant (bound B shows how far that could go), and it misses re-filings outside its windows and tolerance. A re-filing under a new plant id and new generator ids at once is caught by neither rule R nor rule S. Leavers still listed in the last report are not considered, so a stale planned key kept beside its built replacement stays "not online". A replacement month scores whether the plant came, not whether the old key's plan was right. Rows are not independent, and three links carry most of the replaced MW. Not pre-registered: the share carried by the three largest links, the bound-B share of the leavers' MW, the largest-change rankings, the Colby reading and the planned-month check of the twelve other links were computed after the run from the raw output. (b) counts a key as listed from its first report to its last record's valid-until month; if that last valid-until month is not itself a listed month, every (b) count above is the same or one lower.

## Prior art

As in the pre-registration (searched 20 October 2026). PUDL keys EIA-860M generators by plant id and generator id, and its issue #3684 records one plant (1439) whose generator ids changed between EIA-860M and the annual EIA-860. We found no crosswalk for planned generators re-filed under new ids, and no estimate of how much planned capacity that "never came online" in EIA-860M was re-filed. This note gives one for same-plant re-filings, with its rule fixed in advance and its largest links read by hand.
