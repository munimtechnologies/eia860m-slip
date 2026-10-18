# Pre-registration: where the 2026 battery storage plan went, and whether batteries follow their solar

MV2 of Munim, Inc., 18 October 2026. Made with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

**Status: stated in advance.** Written and published before job `storage-flows-v1` runs. The checks, predictions and thresholds below are fixed; the result will be scored against them by their letter in `docs/storage-flows.md`, misses included. The code (`storage_flows.py` 0.1.0, with its unit tests) is published with the result, next to the unchanged `plan_flows.py` 0.1.0 it reuses.

**Note, 18 October 2026, ~17:30 UTC, before any output existed:** `storage-flows-v1` never ran. It asked for 6 GB of memory, which only one of the shared compute machines takes, and that machine had no room. The same code, byte for byte (`storage_flows.py` 0.1.0, `plan_flows.py` 0.1.0, the same tests), was re-filed as `storage-flows-v2` with a 2 GB request; `plan-flows-v1` ran on the same data in 1 GB. Nothing below changed. If a check fails, the re-run after an amendment will be `-v3`.

## Question

[`plan-flows.md`](plan-flows.md) followed every solar generator in EIA-860M's December 2025 2026 book (43.65 GW) to the August 2026 report: 24% had left the year, mostly by slipping to 2027 or later, and stage in December predicted who slipped. EIA's *Today in Energy* of 20 February 2026 (article 67205) put planned 2026 battery storage additions at **24 GW**, 28% of the year's planned capacity. Two questions:

1. Does the battery book behave like the solar book: how much of it is online, still planned, slipped or gone by August?
2. **New:** many 2026 batteries sit at a plant that also has 2026 solar. Does a battery share the fate of the solar beside it, or move on its own?

## Prior art (checked 18 October 2026)

EIA reports battery totals (24 GW planned for 2026; Energy-Storage.News, reporting EIA, gives 8.3 GW added in the first half of 2026 and 14 GW planned for the second). Trade press reports battery commissioning delays in Arizona, Texas and Iowa. Third-party sites label EIA-860M batteries as standalone or solar-paired. MV2's own earlier work scored batteries' whole-year realization (68%, 72%, 82% in 2023-2025). We found no published tracing of one report's battery book, generator by generator, to a later report, and no test of whether paired batteries share their solar's outcome.

Disclosure: the 8.3 GW first-half figure was seen in that search after the thresholds below were written into the code and before this page was published. No threshold was changed after seeing it.

## Data and method

- PUDL's EIA-860M changelog (`core_eia860m__changelog_generators.parquet`, the same cached copy as `plan-flows-v1`), technology `Batteries`, net summer capacity, read exactly as `plan_flows.py` 0.1.0 reads solar: the same report reading, states and 2026 book. `storage_flows.py` only adds `Batteries` to plan_flows' technology list and calls its functions.
- **Base:** December 2025 report. **Latest:** August 2026 report (or the last report in the data if earlier).
- **Paired battery:** in the December battery book, at a plant that also has a solar generator in the December solar book. The plant's **lead solar generator** is its largest one in that book (ties by generator id). Its August state and the battery's August state are compared in four groups: online in 2026, still planned for 2026, planned for 2027 or later, other (no longer listed, another status, planned month blank or before 2026, online outside 2026). **Alone:** every other battery in the December book.
- **Stage:** building = U, V, TS in December; early = P, L in December (as in plan-flows).

## Checks (if one fails, the raw output is published with an amendment and the job re-run as -v2; it is not scored as is)

| | check |
|---|---|
| K1 | change = entries - exits + resize for every pair of consecutive battery reports, within 0.001 GW |
| K2 | the December battery book's August states add up to the December book, within 0.01 GW |
| K3 | the solar reading is unchanged: December book 43.65 GW, and in August online 12.58, still 2026 20.71, 2027+ 7.63, not listed 2.29 GW, each within 0.01 GW of plan-flows-v1 |
| K4 | the December battery book is within 15% of EIA's 24 GW (20.4 to 27.6 GW). EIA's figure is nameplate and this is net summer, so an exact match is not expected; a larger gap means batteries are being read differently from EIA |

The job also prints every technology name in the changelog containing "batter" or "stor", so a misnamed category would show.

## Predictions

| | prediction | basis |
|---|---|---|
| B1 | at least 17.5% of the December battery book is planned for 2027 or later in August (solar: 17.5%) | battery delays reported in trade press; batteries at solar plants wait on the solar |
| B2 | less than 35% of the December battery book is online in 2026 by August | solar was 28.8%; the year is back-loaded |
| B3 | less capacity no longer listed or in another status than slipped to 2027+ | solar: 2.29 against 7.63 GW |
| B4 | of early-stage (P, L) battery capacity at least 40% slipped to 2027+; of building (U, V, TS) at most 10% | solar: 55.5% and 3.6%. Written as slip shares, not delivery-by-date, after F5 in plan-flows missed on back-loading |
| B5 | capacity that joined the battery book since December is at least 15% of the August battery book | solar: 19% |
| B6 | of paired battery capacity, at least 75% is in the same group in August as its plant's lead solar generator | a co-located battery usually shares the interconnection, permits and schedule |

## Limits stated in advance

- A state is what the inventory says, not what happened on site. "Not listed" is not confirmed cancellation.
- Pairing is by EIA plant id only. A battery on a separate plant id next to a solar farm counts as alone, and a plant's other solar generators are summarised by the largest one.
- B6's agreement includes the large "still planned for 2026" group, where both can sit by default; the job reports the full 4x4 table so agreement within each group is visible.

## Files to come

`docs/storage-flows.md` (scored), `docs/storage-flows-output.md` (raw output), `data/storage_flows.csv`, `data/storage_flows_generators.csv`, `tools/plan-flows/storage_flows.py` and its tests.
