> 历史资料快照：以下状态和计划只代表原文日期；当前结论见 [项目状态](../../docs/project_status.md)。已移除服务器连接信息。

# QwenOFT RoboDojo 逐任务失败分析

## 方法与边界

- 每个任务抽取第一个失败回合；5 个存在成功的任务另抽取第一个成功回合作对照。
- 共备份 29 个回合、87 个三相机视频，并检查每个回合的三相机五时点接触图。
- 分类是基于可见行为的诊断，不是对模型内部原因的直接测量。单个失败样本不能代表该任务全部 25 回合，因此详细结论保留中等置信度。

## 总体失败模式

| 失败模式 | 主要任务 | 可见表现 |
|---|---|---|
| 随机布局下感知/定位与动作启动 | arrange/random、push_T/random、pack/random、pour/random、make_toast/random | 手臂有运动，但目标物几乎没有有效状态变化，完整操作链未建立。 |
| 精细对齐与接触控制 | fold、stack_blocks、stack_bowls、hang_mugs、make_toast | 能靠近并抓取/搬运，但在最后对齐、插入、堆叠、挂接或柔性物体整形上失败。 |
| 多物体/多阶段顺序 | arrange、nesting_dolls、store_laptop_and_headphones | 已完成局部交互，但未将多个子目标按完整顺序收敛到终局。 |
| 双臂工具协同 | sweep_blocks 及 random | 刷子、畚箕与对象均有交互，但缺少稳定协同轨迹，对象未被收集。 |
| 倾倒角度/时序控制 | pour_liquid_into_cup | 已抓瓶并到达杯上方，成败区分主要出现在姿态、位置和倾倒持续时间。 |

## 任务级结论

1. **最有学习信号的能力**：倾倒（40%）、碗堆叠（36%）、衣物折叠和积木堆叠（均 24%）。这些任务中策略已学会大部分宏观流程，主要短板是末端精度和对齐。
2. **随机化是主要泛化断层**：除 `fold_clothes_random` 仍有 8% 外，其他有对应非随机成功的随机任务全部降至 0%。影像中常见「手臂运动但不形成有效首次接触」。
3. **长时序任务尚未形成稳定子目标管理**：数字排序、套娃、电脑+耳机收纳中，局部动作不是完全缺失，但多物体顺序没有收敛。
4. **0/25 不等于同一种失败**：`make_toast` 已把面包送到烤面包机但插入失败；`make_toast_random` 则连稳定的抓取→插槽链都没有建立。训练干预应分开。

## 数据与证据

- 逐任务分类：`artifacts/qwenoft-formal600-2026-08-15/task-analysis.tsv`
- 视频索引：`artifacts/qwenoft-formal600-2026-08-15/diagnostic-index.tsv`
- 选中回合：`artifacts/qwenoft-formal600-2026-08-15/diagnostic-selections.tsv`
- 三相机视频：`artifacts/qwenoft-formal600-2026-08-15/diagnostic-videos/`
- 三相机接触图：`artifacts/qwenoft-formal600-2026-08-15/qwenoft-contact-sheets-20260815/`

## 建议的下一个证据步骤

不应仅根据这 29 个抽样回合立即改模型结构。先盘点可比基线和其他 checkpoint；若不存在可比正式结果，则最小方案是对 3–4 个 checkpoint 使用同一个高信号任务子集做受控对比，再决定新训练数据和步数。
