"""Server OS as an MCP Server.

Exposes Autonomous Agentic Operating System primitives as MCP tools
so any MCP-compatible client can create agents, enforce budgets, run tasks,
inspect audit/cost, and orchestrate multi-agent workflows.
"""

from __future__ import annotations

from typing import Any

try:
    from fastmcp import FastMCP
except ImportError:  # pragma: no cover
    from mcp.server.fastmcp import FastMCP

from server_os.agents.runtime import AgentRuntime
from server_os.cost.controller import CostController
from server_os.governance.policy import PolicyEngine
from server_os.kernel.capabilities import CapabilityRegistry
from server_os.kernel.memory import MemoryStore
from server_os.kernel.models import AgentProcess, Task, Workflow, TaskStatus
from server_os.kernel.store import ProcessTable
from server_os.observability.tracer import Tracer
from server_os.tools.builtin import register_builtins

_store = ProcessTable()
_memory = MemoryStore()
_registry = CapabilityRegistry()
_cost = CostController()
_policy = PolicyEngine()
_tracer = Tracer()
_tools = register_builtins(_registry, _memory)
_runtime = AgentRuntime(
    registry=_registry,
    memory=_memory,
    cost=_cost,
    policy=_policy,
    tracer=_tracer,
)

mcp = FastMCP(
    "Server OS",
    instructions=(
        "You are connected to Server OS, an Autonomous Agentic Operating System. "
        "Use the tools to create agent processes, run goals under budget and policy, "
        "inspect cost and audit logs, and orchestrate multi-agent workflows. "
        "Always prefer explicit budgets and least-privilege capabilities."
    ),
)


@mcp.tool()
def list_agents() -> list[dict[str, Any]]:
    """List in-process agent records (id, status, spend, budget, capabilities).

    Use before run_task to discover agent_id values. Read-only snapshot.
    Does not create agents (create_agent) or start work (run_task).
    """
    return [a.model_dump(mode="json") for a in _store.list_agents()]


@mcp.tool()
def create_agent(
    name: str,
    intent: str,
    budget_usd: float = 0.5,
    capabilities: list[str] | None = None,
    model: str = "mock-gpt",
) -> dict[str, Any]:
    """Create an agent process with intent, USD budget, and capabilities.

    Returns agent_id for later run_task / get_agent calls. Does not execute a
    goal. Side effect: writes the process table. Default model is mock-gpt.
    """
    caps = capabilities or ["web_search", "memory_read", "memory_write"]
    agent = AgentProcess(name=name, intent=intent, budget_usd=budget_usd, model=model, capabilities=caps)
    tokens = _registry.synthesize(caps)
    agent.capabilities = [t.name for t in tokens]
    _store.create_agent(agent)
    _tracer.inc("agents_created")
    _tracer.record(agent.id, "system", f"Agent created via MCP: {agent.name}", data={"intent": intent})
    return agent.model_dump(mode="json")


@mcp.tool()
def run_task(agent_id: str, goal: str) -> dict[str, Any]:
    """Run one goal on an existing agent until completion, policy deny, or budget stop.

    Blocks up to 120s. Missing agent_id returns an error object. Use create_agent
    first. Not for multi-agent orchestration (create_workflow). Side effects:
    task row + spend + save().
    """
    agent = _store.get_agent(agent_id)
    if not agent:
        return {"error": f"agent not found: {agent_id}"}
    task = Task(agent_id=agent_id, goal=goal)
    _store.create_task(task)

    import asyncio
    import concurrent.futures

    def _run_sync():
        return asyncio.run(_runtime.run_task(agent, task))

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            task = pool.submit(_run_sync).result(timeout=120)
    except Exception as e:
        return {"error": f"task execution failed: {e}", "agent_id": agent_id, "goal": goal}

    _store.update_task(task)
    _store.save()
    return task.model_dump(mode="json")


@mcp.tool()
def get_agent(agent_id: str) -> dict[str, Any]:
    """Get full state of one agent process by id.

    Use after create_agent or list_agents. Read-only. Missing ids return an
    error object. Does not run work (run_task).
    """
    agent = _store.get_agent(agent_id)
    if not agent:
        return {"error": f"agent not found: {agent_id}"}
    return agent.model_dump(mode="json")


@mcp.tool()
def get_cost_ledger() -> list[dict[str, Any]]:
    """Return the token/$ cost ledger for this process.

    Use to audit spend after run_task. Read-only. Not get_audit_log or get_metrics.
    """
    return _cost.dump()


@mcp.tool()
def get_audit_log() -> list[dict[str, Any]]:
    """Return governance allow/deny records from the policy engine.

    Use after a blocked run_task. Read-only. Not the dollar ledger (get_cost_ledger).
    """
    return _policy.dump()


@mcp.tool()
def get_metrics() -> dict[str, float]:
    """Return runtime counters (agents created, tasks).

    Use for health checks. Read-only. Does not include cost rows or policy events.
    """
    return _tracer.dump_metrics()


@mcp.tool()
def create_workflow(
    name: str,
    goal: str,
    agents: list[str] | None = None,
    budget_usd: float = 1.0,
) -> dict[str, Any]:
    """Create specialist agents and run a sequential multi-agent workflow.

    Default roles are planner then worker, sharing budget_usd. Use when a goal
    needs more than one agent. Do not use to run a single existing agent
    (run_task). Side effects: creates agents + tasks and marks the workflow
    completed.
    """
    roles = agents or ["planner", "worker"]
    agent_ids: list[str] = []
    for role in roles:
        agent = AgentProcess(
            name=f"{name}-{role}",
            intent=f"Role: {role}. Overall goal: {goal}. Stay within budget and use only granted tools.",
            budget_usd=budget_usd / max(len(roles), 1),
            model="mock-gpt",
            capabilities=["web_search", "memory_read", "memory_write"],
        )
        tokens = _registry.synthesize(agent.capabilities)
        agent.capabilities = [t.name for t in tokens]
        _store.create_agent(agent)
        agent_ids.append(agent.id)
        _tracer.inc("agents_created")

    wf = Workflow(name=name, goal=goal, agent_ids=agent_ids)
    _store.create_workflow(wf)

    results = []
    import asyncio
    import concurrent.futures

    def _run_one(agent, task):
        return asyncio.run(_runtime.run_task(agent, task))

    for aid in agent_ids:
        agent = _store.get_agent(aid)
        assert agent is not None
        task = Task(agent_id=aid, goal=f"[{agent.name}] Contribute to: {goal}")
        _store.create_task(task)
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            task = pool.submit(_run_one, agent, task).result(timeout=120)
        _store.update_task(task)
        results.append({"agent": agent.name, "result": task.result, "status": str(task.status)})

    wf.status = TaskStatus.COMPLETED
    wf.result = str(results)
    _store.save()
    return {"workflow": wf.model_dump(mode="json"), "results": results}


@mcp.tool()
def list_available_tools() -> list[str]:
    """List capability names that can be granted to agents.

    Use before create_agent to choose the capabilities argument. Read-only.
    """
    return _registry.list_available()


def main() -> None:
    """Entry point for server-os-mcp / stdio MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
