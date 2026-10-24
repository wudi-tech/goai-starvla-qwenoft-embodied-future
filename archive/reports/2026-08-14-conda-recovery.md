> 历史资料快照：以下状态和计划只代表原文日期；当前结论见 [项目状态](../../docs/project_status.md)。已移除服务器连接信息。

# QwenOFT 恢复修复复审问题 — 严格 TDD 加固（完成）

- 完成日期：2026-08-14
- 修复 worktree：`/root/.config/superpowers/worktrees/XPolicyLab/qwenoft-eval-recovery`
- 分支：`codex/qwenoft-eval-recovery`
- 起点 HEAD：`1fe75c742037176b793878b00d8d09c33697fcd7`
- **修复 commit：`b01f50a882c119f0643577031b5697db4317a131`** `fix(eval): locate conda without caller PATH`（独立提交，非 amend；父提交 `1fe75c7`）

---

## 结论：C1/I1/M1/M2 已修复，RED→GREEN 严格闭环

- 改动范围仅 3 个文件：`utils/setup_env_client.sh`（改）、`tests/test_setup_env_client_env.py`（改）、`tests/conftest.py`（删）。
- 无 token/cookie/私钥泄漏；无大文件；tracked 树 clean；未触碰正式工作区；未启动任何 Isaac/评测/screen/训练/下载。

---

## 1. RED 复现（原样证据，本次会话内重跑）

确定性复现命令（`CONDA_SHLVL=1` 是复现评审 RED 的关键，见下）：

```
$ CONDA_SHLVL=1 /root/autodl-tmp/conda/envs/RoboDojo/bin/python -m pytest tests/test_setup_env_client_env.py -v
1 failed, 1 passed   （退出码 1）
```

失败原文（子进程退出码 127）：

```
utils/setup_env_client.sh: line 28: conda: command not found
utils/setup_env_client.sh: line 28: /etc/profile.d/conda.sh: No such file or directory
```

失败发生在 production 行（`setup_env_client.sh:28` 的 `source "$(conda info --base)/..."`），非测试语法问题。

### 额外发现：原测试是 FLAKY（值得记录）

同一个测试在 **`CONDA_SHLVL` 未设置**时是 **2 passed（绿）**，在 **`CONDA_SHLVL=1`** 时是 **1 failed / 1 passed（红）**。根因是旧 `_run_bootstrap` 在**外层** bash `source conda.sh` 再 `conda deactivate`：

- 若外层 `CONDA_SHLVL` 未设置 → `conda.sh` 会 prepend `/root/miniconda3/condabin` 到 PATH → 子进程继承到 conda → 误绿；
- 若外层 `CONDA_SHLVL` 已设置（评审的启动形态）→ `conda.sh` 跳过 PATH-prepend → 子进程 PATH 无 conda → 红。

这说明旧修复只是把「依赖裸 python」换成「依赖 caller 的 conda 状态」，正是评审 C1 的判定。重写后的测试显式清空 conda 状态（pop `CONDA_EXE/CONDA_PREFIX/CONDA_SHLVL/CONDA_DEFAULT_ENV/CONDA_PYTHON_EXE`）并按场景显式设置 `PATH/CONDA_EXE/HOME`，已与 caller 环境解耦。

---

## 2. 修复设计（`utils/setup_env_client.sh`，最小、可移植、fail-closed）

替换原 `source "$(conda info --base)/etc/profile.d/conda.sh"`，新增 `_resolve_conda_sh()`，按序定位：

1. `$CONDA_EXE`（任何 conda-initialized shell 都会导出）→ `dirname dirname` 推 base prefix；
2. `command -v conda`（PATH fallback）→ 同上推导；
3. 逐用户安装根：`$HOME/miniconda3`、`$HOME/anaconda3`。

最终 source 的路径必须**存在且可读**（`-r`），否则打印清晰错误并非零退出；**绝不**从空的 `conda info --base` 静默拼出 `/etc/profile.d/conda.sh`。激活仍用 `${eval_env_conda_env}`（本任务 RoboDojo），未硬编码 starvla-goai。

### 契约注释已对齐（I1）

新注释明确：不依赖 caller PATH 上的裸 `python`；conda 定位顺序与 fail-closed 语义写清，与实现一致。

### 边界说明（写入手记，非缺陷）

- 已知路径 fallback 只含 `$HOME/miniconda3` / `$HOME/anaconda3`，**故意**不含 `/opt/conda`、`/usr/local/miniconda3`——为了用 `HOME` 覆盖让 fail-closed 测试可封闭、不依赖机器状态。代价：conda 装在别处且 `CONDA_EXE`/`command -v conda` 都失效时会 fail-closed（清晰报错）。本机（recovery 专用）可接受。
- 本机 `conda.sh` 首行硬编码 `export CONDA_EXE='/root/miniconda3/bin/conda'`，source 时会覆盖传入的 CONDA_EXE——因此「CONDA_EXE 无效」只有在**所有**来源都落空时才真正 fail-closed，测试正是用 `HOME` 覆盖强制走到该分支。

---

## 3. 测试覆盖（`tests/test_setup_env_client_env.py`，重写）

4 个测试，真实跑 `utils/setup_env_client.sh` 子进程 + 假派发树：

1. `test_self_activates_via_conda_exe_without_caller_python` — caller PATH 无 python/conda、仅 `CONDA_EXE` 有效 → 自激活 RoboDojo + 后续 bootstrap，且 cache/offline/EULA 变量全保留。
2. `test_self_activates_via_conda_on_path_fallback` — 无 `CONDA_EXE`、conda 在 PATH → fallback 成功。
3. `test_fails_closed_when_conda_unresolvable` — `CONDA_EXE` 无效 + PATH 无 conda + 空 `HOME` → 清晰非零失败，且输出不含伪造的 `/etc/profile.d/conda.sh`。
4. `test_fails_clearly_on_nonexistent_eval_env` — eval env 不存在 → 清晰非零失败（`conda activate` 报 EnvironmentNameNotFound）。

Minor 处理：`tests/conftest.py` 确认无用已删（M1）；conda 根/conda.sh/conda bin 由 `_discover_conda_exe()` 从运行时环境推导（`CONDA_EXE`→`shutil.which`→`$HOME/miniconda3`），不再硬编码 `/root/miniconda3/...`（M2）。`RoboDojo` 仍是命名常量（任务语义参数，非机器路径）。

---

## 4. GREEN（fresh 执行）

**专项测试**（RoboDojo python，含 pytest 9.1.1）：

```
$ /root/autodl-tmp/conda/envs/RoboDojo/bin/python -m pytest tests/test_setup_env_client_env.py -v
4 passed   （退出码 0）
```

**确定性复验**（此前会红的环境）：

```
$ CONDA_SHLVL=1 ... -m pytest tests/test_setup_env_client_env.py -q
4 passed   （退出码 0）
```

**全量三处**（必须用 starvla-goai python，见下）：

```
$ /root/autodl-tmp/conda/envs/starvla-goai/bin/python -m pytest tests/ policy/starVLA/tests/ scripts/internal/tests/ -q
18 passed, 1 warning   （退出码 0）
```

> 环境注意：`policy/starVLA/tests/test_runtime_reproducibility.py` import `accelerate`，只在 `starvla-goai`（1.5.2）有、RoboDojo 无。用 RoboDojo 跑三处会得 `1 failed（No module named 'accelerate'）/17 passed`——这是既有的环境缺依赖，与本修复无关；三处全绿须用 starvla-goai 解释器。

**静态检查**：

- `bash -n utils/setup_env_client.sh` → OK
- `git diff --check` → OK（无空白错误）
- 凭据扫描（`sk-* / api_key / token / password / secret / PRIVATE KEY / cookie / Authorization / Bearer`）→ 无命中
- 大文件（>1MB）→ 无
- tracked 树 clean：`git status --porcelain` 为空；`__pycache__/`、`.pytest_cache/` 均在 `!!` 忽略态

---

## 5. 提交

```
b01f50a fix(eval): locate conda without caller PATH
   tests/conftest.py                  |   8 ---
   tests/test_setup_env_client_env.py | 127 +++++++++++++++++++++++------
   utils/setup_env_client.sh          |  58 +++++++++++++--
   3 files changed, 160 insertions(+), 33 deletions(-)
```

独立提交，未 amend；父提交 `1fe75c7`（评审对象）。分支 `codex/qwenoft-eval-recovery` 现 HEAD = `b01f50a`。

---

## 6. 正式工作区只读确认（未做任何修改）

- `/root/autodl-tmp/GOAI/RoboDojo/XPolicyLab` HEAD = `7748e2d0a284d6c4f2604687cb46a1f140c99d13`（base，detached），未切换。
- tracked clean；`git status --porcelain` 仅 7 个既有 untracked tmp 目录（`policy/starVLA/source_starvla/tmp{1j9y6m7n,4i4fga9y,8j0qmgrb,gt1e_5oi,jgi0x__g,kka1383b,sq98s93m}/_remote_module_non_scriptable.py`），为 torch 运行产物，**未触碰**。
- 无 screen（`No Sockets found`）、无 tmux、无 GPU compute 进程（nvidia-smi 空）。
- `pgrep` 仅命中一个**只读日志监控** bash（PID 45778，`grep/tail` 旧 `smoke_results/2026-08-13-qwenoft-formal600-4x5090/*.screen.log`），非评测/screen/GPU/训练作业；本次会话未启动任何新作业。

---

## 7. 风险 / 遗留

1. 未部署正式工作区、未启动 canary（按指令停在代码+验证）。
2. fail-closed 已知路径 fallback 仅 `$HOME/{miniconda3,anaconda3}`，换机且 CONDA_EXE/command-v-conda 双失效时会清晰失败而非自愈（见 §2 边界）。
3. 全量测试的「三处全绿」依赖 starvla-goai 解释器（accelerate 只在 policy env）；建议后续全量门禁固定用 starvla-goai。
4. 未改动 model/checkpoint/data/动作维度/回合数/统计口径/keepalive 配置。
