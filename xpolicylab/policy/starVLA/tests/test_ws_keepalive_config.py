"""Outer (XPolicyLab) WebSocket keepalive config regression test.

The outer policy server (``client_server.ws.model_server``) defaults its
keepalive to ``ping_interval=20s`` / ``ping_timeout=20s`` whenever
``deploy.yml`` does not override it.  During Isaac scene/model load and the
first reset the eval client blocks its event loop for 40-90s, so the server's
ping goes unanswered and it closes the connection with
``1011 keepalive ping timeout``.  The fix mirrors the inner-loop precedent
(``ping_interval=None`` in ``source_starvla``): ``policy/starVLA/deploy.yml``
must explicitly disable the outer server keepalive.

This test resolves the server keepalive exactly as ``model_server.main()`` does
and asserts it is disabled (``None``), not the 20/20 default.
"""

from __future__ import annotations

from pathlib import Path
import sys

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
POLICY_DIR = Path(__file__).resolve().parents[1]
DEPLOY_YML = POLICY_DIR / "deploy.yml"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from client_server.ws.model_server import PolicyServerConfig  # noqa: E402


def _resolve_server_keepalive(deploy_cfg: dict):
    """Mirror ``model_server.main()`` keepalive resolution for the outer server."""
    return (
        deploy_cfg.get("ws_ping_interval_s", 20.0),
        deploy_cfg.get("ws_ping_timeout_s", 20.0),
    )


def test_starvla_deploy_disables_outer_server_keepalive() -> None:
    cfg = yaml.safe_load(DEPLOY_YML.read_text(encoding="utf-8"))

    # Absent keys fall back to the 20/20 default -> 1011 during long load.
    assert "ws_ping_interval_s" in cfg, (
        "policy/starVLA/deploy.yml must explicitly set ws_ping_interval_s"
    )
    assert "ws_ping_timeout_s" in cfg, (
        "policy/starVLA/deploy.yml must explicitly set ws_ping_timeout_s"
    )

    interval, timeout = _resolve_server_keepalive(cfg)
    server_cfg = PolicyServerConfig(
        ws_ping_interval_s=interval, ws_ping_timeout_s=timeout
    )
    assert server_cfg.ws_ping_interval_s is None, (
        "outer server keepalive must be disabled (null), "
        f"got {server_cfg.ws_ping_interval_s!r}"
    )
    assert server_cfg.ws_ping_timeout_s is None, (
        "outer server keepalive must be disabled (null), "
        f"got {server_cfg.ws_ping_timeout_s!r}"
    )


def test_server_keepalive_null_is_disabled_but_positive_is_kept() -> None:
    # Document the normalizer contract the fix relies on.
    disabled = PolicyServerConfig(ws_ping_interval_s=None, ws_ping_timeout_s=None)
    assert disabled.ws_ping_interval_s is None
    assert disabled.ws_ping_timeout_s is None

    enabled = PolicyServerConfig(ws_ping_interval_s=20.0, ws_ping_timeout_s=20.0)
    assert enabled.ws_ping_interval_s == 20.0
    assert enabled.ws_ping_timeout_s == 20.0
