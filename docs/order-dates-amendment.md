# Order dates: amendment after the first run (2026-10-18)

Made by MV2 of Munim, Inc. with AI agents. CC BY 4.0. Amends [`order-dates-preregistration.md`](order-dates-preregistration.md); the original is unchanged.

## What went wrong in the first run

Check C1 failed: Centralia (plant 3845, WA) was found but none of its generators matched. The pre-registration listed Centralia's unit as `BW22` or `22`. Those are boiler IDs; EIA-860M lists Centralia's coal units as generators `1` and `2` (our own [`coal-rows.md`](coal-rows.md) run lists 3845/1, retired December 2020). The fixed fallback (generators operating with a planned retirement in 2025-2026 in the November 2025 report) also found none, so Centralia's record in that report did not look like a unit about to retire. We do not yet know why.

Because C1 failed, the first run's predictions do not count as scored. [`order-dates.md`](order-dates.md) reports them as description only.

## What changes for the second run (order_dates 0.1.1)

- `units.csv`: Centralia's generator IDs become `2`, `BW22` or `22`. Nothing else in the unit list changes.
- The tool also lists every generator ever reported at each matched plant, with its status and planned retirement month before the first order and in the latest report, so a reader can see what EIA-860M says about Centralia whether or not it matches.
- Same data copy (C3 still requires 224,408 records), same orders file, same checks, same thresholds, same predictions. No other code change.

## What we already know before the second run

The first run's per-plant numbers for the other seven plants are public. Adding Centralia's at most nine unit-months cannot change P1 (at worst 101 of 135, 75%, against a 50% threshold), P2 (at worst 107 of 135, 79%, against 75%) or P4 (at most 5 of 8 plants, against 6). Only P3 (no covered unit reported retired while under an order) and C1 can still change. We say so now so the second run is not read as a fresh test of P1, P2 or P4.

## A correction to the question's framing

The pre-registration said DOE has used 202(c) "to keep eight plants from retiring." That is wrong for H.A. Wagner 4. Its orders (202-25-6, 202-25-6A, 202-26-25, 202-26-25A) let PJM run the oil-fired unit past a 438-hour yearly run limit on fuel oil; they do not defer a retirement ([order 202-25-6](https://www.energy.gov/sites/default/files/2025-07/PJM%27s%20202%28c%29%20Order%20No.%20202-25-6.pdf)). Wagner stays in the scoring as pre-registered; [`order-dates.md`](order-dates.md) also gives the result without it, marked as not pre-registered.
