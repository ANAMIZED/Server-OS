"""SDK integration-style tests (require live Server OS or will skip)."""

from __future__ import annotations

import os

import pytest

from server_os.kernel.models import AgentCreate
from server_os.sdk.client import ServerOSClient

BASE = os.environ.get("SERVER_OS_URL", "http://127.0.0.1:8080")


def _alive() -> bool:
    try:
        with ServerOSClient(BASE, timeout=2.0) as c:
            c.health()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _alive(), reason="Server OS not running")


def test_sdk_health_and_create_run():
    with ServerOSClient(BASE) as c:
        h = c.health()
        assert h.get("status") == "ok"
        agent = c.create_agent(
            AgentCreate(
                name="sdk-pytest",
                intent="Answer factual questions under budget using approved tools",
                budget_usd=0.4,
                capabilities=["web_search", "memory_read"],
            )
        )
        assert agent.id.startswith("agt_")
        assert "web_search" in agent.capabilities
        task = c.run_task(agent.id, "What is the capital of France?")
        assert task.status.value == "completed" or str(task.status) == "completed"
        assert task.result and "paris" in task.result.lower()
        ledger = c.cost_ledger()
        assert isinstance(ledger, list)
        metrics = c.metrics()
        assert "agents_created" in metrics
