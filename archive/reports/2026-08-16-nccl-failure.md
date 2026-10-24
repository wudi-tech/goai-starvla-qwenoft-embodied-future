> 历史资料快照：以下状态和计划只代表原文日期；当前结论见 [项目状态](../../docs/project_status.md)。已移除服务器连接信息。

# QwenOFT 定向20k 双卡训练 NCCL 非法内存访问 — 完整错误报告

日期：2026-08-16 CST
作者：Codex（已直接接管，不经由 Claude）
目的：完整记录从数据准备到训练启动的每一步操作、错误与修复，供外部评估提出双卡 NCCL 解决方案。

## 1. 任务目标

在公开 QwenOFT checkpoint 基础上做“定向 20k + 多检查点早停”微调：

- 从已评测公开 100k checkpoint 续训，新增 20000 optimizer steps。
- 数据：官方 RoboDojo_lerobot_v21_video（固定 revision `abf44de4b10b5c7efdc68f07630157329dbbcb7f`）中选 890 条轨迹。
- 冻结视觉 + VLM 主干，只训练 action head（+ 接口 adapter）。
- 双卡 RTX 5090 训练，保存 2000/5000/10000/20000 四个 checkpoint，之后快筛。
- 不改变 14D action/state、三相机、action_horizon=50、任务、损失、统计口径。

截止时间：2026-08-20 00:00 CST。

## 2. 硬件与软件环境

- 实例：AutoDL，SSH `[服务器连接信息已移除]`，hostname PC5D。
- GPU：2× NVIDIA GeForce RTX 5090，各 32 GiB，compute capability 12.0（sm_120，Blackwell）。
- 系统内存：754 GiB；数据盘 850G（当时剩余约 351G）。
- 驱动：580.95.05；nvidia-smi 显示 CUDA Version 13.0。
- conda 环境：`/root/autodl-tmp/conda/envs/starvla-goai`，Python 3.11.15。
- conda base：`/root/miniconda3`，`conda.sh` 位于 `/root/miniconda3/etc/profile.d/conda.sh`。
- torch：2.7.0+cu128（`torch.version.cuda == 12.8`）。
- torch 架构列表：`['sm_75','sm_80','sm_86','sm_90','sm_100','sm_120','compute_120']`（含 sm_120，Blackwell 支持正常）。
- NCCL：2.26.2（来自 torch 的 nvidia-nccl-cu12）。
- flash_attn：未安装（`import flash_attn` → ModuleNotFoundError）。

## 3. 模型与数据

模型（框架 `QwenOFT`，注意不是 ABot_M0）：

- `framework.qwenvl.base_vlm` 实际应指向本地模型 `/root/autodl-tmp/GOAI/models/Qwen3-VL-4B-Instruct-ebb281ec`（8.6GB，2 个 safetensors shards）。
- 模型类结构：`qwen_vl_interface`（内含 `.model` 为 Qwen VLM 主干）+ `action_model`（动作头）+ `l1_loss`。
- 没有 `spatial_model`/`VGGT`/`fuser`（那些属于 ABot_M0 框架，与本框架无关）。
- 初始化 checkpoint：`/root/autodl-tmp/GOAI/models/StarVLA-Qwen3vl4b-OFT-RoboDojo-97123d6-local/checkpoints/steps_100000_pytorch_model.pt`（9.7GB）。
- 冻结配置：`freeze_modules = "qwen_vl_interface.model"`。
- 冻结结果（训练日志实测）：`# Parameters: 4503.475M Total, 65.659M Trainable`。
- LR 分组：base=1e-5、qwen_vl_interface=1e-5、action_model=1e-4。

数据：

- 890 条轨迹（6 重点任务×100 + 29 任务×10），共 3565 文件（890 parquet + 2670 mp4 + 5 meta）。
- 数据目录：`$RUN/datasets/RoboDojo_lerobot_v21_video`。
- 已把 `meta/episodes.jsonl`、`episodes_stats.jsonl`、`info.json` 子集化到 890 条（`info.json: total_episodes=890, total_frames=406543`）。
- 完整性验收：3565/3565 文件通过（missing=0, empty=0, size_mismatch=0）。

run 目录：`/root/autodl-tmp/GOAI/training_runs/2026-08-16-qwenoft-target20k-a-2x5090`

## 4. 已成功完成的步骤

1. 定向下载 3565 文件（aria2c 断点续传 + 240 次重试循环），最终 parquet=890、mp4=2670、meta=5。
2. `subset_meta_890.py` 把 meta 子集化到 890 条。
3. `verify_download.py` 验收 3565/3565 通过。
4. 派生训练配置 `config_target20k.yaml`（20k、save_interval=1000、is_resume=false、pretrained_checkpoint=100k、freeze、sdpa、本地 base_vlm）。
5. 补齐缺失依赖：wandb 0.28.2、deepspeed 0.19.5、pyarrow 25.0.1。
6. 单卡 torchrun 训练已成功启动并稳定迭代（见第 8 节）。

## 5. 核心问题

双卡（2× RTX 5090）NCCL 多卡训练在 `accelerator.prepare` / DDP 初始化阶段稳定触发：

```
CUDA error: an illegal memory access was encountered
```

具体表现是 NCCL watchdog 线程报非法内存访问，进程以 SIGABRT（exit code -6）退出。单卡训练完全正常，说明模型、数据、checkpoint、配置本身没有问题，问题聚焦在双卡 NCCL 通信路径。

## 6. 启动尝试时间线（每次操作、改动与精确错误）

### 尝试 1：accelerate + DeepSpeed（默认代码）

启动命令（简化）：

```bash
accelerate launch --num_processes 2 --num_machines 1 --mixed_precision bf16 --dynamo_backend no \
  starVLA/training/train_starvla.py --config_yaml config_target20k.yaml
```

`train_starvla.py` 顶部硬编码：

```python
deepspeed_plugin = DeepSpeedPlugin()
accelerator = Accelerator(deepspeed_plugin=deepspeed_plugin)
```

错误：

```
ProcessGroupNCCL watchdog thread terminated with exception:
CUDA error: an illegal memory access was encountered
Signal 6 (SIGABRT) received by PID
```

### 尝试 2：禁用 DeepSpeed

把 `train_starvla.py` 中 `deepspeed_plugin = DeepSpeedPlugin()` 改为 `deepspeed_plugin = None`。

结果：checkpoint 加载成功（日志出现 `✅ loaded <full_model> model parameters`、`Loaded pretrained checkpoint`），但随后在 DDP 初始化时仍崩溃：

```
CUDAGuardImpl.h:119 Warning: CUDA warning: an illegal memory access was encountered (function destroyEvent)
terminate called after throwing an instance of 'c10::Error'
Signal 6 (SIGABRT)
```

### 尝试 3：NCCL 保守参数（仍用 accelerate）

启动脚本加入：

```bash
export NCCL_P2P_DISABLE=1
export NCCL_IB_DISABLE=1
export NCCL_DEBUG=WARN
```

结果：仍在同一位置（checkpoint 加载后、DDP 初始化）SIGABRT，非法内存访问不变。

### 尝试 4：注意力实现改为 sdpa

配置原为 `attn_implementation: flash_attention_2`（但环境未安装 flash_attn），改为 `sdpa`。

结果：仍 SIGABRT，与尝试 2/3 相同。

### 尝试 5：单卡 accelerate

```bash
accelerate launch --num_processes 1 ...
```

结果：不同错误（不崩溃，而是抛异常）：

```
ValueError: Default process group has not been initialized,
please make sure to call init_process_group.
```

原因：训练代码直接调用 `dist.barrier()`/`dist.get_rank()`，而 accelerate 单卡用 simple_launcher，不初始化进程组。

### 尝试 6：单卡 torchrun（成功）

```bash
torchrun --nproc_per_node=1 --nnodes=1 --node_rank=0 \
  --master_addr=127.0.0.1 --master_port=29500 \
  starVLA/training/train_starvla.py --config_yaml config_target20k.yaml
```

结果：成功。torchrun 单进程会初始化 world_size=1 的进程组，`dist.barrier()` 正常。训练稳定迭代（约 1.68 it/s）。

## 7. 诊断结论

1. 单卡 CUDA 测试正常：`torch.zeros(device='cuda:0')` 与 `cuda:1` 都成功，GPU 本身没有挂死。
2. torch 构建支持 sm_120（Blackwell）正常。
3. NCCL 2.26.2、驱动 580.95.05 都满足版本要求。
4. flash_attn 未安装，但改 sdpa 不影响崩溃，说明不是注意力后端问题。
5. 崩溃只发生在“checkpoint 加载完成 → 冻结 → accelerator.prepare/DDP 初始化”之后，且只在双卡出现，指向 NCCL 多卡通信（P2P/PCIe 直通或 Ring/Simple 算法选择）。
6. 崩溃后 GPU 显示异常：两张卡均 `100% utilization, 0 MiB memory, 无进程`，但单卡 CUDA 测试仍能通过，疑似 NCCL 初始化过程中产生非法访存并污染 CUDA 上下文。

## 8. 当前状态（单卡 workaround，运行中）

- 单卡 torchrun 训练运行中：约 230+/20000 步，1.68 it/s，每步约 0.59s。
- GPU0：99% util，28777 MiB 显存。
- 预计 20k 训练约 3.2 小时完成。
- 无 checkpoint 生成（首个在 step 1000）。
- 数据盘剩余约 351G。

## 9. 待验证的双卡修复方案（已备好脚本，尚未执行）

脚本 `launch_train_target20k_dual_torchrun.sh`，直接使用 `torchrun --nproc_per_node=2`（不再走 accelerate launcher），并加：

```bash
export NCCL_P2P_DISABLE=1
export NCCL_IB_DISABLE=1
export NCCL_ALGO=Ring
export NCCL_PROTO=Simple
export NCCL_DEBUG=INFO
```

计划在 20k 单卡结束后做一次约 20 步的双卡 smoke 验证。

## 10. 关键文件与日志

- 训练日志（当前单卡）：`$RUN/train.log`
- 训练退出码：`$RUN/train.exit`
- 启动日志：`$RUN/train_launch.log`
- 配置：`$RUN/config_target20k.yaml`
- 训练代码：`/root/.config/superpowers/worktrees/XPolicyLab/qwenoft-next-train/policy/starVLA/source_starvla/starVLA/training/train_starvla.py`（已改 `deepspeed_plugin = None`，原始备份 `train_starvla.py.orig`）
- 数据集：`$RUN/datasets/RoboDojo_lerobot_v21_video`
