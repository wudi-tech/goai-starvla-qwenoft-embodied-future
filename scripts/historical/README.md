# 历史实验脚本

此处保留原始脚本，不是可移植的一键入口。它们包含历史目录、检查点和运行约定；先阅读、替换路径并确认数据/进程范围，再在自己的实验环境运行。本次归档只做静态检查，没有执行训练、仿真或进程清理。

| 文件 | 用途与运行影响 |
|---|---|
| `subset_meta_890.py` | 将三份 LeRobot 元数据限制为指定 890 条轨迹，首次保留备份；会写元数据，需要历史 `target_manifest.json`，当前未收录该清单 |
| `derive_config_target20k.py` | 从公开模型配置派生 20k 配置，写入历史运行目录；依赖 OmegaConf |
| `nccl_smoke.py` | torchrun 启动的 NCCL all-reduce 自检；会实际使用 GPU |
| `final_summary.py` | 历史 20k 结果汇总，依赖评测目录和日志；会写汇总文件，按修改时间选择运行，使用前要确认有效 run 身份 |
| `run_formal_24x25.sh` | 启动 24×25 评测，会运行仿真并清理匹配进程；不要在共享机器直接运行原版宽泛 `pkill` |
| `run_formal_24x25_resume2.sh` | 补跑受损的 3 个任务，具有相同运行副作用 |
| `run_quick_screen_remote_v3.sh` | 60k/80k/100k 的两任务筛选、有效结果复用、按身份清理和 GPU 空闲检查；依赖已有历史日志 |
| `run_tiebreak_pour_remote.sh` | 追加倾倒任务的候选筛选；会运行仿真并管理相关进程 |

20k 脚本使用 `new_embodiment`，Candidate C 使用 `arx_x5`；归一化应匹配各自训练统计。不要将这些文件名中的「remote」解释为本次会话已经连接服务器。
