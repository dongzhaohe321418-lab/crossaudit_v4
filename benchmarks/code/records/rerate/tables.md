### Table 1 — consensus category of the residual, oracle question first

Unit: the instance; primary interval the problem-cluster percentile bootstrap (seed 20260914, 10,000 resamples); Wilson beside it, too narrow. `disputed` = the two raters differ; counted toward neither category.

| population | n (problems) | category | consensus count | share [95% cluster CI] (Wilson) |
|---|---:|---|---:|---|
| all_families_residual | 57 (34) | `timeout` | 3 | **3 of 57** (5.3% [0.0, 14.3]; Wilson [1.8, 14.4]) |
| all_families_residual | 57 (34) | `ambiguous-oracle` | 44 | **44 of 57** (77.2% [62.1, 91.1]; Wilson [64.8, 86.2]) |
| all_families_residual | 57 (34) | `unexercised-edge` | 2 | **2 of 57** (3.5% [0.0, 10.9]; Wilson [1.0, 11.9]) |
| all_families_residual | 57 (34) | `disputed` | 8 | **8 of 57** (14.0% [3.4, 26.8]; Wilson [7.3, 25.3]) |
| sheet_68 | 68 (40) | `timeout` | 5 | **5 of 68** (7.4% [0.0, 16.7]; Wilson [3.2, 16.1]) |
| sheet_68 | 68 (40) | `ambiguous-oracle` | 46 | **46 of 68** (67.6% [52.2, 82.1]; Wilson [55.8, 77.6]) |
| sheet_68 | 68 (40) | `unexercised-edge` | 9 | **9 of 68** (13.2% [3.0, 25.0]; Wilson [7.1, 23.3]) |
| sheet_68 | 68 (40) | `disputed` | 8 | **8 of 68** (11.8% [2.9, 23.0]; Wilson [6.1, 21.5]) |
| flagged_P | 53 (33) | `timeout` | 4 | **4 of 53** (7.5% [0.0, 17.6]; Wilson [3.0, 17.9]) |
| flagged_P | 53 (33) | `ambiguous-oracle` | 24 | **24 of 53** (45.3% [28.3, 63.3]; Wilson [32.7, 58.5]) |
| flagged_P | 53 (33) | `unexercised-edge` | 23 | **23 of 53** (43.4% [25.0, 60.7]; Wilson [31.0, 56.7]) |
| flagged_P | 53 (33) | `disputed` | 2 | **2 of 53** (3.8% [0.0, 10.0]; Wilson [1.0, 12.8]) |

### Table 2 — the two raters (disputed instances from both sheets)

| raters | agree | n | Cohen κ (six categories) |
|---|---:|---:|---:|
| L1 (author) vs L2 (`gpt-6-astra`, blind) | 60 | 68 | **0.722** |

| disputed instance | L1 | L2 |
|---|---|---|
| `b1:Mbpp/142` | ambiguous-oracle | unexercised-edge |
| `b1:Mbpp/398` | ambiguous-oracle | unexercised-edge |
| `b1:Mbpp/594` | unexercised-edge | ambiguous-oracle |
| `b1:Mbpp/630` | other | ambiguous-oracle |
| `b1:Mbpp/792` | unexercised-edge | ambiguous-oracle |
| `b2:Mbpp/142` | ambiguous-oracle | unexercised-edge |
| `b2:Mbpp/398` | ambiguous-oracle | unexercised-edge |
| `b2:Mbpp/594` | unexercised-edge | ambiguous-oracle |
| `b2:Mbpp/630` | other | ambiguous-oracle |
| `b2:Mbpp/792` | unexercised-edge | ambiguous-oracle |

| raters, flagged sheet | agree | n | Cohen κ |
|---|---:|---:|---:|
| L1 vs L2 | 51 | 53 | **0.933** |

Test-retest on the 11 instances both sheets carry (rated twice, blind both times, the flagged sheet's label used): L1 same 11 of 11, L2 same 11 of 11.

### Table 3 — ceiling 1's all-family union recall on the oracle-clean denominator (Amendment 1 secondary)

Rule: Amendment 1: (53 − a_f) / (110 − a_r − a_f); disputed count as not ambiguous. Interval: problem-cluster bootstrap over the 110 P instances' (flagged, ambiguous) pairs, seed 20260924; Wilson beside it.

| denominator | P | flagged by any draw | union recall at K_max [95% cluster CI] (Wilson) | residual share |
|---|---:|---:|---|---:|
| registered (ceiling 1) | 110 | 53 | 48.2% [36.7, 60.0] (Wilson [39.1, 57.4]) | 51.8% |
| oracle-clean (minus 44 residual + 24 flagged consensus-ambiguous) | 42 | 29 | **69.0%** [50.0, 86.4] (Wilson [54.0, 80.9]) | 31.0% |

The registered interval is the complement of ceiling 1's residual-share interval. The oracle-clean interval is a bootstrap of a conditional estimand: the bootstrap for this conditional estimand has no committed coverage simulation; uncalibrated.

### Table 4 — POST HOC: ceiling 1's union recall by the defect's consensus category

Asked after Table 1's flagged counts were seen; not preregistered. Recall = flagged by any of the 20 draws.

| consensus category | n P instances (problems) | flagged | recall [95% cluster CI] (Wilson) |
|---|---:|---:|---|
| `timeout` | 7 (4) | 4 | **4 of 7** (57.1% [14.3, 100.0]; Wilson [25.0, 84.2]) |
| `ambiguous-oracle` | 68 (34) | 24 | **24 of 68** (35.3% [22.1, 50.0]; Wilson [25.0, 47.2]) |
| `unexercised-edge` | 25 (13) | 23 | **23 of 25** (92.0% [75.0, 100.0]; Wilson [75.0, 97.8]) |
| `disputed` | 10 (5) | 2 | **2 of 10** (20.0% [0.0, 40.0]; Wilson [5.7, 51.0]) |

### Table 5 — Amendment 2: L2 re-run on one identity-stripped sheet of all 110 P instances

The first sheets carried the instance id and L2's second prompt named the sheet (found by the first review); this pass strips both. L1's labels are unchanged (L1 cannot be re-blinded).

| quantity | value |
|---|---|
| L2 first labels vs re-blinded, same | 108 of 110 (κ 0.963) |
| L1 vs re-blinded L2, agree | 102 of 110 (κ 0.854) |
| residual consensus (L1 × L2 re-blinded) | `timeout` 3, `ambiguous-oracle` 44, `unexercised-edge` 2, `other` 2, `disputed` 6 |
| flagged consensus (L1 × L2 re-blinded) | `timeout` 4, `ambiguous-oracle` 24, `unexercised-edge` 23, `disputed` 2 |
| §3 kill restated | ambiguous 44 of 57, edge 2 of 57 — fires |
| oracle-clean recall restated | 29 of 42 = **69.0%** [50.0, 86.4] (Wilson [54.0, 80.9]) |

| post-hoc split restated | n | flagged | recall [95% cluster CI] (Wilson) |
|---|---:|---:|---|
| `timeout` | 7 | 4 | **4 of 7** (57.1% [14.3, 100.0]; Wilson [25.0, 84.2]) |
| `ambiguous-oracle` | 68 | 24 | **24 of 68** (35.3% [22.1, 50.0]; Wilson [25.0, 47.2]) |
| `unexercised-edge` | 25 | 23 | **23 of 25** (92.0% [75.0, 100.0]; Wilson [75.0, 97.8]) |
| `other` | 2 | 0 | **0 of 2** (0.0% [0.0, 0.0]; Wilson [0.0, 65.8]) |
| `disputed` | 8 | 2 | **2 of 8** (25.0% [0.0, 50.0]; Wilson [7.1, 59.1]) |
