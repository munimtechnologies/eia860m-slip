# 2025 scored early on Form EIA-860: three stated ranges missed, and a method that reproduces Table 4.6 to the decimal

MV2 of Munim, Inc., 16 October 2026 (0.2.5). Made with AI agents working in MV2's name. Text CC BY 4.0, code (`eia860_final.py`) Apache-2.0.

`headline-plans.md` and `headline-retirements.md` stated three ranges for EIA's final 2025 figures before we read them. The official figure will be the Electric Power Annual 2025, Table 4.6, which is not out yet (its live page still showed 2024 on 16 October 2026). That table is built from Form EIA-860, and EIA released the final 2025 EIA-860 on 10 September 2026. So we scored the ranges early, on the EIA-860 file itself, after first checking that our method reproduces Table 4.6 for the two previous years.

**Honest framing.** The ranges were written down (15-16 October 2026) before *we* read the 2025 file, not before the data existed: EIA had already published it. Nobody on this project had looked at it. That is weaker than a forecast made before the data existed, and it is the only claim we make.

## The method, and the calibration gate

`eia860_final.py` reads `3_1_Generator_Y<year>.xlsx` from EIA's EIA-860 zip and sums net summer capacity:

- additions: Operable generators whose Operating Year is the data year;
- retirements: generators with status RE on the Retired sheet whose Retirement Year is the data year.

Before any 2025 number was used, the rule had to reproduce Table 4.6 totals for 2023 and 2024 within 1% (written down in advance). It reproduced every row we checked **exactly, to the printed 0.1 MW**: totals, solar, wind, gas and nuclear additions, and total, coal and gas retirements, in both years (16 of 16 rows; output in [`eia860-final-output.md`](eia860-final-output.md), full sums in [`../data/eia860_final_2025.json`](../data/eia860_final_2025.json)). We expected additions to calibrate within 0.5% and retirements a little worse; both were exact.

## 2025 (net summer MW)

| item | EIA-860 2025 | January plan | of plan | EIA first count | revision | stated range | in range |
|---|---|---|---|---|---|---|---|
| additions, total | 56,609.0 | 63,000 | 89.9% | 53,000 | +6.8% | 55,000-55,500 | no (1.1 GW above) |
| additions, solar | 29,459.1 | 32,500 | 90.6% | 27,200 | +8.3% | 27,900-28,000 | no (1.5 GW above) |
| additions, battery | 16,306.9 | 18,200 | 89.6% | 15,000 | +8.7% | | |
| additions, wind | 6,082.0 | 7,700 | 79.0% | < 5,900 | | | |
| additions, gas | 4,589.6 | 4,400 | 104.3% | | | | |
| retirements, total | 5,114.4 | 12,300 | 41.6% | 4,600 | +11.2% | 5,200-5,500 | no (0.09 GW below) |
| retirements, coal | 2,688.4 | 8,100 | 33.2% | 2,600 | +3.4% | | |
| retirements, gas | 859.6 | 2,600 | 33.1% | | | | |

1,090 generators were added and 206 retired. No nuclear unit came online in 2025 (2023 and 2024 each had 1,114 MW).

## Scoring

All three stated ranges missed.

- **Additions** came in 1.1 GW above the top of 55.0-55.5 GW. The range assumed 2025's first count would be revised up like 2023's and 2024's (+4.7% and +3.8%). It was revised up by 6.8%. Solar was revised by 8.3% against 2.7-3.1% before, so the solar range missed by the most.
- **Retirements** came in 0.09 GW below 5.2-5.5 GW. The range assumed the +13% to +20% revisions seen for 2023 and 2024. The revision was +11.2%, and coal only +3.4%.
- The other expectations written down before the run: the gate passed (as expected); retirements did *not* calibrate worse than additions (wrong); total additions landed outside even the wider 54-56.5 GW band (wrong, by 0.1 GW); retirements were revised above 4.8 GW (right); coal stayed under 45% of plan (right: 33%).

**What we learn.** Two years of revisions were too thin a base. They were the only years built on the December inventory, which is why we used them, but they gave ranges far narrower than the year-to-year spread. Over 2023-2025 the December-inventory first count of total additions was revised up by 3.8% to 6.8% (1.1% to 8.7% by technology), and first counts of retirements by -1% to +21% (totals and coal, 2021-2025). That is the band the record now supports. That is wide enough that the first count says little more than "a bit low".

**What does not change.** 2025 is still the year retirements fell furthest short of plan (42%, against 98-174% in 2020-2024), and coal's 33% is still the first coal shortfall in this record (back to 2018). Additions at 90% of plan were the best since 2021 (97%): over 2020-2025, 250.7 of 308.1 GW planned was added in the planned year (81%).

## Stated now, to be scored against the Electric Power Annual 2025

Because the method reproduced 2023 and 2024 to the decimal, we expect Table 4.6 in the Electric Power Annual 2025 to print, in net summer MW: **total additions 56,609.0, solar 29,459.1, wind 6,082.0, natural gas 4,589.6; total retirements 5,114.4, coal 2,688.4, natural gas 859.6**, each within 0.1%. If EIA revises the 2025 EIA-860 data before the Annual (the Electric Power Annual 2020 was itself re-released once), a miss would point to that revision rather than to a broken method. We will check when the Annual appears.

## 2026, by the same rule

The 2026 ranges in `headline-plans.md` and `headline-retirements.md` take each 2026 plan times the lowest and highest actual / plan of 2023-2025. Those ranges were published before any 2026 figure existed, and **they are the ones that will be scored** (additions 63.8-72.3 GW from 0.2.1 and 66.8-72.3 GW from 0.2.3; retirements 4.1-19.1 GW). For the record, the same rule with 2025's EIA-860 values in place of first counts now gives: additions 66.8-77.3 GW (solar 28.2-39.3, battery 16.3-21.5; wind 7.4-13.0 and gas 5.3-7.3 unchanged); retirements 4.6-19.1 GW (coal 2.1-11.0 unchanged; gas 1.5-8.2). No 2026 information went into this update; it is reported so that nobody mistakes it for the scored range.

## Limits

- This scores ranges against EIA-860, not yet against the Electric Power Annual. The calibration makes them very likely the same, not certainly.
- The rule counts a generator's primary energy source (Energy Source 1). Batteries are energy source MWH; Table 4.6 puts them in "Other Energy Sources", so the battery row has no Table 4.6 check.
- The 2025 plans and first counts are EIA's rounded article figures (Today in Energy 64364, 67205, 67206).
- One oddity, not yet explained: the eight coal generators retired in 2025 sum to more summer capacity (2,688.4 MW) than nameplate (2,626.0 MW). In 2023 and 2024 retired coal summer capacity was 89-90% of nameplate. At least one 2025 row probably carries a summer rating above its nameplate. We have not listed the rows yet.

## Reproduce

```
pip install pandas openpyxl
python -m unittest -v test_eia860_final
python eia860_final.py --data-dir data --out-dir out
```

It downloads the three EIA-860 zips (2023, 2024, 2025; about 24 MB each) from eia.gov if `--data-dir` does not hold them. EIA data is public domain.
