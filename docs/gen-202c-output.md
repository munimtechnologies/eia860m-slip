# Net generation of the plants under DOE 202(c) orders

MV2 of Munim, Inc. (made with AI agents). gen_202c 0.1.0. EIA-923 monthly net generation via PUDL, last month with data 2026-06. Baseline: same calendar month, 2021-2024 mean.

| plant | MW | window | months | net MWh | baseline MWh | ratio | CF | CF baseline | idle months |
|---|---|---|---|---|---|---|---|---|---|
| J.H. Campbell | 1330.5 | 2026 | 6 | 1,766,053 | 3,370,852 | 0.524 | 30.6% | 58.3% | 0 |
| J.H. Campbell | 1330.5 | since first order | 13 | 5,410,749 | 8,465,147 | 0.639 | 42.9% | 67.1% | 0 |
| Centralia | 670.0 | 2026 | 6 | 0 | 1,280,930 | 0.000 | 0.0% | 44.0% | 6 |
| Centralia | 670.0 | since first order | 6 | 0 | 1,280,930 | 0.000 | 0.0% | 44.0% | 6 |
| Craig | 427.0 | 2026 | 6 | 56,782 | 1,076,411 | 0.053 | 3.1% | 58.0% | 5 |
| Craig | 427.0 | since first order | 6 | 56,782 | 1,076,411 | 0.053 | 3.1% | 58.0% | 5 |
| F.B. Culley | 90.0 | 2026 | 6 | 48,923 | 93,946 | 0.521 | 12.5% | 24.0% | 1 |
| F.B. Culley | 90.0 | since first order | 6 | 48,923 | 93,946 | 0.521 | 12.5% | 24.0% | 1 |
| Eddystone | 760.0 | 2026 | 0 | 0 | 0 |  |  |  | 0 |
| Eddystone | 760.0 | since first order | 7 | 18,651 | 26,575 | 0.702 | 0.5% | 0.7% | 5 |
| R.M. Schahfer | 722.0 | 2026 | 6 | 303,344 | 853,259 | 0.355 | 9.7% | 27.2% | 4 |
| R.M. Schahfer | 722.0 | since first order | 6 | 303,344 | 853,259 | 0.355 | 9.7% | 27.2% | 4 |
| Stanton Energy Center | 453.4 | 2026 | 0 | 0 | 0 |  |  |  | 0 |
| Stanton Energy Center | 453.4 | since first order | 0 | 0 | 0 |  |  |  | 0 |
| H.A. Wagner | 397.0 | 2026 | 1 | 8,233 | 281 | 29.299 | 2.9% | 0.1% | 0 |
| H.A. Wagner | 397.0 | since first order | 6 | 11,400 | 9,010 | 1.265 | 0.7% | 0.5% | 3 |

Combined, 2026 months: 31 plant-months, 2,183,335 MWh against a baseline of 6,675,679 MWh (ratio 0.327).

## Checks and predictions

```
{
 "C1": {
  "text": "data reach 2026-03 and every covered generator has a 2021-2024 value",
  "last": "2026-06",
  "no_base": [],
  "pass": true
 },
 "C2": {
  "text": "at least 6 of 8 plants have an included 2026 month",
  "plants": [
   "campbell",
   "centralia",
   "craig",
   "culley",
   "schahfer",
   "wagner"
  ],
  "pass": true
 },
 "G1": {
  "text": "combined 2026 ratio below 0.50",
  "ratio": 0.3271,
  "hit": true
 },
 "G2": {
  "text": "Centralia 2: net generation <= 0 in every reported 2026 month (>= 3 months)",
  "months": {
   "2026-01": 0.0,
   "2026-02": 0.0,
   "2026-03": 0.0,
   "2026-04": 0.0,
   "2026-05": 0.0,
   "2026-06": 0.0
  },
  "hit": true
 },
 "G3": {
  "text": "Campbell ratio over all full order months between 0.55 and 0.85",
  "ratio": 0.6392,
  "hit": true
 },
 "G4": {
  "text": "at least 5 plants have a 2026 ratio below 0.75",
  "ratios": {
   "campbell": 0.5239,
   "centralia": 0.0,
   "craig": 0.0528,
   "culley": 0.5208,
   "schahfer": 0.3555,
   "wagner": 29.2989
  },
  "below": [
   "campbell",
   "centralia",
   "craig",
   "culley",
   "schahfer"
  ],
  "hit": true
 },
 "G5": {
  "text": "Stanton 1 ratio over its full 2026 order months below 0.50",
  "months": 0,
  "ratio": null,
  "hit": null
 },
 "X1": {
  "text": "compared, not scored: Utility Dive's five-plant first quarter",
  "q1_2026": 1470565.0,
  "q1_2025": 4483857.0,
  "utility_dive": {
   "2026": 1500000.0,
   "2025": 4300000.0
  }
 }
}
```

## Month by month

| plant | month | order days | full | net MWh | baseline MWh | base years | 2025 MWh | included |
|---|---|---|---|---|---|---|---|---|
| campbell | 2025-05 | 9 | no | 656,694 | 477,882 | 4 | 656,694 | no |
| campbell | 2025-06 | 30 | yes | 615,812 | 767,319 | 4 | 615,812 | yes |
| campbell | 2025-07 | 31 | yes | 552,069 | 829,355 | 4 | 552,069 | yes |
| campbell | 2025-08 | 31 | yes | 498,016 | 806,623 | 4 | 498,016 | yes |
| campbell | 2025-09 | 30 | yes | 220,639 | 691,606 | 4 | 220,639 | yes |
| campbell | 2025-10 | 31 | yes | 619,681 | 720,410 | 4 | 619,681 | yes |
| campbell | 2025-11 | 30 | yes | 535,898 | 639,176 | 4 | 535,898 | yes |
| campbell | 2025-12 | 31 | yes | 602,581 | 639,808 | 4 | 602,581 | yes |
| campbell | 2026-01 | 31 | yes | 586,859 | 782,348 | 4 | 960,164 | yes |
| campbell | 2026-02 | 28 | yes | 394,703 | 565,236 | 4 | 847,578 | yes |
| campbell | 2026-03 | 31 | yes | 145,447 | 535,784 | 4 | 702,630 | yes |
| campbell | 2026-04 | 30 | yes | 62,940 | 242,282 | 4 | 857,282 | yes |
| campbell | 2026-05 | 31 | yes | 241,387 | 477,882 | 4 | 656,694 | yes |
| campbell | 2026-06 | 30 | yes | 334,717 | 767,319 | 4 | 615,812 | yes |
| centralia | 2025-12 | 16 | no | 84,115 | 278,909 | 4 | 84,115 | no |
| centralia | 2026-01 | 31 | yes | 0 | 350,528 | 4 | 430,197 | yes |
| centralia | 2026-02 | 28 | yes | 0 | 329,016 | 4 | 340,594 | yes |
| centralia | 2026-03 | 31 | yes | 0 | 354,447 | 4 | 268,920 | yes |
| centralia | 2026-04 | 30 | yes | 0 | 189,504 | 4 | 0 | yes |
| centralia | 2026-05 | 31 | yes | 0 | 5,110 | 4 | 0 | yes |
| centralia | 2026-06 | 30 | yes | 0 | 52,325 | 4 | 241,902 | yes |
| craig | 2025-12 | 2 | no | 61,805 | 174,243 | 4 | 61,805 | no |
| craig | 2026-01 | 31 | yes | 0 | 218,140 | 4 | 174,089 | yes |
| craig | 2026-02 | 28 | yes | 0 | 196,290 | 4 | 124,764 | yes |
| craig | 2026-03 | 31 | yes | 0 | 191,747 | 4 | 161,356 | yes |
| craig | 2026-04 | 30 | yes | 56,782 | 153,320 | 4 | 119,373 | yes |
| craig | 2026-05 | 31 | yes | 0 | 151,108 | 4 | 123,758 | yes |
| craig | 2026-06 | 30 | yes | 0 | 165,806 | 4 | 139,291 | yes |
| culley | 2025-12 | 9 | no | 17,558 | 25,250 | 4 | 17,558 | no |
| culley | 2026-01 | 31 | yes | 9,338 | 27,802 | 4 | 17,922 | yes |
| culley | 2026-02 | 28 | yes | 14,160 | 12,082 | 4 | 17,352 | yes |
| culley | 2026-03 | 31 | yes | 8,881 | 6,792 | 4 | 2,602 | yes |
| culley | 2026-04 | 30 | yes | 6,178 | 10,858 | 4 | 14,422 | yes |
| culley | 2026-05 | 31 | yes | 11,060 | 20,069 | 4 | 18,748 | yes |
| culley | 2026-06 | 30 | yes | -694 | 16,342 | 4 | 22,378 | yes |
| eddystone | 2025-05 | 2 | no | 0 | 321 | 4 | 0 | no |
| eddystone | 2025-06 | 30 | yes | 13,389 | 2,770 | 4 | 13,389 | yes |
| eddystone | 2025-07 | 31 | yes | 5,262 | 13,314 | 4 | 5,262 | yes |
| eddystone | 2025-08 | 31 | yes | 0 | 6,183 | 4 | 0 | yes |
| eddystone | 2025-09 | 30 | yes | 0 | 2,729 | 4 | 0 | yes |
| eddystone | 2025-10 | 31 | yes | 0 | 738 | 4 | 0 | yes |
| eddystone | 2025-11 | 30 | yes | 0 | 67 | 4 | 0 | yes |
| eddystone | 2025-12 | 31 | yes | 0 | 775 | 4 | 0 | yes |
| eddystone | 2026-01 | 31 | yes |  | 2,378 | 4 | 15,310 | no |
| eddystone | 2026-02 | 28 | yes |  | 981 | 4 | 0 | no |
| eddystone | 2026-03 | 31 | yes |  | 28 | 4 | 0 | no |
| eddystone | 2026-04 | 30 | yes |  | 49 | 4 | 2,007 | no |
| eddystone | 2026-05 | 31 | yes |  | 321 | 4 | 0 | no |
| eddystone | 2026-06 | 30 | yes |  | 2,770 | 4 | 13,389 | no |
| schahfer | 2025-12 | 9 | no | 134,395 | 130,024 | 4 | 134,395 | no |
| schahfer | 2026-01 | 31 | yes | 168,359 | 159,670 | 4 | 235,294 | yes |
| schahfer | 2026-02 | 28 | yes | 147,610 | 132,395 | 4 | 119,578 | yes |
| schahfer | 2026-03 | 31 | yes | -4,792 | 153,576 | 4 | 80,817 | yes |
| schahfer | 2026-04 | 30 | yes | -3,385 | 65,566 | 4 | 101,872 | yes |
| schahfer | 2026-05 | 31 | yes | -2,550 | 172,163 | 4 | 47,945 | yes |
| schahfer | 2026-06 | 30 | yes | -1,898 | 169,888 | 4 | 175,924 | yes |
| stanton | 2026-06 | 27 | no | 171,122 | 143,565 | 4 | 100,523 | no |
| wagner | 2025-07 | 4 | no | 3,485 | 4,302 | 4 | 3,485 | no |
| wagner | 2025-08 | 31 | yes | 0 | 3,206 | 4 | 0 | yes |
| wagner | 2025-09 | 30 | yes | 0 | 2,175 | 4 | 0 | yes |
| wagner | 2025-10 | 31 | yes | 0 | 1,577 | 4 | 0 | yes |
| wagner | 2025-11 | 30 | yes | 2,006 | 0 | 4 | 2,006 | yes |
| wagner | 2025-12 | 31 | yes | 1,161 | 1,772 | 4 | 1,161 | yes |
| wagner | 2026-01 | 0 | no | 1,138 | 1,277 | 4 | 32,941 | no |
| wagner | 2026-02 | 0 | no | 14,747 | 158 | 4 | 0 | no |
| wagner | 2026-03 | 0 | no | 12,129 | 0 | 4 | 0 | no |
| wagner | 2026-04 | 0 | no | 15,547 | 3,774 | 4 | 549 | no |
| wagner | 2026-05 | 10 | no | 36,716 | 1,529 | 4 | 0 | no |
| wagner | 2026-06 | 30 | yes | 8,233 | 281 | 4 | 16,408 | yes |

## Diagnostics

```
{
 "version": "0.1.0",
 "parquet": "core_eia923__monthly_generation.parquet",
 "records": 809021,
 "columns": [
  "plant_id_eia",
  "generator_id",
  "report_date",
  "net_generation_mwh",
  "data_maturity"
 ],
 "maturity_by_month": {
  "2025-07": [
   "final"
  ],
  "2025-08": [
   "final"
  ],
  "2025-09": [
   "final"
  ],
  "2025-10": [
   "final"
  ],
  "2025-11": [
   "final"
  ],
  "2025-12": [
   "final"
  ],
  "2026-01": [
   "incremental_ytd"
  ],
  "2026-02": [
   "incremental_ytd"
  ],
  "2026-03": [
   "incremental_ytd"
  ],
  "2026-04": [
   "incremental_ytd"
  ],
  "2026-05": [
   "incremental_ytd"
  ],
  "2026-06": [
   "incremental_ytd"
  ]
 },
 "coverage": {
  "no_base": [],
  "generators_at_plants": {
   "1012/2": {
    "first": "2008-01",
    "last": "2026-06",
    "months": 222
   },
   "1012/3": {
    "first": "2008-01",
    "last": "2026-06",
    "months": 222
   },
   "1554/1": {
    "first": "2008-01",
    "last": "2026-05",
    "months": 216
   },
   "1554/2": {
    "first": "2008-01",
    "last": "2020-08",
    "months": 152
   },
   "1554/3": {
    "first": "2008-01",
    "last": "2026-06",
    "months": 222
   },
   "1554/4": {
    "first": "2008-01",
    "last": "2026-06",
    "months": 222
   },
   "1710/1": {
    "first": "2008-01",
    "last": "2026-06",
    "months": 222
   },
   "1710/2": {
    "first": "2008-01",
    "last": "2026-06",
    "months": 222
   },
   "1710/3": {
    "first": "2008-01",
    "last": "2026-06",
    "months": 222
   },
   "3161/1": {
    "first": "2008-01",
    "last": "2013-12",
    "months": 72
   },
   "3161/2": {
    "first": "2008-01",
    "last": "2013-12",
    "months": 72
   },
   "3161/3": {
    "first": "2008-01",
    "last": "2025-12",
    "months": 216
   },
   "3161/4": {
    "first": "2008-01",
    "last": "2025-12",
    "months": 216
   },
   "3845/1": {
    "first": "2008-01",
    "last": "2021-01",
    "months": 157
   },
   "3845/2": {
    "first": "2008-01",
    "last": "2026-06",
    "months": 222
   },
   "3845/70": {
    "first": "2008-01",
    "last": "2014-04",
    "months": 76
   },
   "564/1": {
    "first": "2008-01",
    "last": "2026-06",
    "months": 221
   },
   "564/2": {
    "first": "2008-01",
    "last": "2026-06",
    "months": 221
   },
   "564/B": {
    "first": "2010-02",
    "last": "2026-06",
    "months": 196
   },
   "564/B1": {
    "first": "2014-05",
    "last": "2026-06",
    "months": 145
   },
   "6021/1": {
    "first": "2008-01",
    "last": "2026-06",
    "months": 222
   },
   "6021/2": {
    "first": "2008-01",
    "last": "2026-06",
    "months": 222
   },
   "6021/3": {
    "first": "2008-01",
    "last": "2026-06",
    "months": 222
   },
   "6085/14": {
    "first": "2008-01",
    "last": "2023-12",
    "months": 192
   },
   "6085/15": {
    "first": "2008-01",
    "last": "2023-12",
    "months": 192
   },
   "6085/17": {
    "first": "2008-01",
    "last": "2026-06",
    "months": 222
   },
   "6085/18": {
    "first": "2008-01",
    "last": "2026-06",
    "months": 222
   }
  }
 }
}
```

