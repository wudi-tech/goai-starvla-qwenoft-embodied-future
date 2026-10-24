> 历史资料快照：以下状态和计划只代表原文日期；当前结论见 [项目状态](../../docs/project_status.md)。已移除服务器连接信息。

# Candidate C 加赛对比：pour_liquid_into_cup

## 结论

60k、80k、100k 在追加的 `pour_liquid_into_cup` 小样本工程加赛中均为 0/5，仍然并列。加上此前两项快筛后三版均为 0/15，因此本地小样本证据无法证明任何 checkpoint 领先。

按预先约定的并列规则，**建议选择 100k**：它是完整训练终点，且没有证据证明早期 checkpoint 更优。该建议不是性能优越性声明，不依据训练 loss，也不是 X-Eval 官方结果。

## 协议

- task：`pour_liquid_into_cup`
- seed：0
- `EVAL_NUM=5`
- `eval_batch=true` / `num_envs=5`
- 单张 RTX 5090
- policy：`starVLA`
- 三相机：`head / left_wrist / right_wrist`
- state/action：14D / 14D
- `action_type=joint`
- `execute_horizon=16`
- WebSocket Policy Server

## 加赛结果

| checkpoint | 成功 | 失败 | unstable | rc | 硬错误 |
|---|---:|---:|---:|---:|---|
| 60k | 0 | 5 | 0 | 0 | 无 |
| 80k | 0 | 5 | 0 | 0 | 无 |
| 100k | 0 | 5 | 0 | 0 | 无 |

## 三项合并的小样本工程证据

| checkpoint | stack_bowls | fold_clothes_random | pour_liquid_into_cup | 合计 |
|---|---:|---:|---:|---:|
| 60k | 0/5 | 0/5 | 0/5 | 0/15 |
| 80k | 0/5 | 0/5 | 0/5 | 0/15 |
| 100k | 0/5 | 0/5 | 0/5 | 0/15 |

总计 45 个小样本工程回合，成功 0、失败 45、unstable 0。不得将其换算、宣传或提交为模型正式成功率；样本少、任务覆盖窄，结果仅说明本轮筛选没有区分度。

## 原始证据

目录：`raw_smoke_screen_logs/tiebreak_pour_v1_final/`

| 文件 | 字节数 | SHA256 |
|---|---:|---|
| `candidate_c_60000_pour_liquid_into_cup_seed0_eval5_tiebreak.log` | 132,277 | `c28052553c2c551bb15246345f75d099ed1441521f49299e65052664f40eb6ac` |
| `candidate_c_80000_pour_liquid_into_cup_seed0_eval5_tiebreak.log` | 132,277 | `3178d2de5ddb0dbddee9e836a34d52cac779a5c79dce9d27e2ee7c2e875972c6` |
| `candidate_c_100000_pour_liquid_into_cup_seed0_eval5_tiebreak.log` | 132,300 | `29b71510680208924eec1669f2e15c5cd786d00653ea23a1a4510e18140746d5` |
| `tiebreak_pour_summary.log` | 1,942 | `4141faf5212d63100007cd4ffcb42cf958a58e89bc1d546cd7bd28e129f6f6d2` |
| `tiebreak_pour_driver.log` | 1,803 | `d72df7a55e7ea70cc9b99b152989cee02255dc4b78bdfc182174332b6d86274e` |
| `run_tiebreak_pour_remote.sh` | 4,361 | `2eb38a474f54f0882b650cbe12041f8c17c57769088cecdecd473172dc2e9dec` |

## 用户决策结果

用户已明确选择 100k。该选择仅代表提交身份冻结，不改变本报告“三版并列、无性能优越性证据”的结论。
