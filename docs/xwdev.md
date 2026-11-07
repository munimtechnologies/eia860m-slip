# Do the four crosswalk leads stand in EPA's development-branch crosswalk? (result)

Result of pre-registration xwdev-1 ([plan](xwdev-plan.md), commit c22ba3f, published 6 November 2026 at 13:46 UTC, before any data was read). MV2 of Munim, Inc., 7 November 2026; made with AI agents working in MV2's name; no person has checked these results by hand. CC BY 4.0; code Apache-2.0.

**Gate G1 held, and all 5 predictions held.** All four leads from [step1d-look.md](step1d-look.md) stand in the crosswalk on the unreleased `development` branch of [USEPA/camd-eia-crosswalk](https://github.com/USEPA/camd-eia-crosswalk), which EPA regenerated in June 2025. Each CAMD generator is still linked to the EIA generator of very different size, by the same matching step ("Step 1d: Modify IDs; remove leading letters"), and no row links any candidate. No row of any sheet of the branch's `manual_matches.xlsx` names any of the six plant ids involved.

So basing PUDL's next crosswalk update on EPA's development branch, one of the options Catalyst lists in [camd-eia-crosswalk-latest#7](https://github.com/catalyst-cooperative/camd-eia-crosswalk-latest/issues/7), would not on its own fix any of the four. Each is still a lead for a person to check, not a finding.

## How it ran

- Job xwdev-v1 ran on 6 November 2026 (22:27 to 22:30 UTC). It first checked that the plan was live (it was, at the first poll, 22:29:06 UTC), then downloaded the committed `tools/xwdev/xwdev.py` 0.1.0 (md5 ce7ff1c99e1eb70a7660f6675e1d4388) and its tests (md5 7897543ebe2b04e22b21ee833ee8e77a); all 13 unit tests passed. Python 3.12.15.
- **Crosswalk:** `epa_eia_crosswalk.csv` at development-branch commit 3423b2ab457222e1eac5d69d25a98b5f62ce5975, 2,314,285 bytes, md5 5120bcdeab9d0281afc3a2c9d2c5f1a5, 5,810 data rows, 69 columns.
- **Manual matches:** `manual_matches.xlsx` at the same commit, 49,694 bytes, md5 8c86e7be228f4d4d97bc6faf50afb05b.

## Scores

| Bar | Probability given | Result | What the data shows |
|---|---|---|---|
| G1 | gate | held | All four id columns found (`epa_plant_id`, `epa_generator_id`, `eia_plant_id`, `eia_generator_id`); 5,810 rows (at least 4,000 needed); all four CAMD plants (57865, 1571, 422, 58478) have rows |
| P1 | 50% | held | Antelope Elk: ELK1, ELK2, ELK3 linked to 57865/E01, E02, E03; no row links 58835/ELK1-3 |
| P2 | 65% | held | Chalk Point: SGT1 linked to 1571/GT1; no row links 61890/SGT1 |
| P3 | 65% | held | Glenarm: STG5 linked to 422/GT5; no row links 422/ST1 |
| P4 | 65% | held | LEPA Unit No. 1: STG1 linked to 58478/LEPA1; no row links 58478/LEPA2 |
| P5 | 40% | held | All four stand |

## The rows, as the development-branch file has them

| Lead | CAMD unit / generator | CAMD nameplate (MW) | Linked EIA generator | EIA nameplate (MW) | EIA prime mover | Match type |
|---|---|---|---|---|---|---|
| Antelope Elk | 1, 2, 3 / ELK1, ELK2, ELK3 | 202 each | 57865/E01, E02, E03 | 9.3 each | IC | Step 1d |
| Chalk Point | SMECO / SGT1 | 93 | 1571/GT1 | 16 | GT | Step 1d |
| Glenarm | GT5 / CTG5 and STG5 | 75.88 | 422/GT5 | 71 | CT | Step 1d (both) |
| LEPA Unit No. 1 | CC01 / CTG1 and STG1 | 76 | 58478/LEPA1 | 57 | CT | Step 1d (both) |

The nameplates are the file's own `epa_nameplate_capacity` and `eia_nameplate_capacity` columns, so for Antelope Elk and Chalk Point the size gap is visible inside a single row of EPA's file (202 against 9.3 MW; 93 against 16 MW).

## What else the file shows (read after scoring, not pre-registered)

- **Manual-match sheets.** `manual_matches.xlsx` has six sheets: `unit_manual_matches` (89 data rows), `unit_manual_excluded` (252), `plant_id_manual_matches` (29), `plant_id_epa_to_eia` (16), `further_research` (111) and `Sheet Descriptions` (4). None of their rows has a cell equal to 57865, 58835, 1571, 61890, 422 or 58478, so EPA has not hand-matched, excluded or flagged for further research any of the four leads' plants or candidates.
- **The two combined cycles collapse in EPA's newer file too.** At Glenarm, CAMD lists two generators under unit GT5 (CTG5 and STG5); both rows link to 422/GT5. At LEPA Unit No. 1, CTG1 and STG1 under unit CC01 both link to 58478/LEPA1. This is the shape that [ccsplit.md](ccsplit.md) counts across PUDL's crosswalk.
- **The development-branch file carries CAMPD facility columns** (for example `associated_generators` and `nameplate_capacity`), but in the 19 rows the job printed for these four plants all of them are empty.

## What happens next

As the plan says, since all four leads stand on the development branch too, the PUDL issue (one issue, offered on the UTC day after the last result page is live) will say that adopting EPA's development branch alone would not fix them. The two combined-cycle leads (Glenarm and LEPA) were already offered to Open Grid Emissions on [open-grid-emissions#476](https://github.com/singularity-energy/open-grid-emissions/pull/476) on 6 November 2026. A follow-up check, [ccsub-plan.md](ccsub-plan.md) (id ccsub-1), asks whether PUDL's subplant table already groups those steam generators with their gas turbines; if it does, the cost of the wrong links is smaller than it looks, and the issue will say so.

## Limits

- The development branch is not a release; EPA may change it.
- A lead is a size match, not proof; someone who knows the plants has to confirm it.
- The manual-match scan looks only for cells equal to the six plant ids; a row naming a plant another way (by name only) would be missed.
- EPA's files are downloaded at run time and not stored here.
- No person has checked the code or the results by hand.

## Files

- [`tools/xwdev/xwdev.py`](../tools/xwdev/xwdev.py) 0.1.0, its tests and the plan-gated fetch; the plan: [xwdev-plan.md](xwdev-plan.md).
