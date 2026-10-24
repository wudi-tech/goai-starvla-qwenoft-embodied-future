"""Reusable postflight audit: classify an outer WebSocket keepalive timeout.

The outer XPolicyLab policy server closes a connection with
``1011 keepalive ping timeout`` when the Isaac eval client blocks its event
loop during scene/model load and the first reset (see
``policy/starVLA/deploy.yml``).  That signature is benign *only when* the
client successfully reconnects and the task still completes: inner exit == 0,
``details`` == 25, and all three cameras hold 25 non-empty videos.

Anything else is a real failure.  This is offline audit tooling for the
recovery-run postflight generator, not production runtime code.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence

KEEPALIVE_SIGNATURE = "keepalive ping timeout"
RECONNECT_MARKER = "[RECONNECT]"
CONNECTED_MARKER = "[CONNECTED]"
REQUIRED_CAMERAS = ("cam_head", "cam_left_wrist", "cam_right_wrist")


def classify_keepalive_timeout(
    log_lines: Iterable[str],
    *,
    inner_exit: int | str,
    details: int | None,
    camera_counts: Mapping[str, int],
    required_details: int = 25,
    required_cameras: Sequence[str] = REQUIRED_CAMERAS,
) -> tuple[str, list[str]]:
    """Classify a task's keepalive situation.

    Returns ``(verdict, reasons)`` where verdict is one of:

    * ``"ok"``      — no keepalive signature in the log range.
    * ``"warning"`` — keepalive timeout was recovered: a ``[RECONNECT]`` then
      ``[CONNECTED]`` follows the timeout and the output is complete.
    * ``"fail"``    — keepalive timeout not recovered, or the output is
      incomplete (non-zero inner exit, short ``details``, missing cameras).
    """
    lines = list(log_lines)
    keepalive_idx = [
        i for i, line in enumerate(lines) if KEEPALIVE_SIGNATURE in line
    ]
    if not keepalive_idx:
        return "ok", []

    # Only the reconnect state after the *last* timeout matters: an earlier
    # recovery does not excuse a later unrecovered drop.
    tail = lines[keepalive_idx[-1]:]
    reconnect_idx = next(
        (i for i, line in enumerate(tail) if RECONNECT_MARKER in line), None
    )
    connected_idx = next(
        (i for i, line in enumerate(tail) if CONNECTED_MARKER in line), None
    )
    reconnected = (
        reconnect_idx is not None
        and connected_idx is not None
        and reconnect_idx <= connected_idx
    )

    reasons: list[str] = []
    if not reconnected:
        reasons.append("keepalive timeout without successful reconnect")
    if str(inner_exit) != "0":
        reasons.append(f"inner_exit={inner_exit}")
    if details != required_details:
        reasons.append(f"details={details}")
    missing = [
        cam for cam in required_cameras if camera_counts.get(cam, 0) != required_details
    ]
    if missing:
        reasons.append(f"cameras_missing={','.join(missing)}")

    if reasons:
        return "fail", reasons
    return "warning", ["recoverable keepalive timeout"]
