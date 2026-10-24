> 历史资料快照：以下状态和计划只代表原文日期；当前结论见 [项目状态](../../docs/project_status.md)。已移除服务器连接信息。

# Candidate C 代码与运行环境冻结

## Commit 与工作树状态

- RoboDojo commit：`a63e16a7a6dad6acce5f08352beea80b9b314870`
- XPolicyLab / 部署代码 commit：`b01f50a882c119f0643577031b5697db4317a131`
- 实际训练工作树基准 commit：`b01f50a882c119f0643577031b5697db4317a131`
- 实际训练分支：`codex/qwenoft-next-train`
- remote：`https://github.com/XPolicyLab/XPolicyLab.git`（记录中不含凭据）
- 训练和部署工作树均不干净；完整 diff、状态及未跟踪文件清单已单独保存，不得声称 clean checkout。

## 训练代码修改分类

1. 模型/算法适配：
   - `data_config.py`：训练数据 embodiment 从 `NEW_EMBODIMENT` 改为 `arx_x5`。
   - `embodiment_tags.py`：增加 `ARX_X5 = 'arx_x5'`。
   - `QWen3.py`：增加可配置的 gradient-checkpointing 初始化；本轮配置中 `enable_gradient_checkpointing=false`，因此该分支未启用。
2. 训练运行修改：
   - `train_starvla.py`：延后 `Accelerator` 初始化，避免模块导入阶段过早创建分布式状态。
   - `train_starvla.py`：将 Candidate C 保存里程碑固定为 5k、10k、20k、40k、60k、80k、100k。
3. 部署/batch 修改：
   - `deploy.yml`：`eval_batch: false` 改为 `eval_batch: true`。
4. 运维可用性：
   - 本次实际部署树的 `server_policy.py` 中 `idle_timeout` 默认值仍为 1800；没有把第一次材料中描述的 `-1` 修改冒充为本轮实际状态。

## Diff 与证据哈希

- 训练 diff SHA256：`c331e6d473480a03d249628006c88b68c053acc9c3caacf7ebcd492c1beed724`
- 部署 diff SHA256：`4169106fb4efd963f3c9f8d37e72b21d90718f5885cb70467885a0279e3d9356`
- 完整证据清单：`provenance_files.sha256`

## 实测运行环境

- Python：3.11.15
- PyTorch：2.7.0+cu128
- CUDA（PyTorch build）：12.8
- NCCL：2.26.2
- transformers：4.57.0
- GPU：NVIDIA GeForce RTX 5090
- NVIDIA driver：580.76.05
- 训练 conda 环境：`starvla-goai`

早期续接摘要曾写 PyTorch 2.9.1 / NCCL 2.27.5；本冻结以训练结束后从实际环境读取的版本为准，不沿用旧摘要值。

## 配置哈希

- 启动训练配置 `candidate_c/config.yaml`：`9b12b9aa7625fd1e801534abdce9083c3a5ba2412c2f6ea472c1d57ecf99d5cf`
- 启动脚本 `launch.sh`：`f611484ca485e20987418964ef6d2d85181ff26c673685afd7fc12bd9c94b901`
- checkpoint 配套 `config.yaml`：`b48d07f4ba032efe01ea6d62e8a5fcde34574ebe3b5e01f91f01658aa29738fc`
- checkpoint 配套 `config.full.yaml`：`91d5bf7beb8a6115621941315ce88fcbc9089549b85007df59eab30a18b515a9`
- checkpoint 配套 `dataset_statistics.json`：`df6036dc053c9b2407023d601d995c56d6a28e1deeb11bb9321d92fc5d466a2c`
