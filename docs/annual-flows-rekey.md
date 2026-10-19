# Re-keyed generators in EIA-860M: two 2018 combined-cycle plants changed plant id while under construction

Status: description (nothing here is scored). MV2 of Munim, Inc., 19 October 2026. Made with AI agents working in his name. CC BY 4.0.

## Question

The first annual-flows run (eia860m-slip 0.3.0 candidate, job `eia860m-slip-030-v1`; see [`annual-flows-amendment.md`](annual-flows-amendment.md)) found 3,141.5 MW of combined cycle in the January 2018 plan that was "not listed" by February 2019, and exactly 3,141.5 MW of combined cycle built in 2018 that January had not listed ("new entry"). The diagnosis ([`annual-flows-diagnosis.md`](annual-flows-diagnosis.md)) showed that no plant had both, so if this was the same equipment, its plant id had changed.

Job `rekey-v1` (`tools/annual-flows-candidate/rekey.py` 0.1.0, importing eia860m_slip.py 0.3.0 unchanged; 6 unit tests passed in the sealed job) ran on 2026-10-19, 10:40-10:43Z, on the same PUDL file (reports to August 2026). For every closed year 2017-2025 it paired each "not listed" generator with a "new entry" of the same technology group, across plant ids:

- **Pass A (strict):** capacity equal within 0.05 MW, first listed 0-3 months after the dropped generator's last listed month.
- **Pass B (loose):** capacity within 5%, 0-6 months, among what pass A left.

Each generator was used at most once. Its full output is [`annual-flows-rekey-output.md`](annual-flows-rekey-output.md).

## Answer: yes in 2018, and it is two plants

All 3,141.5 MW are two plants that moved to the plant id of the existing station on the same site. In each case every generator id, the status and the planned month are the same on both sides of the move:

| plant | old id, last listed | new id, first listed | generators | MW | online |
|---|---|---|---|---:|---|
| TVA's Allen Combined Cycle (Memphis, TN) | 60671 "Allen Combined Cycle Plant", January 2018 | 3393 "Allen Steam Plant" (later "Allen"), February 2018 | CTG1, CTG2 (347.0 each), STG1 (476.9) | 1,170.9 | April 2018 |
| Duke Energy Florida's Citrus County Combined Cycle | 60138 "Citrus County Combined Cycle Plant", June 2018 | 628 "Crystal River", July 2018 | 1GTA, 1GTB, 2GTA, 2GTB (310.3 each), CC1ST, CC2ST (364.7 each) | 1,970.6 | October-November 2018 |

- **Allen:** under 60671 in January 2018, all three units were under construction (U) planned for June 2018. Under 3393 in February 2018 they were still U, planned for June 2018. They are listed as operating from the April 2018 report, with an operating date of April 2018.
- **Citrus County:** under 60138 in June 2018, all six units were more than half built (V), planned for September 2018 (1GTA, 1GTB, CC1ST) and December 2018 (2GTA, 2GTB, CC2ST). Under 628 in July 2018 they had the same status and the same planned months. The first block is listed as operating from October 2018, the second from November 2018. The plant stands at Duke's Crystal River Energy Complex, which explains the plant id it moved to.
- Pass A paired the Citrus County units crosswise (60138/CC2ST with 628/CC1ST, and so on), because equal capacities tie and the pass breaks ties by key. The plant-level match is what the records support: the same six generator ids appear on both sides.

So in 2018, 3,141.5 of the 3,500.3 MW "not listed" (89.7%) is not a dropped project but a plant that EIA re-filed under another plant id and that came online that year. Read naively, the 0.3.0 flows count it twice: once as a dropped plan and once as an unplanned addition.

## Other years: few real re-keys, many coincidences

Pass A found 104 pairs (4,299.0 MW) and pass B 49 pairs (1,729.5 MW), 54.0% of the 11,154.5 MW "not listed" over 2017-2025. Most of these pairs are not the same equipment. We sorted them by what the records share beyond capacity and timing:

| tier | rule | pairs | dropped MW |
|---|---|---:|---:|
| 1. same generator id and a matching name or site | Allen (3), Citrus County (6); 2019 Albuquerque Solar Energy Center 57567/VISTA to Vista Solar Energy Center 62467/VISTA (10.0 MW, same month); 2022 Aragonne Mesa Wind Project 64845/AREXP to Aragonne Wind LLC 56336/AREXP (145.0 MW, one month) | 11 | 3,296.5 |
| 2. a shared name or plant only | 2018 Lancaster SCE ReMAT 61081/PV1 to Lancaster 62056/LANC (3.0 MW, same month); 2019 Quinhagak 57057/1A to 57057/3A (0.5 MW, same plant, new id) | 2 | 3.5 |
| 3. capacity and timing only, pass A | over 5 MW: Black Bear Wind (MT) to Sac County Wind (80.0, 2021); TX17 Nickel Prairie Storage to McFarland A (100.0, 2023); Chiltepin Solar to TS Power Plant (100.0), Lake Mabel to International Battery Substation (40.0), Kahana Solar to Walden Solar Maine V (20.0, all 2024); Alamo 7 BESS 1 and 2 to Chillingham and Bocanova (150.0 each), Berkman to Knightdale (100.0, all 2025) | 8 | 740.0 |
| 3. capacity and timing only, pass A | 5 MW or less, mostly solar farms of 1, 2, 3 or 5 MW | 83 | 259.0 |
| 3. capacity and timing only, pass B | none shares an id or a name | 49 | 1,729.5 |

- **Tier 1 is 3,296.5 MW: 29.6% of the 11,154.5 MW "not listed" over 2017-2025 and 4.2% of the 77,858.9 MW "new entry".** Without 2018 it is 155.0 of 7,654.2 MW (2.0%).
- **Tier 3 is chance.** Solar farms cluster at round sizes, and each year has 448-786 new entries. The same dropped generator is matched to a different entry in consecutive years, which could not happen if a match meant identity: Bonnie Solar (60175/PV1) pairs with Middle Daisy in 2017 and Foreman's Hill in 2018; Christina Solar with Haywood (2017) and Gratis Road (2018); Alexis Solar with Tanglewood Circle (2018) and Wendell (2019); Wilfork Solar with Sandy Solar (2018) and Cookstown (2019). Many pairs join plants far apart, such as Black Bear Wind (MT) with Sac County Wind, or "CA Moss Landing 3040 Hilltop Rd" (1.2 MW) with "New Britain - 142 Deming Rd".
- **So capacity and timing alone are not enough.** Pass A's 4,299.0 MW is 3,296.5 MW of tier 1, 3.5 of tier 2 and 999.0 of chance matches (23%), and pass B is all chance. In this output, also requiring the same generator id and at least 10 MW keeps exactly the four tier-1 cases: the same id alone would also keep two 5 MW solar pairs whose id is the generic "PV1" (Peanut Solar to Floyd Road, 2017; Rhubarb One to Sun Farm VI, 2018).

## What it changes

- **The 2018 annual flows.** Re-linked, Allen and Citrus County move from "not listed" to "online in year" on the plan side and from "new entry" to "in plan" on the built side. The 2018 January plan (35,982.4 MW) delivered 3,141.5 MW more than run 1 shows, 8.7 points of that year's delivered share.
- **The diagnosis's K3 finding stands.** Allen is in the January 2018 plan only under 0.3.0's inclusive reading of a last record, because its last record under 60671 ends in January 2018.
- **Elsewhere the effect is small.** Outside 2018, tier 1 is 10.0 MW in 2019 and 145.0 MW in 2022: 13.1% of 2022's "not listed" (1,104.8 MW) and 1.7% of its "new entry" (8,535.6 MW); nothing in the other years.
- **2026 was not checked.** This job covers closed years only (2017-2025). The 2026 part-year flows (tenth to twelfth results) were computed by other code and may contain re-keys too.

## Prior art

PUDL's `core_eia860m__changelog_generators` is keyed by plant id, generator id and report date, so a generator that moves to another plant id appears as one exit and one new generator. PUDL issue #3684 (catalyst-cooperative/pudl) documents generator-id renames within one plant in the 2023 EIA-860 (plant 1439). On 19 October 2026 we found no account of EIA-860M generators moving between plant ids during construction, or of how much that inflates "dropped" and "unplanned" capacity. If you know of one, open an issue.

## Limits

- Tiers come from names and ids in the records, read by us, not from a rule the code applied. A re-key that also changed generator ids and plant name would be in tier 3 and missed.
- The pairing is greedy (largest dropped generator first; closest capacity, then earliest listing, then key). Where a same-id candidate tied with another, the other could have won, as it did inside Citrus County.
- Lancaster and Quinhagak (tier 2) were not checked against outside sources.
- Allen's and Citrus County's commissioning were checked against the operating dates in the records. For Citrus County, Duke's own releases describe two 820 MW units at the Crystal River Energy Complex entering service in late 2018.

## Next

A second pre-registration ([`annual-flows-preregistration-v2.md`](annual-flows-preregistration-v2.md)) fixes the linking rule (tier 1's condition, stated as code) and the checks on it before any code changes. eia860m-slip 0.3.1 then runs once under those checks.
