# 复现要点

完整代码和 checkpoint 由主办方离线评测材料获取。本公开仓库不承载 9.8 GB checkpoint。

固定运行契约：

```text
checkpoint: steps_100000_pytorch_model.pt
action_type: joint
unnorm_key: arx_x5
state/action: 14D / 14D
cameras: head / left_wrist / right_wrist
action_horizon: 50
execute_horizon: 16
eval_batch: true
num_envs: 5 (validated)
```

运行前核对 checkpoint SHA256：

```text
62b8333c9af58467a911150e908cc726dd3c2660fd461871ae9300296391a3cd
```
