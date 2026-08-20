# 复现要点

本公开仓库不承载 checkpoint。运行前先确认所选版本及其 SHA256，避免两个同名 `steps_100000_pytorch_model.pt` 混淆。

Candidate C 100k：

```text
size: 9138620878 bytes
sha256: f9653c98f9124065672a659775abe7249f155db96fdeffc288b84ce9a2a87042
action_type: joint
unnorm_key: arx_x5
state/action: 14D / 14D
cameras: head / left_wrist / right_wrist
action_horizon: 50
execute_horizon: 16
eval_batch: true
num_envs: 5
transport: WebSocket
```

历史训练配置中的 `/root/autodl-tmp/...` 只用于溯源。复现时应使用评测机的实际代码和 checkpoint 路径。
