# 代码冻结

| 组件 | 固定版本 |
|---|---|
| RoboDojo | `a63e16a7a6dad6acce5f08352beea80b9b314870` |
| XPolicyLab | `b01f50a882c119f0643577031b5697db4317a131` |
| IsaacLab | `afca7b09d60d8beb9c1cb28b43066499940b969b` |
| curobo | `d17b54ce32cba095c0b000c4c58777075d11de0e` |

完整代码归档中包含以下两项必要修改：

1. `policy/starVLA/deploy.yml`：`eval_batch: false` 改为 `eval_batch: true`，用于批推理；
2. `policy/starVLA/source_starvla/deployment/model_server/server_policy.py`：`idle_timeout` 默认值由 `1800` 改为 `-1`，防止推理服务因空闲自动关闭。

上述修改不改变模型权重、三相机接口、14D `joint` 动作、动作窗口或评测统计口径。
