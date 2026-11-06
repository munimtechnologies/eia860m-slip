# Which EIA generator fits each far-apart crosswalk link? The step1d look

Descriptive follow-up to [step1d.md](step1d.md) (result of pre-registration step1d-1). MV2 of Munim, Inc., 6 November 2026; made with AI agents working in MV2's name; no person has checked these results by hand. CC BY 4.0; code Apache-2.0.

**This look is descriptive, not pre-registered: it sets no bars and scores nothing.** step1d-1 flagged links in EPA's CAMD-EIA crosswalk whose two nameplate capacities differ by 1.5 times or more. A size gap says a link deserves a check; it does not say what the right link is. This look lists, for each flagged link, the EIA generators that EIA's September 2026 EIA-860M workbook shows near it, and whether any crosswalk row already links them.

**For all six far-apart step-1d links, exactly one EIA generator within 1.5 times of the CAMD nameplate, among those looked at (the linked EIA plant's generators and same-id generators in the same state), is linked by no crosswalk row, and its nameplate is within 5% of the CAMD figure.** Each is a lead for a person to check, not a finding.

## How it ran

- Job step1d-look-v1 ran on 6 November 2026 (09:46 to 09:51 UTC). It downloaded the committed `tools/step1d/step1d.py` 0.1.0 unchanged (md5 494a198670cbf7f6449327838be9b1c4) for the crosswalk pairs, then ran `tools/step1d_look/step1d_look.py` 0.1.0; its 8 unit tests passed.
- **Crosswalk:** `epa_eia_crosswalk.csv` at commit 3c7d6724cddee38dfb6a06debca732c33a227ed6 (still the newest commit in EPA's repository on 6 November 2026), md5 b7ec4b014ab66c2926f77ea86fa1ea16, 6,935 rows.
- **EIA workbook:** `september_generator2026.xlsx`, 14,013,970 bytes, md5 4c741eb77a5ccad5aca32ffe43f398af; sheets read: Operating 28,483, Planned 2,357, Retired 7,321, Canceled or Postponed 1,744 generators.
- **Which links:** every link with r >= 1.5 (r = larger nameplate / smaller), and every step-1d link whose two ids start with different letters (the S4 group in step1d.md).
- **Candidates:** every generator at the linked EIA plant, plus every EIA generator in the CAMD unit's state whose id is exactly the CAMD generator id. A "closer candidate" is one of these, other than the linked generator, with r < 1.5 against the CAMD nameplate. "Unlinked" means no crosswalk row links that EIA plant and generator.
- **Sanity check:** the look had to find EIA 58835/ELK1 as a closer candidate for Antelope Elk ELK1, as [xwcap.md](xwcap.md) reported; it did (`sanity_elk1_finds_58835: true`).

## Counts by group

| Group | Links | Linked EIA generator in the Sep 2026 workbook | With an unlinked closer candidate | With a same-id same-state EIA generator |
|---|---|---|---|---|
| 1d far apart (r >= 1.5) | 6 | 6 | 6 | 5 |
| 1d letters differ (r < 1.5) | 34 | 34 | 1 | 12 |
| 1b/1c far apart | 0 | 0 | 0 | 0 |
| 1a far apart | 24 | 24 | 11 | 20 |
| Manual Match far apart | 6 | 6 | 4 | 5 |

## The six far-apart step-1d links

| CAMD plant | CAMD unit / generator | CAMD MW | Linked EIA generator | Unlinked closer candidate in EIA-860M (Sep 2026) | r |
|---|---|---|---|---|---|
| 57865 Antelope Elk Energy Center, TX | 1 / ELK1 | 202 | 57865/E01, 9.3 MW, IC | 58835/ELK1 Elk Station, 199.8 MW, GT, operating | 1.011 |
| 57865 Antelope Elk Energy Center, TX | 2 / ELK2 | 202 | 57865/E02, 9.3 MW, IC | 58835/ELK2 Elk Station, 199.8 MW, GT, operating | 1.011 |
| 57865 Antelope Elk Energy Center, TX | 3 / ELK3 | 202 | 57865/E03, 9.3 MW, IC | 58835/ELK3 Elk Station, 199.8 MW, GT, operating | 1.011 |
| 1571 Chalk Point, MD | SMECO / SGT1 | 93 | 1571/GT1, 16 MW, GT | 61890/SGT1 NRG Chalk Point CT, 94 MW, GT, operating | 1.011 |
| 422 Glenarm, CA | GT5 / STG5 | 16.78 | 422/GT5, 71 MW, CT | 422/ST1 Glenarm, 16 MW, CA, operating | 1.049 |
| 58478 LEPA Unit No. 1, LA | CC01 / STG1 | 17 | 58478/LEPA1, 57 MW, CT | 58478/LEPA2 LEPA Unit No. 1, 17.1 MW, CA, operating | 1.006 |

The six fall into two shapes:

- **The right generator sits under another EIA plant id (Antelope Elk, Chalk Point).** EIA lists a generator with exactly the CAMD id, in the same state, at a different plant: Elk Station (58835) for ELK1 to ELK3, and NRG Chalk Point CT (61890) for SGT1. No crosswalk row links either. Step 1d, which removes leading letters, instead met a same-number generator at the CAMD plant's own EIA id (ELK1 with E01, SGT1 with GT1).
- **The steam part of a combined cycle is left unlinked (Glenarm, LEPA).** CAMD lists one unit with two generators, a combustion turbine and a steam turbine (Glenarm GT5: CTG5 59.1 MW and STG5 16.78 MW; LEPA CC01: CTG1 59 MW and STG1 17 MW). Step 1d links both to EIA's combustion turbine (GT5, LEPA1), because both ids end in the same digit. EIA's steam part of the same combined cycle (prime mover CA: Glenarm ST1, LEPA2) has no crosswalk row.

What each lead would change, if a person confirms it: Antelope Elk ELK1 to ELK3 to EIA 58835/ELK1 to ELK3; Chalk Point SGT1 to EIA 61890/SGT1; Glenarm STG5 to EIA 422/ST1; LEPA STG1 to EIA 58478/LEPA2.

## What the other groups show

- **1d letters differ (34):** the one unlinked closer candidate (for LEPA's CTG1) is a same-id generator at another plant, ExxonMobil Baton Rouge (10690/CTG1, 85.3 MW, r = 1.446), not a lead: LEPA's CTG1 (59 MW) already sits within 1.04 times of its linked LEPA1 (57 MW). The other 33 have either no closer candidate or only ones that other crosswalk rows already link, such as the eight Southeast Chicago turbines that all share one nameplate.
- **1a far apart (24):** in all 11 links with an unlinked closer candidate, every such candidate is at another plant and only shares a short id, such as hydro units numbered 2 across California for Woodland's generator 2. These are not leads; a same-id rule says little when ids are plain numbers.
- **Manual Match far apart (6):** all six are one-to-two splits rather than size gaps. Dan E Karn's CAMD units 1 and 2 (265 MW each) each link to two EIA generators of 136 MW (1A and 1B; 2A and 2B), and Marshfield's CAMD 1A and 1B (27.5 MW each) both link to EIA M1 (60.4 MW). The summed nameplates roughly agree (272 against 265 MW; 55 against 60.4 MW). Their unlinked closer candidates (four links, all at Dan E Karn) are wind and pumped-storage generators at other plants: not leads.
- Every linked EIA generator in the four non-empty groups (70 links) is still in the September 2026 workbook, on one of its four sheets.

## Limits

- Descriptive, not pre-registered: the groups and the 1.5 bound were fixed before the run, but nothing was predicted and nothing is scored.
- A closer candidate matches on nameplate size and, for some, on id. Not read here: operating dates, owners, fuels in detail, or whether EIA plant 58835 or 61890 existed in the EIA data the crosswalk was built from. EIA's technology label for both Chalk Point candidates (1571/GT1 and 61890/SGT1) is petroleum liquids, while CAMD reports pipeline natural gas for SGT1, so fuel does not separate them.
- The EIA workbook is from September 2026; the crosswalk is from October 2022. PUDL and others re-run EPA's crosswalk on later EIA years, and their links can differ; not read here.
- EPA's file and EIA's workbook are downloaded at run time and not stored here.
- No person has checked the code or the results by hand.

## Files

- [`tools/step1d_look/step1d_look.py`](../tools/step1d_look/step1d_look.py) and its tests; it imports `tools/step1d/step1d.py` 0.1.0.
- The plan and result this follows: [step1d-plan.md](step1d-plan.md), [step1d.md](step1d.md).
