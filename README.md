# StarVLA-QwenOFT：统一双臂协同操作系统

GOAI“具身未来”赛题一（通用双臂协作操作能力测试）的项目主页与复现索引。本分支明确区分第一次提交的稳定基线和第二次 X-Eval 申请的 Candidate C 100k。

模型输入为头部、左腕、右腕三路相机、语言指令和 14D 机器人状态；输出为 14D `joint` 动作序列。

## 双版本身份

| 项 | 稳定基线 | Candidate C 100k |
|---|---|---|
| 角色 | 第一次提交参考版本 | 第二次 X-Eval 唯一候选 |
| checkpoint | `steps_100000_pytorch_model.pt` | `steps_100000_pytorch_model.pt` |
| 字节数 | 9,785,133,528 | 9,138,620,878 |
| SHA256 | `62b8333c9af58467a911150e908cc726dd3c2660fd461871ae9300296391a3cd` | `f9653c98f9124065672a659775abe7249f155db96fdeffc288b84ce9a2a87042` |
| 本地评测 | 600 回合工程评测 33/600、5.50%、score 191.6 | 未运行 600 回合评测 |
| 官方状态 | 本地数字不是 X-Eval 官方成绩 | 第二次 X-Eval 结果待返回 |

Candidate C 的 60k/80k/100k 小样本筛选仅用于内部选型，三版无法区分；选择 100k 是因为它是完整训练终点，不是性能优越性声明。

## 固定接口

- action type：`joint`
- state/action：14D / 14D
- cameras：`head`、`left_wrist`、`right_wrist`
- action horizon / execute horizon：50 / 16
- normalization：`arx_x5`
- batch inference：`eval_batch=true`，验证 `num_envs=5`

## 复现材料

- `xpolicylab/`：实际使用的 StarVLA 适配层、模型服务、WebSocket 通信与环境启动工具；
- `configs/inference_config.yaml`：Candidate C 100k 固定推理接口；
- `configs/inference_config_stable_baseline.yaml`：稳定基线身份；
- `docs/code_freeze.md`：代码版本与实际运行差异；
- `docs/evaluation_boundary.md`：本地结果和 X-Eval 官方结果的边界；
- `docs/reproduction.md`：离线评测运行要点；
- `docs/second_xeval_candidate.md`：第二次候选的完整身份。

本公开仓库不包含 checkpoint、RoboDojo 数据、Isaac Sim 资产、缓存、评测视频、邮件草稿或个人信息。

## 开源与第三方说明

本仓库仅公开本项目的配置、复现索引和说明。StarVLA、Qwen、RoboDojo、XPolicyLab、Isaac Sim 及其依赖分别受各自的许可证与条款约束；请参见 [NOTICE.md](NOTICE.md)。
