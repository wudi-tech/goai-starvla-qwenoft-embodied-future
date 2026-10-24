# 本地评测结果

本目录全部是本地工程实验，不是 X-Eval 官方成绩。完整评测、内部筛选和诊断抽样分别保存，不能混用分母。

## 两版完整评测

| 模型 | 任务配置 | 回合 | 成功 | 总体成功率 | 历史总 score |
|---|---:|---:|---:|---:|---:|
| 公开 100k 稳定基线 | 24 | 600 | 33 | 5.50% | 191.6 |
| 定向微调 20k | 24 | 600 | 28 | 4.67% | 164.8 |

每版为 12 个 base 配置与 12 个 random 配置、每项 25 回合。两版合计 1,200 回合不包含快筛和无效运行。每项分母相同，因此每版 micro 和 24 项 macro 平均数值相同。

- [基线 JSON](local600/final_summary_100k.json)、[TSV](local600/final_summary_100k.tsv)。
- [20k JSON](local600/final_summary_20k.json)、[TSV](local600/final_summary_20k.tsv)。
- [基线 24 份原始结果](local600/baseline_raw/)：每个 `_result.json` 保存 25 条 `details`。成功数按 `success is True` 重算，合计 33。

20k 当前公开归档只有逐任务汇总，未包含 600 回合完整原始结果与视频。JSON 中的 `official_revision` 是历史文件字段名，不表示官方成绩认证。复查汇总一致性不等于重新执行仿真。

## Candidate C 小样本筛选

[screening.tsv](candidate_c/screening.tsv)记录 60k/80k/100k 三个检查点，各在堆碗、随机折衣、倾倒三个任务上各运行 5 回合，均为 0 成功、5 失败、0 unstable。每检查点 0/15，总共 45 回合。

[log_evidence.json](candidate_c/log_evidence.json)保留选取的连接、配置、结果和结束行，以及原始日志 SHA256。摘录不能替代完整原始日志；原始系统日志留在本地，未上传。

选择 100k 只代表身份冻结，不代表筛选发现它更好。Candidate C 没有完整本地 600 回合结果。

## 诊断抽样

- [task-analysis.tsv](diagnostics/task-analysis.tsv)：24 项配置的失败表现分类。
- [diagnostic-selections.tsv](diagnostics/diagnostic-selections.tsv)：每项首个失败回合，另加 5 个成功对照，共 29 回合。
- [diagnostic-index.tsv](diagnostics/diagnostic-index.tsv)：29 × 3 = 87 段视频的来源、大小和哈希。

索引中的历史绝对路径只是来源定位，视频本体未进入仓库。单个代表回合不能代表整项任务的所有失败，更不能直接证明模型内部原因。
