# StarVLA-QwenOFT：统一双臂协同操作系统

GOAI“具身未来”赛题一（通用双臂协作操作能力测试）的项目主页与复现索引。

本项目采用单一、固定的 StarVLA QwenOFT RoboDojo 100k checkpoint，面向 RoboDojo 的 12 项双臂长程操作任务。输入为头部、左腕、右腕三路相机、语言指令和 14D 机器人状态；输出为 14D `joint` 动作序列。

## 固定提交身份

| 项 | 值 |
|---|---|
| checkpoint | `steps_100000_pytorch_model.pt` |
| SHA256 | `62b8333c9af58467a911150e908cc726dd3c2660fd461871ae9300296391a3cd` |
| 上游权重 | `StarVLA/Qwen3vl4b-OFT-RoboDojo` @ `97123d6ef9f88b99801d07f3ad0720ca7c539777` |
| XPolicyLab | `b01f50a882c119f0643577031b5697db4317a131` |
| RoboDojo | `a63e16a7a6dad6acce5f08352beea80b9b314870` |
| action type | `joint` |
| state/action | 14D / 14D |
| cameras | `head`, `left_wrist`, `right_wrist` |
| action horizon / execute horizon | 50 / 16 |
| normalization | `arx_x5` |
| batch inference | `eval_batch=true`，已验证 `num_envs=5` |

完整代码包和 checkpoint 已依据主办方离线评测通知单独交付。为了避免未经确认的重分发，本公开仓库不包含 RoboDojo 数据、Isaac Sim 资产、checkpoint、缓存、评测视频或其他第三方策略。

## 复现材料

- `xpolicylab/`：实际使用的 StarVLA 适配层、模型服务、WebSocket 通信与环境启动工具；
- `configs/inference_config.yaml`：固定推理接口；
- `docs/code_freeze.md`：代码版本与两项必要运行时修改；
- `docs/evaluation_boundary.md`：本地结果和 X-Eval 官方结果的边界；
- `docs/reproduction.md`：离线评测运行要点。

## 结果边界

本地 Isaac Sim / XPolicyLab 600 回合工程评测结果为 33/600（5.50%）。该数字不是 X-Eval 官方成绩，正式成绩以主办方返回的 X-Eval 结果为准。

## 开源与第三方说明

本仓库仅公开本项目的配置、复现索引和说明。StarVLA、Qwen、RoboDojo、XPolicyLab、Isaac Sim 及其依赖分别受各自的许可证与条款约束；请参见 [NOTICE.md](NOTICE.md)。
