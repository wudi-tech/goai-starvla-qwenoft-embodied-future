# Candidate C 100k 训练冻结

这些文件是 2026-08-20 交付资料中保存的实际配置、启动方式、差异和修改后的源文件，用于复查当时如何训练。不是一套可直接双击运行的完整训练包。

## 文件

- `training_config.yaml`：本轮启动配置。
- `checkpoint_config.yaml` / `checkpoint_config.full.yaml`：检查点配套配置。
- `dataset_statistics.json`：本轮训练/推理匹配的 `arx_x5` 统计。
- `launch.sh`：历史单卡训练启动脚本，保留当时绝对路径。
- `training_worktree.diff`：相对 XPolicyLab 基准 `b01f50a882c119f0643577031b5697db4317a131` 的训练修改。
- `deployment_worktree.diff`：本轮部署设置 `eval_batch=true`。
- `modified_files/`：4 份修改后的源码，保留上游作者和版权。

## 训练含义

从公开稳定基线权重初始化，冻结 `qwen_vl_interface.model`，在 35 项任务的 3,500 条轨迹上训练 100,000 步。数据记录为 1,859,602 帧，批量 16，seed 42，动作头学习率 2e-5。轨迹和帧数来自历史训练清单，本次没有重新读取服务器数据集。

实际保存里程碑为 5k/10k/20k/40k/60k/80k/100k。Qwen3 的可选 gradient-checkpointing 代码存在，但本轮 `enable_gradient_checkpointing=false`。不要根据配置中另一个同名 trainer 字段宣称该模型分支已启用。

## 使用边界

恢复训练需另行取得对应上游代码、公开初始权重、基础 VLM、数据和依赖，并替换历史路径。可先用 `git apply --check` 检查差异是否匹配目标树；本仓库部署已启用批量评测，不能重复套用部署 diff 来解释为新变更。没有在本次归档中重启训练。

训练源码受 StarVLA 原有许可证约束，见 [LICENSE_StarVLA](LICENSE_StarVLA)。修改内容与本轮实测环境见[历史环境冻结](../../reports/2026-08-20-runtime-freeze.md)。
