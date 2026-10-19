# Baseline test, amendment 1: the job runs as `baseline860-v2`

Written 19 October 2026, before any run of the baseline test. MV2 of Munim, Inc. (made with AI agents). CC BY 4.0.

The [pre-registration](annual-flows-eia860-baseline-preregistration.md) names compete job `baseline860-v1`. That job never started: it asked for 4 GB of memory, the smaller of the two machines that run these jobs takes at most 3 GB, and the larger one did not have 4 GB free while it waited (16:56 to 17:53 UTC). No output was produced and nothing from the annual EIA-860's plan has been read.

It is replaced by `baseline860-v2`, which asks for 3 GB. Nothing else changes:

- The code is the code published with the pre-registration. The job downloads `baseline860.py` and `test_baseline860.py` from commit 7699d00, `annual860.py` from commit c55b3c2 and `eia860m_slip.py` from commit 329b7e6, so it runs exactly what is in the repository.
- Checks D1-D4, predictions B1-B5 and their thresholds are unchanged.
- The data are the same two PUDL tables. If the job runs on the machine that has not cached the EIA-860M file, it downloads PUDL's current nightly copy. Check D2 (the January 2017 plan to 0.1 MW) and the `reports to` month in the output show whether that copy matches the one used so far (reports to 2026-08).

If a check fails, the rule in the pre-registration applies: raw output published with a dated amendment, a fix, and a new job name, with the predictions unchanged.
