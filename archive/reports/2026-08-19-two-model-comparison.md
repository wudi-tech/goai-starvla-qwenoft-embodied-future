> 历史资料快照：以下状态和计划只代表原文日期；当前结论见 [项目状态](../../docs/project_status.md)。已移除服务器连接信息。

# QwenOFT 两版模型本地 600 回合评测结果详细汇总

- 汇总日期：2026-08-19
- 范围：本地 Isaac Sim / XPolicyLab 评测（RoboDojo 24 任务 × 25 回合 = 600 episodes）
- 重要提示：本表为**本地评测结果**，不作为 X-Eval 官方成绩，也不得在提交材料中冒充官方成绩。

## 1. 两版模型身份

| 项目 | 100k（官方基线） | 20k（定向微调） |
|---|---|---|
| checkpoint 文件 | `steps_100000_pytorch_model.pt` | `steps_20000_pytorch_model.pt` |
| checkpoint revision | `97123d6ef9f88b99801d07f3ad0720ca7c539777` | 本项目训练输出（20k 上限） |
| base VLM | `Qwen3-VL-4B-Instruct`（revision `ebb281ec70b05090aa6165b016eac8ec08e71b17`） | 同左 |
| 评测配置 | 14D action/state、三相机、execute_horizon=16、action_horizon=50、seed=0 | 同左 |

## 2. 总览对比

| 指标 | 100k | 20k |
|---|---:|---:|
| 计分任务数 | 24 | 24 |
| 总回合数 | 600 | 600 |
| 总成功回合 | 33 | 28 |
| 总体成功率（micro） | 5.50% | 4.67% |
| 总 score | 191.6 | 164.8 |
| 视频/回合完整性 | 24/24 任务均 75 视频、25 回合、unstable=0 | 24/24 任务均 75 视频、25 回合、unstable=0 |

## 3. 逐任务对比（24 项）

| 任务 | 100k 成功 | 100k score | 20k 成功 | 20k score | 20k-100k 差值 |
|---|---:|---:|---:|---:|---:|
| hang_mugs | 0 | 7.8 | 0 | 6.2 | 0 |
| fold_clothes | 6 | 27.2 | 6 | 28.0 | 0 |
| arrange_largest_number | 0 | 2.0 | 0 | 0.4 | 0 |
| sort_nesting_dolls_by_size | 0 | 0.0 | 0 | 0.0 | 0 |
| stack_blocks | 6 | 28.8 | 2 | 15.8 | -4 |
| make_toast | 0 | 7.0 | 0 | 6.0 | 0 |
| pack_objects_into_box | 0 | 4.6 | 0 | 3.0 | 0 |
| pour_liquid_into_cup | 10 | 40.0 | 11 | 44.0 | +1 |
| push_T | 0 | 0.0 | 0 | 0.0 | 0 |
| stack_bowls | 9 | 38.4 | 6 | 28.8 | -3 |
| store_laptop_and_headphones | 0 | 17.6 | 0 | 13.6 | 0 |
| sweep_blocks | 0 | 0.0 | 0 | 0.0 | 0 |
| hang_mugs_random | 0 | 0.6 | 0 | 0.6 | 0 |
| fold_clothes_random | 2 | 8.0 | 3 | 12.0 | +1 |
| arrange_largest_number_random | 0 | 0.2 | 0 | 0.4 | 0 |
| sort_nesting_dolls_by_size_random | 0 | 0.0 | 0 | 0.0 | 0 |
| stack_blocks_random | 0 | 0.6 | 0 | 0.6 | 0 |
| make_toast_random | 0 | 0.0 | 0 | 0.0 | 0 |
| pack_objects_into_box_random | 0 | 0.8 | 0 | 0.0 | 0 |
| pour_liquid_into_cup_random | 0 | 0.0 | 0 | 0.0 | 0 |
| push_T_random | 0 | 0.0 | 0 | 0.0 | 0 |
| stack_bowls_random | 0 | 2.4 | 0 | 0.6 | 0 |
| store_laptop_and_headphones_random | 0 | 5.6 | 0 | 4.8 | 0 |
| sweep_blocks_random | 0 | 0.0 | 0 | 0.0 | 0 |
| **合计** | **33** | **191.6** | **28** | **164.8** | **-5** |

## 4. 分组统计

| 分组 | 100k | 20k |
|---|---:|---:|
| 12 个 base 任务 | 31 / 300（10.33%） | 25 / 300（8.33%） |
| 12 个 random 任务 | 2 / 300（0.67%） | 3 / 300（1.00%） |
| 合计 | 33 / 600（5.50%） | 28 / 600（4.67%） |

## 5. 关键结论

1. 20k 定向微调总体**略低于**官方 100k 基线：成功 28 vs 33（-5），成功率 4.67% vs 5.50%，score 164.8 vs 191.6。
2. 主要差距集中在 `stack_blocks`（-4）和 `stack_bowls`（-3）。
3. 20k 在 `pour_liquid_into_cup`（+1）和 `fold_clothes_random`（+1）上略有提升。
4. `fold_clothes` 持平（6 成功），其余 19 项均为 0 成功。
5. 两者都有 24 个任务中 19 个任务 0 成功，说明困难长程操作任务仍是主要瓶颈。

## 6. 证据与口径说明

- 100k 的 600 回合由 4 个 source run 合并：orig13（13 任务）+ recovery3 canary（1）+ recovery3 main（9）+ recovery4（1）。详见 `2026-08-15-qwenoft-formal600-final-status.md`。
- 20k 评测过程经历两次硬停止（系统盘写满、Warp 相机缓存损坏），已补跑 3 个受损任务（`stack_blocks_random`、`make_toast_random`、`pack_objects_into_box_random`），最终 24 项均有效。
- 判定口径：`_result.json` 中 `eval_time=25`、`details` 恰 25 条、三相机 mp4 各 25 个且非空；成功数 = `details[*].success==true` 计数。
- 本地评测协议为 RoboDojo 公开的 `12×(25 base + 25 random)=600 episodes`；**X-Eval 官方协议（12 任务、回合数、seed）待主办方确认，本表不作为官方成绩**。

## 7. 逐任务原始文件

- 100k：`final_summary_100k.tsv`、`final_summary_100k.json`
- 20k：`final_summary_20k.tsv`、`final_summary_20k.json`

## 8. 校验和

- 100k TSV SHA256：`cda43dd49055f6761576a8dc5c15de13ccc6c124bcdf192249e5bed54f891cd0`
- 100k JSON SHA256：`2d7551a56eed446f46943805e167bf8128e244264799fbcbb9a778b2f1069251`
- 20k TSV SHA256：`c1f56429f241d55fc657e75811324f2c4a4f0ac04f7c78d1ab0047db1a73a2ef`
- 20k JSON SHA256：`5306a959a00fd0772223099436ef01018d4f399eb95f8ecaed823d1b445c791b`
