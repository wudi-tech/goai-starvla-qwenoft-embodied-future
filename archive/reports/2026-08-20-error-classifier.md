> 历史资料快照：以下状态和计划只代表原文日期；当前结论见 [项目状态](../../docs/project_status.md)。已移除服务器连接信息。

# 快筛错误分类器误报记录

## 结论

`60k / fold_clothes_random / seed=0 / EVAL_NUM=5` 的修订版运行实际完成，结果为 `Success nums: 0, Fail nums: 5, Unstable nums: 0`，退出码为 0。驱动停止的原因是通用 `ERROR` 正则把 Isaac Sim 可选 MaterialX/NGX 组件的启动信息误判为硬错误，并非模型、推理、通信或仿真失败。

## 对照证据

- 有效的 `60k / stack_bowls` 日志中存在相同的 3 条 MaterialX `libXt.so.6` 加载信息及 2 条 NGX 未启用信息。
- 两份日志均在 NGX 信息后完成 `Simulation App Startup Complete` 与 WebSocket 连接。
- `fold_clothes_random` 完成 5 个环境各 500 步、15 个三相机视频落盘、结果汇总、resume manifest 清理和 `[MAIN] eval finished`。
- 针对 `Traceback`、`ERROR_OUT_OF`、显存溢出、CUDA、NCCL、WebSocket、shape/key、NaN/Inf 的硬签名扫描无命中。
- 旧分类器对同一成功日志命中 5 条；去除笼统 `ERROR`、保留明确硬签名后的分类器命中 0 条。

## 处置

- 保留并复用该 60k 随机任务原始结果，不重复消耗 GPU。
- V3 驱动只按明确硬签名停止，同时继续以非零退出码和缺失结果行作为硬门禁。
- 已知 MaterialX/NGX 启动信息仍保留在原始日志中，不删除、不掩盖；最终报告将标注其为非阻断环境信息。
