> 历史资料快照：以下状态和计划只代表原文日期；当前结论见 [项目状态](../../docs/project_status.md)。已移除服务器连接信息。

# QwenOFT RoboDojo 正式 600 回合评测 — 最终验收、合并与报告

- **执行时间**：2026-08-15 16:36–16:39 CST
- **实例**：`autodl-container-4yykv6xgt5-3adc8b8d`，`[服务器连接信息已移除]`（root，公钥 SSH，key=`codex_goai_ed25519`）
- **范围**：只读验收与统计。未启动/停止/重试任何评测/Isaac/policy/screen，未修改模型/checkpoint/数据/任务/动作维度/25 回合口径，未覆盖或移动任何已有结果。
- **结论**：`FINALIZATION_COMPLETE`

## 1. 固定输入（4 个源 run，全部严格只读）

| 来源 | run_id | 计分任务数 | 回合数 |
|---|---|---|---|
| 原始 run | `2026-08-13-qwenoft-formal600-4x5090` | 13 | 325 |
| recovery3 canary | `2026-08-14-qwenoft-formal600-recovery3-canary-2x5090` | 1 | 25 |
| recovery3 main | `2026-08-15-qwenoft-formal600-recovery3-main-2x5090` | 9 | 225 |
| recovery4 GPU1 替代 | `2026-08-15-qwenoft-formal600-recovery4-gpu1` | 1 | 25 |
| **合计** | | **24** | **600** |

## 2. 版本与模型（实测锁定）

- **RoboDojo** commit：`a63e16a7a6dad6acce5f08352beea80b9b314870`（`git rev-parse HEAD`，四 run 一致）。
- **XPolicyLab**：
  - 原始 13 任务（原 run）：`7748e2d0a284d6c4f2604687cb46a1f140c99d13`
  - recovery 11 任务（canary/main/recovery4）：`b01f50a882c119f0643577031b5697db4317a131`（当前 HEAD；修复了客户端环境自激活 + 外圈 WS keepalive）
- **checkpoint**：`/root/autodl-tmp/GOAI/models/StarVLA-Qwen3vl4b-OFT-RoboDojo-97123d6-local/checkpoints/steps_100000_pytorch_model.pt`（9.78 GB，revision `97123d6ef9f88b99801d07f3ad0720ca7c539777`）
- **base_vlm**：`/root/autodl-tmp/GOAI/models/Qwen3-VL-4B-Instruct-ebb281ec`（revision `ebb281ec70b05090aa6165b016eac08ec08e71b17`）
- 两个 XPolicyLab commit 使用同一 checkpoint/base_vlm/任务定义/动作维度/25 回合口径；仅编排层（env 激活、WS keepalive）不同，不影响策略权重。

## 3. 八项硬门结果（全部通过）

1. ✅ **进程/GPU 空闲**：`screen -ls` 无 socket；无 Isaac/policy/eval/shard/robodojo 进程；两卡 0 MiB、compute-apps=0。
2. ✅ **canary 恰 1 任务**：`pack_objects_into_box` 真实 `inner_exit=0`、唯一 `TASK_END exit=0`、postflight `VALID`、details=25、三相机 25/25/25 非空、无 tmp。
3. ✅ **main 恰 9 计分任务**：GPU0 五项 + GPU1 前四项，每项真实 `inner_exit=0`、唯一 `TASK_END exit=0`、`POSTFLIGHT verdict=VALID`、details=25、三相机 25/25/25、无 tmp；失败的 `make_toast_random` 仅 1 回合 + GPU crash（`TASK_START`=1、`TASK_END`=0），已排除。
4. ✅ **recovery4 恰 1 任务**：`make_toast_random` 真实 `inner_exit=0`、唯一 `TASK_END exit=0`、独立修正后检 `inner_exit=0 details=25 head/left/right=25/25/25 gpu_crash=0 verdict=VALID`、无 Vulkan page fault/`ERROR_DEVICE_LOST`/`vkWaitForFences`。原 run 内 postflight 因只搜 `gpu*.results.tsv` 漏读 `recovery4gpu1.results.tsv` 而误报 `inner_exit=MISSING`、`recovery4gpu1.exit=1`——此非 inner 失败，属已知编排 bug（已在 recovery4 状态文档记录，未改输入 run）。
5. ✅ **无失败签名**：24 计分任务日志区间内 Errno28/`Success nums: 0, Fail nums: 0`/OOM/CUDA/GPU crash/device lost/shape·dtype 全 0；原始 13 中可见的少量 Traceback 均为已白名单的可恢复 keepalive-ping-timeout 与 `Simulation context already exists`（非失败签名）。
6. ✅ **原始 13 重核验**：从原始 run 逐任务重扫（details=25、三相机 25/25/25、no_space=0/zero000=0/oom=0/cuda=0/shape=0）锁定恰 13 VALID；未沿用 `recovery_audit.tsv` 初始 INVALID/MISSING 行作为最终 verdict。
7. ✅ **24 名唯一、600 回合**：24 个任务名唯一，Σdetails = 600；旧 recovery2、ABORTED、原始 11 INVALID 及 main 失败 `make_toast_random` 均未混入。
8. ✅ **磁盘**：系统盘 `/` 29 GiB 可用（≥5 GiB）；数据盘 `/root/autodl-tmp` 64 GiB 可用（≥40 GiB）。

## 4. 最终统计（`_result.json` 真实 schema：`details[*].success`）

- 判定口径：`details` 恰 25 条；`success_count` = `details[*].success==true` 计数；`failure_count` = 25 − success。
- **micro 成功率**：`33 / 600` = **5.500%**
- **macro 成功率**（24 任务成功率算术平均）：**5.500%**（因每任务均恰 25 回合，与 micro 数值一致）

### 分组统计

| 组 | 任务数 | 回合数 | 成功回合 | 成功率 |
|---|---|---|---|---|
| 原始 13 | 13 | 325 | 17 | 5.231% |
| recovery3 canary | 1 | 25 | 0 | 0% |
| recovery3 main 9 | 9 | 225 | 16 | 7.111% |
| recovery4 替代 | 1 | 25 | 0 | 0% |
| **合计** | **24** | **600** | **33** | **5.500%** |

### 逐任务表（24 行）

| task | source | shard | succ | fail | rate | verdict |
|---|---|---|---|---|---|---|
| arrange_largest_number | orig13 | gpu0 | 0 | 25 | 0.0 | VALID |
| arrange_largest_number_random | orig13 | gpu0 | 0 | 25 | 0.0 | VALID |
| fold_clothes | orig13 | gpu0 | 6 | 19 | 0.24 | VALID |
| fold_clothes_random | orig13 | gpu0 | 2 | 23 | 0.08 | VALID |
| make_toast | orig13 | gpu1 | 0 | 25 | 0.0 | VALID |
| push_T | orig13 | gpu2 | 0 | 25 | 0.0 | VALID |
| push_T_random | orig13 | gpu2 | 0 | 25 | 0.0 | VALID |
| sort_nesting_dolls_by_size | orig13 | gpu2 | 0 | 25 | 0.0 | VALID |
| sort_nesting_dolls_by_size_random | orig13 | gpu2 | 0 | 25 | 0.0 | VALID |
| stack_bowls | orig13 | gpu3 | 9 | 16 | 0.36 | VALID |
| stack_bowls_random | orig13 | gpu3 | 0 | 25 | 0.0 | VALID |
| store_laptop_and_headphones | orig13 | gpu3 | 0 | 25 | 0.0 | VALID |
| store_laptop_and_headphones_random | orig13 | gpu3 | 0 | 25 | 0.0 | VALID |
| pack_objects_into_box | canary | gpu0 | 0 | 25 | 0.0 | VALID |
| hang_mugs | main | gpu0 | 0 | 25 | 0.0 | VALID |
| pack_objects_into_box_random | main | gpu0 | 0 | 25 | 0.0 | VALID |
| pour_liquid_into_cup | main | gpu0 | 10 | 15 | 0.40 | VALID |
| stack_blocks | main | gpu0 | 6 | 19 | 0.24 | VALID |
| sweep_blocks | main | gpu0 | 0 | 25 | 0.0 | VALID |
| hang_mugs_random | main | gpu1 | 0 | 25 | 0.0 | VALID |
| pour_liquid_into_cup_random | main | gpu1 | 0 | 25 | 0.0 | VALID |
| stack_blocks_random | main | gpu1 | 0 | 25 | 0.0 | VALID |
| sweep_blocks_random | main | gpu1 | 0 | 25 | 0.0 | VALID |
| make_toast_random | recovery4 | gpu1 | 0 | 25 | 0.0 | VALID |

## 5. 排除清单（含原因）

- `2026-08-14-qwenoft-formal600-recovery-4x5090`（ABORTED run）：首次 canary 非零 inner exit 后违规自动重启，重试边界不满足正式证据要求。
- `2026-08-14-qwenoft-formal600-recovery2-canary-4x5090`（旧 recovery2 canary 残留）：克隆前实例中断 canary，非正式结果。
- 原始 run 的 11 个 INVALID 任务（`hang_mugs`/`hang_mugs_random`/`pack_objects_into_box`/`pack_objects_into_box_random`/`pour_liquid_into_cup`/`pour_liquid_into_cup_random`/`stack_blocks`/`stack_blocks_random`/`sweep_blocks`/`sweep_blocks_random`/`make_toast_random`）：Errno28 或 `0/0/0` 失败（details<25 或目录缺失），已被 recovery3/recovery4 替代。
- `make_toast_random`@recovery3 main：Vulkan `ERROR_DEVICE_LOST`/GPU pagefault，仅 1 回合，已被 recovery4 替代。

## 6. 远端报告路径

`/root/autodl-tmp/GOAI/RoboDojo/smoke_results/2026-08-15-qwenoft-formal600-final-audit/`

- `manifest.txt`（主机/时间/commit/checkpoint/revision/来源/汇总指标）
- `final_tasks.tsv`（24 行逐任务：task/source_run/shard/details/success/failure/rate/inner_exit/三相机/verdict/路径）
- `final_summary.json`（micro/macro/分组/硬门/逐任务）
- `excluded_runs.tsv`（ABORTED + 旧 recovery2 + 原始 11 INVALID + main 失败 make_toast_random）
- `checksums.sha256`（覆盖上述 4 个轻量文件，`sha256sum -c` 全 OK）

统计文件已重新读取校验一致（`sha256sum -c checksums.sha256` → 4× OK；`final_summary.json` 重解析 total_tasks=24 / rounds=600 / success=33 / micro=macro=0.055）。

## 7. 监控与实例状态

- 评测与汇总已完成，**自动监控可以停止**。
- **实例继续开机，未关机、未停止**（按用户明确要求）。两卡 0 MiB 空闲，无计算进程。

## 8. 凭证

- 未索取、未打印、未保存任何密码/token/cookie/私钥。仅用已配置公钥 SSH（key `codex_goai_ed25519`）。
