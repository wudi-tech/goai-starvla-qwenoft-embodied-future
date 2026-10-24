"""Tests for eval_guardrails pre/post-flight pure validation.

These tests exercise only the pure, side-effect-free functions in
``scripts/internal/eval_guardrails.py`` (task-set validation, native
eval_nums, result ``details`` count, and per-episode camera video
completeness). No Isaac Sim, GPU, or real evaluation is launched.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

INTERNAL_DIR = Path(__file__).resolve().parents[1]
if str(INTERNAL_DIR) not in sys.path:
    sys.path.insert(0, str(INTERNAL_DIR))

import eval_guardrails as eg  # noqa: E402


# ---------------------------------------------------------------------------
# expected task set
# ---------------------------------------------------------------------------

def test_expected_task_set_has_24_entries():
    tasks = eg.expected_task_set()
    assert len(tasks) == 24
    assert len(tasks) == eg.REQUIRED_TASK_COUNT


def test_expected_task_set_is_12_base_plus_12_random():
    tasks = eg.expected_task_set()
    base = {t for t in tasks if not t.endswith("_random")}
    random = {t for t in tasks if t.endswith("_random")}
    assert len(base) == 12
    assert len(random) == 12
    # every random variant has a matching base task
    assert all(f"{b}_random" in random for b in base)


# ---------------------------------------------------------------------------
# native eval_nums from _task.yml
# ---------------------------------------------------------------------------

def test_native_eval_nums_each_25_and_sum_600():
    native = eg.read_native_eval_nums()
    expected = eg.expected_task_set()
    total = 0
    for name in sorted(expected):
        assert name in native, f"{name} missing from _task.yml tasks section"
        assert native[name] == eg.REQUIRED_NATIVE_EVAL_NUM, f"{name} native={native[name]}"
        total += native[name]
    assert total == eg.REQUIRED_TOTAL_EVAL_NUM
    assert total == 600


# ---------------------------------------------------------------------------
# validate_task_list
# ---------------------------------------------------------------------------

def _valid_names() -> list[str]:
    return sorted(eg.expected_task_set())


def test_validate_task_list_accepts_exact_24():
    assert eg.validate_task_list(_valid_names()) == []


def test_validate_task_list_rejects_23_entries():
    errors = eg.validate_task_list(_valid_names()[:-1])
    assert any("23 entries" in e for e in errors)


def test_validate_task_list_rejects_25_entries_with_extra():
    errors = eg.validate_task_list(_valid_names() + ["not_a_real_task"])
    assert any("25 entries" in e or "unexpected extra" in e for e in errors)


def test_validate_task_list_rejects_missing_random():
    names = [n for n in _valid_names() if n != "stack_bowls_random"]
    errors = eg.validate_task_list(names)
    assert any("missing expected" in e for e in errors)


def test_validate_task_list_rejects_corrupted_native():
    native = dict(eg.read_native_eval_nums())
    native["stack_bowls"] = 50  # simulate a drifted _task.yml
    errors = eg.validate_task_list(_valid_names(), native=native)
    assert any("native eval_nums mismatch" in e for e in errors)


# ---------------------------------------------------------------------------
# post-flight: _result.json details count
# ---------------------------------------------------------------------------

def _write_result(path: Path, n: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    details = {str(i): {"layout_id": i, "success": False, "score": 0.0} for i in range(n)}
    path.write_text(json.dumps({"eval_time": n, "details": details}), encoding="utf-8")


def test_validate_result_details_accepts_25(tmp_path):
    rj = tmp_path / "_result.json"
    _write_result(rj, 25)
    assert eg.validate_result_details(rj) == []


def test_validate_result_details_rejects_24(tmp_path):
    rj = tmp_path / "_result.json"
    _write_result(rj, 24)
    assert any("24 details" in e for e in eg.validate_result_details(rj))


def test_validate_result_details_rejects_26(tmp_path):
    rj = tmp_path / "_result.json"
    _write_result(rj, 26)
    assert any("26 details" in e for e in eg.validate_result_details(rj))


def test_validate_result_details_rejects_missing(tmp_path):
    rj = tmp_path / "_result.json"  # never created
    assert any("missing" in e for e in eg.validate_result_details(rj))


# ---------------------------------------------------------------------------
# post-flight: per-episode camera video completeness
# ---------------------------------------------------------------------------

def _touch_videos(d: Path, episodes: int, cameras, skip: set | None = None) -> None:
    d.mkdir(parents=True, exist_ok=True)
    skip = skip or set()
    for i in range(episodes):
        for cam in cameras:
            if (i, cam) in skip:
                continue
            (d / f"episode_{i:07d}_{cam}_fail.mp4").write_bytes(b"x")


def test_validate_videos_accepts_complete(tmp_path):
    _touch_videos(tmp_path, 25, eg.REQUIRED_CAMERAS)
    assert eg.validate_videos(tmp_path, 25) == []


def test_validate_videos_rejects_missing_camera(tmp_path):
    _touch_videos(tmp_path, 25, eg.REQUIRED_CAMERAS, skip={(0, "cam_head")})
    errors = eg.validate_videos(tmp_path, 25)
    assert any("cam_head" in e for e in errors)


def test_validate_videos_rejects_missing_episode(tmp_path):
    _touch_videos(tmp_path, 25, eg.REQUIRED_CAMERAS)
    for cam in eg.REQUIRED_CAMERAS:
        (tmp_path / f"episode_0000024_{cam}_fail.mp4").unlink()
    errors = eg.validate_videos(tmp_path, 25)
    assert any("episode 24" in e for e in errors)
