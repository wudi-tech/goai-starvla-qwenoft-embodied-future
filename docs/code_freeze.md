# 代码冻结

| 组件 | 固定版本 |
|---|---|
| RoboDojo | `a63e16a7a6dad6acce5f08352beea80b9b314870` |
| XPolicyLab / 训练基准 | `b01f50a882c119f0643577031b5697db4317a131` |

实际训练与部署工作树存在已冻结差异，不能描述为 clean checkout：

- 训练 diff SHA256：`c331e6d473480a03d249628006c88b68c053acc9c3caacf7ebcd492c1beed724`
- 部署 diff SHA256：`4169106fb4efd963f3c9f8d37e72b21d90718f5885cb70467885a0279e3d9356`

主要差异包括：启用 `arx_x5` embodiment、Qwen3 配置兼容、训练保存里程碑、延后 Accelerator 初始化，以及部署 `eval_batch=true`。

本轮实际 `server_policy.py` 默认 `idle_timeout=1800`。旧材料中关于改为 `-1` 的描述不适用于 Candidate C，本分支已纠正该口径。

已验证运行环境：Python 3.11.15、PyTorch 2.7.0+cu128、CUDA 12.8、NCCL 2.26.2、transformers 4.57.0、RTX 5090、driver 580.76.05。
