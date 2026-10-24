> 历史资料快照：以下状态和计划只代表原文日期；当前结论见 [项目状态](../../docs/project_status.md)。已移除服务器连接信息。

# Candidate C 远端 checkpoint 固定清单

生成依据：训练实例 `[服务器连接信息已移除]` 上的真实文件、`realpath`、`stat` 与 `sha256sum` 输出。

## 训练状态

- 训练开始：2026-08-19 16:21:23 CST
- 达到 100,000 步：2026-08-20 13:32:54 CST（训练日志进度条）
- 100k checkpoint 写入完成：2026-08-20 13:33:00 CST
- `final_model` 写入完成：2026-08-20 13:33:17 CST
- 启动脚本退出码：0
- 训练日志末次写入：2026-08-20 13:33:17 CST
- 训练总墙钟时间：约 21 小时 12 分钟

## 固定 checkpoint

| 步数 | 绝对路径 / realpath | 字节数 | mtime（CST） | 模式 | SHA256 |
|---:|---|---:|---|---:|---|
| 60,000 | `/root/autodl-tmp/GOAI/candidate_c/candidate_c_from_100k/checkpoints/steps_60000_pytorch_model.pt` | 9,138,620,143 | 2026-08-20 04:59:37 | 644 | `8e31f632ffca69de904a98b2c0f30e48546c3e708084cf76b5425a9e65de7053` |
| 80,000 | `/root/autodl-tmp/GOAI/candidate_c/candidate_c_from_100k/checkpoints/steps_80000_pytorch_model.pt` | 9,138,620,143 | 2026-08-20 09:08:48 | 644 | `acc8df97d38487f7127b9793c7643ec511ccec49f837ef850ceec04684ad8283` |
| 100,000 | `/root/autodl-tmp/GOAI/candidate_c/candidate_c_from_100k/checkpoints/steps_100000_pytorch_model.pt` | 9,138,620,878 | 2026-08-20 13:33:00 | 644 | `f9653c98f9124065672a659775abe7249f155db96fdeffc288b84ce9a2a87042` |

三者均为普通文件，不是 `latest`、`best` 或软链接。

## 本地下载核验

本地目录：`D:\Documents\GOAI具身未来\第二次提交_20260820\01_checkpoints`

| 步数 | 本地字节数 | 本地 SHA256 | 与远端一致 |
|---:|---:|---|---|
| 60,000 | 9,138,620,143 | `8e31f632ffca69de904a98b2c0f30e48546c3e708084cf76b5425a9e65de7053` | 是 |
| 80,000 | 9,138,620,143 | `acc8df97d38487f7127b9793c7643ec511ccec49f837ef850ceec04684ad8283` | 是 |
| 100,000 | 9,138,620,878 | `f9653c98f9124065672a659775abe7249f155db96fdeffc288b84ce9a2a87042` | 是 |

核验时间：2026-08-20 14:08 CST。三个文件均已完成顺序读取与独立 SHA256 重算。

## 最终模型副本

- 路径：`/root/autodl-tmp/GOAI/candidate_c/candidate_c_from_100k/final_model/pytorch_model.pt`
- 字节数：9,138,611,259
- mtime：2026-08-20 13:33:17 CST
- 模式：644

`final_model` 仅作为训练正常收尾的证据；用户已选定 `steps_100000_pytorch_model.pt` 作为第二次 X-Eval 的唯一固定身份，其 SHA256 为 `f9653c98f9124065672a659775abe7249f155db96fdeffc288b84ce9a2a87042`。

## 数据与基础模型

- 数据集：`RoboDojo_lerobot_v21_video`
- 数据混合：`robodojo_v21_all_h50_q99`
- 轨迹数：3,500（`meta/info.json` 与 `meta/episodes.jsonl` 行数一致）
- 总帧数：1,859,602
- 任务数：35
- 数据集本地目录不是 Git 仓库，因此无可声明的 dataset commit/revision；不得伪造。
- 归一化统计唯一顶层键：`arx_x5`
- 基础模型目录标识：`Qwen3-VL-4B-Instruct-ebb281ec`
- 起始公开 checkpoint：`StarVLA-Qwen3vl4b-OFT-RoboDojo-97123d6/checkpoints/steps_100000_pytorch_model.pt`

## 训练配置摘要

- seed：42
- state/action：14D / 14D
- `action_horizon`：50
- `include_state`：true
- 训练动作类型：`abs_qpos` / `abs`
- 单卡 batch：16
- 最大训练步数：100,000
- action model 学习率：2e-5
- 冻结模块：`qwen_vl_interface.model`
- 部署动作类型：`joint`
- 部署 `execute_horizon`：16
- 部署 `eval_batch`：true
