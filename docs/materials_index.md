# 资料索引与整理范围

整理日期：2026-10-24。先对本地所有目录建立清单，再按来源、版本和价值选择公开内容；重复压缩包和解压副本不当作新的实验。

## 本次核对范围

本地初始清单记录 **5,291 个文件条目**（排除 `.git`、`__pycache__` 和本次整理产物目录；包含当时已写入的整理计划）。读取并计算 **3,875 个小型文本文件**的哈希，得到 **3,242 个内容唯一项**；建立 **51 份主要人工文档**的索引。代码包另按包内条目和与解压副本的一致性检查，不能将盘点数量解释为逐行语义审查了所有第三方源码。

重点核对了根目录路线/提交说明、`docs/reports`、`docs/handoff` 的结果与故障报告、设计稿、正式评测结果、诊断索引、第二次提交的训练冻结、筛选日志和两个代码包。完整的本地文件清单、私人资料与原始日志不进入公开仓库。

## 当前阅读层

| 资料 | 用途 |
|---|---|
| [项目状态](project_status.md) | 当前阶段、未验证事项、资料缺口 |
| [实验演进](experiment_history.md) | 时间线、ACT/基线/微调/候选之间的关系 |
| [系统结构](system_architecture.md) | 双层 WebSocket 服务、动作块、闭环和多环境边界 |
| [个人工作](contributions.md) | 对应代码和差异、开源复用范围 |
| [复现](reproduction.md) | 无 GPU 检查与完整仿真的外部依赖 |
| [评测结果](../results/README.md) | 可重算的数字与抽样范围 |
| [本次验证记录](validation_20261024.md) | 本轮实际运行的检查及已发现的问题 |

## 关键源码与配置

- 已有运行代码：[xpolicylab](../xpolicylab/)，保留原来的服务、适配器与 StarVLA 依赖。
- 评测护栏：[源码和测试](../archive/robodojo/scripts/internal/)，另带最小任务配置和注册器以支持纯校验测试。
- 版本缺口：[不匹配的分片测试原文](../archive/robodojo/unmatched_tests/test_eval_guardrails_shards.py.snapshot)，没有修改其内容来制造通过结果。
- WebSocket 恢复审计：[audit_keepalive.py](../xpolicylab/scripts/internal/audit_keepalive.py)及其原有测试。
- Candidate C：[配置、训练启动脚本、训练/部署 diff 和 4 份修改后的源文件](../archive/training/candidate_c/)。
- 历史实验：[脚本目录与使用边界](../scripts/historical/README.md)。
- 当前推理身份：[Candidate C](../configs/inference_config.yaml)、[稳定基线](../configs/inference_config_stable_baseline.yaml)。

## 历史报告层

以下原文加了历史快照说明，移除了服务器连接信息；正文状态只代表当时日期。

| 日期 | 报告 |
|---|---|
| 08-05 / 08-08 | [GenBiVLA 方案](../archive/designs/2026-08-05-genbivla-proposal.md)、[ACT raw-HDF5 设计](../archive/designs/2026-08-08-act-raw-hdf5-design.md) |
| 08-14 | [conda 环境恢复修复](../archive/reports/2026-08-14-conda-recovery.md) |
| 08-15 | [基线 600 回合](../archive/reports/2026-08-15-baseline600.md)、[重复性对照](../archive/reports/2026-08-15-repeatability.md)、[失败分析](../archive/reports/2026-08-15-failure-analysis.md)、[合并验收](../archive/reports/2026-08-15-evaluation-finalization.md) |
| 08-16 / 08-17 | [NCCL 故障](../archive/reports/2026-08-16-nccl-failure.md)、[GPU 拓扑 A/B](../archive/reports/2026-08-17-gpu-topology.md) |
| 08-19 | [两版完整模型对照](../archive/reports/2026-08-19-two-model-comparison.md) |
| 08-20 | [候选训练](../archive/reports/2026-08-20-candidate-training.md)、[环境冻结](../archive/reports/2026-08-20-runtime-freeze.md)、[候选筛选](../archive/reports/2026-08-20-candidate-screening.md)、[进程泄漏](../archive/reports/2026-08-20-process-leak.md)、[日志误报](../archive/reports/2026-08-20-error-classifier.md) |

## 未公开材料及原因

- 模型权重、训练视频/轨迹、Isaac Sim 资产：大文件和第三方资产，通过独立渠道管理。
- 私人邮件、联系方式、官网个人信息截图、服务器主机/端口：与项目技术复查无关。
- 重复 ZIP/TAR 和解压验证目录：保留一份有来源的内容，不重复上传。
- 原始代理会话、提示词和运行监控记录：提取结论、脚本与证据后保留本地，避免旧指令与中间状态混入现状。
- 原始评测视频：保留 87 段诊断索引及哈希；没有将全部视频作为仓库内容。
- 未经证实的 ACT 全源码、WAM 或新模型模块：不根据设计稿补造实现。

## 来源与完整性

[source_manifest.json](../audit/source_manifest.json)逐项映射本次收录的源文件，包含原始和公开副本 SHA256。新写的状态/结构/实验说明是对上述来源的综合整理，不伪装成历史原始文件。[curated.sha256](../audit/curated.sha256)覆盖本次收录和更新的公开文件，不自校验。
