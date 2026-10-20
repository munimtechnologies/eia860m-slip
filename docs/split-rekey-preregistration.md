# How much "never came online" capacity was re-filed at the same plant under new generator ids? (pre-registration)

Written 20 October 2026, before job `splitkey-v1` is filed and before rule S has been applied to any data. MV2 of Munim, Inc. (made with AI agents). CC BY 4.0.

## Where this comes from

Every eia860m-slip delivery rate follows a planned generator by its key, plant id plus generator id. A plan that is re-filed under a new key reads as never online, even if the plant was built. Rule R ([`annual-flows-rekey.md`](annual-flows-rekey.md)) links the same equipment filed under another plant id: 11 links. It cannot link a plan that stays at its plant but comes back under new generator ids.

The description of the stage-by-lead cells ([`stage-leadtime-cells.md`](stage-leadtime-cells.md)) found one such case. South Field Energy (Ohio, plant 60356) is one 1,105 MW combined-cycle key in the U cell 13-24 months out, with no operating month. The same plant id has four generators in the V cell 0-3 months out. Five of the ten largest U generators and four of the ten largest V generators at 13-24 months have no operating month under their key.

There is a mechanism for this. EIA's prime mover code CC is "Combined Cycle Total Unit (use only for plants/generators that are in planning stage, for which specific generator details cannot be provided)". This is Form EIA-860 Instructions, Table 2, as copied on MATPOWER's gentypes page. A planned combined-cycle plant can be reported as one unit and later as its turbine (CT) and steam (CA) parts, under new generator ids. Wind and solar plans can also be split into phases or renumbered.

The question: **how much of the capacity that eia860m-slip scores as "not online within 12 months" was re-filed at the same plant under new generator ids that did come online, and does it change any published verdict?**

## Rule S (fixed now; code `tools/annual-flows-candidate/splitkey.py` 0.1.0)

1. **Leaver.** A generator with at least one planned record (P, L, T, U, V, TS, OT), no operating month under its key, no record in force in the last report (it left EIA-860M), and capacity above 0 in its last record. PUDL's EIA-860M changelog has no cancelled status: the only status codes in it are OP, RE, V, U, SB, TS, P, L, T, OS, OA and OT (profile of the August 2026 file). A cancelled plan just leaves the list. So many leavers are expected to be cancellations, and rule S looks for the ones that are not.
2. **Cluster.** Leavers at the same plant id and fuel family form a cluster when their last listed months, in order, are at most 3 months apart. All natural-gas technology groups are one family, so a combined-cycle plan can be rebuilt as combustion turbines. Every other technology group is its own family, and "other" is split by technology description.
3. **Arrivals.** For each cluster, the plant's generators of the same family that are not in the cluster, were first listed after the cluster's earliest first listing, and were first listed between 6 months before the cluster's earliest last listed month and 6 months after its latest. Clusters are taken in order of their latest last listed month (then plant id, family and first key). An arrival taken by a linked cluster is not offered to a later one.
4. **Link.** A cluster is linked when it has arrivals and their summed capacity is within 20% of the cluster's. Each arrival's capacity is taken from its first record with capacity above 0, each leaver's from its last record.
5. **Replacement month.** This is the latest operating month among the arrivals, if every arrival has one. An arrival with no operating month of its own that is a leaver in another linked cluster takes that cluster's replacement month, so chains are followed. The leavers of a linked cluster are "replaced", and their rows are re-scored as if they came online in the replacement month.
6. **Bound B (upper bound).** A cluster is "possible" when any generator at the same plant id and family that was first listed after the cluster's earliest first listing came online, with no limit on timing or capacity. Every replaced leaver is in a possible cluster. So B's share is an upper bound on rule S's.

Measures, all capacity-weighted (MW summed over rows, as published):

- **Rows.** The 0-12-month cohort rows exactly as eia860m_slip 0.3.1 scores them (`cohorts`; the published "Overall" row: 78,646 rows, 4,550,498.4 MW). Also the 0-24-month stage-by-lead rows exactly as leadtime.py 0.1.0 reads them (report months 2016-01 to 2023-06).
- **Replaced share.** The MW of not-online rows whose generator is replaced, divided by all not-online MW. Also the linked share (a replacement month is not required) and the possible share (bound B).
- **Re-scored shares.** The on-time and not-online shares before and after re-scoring.
- **Breakdowns.** Overall, by technology group (solar, onshore wind, gas CC, battery, gas CT), by stage, and for each of the 16 stage-by-lead cells. Also the six stage-by-lead predictions (L1-L6) re-evaluated on the re-scored rows.
- **Sensitivity.** Capacity tolerance 0.05, 0.10, 0.20 and 0.30, and crediting the first arrival's operating month instead of the last. These are reported, never used to choose a rule.

## Checks (all must pass, or the run is description only)

- **K1.** The rebuilt 0-12-month rows match the published "Overall" row: rows exact, MW to 0.05, and on-time 0.325 and not-online 0.192 each within half a unit of the third decimal ([`annual-flows-run1-slip.md`](annual-flows-run1-slip.md)). The U and V cells at 0-3 and 13-24 months match [`stage-leadtime.md`](stage-leadtime.md): rows, generators, MW to 0.05, and on-time share to 4 dp.
- **K2.** Every link obeys rule S. Each leaver has no operating month and left before the last report. Leavers and arrivals have the cluster's plant id and family. No arrival is used twice, and no leaver is its own arrival. Capacities are within the tolerance. Every replaced leaver is inside bound B.
- **K3.** Re-scoring keeps every row and its MW, outcomes add up to the MW, and only replaced leavers' rows change. This is checked on both row sets.
- All 12 unit tests pass in the sealed job (`test_splitkey.py`, a hand-built changelog; every expected value is traced by hand in the comments).

## Predictions (stated before the run)

Shares are compared unrounded.

- **S1.** Re-filing at the same plant is a real but minority part of "not online". In the 0-12-month rows, the replaced share of not-online MW is at least 0.03 and at most 0.20.
- **S2.** The headline holds. Re-scoring raises the overall 0-12-month on-time share (published 0.325) by less than 0.02. Replacements tend to come online late, so most re-scored rows move from "not online" to "late", not to "on time".
- **S3.** The effect is larger far out. The replaced share of not-online MW in the U cell 13-24 months out is larger than in the 0-12-month rows overall.
- **S4.** It is mostly a combined-cycle effect (the CC prime mover code above). In the 0-12-month rows, gas CC's replaced share of its not-online MW is larger than solar's, onshore wind's and battery's.
- **S5.** The stage-by-lead verdicts survive. Each of L1-L6 has the same verdict (held or failed) on the re-scored rows as on the published ones.

If S1 and S2 hold, eia860m-slip's delivery rates understate delivery only modestly through same-plant re-keys, and the published on-time shares stand. If S1 fails high, every "not online" share in the twenty results so far needs a dated caveat, and rule S becomes part of the scoring.

## Hand-reading (fixed now, done after the run)

The job writes the raw records of the 10 linked clusters with the most not-online MW in the 0-12-month rows. Each is read by hand and called "same project" only if all three of these hold:

- (a) The arrivals carry on the leavers' plan. Their first planned month, or their operating month if they arrived operating, is within 24 months of the leavers' last planned month.
- (b) Leavers and arrivals were not listed side by side as separate live plans for more than 6 months.
- (c) The technology change is one a single project makes. Examples: CC total unit to CT/CA parts, one wind or solar key to several phase keys, or the same technology renumbered.

If fewer than 7 of the 10 read as the same project, rule S over-links. S1-S5 are then reported as description only, and a follow-up pre-registers a tighter rule before anything else is read. Every reading is published with its records.

## What we had seen before writing this

- The published marginals quoted above: the overall not-online share 0.192, and the U 13-24 cell (636,740.1 MW, not online 0.462).
- The stage-by-lead verdicts: L2, L4, L5 and L6 held, L1 and L3 failed. S5 is partly informed: we know which verdicts sit near their thresholds (L3 at 0.4088 against 0.45).
- The cell description's tables of the ten largest generators and plants in U and V at 0-3 and 13-24 months. They name South Field Energy and, with no operating month under their keys, Chilocco, Alle-Catt, Easter and Canisteo (wind), Washington Parish Energy Center (gas CC) and Rugged Solar. S3 and S4 are partly informed by the South Field lead.
- Rule R's 11 cross-plant links.

Rule S has not been applied to any data. No count of leavers, clusters or arrivals has been computed.

## Run

Compete job `splitkey-v1` (sealed container, Python 3.12, pandas, pyarrow; 4 GB) uses the same cached PUDL file as the seventeenth to twenty-third results (reports to 2026-08). It fetches eia860m_slip.py (329b7e6) and leadtime.py (9ee085b) pinned, and splitkey.py and its tests from the commit that publishes this note. It runs `python -m unittest -v test_splitkey`, then `python splitkey.py --data-dir /data --out-dir /out`. It is filed only after this note is live and the unit tests have passed in their own sealed job (`splitkey-unittests-v2`, queued when this note was written). If a unit test fails, the code is fixed and republished with a dated note before any data is read; rule S, the checks and the predictions do not change. A run with a failed check is never relabelled as scored: its raw output is published with a dated amendment, and it runs again under a new job name with these predictions unchanged. A run that runs out of memory is a failed run, not a failed check, and is re-filed with more memory.

## Prior art

Searched 20 October 2026. PUDL's changelog table keys generators by plant id, generator id and report date, so a changed id shows up as a separate generator. PUDL issue #3684 (integrating the 2023 annual EIA-860) records one plant (1439) whose generator ids changed between EIA-860M and the annual file ("9A, 9B etc., to generators 9, 10, 11"). We found no crosswalk for re-filed planned generators. We also found no estimate of how much planned capacity that "never came online" in EIA-860M was re-filed under new ids. Delivery studies that follow EIA-860M generators by key (including ours so far) do not report this bias.

## Limits known in advance

- Rule S is a heuristic. It can link a cancelled phase to a different phase built at the same plant (bound B shows how far that could go), and it misses re-filings outside its windows or tolerance.
- Re-filing under a new plant id and new generator ids together is caught by neither rule R nor rule S.
- Leavers still listed in the last report are not considered: a stale planned key kept alongside its built replacements stays "not online".
- A replacement month is the arrivals' operating month, not the leaver's: it scores whether the plant came, not whether that key's plan was right.
- Rows are not independent, and a few large plants can dominate MW shares, as the cell description showed.
