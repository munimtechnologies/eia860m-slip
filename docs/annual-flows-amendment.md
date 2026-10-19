# Annual flows, first run: two checks failed, so the run is description only (amendment, 2026-10-18)

MV2 of Munim, Inc. (made with AI agents). CC BY 4.0.

The checks and predictions in [`annual-flows-preregistration.md`](annual-flows-preregistration.md) were committed at 2026-10-18 21:23Z. Job `eia860m-slip-030-v1` ran eia860m-slip 0.3.0 in a sealed container from 22:56 to 23:00Z, after that commit. Two of the four checks failed. By the rule we wrote in advance, this run is **not scored**: we publish its raw output and this note, find the cause, and run again under a new job name. We do not change a check after seeing the output and then call the run scored.

## The checks

| check | rule | result | |
|---|---|---|---|
| K1 | all unit tests pass in the sealed job | 28 of 28 passed | passed |
| K2 | report runs to 2026-08, and exactly 379 operating generators left EIA-860M without a retired record | 2026-08; **377** | **failed** |
| K3 | on-time share within 0.005 of 0.326; not online in 12 months within 0.005 of 0.188; every January plan 2017-2025 within 1% of 0.2.0's | 0.3247; 0.1916; **2018 plan +3.63%** | **failed** |
| K4 | every row's parts add up to its total; closed years 2016-2025 | 179 rows, all add up; 2016-2025 | passed |

The January plans against 0.2.0's (all technologies, MW): 2017 26,268.8 against 26,236.8 (+0.12%); **2018 35,982.4 against 34,723.5 (+3.63%)**; 2019 +0.06%; 2020 +0.58%; 2021 +0.75%; 2022 +0.87%; 2023-2025 +0.01% each. Only 2018 breaks the 1% bound.

## What we see, and what we suspect (not yet confirmed)

- **K2.** The reference, 379, came from the id check (job `eia860m-slip-v3`), which counted every generator whose last record lists it as operating and ends before the last report. `checks.py` compared it with a different count: the same exits less any generator that has a retired record anywhere in its history (`operating_exits_without_retired_record` in `retire.json`). If exactly two of the 379 have an earlier retired record, for example a unit reported retired and later reported operating again, the code is right and the check compared two different numbers.
- **K3.** In 2018, 3,141.5 MW of combined-cycle capacity in January's plan is "not listed" by February 2019, and exactly 3,141.5 MW of combined-cycle capacity built in 2018 was a "new entry" (not listed in January). Identical totals suggest the same plants dropped under one generator id and listed again under another. 0.3.0 reads a generator's last record as running to its last listing, inclusive, as PUDL defines it; 0.2.0 read it as exclusive and so may have missed these generators in January 2018. If that is the whole story, the 1% bound was too tight for the fix it was testing. Either way, re-listing under new ids would also inflate the "not listed" and "new entry" columns of the flows. We have not yet checked this against the raw records.

A diagnosis job (`flows-diag-v1`, code beside eia860m_slip.py 0.3.0 unchanged) prints both exit counts and the generators that differ, every year's January plan under both readings with the generators only one reading has, the dropped and newly listed capacity at the same plants each year, and their raw records.

## What happens next

- If the cause is in the code, we fix it and run again as `eia860m-slip-030-v2` with K1-K4 and F1-F5 unchanged.
- If the code is right and a check's reference was wrong, this run stays description only. Any new check is published before the next run, and the next run is scored only against checks written before it.
- Until then the generator-level tables in the README stay unpublished as results.

## Raw output of this run (description, not scored)

- [`annual-flows-run1-output.md`](annual-flows-run1-output.md): `flows.md`, the annual flows by year, technology and stage.
- [`annual-flows-run1-slip.md`](annual-flows-run1-slip.md) and [`annual-flows-run1-retire.md`](annual-flows-run1-retire.md): the generator-level scoring of planned operating and retirement months under 0.3.0.
- [`annual-flows-run1-checks.json`](annual-flows-run1-checks.json): what `checks.py` printed.
- [`../tools/annual-flows-candidate/`](../tools/annual-flows-candidate/): the code that ran (eia860m_slip.py 0.3.0, checks.py and their tests). It replaces the root `eia860m_slip.py` only once a run passes its checks.

For the record, this is how the five predictions read on this output. They are **not scored**, because two checks failed: F1 (slipped at least twice not listed, pooled 2017-2025) 118,185 against 11,155 MW; F2 (solar slipped more than not listed in at least 8 of 9 years) 9 of 9; F3 (other status under 2% of what did not come online) 0 MW; F4 (building delivered share at least three times early) 0.707 against 0.271, a ratio of 2.6; F5 (new entry the largest unplanned source of additions) 77,859 MW of 104,775. If the K3 cause is re-listing under new ids, F1 and F5 lean on exactly the columns it inflates.
