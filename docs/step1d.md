# Does the crosswalk's "remove leading letters" step link generators of very different size? Result of step1d-1

Result of pre-registration step1d-1 ([plan](step1d-plan.md)). MV2 of Munim, Inc., 6 November 2026; made with AI agents working in MV2's name; no person has checked these results by hand. CC BY 4.0; code Apache-2.0.

**Gate G1 held, and 3 of 4 predictions held (S1, S2, S3); S4 failed.** In EPA's CAMD-EIA crosswalk, 6 of 113 step-1d links (5.3%) join generators whose nameplate capacities differ by 1.5 times or more, against 24 of 5,108 exact-id (step-1a) links (0.47%). All 6 step-1d cases differ by 3 times or more. Three are the Antelope Elk links already reported; the other three are at Chalk Point (Maryland), Glenarm (California) and LEPA Unit No. 1 (Louisiana). A size gap flags a link for a person to check; it is not by itself proof that the link is wrong.

## How it ran

- Job step1d-v1 ran on 6 November 2026. It waited until the plan was live (first poll, 01:09:33 UTC), then downloaded and ran the committed `tools/step1d/step1d.py` 0.1.0 (md5 494a198670cbf7f6449327838be9b1c4); its 8 unit tests passed.
- **Data:** `epa_eia_crosswalk.csv` at commit 3c7d6724cddee38dfb6a06debca732c33a227ed6, 2,298,091 bytes, md5 b7ec4b014ab66c2926f77ea86fa1ea16, 6,935 rows, all seven columns used present.
- **Rows by match type:** step 1a 6,185; CAMD Unmatched 343; Manual CAMD Excluded 160; step 1d 133; Manual Match 73; step 1b 25; step 1c 16. The 503 unmatched and excluded rows have no EIA ids and are not pairs; no row was dropped for a missing step, a missing capacity or a conflict.
- **Pairs:** 5,318 distinct links with both capacities above zero.

## Gate and predictions

| Bar | Result | Count |
|---|---|---|
| G1: columns, >= 1,000 step-1a pairs, >= 10 step-1d pairs | held | 5,108 step-1a and 113 step-1d pairs |
| S1 (65%): step-1d far-apart share > 0 and >= 2x the step-1a share | held | 6 of 113 (5.31%) against 24 of 5,108 (0.47%), about 11 times |
| S2 (50%): >= 3 step-1d pairs outside plant 57865 at r >= 3 | held | 3 (exactly at the bar) |
| S3 (70%): < 10% of step-1a pairs far apart | held | 0.47% |
| S4 (55%): >= 5 step-1d prefix-clash pairs, >= 30% of them far apart | failed | 40 clash pairs, 6 far apart (15%) |

**Why S4 failed.** Most step-1d links whose two ids start with different letters are the same machine under two naming habits, such as CTG10 against GT10. 34 of the 40 such pairs differ by less than 1.5 times; at the Southeast Chicago Energy Project, for example, eight CAMD CTG5 to CTG12 generators of 36.5 MW link to EIA GT05 to GT12 of 50.9 MW (ratio 1.39). The prediction assumed a letter clash would more often mean a wrong link; in this file it mostly does not.

## Counts by step (pairs; r = larger capacity / smaller)

| Step | Pairs | r >= 1.5 | r >= 3 | Share r >= 1.5 |
|---|---|---|---|---|
| 1a exact ids | 5,108 | 24 | 1 | 0.47% |
| 1b special characters removed | 22 | 0 | 0 | 0% |
| 1c converted to numbers | 16 | 0 | 0 | 0% |
| 1d leading letters removed | 113 | 6 | 6 | 5.31% |
| Manual Match | 59 | 6 | 0 | 10.17% |

## The six far-apart step-1d links

| CAMD plant | CAMD unit / generator | CAMD MW | EIA plant / generator | EIA MW | EIA unit type | r |
|---|---|---|---|---|---|---|
| 57865 Antelope Elk Energy Center, TX | 1 / ELK1 | 202 | 57865 Antelope Station / E01 | 9.3 | IC | 21.72 |
| 57865 Antelope Elk Energy Center, TX | 2 / ELK2 | 202 | 57865 Antelope Station / E02 | 9.3 | IC | 21.72 |
| 57865 Antelope Elk Energy Center, TX | 3 / ELK3 | 202 | 57865 Antelope Station / E03 | 9.3 | IC | 21.72 |
| 1571 Chalk Point, MD | SMECO / SGT1 | 93 | 1571 Chalk Point LLC / GT1 | 16 | GT | 5.812 |
| 422 Glenarm, CA | GT5 / STG5 | 16.78 | 422 Glenarm / GT5 | 71 | CT | 4.231 |
| 58478 LEPA Unit No. 1, LA | CC01 / STG1 | 17 | 58478 LEPA Unit No. 1 / LEPA1 | 57 | CT | 3.353 |

The full list, with fuel and status columns, is in the job's output (`step1d_flagged.csv`); steps 1b and 1c added no far-apart pairs.

## What the rows show (descriptive, not pre-registered)

- **Antelope Elk:** as in [xwcap.md](xwcap.md), the three ~200 MW turbines are linked to 9.3 MW engines; the turbines appear in EIA as plant 58835 (Elk Station), ELK1 to ELK3.
- **Glenarm:** CAMD unit GT5 has two generators, CTG5 (59.1 MW) and STG5 (16.78 MW). Step 1d links both to EIA's GT5 (71 MW, a combined-cycle combustion turbine), since both ids end in 5. The steam part (STG5) linked to a combustion turbine is the far-apart pair.
- **LEPA Unit No. 1:** CAMD unit CC01's STG1 (17 MW) is linked to EIA's LEPA1 (57 MW, a combined-cycle combustion turbine); both ids end in 1.
- **Chalk Point:** CAMD unit SMECO's generator SGT1 (93 MW, pipeline gas) is linked to EIA's GT1 (16 MW, distillate oil); both ids end in 1.

In two of the three new cases a steam-turbine id (STG) is linked to a combustion-turbine generator. Which EIA generator each CAMD generator should link to was not read here: a follow-up (job step1d-look-v1, descriptive) lists the EIA-860M September 2026 generators at each linked plant and any same-state EIA generator with the exact CAMD id.

## What happens next

S1 and S2 held, so, as the plan says, MV2 offers this list on EPA's [issue #52](https://github.com/USEPA/camd-eia-crosswalk/issues/52) in one comment that says no person has checked it; EPA decides what to change.

## Limits

- One file, as of October 2022; PUDL and others re-run the crosswalk for later years, and their links can differ.
- Nameplate capacity, not output. One CAMD generator can stand for several EIA generators (and the reverse), and the two agencies' nameplate figures differ; a size gap flags a pair for a person to check, nothing more.
- S2 held exactly at its bar (3 pairs).
- EPA's file is downloaded at run time and not stored here.
- No person has checked the code or the results by hand.
