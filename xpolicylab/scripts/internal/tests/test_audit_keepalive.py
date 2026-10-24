"""Unit tests for the keepalive-timeout postflight discriminator."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from audit_keepalive import classify_keepalive_timeout  # noqa: E402


_COMPLETE = {"cam_head": 25, "cam_left_wrist": 25, "cam_right_wrist": 25}

_RECOVERABLE_LOG = [
    "TASK_START task=pack_objects_into_box",
    "env0 step 1/1300",
    "websockets.exceptions.ConnectionClosedError: sent 1011 (internal error) "
    "keepalive ping timeout; no close frame received",
    "[client.py] ERROR: recv loop ended",
    "[RECONNECT] connection dropped while waiting for reset; retry in 5s",
    "[CONNECTED] websocket policy server connected: ws://localhost:6000 (attempt 1/10)",
    "env0 step 2/1300",
]


def test_recoverable_keepalive_is_warning() -> None:
    verdict, reasons = classify_keepalive_timeout(
        _RECOVERABLE_LOG, inner_exit=0, details=25, camera_counts=_COMPLETE
    )
    assert verdict == "warning"
    assert reasons == ["recoverable keepalive timeout"]


def test_no_keepalive_is_ok() -> None:
    verdict, reasons = classify_keepalive_timeout(
        ["TASK_START task=x", "env0 step 1/100", "env0 step 2/100"],
        inner_exit=0,
        details=25,
        camera_counts=_COMPLETE,
    )
    assert verdict == "ok"
    assert reasons == []


def test_keepalive_without_reconnect_fails() -> None:
    log = [
        "websockets.exceptions.ConnectionClosedError: sent 1011 (internal error) "
        "keepalive ping timeout; no close frame received",
        "[client.py] ERROR: recv loop ended",
    ]
    verdict, reasons = classify_keepalive_timeout(
        log, inner_exit=0, details=25, camera_counts=_COMPLETE
    )
    assert verdict == "fail"
    assert reasons[0] == "keepalive timeout without successful reconnect"


def test_keepalive_reconnect_but_nonzero_exit_fails() -> None:
    verdict, reasons = classify_keepalive_timeout(
        _RECOVERABLE_LOG, inner_exit=1, details=25, camera_counts=_COMPLETE
    )
    assert verdict == "fail"
    assert "inner_exit=1" in reasons


def test_keepalive_reconnect_but_short_details_fails() -> None:
    verdict, reasons = classify_keepalive_timeout(
        _RECOVERABLE_LOG, inner_exit=0, details=24, camera_counts=_COMPLETE
    )
    assert verdict == "fail"
    assert "details=24" in reasons


def test_keepalive_reconnect_but_camera_missing_fails() -> None:
    verdict, reasons = classify_keepalive_timeout(
        _RECOVERABLE_LOG,
        inner_exit=0,
        details=25,
        camera_counts={"cam_head": 25, "cam_left_wrist": 25, "cam_right_wrist": 0},
    )
    assert verdict == "fail"
    assert reasons[0] == "cameras_missing=cam_right_wrist"


def test_later_unrecovered_timeout_fails_even_after_earlier_recovery() -> None:
    log = _RECOVERABLE_LOG + [
        "websockets.exceptions.ConnectionClosedError: sent 1011 (internal error) "
        "keepalive ping timeout; no close frame received",
        "[client.py] ERROR: recv loop ended",
    ]
    verdict, reasons = classify_keepalive_timeout(
        log, inner_exit=0, details=25, camera_counts=_COMPLETE
    )
    assert verdict == "fail"
    assert reasons[0] == "keepalive timeout without successful reconnect"
