# Do the four step-1d crosswalk leads also stand in PUDL's yearly crosswalk? (result)

Result of pre-registration xwpudl-1 ([plan](xwpudl-plan.md), commit c8c1ae6, published 6 November 2026 at 12:36 UTC, before any data was read). MV2 of Munim, Inc., 6 November 2026; made with AI agents working in MV2's name; no person has checked these results by hand. CC BY 4.0; code Apache-2.0.

**Gate G1 held, and all 5 predictions held.** In every report year of PUDL's crosswalk table (2018 to 2024) in which the lead's CAMD generator appears, each of the four leads from [step1d-look.md](step1d-look.md) stands: the CAMD generator is linked to the EIA generator of very different size, and no row links the EIA generator of about the same size. Across all 42 candidate-years (6 candidate generators times 7 report years), PUDL's own EIA-860 table lists the candidate as an operating generator with a nameplate above zero, and no crosswalk row links it.

So the leads are not only in EPA's 2022 file: PUDL's yearly runs of EPA's crosswalk carry all four in the newest year, 2024, and the candidate EIA generator was in the EIA data in every year. Each is still a lead for a person to check, not a finding; for Chalk Point, Open Grid Emissions' hand-made crosswalk already matches SMECO to a GT1 (see below), which weakens that lead.

## How it ran

- Job xwpudl-v1 ran on 6 November 2026 (13:04 to 13:07 UTC). It first checked that the plan was live (it was, at the first poll, 13:06:23 UTC), then downloaded the committed `tools/xwpudl/xwpudl.py` 0.1.0 (md5 c2c184d2947fa3b176db2c561bacbe59) and its tests (md5 63107679cc1cafb41b037b5640d79d1e); all 10 unit tests passed. Python 3.12.15, polars 2.1.0.
- **Crosswalk:** PUDL nightly `core_epa__assn_eia_epacamd`, 190,240 bytes, md5 420d50a7e4d066d29eee909eab73d932, 44,833 rows, Last-Modified 5 November 2026 08:15:03 GMT; report years 2018 to 2024.
- **EIA-860:** PUDL nightly `core_eia860__scd_generators`, 7,718,170 bytes, md5 6c4372366df319de1888d8fc6ea1ec0e, 667,073 rows, Last-Modified 5 November 2026 08:14:53 GMT.

## Scores

| Bar | Probability given | Result | What the data shows |
|---|---|---|---|
| G1 | gate | held | All six columns present; newest report year 2024; all four CAMD plants (57865, 1571, 422, 58478) have rows in 2024 |
| P1 | 80% | held | Chalk Point 2024: SGT1 linked to 1571/GT1 only; no row links 61890/SGT1 |
| P2 | 70% | held | Glenarm 2024: STG5 linked to 422/GT5 only; no row links 422/ST1 |
| P3 | 70% | held | LEPA Unit No. 1 2024: STG1 linked to 58478/LEPA1 only; no row links 58478/LEPA2 |
| P4 | 60% | held | 42 candidate-years in which PUDL's EIA-860 table lists the candidate with a nameplate above zero (at least 10 needed); 0 of 42 linked |
| P5 | 55% | held | All three new candidates are in PUDL's EIA-860 table for 2021: 61890/SGT1 94 MW GT, 422/ST1 16 MW CA, 58478/LEPA2 17.1 MW CA, all operating |

Sanity check (not a prediction): the Antelope Elk lead stands in 2024 (`sanity_elk_2024_persists: true`), as [xwcap.md](xwcap.md) had shown.

## Each lead, year by year

| Lead | CAMD generator(s) | Linked in PUDL to | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|---|---|
| Antelope Elk | ELK1, ELK2, ELK3 | 57865/E01, E02, E03 (9.3 MW IC each) | stands | stands | stands | stands | stands | stands | stands |
| Chalk Point | SGT1 | 1571/GT1 (16 MW GT) | stands | stands | stands | no row | no row | stands | stands |
| Glenarm | STG5 | 422/GT5 (71 MW CT) | stands | stands | stands | stands | stands | stands | stands |
| LEPA Unit No. 1 | STG1 | 58478/LEPA1 (57 MW CT) | stands | stands | stands | stands | stands | stands | stands |

"No row" means PUDL's crosswalk has no row for CAMD generator SGT1 that year, so the lead cannot stand or fall; 26 of the 28 lead-years stand and the other 2 have no row. No row in any report year names EIA plant 58835 or 61890 at all.

The candidates in PUDL's EIA-860 table, by report year:

| Candidate | First year listed | Nameplate in 2018 to 2024 | Prime mover | Status in 2018 to 2024 |
|---|---|---|---|---|
| 58835/ELK1 Elk Station | 2013 (status L), operating from 2015 | 202 MW to 2020, 199.8 MW from 2021 | GT | operating |
| 58835/ELK2 Elk Station | 2014 (status L), operating from 2016 | 202 MW to 2020, 199.8 MW from 2021 | GT | operating |
| 58835/ELK3 Elk Station | 2014 (status L), operating from 2016 | 202 MW to 2020, 199.8 MW from 2021 | GT | operating |
| 61890/SGT1 NRG Chalk Point CT | 2017 | 94 MW | GT | operating |
| 422/ST1 Glenarm | 2015 (status V), operating from 2016 | 16 MW | CA | operating |
| 58478/LEPA2 LEPA Unit No. 1 | 2016 | 17.1 MW | CA | operating |

## What else the rows show (read after scoring, not pre-registered)

- **Chalk Point has a second link of the same kind in 2023 and 2024.** In 2018 to 2020, CAMD unit 1's generator ST1 is linked to EIA 1571/ST1. In 2021 and 2022 there is no row for CAMD unit 1 (and none for SMECO/SGT1). In 2023 and 2024, CAMD unit 1's ST1 is linked to EIA 1571/GT1, the same 16 MW turbine SGT1 is linked to. So in 2023 and 2024 two CAMD units (1 and SMECO) share one 16 MW EIA generator. This fits the one Chalk Point group that [xwcap.md](xwcap.md) found in 2024 (two CEMS units linked to one generator, CEMS peak 5.312 times its capacity), whose members were not read there. Not read here: whether EIA-860 lists 1571/ST1 in 2023 and 2024, and whether CAMD unit 1 still reports emissions.
- **PUDL's EIA-860 table has no row for 1571/GT1 in 2021 and 2022** (it has rows from 2001 to 2020 and from 2023 to 2026), the same two years in which the crosswalk has no row for SGT1. Open Grid Emissions' hand-made crosswalk ([`epa_eia_crosswalk_manual.csv`](https://github.com/singularity-energy/open-grid-emissions/blob/main/src/oge/reference_tables/epa_eia_crosswalk_manual.csv), read 6 November 2026) explains the gap: it maps CAMD 1571 SMECO to EIA 65285/GT1 for 2021 and 2022, with the note that this generator "switches plant IDs for two years then switches back", and CAMD units 1 and 2 to EIA 65285/ST1 and ST2 from 2021. **This cuts against the Chalk Point lead:** someone at Open Grid Emissions has already matched SMECO to a GT1 by hand. Their note is about the plant id, not the size gap (93 MW in CAMD against 16 MW for 1571/GT1), so the lead still needs a person who knows the plant. That file has no row for the other three leads' plants (57865, 58835, 422, 58478) or for 61890.
- **At Glenarm and LEPA, both generators of the combined cycle go to the combustion turbine every year.** Glenarm's CAMD unit GT5 has CTG5 and STG5, and both are linked to 422/GT5 in all seven years; LEPA's CAMD unit CC01 has CTG1 and STG1, and both are linked to 58478/LEPA1 in all seven years. The steam turbines EIA lists for these combined cycles (422/ST1, 58478/LEPA2, prime mover CA) have no crosswalk row in any year.

## What happens next

As the plan says, because P1, P2 and P3 held, MV2 will offer the leads to PUDL in one issue that says no person has checked them; PUDL decides what to change. Before that, a second pre-registered check ([xwdev-plan.md](xwdev-plan.md), id xwdev-1) asks whether the leads also stand in the crosswalk on the `development` branch of EPA's repository, which was regenerated in June 2025 and has not been released. Basing PUDL's next crosswalk update on that branch is one of the options Catalyst lists in [camd-eia-crosswalk-latest#7](https://github.com/catalyst-cooperative/camd-eia-crosswalk-latest/issues/7).

## Limits

- A lead is a size match, not proof; someone who knows the plants has to confirm it.
- PUDL's crosswalk table does not say which matching step made each link; that the links come from step 1d is taken from EPA's 2022 file ([step1d.md](step1d.md)).
- PUDL's tables change nightly; this run read the builds named above. PUDL's data is downloaded at run time and not stored here.
- No person has checked the code or the results by hand.

## Files

- [`tools/xwpudl/xwpudl.py`](../tools/xwpudl/xwpudl.py) 0.1.0, its tests and the plan-gated fetch; the plan: [xwpudl-plan.md](xwpudl-plan.md).
