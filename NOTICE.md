# 第三方组件与重分发说明

本仓库不重分发 checkpoint、RoboDojo 数据、Isaac Sim 资产、完整 RoboDojo 源码或缓存。`xpolicylab/` 保留实际使用的 StarVLA 适配层、必要服务代码及原有许可证。2026-10-24 的整理另收录少量 RoboDojo 任务/验收工具及配置、StarVLA 训练修改快照，均保留来源、作者信息和许可证。

完整离线评测包中使用的第三方组件包括 StarVLA / QwenOFT、Qwen3-VL、RoboDojo、XPolicyLab、IsaacLab、curobo 和 Isaac Sim。使用、下载、再分发或部署这些组件前，应分别遵守其官方仓库、模型卡、软件许可与数据条款。

## 本次新增代码的许可来源

- `archive/robodojo/`：保留原代码包中的 MIT 许可证，见该目录 `LICENSE`。该目录是部分工具快照，不是完整 RoboDojo 仿真系统。
- `archive/training/candidate_c/modified_files/`：StarVLA 源码的项目修改快照，保留源文件作者与版权，见 `LICENSE_StarVLA`（MIT）。
- `xpolicylab/`：原有 XPolicyLab Apache-2.0 许可证，以及其内 StarVLA 的 MIT 许可证继续适用；新增恢复审计工具仍保留在原组件目录中。

`audit/source_manifest.json` 用于来源追溯，不替代许可证。历史报告、项目说明和配置用于解释个人实施与实验，不能据此将第三方算法或代码的完整著作权归为项目作者。没有对整个混合仓库重新指定统一许可证。
