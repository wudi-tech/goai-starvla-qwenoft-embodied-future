> 历史资料快照：以下状态和计划只代表原文日期；当前结论见 [项目状态](../../docs/project_status.md)。已移除服务器连接信息。

# QwenOFT 评测 A/B 与 P3 双卡并发测试报告

日期：2026-08-17 CST

## 1. 背景

评测固定 eval_batch=true、num_envs=5、execute_horizon=16、unnorm_key=new_embodiment。
目标是判断两件事：

- 单任务评测中，分卡（policy GPU0 + Isaac GPU1）是否比同卡（policy+Isaac 共置 GPU0）更快；
- P3 双任务并发（每张卡一套完整策略+仿真）是否可行、能否提升总吞吐。

## 2. A/B：同卡 vs 分卡（stack_bowls x 5，batch=5）

| 配置 | 命令 | 总耗时 | 结果 |
| --- | --- | --- | --- |
| 同卡 | joint 0 0 0 | 16分53秒 | 1/5 成功，unstable=0 |
| 分卡 | joint 0 0 1 | 17分21秒 | 1/5 成功，unstable=0 |

结论：分卡比同卡慢约 2.8%（28 秒），属于噪声。分卡没有单任务加速。

## 3. P3：双任务并发（每卡一套完整栈）

拓扑：

- GPU0：策略 + Isaac，任务 pour_liquid_into_cup，num_envs=5
- GPU1：策略 + Isaac，任务 stack_bowls，num_envs=5

命令：

- 任务A：eval.sh RoboDojo pour_liquid_into_cup steps_2000 arx_x5 joint 0 0 0 ...
- 任务B：eval.sh RoboDojo stack_bowls steps_2000 arx_x5 joint 0 1 1 ...

两个任务 02:38:31 同时启动。

### 结果

- 任务B（stack_bowls，GPU1）：完成，1/5 成功，unstable=0，约 26 分钟。
- 任务A（pour_liquid_into_cup，GPU0）：显存耗尽（OOM）失败，启动约 2.5 分钟后报错。

### 任务A 的 OOM 错误（关键）

```
[Error] [rtx.scenedb.plugin] getResourceFromAccelStructDesc() failed for updateGroup.
[Error] [carb.graphics-vulkan.plugin] Out of GPU memory allocating resource 'Env: Inverse Conditional CDF'
[Error] [carb.graphics-vulkan.plugin] VkResult: ERROR_OUT_OF_DEVICE_MEMORY
[Error] [carb.graphics-vulkan.plugin] vkAllocateMemory failed.
[Error] [gpu.foundation.plugin] Texture creation failed for the device: 0.
```

OOM 前 GPU0 峰值约 22.3GB（策略约 9.7GB + Isaac 5 环境渲染），随后 Vulkan 纹理分配超出 32GB。

## 4. 关键结论

1. 单任务分卡没有吞吐收益：stack_bowls 上 0/0/1 约等于 0/0/0（约 17 分钟）。
2. P3 双任务并发在 num_envs=5 下不可行：显存较重的任务（pour）在策略+Isaac 同卡时 OOM；只有显存较轻的 stack_bowls 能跑完。
3. 分卡（0/0/1）虽然不快，但更安全：Isaac 独占一张 32GB 卡，给渲染留出更多显存余量；同卡共置会让策略和 Isaac 抢一张卡。

## 5. 对 GPT 的问题

1. 如果仍想启用 P3，是否需要按任务显存分级：显存轻任务用 num_envs=5 共置并发，显存重任务降到 num_envs=2~3 或保持分卡？
2. 显存瓶颈是否主要来自 5 环境 x 3 相机的 Vulkan 渲染缓冲区（尤其是 Env: Inverse Conditional CDF 这类环境贴图）？能否通过减小相机分辨率、降低 num_envs 或关闭部分渲染特性来让共置+P3 同时成立？
3. 当前最稳妥路径是否就是：单任务、0/0/1 分卡、num_envs=5，放弃 P3 和同卡共置？
4. 若要提高总吞吐，是否应优先回到真正的策略 batch 前向和 CPU 视频编码优化（veryfast/threads=1），而不是继续折腾双卡拓扑？

## 6. 关键文件

- A/B 日志：ab_split_canary.log
- P3 日志：p3_concurrent_canary.log、p3_a_pour.log、p3_b_stack.log
- 评测脚本：/root/autodl-tmp/GOAI/RoboDojo/XPolicyLab/policy/starVLA/eval.sh
