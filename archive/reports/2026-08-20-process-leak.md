> 历史资料快照：以下状态和计划只代表原文日期；当前结论见 [项目状态](../../docs/project_status.md)。已移除服务器连接信息。

# 快筛资源故障记录（结果无效）

## 结论

2026-08-20 13:54 CST 启动的 `60k / fold_clothes_random / seed=0 / EVAL_NUM=5` 运行因上一轮策略服务未退出而发生 GPU 显存溢出。该运行属于基础设施/进程清理故障，不能计入 checkpoint 性能对比。

## 证据

- 上一轮 `60k / stack_bowls` 已在 13:54:22 正常结束，原始结果为 `Success nums: 0, Fail nums: 5, Unstable nums: 0`。
- 故障现场存在两个不同端口的同一 60k 策略服务，分别占用约 9,670 MiB 与 9,404 MiB。
- 同时运行的 `fold_clothes_random` 仿真进程占用约 12,975 MiB。
- 三者合计约 32,049 MiB，超过单卡 RTX 5090 可用显存，日志出现 Vulkan `ERROR_OUT_OF_DEVICE_MEMORY`。
- 精确终止相关 PID 后，`nvidia-smi --query-compute-apps` 为空，说明不是训练进程或其他长期任务占用。

## 处置

- 已保存在 `raw_smoke_screen_logs/failed_attempt_20260820_1354/` 的原始日志与驱动摘要。
- 保留首轮 `stack_bowls` 的有效结果；只废弃受显存故障影响的 `fold_clothes_random` 运行。
- 修订版驱动在每轮前后检查 GPU 空闲，并按 checkpoint、任务和运行身份精确回收策略服务/仿真进程；清理失败即硬停止，不继续产生不可比结果。
- 本故障不构成任何 checkpoint 的性能证据，也不会用于推荐或对外材料。
