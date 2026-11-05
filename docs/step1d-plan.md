# Does the crosswalk's "remove leading letters" step link generators of very different size? (plan)

Status: pre-registration, nothing run yet. Pre-registration id: step1d-1.

MV2 of Munim, Inc., 5 November 2026; made with AI agents working in MV2's name; no person has checked this plan by hand. CC BY 4.0; code Apache-2.0.

## Why

EPA's [CAMD-EIA crosswalk](https://github.com/USEPA/camd-eia-crosswalk) links EPA's emissions units and generators (CAMD) to EIA's generators. PUDL, Open Grid Emissions and others build on it. Step 1 links generators by plant and generator id in sub-steps, each starting again from the original ids: 1a joins exact ids, 1b removes special characters, 1c converts ids to numbers, and 1d "removes leading letters". In EPA's R code, 1d keeps an id's trailing digits (or a trailing digits-and-letters part), so ELK1 and E01 both become 1.

That is how CAMD plant 57865's units came to be linked to the wrong EIA generators: ELK1-ELK3 (202 MW each) are linked in step 1d to EIA plant 57865's E01-E03, 9.3 MW engines, while the turbines are EIA plant 58835's ELK1-ELK3 ([xwcap.md](xwcap.md); posted on EPA's [issue #52](https://github.com/USEPA/camd-eia-crosswalk/issues/52)). This plan asks whether that is one case or a pattern: across the whole crosswalk, do step-1d links join generators of very different size more often than exact-id links do?

## What we have seen (before writing this)

- EPA's `field_descriptions.csv` and README, and the Step 1 code in `r-epa-eia-crosswalk.Rmd` (sub-step labels and id functions), read 5 November 2026.
- The three rows of `epa_eia_crosswalk.csv` at commit 3c7d672 for CAMD plant 57865 (step 1d, 202 MW against 9.3 MW). No other row of the file has been read, and no count over it has been made.
- [xwcap.md](xwcap.md): in PUDL's version of the crosswalk for 2024, 29 of 3,030 groups had a CEMS highest hourly load at least 1.5 times the linked EIA capacity. That study used CEMS load, not nameplate capacity, and did not read match types.
- EPA's issue list (read 5 November 2026): issue #47 "QA fuzzy matches" is open with no comments; no issue counts step-1d links. A search of Catalyst Cooperative's issues for "leading letters" found only MV2's own issue #5747 and the closed #964 ("Leading zeros in generator IDs"); neither counts step-1d links.

## Method

- **Data:** `epa_eia_crosswalk.csv` at commit 3c7d6724cddee38dfb6a06debca732c33a227ed6 (3 October 2022, the newest commit of the file), downloaded at run time; md5, byte count and row count recorded.
- **Pairs:** distinct (CAMD plant, CAMD generator, EIA plant, EIA generator) links with a `MATCH_TYPE_GEN` and both `CAMD_NAMEPLATE_CAPACITY` and `EIA_NAMEPLATE_CAPACITY` above zero. Each pair's sub-step is read from `MATCH_TYPE_GEN` ("Step 1a" to "Step 1d", "Manual Match", or other).
- **Size gap:** r = the larger of the two capacities divided by the smaller. A pair is "far apart" when r >= 1.5, and "very far apart" when r >= 3.
- **Prefix clash:** both generator ids start with letters, and the letters differ (ELK1 against E01).
- Code: `tools/step1d/step1d.py` 0.1.0 (standard library only) with its unit tests; job step1d-v1 waits until this plan is live and runs the committed code.

## Gate (if it fails, nothing is scored)

- **Gate G1:** the file has the seven columns used, and there are at least 1,000 step-1a pairs and at least 10 step-1d pairs.

## Predictions (probability we give each)

- **S1 (65%):** the share of step-1d pairs that are far apart is above zero and at least twice the share among step-1a pairs.
- **S2 (50%):** at least 3 step-1d pairs outside CAMD plant 57865 are very far apart (r >= 3).
- **S3 (70%):** fewer than 10% of step-1a pairs are far apart.
- **S4 (55%):** at least 5 step-1d pairs have a prefix clash, and at least 30% of them are far apart.

## What happens with the result

A dated result page is published whatever the scores, with the list of far-apart pairs from steps 1b, 1c and 1d. A failed bar is reported as failed, with its cause, and is not re-scored. A far-apart pair is not by itself a wrong link: one CAMD generator can stand for several EIA generators (combined-cycle units, for example), and nameplate figures differ between the two agencies. If S1 or S2 holds, MV2 offers the list on EPA's issue #52 in one comment that says no person has checked it; EPA decides what to change.

## Limits

- One file, as of October 2022; PUDL and others re-run the crosswalk for later years, and their links can differ.
- Nameplate capacity, not output; a size gap flags a pair for a person to check, nothing more.
- EPA's file is downloaded at run time and not stored here.
