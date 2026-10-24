# 个人工作与开源复用边界

项目实施者确认：个人独立项目，2026.07—2026.08。独立组织实施不代表底层模型、框架、服务协议及第三方代码全部原创。本页以保留的差异、脚本、结果与报告说明实际工作。

## 可被代码和记录支持的工作

| 工作 | 具体体现 | 边界 |
|---|---|---|
| 训练数据与机器人配置适配 | [training_worktree.diff](../archive/training/candidate_c/training_worktree.diff) 将 embodiment 标识改为 `arx_x5`，增加枚举 | 基于已有 StarVLA 数据管线，不是从零开发数据框架 |
| 训练运行配置与检查点管理 | 延后 Accelerator 初始化、固定保存里程碑；保留配置和 4 份修改源码 | 不宣称训练算法创新；快照不能单独替代完整上游环境 |
| 部署与批量评测配置 | [deployment_worktree.diff](../archive/training/candidate_c/deployment_worktree.diff) 明确启用 `eval_batch=true` | 不宣称原创 WebSocket 框架或模型批推理提速 |
| 长评测完整性保障 | [eval_guardrails.py](../archive/robodojo/scripts/internal/eval_guardrails.py) 及原有测试 | 核对任务/结果/视频，属于评测工程；历史分片测试缺少匹配实现，不改变成功判定 |
| 通信和环境修复 | conda 自激活、外层 keepalive 配置、[恢复审计](../xpolicylab/scripts/internal/audit_keepalive.py) | 有历史修复记录；代码和回归通过不自动等于策略成功 |
| 数据与实验管理 | [890 轨迹元数据子集脚本](../scripts/historical/subset_meta_890.py)、训练配置派生、运行身份管理 | 历史脚本会写元数据，不能直接作用于唯一数据副本 |
| 结果分析与交付 | 两版 1,200 回合汇总、29/87 诊断索引、候选身份与来源校验 | 本地结果；没有官方成绩、真实硬件验收或整体性能提升结论 |

## 容易讲过头的地方

- Qwen3-VL、QwenOFT、StarVLA 结构、XPolicyLab 协议和 RoboDojo 仿真不是本项目原创。
- `model.py` 中已有观测与动作适配代码是集成基础。没有对应修改证据时，不应将整个文件都描述为本人新写。
- 新增了可配置的 gradient-checkpointing 分支，但 Candidate C 实际 `enable_gradient_checkpointing=false`，不能声称该分支带来了本轮训练节省显存或加速。
- 20k 和 Candidate C 都从公开 checkpoint 初始化，不能说成从零训练大模型。
- 12 个 base 任务与公开训练任务同名，不能宣传为零样本未见任务评测；`_random` 配置名未在训练清单中出现，也不足以证明训练内容从未出现相似布局。

## 面试时可以讲清楚的主线

先说明目标和复用的开源模型，再讲清「三相机/语言/状态 → 动作块 → 16 步执行 → 新观测」的闭环。用一次实际问题说明如何定位和验证，例如残留策略进程引起显存不足，或者仿真加载阻塞引起 WebSocket keepalive 超时。最后用完整评测结果说明已完成的工程范围和仍未解决的泛化问题。

只对自己理解、能指出对应差异和验证方法的部分使用「实现/修改」；其余使用「配置/集成/复用/验证」。
