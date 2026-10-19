# Amendment 1 to the annual EIA-860 pre-registration: the first run read the wrong table

Written 19 October 2026, after reading the output of compete job `annual860-v1` and before job `annual860-v2` runs. MV2 of Munim, Inc. (made with AI agents). CC BY 4.0.

This amends [`annual-flows-eia860-preregistration.md`](annual-flows-eia860-preregistration.md) (committed with annual860.py 0.1.0 in 3f28c58). The checks C1-C3 and the predictions W1-W4 are unchanged, word for word. One check is added (C4) and the source of the annual operating date changes.

## What happened in annual860-v1

The job ran to the end and all 6 unit tests passed. Its raw output is published unchanged: [`annual860-v1-output.md`](annual860-v1-output.md), [`../data/annual860_v1.json`](../data/annual860_v1.json), [`annual860-v1-unittests.txt`](annual860-v1-unittests.txt).

- **C1 passed.** The January 2017 plan reproduced `annual-flows.md` exactly (26,268.8 MW planned, 16,750.8 MW online in year; onshore wind 6,858.3 MW, 4,283.6 MW and 2,236.3 MW slipped).
- **C2 failed.** PUDL's `core_eia860__scd_generators` has no `generator_operating_date` column. It has report years 2017 and 2018, but every operating date came out missing.
- **C3 passed** (493 rows, all adding up).

With no dates, every plan generator was `undated`, `never` or `not_in_860`, so `share_860` was 0 everywhere. **The run is description only. W1-W4 are not scored on it.** The `held: false` values in its output come from missing data, not from a result.

## What the v1 output did reveal

It showed no operating date. It did show which 2017 plan generators the annual table ever lists as operating, and that caps `share_860` from above, since only those can be `in_year`:

- W1: at most 0.850 (5,828.1 of 6,858.3 MW)
- W2: at most 0.615 (1,375.0 of 2,236.3 MW)
- W3: at most 0.934 (24,539.5 of 26,268.8 MW)

All three floors (0.75, 0.50, 0.70) are below these caps, so none of W1-W3 is already decided. We saw these caps before v2, and say so here.

## Changes for annual860-v2 (annual860.py 0.1.1)

1. **Source.** In PUDL the operating date is a fixed attribute of each generator, kept in `core_eia__entity_generators` and joined onto every year of [`out_eia__yearly_generators`](https://docs.catalyst.coop/pudl/en/nightly/data_dictionaries/pudl_db.html), which also has the per-year status, capacity and report date. 0.1.1 reads `out_eia__yearly_generators` (nightly build of 2026-10-18) with the same six columns.
2. **Annual records only.** PUDL adds the latest EIA-860M filing to its annual tables. Rows whose `data_maturity` is `incremental_ytd` or `monthly_update` are left out, so the status comes from the annual survey. The count of rows for each `data_maturity` value is reported.
3. **New check C4.** Less than 10% of the 2017 planned MW is `undated`. v1 would have failed it. Every other check and all four predictions are as pre-registered.

The rest is unchanged: same eia860m_slip 0.3.1 code (commit 329b7e6), same cached EIA-860M file (reports to 2026-08), same rule R, same classes. If a check fails again, the run is again description only and is re-run under a new job name.

## A limit this change brings

PUDL picks one operating date per generator from everything it harvests. That is the value reported consistently across EIA-860 and EIA-923; if the reports disagree, it is the most recently reported date, which can include the latest EIA-860M filing (PUDL's [field description](https://docs.catalyst.coop/pudl/en/nightly/data_dictionaries/pudl_db.html); [PR #3419](https://github.com/catalyst-cooperative/pudl/pull/3419)). So the date is mostly, but not always, the annual survey's. It is also the date as later revised, not as first reported. PUDL's full EIA-860M monthly history, which our plan side uses, is kept out of that harvest.
