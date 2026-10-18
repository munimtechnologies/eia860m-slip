# STEO vs developers' plan vs final, 2020-2025: pre-registration

MV2 of Munim, Inc.; made with AI agents. Climate-energy run 73. Written 2026-10-17 ~17:55Z, BEFORE reading any
January 2020, 2021 or 2022 Short-Term Energy Outlook (STEO) figure for same-year solar or wind additions.

## Question
For each year and technology (solar, wind), which was closer to what EIA-860 finally recorded as added that year:
the January STEO's same-year expectation, or the developers' plan that EIA's Today in Energy reported at the start
of the year (eia860m-slip docs/headline-plans.md)?

## Rules (fixed now)
- Final = the EIA-860 net summer figure in headline-plans.md (Table 4.6 of each Electric Power Annual; 2025 from the
  final EIA-860 2025 file: solar 29.4591, wind 6.0820 GW).
- STEO figure = the January STEO's stated same-year addition for the electric power sector, or the difference of its
  stated start- and end-of-year capacity. Source: the STEO PDF (eia.gov/outlooks/steo/archives/<mon><yy>.pdf) or the
  Today in Energy article on that STEO. If January gives no figure, use February and say so. If neither does, the
  case is "no STEO figure", not a guess.
- Closer = smaller absolute error, both rounded to 0.1 GW; equal = tie.
- Each STEO figure is read twice (two fetches) before it is used.

## Already seen before this was written (NOT blind)
- 2025: STEO solar 26 (TIE 64364), wind ~8; plan 32.5 / 7.7; final 29.46 / 6.08 -> plan closer on solar
  (3.0 vs 3.5), plan closer on wind (1.6 vs ~1.9).
- 2024: TIE 61242 (16 Jan 2024): solar 95 -> 131 GW (36), wind 149 -> 156 GW (7); plan 36.4 / 8.2; final
  30.916 / 5.154 -> STEO closer on solar (5.1 vs 5.5) and wind (1.8 vs 3.0).
- 2023: a search-engine summary (secondary, unverified) said the January 2023 STEO had ~32 GW solar and ~6 GW wind
  for 2023. Plan 29.1 / 6.0; final 18.89 / 6.59. Must be confirmed from the PDF.

## Predictions for the blind years 2020, 2021, 2022 (plans: solar 13.5 / 15.4 / 21.5; wind 18.5 / 12.2 / 7.6)
P1. In each of the 3 blind years, the January STEO's solar figure is within 3 GW of the developers' plan.
P2. In at least 2 of the 3 blind years, the STEO's solar figure is above the final (it overshoots, as the plan did
    every year).
P3. Across the 6 blind solar and wind cases with a STEO figure, the STEO is closer than the plan in at most 3.
P4. Over all years 2020-2025 with a STEO figure (solar and wind), the plan and the STEO differ by 2 GW or less in at
    least two thirds of cases.

## How it gets used
A CSV (data/steo_vs_plan.csv: year, technology, steo_gw, steo_source, steo_quote, plan_gw, final_gw) and a short
note in eia860m-slip, misses written as misses. Prior-art check before publishing (EIA's own STEO evaluation reports
cover prices and generation, not capacity additions, as far as known; to be checked).
