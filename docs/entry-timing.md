# In which month do the annual EIA-860's plan-only projects enter EIA-860M?

Status: scored against its pre-registration ([`entry-timing-preregistration.md`](entry-timing-preregistration.md)). All checks passed; 5 of 5 predictions held. On the terms fixed in advance that is what R1 (lag) predicts, but a pattern read after the run, an edge at the annual file's final release rather than a peak after its filing deadline, fits R2 (revision) at least as well, so this result does not separate the two (see below). MV2 of Munim, Inc. (made with AI agents). CC BY 4.0.

## What this is

The twentieth result ([`annual-flows-eia860-entry.md`](annual-flows-eia860-entry.md)) found that most of the annual EIA-860's annual-only capacity for a year (generators the annual survey plans for year Y that January's EIA-860M plan for Y does not hold) was first listed in EIA-860M during Y, after January. Its correction of 20 October 2026 left two readings open. R1 (lag): the annual filing for Y - 1, due early in Y, already held the project, and EIA-860M listed it only after EIA took the filing in. R2 (revision): the annual record was added or revised during Y, before the final release, after the project had appeared elsewhere. This note scores the follow-up pre-registered to separate them. For each year Y it takes three sets of generators: A, the annual-only generators of Y first listed in EIA-860M after January; A_built, Y's EIA-860M new entries (came online in Y, not listed in January's report) that are in Y's annual plan; and B (the control), Y's new entries that are not. Each generator's MW goes to the month of Y of its first EIA-860M report. The statistic is the share of a set's February-December MW first listed in the March-June reports.

Data: PUDL's EIA-860M changelog (reports to 2026-08) and PUDL's `out_eia__yearly_generators` (report years 2001-2026). Job `entrytime-v1` (sealed container, 2 CPUs, 4 GB) fetched eia860m_slip.py (commit 329b7e6), annual860.py (c55b3c2), baseline860.py (7699d00) and entry860.py (44de204), and entrytime.py and test_entrytime.py from commit 77ee232, the commit that published the pre-registration. It ran the unit tests, then the tool, on 21 October 2026. Raw output: [`entrytime-v1-output.md`](entrytime-v1-output.md), [`../data/entrytime_v1.json`](../data/entrytime_v1.json); every generator in the three sets with its first listing month (7,494 rows, one per generator, year and set): [`../data/entrytime_sets.csv`](../data/entrytime_sets.csv); unit tests: [`entrytime-v1-unittests.txt`](entrytime-v1-unittests.txt). Shares are MW shares, shown to four decimals as the job wrote them; the table by year shows three, as the raw output does.

## What we found

**All five predictions held.** Pooled over 2018-2025, A holds 55,263.5 MW. Of its February-December MW, 0.5608 was first listed in the March-June reports, against a floor of 0.50 (P1; an even spread over the 11 months would give 0.364), and 0.0111 in the October-December reports, against a ceiling of 0.10 (P5). B's March-June share is 0.0472, so A's exceeds it by 0.5136 (P2), and A's share is above B's in 8 of the 8 years (P3). A_built, built in the same year as B, has 0.5799, 0.5327 above B's (P4). For 2017, which is description only, A's share is 0.5493, inside the 0.50-0.83 range its published quarters allowed.

**What the pre-registration said this would mean.** In its words: "If P1, P2 and P4 hold, the annual-only projects enter EIA-860M in the months after the annual filing is due, more than comparable projects the annual survey did not plan, which is what R1 predicts." All three held, so on the terms fixed in advance the result is what R1 predicts.

**What we saw after the run: an edge, not a peak.** These readings were made after the run. They were not pre-registered and they change no verdict. A does not peak after the filing deadline. Its largest month is February (10,548.5 MW), and its March-June share of the February-August MW is 0.5673, close to the 0.5714 (4 of 7) an even spread over those seven months would give. Then it stops: 0.9885 of A's February-December MW was first listed by the August report. B is the mirror image: 0.8787 of its February-December MW was first listed in the September-December reports. Of the year's new entries (A_built and B together), 0.9468 of the MW first listed in February-August is in the annual plan, against 0.0278 of the MW first listed in September-December. EIA publishes each EIA-860M report three to four weeks after its month ends, so the August report comes out at about the time of the annual file's final release in September of Y (dates in the pre-registration).

**What that means for R1 and R2.** Three things weaken the reading fixed in advance, and the pre-registration foresaw none of them. First, P1's yardstick was an even spread over February-December, but the pre-registration expected few entries after the final release under both readings (P5). Against an even spread over February-August, 0.5714, A's March-June share of its February-August MW, 0.5673, is slightly below it. So P1 held because of the edge, not because of a peak after the filing deadline. Second, entry spread across the year and cut off at the final release is the shape the pre-registration gave for R2 ("cut off before the September final release"). Third, suppose EIA adds generators that EIA-860M has listed to the annual file until that file is final. Then every new entry first listed before the edge ends up in the annual plan, B can hold only those first listed after it, and P2 and P4 hold under R2 as well. R1 can produce an edge too, if EIA has taken in every annual filing by late summer. What R1 alone does not explain is why the annual plan's share of the new entries drops from 0.9468 to 0.0278 at the edge instead of falling through the year. So the predictions held as stated and the result is consistent with R1, but it does not separate R1 from R2, and the pattern read after the run fits R2 at least as well. We claim no more than that, and the twentieth result's correction stands as written. Telling the two apart needs a dated copy of the annual file from before its final release, such as EIA's early release of the annual data.

**About half of B entered EIA-860M only after its year (description only).** 0.4856 of B's MW (15,992.8 of 32,937.3 MW) was first listed in a report after the year in which it came online, so EIA-860M first listed that capacity, already built, in a later year. As fixed in advance, the shares above leave it out: they are shares of February-December MW. A has 17.7 MW first listed after its year.

**By technology (description only).** Solar (A 0.5933, B 0.0426) and onshore wind (A 0.5784, B 0.0000) follow the pooled pattern, and so do batteries (A 0.4759, B 0.0000). Gas combustion turbines differ: B's March-June share is 0.3803, from 489.6 MW first listed in May reports, against A's 0.4767. Gas combined cycle A (417.5 MW) is too small to read.

**For anyone using EIA-860M's lists of planned generators:** a generator that the annual EIA-860 plans for a year but January's EIA-860M lacks usually turns up between the February and August reports, and nearly all such capacity that enters EIA-860M during the year does so by the August report (0.9885). Capacity that came online in a year without being in that year's annual plan was mostly first listed in the September-December reports or later. This is an association in two surveys' records, not a cause.

## Checks (all passed)

| check | result |
|---|---|
| U1 | all 9 years 2017-2025 match the twentieth result; 2018: A 4,666.4, A_built 3,828.4, B 2,307.5 MW |
| U2 | 0 groups not adding up |
| U3 | 0 year-set rows over the limit |
| unit tests | 15 of 15 passed |

## Predictions (5 of 5 held)

| prediction | stated before the run | result | verdict |
|---|---|---|---|
| P1 | A's March-June share is at least 0.50 | 0.5608 | held |
| P2 | A's March-June share exceeds B's by at least 0.10 | 0.5608 vs 0.0472 (difference 0.5136) | held |
| P3 | A's March-June share exceeds B's in at least 6 of the 8 years 2018-2025 | 8 of 8 years | held |
| P4 | A_built's March-June share exceeds B's by at least 0.10 | 0.5799 vs 0.0472 (difference 0.5327) | held |
| P5 | A's October-December share is at most 0.10 | 0.0111 | held |

Shares are of February-December MW, pooled over 2018-2025, all technologies.

## First EIA-860M listing by report month, pooled 2018-2025, all technologies (MW)

| set | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec | after the year | total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A | 10,548.5 | 8,947.0 | 9,861.8 | 7,913.7 | 4,259.2 | 8,253.0 | 4,829.3 | 17.5 | 99.0 | 221.0 | 295.8 | 17.7 | 55,263.5 |
| A_built | 7,076.0 | 5,821.2 | 7,301.7 | 5,737.0 | 2,586.8 | 5,407.2 | 2,624.6 | 17.5 | 99.0 | 16.0 | 293.7 | 17.7 | 36,998.4 |
| B | 385.0 | 150.0 | 6.0 | 635.6 | 8.2 | 236.0 | 634.2 | 5,724.3 | 4,750.7 | 1,375.5 | 3,039.0 | 15,992.8 | 32,937.3 |

No set has MW first listed before its year or in January, and none is unlisted (check U3). A month is the month of the report, not of its release.

## March-June share by year, all technologies

| year | A | A_built | B |
|---|---|---|---|
| 2017 (description only) | 0.549 | 0.596 | 0.000 |
| 2018 | 0.622 | 0.580 | 0.003 |
| 2019 | 0.392 | 0.461 | 0.144 |
| 2020 | 0.557 | 0.470 | 0.135 |
| 2021 | 0.761 | 0.729 | 0.001 |
| 2022 | 0.484 | 0.602 | 0.000 |
| 2023 | 0.604 | 0.696 | 0.090 |
| 2024 | 0.507 | 0.530 | 0.003 |
| 2025 | 0.548 | 0.544 | 0.019 |

## Pooled 2018-2025 by technology (description only)

| group | A MW | A March-June | A_built MW | A_built March-June | B MW | B March-June |
|---|---|---|---|---|---|---|
| solar | 22,221.3 | 0.5933 | 16,510.9 | 0.6384 | 15,253.7 | 0.0426 |
| wind_onshore | 18,386.7 | 0.5784 | 10,810.6 | 0.5893 | 5,350.7 | 0.0000 |
| battery | 12,317.4 | 0.4759 | 7,881.8 | 0.4570 | 4,759.8 | 0.0000 |
| gas_ct | 1,088.0 | 0.4767 | 696.9 | 0.3867 | 3,529.7 | 0.3803 |
| gas_cc | 417.5 | 1.0000 | 417.5 | 1.0000 | 2,296.2 | 0.0000 |

## Limits

As in the pre-registration: a report month is not a release date; a contrast with B is evidence, not proof, and R1 and R2 can both hold for different projects; matching is by key only (trimmed, any case), so a project re-keyed between surveys can sit in the wrong set; a generator's first listing is its first record in PUDL's changelog, which starts with the July 2015 report; MW are summed over generators, so a few large projects can dominate a year. Found after the run: P1's yardstick (an even spread over February-December) did not allow for the edge that the pre-registration itself expected under both readings, and P2 and P4 can hold under R2 if the annual file takes in EIA-860M's listings until it is final. The readings of the edge, the annual plan's share of the new entries by month, B's capacity first listed after its year and the comparisons by technology were all made from the raw output after the run.

## Prior art

Searched 21 October 2026. EIA's retrospectives compare the capacity planned in the annual EIA-860 with what came online, and EIA describes EIA-860M as a monthly supplement to the annual survey that sometimes uses annual data before it is fully verified. We found no public analysis of the month in which EIA-860M first lists the annual survey's planned generators, or of how much of a year's new capacity the annual plan holds by month of first EIA-860M listing. This note gives both, with the checks and predictions fixed in advance.

## Next

A test that can separate R1 from R2 needs a copy of the annual file dated before its final release. If archived early-release copies of the annual EIA-860 can be found, a follow-up will be pre-registered before any of them is read: under R1, A's generators first listed in the July and August reports should already be in the early release; under R2, many should not.

Addendum, 21 October 2026: that follow-up was found, pre-registered ([`er-plan-preregistration.md`](er-plan-preregistration.md)) and scored ([`er-plan.md`](er-plan.md)) for plan years 2022-2025. None of A's capacity first listed in the July and August reports was in the early release, on any sheet, though the final release planned all of it for the year: R2 for most, on the pre-registration's terms. A late annual filing, which the pre-registration did not consider, would give the same result, so that note settles that the annual file gained this capacity during the year, not which form brought it in. This note's verdicts are unchanged.
