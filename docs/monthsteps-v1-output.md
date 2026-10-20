# EIA-860M stage moves by report month

monthsteps 0.1.0 on stagemoves 0.1.0 and eia860m-slip 0.3.1; data core_eia860m__changelog_generators.parquet (reports 2016-01 to 2026-08). MV2 of Munim, Inc. (made with AI agents).

Steps as in stagemoves, m in 2016-2025, by the calendar month of report m + 1. Window: reports for months 12, 1, 2, 3. Rates: moves / eligible steps (generator counts); ratio: inside rate / outside rate.

## Inside and outside the window

| kind | in_n | in_steps | in_rate | out_n | out_steps | out_rate | ratio | in_mw_rate | out_mw_rate | mw_ratio |
|---|---|---|---|---|---|---|---|---|---|---|
| backward | 97 | 31347 | 0.003 | 100 | 63448 | 0.002 | 1.963 | 0.004 | 0.001 | 3.158 |
| backward_building | 57 | 23347 | 0.002 | 44 | 47069 | 0.001 | 2.612 | 0.003 | 0.001 | 3.739 |
| forward | 1198 | 30699 | 0.039 | 2683 | 62638 | 0.043 | 0.911 | 0.032 | 0.023 | 1.399 |
| exit_other | 20 | 54046 | 0.000 | 20 | 109707 | 0.000 | 2.030 | 0.000 | 0.000 | 2.941 |
| to_operating | 2651 | 54046 | 0.049 | 3645 | 109707 | 0.033 | 1.476 | 0.026 | 0.018 | 1.511 |

## By calendar month of report m + 1

| month | window | reports | steps | step_mw | backward_n | backward_rate | backward_building_n | backward_building_rate | forward_n | forward_rate | exit_other_n | exit_other_rate | to_operating_n | to_operating_rate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | yes | 10 | 13696 | 1472320.6 | 36 | 0.005 | 20 | 0.004 | 358 | 0.045 | 6 | 0.000 | 510 | 0.037 |
| 2 | yes | 10 | 12842 | 1216855.8 | 15 | 0.002 | 9 | 0.002 | 247 | 0.034 | 2 | 0.000 | 315 | 0.025 |
| 3 | yes | 10 | 13302 | 1245527.8 | 19 | 0.003 | 10 | 0.002 | 246 | 0.032 | 8 | 0.001 | 523 | 0.039 |
| 4 | no | 10 | 13373 | 1257784.9 | 10 | 0.001 | 2 | 0.000 | 315 | 0.040 | 6 | 0.000 | 458 | 0.034 |
| 5 | no | 10 | 13523 | 1379255.5 | 13 | 0.002 | 9 | 0.002 | 359 | 0.046 | 1 | 0.000 | 418 | 0.031 |
| 6 | no | 10 | 13525 | 1380683.4 | 16 | 0.002 | 6 | 0.001 | 359 | 0.046 | 3 | 0.000 | 504 | 0.037 |
| 7 | no | 10 | 13559 | 1383457.2 | 10 | 0.001 | 9 | 0.002 | 364 | 0.046 | 4 | 0.000 | 474 | 0.035 |
| 8 | no | 10 | 13626 | 1399203.2 | 9 | 0.001 | 3 | 0.001 | 384 | 0.049 | 1 | 0.000 | 402 | 0.029 |
| 9 | no | 10 | 13830 | 1440592.1 | 9 | 0.001 | 1 | 0.000 | 327 | 0.042 | 2 | 0.000 | 407 | 0.029 |
| 10 | no | 10 | 14094 | 1461862.0 | 14 | 0.002 | 6 | 0.001 | 305 | 0.039 | 2 | 0.000 | 468 | 0.033 |
| 11 | no | 10 | 14177 | 1476632.7 | 19 | 0.002 | 8 | 0.001 | 270 | 0.035 | 1 | 0.000 | 514 | 0.036 |
| 12 | yes | 10 | 14206 | 1501002.6 | 27 | 0.003 | 18 | 0.003 | 347 | 0.044 | 4 | 0.000 | 1303 | 0.092 |

## Backward rate inside and outside the window, by year of m (W3)

| year | in_rate | out_rate | higher |
|---|---|---|---|
| 2016 | 0.000 | 0.002 | False |
| 2017 | 0.004 | 0.001 | True |
| 2018 | 0.007 | 0.001 | True |
| 2019 | 0.005 | 0.002 | True |
| 2020 | 0.003 | 0.003 | True |
| 2021 | 0.002 | 0.002 | False |
| 2022 | 0.005 | 0.001 | True |
| 2023 | 0.002 | 0.001 | True |
| 2024 | 0.004 | 0.001 | True |
| 2025 | 0.001 | 0.001 | False |

## Checks

```
{
 "C1": {
  "steps": 163753,
  "pooled_steps": 163753,
  "step_mw": 16615177.8,
  "pooled_step_mw": 16615177.8,
  "backward_building_mw": 7620.0,
  "pooled_backward_building_mw": 7620.0,
  "pass": true
 },
 "C2": {
  "months_without_10_reports": [],
  "pass": true
 },
 "C3": {
  "stagemoves_all_pass": true,
  "pass": true
 },
 "all_pass": true
}
```

## Predictions

```
{
 "W1": {
  "kind": "backward",
  "ratio": 1.9633,
  "floor": 1.5,
  "held": true
 },
 "W2": {
  "kind": "forward",
  "ratio": 0.9111,
  "floor": 1.25,
  "held": false
 },
 "W3": {
  "kind": "backward",
  "years_higher": 7,
  "years": 10,
  "floor": 7,
  "held": true
 },
 "W4": {
  "kind": "exit_other",
  "ratio": 2.0299,
  "floor": 1.5,
  "held": true
 }
}
```
