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

### Table 2 — the two raters

| raters | agree | n | Cohen κ (six categories) |
|---|---:|---:|---:|
| L1 (author) vs L2 (`gpt-6-astra`, blind) | 60 | 68 | **0.722** |

| disputed instance | L1 | L2 |
|---|---|---|
| `b1:Mbpp/398` | ambiguous-oracle | unexercised-edge |
| `b1:Mbpp/594` | unexercised-edge | ambiguous-oracle |
| `b1:Mbpp/630` | other | ambiguous-oracle |
| `b1:Mbpp/792` | unexercised-edge | ambiguous-oracle |
| `b2:Mbpp/142` | ambiguous-oracle | unexercised-edge |
| `b2:Mbpp/398` | ambiguous-oracle | unexercised-edge |
| `b2:Mbpp/630` | other | ambiguous-oracle |
| `b2:Mbpp/792` | unexercised-edge | ambiguous-oracle |

### Table 3 — EXPLORATORY: ceiling 1's all-family union recall on an oracle-clean denominator

Assumption stated in the preregistration and repeated here: only the residual was re-rated; the 53 flagged instances are treated as oracle-clean, which they were never checked to be.

| denominator | P | flagged by any draw | union recall at K_max | residual share |
|---|---:|---:|---:|---:|
| registered (ceiling 1) | 110 | 53 | 48.2% | 51.8% |
| oracle-clean (P minus 44 consensus-ambiguous residual instances) | 66 | 53 | 80.3% | 19.7% |
