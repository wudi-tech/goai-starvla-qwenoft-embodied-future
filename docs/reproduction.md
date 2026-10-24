# 复现与验证说明

本仓库提供运行代码、历史训练差异、结果和轻量检查，**不包含**完整权重、数据集和仿真资产。分开理解「复查已归档结果」「测试纯校验逻辑」和「重跑完整 GPU 实验」。

## 1. 无 GPU 的归档代码验证

从仓库根目录，在独立 Python 环境中安装轻量测试依赖并运行：

```bash
python -m pip install -r requirements-validation.txt
python -m pytest archive/robodojo/scripts/internal/tests/test_eval_guardrails.py xpolicylab/scripts/internal/tests/test_audit_keepalive.py -q
```

本次在 Windows / Python 3.14 上复跑，22 项通过：15 项基础评测护栏、7 项 keepalive 恢复审计。它们不加载模型，也不启动 Isaac Sim。

旧包还带有 20 项分片测试，但对应实现没有保留下来，首次全量提取测试运行因此失败。原文另存为 [历史快照](../archive/robodojo/unmatched_tests/test_eval_guardrails_shards.py.snapshot)；不能将上述 22 项通过写成所有历史测试通过。现有 StarVLA 运行测试还需要完整模型依赖，本次没有全量执行。

## 2. 复查结果与文件身份

两版汇总位于 [results/local600](../results/local600/)；基线另有 24 份原始 `_result.json`。重算时按 `details[*].success == true` 计成功，先确认每项恰有 25 条详情，不将受损或补跑前的重复 run 混入。

在具备 `sha256sum` 的环境可从仓库根目录检查本次归档：

```bash
sha256sum -c audit/curated.sha256
```

权重不进入此仓库；以下身份来自 2026-08-20 的历史核验记录，本次没有重读数 GB 权重文件。

| 项 | 稳定基线 | Candidate C 100k |
|---|---|---|
| 文件名 | `steps_100000_pytorch_model.pt` | `steps_100000_pytorch_model.pt` |
| 字节数 | 9,785,133,528 | 9,138,620,878 |
| SHA256 | `62b8333c9af58467a911150e908cc726dd3c2660fd461871ae9300296391a3cd` | `f9653c98f9124065672a659775abe7249f155db96fdeffc288b84ce9a2a87042` |

相同文件名不代表同一个模型。20k 是第三个独立版本，其完整权重身份未在本次公开清单中补造。

## 3. 恢复完整推理与仿真所需内容

1. 根据相应上游版本准备 RoboDojo、Isaac Sim/Isaac Lab、资产和依赖，接受适用许可证。
2. 将本仓库 `xpolicylab/` 的对应代码放入预期的 `RoboDojo/XPolicyLab/` 结构。目录大小写与 Python 导入名有关系，不能假定在当前仓库根目录就能直接启动完整仿真。
3. 另行准备所选 checkpoint、基础 VLM、配套配置和归一化统计。不能把 Candidate C 的统计用于历史 20k 权重。
4. 用实际路径覆盖权重与运行目录，检查两个服务端口、策略 GPU 和仿真 GPU 的分配，再做小规模运行。
5. 核对 `eval_batch` 与实际日志中的 `num_envs`，检查结果条数、三相机输出、退出状态和资源占用，再扩大规模。

主要入口是 [eval.sh](../xpolicylab/policy/starVLA/eval.sh)，参数顺序为：

```text
bench_name task_name ckpt_name env_cfg_type action_type seed policy_gpu_id env_gpu_id policy_conda_env eval_env_conda_env
```

`EVAL_NUM` 控制回合预算；环境数量以实际仿真客户端配置和日志为准，不能与回合数混为一谈。本轮只保留了历史 `num_envs=5` 的验证证据。

Candidate C 固定接口：三相机 224×224、14D 状态/动作、`joint`、`arx_x5`、动作长度 50、执行长度 16。完整训练差异与使用限制见[训练冻结说明](../archive/training/candidate_c/README.md)。

## 4. 历史环境不能混用

Candidate C 冻结环境记录为 Python 3.11.15、PyTorch 2.7.0+cu128、CUDA build 12.8、NCCL 2.26.2、transformers 4.57.0、RTX 5090。早期双卡排障中试用的 PyTorch 2.9.1/NCCL 2.27.5 属于另外的诊断环境，不能冒充 Candidate C 的实际训练环境。

本轮 22 项纯校验测试使用 Python 3.14；这不意味着完整 CUDA/Isaac 运行已在 Python 3.14 复现。详见[本次验证记录](validation_20261024.md)。
