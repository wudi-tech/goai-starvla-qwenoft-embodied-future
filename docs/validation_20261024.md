# 2026-10-24 归档验证记录

本轮验证的对象是收录代码、历史结果与公开资料，不是重新执行 GPU 实验。机器可读记录见 [publication_checks.json](../audit/publication_checks.json)，文件身份见 [curated.sha256](../audit/curated.sha256)。

## 原有轻量测试

在独立 Windows / Python 3.14 环境，使用 pytest 9.1.1、PyYAML 6.0.3 执行：

```bash
python -m pytest archive/robodojo/scripts/internal/tests/test_eval_guardrails.py xpolicylab/scripts/internal/tests/test_audit_keepalive.py -q
```

结果：**22 passed**，其中基础护栏 15 项、keepalive 审计 7 项。没有启动 Isaac Sim、模型加载或训练。

## 首次提取测试发现的问题

首次将原包内的基础护栏、分片护栏和 keepalive 审计一起运行，结果 **22 passed、20 failed**。20 个失败均为缺少分片函数，例如 `build_shard_plan`、`validate_manifest`，而非 GPU 或依赖错误。

进一步核对两份代码包及解压副本，保存的 `eval_guardrails.py` 内容完全相同，且没有这些函数。没有补造新实现来冒充历史代码。原测试内容原样保存到 [分片测试快照](../archive/robodojo/unmatched_tests/test_eval_guardrails_shards.py.snapshot)，正常运行命令只包含当前有配套实现的测试。该缺口仍然存在。

## 其他核验范围

- 对本次 76 份收录源文件检查原始与公开副本哈希，文档脱敏处理单独记录。
- 重算两版 JSON/TSV 的 24 项、600 回合和成功总数；稳定基线另与 24 份原始 `_result.json` 逐任务核对。
- 核对诊断索引 29 回合、87 视频，以及 Candidate C 的 9 个任务/检查点组合、45 小样本回合。
- 对本次新增 Python 源文件做语法解析、Bash 脚本做语法检查；不执行历史脚本的运行副作用。
- 检查当前说明文档的相对链接、训练差异能否应用到所保留的基准树，以及选定公开文件中的敏感信息和大文件类型。
- 对最终 Git 暂存内容做差异和空白检查；推送后再核对远端提交。

## 结论的适用范围

本轮不声称全套 StarVLA 测试通过，不声称旧 GPU 环境已重建，也不将旧报告中的通过数量直接视为本轮通过。20k 全量原始回合、ACT 全源码、匹配的分片实现、最终官方受理和成绩回执仍有缺口。重新读取历史结果只能复核统计一致性，不能证明当前模型会复现相同任务成功率。
