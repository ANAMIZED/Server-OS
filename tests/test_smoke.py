"""Smoke tests that do not require a running server."""

from server_os.cost.controller import CostController
from server_os.governance.policy import PolicyEngine
from server_os.kernel.models import AgentProcess
from server_os.kernel.capabilities import CapabilityRegistry
from server_os.tools.builtin import register_builtins
from server_os.kernel.memory import MemoryStore


def test_cost_estimate():
    c = CostController()
    usd = c.estimate("mock-gpt", 1_000_000, 1_000_000)
    assert usd > 0


def test_policy_deny_missing_capability():
    p = PolicyEngine()
    agent = AgentProcess(name="t", intent="test", budget_usd=1.0, model="mock-gpt", capabilities=["web_search"])
    allowed, reason = p.check_tool(agent, "code_exec")
    assert allowed is False
    assert "not in agent capabilities" in reason


def test_capability_synthesize():
    reg = CapabilityRegistry()
    mem = MemoryStore()
    register_builtins(reg, mem)
    tokens = reg.synthesize(["web_search", "nonexistent"])
    assert len(tokens) == 1
    assert tokens[0].name == "web_search"
