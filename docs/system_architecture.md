# 系统结构与联调

## 一次闭环怎样运行

1. RoboDojo / Isaac Sim 产生三路相机图像、语言指令和机器人状态。
2. 仿真客户端向外层 XPolicyLab WebSocket 策略服务发送观测。
3. StarVLA 适配器转换图像与状态，通过内层 WebSocket 客户端调用模型服务。
4. 模型返回 50×14 的动作序列；模型服务使用对应训练统计完成状态归一化和动作反归一化。
5. 适配器将动作转换回仿真环境的关节/夹爪字段，执行前 16 步。
6. 环境再次获取观测，重新预测；回合结束后记录成功判定、分数与三相机视频。

因此有两层服务：**外层仿真协议/适配服务**和**内层模型推理服务**。端口、进程和配置应分开检查。历史记录证明本地 WebSocket 运行，不能据此声明公网 TLS/WSS 已部署。

## 代码入口

| 文件 | 需要理解的职责 |
|---|---|
| [eval.sh](../xpolicylab/policy/starVLA/eval.sh) | 分配端口，启动服务，等待就绪，再启动仿真客户端 |
| [setup_eval_policy_server.sh](../xpolicylab/policy/starVLA/setup_eval_policy_server.sh) | 解析权重路径、运行环境、GPU 和两层服务端口 |
| [model.py](../xpolicylab/policy/starVLA/model.py) | `_convert_obs`、`_infer_chunk`、动作缓存与按环境编号分离的状态 |
| [runtime_config.py](../xpolicylab/policy/starVLA/runtime_config.py) | 根据权重配置解析是否输入本体状态 |
| [deploy.yml](../xpolicylab/policy/starVLA/deploy.yml) | WebSocket、批量评测、执行长度和 keepalive 配置 |
| [setup_env_client.sh](../xpolicylab/utils/setup_env_client.sh) | 定位 conda 并激活仿真运行环境 |
| [policy_norm_processor.py](../xpolicylab/policy/starVLA/source_starvla/deployment/model_server/policy_norm_processor.py) | 训练统计、状态/动作字段和归一化处理 |

## 多环境的含义

`eval_batch=true` 和 `num_envs=5` 表示启用 5 个环境的评测运行。适配器用 `env_idx` 管理各环境的观测、动作块和步数，避免状态串用。

当前 `get_action_batch()` 逐环境调用动作生成；`_infer_chunk()` 的输入 `examples` 是单个环境。因此这份适配代码不能直接证明一次 GPU 前向同时处理了 5 个样本，更不能证明提速 5 倍。没有同条件吞吐基准时，只陈述已验证的多环境评测能力。

## 真正遇到的联调问题

- **外层 keepalive：** 场景加载和首次 reset 耗时较长，客户端事件循环阻塞时可能触发默认心跳超时。历史修复禁用了该部署的外层 keepalive，并根据重连、内层退出、25 条结果和三相机完整性审计是否恢复；不是把所有断线都忽略。
- **运行环境激活：** 启动仿真客户端时不能假定调用方 PATH 中已经存在 conda/python。修复通过 `CONDA_EXE`、PATH 和用户安装目录逐级定位，定位失败则退出。
- **残留策略服务：** 快筛时上一轮服务未退出，多个模型副本与仿真竞争显存，造成 OOM。后续驱动增加按运行身份清理和 GPU 空闲检查；无效运行不进入候选比较。
- **日志误报：** 不能按笼统的 `ERROR` 字样判定失败。可选 MaterialX/NGX 启动信息在有效运行也出现；验收结合明确错误签名、退出码和结果完整性。

完整案例见[环境修复](../archive/reports/2026-08-14-conda-recovery.md)、[残留服务](../archive/reports/2026-08-20-process-leak.md)和[错误分类器](../archive/reports/2026-08-20-error-classifier.md)。
