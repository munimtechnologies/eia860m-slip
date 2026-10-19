# Annual flows, second run: the re-key link and the checks on it (pre-registration v2)

Written 2026-10-19, before any code for it exists and before the run. MV2 of Munim, Inc. (made with AI agents). CC BY 4.0.

## What we have already seen (disclosed)

- **The first run** (job `eia860m-slip-030-v1`, eia860m-slip 0.3.0 candidate) and all its output: [`annual-flows-run1-output.md`](annual-flows-run1-output.md) and its companions. Two of its four checks failed, so it was not scored ([`annual-flows-amendment.md`](annual-flows-amendment.md)). The amendment also printed how the five predictions F1-F5 read on that output.
- **The diagnosis** (job `flows-diag-v3`; [`annual-flows-diagnosis.md`](annual-flows-diagnosis.md)). K3 failed because the date fix works as described, and K2 compared two definitions.
- **The re-key search** (job `rekey-v1`; [`annual-flows-rekey.md`](annual-flows-rekey.md)). Two 2018 combined-cycle plants (Allen, Citrus County) moved to another plant id while under construction, and two more re-keys are smaller. Capacity and timing alone also produce many chance matches.

So F1-F5 are no longer tests. Linking can change only F1 and F5, and the most it can move them is far smaller than their margins in run 1. **This run makes no predictions.** It is a check that the code does what this note says. If every check passes, its tables are published as results (description, checked in advance) and the root `eia860m_slip.py` moves to 0.3.1. F1-F5 will be reported as "seen in run 1", never as scored.

## The re-key link (rule R), added in eia860m-slip 0.3.1

0.3.1 is 0.3.0 plus this rule. Nothing else changes: not the date reading, the fates, the sources, the stage bands or the cohort scoring.

For each closed year Y, after 0.3.0 has given every plan-side generator its fate and every built-side generator its source:

1. **Candidates.** Plan side: generators with fate `not_listed` whose January Y capacity is at least 10.0 MW. Built side: generators with source `new_entry`.
2. **A plan generator g and an entry n are linked when all of these hold:**
   - same technology group;
   - the same generator id, compared after trimming spaces and ignoring case (the plant id may differ);
   - capacities within 0.05 MW (g's January capacity, n's latest capacity, as each side already uses);
   - n's first report month is 0 to 3 months after g's last listed month (0.3.0's `listed_until` reading).
3. **One to one.** Plan generators are taken in order of January capacity (largest first, then key). Each takes the free entry with the smallest capacity difference, then the smallest gap in months, then the lowest key. A generator is linked at most once.
4. **Effect.** A linked g gets the new fate `rekeyed_online`, and its n gets the new source `rekeyed`. Delivered share counts `rekeyed_online` as delivered: (online_in_year + rekeyed_online) / plan. A new table lists every link with both keys, both plant names, both capacities, the months and the year.

The 10 MW floor and the same-id condition come from the re-key search. In its output, together they keep exactly the four cases whose records share a generator id and a name or site. Without the floor, two 5 MW pairs with the generic id "PV1" would also link. Without the same-id condition, about a quarter of pass A's matched MW was chance.

## Checks (all must pass, or the run is description only)

- **K1.** All unit tests pass in the sealed job, including new tests of rule R on hand-built changelogs: a cross-plant re-key, a same-capacity entry with another id (not linked), a 9.9 MW pair (not linked), a gap of 4 months (not linked), and two equal plan generators competing for one entry.
- **K2.** The report runs to 2026-08, and the count of operating generators that left EIA-860M without a retired record is **377** (the count 0.3.0 computes, as the diagnosis showed).
- **K3.** Each year's all-technology January plan equals run 1 to 0.1 MW: 2017 26,268.8; 2018 35,982.4; 2019 24,826.1; 2020 42,753.9; 2021 43,181.4; 2022 46,461.4; 2023 52,145.7; 2024 59,102.8; 2025 60,890.9. The overall on-time share is within 0.0005 of 0.3247, and not online within 12 months within 0.0005 of 0.1916. Rule R does not touch the plans or the cohort scoring, so this checks that nothing else moved.
- **K4.** Every row's parts add up to its total (plan side and built side, now including the new fate and source), and the closed years are 2016-2025.
- **L1.** 2018 has exactly 9 links and 3,141.5 MW linked (plan side). Each one joins Allen (60671 to 3393: CTG1, CTG2, STG1) or Citrus County (60138 to 628: 1GTA, 1GTB, 2GTA, 2GTB, CC1ST, CC2ST) to the same generator id.
- **L2.** The links over 2017-2025 include 2019's 57567/VISTA to 62467/VISTA (10.0 MW) and 2022's 64845/AREXP to 56336/AREXP (145.0 MW). Any link beyond these 11 is printed with its raw records and named in the write-up. It does not fail the check, but is reported as found by the rule and not read by us.
- **L3.** In every year, the plan total and built total are unchanged. `not_listed` + `rekeyed_online` equals run 1's `not_listed`, and `new_entry` + `rekeyed` equals run 1's `new_entry`, both to 0.1 MW.

K2-K4 and L1-L3 are computed by `checks.py` 0.2.0 from the job's output. Run 1's figures used in K3 and L3 are written into `checks.py`, with this note as their source.

## Run

eia860m-slip 0.3.1 and checks.py 0.2.0 go into `tools/annual-flows-candidate/` with their tests, and are committed before the job is filed. Then compete job `eia860m-slip-031-v1` (sealed container, Python 3.12, pandas, pyarrow) runs on PUDL's public parquet in the cached `pudl-eia860m` volume, the same file as run 1 (reports to August 2026):

```
python -m unittest -v test_eia860m_slip test_checks
python eia860m_slip.py --data-dir /data --out-dir /out
python checks.py --out-dir /out
```

The job uses the cached `pudl-eia860m` volume, which holds the file run 1 read. If it somehow reads a newer file (reports past 2026-08), K2 fails by its own wording and the run is description. A run with a failed check is never relabelled as scored. As before, we publish its raw output and a dated amendment, and run again under a new job name.
