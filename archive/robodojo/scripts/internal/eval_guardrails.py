#!/usr/bin/env python3
"""Minimal pre/post-flight guardrails for the RoboDojo 600-episode benchmark.

This module does NOT run any evaluation, training, or download. It only
validates the boundaries that gate the 600-episode formal re-run so that a
drifted task set, a missing ``--eval-num 25``, an under/over-count of episodes,
or missing camera videos cannot slip through unnoticed.

pre-flight (before starting the sweep):
  * the explicit task list is exactly the 24 Generalization configs
    (12 base + 12 ``_random``);
  * each task's *native* ``eval_nums`` in ``_task.yml`` is exactly 25;
  * the sum of native eval_nums is exactly 600;
  * the disk has >= 80 GiB free;
  * the GPU is idle;
  * no residual screen/Isaac/eval/policy processes are present.

post-flight (after the sweep, before declaring "600 complete"):
  * every task's ``_result.json`` has exactly 25 entries in ``details``;
  * every episode has all three camera videos (head / left_wrist / right_wrist);
  * all 24 tasks pass.

The pure validation functions take plain data so they can be unit-tested
without Isaac Sim or a GPU. System probes (disk/GPU/process) are thin wrappers
that tests can skip or inject.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
INTERNAL_DIR = Path(__file__).resolve().parent
TASK_YML = ROOT_DIR / "task" / "RoboDojo" / "config" / "_task.yml"
EVAL_RESULT_ROOT = ROOT_DIR / "eval_result" / "RoboDojo"

if str(INTERNAL_DIR) not in sys.path:
    sys.path.insert(0, str(INTERNAL_DIR))
import task_inventory  # noqa: E402  (pure stdlib; no Isaac import)

REQUIRED_CAMERAS = ("cam_head", "cam_left_wrist", "cam_right_wrist")
REQUIRED_NATIVE_EVAL_NUM = 25
REQUIRED_TASK_COUNT = 24
REQUIRED_TOTAL_EVAL_NUM = 600
MIN_FREE_DISK_GIB = 80

_RESIDUAL_PATTERNS = (
    "isaac",
    "omni",
    "eval_client",
    "server_policy",
    "setup_policy_server",
    "run_policy_eval",
    "eval_policy",
    "robodojo.sh",
)


# ---------------------------------------------------------------------------
# Pure validation (unit-testable, no side effects)
# ---------------------------------------------------------------------------

def expected_task_set() -> frozenset[str]:
    """Return the exact 24 Generalization configs (12 base + 12 ``_random``)."""
    bases = task_inventory.DIMENSION_TASKS["generalization"]
    return frozenset(list(bases) + [f"{base}_random" for base in bases])


def read_native_eval_nums(task_yml: Path = TASK_YML) -> dict[str, int]:
    """Return ``{task_name: native_eval_nums}`` replicating
    ``pipeline_utils.process_config`` semantics (task override else common=50)."""
    import yaml  # local import keeps pure task-set tests yaml-free

    info = yaml.safe_load(task_yml.read_text(encoding="utf-8")) or {}
    common_num = int((info.get("common") or {}).get("eval_nums", 50))
    out: dict[str, int] = {}
    for name, task_info in (info.get("tasks") or {}).items():
        out[name] = int((task_info or {}).get("eval_nums", common_num))
    return out


def read_tasks_file(path: str | Path) -> list[str]:
    """Read a newline-separated task list, ignoring blank lines and ``#``."""
    names: list[str] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        name = line.strip()
        if name and not name.startswith("#"):
            names.append(name)
    return names


def validate_task_list(task_names: list[str], native: dict[str, int] | None = None) -> list[str]:
    """Return a list of human-readable error strings (empty == valid)."""
    errors: list[str] = []
    expected = expected_task_set()
    names = [n.strip() for n in task_names if n.strip()]

    if len(names) != REQUIRED_TASK_COUNT:
        errors.append(
            f"task list has {len(names)} entries, expected {REQUIRED_TASK_COUNT} "
            "(12 base + 12 _random)"
        )

    actual = set(names)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        if missing:
            errors.append(f"missing expected task(s): {', '.join(missing)}")
        if extra:
            errors.append(f"unexpected extra task(s): {', '.join(extra)}")

    if native is None:
        native = read_native_eval_nums()

    bad: list[str] = []
    total = 0
    for name in sorted(expected):
        num = native.get(name)
        if num is None:
            bad.append(f"{name}: no native eval_nums in _task.yml")
            continue
        total += num
        if num != REQUIRED_NATIVE_EVAL_NUM:
            bad.append(f"{name}: native eval_nums={num} (expected {REQUIRED_NATIVE_EVAL_NUM})")
    if bad:
        errors.append("native eval_nums mismatch: " + "; ".join(bad))
    if total != REQUIRED_TOTAL_EVAL_NUM:
        errors.append(f"sum of native eval_nums={total} (expected {REQUIRED_TOTAL_EVAL_NUM})")

    return errors


def count_details(result_json: Path) -> int | None:
    """Return the number of entries in ``_result.json`` ``details`` (or None)."""
    try:
        data = json.loads(result_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    details = data.get("details")
    return len(details) if isinstance(details, dict) else None


def validate_result_details(
    result_json: Path, expected: int = REQUIRED_NATIVE_EVAL_NUM
) -> list[str]:
    """Return errors if ``_result.json`` does not hold exactly ``expected`` details."""
    n = count_details(result_json)
    if n is None:
        return [f"{result_json}: missing or unreadable _result.json"]
    if n != expected:
        return [f"{result_json}: {n} details (expected {expected})"]
    return []


def validate_videos(
    result_dir: Path,
    num_episodes: int = REQUIRED_NATIVE_EVAL_NUM,
    cameras: tuple[str, ...] = REQUIRED_CAMERAS,
) -> list[str]:
    """Verify each episode 0..num_episodes-1 has one mp4 per camera."""
    errors: list[str] = []
    for idx in range(num_episodes):
        for cam in cameras:
            if not list(result_dir.glob(f"episode_{idx:07d}_{cam}_*.mp4")):
                errors.append(f"episode {idx}: missing {cam} video")
    return errors


def result_dir(
    task: str,
    policy: str,
    env_cfg: str,
    seed: str,
    ckpt: str,
    action_type: str,
    run_id: str,
) -> Path:
    """Reproduce smoke_all_tasks.sh's per-task result directory."""
    return (
        EVAL_RESULT_ROOT
        / task
        / policy
        / env_cfg
        / f"{seed}_ckpt_name={ckpt},action_type={action_type}"
        / f"{run_id}_{task}"
    )


# ---------------------------------------------------------------------------
# System probes (thin subprocess wrappers)
# ---------------------------------------------------------------------------

def check_disk_free_gib(
    path: Path = ROOT_DIR, minimum: int = MIN_FREE_DISK_GIB
) -> tuple[bool, float]:
    usage = shutil.disk_usage(str(path))
    free_gib = usage.free / (1024 ** 3)
    return free_gib >= minimum, free_gib


def check_gpu_idle() -> tuple[bool, str]:
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used,memory.total", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=15,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return False, f"nvidia-smi unavailable: {exc}"
    if out.returncode != 0:
        return False, f"nvidia-smi failed: {out.stderr.strip()}"
    busy: list[str] = []
    for i, line in enumerate(out.stdout.strip().splitlines()):
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 2:
            continue
        try:
            used, total = int(parts[0]), int(parts[1])
        except ValueError:
            continue
        if used > 0:
            busy.append(f"gpu{i}: {used}/{total} MiB")
    if busy:
        return False, "GPU not idle: " + ", ".join(busy)
    return True, "GPU idle"


def check_no_residual_processes() -> tuple[bool, str]:
    problems: list[str] = []
    screen = subprocess.run(["screen", "-ls"], capture_output=True, text=True)
    if screen.returncode == 0 and "No Sockets found" not in screen.stdout:
        problems.append("active screen session(s) present")

    try:
        ps = subprocess.run(["ps", "-eo", "pid,args"], capture_output=True, text=True, timeout=10)
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return False, f"ps unavailable: {exc}"

    self_pid = str(os.getpid())
    hits: list[str] = []
    for line in ps.stdout.splitlines():
        parts = line.split(None, 1)
        if not parts:
            continue
        pid, args = parts[0], parts[1] if len(parts) > 1 else ""
        if pid == self_pid:
            continue
        if any(pattern in args for pattern in _RESIDUAL_PATTERNS):
            hits.append(f"pid {pid}: {args.strip()[:120]}")

    if hits:
        problems.append("residual eval/Isaac/policy process(es): " + "; ".join(hits))
    return (not problems), "; ".join(problems) if problems else "no residual processes"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _fail(errors: list[str]) -> None:
    for e in errors:
        print(f"[guardrail] ERROR: {e}", file=sys.stderr)
    sys.exit(1)


def _ok(msg: str) -> None:
    print(f"[guardrail] OK: {msg}")


def cmd_preflight(args: argparse.Namespace) -> None:
    errors: list[str] = []

    if args.eval_num is None:
        errors.append("--eval-num is required and must be the explicit value 25")
    elif args.eval_num != REQUIRED_NATIVE_EVAL_NUM:
        errors.append(
            f"--eval-num={args.eval_num} is not the explicit value {REQUIRED_NATIVE_EVAL_NUM}"
        )

    task_names = read_tasks_file(args.tasks_file)
    errors.extend(validate_task_list(task_names))

    if not args.skip_system:
        ok_disk, free_gib = check_disk_free_gib()
        if ok_disk:
            print(f"[guardrail] disk free {free_gib:.1f} GiB (>= {MIN_FREE_DISK_GIB} GiB)")
        else:
            errors.append(f"disk free {free_gib:.1f} GiB < {MIN_FREE_DISK_GIB} GiB")

        ok_gpu, gpu_msg = check_gpu_idle()
        print(f"[guardrail] {gpu_msg}")
        if not ok_gpu:
            errors.append(gpu_msg)

        ok_proc, proc_msg = check_no_residual_processes()
        print(f"[guardrail] {proc_msg}")
        if not ok_proc:
            errors.append(proc_msg)

    if errors:
        _fail(errors)

    _ok(
        f"preflight passed: {REQUIRED_TASK_COUNT} tasks, "
        f"native eval_nums sum={REQUIRED_TOTAL_EVAL_NUM}, eval-num={args.eval_num}, "
        f"run-id={args.run_id or '<unset>'}"
    )


def cmd_postflight(args: argparse.Namespace) -> None:
    task_names = read_tasks_file(args.tasks_file)
    errors: list[str] = []
    passed = 0

    for task in task_names:
        d = result_dir(
            task, args.policy, args.env_cfg, args.seed, args.ckpt,
            args.action_type, args.run_id,
        )
        task_errors = validate_result_details(d / "_result.json", expected=args.eval_num)
        task_errors += validate_videos(d, num_episodes=args.eval_num)
        if task_errors:
            errors.append(f"{task}: " + "; ".join(task_errors))
        else:
            passed += 1

    total = len(task_names)
    print(f"[guardrail] postflight: {passed}/{total} tasks complete")
    if errors:
        _fail(errors)

    if total == REQUIRED_TASK_COUNT and passed == REQUIRED_TASK_COUNT:
        _ok(
            f"600-episode complete: {passed}/{total} tasks, "
            f"{passed * args.eval_num} episodes, 3-camera videos verified"
        )
    else:
        _ok(f"{passed}/{total} tasks complete (partial run)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_pre = sub.add_parser("preflight", help="Validate task set + system state before the sweep")
    p_pre.add_argument("--tasks-file", required=True, help="Newline-separated 24-task list")
    p_pre.add_argument("--eval-num", type=int, default=None, help="Explicit per-task episode count (25)")
    p_pre.add_argument("--run-id", default=None, help="Run id (recorded, not validated)")
    p_pre.add_argument("--skip-system", action="store_true", help="Skip disk/GPU/process probes")

    p_post = sub.add_parser("postflight", help="Validate results + videos after the sweep")
    p_post.add_argument("--tasks-file", required=True, help="Newline-separated task list")
    p_post.add_argument("--eval-num", type=int, required=True, help="Per-task episode count (25)")
    p_post.add_argument("--policy", required=True, help="Policy name (basename of --policy-dir)")
    p_post.add_argument("--env-cfg", required=True, help="env_cfg stem (arx_x5)")
    p_post.add_argument("--seed", required=True, help="Eval seed (0)")
    p_post.add_argument("--ckpt", required=True, help="Checkpoint name")
    p_post.add_argument("--action-type", required=True, help="Action type (joint)")
    p_post.add_argument("--run-id", required=True, help="Run id used to locate result dirs")

    args = parser.parse_args()
    if args.command == "preflight":
        cmd_preflight(args)
    else:
        cmd_postflight(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
