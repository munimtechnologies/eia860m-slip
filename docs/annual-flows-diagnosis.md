# Why the first annual-flows run failed two checks: the diagnosis

MV2 of Munim, Inc., 19 October 2026. Made with AI agents working in his name. CC BY 4.0.

Job `eia860m-slip-030-v1` (eia860m-slip 0.3.0 candidate) failed checks K2 and K3 of [`annual-flows-preregistration.md`](annual-flows-preregistration.md), so its run is description only ([`annual-flows-amendment.md`](annual-flows-amendment.md)). The diagnosis job `flows-diag-v3` (diag.py 0.1.2 in [`../tools/annual-flows-candidate/`](../tools/annual-flows-candidate/), importing eia860m_slip.py 0.3.0 unchanged; 7 unit tests passed) ran in a sealed container on 2026-10-19, 07:15-07:18Z, on the same PUDL file (reports to August 2026). Its full output is [`annual-flows-diag-output.md`](annual-flows-diag-output.md). Nothing here is scored.

## 1. K3: the whole difference is generators whose last record ends in that January

0.3.0 reads PUDL's `valid_until_date` as PUDL defines it: a record that another record follows ends the month before that record (exclusive); a generator's last record runs to the last report that lists it (inclusive). 0.2.0 read every end as exclusive. The diagnosis recomputed each year's January plan under both readings:

| year | 0.3.0 plan (MW) | 0.2.0's rule, recomputed | 0.2.0's published figure | only in 0.3.0 (MW, generators) |
|---|---:|---:|---:|---:|
| 2017 | 26,268.8 | 26,236.8 | 26,236.8 | 32.0 (4) |
| 2018 | 35,982.4 | 34,723.5 | 34,723.5 | 1,258.9 (14) |
| 2019 | 24,826.1 | 24,812.1 | 24,812.1 | 14.0 (3) |
| 2020 | 42,753.9 | 42,505.9 | 42,505.9 | 248.0 (8) |
| 2021 | 43,181.4 | 42,861.4 | 42,861.4 | 320.0 (4) |
| 2022 | 46,461.4 | 46,062.1 | 46,062.1 | 399.3 (6) |
| 2023 | 52,145.7 | 52,142.9 | 52,142.9 | 2.8 (1) |
| 2024 | 59,102.8 | 59,099.8 | 59,099.8 | 3.0 (1) |
| 2025 | 60,890.9 | 60,887.1 | 60,887.1 | 3.8 (3) |

- Applying 0.2.0's rule inside 0.3.0 reproduces 0.2.0's published January plans to 0.1 MW in all nine years. Nothing else in 0.3.0 changed the plans.
- Every generator that only 0.3.0 counts (44 in all) is one whose **last** record ends in that January: listed in the January report under 0.3.0's reading and never again. No generator is counted only under 0.2.0's rule.
- In 2018 the 1,258.9 MW is **TVA's Allen Combined Cycle Plant** (plant 60671: CTG1 347.0, CTG2 347.0, STG1 476.9 MW, under construction, planned for June 2018, last record March 2017 to January 2018), Aragonne Solar (40 MW) and ten North Carolina solar farms of 3-5 MW. Allen alone is 3.4% of the 2018 plan; K3's 1% bound did not allow for the fix it was testing.
- So the K3 failure is the rule change working as described, not an error, and the bound was wrong. The remaining question is whether these generators really were in the January report (PUDL's convention says so; see section 4).

## 2. The 2018 combined cycle did not come back under the same plant id

The amendment suspected that 3,141.5 MW of combined cycle dropped from the 2018 plan ("not listed" by February 2019) and 3,141.5 MW of combined cycle built in 2018 "new entry" were the same equipment under new generator ids. The diagnosis looked for plants with both a dropped generator and an unplanned entry:

| year | not listed (MW) | of it at a plant with an entry | new entry (MW) | of it at a plant with a dropped generator | plants |
|---|---:|---:|---:|---:|---:|
| 2017 | 425.3 | 34.0 | 4,626.7 | 20.0 | 1 |
| 2018 | 3,500.3 | 0.0 | 9,277.4 | 0.0 | 0 |
| 2019 | 799.0 | 0.5 | 4,027.4 | 0.5 | 1 |
| 2020 | 1,325.4 | 249.6 | 8,355.6 | 274.2 | 2 |
| 2021-2025 | 5,104.5 | 0.0 | 51,571.8 | 0.0 | 0 |

- **In 2018 no plant has both.** Over all nine years only 284 MW of the 11,154 MW dropped (2.5%) sits at a plant that also has an unplanned entry. If the 2018 combined cycle was re-keyed, its plant id changed too, which a same-plant test cannot see.
- Allen Combined Cycle is the natural case: TVA built it beside its Allen plants in Memphis and it entered service in April 2018, after its record under plant 60671 ends. A new job, `rekey-v1` (rekey.py 0.1.0, beside diag.py), pairs every dropped generator with an unplanned entry of the same technology group, the same capacity (within 0.05 MW; a looser pass allows 5%) and a first listing 0-3 months after the dropped generator's last month, across plant ids, and prints the pairs with both plant names and the 2018 raw records. Its output will say how much of the 11,154 MW "not listed" and the 77,859 MW "new entry" is the same equipment.

## 3. K2 compared two definitions; the two generators are Elwood's

The reference 379 came from the id check (job `eia860m-slip-v3`): operating generators whose last record ends before the last report. 0.3.0 reports that count less any generator with a retired record in its history. Both counts are 379; the count without retired records is 377. The two generators are **Elwood Energy LLC GT8 and GT9** (plant 55199, 192 MW each, Illinois): operating to May 2025, reported retired from June 2025 to February 2026, then out of service (OS) from March 2026, last listed in May 2026 (last record April to May 2026) and absent from the June 2026 report on. The code is right; the check compared a number computed one way with a number computed another.

## 4. PUDL's end-of-record convention, from the records themselves

The records printed by the diagnosis show the convention 0.3.0 assumes. For generators still listed in the August 2026 report, the last record's `valid_until_date` is 2026-08-01 (Apache Station's units, Cumberland 1, Yates 6-10): under an exclusive reading they would all have left the inventory in August, which they did not. A record that begins in the last report, August 2026, ends 2026-09-01 (Ripley RP1, Yates 8), one month long. If last records were exclusive, every generator whose record did not change in August 2026 (most of the inventory) would have been last listed in July, and only changed records would reach August; a changelog built from complete monthly files cannot look like that. So a generator's last record ends at its last listing, inclusive (Elwood GT8's last record, April to 2026-05-01, means last listed in May 2026), and 0.3.0's `listed_until` encodes exactly this. 0.2.0's exclusive reading is wrong for last records. This is read off the records; PUDL's own code for the end date was not checked line by line.

## What happens next

1. `rekey-v1` runs; its output is published as description.
2. A new pre-registration (`annual-flows-preregistration-v2.md`) is committed before any scored re-run. It will state that the first run, this diagnosis and the re-key output were seen; replace K2's reference with the count the code computes (377, or 379 counted the id check's way); widen K3's plan bound to what the inclusive reading implies (every year's 0.3.0 plan equals 0.2.0's plus the generators whose last record ends in that January); and, if re-keying is confirmed, pre-register the linking rule and the checks on it before the code changes.
3. Until then the root `eia860m_slip.py` stays at 0.2.0 and the generator-level tables stay unpublished as results. F1 and F5 of the first run (slipped against not listed; new entry as the largest unplanned source) lean on the two columns that re-keying would inflate, which is why they are not scored on the first run's output.

## Also found, not scored: the names behind the gas-flows result

The diagnosis printed the raw records of the four plants behind the largest moves in [`gas-flows.md`](gas-flows.md). Plant 3399 is **TVA's Cumberland (TN)**: its combined cycle CTG1 and STG1 (454.8 and 323.0 MW nameplate), under construction, moved from December 2026 to **December 2034** in the July 2026 report, while CTG2 and STG2 stay planned for January 2029. Plant 67262 is **Ripley Energy Center** (RP1, 419.0 MW nameplate, more than half built), moved from October 2026 to December 2026 in the June report and to March 2027 in the August report. Plant 728 is Georgia Power's **Yates**: generator 8 (482.8 MW nameplate; at the planning stage in December, more than half built since February) moved from December 2026 to February 2027 in the August report; generators 9 and 10 stay at December 2027. Plant 160 is **Apache Station** (Arizona): its planned turbines GT7 and GT8 moved from December 2026 to June 2027 in the January 2026 report and were last listed in May 2026; they are the two generators from the December gas book that are no longer listed by August.
