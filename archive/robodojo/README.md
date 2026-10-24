# RoboDojo 评测护栏代码快照

这些文件来自历史离线代码包，仅提取不依赖 Isaac 的任务清单、前后验收逻辑、对应原有测试和最小配置。原始版权见 [LICENSE](LICENSE)。这不是完整 RoboDojo 发行包，不能启动仿真。

## 可以验证的部分

`scripts/internal/eval_guardrails.py` 检查固定 24 项任务、每项 25 回合、结果 `details` 数量、三相机视频及运行资源前检。`task_inventory.py` 和 `task/RoboDojo/task_registry.py` 是它的依赖；本仓库没有附带完整 task 实现，因此任务枚举的完整运行仍依赖上游任务目录。

从仓库根目录运行：

```bash
python -m pytest archive/robodojo/scripts/internal/tests/test_eval_guardrails.py -q
```

该组为无 GPU 的纯校验测试。带系统探测的 preflight CLI 不属于纯测试，会查看磁盘、GPU 和进程，完整 postflight 还需要原始视频。

## 已发现的版本缺口

原代码包同时包含分片测试，但其中引用的 `build_shard_plan`、`validate_manifest` 等函数不在保存的实现中。对照两份代码包和本地副本，`eval_guardrails.py` 均为 13,513 字节、SHA256 `82c07459e1679fb522b6377f28400494233e57db60a6165ce7a1f9a272c5728e`。

首次将所有提取测试一起运行，得到 22 通过、20 失败；20 个失败均来自这一不匹配的分片测试。原文逐字保存在 [unmatched_tests](unmatched_tests/test_eval_guardrails_shards.py.snapshot)，扩展名标记为历史快照，未补造实现或删改断言。现有配套的 15 个基础护栏测试可以独立运行；恢复分片功能前应找到对应版本的原实现。
