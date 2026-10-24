> 历史资料快照：以下状态和计划只代表原文日期；当前结论见 [项目状态](../../docs/project_status.md)。已移除服务器连接信息。

# QwenOFT 基线与 checkpoint 对照报告

## 结论

当前证据不支持下“随训练步数提升而持续变好”或“优于某个同口径基线”的结论。新实例上只找到一个 QwenOFT checkpoint：`steps_100000_pytorch_model`。因此，本次 24 任务/600 回合是该 100k checkpoint 的单点正式估计，不是 checkpoint 趋势实验。

## 可比较证据

| 运行 | 策略/checkpoint | 任务 | 回合 | 成功 | 成功率 | 95% Wilson 区间 |
|---|---|---:|---:|---:|---:|---:|
| guardrail dry-run | starVLA / QwenOFT 100k | stack_bowls | 25 | 7 | 28% | 14.3%–47.6% |
| formal600 | starVLA / QwenOFT 100k | stack_bowls | 25 | 9 | 36% | 20.2%–55.5% |

两次均使用 `arx_x5`、`joint`、25 回合、环境 seed 0–24、同一 100k checkpoint 路径和相同的 14D 动作规格。逐 seed 配对后：15 个均失败、6 个均成功、1 个仅 dry-run 成功、3 个仅 formal 成功。配对净差为 +2/25（+8 个百分点），但区间高度重叠，精确 McNemar 双侧 `p=0.625`。这只说明两次观测存在正常波动，不能解读为模型改进。

此外，dry-run 目录没有独立 manifest，无法像 formal run 一样完整证明两次的 RoboDojo/XPolicyLab 代码 revision 完全相同。因此它适合做重复性参考，不应合并进正式 600 回合分母。

## 不可直接对比的结果

远端还有 `stack_bowls` 的 ACT 历史结果，包括 formal100、formal1000、formal6000 和 formal6000-latest；每个只有 1–5 回合且均为 0 成功。它们与本次 starVLA/QwenOFT 的策略类型、checkpoint 命名和评测规模不同，不能用来宣称 QwenOFT 相对 ACT 的统计显著优势。`demo_policy` 仅 1 回合，同样排除。

## 当前可信的判断

- QwenOFT 100k 在 24 任务上的正式成功率为 33/600（5.5%）。
- 五个任务出现成功信号，19 个任务为 0/25；这支持“存在局部能力但泛化与长程操作不足”，不支持“整体问题已解决”。
- `stack_bowls` 两次 25 回合重复估计是相容性/稳定性证据，不是 checkpoint 对照证据。

## 最小 checkpoint 评测矩阵

下一轮训练应固定保存至少 5 个等间隔 checkpoint（例如计划总步数的 20%/40%/60%/80%/100%），加上本次 100k 作为外部锚点。先对每个 checkpoint 跑固定小矩阵：

1. `stack_bowls`、`pour_liquid_into_cup`、`fold_clothes`、`stack_blocks`：检验已有能力是否增强或遗忘。
2. `stack_bowls_random`、`pour_liquid_into_cup_random`：检验布局泛化。
3. `make_toast`、`sweep_blocks`：检验精细接触与双臂序列能力。

每项 checkpoint 先跑 8 任务×5 回合筛选，仅对排名最好且通过管线完整性门的 checkpoint 跑 8 任务×25 回合复核；最终只对预先选定的候选跑 24 任务×25 回合正式评测。小矩阵用于筛选，不与正式 600 回合合并统计。

## 证据来源

- `docs/handoff/2026-08-13-qwenoft-eval-guardrails-result.md`
- `docs/handoff/2026-08-13-qwenoft-600eval-approval-audit.md`
- `artifacts/qwenoft-formal600-2026-08-15/2026-08-15-qwenoft-formal600-final-audit/final_tasks.tsv`
- 远端只读盘点：`eval_result/RoboDojo/**/_result.json`、`smoke_results/2026-08-13-qwenoft-formal600-4x5090/manifest.txt`
