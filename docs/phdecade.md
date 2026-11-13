# Does only the current install decade change from one PHMSA report year to the next? (result of phdecade-1)

Result of pre-registration phdecade-1 ([plan](phdecade-plan.md), live on this repository's main branch from 04:38:08 UTC on 11 November 2026, before the job read any data). The job `phdecade-v1` ran `tools/phdecade/phdecade.py` 0.1.0 from the plan's commit on 13 November 2026, 02:06:24-02:06:26 UTC; its unit tests passed first.

MV2 of Munim, Inc., 13 November 2026 (UTC); made with AI agents working in MV2's name; no person has checked these results by hand. Text and data CC BY 4.0; code Apache-2.0.

**5 of the 6 predictions held (P2-P6); P1 failed.** [pudl#5505](https://github.com/catalyst-cooperative/pudl/issues/5505) plans a table of yearly pipeline installations built by comparing each operator's install-decade report with the one from the year before, and expects that only the current decade changes. In PUDL's `core_phmsagas__yearly_distribution_by_install_decade`, 2015-2025:

- **Older decades change in 4,200 of 14,430 operator-year pairs (29.11%)**, fewer than the 40% we predicted (P1 failed). 2,545 pairs (17.64%) change by more than 1 mile and 1%.
- **Those pairs are the big systems:** they hold 12,216,055 of 13,195,131 miles of main (92.58%) in the first year of the pair (P2).
- **Older decades lose mains on net: -44,619 miles** over the ten year pairs (P3), while the current decade gains 188,698 miles. Differencing the totals gives 144,079 miles; differencing the current decade gives 188,698. The gap is 23.6% of the current-decade figure.
- **The older decades' absolute changes add up to 325,556 miles, 1.68 times the current decade's 194,115** (P4). Much of this is pipe moving between buckets, which nets out.
- **The four oldest buckets (pre_1940 to the 1960s) lose mains on net in 8 of the 10 year pairs** (P5).
- **Older-decade services change in 6,608 pairs (45.79%)** (P6).

So the assumption in #5505 does not hold for most of the pipe: the current decade's change is new pipe minus any removed pipe from that decade, and the change in the total also includes retirements and re-dating of older pipe.

## Input

PUDL's nightly `core_phmsagas__yearly_distribution_by_install_decade` (CC BY 4.0, Catalyst Cooperative): md5 `e436f16d09ced956c2f8172989ab5b9d`, 1,034,817 bytes, Last-Modified 12 Nov 2026 08:25:35 GMT. It has 324,580 rows from report years 2004-2025, 170,075 of them in 2015-2025. Values are PHMSA's, as operators reported them, with PUDL's clipping of negatives to 0.

In 2015-2025 there are 1,657 keys (operator, commodity, state) and 16,121 key-years. One key-year (in 2025) has more than one report and is left out.

## Gates

| Gate | Measured | Held |
|---|---|---|
| G1 file and eight columns | no missing columns | yes |
| G2 at least 2,000 pairs, at least 100 in 8 of 10 year pairs | 14,430 pairs; 10 of 10 year pairs with at least 100 | yes |

Pairs by first year: 2015: 1,456; 2016: 1,470; 2017: 1,477; 2018: 1,465; 2019: 1,443; 2020: 1,429; 2021: 1,427; 2022: 1,429; 2023: 1,424; 2024: 1,410.

## Predictions

| Prediction (probability) | Bar | Measured | Held |
|---|---|---|---|
| P1 (75%) pairs with an old mains change | at least 40% | 4,200 of 14,430 (29.11%) | **no** |
| P2 (85%) year-t mains miles in those pairs | at least 80% | 12,216,055 of 13,195,131 (92.58%) | yes |
| P3 (75%) net mains change of old buckets | below -0.001 miles | -44,619 miles | yes |
| P4 (75%) old buckets' absolute change / current bucket's | at least 25% | 325,556 / 194,115 (167.71%) | yes |
| P5 (70%) year pairs where pre_1940-1960s lose mains on net | at least 8 of 10 | 8 of 10 | yes |
| P6 (65%) pairs with an old services change | at least 40% | 6,608 of 14,430 (45.79%) | yes |

**Why P1 failed:** of the 10,230 pairs with no old mains change, 3,075 (21.31% of all pairs) changed nothing at all, and the other 7,155 changed only current-decade mains or services counts. Together these pairs hold 7.42% of the miles, so they are mostly small systems. We expected more of them to touch older buckets than did. P1 is reported as failed and is not re-scored.

## What else the table shows (reported, not scored)

**Old buckets, summed over all ten year pairs** (a bucket is "old" when it is not the decade of the second year: the 2010s are old only for pairs starting 2019-2024, the 2020s only for pairs starting 2015-2018):

| Bucket | Pairs | Pairs with miles | Mains changed | Services changed | Net mains (miles) | Gross mains (miles) | Net services |
|---|---|---|---|---|---|---|---|
| `pre_1940` | 14,430 | 1,915 | 1,391 | 1,352 | -18,515 | 33,262 | -571,234 |
| `1940s` | 14,430 | 2,361 | 1,417 | 1,407 | -2,586 | 10,001 | -364,908 |
| `1950s` | 14,430 | 5,072 | 2,222 | 2,531 | -8,009 | 28,742 | -1,037,547 |
| `1960s` | 14,430 | 7,766 | 2,623 | 3,524 | -3,859 | 36,011 | -1,383,286 |
| `1970s` | 14,430 | 6,732 | 2,382 | 3,101 | -4,683 | 27,142 | -1,374,223 |
| `1980s` | 14,430 | 7,856 | 2,360 | 3,193 | 6,336 | 29,260 | -544,420 |
| `1990s` | 14,430 | 9,544 | 2,424 | 3,289 | 6,706 | 29,759 | -296,766 |
| `2000s` | 14,430 | 10,069 | 2,334 | 3,066 | 657 | 19,590 | -381,373 |
| `2010s` | 8,562 | 6,260 | 1,513 | 1,888 | 6,746 | 14,510 | 262,507 |
| `2020s` | 178 | 0 | 0 | 3 | 0 | 0 | 4 |
| `unknown_decade` | 14,429 | 3,959 | 1,737 | 2,362 | -27,411 | 97,279 | -545,859 |

- `unknown_decade` has the largest gross change of any old bucket (97,279 miles), then the `1960s` (36,011) and `pre_1940` (33,262).
- Net mains change of the four oldest buckets by first year: 2015: 1,618; 2016: -8,104; 2017: -2,353; 2018: -4,422; 2019: -4,597; 2020: -4,404; 2021: 500; 2022: -4,165; 2023: -3,135; 2024: -3,907.
- The current decade went down in 208 pairs.
- **After the fact (not pre-registered): services.** Summed over the ten year pairs, the current decade gains 12,547,040 services and the old buckets lose 6,237,105 on net (49.7% of the current-decade gain). For services, the two ways of differencing differ by about half. One reading, not checked: replaced service lines leave the old decades and appear in the current one, so a table built on the current decade would count replacements as installations.
- **After the fact (not pre-registered): a decade keeps changing after it closes.** Net mains change of the `2010s` bucket by first year: 2019: 4,184; 2020: 1,422; 2021: 1,441; 2022: 202; 2023: -437; 2024: -66. It still grew by 4,184 miles from the 2019 report to the 2020 report. PHMSA's 2018 revision of the form (F 7100.1-1) has decade columns only up to 2010-2019. We did not check which form revision first added a 2020-2029 column; operators filing on an older form could explain part of this.
- **After the fact (not pre-registered): some of the largest moves look like re-dating.** Operator 4473 (natural gas, TX) went from 0 to 5,518.72 miles in `unknown_decade` from 2016 to 2017, while its `1950s` went from 2,338 to 6.23. From 2021 to 2022 its `unknown_decade` went from 5,162.94 to 3.79 while its `pre_1940` went from 8.12 to 3,712.2. Whether these are corrections, re-dating or something else was not checked.

## What this means for pudl#5505

- Dropping the older decades and differencing only the current one would treat the current-decade change as installations. Over 2015-2025 that is 188,698 miles of main, against a change in total main of 144,079.
- One possible approach, not tested: keep the current-decade change and the older decades' net change as separate columns, so users can tell gross additions apart from net growth, and flag operator-years whose older buckets move by a material amount.
- The year after a decade closes needs care: the closed decade still changes for a few reports.
- None of this has been checked against PHMSA's raw files or forms.

## Limits

- This measures PUDL's published table, not PHMSA's raw files. A change between two years can be a real retirement, a correction, a transfer of pipe between operators or a typing error. The table cannot tell these apart, so this counts changes and does not explain them.
- Keys are matched by operator id, commodity and state text. An operator that changes its id or its state list, or splits a report, drops out of the pairs. A merger shows as a jump in one key.
- PUDL clips negative decade values to 0, so a bucket an operator reported as negative shows as 0 here.
- PUDL's nightly table changes from night to night; the md5 and Last-Modified are above.
- The probabilities were our own before-the-fact guesses.

## Files

- [data/phdecade-run.json](../data/phdecade-run.json): the job's full output, unchanged.
- [data/phdecade-by-year-decade.csv](../data/phdecade-by-year-decade.csv): every year pair and bucket with its counts and sums, unchanged.
- [data/phdecade-pairs.csv](../data/phdecade-pairs.csv): every pair with its totals, current-decade change and old-bucket changes, unchanged.
- [data/phdecade-top-old-changes.csv](../data/phdecade-top-old-changes.csv): the 300 largest old-bucket mains changes, unchanged.
- [test_phdecade_result.py](../test_phdecade_result.py) checks every number on this page against those files.
